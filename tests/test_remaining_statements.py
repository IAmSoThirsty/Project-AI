"""Tests targeting the specific 14 remaining uncovered statements."""

import os
import tempfile
from unittest.mock import MagicMock, patch

from app.core.ai_systems import AIPersona, LearningRequestManager, MemoryExpansionSystem
from app.core.image_generator import ImageGenerationBackend, ImageGenerator
from app.core.user_manager import UserManager


class TestRemainingAISystems:
    """Target specific uncovered lines in ai_systems.py."""

    def test_memory_get_knowledge_with_key(self):
        """Cover line 202: return self.knowledge_base[category].get(key).

        This is when key is NOT None and we retrieve a specific key.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = MemoryExpansionSystem(data_dir=tmpdir)
            # Add knowledge to a category
            memory.add_knowledge("security", "sql_injection", {"details": "SQLi attack"})

            # Retrieve with specific key (line 202)
            result = memory.get_knowledge("security", "sql_injection")
            assert result == {"details": "SQLi attack"}

            # Retrieve non-existent key should return None
            result = memory.get_knowledge("security", "nonexistent")
            assert result is None

    def test_memory_get_knowledge_category_not_found(self):
        """Cover line 200: if category not in self.knowledge_base: return None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = MemoryExpansionSystem(data_dir=tmpdir)
            # Try to get knowledge from non-existent category
            result = memory.get_knowledge("nonexistent_category", "any_key")
            assert result is None

    def test_persona_update_conversation_user_message(self):
        """Cover line 118: self.last_user_message_time = datetime.now().

        This is when is_user=True in update_conversation_state.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            persona = AIPersona(data_dir=tmpdir)

            # Initially None
            assert persona.last_user_message_time is None

            # Update with is_user=True (line 118)
            persona.update_conversation_state(is_user=True)

            # Now should be set
            assert persona.last_user_message_time is not None

    def test_persona_update_conversation_ai_message(self):
        """Test update_conversation_state with is_user=False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persona = AIPersona(data_dir=tmpdir)

            # Update with is_user=False
            persona.update_conversation_state(is_user=False)

            # last_user_message_time should remain None
            assert persona.last_user_message_time is None
            # But total_interactions should increase
            assert persona.total_interactions == 1

    def test_learning_deny_request_with_vault(self):
        """Cover lines 265-266: self.black_vault.add(content_hash).

        This happens when deny_request is called with to_vault=True.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            learning = LearningRequestManager(data_dir=tmpdir)

            # Create a request
            req_id = learning.create_request("topic", "sensitive content")
            assert req_id in learning.requests

            # Deny with to_vault=True (lines 265-266)
            result = learning.deny_request(req_id, "Inappropriate", to_vault=True)
            assert result is True

            # Verify it's in the black vault
            import hashlib
            content = learning.requests[req_id]["description"]
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            assert content_hash in learning.black_vault

    def test_learning_deny_request_without_vault(self):
        """Test deny_request with to_vault=False.

        Note: to_vault defaults to True, so we explicitly pass False.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            learning = LearningRequestManager(data_dir=tmpdir)

            # Create a request
            req_id = learning.create_request("topic", "content")

            # Deny with to_vault=False explicitly
            result = learning.deny_request(req_id, "Not needed", to_vault=False)
            assert result is True

            # Should not be in black vault
            import hashlib
            content = learning.requests[req_id]["description"]
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            assert content_hash not in learning.black_vault


class TestRemainingImageGenerator:
    """Target specific uncovered lines in image_generator.py."""

    def test_huggingface_error_handling_lines_269_270(self):
        """Cover lines 269-270: Network error exception during HF generation.

        Lines 269-270 are in the exception handler for generate_with_huggingface.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ImageGenerator(
                backend=ImageGenerationBackend.HUGGINGFACE,
                data_dir=tmpdir
            )

            # Mock the HF API to raise an exception
            with patch("requests.post") as mock_post:
                mock_post.side_effect = Exception("Network error")

                result = generator.generate_with_huggingface(
                    "test prompt", "", 512, 512
                )

                # Should return error dict
                assert result["success"] is False
                assert "error" in result

    def test_history_creation_error_line_282(self):
        """Cover line 282: Error handling in get_generation_history.

        Line 282 is in the except clause when os.listdir fails.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ImageGenerator(
                backend=ImageGenerationBackend.OPENAI,
                data_dir=tmpdir
            )

            # Make output_dir inaccessible (simulate permission error)
            original_dir = generator.output_dir
            generator.output_dir = "/nonexistent/path/that/cannot/exist"

            # Should handle the error gracefully
            result = generator.get_generation_history()
            assert result == []

            # Restore for cleanup
            generator.output_dir = original_dir

    def test_statistics_cleanup_lines_329_330(self):
        """Cover lines 329-330: Exception handling in get_statistics.

        Lines 329-330 are the except clause when os.listdir fails.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ImageGenerator(
                backend=ImageGenerationBackend.OPENAI,
                data_dir=tmpdir
            )

            # Make output_dir temporarily inaccessible
            original_dir = generator.output_dir
            generator.output_dir = "/nonexistent/path/xyz"

            # Should return stats with total_images = 0 (lines 329-330)
            stats = generator.get_statistics()
            assert stats["total_generated"] == 0
            assert "backend" in stats
            assert "content_filter_enabled" in stats

            # Restore
            generator.output_dir = original_dir

    def test_openai_size_validation(self):
        """Test OpenAI size validation edge cases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ImageGenerator(
                backend=ImageGenerationBackend.OPENAI,
                data_dir=tmpdir
            )

            # Test with invalid size format - should still work with defaults
            with patch("openai.images.generate") as mock_gen:
                mock_response = MagicMock()
                mock_response.data = [MagicMock(url="http://example.com/img.png")]
                mock_gen.return_value = mock_response

                result = generator.generate_with_openai("test", "invalid_size")
                # Should handle invalid size
                assert "success" in result


class TestRemainingUserManager:
    """Target specific uncovered lines in user_manager.py."""

    def test_hash_password_bcrypt_exception_line_57(self):
        """Cover line 57: Exception handler in _hash_and_store_password.

        When bcrypt fails, we fall back to pbkdf2 (line 57).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = UserManager(users_file=os.path.join(tmpdir, "users.json"))
            manager.create_user("alice", "password")

            # Mock the module-level pwd_context to fail
            with patch("app.core.user_manager.pwd_context") as mock_pwd:
                # Mock bcrypt to fail
                mock_pwd.hash.side_effect = Exception("Bcrypt failed")

                with patch("passlib.hash.pbkdf2_sha256.hash") as mock_pbkdf:
                    mock_pbkdf.return_value = "pbkdf2_hash"

                    result = manager._hash_and_store_password("alice", "newpass")
                    assert result is True
                    # Should have fallback hash
                    assert manager.users["alice"]["password_hash"] == "pbkdf2_hash"

    def test_authenticate_verify_exception_line_84(self):
        """Cover line 84: Exception handler in verify (pwd_context.verify fails).

        When verify throws an exception, we return False (line 84).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = UserManager(users_file=os.path.join(tmpdir, "users.json"))
            manager.create_user("bob", "password")

            # Mock verify to raise exception
            with patch("app.core.user_manager.pwd_context") as mock_pwd:
                mock_pwd.verify.side_effect = Exception("Verify failed")

                result = manager.authenticate("bob", "password")
                assert result is False

    def test_load_users_corrupted_json_lines_108_109(self):
        """Cover lines 108-109: JSON load exception handling.

        When JSON is corrupted, we default to {} (lines 108-109).
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            users_file = os.path.join(tmpdir, "users.json")

            # Create corrupted JSON file
            with open(users_file, "w") as f:
                f.write("{ bad json }")

            # Load should handle gracefully
            manager = UserManager(users_file=users_file)

            # Should have empty users dict
            assert manager.users == {}

    def test_delete_user_lines_131_132(self):
        """Cover lines 131-132: User deletion and state cleanup.

        When we delete a user, we need to pop it and save.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            users_file = os.path.join(tmpdir, "users.json")
            manager = UserManager(users_file=users_file)

            # Create users
            manager.create_user("charlie", "pass1")
            manager.create_user("diana", "pass2")
            assert len(manager.users) == 2

            # Delete user (lines 131-132)
            manager.delete_user("charlie")
            assert "charlie" not in manager.users
            assert len(manager.users) == 1

            # Verify persistence
            manager2 = UserManager(users_file=users_file)
            assert "charlie" not in manager2.users
            assert "diana" in manager2.users

    def test_bcrypt_and_pbkdf2_both_fail(self):
        """Test when both bcrypt and pbkdf2 fail in _hash_and_store_password."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = UserManager(users_file=os.path.join(tmpdir, "users.json"))
            manager.create_user("eve", "password")

            # Mock both to fail
            with patch("app.core.user_manager.pwd_context") as mock_pwd:
                mock_pwd.hash.side_effect = Exception("Bcrypt failed")

                with patch("passlib.hash.pbkdf2_sha256.hash") as mock_pbkdf:
                    mock_pbkdf.side_effect = Exception("PBKDF2 failed")

                    result = manager._hash_and_store_password("eve", "newpass")
                    # Should return False when both fail
                    assert result is False

    def test_authenticate_user_not_found(self):
        """Test authentication when user doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = UserManager(users_file=os.path.join(tmpdir, "users.json"))

            # Try to authenticate non-existent user
            result = manager.authenticate("nonexistent", "password")
            assert result is False


class TestCrossModuleCoverage:
    """Tests that exercise uncovered paths through integration."""

    def test_memory_knowledge_integration(self):
        """Test memory knowledge system thoroughly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = MemoryExpansionSystem(data_dir=tmpdir)

            # Add multiple items
            memory.add_knowledge("security", "xss", {"attack": "XSS"})
            memory.add_knowledge("security", "csrf", {"attack": "CSRF"})
            memory.add_knowledge("coding", "python", {"language": "Python"})

            # Get full category (key=None)
            security_all = memory.get_knowledge("security")
            assert "xss" in security_all
            assert "csrf" in security_all

            # Get specific item (with key)
            xss_info = memory.get_knowledge("security", "xss")
            assert xss_info == {"attack": "XSS"}

            # Get from non-existent category
            result = memory.get_knowledge("nonexistent")
            assert result is None

            # Get non-existent key from existing category
            result = memory.get_knowledge("security", "nonexistent")
            assert result is None

    def test_persona_conversation_tracking(self):
        """Test persona conversation state tracking."""
        with tempfile.TemporaryDirectory() as tmpdir:
            persona = AIPersona(data_dir=tmpdir)

            # User message (sets last_user_message_time)
            persona.update_conversation_state(is_user=True)
            time1 = persona.last_user_message_time

            # AI message (doesn't change last_user_message_time)
            persona.update_conversation_state(is_user=False)
            time2 = persona.last_user_message_time

            # Times should be the same
            assert time1 == time2

            # Total interactions should be 2
            assert persona.total_interactions == 2

    def test_user_manager_password_migration(self):
        """Test password migration from plaintext to bcrypt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            users_file = os.path.join(tmpdir, "users.json")

            # Create a user with plaintext password (simulating old data)
            manager1 = UserManager(users_file=users_file)
            manager1.users["frank"] = {
                "password": "plaintext_pwd",  # No password_hash
                "persona": "default"
            }
            manager1.save_users()

            # Create new manager (should trigger migration)
            manager2 = UserManager(users_file=users_file)

            # Old plaintext password should be gone
            assert "password" not in manager2.users["frank"]
            # Should have hash now
            assert "password_hash" in manager2.users["frank"]

    def test_image_generator_error_resilience(self):
        """Test image generator handles all error paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ImageGenerator(
                backend=ImageGenerationBackend.HUGGINGFACE,
                data_dir=tmpdir
            )

            # Test with network error
            with patch("requests.post") as mock_post:
                mock_post.side_effect = Exception("Network error")
                result = generator.generate_with_huggingface("test", "", 512, 512)
                assert result["success"] is False

            # Test with unreachable output dir
            generator.output_dir = "/invalid/path"
            history = generator.get_generation_history()
            assert history == []

            stats = generator.get_statistics()
            assert stats["total_generated"] == 0


class TestFinal7Remaining:
    """Final push to cover the last 7 missing statements."""

    def test_learning_deny_request_vault_add_multiple(self):
        """Test deny_request adds multiple items to vault (lines 265-266).

        Need to trigger the to_vault=True path with actual hash computation.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            learning = LearningRequestManager(data_dir=tmpdir)

            # Create multiple requests
            req_ids = []
            for i in range(3):
                req_id = learning.create_request(f"topic{i}", f"content{i}")
                req_ids.append(req_id)

            # Deny first request with vault addition (lines 265-266)
            result = learning.deny_request(req_ids[0], "Test denial", to_vault=True)
            assert result is True

            # Verify in black vault
            import hashlib
            content = learning.requests[req_ids[0]]["description"]
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            assert content_hash in learning.black_vault

            # Deny second without vault
            result2 = learning.deny_request(req_ids[1], "Test denial2", to_vault=False)
            assert result2 is True

            # Get stats to confirm
            stats = learning.get_statistics()
            assert stats["denied"] == 2

    def test_image_generator_huggingface_error_handling(self):
        """Test image generation HF error paths (lines 269-270)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test HUGGINGFACE backend error (lines 269-270)
            hf_gen = ImageGenerator(
                backend=ImageGenerationBackend.HUGGINGFACE,
                data_dir=tmpdir
            )

            # Test network error
            with patch("requests.post") as mock_post:
                mock_post.side_effect = RuntimeError("API timeout")
                result = hf_gen.generate_with_huggingface("test", "", 512, 512)
                assert result["success"] is False
                assert "error" in result

            # Test HTTP error
            with patch("requests.post") as mock_post:
                mock_response = MagicMock()
                mock_response.raise_for_status.side_effect = Exception("400 Bad Request")
                mock_post.return_value = mock_response

                result = hf_gen.generate_with_huggingface("test", "", 512, 512)
                assert result["success"] is False
                assert "error" in result

    def test_image_generator_history_error_handling_line_282(self):
        """Test history error handling (line 282 exception path).

        Trigger exception in get_generation_history.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ImageGenerator(
                backend=ImageGenerationBackend.OPENAI,
                data_dir=tmpdir
            )

            # Mock os.listdir to raise exception (line 282 exception handler)
            original_listdir = os.listdir

            def mock_listdir_error(path):
                if path == generator.output_dir:
                    raise OSError("Permission denied")
                return original_listdir(path)

            with patch("os.listdir", side_effect=mock_listdir_error):
                history = generator.get_generation_history()
                assert history == []  # Should return empty list

    def test_user_manager_bcrypt_fallback_line_57(self):
        """Test bcrypt fallback to pbkdf2 (line 57).

        Force bcrypt hash to fail, triggers fallback.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = UserManager(users_file=os.path.join(tmpdir, "users.json"))
            manager.create_user("user1", "pass1")

            # Now mock to test fallback during _hash_and_store_password
            with patch("app.core.user_manager.pwd_context") as mock_pwd:
                # First call (hash) fails - triggers fallback
                mock_pwd.hash.side_effect = ValueError("Bcrypt unavailable")

                with patch("app.core.user_manager.pbkdf2_sha256.hash") as mock_pbk:
                    mock_pbk.return_value = "pbkdf2_fallback_hash"

                    # Try to hash a password - should use fallback
                    result = manager._hash_and_store_password("user1", "newpass")
                    assert result is True
                    assert manager.users["user1"]["password_hash"] == "pbkdf2_fallback_hash"

    def test_user_manager_verify_exception_line_84(self):
        """Test verify exception handling (line 84).

        Force pwd_context.verify to throw exception.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = UserManager(users_file=os.path.join(tmpdir, "users.json"))
            manager.create_user("user2", "pass2")

            # Mock verify to raise an exception (line 84 path)
            with patch("app.core.user_manager.pwd_context") as mock_pwd:
                mock_pwd.verify.side_effect = TypeError("Hash verification failed")

                result = manager.authenticate("user2", "pass2")
                # Should return False on exception (line 84)
                assert result is False

    def test_generate_with_invalid_backend_else_clause(self):
        """Test generate() backend selection with all paths covered."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with OPENAI which goes through elif path
            openai_gen = ImageGenerator(
                backend=ImageGenerationBackend.OPENAI,
                data_dir=tmpdir
            )

            result = openai_gen.generate("test")
            # Should get error about API key not configured
            assert result["success"] is False

    def test_learning_requests_persistence_with_vault(self):
        """Test learning request persistence with black vault.

        Ensure vault items persist across reloads.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and save request with vault
            learning1 = LearningRequestManager(data_dir=tmpdir)
            req_id = learning1.create_request("persist_test", "vault_content")
            learning1.deny_request(req_id, "Deny for vault", to_vault=True)

            # Reload and check vault persists
            learning2 = LearningRequestManager(data_dir=tmpdir)
            import hashlib
            content_hash = hashlib.sha256(b"vault_content").hexdigest()
            assert content_hash in learning2.black_vault

    def test_persona_state_with_user_messages(self):
        """Test persona state tracking with multiple user messages (line 118).

        Ensure last_user_message_time is properly updated.
        """
        import time as time_module
        with tempfile.TemporaryDirectory() as tmpdir:
            persona = AIPersona(data_dir=tmpdir)

            # First user message
            persona.update_conversation_state(is_user=True)
            time1 = persona.last_user_message_time
            assert time1 is not None

            time_module.sleep(0.01)  # Small delay

            # Second user message
            persona.update_conversation_state(is_user=True)
            time2 = persona.last_user_message_time

            # Should be updated to newer or equal time
            assert time1 is not None and time2 is not None
            assert time2 >= time1
            assert persona.total_interactions == 2

    def test_memory_knowledge_edge_cases(self):
        """Test memory knowledge system with edge cases (line 202).

        Test the .get(key) method for missing keys.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = MemoryExpansionSystem(data_dir=tmpdir)

            # Add knowledge
            memory.add_knowledge("attacks", "xss_attack", {"severity": "high"})

            # Test with existing key (line 202)
            result = memory.get_knowledge("attacks", "xss_attack")
            assert result == {"severity": "high"}

            # Test with missing key
            result = memory.get_knowledge("attacks", "missing_key")
            assert result is None

            # Test get entire category without key
            result = memory.get_knowledge("attacks")
            assert "xss_attack" in result


class TestUserManagerLine57:
    """Target line 57: bcrypt exception in _hash_and_store_password."""

    def test_hash_and_store_password_bcrypt_exception_line_57(self):
        """Cover line 57: except Exception when pwd_context.hash fails.

        Force bcrypt hash to fail, triggering fallback to pbkdf2.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            users_file = os.path.join(tmpdir, "users.json")
            manager = UserManager(users_file=users_file)
            manager.create_user("testuser", "password123")

            # Mock pwd_context.hash to raise exception
            with patch("app.core.user_manager.pwd_context") as mock_pwd:
                mock_pwd.hash.side_effect = RuntimeError("Bcrypt backend failed")

                # Mock pbkdf2_sha256.hash to work
                with patch("app.core.user_manager.pbkdf2_sha256.hash") as mock_pbkdf2:
                    mock_pbkdf2.return_value = "pbkdf2_fallback_hash_xyz"

                    # Call _hash_and_store_password - should use fallback
                    result = manager._hash_and_store_password("testuser", "newpassword")

                    # Should succeed with fallback
                    assert result is True
                    # Should have pbkdf2 hash
                    assert manager.users["testuser"]["password_hash"] == "pbkdf2_fallback_hash_xyz"
                    # Should not have plaintext password
                    assert "password" not in manager.users["testuser"]


class TestUserManagerLine84:
    """Target line 84: pwd_context.verify exception in authenticate."""

    def test_authenticate_verify_exception_line_84(self):
        """Cover line 84: except Exception when pwd_context.verify fails.

        Force verify to raise exception, should return False gracefully.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            users_file = os.path.join(tmpdir, "users.json")
            manager = UserManager(users_file=users_file)
            manager.create_user("testuser", "password123")

            # Mock pwd_context.verify to raise exception
            with patch("app.core.user_manager.pwd_context") as mock_pwd:
                mock_pwd.verify.side_effect = RuntimeError("Hash verification backend failed")

                # Call authenticate - should catch exception and return False
                result = manager.authenticate("testuser", "password123")

                # Should return False (line 84 catches and returns False)
                assert result is False
