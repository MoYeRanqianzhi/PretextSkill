# React And DOM Recipes

Use this file when the task is about React or DOM-oriented integration rather than custom rendering.

## First-Principles Lens

- React state and hooks do not change the engine model:
  - `prepare()` or `prepareWithSegments()` owns text analysis and measurement
  - `layout()` or the rich layout APIs own width-time recomputation
- The DOM may provide container width or lifecycle timing, but Pretext should still be the text-measurement authority
- Width changes belong in the layout phase
- Text, font, whitespace mode, and locale changes belong in the prepare phase

## Height Cache For Virtualization Or Chat Bubbles

Use this pattern when the UI only needs height and line count.

```ts
import { prepare, layout } from '@chenglou/pretext'

type PreparedKey = {
  text: string
  font: string
  whiteSpace: 'normal' | 'pre-wrap'
  locale: string | undefined
}

function measureBlock(prepared: ReturnType<typeof prepare>, width: number, lineHeight: number) {
  return layout(prepared, width, lineHeight)
}
```

Rules:

- cache prepared state by `(text, font, whiteSpace, locale)`
- rerun `layout()` on width or line-height changes
- rerun `prepare()` only when prepare inputs change
- keep the width source explicit, usually from layout, a container observer, or known column math

Upstream anchors:

- `pretext/pages/demos/accordion.ts`
- `pretext/pages/demos/masonry/index.ts`

## React Hook Shape

Use this pattern when the app needs one reusable hook rather than ad hoc component logic.

```ts
import { useRef } from 'react'
import { prepare, layout } from '@chenglou/pretext'

export function usePretextHeightCache() {
  const cacheRef = useRef(new Map<string, ReturnType<typeof prepare>>())

  function measure(
    text: string,
    font: string,
    width: number,
    lineHeight: number,
    whiteSpace: 'normal' | 'pre-wrap' = 'normal',
    locale?: string,
  ) {
    const key = JSON.stringify({ text, font, whiteSpace, locale })
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
- keep the hook focused on caching and measurement, not on DOM reads
- if locale or whitespace mode can change, include them in the key, call `setLocale(locale)` before preparing new text when needed, and rebuild prepared state

## Whitespace-Preserving Editor

Use this path for textarea-like editing, tabs, visible hard breaks, or locale-aware text editing.

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
- use `pre-wrap` only when spaces, tabs, or hard breaks are meant to stay visible

Validation surfaces:

- `bun run pre-wrap-check`
- `bun run probe-check`

## DOM Integration Guardrails

- Pretext is for DOM-free text measurement, not post-hoc reconciliation with `getBoundingClientRect()` or `offsetHeight`
- keep `font` and `lineHeight` synchronized with actual CSS
- keep prepare-phase state outside the resize hot path
- invalidate hook caches when locale or whitespace mode changes, not only when text changes
- prefer `ResizeObserver` or layout math for width; do not remeasure rendered text with DOM APIs after adopting Pretext

Upstream anchors:

- `pretext/pages/probe.ts`
- `pretext/pages/corpus.ts`

## When React Is The Wrong Surface

- If the product only needs engine debugging, start from `reference/troubleshooting.md`
- If the renderer needs line strings, cursors, or variable-width flow outside the DOM, switch to [custom-renderer-recipes.md](custom-renderer-recipes.md)
- If the task is actually about designing a reusable local wrapper or cache boundary, switch to [adapter-patterns.md](adapter-patterns.md)
- If the task is about exported package shape rather than component integration, switch to [package-workflows.md](package-workflows.md)
