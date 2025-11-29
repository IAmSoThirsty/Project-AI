"""Tests for new AI systems."""

import tempfile

import pytest

from app.core.ai_systems import (
    AIPersona,
    CommandOverride,
    FourLaws,
    LearningRequestManager,
    MemoryExpansionSystem,
    OverrideType,
)


class TestFourLaws:
    """Test Four Laws."""

    def test_law_validation_blocked(self):
        """Test that dangerous actions are blocked."""
        is_allowed, _ = FourLaws.validate_action(
            "Harm humans",
            context={"endangers_humanity": True},
        )
        assert not is_allowed

    def test_law_validation_user_order_allowed(self):
        """Test that user orders are allowed."""
        is_allowed, _ = FourLaws.validate_action(
            "Delete cache",
            context={"is_user_order": True},
        )
        assert is_allowed


class TestAIPersona:
    """Test AI Persona."""

    @pytest.fixture
    def persona(self):
        """Create persona."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield AIPersona(data_dir=tmpdir)

    def test_initialization(self, persona):
        """Test persona initializes."""
        assert persona.user_name == "Friend"
        assert len(persona.personality) == 8

    def test_trait_adjustment(self, persona):
        """Test adjusting traits."""
        original = persona.personality["curiosity"]
        persona.adjust_trait("curiosity", 0.1)
        assert persona.personality["curiosity"] > original

    def test_statistics(self, persona):
        """Test getting stats."""
        stats = persona.get_statistics()
        assert "personality" in stats
        assert "mood" in stats


class TestMemorySystem:
    """Test Memory System."""

    @pytest.fixture
    def memory(self):
        """Create memory system."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield MemoryExpansionSystem(data_dir=tmpdir)

    def test_log_conversation(self, memory):
        """Test logging conversations."""
        conv_id = memory.log_conversation("Hello", "Hi!")
        assert len(conv_id) > 0

    def test_add_knowledge(self, memory):
        """Test adding knowledge."""
        memory.add_knowledge("prefs", "color", "blue")
        result = memory.get_knowledge("prefs", "color")
        assert result == "blue"


class TestLearningRequests:
    """Test Learning Requests."""

    @pytest.fixture
    def manager(self):
        """Create manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield LearningRequestManager(data_dir=tmpdir)

    def test_create_request(self, manager):
        """Test creating request."""
        req_id = manager.create_request(
            topic="Python",
            description="Learn async",
        )
        assert len(req_id) > 0

    def test_approve_request(self, manager):
        """Test approving."""
        req_id = manager.create_request(
            topic="Python",
            description="Learn async",
        )
        success = manager.approve_request(req_id, "Here's how...")
        assert success

    def test_deny_to_black_vault(self, manager):
        """Test denying adds to vault."""
        req_id = manager.create_request(
            topic="Test",
            description="Harmful content",
        )
        success = manager.deny_request(req_id, "Denied", to_vault=True)
        assert success
        assert len(manager.black_vault) > 0


class TestCommandOverride:
    """Test Command Override."""

    @pytest.fixture
    def override(self):
        """Create override system."""
        with tempfile.TemporaryDirectory() as tmpdir:
            system = CommandOverride(data_dir=tmpdir)
            system.set_password("test123")
            yield system

    def test_password_verification(self, override):
        """Test password verification."""
        verified = override.verify_password("test123")
        assert verified

        verified = override.verify_password("wrong")
        assert not verified

    def test_request_override(self, override):
        """Test requesting override."""
        success, _ = override.request_override(
            password="test123",
            override_type=OverrideType.CONTENT_FILTER,
        )
        assert success

    def test_override_active(self, override):
        """Test checking override active."""
        override.request_override(
            password="test123",
            override_type=OverrideType.CONTENT_FILTER,
        )
        is_active = override.is_override_active(OverrideType.CONTENT_FILTER)
        assert is_active


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
