# Eval Design

Use this file when you are improving the skill's evaluation system rather than the skill's user-facing routing.

## First Principle

An eval is only useful if you know what it is supposed to prove.

Do not ask one eval to prove all of these at once:

- the capability exists
- the capability is repo-local
- the capability is more reliable than baseline
- the capability is more efficient than baseline

Separate those goals explicitly.

## Eval Roles

### Smoke

A smoke eval proves:

- the skill can produce the intended reasoning artifact
- the local selectors and references are wired correctly
- the capability still exists after refactors

A smoke eval does **not** need to distinguish from baseline.

### Gate

A gate eval proves:

- the skill adds measurable value over baseline
- the prompt contains a plausible wrong neighboring route
- the skill's repo-local taxonomy helps it recover the correct route

If a gate eval does not produce meaningful delta, it is a weak gate or just a smoke test in disguise.

## How To Design A Gate

### Requirement 1: Add a plausible wrong route

Examples:

- make `streamed-lines` look superficially like `variable-width`
- make `document-reader` look superficially like `custom-renderer`
- make a package-contract issue look superficially like an upstream source issue

### Requirement 2: Make the discriminator repo-specific

The correct answer should depend on local artifacts such as:

- local selector names
- local taxonomy names
- local validation areas
- local reasoning bundle flow

If the answer can be given cleanly from general LLM knowledge alone, the prompt is probably smoke-level.

### Requirement 3: Grade the rejection, not only the final route

A strong gate should check:

- which neighboring routes were rejected
- why they were wrong
- what fact would have made them correct

### Requirement 4: Ask for the smallest local command chain

This raises the bar above generic explanation and makes the prompt depend on repo-local process.

## Anti-Patterns

- prompts with no plausible wrong route
- prompts that only ask for generic principles
- prompts that reward eloquence but not local grounding
- prompts that can pass without naming any repo-local script, taxonomy, or validation area
- prompts that check only the final route but not the route breakers

## Reasoning-Layer Guidance

### `route-plan`

Best when:

- the task mixes goal, surface, issue, tooling, and validation

Gate design focus:

- make at least two of those dimensions easy to confuse

### `socratic-review`

Best when:

- the main failure mode is premature confidence

Gate design focus:

- make the wrong route attractive
- require explicit rejection logic and falsifiers

### `decision-contract`

Best when:

- the failure mode is vague commitment

Gate design focus:

- require explicit assumptions, proof obligations, route breakers, and minimal validation chain

### `reasoning-bundle`

Best when:

- the failure mode is coordination drift across multiple reasoning layers

Gate design focus:

- require one integrated answer
- require repo-local bundle commands
- require neighboring-route rejection plus final contract

## Benchmark Interpretation

Use `python scripts/analyze_pretext_benchmark.py --benchmark <benchmark.json>` after any focused iteration.

Interpretation:

- `non_discriminating_success` with role `smoke` is acceptable
- `non_discriminating_success` with role `gate` means the prompt is underpowered
- `discriminating_positive` with role `gate` is the target state

## Final Question

Before adding a new eval, ask:

If baseline had no access to this skill, what specific wrong route would it still find tempting here?
