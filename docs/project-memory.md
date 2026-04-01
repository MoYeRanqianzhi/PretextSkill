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
- Release tag `v0.6.5` created for the formal eval suite and deeper advanced-type coverage
- Release tag `v0.6.6` created for upstream ownership routing and eval-coverage maintenance
- Release tag `v0.6.7` created for upstream tooling-surface routing and expanded harness eval coverage
- Release tag `v0.6.8` created for owner-issue and validation-area eval coverage expansion
- Release tag `v0.6.9` created for unified route-plan routing across selectors
- Release tag `v0.7.0` created for explicit version-support documentation and the first real skill-creator review loop
- Release tag `v0.7.1` created for vetted external implementation-landscape research
- Release tag `v0.8.0` created for streamed-line routing, document-reader disclosure, and external example selection
- Release tag `v0.8.1` created for grading-consistency repair and the focused second real review iteration
- Release tag `v0.8.2` created for Socratic route critique and route-plan self-challenge integration
- Release tag `v0.8.3` created for decision-contract commitments and three-stage route planning
- External implementation research now recorded in `docs/pretext-implementation-landscape.md`
- `skills/pretext/` now contains:
  - `SKILL.md`
  - `agents/openai.yaml`
  - `evals/evals.json`
  - `evals/coverage.json`
  - `reference/first-principles.md`
  - `reference/public-api.md`
  - `reference/adapter-patterns.md`
  - `reference/socratic-review.md`
  - `reference/decision-contract.md`
  - `reference/internal-exports.md`
  - `reference/internal-architecture.md`
  - `reference/whitespace-and-breaks.md`
  - `reference/behavior-contracts.md`
  - `reference/script-and-browser-caveats.md`
  - `reference/document-reader-recipes.md`
  - `reference/react-dom-recipes.md`
  - `reference/custom-renderer-recipes.md`
  - `reference/package-workflows.md`
  - `reference/upstream-tooling-surfaces.md`
  - `reference/integration-lifecycle.md`
  - `reference/troubleshooting.md`
  - `reference/validation-playbook.md`
  - `scripts/select_pretext_api.py`
  - `scripts/select_pretext_owner.py`
  - `scripts/select_pretext_tooling_surface.py`
  - `scripts/select_pretext_route_plan.py`
  - `scripts/select_pretext_examples.py`
  - `scripts/select_pretext_socratic_review.py`
  - `scripts/select_pretext_decision_contract.py`
  - `scripts/run_pretext_review_iteration.py`
  - `scripts/grade_pretext_review_iteration.py`
  - `scripts/check_layout_api_sync.py`
  - `scripts/check_pretext_eval_coverage.py`
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

## Known Issues

- Two real `skill-creator` review iterations have now been run, but still on focused subsets rather than the full 25-eval suite
- Human review feedback has not yet been collected from the generated static review viewer
- The git-diff validator assumes the local checkout still follows the current `./pretext/` sibling layout when `--repo` is omitted
- Future demand may justify even narrower renderer references such as dedicated `SVG` or `WebGL` recipes
- The external example catalog uses a star snapshot from `2026-04-01` and will need manual refresh when the external landscape changes materially

## Next Tasks

- Run the new formal eval prompts through the full `skill-creator` review loop
- Keep `docs/version-support.md` and this memory snapshot updated whenever upstream package or source anchors move
- Collect human review feedback from `skills/pretext-workspace/iteration-1/review.html`
- Collect human review feedback from `skills/pretext-workspace/iteration-2/review.html`
- Decide whether the next iteration should be the first full 25-eval run or a human-feedback-driven patch round
- Decide whether the Socratic critique layer should later get its own formal eval prompt instead of living only in deterministic script validation
- Decide whether the decision-contract layer should get its own formal eval prompt for assumption quality and route-breaker quality
- Decide whether the external example selector should later grow direct file-owner hints or freshness checks beyond the current star snapshot
- Use the ownership router on the next upstream-internals pass and refine issue categories only if repeated ambiguity remains
- Observe whether the tooling-surface router reduces unnecessary loading of the full validation playbook for harness-only tasks
- Observe whether the unified route-plan router reduces manual composition across selectors for multi-dimensional tasks
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

## Working Rules

- Document important findings before relying on memory
- Prefer verifiable claims with file-backed evidence
- Do not guess about API behavior, CLI behavior, or repo state when a local check is possible
