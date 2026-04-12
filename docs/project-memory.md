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
- Release tag `v0.3.0-restructured` created for the major restructuring milestone
- `skills/pretext/` now contains:
  - `SKILL.md` (rewritten: goal table routing, architectural guardrails, 7-file reference structure)
  - `agents/openai.yaml`
  - `evals/evals.json`
  - `evals/coverage.json`
  - **Reference files (7 total, consolidated from 19):**
    - `reference/public-api.md` — complete public API reference
    - `reference/internal-exports.md` — internal exports documentation
    - `reference/internal-architecture.md` — module ownership guide
    - `reference/adapter-patterns.md` — facade/hook/service boundary patterns
    - `reference/behavior-contracts.md` — merged from 4 files: semantics, whitespace, script caveats, troubleshooting
    - `reference/recipes.md` — merged from 4 files: React/DOM, Canvas/SVG, PDF/EPUB, integration lifecycle
    - `reference/validation-and-tooling.md` — merged from 3 files: validation playbook, tooling surfaces, package workflows
  - **Scripts (6 TypeScript files, converted from 20 Python):**
    - `scripts/select-pretext-validation-from-git.ts` — consolidated validation selector (git diff + file path + inline catalog)
    - `scripts/check-layout-api-sync.ts` — layout.ts exports vs documented API sync checker
    - `scripts/check-pretext-eval-coverage.ts` — eval coverage validator (simplified)
    - `scripts/run-pretext-review-iteration.ts` — eval iteration runner
    - `scripts/grade-pretext-review-iteration.ts` — eval grader
    - `scripts/analyze-pretext-benchmark.ts` — benchmark delta classifier
  - `_archive/` — archived 13 Python scripts and 3 process reference docs

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
- Record version support with two anchors:
  - published npm version
  - local upstream source commit
- Do not collapse package version and source commit into one unsupported "latest" claim
- Prefer verified external implementation code over inspiration-only demos when extending the skill
- Treat non-GitHub search as a discovery layer, not as implementation truth, until inspectable source code is found
- Down-rank low-signal visual demos unless they have both real Pretext code and enough source quality to justify reuse
- Treat cursor-continuation work as its own goal:
  - `layoutNextLine()` is not only for variable-width flow
  - it is also the correct path when fixed-width paragraphs must continue across pages, columns, or streamed slices
- Treat document readers as their own surface instead of overloading the generic custom-renderer bucket
- Provide deterministic access to vetted external implementations through `select_pretext_examples.py` rather than relying on remembered repo names
- Treat route choice as falsifiable, not merely selectable:
  - every serious route should survive challenge from neighboring goals and surfaces
  - the skill should explicitly ask what fact would make the current route wrong
- Make Socratic critique part of the route-planning layer rather than a separate optional habit
- Make the final route decision explicit as a contract:
  - state what must be true
  - state what would break the route
  - state the smallest validation path that justifies implementation
- Distinguish between:
  - smoke-test evals that confirm capability exists
  - discriminating evals that prove the skill adds measurable value over baseline
- Prefer one integrated reasoning bundle over three disconnected reasoning outputs when the task is high-ambiguity and high-stakes
- Treat eval design as a first-class engineering problem:
  - decide whether a prompt is intended as `smoke` or `gate`
  - design misleading neighboring routes on purpose for gate prompts
  - use repo-local discriminators instead of generic explanation prompts
- Keep the review loop traceable and self-consistent:
  - persist raw grader output
  - repair obviously contradictory pass/fail polarity when the evidence text is clearly affirmative or clearly negative

## Version Support Snapshot

- Checked on: `2026-04-01`
- Local upstream branch: `main`
- Local upstream commit: `a8d1e35d3973a0f63c007f7645f4a8918135a57b`
- Local upstream HEAD subject: `Keep correctness browser automation in background`
- Local `pretext/package.json` version: `0.0.3`
- Latest published npm version: `0.0.3`
- Local `origin/HEAD` currently matches the checked-out local upstream clone
- Durable procedure document: `docs/version-support.md`

## Audit & Fix Record (2026-04-12)

10-agent parallel audit completed. All findings applied in commit `98898bd`:

| File | Key Fixes |
|------|-----------|
| `recipes.md` | Fixed 2 broken links (P0), removed misleading locale param from React Hook |
| `public-api.md` | Added explicit `prepared` param types for all 4 layout functions |
| `internal-exports.md` | Coverage ~22% → ~90%: +8 SegmentBreakKind, +14 measurement.ts, +15 analysis.ts, +7 line-break.ts exports, +3 rich-path fields |
| `internal-architecture.md` | Added 3 cross-module dependencies, documented measureAnalysis() CJK logic, fixed dead Python ref |
| `adapter-patterns.md` | Added 3 anti-patterns (system-ui, empty text, font shorthand), cache capacity guidance, fixed switchLocale type |
| `validation-and-tooling.md` | Added accuracy-snapshot series, corpus-status:refresh, 6 Safari variants — all 35 package.json scripts covered |

## Known Issues

- Two real `skill-creator` review iterations have now been run, but still on focused subsets rather than the full 25-eval suite
- Human review feedback has not yet been collected from the generated static review viewer
- The git-diff validator assumes the local checkout still follows the current `./pretext/` sibling layout when `--repo` is omitted
- Future demand may justify even narrower renderer references such as dedicated `SVG` or `WebGL` recipes
- The external example catalog uses a star snapshot from `2026-04-01` and will need manual refresh when the external landscape changes materially
- For very small iteration subsets, `benchmark.json` is the source of truth; external `benchmark.md` summaries may need manual sanity-checking

## Next Tasks

- Run the formal eval prompts through the full `skill-creator` review loop with the new TS scripts
- Keep `docs/version-support.md` and this memory snapshot updated whenever upstream package or source anchors move
- Collect human review feedback from existing iteration review.html files
- Decide whether to clean up `_archive/` directory or keep for reference

## Demo Record (2026-04-12)

- `demos/kitten-dynamic-layout.html` — 765-line self-contained HTML demo
  - Built by agent constrained to ONLY pretext skill guidance (isolated test)
  - Uses `prepareWithSegments()` + `layoutWithLines()` (fixed-lines goal)
  - 5 kitten cards: English, Chinese, Japanese, mixed-language, pre-wrap tab-formatted
  - Interactive controls: width slider (200–800px), font size (12–32px), line height (16–52px), card selector, whiteSpace toggle
  - Performance dashboard: prepare count, layout count, timing in ms, insight indicator
  - **Verified behavior**: width-only changes do NOT trigger re-prepare (prepare count stays at 5, layout count rises to 20); font size change DOES trigger re-prepare (prepare count jumps to 15)
  - Zero console errors
  - Spec at `docs/demo-spec.md`

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
- `python -m json.tool skills/pretext/evals/evals.json`
  - Result: the formal eval suite JSON parses successfully and covers all current selector goals
- `python skills/pretext/scripts/check_pretext_eval_coverage.py`
  - Result: verifies that every supported goal, non-generic surface, maintained tooling area, owner issue, and validation area still has at least one mapped eval
- `python skills/pretext/scripts/select_pretext_owner.py --issue segmentation --format json`
  - Result: routes preprocessing and glue issues to `analysis.ts`, with the expected references and validation area
- `python skills/pretext/scripts/select_pretext_tooling_surface.py --area probe-surface --format json`
  - Result: routes one-paragraph mismatch work to the probe surface with the expected files, references, and validation area
- `python skills/pretext/scripts/select_pretext_route_plan.py --goal variable-width --surface custom-renderer --issue streamed-lines --tooling-area probe-surface --preserve-whitespace --locale-sensitive --format json`
  - Result: returns a single combined route plan with the expected minimal reference set, helper commands, and derived validation plan
- `npm view @chenglou/pretext version time --json`
  - Result: latest published npm version is `0.0.3`
- `git -C pretext rev-parse HEAD`
  - Result: local upstream source anchor is `a8d1e35d3973a0f63c007f7645f4a8918135a57b`
- `python skills/pretext/scripts/run_pretext_review_iteration.py --workspace skills/pretext-workspace/iteration-1`
  - Result: executed the first real review iteration over eval IDs `1, 4, 5, 8, 9, 11, 24`, producing with-skill and without-skill runs
- `python skills/pretext/scripts/grade_pretext_review_iteration.py --workspace skills/pretext-workspace/iteration-1`
  - Result: generated `grading.json` for each run in the first real review iteration
- `python <skill-creator>/scripts/aggregate_benchmark.py skills/pretext-workspace/iteration-1 --skill-name pretext --skill-path skills/pretext`
  - Result: benchmark summary for iteration 1 is `93.6%` pass rate with skill vs `67.9%` without skill, delta `+0.26`
- `python -X utf8 <skill-creator>/eval-viewer/generate_review.py skills/pretext-workspace/iteration-1 --skill-name pretext --benchmark skills/pretext-workspace/iteration-1/benchmark.json --static skills/pretext-workspace/iteration-1/review.html`
  - Result: generated a static review viewer at `skills/pretext-workspace/iteration-1/review.html`
- `gh search code '"@chenglou/pretext"' --limit 100 --json repository,path,url`
  - Result: produced a broad map of real downstream repositories importing the published package
- `gh repo view <owner>/<repo> --json nameWithOwner,description,stargazerCount,url,updatedAt,licenseInfo`
  - Result: captured star-count and license snapshots for vetted external references on `2026-04-01`
- External implementation inspection
  - Result: `docs/pretext-implementation-landscape.md` now records vetted direct users, wrappers, forks, and downgraded low-signal references
- `python skills/pretext/scripts/select_pretext_api.py --goal streamed-lines --surface document-reader --format json`
  - Result: returns the new cursor-continuation routing, document-reader references, and the correct prepare/layout invalidation tuple
- `python skills/pretext/scripts/select_pretext_examples.py --goal streamed-lines --surface document-reader --format json`
  - Result: returns the vetted `zsh-eng/epub-reader-demo` precedent for streamed reader pagination
- `python skills/pretext/scripts/select_pretext_route_plan.py --goal streamed-lines --surface document-reader --format json`
  - Result: the unified route-plan layer now accepts the new goal and surface without widening the reference set unnecessarily
- `python skills/pretext/scripts/select_pretext_socratic_review.py --goal streamed-lines --surface document-reader --issue streamed-lines --tooling-area probe-surface --format json`
  - Result: returns explicit challenge questions, neighboring routes to reject, falsifiers, and follow-up selector commands for the tentative route
- `python skills/pretext/scripts/select_pretext_route_plan.py --goal streamed-lines --surface document-reader --issue streamed-lines --tooling-area probe-surface --format json`
  - Result: the unified route plan now includes `socratic-review.md` plus critique and external-example helper commands automatically
- `python skills/pretext/scripts/select_pretext_decision_contract.py --goal streamed-lines --surface document-reader --issue streamed-lines --tooling-area probe-surface --format json`
  - Result: returns route summary, required statements, assumptions, proof obligations, route breakers, and the minimal validation chain for the streamed reader path
- `python skills/pretext/scripts/select_pretext_route_plan.py --goal streamed-lines --surface document-reader --issue streamed-lines --tooling-area probe-surface --format json`
  - Result: the unified route plan now includes decision-contract follow-up commands as part of the default helper chain
- `python skills/pretext/scripts/run_pretext_review_iteration.py --workspace skills/pretext-workspace/iteration-2 --eval-id 2 --eval-id 4 --eval-id 11 --eval-id 20 --eval-id 24 --eval-id 25`
  - Result: produced the focused second iteration workspace for fixed-lines, variable-width, probe-surface, streamed-line ownership, unified route-plan, and document-reader coverage
- `python skills/pretext/scripts/grade_pretext_review_iteration.py --workspace skills/pretext-workspace/iteration-2`
  - Result: produced grading outputs for iteration 2, revealing a grader polarity-consistency problem
- Iteration-2 grading repair pass
  - Result: repaired contradictory expectation booleans using evidence-polarity normalization and regenerated benchmark artifacts
- `python <skill-creator>/scripts/aggregate_benchmark.py skills/pretext-workspace/iteration-2 --skill-name pretext --skill-path skills/pretext`
  - Result: focused iteration 2 benchmark summary is `100.0%` pass rate with skill vs `69.7%` without skill, delta `+0.30`
- `python -X utf8 <skill-creator>/eval-viewer/generate_review.py skills/pretext-workspace/iteration-2 --skill-name pretext --benchmark skills/pretext-workspace/iteration-2/benchmark.json --previous-workspace skills/pretext-workspace/iteration-1 --static skills/pretext-workspace/iteration-2/review.html`
  - Result: generated a second static review viewer at `skills/pretext-workspace/iteration-2/review.html`
- `python skills/pretext/scripts/run_pretext_review_iteration.py --workspace skills/pretext-workspace/iteration-3 --eval-id 26 --eval-id 27`
  - Result: produced the focused third iteration workspace for Socratic critique and decision-contract evaluation
- `python <skill-creator>/scripts/aggregate_benchmark.py skills/pretext-workspace/iteration-3 --skill-name pretext --skill-path skills/pretext`
  - Result: focused iteration 3 benchmark summary is `100.0%` pass rate with skill vs `100.0%` without skill, delta `+0.00`
- `python skills/pretext/scripts/analyze_pretext_benchmark.py --benchmark skills/pretext-workspace/iteration-3/benchmark.json --format json`
  - Result: classified evals `26` and `27` as `non_discriminating_success`
- `python skills/pretext/scripts/select_pretext_reasoning_bundle.py --goal streamed-lines --surface document-reader --issue streamed-lines --tooling-area probe-surface --format json`
  - Result: returns one integrated reasoning bundle containing route plan, Socratic critique, decision contract, and ordered next steps
- `python skills/pretext/scripts/run_pretext_review_iteration.py --workspace skills/pretext-workspace/iteration-4 --eval-id 28`
  - Result: produced the focused fourth iteration workspace for the integrated reasoning-bundle prompt
- `python <skill-creator>/scripts/aggregate_benchmark.py skills/pretext-workspace/iteration-4 --skill-name pretext --skill-path skills/pretext`
  - Result: iteration 4 `benchmark.json` shows with skill `100.0%` and without skill `100.0%`; use the JSON as the authoritative source for this single-eval run
- `python skills/pretext/scripts/analyze_pretext_benchmark.py --benchmark skills/pretext-workspace/iteration-4/benchmark.json --format json`
  - Result: classified eval `28` as `non_discriminating_success`
- `python skills/pretext/scripts/select_pretext_validation.py --area reporting-tooling --format json`
  - Result: returns the expected reporting-tooling commands and follow-up checks
- `python skills/pretext/scripts/select_pretext_validation_by_files.py --path pretext/scripts/report-server.ts --path pretext/pages/report-utils.ts`
  - Result: matches the new `reporting-tooling` area and returns the expected merged validation plan
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

- `python skills/pretext/scripts/run_pretext_review_iteration.py --workspace skills/pretext-workspace/iteration-5 --eval-id 29 --eval-id 30 --eval-id 31 --eval-id 32 --eval-id 33`
  - Result: produced the focused fifth iteration workspace for trigger-boundary validation and stronger reasoning-layer gate prompts
- `python skills/pretext/scripts/grade_pretext_review_iteration.py --workspace skills/pretext-workspace/iteration-5 --force`
  - Result: grading succeeded after fixing subprocess environment propagation for `CLAUDE_CODE_GIT_BASH_PATH` on Windows
- `python <skill-creator>/scripts/aggregate_benchmark.py skills/pretext-workspace/iteration-5 --skill-name pretext --skill-path skills/pretext`
  - Result: iteration 5 benchmark summary is `90.0%` with skill vs `91.0%` without skill, delta `-0.01`
- `python skills/pretext/scripts/analyze_pretext_benchmark.py --benchmark skills/pretext-workspace/iteration-5/benchmark.json --format json`
  - Result: classified eval `29` and `32` as `discriminating_positive`, eval `31` and `33` as `non_discriminating_success`, and eval `30` as `regression_candidate`
- `python -X utf8 <skill-creator>/eval-viewer/generate_review.py skills/pretext-workspace/iteration-5 --skill-name pretext --benchmark skills/pretext-workspace/iteration-5/benchmark.json --previous-workspace skills/pretext-workspace/iteration-4 --static skills/pretext-workspace/iteration-5/review.html`
  - Result: generated a fifth static review viewer at `skills/pretext-workspace/iteration-5/review.html`
- Iteration-5 interpretation
  - Result: tightened `SKILL.md` description still preserves positive Pretext-specific triggering on eval `29`, strengthens decision-contract discrimination on eval `32`, but eval `31` and `33` remain smoke-like and eval `30` needs wording repair because its negated expectation phrasing confuses grader polarity repair
- Updated `skills/pretext/scripts/run_pretext_review_iteration.py` and `skills/pretext/scripts/grade_pretext_review_iteration.py`
  - Result: both scripts now pass their filtered environment into `subprocess.run(...)`, fixing Windows evaluation runs that depend on `CLAUDE_CODE_GIT_BASH_PATH`
- Updated eval `30` wording in `skills/pretext/evals/evals.json`
  - Result: reframed the negative boundary expectation in positive terms so future grading can verify generic-layout handling without negation-induced polarity flips

- `python skills/pretext/scripts/run_pretext_review_iteration.py --workspace skills/pretext-workspace/iteration-6 --eval-id 34 --eval-id 35 --eval-id 36`
  - Result: produced the focused sixth iteration workspace for harder route-plan, Socratic, and reasoning-bundle gate prompts
- `python skills/pretext/scripts/grade_pretext_review_iteration.py --workspace skills/pretext-workspace/iteration-6`
  - Result: grading completed successfully for all harder-gate runs
- `python <skill-creator>/scripts/aggregate_benchmark.py skills/pretext-workspace/iteration-6 --skill-name pretext --skill-path skills/pretext`
  - Result: iteration 6 benchmark summary is `100.0%` with skill vs `91.7%` without skill, delta `+0.08`
- `python skills/pretext/scripts/analyze_pretext_benchmark.py --benchmark skills/pretext-workspace/iteration-6/benchmark.json --format json`
  - Result: classified eval `35` as `discriminating_positive`, while evals `34` and `36` remain `non_discriminating_success`
- `python -X utf8 <skill-creator>/eval-viewer/generate_review.py skills/pretext-workspace/iteration-6 --skill-name pretext --benchmark skills/pretext-workspace/iteration-6/benchmark.json --previous-workspace skills/pretext-workspace/iteration-5 --static skills/pretext-workspace/iteration-6/review.html`
  - Result: generated a sixth static review viewer at `skills/pretext-workspace/iteration-6/review.html`
- Iteration-6 interpretation
  - Result: stronger gate wording successfully hardened the Socratic path into a real gate, but route-plan and reasoning-bundle remain smoke-like because baseline can still satisfy their stricter formatting constraints
- Updated `skills/pretext/evals/evals.json` and `skills/pretext/evals/coverage.json` for iteration 6
  - Result: promoted route-plan coverage into `gate`, removed eval `29` from `smoke`, and added harder gate prompts `34`, `35`, and `36`

- `python skills/pretext/scripts/run_pretext_review_iteration.py --workspace skills/pretext-workspace/iteration-7 --eval-id 37 --eval-id 38`
  - Result: produced the focused seventh iteration workspace for route-plan and reasoning-bundle internal-consistency gates
- `python skills/pretext/scripts/grade_pretext_review_iteration.py --workspace skills/pretext-workspace/iteration-7`
  - Result: grading completed successfully for both consistency-gate runs
- `python <skill-creator>/scripts/aggregate_benchmark.py skills/pretext-workspace/iteration-7 --skill-name pretext --skill-path skills/pretext`
  - Result: iteration 7 benchmark summary is `100.0%` with skill vs `100.0%` without skill, delta `+0.00`
- `python skills/pretext/scripts/analyze_pretext_benchmark.py --benchmark skills/pretext-workspace/iteration-7/benchmark.json --format json`
  - Result: classified both eval `37` and eval `38` as `non_discriminating_success`
- `python -X utf8 <skill-creator>/eval-viewer/generate_review.py skills/pretext-workspace/iteration-7 --skill-name pretext --benchmark skills/pretext-workspace/iteration-7/benchmark.json --previous-workspace skills/pretext-workspace/iteration-6 --static skills/pretext-workspace/iteration-7/review.html`
  - Result: generated a seventh static review viewer at `skills/pretext-workspace/iteration-7/review.html`
- Iteration-7 interpretation
  - Result: stronger internal-consistency constraints still did not make route-plan or reasoning-bundle prompts discriminating; baseline continues to satisfy these structures reliably enough that they should be treated as smoke tests
- Updated `skills/pretext/evals/evals.json` and `skills/pretext/evals/coverage.json` for iteration 7
  - Result: added stricter consistency gates `37` and `38` that tie command choice to route and contract role alignment

## Working Rules

- Document important findings before relying on memory
- Prefer verifiable claims with file-backed evidence
- Do not guess about API behavior, CLI behavior, or repo state when a local check is possible
