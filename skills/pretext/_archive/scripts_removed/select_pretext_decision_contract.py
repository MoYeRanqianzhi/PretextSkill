#!/usr/bin/env python3
"""Turn a tentative Pretext route into an explicit decision contract."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from pretext_validation_catalog import PLANS
from select_pretext_api import SUPPORTED_GOALS, SUPPORTED_SURFACES, build_recommendation
from select_pretext_owner import CATALOG as OWNER_CATALOG
from select_pretext_tooling_surface import CATALOG as TOOLING_CATALOG, SUPPORTED_TOOLING_AREAS


@dataclass(frozen=True)
class DecisionContract:
    goal: str
    surface: str
    issue: str | None
    tooling_area: str | None
    validation_area: str | None
    route_summary: str
    must_state: list[str]
    assumptions: list[str]
    proof_obligations: list[str]
    route_breakers: list[str]
    validation_commands: list[str]
    follow_up_checks: list[str]
    notes: list[str]


GOAL_PROOF_OBLIGATIONS = {
    "height": [
        "Use `prepare()` plus `layout()` rather than a richer path.",
        "Reuse prepared state across width changes.",
    ],
    "fixed-lines": [
        "Use `prepareWithSegments()` only because concrete line strings are truly required.",
        "Use `layoutWithLines()` at a fixed width.",
    ],
    "streamed-lines": [
        "Use `layoutNextLine()` because cursor continuity across containers matters.",
        "Keep one prepared paragraph while the paragraph continues across containers.",
    ],
    "geometry": [
        "Keep repeated probes in `walkLineRanges()` rather than materializing line strings.",
        "Delay `layoutWithLines()` until line text is truly needed.",
    ],
    "variable-width": [
        "Use `layoutNextLine()` because width budgets change per line.",
        "Keep width selection external to Pretext.",
    ],
    "shrinkwrap": [
        "Keep shrink-wrap search geometry-only during repeated probes.",
        "Materialize concrete lines only after choosing the final width.",
    ],
    "profile": [
        "Use `profilePrepare()` only for prepare-phase diagnostics, not as a rendering primitive.",
    ],
    "correctness": [
        "Reproduce the issue through exported APIs before proposing internals edits.",
        "Name the disputed contract explicitly.",
    ],
    "cache-locale": [
        "Treat `setLocale()` as preparation-affecting and cache-clearing.",
        "Separate locale invalidation from width-only layout invalidation.",
    ],
    "upstream-internals": [
        "Justify why the package-facing route is insufficient.",
        "Localize the first incorrect observable state before patching internals.",
    ],
    "diagnostics": [
        "Prefer the smallest falsifiable repro before broad sweeps.",
    ],
}

GOAL_ROUTE_BREAKERS = {
    "height": [
        "The renderer needs concrete line strings or cursors.",
    ],
    "fixed-lines": [
        "The paragraph must continue across pages, columns, or slices.",
        "The renderer only needs geometry or height.",
    ],
    "streamed-lines": [
        "The paragraph does not actually continue across containers.",
        "Width budgets truly vary per line and continuation is not the main requirement.",
    ],
    "geometry": [
        "The renderer needs final line strings at probe time.",
    ],
    "variable-width": [
        "Widths do not actually vary per line.",
        "Continuation across fixed-width containers is the real requirement.",
    ],
    "shrinkwrap": [
        "Line strings are required during the search loop.",
    ],
    "profile": [
        "The issue is lifecycle misuse rather than prepare-phase cost.",
    ],
    "correctness": [
        "The behavior is actually an integration mismatch rather than a contract dispute.",
    ],
    "cache-locale": [
        "The stale result is caused by local wrapper state, not by locale or cache invalidation.",
    ],
    "upstream-internals": [
        "The problem can be resolved entirely at the exported package surface.",
    ],
    "diagnostics": [
        "A maintained harness can falsify the issue faster than ad hoc reasoning.",
    ],
}

SURFACE_ASSUMPTIONS = {
    "react-dom": [
        "DOM participation is limited to width acquisition and lifecycle timing.",
    ],
    "custom-renderer": [
        "The renderer needs more than DOM-style height measurement.",
    ],
    "document-reader": [
        "Paragraph continuation across pages, columns, or reader regions is central.",
    ],
    "package": [
        "The npm-facing artifact contract matters more than local source reasoning.",
    ],
    "upstream": [
        "The first incorrect state is inside source modules rather than only at the package surface.",
    ],
}


def build_contract(
    goal: str,
    surface: str,
    issue: str | None,
    tooling_area: str | None,
    validation_area: str | None,
    preserve_whitespace: bool,
    locale_sensitive: bool,
) -> DecisionContract:
    recommendation = build_recommendation(goal, surface, preserve_whitespace, locale_sensitive)
    derived_validation_area = validation_area
    notes: list[str] = list(recommendation.notes)

    if derived_validation_area is None and issue is not None:
        derived_validation_area = OWNER_CATALOG[issue].validation_area
    if derived_validation_area is None and tooling_area is not None:
        derived_validation_area = TOOLING_CATALOG[tooling_area].validation_area

    validation_commands: list[str] = []
    follow_up_checks: list[str] = []
    if derived_validation_area is not None:
        plan = PLANS[derived_validation_area]
        validation_commands = list(plan.commands)
        follow_up_checks = list(plan.follow_up_checks)
        notes.append(plan.reason)

    assumptions = [
        "Width source is explicit.",
        "Font shorthand is explicit.",
        "Line-height source is explicit.",
        f"Whitespace mode is treated as `{'pre-wrap' if preserve_whitespace else 'normal unless the task proves otherwise'}`.",
        "Locale policy is explicit." if locale_sensitive else "Locale policy is assumed not to vary unless the task proves otherwise.",
    ]
    assumptions.extend(SURFACE_ASSUMPTIONS.get(surface, []))
    if goal == "streamed-lines":
        assumptions.append("Continuation across containers is a real requirement, not a guess.")
    if goal == "variable-width":
        assumptions.append("Widths vary per line rather than merely per container.")

    must_state = [
        f"Chosen goal: `{goal}`.",
        f"Chosen surface: `{surface}`.",
        "Re-prepare inputs: " + ", ".join(recommendation.invalidates_prepare_on) + ".",
        "Re-layout inputs: " + ", ".join(recommendation.invalidates_layout_on) + ".",
    ]
    if issue is not None:
        must_state.append(f"Owning issue category: `{issue}`.")
    if tooling_area is not None:
        must_state.append(f"Narrow tooling area: `{tooling_area}`.")
    if derived_validation_area is not None:
        must_state.append(f"Validation area: `{derived_validation_area}`.")

    route_summary = recommendation.reason
    if issue is not None:
        route_summary += " " + OWNER_CATALOG[issue].reason
    if tooling_area is not None:
        route_summary += " " + TOOLING_CATALOG[tooling_area].reason

    return DecisionContract(
        goal=goal,
        surface=surface,
        issue=issue,
        tooling_area=tooling_area,
        validation_area=derived_validation_area,
        route_summary=route_summary,
        must_state=must_state,
        assumptions=assumptions,
        proof_obligations=list(GOAL_PROOF_OBLIGATIONS.get(goal, [])),
        route_breakers=list(GOAL_ROUTE_BREAKERS.get(goal, [])),
        validation_commands=validation_commands,
        follow_up_checks=follow_up_checks,
        notes=notes,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Turn a tentative Pretext route into an explicit decision contract.")
    parser.add_argument("--goal", required=True, choices=SUPPORTED_GOALS, help="Chosen goal.")
    parser.add_argument("--surface", choices=SUPPORTED_SURFACES, default="generic", help="Chosen surface.")
    parser.add_argument("--issue", choices=sorted(OWNER_CATALOG.keys()), help="Optional owning issue category.")
    parser.add_argument("--tooling-area", choices=SUPPORTED_TOOLING_AREAS, help="Optional tooling area.")
    parser.add_argument("--validation-area", choices=sorted(PLANS.keys()), help="Optional explicit validation area.")
    parser.add_argument("--preserve-whitespace", action="store_true", help="State `pre-wrap` as part of the contract.")
    parser.add_argument("--locale-sensitive", action="store_true", help="State locale sensitivity as part of the contract.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args()

    contract = build_contract(
        goal=args.goal,
        surface=args.surface,
        issue=args.issue,
        tooling_area=args.tooling_area,
        validation_area=args.validation_area,
        preserve_whitespace=args.preserve_whitespace,
        locale_sensitive=args.locale_sensitive,
    )

    if args.format == "json":
        print(json.dumps(asdict(contract), indent=2))
        return 0

    print(f"Goal: {contract.goal}")
    print(f"Surface: {contract.surface}")
    print(f"Issue: {contract.issue or '(none)'}")
    print(f"Tooling area: {contract.tooling_area or '(none)'}")
    print(f"Validation area: {contract.validation_area or '(none)'}")
    print(f"Route summary: {contract.route_summary}")
    print("Must state:")
    for item in contract.must_state:
        print(f"- {item}")
    print("Assumptions:")
    for item in contract.assumptions:
        print(f"- {item}")
    print("Proof obligations:")
    for item in contract.proof_obligations or ["(none)"]:
        print(f"- {item}")
    print("Route breakers:")
    for item in contract.route_breakers or ["(none)"]:
        print(f"- {item}")
    print("Validation commands:")
    for item in contract.validation_commands or ["(none)"]:
        print(f"- {item}")
    print("Follow-up checks:")
    for item in contract.follow_up_checks or ["(none)"]:
        print(f"- {item}")
    print("Notes:")
    for item in contract.notes or ["(none)"]:
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
