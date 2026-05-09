"""ExecutionGate enforcement-layer fail-closed tests."""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.core.execution_authorization import ExecutionAuthorization
from app.core.execution_gate import ExecutionGate
from app.core.governance_outcomes import GovernanceOutcome, GovernanceResult
from app.core.policy_decision import PolicyDecision


def _legacy_decision(action: str = "read") -> SimpleNamespace:
    return SimpleNamespace(
        decision_id="legacy-decision",
        actor="tests",
        action=action,
        context={},
        approved=True,
        reason=None,
        output_hash="output-hash",
        policy_version="test-policy",
        policy_hash="test-policy-hash",
    )


def _approved_policy(action: str = "read") -> PolicyDecision:
    return PolicyDecision(
        permitted=True,
        outcome=GovernanceOutcome.ALLOW,
        policy_version="test-policy",
        policy_hash="test-policy-hash",
        domain="tests",
        action=action,
        reason="test policy allow",
    )


def _approved_auth(action: str = "read") -> ExecutionAuthorization:
    return ExecutionAuthorization(
        authorized=True,
        outcome=GovernanceOutcome.ALLOW,
        reason="test auth allow",
        domain="tests",
        action=action,
        session_id="sess-1",
        policy_decision_id="policy-decision",
        policy_hash="test-policy-hash",
        context_hash="context-hash",
    )


def _install_happy_path(monkeypatch, action: str = "read") -> ExecutionGate:
    import app.core.execution_authorization as execution_authorization
    import app.core.invariant_severity as invariant_severity
    import app.core.policy_decision as policy_decision
    import app.core.safe_allow_calibration as safe_allow_calibration
    import governance.sovereign_runtime as sovereign_runtime

    gate = ExecutionGate()
    gate.kernel = SimpleNamespace(
        evaluate_action=lambda _domain, _action, _context: (True, _legacy_decision(action))
    )
    monkeypatch.setattr(
        safe_allow_calibration.SafeAllowCalibrationLayer,
        "evaluate",
        lambda self, request_text, context, domain, action: GovernanceResult(
            outcome=GovernanceOutcome.ALLOW,
            reason="test safe allow",
            domain=domain,
            action=action,
        ),
    )
    monkeypatch.setattr(
        policy_decision.PolicyDecisionEvaluator,
        "evaluate",
        lambda self, domain, action, context: _approved_policy(action),
    )
    monkeypatch.setattr(
        execution_authorization.ExecutionAuthorizationEvaluator,
        "evaluate",
        lambda self, policy_decision, context, session_id: _approved_auth(action),
    )

    class FakeSovereignRuntime:
        def create_policy_state_binding(self, policy_state, context):
            return {"binding": "ok"}

        def verify_policy_state_binding(self, policy_state, context, binding):
            return True

        def audit_log(self, event_type, data, severity="INFO"):
            return None

    monkeypatch.setattr(sovereign_runtime, "SovereignRuntime", FakeSovereignRuntime)

    class FakeSeverityEngine:
        def evaluate_all(self, context):
            return []

        def should_block_execution(self, results):
            return False

    monkeypatch.setattr(invariant_severity, "get_severity_engine", lambda: FakeSeverityEngine())
    return gate


def test_safe_allow_exception_fails_closed(monkeypatch):
    import app.core.safe_allow_calibration as safe_allow_calibration

    gate = _install_happy_path(monkeypatch)

    def fail_safe_allow(self, request_text, context, domain, action):
        raise RuntimeError("calibration offline")

    monkeypatch.setattr(
        safe_allow_calibration.SafeAllowCalibrationLayer,
        "evaluate",
        fail_safe_allow,
    )

    executed = False

    def executor(_context):
        nonlocal executed
        executed = True
        return "executed"

    ok, reason = gate.execute(
        "tests",
        "read",
        {"session_id": "sess-1", "request_text": "read status"},
        executor,
    )

    assert not ok
    assert not executed
    assert "SafeAllowCalibration failed closed" in reason


def test_missing_capability_token_denies_protected_execution(monkeypatch):
    gate = _install_happy_path(monkeypatch, action="write_file")

    executed = False

    def executor(_context):
        nonlocal executed
        executed = True
        return "executed"

    ok, reason = gate.execute(
        "tests",
        "write_file",
        {"session_id": "sess-1", "request_text": "write file"},
        executor,
    )

    assert not ok
    assert not executed
    assert "CapabilityToken required" in reason


def test_degraded_read_only_can_continue_without_capability_token(monkeypatch):
    gate = _install_happy_path(monkeypatch, action="get_status")

    ok, result = gate.execute(
        "tests",
        "get_status",
        {
            "session_id": "sess-1",
            "request_text": "get status",
            "governance_degraded": True,
        },
        lambda _context: "read-only-result",
    )

    assert ok
    assert result == "read-only-result"
