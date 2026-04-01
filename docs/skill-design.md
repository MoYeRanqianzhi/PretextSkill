# Pretext Skill Design Notes

## Objective

Create a Codex skill that helps another agent integrate, evaluate, and troubleshoot the `@chenglou/pretext` multiline text layout library.

## Reference-Derived Product Model

The reference repository describes Pretext as a browser-focused JavaScript and TypeScript library for multiline text measurement and layout without DOM reflow.

Core exported workflows from the README and source:

- `prepare()` plus `layout()` for fast repeated height calculation after one-time preparation
- `prepareWithSegments()` plus `layoutWithLines()` for full line materialization
- `walkLineRanges()` for width and cursor-only iteration without building line strings
- `layoutNextLine()` for cursor-based streamed line layout, including pagination and variable-width flow
- `clearCache()` and `setLocale()` for cache and locale management
- `profilePrepare()` as a diagnostic export rather than a default integration path

## Skill Scope

The skill should help with:

- choosing the correct Pretext API for a product requirement
- choosing the correct integration surface, not only the correct API shape
- integrating Pretext into UI code without breaking the prepare/layout split
- preserving correctness constraints such as matching `font`, `lineHeight`, and `whiteSpace`
- debugging common accuracy pitfalls like `system-ui` on macOS or repeated `prepare()` calls
- separating correctness-contract questions from integration, caveat, and validation questions
- planning validation using deterministic selectors instead of memory or intuition

## Design Principles

- Keep `SKILL.md` as a narrow Level-2 router
- Model decisions as `output shape + integration surface + invalidation tuple`
- Treat cursor continuation as a distinct output shape from both fixed batched lines and variable-width flow
- Keep correctness-contract work distinct from integration work so progressive disclosure can stay narrow
- Keep package-facing usage and upstream source modification paths clearly separated
- Treat validation taxonomy as shared data, not duplicated prose across scripts
- Prefer new references only when they reduce ambiguity or shrink the context needed for a common task

## Planned Skill Assets

- `SKILL.md`
  - first-principles routing only
- `reference/first-principles.md`
  - irreducible model and invalidation logic
- `reference/public-api.md`
  - normal package-facing API only
- `reference/adapter-patterns.md`
  - wrapper, hook, facade, and cache-boundary patterns grounded in verified downstream implementations
- `reference/socratic-review.md`
  - route-challenge questions, neighboring-route rejection, evidence ladders, and falsifiers
- `reference/internal-exports.md`
  - diagnostic helpers, advanced exported types, rich-path structural fields, and source-level internals
- `reference/internal-architecture.md`
  - source-level module boundaries, data flow, and change-impact validation
- `reference/whitespace-and-breaks.md`
  - whitespace modes, break policy, tabs, zero-width separators, and soft-hyphen behavior
- `reference/behavior-contracts.md`
  - cross-API semantic contracts and edge-case expectations derived from exported behavior and permanent tests
- `reference/script-and-browser-caveats.md`
  - script-sensitive segmentation, browser caveats, and research canaries
- `reference/document-reader-recipes.md`
  - PDF, EPUB, pagination, column continuation, and text-layer patterns
- `reference/react-dom-recipes.md`
  - React height caching, hook patterns, virtualization, editor-oriented patterns, and DOM guardrails
- `reference/custom-renderer-recipes.md`
  - Canvas/SVG/WebGL, shrink-wrap, variable-width flow, editorial flow, and frame-loop patterns
- `reference/package-workflows.md`
  - build, smoke-test, package-contract, and release-oriented package workflows
- `reference/upstream-tooling-surfaces.md`
  - narrow entry point for benchmark, accuracy, probe, corpus, Gatsby, reporting, demo-site, and package-adjacent harness selection
- `reference/integration-lifecycle.md`
  - prepare/layout lifecycle patterns for product code
- `reference/troubleshooting.md`
  - research-backed debugging guardrails and canaries
- `reference/validation-playbook.md`
  - area selection, git-diff routing, and validation surface inventory
- `scripts/select_pretext_api.py`
  - deterministic helper that maps `goal + surface` to the recommended API path, reference set, and first-principles questions, including correctness-contract routing
- `scripts/select_pretext_owner.py`
  - deterministic helper that maps an upstream issue category to the first owning source module and validation area
- `scripts/select_pretext_tooling_surface.py`
  - deterministic helper that maps an upstream harness or reporting concern to the narrowest tooling surface
- `scripts/select_pretext_route_plan.py`
  - deterministic helper that combines goal, surface, owner issue, tooling area, and validation area into one minimal route plan
- `scripts/select_pretext_examples.py`
  - deterministic helper that maps a goal, surface, or pattern to vetted external Pretext implementations with real code paths
- `scripts/select_pretext_socratic_review.py`
  - deterministic helper that challenges a tentative route before implementation using first-principles questions and route-rejection logic
- `scripts/run_pretext_review_iteration.py`
  - deterministic helper that executes one with-skill vs baseline review iteration into a skill-creator-style workspace
- `scripts/grade_pretext_review_iteration.py`
  - deterministic helper that grades the resulting iteration runs and writes `grading.json`
- `scripts/check_layout_api_sync.py`
  - deterministic maintenance check that compares documented API entries against `pretext/src/layout.ts`
- `scripts/check_pretext_eval_coverage.py`
  - deterministic maintenance check that ensures the formal eval suite still covers every supported goal and surface
- `scripts/pretext_validation_catalog.py`
  - shared validation taxonomy used by the validation-selector helpers
- `scripts/select_pretext_validation.py`
  - deterministic helper that maps a changed subsystem or surface to the smallest defensible validation plan
- `scripts/select_pretext_validation_by_files.py`
  - deterministic helper that infers validation scope from changed file paths
- `scripts/select_pretext_validation_from_git.py`
  - deterministic helper that infers validation scope directly from upstream git diff state
- `evals/evals.json`
  - formal skill-creator eval prompts covering every current selector goal and major surface
- `evals/coverage.json`
  - explicit mapping from eval prompts to goals, surfaces, tooling areas, owner issues, and validation areas

## Current Direction

- Keep package-facing usage and upstream source modification paths clearly separated
- Make API routing explicit across both output shape and integration surface
- Make `layoutNextLine()` routing explicit for fixed-width streamed pagination as well as true variable-width flow
- Make route selection falsifiable by design rather than relying on agent confidence or eloquence
- Make correctness-contract routing explicit instead of burying it inside generic diagnostics
- Make validation routing deterministic instead of relying on memory or intuition
- Keep the formal review loop trustworthy enough to drive iteration by repairing obviously contradictory grading polarity against its own evidence
- Cover package, browser, corpus, Gatsby, probe, and demo-site validation surfaces with one shared taxonomy
- Keep a formal eval suite aligned with the goal and surface taxonomy so regressions are observable
- Keep eval coverage aligned not only with goals and surfaces, but also with owner issues and validation areas
- Keep the upstream tooling layer separate from both package API routing and engine-ownership routing
- Add a top-level route-plan layer so multi-dimensional tasks do not force the agent to manually compose multiple selectors
- Make upstream module ownership explicit with deterministic routing before patching internals
- Keep the first real review loop reproducible in-repo instead of as an ad hoc shell sequence
- Prefer direct narrow recipe files once the implementation shape is known, without keeping an extra generic router file
- Expand from verified external implementations, not from inspiration-only typography demos
- Keep document-reader work separate from the broader custom-renderer bucket so reader-specific pagination patterns do not inflate unrelated renderer tasks

## Non-Goals

The skill still does not try to:

- reproduce the entire research archive from the reference repository
- bundle the whole reference repo into the skill
- expose every internal source file in `SKILL.md`
- pretend repo-internal source modules are equivalent to stable package-public imports

## Evidence Pointers

- `pretext/README.md`
- `pretext/src/layout.ts`
- `pretext/src/layout.test.ts`
- `pretext/src/analysis.ts`
- `pretext/DEVELOPMENT.md`
- `pretext/STATUS.md`
- `pretext/RESEARCH.md`
- `pretext/package.json`
- `docs/pretext-implementation-landscape.md`
