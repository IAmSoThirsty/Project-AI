"""Cross-engine dispatcher canonical-gate integration tests.

Honest scope: proves the dispatcher routes every cascade through the real
ExecutionGate (governance decision + exact-scope one-use capability +
gated executor) with deny-by-default when the gate or capability
authority is missing, mismatched, or governance denies. Uses stub
simulation engines; does not exercise the real alien/ai/global/emp
engines or any HTTP surface.
"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from project_ai_api.integration import CrossEngineDispatcher

from capability import CapabilityAuthority
from execution import ExecutionGate
from governance import GovernanceEngine, Rule, RuleGovernor
from kernel import EventSpine, Outcome


class StubAlienEngine:
    """Records injected events; reports no alien control."""

    def __init__(self) -> None:
        self.injected: list[tuple[str, dict[str, Any]]] = []

    def observe(self) -> dict[str, Any]:
        return {"aliens": {"control_percentage": 0.0}}

    def inject_event(self, event_type: str, parameters: dict[str, Any]) -> str:
        self.injected.append((event_type, parameters))
        return f"evt-{len(self.injected)}"


def corrupted_ai_engine() -> SimpleNamespace:
    """AI engine stub whose corruption triggers exactly one cascade (rule 3)."""
    return SimpleNamespace(
        state=SimpleNamespace(
            corruption_level=0.9,
            infrastructure_dependency=0.5,
            human_agency_remaining=1.0,
            terminal_state=None,
            terminal_transition_snapshot=None,
            failure_count=0,
        )
    )


def allow_gate(authority: CapabilityAuthority) -> ExecutionGate:
    return ExecutionGate(
        governance=GovernanceEngine(
            policy_version="test-v1",
            governors=(RuleGovernor("primary", ()),),
        ),
        capabilities=authority,
        events=EventSpine(),
    )


def deny_gate(authority: CapabilityAuthority) -> ExecutionGate:
    rule = Rule("deny-all", lambda _request, _state: False, Outcome.DENY, "policy denies")
    return ExecutionGate(
        governance=GovernanceEngine(
            policy_version="test-v1",
            governors=(RuleGovernor("primary", (rule,)),),
        ),
        capabilities=authority,
        events=EventSpine(),
    )


def test_no_gate_denies_and_never_fires_engine() -> None:
    alien = StubAlienEngine()
    dispatcher = CrossEngineDispatcher(alien_engine=alien, ai_engine=corrupted_ai_engine())

    result = dispatcher.evaluate_tick(tick_number=1)

    assert result.cascades_detected == 1
    assert result.cascades_executed == 0
    assert result.cascades_rejected == 1
    assert alien.injected == []
    assert "denies by default" in (result.events[0].rejection_reason or "")


def test_gate_without_capability_authority_denies() -> None:
    alien = StubAlienEngine()
    authority = CapabilityAuthority(b"a" * 32, issuer="test")
    dispatcher = CrossEngineDispatcher(
        alien_engine=alien,
        ai_engine=corrupted_ai_engine(),
        execution_gate=allow_gate(authority),
    )

    result = dispatcher.evaluate_tick(tick_number=1)

    assert result.cascades_executed == 0
    assert result.cascades_rejected == 1
    assert alien.injected == []


def test_foreign_capability_authority_denies_and_never_fires_engine() -> None:
    """A token signed by a different secret must fail gate consumption."""
    alien = StubAlienEngine()
    gate_authority = CapabilityAuthority(b"a" * 32, issuer="test")
    foreign_authority = CapabilityAuthority(b"b" * 32, issuer="test")
    dispatcher = CrossEngineDispatcher(
        alien_engine=alien,
        ai_engine=corrupted_ai_engine(),
        execution_gate=allow_gate(gate_authority),
        capability_authority=foreign_authority,
    )

    result = dispatcher.evaluate_tick(tick_number=1)

    assert result.cascades_executed == 0
    assert result.cascades_rejected == 1
    assert alien.injected == []
    event = result.events[0]
    assert event.approved is False
    assert event.executed is False
    assert event.rejection_reason


def test_governance_deny_never_executes() -> None:
    alien = StubAlienEngine()
    authority = CapabilityAuthority(b"a" * 32, issuer="test")
    dispatcher = CrossEngineDispatcher(
        alien_engine=alien,
        ai_engine=corrupted_ai_engine(),
        execution_gate=deny_gate(authority),
        capability_authority=authority,
    )

    result = dispatcher.evaluate_tick(tick_number=1)

    assert result.cascades_executed == 0
    assert result.cascades_rejected == 1
    assert alien.injected == []
    assert "policy denies" in (result.events[0].rejection_reason or "")


def test_exact_scope_allow_executes_with_gate_evidence(tmp_path: Path) -> None:
    alien = StubAlienEngine()
    authority = CapabilityAuthority(b"a" * 32, issuer="test")
    audit_path = tmp_path / "cascades.jsonl"
    dispatcher = CrossEngineDispatcher(
        alien_engine=alien,
        ai_engine=corrupted_ai_engine(),
        execution_gate=allow_gate(authority),
        capability_authority=authority,
        audit_log_path=str(audit_path),
    )

    result = dispatcher.evaluate_tick(tick_number=7)

    assert result.cascades_detected == 1
    assert result.cascades_approved == 1
    assert result.cascades_executed == 1
    assert result.cascades_rejected == 0
    assert len(alien.injected) == 1
    assert alien.injected[0][0] == "ai_systems_compromised"

    event = result.events[0]
    assert event.approved is True
    assert event.executed is True
    assert event.result == {"event_id": "evt-1", "status": "injected"}
    assert event.governance_evidence_sha256 and len(event.governance_evidence_sha256) == 64
    assert event.event_hash and len(event.event_hash) == 64

    audit_record = json.loads(audit_path.read_text(encoding="utf-8").splitlines()[0])
    assert audit_record["executed"] is True
    assert audit_record["governance_evidence_sha256"] == event.governance_evidence_sha256
    assert audit_record["event_hash"] == event.event_hash

    summary = dispatcher.get_dispatch_summary()
    assert summary["authority_gate_available"] is True
    assert summary["executed"] == 1
