"""
Performance Benchmarks for Telemetry System

Validates <100ns overhead requirement for metric recording.
"""

import statistics
import time
from typing import List

from octoreflex.internal.telemetry import PrometheusExporter, OctoTracer
from octoreflex.internal.telemetry.events import eBPFEventStream


def benchmark_counter_increment(iterations: int = 100000) -> List[float]:
    """Benchmark counter increment operation"""
    exporter = PrometheusExporter()
    
    # Register test metric
    from octoreflex.internal.telemetry.prometheus import MetricType
    exporter.register_metric(
        "test_counter",
        MetricType.COUNTER,
        "Test counter",
        []
    )
    
    timings = []
    
    for _ in range(iterations):
        start = time.perf_counter_ns()
        exporter.counter_inc("test_counter", 1.0)
        end = time.perf_counter_ns()
        timings.append(end - start)
    
    return timings


def benchmark_gauge_set(iterations: int = 100000) -> List[float]:
    """Benchmark gauge set operation"""
    exporter = PrometheusExporter()
    
    from octoreflex.internal.telemetry.prometheus import MetricType
    exporter.register_metric(
        "test_gauge",
        MetricType.GAUGE,
        "Test gauge",
        []
    )
    
    timings = []
    
    for i in range(iterations):
        start = time.perf_counter_ns()
        exporter.gauge_set("test_gauge", float(i))
        end = time.perf_counter_ns()
        timings.append(end - start)
    
    return timings


def benchmark_histogram_observe(iterations: int = 100000) -> List[float]:
    """Benchmark histogram observation"""
    exporter = PrometheusExporter()
    
    from octoreflex.internal.telemetry.prometheus import MetricType
    exporter.register_metric(
        "test_histogram",
        MetricType.HISTOGRAM,
        "Test histogram",
        [],
        buckets=[0.001, 0.01, 0.1, 1.0]
    )
    
    timings = []
    
    for i in range(iterations):
        start = time.perf_counter_ns()
        exporter.histogram_observe("test_histogram", float(i % 100) / 100.0)
        end = time.perf_counter_ns()
        timings.append(end - start)
    
    return timings


def benchmark_span_creation(iterations: int = 10000) -> List[float]:
    """Benchmark span creation and completion"""
    tracer = OctoTracer()
    
    timings = []
    
    for _ in range(iterations):
        start = time.perf_counter_ns()
        
        span = tracer.start_span("test_operation")
        span.set_attribute("test", "value")
        tracer.end_span(span)
        
        end = time.perf_counter_ns()
        timings.append(end - start)
    
    return timings


def benchmark_event_push(iterations: int = 100000) -> List[float]:
    """Benchmark event stream push operation"""
    stream = eBPFEventStream()
    
    from octoreflex.internal.telemetry.events import SyscallEvent, EventType
    
    timings = []
    
    for i in range(iterations):
        event = SyscallEvent(
            event_id=i,
            event_type=EventType.SYSCALL,
            timestamp=time.time(),
            pid=1234,
            tid=1234,
            comm="test",
            syscall_name="read",
            duration_ns=1000
        )
        
        start = time.perf_counter_ns()
        stream.push_event(event)
        end = time.perf_counter_ns()
        
        timings.append(end - start)
    
    return timings


def print_results(name: str, timings: List[float]):
    """Print benchmark results"""
    print(f"\n{name}:")
    print(f"  Iterations: {len(timings):,}")
    print(f"  Mean: {statistics.mean(timings):.1f} ns")
    print(f"  Median: {statistics.median(timings):.1f} ns")
    print(f"  P95: {sorted(timings)[int(len(timings) * 0.95)]:.1f} ns")
    print(f"  P99: {sorted(timings)[int(len(timings) * 0.99)]:.1f} ns")
    print(f"  Min: {min(timings):.1f} ns")
    print(f"  Max: {max(timings):.1f} ns")
    
    # Check if within <100ns requirement
    mean_ns = statistics.mean(timings)
    if mean_ns < 100:
        print(f"  ✓ PASS: Mean {mean_ns:.1f}ns < 100ns requirement")
    else:
        print(f"  ✗ FAIL: Mean {mean_ns:.1f}ns >= 100ns requirement")


def run_benchmarks():
    """Run all telemetry benchmarks"""
    print("=" * 70)
    print("OctoReflex Telemetry Performance Benchmarks")
    print("Target: <100ns overhead per operation")
    print("=" * 70)
    
    # Counter benchmark
    print("\n[1/5] Counter Increment...")
    counter_timings = benchmark_counter_increment()
    print_results("Counter Increment", counter_timings)
    
    # Gauge benchmark
    print("\n[2/5] Gauge Set...")
    gauge_timings = benchmark_gauge_set()
    print_results("Gauge Set", gauge_timings)
    
    # Histogram benchmark
    print("\n[3/5] Histogram Observe...")
    histogram_timings = benchmark_histogram_observe()
    print_results("Histogram Observe", histogram_timings)
    
    # Span benchmark
    print("\n[4/5] Span Creation...")
    span_timings = benchmark_span_creation()
    print_results("Span Creation/Completion", span_timings)
    
    # Event push benchmark
    print("\n[5/5] Event Stream Push...")
    event_timings = benchmark_event_push()
    print_results("Event Stream Push", event_timings)
    
    print("\n" + "=" * 70)
    print("Benchmark Complete")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmarks()
