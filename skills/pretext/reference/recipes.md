# Recipes

Use this file when integrating Pretext into application code -- React, Canvas, SVG, PDF/EPUB, or any custom renderer.

## Height-Only UI

Use this path for virtualization, occlusion, chat bubbles, or any UI that only needs height and line count.

```ts
import { prepare, layout } from '@chenglou/pretext'

const prepared = prepare(text, font, options)
const result = layout(prepared, width, lineHeight)
```

Cache rules:

- cache prepared state by `(text, font, whiteSpace, locale)`
- rerun `layout()` on width or line-height changes
- rerun `prepare()` only when prepare-phase inputs change

## React & DOM

### React Hook Pattern

Use when the app needs one reusable hook for caching and measurement.

```ts
import { useRef } from 'react'
import { prepare, layout } from '@chenglou/pretext'

// Locale is intentionally not handled here. setLocale() clears internal
// caches and must be called once at the adapter boundary, not per
// measurement. See adapter-patterns.md Pattern 5 for the recommended
// approach to centralizing locale changes.
export function usePretextHeightCache() {
  const cacheRef = useRef(new Map<string, ReturnType<typeof prepare>>())

  function measure(
    text: string,
    font: string,
    width: number,
    lineHeight: number,
    whiteSpace: 'normal' | 'pre-wrap' = 'normal',
  ) {
    const key = JSON.stringify({ text, font, whiteSpace })
    let prepared = cacheRef.current.get(key)
    if (!prepared) {
      prepared = prepare(text, font, { whiteSpace })
      cacheRef.current.set(key, prepared)
    }
    return layout(prepared, width, lineHeight)
  }

  return { measure, cache: cacheRef.current }
}
```

Rules:

- key the cache by the full invalidation tuple, not only by text
- keep width and line height in the layout phase
- if whitespace mode can change, include it in the key and rebuild prepared state
- manage locale at the adapter boundary (see [adapter-patterns.md](adapter-patterns.md) Pattern 5); do not call `setLocale()` inside a per-measurement hook because it clears caches and belongs in a centralized lifecycle

Upstream anchors: `pretext/pages/demos/accordion.ts`, `pretext/pages/demos/masonry/index.ts`

### Whitespace-Preserving Editor

Use for textarea-like editing, tabs, visible hard breaks, or locale-aware text editing.

```ts
import { prepareWithSegments, layoutWithLines, setLocale } from '@chenglou/pretext'

setLocale(locale)
const prepared = prepareWithSegments(text, font, { whiteSpace: 'pre-wrap' })
const result = layoutWithLines(prepared, width, lineHeight)
```

Rules:

- call `setLocale()` before preparing if locale-sensitive segmentation matters
- re-prepare after locale changes
- do not fall back to `prepare()` if line strings are required
- use `pre-wrap` only when spaces, tabs, or hard breaks must stay visible

Validation: `bun run pre-wrap-check`, `bun run probe-check`

### DOM Guardrails

- Pretext is for DOM-free text measurement, not post-hoc reconciliation with `getBoundingClientRect()` or `offsetHeight`
- keep `font` and `lineHeight` synchronized with actual CSS
- keep prepare-phase state outside the resize hot path
- invalidate hook caches when locale or whitespace mode changes, not only when text changes
- prefer `ResizeObserver` or layout math for width; do not remeasure rendered text with DOM APIs after adopting Pretext

Upstream anchors: `pretext/pages/probe.ts`, `pretext/pages/corpus.ts`

## Canvas, SVG & WebGL

### Fixed-Width Rendering

Use when the renderer needs concrete lines at one width.

```ts
import { prepareWithSegments, layoutWithLines } from '@chenglou/pretext'

const prepared = prepareWithSegments(text, font, options)
const { lines } = layoutWithLines(prepared, width, lineHeight)
```

Upstream anchors: `pretext/pages/probe.ts`, `pretext/pages/corpus.ts`

### Geometry-Only Shrink-Wrap Search

Use when the product wants the tightest width that still fits a multiline block.

```ts
import { prepareWithSegments, walkLineRanges } from '@chenglou/pretext'

let widest = 0
const lineCount = walkLineRanges(prepared, width, line => {
  if (line.width > widest) widest = line.width
})
```

Rules:

- keep repeated width probes in `walkLineRanges()`
- materialize lines only after choosing the final width
- treat geometry-only probing as layout-phase work

Upstream anchors: `pretext/pages/demos/bubbles-shared.ts`, `pretext/pages/demos/bubbles.ts`

### Canvas Animation Loop

Use when the canvas rerenders every frame but the text changes rarely.

```ts
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

## PDF, EPUB & Pagination

### Fixed-Region Text Layer

Use when one text item is laid out into one known page or region width (e.g. PDF.js-style text layers, search-hit overlays).

```ts
const prepared = prepareWithSegments(text, font, options)
const result = layoutWithLines(prepared, regionWidth, lineHeight)
```

### Streamed Pagination Or Column Continuation

Use when the same prepared paragraph must continue across pages, columns, scrolling windows, or virtualized reader slices.

```ts
import { prepareWithSegments, layoutNextLine } from '@chenglou/pretext'

let cursor = { segmentIndex: 0, graphemeIndex: 0 }
while (true) {
  const line = layoutNextLine(prepared, cursor, columnWidth)
  if (line === null) break
  cursor = line.end
}
```

Rules:

- treat `line.end` as the authoritative continuation cursor
- keep one prepared paragraph while text, font, whitespace mode, and locale stay stable
- do not rebuild prepared state per page or column
- width may be constant or variable; cursor continuity is the main reason to choose this path

### Preserved-Break Blocks Inside Readers

For code blocks, poetry, or preserved editor content embedded inside a reader:

- use `prepareWithSegments(..., { whiteSpace: 'pre-wrap' })`
- use `layoutWithLines()` when the block fits one known region
- use `layoutNextLine()` when it must continue across containers

### Reader Adapter Boundary

Keep these responsibilities outside Pretext:

- page/column width selection and region switching
- inline-image or atomic-block reservation
- page-break policy and selection box synthesis

Pretext owns line fitting, not full page semantics.

External anchors:

- `alpeshvas/pretext-pdfjs` -- `src/pretext-text-layer.js` (PDF text-layer integration and responsive reflow)
- `zsh-eng/epub-reader-demo` -- `src/lib/pagination/layout-text-lines.ts` (cursor-based pagination)

## Variable-Width Flow

Use when available width changes per line, such as text flowing around media or shaped regions.

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
- this is a subtype of streamed flow -- prefer it only when widths actually vary per line
- for editorial or multi-column flow, keep one prepared paragraph and advance only the cursor; avoid resegmenting text per column

Upstream anchors: `pretext/pages/demos/dynamic-layout.ts`, `pretext/pages/demos/wrap-geometry.ts`, `pretext/pages/demos/editorial-engine.ts`

## Performance Guardrails

- Is `prepare()` or `prepareWithSegments()` incorrectly running on resize? Prepare belongs outside the resize/frame hot path.
- Is the chosen API richer than the task needs? Use `prepare()`+`layout()` when only height is needed.
- Is `font` identical to the real renderer's font shorthand?
- Is `lineHeight` identical to the real renderer's line height?
- Is the width source explicit and stable?
- Is whitespace mode intentional?
- Do not rebuild prepared state during rendering or animation loops.
- If the final renderer only needs geometry, stay on `walkLineRanges()` as long as possible.
- Do not mistake pagination bugs for segmentation bugs before reproducing one paragraph in isolation.
- If streamed lines diverge from batch lines, reproduce the same paragraph with one width and compare `layoutNextLine()` against `layoutWithLines()`.

Locale and cache lifecycle:

- call `setLocale()` before preparing new text when locale-sensitive segmentation matters
- assume `setLocale()` clears caches
- do not expect existing prepared values to mutate after a locale change
- use `clearCache()` intentionally, not defensively

Validation surfaces: `bun run check`, `bun run site:build`, `bun run probe-check`, `bun run pre-wrap-check`

## When To Leave This File

- Engine debugging, whitespace semantics, or concrete mismatches: [behavior-contracts.md](behavior-contracts.md)
- Reusable adapters, wrappers, or cache boundaries: [adapter-patterns.md](adapter-patterns.md)
- Package shape, export concerns, or validation commands: [validation-and-tooling.md](validation-and-tooling.md)
