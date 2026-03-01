"""
Failure Detector — Anomaly Detection and Circuit Breaking.

Monitors PSIA subsystem health through sliding-window failure
rate tracking, anomaly detection, and circuit breaker patterns.

Detection modes:
    - Per-component failure rate tracking (sliding window)
    - Anomaly detection via z-score over historical baselines
    - Circuit breaker (closed → open → half-open → closed)
    - Failure correlation across components for cascade detection

Security invariants:
    - Failure rates cannot be externally reset without audit
    - Circuit breaker transitions are logged
    - Cascading failures trigger SAFE-HALT escalation

Production notes:
    - In production, metrics would be exported to Prometheus/Grafana
    - Distributed failure correlation would use gossip protocol
    - Health checks would run as separate async tasks
"""

from __future__ import annotations

import logging
import math
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker state."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failures exceed threshold, requests blocked
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class FailureEvent:
    """A recorded failure event."""

    component: str
    error_type: str
    message: str
    timestamp: float  # monotonic seconds
    severity: str = "error"


@dataclass
class ComponentHealth:
    """Health status of a single component."""

    component: str
    circuit_state: CircuitState
    failure_rate: float  # 0.0–1.0
    total_requests: int
    total_failures: int
    last_failure: FailureEvent | None
    z_score: float = 0.0  # Anomaly score


@dataclass
class CascadeAlert:
    """Alert when multiple components fail simultaneously."""

    affected_components: list[str]
    correlation_score: float
    timestamp: str
    recommended_action: str


class FailureDetector:
    """Monitors component health via failure tracking and circuit breaking.

    For each registered component, tracks failures in a sliding window
    and manages a circuit breaker with configurable thresholds.

    Args:
        window_seconds: Sliding window duration for failure rate calculation
        failure_threshold: Failure rate (0.0–1.0) to trip the circuit breaker
        recovery_timeout: Seconds in OPEN state before transitioning to HALF_OPEN
        cascade_threshold: Number of simultaneous open circuits to trigger cascade alert
        on_cascade: Callback for cascade detection
    """

    def __init__(
        self,
        *,
        window_seconds: float = 60.0,
        failure_threshold: float = 0.5,
        recovery_timeout: float = 30.0,
        cascade_threshold: int = 2,
        on_cascade: Callable[[CascadeAlert], None] | None = None,
    ) -> None:
        self.window_seconds = window_seconds
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.cascade_threshold = cascade_threshold
        self.on_cascade = on_cascade

        # Per-component tracking
        self._successes: dict[str, deque[float]] = {}
        self._failures: dict[str, deque[FailureEvent]] = {}
        self._circuit_state: dict[str, CircuitState] = {}
        self._circuit_opened_at: dict[str, float] = {}
        self._historical_rates: dict[str, list[float]] = {}  # For z-score
        self._state_transitions: list[tuple[str, CircuitState, CircuitState, float]] = (
            []
        )

    def register_component(self, component: str) -> None:
        """Register a component for monitoring."""
        if component not in self._circuit_state:
            self._successes[component] = deque()
            self._failures[component] = deque()
            self._circuit_state[component] = CircuitState.CLOSED
            self._historical_rates[component] = []

    def record_success(self, component: str) -> None:
        """Record a successful operation for a component."""
        self._ensure_registered(component)
        now = time.monotonic()
        self._successes[component].append(now)
        self._prune_window(component, now)

        # If half-open and success, transition back to closed
        if self._circuit_state[component] == CircuitState.HALF_OPEN:
            self._transition(component, CircuitState.CLOSED)

    def record_failure(
        self,
        component: str,
        *,
        error_type: str = "error",
        message: str = "",
        severity: str = "error",
    ) -> None:
        """Record a failure for a component."""
        self._ensure_registered(component)
        now = time.monotonic()

        event = FailureEvent(
            component=component,
            error_type=error_type,
            message=message,
            timestamp=now,
            severity=severity,
        )
        self._failures[component].append(event)
        self._prune_window(component, now)

        # Check if circuit should trip
        rate = self._compute_failure_rate(component)
        total = len(self._successes[component]) + len(self._failures[component])

        if (
            self._circuit_state[component] == CircuitState.CLOSED
            and rate >= self.failure_threshold
            and total >= 3  # Minimum sample size
        ):
            self._transition(component, CircuitState.OPEN)
            self._circuit_opened_at[component] = now
            self._check_cascade()

    def check_circuit(self, component: str) -> CircuitState:
        """Check circuit breaker state, potentially transitioning OPEN → HALF_OPEN.

        Args:
            component: Component to check

        Returns:
            Current CircuitState
        """
        self._ensure_registered(component)

        if self._circuit_state[component] == CircuitState.OPEN:
            opened_at = self._circuit_opened_at.get(component, 0.0)
            if time.monotonic() - opened_at >= self.recovery_timeout:
                self._transition(component, CircuitState.HALF_OPEN)

        return self._circuit_state[component]

    def get_health(self, component: str) -> ComponentHealth:
        """Get health status for a component."""
        self._ensure_registered(component)
        now = time.monotonic()
        self._prune_window(component, now)

        failures_list = list(self._failures[component])
        return ComponentHealth(
            component=component,
            circuit_state=self._circuit_state[component],
            failure_rate=self._compute_failure_rate(component),
            total_requests=len(self._successes[component]) + len(failures_list),
            total_failures=len(failures_list),
            last_failure=failures_list[-1] if failures_list else None,
            z_score=self._compute_z_score(component),
        )

    def get_all_health(self) -> dict[str, ComponentHealth]:
        """Get health status for all registered components."""
        return {c: self.get_health(c) for c in self._circuit_state}

    def open_circuit_count(self) -> int:
        """Count the number of currently open circuits."""
        return sum(1 for s in self._circuit_state.values() if s == CircuitState.OPEN)

    @property
    def state_transitions(self) -> list[tuple[str, CircuitState, CircuitState, float]]:
        """All recorded state transitions (component, from, to, timestamp)."""
        return list(self._state_transitions)

    def _ensure_registered(self, component: str) -> None:
        if component not in self._circuit_state:
            self.register_component(component)

    def _prune_window(self, component: str, now: float) -> None:
        """Remove events outside the sliding window."""
        cutoff = now - self.window_seconds
        while self._successes[component] and self._successes[component][0] < cutoff:
            self._successes[component].popleft()
        while (
            self._failures[component]
            and self._failures[component][0].timestamp < cutoff
        ):
            self._failures[component].popleft()

    def _compute_failure_rate(self, component: str) -> float:
        """Compute failure rate within current window."""
        s = len(self._successes[component])
        f = len(self._failures[component])
        total = s + f
        if total == 0:
            return 0.0
        return f / total

    def _compute_z_score(self, component: str) -> float:
        """Compute z-score anomaly over historical rates."""
        current_rate = self._compute_failure_rate(component)
        history = self._historical_rates.get(component, [])
        if len(history) < 3:
            return 0.0
        mean = sum(history) / len(history)
        variance = sum((r - mean) ** 2 for r in history) / len(history)
        if variance == 0:
            return 0.0
        stddev = math.sqrt(variance)
        return (current_rate - mean) / stddev

    def _transition(self, component: str, new_state: CircuitState) -> None:
        old_state = self._circuit_state[component]
        self._circuit_state[component] = new_state
        self._state_transitions.append(
            (component, old_state, new_state, time.monotonic())
        )
        logger.info("Circuit %s: %s → %s", component, old_state.value, new_state.value)

        # Record current rate in history when transitioning
        rate = self._compute_failure_rate(component)
        self._historical_rates.setdefault(component, []).append(rate)

    def _check_cascade(self) -> None:
        """Check if enough circuits are open to constitute a cascade."""
        open_circuits = [
            c for c, s in self._circuit_state.items() if s == CircuitState.OPEN
        ]
        if len(open_circuits) >= self.cascade_threshold:
            alert = CascadeAlert(
                affected_components=open_circuits,
                correlation_score=len(open_circuits) / max(len(self._circuit_state), 1),
                timestamp=datetime.now(timezone.utc).isoformat(),
                recommended_action=(
                    "SAFE-HALT"
                    if len(open_circuits) > self.cascade_threshold
                    else "INVESTIGATE"
                ),
            )
            if self.on_cascade:
                self.on_cascade(alert)


__all__ = [
    "FailureDetector",
    "CircuitState",
    "FailureEvent",
    "ComponentHealth",
    "CascadeAlert",
]
