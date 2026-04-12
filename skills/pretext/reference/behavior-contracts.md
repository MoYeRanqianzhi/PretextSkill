# Behavior Contracts

Use this file when the task is about exact semantic expectations, edge cases, whether a proposed change would break an existing Pretext contract, visible whitespace or break-character behavior, script-sensitive segmentation, punctuation-glue classes, bidi or emoji caveats, browser quirks, or diagnosing "wrong layout" reports.

## Purpose

This file is not the first place to choose an API. It is the place to answer:

- what behavior is supposed to remain invariant across exported APIs
- which edge cases are deliberate semantics rather than accidental implementation details
- which regressions should be treated as contract breaks before patching internals

The canonical evidence base is:

- `pretext/src/layout.ts`
- `pretext/src/layout.test.ts`
- `pretext/README.md`

---

## Cross-API Contracts

Preserve these before attempting internal refactors:

- `prepare()` and `prepareWithSegments()` must agree on layout behavior for the same text, typography, whitespace mode, locale, width, and line height
- `layoutNextLine()` must reproduce the same lines as `layoutWithLines()`
- `walkLineRanges()` must reproduce the same geometry as `layoutWithLines()` without materializing text
- rich line boundary cursors must reconstruct the prepared normalized text exactly
- soft-hyphen rendering may insert visible hyphens in line text, but cursor-based reconstruction must preserve the original source slices

---

## Whitespace Detail

### `whiteSpace: 'normal'`

- collapses ordinary whitespace runs (spaces, tabs, line breaks)
- trims ordinary whitespace at the edges; whitespace-only input becomes empty
- trailing collapsible whitespace hangs past the line edge without forcing a break

### `whiteSpace: 'pre-wrap'`

- ordinary spaces remain visible
- `\t` tabs remain as explicit segments and align to tab stops (default `tab-size: 8`)
- hard breaks are explicit line boundaries; CRLF normalizes to a single hard break
- tab stops restart after a hard break
- whitespace-only lines remain visible
- trailing spaces or tabs before a hard break stay on the current line
- consecutive hard breaks preserve empty lines, but a terminal hard break does not invent an extra trailing empty line

### Explicit Glue And Break Characters

- non-breaking space (`\u00A0`), narrow no-break space (`\u202F`), and word joiner (`\u2060`) stay as visible glue content, not ordinary collapsible whitespace
- zero-width space (`\u200B`) is an explicit break opportunity
- soft hyphen (`\u00AD`) is a discretionary break point, not an ordinary visible glyph in the source stream

### Soft Hyphen Behavior

- stays invisible on unbroken lines
- renders as a visible trailing `-` only when chosen as the break point
- round-trips through rich cursors using source slices, not merely rendered line text

### Narrow-Width Consequence

Because the default target includes `overflow-wrap: break-word`, very narrow widths can still break inside words, but only at grapheme boundaries. Line count should grow monotonically as width shrinks.

---

## Script & Browser Detail

### Punctuation And Structured Token Rules

Tests establish explicit expectations for:

- closing punctuation attaching to the preceding word
- opening punctuation and quote clusters attaching to the following word when context requires
- contextual ASCII quote glue
- Arabic punctuation and punctuation-plus-mark clusters
- Devanagari danda punctuation
- Myanmar punctuation and possessive-marker glue
- CJK and Hangul punctuation attachment
- URL-like runs and query-string structure
- numeric time ranges
- hyphenated numeric identifiers
- repeated punctuation runs

### Script And Directional Behavior

- CJK text can split into grapheme-level break units; astral CJK ideographs are treated as CJK break units
- Hangul punctuation attachment has explicit behavior
- mixed-direction text is a stable smoke-test path for the rich APIs
- locale-sensitive segmentation uses `Intl.Segmenter`
- Thai and other locale-sensitive scripts can depend on `setLocale()` before preparation

### Browser Caveats

- `system-ui` is unsafe for accuracy-sensitive macOS layout
- Chrome and Firefox on macOS can over-measure emoji in canvas at small sizes; Pretext uses a cached correction

### Research Canaries

These are not ordinary "just patch it" bug zones. Treat them as places where the current model has known tension or exactness ceilings.

| Area | Current Read | Design Caution |
| --- | --- | --- |
| Myanmar | unresolved quote and follower-style classes | do not stack instinctive glue rules without broad evidence |
| Japanese | punctuation and proportional-font exactness ceiling | do not keep piling on narrow punctuation heuristics |
| Chinese | narrow-width and font-sensitive exactness ceiling | treat as a real canary, not an obvious missed punctuation rule |
| Arabic | remaining fine-width shaping or context classes | be skeptical of heavy shaping-aware width caches |

---

## Locale And Cache Contracts

- `setLocale()` affects future `prepare()` and `prepareWithSegments()` calls only
- `setLocale()` clears shared caches internally
- existing prepared values do not mutate after a locale change
- `clearCache()` is an intentional cache-lifecycle tool, not a normal render-loop primitive

---

## Custom Rendering Contracts

- `LayoutCursor.start` is inclusive
- `LayoutCursor.end` is exclusive
- `LayoutLineRange` must preserve geometry parity with `LayoutLine`
- rich-path line text reconstruction must not silently lose preserved whitespace, hard breaks, or source-only soft-hyphen markers

---

## Diagnostic Exports

### `profilePrepare()`

Use when the question is specifically about prepare-phase cost or segment counts.

It reports:

- `analysisMs`
- `measureMs`
- `totalMs`
- `analysisSegments`
- `preparedSegments`
- `breakableSegments`

Treat it as a diagnostic helper, not a runtime integration primitive.

---

## Research-Backed Guardrails

The upstream research log strongly favors these constraints:

- keep `layout()` arithmetic-only
- do not move measurement into `layout()`
- do not reintroduce DOM reads as the default measurement path
- prefer small semantic preprocessing rules over heavy runtime corrections

Be skeptical of fixes that:

- add pair-correction tables
- add shaping-aware width caches without strong evidence
- compensate for `system-ui` with guessed substitutions

---

## First-Pass Debug Order

Check these before suspecting a Pretext bug:

1. `font` mismatch
2. `lineHeight` mismatch
3. width mismatch
4. wrong whitespace mode
5. wrong locale state
6. wrong API shape for the task

---

## Bug Report Shape

Always include:

- input text
- font string
- line height
- width
- whitespace mode
- locale
- chosen API
- expected behavior
- actual behavior

Without those, most Pretext bugs are underspecified.

---

## Diagnostic Rule

When a bug report claims "Pretext is wrong," ask:

1. Which exact contract above is being violated?
2. Can the issue be reproduced with the exported APIs before touching internals?
3. Is the failure in segmentation, measurement, line walking, or line materialization?
4. Is this a real regression, or a known canary documented in the Research Canaries table?
5. Is the correct whitespace mode in use? Is the issue actually a glue or break character?

If you cannot answer those questions precisely, stay in diagnosis mode rather than patching internals.
