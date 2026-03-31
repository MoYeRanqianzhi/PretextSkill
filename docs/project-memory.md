# Pretext Skill Project Memory

## Project Summary

- Project name: `PretextSkill`
- Skill name: `pretext`
- Goal: build a standardized Codex skill from the local reference repository at `./pretext/`
- Reference repository: `https://github.com/chenglou/pretext`, cloned locally into `./pretext/`

## Repository Conventions

- Develop the skill in `./skills/pretext/`
- Store durable project memory in `./docs/`
- Use `npx skills init` as the project bootstrap entry point
- Keep the local reference repository ignored via the root-only rule `/pretext/`

## Current Status

- Git repository initialized and pushed to `main`
- Remote repository created at `https://github.com/MoYeRanqianzhi/PretextSkill`
- Release tag `v0.0.0` created for the repository bootstrap milestone
- Release tag `v0.1.0` created for the initial English skill milestone
- Release tag `v0.2.0` created for the first-principles disclosure refactor
- Release tag `v0.3.0` created for trigger refinement, API-boundary cleanup, and sync-check tooling
- Release tag `v0.4.0` created for upstream internal-architecture guidance and validation routing
- Release tag `v0.5.0` created for app-level recipes and file-based validation routing
- Release tag `v0.6.0` created for narrowed recipe routing and git-diff-based validation inference
- `npx skills init` produced the initial minimal `skills/pretext/SKILL.md` scaffold
- A `.gitignore` bug was discovered and fixed: `pretext/` also ignored `skills/pretext/`; the correct rule is `/pretext/`
- `skills/pretext/` now contains:
  - `SKILL.md`
  - `agents/openai.yaml`
  - `reference/first-principles.md`
  - `reference/public-api.md`
  - `reference/internal-exports.md`
  - `reference/internal-architecture.md`
  - `reference/whitespace-and-breaks.md`
  - `reference/script-and-browser-caveats.md`
  - `reference/react-dom-recipes.md`
  - `reference/custom-renderer-recipes.md`
  - `reference/package-workflows.md`
  - `reference/integration-lifecycle.md`
  - `reference/troubleshooting.md`
  - `reference/validation-playbook.md`
  - `scripts/select_pretext_api.py`
  - `scripts/check_layout_api_sync.py`
  - `scripts/select_pretext_validation.py`
  - `scripts/select_pretext_validation_by_files.py`
  - `scripts/select_pretext_validation_from_git.py`

## Durable Decisions

- Write the skill and new project docs in English to support internationalized reuse
- Keep progressive disclosure strict:
  - `SKILL.md` contains only the first-principles model, API-shape routing, and load instructions
  - `reference/` is split by cognitive concern, not by arbitrary feature buckets
  - `scripts/` is reserved for deterministic helpers that are worth executing
- Optimize trigger text for user intent first, and literal export names second
- Treat the reference repository as the source of truth for API names, workflows, and caveats
- Treat `src/layout.ts` as the normal product-facing API, and lower-level source modules as advanced diagnostics or upstream-hacking surfaces rather than package-public import targets
- Prefer direct narrow recipe files over a generic recipe bucket when the task intent is already clear

## Known Issues

- The skill may still need framework-specific recipes if future work targets React, Canvas-only pipelines, or packaging examples in more depth

## Next Tasks

- Add more recipes only when repeated demand appears
- Observe whether the new trigger wording improves build-mode activation without increasing false positives
- Consider deeper recipe references only if repeated demand appears for React hooks, Canvas loops, or package-release workflows
- Consider repo-specific heuristics only if plain git-diff validation routing proves insufficient

## Validation Record

- `python skills/pretext/scripts/select_pretext_api.py --goal variable-width --preserve-whitespace`
  - Result: script executed successfully and returned the expected API recommendation
- `python skills/pretext/scripts/select_pretext_api.py --goal profile --format json`
  - Result: script now returns diagnostic guidance for `profilePrepare()`, plus relevant references and invalidation rules
- `python skills/pretext/scripts/select_pretext_api.py --goal upstream-internals`
  - Result: script now routes explicitly to internal exports only when package-facing APIs are insufficient
- `python skills/pretext/scripts/select_pretext_api.py --goal <every-supported-goal> --format json`
  - Result: all helper-script goals executed successfully after the progressive-disclosure refactor
- `python skills/pretext/scripts/check_layout_api_sync.py`
  - Result: validates that the skill's API docs cover the exports from `pretext/src/layout.ts`
- `python skills/pretext/scripts/select_pretext_validation.py --area <area>`
  - Result: returns a minimal validation plan tied to the changed subsystem
- `python skills/pretext/scripts/select_pretext_validation.py --area analysis --format json`
  - Result: returns the expected first-pass validation commands and escalation checks for preprocessing changes
- `python skills/pretext/scripts/select_pretext_validation_by_files.py --path <changed-file> ...`
  - Result: infers validation scope from changed file ownership and returns the merged command set
- `python skills/pretext/scripts/select_pretext_validation_from_git.py --repo pretext --rev-range ...`
  - Result: infers validation scope directly from upstream git diff state
- Bare `src/...` paths are supported by the by-files validator when the script is invoked from the workspace root
- `python C:/Users/MoYeR/.codex/skills/.system/skill-creator/scripts/quick_validate.py G:/AgentProjects/skillsProjest/PretextSkill/skills/pretext`
  - Result: `Skill is valid!`
- `python C:/Users/MoYeR/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py G:/AgentProjects/skillsProjest/PretextSkill/skills/pretext ...`
  - Result: regenerated `agents/openai.yaml` with build-oriented trigger text and a valid `$pretext` default prompt
- Forward-test prompt: height-only React chat bubble estimation
  - Result: a fresh agent selected `prepare()` plus `layout()`, cached prepared state, and warned against rerunning `prepare()` on resize
- Forward-test prompt: Canvas text flowing around an image with Thai segmentation and preserved breaks
  - Result: a fresh agent selected `prepareWithSegments()` plus `layoutNextLine()`, required `{ whiteSpace: 'pre-wrap' }`, and correctly called out `setLocale('th')`
- Forward-test prompt: diagnose prepare-phase slowness on a large batch
  - Result: a fresh agent selected `profilePrepare()` and recommended `bun run benchmark-check` as the lightest validation step
- Forward-test prompt: textarea-like editor loses tabs and hard breaks after a locale switch
  - Result: a fresh agent selected `prepareWithSegments()` plus `layoutWithLines()`, required `{ whiteSpace: 'pre-wrap' }`, and enforced re-prepare after `setLocale()`
- Forward-test prompt: shrink-wrap width search without materializing line strings
  - Result: a fresh agent selected `prepareWithSegments()` plus `walkLineRanges()`, and kept geometry-only width probes in the layout phase
- Forward-test prompt: upstream preprocessing change for zero-width separators and punctuation glue
  - Result: a fresh agent assigned ownership to `analysis.ts`, recognized `line-break.ts` as the key downstream consumer, and chose the expected minimal validation plan
- Forward-test prompt: React height-caching integration
  - Result: a fresh agent selected the expected `prepare()` plus `layout()` cache pattern and the correct invalidation tuple
- Forward-test prompt: package entrypoint and declaration output changed
  - Result: a fresh agent selected `package-workflows.md`, the package confidence loop, and the correct package-contract checks

## Working Rules

- Document important findings before relying on memory
- Prefer verifiable claims with file-backed evidence
- Do not guess about API behavior, CLI behavior, or repo state when a local check is possible
