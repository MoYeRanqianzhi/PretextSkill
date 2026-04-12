#!/usr/bin/env bun
/**
 * Grade a Pretext review iteration using Claude CLI.
 *
 * Usage:
 *   bun run skills/pretext/scripts/grade-pretext-review-iteration.ts
 *   bun run skills/pretext/scripts/grade-pretext-review-iteration.ts --workspace skills/pretext-workspace/iteration-1
 *   bun run skills/pretext/scripts/grade-pretext-review-iteration.ts --force --model claude-sonnet-4-20250514
 */

import { resolve, join } from "node:path";
import { parseArgs } from "node:util";
import { readdirSync, statSync, existsSync, readFileSync } from "node:fs";

// ── Evidence polarity cues ─────────────────────────────────────────────────

const POSITIVE_EVIDENCE_CUES: readonly string[] = [
  "explicitly state",
  "explicitly states",
  "explicitly require",
  "explicitly requires",
  "explicitly say",
  "explicitly says",
  "explicitly choose",
  "explicitly chooses",
  "explicitly cite",
  "explicitly cites",
  "explicitly list",
  "explicitly lists",
  "clearly",
  "shows",
  "show ",
  "name ",
  "names",
  "list ",
  "lists",
  "recommend ",
  "recommends",
  "uses",
  "returns",
  "point to",
  "points to",
  "includes",
  "states ",
  "state that",
  "states that",
  "describe",
  "describes",
  "contrast",
  "contrasts",
  "mentions",
  "明确",
  "列出",
  "给出",
  "指出",
  "引用",
  "使用",
  "推荐",
  "返回",
  "说明",
];

const NEGATIVE_EVIDENCE_CUES: readonly string[] = [
  "does not",
  "did not",
  "no mention",
  "not mention",
  "never mentions",
  "missing",
  "absent",
  "fails to",
  "stops at",
  "no reference set",
  "no concrete commands",
  "does not route",
  "does not map",
  "未提及",
  "没有",
  "缺少",
  "未返回",
];

// ── Types ──────────────────────────────────────────────────────────────────

interface ExpectationResult {
  text: string;
  passed: boolean;
  evidence: string;
}

interface ClaimResult {
  claim: string;
  type: string;
  verified: boolean;
  evidence: string;
}

interface UserNotesSummary {
  uncertainties: string[];
  needs_review: string[];
  workarounds: string[];
}

interface EvalFeedback {
  suggestions: { reason: string; assertion?: string }[];
  overall: string;
}

interface GradingSummary {
  passed: number;
  failed: number;
  total: number;
  pass_rate: number;
}

interface NormalizedGrading {
  expectations: ExpectationResult[];
  summary: GradingSummary;
  claims: ClaimResult[];
  user_notes_summary: UserNotesSummary;
  eval_feedback: EvalFeedback;
  normalization_notes: string[];
  execution_metrics?: Record<string, unknown>;
  timing?: Record<string, number>;
}

interface EvalMetadata {
  eval_id: number;
  eval_name: string;
  prompt: string;
  expectations: string[];
  expected_output: string;
}

// ── Claude CLI ─────────────────────────────────────────────────────────────

async function runClaude(
  prompt: string,
  workdir: string,
  model: string | undefined,
): Promise<string> {
  const cmd = [
    "claude",
    "-p",
    prompt,
    "--output-format",
    "text",
    "--permission-mode",
    "bypassPermissions",
  ];
  if (model) {
    cmd.push("--model", model);
  }

  const env: Record<string, string> = {};
  for (const [k, v] of Object.entries(process.env)) {
    if (k !== "CLAUDECODE" && v !== undefined) {
      env[k] = v;
    }
  }

  const proc = Bun.spawn(cmd, {
    cwd: workdir,
    env,
    stdout: "pipe",
    stderr: "pipe",
  });

  const [stdout, stderr] = await Promise.all([
    new Response(proc.stdout).text(),
    new Response(proc.stderr).text(),
  ]);
  const exitCode = await proc.exited;

  if (exitCode !== 0) {
    throw new Error(stderr.trim() || "claude grading run failed");
  }
  return stdout;
}

// ── JSON extraction ────────────────────────────────────────────────────────

function extractJsonObject(text: string): Record<string, unknown> {
  const stripped = text.trim();
  if (!stripped) {
    throw new Error("Empty grading output");
  }

  // Try parsing the whole string
  try {
    return JSON.parse(stripped);
  } catch {
    // continue
  }

  // Try fenced code block
  const fenced = stripped.match(/```json\s*(\{[\s\S]*\})\s*```/);
  if (fenced) {
    return JSON.parse(fenced[1]);
  }

  // Try finding first { to last }
  const start = stripped.indexOf("{");
  const end = stripped.lastIndexOf("}");
  if (start !== -1 && end !== -1 && end > start) {
    return JSON.parse(stripped.slice(start, end + 1));
  }

  throw new Error("Could not extract JSON object from grading output");
}

// ── Normalization helpers ──────────────────────────────────────────────────

function normalizeExpectations(
  rawExpectations: Record<string, unknown>[],
  fallbackExpectations: string[],
): ExpectationResult[] {
  const normalized: ExpectationResult[] = [];
  for (let index = 0; index < fallbackExpectations.length; index++) {
    const raw = index < rawExpectations.length ? rawExpectations[index] : {};
    normalized.push({
      text:
        (raw.text as string) ||
        (raw.expectation as string) ||
        fallbackExpectations[index],
      passed: Boolean(raw.passed ?? raw.met ?? false),
      evidence: (raw.evidence as string) || "",
    });
  }
  return normalized;
}

function flattenEvidenceText(evidence: unknown): string {
  if (typeof evidence === "string") return evidence;
  if (Array.isArray(evidence)) {
    return evidence.map((item) => flattenEvidenceText(item)).join(" ");
  }
  if (typeof evidence === "object" && evidence !== null) {
    return Object.values(evidence)
      .map((value) => flattenEvidenceText(value))
      .join(" ");
  }
  return String(evidence);
}

function classifyEvidencePolarity(evidence: unknown): "positive" | "negative" | "unclear" {
  const text = flattenEvidenceText(evidence).toLowerCase();
  if (!text.trim()) return "unclear";

  const hasPositive = POSITIVE_EVIDENCE_CUES.some((cue) => text.includes(cue));
  const hasNegative = NEGATIVE_EVIDENCE_CUES.some((cue) => text.includes(cue));

  if (hasPositive && !hasNegative) return "positive";
  if (hasNegative && !hasPositive) return "negative";
  return "unclear";
}

function repairExpectationPolarity(
  expectations: ExpectationResult[],
): { repaired: ExpectationResult[]; notes: string[] } {
  const repaired: ExpectationResult[] = [];
  const notes: string[] = [];

  for (const item of expectations) {
    const next = { ...item };
    const polarity = classifyEvidencePolarity(next.evidence);
    if (polarity === "positive" && !next.passed) {
      next.passed = true;
      notes.push(
        `Flipped expectation to pass because the evidence text was affirmative: ${next.text}`,
      );
    } else if (polarity === "negative" && next.passed) {
      next.passed = false;
      notes.push(
        `Flipped expectation to fail because the evidence text was negative: ${next.text}`,
      );
    }
    repaired.push(next);
  }

  return { repaired, notes };
}

function normalizeClaims(rawClaims: unknown[]): ClaimResult[] {
  const claims: ClaimResult[] = [];
  for (const raw of rawClaims) {
    if (typeof raw !== "object" || raw === null) {
      claims.push({
        claim: String(raw),
        type: "factual",
        verified: false,
        evidence: "",
      });
      continue;
    }
    const r = raw as Record<string, unknown>;
    claims.push({
      claim: (r.claim as string) || "",
      type: (r.type as string) || "factual",
      verified: Boolean(r.verified ?? r.supported ?? false),
      evidence: (r.evidence as string) || "",
    });
  }
  return claims;
}

function normalizeUserNotes(rawUserNotes: unknown): UserNotesSummary {
  if (typeof rawUserNotes === "object" && rawUserNotes !== null && !Array.isArray(rawUserNotes)) {
    const r = rawUserNotes as Record<string, unknown>;
    return {
      uncertainties: Array.isArray(r.uncertainties)
        ? (r.uncertainties as string[])
        : [],
      needs_review: Array.isArray(r.needs_review)
        ? (r.needs_review as string[])
        : [],
      workarounds: Array.isArray(r.workarounds)
        ? (r.workarounds as string[])
        : [],
    };
  }
  const note = String(rawUserNotes ?? "").trim();
  return {
    uncertainties: note ? [note] : [],
    needs_review: [],
    workarounds: [],
  };
}

function normalizeEvalFeedback(rawEvalFeedback: unknown): EvalFeedback {
  if (typeof rawEvalFeedback === "object" && rawEvalFeedback !== null && !Array.isArray(rawEvalFeedback)) {
    const r = rawEvalFeedback as Record<string, unknown>;
    const suggestions: EvalFeedback["suggestions"] = [];
    if (Array.isArray(r.suggestions)) {
      for (const item of r.suggestions) {
        if (typeof item === "object" && item !== null) {
          const s = item as Record<string, unknown>;
          const suggestion: { reason: string; assertion?: string } = {
            reason: (s.reason as string) || "",
          };
          if (s.assertion) {
            suggestion.assertion = s.assertion as string;
          }
          suggestions.push(suggestion);
        }
      }
    }
    return {
      suggestions,
      overall: (r.overall as string) || "",
    };
  }
  return {
    suggestions: [],
    overall: String(rawEvalFeedback ?? "").trim(),
  };
}

function normalizeGrading(
  raw: Record<string, unknown>,
  fallbackExpectations: string[],
): NormalizedGrading {
  let expectations = normalizeExpectations(
    (raw.expectations as Record<string, unknown>[]) || [],
    fallbackExpectations,
  );
  const { repaired, notes: normalizationNotes } =
    repairExpectationPolarity(expectations);
  expectations = repaired;

  const passed = expectations.filter((e) => e.passed).length;
  const total = expectations.length;
  const failed = total - passed;

  return {
    expectations,
    summary: {
      passed,
      failed,
      total,
      pass_rate: total > 0 ? Math.round((passed / total) * 10000) / 10000 : 0,
    },
    claims: normalizeClaims((raw.claims as unknown[]) || []),
    user_notes_summary: normalizeUserNotes(raw.user_notes_summary ?? {}),
    eval_feedback: normalizeEvalFeedback(raw.eval_feedback ?? {}),
    normalization_notes: normalizationNotes,
  };
}

// ── Workspace traversal ────────────────────────────────────────────────────

function iterRuns(workspace: string): { runDir: string; metadata: EvalMetadata }[] {
  const runs: { runDir: string; metadata: EvalMetadata }[] = [];

  const entries = readdirSync(workspace)
    .filter((name) => name.startsWith("eval-"))
    .sort();

  for (const evalDirName of entries) {
    const evalDir = join(workspace, evalDirName);
    if (!statSync(evalDir).isDirectory()) continue;

    const metadataPath = join(evalDir, "eval_metadata.json");
    if (!existsSync(metadataPath)) continue;

    const metadataText = readFileSync(metadataPath, "utf-8");
    const metadata: EvalMetadata = JSON.parse(metadataText);

    // Look for config dirs (with_skill, without_skill) containing run dirs
    for (const configName of readdirSync(evalDir).sort()) {
      const configDir = join(evalDir, configName);
      if (!statSync(configDir).isDirectory()) continue;

      for (const runName of readdirSync(configDir).sort()) {
        const runDir = join(configDir, runName);
        if (!statSync(runDir).isDirectory()) continue;
        if (existsSync(join(runDir, "outputs"))) {
          runs.push({ runDir, metadata });
        }
      }
    }
  }

  return runs;
}

function buildGradingPrompt(runDir: string, metadata: EvalMetadata): string {
  return (
    "Grade this skill-eval run.\n" +
    "Read the transcript and outputs, then return JSON only.\n\n" +
    `Transcript path: ${join(runDir, "transcript.md")}\n` +
    `Outputs dir: ${join(runDir, "outputs")}\n` +
    `Expectations: ${JSON.stringify(metadata.expectations)}\n\n` +
    "Rules:\n" +
    "- PASS only with concrete evidence from transcript or outputs.\n" +
    "- FAIL if evidence is missing, contradicted, or superficial.\n" +
    "- Keep evidence concise and specific.\n" +
    "- Include claims only when they are real and inspectable.\n" +
    "- Keep eval_feedback suggestions high-signal only.\n" +
    "- Use these keys when possible: expectations, summary, claims, user_notes_summary, eval_feedback.\n"
  );
}

// ── Core grading ───────────────────────────────────────────────────────────

async function gradeWorkspace(
  workspace: string,
  model: string | undefined,
  force: boolean,
): Promise<void> {
  // workdir is 3 levels up from workspace (skills/pretext-workspace/iteration-N → repo root)
  const workdir = resolve(workspace, "..", "..", "..");

  for (const { runDir, metadata } of iterRuns(workspace)) {
    const gradingPath = join(runDir, "grading.json");
    if (existsSync(gradingPath) && !force) {
      continue;
    }

    const prompt = buildGradingPrompt(runDir, metadata);
    const start = performance.now();
    let raw = await runClaude(prompt, workdir, model);
    if (!raw.trim()) {
      raw = await runClaude(prompt, workdir, model);
    }
    await Bun.write(join(runDir, "grading_raw.txt"), raw);

    const grading = normalizeGrading(
      extractJsonObject(raw),
      metadata.expectations,
    ) as NormalizedGrading & {
      execution_metrics?: Record<string, unknown>;
      timing?: Record<string, number>;
    };
    const gradingDuration = (performance.now() - start) / 1000;

    // Load execution metrics and timing
    const metricsPath = join(runDir, "outputs", "metrics.json");
    const timingPath = join(runDir, "timing.json");

    const metrics: Record<string, unknown> = existsSync(metricsPath)
      ? JSON.parse(readFileSync(metricsPath, "utf-8"))
      : {};
    const timing: Record<string, number> = existsSync(timingPath)
      ? JSON.parse(readFileSync(timingPath, "utf-8"))
      : {};

    grading.execution_metrics = metrics;
    grading.timing = {
      executor_duration_seconds:
        timing.executor_duration_seconds ?? timing.total_duration_seconds ?? 0,
      grader_duration_seconds: Math.round(gradingDuration * 1000) / 1000,
      total_duration_seconds:
        Math.round(
          ((timing.total_duration_seconds ??
            timing.executor_duration_seconds ??
            0) +
            gradingDuration) *
            1000,
        ) / 1000,
    };

    await Bun.write(gradingPath, JSON.stringify(grading, null, 2) + "\n");
  }
}

// ── CLI ────────────────────────────────────────────────────────────────────

async function main(): Promise<number> {
  const { values } = parseArgs({
    options: {
      workspace: {
        type: "string",
        default: "skills/pretext-workspace/iteration-1",
      },
      model: { type: "string" },
      force: { type: "boolean", default: false },
    },
    strict: true,
  });

  const workspace = resolve(values.workspace!);
  await gradeWorkspace(workspace, values.model, values.force ?? false);
  console.log(`Grading written for ${workspace}`);
  return 0;
}

process.exit(await main());
