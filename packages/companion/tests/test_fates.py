"""Unit tests for companion.fates.FateLedger.

Covers: record append, validation, query filters, prune, fail-closed
behavior on invalid input and missing ids.
"""

from __future__ import annotations

import pytest
from companion.fates import FateLedger, FateLedgerError, FateRecord


def _valid_record(record_id: str = "fate-1") -> FateRecord:
    return FateRecord(
        id=record_id,
        timestamp="2026-06-25T00:00:00Z",
        agents_involved=["alice", "bob"],
        event_type="decision",
        description="A fate was recorded.",
        decision_made="APPROVE",
        paths_considered=["ALLOW", "DENY"],
        weight=5.0,
    )


def test_empty_ledger_returns_no_records() -> None:
    ledger = FateLedger()
    assert ledger.query_fates() == []


def test_record_fate_appends_and_uses_internal_id() -> None:
    """When record dict has 'id' field, that id is used (no override)."""
    ledger = FateLedger()
    snapshot, returned_id = ledger.record_fate(_valid_record(), expected_revision=0)
    assert returned_id == "fate-1"
    results = ledger.query_fates()
    assert len(results) == 1
    assert results[0]["id"] == "fate-1"
    assert snapshot.revision == 1


def test_explicit_record_id_overrides_internal_id() -> None:
    """record_id parameter wins over record-internal id field."""
    ledger = FateLedger()
    _, returned_id = ledger.record_fate(
        _valid_record("internal-id"), expected_revision=0, record_id="param-id"
    )
    assert returned_id == "param-id"
    results = ledger.query_fates()
    assert results[0]["id"] == "param-id"


def test_record_fate_with_no_id_generates_uuid() -> None:
    """When no id is provided (param or internal), a uuid4 is generated."""
    ledger = FateLedger()
    record_no_id: dict[str, object] = {
        "timestamp": "2026-06-25T00:00:00Z",
        "agents_involved": ["alice"],
        "event_type": "decision",
        "description": "no id provided",
        "decision_made": None,
        "paths_considered": [],
        "weight": 1.0,
    }
    _, generated_id = ledger.record_fate(record_no_id, expected_revision=0)
    # uuid4 string is 36 chars with hyphens
    assert len(generated_id) == 36
    assert "-" in generated_id


def test_duplicate_id_raises_fail_closed() -> None:
    ledger = FateLedger()
    ledger.record_fate(_valid_record("dup"), expected_revision=0)
    with pytest.raises(FateLedgerError, match="already exists"):
        ledger.record_fate(_valid_record("dup"), expected_revision=1)


def test_missing_timestamp_field_raises() -> None:
    """Validation fires for missing required fields OTHER than id (id auto-generated)."""
    ledger = FateLedger()
    bad: dict[str, object] = {
        "id": "x",
        "agents_involved": ["a"],
        "event_type": "x",
        "description": "x",
        "decision_made": None,
        "paths_considered": [],
        "weight": 1.0,
    }
    # missing 'timestamp' (defaults to empty string at coercion, then rejected as non-empty)
    with pytest.raises(FateLedgerError, match="timestamp"):
        ledger.record_fate(bad, expected_revision=0)


def test_wrong_type_for_agents_involved_raises() -> None:
    """Wrong type for agents_involved (int instead of list) is rejected."""
    ledger = FateLedger()
    bad: dict[str, object] = {
        "id": "x",
        "timestamp": "2026-06-25T00:00:00Z",
        "agents_involved": 42,  # int, not list
        "event_type": "x",
        "description": "x",
        "decision_made": None,
        "paths_considered": [],
        "weight": 1.0,
    }
    with pytest.raises(FateLedgerError, match="agents_involved"):
        ledger.record_fate(bad, expected_revision=0)


def test_negative_weight_rejected() -> None:
    ledger = FateLedger()
    bad = _valid_record()
    bad["weight"] = -1.0
    with pytest.raises(FateLedgerError, match="non-negative"):
        ledger.record_fate(bad, expected_revision=0)


def test_query_by_id_returns_single_match() -> None:
    ledger = FateLedger()
    ledger.record_fate(_valid_record("a"), expected_revision=0)
    ledger.record_fate(_valid_record("b"), expected_revision=1)
    results = ledger.query_fates(record_id="b")
    assert len(results) == 1
    assert results[0]["id"] == "b"


def test_query_by_event_type_filters() -> None:
    ledger = FateLedger()
    r1 = _valid_record("x")
    r1["event_type"] = "approval"
    r2 = _valid_record("y")
    r2["event_type"] = "denial"
    ledger.record_fate(r1, expected_revision=0)
    ledger.record_fate(r2, expected_revision=1)
    results = ledger.query_fates(event_type="approval")
    assert len(results) == 1
    assert results[0]["event_type"] == "approval"


def test_prune_fates_removes_named_records() -> None:
    ledger = FateLedger()
    ledger.record_fate(_valid_record("a"), expected_revision=0)  # rev 1
    ledger.record_fate(_valid_record("b"), expected_revision=1)  # rev 2
    ledger.record_fate(_valid_record("c"), expected_revision=2)  # rev 3
    revision_before = ledger.snapshot().revision
    snapshot = ledger.prune_fates(["a", "c"], expected_revision=3)
    remaining = {f["id"] for f in ledger.query_fates()}
    assert remaining == {"b"}
    # Prune bumped revision exactly once
    assert snapshot.revision == revision_before + 1


def test_prune_with_missing_id_raises_fail_closed() -> None:
    ledger = FateLedger()
    ledger.record_fate(_valid_record("exists"), expected_revision=0)
    with pytest.raises(FateLedgerError, match="ids not found"):
        ledger.prune_fates(["exists", "ghost"], expected_revision=1)


def test_prune_with_empty_iterable_is_noop() -> None:
    ledger = FateLedger()
    ledger.record_fate(_valid_record("a"), expected_revision=0)
    revision_before = ledger.snapshot().revision
    snapshot = ledger.prune_fates([], expected_revision=1)
    assert len(ledger.query_fates()) == 1
    # No-op prune does NOT bump revision
    assert snapshot.revision == revision_before


def test_resource_property_is_canonical_companion_fates() -> None:
    ledger = FateLedger()
    assert ledger.resource == "companion:fates"
