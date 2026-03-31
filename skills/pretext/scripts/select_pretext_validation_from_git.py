#!/usr/bin/env python3
"""Infer a validation plan from git diff state."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from select_pretext_validation_by_files import plan_for_paths, render_plan_json, render_plan_text


def run_git_diff(repo_root: Path, staged: bool, rev_range: str | None) -> list[str]:
    cmd = ["git", "diff", "--name-only", "--relative"]
    if staged:
        cmd.append("--staged")
    if rev_range:
        cmd.append(rev_range)

    result = subprocess.run(
        cmd,
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff failed")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description="Infer a Pretext validation plan from git diff state.")
    parser.add_argument("--repo", default=".", help="Repository root to inspect.")
    parser.add_argument("--staged", action="store_true", help="Use staged changes instead of the working tree diff.")
    parser.add_argument("--rev-range", help="Optional git diff revision range, for example HEAD~1..HEAD.")
    parser.add_argument("--revspec", help="Alias for --rev-range, for example HEAD~1..HEAD.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    rev_range = args.revspec or args.rev_range
    try:
        changed_paths = run_git_diff(repo_root, args.staged, rev_range)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not changed_paths:
        if args.format == "json":
            print('{"areas":[],"reason":"No changed files in git diff state.","commands":[],"follow_up_checks":[],"matched_paths":[]}')
        else:
            print("Areas: (none)")
            print("Reason: No changed files in git diff state.")
            print("Matched paths:")
            print("- (none)")
            print("Commands:")
            print("- (none)")
            print("Follow-up checks:")
            print("- (none)")
        return 0

    plan = plan_for_paths(changed_paths)
    if args.format == "json":
        print(render_plan_json(plan))
        return 0
    print(render_plan_text(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
