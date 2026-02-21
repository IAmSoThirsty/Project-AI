"""Tests for MetaSecurityDepartment — Tier-1 enforcement for Project-AI."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from app.miniature_office.meta_security_dept import (
    EnforcementLevel,
    MetaSecurityDepartment,
    Violation,
    ViolationType,
)


@pytest.fixture
def meta_security():
    return MetaSecurityDepartment()


@pytest.fixture
def meta_security_with_triumvirate():
    triumvirate = MagicMock()
    triumvirate.request_consensus.return_value = {
        "approved": True,
        "reason": "Triumvirate approved",
        "members": ["galahad", "cerberus", "codex"],
    }
    return MetaSecurityDepartment(triumvirate=triumvirate)


# ---------------------------------------------------------------------------
# Violation Detection
# ---------------------------------------------------------------------------


class TestViolationDetection:
    def test_detect_governance_bypass(self, meta_security):
        violations = meta_security.scan_for_violations({"bypass_governance": True, "source": "rogue_agent"})
        assert len(violations) == 1
        assert violations[0].violation_type == ViolationType.GOVERNANCE_BYPASS
        assert violations[0].severity == EnforcementLevel.CONTAINMENT

    def test_detect_privilege_escalation(self, meta_security):
        violations = meta_security.scan_for_violations({
            "requested_authority": 10,
            "granted_authority": 3,
            "source": "user_123",
        })
        assert len(violations) == 1
        assert violations[0].violation_type == ViolationType.PRIVILEGE_ESCALATION

    def test_detect_system_override(self, meta_security):
        violations = meta_security.scan_for_violations({"self_override": True})
        assert len(violations) == 1
        assert violations[0].violation_type == ViolationType.SYSTEM_OVERRIDE
        assert violations[0].severity == EnforcementLevel.LOCKDOWN

    def test_clean_context_no_violations(self, meta_security):
        violations = meta_security.scan_for_violations({"source": "user", "action": "read"})
        assert len(violations) == 0

    def test_report_violation_auto_contains(self, meta_security):
        violation = Violation(
            violation_id="test_v1",
            violation_type=ViolationType.DATA_EXFILTRATION,
            source="rogue_plugin",
            description="Data exfiltration attempt",
            severity=EnforcementLevel.CONTAINMENT,
            component_id="rogue_plugin",
        )
        meta_security.report_violation(violation)
        state = meta_security.get_security_state()
        assert "rogue_plugin" in state.contained_components


# ---------------------------------------------------------------------------
# Containment
# ---------------------------------------------------------------------------


class TestContainment:
    def test_contain_component(self, meta_security):
        result = meta_security.contain("bad_component", "Testing containment")
        assert result.success is True
        assert result.component_id == "bad_component"
        assert result.action == "isolated"

    def test_release_without_triumvirate_denied(self, meta_security):
        meta_security.contain("comp_a")
        # Without triumvirate, release should still work (no check possible)
        released = meta_security.release("comp_a")
        # No triumvirate → check fails → denied
        assert released is False

    def test_release_with_triumvirate_approval(self, meta_security_with_triumvirate):
        meta_security_with_triumvirate.contain("comp_a")
        released = meta_security_with_triumvirate.release("comp_a")
        assert released is True


# ---------------------------------------------------------------------------
# Emergency Shutdown
# ---------------------------------------------------------------------------


class TestEmergencyShutdown:
    def test_emergency_shutdown(self, meta_security):
        result = meta_security.emergency_shutdown("compromised_agent", "Detected breach")
        assert result.success is True
        assert result.requires_triumvirate_review is True
        assert result.target == "compromised_agent"
        state = meta_security.get_security_state()
        assert state.alert_level == EnforcementLevel.LOCKDOWN


# ---------------------------------------------------------------------------
# VR Enforcement
# ---------------------------------------------------------------------------


class TestVREnforcement:
    def _make_violation(self, severity: EnforcementLevel) -> Violation:
        return Violation(
            violation_id="test_v",
            violation_type=ViolationType.UNAUTHORIZED_ACTION,
            source="user_1",
            description="Test violation",
            severity=severity,
        )

    def test_warning_level(self, meta_security):
        action = meta_security.enforce_vr_action("user_1", self._make_violation(EnforcementLevel.WARNING))
        assert action.action_taken == "notification"
        assert action.access_restricted is False

    def test_intervention_level(self, meta_security):
        action = meta_security.enforce_vr_action("user_1", self._make_violation(EnforcementLevel.INTERVENTION))
        assert action.action_taken == "blocked"
        assert action.access_restricted is False

    def test_containment_level_boots_user(self, meta_security):
        action = meta_security.enforce_vr_action("user_1", self._make_violation(EnforcementLevel.CONTAINMENT))
        assert action.action_taken == "booted"
        assert action.access_restricted is True
        assert meta_security.is_user_restricted("user_1") is True

    def test_lockdown_level_requires_triumvirate(self, meta_security):
        action = meta_security.enforce_vr_action("user_1", self._make_violation(EnforcementLevel.LOCKDOWN))
        assert action.action_taken == "locked_out"
        assert action.access_restricted is True
        assert action.requires_triumvirate_reinstatement is True


# ---------------------------------------------------------------------------
# Triumvirate Reinstatement
# ---------------------------------------------------------------------------


class TestTriumvirateReinstatement:
    def test_reinstatement_denied_without_triumvirate(self, meta_security):
        violation = Violation(
            violation_id="v1",
            violation_type=ViolationType.UNAUTHORIZED_ACTION,
            source="user_1",
            description="Test",
            severity=EnforcementLevel.CONTAINMENT,
        )
        meta_security.enforce_vr_action("user_1", violation)
        decision = meta_security.request_reinstatement("user_1")
        assert decision.approved is False
        assert meta_security.is_user_restricted("user_1") is True

    def test_reinstatement_approved_with_triumvirate(self, meta_security_with_triumvirate):
        violation = Violation(
            violation_id="v1",
            violation_type=ViolationType.UNAUTHORIZED_ACTION,
            source="user_1",
            description="Test",
            severity=EnforcementLevel.CONTAINMENT,
        )
        meta_security_with_triumvirate.enforce_vr_action("user_1", violation)
        decision = meta_security_with_triumvirate.request_reinstatement("user_1")
        assert decision.approved is True
        assert meta_security_with_triumvirate.is_user_restricted("user_1") is False


# ---------------------------------------------------------------------------
# Security State
# ---------------------------------------------------------------------------


class TestSecurityState:
    def test_nominal_state(self, meta_security):
        state = meta_security.get_security_state()
        assert state.system_integrity == "nominal"
        assert state.active_violations == 0

    def test_degraded_state(self, meta_security):
        meta_security.contain("bad_comp")
        state = meta_security.get_security_state()
        assert state.system_integrity == "degraded"

    def test_compromised_state(self, meta_security):
        meta_security.emergency_shutdown("target")
        state = meta_security.get_security_state()
        assert state.system_integrity == "compromised"
