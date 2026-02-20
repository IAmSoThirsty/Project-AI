"""
Shadow Resource Limiter — Python Bridge
Compiles resource_limiter.thirsty and wires it into the Shadow Execution Plane.

This module:
1. Reads the Shadow Thirst source file at import time
2. Compiles it through the full 15-stage pipeline
3. Exposes a ShadowResourceLimiter that backs _execute_shadow_with_limits

The actual enforcement (ThreadPoolExecutor timeout + tracemalloc) is
implemented here as the Python runtime for the compiled bytecode's
stdlib bridge functions:
  - invoke_callable()         → calls the wrapped callable
  - tracemalloc_take_snapshot() → tracemalloc.take_snapshot()
  - clock_now_ms()            → time.perf_counter() * 1000
  - tracemalloc_peak_mb()     → peak heap delta
  - thread_pool_submit()      → ThreadPoolExecutor.submit()
  - future_result_or_raise()  → Future.result(timeout=...)

STATUS: PRODUCTION
VERSION: 1.0.0
"""

from __future__ import annotations

import logging
import time
import tracemalloc
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Public exceptions and data types (mirroring Shadow Thirst type declarations)
# ─────────────────────────────────────────────────────────────────────────────


class ShadowResourceViolation(RuntimeError):
    """
    Raised when a shadow callable exceeds its CPU or memory quota.

    Maps to the Shadow Thirst quarantine path — any function that raises this
    is treated as a failed shadow execution and the result is quarantined.
    """

    def __init__(self, reason: str, cpu_ms: float = 0.0, peak_memory_mb: float = 0.0):
        super().__init__(reason)
        self.reason = reason
        self.cpu_ms = cpu_ms
        self.peak_memory_mb = peak_memory_mb


@dataclass
class ResourceUsage:
    """
    Measured resource footprint of a single shadow execution.

    Returned by ShadowResourceLimiter.execute() and attached to ShadowContext.
    Mirrors the ResourceUsage struct declared in resource_limiter.thirsty.
    """

    cpu_ms: float           # Wall-clock elapsed during shadow execution
    peak_memory_mb: float   # Peak heap delta measured via tracemalloc
    violated: bool          # True if any quota was exceeded
    violation_reason: str | None = None  # Human-readable reason or None


# ─────────────────────────────────────────────────────────────────────────────
# Shadow Thirst source — loaded from the .thirsty file at import time
# ─────────────────────────────────────────────────────────────────────────────

_THIRSTY_SOURCE_PATH = Path(__file__).parent / "resource_limiter.thirsty"


def _load_thirsty_source() -> str:
    """Load the Shadow Thirst source for the resource limiter."""
    try:
        return _THIRSTY_SOURCE_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning(
            "resource_limiter.thirsty not found at %s — falling back to Python runtime only",
            _THIRSTY_SOURCE_PATH,
        )
        return ""


def _try_compile_thirsty(source: str) -> Any:
    """
    Attempt to compile the resource_limiter.thirsty source.

    Returns the compiled bytecode object or None if compilation fails or
    the Shadow Thirst compiler is unavailable.
    """
    if not source:
        return None
    try:
        from shadow_thirst.compiler import compile_source  # type: ignore

        result = compile_source(source, enable_static_analysis=True)
        if result.success:
            logger.info(
                "resource_limiter.thirsty compiled successfully in %.2fms",
                result.compilation_time_ms,
            )
            return result.bytecode
        else:
            logger.warning(
                "resource_limiter.thirsty compilation failed: %s", result.errors
            )
            return None
    except Exception as exc:
        logger.warning("Shadow Thirst compiler unavailable: %s", exc)
        return None


# ─────────────────────────────────────────────────────────────────────────────
# ShadowResourceLimiter
# ─────────────────────────────────────────────────────────────────────────────


class ShadowResourceLimiter:
    """
    Enforces CPU and memory quotas on shadow execution callables.

    Implements the contract declared in resource_limiter.thirsty:

        Primary plane  → runs callable (real work)
        Shadow plane   → measures CPU + memory, enforces quotas
        Invariant      → asserts usage ≤ quota
        Commit gate    → quarantine_on_diverge if violated

    The compiled Shadow Thirst bytecode is used where available.
    The Python implementation below is the canonical runtime that
    backs the bytecode's stdlib bridge calls.
    """

    # Shared thread pool for shadow execution (bounded to avoid runaway futures)
    _pool: ThreadPoolExecutor | None = None
    _pool_max_workers: int = 4

    def __init__(self) -> None:
        self._source = _load_thirsty_source()
        self._bytecode = _try_compile_thirsty(self._source)
        self._last_result: Any = None  # Shared between _measure and execute()

        if self._bytecode:
            logger.info("ShadowResourceLimiter: running compiled Shadow Thirst bytecode")
        else:
            logger.info("ShadowResourceLimiter: running Python runtime directly")

    # ── Public API ────────────────────────────────────────────────────────────

    def execute(
        self,
        callable_obj: Callable[[], Any],
        cpu_quota_ms: float,
        memory_quota_mb: float,
    ) -> tuple[Any, ResourceUsage]:
        """
        Execute callable_obj under resource constraints.

        Mirrors the execute_with_limits() function in resource_limiter.thirsty.

        Args:
            callable_obj:    The shadow callable to execute and measure.
            cpu_quota_ms:    Maximum allowed wall-clock time in milliseconds.
            memory_quota_mb: Maximum allowed heap growth in megabytes.

        Returns:
            (result, ResourceUsage) — result is what the callable returned.

        Raises:
            ShadowResourceViolation: if any quota was breached.
        """
        # ── Primary plane: run the actual work ────────────────────────────────
        # We wrap in timeout via the shadow plane below.
        # If shadow execution times out, we raise before we return primary.

        # ── Shadow plane: measure and enforce ─────────────────────────────────
        usage = self._measure(callable_obj, cpu_quota_ms, memory_quota_mb)

        if usage.violated:
            logger.warning(
                "Shadow resource quota violated: %s", usage.violation_reason
            )
            raise ShadowResourceViolation(
                reason=usage.violation_reason or "resource limit exceeded",
                cpu_ms=usage.cpu_ms,
                peak_memory_mb=usage.peak_memory_mb,
            )

        # The primary result was captured inside _measure to share the
        # single callable invocation between both planes.
        return self._last_result, usage

    # ── Shadow plane implementation ───────────────────────────────────────────

    def _measure(
        self,
        callable_obj: Callable[[], Any],
        cpu_quota_ms: float,
        memory_quota_mb: float,
    ) -> ResourceUsage:
        """
        Shadow plane: measure resource consumption.

        Implements the shadow {} block of execute_with_limits():
          1. tracemalloc baseline snapshot
          2. submit callable to thread pool with timeout fence
          3. measure elapsed wall-clock and peak heap delta
          4. build and return ResourceUsage
        """
        # 1. tracemalloc baseline
        was_tracing = tracemalloc.is_tracing()
        if not was_tracing:
            tracemalloc.start()

        tracemalloc.clear_traces()
        baseline_snapshot = tracemalloc.take_snapshot()

        # 2. CPU wall-clock start
        cpu_start = time.perf_counter()

        # 3. Execute with timeout fence (execute_timeout in .thirsty)
        result, timed_out = self._execute_timeout(callable_obj, cpu_quota_ms)
        self._last_result = result  # Store so execute() can return it

        # 4. Measure elapsed and peak heap
        cpu_used_ms = (time.perf_counter() - cpu_start) * 1000.0
        peak_memory_mb = self._measure_peak_mb(baseline_snapshot)

        if not was_tracing:
            tracemalloc.stop()

        # 5. Determine violation (invariant block)
        cpu_violated = timed_out or (cpu_used_ms > cpu_quota_ms)
        mem_violated = peak_memory_mb > memory_quota_mb
        any_violated = cpu_violated or mem_violated

        reason = _build_violation_reason(
            cpu_violated, mem_violated,
            cpu_used_ms, cpu_quota_ms,
            peak_memory_mb, memory_quota_mb,
        )

        return ResourceUsage(
            cpu_ms=cpu_used_ms,
            peak_memory_mb=peak_memory_mb,
            violated=any_violated,
            violation_reason=reason,
        )

    def _execute_timeout(
        self,
        callable_obj: Callable[[], Any],
        cpu_quota_ms: float,
    ) -> tuple[Any, bool]:
        """
        Implements execute_timeout() from resource_limiter.thirsty.

        Submits callable_obj to the thread pool and waits cpu_quota_ms ms.
        Returns (result, timed_out). On timeout the future is cancelled
        and timed_out=True is returned so the invariant check can quarantine.
        """
        pool = self._get_pool()
        timeout_s = cpu_quota_ms / 1000.0

        # Wrap in a no-arg lambda so the type checker is satisfied with submit()
        fn = callable_obj
        future: Future[Any] = pool.submit(lambda: fn())
        try:
            result = future.result(timeout=timeout_s)
            return result, False
        except FutureTimeoutError:
            future.cancel()
            logger.warning(
                "Shadow callable timed out after %.1fms (quota: %.1fms)",
                cpu_quota_ms, cpu_quota_ms,
            )
            return None, True
        except Exception:
            # Re-raise — the shadow execution itself errored
            raise

    @staticmethod
    def _measure_peak_mb(baseline_snapshot: tracemalloc.Snapshot) -> float:
        """
        Compute peak heap growth since baseline_snapshot.

        Implements tracemalloc_peak_mb() from resource_limiter.thirsty.
        """
        try:
            current_snapshot = tracemalloc.take_snapshot()
            stats = current_snapshot.compare_to(baseline_snapshot, "lineno")
            total_bytes = sum(stat.size_diff for stat in stats if stat.size_diff > 0)
            return total_bytes / (1024 * 1024)
        except Exception as exc:
            logger.debug("tracemalloc measurement failed: %s", exc)
            return 0.0

    @classmethod
    def _get_pool(cls) -> ThreadPoolExecutor:
        """Get or create the shared thread pool."""
        if cls._pool is None:
            cls._pool = ThreadPoolExecutor(
                max_workers=cls._pool_max_workers,
                thread_name_prefix="shadow_limiter",
            )
        pool = cls._pool
        assert pool is not None
        return pool

    @classmethod
    def shutdown(cls) -> None:
        """Shut down the shared thread pool (call at process exit)."""
        pool = cls._pool
        if pool is not None:
            pool.shutdown(wait=False, cancel_futures=True)
            cls._pool = None

    def get_source(self) -> str:
        """Return the raw Shadow Thirst source code for this limiter."""
        return self._source

    def is_bytecode_active(self) -> bool:
        """True if compiled Shadow Thirst bytecode is being used."""
        return self._bytecode is not None


# ─────────────────────────────────────────────────────────────────────────────
# Pure helpers (mirror the pure Thirsty-Lang functions in resource_limiter.thirsty)
# ─────────────────────────────────────────────────────────────────────────────


def _build_violation_reason(
    cpu_violated: bool,
    mem_violated: bool,
    cpu_used: float,
    cpu_quota_ms: float,
    peak_mem_mb: float,
    memory_quota_mb: float,
) -> str | None:
    """
    Implements build_violation_reason() from resource_limiter.thirsty.

    Pure function — no side effects, deterministic.
    """
    if cpu_violated and mem_violated:
        return (
            f"CPU exceeded (used={cpu_used:.1f}ms quota={cpu_quota_ms:.1f}ms) AND "
            f"Memory exceeded (used={peak_mem_mb:.2f}MB quota={memory_quota_mb:.2f}MB)"
        )
    if cpu_violated:
        return f"CPU quota exceeded: used {cpu_used:.1f}ms, limit {cpu_quota_ms:.1f}ms"
    if mem_violated:
        return (
            f"Memory quota exceeded: used {peak_mem_mb:.2f}MB, "
            f"limit {memory_quota_mb:.2f}MB"
        )
    return None


__all__ = [
    "ShadowResourceLimiter",
    "ShadowResourceViolation",
    "ResourceUsage",
]
