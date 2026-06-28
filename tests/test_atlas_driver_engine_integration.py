"""Integration tests for atlas.driver_engine."""

from __future__ import annotations

from atlas import (
    SUBORDINATION_NOTICE,
    AuditTrail,
    DriverEngine,
    DriverType,
    compute_pca,
)


def _raw(offset: float = 0.0) -> dict[str, float]:
    return {
        driver.value: (driver.historical_range[0] + driver.historical_range[1]) / 2.0 + offset
        for driver in DriverType
    }


def test_driver_engine_explains_and_proves_driver_analysis() -> None:
    trail = AuditTrail()
    engine = DriverEngine(audit_trail=trail)
    states = tuple(
        engine.create_state(_raw(index * 0.005), timestamp=f"2026-06-28T00:0{index}:00Z")
        for index in range(4)
    )
    analysis = engine.analyze(states, target_metric="systemic_risk_index")

    assert analysis.subordination_notice == SUBORDINATION_NOTICE
    assert analysis.pca.subordination_notice == SUBORDINATION_NOTICE
    assert trail.verify_chain().is_valid
    event = trail.events[-1]
    assert event.action == "driver_analysis_completed"
    assert event.outcome == "ALLOW"
    assert ("analysis_sha256", analysis.analysis_sha256) in event.evidence
    assert ("states", "4") in event.evidence


def test_driver_analysis_hash_changes_when_state_changes() -> None:
    engine = DriverEngine()
    first_states = tuple(
        engine.create_state(_raw(index * 0.005), timestamp=f"2026-06-28T00:0{index}:00Z")
        for index in range(4)
    )
    second_states = tuple(
        engine.create_state(_raw(index * 0.010), timestamp=f"2026-06-28T01:0{index}:00Z")
        for index in range(4)
    )
    assert (
        engine.analyze(first_states).analysis_sha256
        != engine.analyze(second_states).analysis_sha256
    )


def test_pca_is_order_independent_at_integration_boundary() -> None:
    engine = DriverEngine()
    states = tuple(
        engine.create_state(_raw(index * 0.005), timestamp=f"2026-06-28T00:0{index}:00Z")
        for index in range(4)
    )
    assert compute_pca(states, components=2) == compute_pca(reversed(states), components=2)


def test_state_hash_binds_subordination_notice() -> None:
    state = DriverEngine().create_state(_raw(), timestamp="2026-06-28T00:00:00Z")
    body = state.to_canonical_dict()
    assert body["subordination_notice"] == SUBORDINATION_NOTICE
    assert body["state_sha256"] == state.state_sha256
