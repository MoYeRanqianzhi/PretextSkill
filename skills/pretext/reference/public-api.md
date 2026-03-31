# Public API

Use this file when the task is about the normal package-facing Pretext API.

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

### `clearCache()`

- Use for: intentional cache release or environment reset
- Notes:
  - do not put this in normal render loops

### `setLocale(locale?)`

- Use for: future locale-sensitive preparation
- Notes:
  - affects future prepare calls only
  - clears caches internally

## Stable Product Types

- `PreparedText`
- `PreparedTextWithSegments`
- `LayoutCursor`
- `LayoutResult`
- `LayoutLine`
- `LayoutLineRange`
- `LayoutLinesResult`
- `PrepareOptions`

## Boundary Note

If the task explicitly needs `profilePrepare()`, `PrepareProfile`, `PreparedLineChunk`, rich-path structural fields like `chunks` or `segLevels`, or source modules such as `analysis.ts`, stop and load [internal-exports.md](internal-exports.md). Those are advanced surfaces, not the normal product-facing path.
