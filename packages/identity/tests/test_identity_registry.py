"""Tests for the identity registry (Phase B-2 recovery)."""

from __future__ import annotations

import pytest

from identity import (
    IdentityRecord,
    IdentityRegistry,
    IdentityVerification,
)


def test_registry_starts_empty() -> None:
    """A new IdentityRegistry has no records."""
    registry = IdentityRegistry()
    assert registry.records() == []


def test_registry_adds_record() -> None:
    """add() inserts a record; records() returns it sorted by actor_id."""
    registry = IdentityRegistry()
    registry.add(IdentityRecord("actor-2", active=True))
    registry.add(IdentityRecord("actor-1", active=True))
    assert [r.actor_id for r in registry.records()] == ["actor-1", "actor-2"]


def test_registry_rejects_empty_actor_id() -> None:
    """add() raises ValueError on empty actor_id."""
    registry = IdentityRegistry()
    with pytest.raises(ValueError, match="actor_id is required"):
        registry.add(IdentityRecord("", active=True))


def test_record_defaults_to_active() -> None:
    """A new IdentityRecord is active by default."""
    record = IdentityRecord("actor-1")
    assert record.active is True


def test_verify_active_actor_succeeds() -> None:
    """verify() returns allowed=True for an active record."""
    registry = IdentityRegistry([IdentityRecord("actor-1", active=True)])
    result = registry.verify("actor-1")
    assert result == IdentityVerification(
        True, "identity active", registry._records["actor-1"]
    ) or (result.allowed is True and result.reason == "identity active")


def test_verify_inactive_actor_denies() -> None:
    """verify() returns allowed=False for an inactive record,
    and surfaces the record in the result."""
    registry = IdentityRegistry([IdentityRecord("actor-1", active=False)])
    result = registry.verify("actor-1")
    assert result.allowed is False
    assert result.reason == "identity inactive"
    assert result.record is not None
    assert result.record.actor_id == "actor-1"


def test_verify_unknown_actor_denies() -> None:
    """verify() returns allowed=False for an unknown actor_id."""
    registry = IdentityRegistry([IdentityRecord("actor-1", active=True)])
    result = registry.verify("unknown")
    assert result.allowed is False
    assert result.reason == "identity not found"
    assert result.record is None


def test_verify_none_actor_denies() -> None:
    """verify() returns allowed=False for a None actor_id
    (treated as missing identity)."""
    registry = IdentityRegistry([IdentityRecord("actor-1", active=True)])
    result = registry.verify(None)
    assert result.allowed is False
    assert result.reason == "missing identity"


def test_verify_empty_string_actor_denies() -> None:
    """verify() returns allowed=False for an empty string actor_id."""
    registry = IdentityRegistry([IdentityRecord("actor-1", active=True)])
    result = registry.verify("")
    assert result.allowed is False
    assert result.reason == "missing identity"


def test_record_round_trip_through_record() -> None:
    """IdentityRecord.to_record() and from_record() round-trip."""
    record = IdentityRecord("actor-1", active=True)
    rebuilt = IdentityRecord.from_record(record.to_record())
    assert rebuilt == record


def test_record_from_record_default_active() -> None:
    """from_record() defaults active=True when the key is missing."""
    rebuilt = IdentityRecord.from_record({"actor_id": "actor-1"})
    assert rebuilt.active is True


def test_record_from_record_inactive() -> None:
    """from_record() respects explicit active=False."""
    rebuilt = IdentityRecord.from_record({"actor_id": "actor-1", "active": False})
    assert rebuilt.active is False


def test_registry_overwrite_same_id() -> None:
    """add() with an existing actor_id overwrites the prior record."""
    registry = IdentityRegistry()
    registry.add(IdentityRecord("actor-1", active=True))
    registry.add(IdentityRecord("actor-1", active=False))
    result = registry.verify("actor-1")
    assert result.allowed is False
    assert result.reason == "identity inactive"


def test_registry_records_count_matches_adds() -> None:
    """records() returns one entry per add()."""
    registry = IdentityRegistry(
        [
            IdentityRecord("a", active=True),
            IdentityRecord("b", active=True),
            IdentityRecord("c", active=False),
        ]
    )
    assert len(registry.records()) == 3
