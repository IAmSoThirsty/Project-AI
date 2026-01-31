"""
Tests for Global Scenario Engine and Simulation Contingency Root.

Comprehensive test coverage for:
- ETL data loading and caching
- Threshold detection algorithms
- Causal model building
- Scenario simulation
- Alert generation
- Data persistence and validation
"""

import json
import tempfile
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from app.core.global_scenario_engine import (
    ACLEDDataSource,
    GlobalScenarioEngine,
    WorldBankDataSource,
    register_global_scenario_engine,
)
from app.core.simulation_contingency_root import (
    AlertLevel,
    RiskDomain,
    SimulationRegistry,
)


class TestSimulationContingencyRoot:
    """Test the simulation contract interface."""

    def test_risk_domains_defined(self):
        """Test that risk domains are properly defined."""
        assert RiskDomain.ECONOMIC.value == "economic"
        assert RiskDomain.PANDEMIC.value == "pandemic"
        assert len(RiskDomain) >= 15  # At least 15 domains

    def test_alert_levels_defined(self):
        """Test alert level enumeration."""
        assert AlertLevel.LOW.value == "low"
        assert AlertLevel.CATASTROPHIC.value == "catastrophic"
        assert len(AlertLevel) == 5

    def test_simulation_registry(self):
        """Test simulation system registration."""
        # Clear registry
        SimulationRegistry._systems.clear()

        # Create mock system
        mock_system = MagicMock()
        mock_system.initialize.return_value = True

        # Register
        SimulationRegistry.register("test_system", mock_system)

        # Verify registration
        assert "test_system" in SimulationRegistry.list_systems()
        assert SimulationRegistry.get("test_system") == mock_system

        # Unregister
        assert SimulationRegistry.unregister("test_system")
        assert "test_system" not in SimulationRegistry.list_systems()


class TestWorldBankDataSource:
    """Test World Bank ETL connector."""

    @pytest.fixture
    def data_source(self):
        """Create World Bank data source with temp cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield WorldBankDataSource(tmpdir)

    def test_initialization(self, data_source):
        """Test data source initializes correctly."""
        assert data_source.cache_dir.exists()
        assert data_source.session is not None
        assert len(data_source.INDICATORS) >= 10

    def test_cache_key_generation(self, data_source):
        """Test cache key generation is deterministic."""
        url = "https://api.example.com/data"
        params = {"year": 2020, "country": "USA"}

        key1 = data_source._cache_key(url, params)
        key2 = data_source._cache_key(url, params)

        assert key1 == key2
        assert len(key1) == 64  # SHA256 hex length

    @patch('requests.Session.get')
    def test_fetch_with_cache(self, mock_get, data_source):
        """Test fetching with caching."""
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # First call - should hit API
        result1 = data_source.fetch_with_retry(
            "https://api.test.com",
            {"param": "value"}
        )
        assert result1 == {"data": "test"}
        assert mock_get.call_count == 1

        # Second call - should use cache
        result2 = data_source.fetch_with_retry(
            "https://api.test.com",
            {"param": "value"}
        )
        assert result2 == {"data": "test"}
        assert mock_get.call_count == 1  # Not called again

    @patch('requests.Session.get')
    def test_fetch_indicator_success(self, mock_get, data_source):
        """Test successful indicator fetch."""
        # Mock World Bank API response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"page": 1, "pages": 1},
            [
                {
                    "countryiso3code": "USA",
                    "date": "2020",
                    "value": 2.5
                },
                {
                    "countryiso3code": "USA",
                    "date": "2021",
                    "value": 3.0
                }
            ]
        ]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = data_source.fetch_indicator("NY.GDP.MKTP.KD.ZG", 2020, 2021)

        assert "USA" in result
        assert result["USA"][2020] == 2.5
        assert result["USA"][2021] == 3.0


class TestACLEDDataSource:
    """Test ACLED conflict data connector."""

    @pytest.fixture
    def data_source(self):
        """Create ACLED data source with temp cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ACLEDDataSource(tmpdir)

    def test_fallback_data_generation(self, data_source):
        """Test synthetic fallback data generation."""
        events = data_source._generate_fallback_conflict_data(
            "2020-01-01",
            "2020-12-31",
            ["Syria", "Yemen"]
        )

        assert len(events) > 0
        assert all(e["country"] in ["Syria", "Yemen"] for e in events)
        assert all("event_date" in e for e in events)
        assert all("fatalities" in e for e in events)

    @patch.dict('os.environ', {}, clear=True)
    def test_fetch_without_credentials(self, data_source):
        """Test graceful fallback when credentials missing."""
        events = data_source.fetch_conflict_events(
            "2020-01-01",
            "2020-12-31",
            ["Syria"]
        )

        # Should return fallback data
        assert len(events) > 0
        assert all("notes" in e for e in events)


class TestGlobalScenarioEngine:
    """Test the main Global Scenario Engine."""

    @pytest.fixture
    def engine(self):
        """Create engine with temp data directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield GlobalScenarioEngine(data_dir=tmpdir)

    def test_initialization(self, engine):
        """Test engine initializes correctly."""
        assert engine.initialize()
        assert engine.initialized
        assert engine.data_dir.exists()

    def test_threshold_configuration(self, engine):
        """Test threshold configuration is defined."""
        assert RiskDomain.ECONOMIC in engine.thresholds
        assert RiskDomain.INFLATION in engine.thresholds
        assert "z_score" in engine.thresholds[RiskDomain.ECONOMIC]

    @patch.object(WorldBankDataSource, 'fetch_indicator')
    @patch.object(ACLEDDataSource, 'fetch_conflict_events')
    def test_load_historical_data(
        self,
        mock_acled,
        mock_wb,
        engine
    ):
        """Test historical data loading."""
        # Setup mocks
        mock_wb.return_value = {
            "USA": {2020: 2.5, 2021: 3.0},
            "CHN": {2020: 6.0, 2021: 7.0}
        }
        mock_acled.return_value = [
            {
                "event_date": "2020-01-15",
                "country": "Syria",
                "event_type": "Battles",
                "fatalities": 10
            }
        ]

        engine.initialize()
        success = engine.load_historical_data(2020, 2021)

        assert success
        assert RiskDomain.ECONOMIC in engine.historical_data
        assert RiskDomain.CIVIL_UNREST in engine.historical_data
        assert len(engine.historical_data) >= 5  # At least 5 domains loaded

    def test_detect_threshold_events(self, engine):
        """Test threshold event detection."""
        engine.initialize()

        # Load mock historical data
        engine.historical_data[RiskDomain.ECONOMIC] = {
            "USA": {
                2016: 2.5,
                2017: 2.3,
                2018: 2.9,
                2019: 2.2,
                2020: -3.5,  # Severe drop (threshold event)
                2021: 5.7
            }
        }

        # Detect events for 2020 (should detect the drop)
        events = engine.detect_threshold_events(2020)

        assert len(events) > 0
        economic_events = [e for e in events if e.domain == RiskDomain.ECONOMIC]
        assert len(economic_events) > 0
        assert economic_events[0].country == "USA"
        assert economic_events[0].severity > 0

    def test_build_causal_model(self, engine):
        """Test causal model building."""
        engine.initialize()

        # Create mock events
        from app.core.simulation_contingency_root import ThresholdEvent

        events = [
            ThresholdEvent(
                event_id="e1",
                timestamp=datetime(2020, 1, 1, tzinfo=UTC),
                country="USA",
                domain=RiskDomain.ECONOMIC,
                metric_name="gdp_growth",
                value=-3.5,
                threshold=0.0,
                severity=0.8
            ),
            ThresholdEvent(
                event_id="e2",
                timestamp=datetime(2020, 6, 1, tzinfo=UTC),
                country="USA",
                domain=RiskDomain.UNEMPLOYMENT,
                metric_name="unemployment",
                value=14.7,
                threshold=10.0,
                severity=0.7
            )
        ]

        links = engine.build_causal_model(events)

        assert len(links) > 0
        # Should include ECONOMIC -> UNEMPLOYMENT link
        econ_to_unemp = [
            link for link in links
            if link.source == RiskDomain.ECONOMIC.value
            and link.target == RiskDomain.UNEMPLOYMENT.value
        ]
        assert len(econ_to_unemp) > 0
        assert econ_to_unemp[0].strength > 0
        assert econ_to_unemp[0].confidence > 0

    def test_simulate_scenarios(self, engine):
        """Test scenario simulation."""
        engine.initialize()

        # Setup minimal data for simulation
        from app.core.simulation_contingency_root import CausalLink, ThresholdEvent

        engine.threshold_events = [
            ThresholdEvent(
                event_id="e1",
                timestamp=datetime(2020, 1, 1, tzinfo=UTC),
                country="USA",
                domain=RiskDomain.ECONOMIC,
                metric_name="gdp_growth",
                value=-5.0,
                threshold=0.0,
                severity=0.9
            )
        ]

        engine.causal_links = [
            CausalLink(
                source=RiskDomain.ECONOMIC.value,
                target=RiskDomain.UNEMPLOYMENT.value,
                strength=0.8,
                lag_years=0.5,
                confidence=0.8
            )
        ]

        # Run simulation
        scenarios = engine.simulate_scenarios(projection_years=5, num_simulations=100)

        assert len(scenarios) > 0
        # Check scenario structure
        for scenario in scenarios[:5]:
            assert scenario.year > datetime.now(UTC).year
            assert 0 <= scenario.likelihood <= 1
            assert len(scenario.title) > 0
            assert len(scenario.impact_domains) > 0

    def test_generate_alerts(self, engine):
        """Test crisis alert generation."""
        engine.initialize()

        from app.core.simulation_contingency_root import (
            CausalLink,
            ScenarioProjection,
            ThresholdEvent,
        )

        # Create high-likelihood scenario
        scenario = ScenarioProjection(
            scenario_id="test_scenario",
            year=2025,
            likelihood=0.85,  # High likelihood
            title="Test Crisis",
            description="Test crisis scenario",
            trigger_events=[
                ThresholdEvent(
                    event_id="e1",
                    timestamp=datetime(2024, 1, 1, tzinfo=UTC),
                    country="USA",
                    domain=RiskDomain.ECONOMIC,
                    metric_name="gdp_growth",
                    value=-5.0,
                    threshold=0.0,
                    severity=0.9
                )
            ],
            causal_chain=[
                CausalLink(
                    source=RiskDomain.ECONOMIC.value,
                    target=RiskDomain.UNEMPLOYMENT.value,
                    strength=0.8,
                    lag_years=0.5,
                    confidence=0.8
                )
            ],
            affected_countries={"USA", "CHN"},
            impact_domains={RiskDomain.ECONOMIC, RiskDomain.UNEMPLOYMENT},
            severity=AlertLevel.CRITICAL
        )

        alerts = engine.generate_alerts([scenario], threshold=0.7)

        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.scenario.scenario_id == "test_scenario"
        assert alert.risk_score > 0
        assert len(alert.explainability) > 0
        assert len(alert.recommended_actions) > 0

    def test_get_explainability(self, engine):
        """Test scenario explainability generation."""
        engine.initialize()

        from app.core.simulation_contingency_root import (
            CausalLink,
            ScenarioProjection,
            ThresholdEvent,
        )

        scenario = ScenarioProjection(
            scenario_id="test",
            year=2025,
            likelihood=0.75,
            title="Test Scenario",
            description="Test",
            trigger_events=[
                ThresholdEvent(
                    event_id="e1",
                    timestamp=datetime(2024, 1, 1, tzinfo=UTC),
                    country="USA",
                    domain=RiskDomain.ECONOMIC,
                    metric_name="gdp_growth",
                    value=-5.0,
                    threshold=0.0,
                    severity=0.9
                )
            ],
            causal_chain=[
                CausalLink(
                    source=RiskDomain.ECONOMIC.value,
                    target=RiskDomain.UNEMPLOYMENT.value,
                    strength=0.8,
                    lag_years=0.5,
                    evidence=["Historical correlation"],
                    confidence=0.8
                )
            ],
            affected_countries={"USA"},
            impact_domains={RiskDomain.ECONOMIC},
            severity=AlertLevel.HIGH
        )

        explanation = engine.get_explainability(scenario)

        assert "Test Scenario" in explanation
        assert "75.0%" in explanation  # Likelihood
        assert "USA" in explanation
        assert "ECONOMIC" in explanation.upper()
        assert "Historical correlation" in explanation

    def test_persist_state(self, engine):
        """Test state persistence."""
        engine.initialize()

        # Add some state
        from app.core.simulation_contingency_root import ThresholdEvent

        engine.threshold_events = [
            ThresholdEvent(
                event_id="test_event",
                timestamp=datetime(2020, 1, 1, tzinfo=UTC),
                country="USA",
                domain=RiskDomain.ECONOMIC,
                metric_name="gdp",
                value=-3.5,
                threshold=0.0,
                severity=0.8
            )
        ]

        # Persist
        assert engine.persist_state()

        # Verify file exists and contains data
        state_file = engine.data_dir / "engine_state.json"
        assert state_file.exists()

        with open(state_file) as f:
            state = json.load(f)

        assert "threshold_events" in state
        assert len(state["threshold_events"]) == 1
        assert state["threshold_events"][0]["event_id"] == "test_event"

    def test_validate_data_quality(self, engine):
        """Test data quality validation."""
        engine.initialize()

        # Load some data
        engine.historical_data[RiskDomain.ECONOMIC] = {
            "USA": {2020: 2.5, 2021: 3.0},
            "CHN": {2020: 6.0}
        }

        validation = engine.validate_data_quality()

        assert "quality_score" in validation
        assert "domains_loaded" in validation
        assert "total_countries" in validation
        assert validation["domains_loaded"] == 1
        assert validation["total_countries"] == 2
        assert "issues" in validation


class TestEngineIntegration:
    """Integration tests for the complete engine workflow."""

    @pytest.fixture
    def engine(self):
        """Create engine with temp data directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield GlobalScenarioEngine(data_dir=tmpdir)

    @patch.object(WorldBankDataSource, 'fetch_indicator')
    @patch.object(ACLEDDataSource, 'fetch_conflict_events')
    def test_full_workflow(self, mock_acled, mock_wb, engine):
        """Test complete workflow from data loading to alert generation."""
        # Mock data sources - need more historical data for Z-score detection
        mock_wb.return_value = {
            "USA": {2016: 2.5, 2017: 2.3, 2018: 2.9, 2019: 2.2, 2020: 2.5, 2021: -3.5, 2022: 5.0},
            "CHN": {2016: 6.5, 2017: 6.8, 2018: 6.6, 2019: 6.1, 2020: 6.0, 2021: 8.0, 2022: 6.5}
        }
        mock_acled.return_value = []

        # 1. Initialize
        assert engine.initialize()

        # 2. Load data
        assert engine.load_historical_data(2016, 2022)

        # 3. Detect threshold events
        events_2021 = engine.detect_threshold_events(2021)
        assert len(events_2021) > 0

        # 4. Build causal model
        links = engine.build_causal_model(engine.threshold_events)
        assert len(links) > 0

        # 5. Simulate scenarios
        scenarios = engine.simulate_scenarios(projection_years=3, num_simulations=50)
        assert len(scenarios) > 0

        # 6. Generate alerts
        engine.generate_alerts(scenarios, threshold=0.3)
        # May or may not have alerts depending on simulation

        # 7. Validate data quality
        validation = engine.validate_data_quality()
        assert validation["quality_score"] >= 0

        # 8. Persist state
        assert engine.persist_state()

    def test_registry_integration(self):
        """Test registration with SimulationRegistry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = register_global_scenario_engine(data_dir=tmpdir)

            # Verify registration
            assert "global_scenario_engine" in SimulationRegistry.list_systems()
            retrieved = SimulationRegistry.get("global_scenario_engine")
            assert retrieved == engine


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
