"""PSIA durable ledger — append-only records, block sealing, Merkle chain."""
from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ExecutionRecord:
    record_id: str
    request_id: str
    actor: str
    action: str
    resource: str
    decision: str
    commit_id: str = ""
    diff_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def compute_hash(self) -> str:
        d = {
            "record_id": self.record_id,
            "request_id": self.request_id,
            "actor": self.actor,
            "action": self.action,
            "resource": self.resource,
            "decision": self.decision,
            "commit_id": self.commit_id,
        }
        return hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()


@dataclass
class LedgerBlock:
    block_id: int
    records: list[ExecutionRecord]
    merkle_root: str
    previous_block_hash: str
    sealed_at: str
    record_count: int
    anchor_hash: str = ""

    def compute_block_hash(self) -> str:
        d = {
            "block_id": self.block_id,
            "merkle_root": self.merkle_root,
            "previous_block_hash": self.previous_block_hash,
            "sealed_at": self.sealed_at,
            "record_count": self.record_count,
        }
        return hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()


@dataclass
class SealedBlock:
    height: int
    previous_block_hash: str
    merkle_root: str
    record_count: int
    block_hash: str
    anchor_hash: str = ""

    def compute_self_hash(self) -> str:
        d = {
            "height": self.height,
            "previous_block_hash": self.previous_block_hash,
            "merkle_root": self.merkle_root,
            "record_count": self.record_count,
        }
        return hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()


def _compute_merkle_root(hashes: list[str]) -> str:
    if not hashes:
        return hashlib.sha256(b"").hexdigest()
    current = list(hashes)
    while len(current) > 1:
        next_level = []
        for i in range(0, len(current), 2):
            left = current[i]
            right = current[i + 1] if i + 1 < len(current) else left
            next_level.append(hashlib.sha256((left + right).encode()).hexdigest())
        current = next_level
    return current[0]


class DurableLedger:
    GENESIS_HASH = "0" * 64

    def __init__(
        self,
        block_size: int = 100,
        on_block_sealed: Callable[[SealedBlock], None] | None = None,
        tsa: Any = None,
    ) -> None:
        self._block_size = block_size
        self._on_block_sealed = on_block_sealed
        self._tsa = tsa
        self._records: dict[str, ExecutionRecord] = {}
        self._pending: list[ExecutionRecord] = []
        self._blocks: list[SealedBlock] = []
        self._ledger_blocks: list[LedgerBlock] = []
        self._pending_snapshot: list[ExecutionRecord] = []
        self._lock = threading.Lock()

    @property
    def block_size(self) -> int:
        return self._block_size

    @property
    def sealed_block_count(self) -> int:
        with self._lock:
            return len(self._blocks)

    @property
    def pending_record_count(self) -> int:
        with self._lock:
            return len(self._pending)

    @property
    def total_records(self) -> int:
        with self._lock:
            return len(self._records)

    @property
    def _total_records(self) -> int:
        with self._lock:
            return len(self._records)

    @property
    def _sealed_blocks(self) -> list[LedgerBlock]:
        with self._lock:
            return list(self._ledger_blocks)

    def append(self, record: ExecutionRecord) -> str:
        with self._lock:
            if record.record_id in self._records:
                raise ValueError(
                    f"INV-ROOT-9: record '{record.record_id}' already exists; no overwrites allowed"
                )
            self._records[record.record_id] = record
            self._pending.append(record)
            self._pending_snapshot.append(record)
            record_hash = record.compute_hash()
            if len(self._pending) >= self._block_size:
                self._seal_block_locked()
            return record_hash

    def _seal_block_locked(self) -> SealedBlock:
        from datetime import datetime, timezone
        prev_hash = self._blocks[-1].block_hash if self._blocks else self.GENESIS_HASH
        record_hashes = [r.compute_hash() for r in self._pending]
        merkle_root = _compute_merkle_root(record_hashes)
        height = len(self._blocks)
        block = SealedBlock(
            height=height,
            previous_block_hash=prev_hash,
            merkle_root=merkle_root,
            record_count=len(self._pending),
            block_hash="",
        )
        block.block_hash = block.compute_self_hash()

        ts = datetime.now(timezone.utc).isoformat()
        ledger_block = LedgerBlock(
            block_id=height,
            records=list(self._pending_snapshot),
            merkle_root=merkle_root,
            previous_block_hash=prev_hash,
            sealed_at=ts,
            record_count=len(self._pending),
        )

        self._pending.clear()
        self._pending_snapshot.clear()
        self._blocks.append(block)
        self._ledger_blocks.append(ledger_block)

        if self._tsa is not None:
            try:
                import hashlib as _h
                bh = _h.sha256(block.block_hash.encode()).hexdigest()
                self._tsa.request_timestamp(bh, nonce=block.block_hash[:32])
            except Exception:
                pass

        if self._on_block_sealed is not None:
            self._on_block_sealed(block)
        return block

    def force_seal(self) -> SealedBlock | None:
        with self._lock:
            if not self._pending:
                return None
            return self._seal_block_locked()

    def get_record(self, record_id: str) -> ExecutionRecord | None:
        with self._lock:
            return self._records.get(record_id)

    def get_records_by_request(self, request_id: str) -> list[ExecutionRecord]:
        with self._lock:
            return [r for r in self._records.values() if r.request_id == request_id]

    def get_block(self, height: int) -> LedgerBlock | None:
        with self._lock:
            if 0 <= height < len(self._ledger_blocks):
                return self._ledger_blocks[height]
            return None

    def get_sealed_block(self, height: int) -> SealedBlock | None:
        with self._lock:
            if 0 <= height < len(self._blocks):
                return self._blocks[height]
            return None

    def _compute_merkle_root(self, records: list[ExecutionRecord]) -> str:
        hashes = [r.compute_hash() for r in records]
        return _compute_merkle_root(hashes)

    def verify_chain(self) -> bool:
        with self._lock:
            for i, block in enumerate(self._blocks):
                if i == 0:
                    if block.previous_block_hash != self.GENESIS_HASH:
                        return False
                else:
                    if block.previous_block_hash != self._blocks[i - 1].block_hash:
                        return False
                if block.block_hash != block.compute_self_hash():
                    return False
            return True

    def anchor_block(self, height: int, anchor_hash: str) -> bool:
        with self._lock:
            if 0 <= height < len(self._blocks):
                self._blocks[height].anchor_hash = anchor_hash
                if 0 <= height < len(self._ledger_blocks):
                    self._ledger_blocks[height].anchor_hash = anchor_hash
                return True
            return False
