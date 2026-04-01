# Socratic Review

Use this file after you have an initial route and need to challenge it before committing to code, validation, or upstream edits.

The point is not to add hesitation. The point is to prevent category mistakes.

## First-Principles Questions

Ask these before trusting your first answer:

1. What is the minimum output shape that would still satisfy the task?
2. What neighboring route am I overpaying for?
3. What fact would make my chosen route wrong?
4. What evidence class justifies this route:
   - exported package contract
   - upstream source ownership
   - real downstream implementation
   - maintained harness or validation artifact
5. Am I reaching for internals before reproducing the issue with exported APIs?

## Goal-Level Challenges

### If you chose `height`

Ask:

- Do I actually need line strings, cursors, or geometry?
- Am I using a rich path only because it feels safer?

Wrong neighboring routes:

- `fixed-lines` if the product only needs height
- `streamed-lines` if there is no continuation requirement

### If you chose `fixed-lines`

Ask:

- Do I really need concrete line text, or only widths and cursors?
- Is this one fixed region, or does the paragraph continue across regions?

Wrong neighboring routes:

- `height` if line text is required
- `geometry` if final line strings are required
- `streamed-lines` only if continuation does not matter

### If you chose `streamed-lines`

Ask:

- Is the paragraph really continuing across pages, columns, or slices?
- Am I confusing continuation with merely variable width?
- If width is constant, is cursor continuity still the real requirement?

Wrong neighboring routes:

- `fixed-lines` if the paragraph must continue across containers
- `variable-width` if widths do not actually vary per line

### If you chose `variable-width`

Ask:

- Do widths truly change per line, or am I just streaming through fixed-width containers?
- Would `streamed-lines` be the simpler truth?

Wrong neighboring routes:

- `fixed-lines` if widths vary per line
- `streamed-lines` if continuation, not width variation, is the real reason for `layoutNextLine()`

### If you chose `geometry` or `shrinkwrap`

Ask:

- Do I really need concrete line strings during the probe loop?
- Can I postpone line materialization until after choosing the width?

Wrong neighboring routes:

- `fixed-lines` if text is not needed during probing

### If you chose `correctness`, `diagnostics`, or `upstream-internals`

Ask:

- What is the smallest exported repro?
- Which module owns the first incorrect observable state?
- Is this a contract dispute, an integration mismatch, or a genuine source-level bug?

Wrong neighboring routes:

- source patches before exported repro
- broad harness runs before a narrow concrete mismatch is isolated

## Surface-Level Challenges

### `react-dom`

Ask:

- Is DOM involvement only width acquisition and lifecycle timing?
- Is this actually a wrapper-boundary problem rather than an API-choice problem?

### `custom-renderer`

Ask:

- Is this renderer really generic, or is it a reader, paginator, or text-layer problem?
- Is the renderer consuming final lines, geometry, or only height?

### `document-reader`

Ask:

- Is continuation across containers the core requirement?
- Are code blocks, poetry, or preserved-break regions mixed into normal prose?

### `package`

Ask:

- Is the failure in the published consumer contract rather than source semantics?
- Would a source-level diagnosis skip the actual npm-facing risk?

### `upstream`

Ask:

- Why is the package-facing API insufficient?
- Which module owns the first incorrect state, not just the most visible final output?

## Evidence Ladder

Collect evidence in this order when possible:

1. First-principles model
2. Exported contract and behavior docs
3. Narrow owner or tooling selector
4. Real downstream implementation precedent
5. Narrowest falsification command or harness

If you skip to step 4 or 5 without steps 1 to 3, you are likely cargo-culting.

## Falsification Questions

Before finalizing the route, ask:

- What command would falsify my chosen goal?
- What command would falsify my chosen surface?
- What observation would force me to downgrade from internals back to exported APIs?
- What observation would force me to upgrade from package-facing advice to upstream ownership analysis?

## External Precedent Rule

Real downstream examples are useful only after the route is already plausible.

Do not let an example choose the route for you.
Use examples to:

- validate the route
- sharpen the adapter boundary
- check whether your proposed shape already exists in practice

Run `python scripts/select_pretext_examples.py ...` only after the route survives the first-principles challenge.
