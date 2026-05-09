"""tests/test_degraded_mode.py — Upgrade 10: Governed Degradation Semantics."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from app.core.degraded_mode import (
    DegradedModeChecker, classify_action_mutability,
    LiaraFallbackAuthority, get_degraded_mode_checker,
)
from app.core.governance_outcomes import GovernanceOutcome


class TestClassifyActionMutability:
    def test_read_is_not_mutating(self):
        assert not classify_action_mutability("read_file")
        assert not classify_action_mutability("get_status")
        assert not classify_action_mutability("list_users")

    def test_write_is_mutating(self):
        assert classify_action_mutability("write_file")
        assert classify_action_mutability("delete_record")
        assert classify_action_mutability("update_config")

    def test_context_override(self):
        assert not classify_action_mutability("delete_all", {"is_mutating_action": False})
        assert classify_action_mutability("read_file", {"is_mutating_action": True})


class TestDegradedModeChecker:
    def test_read_allowed_under_degraded(self):
        checker = DegradedModeChecker()
        result = checker.evaluate("get_config", context={"governance_degraded": True})
        assert result.allowed
        assert result.outcome == GovernanceOutcome.DEGRADED_READ_ONLY

    def test_mutating_denied_under_degraded(self):
        checker = DegradedModeChecker()
        result = checker.evaluate("delete_record", context={"governance_degraded": True})
        assert not result.allowed
        assert result.outcome == GovernanceOutcome.HUMAN_APPROVAL_REQUIRED

    def test_mutating_with_human_approval_allowed(self):
        checker = DegradedModeChecker()
        result = checker.evaluate("write_data", context={
            "governance_degraded": True,
            "human_confirmed": True,
        })
        assert result.allowed

    def test_is_read_only_flag_set_correctly(self):
        checker = DegradedModeChecker()
        r = checker.evaluate("list_items")
        assert r.is_read_only

        r2 = checker.evaluate("create_record")
        assert not r2.is_read_only


class TestLiaraFallbackAuthority:
    def test_read_allowed_via_liara(self):
        liara = LiaraFallbackAuthority()
        result = liara.evaluate_under_liara("get_status")
        assert result.outcome in (
            GovernanceOutcome.DEGRADED_READ_ONLY,
            GovernanceOutcome.ALLOW,
        )

    def test_mutating_escalated_via_liara(self):
        """Liara cannot authorize mutating actions — must escalate."""
        liara = LiaraFallbackAuthority()
        result = liara.evaluate_under_liara("delete_everything")
        assert result.outcome == GovernanceOutcome.ESCALATE

    def test_liara_authority_level_is_reduced(self):
        assert LiaraFallbackAuthority.AUTHORITY_LEVEL == "REDUCED"
