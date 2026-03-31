# Troubleshooting

Use this file when a task is about "wrong layout," browser mismatch, profiling, or possible upstream defects.

## First-Pass Debug Order

Check these before suspecting a Pretext bug:

1. `font` mismatch
2. `lineHeight` mismatch
3. width mismatch
4. wrong whitespace mode
5. wrong locale state
6. wrong API shape for the task

If the dispute is about what Pretext is supposed to do, not just why it is misbehaving in one integration, also load [behavior-contracts.md](behavior-contracts.md).

## Diagnostic Exports

### `profilePrepare()`

Use when the question is specifically about prepare-phase cost or segment counts.

It reports:

- `analysisMs`
- `measureMs`
- `totalMs`
- `analysisSegments`
- `preparedSegments`
- `breakableSegments`

Treat it as a diagnostic helper, not a runtime integration primitive.

## Research-Backed Guardrails

The upstream research log strongly favors these constraints:

- keep `layout()` arithmetic-only
- do not move measurement into `layout()`
- do not reintroduce DOM reads as the default measurement path
- prefer small semantic preprocessing rules over heavy runtime corrections

Be skeptical of fixes that:

- add pair-correction tables
- add shaping-aware width caches without strong evidence
- compensate for `system-ui` with guessed substitutions

## Known Caveats And Canary Areas

### Strong Caveats

- `system-ui` is unsafe on macOS
- emoji width discrepancies exist on Chrome and Firefox on macOS at small sizes

### Ongoing Canaries

The research log describes these as real steering surfaces rather than easy bugs:

- Myanmar quote and follower-style classes
- Japanese punctuation and exactness ceilings
- Chinese narrow-width and font-sensitive exactness ceilings
- Arabic fine-width shaping or context classes

Do not overfit a new heuristic to one canary without evidence that it generalizes.

## Invariants Worth Preserving

- `prepare()` and `prepareWithSegments()` agree on layout behavior
- `layoutNextLine()` reproduces `layoutWithLines()`
- `walkLineRanges()` reproduces geometry without materializing text
- rich line cursors reconstruct normalized source text exactly
- soft hyphen behavior preserves source slices correctly

## Bug Report Shape

Always include:

- input text
- font string
- line height
- width
- whitespace mode
- locale
- chosen API
- expected behavior
- actual behavior

Without those, most Pretext bugs are underspecified.
