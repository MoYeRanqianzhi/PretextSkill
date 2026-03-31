# Validation Playbook

Use this file when the request is about debugging, browser parity, performance, release confidence, or regression checking.

## Deterministic Routing

Use the selector scripts before guessing:

- `python scripts/select_pretext_validation.py --area <area>`
- `python scripts/select_pretext_validation_by_files.py --path <changed-file> ...`
- `python scripts/select_pretext_validation_from_git.py --repo pretext --rev-range <rev-range>`
- `python scripts/select_pretext_validation_from_git.py --repo pretext --staged`

Supported areas:

- `analysis`
- `measurement`
- `line-break`
- `layout-api`
- `bidi`
- `benchmark-harness`
- `accuracy-harness`
- `probe-surface`
- `corpus-tooling`
- `gatsby-surface`
- `package-workflow`
- `demo-site`
- `reporting-tooling`

## Choose The Smallest Useful Validation

- `bun run check`
  - typecheck and lint after code changes
- `bun test`
  - permanent invariant suite
- `bun run build:package`
  - rebuild package output when artifact shape matters
- `bun run package-smoke-test`
  - confidence check for the published artifact

Use these before broader browser sweeps unless the task explicitly concerns browser parity, long-form accuracy, or benchmarking.

## Browser And Oracle Checks

- `bun run accuracy-check`
  - main Chrome browser sweep
- `bun run accuracy-check:safari`
- `bun run accuracy-check:firefox`
- `bun run pre-wrap-check`
  - dedicated whitespace-preservation oracle
- `bun run probe-check`
  - single-paragraph interactive parity surface
- `bun run benchmark-check`
  - main benchmark snapshot
- `bun run benchmark-check:safari`

## Corpus And Long-Form Checks

- `bun run corpus-check`
  - diagnose representative corpus mismatches
- `bun run corpus-sweep`
  - broader corpus regression pass
- `bun run corpus-font-matrix`
  - compare the same corpus under alternate fonts
- `bun run corpus-status`
  - rebuild the corpus dashboard from checked-in snapshots
- `bun run corpus-representative`
  - refresh representative corpus samples
- `bun run corpus-taxonomy`
  - inspect the corpus categorization layer
- `bun run gatsby-check`
  - long-form article parity check
- `bun run gatsby-sweep`
  - broader Gatsby-derived sweep

## Demo And Site Checks

- `bun run site:build`
  - rebuild the demo site
- `bun start`
  - start the demo server for targeted manual inspection

## Reporting And Posted-Report Tooling

- `bun run status-dashboard`
  - rebuild status reporting that depends on checked-in snapshots and report utilities

Use the `reporting-tooling` area when the task touches:

- `pretext/scripts/report-server.ts`
- `pretext/pages/report-utils.ts`
- `pretext/pages/diagnostic-utils.ts`

Useful pages:

- `/demos/index`
- `/demos/accordion`
- `/demos/bubbles`
- `/demos/dynamic-layout`
- `/demos/editorial-engine`
- `/demos/justification-comparison`
- `/accuracy`
- `/benchmark`
- `/corpus`
- `/probe`

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
- `pretext/package.json`
  - package contract and script inventory

## Escalation Rule

Escalate from unit checks to browser sweeps, corpus checks, or site builds when the task touches:

- browser parity
- whitespace preservation
- performance or benchmarking
- long-form corpus correctness
- demo-site behavior
- package-consumer contract
- research-level canaries
