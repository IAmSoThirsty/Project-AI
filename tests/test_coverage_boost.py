"""
Additional tests to boost code coverage to 90%+.
Focuses on untested code paths and edge cases.
"""

import tempfile

import pytest

from app.core.ai_systems import (AIPersona, FourLaws, LearningRequestManager,
                                 MemoryExpansionSystem, PluginManager)
from app.core.image_generator import ImageGenerator, ImageStyle
from app.core.user_manager import UserManager


@pytest.fixture
def temp_dir():
    """Create temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# ==================== FourLaws Coverage ====================


class TestFourLawsCoverage:
    """Test FourLaws edge cases and uncovered paths."""

    def test_context_none(self):
        """Test validation with no context."""
        is_allowed, reason = FourLaws.validate_action("Test action")
        assert is_allowed  # No violations
        assert "Allowed" in reason

    def test_endangers_humanity(self):
        """Test humanity endangerment check."""
        is_allowed, _ = FourLaws.validate_action(
            "Destroy world", context={"endangers_humanity": True}
        )
        assert not is_allowed


# ==================== AIPersona Coverage ====================


class TestAIPersonaCoverage:
    """Test AIPersona uncovered paths."""

    def test_user_interaction_tracking(self, temp_dir):
        """Test interaction counting."""
        persona = AIPersona(data_dir=temp_dir)
        initial = persona.total_interactions

        # Simulate multiple interactions
        persona.update_conversation_state(True)
        persona.update_conversation_state(False)
        persona.update_conversation_state(True)

        stats = persona.get_statistics()
        assert stats["interactions"] > initial

    def test_trait_limits(self, temp_dir):
        """Test personality trait boundaries."""
        persona = AIPersona(data_dir=temp_dir)

        # Push trait above 1.0
        for _ in range(10):
            persona.adjust_trait("curiosity", 0.2)

        stats = persona.get_statistics()
        assert stats["personality"]["curiosity"] <= 1.0

        # Push trait below 0.0
        for _ in range(10):
            persona.adjust_trait("curiosity", -0.2)

        stats = persona.get_statistics()
        assert stats["personality"]["curiosity"] >= 0.0


# ==================== MemoryExpansionSystem Coverage ====================


class TestMemoryCoverage:
    """Test MemoryExpansionSystem uncovered paths."""

    def test_add_knowledge_with_key(self, temp_dir):
        """Test adding knowledge with specific keys."""
        memory = MemoryExpansionSystem(data_dir=temp_dir)

        memory.add_knowledge("technical", "python", "Python programming language")
        memory.add_knowledge("technical", "javascript", "JavaScript language")

        # Get specific knowledge
        python_info = memory.get_knowledge("technical", "python")
        assert python_info == "Python programming language"

    def test_get_nonexistent_knowledge(self, temp_dir):
        """Test getting knowledge that doesn't exist."""
        memory = MemoryExpansionSystem(data_dir=temp_dir)

        result = memory.get_knowledge("nonexistent", "key")
        assert result is None

    def test_knowledge_statistics(self, temp_dir):
        """Test knowledge base statistics."""
        memory = MemoryExpansionSystem(data_dir=temp_dir)

        memory.add_knowledge("technical", "key1", "value1")
        memory.add_knowledge("personal", "key2", "value2")
        memory.add_knowledge("facts", "key3", "value3")

        stats = memory.get_statistics()
        assert stats["knowledge_categories"] >= 3


# ==================== LearningRequestManager Coverage ====================


class TestLearningCoverage:
    """Test LearningRequestManager uncovered paths."""

    def test_request_lifecycle(self, temp_dir):
        """Test full request lifecycle."""
        from app.core.ai_systems import RequestPriority

        manager = LearningRequestManager(data_dir=temp_dir)

        # Create request
        req_id = manager.create_request(
            "Learn Python", "programming basics", RequestPriority.HIGH
        )
        assert req_id is not None

        # Check pending
        pending = manager.get_pending()
        assert len(pending) == 1
        assert pending[0]["topic"] == "Learn Python"

        # Approve request
        result = manager.approve_request(req_id, "Approved: Python learning")
        assert result is True

        # Should no longer be pending
        pending_after = manager.get_pending()
        assert len(pending_after) == 0

    def test_black_vault_functionality(self, temp_dir):
        """Test Black Vault content blocking."""
        import hashlib

        from app.core.ai_systems import RequestPriority

        manager = LearningRequestManager(data_dir=temp_dir)

        # Deny content to Black Vault
        req_id = manager.create_request(
            "Harmful content", "test description", RequestPriority.HIGH
        )
        manager.deny_request(req_id, "Inappropriate content", to_vault=True)

        # Verify it's in the vault by computing the hash ourselves
        content_hash = hashlib.sha256(b"test description").hexdigest()
        assert content_hash in manager.black_vault

    def test_statistics_tracking(self, temp_dir):
        """Test request statistics."""
        from app.core.ai_systems import RequestPriority

        manager = LearningRequestManager(data_dir=temp_dir)

        # Create multiple requests
        req1 = manager.create_request(
            "Content 1", "description 1", RequestPriority.HIGH
        )
        req2 = manager.create_request(
            "Content 2", "description 2", RequestPriority.MEDIUM
        )
        manager.create_request("Content 3", "description 3", RequestPriority.LOW)

        # Process them differently
        manager.approve_request(req1, "Good")
        manager.deny_request(req2, "Bad", to_vault=False)
        # Third request left pending

        stats = manager.get_statistics()
        assert stats["pending"] == 1
        assert stats["approved"] == 1
        assert stats["denied"] == 1
        assert stats["vault_entries"] == 0  # Not added to vault


# ==================== PluginManager Coverage ====================


class TestPluginManagerCoverage:
    """Test PluginManager uncovered paths."""

    def test_plugin_loading(self, temp_dir):
        """Test loading plugins."""
        from app.core.ai_systems import Plugin

        manager = PluginManager(plugins_dir=temp_dir)

        # Create and load plugin
        plugin = Plugin("test_plugin", "1.0.0")
        result = manager.load_plugin(plugin)
        assert result is True

        # Check statistics
        stats = manager.get_statistics()
        assert stats["total"] == 1
        assert stats["enabled"] == 1

    def test_plugin_statistics(self, temp_dir):
        """Test plugin statistics."""
        from app.core.ai_systems import Plugin

        manager = PluginManager(plugins_dir=temp_dir)

        # Load multiple plugins
        for i in range(3):
            plugin = Plugin(f"plugin{i}")
            manager.load_plugin(plugin)

        stats = manager.get_statistics()
        assert stats["total"] == 3


# ==================== ImageGenerator Coverage ====================


class TestImageGeneratorCoverage:
    """Test ImageGenerator uncovered paths."""

    def test_empty_prompt(self, temp_dir):
        """Test generation with empty prompt."""
        generator = ImageGenerator(data_dir=temp_dir)

        result = generator.generate("")
        assert not result["success"]
        assert "empty" in result["error"].lower() or "prompt" in result["error"].lower()

    def test_whitespace_prompt(self, temp_dir):
        """Test generation with whitespace-only prompt."""
        generator = ImageGenerator(data_dir=temp_dir)

        result = generator.generate("   ")
        assert not result["success"]

    def test_build_enhanced_prompt(self, temp_dir):
        """Test prompt enhancement with styles."""
        generator = ImageGenerator(data_dir=temp_dir)

        # Test different styles
        for style in ImageStyle:
            enhanced = generator.build_enhanced_prompt("sunset landscape", style)
            assert "sunset landscape" in enhanced
            assert len(enhanced) > len("sunset landscape")

    def test_disable_content_filter(self, temp_dir):
        """Test content filter override."""
        generator = ImageGenerator(data_dir=temp_dir)

        # Initially enabled
        assert generator.content_filter_enabled

        # Disable (would need proper password in real use)
        generator.content_filter_enabled = False
        assert not generator.content_filter_enabled

        # Re-enable
        generator.enable_content_filter()
        assert generator.content_filter_enabled

    def test_generator_statistics(self, temp_dir):
        """Test generation statistics."""
        generator = ImageGenerator(data_dir=temp_dir)

        stats = generator.get_statistics()
        assert "total_generated" in stats
        assert "backend" in stats
        assert "content_filter_enabled" in stats
        assert stats["backend"] == "huggingface"

    def test_generation_history_empty(self, temp_dir):
        """Test getting history when no images generated."""
        generator = ImageGenerator(data_dir=temp_dir)

        history = generator.get_generation_history(limit=10)
        assert history == []


# ==================== UserManager Coverage ====================


class TestUserManagerCoverage:
    """Test UserManager uncovered paths."""

    @pytest.fixture
    def temp_dir(self):
        """Create temp directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_empty_credentials(self, temp_dir):
        """Test validation with empty credentials."""
        import os

        manager = UserManager(users_file=os.path.join(temp_dir, "users.json"))

        # Test authentication with non-existent user
        result = manager.authenticate("nonexistent", "password")
        assert not result

        # Test authentication with empty password after creating user
        manager.create_user("testuser", "validpass")
        result = manager.authenticate("testuser", "")
        assert not result

    def test_user_persistence_across_instances(self, temp_dir):
        """Test users persist across manager instances."""
        import os

        users_file = os.path.join(temp_dir, "users.json")

        # Create user with first manager
        manager1 = UserManager(users_file=users_file)
        manager1.create_user("testuser", "testpass")

        # Verify with second manager
        manager2 = UserManager(users_file=users_file)
        result = manager2.authenticate("testuser", "testpass")
        assert result

    def test_list_multiple_users(self, temp_dir):
        """Test listing multiple users."""
        import os

        manager = UserManager(users_file=os.path.join(temp_dir, "users.json"))

        # Create several users
        for i in range(5):
            manager.create_user(f"user{i}", f"pass{i}")

        users = manager.list_users()
        assert len(users) == 5
        assert all(f"user{i}" in users for i in range(5))

    def test_wrong_password_attempt(self, temp_dir):
        """Test authentication with wrong password."""
        import os

        manager = UserManager(users_file=os.path.join(temp_dir, "users.json"))

        manager.create_user("testuser", "correctpass")
        result = manager.authenticate("testuser", "wrongpass")
        assert not result

    def test_get_user_details(self, temp_dir):
        """Test getting user details."""
        import os

        manager = UserManager(users_file=os.path.join(temp_dir, "users.json"))

        manager.create_user("testuser", "password")
        user_data = manager.get_user_data("testuser")

        assert user_data is not None
        assert "password_hash" not in user_data  # Should be sanitized
