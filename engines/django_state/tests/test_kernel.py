"""Tests for kernel modules.

Tests all kernel components: state vector, reality clock, irreversibility laws,
and collapse scheduler.
"""

from ..kernel.collapse_scheduler import CollapseScheduler
from ..kernel.irreversibility_laws import IrreversibilityLaws
from ..kernel.reality_clock import RealityClock
from ..schemas.config_schema import IrreversibilityConfig
from ..schemas.state_schema import StateDimension, StateVector


class TestStateDimension:
    """Test StateDimension class."""

    def test_dimension_creation(self):
        """Test creating dimension with bounds."""
        dim = StateDimension(value=0.5, min_value=0.0, max_value=1.0)
        assert dim.value == 0.5
        assert dim.min_value == 0.0
        assert dim.max_value == 1.0

    def test_dimension_bounds_enforcement(self):
        """Test that bounds are enforced."""
        dim = StateDimension(value=1.5, min_value=0.0, max_value=1.0)
        assert dim.value == 1.0  # Clamped to max

    def test_dimension_update(self):
        """Test updating dimension value."""
        dim = StateDimension(value=0.5, min_value=0.0, max_value=1.0)
        change = dim.update(delta=0.2, timestamp=1.0)
        assert dim.value == 0.7
        assert change == 0.2

    def test_ceiling_enforcement(self):
        """Test that ceiling is enforced."""
        dim = StateDimension(value=0.5, min_value=0.0, max_value=1.0)
        dim.impose_ceiling(0.6)
        dim.update(delta=0.3, timestamp=1.0)
        assert dim.value <= 0.6

    def test_floor_enforcement(self):
        """Test that floor is enforced."""
        dim = StateDimension(value=0.5, min_value=0.0, max_value=1.0)
        dim.impose_floor(0.4)
        dim.update(delta=-0.3, timestamp=1.0)
        assert dim.value >= 0.4


class TestStateVector:
    """Test StateVector class."""

    def test_initial_state_creation(self):
        """Test creating initial state."""
        state = StateVector.create_initial_state()
        assert 0.0 <= state.trust.value <= 1.0
        assert 0.0 <= state.legitimacy.value <= 1.0
        assert 0.0 <= state.kindness.value <= 1.0
        assert 0.0 <= state.moral_injury.value <= 1.0

    def test_derived_state_update(self):
        """Test updating derived state metrics."""
        state = StateVector.create_initial_state()
        state.trust.value = 0.8
        state.kindness.value = 0.7
        state.update_derived_state()
        assert 0.0 <= state.social_cohesion <= 1.0
        assert 0.0 <= state.governance_capacity <= 1.0

    def test_collapse_condition_check(self):
        """Test checking collapse conditions."""
        state = StateVector.create_initial_state()
        state.kindness.value = 0.1  # Below threshold
        thresholds = {
            "kindness_singularity": 0.2,
            "trust_collapse": 0.15,
            "moral_injury_critical": 0.85,
            "legitimacy_failure": 0.1,
            "epistemic_collapse": 0.2,
        }
        collapsed, reason = state.check_collapse_conditions(thresholds)
        assert collapsed
        assert reason == "kindness_singularity"

    def test_outcome_classification(self):
        """Test outcome classification."""
        state = StateVector.create_initial_state()
        state.trust.value = 0.4
        state.legitimacy.value = 0.3
        state.moral_injury.value = 0.5
        thresholds = {
            "survivor_trust": 0.3,
            "survivor_legitimacy": 0.25,
            "martyr_kindness": 0.3,
            "martyr_moral": 0.6,
        }
        outcome = state.classify_outcome(thresholds)
        assert outcome in ["survivor", "martyr", "extinction"]

    def test_state_copy(self):
        """Test state copying."""
        state = StateVector.create_initial_state()
        state.trust.value = 0.6
        state_copy = state.copy()
        assert state_copy.trust.value == 0.6
        state_copy.trust.value = 0.5
        assert state.trust.value == 0.6  # Original unchanged


class TestRealityClock:
    """Test RealityClock class."""

    def test_clock_initialization(self):
        """Test clock initialization."""
        clock = RealityClock(start_time=0.0, time_step=1.0)
        assert clock.current_time == 0.0
        assert clock.tick_count == 0

    def test_clock_tick(self):
        """Test advancing clock."""
        clock = RealityClock(start_time=0.0, time_step=1.0)
        new_time = clock.tick()
        assert new_time == 1.0
        assert clock.tick_count == 1

    def test_event_recording(self):
        """Test recording events in causal chain."""
        clock = RealityClock()
        event = clock.record_event("event_1", state_hash="hash1")
        assert event.event_id == "event_1"
        assert event.causal_order == 0
        assert "event_1" in clock.event_index

    def test_causal_chain_verification(self):
        """Test verifying causal chain integrity."""
        clock = RealityClock()
        clock.record_event("event_1", state_hash="hash1")
        clock.record_event("event_2", parent_events=["event_1"], state_hash="hash2")
        is_valid, error = clock.verify_causal_consistency()
        assert is_valid


class TestIrreversibilityLaws:
    """Test IrreversibilityLaws class."""

    def test_trust_decay(self):
        """Test trust decay law."""
        config = IrreversibilityConfig()
        laws = IrreversibilityLaws(config)
        state = StateVector.create_initial_state()
        initial_trust = state.trust.value
        laws.apply_trust_decay_law(state)
        assert state.trust.value < initial_trust

    def test_betrayal_impact(self):
        """Test betrayal impact with ceiling."""
        config = IrreversibilityConfig()
        laws = IrreversibilityLaws(config)
        state = StateVector.create_initial_state()
        initial_trust = state.trust.value
        result = laws.apply_betrayal_impact(state, severity=0.5)
        assert state.trust.value < initial_trust
        assert state.trust.ceiling is not None
        assert result["betrayal_count"] > 0

    def test_kindness_singularity(self):
        """Test kindness singularity detection."""
        config = IrreversibilityConfig()
        laws = IrreversibilityLaws(config)
        state = StateVector.create_initial_state()
        state.kindness.value = 0.1
        crossed, reason = laws.check_kindness_singularity(state)
        assert crossed
        assert reason == "kindness_singularity"

    def test_moral_injury_accumulation(self):
        """Test moral injury accumulation."""
        config = IrreversibilityConfig()
        laws = IrreversibilityLaws(config)
        state = StateVector.create_initial_state()
        initial_moral = state.moral_injury.value
        result = laws.accumulate_moral_injury(state, violation_severity=0.5)
        assert state.moral_injury.value > initial_moral
        assert result["moral_injury_change"] > 0

    def test_legitimacy_erosion(self):
        """Test legitimacy erosion."""
        config = IrreversibilityConfig()
        laws = IrreversibilityLaws(config)
        state = StateVector.create_initial_state()
        initial_legitimacy = state.legitimacy.value
        laws.apply_legitimacy_erosion(state, broken_promises=1, failures=1, visibility=0.5)
        assert state.legitimacy.value < initial_legitimacy

    def test_betrayal_probability(self):
        """Test betrayal probability calculation."""
        config = IrreversibilityConfig()
        laws = IrreversibilityLaws(config)
        state = StateVector.create_initial_state()
        state.trust.value = 0.2
        state.legitimacy.value = 0.2
        prob = laws.calculate_betrayal_probability(state)
        assert 0.0 <= prob <= 1.0
        assert prob > 0.1  # Should be elevated

    def test_manipulation_impact(self):
        """Test information manipulation impact."""
        config = IrreversibilityConfig()
        laws = IrreversibilityLaws(config)
        state = StateVector.create_initial_state()
        initial_epistemic = state.epistemic_confidence.value
        laws.apply_manipulation_impact(state, reach=0.5, sophistication=0.5)
        assert state.epistemic_confidence.value < initial_epistemic


class TestCollapseScheduler:
    """Test CollapseScheduler class."""

    def test_scheduler_initialization(self):
        """Test scheduler initialization."""
        scheduler = CollapseScheduler()
        assert len(scheduler.scheduled_collapses) == 0
        assert len(scheduler.triggered_collapses) == 0

    def test_schedule_collapse(self):
        """Test scheduling collapse event."""
        scheduler = CollapseScheduler()
        collapse = scheduler.schedule_collapse(
            trigger_time=10.0,
            collapse_type="test_collapse",
            severity=0.5,
        )
        assert collapse.trigger_time == 10.0
        assert not collapse.triggered

    def test_threshold_checking(self):
        """Test automatic threshold checking."""
        scheduler = CollapseScheduler()
        state = StateVector.create_initial_state()
        state.kindness.value = 0.1  # Below threshold
        triggered = scheduler.check_thresholds(state)
        assert "kindness_singularity" in triggered

    def test_process_tick(self):
        """Test processing scheduler on tick."""
        scheduler = CollapseScheduler()
        scheduler.schedule_collapse(5.0, "test", 0.5)
        state = StateVector.create_initial_state()
        state.timestamp = 5.0
        triggered = scheduler.process_tick(state)
        assert len(triggered) > 0
