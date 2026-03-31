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

### Metadata Validation

- Command:
  - `python C:/Users/MoYeR/.codex/skills/.system/skill-creator/scripts/generate_openai_yaml.py G:/AgentProjects/skillsProjest/PretextSkill/skills/pretext ...`
- Result:
  - Regenerated `agents/openai.yaml` with a valid `$pretext` default prompt

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
