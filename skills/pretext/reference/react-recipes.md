# React Recipes

Use this file when the task is about React components, resize-driven relayout, virtualization, or chat-style UIs.

## Height Cache Pattern

Use this pattern when the UI only needs height and line count.

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
- keep the width source explicit, typically from a resize observer or container measurement

## Virtualization And Occlusion

Use the same height-only path for:

- virtualized lists
- chat bubbles
- masonry-like height planning
- scroll-anchor preservation

Rules:

- keep the hot path on `layout()`
- avoid rerunning `prepare()` during resize or scroll loops

## Whitespace-Preserving React Editors

Use `prepareWithSegments()` plus `layoutWithLines()` for textarea-like editors that need concrete lines, tabs, hard breaks, or locale-sensitive text editing.

Rules:

- use `{ whiteSpace: 'pre-wrap' }`
- call `setLocale()` before preparing if locale-sensitive segmentation matters
- re-prepare after locale changes
- do not fall back to `prepare()` if the component needs actual line strings
