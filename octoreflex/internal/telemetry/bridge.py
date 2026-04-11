"""
OctoReflex Telemetry Integration Bridge

Integrates kernel telemetry with OctoReflex observability pipeline.
"""

import time
from typing import Optional

from octoreflex.internal.telemetry import (
    PrometheusExporter,
    OctoTracer,
    eBPFEventStream,
    get_logger,
    trace_operation,
)
from octoreflex.internal.telemetry.events import EventType, SyscallEvent

logger = get_logger(__name__)


class TelemetryBridge:
    """
    Bridge between kernel telemetry and OctoReflex observability
    
    Provides unified monitoring across kernel and user space.
    """
    
    def __init__(self):
        self.prometheus = PrometheusExporter()
        self.tracer = OctoTracer("octoreflex-kernel")
        self.event_stream = eBPFEventStream()
        
        # Start event stream
        self.event_stream.start()
        
        # Register event handlers
        self._setup_handlers()
        
        logger.info("Telemetry bridge initialized")
    
    def _setup_handlers(self):
        """Setup event stream handlers"""
        # Subscribe to syscall events
        self.event_stream.subscribe(EventType.SYSCALL, self._handle_syscall)
        
        # Subscribe to network events
        self.event_stream.subscribe(EventType.NETWORK, self._handle_network)
        
        # Subscribe to security events
        self.event_stream.subscribe(EventType.SECURITY, self._handle_security)
    
    def _handle_syscall(self, event: SyscallEvent):
        """Handle syscall event"""
        # Record syscall latency
        if hasattr(event, 'duration_ns'):
            latency_sec = event.duration_ns / 1_000_000_000
            self.prometheus.histogram_observe(
                "octoreflex_processing_latency_seconds",
                latency_sec
            )
    
    def _handle_network(self, event):
        """Handle network event"""
        logger.debug("Network event", protocol=event.data.get("protocol"))
    
    def _handle_security(self, event):
        """Handle security event"""
        # Record as potential threat
        logger.warning("Security event detected", event_id=event.event_id)
        self.prometheus.octo.record_true_positive()
    
    @trace_operation("process_reflex")
    def process_reflex(self, reflex_data: dict):
        """Process reflex with telemetry"""
        start = time.perf_counter()
        
        try:
            # Record threat score
            if "threat_score" in reflex_data:
                self.prometheus.octo.record_threat_score(reflex_data["threat_score"])
            
            # Record state transition
            if "from_state" in reflex_data and "to_state" in reflex_data:
                self.prometheus.octo.record_state_transition(
                    reflex_data["from_state"],
                    reflex_data["to_state"]
                )
            
            # Process reflex
            # ... (actual reflex logic would go here)
            
            # Record success
            self.prometheus.octo.record_event_processed()
            
        finally:
            # Record processing latency
            duration = time.perf_counter() - start
            self.prometheus.octo.record_processing_latency(duration)
    
    def record_containment(self, latency_seconds: float):
        """Record containment action latency"""
        self.prometheus.octo.record_containment(latency_seconds)
    
    def record_detection(self, is_true_positive: bool):
        """Record detection result"""
        if is_true_positive:
            self.prometheus.octo.record_true_positive()
        else:
            self.prometheus.octo.record_false_positive()
    
    def export_metrics(self) -> str:
        """Export all metrics in Prometheus format"""
        return self.prometheus.export_text() + "\n" + self.prometheus.export_octo_metrics()
    
    def get_stats(self) -> dict:
        """Get telemetry statistics"""
        return {
            "prometheus": {
                "total_metrics": len(self.prometheus.metrics),
            },
            "event_stream": self.event_stream.get_stats(),
            "tracer": {
                "active_spans": len(self.tracer.active_spans),
                "completed_spans": len(self.tracer.completed_spans),
            }
        }


# Singleton instance
_bridge: Optional[TelemetryBridge] = None


def get_telemetry_bridge() -> TelemetryBridge:
    """Get global telemetry bridge instance"""
    global _bridge
    if _bridge is None:
        _bridge = TelemetryBridge()
    return _bridge


# Public API
__all__ = [
    "TelemetryBridge",
    "get_telemetry_bridge",
]
