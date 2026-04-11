"""
Unit tests for OctoReflex Telemetry System
"""

import time
import unittest
from unittest.mock import Mock, patch

from octoreflex.internal.telemetry import (
    PrometheusExporter,
    OctoTracer,
    eBPFEventStream,
    get_logger,
    CorrelationContext,
    trace_operation,
)
from octoreflex.internal.telemetry.events import (
    Event,
    EventType,
    SyscallEvent,
    NetworkEvent,
)
from octoreflex.internal.telemetry.prometheus import MetricType


class TestPrometheusExporter(unittest.TestCase):
    """Test Prometheus metrics exporter"""
    
    def setUp(self):
        self.exporter = PrometheusExporter()
    
    def test_counter_increment(self):
        """Test counter increment"""
        self.exporter.counter_inc("octoreflex_events_processed_total", 1.0)
        self.exporter.counter_inc("octoreflex_events_processed_total", 2.0)
        
        # Should accumulate
        counter = self.exporter.counters["octoreflex_events_processed_total"][""]
        self.assertEqual(counter.get(), 3.0)
    
    def test_gauge_set(self):
        """Test gauge set"""
        self.exporter.gauge_set("octoreflex_threat_score_current", 75.0)
        self.exporter.gauge_set("octoreflex_threat_score_current", 85.0)
        
        # Should overwrite
        gauge = self.exporter.gauges["octoreflex_threat_score_current"][""]
        self.assertEqual(gauge.get(), 85.0)
    
    def test_histogram_observe(self):
        """Test histogram observation"""
        self.exporter.histogram_observe("octoreflex_containment_latency_seconds", 0.001)
        self.exporter.histogram_observe("octoreflex_containment_latency_seconds", 0.01)
        self.exporter.histogram_observe("octoreflex_containment_latency_seconds", 0.1)
        
        histogram = self.exporter.histograms["octoreflex_containment_latency_seconds"][""]
        self.assertEqual(histogram.get_count(), 3.0)
        self.assertAlmostEqual(histogram.get_sum(), 0.111, places=3)
    
    def test_octo_metrics(self):
        """Test OctoReflex-specific metrics"""
        # Threat score
        self.exporter.octo.record_threat_score(95.0)
        self.assertEqual(self.exporter.octo.threat_score.get(), 95.0)
        
        # State transitions
        self.exporter.octo.record_state_transition("monitoring", "containment")
        self.assertEqual(
            self.exporter.octo.state_transitions["monitoring_to_containment"].get(),
            1.0
        )
        
        # Detections
        self.exporter.octo.record_true_positive()
        self.exporter.octo.record_false_positive()
        self.assertEqual(self.exporter.octo.true_positives.get(), 1.0)
        self.assertEqual(self.exporter.octo.false_positives.get(), 1.0)
    
    def test_export_text(self):
        """Test Prometheus text export"""
        self.exporter.octo.record_threat_score(85.0)
        self.exporter.octo.record_false_positive()
        
        text = self.exporter.export_octo_metrics()
        
        # Check format
        self.assertIn("# HELP octoreflex_threat_score_current", text)
        self.assertIn("# TYPE octoreflex_threat_score_current gauge", text)
        self.assertIn("octoreflex_threat_score_current 85.0", text)
        self.assertIn("octoreflex_false_positives_total 1.0", text)


class TestOctoTracer(unittest.TestCase):
    """Test distributed tracing"""
    
    def setUp(self):
        self.tracer = OctoTracer("test-service")
    
    def test_span_creation(self):
        """Test span creation and completion"""
        span = self.tracer.start_span("test_operation")
        
        self.assertIsNotNone(span.trace_id)
        self.assertIsNotNone(span.span_id)
        self.assertIn(span.span_id, self.tracer.active_spans)
        
        self.tracer.end_span(span)
        
        self.assertNotIn(span.span_id, self.tracer.active_spans)
        self.assertIn(span, self.tracer.completed_spans)
    
    def test_span_context_manager(self):
        """Test span context manager"""
        with self.tracer.span("test_operation") as span:
            span.set_attribute("test_key", "test_value")
            span.add_event("test_event")
        
        # Span should be completed
        self.assertNotIn(span.span_id, self.tracer.active_spans)
        self.assertEqual(span.attributes["test_key"], "test_value")
        self.assertEqual(len(span.events), 1)
    
    def test_nested_spans(self):
        """Test nested span relationships"""
        with self.tracer.span("parent") as parent:
            with self.tracer.span("child") as child:
                # Child should have parent's trace_id
                self.assertEqual(child.trace_id, parent.trace_id)
                self.assertEqual(child.parent_span_id, parent.span_id)
    
    def test_trace_operation_decorator(self):
        """Test trace operation decorator"""
        @trace_operation("decorated_op")
        def test_function():
            return "success"
        
        result = test_function()
        self.assertEqual(result, "success")
        
        # Should have created a span
        self.assertGreater(len(self.tracer.completed_spans), 0)
    
    def test_export_jaeger(self):
        """Test Jaeger export format"""
        with self.tracer.span("operation"):
            pass
        
        traces = self.tracer.export_jaeger()
        self.assertGreater(len(traces), 0)
        
        trace = traces[0]
        self.assertIn("trace_id", trace)
        self.assertIn("spans", trace)


class TestEventStream(unittest.TestCase):
    """Test eBPF event stream"""
    
    def setUp(self):
        self.stream = eBPFEventStream(buffer_size=1024)
    
    def test_event_push_pop(self):
        """Test event push and pop"""
        event = SyscallEvent(
            event_id=1,
            event_type=EventType.SYSCALL,
            timestamp=time.time(),
            pid=1234,
            tid=1234,
            comm="test",
            syscall_name="read"
        )
        
        self.stream.push_event(event)
        
        self.assertEqual(self.stream.stats["events_received"], 1)
        self.assertEqual(self.stream.buffer.size_used(), 1)
        
        popped = self.stream.buffer.pop()
        self.assertEqual(popped.event_id, 1)
    
    def test_event_subscription(self):
        """Test event subscription"""
        handler = Mock()
        self.stream.subscribe(EventType.SYSCALL, handler)
        
        # Start processing
        self.stream.start()
        
        # Push event
        event = SyscallEvent(
            event_id=1,
            event_type=EventType.SYSCALL,
            timestamp=time.time(),
            pid=1234,
            tid=1234,
            comm="test"
        )
        self.stream.push_event(event)
        
        # Wait for processing
        time.sleep(0.1)
        
        # Handler should be called
        handler.assert_called_once()
        
        self.stream.stop()
    
    def test_buffer_overflow(self):
        """Test buffer overflow handling"""
        # Fill buffer beyond capacity
        for i in range(2000):
            event = Event(
                event_id=i,
                event_type=EventType.SYSCALL,
                timestamp=time.time(),
                pid=1234,
                tid=1234,
                comm="test"
            )
            self.stream.push_event(event)
        
        # Should have dropped events
        self.assertGreater(self.stream.stats["events_dropped"], 0)
    
    def test_event_filter(self):
        """Test event filtering"""
        handler = Mock()
        
        # Add filter for specific PID
        self.stream.add_filter(
            EventType.SYSCALL,
            lambda e: e.pid == 1234
        )
        
        self.stream.subscribe(EventType.SYSCALL, handler)
        self.stream.start()
        
        # Push matching event
        event1 = SyscallEvent(
            event_id=1,
            event_type=EventType.SYSCALL,
            timestamp=time.time(),
            pid=1234,
            tid=1234,
            comm="test"
        )
        self.stream.push_event(event1)
        
        # Push non-matching event
        event2 = SyscallEvent(
            event_id=2,
            event_type=EventType.SYSCALL,
            timestamp=time.time(),
            pid=5678,
            tid=5678,
            comm="other"
        )
        self.stream.push_event(event2)
        
        time.sleep(0.1)
        
        # Only one call (filtered event)
        self.assertEqual(handler.call_count, 1)
        
        self.stream.stop()


class TestStructuredLogging(unittest.TestCase):
    """Test structured JSON logging"""
    
    def test_correlation_context(self):
        """Test correlation context manager"""
        with CorrelationContext() as corr_id:
            from octoreflex.internal.telemetry.logging import get_correlation_id
            
            current_id = get_correlation_id()
            self.assertEqual(current_id, corr_id)
        
        # Should be cleared after context
        from octoreflex.internal.telemetry.logging import get_correlation_id
        self.assertIsNone(get_correlation_id())
    
    def test_logger_with_context(self):
        """Test logger with context variables"""
        logger = get_logger("test")
        
        with CorrelationContext() as corr_id:
            # Should not raise
            logger.info("Test message", key="value")


class TestPerformance(unittest.TestCase):
    """Performance benchmarks"""
    
    def test_counter_performance(self):
        """Test counter increment performance"""
        exporter = PrometheusExporter()
        
        iterations = 10000
        start = time.perf_counter_ns()
        
        for _ in range(iterations):
            exporter.counter_inc("octoreflex_events_processed_total", 1.0)
        
        end = time.perf_counter_ns()
        avg_ns = (end - start) / iterations
        
        # Should be under 100ns
        self.assertLess(avg_ns, 100, f"Counter increment took {avg_ns}ns, exceeds 100ns target")
    
    def test_histogram_performance(self):
        """Test histogram observe performance"""
        exporter = PrometheusExporter()
        
        iterations = 10000
        start = time.perf_counter_ns()
        
        for i in range(iterations):
            exporter.histogram_observe("octoreflex_processing_latency_seconds", 0.001)
        
        end = time.perf_counter_ns()
        avg_ns = (end - start) / iterations
        
        # Should be under 100ns
        self.assertLess(avg_ns, 100, f"Histogram observe took {avg_ns}ns, exceeds 100ns target")


if __name__ == "__main__":
    unittest.main()
