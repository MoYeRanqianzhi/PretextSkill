# Integration Lifecycle

Use this file when writing or reviewing application code that embeds Pretext.

## Height-Only UI

Use this path for virtualization, occlusion, chat bubbles, or any UI that only needs height and line count.

```ts
import { prepare, layout } from '@chenglou/pretext'

const prepared = prepare(text, font, options)
const result = layout(prepared, width, lineHeight)
```

Rules:

- cache prepared state by `(text, font, whiteSpace, locale)`
- rerun `layout()` on width or line-height changes
- rerun `prepare()` only when prepare-phase inputs change

## Fixed-Width Custom Rendering

Use this path for Canvas, SVG, WebGL, or diagnostics when the width is fixed for the whole paragraph.

```ts
import { prepareWithSegments, layoutWithLines } from '@chenglou/pretext'

const prepared = prepareWithSegments(text, font, options)
const { lines } = layoutWithLines(prepared, width, lineHeight)
```

## Streamed Or Continued Flow

Use this path when the same prepared paragraph must continue across:

- pages
- columns
- variable-height windows
- shaped regions
- virtualized slices

```ts
import { prepareWithSegments, layoutNextLine } from '@chenglou/pretext'

let cursor = { segmentIndex: 0, graphemeIndex: 0 }
while (true) {
  const line = layoutNextLine(prepared, cursor, width)
  if (line === null) break
  cursor = line.end
}
```

Use this even when width stays constant if cursor continuity is the real requirement.

## Geometry-Only Work

Use this path when width probing or shrink-wrap behavior matters more than line strings.

```ts
import { prepareWithSegments, walkLineRanges } from '@chenglou/pretext'

// walkLineRanges returns the total line count (number)
const lineCount = walkLineRanges(prepared, width, line => {
  // inspect line.width, line.start, line.end
})
```

Use `layoutWithLines()` only after choosing a final width if concrete lines are actually needed.

## Variable-Width Line Flow

Use this path when available width changes per line, such as text flowing around media.

```ts
import { prepareWithSegments, layoutNextLine } from '@chenglou/pretext'

let cursor = { segmentIndex: 0, graphemeIndex: 0 }
while (true) {
  const line = layoutNextLine(prepared, cursor, currentWidth)
  if (line === null) break
  cursor = line.end
}
```

This is a subtype of streamed flow, not the only reason to use `layoutNextLine()`.

## Locale And Cache Lifecycle

- call `setLocale()` before preparing new text when locale-sensitive segmentation matters
- assume `setLocale()` clears caches
- do not expect existing prepared values to mutate after a locale change
- use `clearCache()` intentionally, not defensively

## Performance Review Checklist

- Is `prepare()` or `prepareWithSegments()` incorrectly running on resize?
- Is the chosen API richer than the task needs?
- Is `font` identical to the real renderer's font shorthand?
- Is `lineHeight` identical to the real renderer's line height?
- Is the width source explicit and stable?
- Is whitespace mode intentional?

## Product-Shape Checklist

Before shipping a Pretext-backed feature, make these decisions explicit:

1. What exact output shape is required?
2. What invalidates prepared state?
3. What invalidates only layout?
4. Does the renderer require line strings, geometry, or only height?
5. Do spaces, tabs, hard breaks, or locale state matter?

## When To Leave This File

- If the task is really about an adapter, hook, service, or composable boundary, switch to [adapter-patterns.md](adapter-patterns.md).
- If the task is specifically about PDF, EPUB, pagination, or reader text layers, switch to [document-reader-recipes.md](document-reader-recipes.md).
