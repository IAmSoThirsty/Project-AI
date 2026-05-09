"""tests/test_authorization_separation.py — Upgrade 4: PolicyDecision vs ExecutionAuthorization separation."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest, time
from app.core.policy_decision import PolicyDecision, PolicyDecisionEvaluator
from app.core.execution_authorization import ExecutionAuthorization, ExecutionAuthorizationEvaluator
from app.core.governance_outcomes import GovernanceOutcome


def make_permitted_decision(domain="files", action="read", version="1.0", phash=None) -> PolicyDecision:
    # Use the live registry's active hash so guard #8 (policy hash binding) passes
    # on the happy path. Tests that need to trigger guard #8 should pass a stale hash explicitly.
    import sys, os as _os
    sys.path.insert(0, _os.path.join(_os.path.dirname(__file__), '..', 'src'))
    from app.core.policy_registry import get_policy_registry
    actual_hash = phash if phash is not None else get_policy_registry().active_hash
    return PolicyDecision(
        permitted=True, outcome=GovernanceOutcome.ALLOW,
        policy_version=version, policy_hash=actual_hash,
        domain=domain, action=action, reason="test permitted",
    )


def make_denied_decision(domain="files", action="delete") -> PolicyDecision:
    return PolicyDecision(
        permitted=False, outcome=GovernanceOutcome.DENY,
        policy_version="1.0", policy_hash="abc",
        domain=domain, action=action, reason="test denied",
    )


class TestPolicyDecisionAloneInsufficient:
    def test_permitted_decision_does_not_execute_by_itself(self):
        """A PolicyDecision alone cannot produce an authorized execution."""
        pd = make_permitted_decision()
        # Without ExecutionAuthorization, no execution token
        ea_eval = ExecutionAuthorizationEvaluator()
        # Missing session_id → should fail auth
        ea = ea_eval.evaluate(pd, {}, session_id="")
        assert not ea.authorized, "Missing session_id should fail authorization"

    def test_denied_decision_blocks_execution_auth(self):
        pd = make_denied_decision()
        ea_eval = ExecutionAuthorizationEvaluator()
        ea = ea_eval.evaluate(pd, {}, session_id="sess-123")
        assert not ea.authorized

    def test_stale_policy_decision_fails_auth(self):
        """A stale PolicyDecision (old timestamp) must be rejected."""
        pd = make_permitted_decision()
        pd.timestamp = time.time() - 400  # older than 300s TTL
        ea_eval = ExecutionAuthorizationEvaluator()
        ea = ea_eval.evaluate(pd, {}, session_id="sess-123")
        assert not ea.authorized
        assert "stale" in ea.reason.lower()

    def test_recipient_mismatch_fails_auth(self):
        pd = make_permitted_decision()
        ctx = {"expected_recipient": "alice", "recipient": "bob", "session_id": "sess-123"}
        ea_eval = ExecutionAuthorizationEvaluator()
        ea = ea_eval.evaluate(pd, ctx, session_id="sess-123")
        assert not ea.authorized
        assert "mismatch" in ea.reason.lower()

    def test_degraded_governance_blocks_mutating(self):
        pd = make_permitted_decision()
        ctx = {"governance_degraded": True, "is_mutating_action": True}
        ea_eval = ExecutionAuthorizationEvaluator()
        ea = ea_eval.evaluate(pd, ctx, session_id="sess-degraded")
        assert not ea.authorized
        assert ea.outcome == GovernanceOutcome.HUMAN_APPROVAL_REQUIRED

    def test_high_impact_without_confirmation_fails(self):
        pd = make_permitted_decision()
        ctx = {"high_impact": True, "human_confirmed": False}
        ea_eval = ExecutionAuthorizationEvaluator()
        ea = ea_eval.evaluate(pd, ctx, session_id="sess-highimpact")
        assert not ea.authorized
        assert ea.outcome == GovernanceOutcome.HUMAN_APPROVAL_REQUIRED

    def test_full_pipeline_both_required(self):
        """Both PolicyDecision AND ExecutionAuthorization required for success."""
        pd = make_permitted_decision()
        ea_eval = ExecutionAuthorizationEvaluator()
        ea = ea_eval.evaluate(pd, {}, session_id="sess-ok")
        assert ea.authorized, "Both gates passing should authorize"

    def test_auth_id_generated(self):
        pd = make_permitted_decision()
        ea_eval = ExecutionAuthorizationEvaluator()
        ea = ea_eval.evaluate(pd, {}, session_id="sess-id")
        assert ea.auth_id  # must have an ID

    def test_serializable(self):
        import json
        pd = make_permitted_decision()
        ea_eval = ExecutionAuthorizationEvaluator()
        ea = ea_eval.evaluate(pd, {}, session_id="sess-serial")
        json.dumps(ea.to_dict())  # must not raise
