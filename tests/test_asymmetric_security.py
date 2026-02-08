"""
Tests for Asymmetric Security Engine

Tests the 10 concrete security strategies.
"""

import time

import pytest

from app.core.asymmetric_security_engine import (
    AsymmetricSecurityEngine,
    CognitiveTripwireDetector,
    InvariantBountySystem,
    InvariantSeverity,
    RuntimeRandomizer,
    SecurityConstitution,
    SystemInvariant,
    TimeShiftFuzzer,
)


class TestInvariantBountySystem:
    """Test invariant bounty system."""

    def test_invariant_registration(self, tmp_path):
        """Test registering custom invariants."""
        system = InvariantBountySystem(str(tmp_path))

        initial_count = len(system.invariants)

        system.register_invariant(
            SystemInvariant(
                name="test_invariant",
                description="Test description",
                check_function=lambda ctx: True,
                severity=InvariantSeverity.LOW,
                bounty_value=100,
            )
        )

        assert len(system.invariants) == initial_count + 1
        assert "test_invariant" in system.invariants

    def test_invariant_violation_detection(self, tmp_path):
        """Test detecting invariant violations."""
        system = InvariantBountySystem(str(tmp_path))

        # Test auth_proof_required invariant
        context_violation = {
            "auth_token": None,  # Missing auth token
            "state_changed": True,
            "user_id": "test_user",
        }

        result = system.check_invariant("auth_proof_required", context_violation)
        assert result is False  # Should fail without auth token

        context_valid = {
            "auth_token": "valid_token",
            "state_changed": True,
            "user_id": "test_user",
        }

        result = system.check_invariant("auth_proof_required", context_valid)
        assert result is True  # Should pass with auth token

    def test_trust_privilege_coupling(self, tmp_path):
        """Test trust-privilege coupling invariant."""
        system = InvariantBountySystem(str(tmp_path))

        # Violation: trust decreased but privilege retained
        context_violation = {
            "trust_decreased": True,
            "privilege_retained": True,
            "trust_score": 0.3,
            "privileges": ["admin"],
            "action": "access_admin_panel",
        }

        result = system.check_invariant("trust_privilege_coupling", context_violation)
        assert result is False

        # Valid: trust decreased and privilege revoked
        context_valid = {
            "trust_decreased": True,
            "privilege_retained": False,
            "trust_score": 0.3,
            "privileges": [],
            "action": "access_admin_panel",
        }

        result = system.check_invariant("trust_privilege_coupling", context_valid)
        assert result is True


class TestTimeShiftFuzzer:
    """Test time-shift fuzzing."""

    def test_delay_callback(self, tmp_path):
        """Test callback delay injection."""
        fuzzer = TimeShiftFuzzer(str(tmp_path))

        callback_executed = []

        def test_callback():
            callback_executed.append(True)

        callback_id = fuzzer.delay_callback(test_callback, 0.1, "test_component")

        assert callback_id in fuzzer.delayed_callbacks
        assert len(fuzzer.anomalies) == 1
        assert fuzzer.anomalies[0].attack_type == "delay"

    def test_temporal_report(self, tmp_path):
        """Test temporal anomaly reporting."""
        fuzzer = TimeShiftFuzzer(str(tmp_path))

        # Inject some anomalies
        fuzzer.delay_callback(lambda: None, 1.0, "component_a")
        fuzzer.delay_callback(lambda: None, 2.0, "component_b")

        report = fuzzer.get_temporal_report()

        assert report["total_anomalies"] == 2
        assert report["by_type"]["delay"] == 2


class TestAsymmetricSecurityEngine:
    """Test the main asymmetric security engine."""

    def test_engine_initialization(self, tmp_path):
        """Test engine initializes all subsystems."""
        engine = AsymmetricSecurityEngine(str(tmp_path))

        assert engine.invariant_bounty is not None
        assert engine.time_fuzzer is not None
        assert engine.hostile_ux is not None
        assert engine.runtime_randomizer is not None
        assert engine.failure_tester is not None
        assert engine.negative_tests is not None
        assert engine.secret_system is not None
        assert engine.tripwire_detector is not None
        assert engine.attacker_exploitation is not None
        assert engine.constitution is not None

    def test_action_validation_pass(self, tmp_path):
        """Test action validation that passes all checks."""
        engine = AsymmetricSecurityEngine(str(tmp_path))

        context = {
            "user_id": "test_user",
            "auth_token": "valid_token",
            "state_changed": True,
            "trust_decreased": False,
            "privilege_retained": False,
        }

        result = engine.validate_action("test_action", context)

        assert result["allowed"] is True
        assert "constitution" in result["layers_checked"]
        assert "invariant" in result["layers_checked"]

    def test_action_validation_invariant_failure(self, tmp_path):
        """Test action validation fails on invariant violation."""
        engine = AsymmetricSecurityEngine(str(tmp_path))

        context = {
            "user_id": "test_user",
            "auth_token": None,  # Missing auth token
            "state_changed": True,
        }

        result = engine.validate_action("test_action", context)

        assert result["allowed"] is False
        assert result["layer"] == "invariant"
        assert result["bounty_eligible"] is True

    def test_comprehensive_report_generation(self, tmp_path):
        """Test generating comprehensive security report."""
        engine = AsymmetricSecurityEngine(str(tmp_path))

        # Perform some validations
        engine.validate_action(
            "action1", {"auth_token": "valid", "state_changed": True}
        )
        engine.validate_action(
            "action2", {"auth_token": "valid", "state_changed": True}
        )

        report = engine.generate_comprehensive_report()

        assert "engine" in report
        assert report["engine"] == "Asymmetric Security Engine"
        assert "timestamp" in report
        assert "subsystems" in report
        assert "invariant_bounty" in report["subsystems"]
        assert "time_fuzzer" in report["subsystems"]


class TestCognitiveTripwireDetector:
    """Test cognitive tripwire detection."""

    def test_behavior_tracking(self):
        """Test tracking user behavior."""
        detector = CognitiveTripwireDetector()

        user_id = "test_user"

        # Simulate some actions
        detector.track_action_timing(user_id, time.time())
        time.sleep(0.1)
        detector.track_action_timing(user_id, time.time())
        time.sleep(0.1)
        detector.track_action_timing(user_id, time.time())

        assert len(detector.behavioral_history[user_id]) == 3

    def test_bot_detection_threshold(self):
        """Test bot detection threshold."""
        detector = CognitiveTripwireDetector()

        user_id = "normal_user"

        # Normal human-like behavior (no detections yet)
        result = detector.is_likely_bot(user_id, threshold=0.7)
        assert result is False


class TestRuntimeRandomizer:
    """Test runtime attack surface randomization."""

    def test_schema_rotation(self):
        """Test schema version rotation."""
        randomizer = RuntimeRandomizer(rotation_interval_seconds=1)

        initial_version = randomizer.current_schema_version

        # Wait for rotation interval
        time.sleep(1.1)

        # Check if rotation should occur
        should_rotate = randomizer.should_rotate()
        assert should_rotate is True


class TestSecurityConstitution:
    """Test security constitutional framework."""

    def test_constitution_enforcement(self, tmp_path):
        """Test constitutional rule enforcement."""
        constitution = SecurityConstitution(str(tmp_path))

        context = {
            "user_id": "test_user",
            "action": "test_action",
        }

        allowed, reason = constitution.enforce(context)

        # Default implementation allows everything
        assert allowed is True
        assert "compliance" in reason.lower()


@pytest.fixture
def tmp_path(tmp_path_factory):
    """Create temporary directory for tests."""
    return tmp_path_factory.mktemp("asymmetric_tests")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
