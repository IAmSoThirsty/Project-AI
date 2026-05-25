"""PSIA Waterfall Stage 5 — canonical commit."""
from __future__ import annotations

from typing import Any

from psia.waterfall.engine import StageDecision, StageResult, WaterfallStage


class InMemoryCanonicalStore:
    def __init__(self) -> None:
        self._version = 0
        self._data: dict[str, Any] = {}

    @property
    def version(self) -> int:
        return self._version

    def commit(self, key: str, value: Any) -> int:
        self._data[key] = value
        self._version += 1
        return self._version


class CommitStage:
    def __init__(self, store: InMemoryCanonicalStore | None = None) -> None:
        self._store = store or InMemoryCanonicalStore()

    def evaluate(self, envelope: Any, prior_results: list[StageResult]) -> StageResult:
        gate_result = next(
            (r for r in prior_results if r.stage == WaterfallStage.GATE), None
        )
        if gate_result is None:
            return StageResult(
                stage=WaterfallStage.COMMIT,
                decision=StageDecision.DENY,
                reasons=["No gate stage result — commit blocked"],
            )

        cerberus = gate_result.metadata.get("cerberus_decision")
        if cerberus is None or cerberus.final_decision != "allow":
            return StageResult(
                stage=WaterfallStage.COMMIT,
                decision=StageDecision.DENY,
                reasons=["Cerberus did not allow — commit blocked"],
            )

        resource = envelope.intent.resource
        value = envelope.intent.parameters
        diff_hash = self._store.commit(resource, value)

        return StageResult(
            stage=WaterfallStage.COMMIT,
            decision=StageDecision.ALLOW,
            metadata={"canonical_diff_hash": str(diff_hash)},
        )
