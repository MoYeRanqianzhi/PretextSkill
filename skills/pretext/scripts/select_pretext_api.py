#!/usr/bin/env python3
"""Recommend a Pretext API path, reference set, and first-principles questions."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


COMMON_QUESTIONS = [
    "What output shape is actually required?",
    "Which inputs invalidate prepare, and which invalidate only layout?",
    "Am I consuming the package API or modifying upstream internals?",
]


@dataclass(frozen=True)
class Recommendation:
    goal: str
    surface: str
    primary_apis: list[str]
    helper_apis: list[str]
    reason: str
    reference_files: list[str]
    invalidates_prepare_on: list[str]
    invalidates_layout_on: list[str]
    questions: list[str]
    notes: list[str]


def append_unique(items: list[str], additions: list[str]) -> list[str]:
    merged = list(items)
    for item in additions:
        if item not in merged:
            merged.append(item)
    return merged


def apply_surface(
    surface: str,
    reference_files: list[str],
    notes: list[str],
) -> tuple[list[str], list[str]]:
    if surface == "react-dom":
        return (
            append_unique(reference_files, ["reference/react-dom-recipes.md"]),
            append_unique(
                notes,
                [
                    "Keep DOM reads limited to width acquisition or lifecycle coordination, not post-hoc text measurement.",
                    "Treat React hooks and component caches as wrappers around the prepare/layout split, not replacements for it.",
                ],
            ),
        )
    if surface == "custom-renderer":
        return (
            append_unique(reference_files, ["reference/custom-renderer-recipes.md"]),
            append_unique(
                notes,
                [
                    "Choose the rich path only when the renderer needs lines, cursors, or geometry rather than height alone.",
                    "Keep repeated frame or width-probe work in the layout phase whenever possible.",
                ],
            ),
        )
    if surface == "package":
        return (
            append_unique(reference_files, ["reference/package-workflows.md"]),
            append_unique(
                notes,
                [
                    "Validate the published artifact separately from source-level reasoning.",
                    "Do not treat shipped `src/` files as a consumer-facing import contract just because they appear in the tarball.",
                ],
            ),
        )
    if surface == "upstream":
        return (
            append_unique(reference_files, ["reference/internal-exports.md", "reference/internal-architecture.md"]),
            append_unique(
                notes,
                [
                    "Use source-level internals only when the task explicitly modifies the cloned upstream repo.",
                    "Be explicit about which module owns the first incorrect observable state before patching internals.",
                ],
            ),
        )
    return reference_files, notes


def build_recommendation(goal: str, surface: str, preserve_whitespace: bool, locale_sensitive: bool) -> Recommendation:
    base: dict[str, Recommendation] = {
        "height": Recommendation(
            goal="height",
            surface=surface,
            primary_apis=["prepare(text, font, options)", "layout(prepared, maxWidth, lineHeight)"],
            helper_apis=[],
            reason="Use the lightest package-facing API when the caller only needs height or line count.",
            reference_files=[
                "reference/first-principles.md",
                "reference/public-api.md",
                "reference/integration-lifecycle.md",
            ],
            invalidates_prepare_on=["text", "font", "whiteSpace", "locale"],
            invalidates_layout_on=["maxWidth", "lineHeight"],
            questions=COMMON_QUESTIONS,
            notes=[
                "Reuse prepared state across width changes.",
                "Do not rerun prepare() on resize unless text or typography changed.",
            ],
        ),
        "fixed-lines": Recommendation(
            goal="fixed-lines",
            surface=surface,
            primary_apis=[
                "prepareWithSegments(text, font, options)",
                "layoutWithLines(prepared, maxWidth, lineHeight)",
            ],
            helper_apis=[],
            reason="Use the rich package-facing API when the caller needs concrete line strings at a fixed width.",
            reference_files=[
                "reference/public-api.md",
                "reference/whitespace-and-breaks.md",
                "reference/script-and-browser-caveats.md",
                "reference/integration-lifecycle.md",
            ],
            invalidates_prepare_on=["text", "font", "whiteSpace", "locale"],
            invalidates_layout_on=["maxWidth", "lineHeight"],
            questions=COMMON_QUESTIONS,
            notes=[
                "Prefer this over manual string slicing.",
                "The returned lines also include widths and cursors.",
            ],
        ),
        "geometry": Recommendation(
            goal="geometry",
            surface=surface,
            primary_apis=[
                "prepareWithSegments(text, font, options)",
                "walkLineRanges(prepared, maxWidth, onLine)",
            ],
            helper_apis=["layoutWithLines(prepared, maxWidth, lineHeight)"],
            reason="Avoid materializing line text when the caller only needs geometry or cursors.",
            reference_files=[
                "reference/public-api.md",
                "reference/integration-lifecycle.md",
            ],
            invalidates_prepare_on=["text", "font", "whiteSpace", "locale"],
            invalidates_layout_on=["maxWidth", "lineHeight"],
            questions=COMMON_QUESTIONS,
            notes=[
                "Good for shrink-wrap calculations and repeated width probes.",
                "Call layoutWithLines() later only if the final code needs actual line strings.",
            ],
        ),
        "variable-width": Recommendation(
            goal="variable-width",
            surface=surface,
            primary_apis=[
                "prepareWithSegments(text, font, options)",
                "layoutNextLine(prepared, cursor, maxWidth)",
            ],
            helper_apis=[],
            reason="Use the iterator-like API when width changes from line to line.",
            reference_files=[
                "reference/public-api.md",
                "reference/whitespace-and-breaks.md",
                "reference/script-and-browser-caveats.md",
                "reference/integration-lifecycle.md",
            ],
            invalidates_prepare_on=["text", "font", "whiteSpace", "locale"],
            invalidates_layout_on=["maxWidth", "lineHeight"],
            questions=COMMON_QUESTIONS,
            notes=[
                "Advance with line.end after each emitted line.",
                "Useful for flowing around images or non-rectangular regions.",
            ],
        ),
        "shrinkwrap": Recommendation(
            goal="shrinkwrap",
            surface=surface,
            primary_apis=[
                "prepareWithSegments(text, font, options)",
                "walkLineRanges(prepared, maxWidth, onLine)",
            ],
            helper_apis=["layoutWithLines(prepared, maxWidth, lineHeight)"],
            reason="Start with geometry-only line walks when searching for a tight container width.",
            reference_files=[
                "reference/public-api.md",
                "reference/integration-lifecycle.md",
            ],
            invalidates_prepare_on=["text", "font", "whiteSpace", "locale"],
            invalidates_layout_on=["maxWidth", "lineHeight"],
            questions=COMMON_QUESTIONS,
            notes=[
                "Combine repeated walkLineRanges() probes with a width-search strategy.",
                "Run layoutWithLines() once after choosing the final width.",
            ],
        ),
        "profile": Recommendation(
            goal="profile",
            surface=surface,
            primary_apis=["profilePrepare(text, font, options)"],
            helper_apis=["prepare(text, font, options)", "prepareWithSegments(text, font, options)"],
            reason="Use the diagnostic export when the question is about prepare-phase cost or segment counts.",
            reference_files=[
                "reference/internal-exports.md",
                "reference/troubleshooting.md",
                "reference/validation-playbook.md",
            ],
            invalidates_prepare_on=["text", "font", "whiteSpace", "locale"],
            invalidates_layout_on=[],
            questions=[
                "Am I diagnosing prepare cost rather than implementing ordinary layout?",
                "Do I need timing and segment counts, or only the normal package-facing API?",
                "Am I holding prepare inputs fixed while measuring?",
            ],
            notes=[
                "Treat profilePrepare() as a diagnostic export, not a rendering hot-path primitive.",
                "Use it to separate analysis cost from measurement cost.",
            ],
        ),
        "correctness": Recommendation(
            goal="correctness",
            surface=surface,
            primary_apis=["depends on the exported path under dispute"],
            helper_apis=[
                "prepare(text, font, options)",
                "prepareWithSegments(text, font, options)",
                "layout(prepared, maxWidth, lineHeight)",
                "layoutWithLines(prepared, maxWidth, lineHeight)",
                "layoutNextLine(prepared, cursor, maxWidth)",
                "walkLineRanges(prepared, maxWidth, onLine)",
            ],
            reason="Use this path when the main question is whether a behavior is a valid contract, a regression, or an integration mistake.",
            reference_files=[
                "reference/first-principles.md",
                "reference/public-api.md",
                "reference/behavior-contracts.md",
                "reference/troubleshooting.md",
                "reference/validation-playbook.md",
            ],
            invalidates_prepare_on=["text", "font", "whiteSpace", "locale"],
            invalidates_layout_on=["maxWidth", "lineHeight"],
            questions=[
                "Which exact semantic contract is being disputed?",
                "Can I reproduce the issue with the exported APIs before touching internals?",
                "Is the failure in segmentation, measurement, line walking, or line materialization?",
            ],
            notes=[
                "Use the smallest repro that still exercises the claimed contract.",
                "Compare the plain and rich exported APIs before assuming an internal module is wrong.",
            ],
        ),
        "cache-locale": Recommendation(
            goal="cache-locale",
            surface=surface,
            primary_apis=["setLocale(locale?)", "clearCache()"],
            helper_apis=["prepare(text, font, options)", "prepareWithSegments(text, font, options)"],
            reason="Use helper APIs deliberately when locale-sensitive segmentation or cache lifecycle is the real concern.",
            reference_files=[
                "reference/first-principles.md",
                "reference/public-api.md",
                "reference/whitespace-and-breaks.md",
                "reference/script-and-browser-caveats.md",
                "reference/integration-lifecycle.md",
                "reference/troubleshooting.md",
            ],
            invalidates_prepare_on=["text", "font", "whiteSpace", "locale"],
            invalidates_layout_on=["maxWidth", "lineHeight"],
            questions=COMMON_QUESTIONS,
            notes=[
                "setLocale() affects future prepare calls only and clears caches.",
                "clearCache() is for intentional cache release, not defensive hot-path usage.",
            ],
        ),
        "upstream-internals": Recommendation(
            goal="upstream-internals",
            surface=surface,
            primary_apis=["source modules: analysis.ts, measurement.ts, line-break.ts, bidi.ts"],
            helper_apis=["profilePrepare(text, font, options)", "prepareWithSegments(text, font, options)"],
            reason="Use this path only when the task explicitly requires upstream source changes or deep diagnostics inside the cloned repo.",
            reference_files=[
                "reference/internal-exports.md",
                "reference/first-principles.md",
                "reference/behavior-contracts.md",
                "reference/troubleshooting.md",
                "reference/validation-playbook.md",
            ],
            invalidates_prepare_on=["text", "font", "whiteSpace", "locale"],
            invalidates_layout_on=["maxWidth", "lineHeight"],
            questions=[
                "Why is the normal package-facing API insufficient?",
                "Am I modifying the upstream repo rather than just consuming the package?",
                "Do I need internal visibility or only a correct app integration?",
            ],
            notes=[
                "These source modules are not normal package-public import targets.",
                "Be explicit about the invariant you are trying to preserve before changing internals.",
            ],
        ),
        "diagnostics": Recommendation(
            goal="diagnostics",
            surface=surface,
            primary_apis=["depends on the failing path"],
            helper_apis=["profilePrepare(text, font, options)", "setLocale(locale?)", "clearCache()"],
            reason="Start by identifying whether the issue is lifecycle, behavior envelope, browser caveat, or upstream canary behavior.",
            reference_files=[
                "reference/first-principles.md",
                "reference/behavior-contracts.md",
                "reference/whitespace-and-breaks.md",
                "reference/script-and-browser-caveats.md",
                "reference/troubleshooting.md",
                "reference/validation-playbook.md",
            ],
            invalidates_prepare_on=["text", "font", "whiteSpace", "locale"],
            invalidates_layout_on=["maxWidth", "lineHeight"],
            questions=[
                "Is this an integration mismatch or a real engine bug?",
                "Is this in a known canary area before I try to patch it?",
                "What is the lightest validation that can falsify my current theory?",
            ],
            notes=[
                "Verify font, lineHeight, width, whitespace mode, and locale before suspecting a library defect.",
                "Separate integration mismatch from true engine limitations or canary behavior.",
            ],
        ),
    }

    recommendation = base[goal]
    reference_files = list(recommendation.reference_files)
    notes = list(recommendation.notes)
    reference_files, notes = apply_surface(surface, reference_files, notes)

    if preserve_whitespace:
        notes.append("Pass options = {'whiteSpace': 'pre-wrap'} to preserve spaces, tabs, and hard breaks.")
    if locale_sensitive:
        notes.append("Call setLocale(locale) before preparing new text; it clears shared caches.")
    if goal != "upstream-internals":
        notes.append("Keep the font shorthand and lineHeight synchronized with the real renderer.")

    return Recommendation(
        goal=recommendation.goal,
        surface=surface,
        primary_apis=recommendation.primary_apis,
        helper_apis=recommendation.helper_apis,
        reason=recommendation.reason,
        reference_files=reference_files,
        invalidates_prepare_on=recommendation.invalidates_prepare_on,
        invalidates_layout_on=recommendation.invalidates_layout_on,
        questions=recommendation.questions,
        notes=notes,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend a Pretext API path.")
    parser.add_argument(
        "--goal",
        required=True,
        choices=[
            "height",
            "fixed-lines",
            "geometry",
            "variable-width",
            "shrinkwrap",
            "profile",
            "correctness",
            "cache-locale",
            "upstream-internals",
            "diagnostics",
        ],
        help="Integration or diagnostic goal to optimize for.",
    )
    parser.add_argument(
        "--surface",
        choices=["generic", "react-dom", "custom-renderer", "package", "upstream"],
        default="generic",
        help="Optional integration surface used to narrow the recommended references and guardrails.",
    )
    parser.add_argument(
        "--preserve-whitespace",
        action="store_true",
        help="Include pre-wrap guidance for spaces, tabs, and hard breaks.",
    )
    parser.add_argument(
        "--locale-sensitive",
        action="store_true",
        help="Include locale guidance for segmentation-sensitive text.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format.",
    )
    args = parser.parse_args()

    recommendation = build_recommendation(
        goal=args.goal,
        surface=args.surface,
        preserve_whitespace=args.preserve_whitespace,
        locale_sensitive=args.locale_sensitive,
    )

    if args.format == "json":
        print(json.dumps(asdict(recommendation), indent=2))
        return 0

    print(f"Goal: {recommendation.goal}")
    print(f"Surface: {recommendation.surface}")
    print(f"Primary APIs: {', '.join(recommendation.primary_apis)}")
    print(f"Helper APIs: {', '.join(recommendation.helper_apis) if recommendation.helper_apis else '(none)'}")
    print(f"Reason: {recommendation.reason}")
    print(f"Reference files: {', '.join(recommendation.reference_files)}")
    print(
        f"Re-prepare on: {', '.join(recommendation.invalidates_prepare_on) if recommendation.invalidates_prepare_on else '(none)'}"
    )
    print(
        f"Re-layout on: {', '.join(recommendation.invalidates_layout_on) if recommendation.invalidates_layout_on else '(none)'}"
    )
    print("Questions:")
    for question in recommendation.questions:
        print(f"- {question}")
    print("Notes:")
    for note in recommendation.notes:
        print(f"- {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
