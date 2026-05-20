"""
Unified integration bus: circuit breaker, retry, tracing, pub/sub, service registry.
"""

from __future__ import annotations

import threading
import time
import uuid
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable

from src.app.core.exceptions import CircuitBreakerOpenError, DependencyNotFoundError


# ── Enums ─────────────────────────────────────────────────────────────────────

class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class ServicePriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


# ── Circuit breaker ───────────────────────────────────────────────────────────

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    success_threshold: int = 1
    timeout: float = 30.0


class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig) -> None:
        self.config = config
        self.state: CircuitBreakerState = CircuitBreakerState.CLOSED
        self.failure_count: int = 0
        self.success_count: int = 0
        self.last_failure_time: float | None = None
        self._lock = threading.Lock()

    def call(self, func: Callable) -> Any:
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                elapsed = (
                    time.time() - self.last_failure_time
                    if self.last_failure_time is not None
                    else 0.0
                )
                if elapsed >= self.config.timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        try:
            result = func()
        except Exception:
            with self._lock:
                if self.state == CircuitBreakerState.HALF_OPEN:
                    self.state = CircuitBreakerState.OPEN
                    self.last_failure_time = time.time()
                else:
                    self.failure_count += 1
                    if self.failure_count >= self.config.failure_threshold:
                        self.state = CircuitBreakerState.OPEN
                        self.last_failure_time = time.time()
            raise

        with self._lock:
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
            elif self.state == CircuitBreakerState.CLOSED:
                self.failure_count = 0

        return result


# ── Retry policy ──────────────────────────────────────────────────────────────

@dataclass
class RetryPolicy:
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

    def calculate_delay(self, attempt: int) -> float:
        delay = self.initial_delay * (self.exponential_base ** attempt)
        if self.jitter:
            import random
            delay *= 0.5 + random.random() * 0.5
        return min(delay, self.max_delay)


# ── Trace context ─────────────────────────────────────────────────────────────

@dataclass
class TraceContext:
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    parent_span_id: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    baggage: dict = field(default_factory=dict)

    def create_child_span(self) -> TraceContext:
        return TraceContext(
            trace_id=self.trace_id,
            parent_span_id=self.span_id,
            baggage=dict(self.baggage),
        )


# ── Internal event ────────────────────────────────────────────────────────────

class _Event:
    def __init__(self, event_type: str, data: Any) -> None:
        self.event_type = event_type
        self.data = data


# ── Unified integration bus ───────────────────────────────────────────────────

class UnifiedIntegrationBus:
    def __init__(self) -> None:
        self._services: dict[str, dict] = {}
        self._subscribers: dict[str, list] = defaultdict(list)

    def register_service(
        self,
        name: str,
        service: Any,
        health_check: Callable | None = None,
        priority: ServicePriority = ServicePriority.MEDIUM,
    ) -> None:
        self._services[name] = {
            "service": service,
            "health_check": health_check,
            "priority": priority,
        }

    def get_service(self, name: str) -> Any:
        if name not in self._services:
            raise DependencyNotFoundError(f"Service not found: {name}")
        return self._services[name]["service"]

    def check_service_health(self, name: str) -> bool:
        entry = self._services.get(name)
        if not entry or entry["health_check"] is None:
            return True
        try:
            return bool(entry["health_check"]())
        except Exception:
            return False

    def request_service(
        self,
        name: str,
        data: Any,
        use_circuit_breaker: bool = True,
        retry_policy: RetryPolicy | None = None,
    ) -> Any:
        service = self.get_service(name)
        trace_ctx = TraceContext()

        if retry_policy is None:
            return service.handle_request(data, trace_ctx)

        last_exc: Exception | None = None
        for attempt in range(retry_policy.max_attempts):
            try:
                return service.handle_request(data, trace_ctx)
            except Exception as exc:
                last_exc = exc
                if attempt < retry_policy.max_attempts - 1:
                    time.sleep(retry_policy.calculate_delay(attempt))

        raise last_exc  # type: ignore[misc]

    def subscribe(self, event_type: str, subscriber: Any) -> None:
        self._subscribers[event_type].append(subscriber)

    def publish_event(self, event_type: str, data: Any) -> None:
        event = _Event(event_type, data)
        for subscriber in self._subscribers[event_type]:
            subscriber.handle_event(event)

    @contextmanager
    def trace_span(self, name: str, **kwargs: Any):
        ctx = TraceContext()
        ctx.baggage["span_name"] = name
        for key, value in kwargs.items():
            ctx.baggage[key] = value
        yield ctx

    def get_all_services(self) -> dict[str, Any]:
        return {name: entry["service"] for name, entry in self._services.items()}

    def health_check_all(self) -> dict[str, bool]:
        return {name: self.check_service_health(name) for name in self._services}

    def shutdown(self) -> None:
        self._services.clear()
        self._subscribers.clear()


# ── Singleton ─────────────────────────────────────────────────────────────────

_bus_instance: UnifiedIntegrationBus | None = None


def get_integration_bus() -> UnifiedIntegrationBus:
    global _bus_instance
    if _bus_instance is None:
        _bus_instance = UnifiedIntegrationBus()
    return _bus_instance


def reset_integration_bus() -> None:
    global _bus_instance
    _bus_instance = None
