#!/usr/bin/env python3
"""
Tests for Planetary Defense Monolith Integration

Tests the three integration points:
A. Invariants as sub-kernel with law evaluation
B. Causal clock as sole time authority
C. Read-only projection for SimulationRegistry
"""

from datetime import datetime

import pytest

from engines.alien_invaders.modules.causal_clock import CausalClock
from engines.alien_invaders.modules.invariants import (
    CompositeInvariantValidator,
)
from engines.alien_invaders.modules.planetary_defense_monolith import (
    ActionRequest,
    ActionVerdict,
    PlanetaryDefenseMonolith,
    RegistryAccessRequest,
)
from engines.alien_invaders.modules.world_state import Country, GlobalState


class TestIntegrationPointA:
    """Test Integration Point A: Invariants as Sub-Kernel with Law Evaluation"""

    def test_action_evaluation_with_no_violations(self):
        """Test that actions are approved when no invariants are violated."""
        clock = CausalClock()
        validator = CompositeInvariantValidator()
        monolith = PlanetaryDefenseMonolith(
            clock, validator, enable_strict_enforcement=True
        )

        # Create states with no violations
        prev_state = GlobalState(
            current_date=datetime(2030, 1, 1),
            day_number=0,
            global_population=8_000_000_000,
            global_gdp_usd=100_000_000_000_000,
        )
        prev_state.countries["USA"] = Country(
            name="USA",
            code="USA",
            population=330_000_000,
            gdp_usd=25_000_000_000_000,
            military_strength=0.9,
            technology_level=0.9,
            public_morale=0.7,
            government_stability=0.8,
        )

        current_state = GlobalState(
            current_date=datetime(2030, 1, 31),
            day_number=30,
            global_population=8_000_000_000,
            global_gdp_usd=100_000_000_000_000,
        )
        current_state.countries["USA"] = Country(
            name="USA",
            code="USA",
            population=330_000_000,
            gdp_usd=25_000_000_000_000,
            military_strength=0.9,
            technology_level=0.9,
            public_morale=0.7,
            government_stability=0.8,
        )

        # Create action request
        action = ActionRequest(
            action_id="test_action_1",
            action_type="economic_update",
            parameters={"change": "minor"},
            requestor="TestEngine",
        )

        # Evaluate action
        verdict = monolith.evaluate_action(action, current_state, prev_state)

        assert verdict.allowed is True
        assert len(verdict.violations) == 0
        assert "legal" in verdict.reason.lower()

    def test_action_rejection_with_invariant_violations(self):
        """Test that actions are rejected when invariants are violated."""
        clock = CausalClock()
        validator = CompositeInvariantValidator()
        monolith = PlanetaryDefenseMonolith(
            clock, validator, enable_strict_enforcement=True
        )

        # Create states with resource depletion but no GDP impact (violation)
        prev_state = GlobalState(
            current_date=datetime(2030, 1, 1),
            day_number=0,
            global_population=8_000_000_000,
            global_gdp_usd=100_000_000_000_000,
        )
        prev_state.remaining_resources = {"oil": 100.0, "minerals": 100.0}
        prev_state.countries["USA"] = Country(
            name="USA",
            code="USA",
            population=330_000_000,
            gdp_usd=25_000_000_000_000,
            military_strength=0.9,
            technology_level=0.9,
            public_morale=0.7,
            government_stability=0.8,
        )

        current_state = GlobalState(
            current_date=datetime(2030, 1, 31),
            day_number=30,
            global_population=8_000_000_000,
            global_gdp_usd=100_000_000_000_000,  # No GDP decline despite resource loss
        )
        current_state.remaining_resources = {
            "oil": 80.0,
            "minerals": 80.0,
        }  # 20% depletion
        current_state.countries["USA"] = Country(
            name="USA",
            code="USA",
            population=330_000_000,
            gdp_usd=25_000_000_000_000,  # GDP unchanged
            military_strength=0.9,
            technology_level=0.9,
            public_morale=0.7,
            government_stability=0.8,
        )

        # Create action request
        action = ActionRequest(
            action_id="test_action_2",
            action_type="resource_extraction",
            parameters={"amount": "large"},
            requestor="TestEngine",
        )

        # Evaluate action
        verdict = monolith.evaluate_action(action, current_state, prev_state)

        assert verdict.allowed is False
        assert len(verdict.violations) > 0
        assert "illegal" in verdict.reason.lower()
        assert "physical coherence" in verdict.reason.lower()

    def test_accountability_record_generation(self):
        """Test that accountability records are generated for all actions."""
        clock = CausalClock()
        validator = CompositeInvariantValidator()
        monolith = PlanetaryDefenseMonolith(
            clock, validator, enable_strict_enforcement=True
        )

        prev_state = GlobalState(
            current_date=datetime(2030, 1, 1),
            day_number=0,
            global_population=8_000_000_000,
            global_gdp_usd=100_000_000_000_000,
        )

        current_state = GlobalState(
            current_date=datetime(2030, 1, 31),
            day_number=30,
            global_population=8_000_000_000,
            global_gdp_usd=100_000_000_000_000,
        )

        action = ActionRequest(
            action_id="test_action_3",
            action_type="test_operation",
            parameters={},
            requestor="TestSystem",
        )

        verdict = monolith.evaluate_action(action, current_state, prev_state)

        # Check accountability record
        assert "accountability_record" in verdict.__dict__
        assert verdict.accountability_record["action_id"] == "test_action_3"
        assert verdict.accountability_record["requestor"] == "TestSystem"
        assert "logical_time" in verdict.accountability_record

    def test_action_log_tracking(self):
        """Test that all actions are logged for auditing."""
        clock = CausalClock()
        validator = CompositeInvariantValidator()
        monolith = PlanetaryDefenseMonolith(clock, validator)

        prev_state = GlobalState(
            current_date=datetime(2030, 1, 1),
            day_number=0,
            global_population=8_000_000_000,
            global_gdp_usd=100_000_000_000_000,
        )

        current_state = GlobalState(
            current_date=datetime(2030, 1, 31),
            day_number=30,
            global_population=8_000_000_000,
            global_gdp_usd=100_000_000_000_000,
        )

        # Execute multiple actions
        for i in range(3):
            action = ActionRequest(
                action_id=f"action_{i}",
                action_type="test",
                parameters={},
                requestor="TestEngine",
            )
            monolith.evaluate_action(action, current_state, prev_state)

        # Check action log
        action_log = monolith.get_action_log()
        assert len(action_log) == 3
        assert all(isinstance(entry[0], ActionRequest) for entry in action_log)
        assert all(isinstance(entry[1], ActionVerdict) for entry in action_log)


class TestIntegrationPointB:
    """Test Integration Point B: Causal Clock as Sole Time Authority"""

    def test_monolith_controls_time_advancement(self):
        """Test that monolith is the only entity advancing time."""
        clock = CausalClock()
        validator = CompositeInvariantValidator()
        monolith = PlanetaryDefenseMonolith(clock, validator)

        initial_time = monolith.get_current_time()
        assert initial_time == 0

        # Advance time through monolith
        new_time = monolith.advance_time()
        assert new_time == 1
        assert monolith.get_current_time() == 1

        # Advance again
        new_time = monolith.advance_time()
        assert new_time == 2
        assert monolith.get_current_time() == 2

    def test_time_consistency_in_evaluations(self):
        """Test that logical time is consistent across evaluations."""
        clock = CausalClock()
        validator = CompositeInvariantValidator()
        monolith = PlanetaryDefenseMonolith(clock, validator)

        prev_state = GlobalState(
            current_date=datetime(2030, 1, 1),
            day_number=0,
            global_population=8_000_000_000,
            global_gdp_usd=100_000_000_000_000,
        )

        current_state = GlobalState(
            current_date=datetime(2030, 1, 31),
            day_number=30,
            global_population=8_000_000_000,
            global_gdp_usd=100_000_000_000_000,
        )

        # Execute action and check time consistency
        action = ActionRequest(
            action_id="timed_action",
            action_type="test",
            parameters={},
            requestor="TestEngine",
        )

        time_before = monolith.get_current_time()
        verdict = monolith.evaluate_action(action, current_state, prev_state)
        time_after = monolith.get_current_time()

        # Time should not advance during evaluation
        assert time_before == time_after
        assert verdict.accountability_record["logical_time"] == time_before

    def test_no_race_conditions_with_sequential_time(self):
        """Test that sequential time advancement prevents race conditions."""
        clock = CausalClock()
        validator = CompositeInvariantValidator()
        monolith = PlanetaryDefenseMonolith(clock, validator)

        times = []
        for _i in range(10):
            times.append(monolith.advance_time())

        # All times should be sequential
        assert times == list(range(1, 11))

    def test_causal_clock_is_shared_reference(self):
        """Test that engine and monolith share the same causal clock."""
        from engines.alien_invaders import AlienInvadersEngine
        from engines.alien_invaders.schemas.config_schema import SimulationConfig

        config = SimulationConfig()
        engine = AlienInvadersEngine(config)

        # Verify that engine's monolith uses the engine's causal clock
        assert engine.monolith.causal_clock is engine.causal_clock


class TestIntegrationPointC:
    """Test Integration Point C: Read-Only Projection for SimulationRegistry"""

    def test_read_only_access_always_granted(self):
        """Test that read-only access is always granted in projection mode."""
        clock = CausalClock()
        validator = CompositeInvariantValidator()
        monolith = PlanetaryDefenseMonolith(clock, validator)

        access_request = RegistryAccessRequest(
            requestor="ExternalSystem",
            access_type="read",
            target="simulation_data",
        )

        allowed, reason = monolith.authorize_registry_access(access_request)

        assert allowed is True
        assert "projection" in reason.lower()

    def test_mutable_access_denied_without_monolith(self):
        """Test that mutable access is denied for external requestors."""
        clock = CausalClock()
        validator = CompositeInvariantValidator()
        monolith = PlanetaryDefenseMonolith(clock, validator)

        access_request = RegistryAccessRequest(
            requestor="ExternalSystem",
            access_type="write",
            target="simulation_data",
            context={"from_monolith": False},
        )

        allowed, reason = monolith.authorize_registry_access(access_request)

        assert allowed is False
        assert "inside the Monolith" in reason

    def test_mutable_access_denied_without_law_evaluation(self):
        """Test that mutable access requires law evaluation approval."""
        clock = CausalClock()
        validator = CompositeInvariantValidator()
        monolith = PlanetaryDefenseMonolith(clock, validator)

        access_request = RegistryAccessRequest(
            requestor="InternalSystem",
            access_type="write",
            target="simulation_data",
            context={"from_monolith": True, "law_evaluation_passed": False},
        )

        allowed, reason = monolith.authorize_registry_access(access_request)

        assert allowed is False
        assert "law evaluation" in reason

    def test_mutable_access_granted_with_full_authorization(self):
        """Test that mutable access is granted with proper authorization."""
        clock = CausalClock()
        validator = CompositeInvariantValidator()
        monolith = PlanetaryDefenseMonolith(clock, validator)

        access_request = RegistryAccessRequest(
            requestor="InternalSystem",
            access_type="write",
            target="simulation_data",
            context={"from_monolith": True, "law_evaluation_passed": True},
        )

        allowed, reason = monolith.authorize_registry_access(access_request)

        assert allowed is True
        assert "accountability" in reason
        assert "accountability_record" in access_request.context

    def test_access_log_tracking(self):
        """Test that all access requests are logged."""
        clock = CausalClock()
        validator = CompositeInvariantValidator()
        monolith = PlanetaryDefenseMonolith(clock, validator)

        # Make multiple access requests
        for i in range(3):
            access_request = RegistryAccessRequest(
                requestor=f"System_{i}",
                access_type="read",
                target=f"target_{i}",
            )
            monolith.authorize_registry_access(access_request)

        # Check access log
        access_log = monolith.get_access_log()
        assert len(access_log) == 3
        assert all(isinstance(entry[0], RegistryAccessRequest) for entry in access_log)
        assert all(isinstance(entry[1], bool) for entry in access_log)

    def test_registry_projection_mode_enforcement(self):
        """Test that SimulationRegistry enforces projection mode."""
        from unittest.mock import Mock

        from src.app.core.simulation_contingency_root import SimulationRegistry

        # Reset registry state
        SimulationRegistry._systems = {}
        SimulationRegistry._projection_mode = False
        SimulationRegistry._monolith_authority = None

        # Create mock monolith
        clock = CausalClock()
        validator = CompositeInvariantValidator()
        monolith = PlanetaryDefenseMonolith(clock, validator)

        # Enable projection mode with monolith
        SimulationRegistry.set_monolith_authority(monolith)
        SimulationRegistry.enable_projection_mode(True)

        # Try to register without monolith authorization
        mock_system = Mock()
        with pytest.raises(PermissionError):
            SimulationRegistry.register("test_system", mock_system, from_monolith=False)

        # Register with monolith authorization should work
        SimulationRegistry.register("test_system", mock_system, from_monolith=True)
        assert "test_system" in SimulationRegistry.list_systems()

        # Clean up
        SimulationRegistry._systems = {}
        SimulationRegistry._projection_mode = False
        SimulationRegistry._monolith_authority = None


class TestMonolithIntegration:
    """Test complete integration of all three points"""

    def test_end_to_end_monolithic_control(self):
        """Test complete monolithic control over engine operations."""
        from engines.alien_invaders import AlienInvadersEngine
        from engines.alien_invaders.schemas.config_schema import SimulationConfig

        config = SimulationConfig()
        engine = AlienInvadersEngine(config)
        engine.init()

        # Verify monolith is integrated
        assert hasattr(engine, "monolith")
        assert engine.monolith is not None

        # Verify causal clock is shared
        assert engine.monolith.causal_clock is engine.causal_clock

        # Execute tick and verify time is managed by monolith
        initial_time = engine.monolith.get_current_time()
        engine.tick()
        new_time = engine.monolith.get_current_time()

        assert new_time > initial_time

    def test_monolith_logs_all_operations(self):
        """Test that monolith maintains complete audit trail."""
        from engines.alien_invaders import AlienInvadersEngine
        from engines.alien_invaders.schemas.config_schema import SimulationConfig

        config = SimulationConfig()
        engine = AlienInvadersEngine(config)
        engine.init()

        # Execute some operations
        engine.tick()
        engine.tick()

        # Check that actions were logged
        action_log = engine.monolith.get_action_log()
        assert len(action_log) >= 2  # At least 2 ticks logged

    def test_monolith_prevents_temporal_exploits(self):
        """Test that monolith prevents time-based exploits."""
        clock = CausalClock()
        validator = CompositeInvariantValidator()
        monolith = PlanetaryDefenseMonolith(clock, validator)

        # Record time sequence
        time_sequence = []
        for _ in range(5):
            time_sequence.append(monolith.advance_time())

        # Verify monotonic increase (no going back in time)
        assert time_sequence == sorted(time_sequence)
        assert len(set(time_sequence)) == len(time_sequence)  # All unique


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
