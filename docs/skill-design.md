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

## Skill Scope

The skill should help with:

- Choosing the correct Pretext API for a product requirement
- Integrating Pretext into UI code without breaking the prepare/layout split
- Preserving correctness constraints such as matching `font`, `lineHeight`, and `whiteSpace`
- Debugging common accuracy pitfalls like `system-ui` on macOS or repeated `prepare()` calls
- Planning validation using the reference repo's demo pages and benchmark or accuracy scripts

## Non-Goals

The first version does not need to:

- Reproduce the entire research archive from the reference repository
- Bundle the whole reference repo into the skill
- Expose every internal source file in `SKILL.md`
- Pretend repo-internal source modules are equivalent to stable package-public imports

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
- `reference/integration-lifecycle.md`
  - prepare/layout lifecycle patterns for product code
- `reference/troubleshooting.md`
  - research-backed debugging guardrails and canaries
- `reference/validation-playbook.md`
  - demo, benchmark, accuracy, and corpus-related validation entry points
- `scripts/select_pretext_api.py`
  - deterministic helper that maps a requested layout scenario to the recommended Pretext API path, reference set, and first-principles questions
- `scripts/check_layout_api_sync.py`
  - deterministic maintenance check that compares documented API entries against `pretext/src/layout.ts`
- `scripts/select_pretext_validation.py`
  - deterministic helper that maps a changed subsystem to the smallest defensible validation plan

## Current Direction

- Keep package-facing usage and upstream source modification paths clearly separated
- Make validation routing deterministic instead of relying on memory or intuition
- Prefer new references only when they reduce ambiguity or shrink the context needed for a common task

## Evidence Pointers

- `pretext/README.md`
- `pretext/src/layout.ts`
- `pretext/src/analysis.ts`
- `pretext/DEVELOPMENT.md`
- `pretext/STATUS.md`
