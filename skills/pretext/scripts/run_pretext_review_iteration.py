#!/usr/bin/env python3
"""Run one review iteration for the Pretext skill using Claude CLI."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path


DEFAULT_EVAL_IDS = [1, 4, 5, 8, 9, 11, 24]


@dataclass(frozen=True)
class EvalItem:
    eval_id: int
    prompt: str
    expected_output: str
    expectations: list[str]


def slugify(text: str, limit: int = 48) -> str:
    lowered = text.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    if not slug:
        return "eval"
    return slug[:limit].rstrip("-")


def load_evals(path: Path) -> dict[int, EvalItem]:
    data = json.loads(path.read_text(encoding="utf-8"))
    mapping: dict[int, EvalItem] = {}
    for item in data["evals"]:
        mapping[item["id"]] = EvalItem(
            eval_id=item["id"],
            prompt=item["prompt"],
            expected_output=item["expected_output"],
            expectations=item["expectations"],
        )
    return mapping


def build_prompt(eval_item: EvalItem, skill_path: Path | None) -> str:
    shared = (
        "Answer the task in concise technical Markdown.\n"
        "State the chosen route explicitly when relevant.\n"
        "Do not mention this evaluation harness.\n\n"
        f"Task:\n{eval_item.prompt}\n"
    )
    if skill_path is None:
        return (
            "You are answering a technical task directly without any external skill instructions.\n\n"
            + shared
        )
    return (
        "You are evaluating a local Claude-style skill.\n"
        f"Skill path: {skill_path}\n\n"
        "Required process:\n"
        f"1. Read {skill_path / 'SKILL.md'} first.\n"
        "2. Follow the skill faithfully.\n"
        "3. Load only the minimum referenced files needed for the task.\n"
        "4. Answer the task directly.\n\n"
        + shared
    )


def run_claude(prompt: str, workdir: Path, model: str | None) -> tuple[str, str, int, float]:
    cmd = [
        "claude",
        "-p",
        prompt,
        "--output-format",
        "text",
        "--permission-mode",
        "bypassPermissions",
    ]
    if model:
        cmd.extend(["--model", model])

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    start = time.time()
    result = subprocess.run(
        cmd,
        cwd=workdir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    elapsed = time.time() - start
    return result.stdout, result.stderr, result.returncode, elapsed


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_iteration(
    eval_set_path: Path,
    skill_path: Path,
    workspace: Path,
    eval_ids: list[int],
    model: str | None,
) -> None:
    evals = load_evals(eval_set_path)
    workspace.mkdir(parents=True, exist_ok=True)

    history = {
        "iteration": workspace.name,
        "skill_path": str(skill_path),
        "eval_ids": eval_ids,
        "started_at_epoch": time.time(),
    }
    write_json(workspace / "iteration_metadata.json", history)

    for eval_id in eval_ids:
        if eval_id not in evals:
            raise KeyError(f"Unknown eval id {eval_id}")
        item = evals[eval_id]
        eval_slug = slugify(item.expected_output)
        eval_dir = workspace / f"eval-{eval_id:02d}-{eval_slug}"
        eval_dir.mkdir(parents=True, exist_ok=True)
        write_json(
            eval_dir / "eval_metadata.json",
            {
                "eval_id": item.eval_id,
                "eval_name": f"eval-{item.eval_id:02d}-{eval_slug}",
                "prompt": item.prompt,
                "expectations": item.expectations,
                "expected_output": item.expected_output,
            },
        )

        configs = [
            ("with_skill", skill_path),
            ("without_skill", None),
        ]
        repo_root = skill_path.parents[1]
        for config_name, config_skill_path in configs:
            run_dir = eval_dir / config_name / "run-1"
            outputs_dir = run_dir / "outputs"
            outputs_dir.mkdir(parents=True, exist_ok=True)

            prompt = build_prompt(item, config_skill_path)
            stdout, stderr, returncode, elapsed = run_claude(prompt, workdir=repo_root, model=model)
            answer = stdout.strip()
            if returncode != 0 and not answer:
                answer = f"Execution failed with return code {returncode}.\n\n{stderr.strip()}"

            transcript = (
                f"# Eval Transcript\n\n"
                f"## Eval Prompt\n\n{item.prompt}\n\n"
                f"## Harness Prompt\n\n```\n{prompt}\n```\n\n"
                f"## Result\n\n{returncode}\n\n"
                f"## Stdout\n\n{answer}\n\n"
                f"## Stderr\n\n{stderr.strip()}\n"
            )

            (outputs_dir / "answer.md").write_text(answer + ("\n" if not answer.endswith("\n") else ""), encoding="utf-8")
            (run_dir / "transcript.md").write_text(transcript, encoding="utf-8")
            (outputs_dir / "user_notes.md").write_text(
                (
                    f"- configuration: `{config_name}`\n"
                    f"- skill_path: `{config_skill_path}`\n"
                    f"- return_code: `{returncode}`\n"
                ),
                encoding="utf-8",
            )
            write_json(
                outputs_dir / "metrics.json",
                {
                    "tool_calls": {},
                    "total_tool_calls": 0,
                    "total_steps": 0,
                    "files_created": ["answer.md"],
                    "errors_encountered": 0 if returncode == 0 else 1,
                    "output_chars": len(answer),
                    "transcript_chars": len(transcript),
                },
            )
            write_json(
                run_dir / "timing.json",
                {
                    "total_tokens": 0,
                    "duration_ms": int(elapsed * 1000),
                    "total_duration_seconds": round(elapsed, 3),
                    "executor_duration_seconds": round(elapsed, 3),
                },
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one Pretext review iteration with Claude CLI.")
    parser.add_argument(
        "--eval-set",
        default="skills/pretext/evals/evals.json",
        help="Path to evals.json.",
    )
    parser.add_argument(
        "--skill-path",
        default="skills/pretext",
        help="Path to the Pretext skill directory.",
    )
    parser.add_argument(
        "--workspace",
        default="skills/pretext-workspace/iteration-1",
        help="Workspace directory for the iteration.",
    )
    parser.add_argument(
        "--eval-id",
        action="append",
        type=int,
        help="Eval ID to run. Repeatable. Defaults to a representative first-iteration subset.",
    )
    parser.add_argument("--model", default=None, help="Optional Claude model override.")
    args = parser.parse_args()

    eval_ids = args.eval_id or DEFAULT_EVAL_IDS
    run_iteration(
        eval_set_path=Path(args.eval_set).resolve(),
        skill_path=Path(args.skill_path).resolve(),
        workspace=Path(args.workspace).resolve(),
        eval_ids=eval_ids,
        model=args.model,
    )
    print(f"Review iteration written to {Path(args.workspace).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
