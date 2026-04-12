---
name: pretext
description: "Pretext is a pure JS/TS text measurement & layout library that avoids DOM reflow. Use this skill when the task involves @chenglou/pretext: choosing APIs (prepare/layout), debugging measurement accuracy, integrating into React/Canvas/SVG/PDF renderers, handling whitespace or locale, or modifying upstream internals. Do not use for generic CSS, DOM, or text-layout work unless the task explicitly uses Pretext."
---

# pretext

Pretext is a two-phase engine — **prepare once, layout many times**:

- **`prepare` phase**: turn `(text, font, whiteSpace, locale)` into reusable measured state
- **`layout` phase**: turn `(prepared, maxWidth, lineHeight)` into height, lines, or line geometry

Keep that split intact. If a proposed solution reruns `prepare()` on resize or reintroduces DOM reads into the hot path, treat it as suspect.

## Simplest Case (80% of tasks)

Most tasks just need text height without touching the DOM:

```ts
import { prepare, layout } from '@chenglou/pretext'

const prepared = prepare('Hello world 你好', '16px Inter')
const { height, lineCount } = layout(prepared, containerWidth, 20)
// On resize: only rerun layout(), never re-prepare
```

If this covers your task, you're done. Read on only when you need lines, geometry, variable widths, or advanced features.

## Ask These Questions First

1. Am I consuming the published package or modifying the upstream repo internals?
2. What output shape do I actually need: height, concrete lines, streamed lines, geometry, variable-width lines, or diagnostics?
3. Which inputs invalidate preparation, and which inputs invalidate only layout?
4. Is this an integration problem, a correctness-contract problem, a browser caveat, or a validation problem?

## Quick Start

1. Name the smallest useful route inputs you already know:

   | Goal | When to use |
   |------|-------------|
   | `height` | Only need height/lineCount — use `prepare()` + `layout()` |
   | `fixed-lines` | Need actual line text at fixed width — use `prepareWithSegments()` + `layoutWithLines()` |
   | `streamed-lines` | Need lines one-at-a-time for pagination/columns — use `prepareWithSegments()` + `layoutNextLine()` |
   | `geometry` | Need line widths/cursors without building strings — use `prepareWithSegments()` + `walkLineRanges()` |
   | `variable-width` | Each line has a different max width — use `prepareWithSegments()` + `layoutNextLine()` |
   | `shrinkwrap` | Find the tightest container width — use `prepareWithSegments()` + `walkLineRanges()` in a binary search |
   | `profile` | Diagnose prepare-phase slowness — use `profilePrepare()` (diagnostic only) |
   | `correctness` | Debug measurement mismatch — check font/lineHeight sync, whitespace mode, locale |
   | `cache-locale` | Manage caches or switch locale — use `clearCache()` / `setLocale()` |

   - `surface` when it matters: `react-dom`, `custom-renderer`, `document-reader`, `package`, or `upstream`

2. Use the goal table to pick the API pair, then read the matching reference file from the Default Path below.
3. Run the smallest validation chain that can falsify the current assumption.

## Default Path

Use this path for normal implementation, refactor, and debugging work.

1. Use the goal table above to pick the right API pair. If the goal is unclear, start with `prepare()` + `layout()` (height-only) and escalate only when you need richer output.
2. Read the smallest reference set first:
   - `reference/public-api.md` for normal package-facing API work
   - `reference/behavior-contracts.md` when the task is about exact semantics, whitespace, script caveats, or debugging
   - `reference/recipes.md` when the task is about integration (React, Canvas, PDF, variable-width, etc.)
   - `reference/adapter-patterns.md` when you need a local facade, hook, or service boundary
   - `reference/internal-exports.md` and `reference/internal-architecture.md` only when the package-facing route is insufficient and the task truly descends into upstream internals
   - `reference/validation-and-tooling.md` for upstream harness commands, dashboards, and package workflows
3. Keep the default path light. Do not load multiple reference files unless the task genuinely spans multiple concerns.

## Escalation Path

Use escalation only when the default path leaves real uncertainty.

- When a bug tempts you toward a complicated runtime correction, first ask: Is this actually an integration mismatch? Is the behavior already covered by a preprocessing rule? Is the problem a known canary rather than a clean local bug? Prefer small, semantically justified rules over heavy runtime work.
- When upstream source ownership is the real question, check `reference/internal-architecture.md` for module ownership.
- When the question is about harnesses, dashboards, probes, or report transport, check `reference/validation-and-tooling.md`.
- When you need external implementation precedent, check `reference/adapter-patterns.md` for vetted downstream examples.

## Validation Order

Prefer the narrowest validation selector that matches what you already know:

1. Run `bun run scripts/select-pretext-validation-from-git.ts --repo pretext --rev-range ...` when you want validation inferred directly from upstream git diff state.
2. Run `bun run scripts/select-pretext-validation-from-git.ts --path <file> --path <file>` when you already know which files changed.
3. When the change area is already known, look up the area in `reference/validation-and-tooling.md` for the matching commands.
4. Report validation in this order: selected area, commands, follow-up checks, then the escalation trigger if those checks fail.

## On-Demand References

- Read [reference/behavior-contracts.md](reference/behavior-contracts.md) for exact semantic expectations, cross-API invariants, whitespace modes, break policy, tabs, script-sensitive segmentation, punctuation glue, bidi, emoji, browser caveats, research canaries, and diagnostic triage.
- Read [reference/recipes.md](reference/recipes.md) for integration patterns: React/DOM, Canvas/SVG/WebGL, PDF/EPUB/pagination, variable-width flow, caching, resize, shrink-wrap, and performance guardrails.
- Read [reference/adapter-patterns.md](reference/adapter-patterns.md) when you need a local facade, hook, service, or composable boundary informed by real downstream implementations.
- Read [reference/public-api.md](reference/public-api.md) for the complete public API reference.
- Read [reference/internal-exports.md](reference/internal-exports.md) and [reference/internal-architecture.md](reference/internal-architecture.md) only when the package-facing API is insufficient and the task descends into upstream internals.
- Read [reference/validation-and-tooling.md](reference/validation-and-tooling.md) for Bun commands, upstream harnesses, dashboards, package workflows, and escalation paths.

## Non-Negotiables

1. Re-prepare only when text, font, whitespace mode, or locale changes.
2. Re-layout when width or line height changes.
3. Keep `font` and `lineHeight` synchronized with the real renderer.
4. Use `prepare()` for height-only; use `prepareWithSegments()` for lines, geometry, or cursors.
5. Use `{ whiteSpace: 'pre-wrap' }` only when visible spaces, tabs, or hard breaks are semantically required.
6. `setLocale()` affects future prepare calls only and clears caches. Centralize locale changes; never call `setLocale()` inside per-measurement hot paths.
7. Avoid `system-ui` for accuracy-sensitive macOS work.

## Architectural Guardrails

- Do not move measurement back into `layout()`.
- Do not introduce DOM reads as the normal measurement path.
- Do not rerun `prepare()` just because width changed.
- Treat the fast `layout()` path as a design constraint, not an optimization accident.
- When a bug tempts you toward a complicated runtime correction, first ask: Is this actually an integration mismatch? Is the behavior already covered by a preprocessing rule? Is the problem a known canary rather than a clean local bug? Prefer small, semantically justified rules over heavy runtime work.

## Output Rules

1. State the chosen output shape and why it matches the task.
2. State the invalidation tuple: which inputs force re-prepare and which force only re-layout.
3. Call out whitespace mode, locale, width source, `font`, and `lineHeight` assumptions explicitly.
4. If you descend into internals, explain why the normal package-facing API is insufficient.
5. Separate integration mistakes from true engine limitations or upstream canaries.
6. Prefer the lightest validation path that can falsify the current assumption.
7. Show the validation command run and its output as evidence.

Every serious answer or implementation should make these inputs explicit: text source, font shorthand, line height, width source, whitespace mode, and locale requirements.
