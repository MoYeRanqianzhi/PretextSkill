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

## Planned Skill Assets

- `SKILL.md`
  - first-principles routing only
- `reference/first-principles.md`
  - irreducible model and invalidation logic
- `reference/public-api.md`
  - full public API surface and export cautions
- `reference/text-behaviors.md`
  - whitespace, glue, segmentation, and script behavior
- `reference/integration-lifecycle.md`
  - prepare/layout lifecycle patterns for product code
- `reference/troubleshooting.md`
  - research-backed debugging guardrails and canaries
- `reference/validation-playbook.md`
  - demo, benchmark, accuracy, and corpus-related validation entry points
- `scripts/select_pretext_api.py`
  - deterministic helper that maps a requested layout scenario to the recommended Pretext API path and reference set

## Evidence Pointers

- `pretext/README.md`
- `pretext/src/layout.ts`
- `pretext/src/analysis.ts`
- `pretext/DEVELOPMENT.md`
- `pretext/STATUS.md`
