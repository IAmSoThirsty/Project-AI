"""
Example: Complete OctoReflex Telemetry Integration

Demonstrates all telemetry features in a realistic scenario.
"""

import random
import time
from contextlib import contextmanager

from octoreflex.internal.telemetry import (
    PrometheusExporter,
    OctoTracer,
    eBPFEventStream,
    get_logger,
    CorrelationContext,
    trace_operation,
)
from octoreflex.internal.telemetry.events import EventType


# Initialize telemetry
prometheus = PrometheusExporter()
tracer = OctoTracer("octoreflex-demo")
event_stream = eBPFEventStream()
logger = get_logger("octoreflex.demo")


class ThreatAnalyzer:
    """Example threat analyzer with full telemetry"""
    
    def __init__(self):
        self.threat_score = 0.0
        self.state = "monitoring"
        
        # Subscribe to security events
        event_stream.subscribe(EventType.SECURITY, self._handle_security_event)
        event_stream.subscribe(EventType.SYSCALL, self._handle_syscall)
        
        logger.info("ThreatAnalyzer initialized")
    
    def _handle_security_event(self, event):
        """Handle security event from eBPF"""
        logger.warning(
            "Security event detected",
            event_id=event.event_id,
            pid=event.pid,
            comm=event.comm
        )
        
        # Increase threat score
        self.threat_score = min(100.0, self.threat_score + 10.0)
        prometheus.octo.record_threat_score(self.threat_score)
    
    def _handle_syscall(self, event):
        """Handle syscall event"""
        # Record syscall latency
        if hasattr(event, 'duration_ns'):
            latency_sec = event.duration_ns / 1_000_000_000
            prometheus.octo.record_processing_latency(latency_sec)
    
    @trace_operation("analyze_threat")
    def analyze(self, data: dict) -> dict:
        """Analyze threat with full telemetry"""
        
        with CorrelationContext() as corr_id:
            logger.info("Starting threat analysis", correlation_id=corr_id)
            
            start_time = time.perf_counter()
            
            try:
                # Simulate threat detection
                threat_level = random.uniform(0, 100)
                is_threat = threat_level > 50
                
                # Record detection
                if is_threat:
                    # Simulate some false positives
                    is_false_positive = random.random() < 0.05
                    
                    if is_false_positive:
                        prometheus.octo.record_false_positive()
                        logger.warning("False positive detected", threat_level=threat_level)
                    else:
                        prometheus.octo.record_true_positive()
                        logger.warning("True threat detected", threat_level=threat_level)
                        
                        # Transition to containment
                        self._transition_state("containment")
                
                # Update threat score
                self.threat_score = threat_level
                prometheus.octo.record_threat_score(threat_level)
                
                # Record event processed
                prometheus.octo.record_event_processed()
                
                result = {
                    "threat_level": threat_level,
                    "is_threat": is_threat,
                    "state": self.state,
                }
                
                logger.info(
                    "Analysis complete",
                    threat_level=threat_level,
                    is_threat=is_threat
                )
                
                return result
                
            finally:
                # Record processing latency
                duration = time.perf_counter() - start_time
                prometheus.octo.record_processing_latency(duration)
    
    @trace_operation("contain_threat")
    def contain(self, threat_id: str):
        """Contain threat with latency tracking"""
        
        logger.warning("Starting containment", threat_id=threat_id)
        
        start_time = time.perf_counter()
        
        try:
            # Simulate containment actions
            time.sleep(random.uniform(0.001, 0.01))  # 1-10ms
            
            # Transition to isolated state
            self._transition_state("isolated")
            
            logger.info("Containment successful", threat_id=threat_id)
            
        finally:
            # Record containment latency
            duration = time.perf_counter() - start_time
            prometheus.octo.record_containment(duration)
    
    def _transition_state(self, new_state: str):
        """Record state transition"""
        old_state = self.state
        
        logger.info(
            "State transition",
            from_state=old_state,
            to_state=new_state
        )
        
        # Record in Prometheus
        prometheus.octo.record_state_transition(old_state, new_state)
        
        self.state = new_state


def simulate_events():
    """Simulate eBPF events"""
    
    logger.info("Starting event simulation")
    
    # Simulate syscall events
    for i in range(100):
        event_stream.simulate_syscall(
            syscall_name=random.choice(["read", "write", "open", "close"]),
            pid=random.randint(1000, 9999),
            duration_ns=random.randint(100, 10000)
        )
        time.sleep(0.01)  # 10ms between events
    
    # Simulate network events
    for i in range(50):
        event_stream.simulate_network(
            protocol="tcp",
            src_addr="192.168.1.100",
            dst_addr="10.0.0.5",
            bytes_sent=random.randint(100, 10000)
        )
        time.sleep(0.02)  # 20ms between events


def main():
    """Main demo"""
    
    print("=" * 70)
    print("OctoReflex Telemetry Demo")
    print("=" * 70)
    
    # Start event stream
    event_stream.start()
    
    # Create analyzer
    analyzer = ThreatAnalyzer()
    
    # Start event simulation in background
    import threading
    event_thread = threading.Thread(target=simulate_events, daemon=True)
    event_thread.start()
    
    print("\n[1] Analyzing threats...")
    
    # Analyze some threats
    for i in range(10):
        data = {"request_id": i, "source": "test"}
        result = analyzer.analyze(data)
        
        # If threat detected, contain it
        if result["is_threat"] and result["threat_level"] > 75:
            analyzer.contain(f"threat-{i}")
        
        time.sleep(0.5)
    
    # Wait for events to process
    time.sleep(2)
    
    print("\n[2] Telemetry Statistics:")
    print(f"  Events received: {event_stream.stats['events_received']:,}")
    print(f"  Events processed: {event_stream.stats['events_processed']:,}")
    print(f"  Events dropped: {event_stream.stats['events_dropped']:,}")
    print(f"  Buffer utilization: {event_stream.buffer.size_used()}/{event_stream.buffer.size}")
    
    print(f"\n  Active spans: {len(tracer.active_spans)}")
    print(f"  Completed spans: {len(tracer.completed_spans)}")
    
    print(f"\n  Current threat score: {prometheus.octo.threat_score.get():.1f}")
    print(f"  True positives: {prometheus.octo.true_positives.get():.0f}")
    print(f"  False positives: {prometheus.octo.false_positives.get():.0f}")
    print(f"  Events processed: {prometheus.octo.total_events_processed.get():.0f}")
    
    print("\n[3] Exporting Prometheus metrics...")
    metrics = prometheus.export_octo_metrics()
    print("\n--- Metrics Preview ---")
    print(metrics[:500] + "...")
    
    print("\n[4] Exporting traces...")
    traces = tracer.export_jaeger()
    print(f"\n  Total traces: {len(traces)}")
    if traces:
        print(f"  Spans in first trace: {len(traces[0]['spans'])}")
    
    # Stop event stream
    event_stream.stop()
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    
    # Show how to access metrics endpoint
    print("\nTo expose metrics for Prometheus:")
    print("  1. Add HTTP endpoint: GET /metrics")
    print("  2. Return: prometheus.export_text() + prometheus.export_octo_metrics()")
    print("  3. Configure Prometheus scrape_configs to poll the endpoint")


if __name__ == "__main__":
    main()
