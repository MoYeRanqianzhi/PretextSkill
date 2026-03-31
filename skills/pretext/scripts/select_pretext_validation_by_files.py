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
    ("src/analysis.ts", "analysis"),
    ("src/measurement.ts", "measurement"),
    ("src/line-break.ts", "line-break"),
    ("src/layout.ts", "layout-api"),
    ("src/bidi.ts", "bidi"),
    ("pages/benchmark.ts", "benchmark-harness"),
    ("scripts/browser-automation.ts", "browser-tooling"),
    ("scripts/accuracy-check.ts", "browser-tooling"),
    ("scripts/probe-check.ts", "browser-tooling"),
    ("scripts/pre-wrap-check.ts", "browser-tooling"),
    ("scripts/benchmark-check.ts", "benchmark-harness"),
    ("scripts/status-dashboard.ts", "benchmark-harness"),
    ("scripts/corpus-check.ts", "corpus-tooling"),
    ("scripts/corpus-sweep.ts", "corpus-tooling"),
    ("scripts/corpus-font-matrix.ts", "corpus-tooling"),
    ("scripts/corpus-status.ts", "corpus-tooling"),
    ("scripts/corpus-representative.ts", "corpus-tooling"),
    ("scripts/corpus-taxonomy.ts", "corpus-tooling"),
    ("scripts/gatsby-check.ts", "corpus-tooling"),
    ("scripts/gatsby-sweep.ts", "corpus-tooling"),
    ("scripts/package-smoke-test.ts", "package-workflow"),
    ("scripts/build-demo-site.ts", "site-tooling"),
    ("package.json", "layout-api"),
    ("README.md", "layout-api"),
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
    "browser-tooling": (
        ["bun run accuracy-check", "bun run probe-check"],
        ["bun run accuracy-check:safari", "bun run accuracy-check:firefox", "bun run pre-wrap-check"],
    ),
    "corpus-tooling": (
        ["bun run corpus-check", "bun run corpus-status"],
        ["bun run corpus-sweep", "bun run corpus-font-matrix", "bun run accuracy-check"],
    ),
    "package-workflow": (
        ["bun run package-smoke-test", "bun run check", "bun run build:package"],
        ["python skills/pretext/scripts/check_layout_api_sync.py"],
    ),
    "site-tooling": (
        ["bun run site:build"],
        ["bun run check"],
    ),
}


def normalize(path: str) -> str:
    return path.replace("\\", "/").strip()


def matches_pattern(path: str, pattern: str) -> bool:
    normalized_path = normalize(path)
    normalized_pattern = normalize(pattern)
    repo_relative_pattern = normalized_pattern.removeprefix("pretext/")
    return normalized_path.endswith(normalized_pattern) or normalized_path.endswith(repo_relative_pattern)


def plan_for_paths(paths: list[str]) -> FilePlan:
    matched_paths: list[str] = []
    areas: list[str] = []
    for raw_path in paths:
        path = normalize(raw_path)
        for pattern, area in AREA_BY_PATTERN:
            if matches_pattern(path, pattern):
                matched_paths.append(path)
                if area not in areas:
                    areas.append(area)
                break

    if not areas:
        return FilePlan(
            areas=[],
            reason="No known subsystem mapping matched these paths. Fall back to manual area selection.",
            commands=[],
            follow_up_checks=[],
            matched_paths=[],
        )

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

    return FilePlan(
        areas=areas,
        reason="Validation scope inferred from changed subsystem ownership.",
        commands=commands,
        follow_up_checks=follow_up_checks,
        matched_paths=matched_paths,
    )


def render_plan_json(plan: FilePlan) -> str:
    return json.dumps(asdict(plan), indent=2)


def render_plan_text(plan: FilePlan) -> str:
    lines = [
        f"Areas: {', '.join(plan.areas) if plan.areas else '(unmatched)'}",
        f"Reason: {plan.reason}",
        "Matched paths:",
    ]
    if plan.matched_paths:
        lines.extend([f"- {path}" for path in plan.matched_paths])
    else:
        lines.append("- (none)")
    lines.append("Commands:")
    if plan.commands:
        lines.extend([f"- {command}" for command in plan.commands])
    else:
        lines.append("- (none)")
    lines.append("Follow-up checks:")
    if plan.follow_up_checks:
        lines.extend([f"- {check}" for check in plan.follow_up_checks])
    else:
        lines.append("- (none)")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Infer a Pretext validation plan from changed file paths.")
    parser.add_argument("--path", action="append", required=True, help="Changed file path. Repeat for multiple files.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args()

    plan = plan_for_paths(args.path)

    if args.format == "json":
        print(render_plan_json(plan))
        return 0

    print(render_plan_text(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
