"""
PSIA Benchmark Harness — Reproducible Performance Measurement.

Addresses the gap: "Empirical methodology not detailed."

This module provides a controlled, reproducible benchmarking framework
for the PSIA subsystems, generating statistically rigorous results
with hardware detection, workload specification, and confidence intervals.

Benchmarks:
    1. Waterfall pipeline throughput (requests/second)
    2. Shadow simulation latency (ms per evaluation)
    3. Quorum decision latency (ms per decision)
    4. Ledger append/seal latency (ms per block)
    5. OCC commit throughput under contention
    6. End-to-end request processing latency

Methodology:
    - Each benchmark runs N_warmup iterations (discarded) followed
      by N_measured iterations (recorded).
    - Hardware detection captures CPU model, core count, RAM, and OS.
    - Results include mean, median, p95, p99, std_dev, and 95%
      confidence intervals.
    - Workload parameters are explicitly recorded for reproducibility.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import platform
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HardwareProfile:
    """Detected hardware profile for reproducibility."""

    cpu_model: str
    cpu_count_logical: int
    cpu_count_physical: int
    ram_total_gb: float
    os_name: str
    os_version: str
    python_version: str
    timestamp: str

    @staticmethod
    def detect() -> HardwareProfile:
        """Auto-detect current hardware profile."""
        try:
            import multiprocessing

            physical = multiprocessing.cpu_count()
        except Exception:
            physical = os.cpu_count() or 1

        return HardwareProfile(
            cpu_model=platform.processor() or "unknown",
            cpu_count_logical=os.cpu_count() or 1,
            cpu_count_physical=physical,
            ram_total_gb=_get_ram_gb(),
            os_name=platform.system(),
            os_version=platform.version(),
            python_version=platform.python_version(),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


def _get_ram_gb() -> float:
    """Attempt to detect total RAM in GB."""
    try:
        if platform.system() == "Windows":
            import ctypes

            kernel32 = ctypes.windll.kernel32
            c_ulonglong = ctypes.c_ulonglong

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", c_ulonglong),
                    ("ullAvailPhys", c_ulonglong),
                    ("ullTotalPageFile", c_ulonglong),
                    ("ullAvailPageFile", c_ulonglong),
                    ("ullTotalVirtual", c_ulonglong),
                    ("ullAvailVirtual", c_ulonglong),
                    ("sullAvailExtendedVirtual", c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(stat)
            kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            return round(stat.ullTotalPhys / (1024**3), 2)
        else:
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        kb = int(line.split()[1])
                        return round(kb / (1024**2), 2)
    except Exception:
        pass
    return 0.0


@dataclass(frozen=True)
class WorkloadSpec:
    """Explicit workload specification for reproducibility."""

    name: str
    description: str
    iterations_warmup: int = 100
    iterations_measured: int = 1000
    concurrency_level: int = 1
    payload_size_bytes: int = 256
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "iterations_warmup": self.iterations_warmup,
            "iterations_measured": self.iterations_measured,
            "concurrency_level": self.concurrency_level,
            "payload_size_bytes": self.payload_size_bytes,
            "parameters": self.parameters,
        }


@dataclass
class BenchmarkResult:
    """Statistical result of a benchmark run."""

    benchmark_name: str
    workload: WorkloadSpec
    hardware: HardwareProfile
    iterations: int
    latencies_ms: list[float]

    @property
    def mean_ms(self) -> float:
        return statistics.mean(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def median_ms(self) -> float:
        return statistics.median(self.latencies_ms) if self.latencies_ms else 0.0

    @property
    def std_dev_ms(self) -> float:
        return (
            statistics.stdev(self.latencies_ms) if len(self.latencies_ms) > 1 else 0.0
        )

    @property
    def p95_ms(self) -> float:
        return self._percentile(95)

    @property
    def p99_ms(self) -> float:
        return self._percentile(99)

    @property
    def throughput_per_sec(self) -> float:
        if self.mean_ms <= 0:
            return 0.0
        return 1000.0 / self.mean_ms

    @property
    def ci_95(self) -> tuple[float, float]:
        """95% confidence interval for the mean."""
        if len(self.latencies_ms) < 2:
            return (self.mean_ms, self.mean_ms)
        se = self.std_dev_ms / math.sqrt(len(self.latencies_ms))
        z = 1.96  # 95% CI
        return (self.mean_ms - z * se, self.mean_ms + z * se)

    def _percentile(self, pct: float) -> float:
        if not self.latencies_ms:
            return 0.0
        sorted_l = sorted(self.latencies_ms)
        idx = int(len(sorted_l) * pct / 100)
        idx = min(idx, len(sorted_l) - 1)
        return sorted_l[idx]

    def to_dict(self) -> dict[str, Any]:
        ci = self.ci_95
        return {
            "benchmark": self.benchmark_name,
            "workload": self.workload.to_dict(),
            "iterations": self.iterations,
            "mean_ms": round(self.mean_ms, 4),
            "median_ms": round(self.median_ms, 4),
            "std_dev_ms": round(self.std_dev_ms, 4),
            "p95_ms": round(self.p95_ms, 4),
            "p99_ms": round(self.p99_ms, 4),
            "throughput_per_sec": round(self.throughput_per_sec, 2),
            "ci_95_lower": round(ci[0], 4),
            "ci_95_upper": round(ci[1], 4),
        }

    def summary(self) -> str:
        ci = self.ci_95
        return (
            f"{self.benchmark_name}: "
            f"mean={self.mean_ms:.3f}ms, "
            f"median={self.median_ms:.3f}ms, "
            f"p95={self.p95_ms:.3f}ms, "
            f"p99={self.p99_ms:.3f}ms, "
            f"stddev={self.std_dev_ms:.3f}ms, "
            f"95%CI=[{ci[0]:.3f}, {ci[1]:.3f}]ms, "
            f"throughput={self.throughput_per_sec:.1f}/s "
            f"(n={self.iterations})"
        )


class BenchmarkHarness:
    """Controlled benchmark execution with statistical reporting.

    Usage:
        harness = BenchmarkHarness()

        # Register benchmarks
        harness.register("waterfall_pipeline", workload, pipeline_fn)
        harness.register("quorum_decision", workload, quorum_fn)

        # Run all
        results = harness.run_all()

        # Export reproducible report
        report = harness.export_report(results)
    """

    def __init__(self) -> None:
        self._benchmarks: dict[str, tuple[WorkloadSpec, Callable[[], None]]] = {}
        self._hardware = HardwareProfile.detect()

    def register(
        self,
        name: str,
        workload: WorkloadSpec,
        fn: Callable[[], None],
    ) -> None:
        """Register a benchmark function.

        Args:
            name: Unique benchmark name
            workload: Workload specification
            fn: Function to benchmark (called with no args, should do one unit of work)
        """
        self._benchmarks[name] = (workload, fn)

    def run(self, name: str) -> BenchmarkResult:
        """Run a single benchmark.

        Args:
            name: Benchmark name to run

        Returns:
            BenchmarkResult with statistical analysis
        """
        if name not in self._benchmarks:
            raise KeyError(f"Unknown benchmark: {name}")

        workload, fn = self._benchmarks[name]

        logger.info(
            "Warming up %s (%d iterations)...", name, workload.iterations_warmup
        )
        for _ in range(workload.iterations_warmup):
            fn()

        logger.info(
            "Measuring %s (%d iterations)...", name, workload.iterations_measured
        )
        latencies: list[float] = []
        for _ in range(workload.iterations_measured):
            start = time.perf_counter()
            fn()
            elapsed_ms = (time.perf_counter() - start) * 1000
            latencies.append(elapsed_ms)

        result = BenchmarkResult(
            benchmark_name=name,
            workload=workload,
            hardware=self._hardware,
            iterations=workload.iterations_measured,
            latencies_ms=latencies,
        )

        logger.info("Result: %s", result.summary())
        return result

    def run_all(self) -> list[BenchmarkResult]:
        """Run all registered benchmarks."""
        results = []
        for name in self._benchmarks:
            results.append(self.run(name))
        return results

    def export_report(
        self,
        results: list[BenchmarkResult],
        output_path: str | None = None,
    ) -> dict[str, Any]:
        """Export a reproducible benchmark report.

        Args:
            results: List of benchmark results
            output_path: Optional file path to write JSON report

        Returns:
            Report dict with hardware, workload, and results
        """
        report = {
            "report_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "hardware": {
                "cpu_model": self._hardware.cpu_model,
                "cpu_count_logical": self._hardware.cpu_count_logical,
                "cpu_count_physical": self._hardware.cpu_count_physical,
                "ram_total_gb": self._hardware.ram_total_gb,
                "os": f"{self._hardware.os_name} {self._hardware.os_version}",
                "python": self._hardware.python_version,
            },
            "results": [r.to_dict() for r in results],
            "report_hash": "",
        }

        # Self-hash for integrity
        report_json = json.dumps(report, sort_keys=True, separators=(",", ":"))
        report["report_hash"] = hashlib.sha256(report_json.encode()).hexdigest()

        if output_path:
            with open(output_path, "w") as f:
                json.dump(report, f, indent=2, sort_keys=True)
            logger.info("Report written to %s", output_path)

        return report


# ──────────────────────────────────────────────────────────────────────
# Pre-defined Workloads
# ──────────────────────────────────────────────────────────────────────

WORKLOAD_WATERFALL = WorkloadSpec(
    name="waterfall_pipeline",
    description="Full 7-stage Waterfall pipeline processing a standard request",
    iterations_warmup=50,
    iterations_measured=500,
    concurrency_level=1,
    payload_size_bytes=256,
    parameters={"stages": 7, "shadow_activation_threshold": 0.05},
)

WORKLOAD_QUORUM = WorkloadSpec(
    name="quorum_decision",
    description="Cerberus triple-head quorum decision (3 votes → decision)",
    iterations_warmup=100,
    iterations_measured=1000,
    payload_size_bytes=128,
    parameters={"head_count": 3, "policy": "unanimous"},
)

WORKLOAD_SHADOW = WorkloadSpec(
    name="shadow_simulation",
    description="Deterministic shadow evaluation with sealed context",
    iterations_warmup=50,
    iterations_measured=500,
    payload_size_bytes=512,
    parameters={"context": "sealed", "determinism_verified": True},
)

WORKLOAD_LEDGER = WorkloadSpec(
    name="ledger_append",
    description="Append and seal a single audit block to the cryptographic ledger",
    iterations_warmup=50,
    iterations_measured=500,
    payload_size_bytes=1024,
    parameters={"hash_algorithm": "SHA-256", "signature_algorithm": "Ed25519"},
)

WORKLOAD_OCC = WorkloadSpec(
    name="occ_commit",
    description="Optimistic concurrency control commit with version validation",
    iterations_warmup=50,
    iterations_measured=500,
    concurrency_level=4,
    payload_size_bytes=256,
    parameters={"read_set_size": 5, "write_set_size": 2, "conflict_rate": 0.1},
)


__all__ = [
    "HardwareProfile",
    "WorkloadSpec",
    "BenchmarkResult",
    "BenchmarkHarness",
    "WORKLOAD_WATERFALL",
    "WORKLOAD_QUORUM",
    "WORKLOAD_SHADOW",
    "WORKLOAD_LEDGER",
    "WORKLOAD_OCC",
]
