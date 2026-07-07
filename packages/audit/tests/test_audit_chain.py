"""Tests for the audit log chain (Phase B recovery).

These tests verify the audit log in isolation. Integration
with ``canonical`` (IdentityRegistry, CapabilityRegistry,
StaticGovernancePolicy) is covered by the ``packages/canonical``
tests; integration with the governance kernel
(``submit_action``) is covered by the ``packages/governance``
tests.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from audit import (
    GENESIS_HASH,
    AuditEvent,
    AuditLog,
    AuditVerification,
    AuditWriteError,
    FileAuditLog,
)

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def _make_event(decision_id: str, action: str, reason: str) -> AuditEvent:
    return AuditEvent(
        decision_id=decision_id,
        actor_id="actor-1",
        action=action,
        resource="resource-1",
        result="allow",
        reason=reason,
        timestamp=NOW.isoformat(),
        previous_hash=GENESIS_HASH if decision_id == "dec-1" else "",
        event_hash="",
        event_type="decision",
    )


def test_genesis_hash_is_64_zeros() -> None:
    """The genesis hash anchor is exactly 64 zero characters."""
    assert GENESIS_HASH == "0" * 64
    assert len(GENESIS_HASH) == 64


def test_audit_event_hash_payload_excludes_event_hash() -> None:
    """The hash payload must not include event_hash itself
    (else it would be self-referential)."""
    event = _make_event("dec-1", "test.echo", "first event")
    event.event_hash = "computed_by_append"
    payload = event.hash_payload()
    assert "event_hash" not in payload


def test_audit_event_round_trip_through_record() -> None:
    """to_record() includes event_hash; from_record() recreates it."""
    log = AuditLog()
    written = log.append_event(
        decision_id="dec-1",
        actor_id="actor-1",
        action="test.echo",
        resource="resource-1",
        result="allow",
        reason="round trip",
        event_type="decision",
        timestamp=NOW,
    )
    record = written.to_record()
    assert "event_hash" in record
    rebuilt = AuditEvent.from_record(record)
    assert rebuilt == written


def test_audit_log_starts_empty() -> None:
    """A new AuditLog has no events."""
    log = AuditLog()
    assert log.events == []
    assert log.verify_chain().valid is True


def test_audit_log_first_event_uses_genesis_previous_hash() -> None:
    """The first event's previous_hash is GENESIS_HASH."""
    log = AuditLog()
    event = log.append_event(
        decision_id="dec-1",
        actor_id="actor-1",
        action="test.echo",
        resource="resource-1",
        result="allow",
        reason="first",
        event_type="decision",
        timestamp=NOW,
    )
    assert event.previous_hash == GENESIS_HASH
    assert event.event_hash != ""


def test_audit_log_chain_links_events() -> None:
    """Each event's previous_hash equals the prior event's event_hash."""
    log = AuditLog()
    e1 = log.append_event(
        decision_id="dec-1",
        actor_id="a",
        action="act",
        resource="r",
        result="allow",
        reason="r1",
        event_type="decision",
        timestamp=NOW,
    )
    e2 = log.append_event(
        decision_id="dec-2",
        actor_id="a",
        action="act",
        resource="r",
        result="allow",
        reason="r2",
        event_type="decision",
        timestamp=NOW,
    )
    e3 = log.append_event(
        decision_id="dec-3",
        actor_id="a",
        action="act",
        resource="r",
        result="allow",
        reason="r3",
        event_type="decision",
        timestamp=NOW,
    )
    assert e2.previous_hash == e1.event_hash
    assert e3.previous_hash == e2.event_hash
    assert log.verify_chain().valid is True


def test_audit_chain_tampering_detected() -> None:
    """Modifying any past event invalidates the chain."""
    log = AuditLog()
    log.append_event(
        decision_id="dec-1",
        actor_id="a",
        action="act",
        resource="r",
        result="allow",
        reason="original",
        event_type="decision",
        timestamp=NOW,
    )
    log.append_event(
        decision_id="dec-2",
        actor_id="a",
        action="act",
        resource="r",
        result="allow",
        reason="r2",
        event_type="decision",
        timestamp=NOW,
    )
    # Tamper with the first event's reason (which is part of the hash)
    log.events[0].reason = "TAMPERED"
    verification = log.verify_chain()
    assert verification.valid is False
    assert "hash mismatch" in verification.reason


def test_audit_chain_breaks_on_previous_hash_tampering() -> None:
    """Modifying an event's previous_hash field also invalidates the chain."""
    log = AuditLog()
    log.append_event(
        decision_id="dec-1",
        actor_id="a",
        action="act",
        resource="r",
        result="allow",
        reason="r1",
        event_type="decision",
        timestamp=NOW,
    )
    log.append_event(
        decision_id="dec-2",
        actor_id="a",
        action="act",
        resource="r",
        result="allow",
        reason="r2",
        event_type="decision",
        timestamp=NOW,
    )
    # Tamper with the second event's previous_hash
    log.events[1].previous_hash = "0" * 64
    verification = log.verify_chain()
    assert verification.valid is False
    assert "previous hash mismatch" in verification.reason


def test_file_audit_log_persists_across_reload(tmp_path: Path) -> None:
    """FileAuditLog writes JSONL and reloads to the same state."""
    path = tmp_path / "audit.jsonl"
    log = FileAuditLog(path)
    log.append_event(
        decision_id="dec-1",
        actor_id="a",
        action="act",
        resource="r",
        result="allow",
        reason="persisted",
        event_type="decision",
        timestamp=NOW,
    )
    log.append_event(
        decision_id="dec-2",
        actor_id="a",
        action="act",
        resource="r",
        result="deny",
        reason="rejected",
        event_type="decision",
        timestamp=NOW,
    )
    reloaded = FileAuditLog(path)
    assert len(reloaded.events) == 2
    assert reloaded.verify_chain().valid is True
    assert reloaded.events[0].decision_id == "dec-1"
    assert reloaded.events[1].result == "deny"


def test_file_audit_log_tampering_blocks_reload(tmp_path: Path) -> None:
    """FileAuditLog raises AuditWriteError on tamper detection at load."""
    path = tmp_path / "audit.jsonl"
    log = FileAuditLog(path)
    log.append_event(
        decision_id="dec-1",
        actor_id="a",
        action="act",
        resource="r",
        result="allow",
        reason="execution completed",
        event_type="execution",
        timestamp=NOW,
    )
    # Tamper with the file
    content = path.read_text(encoding="utf-8")
    path.write_text(
        content.replace("execution completed", "tampered execution", 1),
        encoding="utf-8",
    )
    with pytest.raises(AuditWriteError, match="audit chain invalid on load"):
        FileAuditLog(path)


def test_file_audit_log_rolls_back_on_write_failure(tmp_path: Path) -> None:
    """If a write fails, the in-memory state is rolled back."""
    path = tmp_path / "audit.jsonl"
    log = FileAuditLog(path)
    log.append_event(
        decision_id="dec-1",
        actor_id="a",
        action="act",
        resource="r",
        result="allow",
        reason="r1",
        event_type="decision",
        timestamp=NOW,
    )
    # Make the path un-writable by replacing it with a directory
    path.unlink()
    path.mkdir()
    with pytest.raises(AuditWriteError, match="audit event write failed"):
        log.append_event(
            decision_id="dec-2",
            actor_id="a",
            action="act",
            resource="r",
            result="allow",
            reason="r2",
            event_type="decision",
            timestamp=NOW,
        )
    # The failed event was rolled back; the in-memory state matches the file
    assert len(log.events) == 1


def test_audit_log_with_no_events_verifies_as_valid() -> None:
    """An empty chain is trivially valid (no events to break)."""
    log = AuditLog()
    verification = log.verify_chain()
    assert verification == AuditVerification(True, "audit chain valid")
