---
name: pretext
description: Build with `@chenglou/pretext` for DOM-free multiline text measurement and layout. Use when implementing or refactoring height prediction, custom line rendering, shrink-wrap width search, variable-width text flow, whitespace-preserving editors, locale-aware segmentation, or Pretext-specific debugging and profiling in JavaScript or TypeScript. Also use when modifying the upstream Pretext repo while preserving the prepare/layout split, cache and locale rules, and other documented invariants.
---

# pretext

Treat Pretext as a two-phase engine:

- `prepare` phase: turn `(text, font, whiteSpace, locale)` into reusable measured state
- `layout` phase: turn `(prepared, maxWidth, lineHeight)` into height, lines, or line geometry

Keep that split intact. If a proposed solution reruns `prepare()` on resize or reintroduces DOM reads into the hot path, treat it as suspect.

## Ask These Questions First

1. Am I consuming the published package or modifying the upstream repo internals?
2. What output shape do I actually need: height, concrete lines, geometry, variable-width lines, or diagnostics?
3. Which inputs invalidate preparation, and which inputs invalidate only layout?
4. Is this a lifecycle problem, a behavior problem, a browser caveat, or a validation problem?

## Start From Output Shape

1. Need only block height or line count:
   - use `prepare()` plus `layout()`
2. Need concrete line strings at one fixed width:
   - use `prepareWithSegments()` plus `layoutWithLines()`
3. Need geometry and cursors without line strings:
   - use `prepareWithSegments()` plus `walkLineRanges()`
4. Need per-line varying widths:
   - use `prepareWithSegments()` plus `layoutNextLine()`
5. Need prepare-phase timing or segment-count diagnostics:
   - use `profilePrepare()` as a diagnostic helper, not as the normal integration path
6. Need locale or cache control:
   - use `setLocale()` or `clearCache()`
7. Need deeper access to `analysis.ts`, `measurement.ts`, `line-break.ts`, or `bidi.ts`:
   - treat them as source-level internals for upstream repo work, not as default package-public imports

## Load Only The Needed Reference

- Read [reference/first-principles.md](reference/first-principles.md) for the irreducible model, invalidation rules, and architectural constraints.
- Read [reference/public-api.md](reference/public-api.md) for the normal product-facing package API.
- Read [reference/internal-exports.md](reference/internal-exports.md) only when the task explicitly needs diagnostic helpers, rich-path structural details, or source-level internals.
- Read [reference/internal-architecture.md](reference/internal-architecture.md) when modifying the upstream repo and you need module boundaries, data-flow guidance, or change-impact validation.
- Read [reference/whitespace-and-breaks.md](reference/whitespace-and-breaks.md) for whitespace modes, break policy, tabs, zero-width separators, and soft-hyphen behavior.
- Read [reference/script-and-browser-caveats.md](reference/script-and-browser-caveats.md) for script-sensitive segmentation, punctuation-glue classes, bidi, emoji, browser caveats, and research canaries.
- Read [reference/integration-lifecycle.md](reference/integration-lifecycle.md) for caching, resize, custom rendering, shrink-wrap, React or virtualization, and variable-width line flow patterns.
- Read [reference/app-recipes.md](reference/app-recipes.md) when you need a concrete build pattern such as a React height cache, canvas rendering loop, shrink-wrap search, variable-width flow, or release-oriented package validation.
- Read [reference/troubleshooting.md](reference/troubleshooting.md) for failure modes, research-backed guardrails, and diagnostic triage.
- Read [reference/validation-playbook.md](reference/validation-playbook.md) for Bun commands, dashboards, and escalation paths.
- Run `python scripts/select_pretext_api.py --goal ...` when a deterministic recommendation is helpful.
- Run `python scripts/select_pretext_validation.py --area ...` when you need the smallest defensible regression plan after changing a specific subsystem.
- Run `python scripts/select_pretext_validation_by_files.py --path ...` when you already know which files changed and want the validation plan inferred from them.

## Non-Negotiables

1. Re-prepare only when text, font, whitespace mode, or locale changes.
2. Re-layout when width or line height changes.
3. Keep `font` and `lineHeight` synchronized with the real renderer.
4. Use `{ whiteSpace: 'pre-wrap' }` only when visible spaces, tabs, or hard breaks are semantically required.
5. `setLocale()` affects future prepare calls only and clears caches.
6. Avoid `system-ui` for accuracy-sensitive macOS work.

## Output Rules

1. State the chosen output shape and why it matches the task.
2. State the invalidation tuple: which inputs force re-prepare and which force only re-layout.
3. Call out whitespace mode, locale, width source, `font`, and `lineHeight` assumptions explicitly.
4. If you descend into internals, explain why the normal package-facing API is insufficient.
5. Separate integration mistakes from true engine limitations or upstream canaries.
6. Prefer the lightest validation path that can falsify the current assumption.
