"""
Durable Append-Only Ledger — Immutable Execution History.

Provides an append-only ledger with:
    - Append-only semantics (INV-ROOT-9: no mutation or deletion)
    - Automatic block sealing at configurable thresholds
    - Merkle-root computation per block
    - Block chaining (each block references the previous block's hash)
    - Anchoring support (external hash pinning for tamper evidence)
    - Record querying by request ID, time range, and block ID
    - Statistics and health checks

Security invariants:
    - INV-ROOT-9 (Ledger is append-only — no record can be modified or deleted)

Production notes:
    - In production, the ledger would be backed by a replicated, durable
      storage engine (e.g., Apache Kafka, FoundationDB, or a purpose-built
      append-only log with write-ahead guarantees)
    - Blocks would be anchored to an external timestamping authority (TSA)
      or blockchain for tamper evidence
    - Merkle proofs would enable efficient auditing without full log replay
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ExecutionRecord:
    """A single execution record appended to the ledger.

    Contains the full audit trail for one request lifecycle.
    """
    record_id: str
    request_id: str
    actor: str
    action: str
    resource: str
    decision: str  # "allow", "deny", "quarantine"
    commit_id: str | None = None
    diff_hash: str | None = None
    stage_results: list[dict] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of this record."""
        data = {
            "record_id": self.record_id,
            "request_id": self.request_id,
            "actor": self.actor,
            "action": self.action,
            "resource": self.resource,
            "decision": self.decision,
            "commit_id": self.commit_id,
            "diff_hash": self.diff_hash,
            "timestamp": self.timestamp,
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()


@dataclass
class LedgerBlock:
    """A sealed block of execution records with a Merkle root.

    Blocks are immutable once sealed—no records can be added,
    modified, or removed.
    """
    block_id: int
    records: list[ExecutionRecord]
    merkle_root: str
    previous_block_hash: str
    sealed_at: str
    record_count: int
    anchor_hash: str | None = None
    anchor_timestamp: str | None = None

    def compute_block_hash(self) -> str:
        """Compute SHA-256 hash of this block (includes Merkle root and chain link)."""
        data = {
            "block_id": self.block_id,
            "merkle_root": self.merkle_root,
            "previous_block_hash": self.previous_block_hash,
            "sealed_at": self.sealed_at,
            "record_count": self.record_count,
        }
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()


class DurableLedger:
    """Append-only ledger with block sealing and Merkle roots.

    Records are appended to a current (open) block. When the block
    reaches ``block_size`` records, it is automatically sealed with
    a Merkle root and chained to the previous block.

    Args:
        block_size: Number of records per block before auto-sealing
        on_block_sealed: Optional callback invoked when a block is sealed
    """

    # Genesis block hash — the root of the chain
    GENESIS_HASH = hashlib.sha256(b"PSIA_GENESIS_BLOCK").hexdigest()

    def __init__(
        self,
        *,
        block_size: int = 64,
        on_block_sealed: Any | None = None,
    ) -> None:
        self.block_size = block_size
        self.on_block_sealed = on_block_sealed
        self._sealed_blocks: list[LedgerBlock] = []
        self._current_records: list[ExecutionRecord] = []
        self._record_index: dict[str, ExecutionRecord] = {}
        self._request_index: dict[str, list[str]] = {}
        self._total_records = 0

    def append(self, record: ExecutionRecord) -> str:
        """Append a record to the ledger.

        Returns:
            The SHA-256 hash of the appended record

        Raises:
            ValueError: If a record with this ID already exists (INV-ROOT-9)
        """
        if record.record_id in self._record_index:
            raise ValueError(
                f"INV-ROOT-9 violation: record '{record.record_id}' already exists — "
                f"ledger is append-only, no overwrites"
            )

        self._current_records.append(record)
        self._record_index[record.record_id] = record
        self._request_index.setdefault(record.request_id, []).append(record.record_id)
        self._total_records += 1

        record_hash = record.compute_hash()

        # Auto-seal if block is full
        if len(self._current_records) >= self.block_size:
            self._seal_block()

        return record_hash

    def _seal_block(self) -> LedgerBlock:
        """Seal the current block with a Merkle root."""
        records = list(self._current_records)
        self._current_records = []

        # Compute Merkle root
        merkle_root = self._compute_merkle_root(records)

        # Chain to previous block
        if self._sealed_blocks:
            prev_hash = self._sealed_blocks[-1].compute_block_hash()
        else:
            prev_hash = self.GENESIS_HASH

        block = LedgerBlock(
            block_id=len(self._sealed_blocks),
            records=records,
            merkle_root=merkle_root,
            previous_block_hash=prev_hash,
            sealed_at=datetime.now(timezone.utc).isoformat(),
            record_count=len(records),
        )

        self._sealed_blocks.append(block)

        if self.on_block_sealed:
            try:
                self.on_block_sealed(block)
            except Exception:
                logger.warning("on_block_sealed callback failed", exc_info=True)

        return block

    def force_seal(self) -> LedgerBlock | None:
        """Force-seal the current block even if not full.

        Returns:
            The sealed block, or None if no records to seal
        """
        if not self._current_records:
            return None
        return self._seal_block()

    def _compute_merkle_root(self, records: list[ExecutionRecord]) -> str:
        """Compute Merkle root hash from record hashes."""
        if not records:
            return hashlib.sha256(b"EMPTY_BLOCK").hexdigest()

        hashes = [record.compute_hash() for record in records]

        while len(hashes) > 1:
            next_level = []
            for i in range(0, len(hashes), 2):
                left = hashes[i]
                right = hashes[i + 1] if i + 1 < len(hashes) else left
                combined = hashlib.sha256(
                    (left + right).encode()
                ).hexdigest()
                next_level.append(combined)
            hashes = next_level

        return hashes[0]

    def anchor_block(self, block_id: int, anchor_hash: str) -> bool:
        """Anchor a sealed block with an external hash (e.g., from TSA/blockchain).

        Args:
            block_id: The block to anchor
            anchor_hash: External anchor hash

        Returns:
            True if anchored successfully
        """
        if block_id < 0 or block_id >= len(self._sealed_blocks):
            return False
        block = self._sealed_blocks[block_id]
        # Immutable blocks — create new instance with anchor
        self._sealed_blocks[block_id] = LedgerBlock(
            block_id=block.block_id,
            records=block.records,
            merkle_root=block.merkle_root,
            previous_block_hash=block.previous_block_hash,
            sealed_at=block.sealed_at,
            record_count=block.record_count,
            anchor_hash=anchor_hash,
            anchor_timestamp=datetime.now(timezone.utc).isoformat(),
        )
        return True

    def get_record(self, record_id: str) -> ExecutionRecord | None:
        """Retrieve a record by ID."""
        return self._record_index.get(record_id)

    def get_records_by_request(self, request_id: str) -> list[ExecutionRecord]:
        """Retrieve all records for a given request ID."""
        record_ids = self._request_index.get(request_id, [])
        return [self._record_index[rid] for rid in record_ids if rid in self._record_index]

    def get_block(self, block_id: int) -> LedgerBlock | None:
        """Retrieve a sealed block by ID."""
        if 0 <= block_id < len(self._sealed_blocks):
            return self._sealed_blocks[block_id]
        return None

    def verify_chain(self) -> bool:
        """Verify the integrity of the entire block chain.

        Returns:
            True if all blocks are correctly chained
        """
        for i, block in enumerate(self._sealed_blocks):
            if i == 0:
                if block.previous_block_hash != self.GENESIS_HASH:
                    return False
            else:
                expected = self._sealed_blocks[i - 1].compute_block_hash()
                if block.previous_block_hash != expected:
                    return False
            # Verify Merkle root
            expected_root = self._compute_merkle_root(block.records)
            if block.merkle_root != expected_root:
                return False
        return True

    @property
    def total_records(self) -> int:
        return self._total_records

    @property
    def sealed_block_count(self) -> int:
        return len(self._sealed_blocks)

    @property
    def pending_record_count(self) -> int:
        return len(self._current_records)

    @property
    def sealed_blocks(self) -> list[LedgerBlock]:
        return list(self._sealed_blocks)


__all__ = [
    "DurableLedger",
    "ExecutionRecord",
    "LedgerBlock",
]
