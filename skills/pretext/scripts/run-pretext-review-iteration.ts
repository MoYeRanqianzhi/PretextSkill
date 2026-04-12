#!/usr/bin/env bun
/**
 * Run one review iteration for the Pretext skill using Claude CLI.
 *
 * Usage:
 *   bun run skills/pretext/scripts/run-pretext-review-iteration.ts
 *   bun run skills/pretext/scripts/run-pretext-review-iteration.ts --eval-id 1 --eval-id 5
 *   bun run skills/pretext/scripts/run-pretext-review-iteration.ts --model claude-sonnet-4-20250514
 */

import { resolve, join } from "node:path";
import { parseArgs } from "node:util";
import { mkdirSync, existsSync } from "node:fs";

// ── Constants ──────────────────────────────────────────────────────────────

const DEFAULT_EVAL_IDS = [1, 4, 5, 8, 9, 11, 24];

// ── Types ──────────────────────────────────────────────────────────────────

interface EvalItem {
  evalId: number;
  prompt: string;
  expectedOutput: string;
  expectations: string[];
}

interface EvalsData {
  evals: {
    id: number;
    prompt: string;
    expected_output: string;
    expectations: string[];
  }[];
}

// ── Helpers ────────────────────────────────────────────────────────────────

function slugify(text: string, limit = 48): string {
  const slug = text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");
  if (!slug) return "eval";
  return slug.slice(0, limit).replace(/-$/, "");
}

function loadEvals(data: EvalsData): Map<number, EvalItem> {
  const mapping = new Map<number, EvalItem>();
  for (const item of data.evals) {
    mapping.set(item.id, {
      evalId: item.id,
      prompt: item.prompt,
      expectedOutput: item.expected_output,
      expectations: item.expectations,
    });
  }
  return mapping;
}

function buildPrompt(evalItem: EvalItem, skillPath: string | null): string {
  const shared =
    "Answer the task in concise technical Markdown.\n" +
    "State the chosen route explicitly when relevant.\n" +
    "Do not mention this evaluation harness.\n\n" +
    `Task:\n${evalItem.prompt}\n`;

  if (skillPath === null) {
    return (
      "You are answering a technical task directly without any external skill instructions.\n\n" +
      shared
    );
  }

  const skillMdPath = join(skillPath, "SKILL.md");
  return (
    "You are evaluating a local Claude-style skill.\n" +
    `Skill path: ${skillPath}\n\n` +
    "Required process:\n" +
    `1. Read ${skillMdPath} first.\n` +
    "2. Follow the skill faithfully.\n" +
    "3. Load only the minimum referenced files needed for the task.\n" +
    "4. Answer the task directly.\n\n" +
    shared
  );
}

async function runClaude(
  prompt: string,
  workdir: string,
  model: string | undefined,
): Promise<{ stdout: string; stderr: string; exitCode: number; elapsed: number }> {
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

  // Filter out CLAUDECODE env var
  const env: Record<string, string> = {};
  for (const [k, v] of Object.entries(process.env)) {
    if (k !== "CLAUDECODE" && v !== undefined) {
      env[k] = v;
    }
  }

  const start = performance.now();
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
  const elapsed = (performance.now() - start) / 1000;

  return { stdout, stderr, exitCode, elapsed };
}

async function writeJson(path: string, payload: unknown): Promise<void> {
  await Bun.write(path, JSON.stringify(payload, null, 2) + "\n");
}

// ── Core iteration ─────────────────────────────────────────────────────────

async function runIteration(
  evalSetPath: string,
  skillPath: string,
  workspace: string,
  evalIds: number[],
  model: string | undefined,
): Promise<void> {
  const evalsData: EvalsData = await Bun.file(evalSetPath).json();
  const evals = loadEvals(evalsData);

  mkdirSync(workspace, { recursive: true });

  const history = {
    iteration: workspace.split(/[\\/]/).pop(),
    skill_path: skillPath,
    eval_ids: evalIds,
    started_at_epoch: Date.now() / 1000,
  };
  await writeJson(join(workspace, "iteration_metadata.json"), history);

  // Resolve repo root from skill path (skill_path is …/skills/pretext → 2 parents up)
  const repoRoot = resolve(skillPath, "..", "..");

  for (const evalId of evalIds) {
    const item = evals.get(evalId);
    if (!item) {
      throw new Error(`Unknown eval id ${evalId}`);
    }

    const evalSlug = slugify(item.expectedOutput);
    const evalDir = join(workspace, `eval-${String(evalId).padStart(2, "0")}-${evalSlug}`);
    mkdirSync(evalDir, { recursive: true });

    await writeJson(join(evalDir, "eval_metadata.json"), {
      eval_id: item.evalId,
      eval_name: `eval-${String(item.evalId).padStart(2, "0")}-${evalSlug}`,
      prompt: item.prompt,
      expectations: item.expectations,
      expected_output: item.expectedOutput,
    });

    const configs: [string, string | null][] = [
      ["with_skill", skillPath],
      ["without_skill", null],
    ];

    for (const [configName, configSkillPath] of configs) {
      const runDir = join(evalDir, configName, "run-1");
      const outputsDir = join(runDir, "outputs");
      mkdirSync(outputsDir, { recursive: true });

      const prompt = buildPrompt(item, configSkillPath);
      const { stdout, stderr, exitCode, elapsed } = await runClaude(
        prompt,
        repoRoot,
        model,
      );
      let answer = stdout.trim();
      if (exitCode !== 0 && !answer) {
        answer = `Execution failed with return code ${exitCode}.\n\n${stderr.trim()}`;
      }

      const transcript =
        `# Eval Transcript\n\n` +
        `## Eval Prompt\n\n${item.prompt}\n\n` +
        `## Harness Prompt\n\n\`\`\`\n${prompt}\n\`\`\`\n\n` +
        `## Result\n\n${exitCode}\n\n` +
        `## Stdout\n\n${answer}\n\n` +
        `## Stderr\n\n${stderr.trim()}\n`;

      await Bun.write(
        join(outputsDir, "answer.md"),
        answer + (answer.endsWith("\n") ? "" : "\n"),
      );
      await Bun.write(join(runDir, "transcript.md"), transcript);
      await Bun.write(
        join(outputsDir, "user_notes.md"),
        `- configuration: \`${configName}\`\n` +
          `- skill_path: \`${configSkillPath}\`\n` +
          `- return_code: \`${exitCode}\`\n`,
      );
      await writeJson(join(outputsDir, "metrics.json"), {
        tool_calls: {},
        total_tool_calls: 0,
        total_steps: 0,
        files_created: ["answer.md"],
        errors_encountered: exitCode === 0 ? 0 : 1,
        output_chars: answer.length,
        transcript_chars: transcript.length,
      });
      await writeJson(join(runDir, "timing.json"), {
        total_tokens: 0,
        duration_ms: Math.round(elapsed * 1000),
        total_duration_seconds: Math.round(elapsed * 1000) / 1000,
        executor_duration_seconds: Math.round(elapsed * 1000) / 1000,
      });
    }
  }
}

// ── CLI ────────────────────────────────────────────────────────────────────

async function main(): Promise<number> {
  const { values } = parseArgs({
    options: {
      "eval-set": { type: "string", default: "skills/pretext/evals/evals.json" },
      "skill-path": { type: "string", default: "skills/pretext" },
      workspace: { type: "string", default: "skills/pretext-workspace/iteration-1" },
      "eval-id": { type: "string", multiple: true },
      model: { type: "string" },
    },
    strict: true,
  });

  const evalIds =
    values["eval-id"] && values["eval-id"].length > 0
      ? values["eval-id"].map((id) => parseInt(id, 10))
      : DEFAULT_EVAL_IDS;

  const evalSetPath = resolve(values["eval-set"]!);
  const skillPath = resolve(values["skill-path"]!);
  const workspace = resolve(values.workspace!);

  await runIteration(evalSetPath, skillPath, workspace, evalIds, values.model);
  console.log(`Review iteration written to ${workspace}`);
  return 0;
}

process.exit(await main());
