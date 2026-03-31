#!/usr/bin/env python3
"""Recommend the upstream tooling surface for a Pretext task."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


SUPPORTED_TOOLING_AREAS = [
    "accuracy-harness",
    "benchmark-harness",
    "probe-surface",
    "corpus-tooling",
    "gatsby-surface",
    "reporting-tooling",
    "demo-site",
    "package-workflow",
]


@dataclass(frozen=True)
class ToolingSurfaceRecommendation:
    area: str
    reason: str
    main_question: str
    primary_files: list[str]
    reference_files: list[str]
    validation_area: str
    notes: list[str]


CATALOG: dict[str, ToolingSurfaceRecommendation] = {
    "accuracy-harness": ToolingSurfaceRecommendation(
        area="accuracy-harness",
        reason="Use the broad browser-parity and snapshot-regression harness when the issue spans many rows or maintained browser snapshots.",
        main_question="Does the engine still match browser layout across the maintained accuracy snapshot set?",
        primary_files=[
            "pretext/pages/accuracy.ts",
            "pretext/scripts/accuracy-check.ts",
            "pretext/scripts/pre-wrap-check.ts",
        ],
        reference_files=[
            "reference/upstream-tooling-surfaces.md",
            "reference/validation-playbook.md",
            "reference/script-and-browser-caveats.md",
        ],
        validation_area="accuracy-harness",
        notes=[
            "Prefer this over probe-surface when the question is broad parity, not one concrete mismatch.",
            "If the issue is one paragraph only, switch to probe-surface.",
        ],
    ),
    "benchmark-harness": ToolingSurfaceRecommendation(
        area="benchmark-harness",
        reason="Use the benchmark harness when the task is about throughput, analysis-vs-measure split, or benchmark snapshot methodology.",
        main_question="Did performance or benchmark reporting move, and where did the time go?",
        primary_files=[
            "pretext/pages/benchmark.ts",
            "pretext/scripts/benchmark-check.ts",
            "pretext/scripts/status-dashboard.ts",
        ],
        reference_files=[
            "reference/upstream-tooling-surfaces.md",
            "reference/validation-playbook.md",
            "reference/troubleshooting.md",
        ],
        validation_area="benchmark-harness",
        notes=[
            "Use this when prepare/layout cost or benchmark JSON snapshots are the core concern.",
            "If the task is only package confidence, switch to package-workflow.",
        ],
    ),
    "probe-surface": ToolingSurfaceRecommendation(
        area="probe-surface",
        reason="Use the probe surface when a single text case needs exact line and break diagnostics.",
        main_question="Where is the first concrete mismatch for this one text case?",
        primary_files=[
            "pretext/pages/probe.ts",
            "pretext/scripts/probe-check.ts",
            "pretext/pages/diagnostic-utils.ts",
        ],
        reference_files=[
            "reference/upstream-tooling-surfaces.md",
            "reference/validation-playbook.md",
            "reference/behavior-contracts.md",
        ],
        validation_area="probe-surface",
        notes=[
            "Prefer this over broad accuracy or corpus sweeps when the repro is narrow.",
            "If the issue is only about expected semantics, start with behavior contracts first.",
        ],
    ),
    "corpus-tooling": ToolingSurfaceRecommendation(
        area="corpus-tooling",
        reason="Use corpus tooling for representative long-form documents, width sweeps, font matrices, and corpus taxonomy work.",
        main_question="How does the engine behave across representative long-form corpora?",
        primary_files=[
            "pretext/pages/corpus.ts",
            "pretext/scripts/corpus-check.ts",
            "pretext/scripts/corpus-sweep.ts",
            "pretext/scripts/corpus-font-matrix.ts",
            "pretext/scripts/corpus-status.ts",
            "pretext/scripts/corpus-taxonomy.ts",
        ],
        reference_files=[
            "reference/upstream-tooling-surfaces.md",
            "reference/validation-playbook.md",
            "reference/script-and-browser-caveats.md",
        ],
        validation_area="corpus-tooling",
        notes=[
            "Use this when a long-form sample or representative corpus row is the maintained steering surface.",
            "If the issue is only the Gatsby slice, the Gatsby area may be narrower.",
        ],
    ),
    "gatsby-surface": ToolingSurfaceRecommendation(
        area="gatsby-surface",
        reason="Use the Gatsby slice when the maintained long-form target is specifically the Gatsby compatibility path.",
        main_question="Does the Gatsby reference slice still behave like the maintained long-form compatibility target?",
        primary_files=[
            "pretext/pages/gatsby.ts",
            "pretext/scripts/gatsby-check.ts",
            "pretext/scripts/gatsby-sweep.ts",
        ],
        reference_files=[
            "reference/upstream-tooling-surfaces.md",
            "reference/validation-playbook.md",
            "reference/script-and-browser-caveats.md",
        ],
        validation_area="gatsby-surface",
        notes=[
            "Prefer this over generic corpus work when the task explicitly references Gatsby.",
            "If the question broadens beyond Gatsby, switch back to corpus-tooling.",
        ],
    ),
    "reporting-tooling": ToolingSurfaceRecommendation(
        area="reporting-tooling",
        reason="Use reporting tooling when report posting, report hashing, dashboard helpers, or diagnostic page transport is the real concern.",
        main_question="Is the reporting pipeline itself correct, independent of engine semantics?",
        primary_files=[
            "pretext/scripts/report-server.ts",
            "pretext/pages/report-utils.ts",
            "pretext/pages/diagnostic-utils.ts",
        ],
        reference_files=[
            "reference/upstream-tooling-surfaces.md",
            "reference/validation-playbook.md",
        ],
        validation_area="reporting-tooling",
        notes=[
            "Do not confuse report transport failures with layout-engine correctness failures.",
            "If the issue is the content of one probe or accuracy report, the relevant harness area may still be narrower.",
        ],
    ),
    "demo-site": ToolingSurfaceRecommendation(
        area="demo-site",
        reason="Use the demo-site area for demo page behavior, static site build, and human-facing example presentation.",
        main_question="Does the maintained demo site still build and present the intended examples?",
        primary_files=[
            "pretext/pages/demos/*",
            "pretext/scripts/build-demo-site.ts",
        ],
        reference_files=[
            "reference/upstream-tooling-surfaces.md",
            "reference/validation-playbook.md",
        ],
        validation_area="demo-site",
        notes=[
            "This is about presentation and site assembly, not the engine hot path by itself.",
            "If a demo exposes an engine bug, switch back to the relevant engine or probe path after isolating it.",
        ],
    ),
    "package-workflow": ToolingSurfaceRecommendation(
        area="package-workflow",
        reason="Use the package workflow area for published-artifact shape, consumer smoke tests, and dist contract questions.",
        main_question="Does the published package still match the consumer contract?",
        primary_files=[
            "pretext/package.json",
            "pretext/scripts/package-smoke-test.ts",
            "pretext/tsconfig.build.json",
        ],
        reference_files=[
            "reference/upstream-tooling-surfaces.md",
            "reference/package-workflows.md",
            "reference/validation-playbook.md",
        ],
        validation_area="package-workflow",
        notes=[
            "Prefer this over benchmark or accuracy harnesses when npm consumers are the affected audience.",
            "If the package break comes from core API semantics, also consult public-api.md.",
        ],
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend the upstream tooling surface for a Pretext task.")
    parser.add_argument("--area", required=True, choices=SUPPORTED_TOOLING_AREAS, help="Tooling area to inspect.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args()

    recommendation = CATALOG[args.area]
    if args.format == "json":
        print(json.dumps(asdict(recommendation), indent=2))
        return 0

    print(f"Area: {recommendation.area}")
    print(f"Reason: {recommendation.reason}")
    print(f"Main question: {recommendation.main_question}")
    print(f"Primary files: {', '.join(recommendation.primary_files)}")
    print(f"Reference files: {', '.join(recommendation.reference_files)}")
    print(f"Validation area: {recommendation.validation_area}")
    print("Notes:")
    for note in recommendation.notes:
        print(f"- {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
