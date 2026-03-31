---
name: pretext
description: Integrate, evaluate, or troubleshoot `@chenglou/pretext` for DOM-free multiline text measurement and layout. Use when Codex needs the correct Pretext export for a task (`prepare`, `layout`, `prepareWithSegments`, `layoutWithLines`, `walkLineRanges`, `layoutNextLine`, `profilePrepare`, `clearCache`, `setLocale`), needs guidance on whitespace, soft hyphens, zero-width separators, locale-sensitive segmentation, mixed-direction text, or browser caveats, or needs to validate behavior and performance with the upstream repo's Bun commands and dashboards.
---

# pretext

Treat Pretext as a two-phase engine:

- `prepare` phase: turn `(text, font, whiteSpace, locale)` into reusable measured state
- `layout` phase: turn `(prepared, maxWidth, lineHeight)` into height, lines, or line geometry

Keep that split intact. If a proposed solution reruns `prepare()` on resize or reintroduces DOM reads into the hot path, treat it as suspect.

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
   - use `profilePrepare()`
6. Need locale or cache control:
   - use `setLocale()` or `clearCache()`
7. Need deeper internals from `analysis.ts`, `measurement.ts`, `line-break.ts`, or `bidi.ts`:
   - treat them as low-level exports, not the default product API

## Load Only The Needed Reference

- Read [reference/first-principles.md](reference/first-principles.md) for the irreducible model, invalidation rules, and non-negotiable architecture constraints.
- Read [reference/public-api.md](reference/public-api.md) for exact exported functions, types, and which exports are product-facing versus low-level.
- Read [reference/text-behaviors.md](reference/text-behaviors.md) for whitespace, soft-hyphen, zero-width separator, punctuation-glue, locale, bidi, emoji, and CJK behavior.
- Read [reference/integration-lifecycle.md](reference/integration-lifecycle.md) for caching, resize, custom rendering, shrink-wrap, React or virtualization, and variable-width line flow patterns.
- Read [reference/troubleshooting.md](reference/troubleshooting.md) for likely failure modes, research-backed guardrails, and known canary areas.
- Read [reference/validation-playbook.md](reference/validation-playbook.md) for Bun commands, dashboards, and escalation paths.
- Run `python scripts/select_pretext_api.py --goal ...` when a deterministic recommendation is helpful.

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
4. Separate integration mistakes from true engine limitations or upstream canaries.
5. Prefer the lightest validation path that can falsify the current assumption.
