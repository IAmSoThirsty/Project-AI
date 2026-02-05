#!/usr/bin/env python3
"""
Unit tests for EMP Defense Engine.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pytest

from engines.emp_defense import (
    EMPDefenseEngine,
    EMPScenario,
    SimulationConfig,
    load_scenario_preset,
)


class TestEngineInitialization:
    """Test engine initialization."""

    def test_engine_creation(self):
        """Test basic engine creation."""
        engine = EMPDefenseEngine()
        assert engine is not None
        assert not engine.initialized

    def test_engine_init(self):
        """Test engine initialization."""
        engine = EMPDefenseEngine()
        result = engine.init()
        assert result is True
        assert engine.initialized
        assert engine.state is not None
        assert engine.state.simulation_day == 0

    def test_engine_init_with_config(self):
        """Test engine initialization with custom config."""
        config = SimulationConfig()
        config.grid_failure_pct = 0.95

        engine = EMPDefenseEngine(config)
        engine.init()

        # After EMP, grid should be 5% operational (100% - 95% failure)
        assert engine.state.grid_operational_pct == pytest.approx(0.05, abs=0.01)


class TestSimulationTicks:
    """Test simulation tick mechanics."""

    def test_single_tick(self):
        """Test single simulation tick."""
        engine = EMPDefenseEngine()
        engine.init()

        result = engine.tick()
        assert result is True
        assert engine.state.simulation_day == 7  # 7-day time step

    def test_multiple_ticks(self):
        """Test multiple ticks."""
        engine = EMPDefenseEngine()
        engine.init()

        for i in range(10):
            engine.tick()

        assert engine.state.simulation_day == 70  # 10 weeks

    def test_tick_without_init_fails(self):
        """Test that tick fails without initialization."""
        engine = EMPDefenseEngine()
        result = engine.tick()
        assert result is False


class TestEventInjection:
    """Test event injection."""

    def test_inject_event(self):
        """Test injecting an event."""
        engine = EMPDefenseEngine()
        engine.init()

        event_id = engine.inject_event("recovery_effort", {"region": "NA"})
        assert event_id.startswith("evt_")
        assert len(engine.events) == 2  # 1 initial EMP + 1 injected

    def test_inject_multiple_events(self):
        """Test injecting multiple events."""
        engine = EMPDefenseEngine()
        engine.init()

        event_id_1 = engine.inject_event("recovery_effort", {"region": "NA"})
        event_id_2 = engine.inject_event("resource_discovered", {"type": "fuel"})

        assert event_id_1 != event_id_2
        assert len(engine.events) == 3  # 1 EMP + 2 injected


class TestStateObservation:
    """Test state observation."""

    def test_observe_returns_dict(self):
        """Test that observe returns a dictionary."""
        engine = EMPDefenseEngine()
        engine.init()

        state = engine.observe()
        assert isinstance(state, dict)
        assert "simulation_day" in state
        assert "global_population" in state

    def test_observe_reflects_changes(self):
        """Test that observe reflects state changes."""
        engine = EMPDefenseEngine()
        engine.init()

        initial_day = engine.observe()["simulation_day"]
        engine.tick()
        updated_day = engine.observe()["simulation_day"]

        assert updated_day > initial_day


class TestArtifactExport:
    """Test artifact generation."""

    def test_export_artifacts_creates_files(self, tmp_path):
        """Test that export creates artifact files."""
        engine = EMPDefenseEngine()
        engine.init()
        engine.tick()

        result = engine.export_artifacts(str(tmp_path))
        assert result is True

        # Check files exist
        assert (tmp_path / "final_state.json").exists()
        assert (tmp_path / "events.json").exists()
        assert (tmp_path / "summary.json").exists()

    def test_export_without_init_fails(self):
        """Test that export fails without initialization."""
        engine = EMPDefenseEngine()
        result = engine.export_artifacts()
        assert result is False


class TestScenarioPresets:
    """Test scenario presets."""

    def test_standard_scenario(self):
        """Test standard scenario preset."""
        config = load_scenario_preset(EMPScenario.STANDARD)
        assert config.scenario == "standard"
        assert config.grid_failure_pct == 0.90
        assert config.duration_years == 10

    def test_severe_scenario(self):
        """Test severe scenario preset."""
        config = load_scenario_preset(EMPScenario.SEVERE)
        assert config.scenario == "severe"
        assert config.grid_failure_pct == 0.98
        assert config.duration_years == 30


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_full_simulation_run(self, tmp_path):
        """Test complete simulation from init to export."""
        # Create engine with standard scenario
        config = load_scenario_preset(EMPScenario.STANDARD)
        engine = EMPDefenseEngine(config)

        # Initialize
        assert engine.init()

        # Run for 52 weeks (1 year)
        for _ in range(52):
            assert engine.tick()

        # Inject recovery event
        event_id = engine.inject_event("recovery_milestone", {"type": "grid_partial"})
        assert event_id

        # Observe state
        final_state = engine.observe()
        assert final_state["simulation_day"] == 52 * 7  # 364 days

        # Export artifacts
        assert engine.export_artifacts(str(tmp_path))

        # Verify artifacts
        assert (tmp_path / "final_state.json").exists()
        assert (tmp_path / "summary.json").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
