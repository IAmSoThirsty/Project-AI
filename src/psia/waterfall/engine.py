"""PSIA waterfall engine — 7-stage sequential pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

from psia.events import EventBus, EventType, create_event


class WaterfallStage(IntEnum):
    STRUCTURAL = 0
    SIGNATURE = 1
    BEHAVIORAL = 2
    SHADOW = 3
    GATE = 4
    COMMIT = 5
    MEMORY = 6


class StageDecision(str):
    ALLOW = "allow"
    DENY = "deny"
    QUARANTINE = "quarantine"
    ESCALATE = "escalate"

    def __new__(cls, value: str) -> "StageDecision":
        return str.__new__(cls, value)

    def __eq__(self, other: object) -> bool:
        return str.__eq__(self, other)

    def __hash__(self) -> int:
        return str.__hash__(self)


StageDecision.ALLOW = StageDecision("allow")
StageDecision.DENY = StageDecision("deny")
StageDecision.QUARANTINE = StageDecision("quarantine")
StageDecision.ESCALATE = StageDecision("escalate")

_SEVERITY_RANKS: dict[str, int] = {
    "allow": 0,
    "escalate": 1,
    "quarantine": 2,
    "deny": 3,
}

_ABORT_DECISIONS = {"deny", "quarantine"}


@dataclass
class StageResult:
    stage: WaterfallStage
    decision: Any
    reasons: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    duration_ms: float = 0.0

    @property
    def severity_rank(self) -> int:
        v = str(self.decision)
        return _SEVERITY_RANKS.get(v, 0)


class WaterfallResult:
    def __init__(
        self,
        is_allowed: bool | None = None,
        stage_results: list[StageResult] | None = None,
        aborted_at_stage: WaterfallStage | None = None,
        cerberus_decision: Any = None,
        request_id: str = "",
        final_decision: Any = None,
    ) -> None:
        self.request_id = request_id
        self.final_decision = final_decision
        self.stage_results = stage_results if stage_results is not None else []
        self.aborted_at_stage = aborted_at_stage
        self.cerberus_decision = cerberus_decision
        self._is_allowed_direct = is_allowed

    @property
    def is_allowed(self) -> bool:
        if self._is_allowed_direct is not None:
            return self._is_allowed_direct
        if self.final_decision is not None:
            return str(self.final_decision) == "allow"
        return True


class WaterfallEngine:
    def __init__(
        self,
        structural_stage: Any = None,
        signature_stage: Any = None,
        behavioral_stage: Any = None,
        shadow_stage: Any = None,
        gate_stage: Any = None,
        commit_stage: Any = None,
        memory_stage: Any = None,
        event_bus: EventBus | None = None,
    ) -> None:
        self._stages = [
            (WaterfallStage.STRUCTURAL, structural_stage),
            (WaterfallStage.SIGNATURE, signature_stage),
            (WaterfallStage.BEHAVIORAL, behavioral_stage),
            (WaterfallStage.SHADOW, shadow_stage),
            (WaterfallStage.GATE, gate_stage),
            (WaterfallStage.COMMIT, commit_stage),
            (WaterfallStage.MEMORY, memory_stage),
        ]
        self._bus = event_bus

    @property
    def event_bus(self) -> EventBus | None:
        return self._bus

    def _emit(self, event_type: EventType, **kwargs: Any) -> None:
        if self._bus is not None:
            self._bus.emit(create_event(event_type, **kwargs))

    def _call_stage(self, stage_impl: Any, envelope: Any, results: list[StageResult]) -> StageResult:
        if hasattr(stage_impl, "process"):
            return stage_impl.process(envelope, results)
        return stage_impl.evaluate(envelope, results)

    def process(self, envelope: Any) -> WaterfallResult:
        request_id = getattr(envelope, "request_id", "")
        self._emit(EventType.WATERFALL_START, request_id=request_id)
        results: list[StageResult] = []
        aborted_at: WaterfallStage | None = None
        cerberus_decision = None

        for stage_enum, stage_impl in self._stages:
            if stage_impl is None:
                results.append(StageResult(stage=stage_enum, decision=StageDecision.ALLOW))
                continue
            self._emit(EventType.STAGE_ENTER, stage=stage_enum, request_id=request_id)
            result = self._call_stage(stage_impl, envelope, results)
            results.append(result)
            self._emit(EventType.STAGE_EXIT, stage=stage_enum, decision=result.decision, request_id=request_id)

            if stage_enum == WaterfallStage.GATE:
                cerberus_decision = result.metadata.get("cerberus_decision")

            if str(result.decision) in _ABORT_DECISIONS:
                aborted_at = stage_enum
                break

        is_allowed = aborted_at is None
        if is_allowed:
            self._emit(EventType.REQUEST_ALLOWED, request_id=request_id)
        else:
            self._emit(EventType.REQUEST_DENIED, request_id=request_id)

        return WaterfallResult(
            is_allowed=is_allowed,
            stage_results=results,
            aborted_at_stage=aborted_at,
            cerberus_decision=cerberus_decision,
        )
