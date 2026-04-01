# Adapter Patterns

Use this file when the task is not only "which Pretext API do I call," but also "where should the lifecycle boundary live in app code?"

## First-Principles Boundary

An adapter module should own the translation between product lifecycle and engine lifecycle:

- the product decides when text, font, whitespace mode, locale, width, and line height change
- the adapter decides which changes force re-prepare versus re-layout
- the engine stays a pure two-phase dependency behind that boundary

If every component imports Pretext directly and re-derives its own invalidation rules, drift is likely.

## Pattern 1: One Owner Module

Use one module, hook, composable, or service to own:

- CSS font shorthand construction
- prepared-state cache keys
- `setLocale()` timing
- `clearCache()` timing
- width-independent height or line helpers

Skeleton:

```ts
import {
  clearCache,
  layout,
  layoutWithLines,
  prepare,
  prepareWithSegments,
  setLocale,
} from '@chenglou/pretext'

type PrepareKey = {
  text: string
  font: string
  whiteSpace: 'normal' | 'pre-wrap'
  locale?: string
}

const heightCache = new Map<string, ReturnType<typeof prepare>>()
const richCache = new Map<string, ReturnType<typeof prepareWithSegments>>()

function keyOf(input: PrepareKey) {
  return JSON.stringify(input)
}

export function measureHeight(input: PrepareKey, width: number, lineHeight: number) {
  if (input.locale !== undefined) {
    setLocale(input.locale)
  }

  const key = keyOf(input)
  let prepared = heightCache.get(key)
  if (!prepared) {
    prepared = prepare(input.text, input.font, { whiteSpace: input.whiteSpace })
    heightCache.set(key, prepared)
  }

  return layout(prepared, width, lineHeight)
}

export function measureLines(input: PrepareKey, width: number, lineHeight: number) {
  if (input.locale !== undefined) {
    setLocale(input.locale)
  }

  const key = keyOf(input)
  let prepared = richCache.get(key)
  if (!prepared) {
    prepared = prepareWithSegments(input.text, input.font, {
      whiteSpace: input.whiteSpace,
    })
    richCache.set(key, prepared)
  }

  return layoutWithLines(prepared, width, lineHeight)
}

export function invalidateAll() {
  heightCache.clear()
  richCache.clear()
  clearCache()
}
```

## Pattern 2: Split Height And Rich Paths

Do not force every caller through `prepareWithSegments()` if many paths only need height.

Use:

- `prepare()` plus `layout()` for height-only prediction
- `prepareWithSegments()` plus `layoutWithLines()` or `layoutNextLine()` only when the renderer needs rich lines or cursors

This split appears in real wrappers because it preserves the prepare/layout model and avoids paying rich-path cost everywhere.

## Pattern 3: Keep Width Outside The Adapter Cache Key

Prepared-state caches should usually be keyed by:

- `text`
- `font`
- `whiteSpace`
- `locale`

Do not key prepared state by width unless the adapter is deliberately caching final layout results.

Width belongs in the layout phase.

## Pattern 4: SSR Or No-DOM Fallbacks Are A Separate Contract

If the runtime cannot perform normal preparation yet:

- expose a clearly degraded estimate path
- do not pretend the estimate is equivalent to prepared browser-backed output
- switch to normal Pretext preparation as soon as the real runtime is available

Good fallback boundaries:

- SSR placeholder height estimation
- loading-state measurement estimates
- feature-detected adapters that wait for DOM or renderer readiness

## Pattern 5: Locale And Cache Invalidation Must Be Centralized

Rules:

- call `setLocale()` before preparing new text when locale-sensitive segmentation matters
- assume `setLocale()` clears shared caches
- do not expect old prepared values to mutate after locale changes
- clear local prepared caches when locale policy changes

If locale invalidation happens ad hoc across components, stale prepared values are easy to keep accidentally.

## Pattern 6: Renderer State And Engine State Should Meet In One Place

The adapter should also own:

- font normalization from CSS or renderer props
- line-height normalization
- width acquisition policy

This avoids partial mismatches such as:

- CSS using one font while Pretext uses another
- line height inferred in two different ways
- one component using `pre-wrap` while another silently assumes `normal`

## Anti-Patterns

- rerunning `prepare()` inside resize handlers or frame loops
- calling `clearCache()` defensively on every render
- mixing height-only and rich-path callers behind one opaque method that always chooses the rich path
- deriving locale policy in components instead of in the adapter boundary
- storing prepared values in one cache and width-specific layout results in the same cache without clear separation

## External Anchors

Use these real implementations as precedent, not as copy-paste truth:

- `CoWork-OS/CoWork-OS`
  - `src/renderer/utils/pretext-adapter.ts`
  - centralizes font resolution, prepared caches, and invalidation
- `LucasBassetti/react-pretext`
  - `src/core/layout.ts`
  - separates height-only fast path from rich layout and adds SSR fallback
- `jonsnowljs/usePretext`
  - `src/usePretext.ts`
  - exposes framework wrapper state, resize observation, and optional line materialization
- `mayneyao/eidos`
  - `apps/web-app/components/table/views/gallery/utils.ts`
  - uses prepared caching for real product height prediction
- `PetrGuan/Prelayout`
  - `src/prepare.ts`
  - lifts prepared-state caching from text blocks to structured card schemas

See `python scripts/select_pretext_examples.py --pattern adapter-module` when you need the vetted external shortlist.
