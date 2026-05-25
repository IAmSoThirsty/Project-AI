"""PSIA failure detector — circuit breaker, cascade detection."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class FailureEvent:
    error_type: str = ""
    message: str = ""
    timestamp: float = field(default_factory=time.monotonic)


@dataclass
class ComponentHealth:
    component: str
    circuit_state: CircuitState = CircuitState.CLOSED
    total_requests: int = 0
    total_failures: int = 0
    last_failure: FailureEvent | None = None
    _opened_at: float = field(default=0.0, repr=False)

    @property
    def failure_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return self.total_failures / self.total_requests


@dataclass
class CascadeAlert:
    affected_components: list[str]
    open_count: int


class FailureDetector:
    def __init__(
        self,
        failure_threshold: float = 0.5,
        cascade_threshold: int = 2,
        on_cascade: Callable[[CascadeAlert], None] | None = None,
        recovery_timeout: float = 60.0,
    ) -> None:
        self._threshold = failure_threshold
        self._cascade_threshold = cascade_threshold
        self._on_cascade = on_cascade
        self._recovery_timeout = recovery_timeout
        self._health: dict[str, ComponentHealth] = {}
        self._transitions: list[tuple] = []
        self._cascade_fired = False

    def _ensure(self, component: str) -> ComponentHealth:
        if component not in self._health:
            self._health[component] = ComponentHealth(component=component)
        return self._health[component]

    def register_component(self, component: str) -> None:
        self._ensure(component)

    def record_success(self, component: str) -> None:
        h = self._ensure(component)
        h.total_requests += 1
        if h.circuit_state == CircuitState.HALF_OPEN:
            self._transition(h, CircuitState.CLOSED)

    def record_failure(
        self,
        component: str,
        error_type: str = "",
        message: str = "",
    ) -> None:
        h = self._ensure(component)
        h.total_requests += 1
        h.total_failures += 1
        h.last_failure = FailureEvent(error_type=error_type, message=message)

        if h.circuit_state == CircuitState.CLOSED and h.failure_rate >= self._threshold:
            h._opened_at = time.monotonic()
            self._transition(h, CircuitState.OPEN)
            self._check_cascade()

    def _transition(self, h: ComponentHealth, new_state: CircuitState) -> None:
        old_state = h.circuit_state
        h.circuit_state = new_state
        self._transitions.append((h.component, old_state, new_state))

    def _check_cascade(self) -> None:
        if self._cascade_fired or self._on_cascade is None:
            return
        open_components = [
            name for name, h in self._health.items()
            if h.circuit_state == CircuitState.OPEN
        ]
        if len(open_components) >= self._cascade_threshold:
            self._cascade_fired = True
            self._on_cascade(CascadeAlert(
                affected_components=open_components,
                open_count=len(open_components),
            ))

    def check_circuit(self, component: str) -> CircuitState:
        h = self._ensure(component)
        if h.circuit_state == CircuitState.OPEN:
            elapsed = time.monotonic() - h._opened_at
            if elapsed >= self._recovery_timeout:
                self._transition(h, CircuitState.HALF_OPEN)
        return h.circuit_state

    def get_health(self, component: str) -> ComponentHealth:
        return self._ensure(component)

    def get_all_health(self) -> dict[str, ComponentHealth]:
        return dict(self._health)

    def open_circuit_count(self) -> int:
        return sum(1 for h in self._health.values() if h.circuit_state == CircuitState.OPEN)

    @property
    def state_transitions(self) -> list[tuple]:
        return list(self._transitions)
