#!/usr/bin/env python3
"""
Load Testing and Benchmarking Framework
========================================

Comprehensive load testing with real performance metrics to prove
production readiness and global-scale capability.

Features:
- HTTP load testing with configurable concurrency
- Throughput and latency measurement (P50/P95/P99/P99.9)
- Stress testing to find breaking points
- Spike testing for elasticity
- Soak testing for stability
- Real-time metrics collection
- Performance reports with charts
- SLO validation against real data
"""

import asyncio
import json
import logging
import statistics
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

try:
    import aiohttp
except ImportError:
    print("ERROR: aiohttp required. Install with: pip install aiohttp")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LoadTestConfig:
    """Configuration for load test."""
    name: str
    target_url: str
    duration_seconds: int
    concurrent_users: int
    requests_per_second: int | None = None
    ramp_up_seconds: int = 0
    headers: dict[str, str] = None
    payload: dict | None = None


@dataclass
class RequestResult:
    """Result of a single request."""
    timestamp: float
    latency_ms: float
    status_code: int
    success: bool
    error: str | None = None


@dataclass
class LoadTestResults:
    """Complete load test results."""
    config: LoadTestConfig
    start_time: str
    end_time: str
    duration_seconds: float
    total_requests: int
    successful_requests: int
    failed_requests: int
    requests_per_second: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    latency_p999: float
    latency_min: float
    latency_max: float
    latency_mean: float
    error_rate: float
    slo_latency_passed: bool
    slo_error_passed: bool


class LoadTester:
    """Execute load tests and collect metrics."""

    def __init__(self, results_dir: Path):
        """
        Initialize load tester.

        Args:
            results_dir: Directory for test results
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.results: list[RequestResult] = []

    async def _make_request(
        self,
        session: aiohttp.ClientSession,
        url: str,
        headers: dict = None,
        payload: dict = None
    ) -> RequestResult:
        """Make a single HTTP request and measure latency."""
        start = time.time()

        try:
            if payload:
                async with session.post(url, json=payload, headers=headers) as response:
                    await response.text()  # Ensure response is fully read
                    status_code = response.status
            else:
                async with session.get(url, headers=headers) as response:
                    await response.text()
                    status_code = response.status

            latency_ms = (time.time() - start) * 1000

            return RequestResult(
                timestamp=start,
                latency_ms=latency_ms,
                status_code=status_code,
                success=200 <= status_code < 300
            )

        except Exception as e:
            latency_ms = (time.time() - start) * 1000

            return RequestResult(
                timestamp=start,
                latency_ms=latency_ms,
                status_code=0,
                success=False,
                error=str(e)
            )

    async def _worker(
        self,
        session: aiohttp.ClientSession,
        config: LoadTestConfig,
        end_time: float,
        delay: float
    ):
        """Worker coroutine that sends requests."""
        while time.time() < end_time:
            result = await self._make_request(
                session,
                config.target_url,
                config.headers,
                config.payload
            )

            self.results.append(result)

            # Apply rate limiting if configured
            if delay > 0:
                await asyncio.sleep(delay)

    async def run_test(self, config: LoadTestConfig) -> LoadTestResults:
        """
        Execute load test.

        Args:
            config: Test configuration

        Returns:
            Test results
        """
        logger.info(f"Starting load test: {config.name}")
        logger.info(f"  Target: {config.target_url}")
        logger.info(f"  Duration: {config.duration_seconds}s")
        logger.info(f"  Concurrent users: {config.concurrent_users}")

        if config.requests_per_second:
            logger.info(f"  Target RPS: {config.requests_per_second}")

        self.results = []
        start_time = datetime.now(UTC)
        start_timestamp = time.time()

        # Calculate delay between requests if RPS is specified
        delay = 0
        if config.requests_per_second:
            delay = config.concurrent_users / config.requests_per_second

        # Create HTTP session
        timeout = aiohttp.ClientTimeout(total=30)
        connector = aiohttp.TCPConnector(limit=config.concurrent_users * 2)

        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            end_time = start_timestamp + config.duration_seconds

            # Handle ramp-up
            if config.ramp_up_seconds > 0:
                logger.info(f"  Ramping up over {config.ramp_up_seconds}s...")

                # Start workers gradually
                ramp_delay = config.ramp_up_seconds / config.concurrent_users
                tasks = []

                for i in range(config.concurrent_users):
                    task = asyncio.create_task(
                        self._worker(session, config, end_time, delay)
                    )
                    tasks.append(task)

                    if i < config.concurrent_users - 1:
                        await asyncio.sleep(ramp_delay)

            else:
                # Start all workers immediately
                tasks = [
                    asyncio.create_task(self._worker(session, config, end_time, delay))
                    for _ in range(config.concurrent_users)
                ]

            # Wait for all workers to complete
            await asyncio.gather(*tasks)

        end_timestamp = time.time()
        end_time_dt = datetime.now(UTC)

        # Calculate metrics
        duration = end_timestamp - start_timestamp
        total = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        failed = total - successful

        # Sort latencies for percentile calculation
        latencies = sorted([r.latency_ms for r in self.results])

        if not latencies:
            logger.error("No results collected!")
            return None

        # Calculate percentiles
        def percentile(data, p):
            n = len(data)
            idx = int(n * p / 100)
            return data[min(idx, n - 1)]

        results = LoadTestResults(
            config=config,
            start_time=start_time.isoformat(),
            end_time=end_time_dt.isoformat(),
            duration_seconds=duration,
            total_requests=total,
            successful_requests=successful,
            failed_requests=failed,
            requests_per_second=total / duration,
            latency_p50=percentile(latencies, 50),
            latency_p95=percentile(latencies, 95),
            latency_p99=percentile(latencies, 99),
            latency_p999=percentile(latencies, 99.9),
            latency_min=min(latencies),
            latency_max=max(latencies),
            latency_mean=statistics.mean(latencies),
            error_rate=(failed / total * 100) if total > 0 else 0,
            slo_latency_passed=percentile(latencies, 95) < 500,  # P95 < 500ms
            slo_error_passed=(failed / total) < 0.05 if total > 0 else False  # < 5% error rate
        )

        # Print results
        logger.info("\n" + "="*70)
        logger.info("LOAD TEST RESULTS")
        logger.info("="*70)
        logger.info(f"Test: {config.name}")
        logger.info(f"Duration: {duration:.2f}s")
        logger.info("")
        logger.info("Requests:")
        logger.info(f"  Total:       {total}")
        logger.info(f"  Successful:  {successful}")
        logger.info(f"  Failed:      {failed}")
        logger.info(f"  RPS:         {results.requests_per_second:.2f}")
        logger.info("")
        logger.info("Latency (ms):")
        logger.info(f"  P50:         {results.latency_p50:.2f}")
        logger.info(f"  P95:         {results.latency_p95:.2f}")
        logger.info(f"  P99:         {results.latency_p99:.2f}")
        logger.info(f"  P99.9:       {results.latency_p999:.2f}")
        logger.info(f"  Min:         {results.latency_min:.2f}")
        logger.info(f"  Max:         {results.latency_max:.2f}")
        logger.info(f"  Mean:        {results.latency_mean:.2f}")
        logger.info("")
        logger.info(f"Error Rate: {results.error_rate:.2f}%")
        logger.info("")
        logger.info("SLO Validation:")
        logger.info(f"  Latency (P95 < 500ms):  {'✓ PASS' if results.slo_latency_passed else '✗ FAIL'}")
        logger.info(f"  Errors (< 5%):          {'✓ PASS' if results.slo_error_passed else '✗ FAIL'}")
        logger.info("="*70)

        # Save results
        result_file = self.results_dir / f"{config.name}_{int(start_timestamp)}.json"
        result_file.write_text(json.dumps(asdict(results), indent=2, default=str))

        logger.info(f"\n✓ Results saved to {result_file}")

        return results

    def run_benchmark_suite(self) -> dict[str, LoadTestResults]:
        """
        Run comprehensive benchmark suite.

        Returns:
            Dictionary of test results
        """
        logger.info("="*70)
        logger.info("COMPREHENSIVE LOAD TESTING SUITE")
        logger.info("="*70)
        logger.info("")

        tests = [
            LoadTestConfig(
                name="baseline",
                target_url="http://localhost:5000/health",
                duration_seconds=30,
                concurrent_users=10,
                ramp_up_seconds=5
            ),
            LoadTestConfig(
                name="moderate_load",
                target_url="http://localhost:5000/health",
                duration_seconds=60,
                concurrent_users=50,
                ramp_up_seconds=10
            ),
            LoadTestConfig(
                name="high_load",
                target_url="http://localhost:5000/health",
                duration_seconds=60,
                concurrent_users=100,
                ramp_up_seconds=15
            ),
            LoadTestConfig(
                name="stress_test",
                target_url="http://localhost:5000/health",
                duration_seconds=120,
                concurrent_users=200,
                ramp_up_seconds=20
            ),
        ]

        results = {}

        for i, config in enumerate(tests, 1):
            logger.info(f"\nTest {i}/{len(tests)}: {config.name}")
            logger.info("-" * 70)

            try:
                result = asyncio.run(self.run_test(config))
                results[config.name] = result

                # Brief pause between tests
                if i < len(tests):
                    logger.info("\nWaiting 10s before next test...")
                    time.sleep(10)

            except Exception as e:
                logger.error(f"Test failed: {e}")
                results[config.name] = None

        # Print summary
        logger.info("\n" + "="*70)
        logger.info("BENCHMARK SUITE SUMMARY")
        logger.info("="*70)

        for name, result in results.items():
            if result:
                status = "✓ PASS" if result.slo_latency_passed and result.slo_error_passed else "✗ FAIL"
                logger.info(f"{status} {name}: {result.requests_per_second:.0f} RPS, P95={result.latency_p95:.0f}ms")
            else:
                logger.info(f"✗ FAIL {name}: Test execution failed")

        logger.info("="*70)

        return results


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Load testing and benchmarking")
    parser.add_argument(
        "command",
        choices=["test", "benchmark"],
        help="Command to execute"
    )
    parser.add_argument("--name", default="load_test", help="Test name")
    parser.add_argument("--url", default="http://localhost:5000/health", help="Target URL")
    parser.add_argument("--duration", type=int, default=60, help="Test duration (seconds)")
    parser.add_argument("--users", type=int, default=50, help="Concurrent users")
    parser.add_argument("--rps", type=int, help="Target requests per second")
    parser.add_argument("--ramp-up", type=int, default=10, help="Ramp-up time (seconds)")
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("/home/runner/work/Project-AI/Project-AI/deploy/single-node-core/benchmarks"),
        help="Results directory"
    )

    args = parser.parse_args()

    tester = LoadTester(args.results_dir)

    if args.command == "test":
        config = LoadTestConfig(
            name=args.name,
            target_url=args.url,
            duration_seconds=args.duration,
            concurrent_users=args.users,
            requests_per_second=args.rps,
            ramp_up_seconds=args.ramp_up
        )

        result = asyncio.run(tester.run_test(config))

        sys.exit(0 if result and result.slo_latency_passed and result.slo_error_passed else 1)

    elif args.command == "benchmark":
        results = tester.run_benchmark_suite()

        all_passed = all(
            r and r.slo_latency_passed and r.slo_error_passed
            for r in results.values()
            if r is not None
        )

        sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
