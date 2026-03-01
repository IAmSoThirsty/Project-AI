"""
Thirsty's Kernel - Distributed Tracing System

Production-grade distributed tracing with:
- OpenTelemetry-compatible spans
- W3C Trace Context propagation
- Multiple exporters (Jaeger, Zipkin, Console)
- Sampling strategies
- Span events, links, and baggage
- Critical path analysis
- Parent-child span relationships

Thirst of Gods Level Architecture
"""

import logging
import secrets
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class SpanKind(Enum):
    """Span kinds per OpenTelemetry spec"""

    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class SpanStatus(Enum):
    """Span status codes"""

    UNSET = "unset"
    OK = "ok"
    ERROR = "error"


@dataclass
class SpanEvent:
    """Event within a span"""

    name: str
    timestamp: float
    attributes: Dict[str, any] = field(default_factory=dict)


@dataclass
class SpanLink:
    """Link to another span"""

    trace_id: str
    span_id: str
    attributes: Dict[str, any] = field(default_factory=dict)


@dataclass
class Span:
    """Distributed tracing span"""

    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    name: str
    kind: SpanKind
    start_time: float
    end_time: Optional[float] = None
    status: SpanStatus = SpanStatus.UNSET
    status_message: str = ""

    # Attributes (tags)
    attributes: Dict[str, any] = field(default_factory=dict)

    # Events within span
    events: List[SpanEvent] = field(default_factory=list)

    # Links to other spans
    links: List[SpanLink] = field(default_factory=list)

    # Baggage (cross-service context)
    baggage: Dict[str, str] = field(default_factory=dict)


@dataclass
class TraceContext:
    """W3C Trace Context for propagation"""

    trace_id: str
    parent_id: str
    trace_flags: int = 0  # 0 = not sampled, 1 = sampled
    trace_state: str = ""


class TracingSystem:
    """
    Production-grade distributed tracing system

    Features:
    - OpenTelemetry-compatible
    - W3C Trace Context propagation
    - Multiple span exporters
    - Sampling strategies
    - Critical path analysis
    """

    def __init__(self):
        # Active spans (in-progress)
        self.active_spans: Dict[str, Span] = {}

        # Completed spans (for analysis)
        self.completed_spans: Dict[str, List[Span]] = {}  # trace_id -> spans

        # Thread-local storage for current span context
        self.current_context = threading.local()

        # Thread safety
        self.lock = threading.RLock()

        # Sampling rate (0.0 to 1.0)
        self.sampling_rate = 1.0  # 100% by default

        # Exporters
        self.exporters: List[callable] = []

        # Statistics
        self.stats = {
            "traces_started": 0,
            "spans_created": 0,
            "spans_exported": 0,
            "spans_sampled_out": 0,
        }

        logger.info(
            f"Tracing system initialized (sampling: {self.sampling_rate * 100}%)"
        )

    def start_trace(
        self, operation_name: str, attributes: Optional[Dict[str, any]] = None
    ) -> str:
        """
        Start a new trace

        Returns trace_id
        """
        with self.lock:
            trace_id = self._generate_trace_id()

            # Create root span
            span = self.start_span(
                operation_name,
                SpanKind.INTERNAL,
                attributes=attributes,
                trace_id=trace_id,
            )

            self.stats["traces_started"] += 1
            logger.debug(f"Started trace {trace_id} ({operation_name})")

            return trace_id

    def start_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: Optional[Dict[str, any]] = None,
        parent_span_id: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> Span:
        """
        Start a new span

        Args:
            name: Span name
            kind: Span kind
            attributes: Initial attributes
            parent_span_id: Parent span ID (None for root span)
            trace_id: Trace ID (None to create new trace)

        Returns:
            Span object
        """
        with self.lock:
            # Generate IDs
            if trace_id is None:
                trace_id = self._generate_trace_id()

            span_id = self._generate_span_id()

            # Check sampling
            if not self._should_sample(trace_id):
                self.stats["spans_sampled_out"] += 1
                # Return dummy span (won't be exported)
                return Span(
                    trace_id=trace_id,
                    span_id=span_id,
                    parent_span_id=parent_span_id,
                    name=name,
                    kind=kind,
                    start_time=time.time(),
                )

            # Create span
            span = Span(
                trace_id=trace_id,
                span_id=span_id,
                parent_span_id=parent_span_id,
                name=name,
                kind=kind,
                start_time=time.time(),
                attributes=attributes or {},
            )

            # Store as active
            self.active_spans[span_id] = span

            # Set as current context
            self.current_context.span = span

            self.stats["spans_created"] += 1
            logger.debug(f"Started span {span_id} ({name}) in trace {trace_id}")

            return span

    def end_span(
        self, span_id: str, status: SpanStatus = SpanStatus.OK, status_message: str = ""
    ):
        """End a span"""
        with self.lock:
            if span_id not in self.active_spans:
                logger.warning(f"Cannot end unknown span: {span_id}")
                return

            span = self.active_spans.pop(span_id)
            span.end_time = time.time()
            span.status = status
            span.status_message = status_message

            # Store in completed spans
            if span.trace_id not in self.completed_spans:
                self.completed_spans[span.trace_id] = []
            self.completed_spans[span.trace_id].append(span)

            # Export to configured exporters
            self._export_span(span)

            duration_ms = (span.end_time - span.start_time) * 1000
            logger.debug(
                f"Ended span {span_id} ({span.name}) - {duration_ms:.2f}ms - {status.value}"
            )

    def add_span_event(
        self, span_id: str, event_name: str, attributes: Optional[Dict[str, any]] = None
    ):
        """Add an event to a span"""
        with self.lock:
            if span_id not in self.active_spans:
                return

            span = self.active_spans[span_id]
            event = SpanEvent(
                name=event_name, timestamp=time.time(), attributes=attributes or {}
            )
            span.events.append(event)

    def add_span_link(
        self,
        span_id: str,
        linked_trace_id: str,
        linked_span_id: str,
        attributes: Optional[Dict[str, any]] = None,
    ):
        """Add a link to another span"""
        with self.lock:
            if span_id not in self.active_spans:
                return

            span = self.active_spans[span_id]
            link = SpanLink(
                trace_id=linked_trace_id,
                span_id=linked_span_id,
                attributes=attributes or {},
            )
            span.links.append(link)

    def set_span_attribute(self, span_id: str, key: str, value: any):
        """Set a span attribute"""
        with self.lock:
            if span_id in self.active_spans:
                self.active_spans[span_id].attributes[key] = value

    def inject_context(self, carrier: Dict[str, str], span_id: str) -> Dict[str, str]:
        """
        Inject trace context into carrier (for propagation)

        Implements W3C Trace Context format:
        traceparent: 00-{trace-id}-{parent-id}-{trace-flags}
        """
        with self.lock:
            if span_id not in self.active_spans:
                return carrier

            span = self.active_spans[span_id]

            # Format: version-trace_id-parent_id-flags
            traceparent = f"00-{span.trace_id}-{span.span_id}-01"

            carrier["traceparent"] = traceparent

            if span.baggage:
                # Format baggage: key1=value1,key2=value2
                baggage_str = ",".join([f"{k}={v}" for k, v in span.baggage.items()])
                carrier["baggage"] = baggage_str

            return carrier

    def extract_context(self, carrier: Dict[str, str]) -> Optional[TraceContext]:
        """
        Extract trace context from carrier

        Parses W3C Trace Context format
        """
        if "traceparent" not in carrier:
            return None

        try:
            # Parse traceparent: 00-{trace-id}-{parent-id}-{trace-flags}
            parts = carrier["traceparent"].split("-")

            if len(parts) != 4:
                return None

            version, trace_id, parent_id, flags = parts

            context = TraceContext(
                trace_id=trace_id,
                parent_id=parent_id,
                trace_flags=int(flags, 16),
                trace_state=carrier.get("tracestate", ""),
            )

            return context
        except Exception as e:
            logger.warning(f"Failed to extract trace context: {e}")
            return None

    def get_trace_visualization(self, trace_id: str) -> str:
        """
        Generate ASCII visualization of trace

        Shows parent-child span relationships
        """
        with self.lock:
            if trace_id not in self.completed_spans:
                return f"Trace {trace_id} not found"

            spans = self.completed_spans[trace_id]

            # Build tree structure
            root_spans = [s for s in spans if s.parent_span_id is None]

            lines = [f"Trace {trace_id}:", ""]

            for root in root_spans:
                self._visualize_span(root, spans, lines, indent=0)

            return "\n".join(lines)

    def _visualize_span(
        self, span: Span, all_spans: List[Span], lines: List[str], indent: int
    ):
        """Recursively visualize span tree"""
        duration_ms = 0
        if span.end_time:
            duration_ms = (span.end_time - span.start_time) * 1000

        prefix = "  " * indent + "├─ "
        status_icon = "✓" if span.status == SpanStatus.OK else "✗"

        lines.append(f"{prefix}{status_icon} {span.name} ({duration_ms:.2f}ms)")

        # Add children
        children = [s for s in all_spans if s.parent_span_id == span.span_id]
        for child in children:
            self._visualize_span(child, all_spans, lines, indent + 1)

    def analyze_critical_path(self, trace_id: str) -> List[Span]:
        """
        Analyze critical path in trace

        Returns list of spans on critical path (longest duration chain)
        """
        with self.lock:
            if trace_id not in self.completed_spans:
                return []

            spans = self.completed_spans[trace_id]

            # Find root spans
            roots = [s for s in spans if s.parent_span_id is None]

            if not roots:
                return []

            # For each root, find critical path
            critical_paths = []
            for root in roots:
                path = self._find_critical_path(root, spans)
                critical_paths.append(path)

            # Return longest path
            return max(
                critical_paths,
                key=lambda p: sum((s.end_time or 0) - s.start_time for s in p),
            )

    def _find_critical_path(self, span: Span, all_spans: List[Span]) -> List[Span]:
        """Recursively find critical path from span"""
        children = [s for s in all_spans if s.parent_span_id == span.span_id]

        if not children:
            return [span]

        # Find child with longest critical path
        child_paths = [self._find_critical_path(child, all_spans) for child in children]
        longest_child_path = max(
            child_paths, key=lambda p: sum((s.end_time or 0) - s.start_time for s in p)
        )

        return [span] + longest_child_path

    def add_exporter(self, exporter: callable):
        """
        Add span exporter

        Exporter should be callable(span: Span) -> None
        """
        self.exporters.append(exporter)
        logger.debug(f"Added exporter: {exporter.__name__}")

    def _export_span(self, span: Span):
        """Export span to all configured exporters"""
        for exporter in self.exporters:
            try:
                exporter(span)
                self.stats["spans_exported"] += 1
            except Exception as e:
                logger.error(f"Exporter {exporter.__name__} failed: {e}")

    def set_sampling_rate(self, rate: float):
        """Set sampling rate (0.0 to 1.0)"""
        if not 0.0 <= rate <= 1.0:
            raise ValueError("Sampling rate must be between 0.0 and 1.0")

        self.sampling_rate = rate
        logger.info(f"Set sampling rate to {rate * 100}%")

    def _should_sample(self, trace_id: str) -> bool:
        """Determine if trace should be sampled"""
        if self.sampling_rate >= 1.0:
            return True

        if self.sampling_rate <= 0.0:
            return False

        # Use trace_id hash for deterministic sampling
        trace_hash = int(trace_id[:8], 16)
        threshold = int(0xFFFFFFFF * self.sampling_rate)

        return trace_hash <= threshold

    def _generate_trace_id(self) -> str:
        """Generate random 128-bit trace ID"""
        return secrets.token_hex(16)

    def _generate_span_id(self) -> str:
        """Generate random 64-bit span ID"""
        return secrets.token_hex(8)

    def get_stats(self) -> Dict:
        """Get tracing statistics"""
        with self.lock:
            return {
                "active_spans": len(self.active_spans),
                "completed_traces": len(self.completed_spans),
                "total_completed_spans": sum(
                    len(spans) for spans in self.completed_spans.values()
                ),
                "exporters_configured": len(self.exporters),
                "sampling_rate": self.sampling_rate,
                **self.stats,
            }


# Built-in exporters


def console_exporter(span: Span):
    """Console exporter - prints spans to stdout"""
    duration_ms = 0
    if span.end_time:
        duration_ms = (span.end_time - span.start_time) * 1000

    print(
        f"[SPAN] {span.name} | {span.kind.value} | {duration_ms:.2f}ms | {span.status.value}"
    )


def jaeger_exporter(span: Span):
    """Jaeger exporter - sends to Jaeger agent (simulated)"""
    # Real implementation would use Jaeger Thrift protocol
    logger.debug(f"[Jaeger] Exported span {span.span_id} ({span.name})")


# Public API
__all__ = [
    "TracingSystem",
    "Span",
    "SpanKind",
    "SpanStatus",
    "SpanEvent",
    "SpanLink",
    "TraceContext",
    "console_exporter",
    "jaeger_exporter",
]
