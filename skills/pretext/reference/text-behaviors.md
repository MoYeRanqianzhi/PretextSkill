# Text Behaviors

Use this file when the task touches correctness at the character, segment, or script level.

## Whitespace Modes

### `whiteSpace: 'normal'`

- collapses ordinary whitespace runs
- trims ordinary whitespace at the edges
- lets trailing collapsible whitespace hang past the line edge without forcing a break

### `whiteSpace: 'pre-wrap'`

- preserves ordinary spaces
- preserves `\t` tabs
- preserves hard breaks
- normalizes CRLF to a single hard break
- keeps whitespace-only lines visible
- keeps consecutive hard breaks as empty lines
- does not invent an extra trailing empty line after a final hard break
- restarts tab stops after a hard break

Tabs follow default browser-style `tab-size: 8` behavior.

## Explicit Glue And Break Characters

- non-breaking space (`\u00A0`) stays glued into visible content
- narrow no-break space (`\u202F`) stays glued into visible content
- word joiner (`\u2060`) stays glued into visible content
- zero-width space (`\u200B`) becomes an explicit break opportunity
- soft hyphen (`\u00AD`) becomes a discretionary break point

## Soft Hyphen Behavior

- stays invisible on unbroken lines
- renders as a visible trailing `-` only when chosen as the break point
- round-trips through rich cursors using source slices, not merely rendered line text

## Punctuation And Structured Token Rules

Tests establish explicit expectations for:

- closing punctuation attaching to the preceding word
- opening punctuation and quote clusters attaching to the following word when context requires
- contextual ASCII quote glue
- Arabic punctuation and punctuation-plus-mark clusters
- Devanagari danda punctuation
- Myanmar punctuation and possessive-marker glue
- URL-like runs and query-string structure
- numeric time ranges
- hyphenated numeric identifiers
- repeated punctuation runs

## Script And Directional Behavior

- CJK text can split into grapheme-level break units
- Hangul punctuation attachment has explicit behavior
- astral CJK ideographs are treated as CJK break units
- mixed-direction text is a stable smoke-test path
- locale-sensitive segmentation uses `Intl.Segmenter`
- Thai and other locale-sensitive scripts can depend on `setLocale()` before preparation

## Browser And Model Caveats

- `system-ui` is unsafe for accuracy-sensitive macOS layout
- Chrome and Firefox on macOS can over-measure emoji in canvas at small sizes; Pretext uses a cached correction
- the default target includes `overflow-wrap: break-word`, so very narrow widths can still break inside words, but only at grapheme boundaries

## Practical Rule

When a report says "text layout is wrong," first reduce it to one of these behavior classes:

- whitespace mode
- explicit break or glue character
- punctuation glue
- script-specific segmentation
- bidi or locale state
- browser-font caveat
