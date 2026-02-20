"""Collapse scheduler for deterministic collapse event scheduling.

Schedules and manages collapse events based on state conditions.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..schemas.state_schema import StateVector

logger = logging.getLogger(__name__)


@dataclass
class ScheduledCollapse:
    """Scheduled collapse event."""

    trigger_time: float
    collapse_type: str
    severity: float
    triggered: bool = False
    trigger_state: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "trigger_time": self.trigger_time,
            "collapse_type": self.collapse_type,
            "severity": self.severity,
            "triggered": self.triggered,
            "trigger_state": self.trigger_state,
        }


class CollapseScheduler:
    """Deterministic collapse event scheduler.

    Monitors state conditions and triggers collapse events when thresholds are crossed.
    """

    def __init__(self):
        """Initialize collapse scheduler."""
        self.scheduled_collapses: list[ScheduledCollapse] = []
        self.triggered_collapses: list[ScheduledCollapse] = []
        self.collapse_callbacks: dict[str, list[Callable]] = {}

        # Thresholds for automatic scheduling
        self.auto_schedule_thresholds = {
            "kindness_singularity": 0.2,
            "trust_collapse": 0.15,
            "moral_injury_critical": 0.85,
            "legitimacy_failure": 0.1,
            "epistemic_collapse": 0.2,
        }

        logger.info("Collapse scheduler initialized")

    def schedule_collapse(
        self,
        trigger_time: float,
        collapse_type: str,
        severity: float = 0.5,
    ) -> ScheduledCollapse:
        """Schedule a collapse event for future trigger.

        Args:
            trigger_time: Simulation time to trigger collapse
            collapse_type: Type of collapse event
            severity: Collapse severity (0.0 to 1.0)

        Returns:
            ScheduledCollapse instance
        """
        collapse = ScheduledCollapse(
            trigger_time=trigger_time,
            collapse_type=collapse_type,
            severity=severity,
        )

        self.scheduled_collapses.append(collapse)
        self.scheduled_collapses.sort(key=lambda c: c.trigger_time)

        logger.info(
            "Scheduled collapse: %s at t=%s, severity=%s",
            collapse_type,
            trigger_time,
            severity,
        )
        return collapse

    def register_callback(self, collapse_type: str, callback: Callable) -> None:
        """Register callback for collapse type.

        Args:
            collapse_type: Type of collapse to watch
            callback: Function to call when collapse triggers
        """
        if collapse_type not in self.collapse_callbacks:
            self.collapse_callbacks[collapse_type] = []

        self.collapse_callbacks[collapse_type].append(callback)
        logger.debug("Registered callback for %s", collapse_type)

    def check_thresholds(self, state: StateVector) -> list[str]:
        """Check if any collapse thresholds have been crossed.

        Args:
            state: Current state vector

        Returns:
            List of collapse types triggered
        """
        triggered = []

        # Check kindness singularity
        if state.kindness.value < self.auto_schedule_thresholds["kindness_singularity"]:
            if not any(c.collapse_type == "kindness_singularity" and c.triggered for c in self.triggered_collapses):
                triggered.append("kindness_singularity")

        # Check trust collapse
        if state.trust.value < self.auto_schedule_thresholds["trust_collapse"]:
            if not any(c.collapse_type == "trust_collapse" and c.triggered for c in self.triggered_collapses):
                triggered.append("trust_collapse")

        # Check moral injury critical
        if (state.moral_injury.value > self.auto_schedule_thresholds["moral_injury_critical"]) and not any(
            c.collapse_type == "moral_injury_critical" and c.triggered for c in self.triggered_collapses
        ):
            triggered.append("moral_injury_critical")

        # Check legitimacy failure
        if state.legitimacy.value < self.auto_schedule_thresholds["legitimacy_failure"]:
            if not any(c.collapse_type == "legitimacy_failure" and c.triggered for c in self.triggered_collapses):
                triggered.append("legitimacy_failure")

        # Check epistemic collapse
        if (state.epistemic_confidence.value < self.auto_schedule_thresholds["epistemic_collapse"]) and not any(
            c.collapse_type == "epistemic_collapse" and c.triggered for c in self.triggered_collapses
        ):
            triggered.append("epistemic_collapse")

        return triggered

    def process_tick(self, state: StateVector) -> list[ScheduledCollapse]:
        """Process collapse scheduler for current tick.

        Args:
            state: Current state vector

        Returns:
            List of collapses triggered this tick
        """
        triggered_this_tick = []

        # Check scheduled collapses
        for collapse in self.scheduled_collapses:
            if not collapse.triggered and state.timestamp >= collapse.trigger_time:
                self._trigger_collapse(collapse, state)
                triggered_this_tick.append(collapse)

        # Check automatic thresholds
        auto_triggered = self.check_thresholds(state)
        for collapse_type in auto_triggered:
            collapse = ScheduledCollapse(
                trigger_time=state.timestamp,
                collapse_type=collapse_type,
                severity=1.0,
                triggered=True,
            )
            self._trigger_collapse(collapse, state)
            triggered_this_tick.append(collapse)

        return triggered_this_tick

    def _trigger_collapse(self, collapse: ScheduledCollapse, state: StateVector) -> None:
        """Trigger a collapse event.

        Args:
            collapse: Collapse to trigger
            state: Current state vector
        """
        collapse.triggered = True
        collapse.trigger_state = state.to_dict()
        self.triggered_collapses.append(collapse)

        # Mark state as in collapse
        if not state.in_collapse:
            state.in_collapse = True
            state.collapse_triggered_at = state.timestamp

        logger.critical(
            "COLLAPSE TRIGGERED: %s at t=%s, severity=%s",
            collapse.collapse_type,
            state.timestamp,
            collapse.severity,
        )

        # Execute callbacks
        if collapse.collapse_type in self.collapse_callbacks:
            for callback in self.collapse_callbacks[collapse.collapse_type]:
                try:
                    callback(collapse, state)
                except Exception as e:
                    logger.error("Collapse callback error: %s", e, exc_info=True)

    def get_next_scheduled(self) -> ScheduledCollapse | None:
        """Get next scheduled collapse event.

        Returns:
            Next scheduled collapse or None
        """
        for collapse in self.scheduled_collapses:
            if not collapse.triggered:
                return collapse
        return None

    def get_triggered_count(self) -> int:
        """Get count of triggered collapses.

        Returns:
            Number of triggered collapses
        """
        return len(self.triggered_collapses)

    def get_summary(self) -> dict[str, Any]:
        """Get scheduler summary.

        Returns:
            Dictionary with scheduler state
        """
        return {
            "scheduled_count": len(self.scheduled_collapses),
            "triggered_count": len(self.triggered_collapses),
            "pending_count": sum(1 for c in self.scheduled_collapses if not c.triggered),
            "collapse_types_triggered": list({c.collapse_type for c in self.triggered_collapses}),
        }

    def export_collapses(self) -> dict[str, list[dict[str, Any]]]:
        """Export all collapse events.

        Returns:
            Dictionary with scheduled and triggered collapses
        """
        return {
            "scheduled": [c.to_dict() for c in self.scheduled_collapses],
            "triggered": [c.to_dict() for c in self.triggered_collapses],
        }

    def reset(self) -> None:
        """Reset scheduler to initial state."""
        self.__init__()
        logger.info("Collapse scheduler reset")
