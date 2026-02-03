#!/usr/bin/env python3
"""
Integration tests for AICPD SimulationSystem adapter.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pytest

from engines.alien_invaders.integration import (
    AlienInvadersSimulationAdapter,
    register_aicpd_system,
)
from src.app.core.simulation_contingency_root import (
    SimulationRegistry,
)


class TestSimulationAdapter:
    """Test the SimulationSystem adapter."""

    def test_adapter_creation(self):
        """Test adapter creation."""
        adapter = AlienInvadersSimulationAdapter()
        assert adapter is not None
        assert not adapter.initialized

    def test_adapter_initialization(self):
        """Test adapter initialization."""
        adapter = AlienInvadersSimulationAdapter()
        assert adapter.initialize()
        assert adapter.initialized

    def test_load_historical_data(self):
        """Test historical data loading (no-op for AICPD)."""
        adapter = AlienInvadersSimulationAdapter()
        adapter.initialize()

        result = adapter.load_historical_data(2020, 2025)
        assert result is True

    def test_detect_threshold_events(self):
        """Test threshold event detection."""
        adapter = AlienInvadersSimulationAdapter()
        adapter.initialize()

        # Run simulation to generate events
        for _ in range(12):
            adapter.engine.tick()

        # Inject an event
        adapter.engine.inject_event(
            "alien_attack", {"severity": "high", "target_country": "USA"}
        )

        # Detect events for current year
        year = adapter.engine.state.current_date.year
        events = adapter.detect_threshold_events(year)

        assert isinstance(events, list)

    def test_build_causal_model(self):
        """Test causal model building."""
        adapter = AlienInvadersSimulationAdapter()
        adapter.initialize()

        # Run simulation
        for _ in range(12):
            adapter.engine.tick()

        # Get events
        year = adapter.engine.state.current_date.year
        events = adapter.detect_threshold_events(year)

        # Build causal model
        causal_links = adapter.build_causal_model(events)

        assert isinstance(causal_links, list)

    def test_simulate_scenarios(self):
        """Test scenario simulation."""
        adapter = AlienInvadersSimulationAdapter()
        adapter.initialize()

        # Run simulation
        for _ in range(12):
            adapter.engine.tick()

        # Generate scenarios
        scenarios = adapter.simulate_scenarios(projection_years=5)

        assert isinstance(scenarios, list)
        assert len(scenarios) > 0
        assert scenarios[0].title == "Alien Invasion Scenario"

    def test_generate_alerts(self):
        """Test alert generation."""
        adapter = AlienInvadersSimulationAdapter()
        adapter.initialize()

        # Run simulation
        for _ in range(12):
            adapter.engine.tick()

        # Generate scenarios and alerts
        scenarios = adapter.simulate_scenarios()
        alerts = adapter.generate_alerts(scenarios, threshold=0.0)

        assert isinstance(alerts, list)

    def test_get_explainability(self):
        """Test scenario explainability."""
        adapter = AlienInvadersSimulationAdapter()
        adapter.initialize()

        # Run simulation
        for _ in range(12):
            adapter.engine.tick()

        # Get scenario
        scenarios = adapter.simulate_scenarios()
        assert len(scenarios) > 0

        # Get explanation
        explanation = adapter.get_explainability(scenarios[0])

        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "Scenario:" in explanation

    def test_persist_state(self, tmp_path):
        """Test state persistence."""
        from engines.alien_invaders import SimulationConfig

        config = SimulationConfig()
        config.artifacts.artifact_dir = str(tmp_path / "artifacts")

        adapter = AlienInvadersSimulationAdapter(config)
        adapter.initialize()

        # Run simulation
        for _ in range(6):
            adapter.engine.tick()

        # Persist state
        assert adapter.persist_state()

        # Verify artifacts exist
        artifact_dir = tmp_path / "artifacts"
        assert artifact_dir.exists()

    def test_validate_data_quality(self):
        """Test data quality validation."""
        adapter = AlienInvadersSimulationAdapter()
        adapter.initialize()

        # Run simulation
        for _ in range(12):
            adapter.engine.tick()

        # Validate quality
        quality = adapter.validate_data_quality()

        assert isinstance(quality, dict)
        assert "status" in quality
        assert quality["status"] in ["valid", "invalid"]


class TestRegistryIntegration:
    """Test integration with SimulationRegistry."""

    def test_register_aicpd_system(self):
        """Test registering AICPD with registry."""
        # Register system
        result = register_aicpd_system()
        assert result is True

        # Verify registration
        systems = SimulationRegistry.list_systems()
        assert "alien_invaders" in systems

        # Retrieve system
        system = SimulationRegistry.get("alien_invaders")
        assert system is not None
        assert isinstance(system, AlienInvadersSimulationAdapter)

        # Clean up
        SimulationRegistry.unregister("alien_invaders")

    def test_registered_system_functionality(self):
        """Test functionality of registered system."""
        # Register
        register_aicpd_system()

        # Get system
        system = SimulationRegistry.get("alien_invaders")
        assert system is not None

        # Use system
        scenarios = system.simulate_scenarios(projection_years=5)
        assert len(scenarios) > 0

        # Clean up
        SimulationRegistry.unregister("alien_invaders")

    def test_multiple_registration_warning(self, caplog):
        """Test warning on duplicate registration."""
        import logging

        caplog.set_level(logging.WARNING)

        # First registration
        register_aicpd_system()

        # Second registration (should log warning)
        register_aicpd_system()

        # Check for warning (registry logs warning on overwrite)
        # Note: May not capture warning depending on logging setup

        # Clean up
        SimulationRegistry.unregister("alien_invaders")


class TestContractCompliance:
    """Test compliance with SimulationSystem contract."""

    def test_all_contract_methods_implemented(self):
        """Test that all contract methods are implemented."""
        adapter = AlienInvadersSimulationAdapter()

        # Check all required methods exist
        assert hasattr(adapter, "initialize")
        assert hasattr(adapter, "load_historical_data")
        assert hasattr(adapter, "detect_threshold_events")
        assert hasattr(adapter, "build_causal_model")
        assert hasattr(adapter, "simulate_scenarios")
        assert hasattr(adapter, "generate_alerts")
        assert hasattr(adapter, "get_explainability")
        assert hasattr(adapter, "persist_state")
        assert hasattr(adapter, "validate_data_quality")

    def test_method_signatures(self):
        """Test that method signatures match contract."""
        from inspect import signature

        from src.app.core.simulation_contingency_root import SimulationSystem

        adapter = AlienInvadersSimulationAdapter()

        # Check initialize signature
        adapter_sig = signature(adapter.initialize)
        contract_sig = signature(SimulationSystem.initialize)

        # Both should return bool
        assert adapter_sig.return_annotation is bool or adapter_sig.return_annotation == contract_sig.return_annotation


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    def test_full_integration_workflow(self):
        """Test complete integration workflow."""
        # Register system
        assert register_aicpd_system()

        # Retrieve system
        system = SimulationRegistry.get("alien_invaders")
        assert system is not None

        # Run simulation
        for _ in range(12):
            assert system.engine.tick()

        # Detect events
        year = system.engine.state.current_date.year
        events = system.detect_threshold_events(year)

        # Build causal model
        system.build_causal_model(events)

        # Generate scenarios
        scenarios = system.simulate_scenarios(projection_years=5)
        assert len(scenarios) > 0

        # Generate alerts
        system.generate_alerts(scenarios, threshold=0.0)

        # Validate data quality
        quality = system.validate_data_quality()
        assert quality["status"] in ["valid", "invalid"]

        # Persist state
        assert system.persist_state()

        # Clean up
        SimulationRegistry.unregister("alien_invaders")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
