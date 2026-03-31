# Internal Exports

Use this file only when the task explicitly requires advanced diagnostics, rich-path structural details, or source-level work inside the cloned upstream repo.

## Diagnostic Export From `src/layout.ts`

### `profilePrepare(text, font, options?)`

- Returns: `PrepareProfile`
- Use for: prepare-phase diagnostics and benchmark-oriented timing
- Notes:
  - source comments position it as diagnostic-only
  - do not treat it as the ordinary application integration path

## Advanced Exported Types

- `PrepareProfile`
- `PreparedLineChunk`

## Rich-Path Structural Details

`PreparedTextWithSegments` exposes more than line text:

- segment text via `segments`
- measured arrays such as `widths`, `kinds`, `breakableWidths`, and `breakablePrefixWidths`
- auxiliary layout metadata such as `discretionaryHyphenWidth`, `tabStopAdvance`, `chunks`, and `segLevels`

Treat this as an escape hatch for custom rendering and diagnostics, not as a promise that normal integrations should depend on every field.

## Source Modules

These files export symbols inside the source tree, but the published package `exports` map only exposes `"."`, `./demos/*`, `./assets/*`, and `./package.json`.

Treat these modules as repo-internal or upstream-hacking surfaces, not as normal consumer import targets.

### `src/analysis.ts`

- Exports whitespace modes, segment kinds, locale helpers, CJK and punctuation helpers, and `analyzeText()`

### `src/measurement.ts`

- Exports measurement caches, engine-profile helpers, grapheme-width helpers, and emoji-correction helpers

### `src/line-break.ts`

- Exports low-level line walking helpers such as `countPreparedLines()` and `walkPreparedLines()`

### `src/bidi.ts`

- Exports `computeSegmentLevels()`

## Selection Rule

Ask these before touching internal exports:

1. Can the package-facing API solve the task without this?
2. Am I modifying the upstream repo rather than merely using the package?
3. Do I need diagnostic visibility or only a correct product integration?

If the answer to all three is not clearly "yes," stay on [public-api.md](public-api.md).
