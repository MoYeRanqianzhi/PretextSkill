# Validation Playbook

Use this file when the request is about debugging, browser parity, or regression checking.

## First-Pass Debugging

Check these in order before suspecting a library bug:

1. `font` mismatch between Pretext and the real renderer
2. `lineHeight` mismatch
3. width mismatch
4. wrong whitespace mode
5. wrong locale state
6. using a rich API when height-only logic would be simpler, or vice versa

## Upstream Invariants Worth Preserving

The upstream test suite and comments establish several important expectations:

- `prepare()` and `prepareWithSegments()` should agree on layout behavior.
- `layoutNextLine()` should reproduce `layoutWithLines()` line boundaries.
- `walkLineRanges()` should reproduce geometry without materializing line text.
- `pre-wrap` mode should preserve spaces, tabs, and hard breaks in a browser-like way.

Treat regressions against those invariants as high-signal failures.

## Upstream Commands

When working inside the cloned upstream repo at `./pretext/`, use the existing commands instead of inventing ad hoc validation:

- `bun run check` for typecheck and lint
- `bun test` for invariant tests
- `bun run accuracy-check` for browser accuracy sweeps
- `bun run pre-wrap-check` for whitespace-preservation behavior
- `bun run benchmark-check` for the main benchmark snapshot
- `bun run package-smoke-test` for published-artifact confidence

Use broader sweeps only when the task actually concerns accuracy dashboards or corpus analysis.

- `bun run corpus-check` for representative corpus mismatches at selected widths
- `bun run corpus-sweep` for broader corpus regressions

## Source Files To Read First

For traceable answers, start from these upstream files:

- `pretext/README.md` for public API and usage framing
- `pretext/DEVELOPMENT.md` for commands and validation workflow
- `pretext/src/layout.ts` for exported API semantics
- `pretext/src/layout.test.ts` for invariants and edge cases
- `pretext/STATUS.md` when the task is about current accuracy or benchmark sources of truth

## Bug Report Shape

When reporting or triaging a suspected issue, always include:

- input text
- font string
- line height
- width
- whitespace mode
- locale
- chosen API
- expected behavior
- actual behavior

This keeps reports reproducible and prevents vague "layout looks wrong" debugging.
