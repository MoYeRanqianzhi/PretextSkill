#!/usr/bin/env python3
"""Infer a validation plan from changed Pretext file paths."""

from __future__ import annotations

import argparse
import fnmatch
import json
from dataclasses import asdict, dataclass

from pretext_validation_catalog import FILE_PATTERNS, PLANS


@dataclass(frozen=True)
class FilePlan:
    areas: list[str]
    reason: str
    commands: list[str]
    follow_up_checks: list[str]
    matched_paths: list[str]


def normalize(path: str) -> str:
    return path.replace("\\", "/").strip()


def matches_pattern(path: str, pattern: str) -> bool:
    normalized_path = normalize(path)
    normalized_pattern = normalize(pattern)
    candidates = {
        normalized_path,
        normalized_path.removeprefix("pretext/"),
    }
    patterns = {
        normalized_pattern,
        normalized_pattern.removeprefix("pretext/"),
    }
    for candidate in candidates:
        for candidate_pattern in patterns:
            if "*" in candidate_pattern and fnmatch.fnmatch(candidate, candidate_pattern):
                return True
            if "/" in candidate_pattern:
                if candidate.endswith(candidate_pattern):
                    return True
            elif candidate == candidate_pattern:
                return True
    return False


def plan_for_paths(paths: list[str]) -> FilePlan:
    matched_paths: list[str] = []
    areas: list[str] = []
    for raw_path in paths:
        path = normalize(raw_path)
        for pattern, area in FILE_PATTERNS:
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
        plan = PLANS[area]
        for command in plan.commands:
            if command not in commands:
                commands.append(command)
        for check in plan.follow_up_checks:
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
