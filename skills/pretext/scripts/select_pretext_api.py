#!/usr/bin/env python3
"""Recommend a Pretext API path and reference set for a concrete goal."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Recommendation:
    goal: str
    primary_apis: list[str]
    helper_apis: list[str]
    reason: str
    reference_files: list[str]
    invalidates_prepare_on: list[str]
    invalidates_layout_on: list[str]
    notes: list[str]


def build_recommendation(goal: str, preserve_whitespace: bool, locale_sensitive: bool) -> Recommendation:
    base: dict[str, Recommendation] = {
        "height": Recommendation(
            goal="height",
            primary_apis=["prepare(text, font, options)", "layout(prepared, maxWidth, lineHeight)"],
            helper_apis=[],
            reason="Use the lightest API when the caller only needs height or line count.",
            reference_files=[
                "reference/first-principles.md",
                "reference/public-api.md",
                "reference/integration-lifecycle.md",
            ],
            invalidates_prepare_on=["text", "font", "whiteSpace", "locale"],
            invalidates_layout_on=["maxWidth", "lineHeight"],
            notes=[
                "Reuse prepared state across width changes.",
                "Do not rerun prepare() on resize unless text or typography changed.",
            ],
        ),
        "fixed-lines": Recommendation(
            goal="fixed-lines",
            primary_apis=[
                "prepareWithSegments(text, font, options)",
                "layoutWithLines(prepared, maxWidth, lineHeight)",
            ],
            helper_apis=[],
            reason="Use the rich API when the caller needs concrete line strings at a fixed width.",
            reference_files=[
                "reference/public-api.md",
                "reference/text-behaviors.md",
                "reference/integration-lifecycle.md",
            ],
            invalidates_prepare_on=["text", "font", "whiteSpace", "locale"],
            invalidates_layout_on=["maxWidth", "lineHeight"],
            notes=[
                "Prefer this over manual string slicing.",
                "The returned lines also include widths and cursors.",
            ],
        ),
        "geometry": Recommendation(
            goal="geometry",
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
            notes=[
                "Good for shrink-wrap calculations and repeated width probes.",
                "Call layoutWithLines() later only if the final code needs actual line strings.",
            ],
        ),
        "variable-width": Recommendation(
            goal="variable-width",
            primary_apis=[
                "prepareWithSegments(text, font, options)",
                "layoutNextLine(prepared, cursor, maxWidth)",
            ],
            helper_apis=[],
            reason="Use the iterator-like API when width changes from line to line.",
            reference_files=[
                "reference/public-api.md",
                "reference/text-behaviors.md",
                "reference/integration-lifecycle.md",
            ],
            invalidates_prepare_on=["text", "font", "whiteSpace", "locale"],
            invalidates_layout_on=["maxWidth", "lineHeight"],
            notes=[
                "Advance with line.end after each emitted line.",
                "Useful for flowing around images or non-rectangular regions.",
            ],
        ),
        "shrinkwrap": Recommendation(
            goal="shrinkwrap",
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
            notes=[
                "Combine repeated walkLineRanges() probes with a width-search strategy.",
                "Run layoutWithLines() once after choosing the final width.",
            ],
        ),
        "profile": Recommendation(
            goal="profile",
            primary_apis=["profilePrepare(text, font, options)"],
            helper_apis=["prepare(text, font, options)", "prepareWithSegments(text, font, options)"],
            reason="Use the exported diagnostic helper when the question is about prepare-phase cost or segment counts.",
            reference_files=[
                "reference/public-api.md",
                "reference/troubleshooting.md",
                "reference/validation-playbook.md",
            ],
            invalidates_prepare_on=["text", "font", "whiteSpace", "locale"],
            invalidates_layout_on=[],
            notes=[
                "Treat profilePrepare() as a diagnostic export, not a rendering hot-path primitive.",
                "Use it to separate analysis cost from measurement cost.",
            ],
        ),
        "cache-locale": Recommendation(
            goal="cache-locale",
            primary_apis=["setLocale(locale?)", "clearCache()"],
            helper_apis=["prepare(text, font, options)", "prepareWithSegments(text, font, options)"],
            reason="Use helper APIs deliberately when locale-sensitive segmentation or cache lifecycle is the real concern.",
            reference_files=[
                "reference/first-principles.md",
                "reference/public-api.md",
                "reference/integration-lifecycle.md",
                "reference/troubleshooting.md",
            ],
            invalidates_prepare_on=["text", "font", "whiteSpace", "locale"],
            invalidates_layout_on=["maxWidth", "lineHeight"],
            notes=[
                "setLocale() affects future prepare calls only and clears caches.",
                "clearCache() is for intentional cache release, not defensive hot-path usage.",
            ],
        ),
        "diagnostics": Recommendation(
            goal="diagnostics",
            primary_apis=["depends on the failing path"],
            helper_apis=["profilePrepare(text, font, options)", "setLocale(locale?)", "clearCache()"],
            reason="Start by identifying whether the issue is height-only, fixed-width rich layout, or variable-width streaming.",
            reference_files=[
                "reference/first-principles.md",
                "reference/text-behaviors.md",
                "reference/troubleshooting.md",
                "reference/validation-playbook.md",
            ],
            invalidates_prepare_on=["text", "font", "whiteSpace", "locale"],
            invalidates_layout_on=["maxWidth", "lineHeight"],
            notes=[
                "Verify font, lineHeight, width, whitespace mode, and locale before suspecting a library defect.",
                "Separate integration mismatch from true engine limitations or canary behavior.",
            ],
        ),
    }
    recommendation = base[goal]
    notes = list(recommendation.notes)
    if preserve_whitespace:
        notes.append("Pass options = {'whiteSpace': 'pre-wrap'} to preserve spaces, tabs, and hard breaks.")
    if locale_sensitive:
        notes.append("Call setLocale(locale) before preparing new text; it clears shared caches.")
    notes.append("Keep the font shorthand and lineHeight synchronized with the real renderer.")
    return Recommendation(
        goal=recommendation.goal,
        primary_apis=recommendation.primary_apis,
        helper_apis=recommendation.helper_apis,
        reason=recommendation.reason,
        reference_files=recommendation.reference_files,
        invalidates_prepare_on=recommendation.invalidates_prepare_on,
        invalidates_layout_on=recommendation.invalidates_layout_on,
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
            "cache-locale",
            "diagnostics",
        ],
        help="Integration goal to optimize for.",
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
        preserve_whitespace=args.preserve_whitespace,
        locale_sensitive=args.locale_sensitive,
    )

    if args.format == "json":
        print(json.dumps(asdict(recommendation), indent=2))
        return 0

    print(f"Goal: {recommendation.goal}")
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
    print("Notes:")
    for note in recommendation.notes:
        print(f"- {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
