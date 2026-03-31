# Custom Rendering Recipes

Use this file when the task is about Canvas, SVG, WebGL, geometry-only width probes, or variable-width line flow.

## Fixed-Width Rendering

Use this pattern when the renderer needs concrete line strings at one width.

```ts
import { prepareWithSegments, layoutWithLines } from '@chenglou/pretext'

const prepared = prepareWithSegments(text, font, options)
const { lines } = layoutWithLines(prepared, width, lineHeight)
```

Rules:

- prefer `layoutWithLines()` when the renderer needs actual line text
- keep `font` and `lineHeight` synchronized with the rendering context

## Geometry-Only Shrink-Wrap

Use this pattern when the product wants the tightest width that still fits a multiline block.

```ts
import { prepareWithSegments, walkLineRanges } from '@chenglou/pretext'

let widest = 0
walkLineRanges(prepared, width, line => {
  if (line.width > widest) widest = line.width
})
```

Rules:

- keep repeated width probes in `walkLineRanges()`
- materialize lines only after choosing the final width
- keep the width-search algorithm outside Pretext

## Variable-Width Flow Around Media

Use this pattern when each row has a different width budget.

```ts
import { prepareWithSegments, layoutNextLine } from '@chenglou/pretext'

let cursor = { segmentIndex: 0, graphemeIndex: 0 }
while (true) {
  const line = layoutNextLine(prepared, cursor, currentWidth)
  if (line === null) break
  cursor = line.end
}
```

Rules:

- treat `line.end` as the next cursor
- keep width selection external to Pretext
- use this only when widths truly vary by row
