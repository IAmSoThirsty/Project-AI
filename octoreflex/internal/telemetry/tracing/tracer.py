"""
Tracer - OpenTelemetry distributed tracing

High-performance request tracing with context propagation.
"""

from . import (
    OctoTracer,
    Span,
    SpanKind,
    SpanStatus,
    trace_operation,
    get_tracer,
)

__all__ = [
    "OctoTracer",
    "Span",
    "SpanKind",
    "SpanStatus",
    "trace_operation",
    "get_tracer",
]
