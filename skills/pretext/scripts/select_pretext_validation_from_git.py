#!/usr/bin/env python3
"""Infer a validation plan from git diff state."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from select_pretext_validation_by_files import plan_for_paths, render_plan_json, render_plan_text


def looks_like_pretext_repo(path: Path) -> bool:
    return (path / ".git").exists() and (path / "src" / "layout.ts").exists()


def resolve_repo(repo: str | None) -> Path:
    if repo:
        return Path(repo).resolve()

    cwd = Path.cwd().resolve()
    candidates = [cwd]
    candidates.extend(parent / "pretext" for parent in [cwd, *cwd.parents])

    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if looks_like_pretext_repo(candidate):
            return candidate

    return cwd


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


def collect_changed_paths(repo_root: Path, mode: str, rev_range: str | None) -> list[str]:
    if rev_range:
        return run_git_diff(repo_root, staged=False, rev_range=rev_range)
    if mode == "staged":
        return run_git_diff(repo_root, staged=True, rev_range=None)
    if mode == "working-tree":
        return run_git_diff(repo_root, staged=False, rev_range=None)

    merged: list[str] = []
    for path in run_git_diff(repo_root, staged=False, rev_range=None):
        if path not in merged:
            merged.append(path)
    for path in run_git_diff(repo_root, staged=True, rev_range=None):
        if path not in merged:
            merged.append(path)
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description="Infer a Pretext validation plan from git diff state.")
    parser.add_argument(
        "--repo",
        help="Repository root to inspect. Defaults to the nearest detected Pretext repo, otherwise the current directory.",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--working-tree", action="store_true", help="Use only the unstaged working-tree diff.")
    mode_group.add_argument("--staged", action="store_true", help="Use only staged changes.")
    mode_group.add_argument("--all", action="store_true", help="Union unstaged and staged changes.")
    parser.add_argument("--rev-range", "--revspec", dest="rev_range", help="Optional git diff revision range, for example HEAD~1..HEAD.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    args = parser.parse_args()

    mode = "all"
    if args.working_tree:
        mode = "working-tree"
    elif args.staged:
        mode = "staged"

    if args.rev_range and mode != "all":
        parser.error("--rev-range cannot be combined with --working-tree or --staged.")

    repo_root = resolve_repo(args.repo)

    try:
        changed_paths = collect_changed_paths(repo_root, mode, args.rev_range)
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
