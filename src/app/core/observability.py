"""
Comprehensive Observability System for Project-AI.

Provides cathedral-level observability with:
- OpenTelemetry distributed tracing
- Prometheus metrics collection
- Structured logging
- Performance profiling
- SLA tracking
- Real-time monitoring
"""

import functools
import logging
import time
from collections import defaultdict
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Any, Optional

try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

    HAS_OPENTELEMETRY = True
except ImportError:
    HAS_OPENTELEMETRY = False
    trace = None

try:
    from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, Summary

    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""

    COUNTER = "COUNTER"
    GAUGE = "GAUGE"
    HISTOGRAM = "HISTOGRAM"
    SUMMARY = "SUMMARY"


@dataclass
class PerformanceMetric:
    """Performance measurement."""

    name: str
    value: float
    unit: str
    timestamp: datetime = field(
        default_factory=lambda: (datetime.now(datetime.UTC) if hasattr(datetime, "UTC") else datetime.utcnow())
    )
    labels: dict[str, str] = field(default_factory=dict)


@dataclass
class SLAConfig:
    """Service Level Agreement configuration."""

    name: str
    target_percentile: float = 99.0  # p99
    target_latency_ms: float = 100.0  # Target response time
    error_rate_threshold: float = 0.01  # 1% error rate
    availability_target: float = 99.9  # 99.9% uptime


@dataclass
class SLAMetrics:
    """SLA tracking metrics."""

    config: SLAConfig
    request_count: int = 0
    error_count: int = 0
    latencies: list[float] = field(default_factory=list)
    last_check: datetime = field(
        default_factory=lambda: (datetime.now(datetime.UTC) if hasattr(datetime, "UTC") else datetime.utcnow())
    )

    def calculate_percentile(self, percentile: float) -> float:
        """Calculate latency percentile."""
        if not self.latencies:
            return 0.0
        sorted_latencies = sorted(self.latencies)
        index = int(len(sorted_latencies) * (percentile / 100.0))
        return sorted_latencies[min(index, len(sorted_latencies) - 1)]

    def error_rate(self) -> float:
        """Calculate error rate."""
        if self.request_count == 0:
            return 0.0
        return self.error_count / self.request_count

    def meets_sla(self) -> bool:
        """Check if current metrics meet SLA."""
        if self.request_count == 0:
            return True

        # Check error rate
        if self.error_rate() > self.config.error_rate_threshold:
            return False

        # Check latency
        p_latency = self.calculate_percentile(self.config.target_percentile)
        return not p_latency > self.config.target_latency_ms


class DistributedTracer:
    """Distributed tracing integration with OpenTelemetry."""

    def __init__(self, service_name: str = "project-ai"):
        """
        Initialize distributed tracer.

        Args:
            service_name: Name of the service
        """
        self.service_name = service_name
        self.enabled = HAS_OPENTELEMETRY

        if self.enabled:
            # Configure OpenTelemetry
            resource = Resource.create({"service.name": service_name})
            provider = TracerProvider(resource=resource)

            # Add console exporter for development
            processor = BatchSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(processor)

            trace.set_tracer_provider(provider)
            self.tracer = trace.get_tracer(__name__)

            logger.info(f"OpenTelemetry tracing initialized for {service_name}")
        else:
            self.tracer = None
            logger.warning("OpenTelemetry not available. Install with: pip install opentelemetry-api opentelemetry-sdk")

    @contextmanager
    def start_span(self, name: str, **attributes):
        """
        Start a traced span.

        Args:
            name: Span name
            **attributes: Span attributes

        Yields:
            Span context
        """
        if not self.enabled or self.tracer is None:
            yield None
            return

        with self.tracer.start_as_current_span(name) as span:
            # Set attributes
            for key, value in attributes.items():
                span.set_attribute(key, str(value))

            yield span

    def trace_function(self, name: str | None = None):
        """
        Decorator to trace function execution.

        Args:
            name: Optional span name (defaults to function name)
        """

        def decorator(func: Callable) -> Callable:
            span_name = name or f"{func.__module__}.{func.__name__}"

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                with self.start_span(span_name):
                    return func(*args, **kwargs)

            return wrapper

        return decorator


class MetricsCollector:
    """Prometheus metrics collection."""

    def __init__(self, registry: Optional["CollectorRegistry"] = None):
        """
        Initialize metrics collector.

        Args:
            registry: Prometheus registry (creates default if None)
        """
        self.enabled = HAS_PROMETHEUS

        if self.enabled:
            self.registry = registry or CollectorRegistry()
            self._metrics: dict[str, Any] = {}
            logger.info("Prometheus metrics collection initialized")
        else:
            self.registry = None
            self._metrics = {}
            logger.warning("Prometheus client not available. Install with: pip install prometheus-client")

    def create_counter(self, name: str, description: str, labels: list[str] | None = None) -> Any | None:
        """Create a counter metric."""
        if not self.enabled:
            return None

        key = f"counter_{name}"
        if key not in self._metrics:
            self._metrics[key] = Counter(name, description, labelnames=labels or [], registry=self.registry)

        return self._metrics[key]

    def create_gauge(self, name: str, description: str, labels: list[str] | None = None) -> Any | None:
        """Create a gauge metric."""
        if not self.enabled:
            return None

        key = f"gauge_{name}"
        if key not in self._metrics:
            self._metrics[key] = Gauge(name, description, labelnames=labels or [], registry=self.registry)

        return self._metrics[key]

    def create_histogram(
        self,
        name: str,
        description: str,
        labels: list[str] | None = None,
        buckets: list[float] | None = None,
    ) -> Any | None:
        """Create a histogram metric."""
        if not self.enabled:
            return None

        key = f"histogram_{name}"
        if key not in self._metrics:
            kwargs = {
                "name": name,
                "documentation": description,
                "labelnames": labels or [],
                "registry": self.registry,
            }
            if buckets:
                kwargs["buckets"] = buckets

            self._metrics[key] = Histogram(**kwargs)

        return self._metrics[key]

    def create_summary(self, name: str, description: str, labels: list[str] | None = None) -> Any | None:
        """Create a summary metric."""
        if not self.enabled:
            return None

        key = f"summary_{name}"
        if key not in self._metrics:
            self._metrics[key] = Summary(name, description, labelnames=labels or [], registry=self.registry)

        return self._metrics[key]

    def inc_counter(self, name: str, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        """Increment a counter."""
        if not self.enabled:
            return

        key = f"counter_{name}"
        if key in self._metrics:
            metric = self._metrics[key]
            if labels:
                metric.labels(**labels).inc(value)
            else:
                metric.inc(value)

    def set_gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Set a gauge value."""
        if not self.enabled:
            return

        key = f"gauge_{name}"
        if key in self._metrics:
            metric = self._metrics[key]
            if labels:
                metric.labels(**labels).set(value)
            else:
                metric.set(value)

    def observe_histogram(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        """Observe a histogram value."""
        if not self.enabled:
            return

        key = f"histogram_{name}"
        if key in self._metrics:
            metric = self._metrics[key]
            if labels:
                metric.labels(**labels).observe(value)
            else:
                metric.observe(value)


class SLATracker:
    """Track Service Level Agreements."""

    def __init__(self):
        """Initialize SLA tracker."""
        self._slas: dict[str, SLAMetrics] = {}
        self._lock = Lock()

    def register_sla(self, config: SLAConfig) -> None:
        """Register an SLA configuration."""
        with self._lock:
            self._slas[config.name] = SLAMetrics(config=config)
            logger.info(f"Registered SLA: {config.name}")

    def record_request(self, sla_name: str, latency_ms: float, success: bool = True) -> None:
        """
        Record a request for SLA tracking.

        Args:
            sla_name: Name of the SLA
            latency_ms: Request latency in milliseconds
            success: Whether the request succeeded
        """
        with self._lock:
            if sla_name not in self._slas:
                logger.warning(f"SLA not registered: {sla_name}")
                return

            metrics = self._slas[sla_name]
            metrics.request_count += 1
            metrics.latencies.append(latency_ms)

            if not success:
                metrics.error_count += 1

            # Keep only recent latencies (last 10000)
            if len(metrics.latencies) > 10000:
                metrics.latencies = metrics.latencies[-10000:]

    def check_sla(self, sla_name: str) -> tuple[bool, dict[str, Any]]:
        """
        Check if SLA is being met.

        Returns:
            Tuple of (meets_sla, metrics_dict)
        """
        with self._lock:
            if sla_name not in self._slas:
                return False, {}

            metrics = self._slas[sla_name]
            meets_sla = metrics.meets_sla()

            metrics_dict = {
                "request_count": metrics.request_count,
                "error_count": metrics.error_count,
                "error_rate": metrics.error_rate(),
                "p50_latency_ms": metrics.calculate_percentile(50),
                "p95_latency_ms": metrics.calculate_percentile(95),
                "p99_latency_ms": metrics.calculate_percentile(99),
                "meets_sla": meets_sla,
            }

            return meets_sla, metrics_dict

    def get_all_sla_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all SLAs."""
        with self._lock:
            return {name: self.check_sla(name)[1] for name in self._slas}


class PerformanceProfiler:
    """Performance profiling and measurement."""

    def __init__(self):
        """Initialize performance profiler."""
        self._measurements: dict[str, list[PerformanceMetric]] = defaultdict(list)
        self._lock = Lock()

    @contextmanager
    def measure(self, name: str, unit: str = "ms", labels: dict[str, str] | None = None):
        """
        Context manager to measure performance.

        Args:
            name: Measurement name
            unit: Unit of measurement
            labels: Optional labels

        Yields:
            None
        """
        start_time = time.time()

        try:
            yield
        finally:
            duration = (time.time() - start_time) * 1000  # Convert to ms

            metric = PerformanceMetric(name=name, value=duration, unit=unit, labels=labels or {})

            with self._lock:
                self._measurements[name].append(metric)

                # Keep only recent measurements (last 1000 per metric)
                if len(self._measurements[name]) > 1000:
                    self._measurements[name] = self._measurements[name][-1000:]

    def get_statistics(self, name: str) -> dict[str, float]:
        """
        Get statistics for a measurement.

        Returns:
            Dictionary with min, max, mean, median, p95, p99
        """
        with self._lock:
            if name not in self._measurements:
                return {}

            measurements = self._measurements[name]
            if not measurements:
                return {}

            values = sorted([m.value for m in measurements])
            count = len(values)

            return {
                "count": count,
                "min": values[0],
                "max": values[-1],
                "mean": sum(values) / count,
                "median": values[count // 2],
                "p95": values[int(count * 0.95)],
                "p99": values[int(count * 0.99)],
            }

    def get_all_statistics(self) -> dict[str, dict[str, float]]:
        """Get statistics for all measurements."""
        with self._lock:
            return {name: self.get_statistics(name) for name in self._measurements}


class ObservabilitySystem:
    """
    Comprehensive observability system integrating tracing, metrics, and profiling.
    """

    def __init__(self, service_name: str = "project-ai"):
        """
        Initialize observability system.

        Args:
            service_name: Name of the service
        """
        self.service_name = service_name

        # Initialize components
        self.tracer = DistributedTracer(service_name)
        self.metrics = MetricsCollector()
        self.sla_tracker = SLATracker()
        self.profiler = PerformanceProfiler()

        # Create standard metrics
        self._initialize_standard_metrics()

        logger.info(f"ObservabilitySystem initialized for {service_name}")

    def _initialize_standard_metrics(self) -> None:
        """Initialize standard metrics."""
        # Request metrics
        self.metrics.create_counter("requests_total", "Total number of requests", labels=["method", "status"])

        self.metrics.create_histogram(
            "request_duration_ms",
            "Request duration in milliseconds",
            labels=["method"],
            buckets=[10, 50, 100, 250, 500, 1000, 2500, 5000, 10000],
        )

        # Error metrics
        self.metrics.create_counter("errors_total", "Total number of errors", labels=["error_type", "severity"])

        # System metrics
        self.metrics.create_gauge("subsystems_active", "Number of active subsystems")

        self.metrics.create_gauge("memory_usage_bytes", "Memory usage in bytes")

        # Circuit breaker metrics
        self.metrics.create_counter(
            "circuit_breaker_state_changes",
            "Circuit breaker state changes",
            labels=["service", "from_state", "to_state"],
        )

    @contextmanager
    def trace_request(self, name: str, method: str = "unknown", **attributes):
        """
        Trace a request with metrics collection.

        Args:
            name: Request name
            method: HTTP method or operation type
            **attributes: Additional attributes
        """
        start_time = time.time()
        success = True

        with self.tracer.start_span(name, method=method, **attributes):
            try:
                yield
            except Exception as e:
                success = False
                self.record_error(str(type(e).__name__), "ERROR")
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000

                # Record metrics
                status = "success" if success else "error"
                self.metrics.inc_counter("requests_total", labels={"method": method, "status": status})

                self.metrics.observe_histogram("request_duration_ms", duration_ms, labels={"method": method})

    def record_error(self, error_type: str, severity: str) -> None:
        """Record an error occurrence."""
        self.metrics.inc_counter("errors_total", labels={"error_type": error_type, "severity": severity})

    def update_subsystem_count(self, count: int) -> None:
        """Update active subsystem count."""
        self.metrics.set_gauge("subsystems_active", count)

    def update_memory_usage(self, bytes_used: float) -> None:
        """Update memory usage metric."""
        self.metrics.set_gauge("memory_usage_bytes", bytes_used)

    def record_circuit_breaker_change(self, service: str, from_state: str, to_state: str) -> None:
        """Record circuit breaker state change."""
        self.metrics.inc_counter(
            "circuit_breaker_state_changes",
            labels={"service": service, "from_state": from_state, "to_state": to_state},
        )

    def get_health_report(self) -> dict[str, Any]:
        """
        Get comprehensive health report.

        Returns:
            Dictionary with health metrics
        """
        return {
            "service_name": self.service_name,
            "timestamp": (datetime.now(datetime.UTC) if hasattr(datetime, "UTC") else datetime.utcnow()).isoformat(),
            "sla_status": self.sla_tracker.get_all_sla_status(),
            "performance": self.profiler.get_all_statistics(),
            "tracing_enabled": self.tracer.enabled,
            "metrics_enabled": self.metrics.enabled,
        }


# Global singleton instance
_observability_system: ObservabilitySystem | None = None
_obs_lock = Lock()


def get_observability_system(service_name: str = "project-ai") -> ObservabilitySystem:
    """Get or create the global observability system instance."""
    global _observability_system

    if _observability_system is None:
        with _obs_lock:
            if _observability_system is None:
                _observability_system = ObservabilitySystem(service_name)

    return _observability_system


def reset_observability_system() -> None:
    """Reset the global observability system (primarily for testing)."""
    global _observability_system

    with _obs_lock:
        _observability_system = None
