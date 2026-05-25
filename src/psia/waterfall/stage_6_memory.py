"""PSIA Waterfall Stage 6 — memory/ledger append."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Callable

from psia.waterfall.engine import StageDecision, StageResult, WaterfallStage


class _LedgerRecord:
    def __init__(self, request_id: str, actor: str, decision: str) -> None:
        self.request_id = request_id
        self.actor = actor
        self.decision = decision

    def compute_hash(self) -> str:
        d = {"request_id": self.request_id, "actor": self.actor, "decision": self.decision}
        return hashlib.sha256(json.dumps(d, sort_keys=True).encode()).hexdigest()


class InMemoryLedger:
    def __init__(self, block_size: int = 100) -> None:
        self._block_size = block_size
        self._pending: list[_LedgerRecord] = []
        self._blocks: list[list[_LedgerRecord]] = []

    @property
    def record_count(self) -> int:
        return sum(len(b) for b in self._blocks) + len(self._pending)

    @property
    def block_count(self) -> int:
        return len(self._blocks)

    @property
    def pending_records(self) -> int:
        return len(self._pending)

    def append(self, record: _LedgerRecord) -> None:
        self._pending.append(record)
        if len(self._pending) >= self._block_size:
            self._blocks.append(list(self._pending))
            self._pending.clear()


class MemoryStage:
    def __init__(
        self,
        ledger: InMemoryLedger | None = None,
        on_deny_callback: Callable[[Any, str], None] | None = None,
    ) -> None:
        self._ledger = ledger or InMemoryLedger()
        self._on_deny_callback = on_deny_callback

    def evaluate(self, envelope: Any, prior_results: list[StageResult]) -> StageResult:
        gate_result = next(
            (r for r in prior_results if r.stage == WaterfallStage.GATE), None
        )
        final_decision = "allow"
        if gate_result is not None:
            cerberus = gate_result.metadata.get("cerberus_decision")
            if cerberus is not None:
                final_decision = cerberus.final_decision

        record = _LedgerRecord(
            request_id=envelope.request_id,
            actor=envelope.actor,
            decision=final_decision,
        )
        self._ledger.append(record)

        if final_decision != "allow" and self._on_deny_callback is not None:
            self._on_deny_callback(envelope, final_decision)

        return StageResult(
            stage=WaterfallStage.MEMORY,
            decision=StageDecision.ALLOW,
            metadata={"record_hash": record.compute_hash()},
        )
