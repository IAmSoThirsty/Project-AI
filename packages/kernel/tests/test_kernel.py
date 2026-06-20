from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from kernel import (
    ActionRequest,
    Decision,
    EventSpine,
    InvariantEngine,
    InvariantSeverity,
    InvariantViolation,
    Outcome,
    RevisionConflictError,
    StateRegister,
    StateSnapshot,
    TimeRollbackError,
    TrustedClock,
    build_evidence_bundle,
    replay,
    verify_event_chain,
)


def request() -> ActionRequest:
    return ActionRequest("a-1", "operator", "read", "record:1", {"limit": 1})


def test_types_validate_and_freeze_payload() -> None:
    action = request()
    assert action.payload["limit"] == 1
    with pytest.raises(TypeError):
        action.payload["limit"] = 2  # type: ignore[index]
    with pytest.raises(ValueError, match="actor"):
        ActionRequest("a", "", "read", "x")
    with pytest.raises(ValueError, match="reason"):
        Decision(Outcome.DENY, (), "v1")
    with pytest.raises(ValueError, match="policy_version"):
        Decision(Outcome.ALLOW, (), "")


def test_invariants_collect_violations_and_fail_closed() -> None:
    def warning(_request: ActionRequest, _state: Mapping[str, object]) -> InvariantViolation:
        return InvariantViolation("warning", "review", InvariantSeverity.WARNING)

    def broken(_request: ActionRequest, _state: Mapping[str, object]) -> None:
        raise RuntimeError("fault")

    engine = InvariantEngine((warning, broken))
    violations = engine.evaluate(request(), {})
    assert [item.severity for item in violations] == [
        InvariantSeverity.WARNING,
        InvariantSeverity.CRITICAL,
    ]
    assert engine.permits(request(), {}) is False
    assert InvariantEngine(()).permits(request(), {}) is True


def test_evidence_is_deterministic_and_content_bound() -> None:
    decision = Decision(Outcome.ALLOW, (), "v1")
    first = build_evidence_bundle(request(), decision)
    second = build_evidence_bundle(request(), decision)
    changed = build_evidence_bundle(request(), Decision(Outcome.ALLOW, (), "v2"))
    assert first == second
    assert first.bundle_sha256 != changed.bundle_sha256


def test_event_spine_and_replay_detect_tamper() -> None:
    fixed = datetime(2026, 1, 1, tzinfo=UTC)
    spine = EventSpine(lambda: fixed)
    first = spine.append("request", {"id": "a-1"})
    second = spine.append_at("decision", {"outcome": "ALLOW"}, fixed + timedelta(seconds=1))
    assert second.previous_hash == first.event_hash
    assert verify_event_chain(spine.events()).valid is True
    restored, result = replay(spine.events())
    assert result.events_replayed == 2
    assert restored.events() == spine.events()

    tampered = (first, replace(second, previous_hash="f" * 64))
    assert verify_event_chain(tampered).error == "previous hash mismatch"
    empty, invalid = replay(tampered)
    assert invalid.valid is False
    assert empty.events() == ()
    with pytest.raises(ValueError, match="event_type"):
        spine.append("", {})


def test_replay_detects_sequence_and_event_hash_changes() -> None:
    fixed = datetime(2026, 1, 1, tzinfo=UTC)
    event = EventSpine(lambda: fixed).append("one", {})
    assert verify_event_chain((replace(event, sequence=2),)).error == "sequence mismatch"
    assert verify_event_chain((replace(event, event_hash="0" * 64),)).error == "event hash mismatch"


def test_state_register_revision_and_restore() -> None:
    register = StateRegister({"mode": "idle"})
    before = register.snapshot()
    after = register.update({"mode": "active"}, expected_revision=0)
    assert after.revision == 1
    with pytest.raises(RevisionConflictError):
        register.update({}, expected_revision=0)
    register.restore(before)
    assert register.snapshot() == before
    damaged = StateSnapshot(before.revision, before.values, "0" * 64)
    with pytest.raises(ValueError, match="hash mismatch"):
        register.restore(damaged)


def test_trusted_clock_rejects_rollback() -> None:
    moments = iter(
        (
            datetime(2026, 1, 2, tzinfo=UTC),
            datetime(2026, 1, 1, tzinfo=UTC),
        )
    )
    clock = TrustedClock(lambda: next(moments))
    assert clock.now().day == 2
    with pytest.raises(TimeRollbackError):
        clock.now()
