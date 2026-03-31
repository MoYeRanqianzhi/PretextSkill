# First Principles

Use this file when a task is ambiguous, architectural, or at risk of violating Pretext's core model.

## Irreducible Model

Pretext is a two-phase transform:

1. Prepare phase:
   - Inputs: `text`, `font`, `whiteSpace`, locale state
   - Work: normalize, segment, apply glue rules, measure, cache, compute breakability metadata
   - Output: reusable prepared state
2. Layout phase:
   - Inputs: prepared state, `maxWidth`, `lineHeight`
   - Work: arithmetic-only line walking over cached widths
   - Output: height, line count, line geometry, or concrete line strings

## Invalidation Rules

Re-run preparation when any prepare-phase input changes:

- `text`
- `font`
- `whiteSpace`
- locale state via `setLocale()`

Re-run only layout when only layout-phase inputs change:

- `maxWidth`
- `lineHeight`

## Output Families

- Height only:
  - `prepare()` plus `layout()`
- Fixed-width concrete lines:
  - `prepareWithSegments()` plus `layoutWithLines()`
- Fixed-width geometry only:
  - `prepareWithSegments()` plus `walkLineRanges()`
- Variable-width streaming lines:
  - `prepareWithSegments()` plus `layoutNextLine()`
- Prepare-phase diagnostics:
  - `profilePrepare()`

## Architectural Guardrails

- Do not move measurement back into `layout()`.
- Do not introduce DOM reads as the normal measurement path.
- Do not rerun `prepare()` just because width changed.
- Treat the fast `layout()` path as a design constraint, not an optimization accident.

## Key Inputs To Make Explicit

Every serious answer or implementation should make these inputs explicit:

- text source
- font shorthand
- line height
- width source
- whitespace mode
- locale requirements

## Research-Backed Heuristic

When a bug is tempting you toward a complicated runtime correction, first ask:

- Is this actually an integration mismatch?
- Is the behavior already covered by a preprocessing rule?
- Is the problem a known canary rather than a clean local bug?

Prefer small, semantically justified rules over heavy runtime work.
