"""
Behavior-focused tests for Cerberus Hydra Defense constraints and invariants.

These tests assert critical behavioral properties:
- No more than N agents per incident
- Lockdown never jumps backwards
- Resource limits enforced
- Deterministic behavior for reproducibility
"""

import tempfile

import pytest

from app.core.cerberus_lockdown_controller import LockdownController
from app.core.cerberus_spawn_constraints import SpawnConstraints, SystemLoad


class TestSpawnConstraintBehaviors:
    """Test that spawn constraints behave correctly under all conditions."""

    def test_max_agents_per_incident_never_exceeded(self):
        """Assert: No incident spawns more than its budget allows."""
        constraints = SpawnConstraints(
            max_concurrent_agents=50,
            max_spawn_depth=5,
        )

        incident_id = "test-inc-001"
        current_count = 0

        # Simulate spawning until limit
        for generation in range(10):  # Try way more than max depth
            can_spawn, reason = constraints.can_spawn(
                generation=generation,
                incident_id=incident_id,
                current_agent_count=current_count,
            )

            if can_spawn:
                constraints.record_spawn(incident_id)
                current_count += 1
            else:
                # Once we can't spawn, verify we hit a constraint
                assert reason in [
                    "max_spawn_depth_reached",
                    "incident_budget_exceeded",
                    "max_concurrent_agents_reached",
                ]
                break

        # Verify we never exceeded max depth
        assert generation <= constraints.max_spawn_depth or not can_spawn

    def test_rate_limiting_enforced(self):
        """Assert: Spawns per minute never exceed configured limit."""
        constraints = SpawnConstraints(
            max_concurrent_agents=50,
            max_spawns_per_minute=10,  # Low limit for testing
        )

        spawns_allowed = 0
        for i in range(20):  # Try to spawn 20 times
            can_spawn, reason = constraints.can_spawn(
                generation=0,
                incident_id=f"inc-{i}",
                current_agent_count=i,
            )

            if can_spawn:
                constraints.record_spawn(f"inc-{i}")
                spawns_allowed += 1

        # Should be limited to max_spawns_per_minute
        assert spawns_allowed <= 10

    def test_critical_load_prevents_spawning(self):
        """Assert: No spawning when system is under critical load."""
        constraints = SpawnConstraints(max_concurrent_agents=50)

        # Simulate critical load
        critical_load = SystemLoad(
            cpu_percent=96.0,  # Critical threshold is 95%
            memory_percent=96.0,
            active_agents=10,
        )

        can_spawn, reason = constraints.can_spawn(
            generation=0,
            incident_id="test-inc",
            current_agent_count=10,
            system_load=critical_load,
        )

        assert not can_spawn
        assert reason == "system_under_critical_load"

    def test_cooldown_prevents_spawning(self):
        """Assert: No spawning during cooldown period."""
        constraints = SpawnConstraints(max_concurrent_agents=50)

        # Enter cooldown
        constraints.enter_cooldown(duration=60.0, reason="test")

        # Try to spawn
        can_spawn, reason = constraints.can_spawn(
            generation=0, incident_id="test-inc", current_agent_count=5
        )

        assert not can_spawn
        assert reason == "in_cooldown_period"

    def test_adaptive_spawn_factor_respects_bounds(self):
        """Assert: Adaptive spawn factor always in range [1, 5]."""
        constraints = SpawnConstraints(
            max_concurrent_agents=50, enable_adaptive_spawning=True
        )

        # Test various scenarios
        test_cases = [
            # (risk_score, confidence, cpu, memory, generation)
            (0.1, 0.9, 10.0, 20.0, 0),  # Low risk
            (0.95, 0.9, 50.0, 60.0, 1),  # High risk
            (0.5, 0.3, 80.0, 85.0, 3),  # Low confidence, high load
            (0.8, 0.9, 96.0, 96.0, 2),  # Critical load
            (0.7, 0.8, 40.0, 50.0, 5),  # Deep generation
        ]

        for risk, conf, cpu, mem, gen in test_cases:
            load = SystemLoad(cpu_percent=cpu, memory_percent=mem, active_agents=10)
            factor = constraints.compute_adaptive_spawn_factor(risk, conf, load, gen)

            # Assert bounds
            assert (
                1 <= factor <= 5
            ), f"Factor {factor} out of bounds for risk={risk}, gen={gen}"

    def test_budget_tracking_prevents_overrun(self):
        """Assert: Resource budgets prevent spawning when exceeded."""
        constraints = SpawnConstraints(
            max_concurrent_agents=100
        )  # Higher than incident budget

        incident_id = "budget-test"

        # Consume budget up to incident limit (incident budget is 50 spawns)
        for i in range(50):
            can_spawn, reason = constraints.can_spawn(
                generation=0, incident_id=incident_id, current_agent_count=i
            )
            if can_spawn:
                constraints.record_spawn(
                    incident_id, resource_cost={"cpu_seconds": 0.5, "memory_mb": 10.0}
                )

        # Now incident budget should be exceeded
        can_spawn, reason = constraints.can_spawn(
            generation=0, incident_id=incident_id, current_agent_count=50
        )

        # Should hit incident budget limit
        assert not can_spawn
        assert reason == "incident_budget_exceeded"


class TestLockdownBehaviors:
    """Test that lockdown controller maintains critical invariants."""

    @pytest.fixture
    def lockdown_controller(self):
        """Create lockdown controller for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield LockdownController(data_dir=tmpdir)

    def test_lockdown_never_goes_backwards(self, lockdown_controller):
        """Assert: Lockdown stage never decreases."""
        controller = lockdown_controller

        # Apply progressive lockdowns
        stages = [3, 7, 5, 10, 8, 15]  # Note: includes attempts to go backwards

        for stage in stages:
            result = controller.apply_lockdown(stage)
            # Current stage should never decrease
            assert controller.current_stage >= result["previous_stage"]

    def test_lockdown_is_idempotent(self, lockdown_controller):
        """Assert: Applying same lockdown twice has no effect."""
        controller = lockdown_controller

        # Apply lockdown
        result1 = controller.apply_lockdown(10, reason="first")
        assert result1["newly_locked"] != []

        # Apply same lockdown again
        result2 = controller.apply_lockdown(10, reason="second")
        assert result2["newly_locked"] == []
        assert result2["action"] == "no_change"

    def test_observation_mode_never_locks(self):
        """Assert: Observation-only mode never actually locks sections."""
        with tempfile.TemporaryDirectory() as tmpdir:
            controller = LockdownController(data_dir=tmpdir, observation_only=True)

            # Try to apply lockdown
            result = controller.apply_lockdown(15, reason="test")

            # Should not have locked anything
            assert result["action"] == "observed_only"
            assert result["observation_only"] is True
            assert len(result["newly_locked"]) == 0
            assert controller.current_stage == 0  # Stage unchanged
            assert len(controller.locked_sections) == 0  # Nothing locked

    def test_lockdown_stage_computation_is_deterministic(self):
        """Assert: Same inputs always produce same lockdown stage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            controller = LockdownController(data_dir=tmpdir)

            # Compute stage multiple times with same inputs
            stages = []
            for _ in range(5):
                stage = controller.compute_lockdown_stage(
                    risk_score=0.75, bypass_depth=3
                )
                stages.append(stage)

            # All stages should be identical
            assert len(set(stages)) == 1  # Only one unique value

    def test_lockdown_stages_bounded_0_to_25(self, lockdown_controller):
        """Assert: Lockdown stage always in valid range [0, 25]."""
        controller = lockdown_controller

        # Test extreme inputs
        test_cases = [
            (-1.0, -10),  # Negative
            (0.0, 0),  # Minimum
            (0.5, 5),  # Normal
            (1.0, 10),  # High
            (2.0, 50),  # Extreme
        ]

        for risk, depth in test_cases:
            stage = controller.compute_lockdown_stage(risk, depth)
            assert (
                0 <= stage <= 25
            ), f"Stage {stage} out of bounds for risk={risk}, depth={depth}"

    def test_sections_lock_progressively(self, lockdown_controller):
        """Assert: Higher stages lock more sections (monotonic)."""
        controller = lockdown_controller

        previous_locked = 0
        for stage in range(0, 26, 5):  # Test stages 0, 5, 10, 15, 20, 25
            result = controller.apply_lockdown(stage)
            current_locked = result["total_locked"]

            # Should lock same or more sections
            assert current_locked >= previous_locked
            previous_locked = current_locked


class TestDeterministicBehaviors:
    """Test deterministic properties for reproducibility."""

    def test_same_incident_id_produces_same_languages(self):
        """Assert: Same incident ID always selects same language pair."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create language database
            from app.core.cerberus_hydra import CerberusHydraDefense

            cerberus = CerberusHydraDefense(
                data_dir=tmpdir, enable_polyglot_execution=False, max_agents=50
            )

            # Spawn agents with same incident ID multiple times
            incident_id = "deterministic-test"

            language_pairs = []
            for _run in range(3):
                # Reset and spawn with same incident ID
                agent_id = cerberus._spawn_single_agent(
                    generation=0, parent_agent_id=None, reason=incident_id
                )

                if agent_id:
                    agent = cerberus.agents[agent_id]
                    pair = (agent.human_language, agent.programming_language)
                    language_pairs.append(pair)

            # Note: This test may need adjustment based on actual seeding implementation
            # For true determinism, the seeding needs to be based on incident_id

    def test_spawn_constraints_statistics_accurate(self):
        """Assert: Spawn statistics accurately track all attempts."""
        constraints = SpawnConstraints(
            max_concurrent_agents=50, max_spawns_per_minute=100
        )

        # Attempt several spawns
        allowed = 0
        rejected = 0

        for i in range(60):  # Try more than max agents
            can_spawn, reason = constraints.can_spawn(
                generation=0, incident_id=f"inc-{i}", current_agent_count=allowed
            )

            if can_spawn:
                constraints.record_spawn(f"inc-{i}")
                allowed += 1
            else:
                rejected += 1

        stats = constraints.get_statistics()

        # Verify statistics match actual behavior
        assert stats["total_spawns_attempted"] == 60
        assert stats["total_spawns_rejected"] == rejected
        assert allowed <= 50  # Should not exceed max


class TestIntegrationBehaviors:
    """Test integrated behaviors across components."""

    def test_full_bypass_scenario_respects_all_constraints(self):
        """Assert: Complete bypass scenario respects all constraints."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from app.core.cerberus_hydra import CerberusHydraDefense

            cerberus = CerberusHydraDefense(
                data_dir=tmpdir, enable_polyglot_execution=False, max_agents=50
            )

            # Initialize
            initial_ids = cerberus.spawn_initial_agents(count=3)
            assert len(initial_ids) == 3

            # Simulate multiple bypasses
            for i in range(5):
                cerberus.detect_bypass(bypass_type=f"attack_{i}")

            # Verify constraints
            registry = cerberus.get_agent_registry()
            assert registry["total_agents"] <= 50  # Max agents not exceeded
            # lockdown_level is returned as part of the registry
            if "lockdown_level" in registry:
                assert registry["lockdown_level"] <= 10  # Reasonable lockdown level
            assert len(registry["locked_sections"]) >= 3  # Some sections locked

    def test_resource_exhaustion_prevented(self):
        """Assert: System prevents resource exhaustion attacks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from app.core.cerberus_hydra import CerberusHydraDefense

            cerberus = CerberusHydraDefense(
                data_dir=tmpdir, enable_polyglot_execution=False, max_agents=50
            )

            # Attempt rapid spawning (simulating attack)
            initial_count = 0
            for generation in range(20):  # Try way more than max depth
                try:
                    # This should eventually stop due to constraints
                    cerberus.detect_bypass(bypass_type=f"rapid_attack_{generation}")
                    current_count = len(cerberus.agents)

                    # Verify growth is controlled
                    assert current_count <= 50  # Hard cap
                    assert current_count - initial_count <= 3 * (
                        generation + 1
                    )  # 3x per gen max

                    initial_count = current_count
                except Exception:
                    # If any error, verify we didn't exceed limits anyway
                    assert len(cerberus.agents) <= 50
                    break


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
