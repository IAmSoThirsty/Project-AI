#!/usr/bin/env python3
"""
Tests for red team hardening features.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pytest

from engines.alien_invaders import AlienInvadersEngine, SimulationConfig
from engines.alien_invaders.modules.causal_clock import (
    CausalClock,
    CausalEvent,
    EventQueue,
)
from engines.alien_invaders.modules.invariants import (
    EconomicSocietalInvariant,
    ResourceEconomicInvariant,
)
from engines.alien_invaders.modules.world_state import Country, GlobalState


class TestCompositeInvariants:
    """Test composite invariant validation."""

    def test_resource_economic_invariant_violation(self):
        """Test that resource depletion without GDP impact is caught."""
        from datetime import datetime

        # Create two states - one with resource depletion, GDP unchanged
        prev_state = GlobalState(
            current_date=datetime(2026, 1, 1),
            day_number=0,
        )
        prev_state.countries["USA"] = Country(
            name="USA",
            code="USA",
            population=330_000_000,
            gdp_usd=25_000_000_000_000,
            military_strength=0.95,
            technology_level=0.90,
            government_stability=0.8,
            public_morale=0.7,
        )
        prev_state.remaining_resources = {
            "rare_earth_metals": 1.0,
            "fossil_fuels": 0.7,
            "fresh_water": 0.85,
        }

        curr_state = GlobalState(
            current_date=datetime(2026, 2, 1),
            day_number=30,
        )
        curr_state.countries["USA"] = Country(
            name="USA",
            code="USA",
            population=330_000_000,
            gdp_usd=25_000_000_000_000,  # GDP unchanged despite resource depletion
            military_strength=0.95,
            technology_level=0.90,
            government_stability=0.8,
            public_morale=0.7,
        )
        curr_state.remaining_resources = {
            "rare_earth_metals": 0.75,  # 25% depletion
            "fossil_fuels": 0.55,  # 15% depletion
            "fresh_water": 0.75,  # 10% depletion
        }

        # Validate
        invariant = ResourceEconomicInvariant()
        violations = invariant.validate(curr_state, prev_state)

        # Should detect violation
        assert len(violations) > 0
        assert "resource_economic_coherence" in violations[0].invariant_name

    def test_economic_societal_invariant_violation(self):
        """Test that GDP decline without morale impact is caught."""
        from datetime import datetime

        prev_state = GlobalState(
            current_date=datetime(2026, 1, 1),
            day_number=0,
        )
        prev_state.countries["USA"] = Country(
            name="USA",
            code="USA",
            population=330_000_000,
            gdp_usd=25_000_000_000_000,
            military_strength=0.95,
            technology_level=0.90,
            government_stability=0.8,
            public_morale=0.7,
        )

        curr_state = GlobalState(
            current_date=datetime(2026, 2, 1),
            day_number=30,
        )
        curr_state.countries["USA"] = Country(
            name="USA",
            code="USA",
            population=330_000_000,
            gdp_usd=20_000_000_000_000,  # 20% GDP decline
            military_strength=0.95,
            technology_level=0.90,
            government_stability=0.8,
            public_morale=0.7,  # Morale unchanged
        )

        # Validate
        invariant = EconomicSocietalInvariant()
        violations = invariant.validate(curr_state, prev_state)

        # Should detect violation
        assert len(violations) > 0
        assert "economic_societal_coherence" in violations[0].invariant_name

    def test_composite_validator_with_engine(self):
        """Test composite validator integration with engine."""
        engine = AlienInvadersEngine()
        engine.init()

        # Validator should be initialized
        assert engine.invariant_validator is not None
        assert len(engine.invariant_validator.invariants) > 0

        # Run a few ticks
        for _ in range(3):
            assert engine.tick()

        # Should have validation history
        assert len(engine.validation_history) > 0


class TestCausalClock:
    """Test causal clock and event ordering."""

    def test_causal_clock_advances(self):
        """Test that causal clock advances monotonically."""
        clock = CausalClock()

        assert clock.current == 0

        t1 = clock.next()
        assert t1 == 1
        assert clock.current == 1

        t2 = clock.next()
        assert t2 == 2
        assert clock.current == 2

    def test_event_queue_ordering(self):
        """Test that events are ordered by logical time."""
        from datetime import datetime

        queue = EventQueue()

        # Add events out of order
        event2 = CausalEvent(
            event_id="evt_2",
            event_type="test",
            parameters={},
            logical_time=2,
            physical_time=datetime.now(),
            tick_number=1,
        )
        event1 = CausalEvent(
            event_id="evt_1",
            event_type="test",
            parameters={},
            logical_time=1,
            physical_time=datetime.now(),
            tick_number=1,
        )
        event3 = CausalEvent(
            event_id="evt_3",
            event_type="test",
            parameters={},
            logical_time=3,
            physical_time=datetime.now(),
            tick_number=1,
        )

        queue.enqueue(event2)
        queue.enqueue(event1)
        queue.enqueue(event3)

        # Should retrieve in logical order
        events = queue.get_events_for_tick(1)
        assert len(events) == 3
        assert events[0].logical_time == 1
        assert events[1].logical_time == 2
        assert events[2].logical_time == 3

    def test_engine_event_injection_uses_causal_clock(self):
        """Test that engine uses causal clock for events."""
        engine = AlienInvadersEngine()
        engine.init()

        # Initial logical time should be 0
        assert engine.causal_clock.current == 0

        # Inject event
        engine.inject_event("test_event", {"severity": "low"})

        # Clock should advance
        assert engine.causal_clock.current == 1

        # Event should be queued for next tick
        assert engine.event_queue.has_pending_events(1)

    def test_deterministic_replay_with_different_injection_timing(self):
        """Test that event ordering is deterministic regardless of injection timing."""
        config = SimulationConfig()
        config.validation.random_seed = 42

        # Run 1: Inject events before ticks
        engine1 = AlienInvadersEngine(config)
        engine1.init()

        engine1.inject_event("event_a", {"severity": "low"})
        engine1.inject_event("event_b", {"severity": "low"})
        engine1.tick()  # Execute both events
        engine1.tick()

        state1 = engine1.observe("global", readonly=False)
        history1 = engine1.causal_clock.get_history()

        # Run 2: Inject events between ticks
        config2 = SimulationConfig()
        config2.validation.random_seed = 42

        engine2 = AlienInvadersEngine(config2)
        engine2.init()

        engine2.inject_event("event_a", {"severity": "low"})
        engine2.tick()  # Execute first event
        engine2.inject_event("event_b", {"severity": "low"})
        engine2.tick()  # Execute second event

        state2 = engine2.observe("global", readonly=False)
        history2 = engine2.causal_clock.get_history()

        # Causal histories should match (both events have explicit logical time)
        assert len(history1) == len(history2)

        # States should be deterministic
        assert state1["population"] == state2["population"]


class TestRegistryTrustBoundary:
    """Test registry trust boundary protection."""

    def test_observe_readonly_returns_copy(self):
        """Test that readonly observe returns a deep copy."""
        engine = AlienInvadersEngine()
        engine.init()

        # Get state with readonly=True (default)
        state1 = engine.observe("global")
        original_pop = state1["population"]

        # Try to mutate
        state1["population"] = 999999

        # Get state again
        state2 = engine.observe("global")

        # Should be unchanged
        assert state2["population"] == original_pop
        assert state2["population"] != 999999

    def test_observe_readonly_false_returns_mutable(self):
        """Test that readonly=False returns mutable reference."""
        engine = AlienInvadersEngine()
        engine.init()

        # Get state with readonly=False
        state = engine.observe("global", readonly=False)

        # Should be a dict (not raising errors on modification)
        assert isinstance(state, dict)

    def test_observe_query_filters_work(self):
        """Test that query filters work correctly."""
        engine = AlienInvadersEngine()
        engine.init()

        # Test different queries
        global_state = engine.observe("global")
        assert "population" in global_state

        countries_state = engine.observe("countries")
        assert "countries" in countries_state

        aliens_state = engine.observe("aliens")
        assert "ships" in aliens_state

        # All should return copies by default
        assert isinstance(global_state, dict)
        assert isinstance(countries_state, dict)
        assert isinstance(aliens_state, dict)


class TestIntegration:
    """Integration tests for red team hardening."""

    def test_full_simulation_with_hardening(self):
        """Test full simulation with all hardening features enabled."""
        config = SimulationConfig()
        config.validation.random_seed = 42
        config.validation.enable_strict_validation = True

        engine = AlienInvadersEngine(config)
        assert engine.init()

        # Run simulation with events
        for month in range(12):
            if month % 3 == 0:
                engine.inject_event(
                    "alien_attack",
                    {
                        "target_country": "USA",
                        "severity": "medium",
                    },
                )

            assert engine.tick()

        # Should have causal history
        history = engine.causal_clock.get_history()
        assert len(history) > 0

        # Should have executed events
        assert engine.event_queue.get_executed_count() > 0

        # Should have validation history
        assert len(engine.validation_history) > 0

        # State should be observable
        state = engine.observe()
        assert "global" in state

    def test_event_execution_at_tick_boundaries(self):
        """Test that events execute at tick boundaries only."""
        engine = AlienInvadersEngine()
        engine.init()

        # Current tick is 0
        assert engine.current_tick == 0

        # Inject event
        engine.inject_event("test_event", {"severity": "low"})

        # Event should be queued for tick 1
        assert engine.event_queue.has_pending_events(1)
        assert not engine.event_queue.has_pending_events(0)

        # First tick should execute the event
        engine.tick()
        assert engine.current_tick == 1

        # Event should now be executed
        assert not engine.event_queue.has_pending_events(1)
        assert engine.event_queue.get_executed_count() == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
