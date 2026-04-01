#!/usr/bin/env python3
"""Grade a Pretext review iteration using Claude CLI."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from pathlib import Path


POSITIVE_EVIDENCE_CUES = [
    "explicitly state",
    "explicitly states",
    "explicitly require",
    "explicitly requires",
    "explicitly say",
    "explicitly says",
    "explicitly choose",
    "explicitly chooses",
    "explicitly cite",
    "explicitly cites",
    "explicitly list",
    "explicitly lists",
    "clearly",
    "shows",
    "show ",
    "name ",
    "names",
    "list ",
    "lists",
    "recommend ",
    "recommends",
    "uses",
    "returns",
    "point to",
    "points to",
    "includes",
    "states ",
    "state that",
    "states that",
    "describe",
    "describes",
    "contrast",
    "contrasts",
    "mentions",
    "明确",
    "列出",
    "给出",
    "指出",
    "引用",
    "使用",
    "推荐",
    "返回",
    "说明",
]

NEGATIVE_EVIDENCE_CUES = [
    "does not",
    "did not",
    "no mention",
    "not mention",
    "never mentions",
    "missing",
    "absent",
    "fails to",
    "stops at",
    "no reference set",
    "no concrete commands",
    "does not route",
    "does not map",
    "未提及",
    "没有",
    "缺少",
    "未返回",
]


def run_claude(prompt: str, workdir: Path, model: str | None) -> str:
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
    result = subprocess.run(
        cmd,
        cwd=workdir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "claude grading run failed")
    return result.stdout


def extract_json_object(text: str) -> dict:
    stripped = text.strip()
    if not stripped:
        raise ValueError("Empty grading output")
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    fenced = re.search(r"```json\s*(\{[\s\S]*\})\s*```", stripped)
    if fenced:
        return json.loads(fenced.group(1))

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(stripped[start : end + 1])

    raise ValueError("Could not extract JSON object from grading output")


def normalize_expectations(raw_expectations: list[dict], fallback_expectations: list[str]) -> list[dict]:
    normalized: list[dict] = []
    for index, fallback_text in enumerate(fallback_expectations):
        raw = raw_expectations[index] if index < len(raw_expectations) else {}
        normalized.append(
            {
                "text": raw.get("text") or raw.get("expectation") or fallback_text,
                "passed": bool(raw.get("passed", raw.get("met", False))),
                "evidence": raw.get("evidence", ""),
            }
        )
    return normalized


def flatten_evidence_text(evidence: object) -> str:
    if isinstance(evidence, str):
        return evidence
    if isinstance(evidence, list):
        return " ".join(flatten_evidence_text(item) for item in evidence)
    if isinstance(evidence, dict):
        return " ".join(flatten_evidence_text(value) for value in evidence.values())
    return str(evidence)


def classify_evidence_polarity(evidence: object) -> str:
    text = flatten_evidence_text(evidence).lower()
    if not text.strip():
        return "unclear"

    has_positive = any(cue in text for cue in POSITIVE_EVIDENCE_CUES)
    has_negative = any(cue in text for cue in NEGATIVE_EVIDENCE_CUES)

    if has_positive and not has_negative:
        return "positive"
    if has_negative and not has_positive:
        return "negative"
    return "unclear"


def repair_expectation_polarity(expectations: list[dict]) -> tuple[list[dict], list[str]]:
    repaired: list[dict] = []
    notes: list[str] = []

    for item in expectations:
        next_item = dict(item)
        polarity = classify_evidence_polarity(next_item.get("evidence", ""))
        if polarity == "positive" and not next_item["passed"]:
            next_item["passed"] = True
            notes.append(
                f"Flipped expectation to pass because the evidence text was affirmative: {next_item['text']}"
            )
        elif polarity == "negative" and next_item["passed"]:
            next_item["passed"] = False
            notes.append(
                f"Flipped expectation to fail because the evidence text was negative: {next_item['text']}"
            )
        repaired.append(next_item)

    return repaired, notes


def normalize_claims(raw_claims: list[dict]) -> list[dict]:
    claims: list[dict] = []
    for raw in raw_claims:
        if not isinstance(raw, dict):
            claims.append(
                {
                    "claim": str(raw),
                    "type": "factual",
                    "verified": False,
                    "evidence": "",
                }
            )
            continue
        claims.append(
            {
                "claim": raw.get("claim", ""),
                "type": raw.get("type", "factual"),
                "verified": bool(raw.get("verified", raw.get("supported", False))),
                "evidence": raw.get("evidence", ""),
            }
        )
    return claims


def normalize_user_notes(raw_user_notes: object) -> dict:
    if isinstance(raw_user_notes, dict):
        return {
            "uncertainties": list(raw_user_notes.get("uncertainties", [])),
            "needs_review": list(raw_user_notes.get("needs_review", [])),
            "workarounds": list(raw_user_notes.get("workarounds", [])),
        }
    note = str(raw_user_notes).strip()
    return {
        "uncertainties": [note] if note else [],
        "needs_review": [],
        "workarounds": [],
    }


def normalize_eval_feedback(raw_eval_feedback: object) -> dict:
    if isinstance(raw_eval_feedback, dict):
        suggestions = []
        for item in raw_eval_feedback.get("suggestions", []):
            if isinstance(item, dict):
                suggestion = {"reason": item.get("reason", "")}
                if item.get("assertion"):
                    suggestion["assertion"] = item["assertion"]
                suggestions.append(suggestion)
        return {
            "suggestions": suggestions,
            "overall": raw_eval_feedback.get("overall", ""),
        }
    return {
        "suggestions": [],
        "overall": str(raw_eval_feedback).strip(),
    }


def normalize_grading(raw: dict, fallback_expectations: list[str]) -> dict:
    expectations = normalize_expectations(list(raw.get("expectations", [])), fallback_expectations)
    expectations, normalization_notes = repair_expectation_polarity(expectations)
    passed = sum(1 for item in expectations if item["passed"])
    total = len(expectations)
    failed = total - passed
    return {
        "expectations": expectations,
        "summary": {
            "passed": passed,
            "failed": failed,
            "total": total,
            "pass_rate": round((passed / total) if total else 0.0, 4),
        },
        "claims": normalize_claims(list(raw.get("claims", []))),
        "user_notes_summary": normalize_user_notes(raw.get("user_notes_summary", {})),
        "eval_feedback": normalize_eval_feedback(raw.get("eval_feedback", {})),
        "normalization_notes": normalization_notes,
    }


def iter_runs(workspace: Path) -> list[tuple[Path, dict]]:
    runs: list[tuple[Path, dict]] = []
    for eval_dir in sorted(workspace.glob("eval-*")):
        metadata = json.loads((eval_dir / "eval_metadata.json").read_text(encoding="utf-8"))
        for run_dir in sorted(eval_dir.glob("*/*")):
            if (run_dir / "outputs").is_dir():
                runs.append((run_dir, metadata))
    return runs


def build_prompt(run_dir: Path, metadata: dict) -> str:
    return (
        "Grade this skill-eval run.\n"
        "Read the transcript and outputs, then return JSON only.\n\n"
        f"Transcript path: {run_dir / 'transcript.md'}\n"
        f"Outputs dir: {run_dir / 'outputs'}\n"
        f"Expectations: {json.dumps(metadata.get('expectations', []), ensure_ascii=False)}\n\n"
        "Rules:\n"
        "- PASS only with concrete evidence from transcript or outputs.\n"
        "- FAIL if evidence is missing, contradicted, or superficial.\n"
        "- Keep evidence concise and specific.\n"
        "- Include claims only when they are real and inspectable.\n"
        "- Keep eval_feedback suggestions high-signal only.\n"
        "- Use these keys when possible: expectations, summary, claims, user_notes_summary, eval_feedback.\n"
    )


def grade_workspace(workspace: Path, model: str | None, force: bool) -> None:
    for run_dir, metadata in iter_runs(workspace):
        grading_path = run_dir / "grading.json"
        if grading_path.exists() and not force:
            continue
        prompt = build_prompt(run_dir, metadata)
        start = time.time()
        raw = run_claude(prompt, workdir=workspace.parents[2], model=model)
        if not raw.strip():
            raw = run_claude(prompt, workdir=workspace.parents[2], model=model)
        (run_dir / "grading_raw.txt").write_text(raw, encoding="utf-8")
        grading = normalize_grading(extract_json_object(raw), list(metadata.get("expectations", [])))
        grading_duration = time.time() - start

        metrics_path = run_dir / "outputs" / "metrics.json"
        timing_path = run_dir / "timing.json"
        metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
        timing = json.loads(timing_path.read_text(encoding="utf-8")) if timing_path.exists() else {}

        grading["execution_metrics"] = metrics
        grading["timing"] = {
            "executor_duration_seconds": timing.get("executor_duration_seconds", timing.get("total_duration_seconds", 0.0)),
            "grader_duration_seconds": round(grading_duration, 3),
            "total_duration_seconds": round(
                timing.get("total_duration_seconds", timing.get("executor_duration_seconds", 0.0)) + grading_duration,
                3,
            ),
        }

        grading_path.write_text(json.dumps(grading, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Grade a Pretext review iteration using Claude CLI.")
    parser.add_argument(
        "--workspace",
        default="skills/pretext-workspace/iteration-1",
        help="Workspace directory for the iteration.",
    )
    parser.add_argument("--model", default=None, help="Optional Claude model override.")
    parser.add_argument("--force", action="store_true", help="Regenerate grading even if grading.json already exists.")
    args = parser.parse_args()

    grade_workspace(Path(args.workspace).resolve(), args.model, args.force)
    print(f"Grading written for {Path(args.workspace).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
