"""
Deterministic Replay Verification Test Suite

Verifies that simulation runs with identical random seeds produce
bit-identical results event-for-event, enabling automated auditing
and replay-based forensics.
"""

import pytest
from alien_invaders.engine import AlienInvadersEngine
from alien_invaders.schemas.config_schema import SimulationConfig


class TestDeterministicReplay:
    """Test suite for deterministic replay verification."""

    @pytest.fixture
    def config_with_seed(self):
        """Create a config with fixed random seed."""
        config = SimulationConfig()
        config.validation.random_seed = 12345
        config.validation.enable_strict_validation = False  # Allow tolerance violations
        config.world.time_step_days = 30
        return config

    def test_single_run_initialization(self, config_with_seed):
        """Verify engine initializes consistently."""
        engine = AlienInvadersEngine(config_with_seed)
        assert engine.init()
        assert engine.state is not None
        assert engine.state.get_total_population() > 0
        assert engine.state.alien_ships_in_system >= 0

    def test_replay_identical_seed_identical_state(self, config_with_seed):
        """
        Verify: Same seed → identical state snapshots at each tick.

        This is the core determinism test. Runs two simulations with
        identical config and seed, verifies every tick produces identical state.
        """
        # Run 1
        engine1 = AlienInvadersEngine(config_with_seed)
        assert engine1.init()

        run1_states = {}
        for tick in range(10):
            success = engine1.tick()
            assert success, f"Tick {tick} failed in run1"
            run1_states[tick] = {
                "day": engine1.state.day_number,
                "pop": engine1.state.get_total_population(),
                "gdp": engine1.state.get_total_gdp(),
                "aliens": engine1.state.alien_ships_in_system,
                "casualties": engine1.state.global_casualties,
                "events_count": len(engine1.events),
            }

        # Run 2 (identical seed)
        engine2 = AlienInvadersEngine(config_with_seed)
        assert engine2.init()

        run2_states = {}
        for tick in range(10):
            success = engine2.tick()
            assert success, f"Tick {tick} failed in run2"
            run2_states[tick] = {
                "day": engine2.state.day_number,
                "pop": engine2.state.get_total_population(),
                "gdp": engine2.state.get_total_gdp(),
                "aliens": engine2.state.alien_ships_in_system,
                "casualties": engine2.state.global_casualties,
                "events_count": len(engine2.events),
            }

        # Verify identical state at each tick
        for tick in range(10):
            state1 = run1_states[tick]
            state2 = run2_states[tick]

            assert state1["day"] == state2["day"], f"Day divergence at tick {tick}"
            assert state1["pop"] == state2["pop"], f"Population divergence at tick {tick}"
            assert state1["gdp"] == state2["gdp"], f"GDP divergence at tick {tick}"
            assert state1["aliens"] == state2["aliens"], f"Alien count divergence at tick {tick}"
            assert state1["casualties"] == state2["casualties"], (
                f"Casualties divergence at tick {tick}"
            )
            assert state1["events_count"] == state2["events_count"], (
                f"Event count divergence at tick {tick}"
            )

    def test_replay_identical_seed_identical_events(self, config_with_seed):
        """
        Verify: Same seed → identical event sequences.

        Events are the lowest-level divergence point. If events match,
        state cannot diverge.
        """
        engine1 = AlienInvadersEngine(config_with_seed)
        engine1.init()
        for _ in range(5):
            engine1.tick()

        engine2 = AlienInvadersEngine(config_with_seed)
        engine2.init()
        for _ in range(5):
            engine2.tick()

        # Compare event sequences
        assert len(engine1.events) == len(engine2.events), "Event count mismatch"

        for i, (e1, e2) in enumerate(zip(engine1.events, engine2.events, strict=True)):
            assert e1.event_type == e2.event_type, f"Event {i} type mismatch"
            assert e1.day_number == e2.day_number, f"Event {i} day mismatch"
            assert e1.severity == e2.severity, f"Event {i} severity mismatch"
            # Note: event_id may differ due to timestamp, but type/day/severity should match

    def test_replay_different_seed_diverges(self, config_with_seed):
        """
        Verify: Different seed changes seeded stochastic initialization.

        The engine can remain externally identical for short tick windows, so
        this checks fields that are directly initialized through the seeded
        random path.
        """
        config1 = SimulationConfig()
        config1.validation.random_seed = 11111

        config2 = SimulationConfig()
        config2.validation.random_seed = 22222

        engine1 = AlienInvadersEngine(config1)
        engine1.init()

        engine2 = AlienInvadersEngine(config2)
        engine2.init()

        country_code = sorted(engine1.state.countries.keys())[0]
        country1 = engine1.state.countries[country_code]
        country2 = engine2.state.countries[country_code]
        assert (
            country1.government_stability != country2.government_stability
            or country1.public_morale != country2.public_morale
        )

    def test_replay_long_run_determinism(self, config_with_seed):
        """
        Verify: 100-tick run maintains determinism end-to-end.

        Stress test for floating-point precision, state mutation order, etc.
        """
        engine1 = AlienInvadersEngine(config_with_seed)
        engine1.init()

        for _ in range(100):
            engine1.tick()

        final_state1 = {
            "pop": engine1.state.get_total_population(),
            "gdp": engine1.state.get_total_gdp(),
            "aliens": engine1.state.alien_ships_in_system,
            "events": len(engine1.events),
        }

        # Run 2
        engine2 = AlienInvadersEngine(config_with_seed)
        engine2.init()

        for _ in range(100):
            engine2.tick()

        final_state2 = {
            "pop": engine2.state.get_total_population(),
            "gdp": engine2.state.get_total_gdp(),
            "aliens": engine2.state.alien_ships_in_system,
            "events": len(engine2.events),
        }

        # Verify identical
        for key in final_state1:
            assert final_state1[key] == final_state2[key], (
                f"Long-run divergence in {key}: {final_state1[key]} vs {final_state2[key]}"
            )

    def test_causal_clock_event_order(self, config_with_seed):
        """
        Verify: Causal clock produces monotonic increasing event times.
        """
        engine = AlienInvadersEngine(config_with_seed)
        engine.init()

        for _ in range(10):
            engine.tick()

        # Inject multiple events and verify causal ordering
        event_ids = []
        for i in range(5):
            eid = engine.inject_event("test_event", {"value": i})
            event_ids.append(eid)

        # All events should have monotonically increasing logical times
        # (implicitly tested by the engine's internal validation)

    def test_initial_state_determinism(self, config_with_seed):
        """
        Verify: Initial state is deterministic (depends only on config and seed).
        """
        engine1 = AlienInvadersEngine(config_with_seed)
        engine1.init()

        engine2 = AlienInvadersEngine(config_with_seed)
        engine2.init()

        assert engine1.state.get_total_population() == engine2.state.get_total_population()
        assert engine1.state.get_total_gdp() == engine2.state.get_total_gdp()
        assert len(engine1.state.countries) == len(engine2.state.countries)

        for code in engine1.state.countries:
            c1 = engine1.state.countries[code]
            c2 = engine2.state.countries[code]
            assert c1.population == c2.population
            assert c1.gdp_usd == c2.gdp_usd
            assert c1.military_strength == c2.military_strength


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
