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

The remaining gap is:

- human review feedback has not yet been collected from `skills/pretext-workspace/iteration-1/review.html`
- human review feedback has not yet been collected from `skills/pretext-workspace/iteration-2/review.html`
- the full 25-eval suite has not yet been run through the same loop
