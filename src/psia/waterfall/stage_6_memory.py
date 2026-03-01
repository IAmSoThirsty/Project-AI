"""
Stage 6: Memory — Ledger Append, Block Sealing, and Feedback.

The final stage in the Waterfall pipeline:
    1. Constructs an ExecutionRecord from the pipeline results
    2. Appends it to the in-memory ledger
    3. Seals blocks when the batch threshold is reached
    4. Updates threat fingerprints (if denied) or baselines (if allowed)
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from psia.schemas.identity import Signature
from psia.schemas.ledger import (
    ExecutionRecord,
    LedgerBlock,
    RecordTimestamps,
    TimeProof,
)
from psia.waterfall.engine import StageDecision, StageResult, WaterfallStage

logger = logging.getLogger(__name__)


class InMemoryLedger:
    """Phase 1 in-memory append-only ledger.

    In production, this would be durable (WAL + fsync) with
    replication and external Merkle anchoring via
    ``ExternalMerkleAnchor``.
    """

    def __init__(self, *, block_size: int = 100) -> None:
        self._records: list[ExecutionRecord] = []
        self._record_hashes: list[str] = []
        self._blocks: list[LedgerBlock] = []
        self._block_size = block_size

    def append(self, record: ExecutionRecord) -> str:
        """Append a record to the ledger.

        Args:
            record: The execution record to append

        Returns:
            SHA-256 hash of the record
        """
        record_hash = record.compute_hash()
        self._records.append(record)
        self._record_hashes.append(record_hash)

        # Check if we should seal a block
        if len(self._record_hashes) >= self._block_size:
            self._seal_block()

        return record_hash

    def _seal_block(self) -> LedgerBlock:
        """Seal the current batch of records into a block."""
        hashes_to_seal = list(self._record_hashes)
        self._record_hashes.clear()

        merkle_root = LedgerBlock.compute_merkle_root(hashes_to_seal)
        height = len(self._blocks)
        prev_hash = self._blocks[-1].compute_hash() if self._blocks else ""

        block = LedgerBlock(
            height=height,
            previous_block_hash=prev_hash,
            merkle_root=merkle_root,
            records=hashes_to_seal,
            time_proof=TimeProof(method="rfc3161", proof=""),
            validator_signatures=[
                Signature(alg="ed25519", kid="ledger_k1", sig="block_seal_sig"),
            ],
        )
        self._blocks.append(block)
        logger.info(
            "Sealed ledger block height=%d records=%d", height, len(hashes_to_seal)
        )
        return block

    @property
    def record_count(self) -> int:
        """Total number of records in the ledger."""
        return len(self._records)

    @property
    def block_count(self) -> int:
        """Number of sealed blocks."""
        return len(self._blocks)

    @property
    def pending_records(self) -> int:
        """Number of records not yet sealed into a block."""
        return len(self._record_hashes)

    def get_record(self, record_id: str) -> ExecutionRecord | None:
        """Look up a record by ID."""
        for r in self._records:
            if r.record_id == record_id:
                return r
        return None

    def get_block(self, height: int) -> LedgerBlock | None:
        """Look up a block by height."""
        if 0 <= height < len(self._blocks):
            return self._blocks[height]
        return None

    def force_seal(self) -> LedgerBlock | None:
        """Force-seal the current pending records."""
        if self._record_hashes:
            return self._seal_block()
        return None


class MemoryStage:
    """Stage 6: Ledger append + feedback.

    Constructs an ExecutionRecord from the pipeline results and
    appends it to the ledger.  Also updates baseline and threat
    fingerprint stores via callback hooks.
    """

    def __init__(
        self,
        *,
        ledger: InMemoryLedger | None = None,
        on_deny_callback: Any | None = None,
        on_allow_callback: Any | None = None,
    ) -> None:
        self.ledger = ledger or InMemoryLedger()
        self._on_deny = on_deny_callback
        self._on_allow = on_allow_callback

    def evaluate(self, envelope, prior_results: list[StageResult]) -> StageResult:
        """Append execution record to the ledger.

        Args:
            envelope: RequestEnvelope (source of actor, token ID)
            prior_results: Results from prior stages

        Returns:
            StageResult with record hash and block info in metadata
        """
        # Gather hashes from prior stages
        shadow_hash = ""
        decision_hash = ""
        canonical_diff_hash = ""
        final_result = "allow"

        for pr in prior_results:
            if "shadow_hash" in pr.metadata:
                shadow_hash = pr.metadata["shadow_hash"]
            if "cerberus_decision" in pr.metadata:
                cd = pr.metadata["cerberus_decision"]
                decision_hash = cd.compute_hash() if hasattr(cd, "compute_hash") else ""
                final_result = (
                    cd.final_decision if hasattr(cd, "final_decision") else "allow"
                )
            if "canonical_diff_hash" in pr.metadata:
                canonical_diff_hash = pr.metadata["canonical_diff_hash"]

        # Compute inputs_hash
        inputs_data = json.dumps(
            {"request_hash": envelope.compute_hash(), "action": envelope.intent.action},
            sort_keys=True,
            separators=(",", ":"),
        )
        inputs_hash = hashlib.sha256(inputs_data.encode()).hexdigest()

        now = datetime.now(timezone.utc).isoformat()

        record = ExecutionRecord(
            record_id=f"rec_{uuid.uuid4().hex[:12]}",
            request_id=envelope.request_id,
            actor=envelope.actor,
            capability_token_id=envelope.capability_token_id,
            inputs_hash=inputs_hash,
            shadow_hash=shadow_hash,
            decision_hash=decision_hash,
            canonical_diff_hash=canonical_diff_hash,
            result=final_result,
            timestamps=RecordTimestamps(
                received_at=envelope.timestamps.received_at or now,
                decided_at=now,
                committed_at=now,
            ),
            signature=Signature(alg="ed25519", kid="ledger_k1", sig="record_sig"),
        )

        record_hash = self.ledger.append(record)

        # Fire callbacks
        if final_result in ("deny", "quarantine") and self._on_deny:
            try:
                self._on_deny(envelope, final_result)
            except Exception:
                logger.exception("on_deny callback failed")
        elif final_result == "allow" and self._on_allow:
            try:
                self._on_allow(envelope)
            except Exception:
                logger.exception("on_allow callback failed")

        return StageResult(
            stage=WaterfallStage.MEMORY,
            decision=StageDecision.ALLOW,
            reasons=[
                f"ledger appended record={record.record_id}",
                f"ledger total_records={self.ledger.record_count}",
                f"pending_for_seal={self.ledger.pending_records}",
            ],
            metadata={
                "record_id": record.record_id,
                "record_hash": record_hash,
                "ledger_record_count": self.ledger.record_count,
                "ledger_block_count": self.ledger.block_count,
            },
        )


__all__ = ["InMemoryLedger", "MemoryStage"]
