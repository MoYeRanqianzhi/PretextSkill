# API Selection

Use this file when the request is about choosing the correct Pretext API surface.

## Decision Table

| Goal | Use | Why | Watch for |
| --- | --- | --- | --- |
| Estimate paragraph height or line count | `prepare()` + `layout()` | Cheapest hot path after preparation | Reuse prepared state; keep `font` and `lineHeight` aligned with real rendering |
| Render concrete lines at one fixed width | `prepareWithSegments()` + `layoutWithLines()` | Returns line text, widths, and cursors | Slightly richer output than plain height measurement |
| Compute geometry without building line strings | `prepareWithSegments()` + `walkLineRanges()` | Lets the caller inspect widths and cursors only | Best for shrink-wrap or repeated boundary checks |
| Lay out one line at a time with width changes per row | `prepareWithSegments()` + `layoutNextLine()` | Supports flowing around floats or non-rectangular layouts | Maintain and advance the returned cursor correctly |
| Preserve spaces, tabs, and hard breaks | Add `{ whiteSpace: 'pre-wrap' }` to `prepare` or `prepareWithSegments` | Mirrors textarea-like input behavior | Tabs follow browser-style `tab-size: 8` |
| Change segmentation rules for a locale | `setLocale(locale)` before preparing text | Affects future preparation and clears caches | Do not expect existing prepared values to mutate |

## Core Principle

Pretext is efficient because preparation and layout are different costs:

- `prepare()` or `prepareWithSegments()` performs normalization, segmentation, glue rules, and measurement.
- `layout()` and the rich line APIs reuse prepared measurements and only recompute line placement.

If the code calls `prepare()` on resize, treat that as a likely design bug unless text or typography actually changed.

## Fast Heuristics

- Need only `height` or `lineCount`: stay on `prepare()` + `layout()`.
- Need actual line text: switch to `prepareWithSegments()`.
- Need variable-width rows: use `layoutNextLine()`.
- Need shrink-wrap width search or aggregate geometry: use `walkLineRanges()` first, then `layoutWithLines()` once a width is chosen.

## Important Inputs

Every integration should make these explicit:

- text source
- `font` shorthand string
- `lineHeight`
- width source
- `whiteSpace` mode
- locale, if non-default segmentation matters
