#!/usr/bin/env bun
/**
 * Check whether the formal eval suite covers all supported goals, surfaces,
 * and validation areas.
 *
 * Usage:
 *   bun run skills/pretext/scripts/check-pretext-eval-coverage.ts
 *
 * Exit code 0 if in sync, 1 if mismatches found.
 */

import { resolve, join } from "node:path";

// ── Inline catalog: the 13 validation areas (matching select-pretext-validation-from-git) ──

const VALIDATION_AREAS = [
  "analysis",
  "measurement",
  "line-break",
  "layout-api",
  "bidi",
  "benchmark-harness",
  "accuracy-harness",
  "probe-surface",
  "corpus-tooling",
  "gatsby-surface",
  "package-workflow",
  "demo-site",
  "reporting-tooling",
] as const;

// ── Types ──────────────────────────────────────────────────────────────────

interface EvalsData {
  evals: { id: number; [key: string]: unknown }[];
}

interface CoverageData {
  goals: Record<string, number[]>;
  surfaces: Record<string, number[]>;
  validation_areas?: Record<string, number[]>;
  [key: string]: unknown;
}

// ── Helpers ────────────────────────────────────────────────────────────────

/** Collect all eval IDs referenced in a category map, checking for unknown IDs. */
function collectMissingIds(
  categoryMap: Record<string, number[]> | undefined,
  validIds: Set<number>,
  missingIds: number[],
): void {
  if (!categoryMap) return;
  for (const ids of Object.values(categoryMap)) {
    for (const evalId of ids) {
      if (!validIds.has(evalId) && !missingIds.includes(evalId)) {
        missingIds.push(evalId);
      }
    }
  }
}

function reportList(header: string, items: string[]): void {
  if (items.length === 0) return;
  console.log(header);
  for (const item of items) {
    console.log(`- ${item}`);
  }
}

// ── Main ───────────────────────────────────────────────────────────────────

async function main(): Promise<number> {
  // import.meta.dir → …/skills/pretext/scripts  →  3 parents up = repo root
  const repoRoot = resolve(import.meta.dir, "..", "..", "..");

  const evalsPath = join(repoRoot, "skills", "pretext", "evals", "evals.json");
  const coveragePath = join(repoRoot, "skills", "pretext", "evals", "coverage.json");

  const evalsData: EvalsData = await Bun.file(evalsPath).json();
  const coverageData: CoverageData = await Bun.file(coveragePath).json();

  const evalIds = new Set(evalsData.evals.map((e) => e.id));

  // ── Check for unknown eval IDs in coverage ──
  const missingEvalIds: number[] = [];
  collectMissingIds(coverageData.goals, evalIds, missingEvalIds);
  collectMissingIds(coverageData.surfaces, evalIds, missingEvalIds);
  collectMissingIds(coverageData.validation_areas, evalIds, missingEvalIds);

  // ── Check for missing / empty goals ──
  const goalKeys = Object.keys(coverageData.goals);
  // Goals are user-defined; we just check that the coverage file has them and they're non-empty.
  const emptyGoals = goalKeys.filter((g) => !coverageData.goals[g]?.length);

  // ── Check for missing / empty surfaces ──
  const surfaceKeys = Object.keys(coverageData.surfaces);
  const emptySurfaces = surfaceKeys.filter((s) => !coverageData.surfaces[s]?.length);

  // ── Check for missing / empty validation areas ──
  const coveredValidation = coverageData.validation_areas ?? {};
  const missingValidationAreas = VALIDATION_AREAS.filter(
    (area) => !(area in coveredValidation),
  );
  const emptyValidationAreas = VALIDATION_AREAS.filter(
    (area) => area in coveredValidation && !coveredValidation[area]?.length,
  );

  // ── Verdict ──
  const allClear =
    emptyGoals.length === 0 &&
    emptySurfaces.length === 0 &&
    missingValidationAreas.length === 0 &&
    emptyValidationAreas.length === 0 &&
    missingEvalIds.length === 0;

  if (allClear) {
    console.log(
      "Eval coverage is in sync with goals, surfaces, and validation areas.",
    );
    return 0;
  }

  reportList("Goals without mapped evals:", emptyGoals);
  reportList("Surfaces without mapped evals:", emptySurfaces);
  reportList("Missing validation areas in coverage.json:", missingValidationAreas);
  reportList("Validation areas without mapped evals:", emptyValidationAreas);

  if (missingEvalIds.length > 0) {
    console.log("Coverage references unknown eval IDs:");
    for (const id of missingEvalIds.sort((a, b) => a - b)) {
      console.log(`- ${id}`);
    }
  }

  return 1;
}

process.exit(await main());
