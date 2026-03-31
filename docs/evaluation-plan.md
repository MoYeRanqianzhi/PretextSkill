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
- variable-width line flow
- correctness-contract disputes
- prepare-phase profiling
- cache and locale lifecycle
- upstream internal modifications
- package release confidence
- diagnostics and caveat handling

This gives at least one realistic prompt for every current `select_pretext_api.py` goal:

- `height`
- `fixed-lines`
- `geometry`
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
- `package`
- `upstream`

The coverage mapping is checked in `skills/pretext/evals/coverage.json` and can be validated with `python skills/pretext/scripts/check_pretext_eval_coverage.py`.

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

The eval file now exists, but the full iterative benchmark and review loop has not yet been run in this repository state.
