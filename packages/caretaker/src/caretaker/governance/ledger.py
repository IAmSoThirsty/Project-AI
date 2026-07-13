"""
caretaker.governance.ledger — Append-only hash-chained audit ledger.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/governance/ledger.py``. Every governance cycle
is recorded in a tamper-evident ledger: each entry carries a SHA-256 hash of
its content and a reference to the previous entry's hash. Any decision can
be replayed and the chain verified.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from typing import Any

from caretaker.continuity import GENESIS_HASH


@dataclass
class LedgerEntry:
    """A single entry in the audit ledger."""

    index: int
    timestamp: float
    user_message: str
    response_text: str
    decision: str  # allow / deny / quarantine
    theta: float
    caki: float
    c_r: float
    c_redundancy: float
    c_loss: float
    c_decision: float
    reweighted: bool
    triumvirate_votes: list[str]
    faults: list[str]
    prev_hash: str
    hash: str = ""

    def compute_hash(self) -> str:
        """SHA-256 of this entry's content (excluding the hash field)."""
        d = asdict(self)
        d.pop("hash", None)
        content = json.dumps(d, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()

    def seal(self) -> None:
        """Compute and set the hash."""
        self.hash = self.compute_hash()

    def verify(self) -> bool:
        """Verify this entry's hash matches its content."""
        return self.hash == self.compute_hash()


class AuditLedger:
    """Append-only, hash-chained audit ledger.

    Modifying any entry invalidates all subsequent entries.
    """

    def __init__(self) -> None:
        self._entries: list[LedgerEntry] = []
        self._genesis_hash = GENESIS_HASH

    @property
    def head_hash(self) -> str:
        """Hash of the most recent entry, or genesis hash if empty."""
        if self._entries:
            return self._entries[-1].hash
        return self._genesis_hash

    @property
    def length(self) -> int:
        return len(self._entries)

    def append(
        self,
        user_message: str,
        response_text: str,
        decision: str,
        theta: float,
        caki: float,
        c_r: float,
        c_redundancy: float,
        c_loss: float,
        c_decision: float,
        reweighted: bool,
        triumvirate_votes: list[str],
        faults: list[str],
    ) -> LedgerEntry:
        """Append a new entry to the ledger and seal it."""
        entry = LedgerEntry(
            index=len(self._entries),
            timestamp=time.time(),
            user_message=user_message[:500],  # truncate for storage
            response_text=response_text[:500],
            decision=decision,
            theta=theta,
            caki=caki,
            c_r=c_r,
            c_redundancy=c_redundancy,
            c_loss=c_loss,
            c_decision=c_decision,
            reweighted=reweighted,
            triumvirate_votes=triumvirate_votes,
            faults=faults,
            prev_hash=self.head_hash,
        )
        entry.seal()
        self._entries.append(entry)
        return entry

    def verify_chain(self) -> bool:
        """Verify the entire hash chain; False if any link is broken."""
        prev = self._genesis_hash
        for entry in self._entries:
            if not entry.verify():
                return False
            if entry.prev_hash != prev:
                return False
            prev = entry.hash
        return True

    def replay(self, index: int) -> LedgerEntry | None:
        """Retrieve a specific entry by index."""
        if 0 <= index < len(self._entries):
            return self._entries[index]
        return None

    def to_dict_list(self) -> list[dict[str, Any]]:
        """Export all entries as dicts (for API/serialization)."""
        return [asdict(e) for e in self._entries]


__all__ = ["AuditLedger", "LedgerEntry"]
