# Decision Contract

Use this file after the route survives first-principles and Socratic review.

The purpose is to turn a plausible route into a constrained implementation commitment.

## What A Decision Contract Must Contain

Every serious Pretext answer should be able to name:

1. The chosen output shape
2. The chosen integration surface
3. The invalidation tuple
4. The explicit assumptions
5. The proof obligations
6. The falsifiers
7. The lightest validation commands

If one of these is missing, the route is not yet decision-grade.

## Output Shape Commitment

State exactly one primary output family:

- height
- fixed lines
- streamed lines
- geometry
- variable-width lines
- diagnostics

Do not hedge across multiple primary shapes unless the task explicitly mixes them.

## Invalidation Commitment

Every answer must say what forces:

- re-prepare
- re-layout

At minimum, make explicit:

- `text`
- `font`
- `whiteSpace`
- locale state
- `maxWidth`
- `lineHeight`

## Assumption Commitment

State the concrete assumptions the implementation depends on:

- width source
- font shorthand source
- line-height source
- whitespace mode
- locale policy
- whether continuation across containers is required

If the task is renderer-specific, also state:

- whether the renderer needs final line text, geometry, or only height

## Proof Obligations

These are the claims that must remain true for the route to be valid.

### Height route

- prepared state is reused across width changes
- the rich path is not used unless line text or geometry is required

### Fixed-lines route

- concrete line strings are actually required
- `prepareWithSegments()` is justified
- line materialization happens at a fixed width

### Streamed-lines route

- paragraph continuation across containers is real
- `layoutNextLine()` is used because cursor continuity matters
- batch layout is not being used where continuation is required

### Variable-width route

- width budgets actually vary per line
- `layoutNextLine()` is used because widths vary, not merely because it exists

### Geometry or shrink-wrap route

- repeated probes stay geometry-only
- line text is deferred until the final width is chosen

### Internals route

- the package-facing path was shown insufficient
- the first incorrect observable state was localized before patching source

## Route Breakers

These are the facts that should force the route to be reconsidered.

Examples:

- width turns out to be fixed, so `variable-width` may be wrong
- paragraph does not continue across containers, so `streamed-lines` may be wrong
- the renderer only needs height, so `fixed-lines` is overkill
- the issue reproduces cleanly at the package surface, so `upstream-internals` is premature

## Validation Commitment

Every decision contract must end with the smallest defensible validation path.

The validation path should be:

- specific
- falsifiable
- proportionate to the change

Do not jump directly to broad harnesses when a narrow command can falsify the route first.

## Final Question

Before implementation, ask:

If I had to defend this route in one paragraph, with one repro, and one validation chain, what exactly am I claiming?
