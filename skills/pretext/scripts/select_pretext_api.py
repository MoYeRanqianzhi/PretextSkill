#!/usr/bin/env python3
"""Recommend a Pretext API path for a concrete integration goal."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Recommendation:
    goal: str
    prepare_api: str
    layout_api: str
    reason: str
    notes: list[str]


def build_recommendation(goal: str, preserve_whitespace: bool, locale_sensitive: bool) -> Recommendation:
    base: dict[str, Recommendation] = {
        "height": Recommendation(
            goal="height",
            prepare_api="prepare(text, font, options)",
            layout_api="layout(prepared, maxWidth, lineHeight)",
            reason="Use the lightest API when the caller only needs height or line count.",
            notes=[
                "Reuse prepared state across width changes.",
                "Do not rerun prepare() on resize unless text or typography changed.",
            ],
        ),
        "fixed-lines": Recommendation(
            goal="fixed-lines",
            prepare_api="prepareWithSegments(text, font, options)",
            layout_api="layoutWithLines(prepared, maxWidth, lineHeight)",
            reason="Use the rich API when the caller needs concrete line strings at a fixed width.",
            notes=[
                "Prefer this over manual string slicing.",
                "The returned lines also include widths and cursors.",
            ],
        ),
        "geometry": Recommendation(
            goal="geometry",
            prepare_api="prepareWithSegments(text, font, options)",
            layout_api="walkLineRanges(prepared, maxWidth, onLine)",
            reason="Avoid materializing line text when the caller only needs geometry or cursors.",
            notes=[
                "Good for shrink-wrap calculations and repeated width probes.",
                "Call layoutWithLines() later only if the final code needs actual line strings.",
            ],
        ),
        "variable-width": Recommendation(
            goal="variable-width",
            prepare_api="prepareWithSegments(text, font, options)",
            layout_api="layoutNextLine(prepared, cursor, maxWidth)",
            reason="Use the iterator-like API when width changes from line to line.",
            notes=[
                "Advance with line.end after each emitted line.",
                "Useful for flowing around images or non-rectangular regions.",
            ],
        ),
        "shrinkwrap": Recommendation(
            goal="shrinkwrap",
            prepare_api="prepareWithSegments(text, font, options)",
            layout_api="walkLineRanges(prepared, maxWidth, onLine)",
            reason="Start with geometry-only line walks when searching for a tight container width.",
            notes=[
                "Combine repeated walkLineRanges() probes with a width-search strategy.",
                "Run layoutWithLines() once after choosing the final width.",
            ],
        ),
        "diagnostics": Recommendation(
            goal="diagnostics",
            prepare_api="depends on the failing path",
            layout_api="depends on the failing path",
            reason="Start by identifying whether the issue is height-only, fixed-width rich layout, or variable-width streaming.",
            notes=[
                "Verify font, lineHeight, width, whitespace mode, and locale before suspecting a library defect.",
                "Read reference/validation-playbook.md for the upstream commands and invariants.",
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
        prepare_api=recommendation.prepare_api,
        layout_api=recommendation.layout_api,
        reason=recommendation.reason,
        notes=notes,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend a Pretext API path.")
    parser.add_argument(
        "--goal",
        required=True,
        choices=["height", "fixed-lines", "geometry", "variable-width", "shrinkwrap", "diagnostics"],
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
    print(f"Prepare API: {recommendation.prepare_api}")
    print(f"Layout API: {recommendation.layout_api}")
    print(f"Reason: {recommendation.reason}")
    print("Notes:")
    for note in recommendation.notes:
        print(f"- {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
