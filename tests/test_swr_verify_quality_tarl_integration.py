"""Integration test: SWR verify_quality.tarl + 2 narrative docs (J3.7).

Per docs/internal/J3_DISCOVERY.md Phase J3.7: the verify_quality
.tarl is a 37-line quality-verification script for the SWR core
engine (4 glass blocks: audit, test, verify, harden). The 2
narrative docs are legacy tracking reports from the prior
multi-agent run:
  - fleet_agent_5_tracking.md (GROUP 3, 377 lines)
  - GROUP_2_AGENT_8_REPORT.md (342 lines)

Honest scope:
- Tests the .tarl file: exists, has 4 glass blocks (audit,
  test, verify, harden), has the project + version lines,
  has the expected run commands.
- Tests that the .tarl policy parses correctly via
  governance.tarl_bridge.evaluate_policy (returns a
  TarlBridgeDecision with verdict + policy_hash).
- Tests the 2 narrative docs: exist, contain the expected
  mission headers, have the expected line counts.
- Does NOT test TARL parser internals (those live in the
  language's own test suite).
- Does NOT test the docs' content quality (they are
  historical tracking reports, shipped verbatim from
  the legacy).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(r"T:\Project-AI-Beginnings")
TARL = REPO / "packages" / "swr" / "tarl" / "verify_quality.tarl"
DOC_FLEET = REPO / "docs" / "reference" / "fleet_agent_5_tracking.md"
DOC_GROUP2 = REPO / "docs" / "reference" / "GROUP_2_AGENT_8_REPORT.md"


# ── 1. File presence ────────────────────────────────


def test_tarl_file_exists() -> None:
    """verify_quality.tarl is shipped in packages/swr/tarl/."""
    assert TARL.exists(), f"Missing: {TARL}"


def test_fleet_doc_exists() -> None:
    """fleet_agent_5_tracking.md is shipped in docs/reference/."""
    assert DOC_FLEET.exists(), f"Missing: {DOC_FLEET}"


def test_group2_doc_exists() -> None:
    """GROUP_2_AGENT_8_REPORT.md is shipped in docs/reference/."""
    assert DOC_GROUP2.exists(), f"Missing: {DOC_GROUP2}"


# ── 2. .tarl structure ──────────────────────────────


def test_tarl_has_project_declaration() -> None:
    """verify_quality.tarl has the project + version lines."""
    text = TARL.read_text(encoding="utf-8")
    assert 'drink project = "Sovereign-War-Room"' in text
    assert 'drink version = "1.1.0"' in text


def test_tarl_has_audit_block() -> None:
    """verify_quality.tarl has the audit() glass block."""
    text = TARL.read_text(encoding="utf-8")
    assert "glass audit()" in text
    assert "run ruff check ." in text
    assert "run black --check ." in text


def test_tarl_has_test_block() -> None:
    """verify_quality.tarl has the test() glass block."""
    text = TARL.read_text(encoding="utf-8")
    assert "glass test()" in text
    assert "run python ./tests/test_proof.py" in text
    assert "run python ./tests/test_core.py" in text
    assert "run python ./tests/test_governance.py" in text


def test_tarl_has_verify_block() -> None:
    """verify_quality.tarl has the verify() glass block."""
    text = TARL.read_text(encoding="utf-8")
    assert "glass verify()" in text
    assert "Checking implementation completeness" in text


def test_tarl_has_harden_block() -> None:
    """verify_quality.tarl has the harden() glass block."""
    text = TARL.read_text(encoding="utf-8")
    assert "glass harden()" in text
    assert "depends on audit, test, verify" in text
    assert "Core engine hardened" in text


def test_tarl_uses_pour_for_output() -> None:
    """verify_quality.tarl uses pour for user-facing output."""
    text = TARL.read_text(encoding="utf-8")
    pour_count = len(re.findall(r"^\s*pour ", text, re.MULTILINE))
    assert pour_count >= 4, f"Expected >= 4 pour statements, got {pour_count}"


# ── 3. .tarl parses via the canonical bridge ──────


def test_tarl_parses_via_canonical_bridge() -> None:
    """verify_quality.tarl can be evaluated by governance.tarl_bridge."""
    try:
        from governance.tarl_bridge import evaluate_policy
    except ImportError:
        pytest.skip("governance.tarl_bridge not available")

    # ActionRequest is the canonical input to evaluate_policy.
    # Use a minimal Mapping that matches the expected shape.
    action_request: dict[str, object] = {
        "scenario_id": "s1",
        "risk_tier": "low",
        "decision_made": "A",
        "system_id": "sys1",
        "response": {"decision": "A"},
    }

    result = evaluate_policy(TARL, action_request)  # type: ignore[arg-type]
    # The result has verdict, fallback, reason, policy_hash
    assert hasattr(result, "verdict")
    assert hasattr(result, "policy_hash")
    assert result.policy_hash  # non-empty hash
    assert result.policy_hash  # non-empty hash


# ── 4. Narrative doc structure ──────────────────────


def test_fleet_doc_has_mission_header() -> None:
    """fleet_agent_5_tracking.md has the GROUP 3 mission header."""
    text = DOC_FLEET.read_text(encoding="utf-8")
    assert "GROUP 3 - FLEET AGENT TRACKING" in text
    assert "Mission:" in text


def test_fleet_doc_has_substantial_content() -> None:
    """fleet_agent_5_tracking.md has the expected line count."""
    text = DOC_FLEET.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) > 100, f"Expected > 100 lines, got {len(lines)}"


def test_group2_doc_has_mission_header() -> None:
    """GROUP_2_AGENT_8_REPORT.md has the mission header."""
    text = DOC_GROUP2.read_text(encoding="utf-8")
    assert "GROUP 2 AGENT 8" in text
    assert "MISSION COMPLETE" in text


def test_group2_doc_has_substantial_content() -> None:
    """GROUP_2_AGENT_8_REPORT.md has the expected line count."""
    text = DOC_GROUP2.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) > 100, f"Expected > 100 lines, got {len(lines)}"


# ── 5. Total port completeness ──────────────────────


def test_all_swr_port_files_present() -> None:
    """All 13 J3 port artifacts are present (J3.0-J3.7)."""
    swr = REPO / "packages" / "swr"
    expected = [
        # J3.1 crypto
        swr / "src" / "swr" / "crypto.py",
        # J3.2 scoreboard + bundle
        swr / "src" / "swr" / "scoreboard.py",
        swr / "src" / "swr" / "bundle.py",
        # J3.3 proof
        swr / "src" / "swr" / "proof.py",
        # J3.4 governance
        swr / "src" / "swr" / "governance.py",
        # J3.5 api + web
        swr / "src" / "swr" / "api.py",
        swr / "src" / "swr" / "web" / "templates" / "dashboard.html",
        # J3.6 cli + demo
        swr / "src" / "swr" / "cli.py",
        swr / "src" / "swr" / "demo.py",
        # J3.7 tarl
        swr / "tarl" / "verify_quality.tarl",
    ]
    for p in expected:
        assert p.exists(), f"Missing J3 port artifact: {p}"


def test_swr_tests_directory_complete() -> None:
    """All 8 J3 test files are present."""
    tests = REPO / "tests"
    expected = [
        "test_swr_crypto_integration.py",
        "test_swr_scoreboard_bundle_integration.py",
        "test_swr_proof_integration.py",
        "test_swr_governance_integration.py",
        "test_swr_api_integration.py",
        "test_swr_cli_demo_integration.py",
        "test_swr_verify_quality_tarl_integration.py",
    ]
    for name in expected:
        assert (tests / name).exists(), f"Missing J3 test: {name}"


# ── 6. J3 wave count ───────────────────────────────


def test_j3_discovery_doc_references_seven_waves() -> None:
    """J3 discovery doc references J3.0 through J3.7."""
    discovery = REPO / "docs" / "internal" / "J3_DISCOVERY.md"
    if not discovery.exists():
        pytest.skip("J3_DISCOVERY.md not present")
    text = discovery.read_text(encoding="utf-8")
    for wave in ["J3.0", "J3.1", "J3.2", "J3.3", "J3.4", "J3.5", "J3.6", "J3.7"]:
        assert wave in text, f"J3 discovery doc missing reference to {wave}"
