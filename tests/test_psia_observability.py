"""
Comprehensive test suite for PSIA Phase 6: Observability.

Covers:
    - FailureDetector: per-component tracking, circuit breaker transitions,
      cascade detection, z-score anomaly detection
    - AutoimmuneDampener: sensitivity adjustment, false positive tracking,
      dampened scoring, rule reset
"""

from __future__ import annotations

import pytest

from psia.observability.failure_detector import (
    FailureDetector,
    CircuitState,
)
from psia.observability.autoimmune_dampener import (
    AutoimmuneDampener,
)


# ═══════════════════════════════════════════════════════════════════
#  FailureDetector Tests
# ═══════════════════════════════════════════════════════════════════

class TestFailureDetector:

    def test_initial_state(self):
        fd = FailureDetector()
        fd.register_component("svc-a")
        health = fd.get_health("svc-a")
        assert health.circuit_state == CircuitState.CLOSED
        assert health.failure_rate == 0.0
        assert health.total_requests == 0

    def test_record_success(self):
        fd = FailureDetector()
        fd.record_success("svc-a")
        health = fd.get_health("svc-a")
        assert health.total_requests == 1
        assert health.total_failures == 0

    def test_record_failure(self):
        fd = FailureDetector()
        fd.record_failure("svc-a", error_type="timeout", message="conn timeout")
        health = fd.get_health("svc-a")
        assert health.total_failures == 1
        assert health.last_failure is not None
        assert health.last_failure.error_type == "timeout"

    def test_failure_rate(self):
        fd = FailureDetector()
        fd.record_success("svc-a")
        fd.record_failure("svc-a")
        health = fd.get_health("svc-a")
        assert health.failure_rate == pytest.approx(0.5)

    def test_circuit_trips_on_threshold(self):
        fd = FailureDetector(failure_threshold=0.5)
        # 3 failures, 0 successes → rate = 1.0 → trips
        for _ in range(3):
            fd.record_failure("svc-a")
        assert fd.check_circuit("svc-a") == CircuitState.OPEN

    def test_circuit_stays_closed_below_threshold(self):
        fd = FailureDetector(failure_threshold=0.5)
        fd.record_success("svc-a")
        fd.record_success("svc-a")
        fd.record_failure("svc-a")  # rate = 0.33 < 0.5
        assert fd.check_circuit("svc-a") == CircuitState.CLOSED

    def test_circuit_half_open_after_timeout(self):
        fd = FailureDetector(failure_threshold=0.5, recovery_timeout=0.0)
        for _ in range(3):
            fd.record_failure("svc-a")
        # Recovery timeout = 0, so immediately transitions to HALF_OPEN
        assert fd.check_circuit("svc-a") == CircuitState.HALF_OPEN

    def test_circuit_closes_on_success_in_half_open(self):
        fd = FailureDetector(failure_threshold=0.5, recovery_timeout=0.0)
        for _ in range(3):
            fd.record_failure("svc-a")
        fd.check_circuit("svc-a")  # Transition to HALF_OPEN
        fd.record_success("svc-a")  # Should close
        assert fd.check_circuit("svc-a") == CircuitState.CLOSED

    def test_auto_register(self):
        fd = FailureDetector()
        fd.record_success("auto-comp")
        health = fd.get_health("auto-comp")
        assert health.component == "auto-comp"

    def test_cascade_detection(self):
        cascades = []
        fd = FailureDetector(
            failure_threshold=0.5,
            cascade_threshold=2,
            on_cascade=lambda a: cascades.append(a),
        )
        # Trip two circuits
        for _ in range(3):
            fd.record_failure("svc-a")
        for _ in range(3):
            fd.record_failure("svc-b")
        assert len(cascades) == 1
        assert "svc-a" in cascades[0].affected_components
        assert "svc-b" in cascades[0].affected_components

    def test_open_circuit_count(self):
        fd = FailureDetector(failure_threshold=0.5)
        for _ in range(3):
            fd.record_failure("svc-a")
        assert fd.open_circuit_count() == 1
        for _ in range(3):
            fd.record_failure("svc-b")
        assert fd.open_circuit_count() == 2

    def test_state_transitions_recorded(self):
        fd = FailureDetector(failure_threshold=0.5)
        for _ in range(3):
            fd.record_failure("svc-a")
        transitions = fd.state_transitions
        assert len(transitions) >= 1
        assert transitions[0][0] == "svc-a"
        assert transitions[0][2] == CircuitState.OPEN

    def test_get_all_health(self):
        fd = FailureDetector()
        fd.record_success("svc-a")
        fd.record_success("svc-b")
        all_h = fd.get_all_health()
        assert "svc-a" in all_h
        assert "svc-b" in all_h


# ═══════════════════════════════════════════════════════════════════
#  AutoimmuneDampener Tests
# ═══════════════════════════════════════════════════════════════════

class TestAutoimmuneDampener:

    def test_initial_sensitivity(self):
        ad = AutoimmuneDampener()
        assert ad.get_sensitivity("rule_1") == 1.0  # max_sensitivity default

    def test_record_decision(self):
        ad = AutoimmuneDampener()
        ad.record_decision("rule_1", denied=True)
        stats = ad.get_stats("rule_1")
        assert stats.total_decisions == 1

    def test_record_false_positive(self):
        ad = AutoimmuneDampener()
        ad.record_decision("rule_1")
        ad.record_false_positive("rule_1")
        stats = ad.get_stats("rule_1")
        assert stats.false_positives == 1

    def test_sensitivity_decreases_on_high_fp(self):
        ad = AutoimmuneDampener(
            target_fp_rate=0.05,
            cooldown_decisions=5,
            adjustment_step=0.1,
        )
        # Interleave decisions and false positives so FP rate is high
        # when cooldown triggers (every 5 events)
        for _ in range(3):
            ad.record_decision("rule_1")
            ad.record_false_positive("rule_1")
        # Now total=3, fp=3, decisions_since_adjust=6 → adjusted once
        # FP rate = 3/3 = 1.0 >> target 0.05, so sensitivity decreases
        stats = ad.get_stats("rule_1")
        assert stats.current_sensitivity < 1.0

    def test_sensitivity_bounded_by_minimum(self):
        ad = AutoimmuneDampener(
            target_fp_rate=0.05,
            min_sensitivity=0.5,
            cooldown_decisions=1,
            adjustment_step=0.9,  # Large step
        )
        # All false positives
        for _ in range(20):
            ad.record_decision("rule_1")
            ad.record_false_positive("rule_1")
        assert ad.get_sensitivity("rule_1") >= 0.5

    def test_should_apply_rule(self):
        ad = AutoimmuneDampener()
        assert ad.should_apply_rule("rule_1", 0.8) is True
        assert ad.should_apply_rule("rule_1", 0.3) is False

    def test_disabled_returns_max_sensitivity(self):
        ad = AutoimmuneDampener(enabled=False)
        assert ad.get_sensitivity("rule_1") == 1.0

    def test_tracked_rules(self):
        ad = AutoimmuneDampener()
        ad.record_decision("r1")
        ad.record_decision("r2")
        assert set(ad.tracked_rules) == {"r1", "r2"}

    def test_reset_rule(self):
        ad = AutoimmuneDampener()
        ad.record_decision("r1")
        ad.reset_rule("r1")
        assert "r1" not in ad.tracked_rules

    def test_get_all_stats(self):
        ad = AutoimmuneDampener()
        ad.record_decision("r1")
        ad.record_decision("r2")
        all_stats = ad.get_all_stats()
        assert len(all_stats) == 2

    def test_adjustment_callback(self):
        adjustments = []
        ad = AutoimmuneDampener(
            cooldown_decisions=3,
            adjustment_step=0.1,
            on_adjustment=lambda a: adjustments.append(a),
        )
        # Generate high FP rate to trigger adjustment
        for _ in range(5):
            ad.record_decision("r1")
        for _ in range(5):
            ad.record_false_positive("r1")
        assert len(adjustments) >= 1

    def test_non_denied_decision_ignored(self):
        ad = AutoimmuneDampener()
        ad.record_decision("r1", denied=False)
        assert "r1" not in ad.tracked_rules

    def test_fp_rate_computation(self):
        ad = AutoimmuneDampener()
        for _ in range(10):
            ad.record_decision("r1")
        for _ in range(2):
            ad.record_false_positive("r1")
        stats = ad.get_stats("r1")
        assert stats.false_positive_rate == pytest.approx(0.2)  # 2/10
