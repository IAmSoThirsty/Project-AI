#!/usr/bin/env python3
"""Audit repository files for active markers and stub implementations.

This is a maintenance utility for identifying files that no longer look
active and collecting candidate stubs for archiving or review.
"""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_DIRS = {
    "api",
    "cognition",
    "engines",
    "governance",
    "integrations",
    "kernel",
    "project_ai",
    "scripts",
    "security",
    "src",
}
EXTENSIONS = {
    ".py",
    ".tarl",
    ".thirst",
    ".thirsty",
    ".go",
    ".js",
    ".ts",
    ".c",
    ".cpp",
    ".h",
    ".md",
    ".tscgb",
}

NON_ACTIVE_RESULTS = Path(os.getenv("TMPDIR") or os.getenv("TEMP") or os.getenv("TMP") or ".") / "audit_results_non_active.txt"
STUB_RESULTS = Path(os.getenv("TMPDIR") or os.getenv("TEMP") or os.getenv("TMP") or ".") / "audit_results_stubs.txt"


def audit() -> None:
    non_active: list[str] = []
    stubs: list[str] = []

    for directory in PROJECT_DIRS:
        if not os.path.exists(directory):
            continue

        for root, _dirs, files in os.walk(directory):
            for file_name in files:
                ext = os.path.splitext(file_name)[1]
                if ext not in EXTENSIONS:
                    continue

                path = os.path.join(root, file_name)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                        head = [handle.readline() for _ in range(10)]
                        content = "".join(head)

                        if "STATUS: ACTIVE" not in content:
                            non_active.append(path)

                        handle.seek(0)
                        full_content = handle.read()
                        if "raises NotImplementedError" in full_content or (
                            "def " in full_content
                            and "pass" in full_content
                            and len(full_content) < 500
                        ):
                            stubs.append(path)
                except Exception as exc:  # pragma: no cover - maintenance utility
                    print(f"Error reading {path}: {exc}")

    for file_name in os.listdir("."):
        if not os.path.isfile(file_name):
            continue

        ext = os.path.splitext(file_name)[1]
        if ext not in EXTENSIONS:
            continue

        try:
            with open(file_name, "r", encoding="utf-8", errors="ignore") as handle:
                head = [handle.readline() for _ in range(10)]
                content = "".join(head)
                if "STATUS: ACTIVE" not in content:
                    non_active.append(file_name)
        except Exception:
            pass

    NON_ACTIVE_RESULTS.write_text("\n".join(non_active), encoding="utf-8")
    STUB_RESULTS.write_text("\n".join(sorted(set(stubs))), encoding="utf-8")
    print(f"Audit complete. Non-active: {len(non_active)}, Stubs: {len(stubs)}")


if __name__ == "__main__":
    audit()
