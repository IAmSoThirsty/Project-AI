"""Project-AI Audit Log (Phase B recovery from Project-AI-Canonical).

This package was missing from canonical Project-AI-Beginnings
before this commit. It was recovered from the
``T:\\08-Archive\\Project-AI-Canonical\\`` archive
(docs/SALVAGE_LEDGER.md classifies it as the first-pass
rebuild source for the execution-governance spine).

Public surface:
  - AuditEvent        — hash-chained audit event dataclass
  - AuditLog          — in-memory append-only log
  - FileAuditLog      — file-persisted AuditLog (JSONL, atomic)
  - AuditVerification — chain verification result
  - AuditWriteError   — raised on persistence / chain failures
  - GENESIS_HASH      — the "0" * 64 genesis anchor

The hash chain uses SHA-256 over the JSON-serialized event
payload (sort_keys=True, compact separators) plus the
``previous_hash`` field. Each event's ``event_hash`` covers
the FULL previous chain, so any tampering with any past
event invalidates the chain from that point forward.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from audit.chain import (
    GENESIS_HASH,
    AuditEvent,
    AuditLog,
    AuditVerification,
    AuditWriteError,
    FileAuditLog,
)

try:
    __version__ = _pkg_version("project-ai-audit")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = [
    "GENESIS_HASH",
    "AuditEvent",
    "AuditLog",
    "AuditVerification",
    "AuditWriteError",
    "FileAuditLog",
]
