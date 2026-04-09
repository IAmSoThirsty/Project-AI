#!/usr/bin/env python3
# [Verify Sovereign Loaders]               [2026-04-09 04:10]
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
    "src.app.main",
    "src.app.api_core",
    "src.app.api_server",
    "src.app.main_headless_wrapper",
    "src.app.governance.audit_log",
    "src.app.governance.genesis_continuity",
    "src.app.governance.sovereign_audit_log",
    "src.app.governance.tsa_anchor_manager",
    "web.backend.app",
    "thirsty_lang.src.thirsty_interpreter",
]

FILES = [
    "data/genesis_keys/genesis_audit.pub",
    "data/genesis_keys/genesis_id.txt",
    "data/genesis_pins/external_pins.json",
    "data/genesis_pins/continuity_log.json",
    "data/tsa_anchors/tsa_anchor_chain.json",
    "data/sovereign_audit/operational_audit.yaml",
    "Claude/README.md",
    "Codex/README.md",
    "IDE_README.md",
    "WORKSPACE_SETUP.md",
    "Sovereign_Agent_Standard.md",
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
