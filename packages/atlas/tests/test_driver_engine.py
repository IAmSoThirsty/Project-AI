"""Unit tests for atlas.driver_engine (Phase J2.4.0b)."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from threading import Thread

import pytest

from atlas import (
    SUBORDINATION_NOTICE,
    AuditCategory,
    AuditLevel,
    AuditTrail,
    DriverAnalysis,
    DriverDimension,
    DriverEngine,
    DriverEngineError,
    DriverState,
    DriverType,
    compute_correlation_matrix,
    compute_driver_sensitivities,
    compute_pca,
    get_driver_engine,
    reset_driver_engine,
)


def _raw_values() -> dict[str, float]:
    return {
        "capital_concentration": 0.685,
        "market_volatility": 0.45,
        "resource_scarcity": 0.425,
        "media_gatekeeping": 0.54,
        "institutional_capture_risk": 0.475,
        "governance_fragility": 0.50,
        "inequality_index": 0.475,
        "social_cohesion": 0.50,
        "information_asymmetry": 0.51,
        "technological_disruption": 0.50,
    }


def _state() -> DriverState:
    return DriverEngine().create_state(_raw_values(), timestamp="2026-06-28T00:00:00Z")


def _state_series() -> tuple[DriverState, ...]:
    engine = DriverEngine()
    return tuple(
        engine.create_state(
            {key: value + index * 0.01 for key, value in _raw_values().items()},
            timestamp=f"2026-06-28T00:0{index}:00Z",
        )
        for index in range(4)
    )


def test_driver_type_values_and_ranges() -> None:
    assert len(tuple(DriverType)) == 10
    assert DriverType.CAPITAL_CONCENTRATION.value == "capital_concentration"
    assert DriverType.CAPITAL_CONCENTRATION.historical_range == (0.45, 0.92)
    assert "wealth" in DriverType.CAPITAL_CONCENTRATION.description.lower()


def test_driver_dimension_validation() -> None:
    dim = DriverDimension(DriverType.MARKET_VOLATILITY, weight=0.5)
    assert dim.subordination_notice == SUBORDINATION_NOTICE
    with pytest.raises(DriverEngineError, match="weight"):
        DriverDimension(DriverType.MARKET_VOLATILITY, weight=0.0)
    with pytest.raises(FrozenInstanceError):
        dim.weight = 1.0  # type: ignore[misc]


def test_driver_state_validation() -> None:
    state = _state()
    assert state.subordination_notice == SUBORDINATION_NOTICE
    assert len(state.values) == 10
    assert state.values["capital_concentration"] == pytest.approx(0.5)
    with pytest.raises(DriverEngineError, match="10 driver values"):
        DriverState(values={"x": 0.5}, timestamp="2026-06-28T00:00:00Z")
    with pytest.raises(DriverEngineError, match="driver value"):
        DriverState(values={driver.value: 2.0 for driver in DriverType})
    with pytest.raises(DriverEngineError, match="timestamp"):
        DriverState(values={driver.value: 0.5 for driver in DriverType}, timestamp="")


def test_normalize_and_denormalize_round_trip() -> None:
    engine = DriverEngine()
    raw = 0.685
    normalized = engine.normalize_value(DriverType.CAPITAL_CONCENTRATION, raw)
    assert normalized == pytest.approx(0.5)
    assert engine.denormalize_value(DriverType.CAPITAL_CONCENTRATION, normalized) == pytest.approx(
        raw
    )
    assert engine.normalize_value(DriverType.CAPITAL_CONCENTRATION, 999.0) == 1.0
    with pytest.raises(DriverEngineError, match="normalized_value"):
        engine.denormalize_value(DriverType.CAPITAL_CONCENTRATION, 1.1)


def test_create_state_requires_all_drivers() -> None:
    values = _raw_values()
    del values["media_gatekeeping"]
    with pytest.raises(DriverEngineError, match="missing"):
        DriverEngine().create_state(values)


def test_create_state_is_deterministic() -> None:
    engine = DriverEngine()
    first = engine.create_state(_raw_values(), timestamp="2026-06-28T00:00:00Z")
    second = engine.create_state(
        dict(reversed(_raw_values().items())), timestamp="2026-06-28T00:00:00Z"
    )
    assert first == second
    assert first.state_sha256 == second.state_sha256


def test_compute_derived_metrics() -> None:
    metrics = DriverEngine().compute_derived_metrics(_state())
    assert metrics["systemic_risk_index"] == pytest.approx(0.5)
    assert metrics["information_control_index"] == pytest.approx(0.5)
    assert metrics["elite_capture_potential"] == pytest.approx(0.25)
    assert metrics["economic_instability"] == pytest.approx(0.5)


def test_compute_derived_metrics_includes_graph_metrics() -> None:
    metrics = DriverEngine().compute_derived_metrics(
        _state(),
        graph_metrics={"centralization": 0.4, "modularity": 0.3, "power_concentration": 0.2},
    )
    assert metrics["graph_concentration"] == 0.2
    assert metrics["network_fragmentation"] == 0.3
    assert metrics["influence_centralization"] == 0.4


def test_compute_pca() -> None:
    result = compute_pca(_state_series(), components=2)
    assert len(result.components) == 2
    assert len(result.components[0]) == 10
    assert len(result.explained_variance) == 2
    assert result.subordination_notice == SUBORDINATION_NOTICE
    assert len(result.analysis_sha256) == 64


def test_compute_pca_validates_inputs() -> None:
    with pytest.raises(DriverEngineError, match="at least two"):
        compute_pca((_state(),), components=1)
    with pytest.raises(DriverEngineError, match="components"):
        compute_pca(_state_series(), components=0)


def test_compute_correlation_matrix() -> None:
    matrix = compute_correlation_matrix(_state_series())
    assert tuple(matrix) == tuple(driver.value for driver in DriverType)
    for driver in DriverType:
        assert matrix[driver.value][driver.value] == pytest.approx(1.0)


def test_compute_correlation_matrix_validates_inputs() -> None:
    with pytest.raises(DriverEngineError, match="at least two"):
        compute_correlation_matrix((_state(),))


def test_compute_driver_sensitivities() -> None:
    sensitivities = compute_driver_sensitivities(_state(), target_metric="systemic_risk_index")
    assert sensitivities["capital_concentration"] > 0.0
    assert sensitivities["institutional_capture_risk"] > 0.0
    assert sensitivities["governance_fragility"] > 0.0
    assert sensitivities["market_volatility"] == 0.0


def test_compute_driver_sensitivities_validates_metric() -> None:
    with pytest.raises(DriverEngineError, match="target_metric"):
        compute_driver_sensitivities(_state(), target_metric="missing")


def test_engine_analyze_returns_driver_analysis() -> None:
    analysis = DriverEngine().analyze(_state_series(), target_metric="systemic_risk_index")
    assert isinstance(analysis, DriverAnalysis)
    assert len(analysis.pca.components) == 3
    assert "capital_concentration" in analysis.correlations
    assert "governance_fragility" in analysis.sensitivities
    assert analysis.subordination_notice == SUBORDINATION_NOTICE
    assert len(analysis.analysis_sha256) == 64


def test_engine_analyze_is_deterministic() -> None:
    engine = DriverEngine()
    first = engine.analyze(_state_series())
    second = engine.analyze(reversed(_state_series()))
    assert first.analysis_sha256 == second.analysis_sha256
    assert first == second


def test_engine_audit_events() -> None:
    trail = AuditTrail()
    engine = DriverEngine(audit_trail=trail)
    state = engine.create_state(_raw_values())
    analysis = engine.analyze(_state_series())
    assert len(trail) == 3
    assert trail.events[0].action == "driver_engine_initialized"
    assert trail.events[1].action == "driver_state_created"
    assert trail.events[2].action == "driver_analysis_completed"
    assert trail.events[2].level == AuditLevel.STANDARD
    assert trail.events[2].category == AuditCategory.OPERATION
    assert ("state_sha256", state.state_sha256) in trail.events[1].evidence
    assert ("analysis_sha256", analysis.analysis_sha256) in trail.events[2].evidence
    assert trail.verify_chain().is_valid


def test_engine_audit_failure_event() -> None:
    trail = AuditTrail()
    engine = DriverEngine(audit_trail=trail)
    values = _raw_values()
    del values["social_cohesion"]
    with pytest.raises(DriverEngineError):
        engine.create_state(values)
    assert trail.events[-1].action == "driver_state_create_failed"
    assert trail.events[-1].level == AuditLevel.HIGH_PRIORITY
    assert trail.verify_chain().is_valid


def test_statistics_are_thread_safe() -> None:
    engine = DriverEngine()
    threads = [Thread(target=lambda: engine.create_state(_raw_values())) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert engine.get_statistics()["states_created"] == 8


def test_factory_and_reset() -> None:
    reset_driver_engine()
    first = get_driver_engine()
    second = get_driver_engine()
    assert first is second
    reset_driver_engine()
    assert get_driver_engine() is not first
