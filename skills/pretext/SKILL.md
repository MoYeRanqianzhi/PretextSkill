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

## Choose Output Shape And Surface

1. Choose the output-shape goal:
   - `height`
   - `fixed-lines`
   - `geometry`
   - `variable-width`
   - `shrinkwrap`
   - `profile`
   - `cache-locale`
   - `upstream-internals`
   - `diagnostics`
2. Choose the integration surface when it matters:
   - `react-dom`
   - `custom-renderer`
   - `package`
   - `upstream`
3. Run `python scripts/select_pretext_api.py --goal <goal> --surface <surface>` when you want the narrow API path, invalidation tuple, and reference set selected deterministically.

## Load Only The Needed Reference

- Read [reference/first-principles.md](reference/first-principles.md) for the irreducible model, invalidation rules, and architectural constraints.
- Read [reference/public-api.md](reference/public-api.md) for the normal product-facing package API.
- Read [reference/internal-exports.md](reference/internal-exports.md) only when the task explicitly needs diagnostic helpers, rich-path structural details, or source-level internals.
- Read [reference/internal-architecture.md](reference/internal-architecture.md) when modifying the upstream repo and you need module boundaries, data-flow guidance, or change-impact validation.
- Read [reference/whitespace-and-breaks.md](reference/whitespace-and-breaks.md) for whitespace modes, break policy, tabs, zero-width separators, and soft-hyphen behavior.
- Read [reference/script-and-browser-caveats.md](reference/script-and-browser-caveats.md) for script-sensitive segmentation, punctuation-glue classes, bidi, emoji, browser caveats, and research canaries.
- Read [reference/integration-lifecycle.md](reference/integration-lifecycle.md) for caching, resize, custom rendering, shrink-wrap, React or virtualization, and variable-width line flow patterns.
- Read [reference/react-dom-recipes.md](reference/react-dom-recipes.md) when you need React or DOM-oriented integration patterns such as height caches or whitespace-preserving editors.
- Read [reference/custom-renderer-recipes.md](reference/custom-renderer-recipes.md) when you need Canvas, SVG, WebGL, shrink-wrap, or variable-width rendering patterns.
- Read [reference/package-workflows.md](reference/package-workflows.md) when the task is about package shape, published-artifact confidence, or release-oriented validation.
- Read [reference/troubleshooting.md](reference/troubleshooting.md) for failure modes, research-backed guardrails, and diagnostic triage.
- Read [reference/validation-playbook.md](reference/validation-playbook.md) for Bun commands, dashboards, and escalation paths.
- Run `python scripts/select_pretext_validation.py --area ...` when you need the smallest defensible regression plan after changing a specific subsystem or surface.
- Run `python scripts/select_pretext_validation_by_files.py --path ...` when you already know which files changed and want the validation plan inferred from them.
- Run `python scripts/select_pretext_validation_from_git.py --repo pretext --rev-range ...` when you want validation inferred directly from upstream git diff state.

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
