# Internal Exports

Use this file only when the task explicitly requires advanced diagnostics, rich-path structural details, or source-level work inside the cloned upstream repo.

## Diagnostic Export From `src/layout.ts`

### `profilePrepare(text, font, options?)`

- Returns: `PrepareProfile`
- Use for: prepare-phase diagnostics and benchmark-oriented timing
- Notes:
  - source comments position it as diagnostic-only
  - do not treat it as the ordinary application integration path

### `PrepareProfile`

Fields:

- Field `analysisMs`
  - time spent in preprocessing and segmentation
- Field `measureMs`
  - time spent measuring prepared segments
- Field `totalMs`
  - combined prepare-phase time
- Field `analysisSegments`
  - segment count before measurement expansion into prepared structures
- Field `preparedSegments`
  - final prepared segment count after the prepare pipeline
- Field `breakableSegments`
  - number of prepared segments carrying grapheme-width metadata for break-word behavior

Use it to ask where prepare time or complexity is going, not to drive ordinary rendering logic.

## Advanced Exported Types

- `PrepareProfile`
- `PreparedLineChunk`

### `PreparedLineChunk`

Fields:

- Field `startSegmentIndex`
  - first prepared segment covered by the chunk
- Field `endSegmentIndex`
  - prepared segment boundary where the chunk's visible content ends
- Field `consumedEndSegmentIndex`
  - prepared segment boundary after any hard-break sentinel consumption

Meaning:

- this type exists to support chunk-aware line walking across explicit hard-break structure
- treat it as internal layout metadata, not as a stable consumer contract to build product features around

## Rich-Path Structural Details

`PreparedTextWithSegments` exposes more than line text:

- segment text via `segments`
- measured arrays such as `widths`, `kinds`, `breakableWidths`, and `breakablePrefixWidths`
- auxiliary layout metadata such as `discretionaryHyphenWidth`, `tabStopAdvance`, `chunks`, and `segLevels`

Treat this as an escape hatch for custom rendering and diagnostics, not as a promise that normal integrations should depend on every field.

### High-Value Rich Fields

- Field `segments`
  - normalized prepared segments aligned with the parallel arrays
- Field `widths`
  - measured segment widths
- Field `lineEndFitAdvances`
  - width contribution used for line-fit decisions when a line ends after this segment
- Field `lineEndPaintAdvances`
  - painted width contribution when a line ends after this segment
- Field `simpleLineWalkFastPath`
  - boolean flag indicating that the simpler line walker can be used across all layout APIs
- Field `kinds`
  - break semantics per segment: `text`, `space`, `preserved-space`, `tab`, `glue`, `zero-width-break`, `soft-hyphen`, or `hard-break`
- Field `breakableWidths`
  - per-grapheme widths for breakable runs
- Field `breakablePrefixWidths`
  - prefix-width data used by narrow browser-policy shims on some engines
- Field `discretionaryHyphenWidth`
  - visible width added when a soft hyphen is chosen as a break
- Field `tabStopAdvance`
  - absolute advance between tab stops for pre-wrap tab handling
- Field `chunks`
  - precompiled hard-break-aware chunk metadata
- Field `segLevels`
  - bidi level metadata for rich-path custom rendering

Selection rule:

- if the task only needs height or line strings, stay on the public API path
- if the task needs cursor reconstruction, shrink-wrap geometry, or bidi-aware custom rendering, rich fields may be justified
- if the task wants to persist or expose these fields as product contract, stop and justify why the public surface is insufficient

## Source Modules

These files export symbols inside the source tree, but the published package `exports` map only exposes `"."`, `./demos/*`, `./assets/*`, and `./package.json`.

Treat these modules as repo-internal or upstream-hacking surfaces, not as normal consumer import targets.

### `src/analysis.ts`

Exports whitespace modes, segment kinds, locale helpers, CJK and punctuation helpers, and the main analysis entry point.

Key exports:

- Type `WhiteSpaceMode` — `'normal' | 'pre-wrap'`
- Type `SegmentBreakKind` — `'text' | 'space' | 'preserved-space' | 'tab' | 'glue' | 'zero-width-break' | 'soft-hyphen' | 'hard-break'`
- Type `MergedSegmentation` — parallel arrays: `texts`, `isWordLike`, `kinds`, `starts`, plus `len`
- Type `AnalysisChunk` — `startSegmentIndex`, `endSegmentIndex`, `consumedEndSegmentIndex`
- Type `TextAnalysis` — `normalized`, `chunks`, plus all `MergedSegmentation` fields
- Type `AnalysisProfile` — `{ carryCJKAfterClosingQuote: boolean }`
- `analyzeText(text, profile, whiteSpace?)` → `TextAnalysis` — main entry point for text segmentation and analysis
- `normalizeWhitespaceNormal(text)` → `string` — collapses whitespace runs per CSS `white-space: normal`
- `setAnalysisLocale(locale?)` → `void` — changes the `Intl.Segmenter` locale used for word segmentation
- `clearAnalysisCaches()` → `void` — resets the shared word segmenter
- `isCJK(s)` → `boolean` — checks whether a string contains CJK / kana / Hangul / fullwidth characters
- `endsWithClosingQuote(text)` → `boolean` — checks trailing closing-quote characters
- `kinsokuStart` — `Set<string>` of CJK line-start-prohibited characters
- `kinsokuEnd` — `Set<string>` of CJK line-end-prohibited / opening characters
- `leftStickyPunctuation` — `Set<string>` of punctuation that sticks to the preceding segment

### `src/measurement.ts`

Exports measurement caches, engine-profile helpers, grapheme-width helpers, and emoji-correction helpers.

Key exports:

- Type `SegmentMetrics` — `{ width, containsCJK, emojiCount?, graphemeWidths?, graphemePrefixWidths? }`
- Type `EngineProfile` — `{ lineFitEpsilon, carryCJKAfterClosingQuote, preferPrefixWidthsForBreakableRuns, preferEarlySoftHyphenBreak }`
- `getMeasureContext()` → `CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D` — lazily creates a canvas context for text measurement
- `getSegmentMetricCache(font)` → `Map<string, SegmentMetrics>` — per-font metric cache
- `getSegmentMetrics(seg, cache)` → `SegmentMetrics` — measures a single segment string, returning cached metrics
- `getEngineProfile()` → `EngineProfile` — detects browser engine and returns tuned layout parameters
- `parseFontSize(font)` → `number` — extracts pixel size from a CSS font string
- `textMayContainEmoji(text)` → `boolean` — fast regex check for potential emoji content
- `getCorrectedSegmentWidth(seg, metrics, emojiCorrection)` → `number` — applies per-emoji width correction
- `getSegmentGraphemeWidths(seg, metrics, cache, emojiCorrection)` → `number[] | null` — per-grapheme widths for overflow-wrap breaking
- `getSegmentGraphemePrefixWidths(seg, metrics, cache, emojiCorrection)` → `number[] | null` — cumulative prefix widths for narrow browser-policy shims
- `getFontMeasurementState(font, needsEmojiCorrection)` → `{ cache, fontSize, emojiCorrection }` — bundles measurement state for a given font
- `clearMeasurementCaches()` → `void` — clears all metric and emoji-correction caches

### `src/line-break.ts`

Exports low-level line walking helpers and the types they operate on.

Key exports:

- Type `LineBreakCursor` — `{ segmentIndex, graphemeIndex }`
- Type `PreparedLineBreakData` — the structural contract consumed by the line walker: `widths`, `lineEndFitAdvances`, `lineEndPaintAdvances`, `kinds`, `simpleLineWalkFastPath`, `breakableWidths`, `breakablePrefixWidths`, `discretionaryHyphenWidth`, `tabStopAdvance`, `chunks`
- Type `InternalLayoutLine` — `{ startSegmentIndex, startGraphemeIndex, endSegmentIndex, endGraphemeIndex, width }`
- `countPreparedLines(prepared, maxWidth)` → `number` — fast line-count-only path (no allocations)
- `walkPreparedLines(prepared, maxWidth, onLine?)` → `number` — full line walker with optional per-line callback
- `layoutNextLineRange(prepared, start, maxWidth)` → `InternalLayoutLine | null` — incremental single-line layout from a cursor
- `normalizeLineStart(prepared, start)` → `LineBreakCursor | null` — adjusts a cursor past leading collapsible whitespace

### `src/bidi.ts`

- Exports `computeSegmentLevels()`

## Selection Rule

Ask these before touching internal exports:

1. Can the package-facing API solve the task without this?
2. Am I modifying the upstream repo rather than merely using the package?
3. Do I need diagnostic visibility or only a correct product integration?

If the answer to all three is not clearly "yes," stay on [public-api.md](public-api.md).

When the answer is "yes," also read [internal-architecture.md](internal-architecture.md) before changing source files.
