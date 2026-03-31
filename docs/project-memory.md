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
- Release tag `v0.6.1` created for streamlining recipe references
- Release tag `v0.6.2` created for finalized recipe routing and git-based validation cleanup
- Release tag `v0.6.3` created for surface-aware API routing and the shared validation catalog
- Release tag `v0.6.4` created for behavior-contract routing and correctness-focused progressive disclosure
- `skills/pretext/` now contains:
  - `SKILL.md`
  - `agents/openai.yaml`
  - `reference/first-principles.md`
  - `reference/public-api.md`
  - `reference/internal-exports.md`
  - `reference/internal-architecture.md`
  - `reference/whitespace-and-breaks.md`
  - `reference/behavior-contracts.md`
  - `reference/script-and-browser-caveats.md`
  - `reference/react-dom-recipes.md`
  - `reference/custom-renderer-recipes.md`
  - `reference/package-workflows.md`
  - `reference/integration-lifecycle.md`
  - `reference/troubleshooting.md`
  - `reference/validation-playbook.md`
  - `scripts/select_pretext_api.py`
  - `scripts/check_layout_api_sync.py`
  - `scripts/pretext_validation_catalog.py`
  - `scripts/select_pretext_validation.py`
  - `scripts/select_pretext_validation_by_files.py`
  - `scripts/select_pretext_validation_from_git.py`

## Durable Decisions

- Write the skill and project docs in English to support internationalized reuse
- Keep progressive disclosure strict:
  - `SKILL.md` contains only the first-principles model, routing questions, and load instructions
  - `reference/` is split by cognitive concern, correctness contract, and integration surface
  - `scripts/` is reserved for deterministic helpers that are worth executing
- Model API selection as `goal + surface + invalidation tuple`
- Model correctness work separately from API selection so agents do not confuse "what should happen" with "which API should I call"
- Treat the reference repository as the source of truth for API names, workflows, caveats, and validation commands
- Treat `src/layout.ts` as the normal product-facing API, and lower-level source modules as advanced diagnostics or upstream-hacking surfaces rather than package-public import targets
- Treat validation taxonomy as shared data across scripts so the manual selector, by-file selector, and git-diff selector cannot drift silently
- Prefer direct narrow recipe files over a generic recipe bucket when the task intent is already clear

## Known Issues

- There is not yet a formal `skill-creator` eval suite checked into `evals/`
- The git-diff validator assumes the local checkout still follows the current `./pretext/` sibling layout when `--repo` is omitted
- Future demand may justify even narrower renderer references such as dedicated `SVG` or `WebGL` recipes

## Next Tasks

- Add formal eval prompts and an iterative review loop using the `skill-creator` workflow
- Observe whether the new `goal + surface` API selector reduces unnecessary reference loading in real agent use
- Observe whether explicit correctness-contract routing reduces false jumps into upstream internals during debugging
- Add repo-specific git-diff heuristics only if repeated multi-file change clusters prove worth encoding

## Validation Record

- `python <codex-home>/skills/.system/skill-creator/scripts/quick_validate.py skills/pretext`
  - Result: `Skill is valid!`
- `python skills/pretext/scripts/select_pretext_api.py --goal variable-width --preserve-whitespace`
  - Result: script executed successfully and returned the expected API recommendation
- `python skills/pretext/scripts/select_pretext_api.py --goal profile --format json`
  - Result: returns diagnostic guidance for `profilePrepare()`, plus relevant references and invalidation rules
- `python skills/pretext/scripts/select_pretext_api.py --goal upstream-internals`
  - Result: routes explicitly to internal exports only when package-facing APIs are insufficient
- `python skills/pretext/scripts/select_pretext_api.py --goal height --surface react-dom --format json`
  - Result: now adds `react-dom-recipes.md` to the narrow reference set for height-only UI work
- `python skills/pretext/scripts/select_pretext_api.py --goal shrinkwrap --surface custom-renderer`
  - Result: now adds `custom-renderer-recipes.md` and renderer-specific guardrails for geometry-only shrink-wrap work
- `python skills/pretext/scripts/select_pretext_api.py --goal correctness --surface upstream --preserve-whitespace --locale-sensitive --format json`
  - Result: now routes correctness disputes to `behavior-contracts.md` plus the appropriate diagnostic references and preserves whitespace/locale guidance
- `python skills/pretext/scripts/select_pretext_api.py --goal <every-supported-goal> --format json`
  - Result: all helper-script goals executed successfully after the progressive-disclosure refactor
- `python skills/pretext/scripts/check_layout_api_sync.py`
  - Result: validates that the skill's API docs cover the exports from `pretext/src/layout.ts`
- `python skills/pretext/scripts/select_pretext_validation.py --area <area>`
  - Result: returns a minimal validation plan tied to the changed subsystem or surface
- `python skills/pretext/scripts/select_pretext_validation.py --area package-workflow --format json`
  - Result: returns the expected package-contract confidence loop
- `python skills/pretext/scripts/select_pretext_validation.py --area accuracy-harness`
  - Result: returns the expected browser-parity and whitespace-oracle plan
- `python skills/pretext/scripts/select_pretext_validation_by_files.py --path <changed-file> ...`
  - Result: infers validation scope from changed file ownership and returns the merged command set
- `python skills/pretext/scripts/select_pretext_validation_by_files.py --path pretext/pages/demos/bubbles.ts --path pretext/pages/probe.ts`
  - Result: now merges demo-site and probe validation surfaces correctly
- `python skills/pretext/scripts/select_pretext_validation_by_files.py --path docs/CHANGELOG.md --path pretext/CHANGELOG.md`
  - Result: ignores the workspace changelog and matches only the upstream `pretext/CHANGELOG.md` package surface
- `python skills/pretext/scripts/select_pretext_validation_from_git.py --repo pretext --rev-range HEAD~1..HEAD`
  - Result: infers validation scope directly from upstream git diff state
- `python skills/pretext/scripts/select_pretext_validation_from_git.py --repo pretext --staged`
  - Result: supports an explicit staged-change mode and returns an empty plan when no upstream files are staged
- `Get-ChildItem 'skills/pretext/scripts' -Filter '*.py' | ForEach-Object { python -m py_compile $_.FullName }`
  - Result: all helper scripts compile after the shared-catalog refactor
- `python <codex-home>/skills/.system/skill-creator/scripts/generate_openai_yaml.py skills/pretext ...`
  - Result: regenerated `agents/openai.yaml` with build-oriented trigger text and a valid `$pretext` default prompt
- Forward-test prompt: height-only React chat bubble estimation
  - Result: a fresh agent selected `prepare()` plus `layout()`, cached prepared state correctly, and warned against rerunning `prepare()` on resize
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
