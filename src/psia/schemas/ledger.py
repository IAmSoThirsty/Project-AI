"""PSIA ledger schemas — execution records, blocks, Merkle tree."""
from __future__ import annotations

import hashlib
import json

from pydantic import BaseModel

from psia.schemas.identity import Signature


class TimeProof(BaseModel):
    tsa_name: str = ""
    timestamp_token: str = ""
    serial_number: int = 0


class RecordTimestamps(BaseModel):
    received_at: str
    decided_at: str
    committed_at: str | None = None


class ExecutionRecord(BaseModel):
    record_id: str
    request_id: str
    actor: str
    capability_token_id: str
    inputs_hash: str
    decision_hash: str
    result: str
    timestamps: RecordTimestamps
    time_proof: TimeProof | None = None
    signature: Signature

    def compute_hash(self) -> str:
        d = self.model_dump()
        d.pop("signature", None)
        return hashlib.sha256(
            json.dumps(d, sort_keys=True, default=str).encode()
        ).hexdigest()


class LedgerBlock(BaseModel):
    height: int
    previous_block_hash: str
    merkle_root: str
    records: list[str]
    timestamp: str = ""

    @staticmethod
    def compute_merkle_root(hashes: list[str]) -> str:
        if not hashes:
            return hashlib.sha256(b"").hexdigest()
        current = list(hashes)
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                combined = (left + right).encode()
                next_level.append(hashlib.sha256(combined).hexdigest())
            current = next_level
        return current[0]

    def compute_hash(self) -> str:
        d = {
            "height": self.height,
            "previous_block_hash": self.previous_block_hash,
            "merkle_root": self.merkle_root,
            "records": self.records,
            "timestamp": self.timestamp,
        }
        return hashlib.sha256(
            json.dumps(d, sort_keys=True).encode()
        ).hexdigest()
