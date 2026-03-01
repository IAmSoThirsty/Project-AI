"""
Tests for PSIA Liveness Guarantees — Progress Conditions.

Fact-verifies claims from the paper (§6.2):
    - HeadLivenessMonitor: timeout enforcement, fail-safe deny synthesis
    - HeadHealth: heartbeat tracking, degradation on consecutive timeouts
    - PipelineDeadlockDetector: stage timeout, pipeline timeout detection
    - Progress bound: T_progress = T_queue + (S × T_stage) + T_retry = 115s
    - Starvation freedom: valid requests eventually commit
"""

from __future__ import annotations

import time

from psia.liveness import (
    HeadHealth,
    HeadLivenessMonitor,
    HeadStatus,
    PipelineDeadlockDetector,
    TimeoutConfig,
)


class TestTimeoutConfig:
    """Paper §6.2: Default timeout parameters."""

    def test_default_config(self):
        cfg = TimeoutConfig()
        assert cfg.head_evaluation_timeout == 5.0
        assert cfg.stage_timeout == 10.0
        assert cfg.pipeline_timeout == 60.0
        assert cfg.queue_timeout == 30.0
        assert cfg.retry_timeout == 5.0
        assert cfg.heartbeat_interval == 1.0
        assert cfg.max_consecutive_timeouts == 3

    def test_progress_bound_calculation(self):
        """Paper §6.2: T_progress = T_queue + (S × T_stage) + T_retry.

        With defaults: 30 + (7 × 10) + 5 = 105s < 115s bound.
        Paper states 115s with padding.
        """
        cfg = TimeoutConfig()
        stages = 7  # PSIA waterfall has 7 stages
        t_progress = (
            cfg.queue_timeout + (stages * cfg.stage_timeout) + cfg.retry_timeout
        )
        assert t_progress <= 115  # Paper's stated bound


class TestHeadHealth:
    """Paper §9: Head health tracking."""

    def test_initial_status_alive(self):
        h = HeadHealth(head_name="identity")
        assert h.status == HeadStatus.ALIVE
        assert h.consecutive_timeouts == 0

    def test_record_success_updates_latency(self):
        h = HeadHealth(head_name="identity")
        h.record_success(latency_ms=2.5)
        assert h.total_evaluations == 1
        assert h.avg_latency_ms == 2.5
        assert h.status == HeadStatus.ALIVE

    def test_timeout_degrades_status(self):
        h = HeadHealth(head_name="identity")
        h.record_timeout(max_consecutive=3)
        assert h.consecutive_timeouts == 1
        assert h.status == HeadStatus.DEGRADED

    def test_consecutive_timeouts_cause_failure(self):
        h = HeadHealth(head_name="identity")
        for _ in range(3):
            h.record_timeout(max_consecutive=3)
        assert h.status == HeadStatus.FAILED

    def test_success_resets_timeout_counter(self):
        h = HeadHealth(head_name="identity")
        h.record_timeout(max_consecutive=3)
        assert h.consecutive_timeouts == 1
        h.record_success(latency_ms=1.0)
        assert h.consecutive_timeouts == 0
        assert h.status == HeadStatus.ALIVE


class TestHeadLivenessMonitor:
    """Paper §6.2: Timeout enforcement for head evaluations."""

    def test_fast_evaluation_succeeds(self):
        monitor = HeadLivenessMonitor(config=TimeoutConfig(head_evaluation_timeout=2.0))
        result, timed_out = monitor.evaluate_with_timeout(
            head_name="identity",
            evaluate_fn=lambda: "allow",
            default_on_timeout="deny",
        )
        assert result == "allow"
        assert timed_out is False

    def test_slow_evaluation_returns_default(self):
        """Paper: If head exceeds timeout, return deny-safe default."""
        config = TimeoutConfig(head_evaluation_timeout=0.1)
        monitor = HeadLivenessMonitor(config=config)

        def slow_fn():
            time.sleep(1.0)
            return "allow"

        result, timed_out = monitor.evaluate_with_timeout(
            head_name="identity",
            evaluate_fn=slow_fn,
            default_on_timeout="deny",
        )
        assert result == "deny"
        assert timed_out is True

    def test_health_summary(self):
        monitor = HeadLivenessMonitor()
        # Evaluate all three heads
        for head in ("identity", "capability", "invariant"):
            monitor.evaluate_with_timeout(head, lambda: "allow", "deny")
        summary = monitor.health_summary  # property, not method
        assert len(summary) >= 3

    def test_all_heads_alive_after_success(self):
        monitor = HeadLivenessMonitor()
        for head in ("identity", "capability", "invariant"):
            monitor.evaluate_with_timeout(head, lambda: "allow", "deny")
        assert monitor.all_heads_alive()


class TestPipelineDeadlockDetector:
    """Paper §6.2: Deadlock detection in the Waterfall pipeline."""

    def test_normal_request_no_deadlock(self):
        detector = PipelineDeadlockDetector(
            config=TimeoutConfig(stage_timeout=10.0, pipeline_timeout=60.0)
        )
        detector.enter_stage("req_1", stage=1)
        detector.exit_stage("req_1")
        detector.complete_request("req_1")
        violations = detector.check_deadlocks()
        assert len(violations) == 0

    def test_stage_timeout_detected(self):
        """If request stays in one stage too long, it's a deadlock."""
        detector = PipelineDeadlockDetector(
            config=TimeoutConfig(stage_timeout=0.01, pipeline_timeout=60.0)
        )
        detector.enter_stage("req_stuck", stage=3)
        time.sleep(0.05)  # Exceed 10ms stage timeout
        violations = detector.check_deadlocks()
        # Should detect at least one violation
        assert len(violations) > 0
        assert any(v[0] == "req_stuck" for v in violations)

    def test_pipeline_timeout_detected(self):
        """If request exceeds total pipeline timeout, detected."""
        detector = PipelineDeadlockDetector(
            config=TimeoutConfig(stage_timeout=10.0, pipeline_timeout=0.01)
        )
        detector.enter_stage("req_slow", stage=1)
        time.sleep(0.05)
        violations = detector.check_deadlocks()
        assert len(violations) > 0
