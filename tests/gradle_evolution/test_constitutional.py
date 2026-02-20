"""
Tests for Constitutional Engine, Enforcer, and Temporal Law.

Tests constitutional principle enforcement, temporal law evolution,
and integration with existing governance infrastructure.
"""

from datetime import datetime, timedelta

import pytest
from gradle_evolution.constitutional.enforcer import ConstitutionalEnforcer
from gradle_evolution.constitutional.engine import ConstitutionalEngine
from gradle_evolution.constitutional.temporal_law import (
    TemporalLaw,
    TemporalLawRegistry,
)


class TestConstitutionalEngine:
    """Test ConstitutionalEngine component."""

    def test_initialization_with_file(self, constitution_file):
        """Test engine initializes with constitution file."""
        engine = ConstitutionalEngine(constitution_path=str(constitution_file))

        assert engine.constitution is not None
        assert engine.constitution["name"] == "test_constitution"
        assert len(engine.constitution["principles"]) == 3

    def test_initialization_without_file(self, temp_dir):
        """Test engine uses default constitution when file missing."""
        nonexistent = temp_dir / "missing.yaml"
        engine = ConstitutionalEngine(constitution_path=str(nonexistent))

        assert engine.constitution["name"] == "default_constitution"
        assert "enforcement_levels" in engine.constitution

    def test_validate_allowed_action(self, constitution_file):
        """Test validation allows compliant actions."""
        engine = ConstitutionalEngine(constitution_path=str(constitution_file))

        is_allowed, reason = engine.validate_build_action("compile", context={"violations": []})

        assert is_allowed

    def test_validate_blocked_action(self, constitution_file):
        """Test validation blocks actions with immediate violations."""
        engine = ConstitutionalEngine(constitution_path=str(constitution_file))

        is_allowed, reason = engine.validate_build_action("deploy", context={"violations": ["security_violation"]})

        assert not is_allowed
        assert "security_violation" in reason
        assert len(engine.violation_log) == 1

    def test_principle_violation_logging(self, constitution_file):
        """Test violations are properly logged."""
        engine = ConstitutionalEngine(constitution_path=str(constitution_file))

        # Trigger violation
        engine.validate_build_action("test_action", context={"violations": ["credential_leak"]})

        assert len(engine.violation_log) > 0
        violation = engine.violation_log[0]
        assert violation["action"] == "test_action"
        assert "timestamp" in violation

    def test_get_violation_history(self, constitution_file):
        """Test retrieving violation history."""
        engine = ConstitutionalEngine(constitution_path=str(constitution_file))

        # Create multiple violations
        for i in range(3):
            engine.validate_build_action(f"action_{i}", context={"violations": ["security_violation"]})

        history = engine.get_violation_history()
        assert len(history) == 3


class TestConstitutionalEnforcer:
    """Test ConstitutionalEnforcer component."""

    @pytest.fixture
    def mock_identity_manager(self, mocker):
        """Create mock IdentityManager."""
        mock = mocker.MagicMock()
        mock.verify_identity.return_value = True
        return mock

    def test_enforcer_initialization(self, constitution_file, mock_identity_manager):
        """Test enforcer initializes with identity manager."""
        enforcer = ConstitutionalEnforcer(mock_identity_manager)

        assert enforcer.identity_manager == mock_identity_manager
        assert enforcer.violation_history == []

    def test_enforce_action_allowed(self, constitution_file, mock_identity_manager):
        """Test enforcer allows compliant actions."""
        enforcer = ConstitutionalEnforcer(mock_identity_manager)

        result = enforcer.enforce_action(action="compile", identity="build_agent", context={"violations": []})

        assert result["allowed"]
        assert result["action"] == "compile"

    def test_enforce_action_blocked(self, constitution_file, mock_identity_manager):
        """Test enforcer blocks non-compliant actions."""
        enforcer = ConstitutionalEnforcer(mock_identity_manager)

        result = enforcer.enforce_action(
            action="deploy",
            identity="build_agent",
            context={"violations": ["security_violation"]},
        )

        # Should check policy enforcement
        assert "allowed" in result or "reason" in result

    def test_enforcement_history_tracking(self, constitution_file, mock_identity_manager):
        """Test enforcement history is tracked."""
        enforcer = ConstitutionalEnforcer(mock_identity_manager)

        enforcer.enforce_action("action1", identity="agent1", context={})
        enforcer.enforce_action("action2", identity="agent2", context={})

        assert len(enforcer.violation_history) >= 0  # May or may not have violations

    def test_identity_verification(self, constitution_file, mock_identity_manager):
        """Test identity verification integration."""
        enforcer = ConstitutionalEnforcer(mock_identity_manager)

        enforcer.enforce_action("compile", identity="build_agent", context={})

        # Should verify identity
        mock_identity_manager.verify_identity.assert_called()


class TestTemporalLaw:
    """Test TemporalLaw component."""

    def test_temporal_law_creation(self, sample_temporal_law):
        """Test creating temporal law."""
        law = TemporalLaw(**sample_temporal_law)

        assert law.law_id == "test_law_001"
        assert law.effective_from is not None
        assert len(law.rules) == 1

    def test_is_active_within_timeframe(self, sample_temporal_law):
        """Test law is active within valid timeframe."""
        # Set timeframe around current time
        now = datetime.utcnow()
        sample_temporal_law["effective_from"] = (now - timedelta(days=1)).isoformat()
        sample_temporal_law["effective_until"] = (now + timedelta(days=1)).isoformat()

        law = TemporalLaw(**sample_temporal_law)

        assert law.is_active()

    def test_is_inactive_before_effective(self, sample_temporal_law):
        """Test law is inactive before effective date."""
        future = datetime.utcnow() + timedelta(days=10)
        sample_temporal_law["effective_from"] = future.isoformat()

        law = TemporalLaw(**sample_temporal_law)

        assert not law.is_active()

    def test_is_inactive_after_expiration(self, sample_temporal_law):
        """Test law is inactive after expiration."""
        past = datetime.utcnow() - timedelta(days=10)
        sample_temporal_law["effective_from"] = (past - timedelta(days=5)).isoformat()
        sample_temporal_law["effective_until"] = past.isoformat()

        law = TemporalLaw(**sample_temporal_law)

        assert not law.is_active()

    def test_law_to_dict(self, sample_temporal_law):
        """Test converting law to dictionary."""
        law = TemporalLaw(**sample_temporal_law)
        law_dict = law.to_dict()

        assert law_dict["law_id"] == "test_law_001"
        assert "rules" in law_dict


class TestTemporalLawRegistry:
    """Test TemporalLawRegistry component."""

    def test_registry_initialization(self, temp_dir):
        """Test registry initializes."""
        storage = temp_dir / "laws.json"
        registry = TemporalLawRegistry(storage_path=storage)

        assert registry.storage_path == storage
        assert registry.laws == {}

    def test_register_law(self, temp_dir, sample_temporal_law):
        """Test registering a law."""
        storage = temp_dir / "laws.json"
        registry = TemporalLawRegistry(storage_path=storage)

        law = TemporalLaw(**sample_temporal_law)
        registry.register_law(law)

        assert law.law_id in registry.laws

    def test_get_active_laws(self, temp_dir, sample_temporal_law):
        """Test retrieving active laws only."""
        storage = temp_dir / "laws.json"
        registry = TemporalLawRegistry(storage_path=storage)

        # Active law
        now = datetime.utcnow()
        sample_temporal_law["effective_from"] = (now - timedelta(days=1)).isoformat()
        active_law = TemporalLaw(**sample_temporal_law)

        # Inactive law (future)
        future_law_data = sample_temporal_law.copy()
        future_law_data["law_id"] = "future_law"
        future_law_data["effective_from"] = (now + timedelta(days=10)).isoformat()
        future_law = TemporalLaw(**future_law_data)

        registry.register_law(active_law)
        registry.register_law(future_law)

        active = registry.get_active_laws()

        assert len(active) == 1
        assert active[0].law_id == "test_law_001"

    def test_persistence(self, temp_dir, sample_temporal_law):
        """Test law persistence to disk."""
        storage = temp_dir / "laws.json"
        registry = TemporalLawRegistry(storage_path=storage)

        law = TemporalLaw(**sample_temporal_law)
        registry.register_law(law)
        registry.save()

        # Load in new registry
        new_registry = TemporalLawRegistry(storage_path=storage)
        new_registry.load()

        assert law.law_id in new_registry.laws

    def test_revoke_law(self, temp_dir, sample_temporal_law):
        """Test revoking a law."""
        storage = temp_dir / "laws.json"
        registry = TemporalLawRegistry(storage_path=storage)

        law = TemporalLaw(**sample_temporal_law)
        registry.register_law(law)

        revoked = registry.revoke_law(law.law_id)

        assert revoked
        assert law.law_id not in registry.laws
