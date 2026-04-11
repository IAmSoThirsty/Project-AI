#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Comprehensive tests for distributed trace logger.

This test suite validates:
- Distributed tracing with OpenTelemetry-compatible features
- Span tracking and hierarchical relationships
- Correlation ID propagation
- W3C Trace Context support
- Performance metrics collection
- Context injection and extraction
- Trace querying and analysis
- Causal chain construction
"""

import time
from unittest.mock import Mock

import pytest

try:
    from app.audit.trace_logger import Span, SpanContext, TraceLogger
except ImportError:
    from src.app.audit.trace_logger import Span, SpanContext, TraceLogger


class TestSpanContext:
    """Test suite for SpanContext class."""

    def test_span_context_creation(self):
        """Test creating a span context."""
        context = SpanContext(
            trace_id="1234567890abcdef1234567890abcdef",
            span_id="1234567890abcdef",
            parent_span_id="fedcba0987654321",
        )

        assert context.trace_id == "1234567890abcdef1234567890abcdef"
        assert context.span_id == "1234567890abcdef"
        assert context.parent_span_id == "fedcba0987654321"
        assert context.trace_flags == 1
        assert context.trace_state == {}
        assert context.baggage == {}

    def test_to_w3c_traceparent(self):
        """Test converting to W3C traceparent format."""
        context = SpanContext(
            trace_id="12345678901234567890123456789012",
            span_id="1234567890123456",
        )

        traceparent = context.to_w3c_traceparent()
        assert traceparent == "00-12345678901234567890123456789012-1234567890123456-01"

    def test_from_w3c_traceparent(self):
        """Test parsing W3C traceparent format."""
        traceparent = "00-12345678901234567890123456789012-1234567890123456-01"
        context = SpanContext.from_w3c_traceparent(traceparent)

        assert context.trace_id == "12345678901234567890123456789012"
        assert context.span_id == "1234567890123456"
        assert context.trace_flags == 1

    def test_from_w3c_traceparent_invalid(self):
        """Test parsing invalid traceparent raises error."""
        with pytest.raises(ValueError):
            SpanContext.from_w3c_traceparent("invalid-format")

    def test_to_w3c_tracestate(self):
        """Test converting to W3C tracestate format."""
        context = SpanContext(
            trace_id="12345678901234567890123456789012",
            span_id="1234567890123456",
            trace_state={"vendor1": "value1", "vendor2": "value2"},
        )

        tracestate = context.to_w3c_tracestate()
        assert "vendor1=value1" in tracestate
        assert "vendor2=value2" in tracestate


class TestSpan:
    """Test suite for Span class."""

    def test_span_creation(self):
        """Test creating a span."""
        context = SpanContext(
            trace_id="12345678901234567890123456789012",
            span_id="1234567890123456",
        )

        span = Span(
            name="test-operation",
            context=context,
            operation_type="http",
            attributes={"http.method": "GET"},
        )

        assert span.name == "test-operation"
        assert span.context == context
        assert span.operation_type == "http"
        assert span.attributes == {"http.method": "GET"}
        assert span.events == []
        assert span.status == "unset"
        assert span.end_time is None

    def test_set_attribute(self):
        """Test setting span attributes."""
        context = SpanContext("trace123", "span123")
        span = Span("test", context)

        span.set_attribute("key1", "value1")
        span.set_attribute("key2", 42)

        assert span.attributes["key1"] == "value1"
        assert span.attributes["key2"] == 42

    def test_add_event(self):
        """Test adding events to a span."""
        context = SpanContext("trace123", "span123")
        span = Span("test", context)

        span.add_event("event1", {"attr1": "value1"})
        span.add_event("event2")

        assert len(span.events) == 2
        assert span.events[0]["name"] == "event1"
        assert span.events[0]["attributes"] == {"attr1": "value1"}
        assert span.events[1]["name"] == "event2"
        assert "timestamp" in span.events[0]

    def test_set_status(self):
        """Test setting span status."""
        context = SpanContext("trace123", "span123")
        span = Span("test", context)

        span.set_status("ok", "Operation completed")

        assert span.status == "ok"
        assert span.status_message == "Operation completed"

    def test_span_end(self):
        """Test ending a span."""
        context = SpanContext("trace123", "span123")
        span = Span("test", context)

        assert span.end_time is None
        span.end()
        assert span.end_time is not None

    def test_duration_calculation(self):
        """Test span duration calculation."""
        context = SpanContext("trace123", "span123")
        span = Span("test", context)

        time.sleep(0.01)  # Sleep for 10ms
        span.end()

        duration = span.duration_ms()
        assert duration >= 10  # At least 10ms
        assert duration < 100  # Should be much less than 100ms

    def test_to_dict(self):
        """Test converting span to dictionary."""
        context = SpanContext("trace123", "span123", parent_span_id="parent123")
        span = Span("test", context, operation_type="database")
        span.set_attribute("db.statement", "SELECT * FROM users")
        span.add_event("query_start")
        span.set_status("ok")
        span.end()

        data = span.to_dict()

        assert data["name"] == "test"
        assert data["trace_id"] == "trace123"
        assert data["span_id"] == "span123"
        assert data["parent_span_id"] == "parent123"
        assert data["operation_type"] == "database"
        assert data["status"] == "ok"
        assert data["attributes"]["db.statement"] == "SELECT * FROM users"
        assert len(data["events"]) == 1
        assert data["duration_ms"] is not None


class TestTraceLogger:
    """Test suite for TraceLogger class."""

    def test_init(self):
        """Test initializing trace logger."""
        logger = TraceLogger(
            storage_path="/tmp/traces",
            service_name="test-service",
            enable_export=True,
        )

        assert logger.storage_path == "/tmp/traces"
        assert logger.service_name == "test-service"
        assert logger.enable_export is True
        assert logger.traces == {}
        assert logger.spans == {}
        assert logger.active_trace is None

    def test_start_trace(self):
        """Test starting a new trace."""
        logger = TraceLogger()
        trace_id = logger.start_trace(
            operation="test-operation",
            context={"user_id": "123"},
        )

        assert trace_id in logger.traces
        assert logger.active_trace == trace_id

        trace = logger.traces[trace_id]
        assert trace["operation"] == "test-operation"
        assert trace["context"]["user_id"] == "123"
        assert trace["status"] == "active"
        assert "correlation_id" in trace
        assert trace["service_name"] == "sovereign-governance"

    def test_start_trace_with_correlation_id(self):
        """Test starting trace with explicit correlation ID."""
        logger = TraceLogger()
        trace_id = logger.start_trace(
            operation="test-op",
            correlation_id="corr-123",
        )

        trace = logger.traces[trace_id]
        assert trace["correlation_id"] == "corr-123"
        assert trace_id in logger.correlations["corr-123"]

    def test_start_span(self):
        """Test starting a span."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")

        span_id = logger.start_span(
            name="test-span",
            trace_id=trace_id,
            operation_type="http",
            attributes={"http.method": "POST"},
        )

        assert span_id in logger.spans
        span = logger.spans[span_id]
        assert span.name == "test-span"
        assert span.operation_type == "http"
        assert span.attributes["http.method"] == "POST"

    def test_start_span_with_parent(self):
        """Test starting a nested span."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")

        parent_span_id = logger.start_span("parent-span", trace_id=trace_id)
        child_span_id = logger.start_span(
            "child-span",
            trace_id=trace_id,
            parent_span_id=parent_span_id,
        )

        child_span = logger.spans[child_span_id]
        assert child_span.context.parent_span_id == parent_span_id

    def test_end_span(self):
        """Test ending a span."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")
        span_id = logger.start_span("test-span", trace_id=trace_id)

        time.sleep(0.01)
        success = logger.end_span(span_id, status="ok", status_message="Complete")

        assert success is True
        span = logger.spans[span_id]
        assert span.status == "ok"
        assert span.status_message == "Complete"
        assert span.end_time is not None

    def test_span_context_manager(self):
        """Test span context manager."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")

        with logger.span("test-span", trace_id=trace_id) as span_id:
            assert span_id in logger.spans
            span = logger.spans[span_id]
            assert span.end_time is None

        # Span should be ended after context exit
        span = logger.spans[span_id]
        assert span.end_time is not None
        assert span.status == "ok"

    def test_span_context_manager_with_exception(self):
        """Test span context manager handles exceptions."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")

        with pytest.raises(ValueError):
            with logger.span("test-span", trace_id=trace_id) as span_id:
                raise ValueError("Test error")

        # Span should be ended with error status
        span = logger.spans[span_id]
        assert span.end_time is not None
        assert span.status == "error"
        assert "Test error" in span.status_message

    def test_nested_spans_with_context_manager(self):
        """Test nested spans using context manager."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")

        with logger.span("parent-span", trace_id=trace_id) as parent_id:
            with logger.span("child-span", trace_id=trace_id) as child_id:
                child_span = logger.spans[child_id]
                assert child_span.context.parent_span_id == parent_id

    def test_add_span_attribute(self):
        """Test adding attributes to a span."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")
        span_id = logger.start_span("test-span", trace_id=trace_id)

        success = logger.add_span_attribute(span_id, "custom.attr", "value")
        assert success is True

        span = logger.spans[span_id]
        assert span.attributes["custom.attr"] == "value"

    def test_add_span_event(self):
        """Test adding events to a span."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")
        span_id = logger.start_span("test-span", trace_id=trace_id)

        success = logger.add_span_event(
            span_id,
            "cache_hit",
            {"cache.key": "user:123"},
        )
        assert success is True

        span = logger.spans[span_id]
        assert len(span.events) == 1
        assert span.events[0]["name"] == "cache_hit"

    def test_end_trace(self):
        """Test ending a trace."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")

        time.sleep(0.01)
        success = logger.end_trace(trace_id, result={"status": "success"})

        assert success is True
        trace = logger.traces[trace_id]
        assert trace["status"] == "completed"
        assert trace["result"]["status"] == "success"
        assert "end_time" in trace
        assert "duration_ms" in trace
        assert trace["duration_ms"] > 0

    def test_log_step(self):
        """Test logging a step in trace."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")

        step_id = logger.log_step(
            trace_id,
            "initialization",
            data={"config": "loaded"},
        )

        assert step_id != ""
        trace = logger.traces[trace_id]
        assert len(trace["steps"]) == 1
        assert trace["steps"][0]["step_name"] == "initialization"

    def test_log_step_with_parent(self):
        """Test logging nested steps."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")

        parent_step = logger.log_step(trace_id, "parent-step")
        child_step = logger.log_step(
            trace_id,
            "child-step",
            parent_step=parent_step,
        )

        trace = logger.traces[trace_id]
        child_step_data = next(s for s in trace["steps"] if s["step_id"] == child_step)
        assert child_step_data["parent_step"] == parent_step

    def test_get_trace(self):
        """Test retrieving a trace."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")

        trace = logger.get_trace(trace_id)
        assert trace is not None
        assert trace["trace_id"] == trace_id

    def test_get_span(self):
        """Test retrieving a span."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")
        span_id = logger.start_span("test-span", trace_id=trace_id)

        span_data = logger.get_span(span_id)
        assert span_data is not None
        assert span_data["name"] == "test-span"
        assert span_data["span_id"] == span_id

    def test_inject_context(self):
        """Test injecting trace context into headers."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace", correlation_id="corr-123")
        span_id = logger.start_span("test-span", trace_id=trace_id)

        headers = logger.inject_context(trace_id)

        assert "traceparent" in headers
        assert headers["traceparent"].startswith("00-")
        assert "x-correlation-id" in headers
        assert headers["x-correlation-id"] == "corr-123"

    def test_extract_context(self):
        """Test extracting trace context from headers."""
        logger = TraceLogger()

        headers = {
            "traceparent": "00-12345678901234567890123456789012-1234567890123456-01",
            "tracestate": "vendor1=value1,vendor2=value2",
        }

        context = logger.extract_context(headers)

        assert context is not None
        assert context.trace_id == "12345678901234567890123456789012"
        assert context.span_id == "1234567890123456"
        assert context.trace_flags == 1
        assert "vendor1" in context.trace_state
        assert context.trace_state["vendor1"] == "value1"

    def test_extract_context_no_traceparent(self):
        """Test extracting context with no traceparent returns None."""
        logger = TraceLogger()
        context = logger.extract_context({})
        assert context is None

    def test_query_traces_by_operation(self):
        """Test querying traces by operation name."""
        logger = TraceLogger()

        trace1 = logger.start_trace("operation-a")
        logger.end_trace(trace1)

        trace2 = logger.start_trace("operation-b")
        logger.end_trace(trace2)

        trace3 = logger.start_trace("operation-a")
        logger.end_trace(trace3)

        results = logger.query_traces(operation="operation-a")
        assert len(results) == 2

    def test_query_traces_by_correlation_id(self):
        """Test querying traces by correlation ID."""
        logger = TraceLogger()

        trace1 = logger.start_trace("op1", correlation_id="corr-123")
        trace2 = logger.start_trace("op2", correlation_id="corr-123")
        trace3 = logger.start_trace("op3", correlation_id="corr-456")

        results = logger.query_traces(correlation_id="corr-123")
        assert len(results) == 2

    def test_query_traces_by_status(self):
        """Test querying traces by status."""
        logger = TraceLogger()

        trace1 = logger.start_trace("op1")
        trace2 = logger.start_trace("op2")
        logger.end_trace(trace2)

        active_traces = logger.query_traces(status="active")
        assert len(active_traces) == 1

        completed_traces = logger.query_traces(status="completed")
        assert len(completed_traces) == 1

    def test_get_traces_by_correlation(self):
        """Test getting all traces with same correlation ID."""
        logger = TraceLogger()

        trace1 = logger.start_trace("op1", correlation_id="corr-123")
        trace2 = logger.start_trace("op2", correlation_id="corr-123")
        trace3 = logger.start_trace("op3", correlation_id="corr-456")

        related = logger.get_traces_by_correlation("corr-123")
        assert len(related) == 2
        assert all(t["correlation_id"] == "corr-123" for t in related)

    def test_get_causal_chain(self):
        """Test getting causal chain of steps."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")

        step1 = logger.log_step(trace_id, "step1")
        step2 = logger.log_step(trace_id, "step2", parent_step=step1)
        step3 = logger.log_step(trace_id, "step3", parent_step=step2)

        chain = logger.get_causal_chain(trace_id)
        assert len(chain) == 3
        assert chain[0]["step_name"] == "step1"
        assert chain[1]["parent_step"] == step1
        assert chain[2]["parent_step"] == step2

    def test_get_span_tree(self):
        """Test building hierarchical span tree."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")

        root_span = logger.start_span("root", trace_id=trace_id)
        child1 = logger.start_span("child1", trace_id=trace_id, parent_span_id=root_span)
        child2 = logger.start_span("child2", trace_id=trace_id, parent_span_id=root_span)
        grandchild = logger.start_span("grandchild", trace_id=trace_id, parent_span_id=child1)

        logger.end_span(grandchild)
        logger.end_span(child1)
        logger.end_span(child2)
        logger.end_span(root_span)

        tree = logger.get_span_tree(trace_id)

        assert tree["name"] == "root"
        assert len(tree["children"]) == 2
        assert tree["children"][0]["name"] == "child1"
        assert len(tree["children"][0]["children"]) == 1
        assert tree["children"][0]["children"][0]["name"] == "grandchild"

    def test_get_metrics_summary(self):
        """Test getting performance metrics summary."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")

        # Create and end multiple spans
        for i in range(5):
            span_id = logger.start_span(f"operation-{i % 2}", trace_id=trace_id)
            time.sleep(0.001 * (i + 1))
            logger.end_span(span_id)

        summary = logger.get_metrics_summary()

        assert "operation-0" in summary
        assert "operation-1" in summary
        assert summary["operation-0"]["count"] == 3
        assert summary["operation-1"]["count"] == 2
        assert summary["operation-0"]["min_ms"] > 0
        assert summary["operation-0"]["max_ms"] > summary["operation-0"]["min_ms"]
        assert summary["operation-0"]["avg_ms"] > 0

    def test_get_metrics_summary_filtered(self):
        """Test getting metrics for specific operation."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")

        span1 = logger.start_span("op-a", trace_id=trace_id)
        logger.end_span(span1)

        span2 = logger.start_span("op-b", trace_id=trace_id)
        logger.end_span(span2)

        summary = logger.get_metrics_summary(operation_name="op-a")

        assert "op-a" in summary
        assert "op-b" not in summary

    def test_export_trace_json(self):
        """Test exporting trace in JSON format."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")

        root_span = logger.start_span("root", trace_id=trace_id)
        child_span = logger.start_span("child", trace_id=trace_id, parent_span_id=root_span)
        logger.end_span(child_span)
        logger.end_span(root_span)

        logger.end_trace(trace_id)

        export = logger.export_trace(trace_id, format="json")

        assert export is not None
        assert export["trace_id"] == trace_id
        assert "span_tree" in export
        assert export["span_tree"]["name"] == "root"

    def test_export_trace_jaeger(self):
        """Test exporting trace in Jaeger format."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")

        span_id = logger.start_span("test-span", trace_id=trace_id)
        logger.add_span_attribute(span_id, "http.method", "GET")
        logger.add_span_event(span_id, "request_started")
        logger.end_span(span_id)

        export = logger.export_trace(trace_id, format="jaeger")

        assert export is not None
        assert "data" in export
        assert len(export["data"]) == 1
        assert export["data"][0]["traceID"] == trace_id
        assert len(export["data"][0]["spans"]) == 1

        span_data = export["data"][0]["spans"][0]
        assert span_data["operationName"] == "test-span"
        assert any(tag["key"] == "http.method" for tag in span_data["tags"])
        assert len(span_data["logs"]) == 1

    def test_export_trace_not_found(self):
        """Test exporting non-existent trace returns None."""
        logger = TraceLogger()
        export = logger.export_trace("non-existent-id")
        assert export is None

    def test_performance_metrics_tracking(self):
        """Test that performance metrics are tracked correctly."""
        logger = TraceLogger()
        trace_id = logger.start_trace("test-trace")

        span_id = logger.start_span("test-op", trace_id=trace_id)
        time.sleep(0.01)
        logger.end_span(span_id)

        assert "test-op" in logger.metrics
        assert len(logger.metrics["test-op"]) == 1
        assert logger.metrics["test-op"][0] >= 10  # At least 10ms

    def test_trace_id_generation(self):
        """Test trace ID generation is correct length."""
        logger = TraceLogger()
        trace_id = logger._generate_trace_id()

        assert len(trace_id) == 32  # 32 hex characters for W3C compatibility
        assert all(c in "0123456789abcdef" for c in trace_id)

    def test_span_id_generation(self):
        """Test span ID generation is correct length."""
        logger = TraceLogger()
        span_id = logger._generate_span_id()

        assert len(span_id) == 16  # 16 hex characters for W3C compatibility
        assert all(c in "0123456789abcdef" for c in span_id)

    def test_multiple_concurrent_traces(self):
        """Test handling multiple concurrent traces."""
        logger = TraceLogger()

        trace1 = logger.start_trace("trace-1")
        trace2 = logger.start_trace("trace-2")

        span1 = logger.start_span("span-1", trace_id=trace1)
        span2 = logger.start_span("span-2", trace_id=trace2)

        logger.end_span(span1)
        logger.end_span(span2)

        logger.end_trace(trace1)
        logger.end_trace(trace2)

        assert len(logger.traces) == 2
        assert logger.traces[trace1]["status"] == "completed"
        assert logger.traces[trace2]["status"] == "completed"

    def test_integration_complete_trace(self):
        """Integration test for a complete trace lifecycle."""
        logger = TraceLogger(service_name="test-service")

        # Start trace with correlation
        trace_id = logger.start_trace(
            operation="user-registration",
            context={"user_id": "user123"},
            correlation_id="req-456",
        )

        # Create hierarchical spans
        with logger.span("validate-input", trace_id=trace_id) as validation_span:
            logger.add_span_attribute(validation_span, "validation.rules", 5)
            logger.add_span_event(validation_span, "email_validated")

        with logger.span("database-operation", trace_id=trace_id, operation_type="database") as db_span:
            logger.add_span_attribute(db_span, "db.statement", "INSERT INTO users")

            with logger.span("acquire-lock", trace_id=trace_id) as lock_span:
                logger.add_span_event(lock_span, "lock_acquired")

        # Log decision steps
        step1 = logger.log_step(trace_id, "check-uniqueness", {"email": "unique"})
        step2 = logger.log_step(trace_id, "create-user", {"user_id": "user123"}, parent_step=step1)

        # End trace
        logger.end_trace(trace_id, result={"success": True, "user_id": "user123"})

        # Verify complete trace
        trace = logger.get_trace(trace_id)
        assert trace["status"] == "completed"
        assert trace["correlation_id"] == "req-456"
        assert len(trace["steps"]) == 2
        assert len(trace["span_ids"]) == 3

        # Verify span tree
        tree = logger.get_span_tree(trace_id)
        assert tree["name"] == "validate-input"

        # Verify metrics
        summary = logger.get_metrics_summary()
        assert "validate-input" in summary
        assert "database-operation" in summary

        # Verify context injection
        headers = logger.inject_context(trace_id)
        assert "traceparent" in headers
        assert headers["x-correlation-id"] == "req-456"

        # Verify export
        export = logger.export_trace(trace_id, format="json")
        assert export is not None
        assert export["operation"] == "user-registration"
