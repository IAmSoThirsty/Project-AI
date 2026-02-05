#!/usr/bin/env python3
"""
Causal Clock System
Provides logical time ordering for events to ensure deterministic replay.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CausalEvent:
    """
    Event with explicit causal ordering.

    Includes logical time to ensure deterministic replay regardless of
    physical timing or event injection order.
    """

    event_id: str
    event_type: str
    parameters: dict[str, Any]
    logical_time: int  # Causal clock value
    physical_time: datetime  # Wall clock time for logging
    tick_number: int  # Tick when event will execute
    severity: str = "medium"
    description: str = ""
    affected_countries: list[str] = field(default_factory=list)


class CausalClock:
    """
    Logical clock for event ordering.

    Ensures that event execution order is deterministic and independent
    of physical timing, dict iteration order, or external injection timing.
    """

    def __init__(self, initial_value: int = 0):
        """
        Initialize causal clock.

        Args:
            initial_value: Starting logical time value
        """
        self._logical_time = initial_value
        self._event_history: list[tuple[int, str]] = []

    @property
    def current(self) -> int:
        """Get current logical time."""
        return self._logical_time

    def next(self) -> int:
        """
        Advance logical time and return new value.

        Returns:
            Next logical time value
        """
        self._logical_time += 1
        return self._logical_time

    def record_event(self, event_id: str):
        """
        Record event in causal history.

        Args:
            event_id: Unique event identifier
        """
        self._event_history.append((self._logical_time, event_id))

    def get_history(self) -> list[tuple[int, str]]:
        """
        Get causal event history.

        Returns:
            List of (logical_time, event_id) tuples
        """
        return self._event_history.copy()

    def reset(self):
        """Reset clock to initial state."""
        self._logical_time = 0
        self._event_history.clear()


class EventQueue:
    """
    Queue for events waiting to execute at tick boundaries.

    Enforces that:
    1. Events only execute at tick boundaries
    2. Event order within a tick is deterministic (by logical time)
    3. Replay is guaranteed to produce identical results
    """

    def __init__(self):
        """Initialize empty event queue."""
        self._pending_events: dict[int, list[CausalEvent]] = {}
        self._executed_events: list[CausalEvent] = []

    def enqueue(self, event: CausalEvent):
        """
        Add event to queue for execution at specified tick.

        Args:
            event: Event to queue
        """
        tick = event.tick_number

        if tick not in self._pending_events:
            self._pending_events[tick] = []

        self._pending_events[tick].append(event)

        # Sort by logical time to ensure deterministic order
        self._pending_events[tick].sort(key=lambda e: e.logical_time)

        logger.debug(
            "Enqueued event %s (logical_time=%d) for tick %d",
            event.event_id,
            event.logical_time,
            tick
        )

    def get_events_for_tick(self, tick_number: int) -> list[CausalEvent]:
        """
        Retrieve events scheduled for this tick.

        Args:
            tick_number: Current tick

        Returns:
            List of events to execute (sorted by logical time)
        """
        events = self._pending_events.pop(tick_number, [])

        # Move to executed history
        self._executed_events.extend(events)

        if events:
            logger.debug(
                "Retrieved %d events for tick %d",
                len(events),
                tick_number
            )

        return events

    def has_pending_events(self, tick_number: int) -> bool:
        """
        Check if there are events pending for a tick.

        Args:
            tick_number: Tick to check

        Returns:
            True if events are pending
        """
        return tick_number in self._pending_events

    def get_pending_count(self) -> int:
        """
        Get total number of pending events across all ticks.

        Returns:
            Number of pending events
        """
        return sum(len(events) for events in self._pending_events.values())

    def get_executed_count(self) -> int:
        """
        Get number of executed events.

        Returns:
            Number of executed events
        """
        return len(self._executed_events)

    def get_executed_events(self) -> list[CausalEvent]:
        """
        Get history of executed events.

        Returns:
            List of executed events (in execution order)
        """
        return self._executed_events.copy()

    def clear_history(self):
        """Clear executed event history (for memory management)."""
        self._executed_events.clear()


class CausalValidator:
    """
    Validates causal ordering invariants.

    Ensures that events execute in proper logical order and that
    replay produces identical causal chains.
    """

    @staticmethod
    def validate_event_order(events: list[CausalEvent]) -> bool:
        """
        Validate that events are in proper logical time order.

        Args:
            events: List of events to validate

        Returns:
            True if order is valid
        """
        if len(events) <= 1:
            return True

        for i in range(1, len(events)):
            if events[i].logical_time <= events[i-1].logical_time:
                logger.error(
                    "Event order violation: %s (t=%d) should come after %s (t=%d)",
                    events[i].event_id,
                    events[i].logical_time,
                    events[i-1].event_id,
                    events[i-1].logical_time
                )
                return False

        return True

    @staticmethod
    def validate_tick_boundary(event: CausalEvent, current_tick: int) -> bool:
        """
        Validate that event respects tick boundaries.

        Args:
            event: Event to validate
            current_tick: Current tick number

        Returns:
            True if event is scheduled for future tick
        """
        if event.tick_number < current_tick:
            logger.error(
                "Event %s scheduled for past tick %d (current: %d)",
                event.event_id,
                event.tick_number,
                current_tick
            )
            return False

        return True

    @staticmethod
    def compare_causal_chains(
        chain1: list[tuple[int, str]],
        chain2: list[tuple[int, str]]
    ) -> bool:
        """
        Compare two causal chains for equality.

        Used to verify deterministic replay.

        Args:
            chain1: First causal chain
            chain2: Second causal chain

        Returns:
            True if chains are identical
        """
        if len(chain1) != len(chain2):
            logger.error(
                "Causal chain length mismatch: %d vs %d",
                len(chain1),
                len(chain2)
            )
            return False

        for i, ((t1, e1), (t2, e2)) in enumerate(zip(chain1, chain2, strict=False)):
            if t1 != t2 or e1 != e2:
                logger.error(
                    "Causal chain divergence at position %d: (%d, %s) vs (%d, %s)",
                    i, t1, e1, t2, e2
                )
                return False

        return True
