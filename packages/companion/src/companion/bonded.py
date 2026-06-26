"""
companion.bonded — Bonded companion surface integrating Identity + Fates.

This module wires IdentityManager and FateLedger into a single bonded
companion surface. Mutations route through the existing ExecutionGate
(provided by the caller), preserving the single audit chain invariant.

Architectural invariants:
- Downward-only: companion imports only kernel + companion.{identity,fates}.
- Canonical types: kernel.JsonScalar, kernel.JsonValue, kernel.StateRegister.
- Fail-closed: invalid input raises; never silent ALLOW.
- Single audit chain: every state mutation routes via ExecutionGate.
- Strict typing: mypy --strict clean.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import cast

from companion.fates import FateLedger
from companion.identity import (
    IdentityDerivation,
    IdentityManager,
)
from execution import ExecutionGate, ExecutionResult
from kernel import ActionRequest, JsonValue

BOND_IDENTITY_OPERATION = "companion.bond.identity"
RECORD_FATE_OPERATION = "companion.fate.record"
PRUNE_FATES_OPERATION = "companion.fate.prune"


class BondedCompanion:
    """Bonded companion surface — Identity + Fates wired through ExecutionGate."""

    def __init__(
        self,
        *,
        companion_id: str,
        execution: ExecutionGate,
        derivation: IdentityDerivation | None = None,
    ) -> None:
        if not companion_id.strip():
            raise ValueError("companion_id must not be empty")
        self.companion_id = companion_id
        self._execution = execution
        self._identity = IdentityManager(derivation=derivation)
        self._fates = FateLedger()

    def identity(self) -> IdentityManager:
        return self._identity

    def fates(self) -> FateLedger:
        return self._fates

    def bond(
        self,
        profile: Mapping[str, object],
        *,
        expected_revision: int,
        capability_token: str,
    ) -> ExecutionResult:
        """Apply a bonding profile and switch to bonded phase via ExecutionGate."""
        request_payload: dict[str, JsonValue] = {
            "profile": _to_json_value(profile),
            "expected_revision": expected_revision,
        }
        return self._execution.submit_action(
            _build_request(
                companion_id=self.companion_id,
                operation=BOND_IDENTITY_OPERATION,
                payload=request_payload,
            ),
            capability_token=capability_token,
            executor=lambda req: _snapshot_to_json(
                self._identity.apply_bonding_profile(
                    _coerce_profile(req.payload["profile"]),
                    expected_revision=_as_int(req.payload["expected_revision"]),
                )
            ),
        )

    def record_fate(
        self,
        record: Mapping[str, object],
        *,
        expected_revision: int,
        capability_token: str,
        record_id: str | None = None,
    ) -> ExecutionResult:
        """Append a fate record via ExecutionGate."""
        request_payload: dict[str, JsonValue] = {
            "record": _to_json_value(record),
            "expected_revision": expected_revision,
            "record_id": record_id,
        }
        return self._execution.submit_action(
            _build_request(
                companion_id=self.companion_id,
                operation=RECORD_FATE_OPERATION,
                payload=request_payload,
            ),
            capability_token=capability_token,
            executor=lambda req: {"id": _record_fate_through(self._fates, req.payload, record_id)},
        )

    def prune_fates(
        self,
        record_ids: list[str],
        *,
        expected_revision: int,
        capability_token: str,
    ) -> ExecutionResult:
        """Prune fate records by id via ExecutionGate."""
        request_payload: dict[str, JsonValue] = {
            "record_ids": list(record_ids),
            "expected_revision": expected_revision,
        }
        return self._execution.submit_action(
            _build_request(
                companion_id=self.companion_id,
                operation=PRUNE_FATES_OPERATION,
                payload=request_payload,
            ),
            capability_token=capability_token,
            executor=lambda req: _snapshot_to_json(
                self._fates.prune_fates(
                    req.payload["record_ids"],  # type: ignore[arg-type]
                    expected_revision=_as_int(req.payload["expected_revision"]),
                )
            ),
        )


def _snapshot_to_json(snapshot: object) -> JsonValue:
    """Convert a StateSnapshot (or similar) into a JSON-serializable dict."""
    if hasattr(snapshot, "values"):
        return dict(snapshot.values)
    if isinstance(snapshot, dict):
        return snapshot
    return {"result": str(snapshot)}


def _record_fate_through(
    fates: FateLedger, payload: Mapping[str, JsonValue], default_id: str | None
) -> str:
    """Call FateLedger.record_fate via payload, returning just the assigned id."""
    _, assigned_id = fates.record_fate(
        _coerce_record(payload["record"]),
        expected_revision=_as_int(payload["expected_revision"]),
        record_id=default_id if default_id is not None else payload.get("record_id"),  # type: ignore[arg-type]
    )
    return assigned_id


def _as_int(value: JsonValue) -> int:
    """Narrow a JsonValue to an int. Validated by callers; raises on bad type."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, str)):
        return int(value)
    raise TypeError(f"expected int-like JsonValue, got {type(value).__name__}")


def _to_json_value(mapping: Mapping[str, object]) -> JsonValue:
    """Cast a Mapping[str, object] to a JsonValue (best-effort)."""
    return cast("dict[str, JsonValue]", dict(mapping))


def _build_request(
    *, companion_id: str, operation: str, payload: dict[str, JsonValue]
) -> ActionRequest:
    """Build an ActionRequest for the companion subsystem.

    Imported here (rather than at module top) to avoid circular imports
    between companion and execution at type-check time.
    """
    return ActionRequest(
        action_id=f"{companion_id}:{operation}:{payload.get('expected_revision', 0)}",
        actor=companion_id,
        operation=operation,
        resource=f"companion:{companion_id}",
        payload=payload,
    )


def _coerce_profile(profile: object) -> dict[str, object]:
    """Coerce a profile object to a dict[str, JsonScalar] shape."""
    if not isinstance(profile, dict):
        from companion.fates import FateLedgerError  # reuse import guard

        raise FateLedgerError(f"bond profile must be a dict, got {type(profile).__name__}")
    return cast("dict[str, object]", profile)


def _coerce_record(record: object) -> dict[str, object]:
    """Coerce a fate record object to a dict shape."""
    if not isinstance(record, dict):
        from companion.fates import FateLedgerError

        raise FateLedgerError(f"fate record must be a dict, got {type(record).__name__}")
    return cast("dict[str, object]", record)


__all__ = [
    "BOND_IDENTITY_OPERATION",
    "PRUNE_FATES_OPERATION",
    "RECORD_FATE_OPERATION",
    "BondedCompanion",
]


# Re-export phase constant for caller convenience
__all_phase__ = ["PHASE_BONDED"]
