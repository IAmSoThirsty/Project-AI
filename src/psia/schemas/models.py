"""
PSIA plane data models.

Each plane's frame is the typed output of the corresponding pipeline stage.
Frames are immutable dataclasses — stages create new frames, never mutate.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RawFrame:
    """Plane 0 — Entry. Raw untrusted input as received from the wire."""
    payload: dict[str, Any]
    received_at: float = field(default_factory=time.time)
    source_ip: str = "unknown"
    session_id: str = ""

    @property
    def fingerprint(self) -> str:
        import json
        raw = json.dumps(self.payload, sort_keys=True, default=str).encode()
        return hashlib.sha256(raw).hexdigest()[:16]


@dataclass(frozen=True)
class ValidatedFrame:
    """Plane 1 — Validated. Schema-checked, type-coerced, structurally sound."""
    actor: str               # "human" | "agent" | "system"
    action: str              # "read" | "write" | "execute" | "mutate"
    target: str
    context: dict[str, Any]
    origin: str
    raw_fingerprint: str     # fingerprint of originating RawFrame


@dataclass(frozen=True)
class ClassifiedFrame:
    """Plane 2 — Classified. Intent and risk assessed."""
    validated: ValidatedFrame
    risk_level: str          # "low" | "medium" | "high" | "critical"
    intent_class: str        # "read_only" | "state_change" | "governance_mutation"
    threat_score: float      # 0.0 – 1.0


@dataclass(frozen=True)
class ShadowResult:
    """Output of shadow simulation for a single check."""
    check_name: str
    passed: bool
    detail: str = ""


@dataclass(frozen=True)
class ShadowFrame:
    """Plane 3 — Shadow. Parallel simulation completed; invariants checked."""
    classified: ClassifiedFrame
    shadow_results: tuple[ShadowResult, ...]
    shadow_passed: bool      # True iff all shadow checks passed
    shadow_hash: str         # hash of shadow execution state


@dataclass(frozen=True)
class GovernedFrame:
    """Plane 4 — Governed. Triumvirate constitutional evaluation completed."""
    shadow: ShadowFrame
    final_verdict: str       # "allow" | "deny" | "escalate"
    audit_id: str
    pillar_votes: tuple[dict, ...]   # serialised TriumvirateVote dicts


@dataclass(frozen=True)
class CanonicalFrame:
    """Plane 5 — Canonical. Written to append-only canonical log."""
    governed: GovernedFrame
    log_sequence: int        # monotonically increasing sequence number
    log_timestamp: float     # time.time() at write
    entry_hash: str          # SHA-256 of this canonical record


@dataclass(frozen=True)
class SealedFrame:
    """Plane 6 — Sealed. Merkle-root block seal + Ed25519 anchor applied."""
    canonical: CanonicalFrame
    merkle_root: str         # Merkle root over all log entries up to this block
    block_hash: str          # SHA-256(merkle_root + entry_hash + prev_block_hash)
    prev_block_hash: str
    ed25519_signature: str   # hex Ed25519 signature of block_hash (or "" if no key loaded)
    sealed_at: float = field(default_factory=time.time)
