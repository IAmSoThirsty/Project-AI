"""
PSIA Waterfall Engine — sequential 7-stage pipeline orchestrator.

Implements the core Waterfall lifecycle from §4 of the PSIA v1.0 specification.

The Waterfall engine processes a RequestEnvelope through 7 stages in
strict order.  Each stage produces a StageResult; the pipeline aborts
immediately on deny/quarantine.  Severity is monotonically non-decreasing
across stages (INV-ROOT-7).

Stages:
    0. Structural   — schema validation, token checks
    1. Signature     — threat fingerprint matching
    2. Behavioral    — baseline deviation scoring
    3. Shadow        — deterministic simulation
    4. Gate          — Cerberus triple-head evaluation
    5. Commit        — canonical mutation
    6. Memory        — ledger append + threat/baseline updates
"""

from __future__ import annotations

import enum
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from psia.events import EventBus, EventSeverity, EventType, create_event
from psia.schemas.cerberus_decision import CerberusDecision
from psia.schemas.request import RequestEnvelope

logger = logging.getLogger(__name__)


class WaterfallStage(int, enum.Enum):
    """Stage ordinals in the Waterfall pipeline."""

    STRUCTURAL = 0
    SIGNATURE = 1
    BEHAVIORAL = 2
    SHADOW = 3
    GATE = 4
    COMMIT = 5
    MEMORY = 6


class StageDecision(str, enum.Enum):
    """Decision at each stage boundary."""

    ALLOW = "allow"
    DENY = "deny"
    QUARANTINE = "quarantine"
    ESCALATE = "escalate"


# Severity ordering for INV-ROOT-7 monotonic strictness
_SEVERITY_ORDER = {"allow": 0, "escalate": 1, "quarantine": 2, "deny": 3}


@dataclass
class StageResult:
    """Output of a single Waterfall stage."""

    stage: WaterfallStage
    decision: StageDecision
    reasons: list[str] = field(default_factory=list)
    duration_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def severity_rank(self) -> int:
        """Numerical severity rank (higher = more restrictive)."""
        return _SEVERITY_ORDER.get(self.decision.value, 0)


@dataclass
class WaterfallResult:
    """Aggregate output of the full Waterfall pipeline."""

    request_id: str
    final_decision: StageDecision
    stage_results: list[StageResult] = field(default_factory=list)
    cerberus_decision: CerberusDecision | None = None
    total_duration_ms: float = 0.0
    aborted_at_stage: WaterfallStage | None = None
    reasoning_entry_id: str | None = None

    @property
    def is_allowed(self) -> bool:
        """Return True if the final decision is allow."""
        return self.final_decision == StageDecision.ALLOW


class WaterfallEngine:
    """Sequential 7-stage pipeline orchestrator.

    The engine holds references to stage implementations and an event bus.
    Each stage is a callable accepting ``(RequestEnvelope, list[StageResult])``
    and returning a ``StageResult``.  Stages are injected at construction time.

    Usage::

        engine = WaterfallEngine(
            event_bus=bus,
            structural_stage=StructuralStage(),
            signature_stage=SignatureStage(),
            behavioral_stage=BehavioralStage(),
            shadow_stage=ShadowStage(),
            gate_stage=GateStage(),
            commit_stage=CommitStage(),
            memory_stage=MemoryStage(),
        )
        result = engine.process(envelope)
    """

    def __init__(
        self,
        *,
        event_bus: EventBus | None = None,
        structural_stage: Any = None,
        signature_stage: Any = None,
        behavioral_stage: Any = None,
        shadow_stage: Any = None,
        gate_stage: Any = None,
        commit_stage: Any = None,
        memory_stage: Any = None,
        reasoning_matrix: Any = None,
    ) -> None:
        self.event_bus = event_bus or EventBus()
        self._matrix = reasoning_matrix
        self._stages: list[tuple[WaterfallStage, Any]] = [
            (WaterfallStage.STRUCTURAL, structural_stage),
            (WaterfallStage.SIGNATURE, signature_stage),
            (WaterfallStage.BEHAVIORAL, behavioral_stage),
            (WaterfallStage.SHADOW, shadow_stage),
            (WaterfallStage.GATE, gate_stage),
            (WaterfallStage.COMMIT, commit_stage),
            (WaterfallStage.MEMORY, memory_stage),
        ]

    def process(self, envelope: RequestEnvelope) -> WaterfallResult:
        """Run the full Waterfall pipeline on a request envelope.

        Stages execute sequentially.  The pipeline aborts immediately
        when any stage returns ``deny`` or ``quarantine``.  Severity
        is enforced to be monotonically non-decreasing (INV-ROOT-7).

        Args:
            envelope: The incoming request

        Returns:
            WaterfallResult with all stage results and final decision
        """
        start_time = time.monotonic()
        stage_results: list[StageResult] = []
        request_id = envelope.request_id

        # Emit waterfall start event
        self.event_bus.emit(
            create_event(
                EventType.WATERFALL_START,
                trace_id=envelope.context.trace_id,
                request_id=request_id,
                subject=envelope.subject,
                severity=EventSeverity.INFO,
                payload={"actor": envelope.actor, "action": envelope.intent.action},
            )
        )

        max_severity_rank = 0
        final_decision = StageDecision.ALLOW
        aborted_at: WaterfallStage | None = None
        cerberus_decision: CerberusDecision | None = None

        # Begin reasoning trace (if matrix available)
        rm_entry_id = None
        if self._matrix:
            rm_entry_id = self._matrix.begin_reasoning(
                "waterfall_pipeline",
                {"request_id": request_id},
            )

        for stage_enum, stage_impl in self._stages:
            if stage_impl is None:
                # Stage not configured — skip (allows incremental integration)
                logger.debug("Stage %s not configured, skipping", stage_enum.name)
                continue

            # Emit stage enter
            self.event_bus.emit(
                create_event(
                    EventType.STAGE_ENTER,
                    trace_id=envelope.context.trace_id,
                    request_id=request_id,
                    subject=envelope.subject,
                    severity=EventSeverity.DEBUG,
                    payload={
                        "stage": stage_enum.name,
                        "stage_ordinal": stage_enum.value,
                    },
                )
            )

            stage_start = time.monotonic()
            try:
                result: StageResult = stage_impl.evaluate(envelope, stage_results)
            except Exception as exc:
                logger.exception("Stage %s failed with exception", stage_enum.name)
                result = StageResult(
                    stage=stage_enum,
                    decision=StageDecision.DENY,
                    reasons=[f"Stage {stage_enum.name} exception: {exc}"],
                    duration_ms=(time.monotonic() - stage_start) * 1000,
                )

            result.duration_ms = (time.monotonic() - stage_start) * 1000
            stage_results.append(result)

            # INV-ROOT-7: monotonic strictness — severity can only increase
            if result.severity_rank < max_severity_rank:
                logger.error(
                    "INV-ROOT-7 violation: severity downgrade at stage %s "
                    "(rank %d < max %d) — enforcing previous severity",
                    stage_enum.name,
                    result.severity_rank,
                    max_severity_rank,
                )
                # Do NOT downgrade — keep the most restrictive decision
            else:
                max_severity_rank = result.severity_rank
                final_decision = result.decision

            # Extract Cerberus decision if present (from gate stage)
            if "cerberus_decision" in result.metadata:
                cerberus_decision = result.metadata["cerberus_decision"]

            # Emit stage exit
            self.event_bus.emit(
                create_event(
                    EventType.STAGE_EXIT,
                    trace_id=envelope.context.trace_id,
                    request_id=request_id,
                    subject=envelope.subject,
                    severity=EventSeverity.DEBUG,
                    payload={
                        "stage": stage_enum.name,
                        "decision": result.decision.value,
                        "duration_ms": result.duration_ms,
                        "reasons": result.reasons,
                    },
                )
            )

            # Abort pipeline on deny or quarantine
            if result.decision in (StageDecision.DENY, StageDecision.QUARANTINE):
                aborted_at = stage_enum
                final_decision = result.decision
                # Record abort factor
                if self._matrix and rm_entry_id:
                    self._matrix.add_factor(
                        rm_entry_id,
                        f"stage_{stage_enum.name}_abort",
                        result.decision.value,
                        weight=1.0,
                        score=0.0,
                        source="waterfall",
                        rationale=(
                            f"Pipeline aborted at {stage_enum.name}: "
                            f"{'; '.join(result.reasons)}"
                        ),
                    )
                break
            else:
                # Record passing stage as factor
                if self._matrix and rm_entry_id:
                    # Score: allow=1.0, escalate=0.5
                    stage_score = 1.0 if result.decision == StageDecision.ALLOW else 0.5
                    self._matrix.add_factor(
                        rm_entry_id,
                        f"stage_{stage_enum.name}",
                        result.decision.value,
                        weight=0.8,
                        score=stage_score,
                        source="waterfall",
                        rationale=(
                            f"{stage_enum.name} → {result.decision.value}"
                            f"{': ' + '; '.join(result.reasons) if result.reasons else ''}"
                        ),
                    )

        total_duration_ms = (time.monotonic() - start_time) * 1000

        # Emit terminal event
        terminal_event_type = {
            StageDecision.ALLOW: EventType.REQUEST_ALLOWED,
            StageDecision.DENY: EventType.REQUEST_DENIED,
            StageDecision.QUARANTINE: EventType.REQUEST_QUARANTINED,
            StageDecision.ESCALATE: EventType.REQUEST_QUARANTINED,
        }[final_decision]

        self.event_bus.emit(
            create_event(
                terminal_event_type,
                trace_id=envelope.context.trace_id,
                request_id=request_id,
                subject=envelope.subject,
                severity=(
                    EventSeverity.WARNING
                    if final_decision != StageDecision.ALLOW
                    else EventSeverity.INFO
                ),
                payload={
                    "final_decision": final_decision.value,
                    "stages_completed": len(stage_results),
                    "total_duration_ms": total_duration_ms,
                },
            )
        )

        # Render reasoning verdict
        if self._matrix and rm_entry_id:
            # Map decision to confidence
            confidence_map = {
                StageDecision.ALLOW: 0.95,
                StageDecision.ESCALATE: 0.6,
                StageDecision.QUARANTINE: 0.85,
                StageDecision.DENY: 0.9,
            }
            self._matrix.render_verdict(
                rm_entry_id,
                decision=final_decision.value,
                confidence=confidence_map.get(final_decision, 0.7),
                explanation=(
                    f"Waterfall pipeline: {len(stage_results)} stage(s) "
                    f"completed, final={final_decision.value}"
                    f"{f', aborted at {aborted_at.name}' if aborted_at else ''}"
                ),
            )

        return WaterfallResult(
            request_id=request_id,
            final_decision=final_decision,
            stage_results=stage_results,
            cerberus_decision=cerberus_decision,
            total_duration_ms=total_duration_ms,
            aborted_at_stage=aborted_at,
            reasoning_entry_id=rm_entry_id,
        )


__all__ = [
    "WaterfallStage",
    "StageDecision",
    "StageResult",
    "WaterfallResult",
    "WaterfallEngine",
]
