# Evaluation Plan

## Purpose

This document records the planned `skill-creator` evaluation loop for the `pretext` skill.

The first-principles target is not merely "can the skill mention the API names," but:

- can it choose the correct output shape
- can it choose the correct integration surface
- can it separate correctness-contract questions from integration and validation questions
- can it recommend the lightest defensible validation path

## Eval Coverage Model

The current eval suite in `skills/pretext/evals/evals.json` is designed to cover:

- height-only React or DOM work
- fixed-width custom rendering
- geometry-only shrink-wrap work
- streamed line continuation across pages or columns
- variable-width line flow
- correctness-contract disputes
- prepare-phase profiling
- cache and locale lifecycle
- upstream internal modifications
- package release confidence
- diagnostics and caveat handling
- upstream tooling-surface selection

This gives at least one realistic prompt for every current `select_pretext_api.py` goal:

- `height`
- `fixed-lines`
- `geometry`
- `streamed-lines`
- `variable-width`
- `shrinkwrap`
- `profile`
- `correctness`
- `cache-locale`
- `upstream-internals`
- `diagnostics`

It also covers the major integration surfaces:

- `react-dom`
- `custom-renderer`
- `document-reader`
- `package`
- `upstream`

And it now covers the maintained tooling areas:

- `accuracy-harness`
- `benchmark-harness`
- `probe-surface`
- `corpus-tooling`
- `gatsby-surface`
- `reporting-tooling`
- `demo-site`
- `package-workflow`

The coverage mapping is checked in `skills/pretext/evals/coverage.json` and can be validated with `python skills/pretext/scripts/check_pretext_eval_coverage.py`.

That coverage map now tracks:

- selector goals
- selector surfaces
- tooling areas
- owner issues
- validation areas
- reasoning layers
- eval roles such as `smoke` and `gate`

## Review Standard

Each eval should be reviewed for:

- correct goal selection
- correct surface selection
- correct API recommendation
- explicit invalidation tuple
- correct reference routing
- correct validation routing
- resistance to unnecessary internal patches

## Iteration Plan

When running the formal `skill-creator` loop:

1. Use `skills/pretext/evals/evals.json` as the initial eval set.
   Use `skills/pretext/evals/coverage.json` to verify that every supported goal and non-generic surface still has at least one eval.
2. Store run outputs under `skills/pretext-workspace/iteration-N/`.
3. Compare with-skill and baseline outputs before changing the skill again.
4. Expand the eval set only when a real failure mode appears repeatedly.

## Iteration 5: Trigger-Boundary And Stronger Reasoning Gates

After the progressive-disclosure refactor, iteration 5 adds a small targeted subset instead of broadening the whole suite immediately.

- eval IDs: `29, 30, 31, 32, 33`
- workspace: `skills/pretext-workspace/iteration-5`
- goal:
  - verify that the tightened frontmatter description still triggers on clearly Pretext-specific route-selection work
  - verify that generic frontend layout work is no longer swallowed as a Pretext routing task
  - replace weak reasoning-layer smoke prompts with stricter gate prompts for Socratic critique, decision contracts, and repo-local reasoning bundles

The new subset adds:

- `29` — positive trigger / route-plan sample
- `30` — negative trigger boundary sample
- `31` — stronger Socratic gate
- `32` — stronger decision-contract gate
- `33` — stronger reasoning-bundle gate

Benchmark summary for iteration 5:

- with skill: `90.0%`
- without skill: `91.0%`
- delta: `-0.01`

Discrimination analysis:

- `29` → `discriminating_positive`
- `30` → `regression_candidate`
- `31` → `non_discriminating_success`
- `32` → `discriminating_positive`
- `33` → `non_discriminating_success`

Interpretation:

- The tightened description did **not** break positive triggering for an explicitly Pretext-local route-selection prompt (`29`).
- The negative trigger sample (`30`) exposed a grading issue in the expectation wording: the with-skill answer correctly stayed generic, but the current expectation text uses a negated phrasing that the grader polarity repair can still misread. Treat this sample as a useful boundary test, but revise its wording before using it as a hard gate.
- The stricter decision-contract prompt (`32`) now behaves as a real gate and distinguishes the skill from baseline.
- The stricter Socratic (`31`) and reasoning-bundle (`33`) prompts still behave like smoke tests: they confirm capability but do not yet show meaningful benchmark separation from baseline.

Artifacts:

- `skills/pretext-workspace/iteration-5/benchmark.json`
- `skills/pretext-workspace/iteration-5/benchmark.md`
- `skills/pretext-workspace/iteration-5/review.html`

Next step:

- collect human review feedback from `skills/pretext-workspace/iteration-5/review.html`
- then revise eval `30` wording and decide whether `29` should be promoted from `smoke` to `gate`

## Iteration 6: Gate Hardening For Route-Plan And Reasoning Bundles

Iteration 6 focuses narrowly on replacing the still-smoke-like route-plan and reasoning-bundle prompts with harder gate variants.

- eval IDs: `34, 35, 36`
- workspace: `skills/pretext-workspace/iteration-6`
- goal:
  - harden the route-plan gate so it cannot drift into a loose multi-command answer
  - harden the Socratic gate so it must reject the default route and name a falsifier
  - harden the reasoning-bundle gate so it must use one integrated structure with exact route, explicit contract elements, and a tightly constrained command section

The new subset adds:

- `34` — harder route-plan gate requiring exactly one first command and full invalidation tuples
- `35` — harder Socratic gate requiring an explicit rejection, one falsifier, and one narrower surviving route
- `36` — harder reasoning-bundle gate requiring first-sentence route naming, separate wrong-route rejection, contract elements, and exactly three repo-local commands

Benchmark summary for iteration 6:

- with skill: `100.0%`
- without skill: `91.7%`
- delta: `+0.08`

Discrimination analysis:

- `34` → `non_discriminating_success`
- `35` → `discriminating_positive`
- `36` → `non_discriminating_success`

Interpretation:

- Gate hardening successfully converted the stronger Socratic prompt (`35`) into a meaningful benchmark gate.
- The harder route-plan prompt (`34`) and the harder reasoning-bundle prompt (`36`) still behave like smoke tests: they confirm capability, but baseline can still satisfy them reliably enough that they do not yet separate the skill from baseline.
- The next iteration, if needed, should focus only on making `34` and `36` internally coupled enough that baseline cannot satisfy them by matching format alone.

Artifacts:

- `skills/pretext-workspace/iteration-6/benchmark.json`
- `skills/pretext-workspace/iteration-6/benchmark.md`
- `skills/pretext-workspace/iteration-6/review.html`

## Iteration 7: Internal-Consistency Gates

Iteration 7 narrows further: instead of adding more formatting pressure, it tries to force internal consistency between route choice, invalidation tuples, and command roles.

- eval IDs: `37, 38`
- workspace: `skills/pretext-workspace/iteration-7`
- goal:
  - force route-plan answers to keep route, invalidation tuples, and the first command mutually consistent
  - force reasoning-bundle answers to keep command roles aligned with the route and the contract

The new subset adds:

- `37` — stricter route-plan consistency gate
- `38` — stricter reasoning-bundle consistency gate

Benchmark summary for iteration 7:

- with skill: `100.0%`
- without skill: `100.0%`
- delta: `+0.00`

Discrimination analysis:

- `37` → `non_discriminating_success`
- `38` → `non_discriminating_success`

Interpretation:

- Even after tightening internal-consistency requirements, baseline can still satisfy both prompts well enough that they remain smoke tests rather than useful benchmark gates.
- The results suggest that route-plan and reasoning-bundle prompts are still too naturally satisfiable by baseline when the desired answer shape is strongly specified.
- The most effective reasoning-layer gate remains the stronger Socratic prompt from iteration 6 (`35`).
- A future iteration should probably stop trying to force discrimination through format and instead require repo-grounded evidence or selector-specific failure modes that baseline is less likely to reconstruct on its own.

Artifacts:

- `skills/pretext-workspace/iteration-7/benchmark.json`
- `skills/pretext-workspace/iteration-7/benchmark.md`
- `skills/pretext-workspace/iteration-7/review.html`

## Current Gap

The first two real iterations have now been run on focused subsets:

- eval IDs: `1, 4, 5, 8, 9, 11, 24`
- workspace: `skills/pretext-workspace/iteration-1`
- benchmark summary:
  - with skill: `93.6%`
  - without skill: `67.9%`
  - delta: `+0.26`
- eval IDs: `2, 4, 11, 20, 24, 25`
- workspace: `skills/pretext-workspace/iteration-2`
- benchmark summary:
  - with skill: `100.0%`
  - without skill: `69.7%`
  - delta: `+0.30`
- eval IDs: `26, 27`
- workspace: `skills/pretext-workspace/iteration-3`
- benchmark summary:
  - with skill: `100.0%`
  - without skill: `100.0%`
  - delta: `+0.00`
- eval IDs: `28`
- workspace: `skills/pretext-workspace/iteration-4`
- benchmark summary:
  - with skill: `100.0%`
  - without skill: `100.0%`
  - delta: `+0.00`

The remaining gap is:

- human review feedback has not yet been collected from `skills/pretext-workspace/iteration-1/review.html`
- human review feedback has not yet been collected from `skills/pretext-workspace/iteration-2/review.html`
- human review feedback has not yet been collected from `skills/pretext-workspace/iteration-3/review.html`
- human review feedback has not yet been collected from `skills/pretext-workspace/iteration-4/review.html`
- the full 25-eval suite has not yet been run through the same loop

## Reasoning-Layer Note

Iteration 3 over evals `26` and `27` showed an important meta-result:

- with skill: `100.0%`
- without skill: `100.0%`
- delta: `+0.00`

This means the current reasoning-layer evals behave as smoke tests rather than discriminating benchmark gates.

That is still useful:

- they verify the skill can answer these prompts correctly
- they do not yet prove the skill adds measurable value over baseline on these prompts

Use `python skills/pretext/scripts/analyze_pretext_benchmark.py --benchmark <benchmark.json>` to classify whether an eval is:

- non-discriminating success
- non-discriminating failure
- weak signal
- regression candidate
- discriminating positive

Iteration 4 over eval `28` produced the same result:

- with skill: `100.0%`
- without skill: `100.0%`
- delta: `+0.00`

So the integrated reasoning-bundle eval is also currently a smoke test, not a discriminating gate.

For small iteration subsets, treat `benchmark.json` as the authoritative source when `benchmark.md` looks suspiciously empty or inconsistent.
