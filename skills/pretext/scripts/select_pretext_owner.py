#!/usr/bin/env python3
"""Recommend the owning upstream module for a Pretext issue."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class OwnershipRecommendation:
    issue: str
    primary_module: str
    secondary_modules: list[str]
    first_incorrect_state: str
    reason: str
    reference_files: list[str]
    validation_area: str
    notes: list[str]


CATALOG: dict[str, OwnershipRecommendation] = {
    "segmentation": OwnershipRecommendation(
        issue="segmentation",
        primary_module="pretext/src/analysis.ts",
        secondary_modules=["pretext/src/layout.ts", "pretext/src/layout.test.ts"],
        first_incorrect_state="Prepared segments or segment kinds are wrong before line walking begins.",
        reason="Segmentation, whitespace normalization, locale-sensitive tokenization, and chunk construction originate in analysis.ts.",
        reference_files=[
            "reference/internal-architecture.md",
            "reference/behavior-contracts.md",
            "reference/whitespace-and-breaks.md",
        ],
        validation_area="analysis",
        notes=[
            "Prove the segment stream is wrong before patching line-break.ts.",
            "If the issue is script- or punctuation-specific, also load script-and-browser-caveats.md.",
        ],
    ),
    "whitespace": OwnershipRecommendation(
        issue="whitespace",
        primary_module="pretext/src/analysis.ts",
        secondary_modules=["pretext/src/line-break.ts", "pretext/src/layout.test.ts"],
        first_incorrect_state="Whitespace mode or segment-kind classification is wrong before layout walks the prepared state.",
        reason="Whitespace normalization, preserved-space handling, tabs, hard breaks, and zero-width-break insertion begin in analysis.ts.",
        reference_files=[
            "reference/internal-architecture.md",
            "reference/behavior-contracts.md",
            "reference/whitespace-and-breaks.md",
        ],
        validation_area="analysis",
        notes=[
            "Separate preserved-space generation from tab-stop arithmetic.",
            "If segments are right but wrapping is wrong, fall through to the line-fit or tab-layout issue.",
        ],
    ),
    "glue": OwnershipRecommendation(
        issue="glue",
        primary_module="pretext/src/analysis.ts",
        secondary_modules=["pretext/src/layout.test.ts"],
        first_incorrect_state="Punctuation or script-specific glue boundaries are wrong in the prepared segment stream.",
        reason="Punctuation glue and context-sensitive token attachment are preprocessing rules, not hot-path line-walking rules.",
        reference_files=[
            "reference/internal-architecture.md",
            "reference/behavior-contracts.md",
            "reference/script-and-browser-caveats.md",
        ],
        validation_area="analysis",
        notes=[
            "Do not patch line-break.ts until the prepared segments are demonstrably correct.",
            "Be skeptical of one-off rules in known canary areas.",
        ],
    ),
    "measurement-width": OwnershipRecommendation(
        issue="measurement-width",
        primary_module="pretext/src/measurement.ts",
        secondary_modules=["pretext/src/layout.ts", "pretext/src/layout.test.ts"],
        first_incorrect_state="Measured segment widths or breakable-run width metadata are wrong before layout arithmetic runs.",
        reason="Canvas measurement, grapheme widths, prefix widths, and measurement caches live in measurement.ts.",
        reference_files=[
            "reference/internal-architecture.md",
            "reference/internal-exports.md",
            "reference/script-and-browser-caveats.md",
        ],
        validation_area="measurement",
        notes=[
            "Verify font mismatch first before changing measurement logic.",
            "If only browser fit policy is suspect, inspect engine-profile behavior rather than generic width code first.",
        ],
    ),
    "emoji-correction": OwnershipRecommendation(
        issue="emoji-correction",
        primary_module="pretext/src/measurement.ts",
        secondary_modules=["pretext/src/layout.ts", "pretext/src/layout.test.ts"],
        first_incorrect_state="Emoji width correction or engine-profile measurement state is wrong before layout consumes widths.",
        reason="Emoji correction detection and cached measurement-state policy live in measurement.ts.",
        reference_files=[
            "reference/internal-architecture.md",
            "reference/script-and-browser-caveats.md",
            "reference/troubleshooting.md",
        ],
        validation_area="measurement",
        notes=[
            "Treat macOS emoji width issues as measurement policy questions, not line-break questions.",
            "Use probe or accuracy surfaces before broad refactors.",
        ],
    ),
    "line-fit": OwnershipRecommendation(
        issue="line-fit",
        primary_module="pretext/src/line-break.ts",
        secondary_modules=["pretext/src/layout.ts", "pretext/src/layout.test.ts"],
        first_incorrect_state="Line boundaries are wrong even though the prepared segments and widths are already correct.",
        reason="Line counting, fit decisions, soft-hyphen breaks, and geometry walks are arithmetic responsibilities of line-break.ts.",
        reference_files=[
            "reference/internal-architecture.md",
            "reference/behavior-contracts.md",
            "reference/whitespace-and-breaks.md",
        ],
        validation_area="line-break",
        notes=[
            "Prove prepared widths and segment kinds are already correct before patching this module.",
            "Use correctness contracts to test whether streamed and batched layouts diverge.",
        ],
    ),
    "tab-layout": OwnershipRecommendation(
        issue="tab-layout",
        primary_module="pretext/src/line-break.ts",
        secondary_modules=["pretext/src/analysis.ts", "pretext/src/layout.test.ts"],
        first_incorrect_state="Prepared tab segments exist, but tab-stop advance or line-fit behavior is wrong during layout.",
        reason="Tab-stop arithmetic and tab handling during line walking live in line-break.ts once tab segments already exist.",
        reference_files=[
            "reference/internal-architecture.md",
            "reference/behavior-contracts.md",
            "reference/whitespace-and-breaks.md",
        ],
        validation_area="line-break",
        notes=[
            "If tabs are missing from the prepared stream entirely, switch back to the whitespace issue.",
            "Pre-wrap tab behavior should be judged against the behavior contracts first.",
        ],
    ),
    "streamed-lines": OwnershipRecommendation(
        issue="streamed-lines",
        primary_module="pretext/src/line-break.ts",
        secondary_modules=["pretext/src/layout.ts", "pretext/src/layout.test.ts"],
        first_incorrect_state="Range stepping diverges from batched line walking before text materialization happens.",
        reason="Alignment between countPreparedLines(), walkPreparedLines(), and range stepping is a line-break.ts responsibility.",
        reference_files=[
            "reference/internal-architecture.md",
            "reference/behavior-contracts.md",
            "reference/internal-exports.md",
        ],
        validation_area="line-break",
        notes=[
            "Only blame layout.ts after confirming the line ranges themselves are wrong.",
            "Use the cross-API parity contracts as the first falsification step.",
        ],
    ),
    "rich-line-materialization": OwnershipRecommendation(
        issue="rich-line-materialization",
        primary_module="pretext/src/layout.ts",
        secondary_modules=["pretext/src/line-break.ts", "pretext/src/layout.test.ts"],
        first_incorrect_state="Line ranges are right, but the materialized line text or cursor reconstruction is wrong.",
        reason="layout.ts owns materializing LayoutLine text from line ranges and rich prepared data.",
        reference_files=[
            "reference/internal-architecture.md",
            "reference/behavior-contracts.md",
            "reference/internal-exports.md",
        ],
        validation_area="layout-api",
        notes=[
            "Separate range-generation bugs from text-reconstruction bugs.",
            "Soft-hyphen display issues often belong here if the ranges are already correct.",
        ],
    ),
    "public-api-shape": OwnershipRecommendation(
        issue="public-api-shape",
        primary_module="pretext/src/layout.ts",
        secondary_modules=["pretext/README.md", "pretext/package.json"],
        first_incorrect_state="The exported API shape or public contract is wrong at the package surface.",
        reason="layout.ts owns the exported package-facing functions and types.",
        reference_files=[
            "reference/public-api.md",
            "reference/package-workflows.md",
            "reference/internal-architecture.md",
        ],
        validation_area="layout-api",
        notes=[
            "If consumers are affected, validate the package contract and smoke tests, not just source compilation.",
            "Distinguish API-shape changes from deep behavior changes.",
        ],
    ),
    "cache-locale-wiring": OwnershipRecommendation(
        issue="cache-locale-wiring",
        primary_module="pretext/src/layout.ts",
        secondary_modules=["pretext/src/analysis.ts", "pretext/src/measurement.ts"],
        first_incorrect_state="Exported cache-reset or locale-reset behavior is wired incorrectly at the package surface.",
        reason="layout.ts owns clearCache() and setLocale() as the public wiring layer over analysis and measurement caches.",
        reference_files=[
            "reference/public-api.md",
            "reference/behavior-contracts.md",
            "reference/internal-architecture.md",
        ],
        validation_area="layout-api",
        notes=[
            "If locale-sensitive segmentation itself is wrong, analysis.ts may still be the deeper owner.",
            "Start by checking whether the exported contract is broken before editing deeper modules.",
        ],
    ),
    "bidi-levels": OwnershipRecommendation(
        issue="bidi-levels",
        primary_module="pretext/src/bidi.ts",
        secondary_modules=["pretext/src/layout.ts", "pretext/src/layout.test.ts"],
        first_incorrect_state="Rich-path segment bidi metadata is wrong while ordinary line counting may still look correct.",
        reason="Segment-level bidi metadata for custom rendering lives in bidi.ts.",
        reference_files=[
            "reference/internal-architecture.md",
            "reference/internal-exports.md",
            "reference/script-and-browser-caveats.md",
        ],
        validation_area="bidi",
        notes=[
            "Do not patch bidi.ts for ordinary height-only problems.",
            "Use a mixed-direction repro before broad changes.",
        ],
    ),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend the owning upstream module for a Pretext issue.")
    parser.add_argument(
        "--issue",
        required=True,
        choices=sorted(CATALOG.keys()),
        help="The first-principles issue category.",
    )
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args()

    recommendation = CATALOG[args.issue]
    if args.format == "json":
        print(json.dumps(asdict(recommendation), indent=2))
        return 0

    print(f"Issue: {recommendation.issue}")
    print(f"Primary module: {recommendation.primary_module}")
    print(
        f"Secondary modules: {', '.join(recommendation.secondary_modules) if recommendation.secondary_modules else '(none)'}"
    )
    print(f"First incorrect state: {recommendation.first_incorrect_state}")
    print(f"Reason: {recommendation.reason}")
    print(f"Reference files: {', '.join(recommendation.reference_files)}")
    print(f"Validation area: {recommendation.validation_area}")
    print("Notes:")
    for note in recommendation.notes:
        print(f"- {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
