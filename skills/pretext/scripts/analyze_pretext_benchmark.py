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
    with_skill_pass_rate: float
    baseline_pass_rate: float
    delta: float
    classification: str
    recommendation: str


def classify_delta(with_skill: float, baseline: float, delta_threshold: float) -> tuple[str, str]:
    delta = with_skill - baseline
    if abs(delta) < delta_threshold and with_skill >= 0.95 and baseline >= 0.95:
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
        "The eval meaningfully distinguishes the skill from baseline and is suitable as a benchmark gate.",
    )


def analyze_benchmark(benchmark: dict, delta_threshold: float) -> list[EvalObservation]:
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
        classification, recommendation = classify_delta(with_skill, baseline, delta_threshold)
        observations.append(
            EvalObservation(
                eval_id=eval_id,
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
    parser.add_argument("--delta-threshold", type=float, default=0.1, help="Minimum absolute pass-rate delta treated as meaningful.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args()

    benchmark_path = Path(args.benchmark).resolve()
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    observations = analyze_benchmark(benchmark, args.delta_threshold)

    if args.format == "json":
        payload = {
            "benchmark": str(benchmark_path),
            "delta_threshold": args.delta_threshold,
            "observations": [asdict(item) for item in observations],
        }
        print(json.dumps(payload, indent=2))
        return 0

    print(f"Benchmark: {benchmark_path}")
    print(f"Delta threshold: {args.delta_threshold}")
    print("Observations:")
    if not observations:
        print("- (none)")
        return 0

    for item in observations:
        print(
            f"- eval {item.eval_id}: {item.classification} "
            f"(with_skill={item.with_skill_pass_rate:.2f}, baseline={item.baseline_pass_rate:.2f}, delta={item.delta:+.2f})"
        )
        print(f"  recommendation: {item.recommendation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
