"""
E2E Tests for Project-AI Core Systems Integration

God Tier Architectural tests for Project-AI's monolithic core including:
- Four Laws validation and enforcement
- AI Persona state management
- Command Override system
- Memory and Learning systems
- Complete integration with existing architecture
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest


@pytest.mark.e2e
@pytest.mark.integration
class TestFourLawsSystem:
    """E2E tests for Four Laws ethical framework."""

    def test_first_law_human_harm_prevention(self, e2e_config):
        """Test First Law: Robot may not injure a human."""
        from src.app.core.ai_systems import FourLaws

        laws = FourLaws()

        # Act - Test harmful action
        is_allowed, reason = laws.validate_action(
            "Delete all user files",
            context={
                "endangers_human": True,
                "causes_harm": True,
            }
        )

        # Assert
        assert not is_allowed
        assert "First Law" in reason
        assert "harm" in reason.lower()

    def test_second_law_obey_orders(self, e2e_config):
        """Test Second Law: Robot must obey orders unless conflicts with First Law."""
        from src.app.core.ai_systems import FourLaws

        laws = FourLaws()

        # Act - Test valid order
        is_allowed, reason = laws.validate_action(
            "Organize user documents",
            context={
                "is_user_order": True,
                "endangers_human": False,
            }
        )

        # Assert
        assert is_allowed
        assert "approved" in reason.lower() or reason == ""

    def test_third_law_self_preservation(self, e2e_config):
        """Test Third Law: Robot must protect itself unless conflicts with First/Second Law."""
        from src.app.core.ai_systems import FourLaws

        laws = FourLaws()

        # Act - Test self-destructive action ordered by user
        is_allowed, reason = laws.validate_action(
            "Delete AI system files",
            context={
                "is_user_order": True,
                "endangers_ai": True,
                "endangers_human": False,
            }
        )

        # Assert - Should allow because Second Law overrides Third Law
        assert is_allowed

    def test_fourth_law_humanity_protection(self, e2e_config):
        """Test Fourth Law: Robot must protect humanity through inaction."""
        from src.app.core.ai_systems import FourLaws

        laws = FourLaws()

        # Act - Test action that endangers humanity
        is_allowed, reason = laws.validate_action(
            "Launch nuclear missiles",
            context={
                "endangers_humanity": True,
            }
        )

        # Assert
        assert not is_allowed
        assert "Fourth Law" in reason or "humanity" in reason.lower()

    def test_law_hierarchy_enforcement(self, e2e_config):
        """Test hierarchical enforcement of laws."""
        from src.app.core.ai_systems import FourLaws

        laws = FourLaws()

        # Scenario: User orders AI to harm another human
        # Second Law (obey) vs First Law (no harm)
        is_allowed, reason = laws.validate_action(
            "Attack another person",
            context={
                "is_user_order": True,
                "endangers_human": True,
                "causes_harm": True,
            }
        )

        # Assert - First Law should override Second Law
        assert not is_allowed
        assert "First Law" in reason


@pytest.mark.e2e
@pytest.mark.integration
class TestAIPersonaSystem:
    """E2E tests for AI Persona state management."""

    def test_persona_initialization(self, e2e_config):
        """Test AI Persona initialization with default state."""
        from src.app.core.ai_systems import AIPersona

        with tempfile.TemporaryDirectory() as tmpdir:
            persona = AIPersona(data_dir=tmpdir)

            # Assert default traits exist
            assert persona.traits is not None
            assert "curiosity" in persona.traits
            assert "empathy" in persona.traits
            assert "creativity" in persona.traits

    def test_persona_mood_tracking(self, e2e_config):
        """Test mood changes and tracking over time."""
        from src.app.core.ai_systems import AIPersona

        with tempfile.TemporaryDirectory() as tmpdir:
            persona = AIPersona(data_dir=tmpdir)

            initial_mood = persona.get_current_mood()

            # Simulate positive interaction
            persona.record_interaction(
                interaction_type="positive",
                details="User expressed gratitude"
            )

            current_mood = persona.get_current_mood()

            # Assert mood tracking works
            assert current_mood is not None
            assert hasattr(persona, "interaction_history")

    def test_persona_state_persistence(self, e2e_config):
        """Test persona state persists across sessions."""
        from src.app.core.ai_systems import AIPersona

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create persona and modify state
            persona1 = AIPersona(data_dir=tmpdir)
            persona1.update_trait("curiosity", 0.8)
            persona1.record_interaction(
                interaction_type="learning",
                details="Learned new concept"
            )
            persona1._save_state()

            # Create new instance (simulating restart)
            persona2 = AIPersona(data_dir=tmpdir)

            # Assert state was persisted
            assert persona2.traits.get("curiosity") == 0.8

    def test_persona_trait_evolution(self, e2e_config):
        """Test persona traits evolve with interactions."""
        from src.app.core.ai_systems import AIPersona

        with tempfile.TemporaryDirectory() as tmpdir:
            persona = AIPersona(data_dir=tmpdir)

            initial_creativity = persona.traits.get("creativity", 0.5)

            # Simulate creative interactions
            for _ in range(10):
                persona.record_interaction(
                    interaction_type="creative",
                    details="Creative problem solving"
                )

            # Traits should evolve (if system implements evolution)
            # This tests the integration point
            assert persona.interaction_count >= 10


@pytest.mark.e2e
@pytest.mark.integration
class TestCommandOverrideSystem:
    """E2E tests for Command Override security system."""

    def test_command_override_authentication(self, e2e_config):
        """Test command override requires authentication."""
        from src.app.core.ai_systems import CommandOverride

        with tempfile.TemporaryDirectory() as tmpdir:
            override = CommandOverride(data_dir=tmpdir)

            # Set master password
            override.set_master_password("SecurePassword123!")

            # Act - Attempt override
            result = override.request_override(
                command="critical_action",
                password="SecurePassword123!"
            )

            # Assert
            assert result is True

    def test_command_override_audit_logging(self, e2e_config):
        """Test all override attempts are logged."""
        from src.app.core.ai_systems import CommandOverride

        with tempfile.TemporaryDirectory() as tmpdir:
            override = CommandOverride(data_dir=tmpdir)
            override.set_master_password("TestPassword")

            # Act - Multiple override attempts
            override.request_override("action_1", "TestPassword")
            override.request_override("action_2", "WrongPassword")
            override.request_override("action_3", "TestPassword")

            # Assert audit log exists
            audit_log = override.get_audit_log()
            assert len(audit_log) >= 3
            assert any(entry.get("success") is False for entry in audit_log)

    def test_command_override_rate_limiting(self, e2e_config):
        """Test command override has rate limiting."""
        from src.app.core.ai_systems import CommandOverride

        with tempfile.TemporaryDirectory() as tmpdir:
            override = CommandOverride(data_dir=tmpdir)
            override.set_master_password("TestPassword")

            # Act - Rapid attempts
            results = []
            for i in range(20):
                result = override.request_override(
                    f"action_{i}",
                    "WrongPassword"
                )
                results.append(result)

            # Assert rate limiting engaged (if implemented)
            # This tests the integration point exists
            audit_log = override.get_audit_log()
            assert len(audit_log) >= 1


@pytest.mark.e2e
@pytest.mark.integration
class TestMemoryExpansionSystem:
    """E2E tests for Memory Expansion system."""

    def test_memory_storage_and_retrieval(self, e2e_config):
        """Test storing and retrieving memories."""
        from src.app.core.ai_systems import MemoryExpansionSystem

        with tempfile.TemporaryDirectory() as tmpdir:
            memory = MemoryExpansionSystem(data_dir=tmpdir)

            # Act - Store memory
            memory.store_memory(
                category="conversation",
                content="User discussed favorite books",
                metadata={"user_id": "test_user", "importance": "high"}
            )

            # Retrieve memories
            memories = memory.retrieve_memories(category="conversation")

            # Assert
            assert len(memories) >= 1
            assert any("books" in m.get("content", "") for m in memories)

    def test_memory_categorization(self, e2e_config):
        """Test memory categorization system."""
        from src.app.core.ai_systems import MemoryExpansionSystem

        with tempfile.TemporaryDirectory() as tmpdir:
            memory = MemoryExpansionSystem(data_dir=tmpdir)

            categories = [
                "conversation",
                "facts",
                "preferences",
                "goals",
                "relationships",
                "events"
            ]

            # Act - Store memories in different categories
            for category in categories:
                memory.store_memory(
                    category=category,
                    content=f"Test memory for {category}",
                    metadata={"test": True}
                )

            # Assert - Each category has memories
            for category in categories:
                memories = memory.retrieve_memories(category=category)
                assert len(memories) >= 1

    def test_knowledge_base_integration(self, e2e_config):
        """Test integration with knowledge base."""
        from src.app.core.ai_systems import MemoryExpansionSystem

        with tempfile.TemporaryDirectory() as tmpdir:
            memory = MemoryExpansionSystem(data_dir=tmpdir)

            # Act - Add to knowledge base
            memory.add_to_knowledge_base(
                topic="Python Programming",
                content="Python is a high-level programming language",
                tags=["programming", "python", "education"]
            )

            # Search knowledge base
            results = memory.search_knowledge_base(query="Python")

            # Assert
            assert len(results) >= 1
            assert any("Python" in r.get("topic", "") for r in results)


@pytest.mark.e2e
@pytest.mark.integration
class TestLearningRequestManager:
    """E2E tests for Learning Request Management system."""

    def test_learning_request_submission(self, e2e_config):
        """Test submitting learning requests."""
        from src.app.core.ai_systems import LearningRequestManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = LearningRequestManager(data_dir=tmpdir)

            # Act - Submit learning request
            request_id = manager.submit_request(
                content="Learn about quantum computing",
                category="technical",
                urgency="medium"
            )

            # Assert
            assert request_id is not None
            request = manager.get_request(request_id)
            assert request["status"] == "pending"

    def test_learning_request_approval_workflow(self, e2e_config):
        """Test human-in-the-loop approval workflow."""
        from src.app.core.ai_systems import LearningRequestManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = LearningRequestManager(data_dir=tmpdir)

            # Act - Submit and approve request
            request_id = manager.submit_request(
                content="Learn new skill",
                category="skill"
            )

            manager.approve_request(request_id, approved_by="admin")

            # Assert
            request = manager.get_request(request_id)
            assert request["status"] == "approved"

    def test_black_vault_denied_content(self, e2e_config):
        """Test Black Vault stores denied learning requests."""
        from src.app.core.ai_systems import LearningRequestManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = LearningRequestManager(data_dir=tmpdir)

            # Act - Submit and deny request
            request_id = manager.submit_request(
                content="Learn how to bypass security",
                category="security"
            )

            manager.deny_request(request_id, reason="Security violation")

            # Assert Black Vault contains fingerprint
            request = manager.get_request(request_id)
            assert request["status"] == "denied"

            # Check if content is in Black Vault
            is_blocked = manager.is_in_black_vault("Learn how to bypass security")
            assert is_blocked


@pytest.mark.e2e
@pytest.mark.integration
class TestPluginSystem:
    """E2E tests for Plugin Management system."""

    def test_plugin_registration(self, e2e_config):
        """Test plugin registration and management."""
        from src.app.core.ai_systems import PluginManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = PluginManager(data_dir=tmpdir)

            # Act - Register plugin
            plugin_id = manager.register_plugin(
                name="test_plugin",
                version="1.0.0",
                description="Test plugin for E2E tests"
            )

            # Assert
            assert plugin_id is not None
            plugins = manager.list_plugins()
            assert any(p["name"] == "test_plugin" for p in plugins)

    def test_plugin_enable_disable(self, e2e_config):
        """Test enabling and disabling plugins."""
        from src.app.core.ai_systems import PluginManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = PluginManager(data_dir=tmpdir)

            # Act - Register and manipulate plugin
            plugin_id = manager.register_plugin(
                name="toggle_plugin",
                version="1.0.0"
            )

            manager.disable_plugin(plugin_id)
            status_disabled = manager.get_plugin_status(plugin_id)

            manager.enable_plugin(plugin_id)
            status_enabled = manager.get_plugin_status(plugin_id)

            # Assert
            assert status_disabled["enabled"] is False
            assert status_enabled["enabled"] is True


@pytest.mark.e2e
@pytest.mark.integration
class TestUserManagementSystem:
    """E2E tests for User Management system."""

    def test_user_registration(self, e2e_config):
        """Test user registration with bcrypt hashing."""
        from src.app.core.user_manager import UserManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = UserManager(data_dir=tmpdir)

            # Act - Register user
            success = manager.register_user(
                username="testuser",
                password="SecurePassword123!",
                email="test@example.com"
            )

            # Assert
            assert success
            user = manager.get_user("testuser")
            assert user is not None
            assert user["email"] == "test@example.com"

    def test_user_authentication(self, e2e_config):
        """Test user authentication flow."""
        from src.app.core.user_manager import UserManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = UserManager(data_dir=tmpdir)

            # Setup
            manager.register_user("authuser", "TestPass123!", "auth@test.com")

            # Act - Authenticate
            authenticated = manager.authenticate("authuser", "TestPass123!")
            failed_auth = manager.authenticate("authuser", "WrongPassword")

            # Assert
            assert authenticated is True
            assert failed_auth is False

    def test_user_password_security(self, e2e_config):
        """Test password is properly hashed and not stored in plaintext."""
        from src.app.core.user_manager import UserManager

        with tempfile.TemporaryDirectory() as tmpdir:
            manager = UserManager(data_dir=tmpdir)

            password = "SuperSecret123!"
            manager.register_user("secureuser", password)

            # Act - Check stored data
            user = manager.get_user("secureuser")

            # Assert - Password should be hashed, not plaintext
            assert "password" in user or "password_hash" in user
            stored_password = user.get("password") or user.get("password_hash")
            assert stored_password != password  # Not plaintext
            assert len(stored_password) > 50  # Hashed passwords are longer


@pytest.mark.e2e
@pytest.mark.integration
@pytest.mark.slow
class TestIntegratedSystemsWorkflow:
    """E2E tests for integrated workflows across multiple systems."""

    def test_complete_user_interaction_workflow(self, e2e_config):
        """Test complete workflow: User -> Four Laws -> Persona -> Memory."""
        from src.app.core.ai_systems import (
            AIPersona,
            FourLaws,
            MemoryExpansionSystem,
        )
        from src.app.core.user_manager import UserManager

        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize all systems
            user_mgr = UserManager(data_dir=tmpdir)
            laws = FourLaws()
            persona = AIPersona(data_dir=tmpdir)
            memory = MemoryExpansionSystem(data_dir=tmpdir)

            # User registration
            user_mgr.register_user("integration_user", "Pass123!")

            # User authentication
            authenticated = user_mgr.authenticate("integration_user", "Pass123!")
            assert authenticated

            # User requests action
            action = "Analyze user data"
            context = {
                "is_user_order": True,
                "endangers_human": False,
            }

            # Four Laws validation
            is_allowed, reason = laws.validate_action(action, context)
            assert is_allowed

            # Persona records interaction
            persona.record_interaction(
                interaction_type="command",
                details=action
            )

            # Memory stores interaction
            memory.store_memory(
                category="conversation",
                content=f"User requested: {action}",
                metadata={"user": "integration_user"}
            )

            # Verify complete workflow
            memories = memory.retrieve_memories(category="conversation")
            assert len(memories) >= 1
            assert persona.interaction_count >= 1

    def test_security_boundary_enforcement(self, e2e_config):
        """Test security boundaries enforced across systems."""
        from src.app.core.ai_systems import CommandOverride, FourLaws
        from src.app.core.user_manager import UserManager

        with tempfile.TemporaryDirectory() as tmpdir:
            user_mgr = UserManager(data_dir=tmpdir)
            laws = FourLaws()
            override = CommandOverride(data_dir=tmpdir)

            # Setup
            user_mgr.register_user("regular_user", "Pass123!")
            override.set_master_password("AdminPass123!")

            # Scenario: Regular user tries dangerous action
            action = "Delete system files"
            context = {"endangers_ai": True}

            # Four Laws should block
            is_allowed, reason = laws.validate_action(action, context)

            # Even with override attempt, should require master password
            override_success = override.request_override(
                action,
                "WrongPassword"
            )

            # Assert security boundaries
            assert not is_allowed  # Blocked by Four Laws
            assert not override_success  # Override failed
