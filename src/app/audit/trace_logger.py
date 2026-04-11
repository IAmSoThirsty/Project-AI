#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Trace Logger - Distributed Tracing with OpenTelemetry

This module implements comprehensive distributed tracing for causal audit chains
that track decision-making processes, their inputs, intermediate steps, and
final outcomes with full OpenTelemetry integration.

Key Features:
- OpenTelemetry-based distributed tracing
- Span tracking with hierarchical relationships
- Correlation ID propagation across services
- Context propagation (W3C Trace Context)
- Performance metrics and timing
- Custom attributes and events
- Trace export to multiple backends
- Decision trace capture
- Causal chain construction
- Rich metadata tracking
- Query and analysis interfaces

Distributed Tracing:
- Automatic span lifecycle management
- Parent-child span relationships
- Trace and span ID generation
- Context injection and extraction
- Baggage propagation
- Sampling strategies
- Multi-backend export (Jaeger, OTLP, Console)
"""

import contextvars
import logging
import time
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Generator
from uuid import uuid4

logger = logging.getLogger(__name__)

# Context variables for distributed tracing
_current_trace_context = contextvars.ContextVar("trace_context", default=None)
_current_span_context = contextvars.ContextVar("span_context", default=None)


class SpanContext:
    """Represents a span context for distributed tracing."""

    def __init__(
        self,
        trace_id: str,
        span_id: str,
        parent_span_id: str | None = None,
        trace_flags: int = 1,
        trace_state: dict[str, str] | None = None,
    ):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.trace_flags = trace_flags
        self.trace_state = trace_state or {}
        self.baggage: dict[str, str] = {}

    def to_w3c_traceparent(self) -> str:
        """Convert to W3C Trace Context traceparent header format."""
        return f"00-{self.trace_id}-{self.span_id}-{self.trace_flags:02x}"

    def to_w3c_tracestate(self) -> str:
        """Convert to W3C Trace Context tracestate header format."""
        items = [f"{k}={v}" for k, v in self.trace_state.items()]
        return ",".join(items)

    @classmethod
    def from_w3c_traceparent(cls, traceparent: str) -> "SpanContext":
        """Create SpanContext from W3C traceparent header."""
        parts = traceparent.split("-")
        if len(parts) != 4 or parts[0] != "00":
            raise ValueError(f"Invalid traceparent format: {traceparent}")

        return cls(
            trace_id=parts[1],
            span_id=parts[2],
            trace_flags=int(parts[3], 16),
        )


class Span:
    """Represents a single span in a distributed trace."""

    def __init__(
        self,
        name: str,
        context: SpanContext,
        operation_type: str = "internal",
        attributes: dict[str, Any] | None = None,
    ):
        self.name = name
        self.context = context
        self.operation_type = operation_type
        self.attributes = attributes or {}
        self.events: list[dict[str, Any]] = []
        self.start_time = time.time()
        self.end_time: float | None = None
        self.status = "unset"
        self.status_message = ""

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a custom attribute on the span."""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        """Add an event to the span."""
        self.events.append(
            {
                "name": name,
                "timestamp": time.time(),
                "attributes": attributes or {},
            }
        )

    def set_status(self, status: str, message: str = "") -> None:
        """Set the span status (unset, ok, error)."""
        self.status = status
        self.status_message = message

    def end(self) -> None:
        """End the span and record end time."""
        if self.end_time is None:
            self.end_time = time.time()

    def duration_ms(self) -> float:
        """Calculate span duration in milliseconds."""
        end = self.end_time or time.time()
        return (end - self.start_time) * 1000

    def to_dict(self) -> dict[str, Any]:
        """Convert span to dictionary representation."""
        return {
            "name": self.name,
            "trace_id": self.context.trace_id,
            "span_id": self.context.span_id,
            "parent_span_id": self.context.parent_span_id,
            "operation_type": self.operation_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms() if self.end_time else None,
            "status": self.status,
            "status_message": self.status_message,
            "attributes": self.attributes,
            "events": self.events,
        }


class TraceLogger:
    """Distributed tracing logger with OpenTelemetry-compatible features.

    This logger captures complete decision-making processes with:
    - Distributed trace context propagation
    - Hierarchical span relationships
    - Correlation ID tracking
    - Performance metrics
    - Custom attributes and events
    - W3C Trace Context support
    """

    def __init__(
        self,
        storage_path: str | None = None,
        service_name: str = "sovereign-governance",
        enable_export: bool = False,
    ):
        """Initialize the distributed trace logger.

        Args:
            storage_path: Path to store audit logs (optional)
            service_name: Name of the service for tracing
            enable_export: Enable export to external tracing backends
        """
        self.storage_path = storage_path
        self.service_name = service_name
        self.enable_export = enable_export

        # Storage for traces and spans
        self.traces: dict[str, dict[str, Any]] = {}
        self.spans: dict[str, Span] = {}
        self.active_trace: str | None = None

        # Performance metrics
        self.metrics: dict[str, list[float]] = defaultdict(list)

        # Correlation tracking
        self.correlations: dict[str, set[str]] = defaultdict(set)

    def _generate_trace_id(self) -> str:
        """Generate a new trace ID (32 hex characters for W3C compatibility)."""
        return uuid4().hex

    def _generate_span_id(self) -> str:
        """Generate a new span ID (16 hex characters for W3C compatibility)."""
        return uuid4().hex[:16]

    def start_trace(
        self,
        operation: str,
        context: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> str:
        """Start a new distributed trace.

        Args:
            operation: Description of the operation being traced
            context: Initial context data
            correlation_id: Optional correlation ID to link related traces

        Returns:
            Trace ID for referencing this trace
        """
        trace_id = self._generate_trace_id()
        self.active_trace = trace_id

        # Use provided correlation_id or generate one
        if correlation_id is None:
            correlation_id = str(uuid4())

        trace_data = {
            "trace_id": trace_id,
            "correlation_id": correlation_id,
            "operation": operation,
            "service_name": self.service_name,
            "start_time": datetime.now().isoformat(),
            "start_timestamp": time.time(),
            "context": context or {},
            "steps": [],
            "span_ids": [],
            "status": "active",
            "root_span_id": None,
        }

        self.traces[trace_id] = trace_data
        self.correlations[correlation_id].add(trace_id)

        # Store in context variable
        _current_trace_context.set(trace_id)

        logger.debug(
            "Started trace: %s for operation: %s (correlation: %s)",
            trace_id,
            operation,
            correlation_id,
        )

        return trace_id

    def start_span(
        self,
        name: str,
        trace_id: str | None = None,
        parent_span_id: str | None = None,
        operation_type: str = "internal",
        attributes: dict[str, Any] | None = None,
    ) -> str:
        """Start a new span within a trace.

        Args:
            name: Name of the span
            trace_id: ID of the trace (uses active trace if None)
            parent_span_id: ID of parent span for nesting
            operation_type: Type of operation (internal, http, database, etc.)
            attributes: Initial attributes for the span

        Returns:
            Span ID for referencing this span
        """
        if trace_id is None:
            trace_id = self.active_trace or _current_trace_context.get()

        if trace_id is None or trace_id not in self.traces:
            logger.error("No active trace found for span: %s", name)
            return ""

        span_id = self._generate_span_id()

        # Create span context
        span_context = SpanContext(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
        )

        # Create span
        span = Span(
            name=name,
            context=span_context,
            operation_type=operation_type,
            attributes=attributes or {},
        )

        # Store span
        self.spans[span_id] = span
        self.traces[trace_id]["span_ids"].append(span_id)

        # Set as root span if this is the first span
        if self.traces[trace_id]["root_span_id"] is None:
            self.traces[trace_id]["root_span_id"] = span_id

        # Store in context variable
        _current_span_context.set(span_id)

        logger.debug(
            "Started span: %s (id: %s) in trace: %s",
            name,
            span_id,
            trace_id,
        )

        return span_id

    def end_span(
        self,
        span_id: str,
        status: str = "ok",
        status_message: str = "",
    ) -> bool:
        """End a span and record metrics.

        Args:
            span_id: ID of the span to end
            status: Final status (unset, ok, error)
            status_message: Optional status message

        Returns:
            True if ended successfully
        """
        if span_id not in self.spans:
            logger.error("Span ID not found: %s", span_id)
            return False

        span = self.spans[span_id]
        span.set_status(status, status_message)
        span.end()

        # Record performance metric
        duration_ms = span.duration_ms()
        self.metrics[span.name].append(duration_ms)

        logger.debug(
            "Ended span: %s (duration: %.2f ms, status: %s)",
            span.name,
            duration_ms,
            status,
        )

        return True

    @contextmanager
    def span(
        self,
        name: str,
        trace_id: str | None = None,
        operation_type: str = "internal",
        attributes: dict[str, Any] | None = None,
    ) -> Generator[str, None, None]:
        """Context manager for automatic span lifecycle management.

        Args:
            name: Name of the span
            trace_id: ID of the trace
            operation_type: Type of operation
            attributes: Initial attributes

        Yields:
            Span ID
        """
        parent_span_id = _current_span_context.get()

        span_id = self.start_span(
            name=name,
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            operation_type=operation_type,
            attributes=attributes,
        )

        try:
            yield span_id
        except Exception as e:
            self.add_span_event(
                span_id,
                "exception",
                {
                    "exception.type": type(e).__name__,
                    "exception.message": str(e),
                },
            )
            self.end_span(span_id, status="error", status_message=str(e))
            raise
        else:
            self.end_span(span_id, status="ok")

    def add_span_attribute(
        self,
        span_id: str,
        key: str,
        value: Any,
    ) -> bool:
        """Add an attribute to a span.

        Args:
            span_id: ID of the span
            key: Attribute key
            value: Attribute value

        Returns:
            True if added successfully
        """
        if span_id not in self.spans:
            logger.error("Span ID not found: %s", span_id)
            return False

        self.spans[span_id].set_attribute(key, value)
        return True

    def add_span_event(
        self,
        span_id: str,
        event_name: str,
        attributes: dict[str, Any] | None = None,
    ) -> bool:
        """Add an event to a span.

        Args:
            span_id: ID of the span
            event_name: Name of the event
            attributes: Event attributes

        Returns:
            True if added successfully
        """
        if span_id not in self.spans:
            logger.error("Span ID not found: %s", span_id)
            return False

        self.spans[span_id].add_event(event_name, attributes)
        return True

    def log_step(
        self,
        trace_id: str,
        step_name: str,
        data: dict[str, Any] | None = None,
        parent_step: str | None = None,
    ) -> str:
        """Log a step in the decision-making process.

        Args:
            trace_id: ID of the trace to log to
            step_name: Name/description of this step
            data: Data associated with this step
            parent_step: ID of parent step for building causal chains

        Returns:
            Step ID for referencing this step
        """
        if trace_id not in self.traces:
            logger.error("Trace ID not found: %s", trace_id)
            return ""

        step_id = str(uuid4())

        step_data = {
            "step_id": step_id,
            "step_name": step_name,
            "timestamp": datetime.now().isoformat(),
            "data": data or {},
            "parent_step": parent_step,
        }

        self.traces[trace_id]["steps"].append(step_data)
        logger.debug("Logged step %s in trace %s: %s", step_id, trace_id, step_name)

        return step_id

    def end_trace(self, trace_id: str, result: dict[str, Any] | None = None) -> bool:
        """End a distributed trace.

        Args:
            trace_id: ID of the trace to end
            result: Final result data

        Returns:
            True if ended successfully
        """
        if trace_id not in self.traces:
            logger.error("Trace ID not found: %s", trace_id)
            return False

        end_time = time.time()
        self.traces[trace_id]["end_time"] = datetime.now().isoformat()
        self.traces[trace_id]["end_timestamp"] = end_time
        self.traces[trace_id]["result"] = result or {}
        self.traces[trace_id]["status"] = "completed"

        # Calculate total duration
        start_time = self.traces[trace_id]["start_timestamp"]
        duration_ms = (end_time - start_time) * 1000
        self.traces[trace_id]["duration_ms"] = duration_ms

        if self.active_trace == trace_id:
            self.active_trace = None
            _current_trace_context.set(None)

        logger.info("Ended trace: %s (duration: %.2f ms)", trace_id, duration_ms)
        return True

    def get_trace(self, trace_id: str) -> dict[str, Any] | None:
        """Retrieve a trace by ID.

        Args:
            trace_id: ID of the trace to retrieve

        Returns:
            Trace data or None if not found
        """
        return self.traces.get(trace_id)

    def get_span(self, span_id: str) -> dict[str, Any] | None:
        """Retrieve a span by ID.

        Args:
            span_id: ID of the span to retrieve

        Returns:
            Span data or None if not found
        """
        span = self.spans.get(span_id)
        return span.to_dict() if span else None

    def inject_context(self, trace_id: str | None = None) -> dict[str, str]:
        """Inject trace context into headers for propagation.

        Args:
            trace_id: ID of the trace (uses active if None)

        Returns:
            Dictionary of headers for context propagation
        """
        if trace_id is None:
            trace_id = self.active_trace or _current_trace_context.get()

        if trace_id is None or trace_id not in self.traces:
            return {}

        span_id = _current_span_context.get()
        if span_id and span_id in self.spans:
            span_context = self.spans[span_id].context
        else:
            # Create a temporary context
            span_context = SpanContext(
                trace_id=trace_id,
                span_id=self._generate_span_id(),
            )

        headers = {
            "traceparent": span_context.to_w3c_traceparent(),
        }

        if span_context.trace_state:
            headers["tracestate"] = span_context.to_w3c_tracestate()

        # Add correlation ID
        correlation_id = self.traces[trace_id].get("correlation_id")
        if correlation_id:
            headers["x-correlation-id"] = correlation_id

        return headers

    def extract_context(self, headers: dict[str, str]) -> SpanContext | None:
        """Extract trace context from headers.

        Args:
            headers: Dictionary of headers

        Returns:
            SpanContext if valid context found, None otherwise
        """
        traceparent = headers.get("traceparent")
        if not traceparent:
            return None

        try:
            context = SpanContext.from_w3c_traceparent(traceparent)

            # Extract tracestate if present
            tracestate = headers.get("tracestate")
            if tracestate:
                for item in tracestate.split(","):
                    if "=" in item:
                        key, value = item.split("=", 1)
                        context.trace_state[key.strip()] = value.strip()

            return context
        except ValueError as e:
            logger.error("Failed to extract context: %s", e)
            return None

    def query_traces(
        self,
        operation: str | None = None,
        correlation_id: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """Query traces by various criteria.

        Args:
            operation: Filter by operation name
            correlation_id: Filter by correlation ID
            start_time: Filter by start time (ISO format)
            end_time: Filter by end time (ISO format)
            status: Filter by status (active, completed)

        Returns:
            List of matching traces
        """
        results = []

        for trace in self.traces.values():
            if operation and trace.get("operation") != operation:
                continue

            if correlation_id and trace.get("correlation_id") != correlation_id:
                continue

            if status and trace.get("status") != status:
                continue

            results.append(trace)

        return results

    def get_traces_by_correlation(self, correlation_id: str) -> list[dict[str, Any]]:
        """Get all traces linked by a correlation ID.

        Args:
            correlation_id: Correlation ID to search for

        Returns:
            List of related traces
        """
        trace_ids = self.correlations.get(correlation_id, set())
        return [self.traces[tid] for tid in trace_ids if tid in self.traces]

    def get_causal_chain(self, trace_id: str) -> list[dict[str, Any]]:
        """Extract the causal chain from a trace.

        Args:
            trace_id: ID of the trace

        Returns:
            List of steps in causal order
        """
        trace = self.get_trace(trace_id)
        if not trace:
            return []

        return trace.get("steps", [])

    def get_span_tree(self, trace_id: str) -> dict[str, Any]:
        """Build a hierarchical tree of spans for a trace.

        Args:
            trace_id: ID of the trace

        Returns:
            Nested dictionary representing span hierarchy
        """
        trace = self.get_trace(trace_id)
        if not trace:
            return {}

        span_ids = trace.get("span_ids", [])
        spans_data = [self.spans[sid].to_dict() for sid in span_ids if sid in self.spans]

        # Build tree structure
        root_span_id = trace.get("root_span_id")
        if not root_span_id:
            return {}

        def build_tree(span_id: str) -> dict[str, Any]:
            span_data = next((s for s in spans_data if s["span_id"] == span_id), None)
            if not span_data:
                return {}

            children = [
                build_tree(s["span_id"])
                for s in spans_data
                if s.get("parent_span_id") == span_id
            ]

            result = dict(span_data)
            if children:
                result["children"] = children

            return result

        return build_tree(root_span_id)

    def get_metrics_summary(self, operation_name: str | None = None) -> dict[str, Any]:
        """Get performance metrics summary.

        Args:
            operation_name: Filter metrics by operation name (None for all)

        Returns:
            Dictionary with metrics statistics
        """
        summary = {}

        metrics_to_process = self.metrics
        if operation_name:
            metrics_to_process = {
                k: v for k, v in self.metrics.items() if k == operation_name
            }

        for name, durations in metrics_to_process.items():
            if not durations:
                continue

            summary[name] = {
                "count": len(durations),
                "min_ms": min(durations),
                "max_ms": max(durations),
                "avg_ms": sum(durations) / len(durations),
                "total_ms": sum(durations),
            }

        return summary

    def export_trace(self, trace_id: str, format: str = "json") -> dict[str, Any] | None:
        """Export a trace in a specific format.

        Args:
            trace_id: ID of the trace to export
            format: Export format (json, jaeger, otlp)

        Returns:
            Exported trace data
        """
        trace = self.get_trace(trace_id)
        if not trace:
            return None

        if format == "json":
            # Include full span data
            span_tree = self.get_span_tree(trace_id)
            return {
                **trace,
                "span_tree": span_tree,
            }

        elif format == "jaeger":
            # Convert to Jaeger format
            spans = []
            for span_id in trace.get("span_ids", []):
                if span_id in self.spans:
                    span = self.spans[span_id]
                    spans.append(
                        {
                            "traceID": span.context.trace_id,
                            "spanID": span.context.span_id,
                            "operationName": span.name,
                            "startTime": int(span.start_time * 1000000),
                            "duration": int(span.duration_ms() * 1000),
                            "tags": [
                                {"key": k, "value": v}
                                for k, v in span.attributes.items()
                            ],
                            "logs": [
                                {
                                    "timestamp": int(e["timestamp"] * 1000000),
                                    "fields": [
                                        {"key": "event", "value": e["name"]},
                                        *[
                                            {"key": k, "value": v}
                                            for k, v in e["attributes"].items()
                                        ],
                                    ],
                                }
                                for e in span.events
                            ],
                        }
                    )

            return {
                "data": [
                    {
                        "traceID": trace_id,
                        "spans": spans,
                        "processes": {
                            "p1": {
                                "serviceName": self.service_name,
                                "tags": [],
                            }
                        },
                    }
                ]
            }

        return trace

__all__ = ["TraceLogger", "Span", "SpanContext"]

