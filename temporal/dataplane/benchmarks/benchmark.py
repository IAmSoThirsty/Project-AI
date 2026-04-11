"""
Data Plane Benchmarks

Comprehensive benchmarking suite for measuring throughput, latency, and resource utilization.
"""

import asyncio
import time
import statistics
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
import random
import json

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Results from a benchmark run."""
    name: str
    duration_seconds: float
    operations: int
    bytes_transferred: int
    avg_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_mbps: float
    ops_per_second: float
    errors: int = 0


class DataPlaneBenchmark:
    """Benchmark suite for data plane components."""

    def __init__(self, client):
        """Initialize benchmark with data plane client."""
        self.client = client
        self.results: List[BenchmarkResult] = []

    async def run_all(self) -> List[BenchmarkResult]:
        """Run all benchmarks."""
        logger.info("Starting comprehensive benchmark suite...")

        # Run benchmarks sequentially
        await self.bench_small_messages()
        await self.bench_large_messages()
        await self.bench_cache_operations()
        await self.bench_storage_upload()
        await self.bench_storage_download()
        await self.bench_mixed_workload()

        return self.results

    async def bench_small_messages(self, num_messages: int = 10000, message_size: int = 1024) -> BenchmarkResult:
        """Benchmark small message throughput."""
        logger.info(f"Benchmarking small messages ({num_messages} x {message_size} bytes)...")

        latencies = []
        errors = 0
        data = b"x" * message_size

        start = time.perf_counter()

        for i in range(num_messages):
            msg_start = time.perf_counter()
            try:
                await self.client.send_message(
                    topic="benchmark.small",
                    data=data,
                    agent_id=f"bench-{i}",
                    use_cache=False,  # Don't pollute cache during benchmarks
                )
                latencies.append((time.perf_counter() - msg_start) * 1000)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                errors += 1

        end = time.perf_counter()
        duration = end - start

        result = BenchmarkResult(
            name="Small Messages (1KB)",
            duration_seconds=duration,
            operations=num_messages,
            bytes_transferred=num_messages * message_size,
            avg_latency_ms=statistics.mean(latencies) if latencies else 0,
            p50_latency_ms=statistics.median(latencies) if latencies else 0,
            p95_latency_ms=self._percentile(latencies, 0.95) if latencies else 0,
            p99_latency_ms=self._percentile(latencies, 0.99) if latencies else 0,
            throughput_mbps=(num_messages * message_size / duration) / (1024 * 1024) * 8,
            ops_per_second=num_messages / duration,
            errors=errors,
        )

        self.results.append(result)
        logger.info(f"Small message benchmark: {result.throughput_mbps:.2f} Mbps, {result.ops_per_second:.0f} ops/sec")
        return result

    async def bench_large_messages(self, num_messages: int = 100, message_size: int = 10 * 1024 * 1024) -> BenchmarkResult:
        """Benchmark large message throughput (storage path)."""
        logger.info(f"Benchmarking large messages ({num_messages} x {message_size // (1024*1024)}MB)...")

        latencies = []
        errors = 0
        data = b"y" * message_size

        start = time.perf_counter()

        for i in range(num_messages):
            msg_start = time.perf_counter()
            try:
                await self.client.send_message(
                    topic="benchmark.large",
                    data=data,
                    agent_id=f"bench-large-{i}",
                    use_cache=False,
                )
                latencies.append((time.perf_counter() - msg_start) * 1000)
            except Exception as e:
                logger.error(f"Error sending large message: {e}")
                errors += 1

        end = time.perf_counter()
        duration = end - start

        result = BenchmarkResult(
            name="Large Messages (10MB)",
            duration_seconds=duration,
            operations=num_messages,
            bytes_transferred=num_messages * message_size,
            avg_latency_ms=statistics.mean(latencies) if latencies else 0,
            p50_latency_ms=statistics.median(latencies) if latencies else 0,
            p95_latency_ms=self._percentile(latencies, 0.95) if latencies else 0,
            p99_latency_ms=self._percentile(latencies, 0.99) if latencies else 0,
            throughput_mbps=(num_messages * message_size / duration) / (1024 * 1024) * 8,
            ops_per_second=num_messages / duration,
            errors=errors,
        )

        self.results.append(result)
        logger.info(f"Large message benchmark: {result.throughput_mbps:.2f} Mbps, {result.ops_per_second:.0f} ops/sec")
        return result

    async def bench_cache_operations(self, num_operations: int = 100000) -> BenchmarkResult:
        """Benchmark cache get/set operations."""
        logger.info(f"Benchmarking cache operations ({num_operations} ops)...")

        latencies = []
        errors = 0

        start = time.perf_counter()

        for i in range(num_operations):
            key = f"bench:cache:{i % 1000}"  # Reuse keys for realistic cache hits
            value = f"value-{i}".encode('utf-8')

            op_start = time.perf_counter()
            try:
                # Mix of reads and writes
                if i % 3 == 0:
                    await self.client.cache_set(key, value)
                else:
                    await self.client.cache_get(key)
                latencies.append((time.perf_counter() - op_start) * 1000)
            except Exception as e:
                logger.error(f"Cache error: {e}")
                errors += 1

        end = time.perf_counter()
        duration = end - start

        result = BenchmarkResult(
            name="Cache Operations",
            duration_seconds=duration,
            operations=num_operations,
            bytes_transferred=num_operations * 50,  # Approximate
            avg_latency_ms=statistics.mean(latencies) if latencies else 0,
            p50_latency_ms=statistics.median(latencies) if latencies else 0,
            p95_latency_ms=self._percentile(latencies, 0.95) if latencies else 0,
            p99_latency_ms=self._percentile(latencies, 0.99) if latencies else 0,
            throughput_mbps=0,  # Not applicable
            ops_per_second=num_operations / duration,
            errors=errors,
        )

        self.results.append(result)
        logger.info(f"Cache benchmark: {result.ops_per_second:.0f} ops/sec")
        return result

    async def bench_storage_upload(self, num_files: int = 100, file_size: int = 5 * 1024 * 1024) -> BenchmarkResult:
        """Benchmark storage upload throughput."""
        logger.info(f"Benchmarking storage uploads ({num_files} x {file_size // (1024*1024)}MB)...")

        latencies = []
        errors = 0
        data = b"z" * file_size

        start = time.perf_counter()

        for i in range(num_files):
            upload_start = time.perf_counter()
            try:
                await self.client.upload_artifact(
                    artifact_name=f"bench-{i}.bin",
                    data=data,
                    artifact_type="benchmark",
                )
                latencies.append((time.perf_counter() - upload_start) * 1000)
            except Exception as e:
                logger.error(f"Upload error: {e}")
                errors += 1

        end = time.perf_counter()
        duration = end - start

        result = BenchmarkResult(
            name="Storage Upload (5MB)",
            duration_seconds=duration,
            operations=num_files,
            bytes_transferred=num_files * file_size,
            avg_latency_ms=statistics.mean(latencies) if latencies else 0,
            p50_latency_ms=statistics.median(latencies) if latencies else 0,
            p95_latency_ms=self._percentile(latencies, 0.95) if latencies else 0,
            p99_latency_ms=self._percentile(latencies, 0.99) if latencies else 0,
            throughput_mbps=(num_files * file_size / duration) / (1024 * 1024) * 8,
            ops_per_second=num_files / duration,
            errors=errors,
        )

        self.results.append(result)
        logger.info(f"Storage upload benchmark: {result.throughput_mbps:.2f} Mbps")
        return result

    async def bench_storage_download(self, num_files: int = 100) -> BenchmarkResult:
        """Benchmark storage download throughput."""
        logger.info(f"Benchmarking storage downloads ({num_files} files)...")

        latencies = []
        errors = 0
        total_bytes = 0

        start = time.perf_counter()

        for i in range(num_files):
            download_start = time.perf_counter()
            try:
                # Download from previously uploaded files
                data = await self.client.download_artifact(
                    object_key=f"artifacts/benchmark/{time.strftime('%Y/%m/%d')}/bench-{i}.bin",
                    use_cache=False,
                )
                total_bytes += len(data)
                latencies.append((time.perf_counter() - download_start) * 1000)
            except Exception as e:
                logger.debug(f"Download error (expected if file doesn't exist): {e}")
                errors += 1

        end = time.perf_counter()
        duration = end - start

        if not latencies:
            latencies = [0]
            total_bytes = 0

        result = BenchmarkResult(
            name="Storage Download (5MB)",
            duration_seconds=duration,
            operations=num_files - errors,
            bytes_transferred=total_bytes,
            avg_latency_ms=statistics.mean(latencies) if latencies else 0,
            p50_latency_ms=statistics.median(latencies) if latencies else 0,
            p95_latency_ms=self._percentile(latencies, 0.95) if latencies else 0,
            p99_latency_ms=self._percentile(latencies, 0.99) if latencies else 0,
            throughput_mbps=(total_bytes / duration) / (1024 * 1024) * 8 if duration > 0 else 0,
            ops_per_second=(num_files - errors) / duration if duration > 0 else 0,
            errors=errors,
        )

        self.results.append(result)
        logger.info(f"Storage download benchmark: {result.throughput_mbps:.2f} Mbps")
        return result

    async def bench_mixed_workload(self, duration_seconds: int = 60) -> BenchmarkResult:
        """Benchmark mixed workload (realistic scenario)."""
        logger.info(f"Benchmarking mixed workload ({duration_seconds}s)...")

        latencies = []
        errors = 0
        operations = 0
        total_bytes = 0

        start = time.perf_counter()
        end_time = start + duration_seconds

        while time.perf_counter() < end_time:
            op_type = random.choices(
                ["small_msg", "large_msg", "cache_get", "cache_set"],
                weights=[40, 10, 30, 20],
            )[0]

            op_start = time.perf_counter()
            try:
                if op_type == "small_msg":
                    data = b"x" * 1024
                    await self.client.send_message("bench.mixed", data, "agent-mixed")
                    total_bytes += len(data)

                elif op_type == "large_msg":
                    data = b"y" * (1024 * 1024)  # 1MB
                    await self.client.send_message("bench.mixed", data, "agent-mixed")
                    total_bytes += len(data)

                elif op_type == "cache_get":
                    await self.client.cache_get(f"bench:mixed:{random.randint(0, 100)}")

                elif op_type == "cache_set":
                    await self.client.cache_set(
                        f"bench:mixed:{random.randint(0, 100)}",
                        b"value"
                    )

                latencies.append((time.perf_counter() - op_start) * 1000)
                operations += 1

            except Exception as e:
                logger.error(f"Mixed workload error: {e}")
                errors += 1

        duration = time.perf_counter() - start

        result = BenchmarkResult(
            name="Mixed Workload",
            duration_seconds=duration,
            operations=operations,
            bytes_transferred=total_bytes,
            avg_latency_ms=statistics.mean(latencies) if latencies else 0,
            p50_latency_ms=statistics.median(latencies) if latencies else 0,
            p95_latency_ms=self._percentile(latencies, 0.95) if latencies else 0,
            p99_latency_ms=self._percentile(latencies, 0.99) if latencies else 0,
            throughput_mbps=(total_bytes / duration) / (1024 * 1024) * 8,
            ops_per_second=operations / duration,
            errors=errors,
        )

        self.results.append(result)
        logger.info(f"Mixed workload: {result.throughput_mbps:.2f} Mbps, {result.ops_per_second:.0f} ops/sec")
        return result

    @staticmethod
    def _percentile(data: List[float], percentile: float) -> float:
        """Calculate percentile from sorted data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def print_results(self) -> None:
        """Print benchmark results in a formatted table."""
        print("\n" + "=" * 100)
        print("DATA PLANE BENCHMARK RESULTS")
        print("=" * 100)
        print(f"{'Benchmark':<30} {'Ops/sec':>12} {'Throughput':>12} {'Avg Lat':>10} {'P99 Lat':>10} {'Errors':>8}")
        print("-" * 100)

        for result in self.results:
            throughput_str = f"{result.throughput_mbps:.1f} Mbps" if result.throughput_mbps > 0 else "N/A"
            print(
                f"{result.name:<30} "
                f"{result.ops_per_second:>12.0f} "
                f"{throughput_str:>12} "
                f"{result.avg_latency_ms:>9.2f}ms "
                f"{result.p99_latency_ms:>9.2f}ms "
                f"{result.errors:>8}"
            )

        print("=" * 100)

        # Calculate aggregate throughput
        total_throughput = sum(r.throughput_mbps for r in self.results if r.throughput_mbps > 0)
        total_throughput_gbps = total_throughput / 1000
        print(f"\nAggregate Throughput: {total_throughput_gbps:.2f} GB/s")
        print(f"Target: 10 GB/s | Current: {total_throughput_gbps:.2f} GB/s | " +
              f"Achievement: {(total_throughput_gbps / 10) * 100:.1f}%")

    def save_results(self, filename: str = "benchmark_results.json") -> None:
        """Save results to JSON file."""
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": [
                {
                    "name": r.name,
                    "duration_seconds": r.duration_seconds,
                    "operations": r.operations,
                    "bytes_transferred": r.bytes_transferred,
                    "avg_latency_ms": r.avg_latency_ms,
                    "p50_latency_ms": r.p50_latency_ms,
                    "p95_latency_ms": r.p95_latency_ms,
                    "p99_latency_ms": r.p99_latency_ms,
                    "throughput_mbps": r.throughput_mbps,
                    "ops_per_second": r.ops_per_second,
                    "errors": r.errors,
                }
                for r in self.results
            ]
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Results saved to {filename}")
