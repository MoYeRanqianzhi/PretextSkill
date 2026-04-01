# Pretext Implementation Landscape

## Purpose

This document records real-world `pretext` implementation code that is worth using as reference when improving the `pretext` skill.

The goal is not to collect visual inspiration. The goal is to identify:

- real downstream code that imports `@chenglou/pretext`
- real wrappers and adapters around Pretext APIs
- real product surfaces where Pretext is already used
- useful forks and ports that reveal architectural extension points

## Snapshot

- Research date: `2026-04-01`
- Package anchor used for search: `@chenglou/pretext@0.0.3`
- Local upstream source anchor at research time: `a8d1e35d3973a0f63c007f7645f4a8918135a57b`
- Star counts below were captured on `2026-04-01`

## Search Method

Public-web pass first:

- Search for `@chenglou/pretext`
- Search for `@chenglou/pretext demo`, `playground`, `react`, `pdfjs`, `epub`
- Check whether public pages expose source code or only show demos or commentary

Code-bearing pass second:

- GitHub code search for exact imports of `@chenglou/pretext`
- GitHub code search for direct API names such as:
  - `prepare`
  - `layout`
  - `prepareWithSegments`
  - `layoutWithLines`
  - `layoutNextLine`
  - `walkLineRanges`
- GitHub repo metadata checks for stars, license, and update recency

## What The Public Web Showed

The public web did help confirm that Pretext has package visibility and demo visibility, but most non-GitHub results were secondary rather than code-authoritative:

- official package page and version index
- official or community demos
- blog posts and showcase-style articles

Important conclusion:

- non-GitHub search is useful for discovery
- actual inspectable implementation code is concentrated in source repositories
- public demo pages without source links should not be treated as implementation references

## Vetted Direct Implementations

### High-signal product or library references

| Repo | Stars | Surface | Direct evidence | Why it matters |
|---|---:|---|---|---|
| [`mayneyao/eidos`](https://github.com/mayneyao/eidos) | 3095 | gallery card height prediction | `apps/web-app/components/table/views/gallery/utils.ts` imports `prepare` and `layout` | Strong evidence for height-only caching and virtual-grid sizing in a real product |
| [`xiaoiver/infinite-canvas-tutorial`](https://github.com/xiaoiver/infinite-canvas-tutorial) | 959 | canvas text metrics | `packages/ecs/src/systems/ComputeTextMetrics.ts` imports `prepareWithSegments` and `layoutWithLines` | Strong evidence for renderer-side text layout with bidi and script-specific fallbacks |
| [`CoWork-OS/CoWork-OS`](https://github.com/CoWork-OS/CoWork-OS) | 184 | centralized adapter for UI virtualization | `src/renderer/utils/pretext-adapter.ts` imports `prepare`, `layout`, and `clearCache` | Strong evidence for the "one adapter module owns font resolution, prepared caches, and invalidation" pattern |
| [`PetrGuan/Prelayout`](https://github.com/PetrGuan/Prelayout) | 12 | reusable virtualization helper library | `src/prepare.ts` imports `prepare` and stores `PreparedText` handles per field | Good evidence for lifting the prepare/layout split from one text block to structured card schemas |
| [`0xNyk/pretext-playground`](https://github.com/0xNyk/pretext-playground) | 15 | canvas ASCII and dynamic typography | `src/dragon.ts` imports `prepareWithSegments` and `layoutWithLines` | Useful evidence that Pretext can drive dynamic canvas-heavy scenes, not only normal UI text |

### Narrow but still real downstream references

| Repo | Stars | Surface | Direct evidence | Why it matters |
|---|---:|---|---|---|
| [`LucasBassetti/react-pretext`](https://github.com/LucasBassetti/react-pretext) | 2 | headless React adapter | `src/core/layout.ts` uses both `prepare/layout` and `prepareWithSegments/layoutWithLines` | Good reference for separating height-only fast paths from line-materialization paths, plus SSR fallback |
| [`codehz/chat-layout`](https://github.com/codehz/chat-layout) | 2 | chat line fitting | `src/text.ts` imports `prepareWithSegments` and `layoutWithLines` | Good reference for first-line extraction and chat-bubble line materialization |
| [`alpeshvas/pretext-pdfjs`](https://github.com/alpeshvas/pretext-pdfjs) | 0 | PDF.js text layer | `src/pretext-text-layer.js` lazily imports `@chenglou/pretext` and uses `prepareWithSegments/layoutWithLines` | Good reference for reflow-capable PDF text layers and measurement caching |
| [`zsh-eng/epub-reader-demo`](https://github.com/zsh-eng/epub-reader-demo) | 0 | EPUB pagination | `src/lib/pagination/layout-text-lines.ts` uses `layoutNextLine` and `layoutWithLines` | Good reference for pagination, incremental cursor-based layout, and pre-wrap code blocks |
| [`jonsnowljs/usePretext`](https://github.com/jonsnowljs/usePretext) | 1 | Vue composable | `src/usePretext.ts` uses `setLocale`, `prepare`, `prepareWithSegments`, `layout`, and `layoutWithLines` | Good reference for framework wrappers, resize observation, and optional line materialization |
| [`beorn/silvery`](https://github.com/beorn/silvery) | 4 | terminal UI pixel measurer | `packages/ag-react/src/ui/canvas/pretext-measurer.ts` uses `prepareWithSegments` and `layoutWithLines` | Good reference for non-DOM renderers and pixel-accurate wrapping inside custom layout engines |
| [`heygen-com/hyperframes`](https://github.com/heygen-com/hyperframes) | 4 | text fitting | `packages/core/src/text/fitTextFontSize.ts` uses `prepare` and `layout` | Good reference for repeated single-line fit checks without line materialization |

## Useful Forks And Ports

These are useful for architecture study, but they are not the same thing as downstream consumers using the published package directly.

| Repo | Stars | Type | Why it matters |
|---|---:|---|---|
| [`skastr0/pretext-skia`](https://github.com/skastr0/pretext-skia) | 0 | backend port / fork | Ports the Pretext model to React Native Skia and exposes `prepare`, `prepareWithSegments`, `layout`, `layoutWithLines`, `walkLineRanges`, and `layoutNextLine` equivalents |

## Rejected Or Downgraded References

### Public demo pages without inspectable source

These may be useful for awareness, but not as implementation truth:

- showcase pages
- blog posts
- announcement-style articles
- demos with no clear source link

### Repositories with weak evidence

These should not be treated as first-line references:

- repos where `pretext` appears only in `package.json`, `bun.lock`, or generated files
- one-off aesthetic demos with low stars and no clear engineering depth
- "magic newspaper", "Bad Apple", or other visually interesting demos unless the source itself clearly uses Pretext and the code quality is inspectable

## Stable Implementation Patterns Extracted

### Pattern 1: Height-only fast path

Use:

- `prepare()` once
- `layout()` many times

Seen in:

- `mayneyao/eidos`
- `CoWork-OS/CoWork-OS`
- `heygen-com/hyperframes`
- `PetrGuan/Prelayout`

### Pattern 2: Full line materialization

Use:

- `prepareWithSegments()`
- `layoutWithLines()`

Seen in:

- `xiaoiver/infinite-canvas-tutorial`
- `LucasBassetti/react-pretext`
- `codehz/chat-layout`
- `0xNyk/pretext-playground`
- `alpeshvas/pretext-pdfjs`
- `beorn/silvery`

### Pattern 3: Incremental or variable-width pagination

Use:

- `layoutNextLine()`

Seen in:

- `zsh-eng/epub-reader-demo`

This is the clearest external evidence for cursor-based, progressive line construction.

### Pattern 4: Adapter module ownership

Wrap Pretext in one local adapter that owns:

- font string construction
- prepared-text caching
- `clearCache()` usage
- locale invalidation
- framework-specific width observation

Seen in:

- `CoWork-OS/CoWork-OS`
- `LucasBassetti/react-pretext`
- `jonsnowljs/usePretext`

### Pattern 5: Renderer-specific fallbacks remain necessary

Several real implementations still add local fallbacks around Pretext:

- SSR estimation in `LucasBassetti/react-pretext`
- script-specific glyph handling in `xiaoiver/infinite-canvas-tutorial`
- canvas or grapheme fallback measurement in `beorn/silvery`

This means the skill should not oversell Pretext as a zero-wrapper drop-in for every renderer.

## Implications For The Skill

The current research supports several future improvements:

- add stronger adapter-pattern guidance as a first-class integration recipe
- add external-reference notes for:
  - React wrappers
  - Vue wrappers
  - PDF text layers
  - EPUB or pagination flows
  - canvas or terminal renderers
- keep the prepare/layout split central, because real downstream users repeatedly converge on that design
- keep line-materialization and height-only flows separate, because real downstream code treats them as different performance surfaces
- keep renderer caveats explicit, because real implementations still layer browser, SSR, or script-specific handling around Pretext

## Durable Rule

When updating this skill, treat verified implementation code as the primary reference class.

Do not upgrade a visual demo, article, or inspiration page into a reference until the underlying source code has been located and inspected.
