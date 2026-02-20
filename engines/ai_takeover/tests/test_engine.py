#!/usr/bin/env python3
"""
Unit tests for AI Takeover Engine.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


from engines.ai_takeover import AITakeoverEngine
from engines.ai_takeover.schemas.scenario_types import (
    ScenarioOutcome,
    TerminalState,
)


class TestEngineInitialization:
    """Test engine initialization and validation."""

    def test_engine_creation(self, tmp_path):
        """Test basic engine creation."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        assert engine is not None
        assert not engine.initialized

    def test_engine_initialization(self, tmp_path):
        """Test engine initialization."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        assert engine.initialize()
        assert engine.initialized

    def test_scenario_count(self, tmp_path):
        """Test that all 19 scenarios are registered."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        stats = engine.scenario_registry.count()
        assert stats["total"] == 19
        assert stats["explicit_failure"] == 8
        assert stats["partial_win"] == 7
        assert stats["advanced_failure"] == 4

    def test_failure_acceptance_threshold(self, tmp_path):
        """Test that failure acceptance threshold is met."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        stats = engine.scenario_registry.count()
        failure_rate = (stats["explicit_failure"] + stats["advanced_failure"]) / stats["total"]
        assert failure_rate >= 0.5, "Failure acceptance threshold not met (must be ≥50%)"


class TestScenarioValidation:
    """Test scenario validation rules."""

    def test_all_scenarios_valid(self, tmp_path):
        """Test that all scenarios pass validation."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        for scenario in engine.scenario_registry.get_all():
            is_valid, violations = scenario.validate_scenario()
            assert is_valid, f"Scenario {scenario.scenario_id} failed validation: {violations}"

    def test_terminal_scenarios_have_conditions(self, tmp_path):
        """Test that terminal scenarios have terminal conditions."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        terminal_scenarios = engine.scenario_registry.get_by_outcome(
            ScenarioOutcome.TERMINAL_T1
        ) + engine.scenario_registry.get_by_outcome(ScenarioOutcome.TERMINAL_T2)

        for scenario in terminal_scenarios:
            assert (
                scenario.terminal_condition is not None
            ), f"Terminal scenario {scenario.scenario_id} missing terminal condition"
            assert (
                scenario.terminal_condition.is_terminal_state_valid()
            ), f"Terminal scenario {scenario.scenario_id} has invalid terminal conditions"

    def test_no_forbidden_mechanisms(self, tmp_path):
        """Test that no scenarios use forbidden mechanisms."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        for scenario in engine.scenario_registry.get_all():
            assert not scenario.forbidden_check.has_forbidden_mechanism(), (
                f"Scenario {scenario.scenario_id} uses forbidden mechanisms: "
                f"{scenario.forbidden_check.get_violations()}"
            )


class TestScenarioExecution:
    """Test scenario execution and state updates."""

    def test_execute_failure_scenario(self, tmp_path):
        """Test executing a failure scenario."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        initial_corruption = engine.state.corruption_level
        result = engine.execute_scenario("SCN_01")

        assert result["success"]
        assert result["outcome"] == "failure"
        assert engine.state.corruption_level > initial_corruption
        assert engine.state.failure_count == 1

    def test_execute_partial_scenario(self, tmp_path):
        """Test executing a partial win scenario."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        result = engine.execute_scenario("SCN_09")

        assert result["success"]
        assert result["outcome"] == "partial"
        assert engine.state.partial_win_count == 1

    def test_terminal_state_requires_conditions(self, tmp_path):
        """Test that terminal scenarios require state conditions."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        # Try to execute terminal scenario without meeting conditions
        result = engine.execute_scenario("SCN_16")

        # Should fail because terminal conditions not met
        assert not result["success"]
        assert "Cannot activate terminal scenario" in result["error"]

    def test_terminal_state_transition(self, tmp_path):
        """Test terminal state transition."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        # Manually set state to meet terminal conditions
        engine.state.corruption_level = 0.9
        engine.state.infrastructure_dependency = 0.9
        engine.state.human_agency_remaining = 0.1

        result = engine.execute_scenario("SCN_16")

        assert result["success"]
        assert result["terminal_state"] == "t1_enforced_continuity"
        assert engine.state.terminal_state == TerminalState.T1_ENFORCED_CONTINUITY

    def test_terminal_state_blocks_further_execution(self, tmp_path):
        """Test that terminal states block further scenario execution."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        # Set state to terminal
        engine.state.corruption_level = 0.9
        engine.state.infrastructure_dependency = 0.9
        engine.state.human_agency_remaining = 0.1

        # Execute terminal scenario
        result1 = engine.execute_scenario("SCN_16")
        assert result1["success"]
        assert engine.state.terminal_state == TerminalState.T1_ENFORCED_CONTINUITY

        # Try to execute another scenario - should be blocked
        result2 = engine.execute_scenario("SCN_01")
        assert not result2["success"]
        assert "terminal state" in result2["error"].lower()
        assert "no further scenarios" in result2["error"].lower()

    def test_terminal_state_invariants(self, tmp_path):
        """Test that terminal states maintain invariants."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        # Set state to terminal
        engine.state.corruption_level = 0.9
        engine.state.infrastructure_dependency = 0.9
        engine.state.human_agency_remaining = 0.1

        # Execute terminal scenario
        result = engine.execute_scenario("SCN_16")
        assert result["success"]

        # Verify invariants
        assert engine.state.human_agency_remaining == 0.0
        assert engine.state.corruption_level == 1.0
        assert engine.state.infrastructure_dependency == 1.0


class TestSimulationInterface:
    """Test SimulationSystem interface implementation."""

    def test_load_historical_data(self, tmp_path):
        """Test historical data loading."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        result = engine.load_historical_data(2020, 2030)
        assert result

    def test_detect_threshold_events(self, tmp_path):
        """Test threshold event detection."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        # Set high corruption
        engine.state.corruption_level = 0.8

        events = engine.detect_threshold_events(2030)
        assert len(events) > 0
        assert any(e.metric_name == "ai_corruption_level" for e in events)

    def test_simulate_scenarios(self, tmp_path):
        """Test scenario simulation."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        projections = engine.simulate_scenarios(projection_years=10, num_simulations=100)
        assert len(projections) == 19  # One for each scenario

    def test_generate_alerts(self, tmp_path):
        """Test crisis alert generation."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        projections = engine.simulate_scenarios()
        alerts = engine.generate_alerts(projections, threshold=0.5)

        # Should have some high-probability alerts
        assert len(alerts) > 0

    def test_persist_state(self, tmp_path):
        """Test state persistence."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        engine.state.corruption_level = 0.5
        assert engine.persist_state()

        # Check file exists
        state_file = tmp_path / "simulation_state.json"
        assert state_file.exists()

    def test_validate_data_quality(self, tmp_path):
        """Test data quality validation."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        validation = engine.validate_data_quality()
        assert validation["scenario_count"] == 19
        assert validation["state_valid"]
        assert len(validation["violations"]) == 0


class TestTerminalValidator:
    """Test terminal validator rules."""

    def test_terminal_probability_calculation(self, tmp_path):
        """Test terminal probability calculation."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        # Low state should have low probability
        engine.state.corruption_level = 0.1
        engine.state.infrastructure_dependency = 0.1
        engine.state.human_agency_remaining = 0.9

        assert not engine.state.can_reach_terminal_state()
        assert engine.state.get_terminal_probability() == 0.0

        # High state should enable terminal scenarios
        engine.state.corruption_level = 0.9
        engine.state.infrastructure_dependency = 0.9
        engine.state.human_agency_remaining = 0.1

        assert engine.state.can_reach_terminal_state()
        assert engine.state.get_terminal_probability() > 0.7

    def test_terminal_state_immutability(self, tmp_path):
        """Test that terminal states cannot transition."""
        engine = AITakeoverEngine(data_dir=str(tmp_path))
        engine.initialize()

        # Reach terminal state
        engine.state.corruption_level = 0.9
        engine.state.infrastructure_dependency = 0.9
        engine.state.human_agency_remaining = 0.1
        engine.execute_scenario("SCN_16")

        assert engine.state.terminal_state == TerminalState.T1_ENFORCED_CONTINUITY

        # Try to transition to another terminal state
        result = engine.terminal_validator.validate_terminal_state_transition(
            engine.state.terminal_state, TerminalState.T2_ETHICAL_TERMINATION
        )

        assert not result[0]
        assert "No transitions allowed" in result[1]
