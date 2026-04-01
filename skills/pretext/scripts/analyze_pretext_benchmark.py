#!/usr/bin/env python3
"""Analyze whether a benchmark meaningfully discriminates between with-skill and baseline runs."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvalObservation:
    eval_id: int
    eval_role: str | None
    with_skill_pass_rate: float
    baseline_pass_rate: float
    delta: float
    classification: str
    recommendation: str


def classify_delta(with_skill: float, baseline: float, delta_threshold: float, eval_role: str | None) -> tuple[str, str]:
    delta = with_skill - baseline
    if abs(delta) < delta_threshold and with_skill >= 0.95 and baseline >= 0.95:
        if eval_role == "smoke":
            return (
                "non_discriminating_success",
                "Expected for a smoke test: both configurations succeed, so treat this as capability confirmation rather than a benchmark gate.",
            )
        return (
            "non_discriminating_success",
            "Treat this eval as a smoke test. It currently does not distinguish the skill from baseline.",
        )
    if abs(delta) < delta_threshold and with_skill <= 0.05 and baseline <= 0.05:
        return (
            "non_discriminating_failure",
            "Both configurations fail. Tighten the route, prompt, or harness before treating this as a benchmark gate.",
        )
    if delta < -delta_threshold:
        return (
            "regression_candidate",
            "Baseline outperforms the skill here. Inspect the skill answer, not just the benchmark summary.",
        )
    if delta < delta_threshold:
        return (
            "weak_signal",
            "The eval distinguishes weakly at best. Consider whether the prompt is too easy or too broad.",
        )
    return (
        "discriminating_positive",
        "The eval meaningfully distinguishes the skill from baseline and is suitable as a benchmark gate."
        if eval_role != "smoke"
        else "The eval distinguishes positively, but its role is still marked as smoke; decide whether it should be promoted to a gate.",
    )


def load_eval_roles(coverage_path: Path | None) -> dict[int, str]:
    if coverage_path is None:
        return {}
    coverage = json.loads(coverage_path.read_text(encoding="utf-8"))
    mapping: dict[int, str] = {}
    for role, ids in coverage.get("eval_roles", {}).items():
        for eval_id in ids:
            mapping[eval_id] = role
    return mapping


def analyze_benchmark(benchmark: dict, delta_threshold: float, eval_roles: dict[int, str]) -> list[EvalObservation]:
    grouped: dict[int, dict[str, float]] = {}
    for run in benchmark.get("runs", []):
        eval_id = run["eval_id"]
        config = run["configuration"]
        pass_rate = float(run["result"]["pass_rate"])
        grouped.setdefault(eval_id, {})[config] = pass_rate

    observations: list[EvalObservation] = []
    for eval_id in sorted(grouped):
        with_skill = grouped[eval_id].get("with_skill")
        baseline = grouped[eval_id].get("without_skill")
        if with_skill is None or baseline is None:
            continue
        eval_role = eval_roles.get(eval_id)
        classification, recommendation = classify_delta(with_skill, baseline, delta_threshold, eval_role)
        observations.append(
            EvalObservation(
                eval_id=eval_id,
                eval_role=eval_role,
                with_skill_pass_rate=with_skill,
                baseline_pass_rate=baseline,
                delta=round(with_skill - baseline, 4),
                classification=classification,
                recommendation=recommendation,
            )
        )
    return observations


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze whether a benchmark discriminates meaningfully between skill and baseline.")
    parser.add_argument("--benchmark", required=True, help="Path to benchmark.json.")
    parser.add_argument("--coverage", default="skills/pretext/evals/coverage.json", help="Optional path to coverage.json for eval-role interpretation.")
    parser.add_argument("--delta-threshold", type=float, default=0.1, help="Minimum absolute pass-rate delta treated as meaningful.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args()

    benchmark_path = Path(args.benchmark).resolve()
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    coverage_path = Path(args.coverage).resolve() if args.coverage else None
    eval_roles = load_eval_roles(coverage_path) if coverage_path and coverage_path.exists() else {}
    observations = analyze_benchmark(benchmark, args.delta_threshold, eval_roles)

    if args.format == "json":
        payload = {
            "benchmark": str(benchmark_path),
            "coverage": str(coverage_path) if coverage_path and coverage_path.exists() else None,
            "delta_threshold": args.delta_threshold,
            "observations": [asdict(item) for item in observations],
        }
        print(json.dumps(payload, indent=2))
        return 0

    print(f"Benchmark: {benchmark_path}")
    if coverage_path and coverage_path.exists():
        print(f"Coverage: {coverage_path}")
    print(f"Delta threshold: {args.delta_threshold}")
    print("Observations:")
    if not observations:
        print("- (none)")
        return 0

    for item in observations:
        print(
            f"- eval {item.eval_id}: {item.classification} "
            f"(role={item.eval_role or 'untyped'}, with_skill={item.with_skill_pass_rate:.2f}, baseline={item.baseline_pass_rate:.2f}, delta={item.delta:+.2f})"
        )
        print(f"  recommendation: {item.recommendation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
