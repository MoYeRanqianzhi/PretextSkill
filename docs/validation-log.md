# Validation Log

## 2026-03-31

### Structure Validation

- Command:
  - `python C:/Users/MoYeR/.codex/skills/.system/skill-creator/scripts/quick_validate.py G:/AgentProjects/skillsProjest/PretextSkill/skills/pretext`
- Result:
  - `Skill is valid!`

### Script Validation

- Command:
  - `python skills/pretext/scripts/select_pretext_api.py --goal height --format json`
- Result:
  - Returned a valid JSON recommendation for the height-only path

- Command:
  - `python skills/pretext/scripts/select_pretext_api.py --goal variable-width --preserve-whitespace --locale-sensitive`
- Result:
  - Returned the expected `layoutNextLine()` recommendation with `pre-wrap` and locale guidance

- Command:
  - `python skills/pretext/scripts/select_pretext_api.py --goal profile --format json`
- Result:
  - Returned the expected `profilePrepare()` guidance, including reference files and invalidation rules

- Command:
  - `python skills/pretext/scripts/select_pretext_api.py --goal upstream-internals`
- Result:
  - Returned the expected internal-surface routing and explicit package-vs-upstream questions

- Command:
  - `python skills/pretext/scripts/check_layout_api_sync.py`
- Result:
  - Returned `Layout export docs are in sync.`

- Command:
  - `python skills/pretext/scripts/select_pretext_validation.py --area line-break`
- Result:
  - Returned the expected minimal validation plan for line-walking changes

- Command:
  - `python skills/pretext/scripts/select_pretext_validation_by_files.py --path pretext/src/analysis.ts --path pretext/src/line-break.ts`
- Result:
  - Returned the expected merged validation plan spanning analysis and line-break ownership

- Command:
  - `python skills/pretext/scripts/select_pretext_validation_by_files.py --path pretext/src/layout.ts --format json`
- Result:
  - Returned the expected layout-API validation plan including package smoke testing and API-doc sync checks

- Command:
  - `python skills/pretext/scripts/select_pretext_validation_from_git.py --repo pretext --rev-range HEAD~1..HEAD`
- Result:
  - Returned a git-diff-derived validation plan based on the changed upstream files

- Command:
  - `python skills/pretext/scripts/select_pretext_validation_by_files.py --path src/analysis.ts --path src/line-break.ts`
- Result:
  - Confirmed the by-files validator now works for bare `src/...` paths when invoked from the workspace root

- Command:
  - `python skills/pretext/scripts/select_pretext_validation_from_git.py --repo pretext --staged`
- Result:
  - Returned the expected empty staged-change plan when no upstream files were staged

- Command:
  - `python skills/pretext/scripts/select_pretext_api.py --goal <every-supported-goal> --format json`
- Result:
  - All helper goals executed successfully after the trigger and disclosure refactor

### Metadata Validation

- Command:
  - `python C:/Users/MoYeR/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py G:/AgentProjects/skillsProjest/PretextSkill/skills/pretext ...`
- Result:
  - Regenerated `agents/openai.yaml` with build-oriented trigger wording and a valid `$pretext` default prompt

### Reliability Checks

- Check:
  - Compared `SKILL.md` reference links against the actual `skills/pretext/reference/` directory
- Result:
  - Fixed a real structural mismatch where the skill referenced recipe filenames that did not exist on disk

### Forward Testing

- Prompt:
  - Height-only React chat bubble estimation during resize without DOM measurement
- Result:
  - A fresh agent selected `prepare()` plus `layout()`, cached prepared state correctly, and highlighted width and typography synchronization risks

- Prompt:
  - Canvas text flow around an image with preserved line breaks, tabs, and Thai segmentation
- Result:
  - A fresh agent selected `prepareWithSegments()` plus `layoutNextLine()`, required `{ whiteSpace: 'pre-wrap' }`, and correctly used `setLocale('th')`

- Prompt:
  - Diagnose whether prepare-phase slowness comes from text analysis or measurement on a large batch
- Result:
  - A fresh agent selected `profilePrepare()`, kept prepare and layout inputs conceptually separated, and recommended `bun run benchmark-check` as the lightest follow-up validation

- Prompt:
  - A textarea-like editor loses tabs, hard breaks, and soft-hyphen behavior after a locale switch
- Result:
  - A fresh agent selected `prepareWithSegments()` plus `layoutWithLines()`, required `{ whiteSpace: 'pre-wrap' }`, and correctly enforced re-prepare on locale changes after `setLocale()`

- Prompt:
  - A product team wants the tightest multiline container width without materializing line strings on every width probe
- Result:
  - A fresh agent selected `prepareWithSegments()` plus `walkLineRanges()`, kept prepare/layout invalidation separate, and used the line-break validation plan correctly

- Prompt:
  - Modify upstream preprocessing for zero-width separators and punctuation glue, with the smallest defensible regression plan
- Result:
  - A fresh agent assigned ownership to `analysis.ts`, identified `line-break.ts` as the main downstream consumer, and chose `bun test` plus `bun run check` as the first validation step before broader sweeps

- Prompt:
  - A React chat app wants to cache prepared text and only recompute cheap layout on resize
- Result:
  - A fresh agent selected the height-only `prepare()` plus `layout()` pattern, cached prepared state by the correct invalidation tuple, and chose `bun run check` as the smallest validation step

- Prompt:
  - The package entrypoint and declaration output changed, and release confidence is needed for published consumers
- Result:
  - A fresh agent selected `package-workflows.md`, chose `bun run check`, `bun run build:package`, and `bun run package-smoke-test`, and validated the package contract correctly

- Prompt:
  - A reusable React hook should cache prepared text for height-only measurement across many chat bubbles
- Result:
  - A fresh agent selected the height-only React pattern, preserved the prepare/layout split in hook form, and used the expected invalidation tuple
