#!/usr/bin/env python3
# (System Integrity Affirmation)             [2026-04-09 04:26]
#                                          Status: Active
"""Verify that the canonical Project-AI loaders can be imported."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

from src.block_pyqt6 import ensure_pyqt6_available

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

for path_entry in (ROOT, SRC):
    path_str = str(path_entry)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

ensure_pyqt6_available()

MODULES = [
    "app.inspection.repository_inspector",
    "app.ui.render_engine",
    "thirsty_lang.src.thirsty_interpreter",
]

FILES = [
    "launcher.py",
    "src/app/inspection/repository_inspector.py",
    "src/app/ui/render_engine.py",
    "src/thirsty_lang/src/thirsty_interpreter.py",
    "src/app/sovereign/sovereign_boot.thirsty",
    "README.md",
    "inventory.csv",
]


def main() -> int:
    """Run loader and file presence checks."""

    failures: list[str] = []

    for module_name in MODULES:
        try:
            importlib.import_module(module_name)
        except Exception as exc:
            failures.append(f"{module_name}: {exc}")

    for relative_path in FILES:
        file_path = ROOT / relative_path
        if not file_path.exists():
            failures.append(f"missing file: {relative_path}")

    if failures:
        print("VERIFY_SOVEREIGN_LOADERS_FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("VERIFY_SOVEREIGN_LOADERS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
