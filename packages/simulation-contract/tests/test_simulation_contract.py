"""Tests for the shared simulation contract.

These tests verify the public surface of the
``simulation_contract`` package: the 9 types, their
behavior, and their interaction with the
``SimulationRegistry``.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest
from simulation_contract import (
    AlertLevel,
    CausalLink,
    CrisisAlert,
    RegistryAccessRequest,
    RiskDomain,
    ScenarioProjection,
    SimulationRegistry,
    SimulationSystem,
    ThresholdEvent,
)

# --- RiskDomain ----------------------------------------------------------


def test_risk_domain_has_20_values() -> None:
    """RiskDomain is the 20-value enum from the J2 contract."""
    assert len(RiskDomain) == 20
    # Spot-check a few expected values
    assert RiskDomain.ECONOMIC.value == "economic"
    assert RiskDomain.CYBERSECURITY.value == "cybersecurity"
    assert RiskDomain.SPACE.value == "space"
    assert RiskDomain.FINANCIAL.value == "financial"


# --- AlertLevel ----------------------------------------------------------


def test_alert_level_has_5_values() -> None:
    """AlertLevel is the 5-level enum."""
    assert len(AlertLevel) == 5
    assert AlertLevel.LOW.value == "low"
    assert AlertLevel.MEDIUM.value == "medium"
    assert AlertLevel.HIGH.value == "high"
    assert AlertLevel.CRITICAL.value == "critical"
    assert AlertLevel.CATASTROPHIC.value == "catastrophic"


# --- ThresholdEvent ------------------------------------------------------


def test_threshold_event_constructs_with_required_fields() -> None:
    """ThresholdEvent has event_id, timestamp, country, domain,
    metric_name, value, threshold, severity."""
    evt = ThresholdEvent(
        event_id="evt-1",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        country="USA",
        domain=RiskDomain.ECONOMIC,
        metric_name="inflation_rate",
        value=0.075,
        threshold=0.05,
        severity=0.8,
    )
    assert evt.event_id == "evt-1"
    assert evt.country == "USA"
    assert evt.domain == RiskDomain.ECONOMIC
    assert evt.metric_name == "inflation_rate"
    assert evt.value == 0.075
    assert evt.threshold == 0.05
    assert evt.severity == 0.8
    assert evt.context == {}  # default factory


# --- CausalLink ----------------------------------------------------------


def test_causal_link_constructs_with_required_fields() -> None:
    """CausalLink represents an edge in a causal graph."""
    link = CausalLink(
        source="event-A",
        target="event-B",
        strength=0.8,
        lag_years=2.5,
    )
    assert link.source == "event-A"
    assert link.target == "event-B"
    assert link.strength == 0.8
    assert link.lag_years == 2.5
    assert link.evidence == []  # default factory
    assert link.confidence == 0.0  # default


# --- ScenarioProjection --------------------------------------------------


def test_scenario_projection_constructs_with_required_fields() -> None:
    """ScenarioProjection holds the what-if scenario output."""
    evt = ThresholdEvent(
        event_id="evt-1",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        country="USA",
        domain=RiskDomain.ECONOMIC,
        metric_name="inflation_rate",
        value=0.075,
        threshold=0.05,
        severity=0.8,
    )
    proj = ScenarioProjection(
        scenario_id="proj-1",
        year=2026,
        likelihood=0.75,
        title="Sample scenario",
        description="A test scenario",
        trigger_events=[evt],
        causal_chain=[],
    )
    assert proj.scenario_id == "proj-1"
    assert proj.year == 2026
    assert proj.likelihood == 0.75
    assert proj.severity == AlertLevel.MEDIUM  # default


# --- CrisisAlert ---------------------------------------------------------


def test_crisis_alert_constructs_with_required_fields() -> None:
    """CrisisAlert is the fire-and-acknowledge alert."""
    evt = ThresholdEvent(
        event_id="evt-1",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        country="USA",
        domain=RiskDomain.PANDEMIC,
        metric_name="outbreak_size",
        value=1000.0,
        threshold=100.0,
        severity=0.95,
    )
    proj = ScenarioProjection(
        scenario_id="proj-1",
        year=2026,
        likelihood=0.9,
        title="Pandemic outbreak",
        description="outbreak detected",
        trigger_events=[evt],
        causal_chain=[],
    )
    alert = CrisisAlert(
        alert_id="alert-1",
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        scenario=proj,
        evidence=[evt],
        causal_activation=[],
        risk_score=95.0,
        explainability="Pandemic outbreak with 1000 cases",
    )
    assert alert.alert_id == "alert-1"
    assert alert.scenario == proj
    assert alert.risk_score == 95.0
    assert alert.recommended_actions == []  # default


# --- RegistryAccessRequest ----------------------------------------------


def test_registry_access_request_defaults() -> None:
    """RegistryAccessRequest has 3 required fields + 1 defaulted."""
    req = RegistryAccessRequest(
        requestor="monolith",
        access_type="write",
        target="register_test",
    )
    assert req.requestor == "monolith"
    assert req.access_type == "write"
    assert req.target == "register_test"
    assert req.context == {}  # default factory


def test_registry_access_request_with_context() -> None:
    """RegistryAccessRequest accepts an optional context dict."""
    req = RegistryAccessRequest(
        requestor="monolith",
        access_type="write",
        target="register_test",
        context={"from_monolith": True, "trace_id": "abc123"},
    )
    assert req.context == {"from_monolith": True, "trace_id": "abc123"}


# --- SimulationSystem (ABC) ----------------------------------------------


def test_simulation_system_is_abstract() -> None:
    """SimulationSystem cannot be instantiated directly
    (it has multiple abstract methods)."""
    with pytest.raises(TypeError):
        SimulationSystem()  # type: ignore[abstract]


def test_simulation_system_subclass_must_implement_all_abstracts() -> None:
    """A subclass that does not implement all abstract methods
    is itself abstract and cannot be instantiated."""

    class PartialEngine(SimulationSystem):
        # Implements nothing — should still be abstract.
        pass

    with pytest.raises(TypeError):
        PartialEngine()  # type: ignore[abstract]


def _make_stub_engine_class(name: str) -> type[SimulationSystem]:
    """Factory that creates a concrete ``SimulationSystem`` subclass
    with all 9 abstract methods stubbed out.

    SimulationSystem is an ABC with 9 abstract methods
    (initialize, load_historical_data,
    detect_threshold_events, build_causal_model,
    simulate_scenarios, generate_alerts,
    get_explainability, persist_state,
    validate_data_quality). The registry tests only
    care that the registered object IS a
    SimulationSystem, so we stub all 9 methods with
    ``NotImplementedError`` — a clear signal that
    this is a test-only stub and any actual use
    would require a real implementation.
    """

    class StubEngine(SimulationSystem):
        def name(self) -> str:
            return name

        def initialize(self) -> bool:
            raise NotImplementedError

        def load_historical_data(
            self,
            start_year: int,
            end_year: int,
            domains: list[RiskDomain] | None = None,
            countries: list[str] | None = None,
        ) -> bool:
            raise NotImplementedError

        def detect_threshold_events(
            self, year: int, domains: list[RiskDomain] | None = None
        ) -> list[ThresholdEvent]:
            raise NotImplementedError

        def build_causal_model(self, historical_events: list[ThresholdEvent]) -> list[CausalLink]:
            raise NotImplementedError

        def simulate_scenarios(
            self, projection_years: int = 10, num_simulations: int = 1000
        ) -> list[ScenarioProjection]:
            raise NotImplementedError

        def generate_alerts(
            self, scenarios: list[ScenarioProjection], threshold: float = 0.7
        ) -> list[CrisisAlert]:
            raise NotImplementedError

        def get_explainability(self, scenario: ScenarioProjection) -> str:
            raise NotImplementedError

        def persist_state(self) -> bool:
            raise NotImplementedError

        def validate_data_quality(self) -> dict[str, Any]:
            raise NotImplementedError

    return StubEngine


# --- SimulationRegistry --------------------------------------------------


def test_simulation_registry_register_and_get() -> None:
    """SimulationRegistry.register / get round-trip.

    Uses a stub ``SimulationSystem`` subclass that
    implements the 9 abstract methods with
    ``NotImplementedError`` — the registry only
    requires that the registered object IS a
    SimulationSystem instance.
    """
    StubEngine = _make_stub_engine_class("stub-engine-1")
    engine = StubEngine()
    SimulationRegistry.register("stub-engine-1", engine)
    try:
        got = SimulationRegistry.get("stub-engine-1")
        assert got is engine
    finally:
        if "stub-engine-1" in SimulationRegistry._systems:
            del SimulationRegistry._systems["stub-engine-1"]


def test_simulation_registry_get_unknown_returns_none() -> None:
    """get() returns None for an unknown name."""
    result = SimulationRegistry.get("nonexistent-engine-xyz")
    assert result is None


def test_simulation_registry_unregister() -> None:
    """SimulationRegistry.unregister removes a registered system."""
    TempEngine = _make_stub_engine_class("temp-engine-for-unregister")
    engine = TempEngine()
    SimulationRegistry.register("temp-engine-for-unregister", engine)
    assert SimulationRegistry.get("temp-engine-for-unregister") is engine
    SimulationRegistry.unregister("temp-engine-for-unregister")
    assert SimulationRegistry.get("temp-engine-for-unregister") is None
