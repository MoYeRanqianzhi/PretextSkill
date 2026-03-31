#!/usr/bin/env python3
"""Build a unified first-principles route plan for a Pretext task."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from pretext_validation_catalog import PLANS
from select_pretext_api import SUPPORTED_GOALS, SUPPORTED_SURFACES, build_recommendation
from select_pretext_owner import CATALOG as OWNER_CATALOG
from select_pretext_tooling_surface import CATALOG as TOOLING_CATALOG, SUPPORTED_TOOLING_AREAS


@dataclass(frozen=True)
class RoutePlan:
    goal: str | None
    surface: str
    issue: str | None
    tooling_area: str | None
    validation_area: str | None
    primary_question: str
    reference_files: list[str]
    helper_commands: list[str]
    next_validation_commands: list[str]
    follow_up_checks: list[str]
    notes: list[str]


def append_unique(items: list[str], additions: list[str]) -> list[str]:
    merged = list(items)
    for item in additions:
        if item not in merged:
            merged.append(item)
    return merged


def build_route_plan(
    goal: str | None,
    surface: str,
    issue: str | None,
    tooling_area: str | None,
    validation_area: str | None,
    preserve_whitespace: bool,
    locale_sensitive: bool,
) -> RoutePlan:
    references = ["reference/first-principles.md"]
    helper_commands = []
    notes = []
    primary_question_parts: list[str] = []

    derived_validation_area = validation_area

    if goal is not None:
        recommendation = build_recommendation(goal, surface, preserve_whitespace, locale_sensitive)
        references = append_unique(references, recommendation.reference_files)
        helper_commands.append(
            f"python scripts/select_pretext_api.py --goal {goal} --surface {surface}"
            + (" --preserve-whitespace" if preserve_whitespace else "")
            + (" --locale-sensitive" if locale_sensitive else "")
        )
        notes = append_unique(notes, recommendation.notes)
        primary_question_parts.append(recommendation.reason)

    if issue is not None:
        owner = OWNER_CATALOG[issue]
        references = append_unique(references, owner.reference_files)
        helper_commands.append(f"python scripts/select_pretext_owner.py --issue {issue}")
        notes = append_unique(notes, owner.notes)
        primary_question_parts.append(owner.reason)
        if derived_validation_area is None:
            derived_validation_area = owner.validation_area

    if tooling_area is not None:
        tooling = TOOLING_CATALOG[tooling_area]
        references = append_unique(references, tooling.reference_files)
        helper_commands.append(f"python scripts/select_pretext_tooling_surface.py --area {tooling_area}")
        notes = append_unique(notes, tooling.notes)
        primary_question_parts.append(tooling.reason)
        if derived_validation_area is None:
            derived_validation_area = tooling.validation_area

    next_validation_commands: list[str] = []
    follow_up_checks: list[str] = []
    if derived_validation_area is not None:
        plan = PLANS[derived_validation_area]
        helper_commands.append(f"python scripts/select_pretext_validation.py --area {derived_validation_area}")
        next_validation_commands = list(plan.commands)
        follow_up_checks = list(plan.follow_up_checks)
        primary_question_parts.append(plan.reason)

    if not primary_question_parts:
        primary_question_parts.append(
            "Clarify whether this is an API-selection problem, an upstream ownership problem, a tooling-surface problem, or a validation-scoping problem."
        )

    return RoutePlan(
        goal=goal,
        surface=surface,
        issue=issue,
        tooling_area=tooling_area,
        validation_area=derived_validation_area,
        primary_question=" ".join(primary_question_parts),
        reference_files=references,
        helper_commands=helper_commands,
        next_validation_commands=next_validation_commands,
        follow_up_checks=follow_up_checks,
        notes=notes,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a unified first-principles route plan for a Pretext task.")
    parser.add_argument("--goal", choices=SUPPORTED_GOALS, help="Optional API-selection goal.")
    parser.add_argument("--surface", choices=SUPPORTED_SURFACES, default="generic", help="Optional integration surface.")
    parser.add_argument("--issue", choices=sorted(OWNER_CATALOG.keys()), help="Optional upstream ownership issue.")
    parser.add_argument("--tooling-area", choices=SUPPORTED_TOOLING_AREAS, help="Optional upstream tooling area.")
    parser.add_argument("--validation-area", choices=sorted(PLANS.keys()), help="Optional explicit validation area.")
    parser.add_argument("--preserve-whitespace", action="store_true", help="Include pre-wrap guidance when goal routing is used.")
    parser.add_argument("--locale-sensitive", action="store_true", help="Include locale guidance when goal routing is used.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args()

    plan = build_route_plan(
        goal=args.goal,
        surface=args.surface,
        issue=args.issue,
        tooling_area=args.tooling_area,
        validation_area=args.validation_area,
        preserve_whitespace=args.preserve_whitespace,
        locale_sensitive=args.locale_sensitive,
    )

    if args.format == "json":
        print(json.dumps(asdict(plan), indent=2))
        return 0

    print(f"Goal: {plan.goal or '(none)'}")
    print(f"Surface: {plan.surface}")
    print(f"Issue: {plan.issue or '(none)'}")
    print(f"Tooling area: {plan.tooling_area or '(none)'}")
    print(f"Validation area: {plan.validation_area or '(none)'}")
    print(f"Primary question: {plan.primary_question}")
    print(f"Reference files: {', '.join(plan.reference_files)}")
    print("Helper commands:")
    if plan.helper_commands:
        for command in plan.helper_commands:
            print(f"- {command}")
    else:
        print("- (none)")
    print("Next validation commands:")
    if plan.next_validation_commands:
        for command in plan.next_validation_commands:
            print(f"- {command}")
    else:
        print("- (none)")
    print("Follow-up checks:")
    if plan.follow_up_checks:
        for check in plan.follow_up_checks:
            print(f"- {check}")
    else:
        print("- (none)")
    print("Notes:")
    if plan.notes:
        for note in plan.notes:
            print(f"- {note}")
    else:
        print("- (none)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
