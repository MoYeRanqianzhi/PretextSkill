#!/usr/bin/env python3
"""Infer a validation plan from changed Pretext file paths."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class FilePlan:
    areas: list[str]
    reason: str
    commands: list[str]
    follow_up_checks: list[str]
    matched_paths: list[str]


AREA_BY_PATTERN: list[tuple[str, str]] = [
    ("pretext/src/analysis.ts", "analysis"),
    ("pretext/src/measurement.ts", "measurement"),
    ("pretext/src/line-break.ts", "line-break"),
    ("pretext/src/layout.ts", "layout-api"),
    ("pretext/src/bidi.ts", "bidi"),
    ("pretext/pages/benchmark.ts", "benchmark-harness"),
    ("pretext/package.json", "layout-api"),
    ("pretext/README.md", "layout-api"),
]

COMMANDS_BY_AREA: dict[str, tuple[list[str], list[str]]] = {
    "analysis": (
        ["bun test", "bun run check"],
        ["bun run pre-wrap-check", "bun run accuracy-check", "bun run corpus-check"],
    ),
    "measurement": (
        ["bun test", "bun run check"],
        ["bun run benchmark-check", "bun run accuracy-check", "bun run probe-check", "bun run benchmark-check:safari"],
    ),
    "line-break": (
        ["bun test", "bun run check"],
        ["bun run pre-wrap-check", "geometry-only forward test", "shrink-wrap forward test", "bun run accuracy-check", "bun run corpus-check"],
    ),
    "layout-api": (
        ["bun test", "bun run check", "bun run package-smoke-test", "python skills/pretext/scripts/check_layout_api_sync.py"],
        ["bun run benchmark-check"],
    ),
    "bidi": (
        ["bun test", "bun run check"],
        ["targeted mixed-direction repro", "bun run accuracy-check", "bun run corpus-check"],
    ),
    "benchmark-harness": (
        ["bun run benchmark-check", "bun run status-dashboard"],
        ["bun run benchmark-check:safari"],
    ),
}


def normalize(path: str) -> str:
    return path.replace("\\", "/").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Infer a Pretext validation plan from changed file paths.")
    parser.add_argument("--path", action="append", required=True, help="Changed file path. Repeat for multiple files.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args()

    matched_paths: list[str] = []
    areas: list[str] = []
    for raw_path in args.path:
        path = normalize(raw_path)
        for pattern, area in AREA_BY_PATTERN:
            if path.endswith(pattern):
                matched_paths.append(path)
                if area not in areas:
                    areas.append(area)
                break

    if not areas:
        plan = FilePlan(
            areas=[],
            reason="No known subsystem mapping matched these paths. Fall back to manual area selection.",
            commands=[],
            follow_up_checks=[],
            matched_paths=[],
        )
    else:
        commands: list[str] = []
        follow_up_checks: list[str] = []
        for area in areas:
            base_commands, base_follow_ups = COMMANDS_BY_AREA[area]
            for command in base_commands:
                if command not in commands:
                    commands.append(command)
            for check in base_follow_ups:
                if check not in follow_up_checks:
                    follow_up_checks.append(check)
        plan = FilePlan(
            areas=areas,
            reason="Validation scope inferred from changed subsystem ownership.",
            commands=commands,
            follow_up_checks=follow_up_checks,
            matched_paths=matched_paths,
        )

    if args.format == "json":
        print(json.dumps(asdict(plan), indent=2))
        return 0

    print(f"Areas: {', '.join(plan.areas) if plan.areas else '(unmatched)'}")
    print(f"Reason: {plan.reason}")
    print("Matched paths:")
    if plan.matched_paths:
        for path in plan.matched_paths:
            print(f"- {path}")
    else:
        print("- (none)")
    print("Commands:")
    if plan.commands:
        for command in plan.commands:
            print(f"- {command}")
    else:
        print("- (none)")
    print("Follow-up checks:")
    if plan.follow_up_checks:
        for check in plan.follow_up_checks:
            print(f"- {check}")
    else:
        print("- (none)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
