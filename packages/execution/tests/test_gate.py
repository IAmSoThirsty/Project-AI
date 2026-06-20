from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from capability import CapabilityAuthority
from execution import ExecutionGate, submit_action
from governance import GovernanceEngine, GovernanceResult, Rule, RuleGovernor
from kernel import ActionRequest, EventSpine, JsonValue, Outcome, TrustedClock, verify_event_chain
from security import AppendOnlyAuditRelay, start_audit_relay

type JsonScalar = str | int | float | bool | None


def request() -> ActionRequest:
    return ActionRequest("a-1", "operator", "write", "record:1")


def governance(outcome: Outcome = Outcome.ALLOW) -> GovernanceEngine:
    rules: tuple[Rule, ...] = ()
    if outcome is not Outcome.ALLOW:
        rules = (Rule("decision", lambda _request, _state: False, outcome, "policy decision"),)
    return GovernanceEngine(policy_version="v1", governors=(RuleGovernor("primary", rules),))


def authority(clock: TrustedClock | None = None) -> CapabilityAuthority:
    return CapabilityAuthority(
        b"c" * 32,
        issuer="project-ai",
        clock=clock,
        token_id_factory=lambda: "cap-1",
    )


def token(service: CapabilityAuthority) -> str:
    return service.issue(
        subject="operator",
        operation="write",
        resource="record:1",
        ttl=timedelta(minutes=5),
    )


def test_allow_executes_once_and_records_valid_chain() -> None:
    capabilities = authority()
    events = EventSpine()
    gate = ExecutionGate(governance=governance(), capabilities=capabilities, events=events)
    calls: list[str] = []

    def execute(action: ActionRequest) -> JsonValue:
        calls.append(action.action_id)
        return {"changed": True}

    result = submit_action(
        gate,
        request(),
        capability_token=token(capabilities),
        executor=execute,
    )

    assert result.outcome is Outcome.ALLOW
    assert result.output == {"changed": True}
    assert calls == ["a-1"]
    assert verify_event_chain(events.events()).valid is True
    assert [event.event_type for event in events.events()] == [
        "execution.request_received",
        "execution.authorized",
        "execution.completed",
    ]


@pytest.mark.parametrize("outcome", [Outcome.DENY, Outcome.ESCALATE])
def test_non_allow_governance_never_executes_or_consumes(outcome: Outcome) -> None:
    capabilities = authority()
    issued = token(capabilities)
    calls: list[str] = []
    result = ExecutionGate(
        governance=governance(outcome),
        capabilities=capabilities,
        events=EventSpine(),
    ).submit_action(
        request(),
        capability_token=issued,
        executor=lambda action: calls.append(action.action_id),
    )
    assert result.outcome is outcome
    assert calls == []
    capabilities.consume(issued, subject="operator", operation="write", resource="record:1")


def test_missing_scope_and_replay_fail_closed_without_executor() -> None:
    capabilities = authority()
    gate = ExecutionGate(governance=governance(), capabilities=capabilities, events=EventSpine())
    calls: list[str] = []
    wrong = capabilities.issue(
        subject="operator",
        operation="read",
        resource="record:1",
        ttl=timedelta(minutes=5),
    )
    denied = gate.submit_action(
        request(),
        capability_token=wrong,
        executor=lambda action: calls.append(action.action_id),
    )
    issued = token(capabilities)
    gate.submit_action(request(), capability_token=issued, executor=lambda _action: "done")
    replayed = gate.submit_action(
        request(),
        capability_token=issued,
        executor=lambda action: calls.append(action.action_id),
    )
    assert denied.outcome is Outcome.DENY
    assert replayed.outcome is Outcome.DENY
    assert calls == []


def test_expired_token_and_executor_fault_fail_closed() -> None:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    moments = iter((now, now + timedelta(minutes=6)))
    capabilities = authority(TrustedClock(lambda: next(moments)))
    expired = token(capabilities)
    gate = ExecutionGate(governance=governance(), capabilities=capabilities, events=EventSpine())
    result = gate.submit_action(request(), capability_token=expired, executor=lambda _action: "no")
    assert result.outcome is Outcome.DENY

    live = authority()
    fault = ExecutionGate(
        governance=governance(), capabilities=live, events=EventSpine()
    ).submit_action(
        request(),
        capability_token=token(live),
        executor=lambda _action: (_ for _ in ()).throw(RuntimeError("fault")),
    )
    assert fault.outcome is Outcome.DENY
    assert fault.reason == "executor failed: RuntimeError"


def test_denial_relays_to_chimera_without_private_state(tmp_path: Path) -> None:
    relay_path = tmp_path / "chimera.jsonl"
    relay = start_audit_relay(relay_path)
    capabilities = authority()
    result = ExecutionGate(
        governance=governance(Outcome.DENY),
        capabilities=capabilities,
        events=EventSpine(),
        chimera_relay=relay,
    ).submit_action(request(), capability_token=token(capabilities), executor=lambda _action: "no")
    record = json.loads(relay_path.read_text(encoding="utf-8"))
    assert result.outcome is Outcome.DENY
    assert record["event"] == "chimera.governance_denial"
    assert record["action_id"] == "a-1"


def test_governance_and_relay_faults_stay_closed(tmp_path: Path) -> None:
    class FailingGovernance(GovernanceEngine):
        def decide(
            self,
            request: ActionRequest,
            state: Mapping[str, object] | None = None,
        ) -> GovernanceResult:
            del request, state
            raise RuntimeError("fault")

    class FailingRelay(AppendOnlyAuditRelay):
        def append(
            self,
            event: str,
            fields: Mapping[str, JsonScalar],
        ) -> dict[str, JsonScalar]:
            del event, fields
            raise OSError("disk fault")

    capabilities = authority()
    events = EventSpine()
    result = ExecutionGate(
        governance=FailingGovernance(policy_version="v1", governors=()),
        capabilities=capabilities,
        events=events,
        chimera_relay=FailingRelay(tmp_path / "unused.jsonl"),
    ).submit_action(request(), capability_token=token(capabilities), executor=lambda _action: "no")

    assert result.outcome is Outcome.DENY
    assert result.reason == "governance evaluation failed: RuntimeError"
    assert events.events()[-1].event_type == "execution.chimera_relay_failed"
