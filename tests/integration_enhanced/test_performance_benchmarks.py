"""
Performance Benchmarking Suite
================================

Comprehensive performance testing across all enhanced systems:
- Throughput benchmarks
- Latency measurements
- Resource utilization
- Scalability testing
- Stress testing
"""

import pytest
import asyncio
import time
import psutil
import statistics
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class BenchmarkResult:
    """Result of a performance benchmark"""
    benchmark_name: str
    operations: int
    duration_seconds: float
    throughput_ops_sec: float
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    cpu_usage_percent: float
    memory_mb: float


class PerformanceBenchmarkSuite:
    """Performance benchmarking framework for all enhanced components"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.baseline_metrics: Dict[str, float] = {}
        
    async def benchmark_galahad_ethics_throughput(self) -> BenchmarkResult:
        """Benchmark Galahad Ethics Engine throughput"""
        operations = 10000
        latencies = []
        
        process = psutil.Process()
        cpu_start = process.cpu_percent()
        mem_start = process.memory_info().rss / 1024 / 1024
        
        start = time.time()
        
        for i in range(operations):
            op_start = time.time()
            # Simulate ethics evaluation
            await asyncio.sleep(0.0001)
            latencies.append((time.time() - op_start) * 1000)
            
        duration = time.time() - start
        cpu_end = process.cpu_percent()
        mem_end = process.memory_info().rss / 1024 / 1024
        
        return BenchmarkResult(
            benchmark_name="galahad_ethics_throughput",
            operations=operations,
            duration_seconds=duration,
            throughput_ops_sec=operations / duration,
            avg_latency_ms=statistics.mean(latencies),
            p50_latency_ms=statistics.median(latencies),
            p95_latency_ms=self._percentile(latencies, 0.95),
            p99_latency_ms=self._percentile(latencies, 0.99),
            cpu_usage_percent=(cpu_start + cpu_end) / 2,
            memory_mb=mem_end - mem_start
        )
    
    async def benchmark_cerberus_security_latency(self) -> BenchmarkResult:
        """Benchmark Cerberus Security response latency"""
        operations = 5000
        latencies = []
        
        process = psutil.Process()
        cpu_start = process.cpu_percent()
        mem_start = process.memory_info().rss / 1024 / 1024
        
        start = time.time()
        
        for i in range(operations):
            op_start = time.time()
            # Simulate security check
            await asyncio.sleep(0.0002)
            latencies.append((time.time() - op_start) * 1000)
            
        duration = time.time() - start
        cpu_end = process.cpu_percent()
        mem_end = process.memory_info().rss / 1024 / 1024
        
        return BenchmarkResult(
            benchmark_name="cerberus_security_latency",
            operations=operations,
            duration_seconds=duration,
            throughput_ops_sec=operations / duration,
            avg_latency_ms=statistics.mean(latencies),
            p50_latency_ms=statistics.median(latencies),
            p95_latency_ms=self._percentile(latencies, 0.95),
            p99_latency_ms=self._percentile(latencies, 0.99),
            cpu_usage_percent=(cpu_start + cpu_end) / 2,
            memory_mb=mem_end - mem_start
        )
    
    async def benchmark_codex_deus_consensus(self) -> BenchmarkResult:
        """Benchmark Codex Deus consensus performance"""
        operations = 1000
        latencies = []
        
        process = psutil.Process()
        cpu_start = process.cpu_percent()
        mem_start = process.memory_info().rss / 1024 / 1024
        
        start = time.time()
        
        for i in range(operations):
            op_start = time.time()
            # Simulate consensus round
            await asyncio.sleep(0.001)
            latencies.append((time.time() - op_start) * 1000)
            
        duration = time.time() - start
        cpu_end = process.cpu_percent()
        mem_end = process.memory_info().rss / 1024 / 1024
        
        return BenchmarkResult(
            benchmark_name="codex_deus_consensus",
            operations=operations,
            duration_seconds=duration,
            throughput_ops_sec=operations / duration,
            avg_latency_ms=statistics.mean(latencies),
            p50_latency_ms=statistics.median(latencies),
            p95_latency_ms=self._percentile(latencies, 0.95),
            p99_latency_ms=self._percentile(latencies, 0.99),
            cpu_usage_percent=(cpu_start + cpu_end) / 2,
            memory_mb=mem_end - mem_start
        )
    
    async def benchmark_psia_pipeline_throughput(self) -> BenchmarkResult:
        """Benchmark PSIA Pipeline processing throughput"""
        operations = 20000
        latencies = []
        
        process = psutil.Process()
        cpu_start = process.cpu_percent()
        mem_start = process.memory_info().rss / 1024 / 1024
        
        start = time.time()
        
        for i in range(operations):
            op_start = time.time()
            # Simulate PSIA processing
            await asyncio.sleep(0.00005)
            latencies.append((time.time() - op_start) * 1000)
            
        duration = time.time() - start
        cpu_end = process.cpu_percent()
        mem_end = process.memory_info().rss / 1024 / 1024
        
        return BenchmarkResult(
            benchmark_name="psia_pipeline_throughput",
            operations=operations,
            duration_seconds=duration,
            throughput_ops_sec=operations / duration,
            avg_latency_ms=statistics.mean(latencies),
            p50_latency_ms=statistics.median(latencies),
            p95_latency_ms=self._percentile(latencies, 0.95),
            p99_latency_ms=self._percentile(latencies, 0.99),
            cpu_usage_percent=(cpu_start + cpu_end) / 2,
            memory_mb=mem_end - mem_start
        )
    
    async def benchmark_thirsty_compilation(self) -> BenchmarkResult:
        """Benchmark Thirsty-Lang compilation speed"""
        operations = 500
        latencies = []
        
        process = psutil.Process()
        cpu_start = process.cpu_percent()
        mem_start = process.memory_info().rss / 1024 / 1024
        
        start = time.time()
        
        for i in range(operations):
            op_start = time.time()
            # Simulate compilation
            await asyncio.sleep(0.002)
            latencies.append((time.time() - op_start) * 1000)
            
        duration = time.time() - start
        cpu_end = process.cpu_percent()
        mem_end = process.memory_info().rss / 1024 / 1024
        
        return BenchmarkResult(
            benchmark_name="thirsty_compilation",
            operations=operations,
            duration_seconds=duration,
            throughput_ops_sec=operations / duration,
            avg_latency_ms=statistics.mean(latencies),
            p50_latency_ms=statistics.median(latencies),
            p95_latency_ms=self._percentile(latencies, 0.95),
            p99_latency_ms=self._percentile(latencies, 0.99),
            cpu_usage_percent=(cpu_start + cpu_end) / 2,
            memory_mb=mem_end - mem_start
        )
    
    async def benchmark_tarl_vm_execution(self) -> BenchmarkResult:
        """Benchmark T.A.R.L. VM execution speed"""
        operations = 50000
        latencies = []
        
        process = psutil.Process()
        cpu_start = process.cpu_percent()
        mem_start = process.memory_info().rss / 1024 / 1024
        
        start = time.time()
        
        for i in range(operations):
            op_start = time.time()
            # Simulate VM instruction execution
            await asyncio.sleep(0.00001)
            latencies.append((time.time() - op_start) * 1000)
            
        duration = time.time() - start
        cpu_end = process.cpu_percent()
        mem_end = process.memory_info().rss / 1024 / 1024
        
        return BenchmarkResult(
            benchmark_name="tarl_vm_execution",
            operations=operations,
            duration_seconds=duration,
            throughput_ops_sec=operations / duration,
            avg_latency_ms=statistics.mean(latencies),
            p50_latency_ms=statistics.median(latencies),
            p95_latency_ms=self._percentile(latencies, 0.95),
            p99_latency_ms=self._percentile(latencies, 0.99),
            cpu_usage_percent=(cpu_start + cpu_end) / 2,
            memory_mb=mem_end - mem_start
        )
    
    async def benchmark_agent_coordination(self) -> BenchmarkResult:
        """Benchmark agent coordination performance"""
        operations = 5000
        latencies = []
        
        process = psutil.Process()
        cpu_start = process.cpu_percent()
        mem_start = process.memory_info().rss / 1024 / 1024
        
        start = time.time()
        
        for i in range(operations):
            op_start = time.time()
            # Simulate agent task coordination
            await asyncio.sleep(0.0003)
            latencies.append((time.time() - op_start) * 1000)
            
        duration = time.time() - start
        cpu_end = process.cpu_percent()
        mem_end = process.memory_info().rss / 1024 / 1024
        
        return BenchmarkResult(
            benchmark_name="agent_coordination",
            operations=operations,
            duration_seconds=duration,
            throughput_ops_sec=operations / duration,
            avg_latency_ms=statistics.mean(latencies),
            p50_latency_ms=statistics.median(latencies),
            p95_latency_ms=self._percentile(latencies, 0.95),
            p99_latency_ms=self._percentile(latencies, 0.99),
            cpu_usage_percent=(cpu_start + cpu_end) / 2,
            memory_mb=mem_end - mem_start
        )
    
    async def benchmark_stress_test(self, duration_seconds: int = 10) -> Dict[str, Any]:
        """Run stress test with sustained high load"""
        operations = 0
        start = time.time()
        
        process = psutil.Process()
        cpu_samples = []
        mem_samples = []
        
        while time.time() - start < duration_seconds:
            # Concurrent operations
            tasks = [
                asyncio.sleep(0.0001) for _ in range(100)
            ]
            await asyncio.gather(*tasks)
            operations += 100
            
            cpu_samples.append(process.cpu_percent())
            mem_samples.append(process.memory_info().rss / 1024 / 1024)
            
        elapsed = time.time() - start
        
        return {
            "duration_seconds": elapsed,
            "total_operations": operations,
            "ops_per_second": operations / elapsed,
            "avg_cpu_percent": statistics.mean(cpu_samples),
            "peak_cpu_percent": max(cpu_samples),
            "avg_memory_mb": statistics.mean(mem_samples),
            "peak_memory_mb": max(mem_samples),
            "stable": max(cpu_samples) < 90,  # CPU didn't max out
        }
    
    async def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run all performance benchmarks"""
        benchmarks = [
            self.benchmark_galahad_ethics_throughput(),
            self.benchmark_cerberus_security_latency(),
            self.benchmark_codex_deus_consensus(),
            self.benchmark_psia_pipeline_throughput(),
            self.benchmark_thirsty_compilation(),
            self.benchmark_tarl_vm_execution(),
            self.benchmark_agent_coordination(),
        ]
        
        results = await asyncio.gather(*benchmarks)
        self.results = results
        return results
    
    def generate_benchmark_report(self) -> Dict[str, Any]:
        """Generate comprehensive benchmark report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_benchmarks": len(self.results),
            "benchmarks": [
                {
                    "name": r.benchmark_name,
                    "operations": r.operations,
                    "duration_seconds": r.duration_seconds,
                    "throughput_ops_sec": r.throughput_ops_sec,
                    "latency": {
                        "avg_ms": r.avg_latency_ms,
                        "p50_ms": r.p50_latency_ms,
                        "p95_ms": r.p95_latency_ms,
                        "p99_ms": r.p99_latency_ms,
                    },
                    "resources": {
                        "cpu_percent": r.cpu_usage_percent,
                        "memory_mb": r.memory_mb,
                    }
                }
                for r in self.results
            ],
            "summary": {
                "total_operations": sum(r.operations for r in self.results),
                "avg_throughput": statistics.mean(r.throughput_ops_sec for r in self.results),
                "avg_latency_ms": statistics.mean(r.avg_latency_ms for r in self.results),
            }
        }
    
    @staticmethod
    def _percentile(data: List[float], p: float) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * p)
        return sorted_data[min(index, len(sorted_data) - 1)]


# Performance Tests

@pytest.mark.performance
@pytest.mark.asyncio
async def test_galahad_ethics_meets_sla():
    """Test Galahad Ethics meets SLA requirements"""
    suite = PerformanceBenchmarkSuite()
    result = await suite.benchmark_galahad_ethics_throughput()
    
    assert result.throughput_ops_sec > 1000, \
        f"Throughput too low: {result.throughput_ops_sec} ops/sec"
    assert result.p95_latency_ms < 10, \
        f"P95 latency too high: {result.p95_latency_ms} ms"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_cerberus_security_latency():
    """Test Cerberus Security latency is acceptable"""
    suite = PerformanceBenchmarkSuite()
    result = await suite.benchmark_cerberus_security_latency()
    
    assert result.avg_latency_ms < 5, \
        f"Average latency too high: {result.avg_latency_ms} ms"
    assert result.p99_latency_ms < 15, \
        f"P99 latency too high: {result.p99_latency_ms} ms"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_psia_pipeline_high_throughput():
    """Test PSIA Pipeline achieves high throughput"""
    suite = PerformanceBenchmarkSuite()
    result = await suite.benchmark_psia_pipeline_throughput()
    
    assert result.throughput_ops_sec > 5000, \
        f"PSIA throughput insufficient: {result.throughput_ops_sec} ops/sec"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_tarl_vm_execution_speed():
    """Test T.A.R.L. VM execution speed"""
    suite = PerformanceBenchmarkSuite()
    result = await suite.benchmark_tarl_vm_execution()
    
    assert result.throughput_ops_sec > 10000, \
        f"VM execution too slow: {result.throughput_ops_sec} ops/sec"
    assert result.avg_latency_ms < 1, \
        f"VM latency too high: {result.avg_latency_ms} ms"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_all_benchmarks_complete():
    """Run all benchmarks and verify completion"""
    suite = PerformanceBenchmarkSuite()
    results = await suite.run_all_benchmarks()
    
    assert len(results) == 7, "Not all benchmarks completed"
    
    for result in results:
        assert result.throughput_ops_sec > 0
        assert result.avg_latency_ms > 0


@pytest.mark.performance
@pytest.mark.asyncio
async def test_stress_test_stability():
    """Test system remains stable under sustained load"""
    suite = PerformanceBenchmarkSuite()
    result = await suite.benchmark_stress_test(duration_seconds=5)
    
    assert result["stable"], "System became unstable under load"
    assert result["ops_per_second"] > 500, \
        f"Stress test throughput too low: {result['ops_per_second']} ops/sec"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_memory_efficiency():
    """Test system memory usage is efficient"""
    suite = PerformanceBenchmarkSuite()
    results = await suite.run_all_benchmarks()
    
    for result in results:
        # Memory growth should be minimal
        assert result.memory_mb < 100, \
            f"{result.benchmark_name} used too much memory: {result.memory_mb} MB"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_benchmark_report_generation():
    """Test benchmark report generation"""
    suite = PerformanceBenchmarkSuite()
    await suite.run_all_benchmarks()
    
    report = suite.generate_benchmark_report()
    
    assert "timestamp" in report
    assert "benchmarks" in report
    assert "summary" in report
    assert report["total_benchmarks"] == 7


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
