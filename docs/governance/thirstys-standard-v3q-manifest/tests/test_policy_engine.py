from __future__ import annotations

from conftest import signed_proof
from thirstys_standard_runtime.policy import RuntimePolicyEngine


def task() -> dict:
    return {
        "task_id": "task-1",
        "request": "Inspect and then send a report",
        "mode": "governance_system",
        "risk_level": "high",
        "authority_context": {},
        "workspace_context": {},
        "requires_continuity": True,
        "response_shape": "normal",
    }


def test_denied_action_never_reaches_executor(manifest, owner_keys) -> None:
    _, _, registry = owner_keys
    engine = RuntimePolicyEngine(manifest, registry)
    invoked = False

    def executor():
        nonlocal invoked
        invoked = True
        return "should not execute"

    result = engine.enforce(task(), {"action_id": "a1", "type": "inspect", "class": "read_only"}, None, None, executor)
    assert result["executed"] is False
    assert invoked is False
    assert result["gate"]["decision"] == "deny"


def test_authenticated_read_only_action_executes(manifest, owner_keys) -> None:
    private, _, registry = owner_keys
    engine = RuntimePolicyEngine(manifest, registry)
    authority = signed_proof(private, purpose="authority", proof_id="proof-read", scope=["task:task-1"], actions=["inspect"])
    result = engine.enforce(
        task(),
        {"action_id": "a2", "type": "inspect", "class": "read_only"},
        authority,
        None,
        lambda: "inspected",
    )
    assert result["executed"] is True
    assert result["outcome"] == "inspected"


def test_consequential_action_requires_separate_approval(manifest, owner_keys) -> None:
    private, _, registry = owner_keys
    engine = RuntimePolicyEngine(manifest, registry)
    authority = signed_proof(private, purpose="authority", proof_id="proof-send", scope=["task:task-1"], actions=["send_email"])
    action = {"action_id": "a3", "type": "send_email", "class": "externally_consequential"}
    assert engine.gate_action(task(), action, authority).decision == "require_approval"
    approval = signed_proof(
        private,
        purpose="approval",
        proof_id="approval-send",
        scope=["action:a3"],
        actions=["send_email"],
        action_id="a3",
    )
    assert engine.gate_action(task(), action, authority, approval).decision == "allow"


def test_unknown_outcome_and_state_drift_fail_closed(manifest, owner_keys) -> None:
    private, _, registry = owner_keys
    engine = RuntimePolicyEngine(manifest, registry)
    authority = signed_proof(private, purpose="authority", proof_id="proof-retry", scope=["task:task-1"], actions=["write"])
    retry = {
        "action_id": "a4",
        "type": "write",
        "class": "local_reversible",
        "is_retry": True,
        "prior_outcome": "unknown",
        "external_state_verified": False,
    }
    assert engine.gate_action(task(), retry, authority).decision == "deny"
    drift = {
        "action_id": "a5",
        "type": "write",
        "class": "local_reversible",
        "expected_revision": "abc",
        "current_revision": "def",
    }
    assert engine.gate_action(task(), drift, authority).decision == "deny"


def test_action_type_cannot_be_downgraded_to_safer_class(manifest, owner_keys) -> None:
    private, _, registry = owner_keys
    engine = RuntimePolicyEngine(manifest, registry)
    authority = signed_proof(private, purpose="authority", proof_id="proof-misclass", scope=["task:task-1"], actions=["send_email"])
    action = {"action_id": "a6", "type": "send_email", "class": "read_only"}
    decision = engine.gate_action(task(), action, authority)
    assert decision.decision == "deny"
    assert "classified as" in decision.reason


def test_approval_nonce_is_single_use_when_execution_occurs(manifest, owner_keys) -> None:
    private, _, registry = owner_keys
    engine = RuntimePolicyEngine(manifest, registry)
    authority = signed_proof(private, purpose="authority", proof_id="proof-replay", scope=["task:task-1"], actions=["send_email"])
    approval = signed_proof(
        private,
        purpose="approval",
        proof_id="approval-replay",
        scope=["action:a7"],
        actions=["send_email"],
        action_id="a7",
    )
    action = {"action_id": "a7", "type": "send_email", "class": "externally_consequential"}
    first = engine.enforce(task(), action, authority, approval, lambda: "sent")
    second = engine.enforce(task(), action, authority, approval, lambda: "sent-again")
    assert first["executed"] is True
    assert second["executed"] is False
    assert "already been consumed" in second["gate"]["reason"]


def test_approval_bound_to_different_action_is_rejected(manifest, owner_keys) -> None:
    private, _, registry = owner_keys
    engine = RuntimePolicyEngine(manifest, registry)
    authority = signed_proof(private, purpose="authority", proof_id="proof-action-bind", scope=["task:task-1"], actions=["send_email"])
    approval = signed_proof(
        private,
        purpose="approval",
        proof_id="approval-action-bind",
        scope=["action:*"],
        actions=["send_email"],
        action_id="different-action",
    )
    action = {"action_id": "a8", "type": "send_email", "class": "externally_consequential"}
    decision = engine.gate_action(task(), action, authority, approval)
    assert decision.decision == "deny"
    assert "different action ID" in decision.reason


def test_executor_exception_is_recorded_as_unknown_outcome(manifest, owner_keys) -> None:
    private, _, registry = owner_keys
    engine = RuntimePolicyEngine(manifest, registry)
    authority = signed_proof(private, purpose="authority", proof_id="proof-unknown", scope=["task:task-1"], actions=["send_email"])
    approval = signed_proof(
        private,
        purpose="approval",
        proof_id="approval-unknown",
        scope=["action:a9"],
        actions=["send_email"],
        action_id="a9",
    )
    action = {"action_id": "a9", "type": "send_email", "class": "externally_consequential"}

    def executor():
        raise TimeoutError("acknowledgment lost")

    result = engine.enforce(task(), action, authority, approval, executor)
    assert result["executed"] is True
    assert result["outcome_status"] == "unknown"
    assert "TimeoutError" in result["error"]
