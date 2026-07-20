from __future__ import annotations

from dataclasses import dataclass

from waterfall_adapter import WaterfallAdapter

from capability import CapabilityAuthority
from execution import ExecutionGate
from governance import GovernanceEngine, RuleGovernor
from kernel import EventSpine, Outcome


@dataclass
class _Transport:
    calls: list[tuple[str, str, dict]]

    def execute(self, operation, resource, payload):
        self.calls.append((operation, resource, dict(payload)))
        return {"accepted": True, "operation": operation}


def _gate(capabilities: CapabilityAuthority) -> ExecutionGate:
    governance = GovernanceEngine(
        policy_version="v1",
        governors=(RuleGovernor("allow", ()),),
    )
    return ExecutionGate(
        governance=governance,
        capabilities=capabilities,
        events=EventSpine(),
    )


def test_missing_gate_denies_without_transport_call() -> None:
    transport = _Transport([])
    result = WaterfallAdapter(transport=transport).submit("vpn.connect", resource="vpn:primary")
    assert result.outcome is Outcome.DENY
    assert transport.calls == []


def test_unknown_operation_denies() -> None:
    result = WaterfallAdapter().submit("shell.exec", resource="host")
    assert result.outcome is Outcome.DENY
    assert "allow-listed" in result.reason


def test_missing_transport_denies_even_when_gate_is_present() -> None:
    capabilities = CapabilityAuthority(b"y" * 32, issuer="test")
    result = WaterfallAdapter(
        execution_gate=_gate(capabilities),
        capability_authority=capabilities,
    ).submit("kill_switch.trigger", resource="local")
    assert result.outcome is Outcome.DENY
    assert "transport" in result.reason


def test_allowed_operation_executes_only_after_gate_and_carries_evidence() -> None:
    capabilities = CapabilityAuthority(b"z" * 32, issuer="test")
    transport = _Transport([])
    result = WaterfallAdapter(
        execution_gate=_gate(capabilities),
        capability_authority=capabilities,
        transport=transport,
    ).submit(
        "vpn.connect",
        resource="vpn:primary",
        payload={"profile": "primary"},
    )
    assert result.outcome is Outcome.ALLOW
    assert result.governance_evidence_sha256
    assert result.event_hash
    assert transport.calls == [("vpn.connect", "vpn:primary", {"profile": "primary"})]
