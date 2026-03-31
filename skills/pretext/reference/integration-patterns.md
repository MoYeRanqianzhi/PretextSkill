# Integration Patterns

Use this file when implementing application code with Pretext.

## Height Estimation For DOM Or Virtualization

Use this pattern when the UI needs paragraph height without touching DOM layout:

```ts
import { prepare, layout } from '@chenglou/pretext'

const prepared = prepare(text, font, options)
const result = layout(prepared, width, lineHeight)
```

Implementation rules:

- Cache `prepared` by the tuple `(text, font, whiteSpace, locale)`.
- Recompute `layout()` when width or line height changes.
- Keep the `font` string aligned with the actual CSS shorthand used by the renderer.

## Fixed-Width Manual Rendering

Use this pattern when rendering text into Canvas, SVG, or another custom renderer at a fixed width:

```ts
import { prepareWithSegments, layoutWithLines } from '@chenglou/pretext'

const prepared = prepareWithSegments(text, font, options)
const { lines } = layoutWithLines(prepared, width, lineHeight)
```

Use `layoutWithLines()` when the caller actually needs line text.

## Variable-Width Line Flow

Use this pattern when line width changes as layout progresses, such as text flowing around an image:

```ts
import { prepareWithSegments, layoutNextLine } from '@chenglou/pretext'

let cursor = { segmentIndex: 0, graphemeIndex: 0 }
while (true) {
  const line = layoutNextLine(prepared, cursor, currentWidth)
  if (line === null) break
  cursor = line.end
}
```

Use `layoutNextLine()` instead of slicing strings manually.

## Shrink-Wrap Width Search

Use `walkLineRanges()` when the caller wants the smallest useful width or only needs widths and cursors:

```ts
import { prepareWithSegments, walkLineRanges } from '@chenglou/pretext'

let widest = 0
walkLineRanges(prepared, width, line => {
  if (line.width > widest) widest = line.width
})
```

Once a width is selected, call `layoutWithLines()` only if the final code needs concrete lines.

## Whitespace-Preserving Input

For textarea-like input:

```ts
const prepared = prepare(text, font, { whiteSpace: 'pre-wrap' })
```

Use `pre-wrap` when the input must preserve:

- ordinary spaces
- tab characters
- hard line breaks

Do not use it for ordinary prose unless the UI semantics require preserved whitespace.

## Locale Handling

If segmentation depends on locale:

```ts
import { setLocale } from '@chenglou/pretext'

setLocale('th')
```

Then prepare new text. Existing prepared values are not retroactively updated.

## Integration Checklist

Before calling an implementation correct, verify:

1. The `font` string matches the real renderer.
2. The `lineHeight` matches the real renderer.
3. The width source is explicit and stable.
4. The chosen API matches whether line text is required.
5. Whitespace and locale assumptions are intentional rather than accidental.
