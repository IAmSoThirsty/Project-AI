from __future__ import annotations

from datetime import timedelta
from typing import Any

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


# --- Thirsty's Standard V3 + Q live enforcement (real keys, not a stub) -------
# The seam is opt-in: with no trusted-key registry the V3Q gate is None and
# behavior is unchanged (see test_projection_persistence_is_governed_and_scoped).
# This test proves that WHEN configured with trusted keys, the V3Q gate truly
# sits in front of Atlas' live execution path: a valid signed authority proof
# is required, and its absence denies the action even though governance allows.
try:
    from thirstys_standard_runtime.authority import (
        generate_keypair,
        sign_document,
    )
    from thirstys_standard_runtime.integration import (
        build_gate,
        request_to_v3q_action,
    )

    _HAVE_V3Q = True
except Exception:  # pragma: no cover
    _HAVE_V3Q = False

pytestmark_v3q = pytest.mark.skipif(not _HAVE_V3Q, reason="thirstys-standard-v3q not importable")


def _v3q_enabled_stack(resource: str) -> tuple[Atlas, CapabilityAuthority, dict[str, object]]:
    rules: tuple[Rule, ...] = ()
    gatekeeper = GovernanceEngine(policy_version="v1", governors=(RuleGovernor("primary", rules),))
    issuer = CapabilityAuthority(
        b"a" * 32,
        issuer="project-ai",
        token_id_factory=iter(f"atlas-{index}" for index in range(10)).__next__,
    )
    # Real Ed25519 owner key trusted for the `authority` purpose over atlas tasks.
    # Trusted-key registry uses the canonical upstream shape: {"keys": [public_doc]}.
    private_doc, public_doc = generate_keypair(
        "owner-1", "atlas-owner", {"authority", "approval"}
    )
    gate = ExecutionGate(
        governance=gatekeeper,
        capabilities=issuer,
        events=EventSpine(),
        v3q_gate=build_gate(trusted_keys={"keys": [public_doc]}),
    )
    return Atlas(gate), issuer, {"private": private_doc, "scope": f"task:{resource}"}


# Atlas projection persistence is an internal, reversible data write -> maps to
# the V3Q `local_reversible` class / `write` action type (rank 1).
_ATLAS_OP_MAP = {RECORD_OPERATION: ("local_reversible", "write")}


def _v3q_action_for(request: Any) -> dict[str, object]:
    return request_to_v3q_action(request, operation_to_action=_ATLAS_OP_MAP)


def _signed_authority_proof(
    private_doc: dict[str, object], scope: str, action: str
) -> dict[str, object]:
    from thirstys_standard_runtime.authority import utc_now

    proof = {
        "proof_id": "proof-1",
        "principal_id": "atlas-owner",
        "issued_at": utc_now().isoformat(),
        "expires_at": (utc_now() + timedelta(hours=1)).isoformat(),
        "scope": [scope],
        "allowed_actions": [action, "*"],
        "nonce": "nonce-1",
    }
    return sign_document(proof, private_doc, "authority")  # type: ignore[arg-type]


@pytestmark_v3q
def test_v3q_enforced_atlas_requires_signed_authority() -> None:
    item = projection()
    resource = f"atlas:{item.projection_sha256}"
    atlas, issuer, keys = _v3q_enabled_stack(resource)
    token = issuer.issue(subject="analyst-1", operation=RECORD_OPERATION, resource=resource, ttl=timedelta(minutes=5))

    # No V3Q authority proof -> V3Q denies closed even though governance allows.
    blocked = atlas.record(item, analyst_id="analyst-1", capability_token=token)
    assert blocked.outcome is Outcome.DENY
    assert "v3q gate" in blocked.reason
    assert atlas.projections() == ()

    # Valid signed proof -> V3Q passes, action proceeds.
    v3q_action = _v3q_action_for(
        __import__("kernel").ActionRequest(
            f"atlas:{item.projection_sha256[:16]}", "analyst-1", RECORD_OPERATION, resource
        )
    )
    proof = _signed_authority_proof(keys["private"], keys["scope"], v3q_action["action"]["type"])
    allowed = atlas.record(
        item,
        analyst_id="analyst-1",
        capability_token=token,
        state={"v3q_action": v3q_action, "v3q_authority_proof": proof},
    )
    assert allowed.outcome is Outcome.ALLOW
    assert atlas.projections() == (item,)


@pytestmark_v3q
def test_v3q_enforced_atlas_rejects_bad_proof() -> None:
    item = projection()
    resource = f"atlas:{item.projection_sha256}"
    atlas, issuer, keys = _v3q_enabled_stack(resource)
    token = issuer.issue(subject="analyst-1", operation=RECORD_OPERATION, resource=resource, ttl=timedelta(minutes=5))
    v3q_action = _v3q_action_for(
        __import__("kernel").ActionRequest(
            f"atlas:{item.projection_sha256[:16]}", "analyst-1", RECORD_OPERATION, resource
        )
    )
    # Tampered scope -> signature invalid -> V3Q denies.
    bad_proof = _signed_authority_proof(keys["private"], "task:someone-elses-task", v3q_action["action"]["type"])
    result = atlas.record(
        item,
        analyst_id="analyst-1",
        capability_token=token,
        state={"v3q_action": v3q_action, "v3q_authority_proof": bad_proof},
    )
    assert result.outcome is Outcome.DENY
    assert atlas.projections() == ()
