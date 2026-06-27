"""Integration tests for atlas.audit + Atlas service (Phase J2.2.2).

Per Thirstys standards: production-ready integration tests proving that
every Atlas decision emits an audit event with full rationale. This
implements the user's mission:

> "This system needs to explain, prove, replay why reality was allowed
> to continue."

After these tests pass, the audit trail becomes the **explanation
chain** that makes every allow/deny decision auditable.
"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pytest

from atlas import (
    Atlas,
    AuditCategory,
    AuditLevel,
    AuditTrail,
    Claim,
    ClaimType,
    Evidence,
    EvidenceTier,
    JsonlStorage,
    analyze,
)
from capability import CapabilityAuthority
from execution import ExecutionGate
from governance import GovernanceEngine, Rule, RuleGovernor
from kernel import EventSpine
def _make_authority_and_gate(
    *, allow: bool = True
) -> tuple[CapabilityAuthority, ExecutionGate]:
    """Create a fresh capability authority + execution gate for tests."""
    rules: tuple[object, ...] = (
        ()
        if allow
        else (
            Rule(
                "deny",
                lambda _request, _state: False,
                __import__("kernel", fromlist=["Outcome"]).Outcome.DENY,
                "blocked by test",
            ),
        )
    )
    gatekeeper = GovernanceEngine(
        policy_version="v1",
        governors=(RuleGovernor("primary", rules),),
    )
    authority = CapabilityAuthority(
        b"a" * 32,
        issuer="project-ai",
        token_id_factory=iter(f"atlas-int-{index}" for index in range(20)).__next__,
    )
    gate = ExecutionGate(
        governance=gatekeeper,
        capabilities=authority,
        events=EventSpine(),
    )
    return authority, gate


def _make_claim_evidence() -> tuple[Claim, tuple[Evidence, ...], dict[str, float]]:
    return (
        Claim(
            claim_id="claim-int-1",
            statement="integration test claim",
            claim_type=ClaimType.PREDICTIVE,
        ),
        (
            Evidence(tier=EvidenceTier.A, confidence=0.95, source="primary"),
            Evidence(tier=EvidenceTier.B, confidence=0.80, source="secondary"),
        ),
        {"d1": 0.6, "d2": 0.8, "d3": 0.4},
    )


# ---------------------------------------------------------------------------
# Atlas + AuditTrail wiring
# ---------------------------------------------------------------------------


def test_atlas_attach_audit_trail() -> None:
    """Atlas can be initialized with an audit_trail."""
    _, gate = _make_authority_and_gate()
    trail = AuditTrail()
    Atlas(gate, audit_trail=trail)
    # No projection yet, so trail is empty
    assert len(trail) == 0


def test_atlas_attach_audit_trail_method() -> None:
    """Atlas.attach_audit_trail() attaches after construction."""
    _, gate = _make_authority_and_gate()
    atlas = Atlas(gate)
    trail = AuditTrail()
    atlas.attach_audit_trail(trail)
    # Subsequent record() should use the trail
    claim, evidence, drivers = _make_claim_evidence()
    projection = analyze(claim, evidence, drivers=drivers)

    authority = CapabilityAuthority(
        b"a" * 32,
        issuer="project-ai",
        token_id_factory=iter(f"atlas-int-{i}" for i in range(20)).__next__,
    )
    token = authority.issue(
        subject="analyst-1",
        operation="atlas.projection.record",
        resource=f"atlas:{projection.projection_sha256}",
        ttl=timedelta(minutes=5),
    )
    atlas.record(projection, analyst_id="analyst-1", capability_token=token)
    assert len(trail) == 1


def test_attach_audit_trail_validates_type() -> None:
    _, gate = _make_authority_and_gate()
    atlas = Atlas(gate)
    with pytest.raises(TypeError, match="AuditTrail"):
        atlas.attach_audit_trail("not a trail")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Allow path: trail records ALLOW event
# ---------------------------------------------------------------------------


def test_record_allowed_emits_audit_event() -> None:
    authority, gate = _make_authority_and_gate(allow=True)
    trail = AuditTrail()
    atlas = Atlas(gate, audit_trail=trail)
    claim, evidence, drivers = _make_claim_evidence()
    projection = analyze(claim, evidence, drivers=drivers)

    token = authority.issue(
        subject="analyst-allow",
        operation="atlas.projection.record",
        resource=f"atlas:{projection.projection_sha256}",
        ttl=timedelta(minutes=5),
    )
    atlas.record(projection, analyst_id="analyst-allow", capability_token=token)

    # Trail now has 1 event explaining why reality was allowed to continue
    assert len(trail) == 1
    event = trail.events[0]
    assert event.actor == "analyst-allow"
    assert event.action == "atlas.projection.record"
    assert event.resource == f"atlas:{projection.projection_sha256}"
    assert event.outcome == "ALLOW"
    assert event.level == AuditLevel.STANDARD
    assert event.category == AuditCategory.OPERATION
    assert "allowed" in event.rationale.lower()
    assert ("claim_id", projection.claim_id) in event.evidence
    assert ("projection_sha256", projection.projection_sha256) in event.evidence

    # Hash chain is valid
    v = trail.verify_chain()
    assert v.is_valid


# ---------------------------------------------------------------------------
# Deny path: trail records DENY event
# ---------------------------------------------------------------------------


def test_record_denied_emits_audit_event() -> None:
    authority, gate = _make_authority_and_gate(allow=False)
    trail = AuditTrail()
    atlas = Atlas(gate, audit_trail=trail)
    claim, evidence, drivers = _make_claim_evidence()
    projection = analyze(claim, evidence, drivers=drivers)

    token = authority.issue(
        subject="analyst-deny",
        operation="atlas.projection.record",
        resource=f"atlas:{projection.projection_sha256}",
        ttl=timedelta(minutes=5),
    )
    atlas.record(projection, analyst_id="analyst-deny", capability_token=token)

    # Trail records the denial
    assert len(trail) == 1
    event = trail.events[0]
    assert event.actor == "analyst-deny"
    assert event.outcome == "DENY"
    assert event.level == AuditLevel.HIGH_PRIORITY
    assert "denied" in event.rationale.lower()

    # Verify chain
    v = trail.verify_chain()
    assert v.is_valid


# ---------------------------------------------------------------------------
# Multiple records produce a chain
# ---------------------------------------------------------------------------


def test_multiple_records_produce_chain() -> None:
    authority, gate = _make_authority_and_gate(allow=True)
    trail = AuditTrail()
    atlas = Atlas(gate, audit_trail=trail)

    for i in range(3):
        claim = Claim(f"c{i}", f"claim {i}", ClaimType.PREDICTIVE)
        evidence = (Evidence(f"src-{i}", EvidenceTier.A, 0.9),)
        drivers = {"d": 0.5 + i * 0.1}
        projection = analyze(claim, evidence, drivers=drivers)

        token = authority.issue(
            subject=f"analyst-{i}",
            operation="atlas.projection.record",
            resource=f"atlas:{projection.projection_sha256}",
            ttl=timedelta(minutes=5),
        )
        atlas.record(projection, analyst_id=f"analyst-{i}", capability_token=token)

    assert len(trail) == 3
    v = trail.verify_chain()
    assert v.is_valid
    assert v.events_checked == 3
    # Sequence numbers are monotonic
    assert [e.sequence for e in trail.events] == [0, 1, 2]


# ---------------------------------------------------------------------------
# JSONL persistence end-to-end
# ---------------------------------------------------------------------------


def test_audit_trail_persists_to_jsonl(tmp_path: Path) -> None:
    """Audit trail persists across save + reload."""
    p = tmp_path / "audit.jsonl"
    storage = JsonlStorage(p)
    authority, gate = _make_authority_and_gate(allow=True)
    trail = AuditTrail(storage=storage)
    atlas = Atlas(gate, audit_trail=trail)

    claim, evidence, drivers = _make_claim_evidence()
    projection = analyze(claim, evidence, drivers=drivers)
    token = authority.issue(
        subject="persisted",
        operation="atlas.projection.record",
        resource=f"atlas:{projection.projection_sha256}",
        ttl=timedelta(minutes=5),
    )
    atlas.record(projection, analyst_id="persisted", capability_token=token)

    # Reload from disk
    trail2 = AuditTrail.load(p)
    assert len(trail2) == 1
    v = trail2.verify_chain()
    assert v.is_valid


# ---------------------------------------------------------------------------
# Replay reconstructs decision sequence
# ---------------------------------------------------------------------------


def test_replay_reconstructs_decisions() -> None:
    """Replay walks events in order, reconstructing what happened."""
    authority, gate = _make_authority_and_gate(allow=True)
    trail = AuditTrail()
    atlas = Atlas(gate, audit_trail=trail)

    # Mix of allow and deny
    claims_data = [
        ("c1", "first", 0.5),
        ("c2", "second", 0.7),
    ]
    for cid, _stmt, dv in claims_data:
        claim = Claim(cid, _stmt, ClaimType.PREDICTIVE)
        evidence = (Evidence("src", EvidenceTier.A, 0.9),)
        projection = analyze(claim, evidence, drivers={"x": dv})
        token = authority.issue(
            subject=f"a-{cid}",
            operation="atlas.projection.record",
            resource=f"atlas:{projection.projection_sha256}",
            ttl=timedelta(minutes=5),
        )
        atlas.record(projection, analyst_id=f"a-{cid}", capability_token=token)

    # Replay and capture
    replayed: list[tuple[int, str, str]] = []

    def show(event: object) -> None:
        replayed.append((event.sequence, event.actor, event.outcome))  # type: ignore[attr-defined]

    n = trail.replay(show)
    assert n == 2
    assert replayed == [
        (0, "a-c1", "ALLOW"),
        (1, "a-c2", "ALLOW"),
    ]


# ---------------------------------------------------------------------------
# Atlas without audit_trail still works (backward compat)
# ---------------------------------------------------------------------------


def test_atlas_without_audit_trail_works() -> None:
    """Backward compat: Atlas() without audit_trail parameter works as before."""
    authority, gate = _make_authority_and_gate(allow=True)
    atlas = Atlas(gate)  # no audit_trail
    claim, evidence, drivers = _make_claim_evidence()
    projection = analyze(claim, evidence, drivers=drivers)
    token = authority.issue(
        subject="no-trail",
        operation="atlas.projection.record",
        resource=f"atlas:{projection.projection_sha256}",
        ttl=timedelta(minutes=5),
    )
    result = atlas.record(projection, analyst_id="no-trail", capability_token=token)
    assert result.outcome.value == "ALLOW"


# ---------------------------------------------------------------------------
# Subordination notice in audit events
# ---------------------------------------------------------------------------


def test_audit_events_carry_subordination_notice() -> None:
    """Every audit event includes the canonical subordination notice."""
    authority, gate = _make_authority_and_gate(allow=True)
    trail = AuditTrail()
    atlas = Atlas(gate, audit_trail=trail)
    claim, evidence, drivers = _make_claim_evidence()
    projection = analyze(claim, evidence, drivers=drivers)
    token = authority.issue(
        subject="subord",
        operation="atlas.projection.record",
        resource=f"atlas:{projection.projection_sha256}",
        ttl=timedelta(minutes=5),
    )
    atlas.record(projection, analyst_id="subord", capability_token=token)

    from atlas import SUBORDINATION_NOTICE

    for event in trail.events:
        assert event.subordination_notice == SUBORDINATION_NOTICE


# ---------------------------------------------------------------------------
# Mission statement: explain, prove, replay
# ---------------------------------------------------------------------------


def test_mission_explain() -> None:
    """The audit trail EXPLAINS why reality was allowed to continue.

    Each event carries a rationale string that documents the decision.
    """
    authority, gate = _make_authority_and_gate(allow=True)
    trail = AuditTrail()
    atlas = Atlas(gate, audit_trail=trail)
    claim, evidence, drivers = _make_claim_evidence()
    projection = analyze(claim, evidence, drivers=drivers)
    token = authority.issue(
        subject="explain",
        operation="atlas.projection.record",
        resource=f"atlas:{projection.projection_sha256}",
        ttl=timedelta(minutes=5),
    )
    atlas.record(projection, analyst_id="explain", capability_token=token)

    event = trail.events[0]
    # Rationale explains what happened
    assert event.rationale != ""
    assert event.actor != ""
    assert event.action != ""
    assert event.outcome in ("ALLOW", "DENY")
    # Evidence carries supporting context
    assert len(event.evidence) > 0


def test_mission_prove() -> None:
    """The audit trail PROVES integrity via hash chain.

    verify_chain() returns is_valid=True iff the chain is intact.
    """
    authority, gate = _make_authority_and_gate(allow=True)
    trail = AuditTrail()
    atlas = Atlas(gate, audit_trail=trail)
    claim, evidence, drivers = _make_claim_evidence()
    projection = analyze(claim, evidence, drivers=drivers)
    token = authority.issue(
        subject="prove",
        operation="atlas.projection.record",
        resource=f"atlas:{projection.projection_sha256}",
        ttl=timedelta(minutes=5),
    )
    atlas.record(projection, analyst_id="prove", capability_token=token)

    v = trail.verify_chain()
    assert v.is_valid
    assert v.events_checked == 1
    assert v.issues == ()


def test_mission_replay() -> None:
    """The audit trail REPLAYS the decision sequence via callback."""
    authority, gate = _make_authority_and_gate(allow=True)
    trail = AuditTrail()
    atlas = Atlas(gate, audit_trail=trail)

    # Make 5 decisions
    for i in range(5):
        claim = Claim(f"replay-{i}", "x", ClaimType.PREDICTIVE)
        evidence = (Evidence("s", EvidenceTier.A, 0.9),)
        projection = analyze(claim, evidence, drivers={"x": 0.5})
        token = authority.issue(
            subject=f"replay-{i}",
            operation="atlas.projection.record",
            resource=f"atlas:{projection.projection_sha256}",
            ttl=timedelta(minutes=5),
        )
        atlas.record(projection, analyst_id=f"replay-{i}", capability_token=token)

    # Replay
    seen: list[int] = []

    def cb(event: object) -> None:
        seen.append(event.sequence)  # type: ignore[attr-defined]

    n = trail.replay(cb)
    assert n == 5
    assert seen == [0, 1, 2, 3, 4]


def test_mission_tamper_detection() -> None:
    """Modifying any audit event invalidates the chain — proving integrity."""
    authority, gate = _make_authority_and_gate(allow=True)
    trail = AuditTrail()
    atlas = Atlas(gate, audit_trail=trail)
    claim, evidence, drivers = _make_claim_evidence()
    projection = analyze(claim, evidence, drivers=drivers)
    token = authority.issue(
        subject="tamper-test",
        operation="atlas.projection.record",
        resource=f"atlas:{projection.projection_sha256}",
        ttl=timedelta(minutes=5),
    )
    atlas.record(projection, analyst_id="tamper-test", capability_token=token)

    # Tamper
    from atlas import AuditEvent

    e = trail.events[0]
    trail._events[0] = AuditEvent(
        sequence=e.sequence,
        timestamp=e.timestamp,
        level=e.level,
        category=e.category,
        actor="TAMPERED",
        action=e.action,
        resource=e.resource,
        outcome=e.outcome,
        rationale=e.rationale,
        evidence=e.evidence,
        prev_hash=e.prev_hash,
        record_hash=e.record_hash,
    )
    v = trail.verify_chain()
    assert not v.is_valid
    assert len(v.issues) > 0


# ---------------------------------------------------------------------------
# Pre-existing tests still pass (regression check)
# ---------------------------------------------------------------------------


def test_pre_existing_atlas_api_unchanged() -> None:
    """Atlas() without audit_trail still works as it did before J2.2."""
    from atlas import Atlas as AtlasOriginal

    _, gate = _make_authority_and_gate()
    # No audit_trail kwarg
    atlas = AtlasOriginal(gate)
    assert hasattr(atlas, "record")
    assert hasattr(atlas, "projections")
    assert not hasattr(atlas, "_audit_trail") or atlas._audit_trail is None
