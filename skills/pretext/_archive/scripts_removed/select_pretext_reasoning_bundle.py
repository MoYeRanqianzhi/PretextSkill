#!/usr/bin/env python3
"""Build one integrated reasoning bundle for a Pretext task."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from select_pretext_api import SUPPORTED_GOALS, SUPPORTED_SURFACES
from select_pretext_decision_contract import DecisionContract, build_contract
from select_pretext_owner import CATALOG as OWNER_CATALOG
from select_pretext_route_plan import RoutePlan, build_route_plan
from select_pretext_socratic_review import SocraticReview, build_review
from select_pretext_tooling_surface import SUPPORTED_TOOLING_AREAS


def append_unique(items: list[str], additions: list[str]) -> list[str]:
    merged = list(items)
    for item in additions:
        if item not in merged:
            merged.append(item)
    return merged


@dataclass(frozen=True)
class ReasoningBundle:
    goal: str
    surface: str
    issue: str | None
    tooling_area: str | None
    validation_area: str | None
    route_plan: RoutePlan
    socratic_review: SocraticReview
    decision_contract: DecisionContract
    minimal_reference_files: list[str]
    execution_order: list[str]
    final_claim: str
    notes: list[str]


def build_reasoning_bundle(
    goal: str,
    surface: str,
    issue: str | None,
    tooling_area: str | None,
    validation_area: str | None,
    preserve_whitespace: bool,
    locale_sensitive: bool,
) -> ReasoningBundle:
    route_plan = build_route_plan(
        goal=goal,
        surface=surface,
        issue=issue,
        tooling_area=tooling_area,
        validation_area=validation_area,
        preserve_whitespace=preserve_whitespace,
        locale_sensitive=locale_sensitive,
        include_escalation=True,
    )
    socratic_review = build_review(goal=goal, surface=surface, issue=issue, tooling_area=tooling_area)
    decision_contract = build_contract(
        goal=goal,
        surface=surface,
        issue=issue,
        tooling_area=tooling_area,
        validation_area=route_plan.validation_area,
        preserve_whitespace=preserve_whitespace,
        locale_sensitive=locale_sensitive,
    )

    minimal_reference_files: list[str] = []
    minimal_reference_files = append_unique(minimal_reference_files, route_plan.reference_files)
    if "reference/socratic-review.md" not in minimal_reference_files:
        minimal_reference_files.append("reference/socratic-review.md")
    if "reference/decision-contract.md" not in minimal_reference_files:
        minimal_reference_files.append("reference/decision-contract.md")

    execution_order = [
        f"1. Route: `{goal}` on `{surface}`" + (f", issue `{issue}`" if issue else "") + (f", tooling `{tooling_area}`" if tooling_area else ""),
        "2. Challenge the route against neighboring goals and surfaces.",
        "3. Commit the surviving route as a decision contract.",
        "4. Run the smallest validation chain before any broader harness.",
    ]

    final_claim = (
        f"The best current route is `{goal}` on `{surface}`."
        " It survives first-principles routing, Socratic challenge, and decision-contract scrutiny,"
        f" and should be implemented only under validation area `{route_plan.validation_area or 'none yet'}`."
    )

    notes = append_unique(list(route_plan.notes), list(socratic_review.notes))
    notes = append_unique(notes, list(decision_contract.notes))
    if issue in OWNER_CATALOG:
        notes.append("The owning issue category should be treated as a hypothesis about the first incorrect state, not just a file label.")

    return ReasoningBundle(
        goal=goal,
        surface=surface,
        issue=issue,
        tooling_area=tooling_area,
        validation_area=route_plan.validation_area,
        route_plan=route_plan,
        socratic_review=socratic_review,
        decision_contract=decision_contract,
        minimal_reference_files=minimal_reference_files,
        execution_order=execution_order,
        final_claim=final_claim,
        notes=notes,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build one integrated reasoning bundle for a Pretext task.")
    parser.add_argument("--goal", required=True, choices=SUPPORTED_GOALS, help="Chosen goal.")
    parser.add_argument("--surface", choices=SUPPORTED_SURFACES, default="generic", help="Chosen surface.")
    parser.add_argument("--issue", choices=sorted(OWNER_CATALOG.keys()), help="Optional owning issue.")
    parser.add_argument("--tooling-area", choices=SUPPORTED_TOOLING_AREAS, help="Optional tooling area.")
    parser.add_argument("--validation-area", help="Optional explicit validation area override.")
    parser.add_argument("--preserve-whitespace", action="store_true", help="Include pre-wrap assumptions.")
    parser.add_argument("--locale-sensitive", action="store_true", help="Include locale assumptions.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args()

    bundle = build_reasoning_bundle(
        goal=args.goal,
        surface=args.surface,
        issue=args.issue,
        tooling_area=args.tooling_area,
        validation_area=args.validation_area,
        preserve_whitespace=args.preserve_whitespace,
        locale_sensitive=args.locale_sensitive,
    )

    if args.format == "json":
        print(json.dumps(asdict(bundle), indent=2))
        return 0

    print(f"Goal: {bundle.goal}")
    print(f"Surface: {bundle.surface}")
    print(f"Issue: {bundle.issue or '(none)'}")
    print(f"Tooling area: {bundle.tooling_area or '(none)'}")
    print(f"Validation area: {bundle.validation_area or '(none)'}")
    print(f"Final claim: {bundle.final_claim}")
    print("Minimal reference files:")
    for item in bundle.minimal_reference_files:
        print(f"- {item}")
    print("Execution order:")
    for item in bundle.execution_order:
        print(f"- {item}")
    print("Notes:")
    for item in bundle.notes:
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
