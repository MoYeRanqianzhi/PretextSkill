---
name: pretext
description: Work with the `@chenglou/pretext` library for DOM-free text measurement and multiline text layout. Use when integrating Pretext into JavaScript or TypeScript code, choosing between `prepare()` and the rich line APIs, preserving `pre-wrap` whitespace, handling locale-sensitive segmentation, or validating browser accuracy and performance for virtualization, Canvas, SVG, WebGL, shrink-wrap widths, and variable-width line flows.
---

# pretext

Treat Pretext as a two-phase engine: prepare text once, then lay it out as often as needed.

## Start Here

1. Classify the request before writing code:
   - Use `prepare()` plus `layout()` for paragraph height or line-count estimation.
   - Use `prepareWithSegments()` plus `layoutWithLines()` when the caller needs concrete line strings at one fixed width.
   - Use `prepareWithSegments()` plus `walkLineRanges()` when the caller needs geometry only and wants to avoid materializing line text.
   - Use `prepareWithSegments()` plus `layoutNextLine()` when width changes from line to line.
2. Keep typography synchronized with the real renderer. Treat mismatched `font` or `lineHeight` as the first suspected bug.
3. Reuse prepared handles. Re-run `prepare()` only when text, font, locale, or whitespace mode changes. Re-run layout functions when width or line height changes.
4. Pass `{ whiteSpace: 'pre-wrap' }` for textarea-like text or any request that must preserve spaces, tabs, or hard breaks.
5. Call `setLocale()` before preparing new text when segmentation must be locale-aware. Remember that `setLocale()` clears caches and only affects future prepared values.

## Workflow

1. Read [reference/api-selection.md](reference/api-selection.md) to map the task to the correct API surface.
2. Read [reference/integration-patterns.md](reference/integration-patterns.md) when implementing application code or adapting Pretext to a rendering path.
3. Read [reference/validation-playbook.md](reference/validation-playbook.md) when debugging accuracy, whitespace, locale behavior, or performance.
4. Optionally run `python scripts/select_pretext_api.py --goal ...` for a deterministic recommendation when the request is ambiguous.

## Output Rules

1. Prefer examples that cache prepared state and only recompute the cheapest stage required.
2. Always call out the required `font`, `lineHeight`, width source, whitespace mode, and locale assumptions.
3. Separate integration mistakes from library limitations:
   - API mismatch
   - typography mismatch
   - whitespace or locale mismatch
   - genuine engine limitation or upstream bug
4. If the request is about validation inside the upstream repo, prefer the existing Bun commands before inventing one-off diagnostics.
