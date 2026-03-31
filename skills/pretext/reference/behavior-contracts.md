# Behavior Contracts

Use this file when the task is about exact semantic expectations, edge cases, or whether a proposed change would break an existing Pretext contract.

## Purpose

This file is not the first place to choose an API. It is the place to answer:

- what behavior is supposed to remain invariant across exported APIs
- which edge cases are deliberate semantics rather than accidental implementation details
- which regressions should be treated as contract breaks before patching internals

The canonical evidence base is:

- `pretext/src/layout.ts`
- `pretext/src/layout.test.ts`
- `pretext/README.md`

## Cross-API Contracts

Preserve these before attempting internal refactors:

- `prepare()` and `prepareWithSegments()` must agree on layout behavior for the same text, typography, whitespace mode, locale, width, and line height
- `layoutNextLine()` must reproduce the same lines as `layoutWithLines()`
- `walkLineRanges()` must reproduce the same geometry as `layoutWithLines()` without materializing text
- rich line boundary cursors must reconstruct the prepared normalized text exactly
- soft-hyphen rendering may insert visible hyphens in line text, but cursor-based reconstruction must preserve the original source slices

## Whitespace Contracts

### Normal Mode

- ordinary spaces, tabs, and line breaks collapse under the normal path
- whitespace-only input becomes empty under the normal path
- trailing whitespace hangs past the line edge and does not trigger a wrap on its own

### `pre-wrap` Mode

- ordinary spaces remain visible
- hard breaks are explicit line boundaries
- CRLF is normalized to a single hard break
- tabs remain explicit segments and align to tab stops
- tab stops restart after a hard break
- whitespace-only lines remain visible
- trailing spaces or tabs before a hard break stay on the current line
- consecutive hard breaks preserve empty lines, but a terminal hard break does not invent an extra trailing empty line

## Break Contracts

- non-breaking spaces, narrow no-break spaces, and word joiners stay as visible glue content rather than ordinary collapsible whitespace
- zero-width spaces are explicit break opportunities
- soft hyphens are discretionary break points, not ordinary visible glyphs in the source stream
- overlong breakable runs may split at grapheme boundaries
- long breakable segments should move to a fresh line when the current line already has content and the next segment cannot fit
- line count should grow monotonically as width shrinks

## Script And Glue Contracts

The current model intentionally preserves these high-value behaviors:

- closing punctuation attaches to the preceding word
- opening punctuation and opening-quote clusters attach to the following word only when context justifies it
- Arabic punctuation and punctuation-plus-mark clusters remain attached correctly
- Myanmar punctuation and follower-style classes remain in the preprocessing domain, not the layout hot path
- Devanagari danda punctuation remains attached to the preceding word
- CJK and Hangul punctuation attachment remains explicit
- astral CJK ideographs are treated as CJK break units
- mixed-direction text is a stable smoke-test path for the rich APIs

For deeper script-specific boundaries and canaries, also load [script-and-browser-caveats.md](script-and-browser-caveats.md).

## Locale And Cache Contracts

- `setLocale()` affects future `prepare()` and `prepareWithSegments()` calls only
- `setLocale()` clears shared caches internally
- existing prepared values do not mutate after a locale change
- `clearCache()` is an intentional cache-lifecycle tool, not a normal render-loop primitive

## Custom Rendering Contracts

- `LayoutCursor.start` is inclusive
- `LayoutCursor.end` is exclusive
- `LayoutLineRange` must preserve geometry parity with `LayoutLine`
- rich-path line text reconstruction must not silently lose preserved whitespace, hard breaks, or source-only soft-hyphen markers

## Diagnostic Rule

When a bug report claims “Pretext is wrong,” ask:

1. Which exact contract above is being violated?
2. Can the issue be reproduced with the exported APIs before touching internals?
3. Is the failure in segmentation, measurement, line walking, or line materialization?
4. Is this a real regression, or a known canary documented elsewhere?

If you cannot answer those questions precisely, stay in diagnosis mode rather than patching internals.
