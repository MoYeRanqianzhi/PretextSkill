#!/usr/bin/env python3
"""Challenge a tentative Pretext route before committing to it."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from select_pretext_api import SUPPORTED_GOALS, SUPPORTED_SURFACES
from select_pretext_owner import CATALOG as OWNER_CATALOG
from select_pretext_tooling_surface import SUPPORTED_TOOLING_AREAS


@dataclass(frozen=True)
class SocraticReview:
    goal: str | None
    surface: str | None
    issue: str | None
    tooling_area: str | None
    central_claim: str
    socratic_questions: list[str]
    routes_to_rule_out: list[str]
    evidence_ladder: list[str]
    falsifiers: list[str]
    suggested_commands: list[str]
    notes: list[str]


GOAL_QUESTIONS = {
    "height": [
        "Do I actually need line strings, cursors, or geometry, or only height and line count?",
        "Am I choosing a richer path only because it feels safer rather than because the product requires it?",
    ],
    "fixed-lines": [
        "Do I truly need concrete line text, or would geometry-only iteration be enough?",
        "Is this one fixed region, or does the paragraph continue across containers?",
    ],
    "streamed-lines": [
        "Is the paragraph continuing across pages, columns, or slices, or am I only reacting to `layoutNextLine()` existing?",
        "If width is constant, is cursor continuity still the real requirement?",
    ],
    "geometry": [
        "Can I defer line-text materialization until after the probe or width-search loop?",
        "Am I accidentally paying for `LayoutLine.text` when widths and cursors would be enough?",
    ],
    "variable-width": [
        "Do widths truly change per line, or is the real need paragraph continuation across fixed-width regions?",
        "Would `streamed-lines` be the simpler truth for this task?",
    ],
    "shrinkwrap": [
        "Do I need actual line strings during the width search, or only geometry?",
        "Can I keep all repeated probes in `walkLineRanges()` and materialize lines once at the end?",
    ],
    "profile": [
        "Am I measuring prepare-phase cost, or am I actually dealing with an application lifecycle problem?",
        "What is the lightest command that would falsify my performance theory?",
    ],
    "correctness": [
        "What exact exported behavior is under dispute?",
        "Can I reproduce the issue with exported APIs before I inspect internals?",
    ],
    "cache-locale": [
        "Is the stale result caused by local wrapper state, or by misunderstanding `setLocale()` and cache invalidation?",
        "Which values must be re-prepared, and which only need re-layout?",
    ],
    "upstream-internals": [
        "Why is the package-facing API insufficient for this task?",
        "Which module owns the first incorrect observable state rather than the most visible final symptom?",
    ],
    "diagnostics": [
        "What is the smallest falsifiable repro?",
        "Am I looking at a known caveat, an integration mismatch, or a real engine defect?",
    ],
}

GOAL_RULE_OUTS = {
    "height": [
        "Rule out `fixed-lines` unless concrete line strings are truly required.",
        "Rule out `streamed-lines` unless continuation across containers matters.",
    ],
    "fixed-lines": [
        "Rule out `height` if the renderer truly needs line text.",
        "Rule out `streamed-lines` unless continuation across regions is part of the requirement.",
    ],
    "streamed-lines": [
        "Rule out `fixed-lines` if the paragraph must continue across pages or columns.",
        "Rule out `variable-width` if widths do not actually vary per line.",
    ],
    "geometry": [
        "Rule out `fixed-lines` unless final line strings are needed during the probe loop.",
    ],
    "variable-width": [
        "Rule out `fixed-lines` if width budgets differ per line.",
        "Rule out `streamed-lines` if continuation is not the core reason for choosing `layoutNextLine()`.",
    ],
    "shrinkwrap": [
        "Rule out `fixed-lines` if width-search iterations do not need concrete line strings.",
    ],
    "profile": [
        "Rule out broad architecture changes before separating analysis cost from measurement cost.",
    ],
    "correctness": [
        "Rule out source patches before reproducing the issue with exported APIs.",
    ],
    "cache-locale": [
        "Rule out width-only invalidation as the cause if locale or whitespace policy changed.",
    ],
    "upstream-internals": [
        "Rule out package-facing guidance only if the first incorrect state is definitely inside source modules.",
    ],
    "diagnostics": [
        "Rule out broad harness sweeps before isolating one concrete mismatch.",
    ],
}

SURFACE_QUESTIONS = {
    "react-dom": [
        "Is DOM involvement limited to width acquisition and lifecycle timing?",
        "Is this actually a wrapper-boundary problem rather than a renderer problem?",
    ],
    "custom-renderer": [
        "Is this renderer truly generic, or is it a reader or paginator in disguise?",
        "Does the renderer consume height, geometry, or concrete lines?",
    ],
    "document-reader": [
        "Is continuation across containers the core requirement?",
        "Are preserved-break blocks mixed into normal flowing prose?",
    ],
    "package": [
        "Is the failure really npm-consumer-facing rather than source-internal?",
        "Would source-level reasoning skip the actual dist contract risk?",
    ],
    "upstream": [
        "Why is the published package path insufficient here?",
        "Which module owns the first incorrect state rather than the most visible final output?",
    ],
}

SURFACE_RULE_OUTS = {
    "react-dom": ["Rule out `custom-renderer` if the DOM is only supplying width and lifecycle timing."],
    "custom-renderer": ["Rule out `document-reader` only if continuation across pages or columns is irrelevant."],
    "document-reader": ["Rule out generic `custom-renderer` if pagination or continuation semantics are central."],
    "package": ["Rule out `upstream` if the consumer contract can be validated at the package boundary."],
    "upstream": ["Rule out `package` if the first incorrect state is already inside a source module."],
}

ISSUE_QUESTIONS = {
    "streamed-lines": [
        "Is the first incorrect state before or after line materialization?",
        "Does `layoutNextLine()` diverge from `layoutWithLines()` because of line walking, not because of rendering?",
    ],
    "line-fit": [
        "Are segmentation and measurement already correct before the wrong line boundary appears?",
    ],
    "measurement-width": [
        "Is the defect in width metadata rather than in line walking or materialization?",
    ],
}


def build_review(goal: str | None, surface: str | None, issue: str | None, tooling_area: str | None) -> SocraticReview:
    central_parts: list[str] = []
    questions: list[str] = [
        "What is the minimum output shape that still satisfies the task?",
        "What fact would make the current route wrong?",
        "Am I reaching for internals before exported behavior has been reproduced?",
    ]
    routes_to_rule_out: list[str] = []
    evidence_ladder = [
        "First-principles model",
        "Exported contract or behavior reference",
        "Narrow owner or tooling selector",
        "Real downstream implementation precedent",
        "Smallest falsification command or harness",
    ]
    falsifiers: list[str] = []
    suggested_commands: list[str] = []
    notes: list[str] = []

    if goal is not None:
        central_parts.append(f"Challenge whether `{goal}` is truly the minimal output-shape route.")
        questions.extend(GOAL_QUESTIONS.get(goal, []))
        routes_to_rule_out.extend(GOAL_RULE_OUTS.get(goal, []))
        suggested_commands.append(f"python scripts/select_pretext_api.py --goal {goal}" + (f" --surface {surface}" if surface else ""))
        if surface is not None:
            suggested_commands.append(f"python scripts/select_pretext_examples.py --goal {goal} --surface {surface}")
        falsifiers.append(
            "If a neighboring route can satisfy the same task with less output materialization or less surface complexity, the current goal is probably too rich."
        )

    if surface is not None:
        central_parts.append(f"Challenge whether `{surface}` is the correct integration surface.")
        questions.extend(SURFACE_QUESTIONS.get(surface, []))
        routes_to_rule_out.extend(SURFACE_RULE_OUTS.get(surface, []))
        falsifiers.append(
            "If the main problem can be expressed without this surface's unique constraints, the chosen surface is probably too broad."
        )

    if issue is not None:
        central_parts.append(f"Challenge whether `{issue}` really identifies the first incorrect state.")
        questions.extend(ISSUE_QUESTIONS.get(issue, []))
        suggested_commands.append(f"python scripts/select_pretext_owner.py --issue {issue}")
        falsifiers.append(
            "If the first incorrect observable state appears earlier than the assumed owner module, the issue category is wrong."
        )

    if tooling_area is not None:
        central_parts.append(f"Challenge whether `{tooling_area}` is the narrowest falsification surface.")
        suggested_commands.append(f"python scripts/select_pretext_tooling_surface.py --area {tooling_area}")
        falsifiers.append(
            "If a smaller repro or a narrower harness can answer the same question, the chosen tooling area is too broad."
        )

    if goal is not None or surface is not None or issue is not None or tooling_area is not None:
        route_cmd = ["python scripts/select_pretext_route_plan.py"]
        if goal is not None:
            route_cmd.append(f"--goal {goal}")
        if surface is not None:
            route_cmd.append(f"--surface {surface}")
        if issue is not None:
            route_cmd.append(f"--issue {issue}")
        if tooling_area is not None:
            route_cmd.append(f"--tooling-area {tooling_area}")
        suggested_commands.append(" ".join(route_cmd))

    if goal == "streamed-lines" and surface == "document-reader":
        notes.append("Do not let constant width trick you into batch layout if continuation across containers is the real requirement.")
    if goal == "variable-width":
        notes.append("Prove that widths truly vary per line before defending a variable-width route.")
    if surface == "document-reader":
        notes.append("Reader problems often need both continuation logic and preserved-break exceptions for code-like blocks.")
    if issue in OWNER_CATALOG:
        notes.append("Owner selection should explain the first wrong state, not just the module where the final symptom is visible.")

    central_claim = " ".join(central_parts) if central_parts else "Challenge the tentative route before committing to code."

    return SocraticReview(
        goal=goal,
        surface=surface,
        issue=issue,
        tooling_area=tooling_area,
        central_claim=central_claim,
        socratic_questions=questions,
        routes_to_rule_out=routes_to_rule_out,
        evidence_ladder=evidence_ladder,
        falsifiers=falsifiers,
        suggested_commands=suggested_commands,
        notes=notes,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Challenge a tentative Pretext route before committing to it.")
    parser.add_argument("--goal", choices=SUPPORTED_GOALS, help="Optional tentative goal.")
    parser.add_argument("--surface", choices=[surface for surface in SUPPORTED_SURFACES if surface != "generic"], help="Optional tentative surface.")
    parser.add_argument("--issue", choices=sorted(OWNER_CATALOG.keys()), help="Optional tentative issue category.")
    parser.add_argument("--tooling-area", choices=SUPPORTED_TOOLING_AREAS, help="Optional tentative tooling area.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args()

    if not any([args.goal, args.surface, args.issue, args.tooling_area]):
        parser.error("at least one of --goal, --surface, --issue, or --tooling-area is required")

    review = build_review(args.goal, args.surface, args.issue, args.tooling_area)

    if args.format == "json":
        print(json.dumps(asdict(review), indent=2))
        return 0

    print(f"Goal: {review.goal or '(none)'}")
    print(f"Surface: {review.surface or '(none)'}")
    print(f"Issue: {review.issue or '(none)'}")
    print(f"Tooling area: {review.tooling_area or '(none)'}")
    print(f"Central claim: {review.central_claim}")
    print("Socratic questions:")
    for question in review.socratic_questions:
        print(f"- {question}")
    print("Routes to rule out:")
    for item in review.routes_to_rule_out or ["(none)"]:
        print(f"- {item}")
    print("Evidence ladder:")
    for item in review.evidence_ladder:
        print(f"- {item}")
    print("Falsifiers:")
    for item in review.falsifiers or ["(none)"]:
        print(f"- {item}")
    print("Suggested commands:")
    for command in review.suggested_commands or ["(none)"]:
        print(f"- {command}")
    print("Notes:")
    for note in review.notes or ["(none)"]:
        print(f"- {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
