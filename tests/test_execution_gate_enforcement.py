"""ExecutionGate enforcement-layer fail-closed tests."""
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.core.execution_authorization import ExecutionAuthorization
from app.core.execution_gate import ExecutionGate
from app.core.governance_outcomes import GovernanceOutcome, GovernanceResult
from app.core.policy_decision import PolicyDecision
from psia.canonical.capability_authority import CapabilityAuthority
from psia.schemas.capability import CapabilityScope


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


def _canonical_authority_and_token(
    action: str = "write_file",
    resource: str = "state://data/*",
) -> tuple[CapabilityAuthority, object]:
    authority = CapabilityAuthority()
    token = authority.issue(
        subject="tests",
        scopes=[CapabilityScope(resource=resource, actions=[action])],
    )
    return authority, token


def _install_bridge(monkeypatch, bridge):
    import app.core.capability_authority_bridge as capability_authority_bridge

    monkeypatch.setattr(
        capability_authority_bridge,
        "get_capability_authority_bridge",
        lambda: bridge,
    )


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


def test_valid_canonical_capability_token_executes(monkeypatch):
    from app.core.capability_authority_bridge import CapabilityAuthorityBridge

    gate = _install_happy_path(monkeypatch, action="write_file")
    authority, token = _canonical_authority_and_token()
    _install_bridge(monkeypatch, CapabilityAuthorityBridge(authority=authority))

    executed = False

    def executor(_context):
        nonlocal executed
        executed = True
        return "executed"

    ok, result = gate.execute(
        "tests",
        "write_file",
        {
            "actor": "tests",
            "session_id": "sess-1",
            "request_text": "write file",
            "requires_capability_token": True,
            "required_resource": "state://data/item",
            "_capability_token": token,
        },
        executor,
    )

    assert ok
    assert result == "executed"
    assert executed


def test_revoked_canonical_capability_token_does_not_execute(monkeypatch):
    from app.core.capability_authority_bridge import CapabilityAuthorityBridge

    gate = _install_happy_path(monkeypatch, action="write_file")
    authority, token = _canonical_authority_and_token()
    authority.revoke(token.token_id, reason="test")
    _install_bridge(monkeypatch, CapabilityAuthorityBridge(authority=authority))

    executed = False

    def executor(_context):
        nonlocal executed
        executed = True
        return "executed"

    ok, reason = gate.execute(
        "tests",
        "write_file",
        {
            "actor": "tests",
            "session_id": "sess-1",
            "request_text": "write file",
            "requires_capability_token": True,
            "required_resource": "state://data/item",
            "_capability_token": token,
        },
        executor,
    )

    assert not ok
    assert not executed
    assert "CapabilityToken rejected" in reason
    assert "revoked" in reason.lower()


def test_replayed_canonical_capability_token_does_not_execute_second_time(
    monkeypatch,
):
    from app.core.capability_authority_bridge import CapabilityAuthorityBridge

    gate = _install_happy_path(monkeypatch, action="write_file")
    authority, token = _canonical_authority_and_token()
    _install_bridge(monkeypatch, CapabilityAuthorityBridge(authority=authority))

    executions = 0

    def executor(_context):
        nonlocal executions
        executions += 1
        return "executed"

    context = {
        "actor": "tests",
        "session_id": "sess-1",
        "request_text": "write file",
        "requires_capability_token": True,
        "required_resource": "state://data/item",
        "_capability_token": token,
    }

    first_ok, first_result = gate.execute("tests", "write_file", context, executor)
    second_ok, second_reason = gate.execute("tests", "write_file", context, executor)

    assert first_ok
    assert first_result == "executed"
    assert not second_ok
    assert executions == 1
    assert "replay" in second_reason.lower() or "consumed" in second_reason.lower()


def test_default_secret_legacy_hmac_capability_token_does_not_execute(monkeypatch):
    import app.core.capability_token as capability_token
    from app.core.capability_authority_bridge import CapabilityAuthorityBridge
    from app.core.capability_token import CapabilityTokenService

    monkeypatch.delenv("CAPABILITY_TOKEN_SECRET", raising=False)
    monkeypatch.setattr(
        capability_token,
        "_SECRET",
        "dev-secret-change-in-production",
    )
    capability_token._USED_TOKENS.clear()

    gate = _install_happy_path(monkeypatch, action="write_file")
    token = CapabilityTokenService().mint(
        "write_file",
        ["files:write"],
        "sess-1",
        "conv-1",
        "ctx",
        "auth",
        policy_hash="test-policy-hash",
    )
    _install_bridge(monkeypatch, CapabilityAuthorityBridge())

    executed = False

    def executor(_context):
        nonlocal executed
        executed = True
        return "executed"

    ok, reason = gate.execute(
        "tests",
        "write_file",
        {
            "session_id": "sess-1",
            "request_text": "write file",
            "requires_capability_token": True,
            "capability_token_format": "legacy_hmac",
            "required_scope": ["files:write"],
            "_capability_token": token,
        },
        executor,
    )

    assert not ok
    assert not executed
    assert "secret" in reason.lower()


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
