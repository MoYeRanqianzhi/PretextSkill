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
   - optional `issue`, `tooling-area`, or explicit validation scope when the task is already narrowed

2. Run `python scripts/select_pretext_route_plan.py --goal <goal> --surface <surface>` as the default entry point.
3. Read only the references named by the route plan, then run the smallest validation chain that can falsify the current assumption.

## Default Path

Use this path for normal implementation, refactor, and debugging work.

1. Start with `python scripts/select_pretext_route_plan.py --goal ... --surface ... --issue ... --tooling-area ...` when the task mixes API choice, upstream ownership, tooling-surface selection, or validation scoping.
2. Use `python scripts/select_pretext_api.py --goal <goal> --surface <surface>` only when the API route is already clear and you only need the narrow API path, invalidation tuple, and minimal reference set.
3. Read the smallest reference set first:
   - `reference/first-principles.md` for the irreducible model and invalidation rules
   - `reference/public-api.md` for normal package-facing API work
   - `reference/internal-exports.md` and `reference/internal-architecture.md` only when the package-facing route is insufficient and the task truly descends into upstream internals
4. Keep the default path light. Do not load critique, decision-contract, or bundled reasoning layers unless the task is ambiguous, high-stakes, or still feels under-justified after the first route pass.

## Escalation Path

Use escalation only when the default path leaves real uncertainty.

- Run `python scripts/select_pretext_socratic_review.py --goal ... --surface ... --issue ... --tooling-area ...` when the route is plausible but still needs to be challenged against neighboring routes, weaker evidence, or a better falsifier.
- Run `python scripts/select_pretext_decision_contract.py --goal ... --surface ... --issue ... --tooling-area ...` after the route survives critique and you need explicit assumptions, proof obligations, route breakers, and validation commitments before coding.
- Run `python scripts/select_pretext_reasoning_bundle.py --goal ... --surface ... --issue ... --tooling-area ...` only for high-ambiguity or high-risk tasks that need route selection, critique, and decision contract emitted as one integrated bundle.
- Run `python scripts/select_pretext_owner.py --issue ...` when upstream source ownership is the real question.
- Run `python scripts/select_pretext_tooling_surface.py --area ...` when the question is about harnesses, dashboards, probes, or report transport rather than the package API.
- Run `python scripts/select_pretext_examples.py --goal ... --surface ...` only after a route is already plausible and you need external implementation precedent to validate, not choose, the route.
- Run `python scripts/select_pretext_eval_design.py --role smoke|gate --goal ... --surface ... --reasoning-layer ...` when improving eval prompts, benchmark discrimination, or reasoning-layer coverage.

## Validation Order

Prefer the narrowest validation selector that matches what you already know:

1. Run `python scripts/select_pretext_validation_from_git.py --repo pretext --rev-range ...` when you want validation inferred directly from upstream git diff state.
2. Otherwise run `python scripts/select_pretext_validation_by_files.py --path ...` when you already know which files changed.
3. Otherwise run `python scripts/select_pretext_validation.py --area ...` when the change area is already known.
4. Report validation in this order: selected area, commands, follow-up checks, then the escalation trigger if those checks fail.

## On-Demand References

- Read [reference/behavior-contracts.md](reference/behavior-contracts.md) when the task is about exact semantic expectations, cross-API invariants, or whether a behavior change would be a regression.
- Read [reference/whitespace-and-breaks.md](reference/whitespace-and-breaks.md) for whitespace modes, break policy, tabs, zero-width separators, and soft-hyphen behavior.
- Read [reference/script-and-browser-caveats.md](reference/script-and-browser-caveats.md) for script-sensitive segmentation, punctuation glue, bidi, emoji, browser caveats, and research canaries.
- Read [reference/integration-lifecycle.md](reference/integration-lifecycle.md) for caching, resize, custom rendering, shrink-wrap, React or virtualization, and variable-width line flow patterns.
- Read [reference/adapter-patterns.md](reference/adapter-patterns.md) when you need a local facade, hook, service, or composable boundary informed by real downstream implementations.
- Read [reference/react-dom-recipes.md](reference/react-dom-recipes.md) for React or DOM-oriented integration patterns such as height caches or whitespace-preserving editors.
- Read [reference/custom-renderer-recipes.md](reference/custom-renderer-recipes.md) for Canvas, SVG, WebGL, shrink-wrap, or variable-width rendering patterns.
- Read [reference/document-reader-recipes.md](reference/document-reader-recipes.md) for PDF, EPUB, pagination, text-layer, or multi-column continuation patterns.
- Read [reference/package-workflows.md](reference/package-workflows.md) when the task is about package shape, published-artifact confidence, or release-oriented validation.
- Read [reference/upstream-tooling-surfaces.md](reference/upstream-tooling-surfaces.md) when the task is about upstream harnesses, browser checkers, dashboards, report transport, or demo-site plumbing rather than the package API itself.
- Read [reference/troubleshooting.md](reference/troubleshooting.md) for failure modes, research-backed guardrails, and diagnostic triage.
- Read [reference/validation-playbook.md](reference/validation-playbook.md) for Bun commands, dashboards, and escalation paths.
- Read [reference/socratic-review.md](reference/socratic-review.md) only after an initial route exists and still needs to be challenged.
- Read [reference/decision-contract.md](reference/decision-contract.md) only after a route survives critique and needs a decision-grade commitment.
- Read [reference/eval-design.md](reference/eval-design.md) only when the task is about eval design rather than product integration or engine behavior.

## Non-Negotiables

1. Re-prepare only when text, font, whitespace mode, or locale changes.
2. Re-layout when width or line height changes.
3. Keep `font` and `lineHeight` synchronized with the real renderer.
4. Use `prepare()` for height-only; use `prepareWithSegments()` for lines, geometry, or cursors.
5. Use `{ whiteSpace: 'pre-wrap' }` only when visible spaces, tabs, or hard breaks are semantically required.
6. `setLocale()` affects future prepare calls only and clears caches. Centralize locale changes; never call `setLocale()` inside per-measurement hot paths.
7. Avoid `system-ui` for accuracy-sensitive macOS work.

## Output Rules

1. State the chosen output shape and why it matches the task.
2. State the invalidation tuple: which inputs force re-prepare and which force only re-layout.
3. Call out whitespace mode, locale, width source, `font`, and `lineHeight` assumptions explicitly.
4. If you descend into internals, explain why the normal package-facing API is insufficient.
5. Separate integration mistakes from true engine limitations or upstream canaries.
6. Prefer the lightest validation path that can falsify the current assumption.
7. Show the validation command run and its output as evidence.
