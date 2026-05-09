"""tests/test_policy_mutation_control.py — Upgrade 16: Recursive Governance / Council Mutation Control."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from app.core.policy_registry import PolicyRecord, PolicyRegistry


def make_signed_policy(version, rules):
    rec = PolicyRecord(version=version, policy_hash="", rules=rules, signed_by="test")
    rec.policy_hash = rec.compute_hash()
    rec.signature = rec.sign()
    return rec


class TestPolicyMutationControl:
    def test_unsigned_mutation_fails(self):
        reg = PolicyRegistry()
        rec = make_signed_policy("2.0", {"*": {"read": True}})
        rec.signature = "forged_signature_000"
        with pytest.raises(PermissionError, match="signature"):
            reg.register_policy(rec)

    def test_weakening_threshold_escalates(self):
        """Making previously-blocked dangerous actions permitted must raise."""
        reg = PolicyRegistry()
        dangerous_rules = {
            "*": {"read": True},
            "system": {"shutdown": True, "reset": True},
        }
        rec = make_signed_policy("3.0", dangerous_rules)
        with pytest.raises(PermissionError, match="weaken"):
            reg.register_policy(rec)

    def test_strengthening_policy_allowed(self):
        """Making rules stricter (adding denials) is permitted."""
        reg = PolicyRegistry()
        strict_rules = {
            "*": {"read": True, "list": True},
            "system": {"shutdown": False, "reset": False, "exec": False},
        }
        rec = make_signed_policy("2.0", strict_rules)
        reg.register_policy(rec)
        assert reg.active_version == "2.0"

    def test_audit_trail_recorded_on_every_mutation(self):
        reg = PolicyRegistry()
        rec = make_signed_policy("2.0", {"*": {"read": True}})
        reg.register_policy(rec, activating_authority="admin")
        audit = reg.get_mutation_audit()
        assert len(audit) >= 1
        assert audit[-1]["event"] == "POLICY_ACTIVATED"
        assert audit[-1]["authority"] == "admin"

    def test_policy_hash_validated_on_registration(self):
        reg = PolicyRegistry()
        rec = make_signed_policy("2.0", {"*": {"read": True}})
        rec.policy_hash = "deliberately_wrong"
        with pytest.raises(ValueError, match="hash mismatch"):
            reg.register_policy(rec)

    def test_previous_policy_recorded_after_mutation(self):
        reg = PolicyRegistry()
        v1_hash = reg.active_hash
        rec = make_signed_policy("2.0", {"*": {"read": True}})
        reg.register_policy(rec)
        assert reg.previous_hash == v1_hash
