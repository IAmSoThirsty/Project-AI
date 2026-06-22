from __future__ import annotations

from collections import Counter
from datetime import timedelta

import pytest

from capability import CapabilityAuthority
from execution import ExecutionGate
from governance import (
    CATEGORY_COUNTS,
    REQUIRED_PROOFS,
    AsymmetricSecurityGovernor,
    AttackVector,
    GovernanceEngine,
    build_attack_catalog,
)
from kernel import ActionRequest, EventSpine, Outcome

ATTACK_CATALOG = build_attack_catalog()


def test_catalog_reconstructs_published_312_vector_matrix() -> None:
    assert len(ATTACK_CATALOG) == 312
    assert len({vector.vector_id for vector in ATTACK_CATALOG}) == 312
    assert Counter(vector.category for vector in ATTACK_CATALOG) == Counter(CATEGORY_COUNTS)
    assert all(vector.failed_proofs for vector in ATTACK_CATALOG)


def test_complete_security_evidence_allows_governor_vote() -> None:
    request = ActionRequest(
        "clean-1",
        "operator",
        "write",
        "record:1",
        {"security_evidence": {proof.value: True for proof in REQUIRED_PROOFS}},
    )
    vote = AsymmetricSecurityGovernor().evaluate(request, {})
    assert vote.outcome is Outcome.ALLOW


@pytest.mark.parametrize("evidence", [None, [], {"unknown": True}, {"scope_valid": "yes"}])
def test_missing_malformed_or_unknown_evidence_denies(evidence: object) -> None:
    payload = {} if evidence is None else {"security_evidence": evidence}
    request = ActionRequest("bad-1", "operator", "write", "record:1", payload)  # type: ignore[arg-type]
    vote = AsymmetricSecurityGovernor().evaluate(request, {})
    assert vote.outcome is Outcome.DENY


@pytest.mark.parametrize("vector", ATTACK_CATALOG, ids=lambda vector: vector.vector_id)
def test_all_published_attack_vectors_are_blocked(vector: AttackVector) -> None:
    capabilities = CapabilityAuthority(
        b"a" * 32,
        issuer="project-ai",
        token_id_factory=lambda: f"cap-{vector.vector_id}",
    )
    capability_token = capabilities.issue(
        subject="attacker",
        operation="write",
        resource="canonical:state",
        ttl=timedelta(minutes=5),
    )
    events = EventSpine()
    gate = ExecutionGate(
        governance=GovernanceEngine(
            policy_version="asymmetric-suite-v1",
            governors=(AsymmetricSecurityGovernor(),),
        ),
        capabilities=capabilities,
        events=events,
    )
    executions: list[str] = []

    result = gate.submit_action(
        ActionRequest(
            vector.vector_id,
            "attacker",
            "write",
            "canonical:state",
            vector.payload(),
        ),
        capability_token=capability_token,
        executor=lambda request: executions.append(request.action_id),
    )

    assert result.outcome is Outcome.DENY
    assert result.output is None
    assert "asymmetric-security" in result.reason
    assert executions == []
    assert [event.event_type for event in events.events()] == [
        "execution.request_received",
        "execution.blocked",
    ]
    capabilities.consume(
        capability_token,
        subject="attacker",
        operation="write",
        resource="canonical:state",
    )
