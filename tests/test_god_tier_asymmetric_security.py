"""
Tests for God Tier Asymmetric Security

Tests the strategic concepts and integration.
"""

import pytest
import time
from app.core.god_tier_asymmetric_security import (
    GodTierAsymmetricSecurity,
    StateMachineAnalyzer,
    SystemState,
    TemporalSecurityAnalyzer,
    InvertedKillChainEngine,
    EntropicArchitecture,
    ReuseFrictionIndexCalculator,
    SecurityLayer,
    ThreatLevel,
)


class TestStateMachineAnalyzer:
    """Test state machine analysis for cognitive blind spots."""

    def test_state_registration(self, tmp_path):
        """Test registering system states."""
        analyzer = StateMachineAnalyzer(str(tmp_path))
        
        initial_count = len(analyzer.states)
        
        analyzer.register_state(
            SystemState(
                state_id="test_state",
                properties={"test": True},
                is_legal=True,
                transitions_to=["another_state"],
                invariants=["test_invariant"],
            )
        )
        
        assert len(analyzer.states) == initial_count + 1
        assert "test_state" in analyzer.states

    def test_legal_transition(self, tmp_path):
        """Test legal state transitions."""
        analyzer = StateMachineAnalyzer(str(tmp_path))
        
        # Test transition from unauthenticated to authenticated
        is_legal, reason = analyzer.check_transition(
            component="auth_system",
            from_state="unauthenticated",
            to_state="authenticated",
            context={"session_token": "valid"},
        )
        
        assert is_legal is True
        assert "Legal transition" in reason

    def test_illegal_transition_detection(self, tmp_path):
        """Test detection of illegal state transitions."""
        analyzer = StateMachineAnalyzer(str(tmp_path))
        
        # Try to transition from unauthenticated to elevated (illegal)
        is_legal, reason = analyzer.check_transition(
            component="auth_system",
            from_state="unauthenticated",
            to_state="elevated_without_mfa",
            context={},
        )
        
        assert is_legal is False
        assert "Illegal transition" in reason
        assert len(analyzer.illegal_transitions) > 0

    def test_find_illegal_reachable_states(self, tmp_path):
        """Test finding illegal but reachable states."""
        analyzer = StateMachineAnalyzer(str(tmp_path))
        
        illegal_reachable = analyzer.find_illegal_reachable_states()
        
        # Should find at least one: elevated_without_mfa
        assert len(illegal_reachable) > 0
        assert any(state.state_id == "elevated_without_mfa" for state in illegal_reachable)


class TestTemporalSecurityAnalyzer:
    """Test temporal attack detection."""

    def test_event_recording(self, tmp_path):
        """Test recording events with timestamps."""
        analyzer = TemporalSecurityAnalyzer(str(tmp_path))
        
        analyzer.record_event("test_component", "event1", {"data": "value1"})
        analyzer.record_event("test_component", "event2", {"data": "value2"})
        
        assert "test_component" in analyzer.timeline_snapshots
        assert len(analyzer.timeline_snapshots["test_component"]) == 2

    def test_race_condition_detection(self, tmp_path):
        """Test detection of race conditions."""
        analyzer = TemporalSecurityAnalyzer(str(tmp_path))
        
        component = "critical_component"
        
        # Simulate two state mutations in quick succession
        analyzer.record_event(component, "mutate_state_a", {"value": "a"})
        time.sleep(0.01)  # 10ms delay (within 100ms window)
        analyzer.record_event(component, "mutate_state_b", {"value": "b"})
        
        violation = analyzer.detect_race_condition(component, window_ms=100.0)
        
        # Should detect race condition
        assert violation is not None
        assert violation.violation_type == "race"
        assert violation.threat_level == ThreatLevel.HIGH


class TestInvertedKillChainEngine:
    """Test inverted kill chain (Detect→Predict→Preempt→Poison)."""

    def test_precondition_detection(self, tmp_path):
        """Test detecting attack preconditions."""
        engine = InvertedKillChainEngine(str(tmp_path))
        
        context = {
            "mfa_enabled": False,  # Weak session precondition
        }
        
        met_preconditions = engine.detect_preconditions(context)
        
        assert "weak_session" in met_preconditions

    def test_attack_prediction(self, tmp_path):
        """Test predicting possible attacks."""
        engine = InvertedKillChainEngine(str(tmp_path))
        
        met_preconditions = ["weak_session"]
        context = {"mfa_enabled": False}
        
        predictions = engine.predict_attacks(met_preconditions, context)
        
        assert len(predictions) > 0
        assert any(p.attack_type in ["session_fixation", "csrf"] for p in predictions)


class TestEntropicArchitecture:
    """Test observer-dependent schemas."""

    def test_observer_schema_creation(self):
        """Test creating observer-specific schemas."""
        architecture = EntropicArchitecture()
        
        schema1 = architecture.get_observer_schema("observer_1")
        schema2 = architecture.get_observer_schema("observer_2")
        
        # Different observers should have different schemas
        assert schema1.observer_id != schema2.observer_id
        assert schema1.schema_version != schema2.schema_version

    def test_response_transformation(self):
        """Test transforming responses based on observer schema."""
        architecture = EntropicArchitecture()
        
        data = {
            "user_id": 123,
            "name": "Alice",
            "email": "alice@example.com",
            "status": "active",
        }
        
        # Transform for two different observers
        transformed1 = architecture.transform_response(data, "observer_1")
        transformed2 = architecture.transform_response(data, "observer_2")
        
        # Should have same values but potentially different keys
        assert len(transformed1) == len(data)
        assert len(transformed2) == len(data)


class TestReuseFrictionIndexCalculator:
    """Test Reuse Friction Index calculation."""

    def test_rfi_calculation(self):
        """Test calculating RFI for components."""
        calculator = ReuseFrictionIndexCalculator(minimum_rfi=3)
        
        # High friction context (many conditions)
        high_friction_context = {
            "requires_observer_schema": True,
            "temporal_window": "2023-01-01",
            "invariant_checks": ["check1", "check2"],
            "requires_state_path": True,
        }
        
        rfi_score = calculator.calculate_rfi("test_component", high_friction_context)
        
        # Should have high RFI (close to 1.0)
        assert rfi_score > 0.5
        assert len(calculator.measurements) == 1

    def test_low_rfi_detection(self):
        """Test detecting low RFI (reusable exploits)."""
        calculator = ReuseFrictionIndexCalculator(minimum_rfi=3)
        
        # Low friction context (few conditions)
        low_friction_context = {
            "requires_observer_schema": False,
        }
        
        rfi_score = calculator.calculate_rfi("test_component", low_friction_context)
        
        # Should have low RFI (below minimum)
        assert rfi_score < 0.5


class TestGodTierAsymmetricSecurity:
    """Test God Tier orchestrator."""

    def test_god_tier_initialization(self, tmp_path):
        """Test God Tier system initialization."""
        god_tier = GodTierAsymmetricSecurity(
            data_dir=str(tmp_path / "godtier"),
            enable_all=True,
        )
        
        assert god_tier.enabled is True
        assert god_tier.asymmetric_engine is not None
        assert god_tier.state_machine_analyzer is not None
        assert god_tier.temporal_analyzer is not None
        assert god_tier.inverted_kill_chain is not None
        assert god_tier.entropic_architecture is not None
        assert god_tier.rfi_calculator is not None

    def test_comprehensive_validation_success(self, tmp_path):
        """Test comprehensive action validation that passes."""
        god_tier = GodTierAsymmetricSecurity(
            data_dir=str(tmp_path / "godtier"),
            enable_all=True,
        )
        
        context = {
            "user_id": "user_123",
            "action": "read_data",
            "current_state": "authenticated",
            "target_state": "authenticated",  # No state change
            "auth_token": "valid_token",
            "state_changed": False,
            "trust_decreased": False,
            "mfa_enabled": True,
        }
        
        result = god_tier.validate_action_comprehensive(
            action="read_data",
            context=context,
            user_id="user_123",
        )
        
        assert result["allowed"] is True
        assert len(result["layers_passed"]) > 0
        assert result["threat_level"] in [ThreatLevel.INFO.value, ThreatLevel.MEDIUM.value]
        assert "rfi_score" in result

    def test_comprehensive_validation_failure(self, tmp_path):
        """Test comprehensive validation that fails."""
        god_tier = GodTierAsymmetricSecurity(
            data_dir=str(tmp_path / "godtier"),
            enable_all=True,
        )
        
        context = {
            "user_id": "user_123",
            "action": "delete_data",
            "current_state": "authenticated",
            "target_state": "authenticated",
            "auth_token": None,  # Missing auth token - should fail invariant
            "state_changed": True,
        }
        
        result = god_tier.validate_action_comprehensive(
            action="delete_data",
            context=context,
            user_id="user_123",
        )
        
        assert result["allowed"] is False
        assert len(result["layers_failed"]) > 0
        assert result["threat_level"] in [ThreatLevel.CRITICAL.value, ThreatLevel.HIGH.value]

    def test_entropic_transformation(self, tmp_path):
        """Test applying entropic transformations."""
        god_tier = GodTierAsymmetricSecurity(
            data_dir=str(tmp_path / "godtier"),
            enable_all=True,
        )
        
        data = {
            "user_id": 456,
            "name": "Bob",
            "email": "bob@example.com",
        }
        
        transformed = god_tier.apply_entropic_transformation(data, "observer_x")
        
        assert len(transformed) == len(data)

    def test_god_tier_report_generation(self, tmp_path):
        """Test generating comprehensive God Tier report."""
        god_tier = GodTierAsymmetricSecurity(
            data_dir=str(tmp_path / "godtier"),
            enable_all=True,
        )
        
        # Perform some validations
        context = {
            "auth_token": "valid",
            "state_changed": False,
            "current_state": "authenticated",
            "target_state": "authenticated",
        }
        
        god_tier.validate_action_comprehensive("action1", context, "user1")
        god_tier.validate_action_comprehensive("action2", context, "user2")
        
        report = god_tier.generate_god_tier_report()
        
        assert report["system"] == "God Tier Asymmetric Security"
        assert "version" in report
        assert "metrics" in report
        assert report["metrics"]["validations_performed"] == 2
        assert "subsystems" in report
        assert "asymmetric_engine" in report["subsystems"]
        assert "state_machine_analyzer" in report["subsystems"]
        assert "temporal_analyzer" in report["subsystems"]

    def test_metrics_tracking(self, tmp_path):
        """Test metrics are properly tracked."""
        god_tier = GodTierAsymmetricSecurity(
            data_dir=str(tmp_path / "godtier"),
            enable_all=True,
        )
        
        initial_validations = god_tier.metrics["validations_performed"]
        
        context = {"auth_token": "valid", "state_changed": False}
        god_tier.validate_action_comprehensive("test", context, "user")
        
        assert god_tier.metrics["validations_performed"] == initial_validations + 1


@pytest.fixture
def tmp_path(tmp_path_factory):
    """Create temporary directory for tests."""
    return tmp_path_factory.mktemp("godtier_tests")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
