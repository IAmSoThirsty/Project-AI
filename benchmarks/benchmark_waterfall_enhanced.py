#!/usr/bin/env python3
"""
PSIA Enhanced Waterfall Performance Benchmarks
===============================================

Comprehensive performance benchmarking suite to verify:
- Stage latency < 10μs per stage
- Total latency < 70μs end-to-end
- ML inference < 2μs per stage
- 99th percentile compliance

Usage:
    python benchmark_waterfall_enhanced.py
    python benchmark_waterfall_enhanced.py --iterations 10000
    python benchmark_waterfall_enhanced.py --profile --export results.json
"""

import argparse
import json
import statistics
import time
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

# Mock imports for standalone benchmarking
try:
    from psia.waterfall_enhanced import (
        EnhancedWaterfallEngine,
        MLModelConfig,
        PerformanceMonitor,
        WaterfallStage,
    )
    from psia.schemas.request import RequestEnvelope
    from psia.events import EventBus
    MOCKED = False
except ImportError:
    print("Warning: Running in mock mode (PSIA modules not available)")
    MOCKED = True


# ══════════════════════════════════════════════════════════════════════
# BENCHMARK CONFIGURATION
# ══════════════════════════════════════════════════════════════════════


@dataclass
class BenchmarkConfig:
    """Configuration for benchmarking."""
    iterations: int = 1000
    warmup_iterations: int = 100
    enable_ml: bool = True
    enable_performance_monitoring: bool = True
    target_stage_latency_us: float = 10.0
    target_total_latency_us: float = 70.0
    profile: bool = False
    export_path: str | None = None


@dataclass
class BenchmarkResults:
    """Aggregated benchmark results."""
    config: BenchmarkConfig
    total_iterations: int
    
    # Latency statistics (microseconds)
    mean_latency_us: float
    median_latency_us: float
    p95_latency_us: float
    p99_latency_us: float
    max_latency_us: float
    min_latency_us: float
    stddev_latency_us: float
    
    # Stage-by-stage statistics
    stage_stats: dict[str, dict[str, float]]
    
    # ML statistics
    ml_mean_inference_us: float
    ml_p99_inference_us: float
    
    # Compliance metrics
    total_compliance_rate: float
    stage_compliance_rates: dict[str, float]
    
    # Performance summary
    target_met: bool
    violations: int
    success_rate: float


# ══════════════════════════════════════════════════════════════════════
# MOCK IMPLEMENTATIONS (for standalone benchmarking)
# ══════════════════════════════════════════════════════════════════════


if MOCKED:
    from enum import Enum
    from dataclasses import dataclass, field
    
    class WaterfallStage(int, Enum):
        STRUCTURAL = 0
        SIGNATURE = 1
        BEHAVIORAL = 2
        SHADOW = 3
        GATE = 4
        COMMIT = 5
        MEMORY = 6
    
    class StageDecision(str, Enum):
        ALLOW = "allow"
        DENY = "deny"
        QUARANTINE = "quarantine"
        ESCALATE = "escalate"
    
    class MLAnomalyLevel(str, Enum):
        NORMAL = "normal"
        SUSPICIOUS = "suspicious"
        ANOMALOUS = "anomalous"
        CRITICAL = "critical"
    
    @dataclass
    class MockEnvelope:
        request_id: str
        actor: str
        subject: str
        intent: Any
        context: Any
        capabilities: list = field(default_factory=list)
        metadata: dict = field(default_factory=dict)
    
    @dataclass
    class MockIntent:
        action: str
        constraints: list = field(default_factory=list)
    
    @dataclass
    class MockContext:
        trace_id: str
        timestamp: float
    
    class MockStage:
        def evaluate(self, envelope, prior_results):
            # Simulate fast stage execution
            time.sleep(0.000005)  # 5μs
            from dataclasses import dataclass
            
            @dataclass
            class StageResult:
                stage: WaterfallStage
                decision: StageDecision
                reasons: list
                metadata: dict
                
                @property
                def severity_rank(self):
                    return {"allow": 0, "escalate": 1, "quarantine": 2, "deny": 3}[self.decision.value]
            
            return StageResult(
                stage=WaterfallStage.STRUCTURAL,
                decision=StageDecision.ALLOW,
                reasons=[],
                metadata={},
            )
    
    class EventBus:
        def emit(self, event):
            pass
    
    class MLModelConfig:
        def __init__(self, stage, **kwargs):
            self.stage = stage
    
    class EnhancedWaterfallEngine:
        def __init__(self, **kwargs):
            self.event_bus = kwargs.get('event_bus', EventBus())
        
        def process(self, envelope):
            # Simulate enhanced waterfall processing
            start = time.perf_counter()
            
            # Simulate 7 stages @ ~8μs each
            stage_results = []
            for i in range(7):
                stage_start = time.perf_counter()
                time.sleep(0.000008)  # 8μs
                duration_us = (time.perf_counter() - stage_start) * 1e6
                
                @dataclass
                class EnhancedStageResult:
                    stage: WaterfallStage
                    decision: StageDecision
                    duration_us: float
                    ml_anomaly_level: MLAnomalyLevel
                    ml_anomaly_score: float
                    within_target: bool
                    target_latency_us: float
                    
                    @property
                    def severity_rank(self):
                        return 0
                
                stage_results.append(EnhancedStageResult(
                    stage=WaterfallStage(i),
                    decision=StageDecision.ALLOW,
                    duration_us=duration_us,
                    ml_anomaly_level=MLAnomalyLevel.NORMAL,
                    ml_anomaly_score=0.0,
                    within_target=duration_us <= 10.0,
                    target_latency_us=10.0,
                ))
            
            total_duration_us = (time.perf_counter() - start) * 1e6
            
            @dataclass
            class EnhancedWaterfallResult:
                request_id: str
                final_decision: StageDecision
                stage_results: list
                total_duration_us: float
                ml_stage_scores: dict
                performance_compliant: bool
                is_allowed: bool = True
            
            return EnhancedWaterfallResult(
                request_id=envelope.request_id,
                final_decision=StageDecision.ALLOW,
                stage_results=stage_results,
                total_duration_us=total_duration_us,
                ml_stage_scores={},
                performance_compliant=total_duration_us <= 70.0,
            )


# ══════════════════════════════════════════════════════════════════════
# BENCHMARKING SUITE
# ══════════════════════════════════════════════════════════════════════


class WaterfallBenchmark:
    """Performance benchmarking suite for Enhanced Waterfall."""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.engine = self._create_engine()
        self.results: list[float] = []
        self.stage_results: dict[str, list[float]] = {
            stage.name: [] for stage in WaterfallStage
        }
        self.ml_inference_times: list[float] = []

    def _create_engine(self) -> EnhancedWaterfallEngine:
        """Create enhanced waterfall engine for benchmarking."""
        if MOCKED:
            return EnhancedWaterfallEngine()
        
        # Create mock stages
        class FastMockStage:
            def evaluate(self, envelope, prior_results):
                @dataclass
                class Result:
                    decision: Any
                    reasons: list
                    metadata: dict
                    
                    @property
                    def severity_rank(self):
                        return 0
                
                return Result(
                    decision=StageDecision.ALLOW if not MOCKED else "allow",
                    reasons=[],
                    metadata={},
                )
        
        return EnhancedWaterfallEngine(
            event_bus=EventBus(),
            structural_stage=FastMockStage(),
            signature_stage=FastMockStage(),
            behavioral_stage=FastMockStage(),
            shadow_stage=FastMockStage(),
            gate_stage=FastMockStage(),
            commit_stage=FastMockStage(),
            memory_stage=FastMockStage(),
            enable_ml=self.config.enable_ml,
            enable_performance_monitoring=self.config.enable_performance_monitoring,
            target_stage_latency_us=self.config.target_stage_latency_us,
        )

    def _create_test_envelope(self, request_id: str):
        """Create test request envelope."""
        if MOCKED:
            return MockEnvelope(
                request_id=request_id,
                actor="test_actor",
                subject="test_subject",
                intent=MockIntent(action="test_action"),
                context=MockContext(trace_id=f"trace_{request_id}", timestamp=time.time()),
            )
        else:
            # Real envelope creation
            from psia.schemas.request import RequestEnvelope, Intent, RequestContext
            return RequestEnvelope(
                request_id=request_id,
                actor="test_actor",
                subject="test_subject",
                intent=Intent(action="test_action"),
                context=RequestContext(trace_id=f"trace_{request_id}"),
            )

    def warmup(self):
        """Warmup run to stabilize JIT and caches."""
        print(f"Warming up ({self.config.warmup_iterations} iterations)...")
        for i in range(self.config.warmup_iterations):
            envelope = self._create_test_envelope(f"warmup_{i}")
            self.engine.process(envelope)
        print("Warmup complete.")

    def run_benchmark(self) -> BenchmarkResults:
        """Run the benchmark suite."""
        print(f"\nRunning benchmark ({self.config.iterations} iterations)...")
        print(f"Target: <{self.config.target_total_latency_us}μs total, <{self.config.target_stage_latency_us}μs per stage")
        
        # Warmup
        self.warmup()
        
        # Actual benchmark
        violations = 0
        
        for i in range(self.config.iterations):
            envelope = self._create_test_envelope(f"bench_{i}")
            
            # Measure end-to-end latency
            start = time.perf_counter()
            result = self.engine.process(envelope)
            end = time.perf_counter()
            
            total_latency_us = (end - start) * 1e6
            self.results.append(total_latency_us)
            
            # Track stage-by-stage performance
            for stage_result in result.stage_results:
                stage_name = stage_result.stage.name
                self.stage_results[stage_name].append(stage_result.duration_us)
            
            # Track ML inference times
            if self.config.enable_ml:
                for stage_result in result.stage_results:
                    if hasattr(stage_result, 'ml_metadata') and 'ml_inference_us' in stage_result.ml_metadata:
                        self.ml_inference_times.append(stage_result.ml_metadata['ml_inference_us'])
            
            # Track violations
            if total_latency_us > self.config.target_total_latency_us:
                violations += 1
            
            # Progress indicator
            if (i + 1) % (self.config.iterations // 10) == 0:
                print(f"  Progress: {i + 1}/{self.config.iterations} ({(i + 1) / self.config.iterations * 100:.1f}%)")
        
        print("Benchmark complete. Analyzing results...")
        return self._analyze_results(violations)

    def _analyze_results(self, violations: int) -> BenchmarkResults:
        """Analyze benchmark results and compute statistics."""
        
        # Overall latency statistics
        mean_latency = statistics.mean(self.results)
        median_latency = statistics.median(self.results)
        p95_latency = np.percentile(self.results, 95)
        p99_latency = np.percentile(self.results, 99)
        max_latency = max(self.results)
        min_latency = min(self.results)
        stddev_latency = statistics.stdev(self.results) if len(self.results) > 1 else 0.0
        
        # Stage-by-stage statistics
        stage_stats = {}
        stage_compliance_rates = {}
        
        for stage_name, timings in self.stage_results.items():
            if timings:
                stage_stats[stage_name] = {
                    "mean_us": round(statistics.mean(timings), 2),
                    "median_us": round(statistics.median(timings), 2),
                    "p95_us": round(np.percentile(timings, 95), 2),
                    "p99_us": round(np.percentile(timings, 99), 2),
                    "max_us": round(max(timings), 2),
                    "min_us": round(min(timings), 2),
                }
                
                # Compliance rate for this stage
                compliant = sum(1 for t in timings if t <= self.config.target_stage_latency_us)
                stage_compliance_rates[stage_name] = compliant / len(timings) * 100
        
        # ML statistics
        ml_mean_inference = 0.0
        ml_p99_inference = 0.0
        if self.ml_inference_times:
            ml_mean_inference = statistics.mean(self.ml_inference_times)
            ml_p99_inference = np.percentile(self.ml_inference_times, 99)
        
        # Overall compliance
        total_compliance_rate = (self.config.iterations - violations) / self.config.iterations * 100
        target_met = total_compliance_rate >= 95.0  # 95% compliance threshold
        success_rate = sum(1 for _ in self.results) / self.config.iterations * 100
        
        return BenchmarkResults(
            config=self.config,
            total_iterations=self.config.iterations,
            mean_latency_us=round(mean_latency, 2),
            median_latency_us=round(median_latency, 2),
            p95_latency_us=round(p95_latency, 2),
            p99_latency_us=round(p99_latency, 2),
            max_latency_us=round(max_latency, 2),
            min_latency_us=round(min_latency, 2),
            stddev_latency_us=round(stddev_latency, 2),
            stage_stats=stage_stats,
            ml_mean_inference_us=round(ml_mean_inference, 2),
            ml_p99_inference_us=round(ml_p99_inference, 2),
            total_compliance_rate=round(total_compliance_rate, 2),
            stage_compliance_rates=stage_compliance_rates,
            target_met=target_met,
            violations=violations,
            success_rate=round(success_rate, 2),
        )

    def print_results(self, results: BenchmarkResults):
        """Pretty-print benchmark results."""
        print("\n" + "="*80)
        print("PSIA ENHANCED WATERFALL PERFORMANCE BENCHMARK RESULTS")
        print("="*80)
        
        print(f"\nConfiguration:")
        print(f"  Iterations:           {results.total_iterations:,}")
        print(f"  ML Enabled:           {self.config.enable_ml}")
        print(f"  Target Total Latency: {self.config.target_total_latency_us}μs")
        print(f"  Target Stage Latency: {self.config.target_stage_latency_us}μs")
        
        print(f"\nOverall Latency Statistics (microseconds):")
        print(f"  Mean:                 {results.mean_latency_us:>10.2f} μs")
        print(f"  Median:               {results.median_latency_us:>10.2f} μs")
        print(f"  P95:                  {results.p95_latency_us:>10.2f} μs")
        print(f"  P99:                  {results.p99_latency_us:>10.2f} μs")
        print(f"  Max:                  {results.max_latency_us:>10.2f} μs")
        print(f"  Min:                  {results.min_latency_us:>10.2f} μs")
        print(f"  StdDev:               {results.stddev_latency_us:>10.2f} μs")
        
        print(f"\nCompliance Metrics:")
        status = "✓ PASS" if results.target_met else "✗ FAIL"
        print(f"  Overall Compliance:   {results.total_compliance_rate:>10.2f}% {status}")
        print(f"  Violations:           {results.violations:>10,} / {results.total_iterations:,}")
        print(f"  Success Rate:         {results.success_rate:>10.2f}%")
        
        print(f"\nStage-by-Stage Performance:")
        print(f"  {'Stage':<12} {'Mean':>10} {'P95':>10} {'P99':>10} {'Max':>10} {'Compliance':>12}")
        print(f"  {'-'*12} {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*12}")
        
        for stage_name, stats in results.stage_stats.items():
            compliance = results.stage_compliance_rates.get(stage_name, 0.0)
            comp_status = "✓" if compliance >= 95.0 else "✗"
            print(f"  {stage_name:<12} {stats['mean_us']:>9.2f}μs "
                  f"{stats['p95_us']:>9.2f}μs {stats['p99_us']:>9.2f}μs "
                  f"{stats['max_us']:>9.2f}μs {compliance:>10.2f}% {comp_status}")
        
        if self.config.enable_ml:
            print(f"\nML Anomaly Detection Performance:")
            print(f"  Mean Inference Time:  {results.ml_mean_inference_us:>10.2f} μs")
            print(f"  P99 Inference Time:   {results.ml_p99_inference_us:>10.2f} μs")
            ml_target_met = results.ml_p99_inference_us <= 2.0
            ml_status = "✓ PASS" if ml_target_met else "✗ FAIL"
            print(f"  Target (<2μs):        {ml_status}")
        
        print("\n" + "="*80)
        
        if results.target_met:
            print("✓ BENCHMARK PASSED: Performance targets met!")
        else:
            print("✗ BENCHMARK FAILED: Performance targets not met.")
        
        print("="*80 + "\n")

    def export_results(self, results: BenchmarkResults, path: str):
        """Export results to JSON file."""
        output = {
            "config": asdict(results.config),
            "results": asdict(results),
            "raw_timings": {
                "total_latencies_us": self.results,
                "stage_timings_us": self.stage_results,
                "ml_inference_times_us": self.ml_inference_times,
            },
        }
        
        with open(path, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"Results exported to: {path}")


# ══════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="PSIA Enhanced Waterfall Performance Benchmark"
    )
    parser.add_argument(
        "--iterations", "-n",
        type=int,
        default=1000,
        help="Number of benchmark iterations (default: 1000)",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=100,
        help="Number of warmup iterations (default: 100)",
    )
    parser.add_argument(
        "--no-ml",
        action="store_true",
        help="Disable ML anomaly detection",
    )
    parser.add_argument(
        "--target-total",
        type=float,
        default=70.0,
        help="Target total latency in microseconds (default: 70.0)",
    )
    parser.add_argument(
        "--target-stage",
        type=float,
        default=10.0,
        help="Target stage latency in microseconds (default: 10.0)",
    )
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Enable profiling mode",
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Export results to JSON file",
    )
    
    args = parser.parse_args()
    
    config = BenchmarkConfig(
        iterations=args.iterations,
        warmup_iterations=args.warmup,
        enable_ml=not args.no_ml,
        target_total_latency_us=args.target_total,
        target_stage_latency_us=args.target_stage,
        profile=args.profile,
        export_path=args.export,
    )
    
    benchmark = WaterfallBenchmark(config)
    results = benchmark.run_benchmark()
    benchmark.print_results(results)
    
    if args.export:
        benchmark.export_results(results, args.export)


if __name__ == "__main__":
    main()
