#!/usr/bin/env python3
"""
Tests for Irreversibility State Lock Enforcement System

Tests the formalization of irreversibility as enforced physics:
- Variable constraints that prevent increases
- Permanently disabled recovery events
- Lowered governance ceilings
"""

import tempfile
from datetime import datetime, timedelta

import pytest

from app.core.hydra_50_engine import (
    DisabledRecoveryEvent,
    EscalationLevel,
    GovernanceCeiling,
    Hydra50Engine,
    IrreversibilityLock,
    ScenarioStatus,
    VariableConstraint,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def temp_data_dir():
    """Create temporary data directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def engine(temp_data_dir):
    """Create engine instance"""
    return Hydra50Engine(data_dir=temp_data_dir)


@pytest.fixture
def active_scenario(engine):
    """Create and activate a scenario"""
    scenario = engine.scenarios["S01"]
    scenario.activation_time = datetime.utcnow() - timedelta(days=1000)
    scenario.status = ScenarioStatus.ESCALATING
    scenario.escalation_level = EscalationLevel.LEVEL_4_CASCADE_THRESHOLD

    # Set some baseline metrics
    scenario.metrics = {
        "verification_capacity": 0.5,
        "public_trust_score": 0.3,
        "synthetic_content_ratio": 0.8,
    }

    return scenario


# ============================================================================
# VARIABLE CONSTRAINT TESTS
# ============================================================================


class TestVariableConstraints:
    """Test variable constraint enforcement"""

    def test_constraint_creation(self):
        """Test creating variable constraints"""
        constraint = VariableConstraint(
            variable_name="verification_capacity",
            constraint_type="ceiling",
            locked_value=0.5,
            locked_at=datetime.utcnow(),
            reason="Epistemic collapse",
            can_never_increase=True,
        )

        assert constraint.variable_name == "verification_capacity"
        assert constraint.constraint_type == "ceiling"
        assert constraint.can_never_increase is True

    def test_ceiling_constraint_validation(self):
        """Test ceiling constraint validation"""
        constraint = VariableConstraint(
            variable_name="trust_score",
            constraint_type="ceiling",
            locked_value=0.5,
            locked_at=datetime.utcnow(),
            reason="Trust collapse",
        )

        # Below ceiling - should pass
        is_valid, reason = constraint.validate(0.4)
        assert is_valid is True

        # At ceiling - should pass
        is_valid, reason = constraint.validate(0.5)
        assert is_valid is True

        # Above ceiling - should fail
        is_valid, reason = constraint.validate(0.6)
        assert is_valid is False
        assert "cannot exceed ceiling" in reason.lower()

    def test_floor_constraint_validation(self):
        """Test floor constraint validation"""
        constraint = VariableConstraint(
            variable_name="crisis_level",
            constraint_type="floor",
            locked_value=0.7,
            locked_at=datetime.utcnow(),
            reason="Irreversible escalation",
        )

        # Above floor - should pass
        is_valid, reason = constraint.validate(0.8)
        assert is_valid is True

        # Below floor - should fail
        is_valid, reason = constraint.validate(0.6)
        assert is_valid is False
        assert "cannot fall below floor" in reason.lower()

    def test_can_never_increase_constraint(self):
        """Test can_never_increase constraint"""
        constraint = VariableConstraint(
            variable_name="capacity",
            constraint_type="ceiling",
            locked_value=0.5,
            locked_at=datetime.utcnow(),
            reason="Permanent degradation",
            can_never_increase=True,
        )

        # Decrease - should pass
        is_valid, reason = constraint.validate(0.4)
        assert is_valid is True

        # Stay same - should pass
        is_valid, reason = constraint.validate(0.5)
        assert is_valid is True

        # Increase - should fail
        is_valid, reason = constraint.validate(0.6)
        assert is_valid is False
        assert "can never increase" in reason.lower()

    def test_can_never_decrease_constraint(self):
        """Test can_never_decrease constraint"""
        constraint = VariableConstraint(
            variable_name="threat_level",
            constraint_type="floor",
            locked_value=0.8,
            locked_at=datetime.utcnow(),
            reason="Irreversible escalation",
            can_never_decrease=True,
        )

        # Increase - should pass
        is_valid, reason = constraint.validate(0.9)
        assert is_valid is True

        # Decrease - should fail
        is_valid, reason = constraint.validate(0.7)
        assert is_valid is False
        assert "can never decrease" in reason.lower()


# ============================================================================
# DISABLED RECOVERY EVENT TESTS
# ============================================================================


class TestDisabledRecoveryEvents:
    """Test permanently disabled recovery events"""

    def test_disabled_event_creation(self):
        """Test creating disabled recovery event"""
        event = DisabledRecoveryEvent(
            event_name="centralized_fact_checking",
            disabled_at=datetime.utcnow(),
            reason="Trust collapse",
            scenario_id="S01",
            alternative_actions=["distributed_verification"],
        )

        assert event.event_name == "centralized_fact_checking"
        assert event.reason == "Trust collapse"
        assert "distributed_verification" in event.alternative_actions

    def test_disabled_event_serialization(self):
        """Test disabled event to_dict"""
        event = DisabledRecoveryEvent(
            event_name="monetary_policy",
            disabled_at=datetime.utcnow(),
            reason="Currency collapse",
            scenario_id="S11",
            alternative_actions=["alternative_currencies"],
        )

        data = event.to_dict()
        assert "event_name" in data
        assert "disabled_at" in data
        assert "alternative_actions" in data


# ============================================================================
# GOVERNANCE CEILING TESTS
# ============================================================================


class TestGovernanceCeilings:
    """Test lowered governance legitimacy ceilings"""

    def test_governance_ceiling_creation(self):
        """Test creating governance ceiling"""
        ceiling = GovernanceCeiling(
            domain="democratic_legitimacy",
            original_ceiling=1.0,
            lowered_ceiling=0.6,
            lowered_at=datetime.utcnow(),
            reason="Legitimacy collapse",
            multiplier=0.6,
        )

        assert ceiling.domain == "democratic_legitimacy"
        assert ceiling.original_ceiling == 1.0
        assert ceiling.lowered_ceiling == 0.6

    def test_effective_ceiling_calculation(self):
        """Test effective ceiling with multiplier"""
        ceiling = GovernanceCeiling(
            domain="policy_effectiveness",
            original_ceiling=1.0,
            lowered_ceiling=0.8,
            lowered_at=datetime.utcnow(),
            reason="Institutional failure",
            multiplier=0.5,  # Additional 50% reduction
        )

        effective = ceiling.get_effective_ceiling()
        assert effective == 0.4  # 0.8 * 0.5

    def test_governance_ceiling_serialization(self):
        """Test ceiling to_dict"""
        ceiling = GovernanceCeiling(
            domain="institutional_trust",
            original_ceiling=1.0,
            lowered_ceiling=0.7,
            lowered_at=datetime.utcnow(),
            reason="Trust erosion",
            multiplier=0.7,
        )

        data = ceiling.to_dict()
        assert "domain" in data
        assert "effective_ceiling" in data
        assert abs(data["effective_ceiling"] - 0.49) < 0.001  # Floating point tolerance


# ============================================================================
# IRREVERSIBILITY LOCK TESTS
# ============================================================================


class TestIrreversibilityLock:
    """Test complete irreversibility lock"""

    def test_lock_creation(self, engine, active_scenario):
        """Test creating a state lock"""
        # Trigger irreversibility
        elapsed = datetime.utcnow() - active_scenario.activation_time
        assessment = engine.irreversibility_detector.assess_irreversibility(active_scenario, elapsed)

        # Create lock
        lock = engine.irreversibility_detector.create_state_lock(
            scenario=active_scenario,
            irreversibility_score=assessment["score"],
            triggered_collapses=assessment.get("triggered_collapses", []),
        )

        assert lock is not None
        assert lock.scenario_id == active_scenario.scenario_id
        # Locks always have governance ceilings
        assert len(lock.governance_ceilings) > 0
        # May or may not have variable constraints depending on collapse modes
        # May or may not have disabled events depending on recovery poisons

    def test_lock_enforced_on_scenario(self, engine, active_scenario):
        """Test that lock is added to scenario"""
        elapsed = datetime.utcnow() - active_scenario.activation_time
        assessment = engine.irreversibility_detector.assess_irreversibility(active_scenario, elapsed)

        lock = engine.irreversibility_detector.create_state_lock(
            scenario=active_scenario,
            irreversibility_score=assessment["score"],
            triggered_collapses=assessment.get("triggered_collapses", []),
        )

        assert lock in active_scenario.active_locks

    def test_lock_serialization(self, engine, active_scenario):
        """Test lock to_dict"""
        elapsed = datetime.utcnow() - active_scenario.activation_time
        assessment = engine.irreversibility_detector.assess_irreversibility(active_scenario, elapsed)

        lock = engine.irreversibility_detector.create_state_lock(
            scenario=active_scenario,
            irreversibility_score=assessment["score"],
            triggered_collapses=assessment.get("triggered_collapses", []),
        )

        data = lock.to_dict()
        assert "lock_id" in data
        assert "scenario_id" in data
        assert "variable_constraints" in data
        assert "disabled_recovery_events" in data
        assert "governance_ceilings" in data


# ============================================================================
# METRIC UPDATE ENFORCEMENT TESTS
# ============================================================================


class TestMetricUpdateEnforcement:
    """Test that metric updates are blocked by constraints"""

    def test_metric_update_passes_without_locks(self, engine):
        """Test normal metric updates work without locks"""
        scenario = engine.scenarios["S01"]

        # Should succeed
        scenario.update_metrics({"verification_capacity": 0.8})
        assert scenario.metrics["verification_capacity"] == 0.8

    def test_metric_update_blocked_by_ceiling(self, engine, active_scenario):
        """Test metric update blocked by ceiling constraint"""
        # Create lock with constraint
        constraint = VariableConstraint(
            variable_name="verification_capacity",
            constraint_type="ceiling",
            locked_value=0.5,
            locked_at=datetime.utcnow(),
            reason="Epistemic collapse",
            can_never_increase=True,
        )

        lock = IrreversibilityLock(
            lock_id="TEST_LOCK",
            scenario_id=active_scenario.scenario_id,
            locked_at=datetime.utcnow(),
            irreversibility_score=0.8,
            variable_constraints=[constraint],
        )

        active_scenario.active_locks.append(lock)

        # Try to update above ceiling - should fail
        with pytest.raises(ValueError) as exc_info:
            active_scenario.update_metrics({"verification_capacity": 0.8})

        assert "constraint violated" in str(exc_info.value).lower()

    def test_metric_update_allowed_within_ceiling(self, engine, active_scenario):
        """Test metric update allowed within ceiling"""
        constraint = VariableConstraint(
            variable_name="verification_capacity",
            constraint_type="ceiling",
            locked_value=0.5,
            locked_at=datetime.utcnow(),
            reason="Epistemic collapse",
        )

        lock = IrreversibilityLock(
            lock_id="TEST_LOCK",
            scenario_id=active_scenario.scenario_id,
            locked_at=datetime.utcnow(),
            irreversibility_score=0.8,
            variable_constraints=[constraint],
        )

        active_scenario.active_locks.append(lock)

        # Update within ceiling - should succeed
        active_scenario.update_metrics({"verification_capacity": 0.4})
        assert active_scenario.metrics["verification_capacity"] == 0.4


# ============================================================================
# RECOVERY EVENT ENFORCEMENT TESTS
# ============================================================================


class TestRecoveryEventEnforcement:
    """Test that recovery events are blocked when disabled"""

    def test_recovery_allowed_without_locks(self, engine, active_scenario):
        """Test recovery events allowed without locks"""
        is_allowed, reason = active_scenario.check_recovery_event_allowed("centralized_fact_checking")
        assert is_allowed is True

    def test_recovery_blocked_when_disabled(self, engine, active_scenario):
        """Test recovery event blocked when disabled"""
        disabled_event = DisabledRecoveryEvent(
            event_name="centralized_fact_checking",
            disabled_at=datetime.utcnow(),
            reason="Trust collapse: centralized authorities no longer credible",
            scenario_id=active_scenario.scenario_id,
            alternative_actions=["distributed_verification"],
        )

        lock = IrreversibilityLock(
            lock_id="TEST_LOCK",
            scenario_id=active_scenario.scenario_id,
            locked_at=datetime.utcnow(),
            irreversibility_score=0.9,
            disabled_recovery_events=[disabled_event],
        )

        active_scenario.active_locks.append(lock)

        # Check if event is allowed
        is_allowed, reason = active_scenario.check_recovery_event_allowed("centralized_fact_checking")

        assert is_allowed is False
        assert "permanently disabled" in reason.lower()

    def test_engine_recovery_attempt_blocked(self, engine, active_scenario):
        """Test engine-level recovery attempt blocking"""
        disabled_event = DisabledRecoveryEvent(
            event_name="monetary_policy",
            disabled_at=datetime.utcnow(),
            reason="Currency confidence destroyed",
            scenario_id=active_scenario.scenario_id,
        )

        lock = IrreversibilityLock(
            lock_id="TEST_LOCK",
            scenario_id=active_scenario.scenario_id,
            locked_at=datetime.utcnow(),
            irreversibility_score=0.9,
            disabled_recovery_events=[disabled_event],
        )

        active_scenario.active_locks.append(lock)

        # Attempt recovery through engine
        result = engine.attempt_recovery_action(
            scenario_id=active_scenario.scenario_id,
            recovery_action="monetary_policy_intervention",
            user_id="test_user",
        )

        assert result["success"] is False
        assert result["blocked"] is True


# ============================================================================
# GOVERNANCE CEILING ENFORCEMENT TESTS
# ============================================================================


class TestGovernanceCeilingEnforcement:
    """Test governance ceiling retrieval and enforcement"""

    def test_no_ceiling_without_locks(self, engine, active_scenario):
        """Test no ceiling returned without locks"""
        ceiling = active_scenario.get_governance_ceiling("democratic_legitimacy")
        assert ceiling is None

    def test_ceiling_returned_with_lock(self, engine, active_scenario):
        """Test ceiling returned when lock active"""
        gov_ceiling = GovernanceCeiling(
            domain="democratic_legitimacy",
            original_ceiling=1.0,
            lowered_ceiling=0.6,
            lowered_at=datetime.utcnow(),
            reason="Legitimacy collapse",
            multiplier=0.6,
        )

        lock = IrreversibilityLock(
            lock_id="TEST_LOCK",
            scenario_id=active_scenario.scenario_id,
            locked_at=datetime.utcnow(),
            irreversibility_score=0.9,
            governance_ceilings=[gov_ceiling],
        )

        active_scenario.active_locks.append(lock)

        ceiling = active_scenario.get_governance_ceiling("democratic_legitimacy")
        assert ceiling is not None
        assert ceiling == 0.36  # 0.6 * 0.6

    def test_lowest_ceiling_returned_with_multiple_locks(self, engine, active_scenario):
        """Test that lowest ceiling is returned with multiple locks"""
        ceiling1 = GovernanceCeiling(
            domain="institutional_trust",
            original_ceiling=1.0,
            lowered_ceiling=0.7,
            lowered_at=datetime.utcnow(),
            reason="First collapse",
            multiplier=1.0,
        )

        ceiling2 = GovernanceCeiling(
            domain="institutional_trust",
            original_ceiling=1.0,
            lowered_ceiling=0.5,
            lowered_at=datetime.utcnow(),
            reason="Second collapse",
            multiplier=1.0,
        )

        lock1 = IrreversibilityLock(
            lock_id="LOCK1",
            scenario_id=active_scenario.scenario_id,
            locked_at=datetime.utcnow(),
            irreversibility_score=0.8,
            governance_ceilings=[ceiling1],
        )

        lock2 = IrreversibilityLock(
            lock_id="LOCK2",
            scenario_id=active_scenario.scenario_id,
            locked_at=datetime.utcnow(),
            irreversibility_score=0.9,
            governance_ceilings=[ceiling2],
        )

        active_scenario.active_locks.extend([lock1, lock2])

        ceiling = active_scenario.get_governance_ceiling("institutional_trust")
        assert ceiling == 0.5  # Lowest of 0.7 and 0.5


# ============================================================================
# ENGINE INTEGRATION TESTS
# ============================================================================


class TestEngineIntegration:
    """Test end-to-end engine integration with locks"""

    def test_lock_created_on_tick_when_irreversible(self, engine):
        """Test that lock is automatically created during tick"""
        scenario = engine.scenarios["S01"]
        scenario.activation_time = datetime.utcnow() - timedelta(days=1000)
        scenario.status = ScenarioStatus.ESCALATING
        scenario.escalation_level = EscalationLevel.LEVEL_4_CASCADE_THRESHOLD

        # Run tick - should detect irreversibility and create lock
        result = engine.run_tick()

        # Check if lock was created
        if "S01" in result["irreversible_scenarios"]:
            assert len(result["new_state_locks"]) > 0
            assert any(lock["scenario_id"] == "S01" for lock in result["new_state_locks"])

    def test_dashboard_shows_lock_count(self, engine, active_scenario):
        """Test dashboard includes lock information"""
        # Create lock
        lock = IrreversibilityLock(
            lock_id="TEST_LOCK",
            scenario_id=active_scenario.scenario_id,
            locked_at=datetime.utcnow(),
            irreversibility_score=0.9,
        )
        active_scenario.active_locks.append(lock)
        engine.irreversibility_detector.active_locks["TEST_LOCK"] = lock

        dashboard = engine.get_dashboard_state()

        assert "locked_count" in dashboard
        assert "active_state_locks" in dashboard

    def test_get_state_lock_summary(self, engine, active_scenario):
        """Test getting lock summary"""
        lock = IrreversibilityLock(
            lock_id="TEST_LOCK",
            scenario_id=active_scenario.scenario_id,
            locked_at=datetime.utcnow(),
            irreversibility_score=0.9,
            variable_constraints=[
                VariableConstraint(
                    variable_name="test_var",
                    constraint_type="ceiling",
                    locked_value=0.5,
                    locked_at=datetime.utcnow(),
                    reason="Test",
                )
            ],
        )

        active_scenario.active_locks.append(lock)
        engine.irreversibility_detector.active_locks["TEST_LOCK"] = lock

        summary = engine.get_state_lock_summary()

        assert summary["total_locks"] == 1
        assert summary["total_variable_constraints"] == 1
        assert len(summary["locks"]) == 1

    def test_state_snapshot_includes_locks(self, engine, active_scenario):
        """Test state snapshot includes lock IDs"""
        lock = IrreversibilityLock(
            lock_id="TEST_LOCK",
            scenario_id=active_scenario.scenario_id,
            locked_at=datetime.utcnow(),
            irreversibility_score=0.9,
        )

        active_scenario.active_locks.append(lock)

        state = active_scenario.capture_state()

        assert "TEST_LOCK" in state.active_locks
        assert len(state.active_locks) == 1


# ============================================================================
# CATEGORY-SPECIFIC CONSTRAINT TESTS
# ============================================================================


class TestCategorySpecificConstraints:
    """Test that different scenario categories generate appropriate constraints"""

    def test_digital_cognitive_constraints(self, engine):
        """Test digital/cognitive scenarios get appropriate constraints"""
        scenario = engine.scenarios["S01"]  # AI Reality Flood
        scenario.activation_time = datetime.utcnow() - timedelta(days=1000)
        scenario.metrics = {
            "verification_capacity": 0.5,
            "public_trust_score": 0.3,
        }

        lock = engine.irreversibility_detector.create_state_lock(
            scenario=scenario,
            irreversibility_score=0.9,
            triggered_collapses=["epistemic_collapse", "trust_collapse"],
        )

        # Should have verification and trust constraints
        var_names = [c.variable_name for c in lock.variable_constraints]
        assert "verification_capacity" in var_names or "public_trust_score" in var_names

    def test_economic_constraints(self, engine):
        """Test economic scenarios get appropriate constraints"""
        scenario = engine.scenarios["S11"]  # Sovereign Debt Cascade
        scenario.activation_time = datetime.utcnow() - timedelta(days=1000)
        scenario.metrics = {
            "currency_confidence": 0.4,
            "market_liquidity": 0.5,
        }

        lock = engine.irreversibility_detector.create_state_lock(
            scenario=scenario,
            irreversibility_score=0.9,
            triggered_collapses=["currency_collapse", "liquidity_crisis"],
        )

        # Should have economic constraints
        var_names = [c.variable_name for c in lock.variable_constraints]
        assert "currency_confidence" in var_names or "market_liquidity" in var_names

        # Should have fiscal capacity ceiling
        gov_domains = [c.domain for c in lock.governance_ceilings]
        assert "fiscal_capacity" in gov_domains

    def test_infrastructure_constraints(self, engine):
        """Test infrastructure scenarios get appropriate constraints"""
        scenario = engine.scenarios["S21"]  # Power Grid Warfare
        scenario.activation_time = datetime.utcnow() - timedelta(days=1000)
        scenario.metrics = {
            "infrastructure_capacity": 0.6,
        }

        lock = engine.irreversibility_detector.create_state_lock(
            scenario=scenario,
            irreversibility_score=0.9,
            triggered_collapses=["cascade_failure", "grid_collapse"],
        )

        # Should have infrastructure constraint
        var_names = [c.variable_name for c in lock.variable_constraints]
        assert "infrastructure_capacity" in var_names

    def test_biological_environmental_constraints(self, engine):
        """Test biological/environmental scenarios get appropriate constraints"""
        scenario = engine.scenarios["S31"]  # Slow Burn Pandemic
        scenario.activation_time = datetime.utcnow() - timedelta(days=1000)
        scenario.metrics = {
            "ecosystem_health": 0.4,
            "resource_regeneration_rate": 0.3,
        }

        lock = engine.irreversibility_detector.create_state_lock(
            scenario=scenario,
            irreversibility_score=0.9,
            triggered_collapses=["ecosystem_collapse", "species_extinction"],
        )

        # Should have ecological constraints
        var_names = [c.variable_name for c in lock.variable_constraints]
        assert "ecosystem_health" in var_names or "resource_regeneration_rate" in var_names

    def test_societal_constraints(self, engine):
        """Test societal scenarios get appropriate constraints and ceilings"""
        scenario = engine.scenarios["S41"]  # Legitimacy Collapse
        scenario.activation_time = datetime.utcnow() - timedelta(days=1000)
        scenario.metrics = {
            "social_cohesion": 0.3,
        }

        lock = engine.irreversibility_detector.create_state_lock(
            scenario=scenario,
            irreversibility_score=0.9,
            triggered_collapses=["legitimacy_collapse", "social_fracture"],
        )

        # Should have social cohesion constraint
        var_names = [c.variable_name for c in lock.variable_constraints]
        assert "social_cohesion" in var_names

        # Should have social mandate ceiling
        gov_domains = [c.domain for c in lock.governance_ceilings]
        assert "social_mandate" in gov_domains


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
