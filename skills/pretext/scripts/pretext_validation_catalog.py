#!/usr/bin/env python3
"""Shared validation catalog for the Pretext skill."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationPlan:
    area: str
    reason: str
    commands: list[str]
    follow_up_checks: list[str]
    source_files: list[str]


PLANS: dict[str, ValidationPlan] = {
    "analysis": ValidationPlan(
        area="analysis",
        reason="Segmentation, whitespace normalization, punctuation glue, locale-sensitive preprocessing, and chunk ownership live here.",
        commands=["bun test", "bun run check"],
        follow_up_checks=[
            "bun run pre-wrap-check",
            "bun run accuracy-check",
            "bun run corpus-check",
        ],
        source_files=["pretext/src/analysis.ts", "pretext/src/layout.test.ts"],
    ),
    "measurement": ValidationPlan(
        area="measurement",
        reason="Canvas measurement, engine profiling, emoji correction, and grapheme-width derivation live here.",
        commands=["bun test", "bun run check"],
        follow_up_checks=[
            "bun run benchmark-check",
            "bun run accuracy-check",
            "bun run probe-check",
            "bun run benchmark-check:safari",
        ],
        source_files=["pretext/src/measurement.ts", "pretext/src/layout.test.ts"],
    ),
    "line-break": ValidationPlan(
        area="line-break",
        reason="Arithmetic-only line walking, tabs, streamed lines, shrink-wrap geometry, and break decisions live here.",
        commands=["bun test", "bun run check"],
        follow_up_checks=[
            "bun run pre-wrap-check",
            "geometry-only forward test",
            "shrink-wrap forward test",
            "bun run accuracy-check",
            "bun run corpus-check",
        ],
        source_files=["pretext/src/line-break.ts", "pretext/src/layout.test.ts"],
    ),
    "layout-api": ValidationPlan(
        area="layout-api",
        reason="Public API orchestration, exported types, line materialization, and prepare/layout consistency live here.",
        commands=[
            "bun test",
            "bun run check",
            "bun run build:package",
            "bun run package-smoke-test",
            "python skills/pretext/scripts/check_layout_api_sync.py",
        ],
        follow_up_checks=[
            "bun run benchmark-check",
            "bun run accuracy-check",
        ],
        source_files=["pretext/src/layout.ts", "pretext/README.md"],
    ),
    "bidi": ValidationPlan(
        area="bidi",
        reason="Rich-path bidi metadata and mixed-direction custom-rendering support live here.",
        commands=["bun test", "bun run check"],
        follow_up_checks=[
            "targeted mixed-direction repro",
            "bun run accuracy-check",
            "bun run corpus-check",
        ],
        source_files=["pretext/src/bidi.ts", "pretext/src/layout.test.ts"],
    ),
    "benchmark-harness": ValidationPlan(
        area="benchmark-harness",
        reason="Prepare/layout benchmark methodology and status reporting live here.",
        commands=["bun run benchmark-check", "bun run status-dashboard"],
        follow_up_checks=[
            "bun run benchmark-check:safari",
        ],
        source_files=["pretext/pages/benchmark.ts", "pretext/STATUS.md"],
    ),
    "accuracy-harness": ValidationPlan(
        area="accuracy-harness",
        reason="Browser-parity and whitespace-preservation oracles live here.",
        commands=["bun run accuracy-check", "bun run pre-wrap-check"],
        follow_up_checks=[
            "bun run accuracy-check:safari",
            "bun run accuracy-check:firefox",
        ],
        source_files=["pretext/pages/accuracy.ts", "pretext/scripts/accuracy-check.ts"],
    ),
    "probe-surface": ValidationPlan(
        area="probe-surface",
        reason="The probe surface is the closest manual parity and visual-debugging harness for a single paragraph.",
        commands=["bun run probe-check", "bun run check"],
        follow_up_checks=[
            "bun run accuracy-check",
        ],
        source_files=["pretext/pages/probe.ts", "pretext/scripts/probe-check.ts"],
    ),
    "corpus-tooling": ValidationPlan(
        area="corpus-tooling",
        reason="Representative corpus inspection, sweeps, and font-matrix analysis live here.",
        commands=["bun run corpus-check", "bun run corpus-status"],
        follow_up_checks=[
            "bun run corpus-sweep",
            "bun run corpus-font-matrix",
            "bun run corpus-representative",
            "bun run corpus-taxonomy",
            "bun run accuracy-check",
        ],
        source_files=["pretext/pages/corpus.ts", "pretext/scripts/corpus-check.ts"],
    ),
    "gatsby-surface": ValidationPlan(
        area="gatsby-surface",
        reason="Long-form article parity against Gatsby-derived samples lives here.",
        commands=["bun run gatsby-check", "bun run corpus-status"],
        follow_up_checks=[
            "bun run gatsby-sweep",
            "bun run accuracy-check",
        ],
        source_files=["pretext/pages/gatsby.ts", "pretext/scripts/gatsby-check.ts"],
    ),
    "package-workflow": ValidationPlan(
        area="package-workflow",
        reason="Published-artifact shape, build output, and consumer smoke tests live here.",
        commands=["bun run check", "bun run build:package", "bun run package-smoke-test"],
        follow_up_checks=[
            "python skills/pretext/scripts/check_layout_api_sync.py",
        ],
        source_files=["pretext/package.json", "pretext/scripts/package-smoke-test.ts"],
    ),
    "demo-site": ValidationPlan(
        area="demo-site",
        reason="Demo pages and site assembly live here rather than engine semantics.",
        commands=["bun run check", "bun run site:build"],
        follow_up_checks=[
            "bun start",
            "targeted demo page inspection",
        ],
        source_files=["pretext/pages/demos", "pretext/scripts/build-demo-site.ts"],
    ),
}


FILE_PATTERNS: list[tuple[str, str]] = [
    ("src/analysis.ts", "analysis"),
    ("src/measurement.ts", "measurement"),
    ("src/line-break.ts", "line-break"),
    ("src/layout.ts", "layout-api"),
    ("src/bidi.ts", "bidi"),
    ("README.md", "layout-api"),
    ("pages/benchmark.ts", "benchmark-harness"),
    ("pages/benchmark.html", "benchmark-harness"),
    ("scripts/benchmark-check.ts", "benchmark-harness"),
    ("scripts/status-dashboard.ts", "benchmark-harness"),
    ("pages/accuracy.ts", "accuracy-harness"),
    ("pages/accuracy.html", "accuracy-harness"),
    ("scripts/browser-automation.ts", "accuracy-harness"),
    ("scripts/accuracy-check.ts", "accuracy-harness"),
    ("scripts/pre-wrap-check.ts", "accuracy-harness"),
    ("pages/probe.ts", "probe-surface"),
    ("pages/probe.html", "probe-surface"),
    ("scripts/probe-check.ts", "probe-surface"),
    ("pages/corpus.ts", "corpus-tooling"),
    ("pages/corpus.html", "corpus-tooling"),
    ("scripts/corpus-check.ts", "corpus-tooling"),
    ("scripts/corpus-sweep.ts", "corpus-tooling"),
    ("scripts/corpus-font-matrix.ts", "corpus-tooling"),
    ("scripts/corpus-status.ts", "corpus-tooling"),
    ("scripts/corpus-representative.ts", "corpus-tooling"),
    ("scripts/corpus-taxonomy.ts", "corpus-tooling"),
    ("pages/gatsby.ts", "gatsby-surface"),
    ("pages/gatsby.html", "gatsby-surface"),
    ("scripts/gatsby-check.ts", "gatsby-surface"),
    ("scripts/gatsby-sweep.ts", "gatsby-surface"),
    ("scripts/package-smoke-test.ts", "package-workflow"),
    ("package.json", "package-workflow"),
    ("tsconfig.build.json", "package-workflow"),
    ("CHANGELOG.md", "package-workflow"),
    ("scripts/build-demo-site.ts", "demo-site"),
    ("pages/demos/*", "demo-site"),
    ("pages/assets/*", "demo-site"),
    ("pages/*.html", "demo-site"),
]
