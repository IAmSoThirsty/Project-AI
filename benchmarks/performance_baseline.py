"""
Performance Baseline Benchmarks
Establishes baseline metrics for production deployment.
"""

import time
import statistics
from typing import List, Dict, Any


def benchmark_function(func, iterations: int = 1000) -> Dict[str, float]:
    """Benchmark a function with multiple iterations."""
    times: List[float] = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms
    
    return {
        "mean_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0,
        "p95_ms": statistics.quantiles(times, n=20)[18],  # 95th percentile
        "p99_ms": statistics.quantiles(times, n=100)[98],  # 99th percentile
    }


def test_import_performance():
    """Test basic import performance."""
    def import_test():
        import json
        import hashlib
        import datetime
    
    return benchmark_function(import_test, 100)


def test_crypto_performance():
    """Test cryptographic operations."""
    from cryptography.fernet import Fernet
    
    key = Fernet.generate_key()
    f = Fernet(key)
    test_data = b"Performance test data" * 100
    
    def encrypt_decrypt():
        encrypted = f.encrypt(test_data)
        f.decrypt(encrypted)
    
    return benchmark_function(encrypt_decrypt, 100)


def test_json_performance():
    """Test JSON serialization."""
    test_obj = [{"key": "value", "nested": {"data": [1, 2, 3] * 10}} for _ in range(10)]
    
    def json_ops():
        serialized = __import__('json').dumps(test_obj)
        __import__('json').loads(serialized)
    
    return benchmark_function(json_ops, 100)


BASELINE_TARGETS = {
    "import_performance": {"mean_ms": 5.0, "p95_ms": 10.0},
    "crypto_performance": {"mean_ms": 2.0, "p95_ms": 5.0},
    "json_performance": {"mean_ms": 1.0, "p95_ms": 2.0},
}


def run_all_benchmarks() -> Dict[str, Any]:
    """Run all performance benchmarks."""
    results = {
        "import_performance": test_import_performance(),
        "crypto_performance": test_crypto_performance(),
        "json_performance": test_json_performance(),
    }
    
    # Check against baselines
    passed = True
    for test_name, metrics in results.items():
        if test_name in BASELINE_TARGETS:
            target = BASELINE_TARGETS[test_name]
            if metrics["mean_ms"] > target["mean_ms"] * 2:
                passed = False
                print(f"⚠️  {test_name}: mean {metrics['mean_ms']:.2f}ms exceeds target {target['mean_ms']}ms")
            else:
                print(f"✅ {test_name}: mean {metrics['mean_ms']:.2f}ms (target: {target['mean_ms']}ms)")
    
    results["overall_pass"] = passed
    return results


if __name__ == "__main__":
    print("🚀 Running Performance Benchmarks...\n")
    results = run_all_benchmarks()
    
    print(f"\n{'='*60}")
    print("BENCHMARK SUMMARY")
    print(f"{'='*60}")
    
    for test_name, metrics in results.items():
        if test_name != "overall_pass":
            print(f"\n{test_name}:")
            print(f"  Mean: {metrics['mean_ms']:.3f}ms")
            print(f"  P95:  {metrics['p95_ms']:.3f}ms")
            print(f"  P99:  {metrics['p99_ms']:.3f}ms")
    
    if results["overall_pass"]:
        print("\n✅ All benchmarks PASSED")
    else:
        print("\n⚠️  Some benchmarks exceeded targets")
