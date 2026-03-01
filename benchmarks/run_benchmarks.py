"""
PSIA Performance Benchmarks — Real Hardware Measurements.

Measures actual cryptographic operation throughput on the current hardware
to produce factual performance claims for the PSIA research paper.

Benchmarks:
    1. Ed25519 key generation throughput
    2. Ed25519 sign throughput (varying payload sizes)
    3. Ed25519 verify throughput
    4. RFC 3161 timestamp issuance throughput
    5. RFC 3161 token verification throughput
    6. Ledger append throughput
    7. Ledger block sealing (incl. Merkle root, signing, timestamping)
    8. Capability token issuance throughput
    9. Full pipeline (keygen → sign → verify → timestamp)

Each benchmark reports:
    - Ops/sec (mean, p50, p95, p99)
    - Latency per operation (mean, p50, p95, p99)
    - Total execution time
    - Hardware info
"""

from __future__ import annotations

import os
import platform
import statistics
import sys
import time
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from psia.canonical.capability_authority import CapabilityAuthority
from psia.canonical.ledger import DurableLedger, ExecutionRecord
from psia.crypto.ed25519_provider import Ed25519Provider, KeyStore
from psia.crypto.rfc3161_provider import LocalTSA
from psia.schemas.capability import CapabilityScope

# ── Configuration ───────────────────────────────────────────────────────

WARMUP_ITERATIONS = 50
BENCHMARK_ITERATIONS = 1000
PAYLOAD_SIZES = [32, 256, 1024, 4096]


# ── Utilities ───────────────────────────────────────────────────────────


def get_hardware_info() -> dict:
    """Collect hardware information for the benchmark report."""
    return {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def percentile(data: list[float], p: int) -> float:
    """Compute the p-th percentile of a list of values."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * p / 100
    f = int(k)
    c = min(f + 1, len(sorted_data) - 1)
    if f == c:
        return sorted_data[f]
    return sorted_data[f] * (c - k) + sorted_data[c] * (k - f)


def run_benchmark(
    name: str,
    func: callable,  # type: ignore[valid-type]
    iterations: int = BENCHMARK_ITERATIONS,
    warmup: int = WARMUP_ITERATIONS,
) -> dict:
    """Run a benchmark function and collect stats."""
    # Warmup
    for _ in range(warmup):
        func()

    # Benchmark
    latencies: list[float] = []
    start = time.perf_counter()
    for _ in range(iterations):
        t0 = time.perf_counter()
        func()
        t1 = time.perf_counter()
        latencies.append(t1 - t0)
    total_time = time.perf_counter() - start

    ops_per_sec = iterations / total_time if total_time > 0 else float("inf")

    return {
        "name": name,
        "iterations": iterations,
        "total_time_sec": round(total_time, 6),
        "ops_per_sec": round(ops_per_sec, 2),
        "latency_mean_us": round(statistics.mean(latencies) * 1e6, 2),
        "latency_p50_us": round(percentile(latencies, 50) * 1e6, 2),
        "latency_p95_us": round(percentile(latencies, 95) * 1e6, 2),
        "latency_p99_us": round(percentile(latencies, 99) * 1e6, 2),
        "latency_stdev_us": (
            round(statistics.stdev(latencies) * 1e6, 2) if len(latencies) > 1 else 0
        ),
    }


# ── Benchmarks ──────────────────────────────────────────────────────────


def bench_keygen() -> dict:
    """Benchmark Ed25519 key generation."""
    counter = [0]

    def op():
        Ed25519Provider.generate_keypair(f"bench_{counter[0]}")
        counter[0] += 1

    return run_benchmark("ed25519_keygen", op)


def bench_sign(payload_size: int) -> dict:
    """Benchmark Ed25519 signing for a given payload size."""
    kp = Ed25519Provider.generate_keypair("bench_sign")
    data = os.urandom(payload_size)

    def op():
        Ed25519Provider.sign(kp.private_key, data)

    return run_benchmark(f"ed25519_sign_{payload_size}B", op)


def bench_verify(payload_size: int) -> dict:
    """Benchmark Ed25519 verification for a given payload size."""
    kp = Ed25519Provider.generate_keypair("bench_verify")
    data = os.urandom(payload_size)
    sig = Ed25519Provider.sign(kp.private_key, data)

    def op():
        Ed25519Provider.verify(kp.public_key, sig, data)

    return run_benchmark(f"ed25519_verify_{payload_size}B", op)


def bench_rfc3161_issue() -> dict:
    """Benchmark RFC 3161 timestamp issuance."""
    tsa = LocalTSA()
    counter = [0]

    def op():
        tsa.request_timestamp(f"{counter[0]:064x}")
        counter[0] += 1

    return run_benchmark("rfc3161_issue", op)


def bench_rfc3161_verify() -> dict:
    """Benchmark RFC 3161 token verification."""
    tsa = LocalTSA()
    resp = tsa.request_timestamp("a" * 64)
    token = resp.token
    assert token is not None

    def op():
        tsa.verify_timestamp(token)

    return run_benchmark("rfc3161_verify", op)


def bench_ledger_append() -> dict:
    """Benchmark ledger append (no signing/TSA)."""
    ledger = DurableLedger(block_size=10000)
    counter = [0]

    def op():
        ledger.append(
            ExecutionRecord(
                record_id=f"bench_rec_{counter[0]}",
                request_id=f"bench_req_{counter[0]}",
                actor="bench_agent",
                action="bench_action",
                resource="bench_resource",
                decision="allow",
            )
        )
        counter[0] += 1

    return run_benchmark("ledger_append", op)


def bench_ledger_seal() -> dict:
    """Benchmark ledger block sealing with Ed25519 signing + RFC 3161 timestamps."""
    ks = KeyStore()
    kp = Ed25519Provider.generate_keypair("ledger")
    ks.register(kp)
    tsa = LocalTSA()

    def op():
        ledger = DurableLedger(block_size=64, key_store=ks, tsa=tsa)
        for i in range(64):
            ledger.append(
                ExecutionRecord(
                    record_id=f"seal_{id(ledger)}_{i}",
                    request_id=f"req_{i}",
                    actor="agent",
                    action="action",
                    resource="res",
                    decision="allow",
                )
            )
        # Block should be auto-sealed at 64 records

    return run_benchmark("ledger_seal_64_records", op, iterations=100, warmup=5)


def bench_capability_issue() -> dict:
    """Benchmark capability token issuance with Ed25519 signing."""
    ca = CapabilityAuthority()
    scope = CapabilityScope(resource="bench_resource", actions=["read"])
    counter = [0]

    def op():
        ca.issue(subject=f"user_{counter[0]}", scopes=[scope])
        counter[0] += 1

    return run_benchmark("capability_issue", op)


def bench_full_pipeline() -> dict:
    """Benchmark full pipeline: keygen → sign → verify → timestamp."""
    tsa = LocalTSA()
    counter = [0]

    def op():
        kp = Ed25519Provider.generate_keypair(f"pipe_{counter[0]}")
        sig = Ed25519Provider.sign(kp.private_key, b"pipeline_data")
        Ed25519Provider.verify(kp.public_key, sig, b"pipeline_data")
        tsa.request_timestamp(sig[:64])
        counter[0] += 1

    return run_benchmark("full_pipeline", op, iterations=500, warmup=10)


# ── Main ────────────────────────────────────────────────────────────────


def main() -> None:
    """Run all benchmarks and print results."""
    print("=" * 80)
    print("PSIA Cryptographic Performance Benchmarks")
    print("=" * 80)

    hw = get_hardware_info()
    print(f"\nPlatform:       {hw['platform']}")
    print(f"Processor:      {hw['processor']}")
    print(f"CPU Cores:      {hw['cpu_count']}")
    print(f"Python:         {hw['python_version']}")
    print(f"Timestamp:      {hw['timestamp']}")
    print()

    results: list[dict] = []

    # Ed25519 key generation
    print("Running: Ed25519 Key Generation...")
    results.append(bench_keygen())

    # Ed25519 signing at various sizes
    for size in PAYLOAD_SIZES:
        print(f"Running: Ed25519 Sign ({size}B)...")
        results.append(bench_sign(size))

    # Ed25519 verification at various sizes
    for size in PAYLOAD_SIZES:
        print(f"Running: Ed25519 Verify ({size}B)...")
        results.append(bench_verify(size))

    # RFC 3161
    print("Running: RFC 3161 Issue...")
    results.append(bench_rfc3161_issue())
    print("Running: RFC 3161 Verify...")
    results.append(bench_rfc3161_verify())

    # Ledger
    print("Running: Ledger Append...")
    results.append(bench_ledger_append())
    print("Running: Ledger Seal (64 records with crypto)...")
    results.append(bench_ledger_seal())

    # Capability
    print("Running: Capability Token Issuance...")
    results.append(bench_capability_issue())

    # Full pipeline
    print("Running: Full Pipeline (keygen+sign+verify+timestamp)...")
    results.append(bench_full_pipeline())

    # Print results table
    print()
    print("=" * 80)
    print(
        f"{'Benchmark':<35} {'Ops/sec':>12} {'Mean μs':>12} {'P50 μs':>10} {'P95 μs':>10} {'P99 μs':>10}"
    )
    print("-" * 80)
    for r in results:
        print(
            f"{r['name']:<35} {r['ops_per_sec']:>12,.0f} "
            f"{r['latency_mean_us']:>12,.1f} "
            f"{r['latency_p50_us']:>10,.1f} "
            f"{r['latency_p95_us']:>10,.1f} "
            f"{r['latency_p99_us']:>10,.1f}"
        )
    print("=" * 80)
    print()

    # Write JSON report
    report = {
        "hardware": hw,
        "results": results,
    }
    report_path = os.path.join(os.path.dirname(__file__), "benchmark_report.json")
    import json

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
