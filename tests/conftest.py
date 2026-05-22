"""Pytest configuration: ensure repository root (for non-src packages like `web`) is importable.

This adds the project root to sys.path so tests can import the top-level `web` package.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

for path in (ROOT, SRC):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

# ── D3D: PSIA package not yet implemented ────────────────────────────────────
# psia.* modules are a planned system (Protocol for Sovereign Intelligence
# Auditing). No psia package exists anywhere in the repo. These test files
# describe intended future behavior and must not be collected until psia/ is
# written. Do not create stubs — stubs give false confidence.
collect_ignore_glob = [
    "test_psia_*.py",
]

# Additional PSIA-dependent tests not matching the psia_ prefix:
_PSIA_TESTS = [
    "test_bft_deployed.py",               # psia.gate.quorum_engine
    "test_ed25519_crypto.py",             # psia.crypto.ed25519_provider
    "test_formal_properties.py",          # psia.canonical.capability_authority
    "test_governance_server.py",          # psia.server.governance_server
    "test_rfc3161.py",                    # psia.crypto.ed25519_provider
    "test_shadow_operational_semantics.py",  # psia.shadow.operational_semantics
]

# ── D3E: Shadow Thirst UTF sub-modules not yet implemented ───────────────────
# shadow_thirst.bytecode and shadow_thirst.type_system are planned Tier 4 UTF
# sub-modules. The shadow_thirst package exists but these sub-modules are not
# yet written. Isolate until D3E UTF completion phase.
_SHADOW_THIRST_TESTS = [
    "test_shadow_thirst.py",              # shadow_thirst.bytecode
    "test_shadow_thirst_type_system.py",  # shadow_thirst.type_system
]

# ── D3C: App sub-modules not yet implemented ─────────────────────────────────
# These tests reference internal app modules that were never written.
# Isolated here until the corresponding modules are implemented.
_GROUP_C_TESTS = [
    # sovereign_audit_log family (6) — test_sovereign_audit_log.py implemented
    "test_12_vector_constitutional_break.py",
    "test_attack_simulation_suite.py",
    "test_external_merkle_anchor.py",
    "test_tsa_integration.py",
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
    "test_repo_scan_contract.py",        # repo_scan_contract (not on sys.path)
    # subdirectory tests
    "manual/test_12_vector_break_suite.py",
    # manual/test_audit_integration.py — implemented 2026-05-20
    "manual/test_sovereign_manual.py",
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
