"""
PSIA Ledger Schema — append-only execution records and blocks.

Implements §3.8 of the PSIA v1.0 specification.

The ledger is the immutable audit trail of all PSIA decisions and
canonical mutations.  It uses a blockchain-like structure with Merkle
roots, trusted timestamps, and multi-validator signatures to ensure
non-repudiation, tamper detection, and external verifiability.

Block structure:
    - Each block contains an ordered list of ExecutionRecord hashes
    - Blocks are chained via ``previous_block_hash``
    - Merkle root proves inclusion of all records
    - Time proof provides external temporal anchoring
    - Validator signatures provide multi-party attestation
"""

from __future__ import annotations

import hashlib
import json

from pydantic import BaseModel, Field

from psia.schemas.identity import Signature


class RecordTimestamps(BaseModel):
    """Temporal anchors for an execution record lifecycle."""

    received_at: str = Field(..., description="RFC 3339 — when request was received")
    decided_at: str = Field(..., description="RFC 3339 — when Cerberus decided")
    committed_at: str = Field("", description="RFC 3339 — when canonical commit completed")

    model_config = {"frozen": True}


class ExecutionRecord(BaseModel):
    """
    PSIA Execution Record — a single ledger entry.

    Captures the complete cryptographic chain from request through
    decision to canonical commit.  Each hash field is computed
    independently so that any tampering is detectable.

    Invariants:
        - ``inputs_hash`` = SHA-256(RequestEnvelope + PolicyGraph + InvariantSet)
        - ``shadow_hash`` = SHA-256(ShadowReport)
        - ``decision_hash`` = SHA-256(CerberusDecision)
        - ``canonical_diff_hash`` = SHA-256(applied diff)
        - ``result`` must match ``CerberusDecision.final_decision``
    """

    record_id: str = Field(..., description="Unique record ID (rec_...)")
    request_id: str = Field(..., description="Original request ID")
    actor: str = Field(..., description="DID of the actor")
    capability_token_id: str = Field(..., description="CapabilityToken used")
    inputs_hash: str = Field(..., description="SHA-256 of combined inputs")
    shadow_hash: str = Field("", description="SHA-256 of ShadowReport")
    decision_hash: str = Field(..., description="SHA-256 of CerberusDecision")
    canonical_diff_hash: str = Field("", description="SHA-256 of applied canonical diff")
    result: str = Field(..., description="Final result: allow, deny, quarantine")
    timestamps: RecordTimestamps = Field(..., description="Lifecycle timestamps")
    signature: Signature = Field(..., description="Ledger validator signature")

    model_config = {"frozen": True}

    def compute_hash(self) -> str:
        """Compute deterministic SHA-256 hash of the record (excludes signature)."""
        body = self.model_dump(exclude={"signature"})
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()


class TimeProof(BaseModel):
    """Trusted timestamp proof for ledger block anchoring."""

    method: str = Field("rfc3161", description="Timestamp method: rfc3161 or trusted_timestamp")
    proof: str = Field("", description="Base64-encoded timestamp proof")

    model_config = {"frozen": True}


class LedgerBlock(BaseModel):
    """
    PSIA Ledger Block — a sealed, chained unit of execution records.

    Invariants:
        - ``height`` is monotonically increasing (genesis = 0)
        - ``previous_block_hash`` must match the hash of the prior block
          (empty string for genesis)
        - ``merkle_root`` is the root of the Merkle tree over ``records``
        - ``validator_signatures`` must contain at least 2f+1 signatures
          for BFT tolerance of f faulty validators
    """

    height: int = Field(..., ge=0, description="Block height (genesis = 0)")
    previous_block_hash: str = Field("", description="SHA-256 of previous block")
    merkle_root: str = Field(..., description="Merkle root of record hashes")
    records: list[str] = Field(..., description="Ordered list of record hashes")
    time_proof: TimeProof = Field(default_factory=TimeProof)
    validator_signatures: list[Signature] = Field(
        default_factory=list, description="Multi-validator attestation signatures"
    )

    model_config = {"frozen": True}

    def compute_hash(self) -> str:
        """Compute deterministic SHA-256 hash of the block (excludes validator_signatures)."""
        body = self.model_dump(exclude={"validator_signatures"})
        canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    @staticmethod
    def compute_merkle_root(record_hashes: list[str]) -> str:
        """Compute Merkle root from an ordered list of record hashes.

        Uses a standard binary Merkle tree with SHA-256.  If the number
        of leaves is odd, the last leaf is duplicated.

        Args:
            record_hashes: Hex-encoded SHA-256 hashes of execution records

        Returns:
            Hex-encoded Merkle root hash
        """
        if not record_hashes:
            return hashlib.sha256(b"").hexdigest()

        # Convert to bytes for hashing
        level = [bytes.fromhex(h) for h in record_hashes]

        while len(level) > 1:
            next_level: list[bytes] = []
            for i in range(0, len(level), 2):
                left = level[i]
                right = level[i + 1] if i + 1 < len(level) else level[i]
                combined = hashlib.sha256(left + right).digest()
                next_level.append(combined)
            level = next_level

        return level[0].hex()


__all__ = [
    "RecordTimestamps",
    "ExecutionRecord",
    "TimeProof",
    "LedgerBlock",
]
