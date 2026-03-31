# Validation Playbook

Use this file when the request is about debugging, browser parity, performance, or regression checking.

## Choose The Smallest Useful Validation

- `bun run check`
  - typecheck and lint after code changes
- `bun test`
  - permanent invariant suite
- `bun run package-smoke-test`
  - confidence check for the published artifact

Use these before broader browser sweeps unless the task explicitly concerns browser parity or performance.

## Browser And Oracle Checks

- `bun run accuracy-check`
  - main Chrome browser sweep
- `bun run accuracy-check:safari`
- `bun run accuracy-check:firefox`
- `bun run pre-wrap-check`
  - dedicated whitespace-preservation oracle
- `bun run benchmark-check`
  - main benchmark snapshot
- `bun run benchmark-check:safari`

## Corpus And Dashboard Work

- `bun run corpus-check`
  - diagnose representative corpus mismatches
- `bun run corpus-sweep`
  - broader corpus regression pass
- `bun run corpus-font-matrix`
  - compare the same corpus under alternate fonts
- `bun run corpus-status`
  - rebuild the corpus dashboard from checked-in snapshots
- `bun run status-dashboard`
  - rebuild the main status dashboard from checked-in snapshots

## Demo And Manual Inspection

- `bun start`
  - start the demo server
- useful pages:
  - `/demos/index`
  - `/demos/accordion`
  - `/demos/bubbles`
  - `/demos/dynamic-layout`
  - `/demos/justification-comparison`
  - `/accuracy`
  - `/benchmark`
  - `/corpus`

## Source-Of-Truth Files

- `pretext/README.md`
  - public API framing
- `pretext/src/layout.ts`
  - exported semantics and source comments
- `pretext/src/layout.test.ts`
  - invariant and edge-case expectations
- `pretext/DEVELOPMENT.md`
  - developer commands and workflow
- `pretext/STATUS.md`
  - current main status dashboard pointers
- `pretext/RESEARCH.md`
  - durable reasoning log and guardrails

## Escalation Rule

Escalate from unit checks to browser sweeps only when the task touches:

- browser parity
- whitespace preservation
- performance or benchmarking
- long-form corpus correctness
- research-level canaries
