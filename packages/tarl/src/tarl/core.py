"""
tarl.core — TARL core data structures (intent, scope, authority).

The TARL (Trust and Authorization Runtime Layer) is the typed surface
that captures a single authorization request as (intent, scope,
authority, constraints). Each TARL is hashable by canonical JSON for
tamper-evidence.

This is the minimum surface from legacy `tarl/core.py`:
- TARL_VERSION constant
- TARL frozen dataclass
- TARL.canonical() and TARL.hash()

Architectural invariants (AGENTS.md v3):
- Downward-only deps: tarl.core imports only stdlib.
- Canonical types: JSON-serializable via canonical().
- Deterministic: hash() is sha256(canonical_json) with sort_keys.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

TARL_VERSION = "2.0"  # Policy/Governance TARL version


@dataclass(frozen=True)
class TARL:
    """Trust and Authorization Runtime Layer record.

    Attributes:
        intent: What the request is trying to do.
        scope: What resources/domains it touches.
        authority: Who/what is requesting (capability token id).
        constraints: Tuple of constraint strings (e.g. "read-only", "no-network").
        version: TARL schema version.
    """

    intent: str
    scope: str
    authority: str
    constraints: tuple[str, ...]
    version: str = TARL_VERSION

    def canonical(self) -> dict[str, object]:
        """Return a canonical JSON-serializable dict representation.

        Constraints are sorted for determinism (so hash() is stable
        regardless of input ordering).
        """
        return {
            "version": self.version,
            "intent": self.intent,
            "scope": self.scope,
            "authority": self.authority,
            "constraints": sorted(self.constraints),
        }

    def hash(self) -> str:
        """Return sha256 hex digest of the canonical JSON."""
        blob = json.dumps(self.canonical(), sort_keys=True).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()


def make_tarl(
    *,
    intent: str,
    scope: str,
    authority: str,
    constraints: tuple[str, ...] | list[str] = (),
    version: str = TARL_VERSION,
) -> TARL:
    """Construct a TARL with input validation."""
    if not isinstance(intent, str) or not intent.strip():
        raise ValueError("intent must be a non-empty string")
    if not isinstance(scope, str) or not scope.strip():
        raise ValueError("scope must be a non-empty string")
    if not isinstance(authority, str) or not authority.strip():
        raise ValueError("authority must be a non-empty string")
    if isinstance(constraints, list):
        constraints_tuple: tuple[str, ...] = tuple(constraints)
    elif isinstance(constraints, tuple):
        constraints_tuple = constraints
    else:
        raise ValueError(
            f"constraints must be tuple or list of str, got {type(constraints).__name__}"
        )
    for c in constraints_tuple:
        if not isinstance(c, str):
            raise ValueError(f"constraint entries must be str, got {type(c).__name__}")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("version must be a non-empty string")
    return TARL(
        intent=intent,
        scope=scope,
        authority=authority,
        constraints=constraints_tuple,
        version=version,
    )


__all__ = [
    "TARL",
    "TARL_VERSION",
    "make_tarl",
]
