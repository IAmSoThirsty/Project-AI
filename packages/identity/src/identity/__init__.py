"""Project-AI Identity Registry (Phase B recovery from Project-AI-Canonical).

This package was missing from canonical Project-AI-Beginnings
before this commit. It was recovered from the
``T:\\08-Archive\\Project-AI-Canonical\\`` archive
(the first-pass rebuild source per docs/SOURCE_BOUNDARY.md).

Public surface:
  - IdentityRecord        — frozen dataclass for one actor
  - IdentityRegistry      — keyed registry of identity records
  - IdentityVerification  — result of verify() — allowed bool,
                            reason, optional record

The identity model is intentionally minimal: an actor has an
``actor_id`` (string) and an ``active`` flag. The registry
verifies that an actor is known, active, and matches the
provided id. There is no concept of credentials, roles, or
permissions here — those live in ``packages/capability/``
(canonical) and ``packages/audit/`` (Phase B-1) respectively.
"""

from __future__ import annotations

from identity.records import (
    IdentityRecord,
    IdentityRegistry,
    IdentityVerification,
)

__version__ = "0.0.0.dev0"

__all__ = [
    "IdentityRecord",
    "IdentityRegistry",
    "IdentityVerification",
]
