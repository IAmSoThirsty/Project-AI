"""
OctoReflex Telemetry System - Production-Grade Observability

Comprehensive monitoring and debugging with:
- Prometheus metrics with <100ns recording overhead
- OpenTelemetry distributed tracing
- eBPF real-time event streams
- Structured JSON logging with correlation IDs
- Grafana integration

Performance-optimized for production environments.
"""

from .prometheus.exporter import PrometheusExporter, OctoMetrics
from .tracing.tracer import OctoTracer, trace_operation
from .events.ebpf_stream import eBPFEventStream
from .logging import StructuredLogger, get_logger

__all__ = [
    "PrometheusExporter",
    "OctoMetrics",
    "OctoTracer",
    "trace_operation",
    "eBPFEventStream",
    "StructuredLogger",
    "get_logger",
]

__version__ = "1.0.0"
