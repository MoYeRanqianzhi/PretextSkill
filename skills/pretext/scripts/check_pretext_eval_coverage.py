#!/usr/bin/env python3
"""Check whether the formal eval suite covers all supported goals and surfaces."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from select_pretext_api import SUPPORTED_GOALS, SUPPORTED_SURFACES
from select_pretext_owner import CATALOG as OWNER_CATALOG
from select_pretext_tooling_surface import SUPPORTED_TOOLING_AREAS
from pretext_validation_catalog import PLANS


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    evals_path = repo_root / "skills" / "pretext" / "evals" / "evals.json"
    coverage_path = repo_root / "skills" / "pretext" / "evals" / "coverage.json"

    evals_data = json.loads(evals_path.read_text(encoding="utf-8"))
    coverage_data = json.loads(coverage_path.read_text(encoding="utf-8"))

    eval_ids = {item["id"] for item in evals_data["evals"]}
    missing_eval_ids: list[int] = []
    for goal, ids in coverage_data["goals"].items():
        for eval_id in ids:
            if eval_id not in eval_ids and eval_id not in missing_eval_ids:
                missing_eval_ids.append(eval_id)
    for surface, ids in coverage_data["surfaces"].items():
        for eval_id in ids:
            if eval_id not in eval_ids and eval_id not in missing_eval_ids:
                missing_eval_ids.append(eval_id)
    for area, ids in coverage_data.get("tooling_areas", {}).items():
        for eval_id in ids:
            if eval_id not in eval_ids and eval_id not in missing_eval_ids:
                missing_eval_ids.append(eval_id)
    for issue, ids in coverage_data.get("owner_issues", {}).items():
        for eval_id in ids:
            if eval_id not in eval_ids and eval_id not in missing_eval_ids:
                missing_eval_ids.append(eval_id)
    for area, ids in coverage_data.get("validation_areas", {}).items():
        for eval_id in ids:
            if eval_id not in eval_ids and eval_id not in missing_eval_ids:
                missing_eval_ids.append(eval_id)

    missing_goals = [goal for goal in SUPPORTED_GOALS if goal not in coverage_data["goals"]]
    missing_surfaces = [surface for surface in SUPPORTED_SURFACES if surface != "generic" and surface not in coverage_data["surfaces"]]
    missing_tooling_areas = [area for area in SUPPORTED_TOOLING_AREAS if area not in coverage_data.get("tooling_areas", {})]
    missing_owner_issues = [issue for issue in sorted(OWNER_CATALOG.keys()) if issue not in coverage_data.get("owner_issues", {})]
    missing_validation_areas = [area for area in sorted(PLANS.keys()) if area not in coverage_data.get("validation_areas", {})]
    empty_goals = [goal for goal in SUPPORTED_GOALS if not coverage_data["goals"].get(goal)]
    empty_surfaces = [
        surface
        for surface in SUPPORTED_SURFACES
        if surface != "generic" and not coverage_data["surfaces"].get(surface)
    ]
    empty_tooling_areas = [
        area for area in SUPPORTED_TOOLING_AREAS if not coverage_data.get("tooling_areas", {}).get(area)
    ]
    empty_owner_issues = [
        issue for issue in sorted(OWNER_CATALOG.keys()) if not coverage_data.get("owner_issues", {}).get(issue)
    ]
    empty_validation_areas = [
        area for area in sorted(PLANS.keys()) if not coverage_data.get("validation_areas", {}).get(area)
    ]

    if (
        not missing_goals
        and not missing_surfaces
        and not missing_tooling_areas
        and not missing_owner_issues
        and not missing_validation_areas
        and not empty_goals
        and not empty_surfaces
        and not empty_tooling_areas
        and not empty_owner_issues
        and not empty_validation_areas
        and not missing_eval_ids
    ):
        print("Eval coverage is in sync with supported goals, surfaces, tooling areas, owner issues, and validation areas.")
        return 0

    if missing_goals:
        print("Missing goals in coverage.json:")
        for goal in missing_goals:
            print(f"- {goal}")
    if empty_goals:
        print("Goals without mapped evals:")
        for goal in empty_goals:
            print(f"- {goal}")
    if missing_surfaces:
        print("Missing surfaces in coverage.json:")
        for surface in missing_surfaces:
            print(f"- {surface}")
    if empty_surfaces:
        print("Surfaces without mapped evals:")
        for surface in empty_surfaces:
            print(f"- {surface}")
    if missing_tooling_areas:
        print("Missing tooling areas in coverage.json:")
        for area in missing_tooling_areas:
            print(f"- {area}")
    if empty_tooling_areas:
        print("Tooling areas without mapped evals:")
        for area in empty_tooling_areas:
            print(f"- {area}")
    if missing_owner_issues:
        print("Missing owner issues in coverage.json:")
        for issue in missing_owner_issues:
            print(f"- {issue}")
    if empty_owner_issues:
        print("Owner issues without mapped evals:")
        for issue in empty_owner_issues:
            print(f"- {issue}")
    if missing_validation_areas:
        print("Missing validation areas in coverage.json:")
        for area in missing_validation_areas:
            print(f"- {area}")
    if empty_validation_areas:
        print("Validation areas without mapped evals:")
        for area in empty_validation_areas:
            print(f"- {area}")
    if missing_eval_ids:
        print("Coverage references unknown eval IDs:")
        for eval_id in sorted(missing_eval_ids):
            print(f"- {eval_id}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
