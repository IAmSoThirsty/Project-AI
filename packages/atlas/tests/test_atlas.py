from __future__ import annotations

from datetime import timedelta

import pytest

from atlas import (
    RECORD_OPERATION,
    SUBORDINATION_NOTICE,
    Atlas,
    Claim,
    ClaimType,
    Evidence,
    EvidenceTier,
    Projection,
    analyze,
)
from capability import CapabilityAuthority
from execution import ExecutionGate
from governance import GovernanceEngine, Rule, RuleGovernor
from kernel import EventSpine, Outcome


def stack(*, allow: bool = True) -> tuple[Atlas, CapabilityAuthority]:
    rules: tuple[Rule, ...] = (
        () if allow else (Rule("deny", lambda _request, _state: False, Outcome.DENY, "blocked"),)
    )
    gatekeeper = GovernanceEngine(
        policy_version="v1",
        governors=(RuleGovernor("primary", rules),),
    )
    authority = CapabilityAuthority(
        b"a" * 32,
        issuer="project-ai",
        token_id_factory=iter(f"atlas-{index}" for index in range(10)).__next__,
    )
    gate = ExecutionGate(
        governance=gatekeeper,
        capabilities=authority,
        events=EventSpine(),
    )
    return Atlas(gate), authority


def projection() -> Projection:
    claim = Claim("claim-1", "A measured indicator is increasing", ClaimType.FACTUAL)
    return analyze(
        claim,
        (Evidence("audited report", EvidenceTier.A, 0.9),),
        drivers={"indicator": 0.8},
    )


def test_analysis_is_deterministic_and_subordinate() -> None:
    claim = Claim("claim-1", "A measured indicator is increasing", ClaimType.FACTUAL)
    evidence = (Evidence("audited report", EvidenceTier.A, 0.9),)
    first = analyze(claim, evidence, drivers={"indicator": 0.8})
    second = analyze(claim, evidence, drivers={"indicator": 0.8})
    assert first == second
    assert first.subordination_notice == SUBORDINATION_NOTICE
    assert first.posterior == 0.72
    assert len(first.projection_sha256) == 64


def test_agency_and_simulation_penalties_are_fail_conservative() -> None:
    claim = Claim("claim-2", "An actor intends an outcome", ClaimType.AGENCY)
    low = (Evidence("secondary", EvidenceTier.D, 1.0),)
    agency = analyze(claim, low, drivers={"signal": 1.0})
    simulated = analyze(claim, low, drivers={"signal": 1.0}, stack="SS")
    assert agency.posterior == 0.2
    assert simulated.posterior == 0.0
    assert analyze(claim, (), drivers={}).posterior == 0.035


def test_projection_persistence_is_governed_and_scoped() -> None:
    atlas, authority = stack()
    item = projection()
    resource = f"atlas:{item.projection_sha256}"
    token = authority.issue(
        subject="analyst-1",
        operation=RECORD_OPERATION,
        resource=resource,
        ttl=timedelta(minutes=5),
    )
    result = atlas.record(item, analyst_id="analyst-1", capability_token=token)
    assert result.outcome is Outcome.ALLOW
    assert atlas.projections() == (item,)

    denied_atlas, denied_authority = stack(allow=False)
    denied_token = denied_authority.issue(
        subject="analyst-1",
        operation=RECORD_OPERATION,
        resource=resource,
        ttl=timedelta(minutes=5),
    )
    denied = denied_atlas.record(item, analyst_id="analyst-1", capability_token=denied_token)
    assert denied.outcome is Outcome.DENY
    assert denied_atlas.projections() == ()


def test_input_validation() -> None:
    with pytest.raises(ValueError, match="source"):
        Evidence("", EvidenceTier.A, 1.0)
    with pytest.raises(ValueError, match="confidence"):
        Evidence("x", EvidenceTier.A, 2.0)
    with pytest.raises(ValueError, match="claim ID"):
        Claim("", "x", ClaimType.FACTUAL)
    claim = Claim("x", "x", ClaimType.FACTUAL)
    with pytest.raises(ValueError, match="stack"):
        analyze(claim, (), drivers={}, stack="")
    with pytest.raises(ValueError, match="driver"):
        analyze(claim, (), drivers={"x": 2.0})
