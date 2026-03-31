# Changelog

## 2026-04-01

- Narrowed `SKILL.md` further into a first-principles router based on `goal + surface`
- Extended `select_pretext_api.py` with surface-aware routing for `react-dom`, `custom-renderer`, `package`, and `upstream`
- Added `skills/pretext/scripts/pretext_validation_catalog.py` as the shared validation taxonomy
- Refactored the validation selectors to consume one shared set of areas, commands, and source files
- Expanded validation coverage to include `accuracy-harness`, `probe-surface`, `corpus-tooling`, `gatsby-surface`, `package-workflow`, and `demo-site`
- Tightened by-file path matching to avoid over-matching unrelated workspace files
- Hardened the git-diff validator with Pretext repo auto-detection, `--all`, and safer flag semantics
- Deepened `react-dom-recipes.md` with stricter cache invalidation and DOM guardrails
- Deepened `custom-renderer-recipes.md` with upstream demo anchors for shrink-wrap, variable-width flow, and editorial layouts
- Deepened `package-workflows.md` with shipped-files versus exported-contract guidance and release-oriented guardrails
- Expanded `validation-playbook.md` to document the full selector surface and validation command inventory
- Refreshed durable memory in `docs/project-memory.md`, `docs/skill-design.md`, and `docs/validation-log.md`

## 2026-03-31

- Initialized the Git repository with `main` as the default branch
- Added the first `.gitignore` rule for the local reference repository
- Created the initial durable memory docs in `./docs/`
- Created and pushed the public GitHub repository `MoYeRanqianzhi/PretextSkill`
- Added and pushed the annotated bootstrap tag `v0.0.0`
- Ran `npx skills init` and generated the first minimal `skills/pretext/SKILL.md`
- Corrected `.gitignore` from `pretext/` to `/pretext/` so `skills/pretext/` is trackable
- Authored the first English `pretext` skill draft with curated references and a deterministic helper script
- Generated `skills/pretext/agents/openai.yaml` with `skill-creator` tooling
- Validated the skill structure with `quick_validate.py`
- Forward-tested the skill on height-only and variable-width line scenarios with fresh subagents
- Refactored the skill around first-principles progressive disclosure
- Expanded reference coverage to include the full public API, text behaviors, lifecycle patterns, and troubleshooting guardrails
- Extended the helper script to cover `profilePrepare()`, cache and locale guidance, and reference selection
- Reworked trigger wording toward build-mode intent instead of literal export enumeration
- Split product-facing API docs from internal exports and split text behavior docs into narrower reference files
- Added a sync-check helper to verify the skill's API docs stay aligned with `pretext/src/layout.ts`
- Added an internal architecture reference and a validation-selector helper for upstream source modifications
- Forward-tested geometry-only shrink-wrap usage and upstream preprocessing ownership routing
- Added application-level recipes and a file-based validation-selector helper
- Split app recipes into narrower recipe files and added git-diff-driven validation routing
- Added finer React hook and Canvas frame-loop recipe guidance
- Added explicit staged and working-tree presets to git-diff-based validation routing
