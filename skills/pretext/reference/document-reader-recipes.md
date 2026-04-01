# Document Reader Recipes

Use this file when the task is about PDF text layers, EPUB readers, pagination, multi-column continuation, or any reader where paragraphs continue across containers.

## First-Principles Lens

Document-reader integrations have a different primary constraint from ordinary fixed-width rendering:

- text often continues across pages, columns, or regions
- width may stay constant per region, but cursor continuity still matters
- selection, hit testing, and page assembly often need stable line materialization
- preserved breaks and code-like blocks may need a different path than flowing prose

The key question is often not "is width fixed?" but "does the paragraph continue?"

## Fixed-Region Text Layer

Use this path when one text item is laid out into one known page or region width.

```ts
import { prepareWithSegments, layoutWithLines } from '@chenglou/pretext'

const prepared = prepareWithSegments(text, font, options)
const result = layoutWithLines(prepared, regionWidth, lineHeight)
```

Use it for:

- PDF.js-style text layers
- one page region with stable width
- search-hit overlays that need explicit line strings and widths

## Streamed Pagination Or Column Continuation

Use this path when the same prepared paragraph must continue across:

- pages
- columns
- scrolling windows
- virtualized reader slices

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
- keep one prepared paragraph while the text, font, whitespace mode, and locale stay stable
- do not rebuild prepared state per page or column
- width may be constant or variable; cursor continuity is the main reason to choose this path

## Preserved-Break Blocks Inside Readers

For code blocks, poetry, or preserved editor content embedded inside a reader:

- use `prepareWithSegments(..., { whiteSpace: 'pre-wrap' })`
- use `layoutWithLines()` when the block is laid out inside one known region
- use `layoutNextLine()` when the preserved block itself must continue across containers

## Reader Adapter Boundary

Keep these responsibilities outside the core Pretext call:

- page or column width selection
- region switching
- inline-image or atomic-block reservation
- page-break policy
- selection box synthesis

Pretext should own line fitting, not full page semantics.

## Guardrails

- do not mistake pagination bugs for segmentation bugs before reproducing one paragraph in isolation
- separate atomic media placement from inline text flow
- if streamed lines diverge from batch lines, reproduce the same paragraph with one width and compare `layoutNextLine()` against `layoutWithLines()`
- when the issue is one concrete mismatch, prefer the probe surface before broader sweeps

## External Anchors

- `alpeshvas/pretext-pdfjs`
  - `src/pretext-text-layer.js`
  - shows Pretext-backed PDF text-layer integration and responsive reflow
- `zsh-eng/epub-reader-demo`
  - `src/lib/pagination/layout-text-lines.ts`
  - shows cursor-based pagination with `layoutNextLine()`

See:

- `python scripts/select_pretext_examples.py --surface document-reader`
- `python scripts/select_pretext_examples.py --goal streamed-lines`
