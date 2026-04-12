#!/usr/bin/env bun
/**
 * Analyze whether a benchmark meaningfully discriminates between with-skill
 * and baseline runs.
 *
 * Usage:
 *   bun run skills/pretext/scripts/analyze-pretext-benchmark.ts --benchmark path/to/benchmark.json
 *   bun run skills/pretext/scripts/analyze-pretext-benchmark.ts --benchmark b.json --format json
 *   bun run skills/pretext/scripts/analyze-pretext-benchmark.ts --benchmark b.json --delta-threshold 0.15
 */

import { resolve } from "node:path";
import { parseArgs } from "node:util";
import { existsSync, readFileSync } from "node:fs";

// ── Types ──────────────────────────────────────────────────────────────────

interface EvalObservation {
  eval_id: number;
  eval_role: string | null;
  with_skill_pass_rate: number;
  baseline_pass_rate: number;
  delta: number;
  classification: string;
  recommendation: string;
}

interface BenchmarkRun {
  eval_id: number;
  configuration: string;
  result: { pass_rate: number | string; [key: string]: unknown };
  [key: string]: unknown;
}

interface BenchmarkData {
  runs?: BenchmarkRun[];
  [key: string]: unknown;
}

interface CoverageData {
  eval_roles?: Record<string, number[]>;
  [key: string]: unknown;
}

// ── Classification ─────────────────────────────────────────────────────────

function classifyDelta(
  withSkill: number,
  baseline: number,
  deltaThreshold: number,
  evalRole: string | null,
): { classification: string; recommendation: string } {
  const delta = withSkill - baseline;

  if (
    Math.abs(delta) < deltaThreshold &&
    withSkill >= 0.95 &&
    baseline >= 0.95
  ) {
    if (evalRole === "smoke") {
      return {
        classification: "non_discriminating_success",
        recommendation:
          "Expected for a smoke test: both configurations succeed, so treat this as capability confirmation rather than a benchmark gate.",
      };
    }
    return {
      classification: "non_discriminating_success",
      recommendation:
        "Treat this eval as a smoke test. It currently does not distinguish the skill from baseline.",
    };
  }

  if (
    Math.abs(delta) < deltaThreshold &&
    withSkill <= 0.05 &&
    baseline <= 0.05
  ) {
    return {
      classification: "non_discriminating_failure",
      recommendation:
        "Both configurations fail. Tighten the route, prompt, or harness before treating this as a benchmark gate.",
    };
  }

  if (delta < -deltaThreshold) {
    return {
      classification: "regression_candidate",
      recommendation:
        "Baseline outperforms the skill here. Inspect the skill answer, not just the benchmark summary.",
    };
  }

  if (delta < deltaThreshold) {
    return {
      classification: "weak_signal",
      recommendation:
        "The eval distinguishes weakly at best. Consider whether the prompt is too easy or too broad.",
    };
  }

  return {
    classification: "discriminating_positive",
    recommendation:
      evalRole !== "smoke"
        ? "The eval meaningfully distinguishes the skill from baseline and is suitable as a benchmark gate."
        : "The eval distinguishes positively, but its role is still marked as smoke; decide whether it should be promoted to a gate.",
  };
}

// ── Eval roles ─────────────────────────────────────────────────────────────

function loadEvalRoles(coveragePath: string | null): Map<number, string> {
  if (!coveragePath) return new Map();
  const coverage: CoverageData = JSON.parse(
    readFileSync(coveragePath, "utf-8"),
  );
  const mapping = new Map<number, string>();
  for (const [role, ids] of Object.entries(coverage.eval_roles ?? {})) {
    for (const evalId of ids) {
      mapping.set(evalId, role);
    }
  }
  return mapping;
}

// ── Core analysis ──────────────────────────────────────────────────────────

function analyzeBenchmark(
  benchmark: BenchmarkData,
  deltaThreshold: number,
  evalRoles: Map<number, string>,
): EvalObservation[] {
  const grouped = new Map<number, Map<string, number>>();

  for (const run of benchmark.runs ?? []) {
    const evalId = run.eval_id;
    const config = run.configuration;
    const passRate = Number(run.result.pass_rate);

    if (!grouped.has(evalId)) {
      grouped.set(evalId, new Map());
    }
    grouped.get(evalId)!.set(config, passRate);
  }

  const observations: EvalObservation[] = [];
  const sortedIds = [...grouped.keys()].sort((a, b) => a - b);

  for (const evalId of sortedIds) {
    const configs = grouped.get(evalId)!;
    const withSkill = configs.get("with_skill");
    const baseline = configs.get("without_skill");

    if (withSkill === undefined || baseline === undefined) continue;

    const evalRole = evalRoles.get(evalId) ?? null;
    const { classification, recommendation } = classifyDelta(
      withSkill,
      baseline,
      deltaThreshold,
      evalRole,
    );

    observations.push({
      eval_id: evalId,
      eval_role: evalRole,
      with_skill_pass_rate: withSkill,
      baseline_pass_rate: baseline,
      delta: Math.round((withSkill - baseline) * 10000) / 10000,
      classification,
      recommendation,
    });
  }

  return observations;
}

// ── CLI ────────────────────────────────────────────────────────────────────

async function main(): Promise<number> {
  const { values } = parseArgs({
    options: {
      benchmark: { type: "string" },
      coverage: {
        type: "string",
        default: "skills/pretext/evals/coverage.json",
      },
      "delta-threshold": { type: "string", default: "0.1" },
      format: { type: "string", default: "text" },
    },
    strict: true,
  });

  if (!values.benchmark) {
    console.error("Error: --benchmark is required.");
    process.exit(1);
  }

  const benchmarkPath = resolve(values.benchmark);
  const benchmark: BenchmarkData = await Bun.file(benchmarkPath).json();

  const coveragePath = values.coverage ? resolve(values.coverage) : null;
  const evalRoles =
    coveragePath && existsSync(coveragePath)
      ? loadEvalRoles(coveragePath)
      : new Map<number, string>();

  const deltaThreshold = parseFloat(values["delta-threshold"]!);
  const observations = analyzeBenchmark(benchmark, deltaThreshold, evalRoles);

  if (values.format === "json") {
    const payload = {
      benchmark: benchmarkPath,
      coverage:
        coveragePath && existsSync(coveragePath) ? coveragePath : null,
      delta_threshold: deltaThreshold,
      observations,
    };
    console.log(JSON.stringify(payload, null, 2));
    return 0;
  }

  // Text output
  console.log(`Benchmark: ${benchmarkPath}`);
  if (coveragePath && existsSync(coveragePath)) {
    console.log(`Coverage: ${coveragePath}`);
  }
  console.log(`Delta threshold: ${deltaThreshold}`);
  console.log("Observations:");

  if (observations.length === 0) {
    console.log("- (none)");
    return 0;
  }

  for (const item of observations) {
    console.log(
      `- eval ${item.eval_id}: ${item.classification} ` +
        `(role=${item.eval_role ?? "untyped"}, ` +
        `with_skill=${item.with_skill_pass_rate.toFixed(2)}, ` +
        `baseline=${item.baseline_pass_rate.toFixed(2)}, ` +
        `delta=${item.delta >= 0 ? "+" : ""}${item.delta.toFixed(2)})`,
    );
    console.log(`  recommendation: ${item.recommendation}`);
  }

  return 0;
}

process.exit(await main());
