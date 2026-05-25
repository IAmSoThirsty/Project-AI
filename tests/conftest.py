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

# ── D3C: App sub-modules not yet implemented ─────────────────────────────────
# These tests reference internal app modules that were never written.
# Isolated here until the corresponding modules are implemented.
_GROUP_C_TESTS = [
    # sovereign_audit_log family (6) — all implemented 2026-05-22
    # test_12_vector_constitutional_break.py — implemented 2026-05-22
    # test_attack_simulation_suite.py — implemented 2026-05-22
    # test_external_merkle_anchor.py — implemented 2026-05-22
    # test_tsa_integration.py — implemented 2026-05-22
    # miniature_office sub-modules (3)
    # test_agent_lounge.py — implemented 2026-05-20
    # test_meta_security_dept.py — implemented 2026-05-20
    # test_repair_crew.py — implemented 2026-05-20
    # governance / pricing modules (3)
    # test_company_pricing.py — implemented 2026-05-20
    # test_government_pricing.py — implemented 2026-05-20
    # test_government_pricing_manual.py — implemented 2026-05-20
    # security sub-modules (3)
    # test_asymmetric_security_coverage.py — implemented 2026-05-20
    # test_immutable_audit_log.py — implemented 2026-05-20
    # test_security_comprehensive.py — implemented 2026-05-20
    # signal_flows (2) — implemented 2026-05-20
    # test_signal_flows_100_percent.py — implemented 2026-05-20
    # test_signal_flows_complete_coverage.py — implemented 2026-05-20
    # vault (1)
    # test_vault_comprehensive.py — implemented 2026-05-20
    # infrastructure / singletons (3) — test_cathedral_infrastructure.py implemented 2026-05-20
    # test_tseca_ghost_protocol.py — implemented 2026-05-20
    # test_personal_agent.py — implemented 2026-05-20
    # cerberus.sase sub-modules (2)
    # test_containment.py — implemented 2026-05-20
    # test_substrate.py — implemented 2026-05-20
    # misc structural (3)
    # test_entropy_slope.py — implemented 2026-05-21
    # test_reasoning_matrix.py — implemented 2026-05-20
    # test_cognition_comprehensive.py — enabled 2026-05-20
    # test_repo_scan_contract.py — implemented 2026-05-22
    # subdirectory tests
    # manual/test_12_vector_break_suite.py — implemented 2026-05-22
    # manual/test_audit_integration.py — implemented 2026-05-20
    # manual/test_sovereign_manual.py — implemented 2026-05-22
    # sase/core/test_normalization.py — implemented 2026-05-20
]

# ── Platform-specific: PyQt6 not available in CI / Docker ────────────────────
_PYQT6_TESTS = [
    "test_leather_book_smoke.py",
    "gui_e2e/test_launch_and_login.py",
]

# Merge all isolation lists into collect_ignore (paths relative to tests/)
collect_ignore: list[str] = (
    _PSIA_TESTS + _SHADOW_THIRST_TESTS + _GROUP_C_TESTS + _PYQT6_TESTS
)
