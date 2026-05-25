"""Pytest configuration: ensure repository root (for non-src packages like `web`) is importable.

This adds the project root to sys.path so tests can import the top-level `web` package.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

for path in (ROOT, SRC):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)


def pytest_configure(config) -> None:  # noqa: ANN001
    """Alias app.* modules under src.app.* so unittest.mock.patch targets work
    regardless of which import path the test module used."""
    _GOVERNANCE_MODULES = [
        "app.governance.external_merkle_anchor",
        "app.governance.tsa_anchor_manager",
        "app.governance.tsa_provider",
        "app.governance.sovereign_audit_log",
        "app.governance.genesis_continuity",
    ]
    for short in _GOVERNANCE_MODULES:
        src_name = "src." + short
        try:
            m = importlib.import_module(short)
            if src_name not in sys.modules:
                sys.modules[src_name] = m
        except ImportError:
            pass


# ── D3D: PSIA package — implemented 2026-05-23; governance_server 2026-05-25 ──
# All test_psia_*.py files and all PSIA-dependent tests now pass.
collect_ignore_glob: list[str] = []

# Additional PSIA-dependent tests not matching the psia_ prefix:
# test_governance_server.py — implemented 2026-05-25 (psia.server.governance_server)
_PSIA_TESTS: list[str] = []

# ── D3E: Shadow Thirst UTF sub-modules — implemented 2026-05-25 ──────────────
# shadow_thirst package (src/shadow_thirst/) implements lexer, parser, IR,
# static analysis, bytecode, VM, constitutional, compiler, type_system.
# All 41 tests passing.
_SHADOW_THIRST_TESTS: list[str] = []

# ── Platform-specific: PyQt6 not available in CI / Docker ────────────────────
_PYQT6_TESTS = [
    "test_leather_book_smoke.py",
    "gui_e2e/test_launch_and_login.py",
]

# Merge all isolation lists into collect_ignore (paths relative to tests/)
collect_ignore: list[str] = _PSIA_TESTS + _SHADOW_THIRST_TESTS + _PYQT6_TESTS
