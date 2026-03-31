# Public API

Use this file when the task requires exact function names, signatures, exported types, or clarity about which exports are intended for normal consumers.

## Product-Facing Exports From `src/layout.ts`

### `prepare(text, font, options?)`

- Returns: `PreparedText`
- Use for: height-only and line-count workflows
- Notes:
  - `PreparedText` is intentionally opaque
  - pair it with `layout()`

### `prepareWithSegments(text, font, options?)`

- Returns: `PreparedTextWithSegments`
- Use for: any workflow that needs concrete lines, cursors, geometry, or custom rendering
- Notes:
  - pair it with `layoutWithLines()`, `walkLineRanges()`, or `layoutNextLine()`

### `layout(prepared, maxWidth, lineHeight)`

- Returns: `LayoutResult`
- Use for: cheap repeated height and line-count layout at a fixed width
- Notes:
  - this is the hot path
  - it should remain arithmetic-only

### `layoutWithLines(prepared, maxWidth, lineHeight)`

- Returns: `LayoutLinesResult`
- Use for: fixed-width line materialization
- Notes:
  - richer than `layout()`
  - not the preferred resize hot path if only height is needed

### `walkLineRanges(prepared, maxWidth, onLine)`

- Returns: line count
- Use for: geometry-only iteration, shrink-wrap search, and width probing
- Notes:
  - avoids building line strings

### `layoutNextLine(prepared, start, maxWidth)`

- Returns: `LayoutLine | null`
- Use for: variable-width per-line layout
- Notes:
  - pass the previous line's `end` cursor into the next call

### `profilePrepare(text, font, options?)`

- Returns: `PrepareProfile`
- Use for: diagnostic or benchmark-oriented timing of the prepare phase
- Notes:
  - exported in `src/layout.ts`
  - positioned by source comments as diagnostic-only, not the normal integration API

### `clearCache()`

- Use for: intentional cache release or environment reset
- Notes:
  - do not put this in normal render loops

### `setLocale(locale?)`

- Use for: future locale-sensitive preparation
- Notes:
  - affects future prepare calls only
  - clears caches internally

## Public Types

### Stable Product Types

- `PreparedText`
- `PreparedTextWithSegments`
- `LayoutCursor`
- `LayoutResult`
- `LayoutLine`
- `LayoutLineRange`
- `LayoutLinesResult`
- `PrepareProfile`
- `PrepareOptions`

### Important Rich-Path Details

`PreparedTextWithSegments` exposes more than line text:

- `segments`
- `widths`
- `kinds`
- `breakableWidths`
- `breakablePrefixWidths`
- `discretionaryHyphenWidth`
- `tabStopAdvance`
- `chunks`
- `segLevels`

Treat this as a rich escape hatch for custom rendering and diagnostics, not as a promise that normal integrations should poke every field.

## Lower-Level Exported Modules

These are real exports, but the README and `src/layout.ts` position `layout.ts` as the intended product-facing surface.

### `src/analysis.ts`

- Exports whitespace modes, segment kinds, locale helpers, CJK and punctuation helpers, and `analyzeText()`
- Use only for upstream hacking or deep diagnostics

### `src/measurement.ts`

- Exports measurement caches, engine-profile helpers, grapheme-width helpers, and emoji-correction helpers
- Use only when investigating internal measurement behavior

### `src/line-break.ts`

- Exports low-level line walking helpers such as `countPreparedLines()` and `walkPreparedLines()`
- Useful for invariants and diagnostics, not ordinary app integration

### `src/bidi.ts`

- Exports `computeSegmentLevels()`
- Relevant only for rich bidi metadata work

## Selection Rule

Reach for low-level exports only when the task explicitly requires internal mechanics or upstream modifications. For product integration advice, stay on the `src/layout.ts` surface first.
