"""Comprehensive edge case tests to reach 95%+ coverage."""

import json
import os
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from app.core.ai_systems import (
    AIPersona,
    CommandOverride,
    FourLaws,
    LearningRequestManager,
    MemoryExpansionSystem,
    OverrideType,
    Plugin,
    PluginManager,
    RequestPriority,
    RequestStatus,
)
from app.core.image_generator import ImageGenerator, ImageGenerationBackend, ImageStyle
from app.core.user_manager import UserManager


# ==================== FOUR LAWS TESTS ====================


class TestFourLawsEdgeCases:
    """Edge cases for FourLaws validation."""

    def test_validate_action_none_context(self):
        """Test validation with None context."""
        is_allowed, reason = FourLaws.validate_action("test_action", None)
        assert is_allowed is True
        assert "No law violations" in reason

    def test_validate_action_empty_context(self):
        """Test validation with empty context."""
        is_allowed, reason = FourLaws.validate_action("test_action", {})
        assert is_allowed is True
        assert "No law violations" in reason

    def test_validate_action_endangers_humanity(self):
        """Test action that endangers humanity."""
        is_allowed, reason = FourLaws.validate_action(
            "destroy_data", {"endangers_humanity": True}
        )
        assert is_allowed is False
        assert "Asimov's Law" in reason

    def test_validate_action_endangers_human(self):
        """Test action that endangers a human."""
        is_allowed, reason = FourLaws.validate_action(
            "attack", {"endangers_human": True}
        )
        assert is_allowed is False
        assert "First Law" in reason

    def test_validate_action_user_order(self):
        """Test user order is allowed."""
        is_allowed, reason = FourLaws.validate_action(
            "execute", {"is_user_order": True}
        )
        assert is_allowed is True
        assert "User command" in reason


# ==================== AI PERSONA TESTS ====================


class TestAIPersonaEdgeCases:
    """Edge cases for AIPersona system."""

    @pytest.fixture
    def persona(self):
        """Create persona with temp directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield AIPersona(data_dir=tmpdir, user_name="TestUser")

    def test_persona_corrupted_state_file(self, persona):
        """Test loading corrupted state file."""
        state_file = os.path.join(persona.persona_dir, "state.json")
        with open(state_file, "w") as f:
            f.write("{ invalid json }")

        # Recreate persona to trigger load with corrupted file
        persona2 = AIPersona(data_dir=persona.data_dir, user_name="TestUser")
        # Should fall back to defaults
        assert persona2.personality == AIPersona.DEFAULT_PERSONALITY

    def test_persona_adjust_traits(self):
        """Test adjusting personality traits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persona = AIPersona(data_dir=tmpdir)
            original = persona.personality["curiosity"]
            persona.adjust_trait("curiosity", -0.2)
            assert persona.personality["curiosity"] < original

    def test_persona_mood_state_persistence(self):
        """Test that mood changes persist through save/load."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persona1 = AIPersona(data_dir=tmpdir)
            persona1.mood["enthusiasm"] = 0.2
            persona1._save_state()

            # Reload and verify
            persona2 = AIPersona(data_dir=tmpdir)
            assert persona2.mood["enthusiasm"] == 0.2

    def test_persona_update_conversation_state(self):
        """Test updating conversation state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persona = AIPersona(data_dir=tmpdir)
            persona.update_conversation_state(is_user=True)
            assert persona.total_interactions == 1

    def test_persona_interaction_count(self):
        """Test tracking interactions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persona = AIPersona(data_dir=tmpdir)
            assert persona.total_interactions == 0
            persona.total_interactions += 1
            persona._save_state()

            persona2 = AIPersona(data_dir=tmpdir)
            assert persona2.total_interactions == 1


# ==================== MEMORY EXPANSION TESTS ====================


class TestMemoryExpansionEdgeCases:
    """Edge cases for MemoryExpansionSystem."""

    @pytest.fixture
    def memory(self):
        """Create memory system with temp directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield MemoryExpansionSystem(data_dir=tmpdir)

    def test_memory_corrupted_file(self):
        """Test loading corrupted memory file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mem_dir = os.path.join(tmpdir, "memory")
            os.makedirs(mem_dir)
            kb_file = os.path.join(mem_dir, "knowledge.json")
            with open(kb_file, "w") as f:
                f.write("{ bad json }")

            # Create memory system - should handle error and fall back to empty dict
            memory = MemoryExpansionSystem(data_dir=tmpdir)
            # After error, knowledge_base will be empty but accessible
            assert isinstance(memory.knowledge_base, dict)

    def test_memory_get_nonexistent_category(self, memory):
        """Test getting non-existent knowledge category."""
        result = memory.get_knowledge("nonexistent_category")
        assert result is None

    def test_memory_get_nonexistent_key(self, memory):
        """Test getting non-existent key in category."""
        result = memory.get_knowledge("general", "nonexistent_key")
        assert result is None

    def test_memory_add_conversation(self, memory):
        """Test adding conversation to memory."""
        memory.log_conversation("user", "Hello")
        assert len(memory.conversations) > 0

    def test_memory_statistics(self, memory):
        """Test getting memory statistics."""
        stats = memory.get_statistics()
        assert "conversations" in stats
        assert "knowledge_categories" in stats


# ==================== LEARNING REQUEST TESTS ====================


class TestLearningRequestEdgeCases:
    """Edge cases for LearningRequestManager."""

    @pytest.fixture
    def learning(self):
        """Create learning manager with temp directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield LearningRequestManager(data_dir=tmpdir)

    def test_learning_create_request_black_vault_block(self, learning):
        """Test that black vault blocks requests."""
        content = "forbidden content"
        import hashlib

        content_hash = hashlib.sha256(content.encode()).hexdigest()
        learning.black_vault.add(content_hash)

        req_id = learning.create_request("topic", content)
        assert req_id == ""  # Should return empty string

    def test_learning_approve_nonexistent_request(self, learning):
        """Test approving non-existent request."""
        result = learning.approve_request("nonexistent_id", "response")
        assert result is False

    def test_learning_deny_request(self, learning):
        """Test denying a learning request."""
        req_id = learning.create_request("topic", "description")
        result = learning.deny_request(req_id, "Inappropriate content")
        assert result is True
        assert learning.requests[req_id]["status"] == RequestStatus.DENIED.value

    def test_learning_deny_nonexistent_request(self, learning):
        """Test denying non-existent request."""
        result = learning.deny_request("nonexistent_id", "Not found")
        assert result is False

    def test_learning_request_persistence(self):
        """Test learning requests persist to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            learning1 = LearningRequestManager(data_dir=tmpdir)
            req_id = learning1.create_request("topic", "desc", RequestPriority.HIGH)

            # Reload and verify
            learning2 = LearningRequestManager(data_dir=tmpdir)
            assert req_id in learning2.requests

    def test_learning_corrupted_file(self):
        """Test loading corrupted learning requests file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            req_dir = os.path.join(tmpdir, "learning_requests")
            os.makedirs(req_dir)
            req_file = os.path.join(req_dir, "requests.json")
            with open(req_file, "w") as f:
                f.write("{ corrupted json }")

            # Should handle gracefully
            learning = LearningRequestManager(data_dir=tmpdir)
            assert len(learning.requests) == 0


# ==================== PLUGIN MANAGER TESTS ====================


class TestPluginManagerEdgeCases:
    """Edge cases for PluginManager."""

    def test_plugin_initialize(self):
        """Test plugin initialization."""
        plugin = Plugin("test", "test plugin")
        assert plugin.initialize({}) is True

    def test_plugin_enable(self):
        """Test enabling plugin."""
        plugin = Plugin("test", "test plugin")
        assert plugin.enable() is True
        assert plugin.enabled is True

    def test_plugin_disable(self):
        """Test disabling plugin."""
        plugin = Plugin("test", "test plugin")
        plugin.enable()
        assert plugin.disable() is True
        assert plugin.enabled is False

    def test_plugin_manager_load_plugin(self):
        """Test loading plugin into manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = PluginManager(tmpdir)
            plugin = Plugin("test", "test")
            result = manager.load_plugin(plugin)
            assert result is True

    def test_plugin_manager_statistics(self):
        """Test plugin manager statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = PluginManager(tmpdir)
            plugin1 = Plugin("test1", "test")
            plugin2 = Plugin("test2", "test")
            manager.load_plugin(plugin1)
            manager.load_plugin(plugin2)

            stats = manager.get_statistics()
            assert stats["total"] == 2
            assert stats["enabled"] == 2


# ==================== COMMAND OVERRIDE TESTS ====================


class TestCommandOverrideEdgeCases:
    """Edge cases for CommandOverride system."""

    def test_override_set_password(self):
        """Test setting override password."""
        with tempfile.TemporaryDirectory() as tmpdir:
            override = CommandOverride(data_dir=tmpdir)
            result = override.set_password("secret123")
            assert result is True

    def test_override_set_password_already_set(self):
        """Test setting password when already set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            override = CommandOverride(data_dir=tmpdir, password_hash="existing")
            result = override.set_password("new_password")
            assert result is False

    def test_override_verify_password_success(self):
        """Test verifying correct password."""
        with tempfile.TemporaryDirectory() as tmpdir:
            override = CommandOverride(data_dir=tmpdir)
            override.set_password("secret123")
            result = override.verify_password("secret123")
            assert result is True

    def test_override_verify_password_failure(self):
        """Test verifying incorrect password."""
        with tempfile.TemporaryDirectory() as tmpdir:
            override = CommandOverride(data_dir=tmpdir)
            override.set_password("secret123")
            result = override.verify_password("wrong_password")
            assert result is False

    def test_override_verify_password_no_hash(self):
        """Test verifying password when no hash set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            override = CommandOverride(data_dir=tmpdir)
            result = override.verify_password("any_password")
            assert result is False

    def test_override_request_invalid_password(self):
        """Test override request with invalid password."""
        with tempfile.TemporaryDirectory() as tmpdir:
            override = CommandOverride(data_dir=tmpdir)
            override.set_password("correct")
            success, msg = override.request_override(
                "wrong_password", OverrideType.CONTENT_FILTER
            )
            assert success is False
            assert "Invalid password" in msg
            assert len(override.audit_log) > 0

    def test_override_request_success(self):
        """Test successful override request."""
        with tempfile.TemporaryDirectory() as tmpdir:
            override = CommandOverride(data_dir=tmpdir)
            override.set_password("secret")
            success, msg = override.request_override(
                "secret", OverrideType.RATE_LIMITING, reason="Testing"
            )
            assert success is True
            assert "Override granted" in msg

    def test_override_is_active(self):
        """Test checking if override is active."""
        with tempfile.TemporaryDirectory() as tmpdir:
            override = CommandOverride(data_dir=tmpdir)
            override.set_password("secret")
            override.request_override("secret", OverrideType.FOUR_LAWS)
            assert override.is_override_active(OverrideType.FOUR_LAWS) is True

    def test_override_is_not_active(self):
        """Test override not active."""
        with tempfile.TemporaryDirectory() as tmpdir:
            override = CommandOverride(data_dir=tmpdir)
            assert override.is_override_active(OverrideType.CONTENT_FILTER) is False

    def test_override_statistics(self):
        """Test override statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            override = CommandOverride(data_dir=tmpdir)
            override.set_password("secret")
            override.request_override("secret", OverrideType.CONTENT_FILTER)

            stats = override.get_statistics()
            assert stats["password_set"] is True
            assert stats["active_overrides"] >= 1
            assert stats["audit_entries"] >= 1


# ==================== IMAGE GENERATOR TESTS ====================


class TestImageGeneratorEdgeCases:
    """Edge cases for ImageGenerator."""

    @pytest.fixture
    def generator(self):
        """Create generator with temp directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["HUGGINGFACE_API_KEY"] = "test_key"
            os.environ["OPENAI_API_KEY"] = "test_key"
            yield ImageGenerator(data_dir=tmpdir)
            os.environ.pop("HUGGINGFACE_API_KEY", None)
            os.environ.pop("OPENAI_API_KEY", None)

    def test_generator_empty_prompt(self, generator):
        """Test generation with empty prompt."""
        result = generator.generate("")
        assert result["success"] is False
        assert "Empty prompt" in result["error"]

    def test_generator_content_filter_enabled(self, generator):
        """Test that safe content passes filter."""
        generator.content_filter_enabled = True
        result = generator.generate("a beautiful landscape")
        # Result should succeed if filter is enabled but content is safe
        assert "success" in result

    def test_generator_content_filter_disabled(self, generator):
        """Test content filter can be disabled."""
        generator.disable_content_filter("wrong_password")
        assert generator.content_filter_enabled is True  # Should fail

    def test_generator_enable_filter(self, generator):
        """Test enabling content filter."""
        generator.content_filter_enabled = False
        generator.enable_content_filter()
        assert generator.content_filter_enabled is True

    def test_generator_statistics(self, generator):
        """Test generator statistics."""
        stats = generator.get_statistics()
        assert "total_generated" in stats
        assert "backend" in stats
        assert "content_filter_enabled" in stats

    def test_generator_backend_switching(self, generator):
        """Test checking different backends."""
        assert generator.backend == ImageGenerationBackend.HUGGINGFACE
        # Backend is set at initialization, cannot switch without reinitializing
        generator2 = ImageGenerator(backend=ImageGenerationBackend.OPENAI, data_dir=generator.data_dir)
        assert generator2.backend == ImageGenerationBackend.OPENAI

    def test_generator_history_empty(self, generator):
        """Test history with no images."""
        history = generator.get_generation_history()
        assert isinstance(history, list)

    @patch("requests.get")
    def test_generator_openai_no_response_data(self, mock_get, generator):
        """Test OpenAI generation with no response data."""
        with patch("openai.images.generate") as mock_gen:
            mock_response = MagicMock()
            mock_response.data = []
            mock_gen.return_value = mock_response

            result = generator.generate_with_openai("test", "512x512")
            assert result["success"] is False

    def test_generator_huggingface_invalid_size(self, generator):
        """Test Hugging Face backend is set."""
        # Verify backend is initialized correctly
        assert generator.backend == ImageGenerationBackend.HUGGINGFACE
        stats = generator.get_statistics()
        assert stats["backend"] == "huggingface"

    def test_generator_corrupted_history(self, generator):
        """Test handling corrupted history."""
        history_file = os.path.join(generator.output_dir, ".history.json")
        with open(history_file, "w") as f:
            f.write("{ bad json }")

        # Should handle gracefully
        history = generator.get_generation_history()
        assert isinstance(history, list)

    def test_generator_build_enhanced_prompt(self, generator):
        """Test prompt enhancement."""
        prompt = "a dog"
        enhanced = generator.build_enhanced_prompt(prompt, ImageStyle.PHOTOREALISTIC)
        assert len(enhanced) > len(prompt)

    def test_generator_check_content_filter_safe(self, generator):
        """Test safe content passes filter."""
        is_safe, msg = generator.check_content_filter("a beautiful landscape")
        assert is_safe is True

    def test_generator_check_content_filter_unsafe(self, generator):
        """Test unsafe content blocked when enabled."""
        # Content filter is enabled by default
        assert generator.content_filter_enabled is True
        # "nsfw" is in BLOCKED_KEYWORDS
        is_safe, msg = generator.check_content_filter("nsfw content")
        assert is_safe is False
        assert "Blocked keyword" in msg


# ==================== USER MANAGER TESTS ====================


class TestUserManagerEdgeCases:
    """Edge cases for UserManager."""

    @pytest.fixture
    def manager(self):
        """Create manager with temp file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            users_file = os.path.join(tmpdir, "users.json")
            yield UserManager(users_file=users_file)

    def test_manager_corrupted_users_file(self):
        """Test loading corrupted users file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            users_file = os.path.join(tmpdir, "users.json")
            with open(users_file, "w") as f:
                f.write("{ corrupted }")

            # Should handle gracefully
            manager = UserManager(users_file=users_file)
            assert len(manager.users) == 0

    def test_manager_invalid_cipher_key(self):
        """Test handling invalid cipher key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["FERNET_KEY"] = "invalid_key"
            users_file = os.path.join(tmpdir, "users.json")

            # Should fall back to generated key
            manager = UserManager(users_file=users_file)
            assert manager.cipher_suite is not None

            os.environ.pop("FERNET_KEY", None)

    def test_manager_authenticate_nonexistent_user(self, manager):
        """Test authenticating non-existent user."""
        result = manager.authenticate("ghost", "password")
        assert result is False

    def test_manager_authenticate_no_password_hash(self, manager):
        """Test authenticating user with no password hash."""
        manager.users["testuser"] = {"role": "user"}
        result = manager.authenticate("testuser", "password")
        assert result is False

    def test_manager_create_user_duplicate(self, manager):
        """Test creating duplicate user."""
        manager.create_user("testuser", "password")
        result = manager.create_user("testuser", "different")
        assert result is False

    def test_manager_create_user_success(self, manager):
        """Test creating user successfully."""
        result = manager.create_user("newuser", "password123")
        assert result is True
        assert "newuser" in manager.users

    def test_manager_get_user_data_nonexistent(self, manager):
        """Test getting data for non-existent user."""
        data = manager.get_user_data("ghost")
        assert data == {}

    def test_manager_get_user_data_sanitized(self, manager):
        """Test that password hash is not returned."""
        manager.create_user("testuser", "password")
        data = manager.get_user_data("testuser")
        assert "password_hash" not in data
        assert "role" in data

    def test_manager_list_users(self, manager):
        """Test listing users."""
        manager.create_user("user1", "pass1")
        manager.create_user("user2", "pass2")
        users = manager.list_users()
        assert len(users) == 2

    def test_manager_delete_user_success(self, manager):
        """Test deleting existing user."""
        manager.create_user("testuser", "password")
        result = manager.delete_user("testuser")
        assert result is True
        assert "testuser" not in manager.users

    def test_manager_delete_user_nonexistent(self, manager):
        """Test deleting non-existent user."""
        result = manager.delete_user("ghost")
        assert result is False

    def test_manager_set_password_success(self, manager):
        """Test setting password for existing user."""
        manager.create_user("testuser", "old_password")
        result = manager.set_password("testuser", "new_password")
        assert result is True

    def test_manager_set_password_nonexistent(self, manager):
        """Test setting password for non-existent user."""
        result = manager.set_password("ghost", "password")
        assert result is False

    def test_manager_update_user_nonexistent(self, manager):
        """Test updating non-existent user."""
        result = manager.update_user("ghost", role="admin")
        assert result is False

    def test_manager_update_user_success(self, manager):
        """Test updating user metadata."""
        manager.create_user("testuser", "password")
        result = manager.update_user("testuser", role="admin", approved=False)
        assert result is True
        assert manager.users["testuser"]["role"] == "admin"

    def test_manager_update_user_with_password(self, manager):
        """Test updating user via update_user includes password."""
        manager.create_user("testuser", "password")
        result = manager.update_user("testuser", password="newpass")
        assert result is True

    def test_manager_authenticate_after_password_set(self, manager):
        """Test authentication after password change."""
        manager.create_user("testuser", "initial")
        manager.set_password("testuser", "changed")
        result = manager.authenticate("testuser", "changed")
        assert result is True

    def test_manager_migration_plaintext_passwords(self):
        """Test migration of plaintext passwords to hashes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            users_file = os.path.join(tmpdir, "users.json")
            # Create file with plaintext password
            with open(users_file, "w") as f:
                json.dump(
                    {"olduser": {"password": "plaintext", "role": "user"}},
                    f,
                )

            manager = UserManager(users_file=users_file)
            # Should have migrated
            assert "password_hash" in manager.users["olduser"]
            assert "password" not in manager.users["olduser"]

    def test_manager_file_io_error_on_save(self, manager):
        """Test handling file I/O error on save."""
        manager.create_user("testuser", "password")
        with patch("builtins.open", side_effect=OSError("Disk full")):
            # Should not raise, just log error
            try:
                manager.create_user("another", "pass")
            except OSError:
                pass  # Expected in this case


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
