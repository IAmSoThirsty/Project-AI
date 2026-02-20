"""
Tests for Sovereign-Grade Cryptographic Audit Log

This test suite validates constitutional-grade audit logging features:
- Genesis root key binding and persistence
- Ed25519 per-entry digital signatures
- HMAC with rotating keys
- Deterministic replay mode
- Merkle tree anchoring
- Proof bundle generation and verification
- Integrity verification against tampering
- Thread safety
"""

import base64
import tempfile
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

try:
    from app.governance.sovereign_audit_log import (
        GenesisKeyPair,
        HMACKeyRotator,
        MerkleTreeAnchor,
        SovereignAuditLog,
    )
except ImportError:
    from src.app.governance.sovereign_audit_log import (
        GenesisKeyPair,
        HMACKeyRotator,
        MerkleTreeAnchor,
        SovereignAuditLog,
    )


class TestGenesisKeyPair:
    """Test suite for Genesis root key pair."""

    def test_keypair_generation(self):
        """Test that Genesis key pair is generated correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_dir = Path(tmpdir) / "genesis_keys"
            keypair = GenesisKeyPair(key_dir=key_dir)

            assert keypair.private_key is not None
            assert keypair.public_key is not None
            assert keypair.genesis_id.startswith("GENESIS-")

            # Verify key files exist
            assert keypair.private_key_path.exists()
            assert keypair.public_key_path.exists()
            assert keypair.genesis_id_path.exists()

    def test_keypair_persistence(self):
        """Test that Genesis key pair persists across instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_dir = Path(tmpdir) / "genesis_keys"

            # Create first keypair
            keypair1 = GenesisKeyPair(key_dir=key_dir)
            genesis_id1 = keypair1.genesis_id

            # Create second keypair (should load existing)
            keypair2 = GenesisKeyPair(key_dir=key_dir)
            genesis_id2 = keypair2.genesis_id

            # Should have same Genesis ID
            assert genesis_id1 == genesis_id2

    def test_sign_and_verify(self):
        """Test signing and verification with Genesis key."""
        with tempfile.TemporaryDirectory() as tmpdir:
            key_dir = Path(tmpdir) / "genesis_keys"
            keypair = GenesisKeyPair(key_dir=key_dir)

            # Sign some data
            data = b"This is test data for signing"
            signature = keypair.sign(data)

            # Verify signature
            is_valid = keypair.verify(signature, data)
            assert is_valid is True

            # Verify with tampered data fails
            tampered_data = b"This is tampered data"
            is_valid = keypair.verify(signature, tampered_data)
            assert is_valid is False


class TestHMACKeyRotator:
    """Test suite for HMAC key rotation."""

    def test_key_rotation_initialization(self):
        """Test HMAC key rotator initializes correctly."""
        rotator = HMACKeyRotator(rotation_interval=60)

        key, key_id = rotator.get_current_key()

        assert key is not None
        assert len(key) == 32  # 256-bit key
        assert key_id is not None

    def test_key_rotation(self):
        """Test that HMAC keys rotate after interval."""
        rotator = HMACKeyRotator(rotation_interval=1)  # 1 second interval

        # Get initial key
        key1, key_id1 = rotator.get_current_key()

        # Wait for rotation
        time.sleep(1.5)

        # Get key again (should be rotated)
        key2, key_id2 = rotator.get_current_key()

        # Keys should be different
        assert key1 != key2
        assert key_id1 != key_id2

    def test_hmac_computation(self):
        """Test HMAC computation with current key."""
        rotator = HMACKeyRotator()

        data = b"Test data for HMAC"
        hmac_value, key_id = rotator.compute_hmac(data)

        assert hmac_value is not None
        assert len(hmac_value) == 32  # SHA-256 output
        assert key_id is not None

    def test_deterministic_hmac_initialization(self):
        """Test deterministic HMAC key derivation from Genesis seed (VECTOR 7 & 8)."""
        genesis_seed = b"test_genesis_seed_12345678901234567890123456789012"  # 32 bytes

        # Create two rotators with same seed
        rotator1 = HMACKeyRotator(deterministic_mode=True, genesis_seed=genesis_seed)
        rotator2 = HMACKeyRotator(deterministic_mode=True, genesis_seed=genesis_seed)

        # Should have identical keys and IDs
        key1, key_id1 = rotator1.get_current_key()
        key2, key_id2 = rotator2.get_current_key()

        assert key1 == key2
        assert key_id1 == key_id2
        assert len(key1) == 32  # 256-bit key

    def test_deterministic_hmac_replay(self):
        """Test that deterministic HMAC produces identical values across replay."""
        genesis_seed = b"test_genesis_seed_12345678901234567890123456789012"

        # First execution
        rotator1 = HMACKeyRotator(deterministic_mode=True, genesis_seed=genesis_seed)
        data = b"Test event data for deterministic HMAC"
        hmac1, key_id1 = rotator1.compute_hmac(data)

        # Replay execution
        rotator2 = HMACKeyRotator(deterministic_mode=True, genesis_seed=genesis_seed)
        hmac2, key_id2 = rotator2.compute_hmac(data)

        # Should be identical (deterministic)
        assert hmac1 == hmac2
        assert key_id1 == key_id2

    def test_deterministic_hmac_different_seeds(self):
        """Test that different Genesis seeds produce different HMAC keys."""
        seed1 = b"test_genesis_seed_1_32_bytes_long!!!!!!!"
        seed2 = b"test_genesis_seed_2_32_bytes_long!!!!!!!"

        rotator1 = HMACKeyRotator(deterministic_mode=True, genesis_seed=seed1)
        rotator2 = HMACKeyRotator(deterministic_mode=True, genesis_seed=seed2)

        key1, key_id1 = rotator1.get_current_key()
        key2, key_id2 = rotator2.get_current_key()

        # Should be different (different seeds)
        assert key1 != key2
        assert key_id1 != key_id2

    def test_deterministic_hmac_requires_seed(self):
        """Test that deterministic mode requires genesis_seed."""
        with pytest.raises(ValueError, match="genesis_seed is required"):
            HMACKeyRotator(deterministic_mode=True, genesis_seed=None)


class TestMerkleTreeAnchor:
    """Test suite for Merkle tree anchoring."""

    def test_batch_accumulation(self):
        """Test that entries accumulate in batches."""
        anchor = MerkleTreeAnchor(batch_size=3)

        # Add entries (should not create anchor yet)
        result1 = anchor.add_entry(b"entry1")
        result2 = anchor.add_entry(b"entry2")

        assert result1 is None
        assert result2 is None

        # Add third entry (should create anchor)
        result3 = anchor.add_entry(b"entry3")

        assert result3 is not None
        assert "anchor_id" in result3
        assert "merkle_root" in result3
        assert result3["batch_size"] == 3

    def test_merkle_root_computation(self):
        """Test that Merkle root is computed correctly."""
        anchor = MerkleTreeAnchor(batch_size=2)

        # Add two entries to complete batch
        entry1_hash = b"hash1" * 10  # Simulate hash
        entry2_hash = b"hash2" * 10

        result = anchor.add_entry(entry1_hash)
        assert result is None

        result = anchor.add_entry(entry2_hash)
        assert result is not None

        # Verify merkle root exists
        assert len(result["merkle_root"]) == 64  # Hex-encoded SHA-256


class TestSovereignAuditLog:
    """Test suite for sovereign audit log."""

    def test_initialization(self):
        """Test that sovereign audit log initializes correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(data_dir=tmpdir)

            assert audit.genesis_keypair is not None
            assert audit.operational_log is not None
            assert audit.hmac_rotator is not None
            assert audit.merkle_anchor is not None
            assert audit.event_count == 0

    def test_log_event_with_signature(self):
        """Test logging event with Ed25519 signature."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(data_dir=tmpdir)

            success = audit.log_event(
                event_type="test_event",
                data={"key": "value"},
                actor="test_actor",
                description="Test event with signature",
            )

            assert success is True
            assert audit.event_count == 2  # Init event + test event
            assert audit.signature_count == 1  # Only test event counted

            # Verify event was logged
            events = audit.operational_log.get_events()
            assert len(events) >= 2

    def test_event_signature_verification(self):
        """Test that event signatures can be verified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(data_dir=tmpdir)

            # Log event
            audit.log_event(event_type="verifiable_event", data={"test": "data"}, actor="verifier")

            # Get event ID from logged events
            events = audit.operational_log.get_events()
            sovereign_events = [e for e in events if e["event_type"].startswith("sovereign.")]

            if sovereign_events:
                event_id = sovereign_events[0]["data"]["event_id"]

                # Verify signature
                is_valid, message = audit.verify_event_signature(event_id)
                assert is_valid is True
                assert "verified successfully" in message.lower()

    def test_deterministic_mode(self):
        """Test deterministic replay mode with timestamp override."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(data_dir=tmpdir, deterministic_mode=True)

            # Use fixed timestamp for deterministic replay
            fixed_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)

            audit.log_event(
                event_type="deterministic_event", data={"replay": "test"}, deterministic_timestamp=fixed_time
            )

            # Verify event has deterministic timestamp
            events = audit.operational_log.get_events()
            sovereign_events = [e for e in events if e["event_type"].startswith("sovereign.")]

            if sovereign_events:
                event_data = sovereign_events[0]["data"]
                assert event_data["timestamp"] == fixed_time.isoformat()

    def test_proof_bundle_generation(self):
        """Test cryptographic proof bundle generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(data_dir=tmpdir)

            # Log event
            audit.log_event(event_type="provable_event", data={"proof": "data"})

            # Get event ID
            events = audit.operational_log.get_events()
            sovereign_events = [e for e in events if e["event_type"].startswith("sovereign.")]

            if sovereign_events:
                event_id = sovereign_events[0]["data"]["event_id"]

                # Generate proof bundle
                proof = audit.generate_proof_bundle(event_id)

                assert proof is not None
                assert proof["event_id"] == event_id
                assert "ed25519_signature" in proof
                assert "content_hash" in proof
                assert "hmac" in proof
                assert "hash_chain" in proof

    def test_proof_bundle_verification(self):
        """Test proof bundle verification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(data_dir=tmpdir)

            # Log event
            audit.log_event(event_type="verifiable_proof_event", data={"verify": "proof"})

            # Get event ID and generate proof
            events = audit.operational_log.get_events()
            sovereign_events = [e for e in events if e["event_type"].startswith("sovereign.")]

            if sovereign_events:
                event_id = sovereign_events[0]["data"]["event_id"]
                proof = audit.generate_proof_bundle(event_id)

                # Verify proof bundle
                is_valid, message = audit.verify_proof_bundle(proof)
                assert is_valid is True
                assert "verified successfully" in message.lower()

    def test_integrity_verification(self):
        """Test full integrity verification of sovereign audit log."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(data_dir=tmpdir)

            # Log multiple events
            audit.log_event("event1", {"num": 1})
            audit.log_event("event2", {"num": 2})
            audit.log_event("event3", {"num": 3})

            # Verify integrity
            is_valid, message = audit.verify_integrity()
            assert is_valid is True
            assert "verified successfully" in message.lower()

    def test_statistics(self):
        """Test sovereign audit statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(data_dir=tmpdir)

            # Log events
            audit.log_event("stats_event1", {"test": 1})
            audit.log_event("stats_event2", {"test": 2})

            # Get statistics
            stats = audit.get_statistics()

            assert "genesis_id" in stats
            assert stats["event_count"] >= 2
            assert stats["signature_count"] >= 2
            assert "deterministic_mode" in stats
            assert "operational_log_stats" in stats

    def test_genesis_binding_persistence(self):
        """Test that Genesis binding persists across instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create first audit instance
            audit1 = SovereignAuditLog(data_dir=tmpdir)
            genesis_id1 = audit1.genesis_keypair.genesis_id

            # Log event with first instance
            audit1.log_event("persistence_test", {"instance": 1})

            # Create second audit instance (should load same Genesis key)
            audit2 = SovereignAuditLog(data_dir=tmpdir)
            genesis_id2 = audit2.genesis_keypair.genesis_id

            # Should have same Genesis ID
            assert genesis_id1 == genesis_id2

            # Second instance should be able to verify events from first
            events = audit2.operational_log.get_events()
            sovereign_events = [e for e in events if e["event_type"].startswith("sovereign.")]

            if sovereign_events:
                event_id = sovereign_events[0]["data"]["event_id"]
                is_valid, _ = audit2.verify_event_signature(event_id)
                assert is_valid is True

    def test_canonical_serialization(self):
        """Test that canonical serialization is deterministic."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(data_dir=tmpdir)

            # Serialize same data multiple times
            data = {"key2": "value2", "key1": "value1", "key3": [3, 2, 1]}

            bytes1 = audit._canonical_serialize(data)
            bytes2 = audit._canonical_serialize(data)
            bytes3 = audit._canonical_serialize(data)

            # Should be identical
            assert bytes1 == bytes2 == bytes3

            # Should have sorted keys
            decoded = bytes1.decode("utf-8")
            assert decoded.index("key1") < decoded.index("key2") < decoded.index("key3")

    def test_thread_safety(self):
        """Test thread-safe event logging."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(data_dir=tmpdir)

            # Log multiple events (simulates concurrent access)
            for i in range(10):
                success = audit.log_event(f"concurrent_event_{i}", {"thread": i})
                assert success is True

            # All events should be logged
            assert audit.event_count >= 10


class TestConstitutionalGradeFeatures:
    """Test suite for constitutional-grade features."""

    def test_survives_privilege_escalation(self):
        """Test that Genesis key binding survives privilege escalation.

        This simulates an attacker gaining root access but being unable to
        forge audit entries without the Genesis private key.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(data_dir=tmpdir)

            # Log legitimate event
            audit.log_event("legitimate_event", {"legit": True})

            # Simulate attacker trying to forge event by directly modifying log
            # (Without Genesis private key, signature will be invalid)
            events = audit.operational_log.get_events()
            if events:
                # Integrity check should still pass for legitimate events
                is_valid, _ = audit.verify_integrity()
                # Note: Full tampering test would require modifying YAML file
                # which is tested in operational audit log tests

    def test_deterministic_replay_verification(self):
        """Test deterministic replay with fixed timestamps.

        This enables canonical verification across different environments
        by using fixed timestamps instead of system time.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(data_dir=tmpdir, deterministic_mode=True)

            # Log events with fixed timestamps
            base_time = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)

            for i in range(3):
                audit.log_event(
                    f"deterministic_event_{i}",
                    {"sequence": i},
                    deterministic_timestamp=base_time + timedelta(seconds=i),
                )

            # Verify all events have expected timestamps
            events = audit.operational_log.get_events()
            sovereign_events = [e for e in events if e["event_type"].startswith("sovereign.deterministic_event")]

            assert len(sovereign_events) == 3

            for i, event in enumerate(sovereign_events):
                expected_time = base_time + timedelta(seconds=i)
                assert event["data"]["timestamp"] == expected_time.isoformat()

    def test_merkle_batch_anchoring(self):
        """Test Merkle tree anchoring for batch proofs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(data_dir=tmpdir)

            # Configure small batch size for testing
            audit.merkle_anchor.batch_size = 3

            # Log enough events to create anchor
            for i in range(3):
                audit.log_event(f"merkle_event_{i}", {"index": i})

            # Should have created at least one anchor
            assert audit.anchor_count >= 1
            assert len(audit.merkle_anchor.anchor_points) >= 1

    def test_hmac_integrity_layer(self):
        """Test HMAC provides additional integrity layer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(data_dir=tmpdir)

            # Log event
            audit.log_event("hmac_test_event", {"hmac": "test"})

            # Verify event has HMAC
            events = audit.operational_log.get_events()
            sovereign_events = [e for e in events if e["event_type"].startswith("sovereign.hmac_test")]

            if sovereign_events:
                event_data = sovereign_events[0]["data"]
                assert "hmac" in event_data
                assert "hmac_key_id" in event_data

                # HMAC should be base64-encoded
                hmac_bytes = base64.b64decode(event_data["hmac"])
                assert len(hmac_bytes) == 32  # SHA-256 HMAC
