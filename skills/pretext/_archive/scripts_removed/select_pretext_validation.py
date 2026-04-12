#!/usr/bin/env python3
"""Recommend a minimal validation plan for a Pretext change area."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from pretext_validation_catalog import PLANS


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend a validation plan for a Pretext change area.")
    parser.add_argument(
        "--area",
        required=True,
        choices=sorted(PLANS.keys()),
        help="The subsystem or change area.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format.",
    )
    args = parser.parse_args()

    plan = PLANS[args.area]
    if args.format == "json":
        print(json.dumps(asdict(plan), indent=2))
        return 0

    print(f"Area: {plan.area}")
    print(f"Reason: {plan.reason}")
    print("Commands:")
    for command in plan.commands:
        print(f"- {command}")
    print("Follow-up checks:")
    for check in plan.follow_up_checks:
        print(f"- {check}")
    print("Source files:")
    for source in plan.source_files:
        print(f"- {source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
