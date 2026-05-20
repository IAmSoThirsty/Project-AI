"""
Observability: distributed tracing, performance profiling, and SLA tracking.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass


class DistributedTracer:
    def __init__(self, service_name: str) -> None:
        self.service_name = service_name

    @contextmanager
    def start_span(self, operation_name: str, **kwargs):
        yield None


class PerformanceProfiler:
    def __init__(self) -> None:
        self._stats: dict[str, list[float]] = {}

    @contextmanager
    def measure(self, operation: str):
        start = time.perf_counter()
        yield
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        self._stats.setdefault(operation, []).append(elapsed_ms)

    def get_statistics(self, operation: str) -> dict:
        durations = self._stats.get(operation, [])
        if not durations:
            return {"count": 0, "min": 0.0, "max": 0.0, "mean": 0.0}
        return {
            "count": len(durations),
            "min": min(durations),
            "max": max(durations),
            "mean": sum(durations) / len(durations),
        }


@dataclass
class SLAConfig:
    name: str
    target_latency_ms: float
    error_rate_threshold: float


class SLATracker:
    def __init__(self) -> None:
        self._configs: dict[str, SLAConfig] = {}
        self._records: dict[str, list[dict]] = {}

    def register_sla(self, config: SLAConfig) -> None:
        self._configs[config.name] = config
        self._records.setdefault(config.name, [])

    def record_request(self, name: str, latency_ms: float, success: bool) -> None:
        self._records.setdefault(name, []).append(
            {"latency_ms": latency_ms, "success": success}
        )

    def check_sla(self, name: str) -> tuple[bool, dict]:
        records = self._records.get(name, [])
        config = self._configs.get(name)
        count = len(records)
        error_count = sum(1 for r in records if not r["success"])
        avg_latency = sum(r["latency_ms"] for r in records) / count if count else 0.0
        error_rate = error_count / count if count else 0.0

        meets_sla = True
        if config:
            if avg_latency > config.target_latency_ms:
                meets_sla = False
            if error_rate > config.error_rate_threshold:
                meets_sla = False

        return meets_sla, {
            "request_count": count,
            "error_count": error_count,
            "avg_latency_ms": avg_latency,
            "error_rate": error_rate,
        }
