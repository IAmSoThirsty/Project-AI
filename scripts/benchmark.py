"""
Performance benchmarking for Project AI API.
"""

import statistics
import time

import requests

API_BASE = "http://localhost:8001"


def benchmark_endpoint(
    name: str, method: str, endpoint: str, iterations: int = 100, **kwargs
) -> dict:
    """
    Benchmark an API endpoint.

    Args:
        name: Benchmark name
        method: HTTP method
        endpoint: API endpoint
        iterations: Number of iterations
        **kwargs: Additional request parameters

    Returns:
        Benchmark results
    """
    print(f"\n🔬 Benchmarking: {name}")
    print(f"   Iterations: {iterations}")

    times: list[float] = []
    errors = 0

    for i in range(iterations):
        start = time.time()
        try:
            response = requests.request(method, f"{API_BASE}{endpoint}", **kwargs)
            elapsed = (time.time() - start) * 1000  # Convert to ms
            times.append(elapsed)

            if response.status_code >= 400:
                errors += 1
        except Exception as e:
            errors += 1
            print(f"   Error on iteration {i+1}: {e}")

    if not times:
        return {"error": "All requests failed"}

    results = {
        "name": name,
        "iterations": iterations,
        "errors": errors,
        "min_ms": min(times),
        "max_ms": max(times),
        "mean_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0,
        "p95_ms": sorted(times)[int(len(times) * 0.95)],
        "p99_ms": sorted(times)[int(len(times) * 0.99)],
    }

    print(f"   Mean: {results['mean_ms']:.2f}ms")
    print(f"   P95: {results['p95_ms']:.2f}ms")
    print(f"   P99: {results['p99_ms']:.2f}ms")
    print(f"   Errors: {errors}/{iterations}")

    return results


def run_benchmarks():
    """Run all benchmarks."""
    print("=" * 60)
    print("Project AI - Performance Benchmarks")
    print("=" * 60)

    benchmarks = []

    # Health check
    benchmarks.append(
        benchmark_endpoint("Health Check", "GET", "/health", iterations=200)
    )

    # TARL retrieval
    benchmarks.append(benchmark_endpoint("TARL Rules", "GET", "/tarl", iterations=100))

    # Audit log
    benchmarks.append(
        benchmark_endpoint(
            "Audit Log (limit=10)", "GET", "/audit?limit=10", iterations=100
        )
    )

    # Intent submission
    intent_data = {
        "actor": "human",
        "action": "read",
        "target": "/test",
        "origin": "benchmark",
    }
    benchmarks.append(
        benchmark_endpoint(
            "Submit Intent", "POST", "/intent", iterations=50, json=intent_data
        )
    )

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'Endpoint':<30} {'Mean (ms)':<12} {'P95 (ms)':<12} {'Errors'}")
    print("-" * 60)

    for b in benchmarks:
        if "error" not in b:
            print(
                f"{b['name']:<30} {b['mean_ms']:<12.2f} {b['p95_ms']:<12.2f} {b['errors']}"
            )

    print("=" * 60)


if __name__ == "__main__":
    run_benchmarks()
