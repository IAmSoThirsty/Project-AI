"""tests/test_policy_registry.py — Upgrade 6: PolicyRegistry versioning, drift detection, migration."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from app.core.policy_registry import PolicyRecord, PolicyRegistry


def make_policy(version="2.0", rules=None, weaken=False):
    r = rules or {"*": {"read": True, "list": True}}
    if weaken:
        r = {"*": {"read": True}, "system": {"shutdown": True, "reset": True}}
    rec = PolicyRecord(version=version, policy_hash="", rules=r, signed_by="test")
    rec.policy_hash = rec.compute_hash()
    rec.signature = rec.sign()
    return rec


class TestPolicyRegistry:
    def test_default_policy_initialized(self):
        reg = PolicyRegistry()
        assert reg.active_version == "1.0.0"
        assert reg.active_hash

    def test_register_valid_policy(self):
        reg = PolicyRegistry()
        rec = make_policy("2.0")
        reg.register_policy(rec, activating_authority="test-admin")
        assert reg.active_version == "2.0"

    def test_unsigned_policy_rejected(self):
        reg = PolicyRegistry()
        rec = make_policy("3.0")
        rec.signature = "invalid"
        with pytest.raises(PermissionError):
            reg.register_policy(rec)

    def test_hash_mismatch_rejected(self):
        reg = PolicyRegistry()
        rec = make_policy("3.0")
        rec.policy_hash = "wrong"
        with pytest.raises(ValueError):
            reg.register_policy(rec)

    def test_governance_weakening_blocked(self):
        reg = PolicyRegistry()
        bad_rec = make_policy("4.0", weaken=True)
        with pytest.raises(PermissionError, match="weaken"):
            reg.register_policy(bad_rec)

    def test_drift_detection(self):
        reg = PolicyRegistry()
        # Tamper with active hash
        reg._active.policy_hash = "tampered"
        assert reg.detect_drift()

    def test_no_drift_when_clean(self):
        reg = PolicyRegistry()
        assert not reg.detect_drift()

    def test_human_gap_check_significant_gap(self):
        reg = PolicyRegistry()
        rec = make_policy("2.0")
        reg.register_policy(rec)
        result = reg.human_gap_check("significant")
        assert result == "CLARIFY"

    def test_human_gap_check_epochal_gap(self):
        reg = PolicyRegistry()
        rec = make_policy("2.0")
        reg.register_policy(rec)
        result = reg.human_gap_check("epochal")
        assert result == "HUMAN_APPROVAL_REQUIRED"

    def test_human_gap_check_no_gap_no_action(self):
        reg = PolicyRegistry()
        # No policy change — same hash
        result = reg.human_gap_check("significant")
        assert result is None

    def test_mutation_audit_recorded(self):
        reg = PolicyRegistry()
        rec = make_policy("2.0")
        reg.register_policy(rec, activating_authority="admin")
        audit = reg.get_mutation_audit()
        assert any(e["event"] == "POLICY_ACTIVATED" for e in audit)

    def test_action_permitted(self):
        reg = PolicyRegistry()
        ok, reason = reg.is_action_permitted("any", "read")
        assert ok

    def test_system_shutdown_denied_by_default(self):
        reg = PolicyRegistry()
        ok, _ = reg.is_action_permitted("system", "shutdown")
        assert not ok
