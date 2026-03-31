# App Recipes

Use this file when the task is implementation-heavy and you need a concrete application pattern rather than only abstract API selection.

## React Height Cache

Use this pattern when the UI only needs height and line count for virtualization, occlusion, or chat bubbles.

```ts
import { prepare, layout } from '@chenglou/pretext'

type PreparedKey = {
  text: string
  font: string
  whiteSpace: 'normal' | 'pre-wrap'
  locale: string | undefined
}

function measureBubble(prepared: ReturnType<typeof prepare>, width: number, lineHeight: number) {
  return layout(prepared, width, lineHeight)
}
```

Rules:

- cache prepared state by `(text, font, whiteSpace, locale)`
- rerun `layout()` on width or line-height changes
- rerun `prepare()` only when prepare inputs change

## Fixed-Width Canvas Or SVG Rendering

Use this pattern when the renderer needs concrete lines.

```ts
import { prepareWithSegments, layoutWithLines } from '@chenglou/pretext'

const prepared = prepareWithSegments(text, font, options)
const { lines } = layoutWithLines(prepared, width, lineHeight)
```

Rules:

- prefer `layoutWithLines()` when the renderer needs actual line text
- keep `font` and `lineHeight` synchronized with the rendering context

## Geometry-Only Shrink-Wrap Search

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

## Whitespace-Preserving Editor

Use this path for textarea-like editing, tabs, visible hard breaks, or locale-aware text editing.

```ts
const prepared = prepareWithSegments(text, font, { whiteSpace: 'pre-wrap' })
```

Rules:

- call `setLocale()` before preparing if locale-sensitive segmentation matters
- re-prepare after locale changes
- do not fall back to `prepare()` if line strings are required

## Package Release Or Published-Artifact Checks

Use this path when the task is about package shape rather than rendering behavior.

Commands:

- `bun run package-smoke-test`
- `bun run check`
- `bun run build:package`

Rules:

- validate package-consumer behavior separately from upstream source internals
- use [public-api.md](public-api.md) for the package-facing contract
