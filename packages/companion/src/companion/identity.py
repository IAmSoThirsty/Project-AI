"""
companion.identity — Identity manager for companion subsystem.

Ported from legacy `project_ai/engine/identity/identity_manager.py` (82 LOC).
Rewritten to use `kernel.StateRegister` for identity record, downward-only
deps (companion -> kernel only), and explicit Protocol for pluggable
identity-derivation. No upward import into execution/governance.

Architectural invariants:
- Downward-only: companion imports only kernel + stdlib.
- Canonical types: kernel.JsonScalar, kernel.JsonValue, kernel.StateRegister.
- Fail-closed: invalid identity input raises ValueError; never silent ALLOW.
- Pluggable: IdentityDerivation Protocol allows alternate id-derivation functions.
- Strict typing: mypy --strict clean.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Protocol, cast

from kernel import JsonScalar, JsonValue, StateRegister, StateSnapshot

# Identity phases (canonical strings — never accept arbitrary phase names)
PHASE_UNBONDED = "unbonded"
PHASE_BONDED = "bonded"
ALLOWED_PHASES: frozenset[str] = frozenset({PHASE_UNBONDED, PHASE_BONDED})


class IdentityError(ValueError):
    """Raised when identity input is invalid. Inherits ValueError for caller compat."""


class IdentityDerivation(Protocol):
    """Pluggable identity-derivation function.

    Implementations receive the raw identity fields and return either a derived
    id-string or raise IdentityError. Default implementation derives from `name`.
    """

    def __call__(self, fields: Mapping[str, JsonScalar]) -> str: ...


def _default_derivation(fields: Mapping[str, JsonScalar]) -> str:
    """Derive identity id from `name` field; fail-closed if missing."""
    name = fields.get("name")
    if not isinstance(name, str) or not name.strip():
        raise IdentityError("identity fields missing non-empty 'name'")
    return name.strip()


class IdentityManager:
    """Manages companion identity profiles and bonding-aware phases.

    Phases:
      - unbonded: bootstrap mode (initial state)
      - bonded: full identity active (after apply_bonding_profile)

    Identity record is held in a kernel.StateRegister so all state mutations
    are revision-tracked and audit-traceable.
    """

    def __init__(
        self,
        *,
        derivation: IdentityDerivation | None = None,
    ) -> None:
        self._derivation: IdentityDerivation = derivation or _default_derivation
        self._state = StateRegister(
            {
                "name": "Project-AI (Unbonded)",
                "phase": PHASE_UNBONDED,
                "values": {},
                "temperament": {},
                "relationship": {},
                "constraints": {"conservative": True},
            }
        )

    @property
    def resource(self) -> str:
        return "companion:identity"

    def snapshot(self) -> StateSnapshot:
        return self._state.snapshot()

    def get_identity(self) -> dict[str, JsonValue]:
        """Return current identity profile (unbonded bootstrap or bonded profile)."""
        return dict(self._state.snapshot().values)

    def get_phase(self) -> str:
        """Return current phase ('unbonded' or 'bonded')."""
        return str(self._state.snapshot().values["phase"])

    def apply_bonding_profile(
        self,
        profile: Mapping[str, object],
        *,
        expected_revision: int,
    ) -> StateSnapshot:
        """Apply bonded identity profile and switch to bonded phase.

        Raises IdentityError on invalid input.
        Returns the new StateSnapshot after update.
        """
        name = profile.get("name")
        if not isinstance(name, str) or not name.strip():
            raise IdentityError("bonding profile missing non-empty 'name'")
        # Derive identity id (pluggable); fail-closed if derivation raises
        derived_id = self._derivation({"name": name})
        if not derived_id:
            raise IdentityError("identity derivation returned empty id")
        new_identity: dict[str, JsonValue] = {
            "name": derived_id,
            "phase": PHASE_BONDED,
            "values": dict(cast(Mapping[str, JsonValue], profile.get("values", {}))),
            "temperament": dict(cast(Mapping[str, JsonValue], profile.get("temperament", {}))),
            "relationship": dict(cast(Mapping[str, JsonValue], profile.get("relationship", {}))),
            "constraints": dict(cast(Mapping[str, JsonValue], profile.get("constraints", {}))),
        }
        return self._state.update(new_identity, expected_revision=expected_revision)

    def run_bonding_protocol(
        self,
        bonding_input: Mapping[str, object],
        *,
        expected_revision: int,
    ) -> StateSnapshot:
        """High-level bonding protocol hook.

        If already bonded, this is a no-op and returns current snapshot.
        Otherwise delegates to apply_bonding_profile.
        """
        if self.get_phase() == PHASE_BONDED:
            return self._state.snapshot()
        return self.apply_bonding_profile(bonding_input, expected_revision=expected_revision)


__all__ = [
    "ALLOWED_PHASES",
    "PHASE_BONDED",
    "PHASE_UNBONDED",
    "IdentityDerivation",
    "IdentityError",
    "IdentityManager",
]
