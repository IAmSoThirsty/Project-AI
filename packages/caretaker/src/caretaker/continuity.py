"""
caretaker.continuity — Hash-chain lineage, not serialization.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/continuity.py``. Every state has a verifiable
hash-chain parent; transitions are recorded with digests; the constitutional
and policy versions are tracked; the entire state lineage can be replayed.
This is NOT save/load serialization — each checkpoint links to its parent by
hash, making the history tamper-evident and replayable.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass

GENESIS_HASH = "0" * 64


@dataclass
class ContinuityCheckpoint:
    """A single checkpoint in the continuity chain."""

    index: int
    timestamp: float
    constitutional_version: str
    policy_version: str
    memory_digest: str
    execution_digest: str
    transition: str  # what triggered this checkpoint
    parent_hash: str
    hash: str = ""

    def compute_hash(self) -> str:
        d = asdict(self)
        d.pop("hash", None)
        content = json.dumps(d, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()

    def seal(self) -> None:
        self.hash = self.compute_hash()

    def verify(self) -> bool:
        return self.hash == self.compute_hash()


class ContinuityManager:
    """Manages the continuity hash chain.

    Every state transition creates a checkpoint linked to the previous
    one by hash, making the entire system history tamper-evident and
    replayable.
    """

    CONSTITUTIONAL_VERSION = "0.2.0"
    POLICY_VERSION = "1.0.0"

    def __init__(self) -> None:
        self._checkpoints: list[ContinuityCheckpoint] = []
        self._genesis_hash = GENESIS_HASH

    @property
    def head_hash(self) -> str:
        if self._checkpoints:
            return self._checkpoints[-1].hash
        return self._genesis_hash

    @property
    def length(self) -> int:
        return len(self._checkpoints)

    def checkpoint(
        self,
        transition: str,
        memory_digest: str = "",
        execution_digest: str = "",
    ) -> ContinuityCheckpoint:
        """Create a new checkpoint linked to the current head."""
        cp = ContinuityCheckpoint(
            index=len(self._checkpoints),
            timestamp=time.time(),
            constitutional_version=self.CONSTITUTIONAL_VERSION,
            policy_version=self.POLICY_VERSION,
            memory_digest=memory_digest or self._genesis_hash,
            execution_digest=execution_digest or self._genesis_hash,
            transition=transition,
            parent_hash=self.head_hash,
        )
        cp.seal()
        self._checkpoints.append(cp)
        return cp

    def verify_chain(self) -> bool:
        """Verify the entire continuity chain."""
        prev = self._genesis_hash
        for cp in self._checkpoints:
            if not cp.verify():
                return False
            if cp.parent_hash != prev:
                return False
            prev = cp.hash
        return True

    def replay(self, index: int) -> ContinuityCheckpoint | None:
        """Retrieve a checkpoint by index."""
        if 0 <= index < len(self._checkpoints):
            return self._checkpoints[index]
        return None

    def lineage(self) -> list[str]:
        """Return the full hash lineage."""
        return [cp.hash for cp in self._checkpoints]


__all__ = ["GENESIS_HASH", "ContinuityCheckpoint", "ContinuityManager"]
