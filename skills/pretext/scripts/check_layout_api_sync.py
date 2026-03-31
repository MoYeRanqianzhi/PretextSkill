#!/usr/bin/env python3
"""Check whether skill docs cover the exports from pretext/src/layout.ts."""

from __future__ import annotations

import re
import sys
from pathlib import Path


FUNCTION_RE = re.compile(r"^export function (\w+)\(", re.MULTILINE)
TYPE_RE = re.compile(r"^export type (\w+)\b", re.MULTILINE)
HEADING_RE = re.compile(r"^### `([A-Za-z_]\w*)(?:\(|`)", re.MULTILINE)
BULLET_CODE_RE = re.compile(r"^- `([A-Za-z_]\w*)`$", re.MULTILINE)


def extract_layout_exports(layout_ts: str) -> set[str]:
    exports = set(FUNCTION_RE.findall(layout_ts))
    exports.update(TYPE_RE.findall(layout_ts))
    return exports


def extract_documented_names(markdown: str) -> set[str]:
    names = set(HEADING_RE.findall(markdown))
    names.update(BULLET_CODE_RE.findall(markdown))
    return names


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    layout_path = repo_root / "pretext" / "src" / "layout.ts"
    public_api_path = repo_root / "skills" / "pretext" / "reference" / "public-api.md"
    internal_exports_path = repo_root / "skills" / "pretext" / "reference" / "internal-exports.md"

    layout_exports = extract_layout_exports(layout_path.read_text(encoding="utf-8"))
    documented_names = extract_documented_names(public_api_path.read_text(encoding="utf-8"))
    documented_names.update(extract_documented_names(internal_exports_path.read_text(encoding="utf-8")))

    missing = sorted(layout_exports - documented_names)
    extra = sorted(documented_names - layout_exports)

    if not missing and not extra:
        print("Layout export docs are in sync.")
        return 0

    if missing:
        print("Missing documented exports:")
        for name in missing:
            print(f"- {name}")
    if extra:
        print("Documented names that are not layout.ts exports:")
        for name in extra:
            print(f"- {name}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
