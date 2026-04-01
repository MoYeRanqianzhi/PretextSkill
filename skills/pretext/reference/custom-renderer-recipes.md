# Custom Renderer Recipes

Use this file when the task is about Canvas, SVG, WebGL, shrink-wrap search, or variable-width flow.

## First-Principles Lens

- Height-only consumers should stay on `prepare()` plus `layout()`
- Rich renderers should pay for `prepareWithSegments()` only when they need lines, cursors, or geometry
- Repeated width probes, animation frames, and row-by-row flow belong in the layout phase
- Final text materialization should happen as late as possible

## Fixed-Width Canvas Or SVG Rendering

Use this pattern when the renderer needs concrete lines at one width.

```ts
import { prepareWithSegments, layoutWithLines } from '@chenglou/pretext'

const prepared = prepareWithSegments(text, font, options)
const { lines } = layoutWithLines(prepared, width, lineHeight)
```

Rules:

- prefer `layoutWithLines()` when the renderer needs actual line text
- keep `font` and `lineHeight` synchronized with the rendering context
- do not use the rich path if the renderer only needs final height

Upstream anchors:

- `pretext/pages/probe.ts`
- `pretext/pages/corpus.ts`

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
- treat geometry-only probing as layout-phase work, not prepare-phase work

Upstream anchors:

- `pretext/pages/demos/bubbles-shared.ts`
- `pretext/pages/demos/bubbles.ts`
- `pretext/pages/demos/bubbles.html`

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
- prefer this only when widths actually vary per line

Upstream anchors:

- `pretext/pages/demos/dynamic-layout.ts`
- `pretext/pages/demos/wrap-geometry.ts`

## Editorial Or Multi-Column Flow

Use this path when the same prepared paragraph must continue across columns, slots, or shaped regions.

Rules:

- keep one prepared paragraph and move only the cursor forward
- use `walkLineRanges()` for speculative geometry and `layoutNextLine()` for the final stream
- avoid reconstructing or resegmenting text per column

Upstream anchor:

- `pretext/pages/demos/editorial-engine.ts`

## Canvas Animation Loop

Use this pattern when the canvas rerenders every frame but the text changes rarely.

```ts
import { prepareWithSegments, layoutWithLines } from '@chenglou/pretext'

const prepared = prepareWithSegments(text, font, options)

function renderFrame(width: number, lineHeight: number) {
  const { lines } = layoutWithLines(prepared, width, lineHeight)
  // draw lines into the current frame
}
```

Rules:

- prepare once outside the frame loop
- rerun only the layout call per frame if width or line height changes
- rebuild prepared state only when text, font, whitespace, or locale changes

## Renderer Guardrails

- use the rich path only when height-only output is insufficient
- do not rebuild prepared state during rendering loops
- if the final renderer only needs geometry, stay on `walkLineRanges()` as long as possible
- when debugging custom rendering, distinguish engine line geometry from your own draw-order, transform, or clipping bugs

## When Custom Renderer Is Still Too Broad

- If the task is really a PDF, EPUB, pagination, or reader text-layer problem, switch to [document-reader-recipes.md](document-reader-recipes.md).
- If the task is really about a shared wrapper or cache facade around Pretext, switch to [adapter-patterns.md](adapter-patterns.md).

Validation surfaces:

- `bun run check`
- `bun run site:build`
- `bun run probe-check`
- targeted demo inspection via `bun start`
