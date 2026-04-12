#!/usr/bin/env bun
/**
 * Infer a validation plan from git diff state or explicit file paths.
 *
 * Usage:
 *   # From git diff:
 *   bun run scripts/select-pretext-validation-from-git.ts --repo pretext --rev-range HEAD~1..HEAD
 *   bun run scripts/select-pretext-validation-from-git.ts --repo pretext --staged
 *
 *   # From explicit file paths:
 *   bun run scripts/select-pretext-validation-from-git.ts --path src/analysis.ts --path src/layout.ts
 */

import { existsSync } from "node:fs";
import { resolve, join } from "node:path";
import { parseArgs } from "node:util";

// ---------------------------------------------------------------------------
// Inline validation catalog
// ---------------------------------------------------------------------------

interface ValidationPlan {
  area: string;
  reason: string;
  commands: string[];
  follow_up_checks: string[];
}

interface FilePlan {
  areas: string[];
  reason: string;
  commands: string[];
  follow_up_checks: string[];
  matched_paths: string[];
}

const PLANS: Record<string, ValidationPlan> = {
  analysis: {
    area: "analysis",
    reason:
      "Segmentation, whitespace normalization, punctuation glue, locale-sensitive preprocessing.",
    commands: ["bun test", "bun run check"],
    follow_up_checks: [
      "bun run pre-wrap-check",
      "bun run accuracy-check",
      "bun run corpus-check",
    ],
  },
  measurement: {
    area: "measurement",
    reason:
      "Canvas measurement, engine profiling, emoji correction, grapheme-width derivation.",
    commands: ["bun test", "bun run check"],
    follow_up_checks: [
      "bun run benchmark-check",
      "bun run accuracy-check",
      "bun run probe-check",
    ],
  },
  "line-break": {
    area: "line-break",
    reason:
      "Arithmetic-only line walking, tabs, streamed lines, shrink-wrap geometry, break decisions.",
    commands: ["bun test", "bun run check"],
    follow_up_checks: [
      "bun run pre-wrap-check",
      "bun run accuracy-check",
      "bun run corpus-check",
    ],
  },
  "layout-api": {
    area: "layout-api",
    reason:
      "Public API orchestration, exported types, line materialization, prepare/layout consistency.",
    commands: [
      "bun test",
      "bun run check",
      "bun run build:package",
      "bun run package-smoke-test",
      "bun run skills/pretext/scripts/check-layout-api-sync.ts",
    ],
    follow_up_checks: ["bun run benchmark-check", "bun run accuracy-check"],
  },
  bidi: {
    area: "bidi",
    reason:
      "Rich-path bidi metadata and mixed-direction custom-rendering support.",
    commands: ["bun test", "bun run check"],
    follow_up_checks: ["bun run accuracy-check", "bun run corpus-check"],
  },
  "benchmark-harness": {
    area: "benchmark-harness",
    reason: "Prepare/layout benchmark methodology and status reporting.",
    commands: ["bun run benchmark-check", "bun run status-dashboard"],
    follow_up_checks: ["bun run benchmark-check:safari"],
  },
  "accuracy-harness": {
    area: "accuracy-harness",
    reason: "Browser-parity and whitespace-preservation oracles.",
    commands: ["bun run accuracy-check", "bun run pre-wrap-check"],
    follow_up_checks: [
      "bun run accuracy-check:safari",
      "bun run accuracy-check:firefox",
    ],
  },
  "probe-surface": {
    area: "probe-surface",
    reason:
      "Single-paragraph manual parity and visual-debugging harness.",
    commands: ["bun run probe-check", "bun run check"],
    follow_up_checks: ["bun run accuracy-check"],
  },
  "corpus-tooling": {
    area: "corpus-tooling",
    reason:
      "Representative corpus inspection, sweeps, and font-matrix analysis.",
    commands: ["bun run corpus-check", "bun run corpus-status"],
    follow_up_checks: [
      "bun run corpus-sweep",
      "bun run corpus-font-matrix",
    ],
  },
  "gatsby-surface": {
    area: "gatsby-surface",
    reason: "Long-form article parity against Gatsby-derived samples.",
    commands: ["bun run gatsby-check", "bun run corpus-status"],
    follow_up_checks: ["bun run gatsby-sweep", "bun run accuracy-check"],
  },
  "package-workflow": {
    area: "package-workflow",
    reason:
      "Published-artifact shape, build output, and consumer smoke tests.",
    commands: [
      "bun run check",
      "bun run build:package",
      "bun run package-smoke-test",
    ],
    follow_up_checks: [
      "bun run skills/pretext/scripts/check-layout-api-sync.ts",
    ],
  },
  "demo-site": {
    area: "demo-site",
    reason: "Demo pages and site assembly.",
    commands: ["bun run check", "bun run site:build"],
    follow_up_checks: [],
  },
  "reporting-tooling": {
    area: "reporting-tooling",
    reason:
      "Browser report capture, diagnostic page helpers, posted-report plumbing.",
    commands: ["bun run check", "bun run status-dashboard"],
    follow_up_checks: [
      "bun run accuracy-check",
      "bun run benchmark-check",
    ],
  },
};

const FILE_PATTERNS: [string, string][] = [
  ["src/analysis.ts", "analysis"],
  ["src/measurement.ts", "measurement"],
  ["src/line-break.ts", "line-break"],
  ["src/layout.ts", "layout-api"],
  ["src/layout.test.ts", "layout-api"],
  ["src/bidi.ts", "bidi"],
  ["README.md", "layout-api"],
  ["DEVELOPMENT.md", "layout-api"],
  ["RESEARCH.md", "layout-api"],
  ["STATUS.md", "benchmark-harness"],
  ["pages/benchmark.ts", "benchmark-harness"],
  ["pages/benchmark.html", "benchmark-harness"],
  ["scripts/benchmark-check.ts", "benchmark-harness"],
  ["scripts/status-dashboard.ts", "benchmark-harness"],
  ["pages/accuracy.ts", "accuracy-harness"],
  ["pages/accuracy.html", "accuracy-harness"],
  ["scripts/browser-automation.ts", "accuracy-harness"],
  ["scripts/accuracy-check.ts", "accuracy-harness"],
  ["scripts/pre-wrap-check.ts", "accuracy-harness"],
  ["pages/probe.ts", "probe-surface"],
  ["pages/probe.html", "probe-surface"],
  ["scripts/probe-check.ts", "probe-surface"],
  ["pages/corpus.ts", "corpus-tooling"],
  ["pages/corpus.html", "corpus-tooling"],
  ["scripts/corpus-check.ts", "corpus-tooling"],
  ["scripts/corpus-sweep.ts", "corpus-tooling"],
  ["scripts/corpus-font-matrix.ts", "corpus-tooling"],
  ["scripts/corpus-status.ts", "corpus-tooling"],
  ["scripts/corpus-representative.ts", "corpus-tooling"],
  ["scripts/corpus-taxonomy.ts", "corpus-tooling"],
  ["pages/gatsby.ts", "gatsby-surface"],
  ["pages/gatsby.html", "gatsby-surface"],
  ["scripts/gatsby-check.ts", "gatsby-surface"],
  ["scripts/gatsby-sweep.ts", "gatsby-surface"],
  ["scripts/package-smoke-test.ts", "package-workflow"],
  ["package.json", "package-workflow"],
  ["tsconfig.build.json", "package-workflow"],
  ["CHANGELOG.md", "package-workflow"],
  ["scripts/build-demo-site.ts", "demo-site"],
  ["scripts/report-server.ts", "reporting-tooling"],
  ["pages/report-utils.ts", "reporting-tooling"],
  ["pages/diagnostic-utils.ts", "reporting-tooling"],
  ["pages/emoji-test.html", "accuracy-harness"],
  ["pages/demos/*", "demo-site"],
  ["pages/assets/*", "demo-site"],
  ["pages/*.html", "demo-site"],
];

// ---------------------------------------------------------------------------
// Simple fnmatch-style glob matching (handles * wildcards)
// ---------------------------------------------------------------------------

function fnmatch(path: string, pattern: string): boolean {
  // Convert glob pattern to regex: escape special regex chars, then replace * with .*
  const regexStr =
    "^" +
    pattern
      .replace(/[.+^${}()|[\]\\]/g, "\\$&")
      .replace(/\*/g, "[^/]*") +
    "$";
  return new RegExp(regexStr).test(path);
}

// ---------------------------------------------------------------------------
// File-path matching
// ---------------------------------------------------------------------------

function normalize(path: string): string {
  return path.replace(/\\/g, "/").trim();
}

function removePrefix(str: string, prefix: string): string {
  return str.startsWith(prefix) ? str.slice(prefix.length) : str;
}

function matchesPattern(path: string, pattern: string): boolean {
  const normalizedPath = normalize(path);
  const normalizedPattern = normalize(pattern);

  const candidates = [normalizedPath, removePrefix(normalizedPath, "pretext/")];
  const patterns = [normalizedPattern, removePrefix(normalizedPattern, "pretext/")];

  for (const candidate of candidates) {
    for (const candidatePattern of patterns) {
      if (candidatePattern.includes("*") && fnmatch(candidate, candidatePattern)) {
        return true;
      }
      if (candidatePattern.includes("/")) {
        if (candidate.endsWith(candidatePattern)) {
          return true;
        }
      } else if (candidate === candidatePattern) {
        return true;
      }
    }
  }
  return false;
}

function planForPaths(paths: string[]): FilePlan {
  const matchedPaths: string[] = [];
  const areas: string[] = [];

  for (const rawPath of paths) {
    const path = normalize(rawPath);
    for (const [pattern, area] of FILE_PATTERNS) {
      if (matchesPattern(path, pattern)) {
        matchedPaths.push(path);
        if (!areas.includes(area)) {
          areas.push(area);
        }
        break;
      }
    }
  }

  if (areas.length === 0) {
    return {
      areas: [],
      reason:
        "No known subsystem mapping matched. Fall back to manual area selection.",
      commands: [],
      follow_up_checks: [],
      matched_paths: [],
    };
  }

  const commands: string[] = [];
  const followUpChecks: string[] = [];

  for (const area of areas) {
    const plan = PLANS[area];
    for (const cmd of plan.commands) {
      if (!commands.includes(cmd)) {
        commands.push(cmd);
      }
    }
    for (const chk of plan.follow_up_checks) {
      if (!followUpChecks.includes(chk)) {
        followUpChecks.push(chk);
      }
    }
  }

  return {
    areas,
    reason: "Validation scope inferred from changed subsystem ownership.",
    commands,
    follow_up_checks: followUpChecks,
    matched_paths: matchedPaths,
  };
}

// ---------------------------------------------------------------------------
// Git integration
// ---------------------------------------------------------------------------

function looksLikePretextRepo(repoPath: string): boolean {
  return (
    existsSync(join(repoPath, ".git")) &&
    existsSync(join(repoPath, "src", "layout.ts"))
  );
}

function resolveRepo(repo: string | undefined): string {
  if (repo) {
    return resolve(repo);
  }
  const cwd = resolve(process.cwd());

  const candidates: string[] = [cwd];
  // Walk up parents and check for <parent>/pretext
  let current = cwd;
  while (true) {
    candidates.push(join(current, "pretext"));
    const parent = resolve(current, "..");
    if (parent === current) break; // reached root
    current = parent;
    candidates.push(join(current, "pretext"));
  }

  const seen = new Set<string>();
  for (const candidate of candidates) {
    if (seen.has(candidate)) continue;
    seen.add(candidate);
    if (looksLikePretextRepo(candidate)) {
      return candidate;
    }
  }
  return cwd;
}

async function runGitDiff(
  repoRoot: string,
  staged: boolean,
  revRange: string | undefined,
): Promise<string[]> {
  const cmd = ["git", "diff", "--name-only", "--relative"];
  if (staged) cmd.push("--staged");
  if (revRange) cmd.push(revRange);

  const proc = Bun.spawn(cmd, {
    cwd: repoRoot,
    stdout: "pipe",
    stderr: "pipe",
  });

  const [stdout, stderr] = await Promise.all([
    new Response(proc.stdout).text(),
    new Response(proc.stderr).text(),
  ]);

  const exitCode = await proc.exited;

  if (exitCode !== 0) {
    throw new Error(stderr.trim() || "git diff failed");
  }

  return stdout
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
}

async function collectChangedPaths(
  repoRoot: string,
  mode: string,
  revRange: string | undefined,
): Promise<string[]> {
  if (revRange) {
    return runGitDiff(repoRoot, false, revRange);
  }
  if (mode === "staged") {
    return runGitDiff(repoRoot, true, undefined);
  }
  if (mode === "working-tree") {
    return runGitDiff(repoRoot, false, undefined);
  }

  // mode === "all": merge working-tree + staged
  const merged: string[] = [];
  for (const path of await runGitDiff(repoRoot, false, undefined)) {
    if (!merged.includes(path)) {
      merged.push(path);
    }
  }
  for (const path of await runGitDiff(repoRoot, true, undefined)) {
    if (!merged.includes(path)) {
      merged.push(path);
    }
  }
  return merged;
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------

function renderJson(plan: FilePlan): string {
  return JSON.stringify(plan, null, 2);
}

function renderText(plan: FilePlan): string {
  const lines: string[] = [
    `Areas: ${plan.areas.length > 0 ? plan.areas.join(", ") : "(unmatched)"}`,
    `Reason: ${plan.reason}`,
    "Matched paths:",
  ];

  if (plan.matched_paths.length > 0) {
    for (const p of plan.matched_paths) {
      lines.push(`- ${p}`);
    }
  } else {
    lines.push("- (none)");
  }

  lines.push("Commands:");
  if (plan.commands.length > 0) {
    for (const c of plan.commands) {
      lines.push(`- ${c}`);
    }
  } else {
    lines.push("- (none)");
  }

  lines.push("Follow-up checks:");
  if (plan.follow_up_checks.length > 0) {
    for (const c of plan.follow_up_checks) {
      lines.push(`- ${c}`);
    }
  } else {
    lines.push("- (none)");
  }

  return lines.join("\n");
}

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

async function main(): Promise<number> {
  let parsed: ReturnType<typeof parseArgs>;
  try {
    parsed = parseArgs({
      args: Bun.argv.slice(2),
      options: {
        repo: { type: "string" },
        path: { type: "string", multiple: true },
        "working-tree": { type: "boolean", default: false },
        staged: { type: "boolean", default: false },
        all: { type: "boolean", default: false },
        "rev-range": { type: "string" },
        format: { type: "string", default: "text" },
        help: { type: "boolean", default: false },
      },
      strict: true,
    });
  } catch (err: any) {
    console.error(`Error: ${err.message}`);
    console.error(
      "Usage: bun run select-pretext-validation-from-git.ts [--repo DIR] [--path FILE ...] [--working-tree|--staged|--all] [--rev-range RANGE] [--format text|json]",
    );
    return 1;
  }

  const {
    values: {
      repo,
      path: explicitPaths,
      "working-tree": workingTree,
      staged,
      all,
      "rev-range": revRange,
      format: outputFormat,
      help,
    },
  } = parsed;

  if (help) {
    console.log(
      "Infer a Pretext validation plan from git diff state or explicit file paths.\n\n" +
        "Options:\n" +
        "  --repo DIR            Repository root (auto-detected if omitted)\n" +
        "  --path FILE           Explicit changed file path (repeat for multiple)\n" +
        "  --working-tree        Show only unstaged changes\n" +
        "  --staged              Show only staged changes\n" +
        "  --all                 Show staged + unstaged changes (default)\n" +
        "  --rev-range RANGE     Git diff revision range (e.g. HEAD~1..HEAD)\n" +
        "  --format text|json    Output format (default: text)\n" +
        "  --help                Show this help message",
    );
    return 0;
  }

  // Validate format
  if (outputFormat && outputFormat !== "text" && outputFormat !== "json") {
    console.error(`Error: --format must be "text" or "json", got "${outputFormat}"`);
    return 1;
  }

  // Validate mutually exclusive mode flags
  const modeFlags = [workingTree, staged, all].filter(Boolean).length;
  if (modeFlags > 1) {
    console.error(
      "Error: --working-tree, --staged, and --all are mutually exclusive.",
    );
    return 1;
  }

  const fmt = (outputFormat as string) || "text";

  // Explicit paths mode
  if (explicitPaths && explicitPaths.length > 0) {
    const plan = planForPaths(explicitPaths);
    console.log(fmt === "json" ? renderJson(plan) : renderText(plan));
    return 0;
  }

  // Git diff mode
  let mode = "all";
  if (workingTree) {
    mode = "working-tree";
  } else if (staged) {
    mode = "staged";
  }

  if (revRange && mode !== "all") {
    console.error(
      "Error: --rev-range cannot be combined with --working-tree or --staged.",
    );
    return 1;
  }

  const repoRoot = resolveRepo(repo);

  let changedPaths: string[];
  try {
    changedPaths = await collectChangedPaths(repoRoot, mode, revRange);
  } catch (err: any) {
    console.error(err.message);
    return 1;
  }

  if (changedPaths.length === 0) {
    const empty: FilePlan = {
      areas: [],
      reason: "No changed files in git diff state.",
      commands: [],
      follow_up_checks: [],
      matched_paths: [],
    };
    console.log(fmt === "json" ? renderJson(empty) : renderText(empty));
    return 0;
  }

  const plan = planForPaths(changedPaths);
  console.log(fmt === "json" ? renderJson(plan) : renderText(plan));
  return 0;
}

process.exit(await main());
