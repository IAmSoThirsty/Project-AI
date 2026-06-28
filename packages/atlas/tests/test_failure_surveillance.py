"""Tests for canonical Atlas failure surveillance (Phase J2.6)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from atlas import (
    SUBORDINATION_NOTICE,
    Anomaly,
    AnomalyType,
    AuditLevel,
    AuditTrail,
    FailureSurveillanceError,
    FailureSurveillanceSystem,
    SeverityLevel,
    SurveillanceThresholds,
    SystemHealth,
    get_failure_surveillance,
    reset_failure_surveillance,
)


def fixed_clock() -> datetime:
    return datetime(2026, 6, 28, 12, 0, 0, tzinfo=UTC)


def test_thresholds_validate_unit_interval() -> None:
    with pytest.raises(FailureSurveillanceError, match="drift_threshold"):
        SurveillanceThresholds(drift_threshold=-0.1)


def test_anomaly_validates_identity_and_subordination() -> None:
    with pytest.raises(FailureSurveillanceError, match="anomaly_id"):
        Anomaly(
            anomaly_id="",
            anomaly_type=AnomalyType.DRIFT_DETECTION,
            severity=SeverityLevel.MEDIUM,
            timestamp="2026-06-28T12:00:00+00:00",
            description="x",
        )
    anomaly = Anomaly(
        anomaly_id="a1",
        anomaly_type=AnomalyType.DRIVER_VOLATILITY,
        severity=SeverityLevel.HIGH,
        timestamp="2026-06-28T12:00:00+00:00",
        description="driver moved",
    )
    assert anomaly.subordination_notice == SUBORDINATION_NOTICE


def test_health_scores_and_attention_thresholds() -> None:
    health = SystemHealth(
        timestamp="2026-06-28T12:00:00+00:00",
        is_healthy=False,
        drift_score=0.5,
        volatility_score=0.75,
        integrity_score=1.0,
        performance_score=0.25,
        anomalies_high=4,
    )
    assert health.overall_score() == 0.625
    assert health.needs_attention() is True


def test_detect_drift_records_anomaly_and_audit_event() -> None:
    trail = AuditTrail(clock=fixed_clock)
    system = FailureSurveillanceSystem(audit_trail=trail, clock=fixed_clock)

    anomaly = system.detect_drift(1.25, 1.0, "posterior")

    assert anomaly is not None
    assert anomaly.anomaly_type is AnomalyType.DRIFT_DETECTION
    assert anomaly.severity is SeverityLevel.MEDIUM
    assert anomaly.value == pytest.approx(0.25)
    assert anomaly.threshold == 0.1
    assert len(system.anomalies) == 1
    assert trail.events[-1].action == "failure_anomaly_detected"
    assert dict(trail.events[-1].evidence)["anomaly_type"] == "drift_detection"


def test_drift_under_threshold_returns_none() -> None:
    system = FailureSurveillanceSystem(clock=fixed_clock)
    assert system.detect_drift(1.05, 1.0, "posterior") is None
    assert system.anomalies == ()


def test_detect_driver_volatility_uses_population_stdev() -> None:
    system = FailureSurveillanceSystem(clock=fixed_clock)

    anomaly = system.detect_driver_volatility((0.0, 1.0), "trust")

    assert anomaly is not None
    assert anomaly.anomaly_type is AnomalyType.DRIVER_VOLATILITY
    assert anomaly.severity is SeverityLevel.HIGH
    assert anomaly.value == pytest.approx(0.5)


def test_driver_volatility_requires_two_values() -> None:
    system = FailureSurveillanceSystem(clock=fixed_clock)
    assert system.detect_driver_volatility((0.4,), "trust") is None


def test_detect_edge_inflation_is_critical() -> None:
    system = FailureSurveillanceSystem(clock=fixed_clock)

    anomaly = system.detect_edge_inflation(120, 10)

    assert anomaly is not None
    assert anomaly.anomaly_type is AnomalyType.EDGE_INFLATION
    assert anomaly.severity is SeverityLevel.CRITICAL
    assert anomaly.action_taken == "ABORT_REQUIRED"


def test_edge_inflation_rejects_zero_baseline() -> None:
    system = FailureSurveillanceSystem(clock=fixed_clock)
    with pytest.raises(FailureSurveillanceError, match="baseline_edge_count"):
        system.detect_edge_inflation(1, 0)


def test_detect_claim_posterior_explosion() -> None:
    system = FailureSurveillanceSystem(clock=fixed_clock)

    anomaly = system.detect_claim_posterior_explosion((0.995, 0.994, 0.2))

    assert anomaly is not None
    assert anomaly.anomaly_type is AnomalyType.CLAIM_POSTERIOR_EXPLOSION
    assert anomaly.value == pytest.approx(2 / 3)


def test_claim_posterior_rejects_out_of_range_values() -> None:
    system = FailureSurveillanceSystem(clock=fixed_clock)
    with pytest.raises(FailureSurveillanceError, match="posterior"):
        system.detect_claim_posterior_explosion((1.2,))


def test_detect_narrative_bleed_is_critical_abort() -> None:
    system = FailureSurveillanceSystem(clock=fixed_clock)

    anomaly = system.detect_narrative_bleed(("mythic sludge",), "RS contains Mythic Sludge")

    assert anomaly is not None
    assert anomaly.anomaly_type is AnomalyType.NARRATIVE_BLEED
    assert anomaly.severity is SeverityLevel.CRITICAL
    assert anomaly.action_taken == "ABORT_REQUIRED"


def test_detect_sensitivity_blowup() -> None:
    system = FailureSurveillanceSystem(clock=fixed_clock)

    anomaly = system.detect_sensitivity_blowup(-12.0, "inflation")

    assert anomaly is not None
    assert anomaly.anomaly_type is AnomalyType.SENSITIVITY_BLOWUP
    assert anomaly.severity is SeverityLevel.HIGH


def test_detect_parameter_bounds_violation() -> None:
    system = FailureSurveillanceSystem(clock=fixed_clock)

    anomaly = system.detect_parameter_bounds_violation("trust", 1.1, 0.0, 1.0)

    assert anomaly is not None
    assert anomaly.anomaly_type is AnomalyType.PARAMETER_BOUNDS_VIOLATION
    assert anomaly.severity is SeverityLevel.CRITICAL


def test_hash_integrity_failure_only_records_on_mismatch() -> None:
    system = FailureSurveillanceSystem(clock=fixed_clock)

    assert system.detect_hash_integrity_failure("a" * 64, "a" * 64, "graph") is None
    anomaly = system.detect_hash_integrity_failure("a" * 64, "b" * 64, "graph")

    assert anomaly is not None
    assert anomaly.anomaly_type is AnomalyType.HASH_INTEGRITY_FAILURE
    assert anomaly.severity is SeverityLevel.CRITICAL


def test_compute_health_counts_anomalies_by_severity() -> None:
    system = FailureSurveillanceSystem(clock=fixed_clock)
    system.detect_drift(1.2, 1.0, "posterior")
    system.detect_sensitivity_blowup(11.0, "inflation")
    system.detect_narrative_bleed(("sludge",), "RS sludge")

    health = system.compute_health()

    assert health.anomalies_medium == 1
    assert health.anomalies_high == 1
    assert health.anomalies_critical == 1
    assert health.is_healthy is False
    assert system.health_history[-1] == health


def test_check_abort_conditions_emits_audit() -> None:
    trail = AuditTrail(clock=fixed_clock)
    system = FailureSurveillanceSystem(audit_trail=trail, clock=fixed_clock)
    system.detect_narrative_bleed(("sludge",), "RS sludge")

    should_abort, reasons = system.check_abort_conditions()

    assert should_abort is True
    assert any("Critical anomalies" in reason for reason in reasons)
    assert trail.events[-1].action == "failure_abort_conditions_met"
    assert trail.events[-1].level is AuditLevel.CRITICAL


def test_kill_switch_is_local_state_and_audit_visible() -> None:
    trail = AuditTrail(clock=fixed_clock)
    system = FailureSurveillanceSystem(audit_trail=trail, clock=fixed_clock)

    system.activate_kill_switch("operator ordered halt")

    assert system.kill_switch_activated is True
    assert system.is_active is False
    assert trail.events[-1].action == "failure_kill_switch_activated"


def test_reset_refuses_after_kill_switch() -> None:
    system = FailureSurveillanceSystem(clock=fixed_clock)
    system.activate_kill_switch("halt")

    with pytest.raises(FailureSurveillanceError, match="kill switch"):
        system.reset()


def test_statistics_are_serializable_summary() -> None:
    system = FailureSurveillanceSystem(clock=fixed_clock)
    system.detect_sensitivity_blowup(11.0, "inflation")

    stats = system.get_statistics()

    assert stats["total_anomalies"] == 1
    assert stats["by_severity"] == {"low": 0, "medium": 0, "high": 1, "critical": 0}
    health = stats["health"]
    assert isinstance(health, dict)
    assert health["needs_attention"] is False


def test_singleton_reset_creates_fresh_instance() -> None:
    reset_failure_surveillance()
    first = get_failure_surveillance(clock=fixed_clock)
    second = get_failure_surveillance(clock=fixed_clock)
    assert first is second

    reset_failure_surveillance()
    third = get_failure_surveillance(clock=fixed_clock)
    assert third is not first
