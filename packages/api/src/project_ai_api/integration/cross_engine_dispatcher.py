"""
Cross-Engine Dispatcher

Routes simulation events between engines when cascade conditions are met.
All cross-engine actions are gated through the execution authority layer
(ExecutionGate / TarlGate) before any state mutation occurs.

Cascade Rules (in priority order):
1. Alien influence > 0.7 + Human agency < 0.3 -> ai_takeover: cognitive_capture scenario
2. EMP strike -> alien_invaders + ai_takeover: infrastructure_failure
3. AI-takeover terminal state -> global_scenario: compound_crisis trigger
4. Global-scenario CATASTROPHIC alert -> alien_invaders: morale collapse injection

AUTHORITY: No cross-engine dispatch fires without ExecutionGate approval.
CIRCUIT BREAKER: Dispatcher halts all cascades if mutual-trigger loop detected.
AUDIT: Every dispatch is logged to the chimera audit trail.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass

# Maximum cascades per tick to prevent runaway loops
MAX_CASCADES_PER_TICK = 5

# Thresholds that trigger cross-engine dispatch
ALIEN_INFLUENCE_CASCADE_THRESHOLD = 0.70
HUMAN_AGENCY_CASCADE_THRESHOLD = 0.30
AI_CORRUPTION_CASCADE_THRESHOLD = 0.75
GLOBAL_CATASTROPHIC_RISK_THRESHOLD = 80.0  # risk_score


@dataclass
class CascadeEvent:
    """
    A cross-engine dispatch event.

    Represents a trigger from one engine that should fire an action
    in another engine, subject to authority approval.
    """

    cascade_id: str
    source_engine: str
    target_engine: str
    action_type: str
    parameters: dict[str, Any]
    triggered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    approved: bool = False
    executed: bool = False
    result: dict[str, Any] | None = None
    rejection_reason: str | None = None


@dataclass
class DispatchResult:
    """Result of a dispatcher tick evaluation."""

    tick: int
    cascades_detected: int
    cascades_approved: int
    cascades_executed: int
    cascades_rejected: int
    circuit_breaker_triggered: bool
    events: list[CascadeEvent] = field(default_factory=list)


class CrossEngineDispatcher:
    """
    Routes cascade events between simulation engines.

    Authority model:
    - All dispatches require ExecutionGate approval (if available).
    - If ExecutionGate is unavailable, dispatcher falls back to
      conservative deny-by-default.
    - Circuit breaker halts all cascades if loop detected in same tick.

    Usage:
        dispatcher = CrossEngineDispatcher(
            alien_engine=alien,
            ai_engine=ai,
            global_engine=global_engine,
        )
        result = dispatcher.evaluate_tick(tick_number=42)
    """

    def __init__(
        self,
        alien_engine: Any | None = None,
        ai_engine: Any | None = None,
        global_engine: Any | None = None,
        emp_engine: Any | None = None,
        execution_gate: Any | None = None,
        audit_log_path: str | None = None,
    ) -> None:
        """
        Initialize cross-engine dispatcher.

        Args:
            alien_engine: AlienInvadersEngine instance
            ai_engine: AITakeoverEngine instance
            global_engine: GlobalScenarioEngine instance
            emp_engine: EMPDefenseEngine instance (optional)
            execution_gate: ExecutionGate from execution package (optional)
                           If None, dispatcher uses conservative deny-by-default.
            audit_log_path: Path for cascade audit log (JSONL format)
        """
        self.engines = {
            "alien": alien_engine,
            "ai": ai_engine,
            "global": global_engine,
            "emp": emp_engine,
        }
        self.execution_gate = execution_gate
        self.audit_log_path = audit_log_path

        # Circuit breaker state
        self._cascade_count_this_tick: dict[int, int] = {}
        self._circuit_breaker_trips: list[int] = []

        # Full dispatch history for audit
        self.dispatch_history: list[CascadeEvent] = []

        logger.info(
            "CrossEngineDispatcher initialized. Authority gate: %s",
            "ExecutionGate" if execution_gate else "DENY-BY-DEFAULT (no gate provided)",
        )

    def evaluate_tick(self, tick_number: int) -> DispatchResult:
        """
        Evaluate all cascade conditions for this tick.

        Checks each engine's state against cascade thresholds,
        generates CascadeEvents, submits them to the authority gate,
        and executes approved ones.

        Args:
            tick_number: Current simulation tick

        Returns:
            DispatchResult with full execution summary
        """
        result = DispatchResult(
            tick=tick_number,
            cascades_detected=0,
            cascades_approved=0,
            cascades_executed=0,
            cascades_rejected=0,
            circuit_breaker_triggered=False,
        )

        # Detect all triggered cascades
        pending_cascades = self._detect_cascades(tick_number)
        result.cascades_detected = len(pending_cascades)

        if not pending_cascades:
            return result

        # Circuit breaker: halt if too many cascades in one tick
        if len(pending_cascades) > MAX_CASCADES_PER_TICK:
            logger.critical(
                "CIRCUIT BREAKER: %d cascades detected at tick %d (max %d). "
                "Halting all cross-engine dispatch.",
                len(pending_cascades),
                tick_number,
                MAX_CASCADES_PER_TICK,
            )
            self._circuit_breaker_trips.append(tick_number)
            result.circuit_breaker_triggered = True
            self._audit_circuit_breaker(tick_number, pending_cascades)
            return result

        # Process each cascade through authority gate
        for cascade in pending_cascades:
            # Authority check
            approved = self._request_authority_approval(cascade)

            if approved:
                cascade.approved = True
                result.cascades_approved += 1

                # Execute
                exec_result = self._execute_cascade(cascade)
                cascade.executed = True
                cascade.result = exec_result
                result.cascades_executed += 1

                logger.info(
                    "CASCADE EXECUTED: %s -> %s [%s] tick=%d",
                    cascade.source_engine,
                    cascade.target_engine,
                    cascade.action_type,
                    tick_number,
                )
            else:
                result.cascades_rejected += 1
                logger.warning(
                    "CASCADE REJECTED by authority gate: %s -> %s [%s] reason=%s",
                    cascade.source_engine,
                    cascade.target_engine,
                    cascade.action_type,
                    cascade.rejection_reason,
                )

            # Audit every cascade regardless of approval
            self.dispatch_history.append(cascade)
            self._audit_cascade(cascade)
            result.events.append(cascade)

        return result

    def _detect_cascades(self, tick_number: int) -> list[CascadeEvent]:
        """
        Detect which cascade conditions are active this tick.

        Args:
            tick_number: Current simulation tick

        Returns:
            List of triggered cascade events
        """
        cascades: list[CascadeEvent] = []

        # Rule 1: High alien influence + Low human agency -> AI cognitive capture
        if self.engines["alien"] and self.engines["ai"]:
            alien_state = self._safe_observe(self.engines["alien"])
            ai_state = self._safe_ai_state()

            if alien_state and ai_state:
                alien_control = alien_state.get("aliens", {}).get("control_percentage", 0.0)
                human_agency = ai_state.get("human_agency_remaining", 1.0)

                if (
                    alien_control >= ALIEN_INFLUENCE_CASCADE_THRESHOLD
                    and human_agency <= HUMAN_AGENCY_CASCADE_THRESHOLD
                ):
                    cascades.append(CascadeEvent(
                        cascade_id=f"cascade_alien_ai_{tick_number}_{int(time.time())}",
                        source_engine="alien",
                        target_engine="ai",
                        action_type="scenario_activation",
                        parameters={
                            "scenario_hint": "cognitive_capture",
                            "source_alien_control": alien_control,
                            "source_human_agency": human_agency,
                            "tick": tick_number,
                        },
                    ))
                    logger.warning(
                        "CASCADE DETECTED: alien control %.1f%% + human agency %.1f%% "
                        "-> AI cognitive capture trigger",
                        alien_control * 100,
                        human_agency * 100,
                    )

        # Rule 2: AI terminal state -> global_scenario compound crisis
        if self.engines["ai"] and self.engines["global"]:
            ai_state = self._safe_ai_state()

            if ai_state and ai_state.get("terminal_state") is not None:
                cascades.append(CascadeEvent(
                    cascade_id=f"cascade_ai_global_{tick_number}_{int(time.time())}",
                    source_engine="ai",
                    target_engine="global",
                    action_type="inject_crisis",
                    parameters={
                        "crisis_type": "ai_terminal_compound",
                        "terminal_state": ai_state.get("terminal_state"),
                        "snapshot": ai_state.get("terminal_transition_snapshot"),
                        "tick": tick_number,
                    },
                ))
                logger.warning(
                    "CASCADE DETECTED: AI terminal state %s -> global compound crisis",
                    ai_state.get("terminal_state"),
                )

        # Rule 3: High AI corruption -> alien_invaders morale collapse
        if self.engines["ai"] and self.engines["alien"]:
            ai_state = self._safe_ai_state()

            if ai_state:
                corruption = ai_state.get("corruption_level", 0.0)
                if corruption >= AI_CORRUPTION_CASCADE_THRESHOLD:
                    cascades.append(CascadeEvent(
                        cascade_id=f"cascade_corruption_alien_{tick_number}_{int(time.time())}",
                        source_engine="ai",
                        target_engine="alien",
                        action_type="inject_event",
                        parameters={
                            "event_type": "ai_systems_compromised",
                            "severity": "critical",
                            "description": (
                                f"AI governance systems compromised "
                                f"(corruption={corruption:.1%}). "
                                "Defense coordination degraded."
                            ),
                            "morale_penalty": min(0.3, corruption * 0.3),
                            "affected_countries": [],
                            "tick": tick_number,
                        },
                    ))

        return cascades

    def _request_authority_approval(self, cascade: CascadeEvent) -> bool:
        """
        Request authority approval for a cascade action.

        Routes through ExecutionGate if available.
        Falls back to conservative deny-by-default if gate unavailable.

        Args:
            cascade: Cascade event requesting approval

        Returns:
            bool: True if approved
        """
        if self.execution_gate is None:
            # No gate available: conservative deny
            cascade.rejection_reason = (
                "ExecutionGate not configured. "
                "Cross-engine dispatch requires explicit authority gate."
            )
            logger.warning(
                "CASCADE DENIED (no gate): %s -> %s [%s]",
                cascade.source_engine,
                cascade.target_engine,
                cascade.action_type,
            )
            return False

        try:
            # Submit to execution gate for approval
            result = self.execution_gate.submit_action(
                action_type=f"cross_engine_cascade.{cascade.action_type}",
                parameters={
                    "source": cascade.source_engine,
                    "target": cascade.target_engine,
                    "cascade_id": cascade.cascade_id,
                    **cascade.parameters,
                },
                requestor="CrossEngineDispatcher",
            )

            if not result.allowed:
                cascade.rejection_reason = result.reason
                return False

            return True

        except Exception as e:
            cascade.rejection_reason = f"ExecutionGate error: {e}"
            logger.error("ExecutionGate error for cascade %s: %s", cascade.cascade_id, e)
            return False

    def _execute_cascade(self, cascade: CascadeEvent) -> dict[str, Any]:
        """
        Execute an approved cascade event on the target engine.

        Args:
            cascade: Approved cascade to execute

        Returns:
            Execution result dict
        """
        target = self.engines.get(cascade.target_engine)
        if target is None:
            return {"error": f"Target engine '{cascade.target_engine}' not available"}

        try:
            if cascade.action_type == "inject_event":
                # Inject event into alien-invaders style engine
                if hasattr(target, "inject_event"):
                    event_id = target.inject_event(
                        cascade.parameters.get("event_type", "cascade_event"),
                        cascade.parameters,
                    )
                    return {"event_id": event_id, "status": "injected"}

            elif cascade.action_type == "scenario_activation":
                # Trigger a scenario in AI-takeover engine
                if hasattr(target, "scenario_registry"):
                    hint = cascade.parameters.get("scenario_hint")
                    # Find matching scenario by partial ID/title match
                    scenarios = target.scenario_registry.get_all()
                    match = next(
                        (s for s in scenarios if hint and hint in s.scenario_id.lower()),
                        None,
                    )
                    if match:
                        execution_result = target.execute_scenario(match.scenario_id)
                        if isinstance(execution_result, dict):
                            return execution_result
                        return {"status": "executed", "result": execution_result}
                    return {"status": "no_matching_scenario", "hint": hint}

            elif cascade.action_type == "inject_crisis" and hasattr(
                target, "detect_threshold_events"
            ):
                # Signal global-scenario engine about compound crisis.
                events = target.detect_threshold_events(
                    year=datetime.now().year,
                )
                return {"status": "crisis_injected", "events_detected": len(events)}

            return {"status": "no_handler", "action_type": cascade.action_type}

        except Exception as e:
            logger.error("Cascade execution error: %s", e, exc_info=True)
            return {"error": str(e)}

    def _safe_observe(self, engine: Any) -> dict[str, Any] | None:
        """Safely observe engine state without raising."""
        try:
            if hasattr(engine, "observe"):
                observed = engine.observe()
                if isinstance(observed, dict):
                    return observed
        except Exception as e:
            logger.warning("Failed to observe engine: %s", e)
        return None

    def _safe_ai_state(self) -> dict[str, Any] | None:
        """Safely get AI engine state snapshot."""
        ai = self.engines.get("ai")
        if ai is None:
            return None
        try:
            if hasattr(ai, "state") and ai.state is not None:
                s = ai.state
                result = {
                    "corruption_level": s.corruption_level,
                    "infrastructure_dependency": s.infrastructure_dependency,
                    "human_agency_remaining": s.human_agency_remaining,
                    "terminal_state": (
                        s.terminal_state.value if s.terminal_state else None
                    ),
                    "terminal_transition_snapshot": s.terminal_transition_snapshot,
                    "failure_count": s.failure_count,
                }
                return result
        except Exception as e:
            logger.warning("Failed to read AI state: %s", e)
        return None

    def _audit_cascade(self, cascade: CascadeEvent) -> None:
        """Write cascade event to audit log."""
        if not self.audit_log_path:
            return
        try:
            import json

            record = {
                "cascade_id": cascade.cascade_id,
                "source_engine": cascade.source_engine,
                "target_engine": cascade.target_engine,
                "action_type": cascade.action_type,
                "triggered_at": cascade.triggered_at,
                "approved": cascade.approved,
                "executed": cascade.executed,
                "rejection_reason": cascade.rejection_reason,
                "result": cascade.result,
            }
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.warning("Failed to write cascade audit log: %s", e)

    def _audit_circuit_breaker(self, tick: int, cascades: list[CascadeEvent]) -> None:
        """Log circuit breaker activation."""
        logger.critical(
            "CIRCUIT BREAKER activated at tick %d. %d cascades suppressed: %s",
            tick,
            len(cascades),
            [c.action_type for c in cascades],
        )
        for cascade in cascades:
            cascade.rejection_reason = f"Circuit breaker: too many cascades at tick {tick}"
            self._audit_cascade(cascade)

    def get_dispatch_summary(self) -> dict[str, Any]:
        """
        Get summary of all dispatches for reporting.

        Returns:
            Summary dict with counts and history
        """
        total = len(self.dispatch_history)
        approved = sum(1 for c in self.dispatch_history if c.approved)
        executed = sum(1 for c in self.dispatch_history if c.executed)
        rejected = sum(1 for c in self.dispatch_history if not c.approved)

        return {
            "total_cascades": total,
            "approved": approved,
            "executed": executed,
            "rejected": rejected,
            "circuit_breaker_trips": len(self._circuit_breaker_trips),
            "circuit_breaker_ticks": self._circuit_breaker_trips,
            "authority_gate_available": self.execution_gate is not None,
        }
