# Internal Architecture

Use this file only when the task is about modifying the cloned upstream repo, not merely consuming the published package.

Before changing source internals, also load [behavior-contracts.md](behavior-contracts.md) if the proposed patch could change exported semantics.

## Architectural Center Of Gravity

Pretext keeps one non-negotiable split:

1. Prepare phase:
   - analyze text
   - measure segments
   - cache derived metadata
2. Layout phase:
   - walk prepared widths with arithmetic-only logic

Any upstream change should preserve that split unless there is strong evidence that the architectural center is wrong.

## Module Responsibilities

### `src/analysis.ts`

Owns:

- whitespace normalization
- segmentation with `Intl.Segmenter`
- segment kinds such as `space`, `tab`, `soft-hyphen`, `hard-break`, and `zero-width-break`
- punctuation glue rules
- script-sensitive preprocessing such as CJK, Arabic, and Myanmar-oriented rules
- locale-sensitive word segmentation state
- chunk generation for hard-break-aware line walking

Reach here when the problem is:

- wrong segments
- wrong glue or break boundaries
- locale-sensitive segmentation
- whitespace-mode semantics

Avoid changing this file when the real problem is:

- width measurement
- tab-stop arithmetic
- line walking over already-correct segments

### `src/measurement.ts`

Owns:

- canvas or OffscreenCanvas measurement access
- per-font segment metric caches
- engine profile detection
- emoji correction detection and caching
- grapheme-width and prefix-width derivation for breakable runs

Reach here when the problem is:

- measured widths are wrong
- browser-specific fit tolerance or prefix-width policy is wrong
- emoji correction is wrong
- measurement caching is wrong

Avoid changing this file when the real problem is:

- segmentation or punctuation glue
- line-break cursor logic

### `src/line-break.ts`

Owns:

- arithmetic-only line walking
- tab-stop advance arithmetic
- fit decisions for breakable runs and soft hyphens
- conversion from prepared arrays into line ranges and counts
- alignment between `countPreparedLines()`, `walkPreparedLines()`, and range stepping

Reach here when the problem is:

- line boundaries are wrong despite correct segments and widths
- tab handling during layout is wrong
- `walkLineRanges()` or `layoutNextLine()` diverges from `layoutWithLines()`

Avoid changing this file when the real problem is:

- segment generation
- width measurement

### `src/layout.ts`

Owns:

- orchestration across analysis, measurement, bidi, and line-break layers
- public package-facing API surface
- shape of prepared rich-path data
- rich line materialization from line ranges
- cache reset and locale reset wiring
- `profilePrepare()` as a diagnostic export

Reach here when the problem is:

- public API shape should change
- prepared rich-path fields should change
- package-level orchestration is wrong
- `prepare()` and `prepareWithSegments()` no longer behave consistently

Avoid using this file as the first place to patch deep behavior unless the bug is truly orchestration-level.

### `src/bidi.ts`

Owns:

- segment-level bidi metadata for rich-path custom rendering

Reach here when the problem is:

- rich-path bidi metadata is wrong
- custom rendering depending on `segLevels` is wrong

Avoid changing this file when the issue only affects ordinary line counting or height estimation.

## Data Flow

1. `layout.ts` calls `analyzeText()` in `analysis.ts`
2. `layout.ts` calls measurement helpers in `measurement.ts`
3. `layout.ts` optionally computes segment bidi levels through `bidi.ts`
4. `layout.ts` exposes prepared structures
5. `line-break.ts` consumes prepared arrays to count or walk lines
6. `layout.ts` materializes line text only for rich APIs

## Safe Change Questions

Before patching upstream code, ask:

1. Which module owns the first incorrect observable state?
2. Is the bug in segmentation, measurement, line walking, orchestration, or bidi metadata?
3. Am I about to move work from prepare into layout?
4. Am I about to overfit a known canary instead of fixing a general rule?

If ownership is still unclear after those questions, run `python scripts/select_pretext_owner.py --issue ...` before patching source.

## Change-To-Validation Map

### If you change `src/analysis.ts`

Always rerun:

- `bun test`
- `bun run check`

Usually rerun:

- `bun run pre-wrap-check` for whitespace changes
- `bun run corpus-check` for segmentation or glue changes
- `bun run accuracy-check` if broad browser parity may move

### If you change `src/measurement.ts`

Always rerun:

- `bun test`
- `bun run check`

Usually rerun:

- `bun run benchmark-check`
- `bun run accuracy-check`
- `bun run probe-check` when the change is browser-measurement-specific

### If you change `src/line-break.ts`

Always rerun:

- `bun test`
- `bun run check`

Usually rerun:

- `bun run pre-wrap-check`
- `bun run accuracy-check`
- `bun run corpus-check` for line-fit regressions

### If you change `src/layout.ts`

Always rerun:

- `bun test`
- `bun run check`
- `bun run package-smoke-test`

Usually rerun:

- `bun run benchmark-check`
- `bun run accuracy-check`

### If you change `src/bidi.ts`

Always rerun:

- `bun test`
- `bun run check`

Usually rerun:

- `bun run accuracy-check`
- a mixed-direction focused repro or corpus check

## Escalation Rule

If a change touches more than one of `analysis.ts`, `measurement.ts`, `line-break.ts`, `layout.ts`, or `bidi.ts`, escalate validation breadth. Do not rely on one narrow repro once the architectural boundary is crossed.
