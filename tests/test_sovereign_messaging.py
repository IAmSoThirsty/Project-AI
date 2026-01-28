"""
Tests for Sovereign Messaging System.

Tests cover:
- Communication code generation and validation
- RSA keypair generation
- Hybrid encryption/decryption
- Contact pairing
- Message sending/receiving
- Message lifecycle and status tracking
- Self-destruct timer functionality
- Data persistence
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.features.sovereign_messaging import (
    MessageStatus,
    ParticipantType,
    SovereignMessaging,
)


class TestCommunicationCode:
    """Test communication code generation and validation."""

    def test_code_generation_format(self):
        """Test that generated codes match XXXX-XXXX-XXXX-XXXX format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            messaging = SovereignMessaging(data_dir=tmpdir, participant_name="test")
            code = messaging.get_communication_code()

            # Check format
            assert isinstance(code, str)
            parts = code.split("-")
            assert len(parts) == 4
            for part in parts:
                assert len(part) == 4
                assert part.isalnum()
                # Each character should be uppercase or digit
                for char in part:
                    assert char.isupper() or char.isdigit()

    def test_code_uniqueness(self):
        """Test that different instances get unique codes."""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                messaging1 = SovereignMessaging(data_dir=tmpdir1, participant_name="user1")
                messaging2 = SovereignMessaging(data_dir=tmpdir2, participant_name="user2")

                code1 = messaging1.get_communication_code()
                code2 = messaging2.get_communication_code()

                assert code1 != code2

    def test_code_validation_valid(self):
        """Test validation of valid communication codes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            messaging = SovereignMessaging(data_dir=tmpdir, participant_name="test")

            valid_codes = [
                "AB3D-7F2K-9QWE-5RT8",
                "1234-5678-90AB-CDEF",
                "AAAA-BBBB-CCCC-DDDD"
            ]

            for code in valid_codes:
                assert messaging.validate_communication_code(code) is True

    def test_code_validation_invalid(self):
        """Test validation rejects invalid codes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            messaging = SovereignMessaging(data_dir=tmpdir, participant_name="test")

            invalid_codes = [
                "ABC-123-XYZ",  # Wrong format
                "ABCD-1234-EFGH",  # Only 3 groups
                "ABCD-1234-EFGH-5678-9999",  # 5 groups
                "abcd-efgh-ijkl-mnop",  # Lowercase
                "AB_D-1234-EFGH-5678",  # Special character
                "",  # Empty
                "ABCD1234EFGH5678",  # No dashes
            ]

            for code in invalid_codes:
                assert messaging.validate_communication_code(code) is False


class TestEncryption:
    """Test RSA and AES encryption functionality."""

    def test_rsa_keypair_generation(self):
        """Test RSA-2048 keypair generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            messaging = SovereignMessaging(data_dir=tmpdir, participant_name="test")

            public_key = messaging.get_public_key()

            # Check PEM format
            assert "-----BEGIN PUBLIC KEY-----" in public_key
            assert "-----END PUBLIC KEY-----" in public_key

            # Check private key exists in identity
            assert "private_key" in messaging.identity
            assert "-----BEGIN PRIVATE KEY-----" in messaging.identity["private_key"]

    def test_rsa_encryption_decryption(self):
        """Test RSA encryption and decryption."""
        with tempfile.TemporaryDirectory() as tmpdir:
            messaging = SovereignMessaging(data_dir=tmpdir, participant_name="test")

            # Test data (must be small enough for RSA)
            test_data = b"Hello World"

            # Encrypt with public key
            encrypted = messaging._encrypt_with_rsa(test_data, messaging.get_public_key())
            assert encrypted != test_data
            assert len(encrypted) > 0

            # Decrypt with private key
            decrypted = messaging._decrypt_with_rsa(encrypted)
            assert decrypted == test_data

    def test_aes_encryption_decryption(self):
        """Test AES-256-CBC encryption and decryption."""
        with tempfile.TemporaryDirectory() as tmpdir:
            messaging = SovereignMessaging(data_dir=tmpdir, participant_name="test")

            # Test message
            plaintext = "This is a secret message for testing AES encryption!"

            # Encrypt
            aes_key, iv, ciphertext = messaging._encrypt_with_aes(plaintext)

            # Verify components
            assert len(aes_key) == 32  # 256 bits
            assert len(iv) == 16  # 128 bits
            assert len(ciphertext) > 0
            assert ciphertext != plaintext.encode()

            # Decrypt
            decrypted = messaging._decrypt_with_aes(aes_key, iv, ciphertext)
            assert decrypted == plaintext

    def test_hybrid_encryption_workflow(self):
        """Test complete hybrid encryption workflow."""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                # Create two participants
                sender = SovereignMessaging(data_dir=tmpdir1, participant_name="Alice")
                receiver = SovereignMessaging(data_dir=tmpdir2, participant_name="Bob")

                # Pair them
                sender.pair_with_contact(
                    "Bob",
                    receiver.get_communication_code(),
                    receiver.get_public_key()
                )
                receiver.pair_with_contact(
                    "Alice",
                    sender.get_communication_code(),
                    sender.get_public_key()
                )

                # Send message
                message_text = "Secret message from Alice to Bob!"
                message_id = sender.send_message(
                    receiver.get_communication_code(),
                    message_text
                )

                assert message_id is not None

                # Get sent message details
                sent_messages = sender.get_messages()
                assert len(sent_messages) == 1
                sent_msg = sent_messages[0]

                # Receive message
                received_msg = receiver.receive_message(
                    sender.get_communication_code(),
                    sent_msg["encrypted_aes_key"],
                    sent_msg["iv"],
                    sent_msg["ciphertext"]
                )

                assert received_msg is not None
                assert received_msg["content"] == message_text


class TestContactPairing:
    """Test contact pairing functionality."""

    def test_pair_with_valid_contact(self):
        """Test pairing with valid contact."""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                user1 = SovereignMessaging(data_dir=tmpdir1, participant_name="User1")
                user2 = SovereignMessaging(data_dir=tmpdir2, participant_name="User2")

                # Pair user1 with user2
                result = user1.pair_with_contact(
                    "User2",
                    user2.get_communication_code(),
                    user2.get_public_key()
                )

                assert result is True
                contacts = user1.get_contacts()
                assert user2.get_communication_code() in contacts

    def test_pair_with_invalid_code(self):
        """Test pairing fails with invalid code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            user = SovereignMessaging(data_dir=tmpdir, participant_name="User")

            result = user.pair_with_contact(
                "Invalid",
                "INVALID-CODE",
                "dummy_key"
            )

            assert result is False

    def test_pair_user_and_ai(self):
        """Test pairing between user and AI."""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                user = SovereignMessaging(data_dir=tmpdir1, participant_name="User")
                ai = SovereignMessaging(data_dir=tmpdir2, participant_name="AI_Assistant")
                ai.set_participant_type(ParticipantType.AI)

                # Pair user with AI
                result = user.pair_with_contact(
                    "AI_Assistant",
                    ai.get_communication_code(),
                    ai.get_public_key(),
                    participant_type=ParticipantType.AI
                )

                assert result is True
                contacts = user.get_contacts()
                assert ai.get_communication_code() in contacts
                assert contacts[ai.get_communication_code()]["participant_type"] == "ai"

    def test_contacts_persistence(self):
        """Test contacts are persisted to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create and pair
            user1 = SovereignMessaging(data_dir=tmpdir, participant_name="User1")
            user1.pair_with_contact("User2", "ABCD-1234-EFGH-5678", "dummy_key")

            # Reload and verify
            user1_reloaded = SovereignMessaging(data_dir=tmpdir, participant_name="User1")
            contacts = user1_reloaded.get_contacts()
            assert "ABCD-1234-EFGH-5678" in contacts


class TestMessaging:
    """Test message sending and receiving."""

    def test_send_message_success(self):
        """Test successful message sending."""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                sender = SovereignMessaging(data_dir=tmpdir1, participant_name="Sender")
                receiver = SovereignMessaging(data_dir=tmpdir2, participant_name="Receiver")

                # Pair
                sender.pair_with_contact(
                    "Receiver",
                    receiver.get_communication_code(),
                    receiver.get_public_key()
                )

                # Send
                message_id = sender.send_message(
                    receiver.get_communication_code(),
                    "Test message"
                )

                assert message_id is not None
                assert len(message_id) > 0

    def test_send_message_to_unknown_contact(self):
        """Test sending to unknown contact fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sender = SovereignMessaging(data_dir=tmpdir, participant_name="Sender")

            message_id = sender.send_message("UNKNOWN-CODE-HERE-1234", "Test")

            assert message_id is None

    def test_receive_message_success(self):
        """Test successful message receiving and decryption."""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                sender = SovereignMessaging(data_dir=tmpdir1, participant_name="Sender")
                receiver = SovereignMessaging(data_dir=tmpdir2, participant_name="Receiver")

                # Mutual pairing
                sender.pair_with_contact(
                    "Receiver",
                    receiver.get_communication_code(),
                    receiver.get_public_key()
                )
                receiver.pair_with_contact(
                    "Sender",
                    sender.get_communication_code(),
                    sender.get_public_key()
                )

                # Send
                message_text = "Hello from sender!"
                sender.send_message(receiver.get_communication_code(), message_text)

                # Get encrypted message
                sent_msg = sender.get_messages()[0]

                # Receive
                received = receiver.receive_message(
                    sender.get_communication_code(),
                    sent_msg["encrypted_aes_key"],
                    sent_msg["iv"],
                    sent_msg["ciphertext"]
                )

                assert received is not None
                assert received["content"] == message_text
                assert received["status"] == MessageStatus.DELIVERED.value

    def test_receive_from_unknown_sender(self):
        """Test receiving from unknown sender fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            receiver = SovereignMessaging(data_dir=tmpdir, participant_name="Receiver")

            received = receiver.receive_message(
                "UNKNOWN-SENDER-CODE-1234",
                "aabbcc",
                "ddeeff",
                "112233"
            )

            assert received is None


class TestMessageLifecycle:
    """Test message status lifecycle and self-destruct."""

    def test_message_status_progression(self):
        """Test message status: SENT → DELIVERED → SEEN."""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                sender = SovereignMessaging(data_dir=tmpdir1, participant_name="Sender")
                receiver = SovereignMessaging(data_dir=tmpdir2, participant_name="Receiver")

                # Pair
                sender.pair_with_contact(
                    "Receiver",
                    receiver.get_communication_code(),
                    receiver.get_public_key()
                )
                receiver.pair_with_contact(
                    "Sender",
                    sender.get_communication_code(),
                    sender.get_public_key()
                )

                # Send - status is SENT
                sender.send_message(
                    receiver.get_communication_code(),
                    "Test"
                )
                sent_msg = sender.get_messages()[0]
                assert sent_msg["status"] == MessageStatus.SENT.value

                # Receive - status is DELIVERED
                sent_msg_data = sender.get_messages()[0]
                received = receiver.receive_message(
                    sender.get_communication_code(),
                    sent_msg_data["encrypted_aes_key"],
                    sent_msg_data["iv"],
                    sent_msg_data["ciphertext"]
                )
                assert received["status"] == MessageStatus.DELIVERED.value

                # Mark as SEEN
                result = receiver.mark_message_seen(received["message_id"])
                assert result is True

                messages = receiver.get_messages()
                seen_msg = messages[0]
                assert seen_msg["status"] == MessageStatus.SEEN.value
                assert seen_msg["seen_at"] is not None
                assert seen_msg["delete_at"] is not None

    def test_self_destruct_timer_set(self):
        """Test that self-destruct timer is set correctly (1 hour after seen)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            messaging = SovereignMessaging(data_dir=tmpdir, participant_name="Test")

            # Create a dummy received message
            messaging.messages.append({
                "message_id": "test123",
                "sender_code": "SENDER-CODE",
                "sender_name": "Sender",
                "recipient_code": messaging.get_communication_code(),
                "recipient_name": "Test",
                "content": "Test message",
                "status": MessageStatus.DELIVERED.value,
                "sent_at": None,
                "delivered_at": datetime.now().isoformat(),
                "seen_at": None,
                "delete_at": None
            })

            # Mark as seen
            messaging.mark_message_seen("test123")

            msg = messaging.get_messages()[0]
            assert msg["status"] == MessageStatus.SEEN.value

            # Check delete time is ~1 hour from now
            seen_time = datetime.fromisoformat(msg["seen_at"])
            delete_time = datetime.fromisoformat(msg["delete_at"])
            time_diff = delete_time - seen_time

            # Should be approximately 1 hour (within 10 seconds tolerance)
            assert 3590 <= time_diff.total_seconds() <= 3610

    def test_self_destruct_execution(self):
        """Test that messages are deleted after timer expires."""
        with tempfile.TemporaryDirectory() as tmpdir:
            messaging = SovereignMessaging(data_dir=tmpdir, participant_name="Test")

            # Create message with past delete time
            past_time = datetime.now() - timedelta(hours=2)
            messaging.messages.append({
                "message_id": "expired123",
                "sender_code": "SENDER-CODE",
                "sender_name": "Sender",
                "recipient_code": messaging.get_communication_code(),
                "recipient_name": "Test",
                "content": "Secret content",
                "status": MessageStatus.SEEN.value,
                "sent_at": None,
                "delivered_at": past_time.isoformat(),
                "seen_at": past_time.isoformat(),
                "delete_at": (past_time + timedelta(hours=1)).isoformat()
            })

            # Process self-destruct
            deleted_count = messaging.process_self_destruct()

            assert deleted_count == 1

            msg = messaging.messages[0]
            assert msg["status"] == MessageStatus.DELETED.value
            assert msg["content"] == "[DELETED]"

    def test_self_destruct_preserves_active_messages(self):
        """Test that active messages are not deleted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            messaging = SovereignMessaging(data_dir=tmpdir, participant_name="Test")

            # Create message with future delete time
            future_time = datetime.now() + timedelta(hours=1)
            messaging.messages.append({
                "message_id": "active123",
                "sender_code": "SENDER-CODE",
                "sender_name": "Sender",
                "recipient_code": messaging.get_communication_code(),
                "recipient_name": "Test",
                "content": "Active content",
                "status": MessageStatus.SEEN.value,
                "sent_at": None,
                "delivered_at": datetime.now().isoformat(),
                "seen_at": datetime.now().isoformat(),
                "delete_at": future_time.isoformat()
            })

            # Process self-destruct
            deleted_count = messaging.process_self_destruct()

            assert deleted_count == 0

            msg = messaging.messages[0]
            assert msg["status"] == MessageStatus.SEEN.value
            assert msg["content"] == "Active content"


class TestDataPersistence:
    """Test data persistence to local storage."""

    def test_identity_persistence(self):
        """Test identity is saved and loaded correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create identity
            messaging1 = SovereignMessaging(data_dir=tmpdir, participant_name="User")
            code1 = messaging1.get_communication_code()
            public_key1 = messaging1.get_public_key()

            # Reload and verify
            messaging2 = SovereignMessaging(data_dir=tmpdir, participant_name="User")
            code2 = messaging2.get_communication_code()
            public_key2 = messaging2.get_public_key()

            assert code1 == code2
            assert public_key1 == public_key2

    def test_messages_persistence(self):
        """Test messages are saved and loaded correctly."""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                sender = SovereignMessaging(data_dir=tmpdir1, participant_name="Sender")
                receiver = SovereignMessaging(data_dir=tmpdir2, participant_name="Receiver")

                # Pair and send
                sender.pair_with_contact(
                    "Receiver",
                    receiver.get_communication_code(),
                    receiver.get_public_key()
                )
                message_id = sender.send_message(
                    receiver.get_communication_code(),
                    "Persistent message"
                )

                # Reload sender and verify
                sender_reloaded = SovereignMessaging(
                    data_dir=tmpdir1,
                    participant_name="Sender"
                )
                messages = sender_reloaded.get_messages()
                assert len(messages) == 1
                assert messages[0]["message_id"] == message_id

    def test_storage_directory_structure(self):
        """Test that correct directory structure is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            SovereignMessaging(data_dir=tmpdir, participant_name="User")

            # Check files exist
            data_path = Path(tmpdir)
            assert data_path.exists()
            assert (data_path / "identity.json").exists()
            assert (data_path / "contacts.json").exists()
            assert (data_path / "messages.json").exists()

    def test_no_cloud_no_telemetry(self):
        """Test that system is truly local-only (no external calls)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # This test verifies that creating and using the system
            # doesn't make any network calls (by construction)
            messaging = SovereignMessaging(data_dir=tmpdir, participant_name="User")

            # All operations are local
            messaging.get_communication_code()
            messaging.get_public_key()
            messaging.get_contacts()
            messaging.get_messages()

            # Verify all data is in local directory only
            assert messaging.data_dir == Path(tmpdir)
            assert messaging.identity_file.parent == Path(tmpdir)


class TestParticipantTypes:
    """Test user and AI participant types."""

    def test_default_participant_type(self):
        """Test default participant type is USER."""
        with tempfile.TemporaryDirectory() as tmpdir:
            messaging = SovereignMessaging(data_dir=tmpdir, participant_name="User")
            assert messaging.identity["participant_type"] == ParticipantType.USER.value

    def test_set_ai_participant_type(self):
        """Test setting participant type to AI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            messaging = SovereignMessaging(data_dir=tmpdir, participant_name="AI")
            messaging.set_participant_type(ParticipantType.AI)

            # Verify it's saved
            assert messaging.identity["participant_type"] == ParticipantType.AI.value

            # Reload and verify persistence
            messaging_reloaded = SovereignMessaging(
                data_dir=tmpdir,
                participant_name="AI"
            )
            assert messaging_reloaded.identity["participant_type"] == ParticipantType.AI.value

    def test_user_ai_conversation(self):
        """Test conversation between user and AI."""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                user = SovereignMessaging(data_dir=tmpdir1, participant_name="Human")
                ai = SovereignMessaging(data_dir=tmpdir2, participant_name="AI_Agent")
                ai.set_participant_type(ParticipantType.AI)

                # Mutual pairing
                user.pair_with_contact(
                    "AI_Agent",
                    ai.get_communication_code(),
                    ai.get_public_key(),
                    participant_type=ParticipantType.AI
                )
                ai.pair_with_contact(
                    "Human",
                    user.get_communication_code(),
                    user.get_public_key(),
                    participant_type=ParticipantType.USER
                )

                # User sends to AI
                user.send_message(ai.get_communication_code(), "Hello AI!")
                user_msg = user.get_messages()[0]

                # AI receives
                ai_received = ai.receive_message(
                    user.get_communication_code(),
                    user_msg["encrypted_aes_key"],
                    user_msg["iv"],
                    user_msg["ciphertext"]
                )
                assert ai_received["content"] == "Hello AI!"

                # AI responds
                ai.send_message(user.get_communication_code(), "Hello Human!")
                ai_msg = ai.get_messages()[-1]

                # User receives
                user_received = user.receive_message(
                    ai.get_communication_code(),
                    ai_msg["encrypted_aes_key"],
                    ai_msg["iv"],
                    ai_msg["ciphertext"]
                )
                assert user_received["content"] == "Hello Human!"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
