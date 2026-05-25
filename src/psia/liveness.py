"""PSIA liveness guarantees — timeouts, head health, deadlock detection (paper §6.2)."""
from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


@dataclass
class TimeoutConfig:
    head_evaluation_timeout: float = 5.0
    stage_timeout: float = 10.0
    pipeline_timeout: float = 60.0
    queue_timeout: float = 30.0
    retry_timeout: float = 5.0
    heartbeat_interval: float = 1.0
    max_consecutive_timeouts: int = 3


class HeadStatus(str, Enum):
    ALIVE = "alive"
    DEGRADED = "degraded"
    FAILED = "failed"


class HeadHealth:
    def __init__(self, head_name: str) -> None:
        self.head_name = head_name
        self.status = HeadStatus.ALIVE
        self.consecutive_timeouts = 0
        self.total_evaluations = 0
        self._total_latency_ms = 0.0

    @property
    def avg_latency_ms(self) -> float:
        if self.total_evaluations == 0:
            return 0.0
        return self._total_latency_ms / self.total_evaluations

    def record_success(self, latency_ms: float) -> None:
        self.consecutive_timeouts = 0
        self.total_evaluations += 1
        self._total_latency_ms += latency_ms
        self.status = HeadStatus.ALIVE

    def record_timeout(self, max_consecutive: int) -> None:
        self.consecutive_timeouts += 1
        if self.consecutive_timeouts >= max_consecutive:
            self.status = HeadStatus.FAILED
        else:
            self.status = HeadStatus.DEGRADED


class HeadLivenessMonitor:
    def __init__(self, config: TimeoutConfig | None = None) -> None:
        self._config = config or TimeoutConfig()
        self._health: dict[str, HeadHealth] = {}

    @property
    def health_summary(self) -> dict[str, HeadStatus]:
        return {name: h.status for name, h in self._health.items()}

    def all_heads_alive(self) -> bool:
        return all(h.status == HeadStatus.ALIVE for h in self._health.values())

    def evaluate_with_timeout(
        self,
        head_name: str,
        evaluate_fn: Callable[[], Any],
        default_on_timeout: Any,
    ) -> tuple[Any, bool]:
        if head_name not in self._health:
            self._health[head_name] = HeadHealth(head_name)

        result_queue: queue.Queue = queue.Queue()

        def _run() -> None:
            try:
                result_queue.put(("ok", evaluate_fn()))
            except Exception as e:
                result_queue.put(("err", e))

        t_start = time.monotonic()
        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        thread.join(timeout=self._config.head_evaluation_timeout)

        latency_ms = (time.monotonic() - t_start) * 1000

        if thread.is_alive():
            self._health[head_name].record_timeout(self._config.max_consecutive_timeouts)
            return default_on_timeout, True

        try:
            kind, value = result_queue.get_nowait()
        except queue.Empty:
            self._health[head_name].record_timeout(self._config.max_consecutive_timeouts)
            return default_on_timeout, True

        self._health[head_name].record_success(latency_ms)
        if kind == "err":
            return default_on_timeout, False
        return value, False


@dataclass
class _ActiveRequest:
    request_id: str
    stage: int
    stage_entered_at: float
    pipeline_started_at: float


class PipelineDeadlockDetector:
    def __init__(self, config: TimeoutConfig | None = None) -> None:
        self._config = config or TimeoutConfig()
        self._active: dict[str, _ActiveRequest] = {}
        self._lock = threading.Lock()

    def enter_stage(self, request_id: str, stage: int) -> None:
        now = time.monotonic()
        with self._lock:
            if request_id in self._active:
                # Update stage entry time
                self._active[request_id].stage = stage
                self._active[request_id].stage_entered_at = now
            else:
                self._active[request_id] = _ActiveRequest(
                    request_id=request_id,
                    stage=stage,
                    stage_entered_at=now,
                    pipeline_started_at=now,
                )

    def exit_stage(self, request_id: str) -> None:
        with self._lock:
            if request_id in self._active:
                self._active[request_id].stage_entered_at = time.monotonic()

    def complete_request(self, request_id: str) -> None:
        with self._lock:
            self._active.pop(request_id, None)

    def check_deadlocks(self) -> list[tuple]:
        now = time.monotonic()
        violations = []
        with self._lock:
            for req_id, req in list(self._active.items()):
                stage_elapsed = now - req.stage_entered_at
                pipeline_elapsed = now - req.pipeline_started_at
                if stage_elapsed > self._config.stage_timeout:
                    violations.append((req_id, "stage_timeout", req.stage, stage_elapsed))
                elif pipeline_elapsed > self._config.pipeline_timeout:
                    violations.append((req_id, "pipeline_timeout", pipeline_elapsed))
        return violations
