"""PSIA Waterfall Stage 2 — behavioral baseline deviation."""
from __future__ import annotations

from typing import Any

from psia.waterfall.engine import StageDecision, StageResult, WaterfallStage


class BaselineProfileStore:
    def __init__(self) -> None:
        self._history: dict[str, list[tuple[str, str]]] = {}

    def record_request(self, actor: str, action: str, resource: str) -> None:
        if actor not in self._history:
            self._history[actor] = []
        self._history[actor].append((action, resource))

    def get_history(self, actor: str) -> list[tuple[str, str]]:
        return self._history.get(actor, [])


class BehavioralStage:
    def __init__(
        self,
        store: BaselineProfileStore | None = None,
        escalation_threshold: float = 0.5,
    ) -> None:
        self._store = store or BaselineProfileStore()
        self._threshold = escalation_threshold

    def evaluate(self, envelope: Any, prior_results: list[StageResult]) -> StageResult:
        actor = envelope.actor
        action = envelope.intent.action
        resource = envelope.intent.resource

        history = self._store.get_history(actor)
        if not history:
            return StageResult(stage=WaterfallStage.BEHAVIORAL, decision=StageDecision.ALLOW)

        matching = sum(
            1 for (hist_action, hist_resource) in history
            if hist_action == action and hist_resource == resource
        )
        familiarity = matching / len(history)

        if familiarity < self._threshold:
            return StageResult(
                stage=WaterfallStage.BEHAVIORAL,
                decision=StageDecision.ESCALATE,
                reasons=[f"Novel behavior: familiarity={familiarity:.2f} < threshold={self._threshold}"],
            )

        return StageResult(stage=WaterfallStage.BEHAVIORAL, decision=StageDecision.ALLOW)
