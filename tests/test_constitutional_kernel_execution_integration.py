"""Integration tests for constitutional kernel denial through ExecutionGate."""

from __future__ import annotations

from datetime import timedelta

from capability import CapabilityAuthority
from execution import ExecutionGate
from governance import ConstitutionalKernel, GovernanceEngine, RuleGovernor
from kernel import ActionRequest, EventSpine, InvariantEngine, Outcome


def test_constitutional_kernel_blocks_execution_before_capability_consumption() -> None:
    request = ActionRequest("a-constitutional-exec", "operator", "simulate", "atlas:projection")
    capabilities = CapabilityAuthority(
        b"c" * 32,
        issuer="project-ai",
        token_id_factory=lambda: "cap-constitutional",
    )
    token = capabilities.issue(
        subject="operator",
        operation="simulate",
        resource="atlas:projection",
        ttl=timedelta(minutes=5),
    )
    events = EventSpine()
    governance = GovernanceEngine(
        policy_version="constitutional-v1",
        governors=(RuleGovernor("primary", ()),),
        invariants=InvariantEngine((ConstitutionalKernel(),)),
    )
    calls: list[str] = []
    result = ExecutionGate(
        governance=governance,
        capabilities=capabilities,
        events=events,
    ).submit_action(
        request,
        capability_token=token,
        executor=lambda action: calls.append(action.action_id),
        state={"stack": "RS", "metadata": {"source": "sludge_sandbox"}},
    )

    assert result.outcome is Outcome.DENY
    assert "sludge_to_rs_blocked" in result.reason
    assert calls == []
    capabilities.consume(
        token,
        subject="operator",
        operation="simulate",
        resource="atlas:projection",
    )
    assert [event.event_type for event in events.events()] == [
        "execution.request_received",
        "execution.blocked",
    ]
