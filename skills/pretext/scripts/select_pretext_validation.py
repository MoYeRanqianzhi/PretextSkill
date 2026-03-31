#!/usr/bin/env python3
"""Recommend a minimal validation plan for a Pretext change area."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


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
        reason="Segmentation, whitespace, punctuation glue, and script preprocessing live here.",
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
        reason="Width measurement, engine profiles, emoji correction, and grapheme-width derivation live here.",
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
        reason="Line walking, break decisions, tabs, streamed lines, and geometry-only iteration live here.",
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
        reason="Public API orchestration, exported types, and rich line materialization live here.",
        commands=["bun test", "bun run package-smoke-test", "python skills/pretext/scripts/check_layout_api_sync.py"],
        follow_up_checks=[
            "bun run check",
        ],
        source_files=["pretext/src/layout.ts", "pretext/README.md"],
    ),
    "bidi": ValidationPlan(
        area="bidi",
        reason="Rich-path bidi metadata lives here.",
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
        reason="Benchmark methodology and reporting live here.",
        commands=["bun run benchmark-check", "bun run status-dashboard"],
        follow_up_checks=[
            "bun run benchmark-check:safari",
        ],
        source_files=["pretext/pages/benchmark.ts", "pretext/STATUS.md"],
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend a validation plan for a Pretext change area.")
    parser.add_argument(
        "--area",
        required=True,
        choices=sorted(PLANS.keys()),
        help="The subsystem or change area.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format.",
    )
    args = parser.parse_args()

    plan = PLANS[args.area]
    if args.format == "json":
      print(json.dumps(asdict(plan), indent=2))
      return 0

    print(f"Area: {plan.area}")
    print(f"Reason: {plan.reason}")
    print("Commands:")
    for command in plan.commands:
        print(f"- {command}")
    print("Follow-up checks:")
    for check in plan.follow_up_checks:
        print(f"- {check}")
    print("Source files:")
    for source in plan.source_files:
        print(f"- {source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
