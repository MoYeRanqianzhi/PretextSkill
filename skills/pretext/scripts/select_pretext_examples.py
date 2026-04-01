#!/usr/bin/env python3
"""Recommend vetted external Pretext implementations for code precedent."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from select_pretext_api import SUPPORTED_GOALS, SUPPORTED_SURFACES


STAR_SNAPSHOT_DATE = "2026-04-01"

SUPPORTED_PATTERNS = [
    "height-cache",
    "adapter-module",
    "framework-wrapper",
    "fixed-lines",
    "streamed-lines",
    "document-reader",
    "pdf-text-layer",
    "custom-renderer",
    "terminal-renderer",
    "experimental-canvas",
    "backend-port",
    "text-fitting",
]


@dataclass(frozen=True)
class ExampleReference:
    repo: str
    stars: int
    repo_url: str
    source_file: str
    source_url: str
    goals: list[str]
    surfaces: list[str]
    patterns: list[str]
    main_apis: list[str]
    reason: str
    notes: list[str]


CATALOG = [
    ExampleReference(
        repo="mayneyao/eidos",
        stars=3095,
        repo_url="https://github.com/mayneyao/eidos",
        source_file="apps/web-app/components/table/views/gallery/utils.ts",
        source_url="https://github.com/mayneyao/eidos/blob/main/apps/web-app/components/table/views/gallery/utils.ts",
        goals=["height"],
        surfaces=["generic", "react-dom"],
        patterns=["height-cache"],
        main_apis=["prepare", "layout"],
        reason="Real product use of prepared height caching for gallery-card sizing.",
        notes=[
            "High-signal product reference for height prediction.",
            "Useful when the task is virtualization or card measurement, not rich-line rendering.",
        ],
    ),
    ExampleReference(
        repo="CoWork-OS/CoWork-OS",
        stars=184,
        repo_url="https://github.com/CoWork-OS/CoWork-OS",
        source_file="src/renderer/utils/pretext-adapter.ts",
        source_url="https://github.com/CoWork-OS/CoWork-OS/blob/main/src/renderer/utils/pretext-adapter.ts",
        goals=["height", "cache-locale"],
        surfaces=["react-dom"],
        patterns=["height-cache", "adapter-module"],
        main_apis=["prepare", "layout", "clearCache"],
        reason="Centralized adapter that owns font resolution, prepared caches, and invalidation.",
        notes=[
            "Best precedent when the task needs one local facade around Pretext.",
            "Shows a narrow owner module rather than many direct imports.",
        ],
    ),
    ExampleReference(
        repo="PetrGuan/Prelayout",
        stars=12,
        repo_url="https://github.com/PetrGuan/Prelayout",
        source_file="src/prepare.ts",
        source_url="https://github.com/PetrGuan/Prelayout/blob/main/src/prepare.ts",
        goals=["height"],
        surfaces=["generic", "react-dom"],
        patterns=["height-cache", "adapter-module"],
        main_apis=["prepare"],
        reason="Lifts Pretext preparation into structured component-height prediction for virtual lists.",
        notes=[
            "Useful when a whole card schema must be prepared once and laid out many times.",
            "Pairs well with height-only UI or virtualization tasks.",
        ],
    ),
    ExampleReference(
        repo="LucasBassetti/react-pretext",
        stars=2,
        repo_url="https://github.com/LucasBassetti/react-pretext",
        source_file="src/core/layout.ts",
        source_url="https://github.com/LucasBassetti/react-pretext/blob/main/src/core/layout.ts",
        goals=["height", "fixed-lines", "cache-locale"],
        surfaces=["react-dom"],
        patterns=["adapter-module", "framework-wrapper"],
        main_apis=["prepare", "layout", "prepareWithSegments", "layoutWithLines", "setLocale"],
        reason="Headless React adapter that separates height-only and rich-line paths and adds SSR fallback.",
        notes=[
            "Good precedent for wrapper design.",
            "Low-star but still useful because the adapter boundary is explicit.",
        ],
    ),
    ExampleReference(
        repo="jonsnowljs/usePretext",
        stars=1,
        repo_url="https://github.com/jonsnowljs/usePretext",
        source_file="src/usePretext.ts",
        source_url="https://github.com/jonsnowljs/usePretext/blob/main/src/usePretext.ts",
        goals=["height", "fixed-lines", "cache-locale"],
        surfaces=["react-dom"],
        patterns=["adapter-module", "framework-wrapper"],
        main_apis=["setLocale", "prepare", "prepareWithSegments", "layout", "layoutWithLines", "clearCache"],
        reason="Framework composable with resize observation and optional rich-line output.",
        notes=[
            "Useful when the task is a reusable wrapper rather than one component.",
            "Shows how to expose width, prepared state, and refresh hooks cleanly.",
        ],
    ),
    ExampleReference(
        repo="xiaoiver/infinite-canvas-tutorial",
        stars=959,
        repo_url="https://github.com/xiaoiver/infinite-canvas-tutorial",
        source_file="packages/ecs/src/systems/ComputeTextMetrics.ts",
        source_url="https://github.com/xiaoiver/infinite-canvas-tutorial/blob/main/packages/ecs/src/systems/ComputeTextMetrics.ts",
        goals=["fixed-lines"],
        surfaces=["custom-renderer"],
        patterns=["fixed-lines", "custom-renderer"],
        main_apis=["prepareWithSegments", "layoutWithLines"],
        reason="High-signal renderer-side text layout with bidi and script-specific handling.",
        notes=[
            "Strong precedent for Canvas or custom-renderer text layout.",
            "Useful when renderer correctness matters more than DOM integration.",
        ],
    ),
    ExampleReference(
        repo="codehz/chat-layout",
        stars=2,
        repo_url="https://github.com/codehz/chat-layout",
        source_file="src/text.ts",
        source_url="https://github.com/codehz/chat-layout/blob/main/src/text.ts",
        goals=["fixed-lines"],
        surfaces=["custom-renderer"],
        patterns=["fixed-lines", "custom-renderer"],
        main_apis=["prepareWithSegments", "layoutWithLines"],
        reason="Compact chat-layout example for first-line extraction and line materialization.",
        notes=[
            "Useful when the task is chat bubbles or subtitle-like line fitting.",
        ],
    ),
    ExampleReference(
        repo="beorn/silvery",
        stars=4,
        repo_url="https://github.com/beorn/silvery",
        source_file="packages/ag-react/src/ui/canvas/pretext-measurer.ts",
        source_url="https://github.com/beorn/silvery/blob/main/packages/ag-react/src/ui/canvas/pretext-measurer.ts",
        goals=["fixed-lines", "geometry"],
        surfaces=["custom-renderer"],
        patterns=["custom-renderer", "terminal-renderer"],
        main_apis=["prepareWithSegments", "layoutWithLines"],
        reason="Pretext-backed pixel measurer for terminal-style UI layout.",
        notes=[
            "Useful for non-DOM renderer integration and grapheme-aware width slicing.",
        ],
    ),
    ExampleReference(
        repo="0xNyk/pretext-playground",
        stars=15,
        repo_url="https://github.com/0xNyk/pretext-playground",
        source_file="src/dragon.ts",
        source_url="https://github.com/0xNyk/pretext-playground/blob/main/src/dragon.ts",
        goals=["fixed-lines"],
        surfaces=["custom-renderer"],
        patterns=["experimental-canvas", "fixed-lines", "custom-renderer"],
        main_apis=["prepareWithSegments", "layoutWithLines"],
        reason="Canvas-heavy experimental scene that still keeps Pretext as the line-fitting source of truth.",
        notes=[
            "Useful as a cautionary example for frame-loop placement and prepared-state reuse.",
        ],
    ),
    ExampleReference(
        repo="alpeshvas/pretext-pdfjs",
        stars=0,
        repo_url="https://github.com/alpeshvas/pretext-pdfjs",
        source_file="src/pretext-text-layer.js",
        source_url="https://github.com/alpeshvas/pretext-pdfjs/blob/main/src/pretext-text-layer.js",
        goals=["fixed-lines"],
        surfaces=["document-reader"],
        patterns=["document-reader", "pdf-text-layer"],
        main_apis=["prepareWithSegments", "layoutWithLines"],
        reason="Pretext-backed PDF.js text-layer adapter with reflow and measurement caching.",
        notes=[
            "Best direct precedent for PDF text layers.",
            "Low-star but highly specific to the reader surface.",
        ],
    ),
    ExampleReference(
        repo="zsh-eng/epub-reader-demo",
        stars=0,
        repo_url="https://github.com/zsh-eng/epub-reader-demo",
        source_file="src/lib/pagination/layout-text-lines.ts",
        source_url="https://github.com/zsh-eng/epub-reader-demo/blob/main/src/lib/pagination/layout-text-lines.ts",
        goals=["streamed-lines", "fixed-lines", "variable-width"],
        surfaces=["document-reader", "custom-renderer"],
        patterns=["document-reader", "streamed-lines"],
        main_apis=["layoutNextLine", "layoutWithLines", "prepareWithSegments"],
        reason="Direct precedent for pagination, streamed cursor continuation, and pre-wrap code blocks.",
        notes=[
            "Best precedent when the paragraph must continue across containers.",
            "Useful for EPUB or other reader pagination tasks.",
        ],
    ),
    ExampleReference(
        repo="heygen-com/hyperframes",
        stars=4,
        repo_url="https://github.com/heygen-com/hyperframes",
        source_file="packages/core/src/text/fitTextFontSize.ts",
        source_url="https://github.com/heygen-com/hyperframes/blob/main/packages/core/src/text/fitTextFontSize.ts",
        goals=["height"],
        surfaces=["generic"],
        patterns=["text-fitting", "height-cache"],
        main_apis=["prepare", "layout"],
        reason="Simple, clean example of repeated fit checks without rich-line materialization.",
        notes=[
            "Useful when the task is one-line fit or width-constrained title sizing.",
        ],
    ),
    ExampleReference(
        repo="skastr0/pretext-skia",
        stars=0,
        repo_url="https://github.com/skastr0/pretext-skia",
        source_file="packages/pretext-skia/README.md",
        source_url="https://github.com/skastr0/pretext-skia/blob/main/packages/pretext-skia/README.md",
        goals=["height", "fixed-lines", "geometry", "streamed-lines", "variable-width"],
        surfaces=["custom-renderer"],
        patterns=["backend-port"],
        main_apis=["prepare", "prepareWithSegments", "layout", "layoutWithLines", "walkLineRanges", "layoutNextLine"],
        reason="Useful architecture reference for porting the Pretext model to a different backend.",
        notes=[
            "Treat as a port or fork, not as a normal downstream consumer example.",
        ],
    ),
]


def matches(entry: ExampleReference, goal: str | None, surface: str | None, pattern: str | None) -> bool:
    if goal is not None and goal not in entry.goals:
        return False
    if surface is not None and surface not in entry.surfaces:
        return False
    if pattern is not None and pattern not in entry.patterns:
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend vetted external Pretext implementations for code precedent.")
    parser.add_argument("--goal", choices=SUPPORTED_GOALS, help="Optional goal used to narrow the shortlist.")
    parser.add_argument(
        "--surface",
        choices=[surface for surface in SUPPORTED_SURFACES if surface != "generic"],
        help="Optional surface used to narrow the shortlist.",
    )
    parser.add_argument("--pattern", choices=SUPPORTED_PATTERNS, help="Optional implementation pattern used to narrow the shortlist.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of matches to return.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args()

    if args.goal is None and args.surface is None and args.pattern is None:
        parser.error("at least one of --goal, --surface, or --pattern is required")

    matches_found = [
        entry for entry in CATALOG if matches(entry, args.goal, args.surface, args.pattern)
    ]
    matches_found.sort(key=lambda entry: entry.stars, reverse=True)
    matches_found = matches_found[: max(1, args.limit)]

    if args.format == "json":
        payload = {
            "star_snapshot_date": STAR_SNAPSHOT_DATE,
            "goal": args.goal,
            "surface": args.surface,
            "pattern": args.pattern,
            "matches": [asdict(entry) for entry in matches_found],
        }
        print(json.dumps(payload, indent=2))
        return 0

    print(f"Star snapshot date: {STAR_SNAPSHOT_DATE}")
    print(f"Goal: {args.goal or '(none)'}")
    print(f"Surface: {args.surface or '(none)'}")
    print(f"Pattern: {args.pattern or '(none)'}")
    print("Matches:")
    if not matches_found:
        print("- (none)")
        return 0

    for entry in matches_found:
        print(f"- {entry.repo} ({entry.stars} stars)")
        print(f"  repo: {entry.repo_url}")
        print(f"  source: {entry.source_file}")
        print(f"  source_url: {entry.source_url}")
        print(f"  main_apis: {', '.join(entry.main_apis)}")
        print(f"  reason: {entry.reason}")
        for note in entry.notes:
            print(f"  note: {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
