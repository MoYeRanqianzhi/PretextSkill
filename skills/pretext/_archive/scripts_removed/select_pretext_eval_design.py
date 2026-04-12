#!/usr/bin/env python3
"""Recommend how to design a Pretext eval as smoke or gate."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from pretext_eval_roles import SUPPORTED_EVAL_ROLES
from pretext_reasoning_layers import SUPPORTED_REASONING_LAYERS
from select_pretext_api import SUPPORTED_GOALS, SUPPORTED_SURFACES
from select_pretext_socratic_review import build_review


@dataclass(frozen=True)
class EvalDesignPlan:
    role: str
    goal: str
    surface: str
    reasoning_layer: str
    design_objective: str
    ambiguity_hooks: list[str]
    required_local_signals: list[str]
    benchmark_success_condition: str
    anti_patterns: list[str]
    grading_focus: list[str]
    notes: list[str]


LAYER_SIGNALS = {
    "route-plan": [
        "`select_pretext_route_plan.py`",
        "goal + surface + issue + tooling + validation composition",
    ],
    "socratic-review": [
        "`select_pretext_socratic_review.py`",
        "neighbor-route rejection",
        "falsifiers",
    ],
    "decision-contract": [
        "`select_pretext_decision_contract.py`",
        "proof obligations",
        "route breakers",
        "minimal validation chain",
    ],
    "reasoning-bundle": [
        "`select_pretext_reasoning_bundle.py`",
        "integrated route + critique + contract output",
    ],
}


def default_ambiguity_hooks(goal: str, surface: str) -> list[str]:
    hooks: list[str] = []
    if goal == "streamed-lines":
        hooks.append("Describe fixed-width continuation so `variable-width` still looks superficially tempting.")
    if goal == "variable-width":
        hooks.append("Describe continuation-like behavior so `streamed-lines` still looks superficially tempting.")
    if surface == "document-reader":
        hooks.append("Include renderer language so `custom-renderer` still looks plausible.")
    if surface == "custom-renderer":
        hooks.append("Include reader-like continuation semantics so `document-reader` still looks plausible.")
    if goal == "correctness":
        hooks.append("Include symptoms that tempt premature upstream patching before exported repro.")
    if goal == "upstream-internals":
        hooks.append("Make the package surface look plausible so owner selection must be justified.")
    return hooks


def build_eval_design(role: str, goal: str, surface: str, reasoning_layer: str) -> EvalDesignPlan:
    review = build_review(goal=goal, surface=surface, issue=None, tooling_area=None)
    ambiguity_hooks = default_ambiguity_hooks(goal, surface)
    required_local_signals = list(LAYER_SIGNALS[reasoning_layer])
    grading_focus = [
        "Correct route",
        "Correct rejection of neighboring wrong routes",
        "Repo-local commands or taxonomy references",
    ]
    anti_patterns = [
        "Prompt solvable from generic knowledge without repo-local selectors.",
        "No plausible wrong neighboring route.",
        "Rewarding general explanation without local command or taxonomy use.",
    ]
    notes: list[str] = []

    if role == "smoke":
        design_objective = (
            "Confirm that the reasoning layer still works and emits the intended local artifact after refactors."
        )
        benchmark_success_condition = (
            "Both configurations may succeed; this eval exists to confirm capability, not to demand positive delta."
        )
        grading_focus.append("Artifact existence and local grounding")
        notes.append("Smoke evals should be easy enough to prove capability exists.")
    else:
        design_objective = (
            "Create a high-ambiguity prompt where a strong baseline is tempted toward a plausible wrong route but the skill's local taxonomy should recover the right one."
        )
        benchmark_success_condition = (
            "With skill should materially outperform baseline and `analyze_pretext_benchmark.py` should classify the eval as discriminating positive."
        )
        grading_focus.append("Route-breaker quality and falsifier quality")
        anti_patterns.append("Prompt with no misleading signal or no local discriminator.")
        notes.extend(review.routes_to_rule_out)
        notes.append("A gate eval that ends as `non_discriminating_success` is underpowered and should be redesigned.")

    return EvalDesignPlan(
        role=role,
        goal=goal,
        surface=surface,
        reasoning_layer=reasoning_layer,
        design_objective=design_objective,
        ambiguity_hooks=ambiguity_hooks,
        required_local_signals=required_local_signals,
        benchmark_success_condition=benchmark_success_condition,
        anti_patterns=anti_patterns,
        grading_focus=grading_focus,
        notes=notes,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend how to design a Pretext eval as smoke or gate.")
    parser.add_argument("--role", required=True, choices=SUPPORTED_EVAL_ROLES, help="Eval role.")
    parser.add_argument("--goal", required=True, choices=SUPPORTED_GOALS, help="Primary goal.")
    parser.add_argument("--surface", required=True, choices=[s for s in SUPPORTED_SURFACES if s != "generic"], help="Primary surface.")
    parser.add_argument("--reasoning-layer", required=True, choices=SUPPORTED_REASONING_LAYERS, help="Primary reasoning layer.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args()

    plan = build_eval_design(
        role=args.role,
        goal=args.goal,
        surface=args.surface,
        reasoning_layer=args.reasoning_layer,
    )

    if args.format == "json":
        print(json.dumps(asdict(plan), indent=2))
        return 0

    print(f"Role: {plan.role}")
    print(f"Goal: {plan.goal}")
    print(f"Surface: {plan.surface}")
    print(f"Reasoning layer: {plan.reasoning_layer}")
    print(f"Design objective: {plan.design_objective}")
    print("Ambiguity hooks:")
    for item in plan.ambiguity_hooks:
        print(f"- {item}")
    print("Required local signals:")
    for item in plan.required_local_signals:
        print(f"- {item}")
    print(f"Benchmark success condition: {plan.benchmark_success_condition}")
    print("Anti-patterns:")
    for item in plan.anti_patterns:
        print(f"- {item}")
    print("Grading focus:")
    for item in plan.grading_focus:
        print(f"- {item}")
    print("Notes:")
    for item in plan.notes:
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
