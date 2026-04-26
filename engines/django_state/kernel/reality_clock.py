"""Reality clock with causal time tracking.

Implements time progression with irreversibility tracking and causal ordering.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CausalEvent:
    """Event with causal ordering information."""

    event_id: str
    timestamp: float
    causal_order: int
    parent_events: list[str] = field(default_factory=list)
    state_hash: str = ""
    irreversible: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "causal_order": self.causal_order,
            "parent_events": self.parent_events,
            "state_hash": self.state_hash,
            "irreversible": self.irreversible,
        }


class RealityClock:
    """Causal time tracking with irreversibility enforcement.

    Maintains causal ordering of events and tracks irreversible state transitions.
    """

    def __init__(self, start_time: float = 0.0, time_step: float = 1.0):
        """Initialize reality clock.

        Args:
            start_time: Initial simulation time
            time_step: Duration of each tick
        """
        self.current_time = start_time
        self.time_step = time_step
        self.tick_count = 0
        self.causal_order = 0

        # Causal chain tracking
        self.causal_chain: list[CausalEvent] = []
        self.event_index: dict[str, CausalEvent] = {}

        # Irreversibility tracking
        self.irreversible_events: list[str] = []
        self.state_checkpoints: dict[int, str] = {}  # tick -> state_hash

        # Metadata
        self.simulation_start = datetime.utcnow()
        self.real_time_elapsed = 0.0

        logger.info("Reality clock initialized at t=%s, step=%s", start_time, time_step)

    def tick(self) -> float:
        """Advance time by one step.

        Returns:
            New current time
        """
        self.current_time += self.time_step
        self.tick_count += 1

        logger.debug("Clock tick: t=%s, tick=%s", self.current_time, self.tick_count)
        return self.current_time

    def record_event(
        self,
        event_id: str,
        parent_events: list[str] | None = None,
        state_hash: str = "",
        irreversible: bool = True,
    ) -> CausalEvent:
        """Record event in causal chain.

        Args:
            event_id: Unique event identifier
            parent_events: List of parent event IDs (causal dependencies)
            state_hash: Hash of state after event
            irreversible: Whether event is irreversible

        Returns:
            CausalEvent instance
        """
        causal_event = CausalEvent(
            event_id=event_id,
            timestamp=self.current_time,
            causal_order=self.causal_order,
            parent_events=parent_events or [],
            state_hash=state_hash,
            irreversible=irreversible,
        )

        self.causal_chain.append(causal_event)
        self.event_index[event_id] = causal_event
        self.causal_order += 1

        if irreversible:
            self.irreversible_events.append(event_id)

        logger.debug(
            "Recorded event: %s at t=%s, order=%s",
            event_id,
            self.current_time,
            self.causal_order - 1,
        )
        return causal_event

    def checkpoint_state(self, state_hash: str) -> None:
        """Record state checkpoint for this tick.

        Args:
            state_hash: Hash of current state
        """
        self.state_checkpoints[self.tick_count] = state_hash
        logger.debug(
            "State checkpoint at tick %s: %s", self.tick_count, state_hash[:16]
        )

    def get_causal_ancestors(self, event_id: str) -> list[CausalEvent]:
        """Get all causal ancestors of an event.

        Args:
            event_id: Event to trace back from

        Returns:
            List of ancestor events in causal order
        """
        if event_id not in self.event_index:
            return []

        visited = set()
        ancestors = []
        queue = [event_id]

        while queue:
            current_id = queue.pop(0)
            if current_id in visited:
                continue

            visited.add(current_id)
            if current_id in self.event_index:
                event = self.event_index[current_id]
                ancestors.append(event)
                queue.extend(event.parent_events)

        # Sort by causal order
        ancestors.sort(key=lambda e: e.causal_order)
        return ancestors

    def verify_causal_consistency(self) -> tuple[bool, str]:
        """Verify causal chain consistency.

        Returns:
            Tuple of (is_consistent, error_message)
        """
        # Check causal order monotonicity
        for i in range(len(self.causal_chain) - 1):
            if (
                self.causal_chain[i].causal_order
                >= self.causal_chain[i + 1].causal_order
            ):
                return False, f"Causal order violation at index {i}"

        # Check parent references
        for event in self.causal_chain:
            for parent_id in event.parent_events:
                if parent_id not in self.event_index:
                    return False, f"Missing parent event: {parent_id}"
                parent = self.event_index[parent_id]
                if parent.causal_order >= event.causal_order:
                    return (
                        False,
                        f"Parent-child order violation: {parent_id} -> {event.event_id}",
                    )

        return True, ""

    def can_rewind_to(self, target_tick: int) -> tuple[bool, str]:
        """Check if time can be rewound to target tick.

        Rewinding is only possible if no irreversible events occurred after target.

        Args:
            target_tick: Target tick to rewind to

        Returns:
            Tuple of (can_rewind, reason)
        """
        if target_tick >= self.tick_count:
            return False, "Target tick is in the future or present"

        if target_tick < 0:
            return False, "Target tick is before simulation start"

        # Check for irreversible events after target
        for event in self.causal_chain:
            if event.timestamp > (target_tick * self.time_step):
                if event.irreversible:
                    return False, f"Irreversible event {event.event_id} blocks rewind"

        return True, ""

    def get_timeline_summary(self) -> dict[str, Any]:
        """Get summary of timeline state.

        Returns:
            Dictionary with timeline statistics
        """
        return {
            "current_time": self.current_time,
            "tick_count": self.tick_count,
            "causal_order": self.causal_order,
            "total_events": len(self.causal_chain),
            "irreversible_events": len(self.irreversible_events),
            "checkpoints": len(self.state_checkpoints),
            "simulation_duration": (
                datetime.utcnow() - self.simulation_start
            ).total_seconds(),
        }

    def export_causal_chain(self) -> list[dict[str, Any]]:
        """Export complete causal chain.

        Returns:
            List of causal events as dictionaries
        """
        return [event.to_dict() for event in self.causal_chain]

    def reset(self) -> None:
        """Reset clock to initial state."""
        start_time = self.current_time - (self.tick_count * self.time_step)
        self.__init__(start_time=start_time, time_step=self.time_step)
        logger.info("Reality clock reset")
