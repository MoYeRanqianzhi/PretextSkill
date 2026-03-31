# Pretext Skill Design Notes

## Objective

Create a Codex skill that helps another agent integrate, evaluate, and troubleshoot the `@chenglou/pretext` multiline text layout library.

## Reference-Derived Product Model

The reference repository describes Pretext as a browser-focused JavaScript and TypeScript library for multiline text measurement and layout without DOM reflow.

Core exported workflows from the README and source:

- `prepare()` plus `layout()` for fast repeated height calculation after one-time preparation
- `prepareWithSegments()` plus `layoutWithLines()` for full line materialization
- `walkLineRanges()` for width and cursor-only iteration without building line strings
- `layoutNextLine()` for variable-width line-by-line layout
- `clearCache()` and `setLocale()` for cache and locale management
- `profilePrepare()` as a diagnostic export rather than a default integration path

## Skill Scope

The skill should help with:

- choosing the correct Pretext API for a product requirement
- choosing the correct integration surface, not only the correct API shape
- integrating Pretext into UI code without breaking the prepare/layout split
- preserving correctness constraints such as matching `font`, `lineHeight`, and `whiteSpace`
- debugging common accuracy pitfalls like `system-ui` on macOS or repeated `prepare()` calls
- planning validation using deterministic selectors instead of memory or intuition

## Design Principles

- Keep `SKILL.md` as a narrow Level-2 router
- Model decisions as `output shape + integration surface + invalidation tuple`
- Keep package-facing usage and upstream source modification paths clearly separated
- Treat validation taxonomy as shared data, not duplicated prose across scripts
- Prefer new references only when they reduce ambiguity or shrink the context needed for a common task

## Planned Skill Assets

- `SKILL.md`
  - first-principles routing only
- `reference/first-principles.md`
  - irreducible model and invalidation logic
- `reference/public-api.md`
  - normal package-facing API only
- `reference/internal-exports.md`
  - diagnostic helpers, rich-path structural fields, and source-level internals
- `reference/internal-architecture.md`
  - source-level module boundaries, data flow, and change-impact validation
- `reference/whitespace-and-breaks.md`
  - whitespace modes, break policy, tabs, zero-width separators, and soft-hyphen behavior
- `reference/script-and-browser-caveats.md`
  - script-sensitive segmentation, browser caveats, and research canaries
- `reference/react-dom-recipes.md`
  - React height caching, hook patterns, virtualization, editor-oriented patterns, and DOM guardrails
- `reference/custom-renderer-recipes.md`
  - Canvas/SVG/WebGL, shrink-wrap, variable-width flow, editorial flow, and frame-loop patterns
- `reference/package-workflows.md`
  - build, smoke-test, package-contract, and release-oriented package workflows
- `reference/integration-lifecycle.md`
  - prepare/layout lifecycle patterns for product code
- `reference/troubleshooting.md`
  - research-backed debugging guardrails and canaries
- `reference/validation-playbook.md`
  - area selection, git-diff routing, and validation surface inventory
- `scripts/select_pretext_api.py`
  - deterministic helper that maps `goal + surface` to the recommended API path, reference set, and first-principles questions
- `scripts/check_layout_api_sync.py`
  - deterministic maintenance check that compares documented API entries against `pretext/src/layout.ts`
- `scripts/pretext_validation_catalog.py`
  - shared validation taxonomy used by the validation-selector helpers
- `scripts/select_pretext_validation.py`
  - deterministic helper that maps a changed subsystem or surface to the smallest defensible validation plan
- `scripts/select_pretext_validation_by_files.py`
  - deterministic helper that infers validation scope from changed file paths
- `scripts/select_pretext_validation_from_git.py`
  - deterministic helper that infers validation scope directly from upstream git diff state

## Current Direction

- Keep package-facing usage and upstream source modification paths clearly separated
- Make API routing explicit across both output shape and integration surface
- Make validation routing deterministic instead of relying on memory or intuition
- Cover package, browser, corpus, Gatsby, probe, and demo-site validation surfaces with one shared taxonomy
- Prefer direct narrow recipe files once the implementation shape is known, without keeping an extra generic router file

## Non-Goals

The skill still does not try to:

- reproduce the entire research archive from the reference repository
- bundle the whole reference repo into the skill
- expose every internal source file in `SKILL.md`
- pretend repo-internal source modules are equivalent to stable package-public imports

## Evidence Pointers

- `pretext/README.md`
- `pretext/src/layout.ts`
- `pretext/src/layout.test.ts`
- `pretext/src/analysis.ts`
- `pretext/DEVELOPMENT.md`
- `pretext/STATUS.md`
- `pretext/RESEARCH.md`
- `pretext/package.json`
