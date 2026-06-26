"""
companion.fates — Append-only fate ledger over kernel.StateRegister.

Ported from legacy `src/app/core/fates/fates.py` (memory-thread / Clotho /
Lachesis / Atropos). This is the MINIMUM VIABLE surface for the companion
package: append-only fate records, query by id, prune by id. The full
emotional-weight / decay-rate / reinforcement semantics of legacy fates
are intentionally deferred to a separate "full Fates port" wave — that
work belongs in `packages/fates/` as its own package per the architectural
boundary (downward-only deps).

Architectural invariants:
- Downward-only: companion imports only kernel + stdlib.
- Canonical types: kernel.JsonScalar, kernel.JsonValue, kernel.StateRegister.
- Fail-closed: invalid fate input raises ValueError; never silent drop.
- Append-only: prune_fates requires explicit id; bulk operations are caller-side.
- Strict typing: mypy --strict clean.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable, Mapping
from typing import TypedDict, cast

from kernel import JsonValue, StateRegister, StateSnapshot


class FateRecord(TypedDict):
    """Canonical shape of a fate record held in the ledger.

    All fields are required; missing fields are rejected at record time.
    """

    id: str
    timestamp: str
    agents_involved: list[str]
    event_type: str
    description: str
    decision_made: str | None
    paths_considered: list[str]
    weight: float


class FateLedgerError(ValueError):
    """Raised when fate record input is invalid. Inherits ValueError for caller compat."""


def _validate_record(record: Mapping[str, JsonValue]) -> None:
    """Validate a fate record has all required fields with correct types.

    Raises FateLedgerError on any validation failure.
    """
    required: tuple[tuple[str, type[object]], ...] = (
        ("id", str),
        ("timestamp", str),
        ("event_type", str),
        ("description", str),
    )
    for field_name, field_type in required:
        value = record.get(field_name)
        if value is None:
            raise FateLedgerError(f"fate record missing required field '{field_name}'")
        if not isinstance(value, field_type):
            raise FateLedgerError(f"fate record field '{field_name}' must be {field_type.__name__}")
        if isinstance(value, str) and not value.strip():
            raise FateLedgerError(f"fate record field '{field_name}' must be non-empty")
    agents = record.get("agents_involved")
    if agents is None:
        raise FateLedgerError("fate record missing required field 'agents_involved'")
    if not isinstance(agents, list) or not all(isinstance(a, str) for a in agents):
        raise FateLedgerError("fate record field 'agents_involved' must be list[str]")
    decision = record.get("decision_made")
    if decision is not None and not isinstance(decision, str):
        raise FateLedgerError("fate record field 'decision_made' must be str or None")
    paths = record.get("paths_considered")
    if paths is None:
        raise FateLedgerError("fate record missing required field 'paths_considered'")
    if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
        raise FateLedgerError("fate record field 'paths_considered' must be list[str]")
    weight = record.get("weight")
    if not isinstance(weight, (int, float)):
        raise FateLedgerError("fate record field 'weight' must be numeric")
    if float(weight) < 0:
        raise FateLedgerError("fate record field 'weight' must be non-negative")


def _validate_raw_record(record: Mapping[str, object]) -> None:
    """Validate the raw record input BEFORE coercion.

    Catches wrong types (e.g., agents_involved as int instead of list) before
    list() coercion would raise TypeError. This ensures fail-closed behavior
    on type mismatches with a FateLedgerError, not a raw TypeError.

    `id` is allowed to be missing (auto-generated); `timestamp`, `event_type`,
    `description` are required as strings (empty rejected). `agents_involved`
    and `paths_considered` must be list-like (list/tuple) — exact list type
    check is deferred to _validate_record after coercion.
    """
    if not isinstance(record, Mapping):
        raise FateLedgerError(f"fate record must be a Mapping, got {type(record).__name__}")
    for field_name in ("timestamp", "event_type", "description"):
        value = record.get(field_name)
        if not isinstance(value, str):
            raise FateLedgerError(
                f"fate record field '{field_name}' must be str (got {type(value).__name__ if value is not None else 'None'})"
            )
        if not value.strip():
            raise FateLedgerError(f"fate record field '{field_name}' must be non-empty")
    for field_name in ("agents_involved", "paths_considered"):
        value = record.get(field_name)
        if not isinstance(value, (list, tuple)):
            raise FateLedgerError(
                f"fate record field '{field_name}' must be list or tuple (got {type(value).__name__ if value is not None else 'None'})"
            )
    decision = record.get("decision_made")
    if decision is not None and not isinstance(decision, str):
        raise FateLedgerError(
            f"fate record field 'decision_made' must be str or None (got {type(decision).__name__})"
        )
    weight = record.get("weight")
    if not isinstance(weight, (int, float)) or isinstance(weight, bool):
        raise FateLedgerError(
            f"fate record field 'weight' must be numeric (got {type(weight).__name__ if weight is not None else 'None'})"
        )


class FateLedger:
    """Append-only fate ledger backed by kernel.StateRegister.

    The ledger holds a list of fate records (JSON-serializable dicts).
    Every state transition is revision-tracked via the StateRegister, so
    audit replay can reconstruct the fate history deterministically.
    """

    def __init__(self) -> None:
        self._state = StateRegister({"fates": []})

    @property
    def resource(self) -> str:
        return "companion:fates"

    def snapshot(self) -> StateSnapshot:
        return self._state.snapshot()

    def record_fate(
        self,
        record: Mapping[str, object],
        *,
        expected_revision: int,
        record_id: str | None = None,
    ) -> tuple[StateSnapshot, str]:
        """Append a fate record to the ledger.

        Returns (new_state_snapshot, assigned_id). The id resolution order is:
          1. explicit `record_id` parameter (highest priority)
          2. `id` field within the record dict
          3. generated uuid4 (lowest priority)

        Raises FateLedgerError on duplicate id (idempotent-fail; never silent
        duplicate) or validation failure.
        """
        # Resolve the target id (explicit param wins over record-internal id)
        explicit_id = record_id
        if explicit_id is None:
            internal_id = record.get("id")
            if isinstance(internal_id, str) and internal_id.strip():
                explicit_id = internal_id
        # If caller provided an id (via param or record), check for duplicate
        if explicit_id is not None:
            existing = self._state.snapshot().values["fates"]
            assert isinstance(existing, list)
            if any(isinstance(f, dict) and f.get("id") == explicit_id for f in existing):
                raise FateLedgerError(f"fate id '{explicit_id}' already exists")
        # Resolve final id
        new_id = explicit_id if explicit_id is not None else str(uuid.uuid4())
        # Validate raw input BEFORE coercion (catch wrong types before list() blows up)
        _validate_raw_record(record)
        # Build the to-be-recorded dict (safe to coerce now)
        record_dict: dict[str, JsonValue] = {
            "id": new_id,
            "timestamp": str(cast(str, record.get("timestamp", ""))),
            "agents_involved": [
                str(a) for a in cast("list[object]", record.get("agents_involved", []))
            ],
            "event_type": str(cast(str, record.get("event_type", ""))),
            "description": str(cast(str, record.get("description", ""))),
            "decision_made": cast("str | None", record.get("decision_made")),
            "paths_considered": [
                str(p) for p in cast("list[object]", record.get("paths_considered", []))
            ],
            "weight": float(cast("float | int", record.get("weight", 0.0))),
        }
        # Re-validate the coerced record (catches empty strings, list-of-non-str)
        _validate_record(record_dict)
        # Append to ledger
        snapshot = self._state.snapshot()
        existing_list = snapshot.values["fates"]
        assert isinstance(existing_list, list)
        new_list: list[JsonValue] = [*list(existing_list), record_dict]
        new_snapshot = self._state.update({"fates": new_list}, expected_revision=expected_revision)
        return new_snapshot, new_id

    def query_fates(
        self,
        *,
        record_id: str | None = None,
        event_type: str | None = None,
    ) -> list[dict[str, JsonValue]]:
        """Query fates from the ledger.

        Filters by id (exact) and/or event_type (exact). Returns matching
        fate records as a list of dicts (JSON-serializable).
        """
        snapshot = self._state.snapshot()
        fates_raw = snapshot.values["fates"]
        if not isinstance(fates_raw, list):
            return []
        results: list[dict[str, JsonValue]] = []
        for fate in fates_raw:
            if not isinstance(fate, dict):
                continue
            if record_id is not None and fate.get("id") != record_id:
                continue
            if event_type is not None and fate.get("event_type") != event_type:
                continue
            results.append(dict(fate))
        return results

    def prune_fates(
        self,
        record_ids: Iterable[str],
        *,
        expected_revision: int,
    ) -> StateSnapshot:
        """Remove fate records by id.

        Append-only semantics: this is a logical prune (the prune operation
        itself is appended to the audit chain via StateRegister revision).
        Returns new StateSnapshot after prune.

        Raises FateLedgerError if any requested id is not found (fail-closed;
        no silent partial prune).
        """
        ids_to_prune = set(record_ids)
        if not ids_to_prune:
            return self._state.snapshot()
        snapshot = self._state.snapshot()
        fates_raw = snapshot.values["fates"]
        if not isinstance(fates_raw, list):
            raise FateLedgerError("ledger state is corrupted: fates is not a list")
        existing_ids: set[str] = set()
        kept: list[JsonValue] = []
        for fate in fates_raw:
            if not isinstance(fate, dict):
                continue
            fid = fate.get("id")
            if isinstance(fid, str):
                existing_ids.add(fid)
            if fid in ids_to_prune:
                continue
            kept.append(fate)
        missing = ids_to_prune - existing_ids
        if missing:
            raise FateLedgerError(f"prune_fates: ids not found in ledger: {sorted(missing)}")
        return self._state.update({"fates": kept}, expected_revision=expected_revision)


__all__ = [
    "FateLedger",
    "FateLedgerError",
    "FateRecord",
]
