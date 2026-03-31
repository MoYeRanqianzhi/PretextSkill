# Upstream Tooling Surfaces

Use this file when the task is about upstream diagnostic harnesses, browser checkers, dashboards, or site/reporting plumbing rather than the library API itself.

## First-Principles Split

Separate these questions before loading more context:

- Is the question about exported layout behavior?
  - stay on the API, behavior, or architecture references
- Is the question about which upstream page, checker, or dashboard should be used?
  - stay on this file first

The harness layer answers "where do I inspect or validate this?" rather than "which exported API do I call?"

## Tooling Areas

### `accuracy-harness`

Use when:

- broad browser parity is under question
- whitespace-preservation or browser-level accuracy needs a multi-row sweep
- the task is about refreshing or comparing checked-in browser snapshots

Primary files:

- `pretext/pages/accuracy.ts`
- `pretext/scripts/accuracy-check.ts`
- `pretext/scripts/pre-wrap-check.ts`

Main question answered:

- Does the engine still match browser layout across the maintained snapshot set?

### `benchmark-harness`

Use when:

- prepare or layout throughput changed
- benchmark methodology or benchmark snapshots changed
- the task is about prepare-phase split metrics such as analysis vs measurement

Primary files:

- `pretext/pages/benchmark.ts`
- `pretext/scripts/benchmark-check.ts`
- `pretext/scripts/status-dashboard.ts`

Main question answered:

- Did performance or benchmark reporting move, and where did the time go?

### `probe-surface`

Use when:

- one paragraph or one break mismatch needs deep inspection
- you need actual vs predicted lines and the first break mismatch
- a bug report is narrow enough that a whole corpus sweep would be wasteful

Primary files:

- `pretext/pages/probe.ts`
- `pretext/scripts/probe-check.ts`
- `pretext/pages/diagnostic-utils.ts`

Main question answered:

- Where is the first concrete mismatch for this one text case?

### `corpus-tooling`

Use when:

- a representative corpus row or long-form document mismatch is under investigation
- you need width sweeps, font-matrix comparisons, or corpus taxonomy work
- the task is about rebuilding corpus dashboards from checked-in snapshots

Primary files:

- `pretext/pages/corpus.ts`
- `pretext/scripts/corpus-check.ts`
- `pretext/scripts/corpus-sweep.ts`
- `pretext/scripts/corpus-font-matrix.ts`
- `pretext/scripts/corpus-status.ts`
- `pretext/scripts/corpus-taxonomy.ts`

Main question answered:

- How does the engine behave across representative long-form corpora?

### `gatsby-surface`

Use when:

- the task is really the Gatsby long-form compatibility slice
- you want the existing alias workflow rather than a generic corpus command

Primary files:

- `pretext/pages/gatsby.ts`
- `pretext/scripts/gatsby-check.ts`
- `pretext/scripts/gatsby-sweep.ts`

Main question answered:

- Does the Gatsby reference slice still behave like the maintained corpus target?

### `reporting-tooling`

Use when:

- posted-report plumbing or report hashing is under question
- dashboard/report helpers changed
- browser report capture and transport look broken

Primary files:

- `pretext/scripts/report-server.ts`
- `pretext/pages/report-utils.ts`
- `pretext/pages/diagnostic-utils.ts`

Main question answered:

- Is the reporting pipeline itself correct, independent of the engine semantics?

### `demo-site`

Use when:

- demo pages or site assembly changed
- the static site build or demo navigation is under question
- the task is about human-facing demo presentation rather than engine correctness

Primary files:

- `pretext/pages/demos/*`
- `pretext/scripts/build-demo-site.ts`

Main question answered:

- Does the maintained demo site still build and present the intended examples?

### `package-workflow`

Use when:

- published-artifact shape changed
- smoke-test consumers or dist output changed
- the package contract matters more than browser pages

Primary files:

- `pretext/package.json`
- `pretext/scripts/package-smoke-test.ts`
- `pretext/tsconfig.build.json`

Main question answered:

- Does the published package still match the consumer contract?

## Selection Rule

If the problem is:

- one paragraph and one mismatch:
  - choose `probe-surface`
- many browser rows or snapshot drift:
  - choose `accuracy-harness`
- throughput or benchmark split:
  - choose `benchmark-harness`
- long-form corpora:
  - choose `corpus-tooling`
- Gatsby-specific long-form slice:
  - choose `gatsby-surface`
- report transport or dashboard/report helpers:
  - choose `reporting-tooling`
- demo presentation or static site build:
  - choose `demo-site`
- package consumers and dist artifact:
  - choose `package-workflow`

If the problem is still "what behavior should the engine have?", switch back to [behavior-contracts.md](behavior-contracts.md) or [internal-architecture.md](internal-architecture.md).
