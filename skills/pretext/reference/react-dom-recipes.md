# React And DOM Recipes

Use this file when the task is about React or DOM-oriented integration rather than custom rendering.

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
- keep the width source explicit, usually from layout or a resize observer

## React Hook Shape

Use this pattern when the app needs one reusable hook rather than ad hoc component logic.

```ts
import { useRef } from 'react'
import { prepare, layout } from '@chenglou/pretext'

export function usePretextHeightCache() {
  const cacheRef = useRef(new Map<string, ReturnType<typeof prepare>>())

  function measure(key: string, text: string, font: string, width: number, lineHeight: number) {
    let prepared = cacheRef.current.get(key)
    if (!prepared) {
      prepared = prepare(text, font)
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

## DOM Integration Guardrails

- Pretext is for DOM-free measurement, not post-hoc reconciliation with `getBoundingClientRect()`
- keep `font` and `lineHeight` synchronized with actual CSS
- keep prepare-phase state outside the resize hot path
- invalidate hook caches when locale or whitespace mode changes, not only when text changes
