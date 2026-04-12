# Validation & Tooling

Use this file when validating changes, choosing upstream harnesses, or checking package confidence.

## Quick Validation

- `bun run check` — typecheck and lint after code changes
- `bun test` — permanent invariant suite
- `bun run build:package` — rebuild package output when artifact shape matters
- `bun run package-smoke-test` — confidence check for the published artifact

Use these before broader browser sweeps unless the task explicitly concerns browser parity, long-form accuracy, or benchmarking.

## Tooling Areas

### `accuracy-harness`

Broad browser parity, whitespace-preservation sweeps, refreshing checked-in browser snapshots.

- `pretext/pages/accuracy.ts`
- `pretext/scripts/accuracy-check.ts`
- `pretext/scripts/pre-wrap-check.ts`

Snapshot commands write full-sweep results to `accuracy/*.json` for checked-in regression baselines.

### `benchmark-harness`

Throughput changes, benchmark methodology or snapshot changes, prepare-phase split metrics.

- `pretext/pages/benchmark.ts`
- `pretext/scripts/benchmark-check.ts`
- `pretext/scripts/status-dashboard.ts`

### `probe-surface`

Single-paragraph or single-break mismatch inspection; actual vs predicted lines.

- `pretext/pages/probe.ts`
- `pretext/scripts/probe-check.ts`
- `pretext/pages/diagnostic-utils.ts`

### `corpus-tooling`

Representative corpus rows, width sweeps, font-matrix comparisons, corpus taxonomy, dashboard rebuilds.

- `pretext/pages/corpus.ts`
- `pretext/scripts/corpus-check.ts`
- `pretext/scripts/corpus-sweep.ts`
- `pretext/scripts/corpus-font-matrix.ts`
- `pretext/scripts/corpus-representative.ts`
- `pretext/scripts/corpus-status.ts`
- `pretext/scripts/corpus-taxonomy.ts`

### `gatsby-surface`

Gatsby long-form compatibility slice and existing alias workflow.

- `pretext/pages/gatsby.ts`
- `pretext/scripts/gatsby-check.ts`
- `pretext/scripts/gatsby-sweep.ts`

### `reporting-tooling`

Report plumbing, report hashing, dashboard/report helpers, browser report capture.

- `pretext/scripts/report-server.ts`
- `pretext/pages/report-utils.ts`
- `pretext/pages/diagnostic-utils.ts`

### `demo-site`

Demo pages, site assembly, static site build, demo navigation.

- `pretext/pages/demos/*`
- `pretext/scripts/build-demo-site.ts`

### `package-workflow`

Published-artifact shape, smoke-test consumers, dist output, package contract.

- `pretext/package.json`
- `pretext/scripts/package-smoke-test.ts`
- `pretext/tsconfig.build.json`

### Selection Rule

| Problem | Area |
|---------|------|
| One paragraph, one mismatch | `probe-surface` |
| Many browser rows or snapshot drift | `accuracy-harness` |
| Throughput or benchmark split | `benchmark-harness` |
| Long-form corpora | `corpus-tooling` |
| Gatsby-specific long-form slice | `gatsby-surface` |
| Report transport or dashboard helpers | `reporting-tooling` |
| Demo presentation or static site build | `demo-site` |
| Package consumers and dist artifact | `package-workflow` |

If the problem is "what behavior should the engine have?", switch to [behavior-contracts.md](behavior-contracts.md) or [internal-architecture.md](internal-architecture.md).

## Browser & Oracle Checks

- `bun run accuracy-check` — main Chrome browser sweep
- `bun run accuracy-check:firefox`
- `bun run accuracy-check:safari`
- `bun run accuracy-snapshot` — full Chrome sweep → `accuracy/chrome.json`
- `bun run accuracy-snapshot:firefox` — full Firefox sweep → `accuracy/firefox.json`
- `bun run accuracy-snapshot:safari` — full Safari sweep → `accuracy/safari.json`
- `bun run pre-wrap-check` — dedicated whitespace-preservation oracle
- `bun run probe-check` — single-paragraph interactive parity surface
- `bun run probe-check:safari`
- `bun run benchmark-check` — main benchmark snapshot
- `bun run benchmark-check:safari`

## Corpus & Long-Form Checks

- `bun run corpus-check` — diagnose representative corpus mismatches
- `bun run corpus-check:safari`
- `bun run corpus-sweep` — broader corpus regression pass
- `bun run corpus-sweep:safari`
- `bun run corpus-font-matrix` — compare the same corpus under alternate fonts
- `bun run corpus-font-matrix:safari`
- `bun run corpus-status` — rebuild the corpus dashboard from checked-in snapshots
- `bun run corpus-status:refresh` — end-to-end refresh: re-sample representative corpus, re-sweep Chrome, rebuild dashboard
- `bun run corpus-representative` — refresh representative corpus samples → `corpora/representative.json`
- `bun run corpus-taxonomy` — inspect the corpus categorization layer
- `bun run gatsby-check` — long-form article parity check
- `bun run gatsby-check:safari`
- `bun run gatsby-sweep` — broader Gatsby-derived sweep
- `bun run gatsby-sweep:safari`

## Package Confidence

The published package is a built ESM artifact:

- `main` → `./dist/layout.js`
- `types` → `./dist/layout.d.ts`
- `exports` map exposes: `.`, `./demos/*`, `./assets/*`, `./package.json`

The tarball also ships `dist/`, `src/`, `pages/demos/`, `pages/assets/`, `CHANGELOG.md`, `LICENSE` — but the `exports` map defines the supported import surface, not the file list.

**Confidence loop commands:**

- `bun run check`
- `bun run build:package`
- `bun run package-smoke-test`

Run this loop when: package entrypoint changes, exported types change, build output changes, consumer-facing API shape changes, or `package.json` / `tsconfig.build.json` / `scripts/package-smoke-test.ts` changes.

**Mechanics:** `prepack` rebuilds `dist/` before packaging. Internal `.ts` source imports keep `.js` specifiers so `tsc -p tsconfig.build.json` emits correct runtime JS and declarations. Use [public-api.md](public-api.md) for the package-facing contract.

## Demo & Site Checks

- `bun run site:build` — rebuild the demo site
- `bun start` — start the demo server for manual inspection
- `bun run start:watch` — start the demo server with file watching (auto-reload)
- `bun run start:lan` — start the demo server on LAN (0.0.0.0)
- `bun run status-dashboard` — rebuild status reporting from checked-in snapshots

Useful pages: `/demos/index`, `/demos/accordion`, `/demos/bubbles`, `/demos/dynamic-layout`, `/demos/editorial-engine`, `/demos/justification-comparison`, `/accuracy`, `/benchmark`, `/corpus`, `/probe`

## Source-Of-Truth Files

- `pretext/README.md` — public API framing
- `pretext/src/layout.ts` — exported semantics and source comments
- `pretext/src/layout.test.ts` — invariant and edge-case expectations
- `pretext/DEVELOPMENT.md` — developer commands and workflow
- `pretext/STATUS.md` — current main status dashboard pointers
- `pretext/RESEARCH.md` — durable reasoning log and guardrails
- `pretext/package.json` — package contract and script inventory
- `pretext/CHANGELOG.md` — release history
- `pretext/tsconfig.build.json` — package build configuration

## Escalation Rule

Escalate from quick validation to browser sweeps, corpus checks, or site builds when the task touches:

- browser parity or whitespace preservation
- performance or benchmarking
- long-form corpus correctness
- demo-site behavior
- package-consumer contract
- research-level canaries
- benchmark methodology changes
- text-engine internals that could move correctness or performance
