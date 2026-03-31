# Whitespace And Breaks

Use this file when the task is about visible spaces, tabs, hard breaks, zero-width separators, soft hyphens, or line-break policy.

## Mode Envelope

Pretext currently targets the common text setup:

- `white-space: normal`
- `word-break: normal`
- `overflow-wrap: break-word`
- `line-break: auto`

If you pass `{ whiteSpace: 'pre-wrap' }`, the wrapping defaults stay the same while ordinary spaces, tabs, and hard breaks become visible and significant.

## `whiteSpace: 'normal'`

- collapses ordinary whitespace runs
- trims ordinary whitespace at the edges
- lets trailing collapsible whitespace hang past the line edge without forcing a break

## `whiteSpace: 'pre-wrap'`

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

## Narrow-Width Consequence

Because the default target includes `overflow-wrap: break-word`, very narrow widths can still break inside words, but only at grapheme boundaries.

## Practical Rule

When the bug report says "characters disappeared" or "wrapping looks wrong," first ask:

1. Is the correct whitespace mode in use?
2. Is the issue actually a glue or break character?
3. Is the width simply narrow enough to trigger grapheme-level breaking?
