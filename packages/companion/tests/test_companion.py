from __future__ import annotations

from datetime import timedelta

import pytest

from capability import CapabilityAuthority
from companion import RESTORE_OPERATION, UPDATE_OPERATION, Companion
from execution import ExecutionGate
from governance import GovernanceEngine, Rule, RuleGovernor
from kernel import EventSpine, Outcome, StateSnapshot


def stack(*, allow: bool = True) -> tuple[Companion, CapabilityAuthority]:
    rules: tuple[Rule, ...] = (
        () if allow else (Rule("deny", lambda _request, _state: False, Outcome.DENY, "no"),)
    )
    governance = GovernanceEngine(
        policy_version="v1",
        governors=(RuleGovernor("primary", rules),),
    )
    capabilities = CapabilityAuthority(
        b"c" * 32,
        issuer="project-ai",
        token_id_factory=iter(f"cap-{index}" for index in range(10)).__next__,
    )
    gate = ExecutionGate(
        governance=governance,
        capabilities=capabilities,
        events=EventSpine(),
    )
    return Companion("companion-1", gate), capabilities


def issue(service: CapabilityAuthority, operation: str) -> str:
    return service.issue(
        subject="companion-1",
        operation=operation,
        resource="companion:companion-1",
        ttl=timedelta(minutes=5),
    )


def test_governed_update_and_restore() -> None:
    companion, capabilities = stack()
    initial = companion.snapshot()
    updated = companion.update_state(
        {"status": "bonded", "relationship_score": 0.5},
        expected_revision=0,
        capability_token=issue(capabilities, UPDATE_OPERATION),
    )
    assert updated.outcome is Outcome.ALLOW
    assert companion.snapshot().revision == 1
    assert companion.snapshot().values["status"] == "bonded"

    restored = companion.restore_state(
        initial,
        capability_token=issue(capabilities, RESTORE_OPERATION),
    )
    assert restored.outcome is Outcome.ALLOW
    assert companion.snapshot() == initial


def test_governance_denial_preserves_state() -> None:
    companion, capabilities = stack(allow=False)
    before = companion.snapshot()
    result = companion.update_state(
        {"status": "changed"},
        expected_revision=0,
        capability_token=issue(capabilities, UPDATE_OPERATION),
    )
    assert result.outcome is Outcome.DENY
    assert companion.snapshot() == before


def test_wrong_scope_and_revision_preserve_state() -> None:
    companion, capabilities = stack()
    wrong_scope = issue(capabilities, RESTORE_OPERATION)
    denied = companion.update_state(
        {"status": "changed"},
        expected_revision=0,
        capability_token=wrong_scope,
    )
    conflict = companion.update_state(
        {"status": "changed"},
        expected_revision=9,
        capability_token=issue(capabilities, UPDATE_OPERATION),
    )
    assert denied.outcome is Outcome.DENY
    assert conflict.outcome is Outcome.DENY
    assert companion.snapshot().revision == 0


def test_identity_and_snapshot_validation() -> None:
    companion, capabilities = stack()
    with pytest.raises(ValueError, match="immutable"):
        companion.update_state(
            {"companion_id": "other"},
            expected_revision=0,
            capability_token="unused",
        )
    snapshot = companion.snapshot()
    foreign = StateSnapshot(
        snapshot.revision,
        {**snapshot.values, "companion_id": "other"},
        snapshot.state_sha256,
    )
    with pytest.raises(ValueError, match="identity mismatch"):
        companion.restore_state(foreign, capability_token=issue(capabilities, RESTORE_OPERATION))
    with pytest.raises(ValueError, match="companion_id"):
        Companion("", companion._execution)
