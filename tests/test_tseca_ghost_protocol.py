"""
Comprehensive tests for T-SECA/GHOST Protocol.

Tests cover:
- Shamir Secret Sharing (split/reconstruct)
- Ghost Protocol (identity, fragmentation, resurrection)
- T-SECA (runtime hardening, secure inference)
- Heartbeat Monitor (failure detection)
- Unified TSECA_Ghost_System
"""

import time

import pytest

from src.app.security.tseca_ghost_protocol import (
    TSECA,
    GhostProtocol,
    HeartbeatMonitor,
    TSECA_Ghost_System,
    shamir_reconstruct,
    shamir_split,
)

# Shard structure constants
SHARD_INDEX_SIZE = 1  # bytes
SHARD_NONCE_SIZE = 12  # bytes
MIN_SHARD_SIZE = SHARD_INDEX_SIZE + SHARD_NONCE_SIZE  # 13 bytes minimum


class TestShamirSecretSharing:
    """Test Shamir Secret Sharing implementation."""

    def test_split_and_reconstruct_basic(self):
        """Test basic secret splitting and reconstruction."""
        secret = b"Hello, World!"
        k, n = 3, 5

        shares = shamir_split(secret, k, n)

        assert len(shares) == n
        assert all(isinstance(share, tuple) for share in shares)
        assert all(len(share) == 2 for share in shares)

        # Reconstruct with exactly k shares
        reconstructed = shamir_reconstruct(shares[:k])
        assert reconstructed == secret

    def test_reconstruct_with_different_subsets(self):
        """Test reconstruction with different k-subsets of shares."""
        secret = b"Test Secret 123"
        k, n = 3, 5

        shares = shamir_split(secret, k, n)

        # Try different combinations of k shares
        reconstructed1 = shamir_reconstruct(shares[0:3])
        reconstructed2 = shamir_reconstruct(shares[1:4])
        reconstructed3 = shamir_reconstruct(shares[2:5])

        assert reconstructed1 == secret
        assert reconstructed2 == secret
        assert reconstructed3 == secret

    def test_reconstruction_with_more_than_k_shares(self):
        """Test that reconstruction works with more than k shares."""
        secret = b"Extra shares test"
        k, n = 2, 4

        shares = shamir_split(secret, k, n)

        # Use 3 shares (more than k=2)
        reconstructed = shamir_reconstruct(shares[:3])
        assert reconstructed == secret

    def test_split_with_k_equals_n(self):
        """Test splitting when threshold equals total shares."""
        secret = b"All shares needed"
        k, n = 3, 3

        shares = shamir_split(secret, k, n)
        reconstructed = shamir_reconstruct(shares)

        assert reconstructed == secret

    def test_split_with_k_equals_1(self):
        """Test splitting with minimum threshold (k=1)."""
        secret = b"Single share"
        k, n = 1, 3

        shares = shamir_split(secret, k, n)

        # Any single share should be sufficient
        for i in range(n):
            reconstructed = shamir_reconstruct([shares[i]])
            assert reconstructed == secret

    def test_split_invalid_parameters(self):
        """Test error handling for invalid parameters."""
        secret = b"Test"

        with pytest.raises(ValueError):
            shamir_split(secret, 5, 3)  # k > n

        with pytest.raises(ValueError):
            shamir_split(secret, 0, 3)  # k < 1

    def test_reconstruct_empty_shares(self):
        """Test error handling for empty share list."""
        with pytest.raises(ValueError):
            shamir_reconstruct([])

    def test_reconstruct_mismatched_lengths(self):
        """Test error handling for shares with different lengths."""
        shares = [
            (1, b"abc"),
            (2, b"abcd"),  # Different length
        ]

        with pytest.raises(ValueError):
            shamir_reconstruct(shares)

    def test_large_secret(self):
        """Test splitting and reconstructing a large secret."""
        secret = b"X" * 1000  # 1KB secret
        k, n = 3, 5

        shares = shamir_split(secret, k, n)
        reconstructed = shamir_reconstruct(shares[:k])

        assert reconstructed == secret


class TestGhostProtocol:
    """Test Ghost Protocol identity continuity system."""

    def test_initialization(self):
        """Test Ghost Protocol initialization."""
        ghost = GhostProtocol(quorum_k=3, total_n=5)

        assert ghost.quorum_k == 3
        assert ghost.total_n == 5
        assert ghost.identity_key is not None
        assert ghost.identity_hash is not None
        assert len(ghost.identity_hash) == 64  # SHA-256 hex length
        assert ghost.master_key is not None

    def test_invalid_quorum_parameters(self):
        """Test error handling for invalid quorum parameters."""
        with pytest.raises(ValueError):
            GhostProtocol(quorum_k=5, total_n=3)  # k > n

        with pytest.raises(ValueError):
            GhostProtocol(quorum_k=0, total_n=5)  # k < 1

    def test_identity_hash_consistency(self):
        """Test that identity hash is consistent."""
        ghost = GhostProtocol()

        original_hash = ghost.identity_hash
        computed_hash = ghost._compute_identity_hash()

        assert original_hash == computed_hash

    def test_fragment_identity(self):
        """Test identity fragmentation into encrypted shards."""
        ghost = GhostProtocol(quorum_k=3, total_n=5)

        shards = ghost.fragment_identity()

        assert len(shards) == 5
        assert all(isinstance(shard, bytes) for shard in shards)
        assert all(
            len(shard) > MIN_SHARD_SIZE for shard in shards
        )  # index + nonce + ciphertext

    def test_resurrect_identity(self):
        """Test identity resurrection from shards."""
        ghost = GhostProtocol(quorum_k=3, total_n=5)

        original_hash = ghost.identity_hash
        shards = ghost.fragment_identity()

        # Resurrect with exactly quorum_k shards
        restored_hash = ghost.resurrect(shards[:3])

        assert restored_hash == original_hash
        assert ghost.identity_hash == original_hash

    def test_resurrect_with_more_than_quorum(self):
        """Test resurrection with more than quorum shares."""
        ghost = GhostProtocol(quorum_k=2, total_n=4)

        original_hash = ghost.identity_hash
        shards = ghost.fragment_identity()

        # Use 3 shares (more than quorum=2)
        restored_hash = ghost.resurrect(shards[:3])

        assert restored_hash == original_hash

    def test_resurrect_insufficient_shards(self):
        """Test error handling for insufficient shards."""
        ghost = GhostProtocol(quorum_k=3, total_n=5)
        shards = ghost.fragment_identity()

        with pytest.raises(ValueError, match="Insufficient shards"):
            ghost.resurrect(shards[:2])  # Only 2 of required 3

    def test_resurrect_corrupted_shard(self):
        """Test error handling for corrupted shard data."""
        ghost = GhostProtocol(quorum_k=3, total_n=5)
        shards = ghost.fragment_identity()

        # Corrupt one shard
        corrupted_shards = shards[:2] + [b"corrupted_data"]

        with pytest.raises(ValueError, match="Failed to decrypt"):
            ghost.resurrect(corrupted_shards)

    def test_multiple_fragmentation_cycles(self):
        """Test multiple fragmentation and resurrection cycles."""
        ghost = GhostProtocol(quorum_k=2, total_n=3)

        original_hash = ghost.identity_hash

        # Cycle 1
        shards1 = ghost.fragment_identity()
        restored_hash1 = ghost.resurrect(shards1[:2])
        assert restored_hash1 == original_hash

        # Cycle 2
        shards2 = ghost.fragment_identity()
        restored_hash2 = ghost.resurrect(shards2[:2])
        assert restored_hash2 == original_hash


class TestTSECA:
    """Test T-SECA runtime hardening layer."""

    def test_initialization(self):
        """Test T-SECA initialization with Ghost Protocol."""
        ghost = GhostProtocol()
        tseca = TSECA(ghost)

        assert tseca.ghost is ghost

    def test_verify_identity_success(self):
        """Test successful identity verification."""
        ghost = GhostProtocol()
        tseca = TSECA(ghost)

        # Should not raise exception
        tseca.verify_identity()

    def test_verify_identity_failure(self):
        """Test identity verification failure."""
        ghost = GhostProtocol()
        tseca = TSECA(ghost)

        # Remove identity hash
        ghost.identity_hash = None

        with pytest.raises(RuntimeError, match="Identity anchor missing"):
            tseca.verify_identity()

    def test_secure_inference_basic(self):
        """Test basic secure inference operation."""
        ghost = GhostProtocol()
        tseca = TSECA(ghost)

        payload = {"input": "test data"}
        result = tseca.secure_inference(payload)

        assert "result" in result
        assert "identity_hash" in result
        assert "response_hash" in result
        assert "signature" in result

        assert result["identity_hash"] == ghost.identity_hash
        assert len(result["response_hash"]) == 64  # SHA-256 hex
        assert len(result["signature"]) == 128  # Ed25519 signature hex

    def test_secure_inference_result_structure(self):
        """Test secure inference result structure."""
        ghost = GhostProtocol()
        tseca = TSECA(ghost)

        result = tseca.secure_inference({"test": "data"})

        inference_result = result["result"]
        assert "strategic_summary" in inference_result
        assert "risk_assessment" in inference_result
        assert "identified_gaps" in inference_result
        assert "confidence_score" in inference_result

    def test_secure_inference_without_identity(self):
        """Test secure inference fails without identity."""
        ghost = GhostProtocol()
        tseca = TSECA(ghost)

        ghost.identity_hash = None

        with pytest.raises(RuntimeError, match="Identity anchor missing"):
            tseca.secure_inference({"test": "data"})

    def test_signature_verification(self):
        """Test that signature can be verified."""
        ghost = GhostProtocol()
        tseca = TSECA(ghost)

        result = tseca.secure_inference({"test": "data"})

        # Get signature and response hash
        signature_hex = result["signature"]
        response_hash = result["response_hash"]

        # Convert signature back to bytes
        signature = bytes.fromhex(signature_hex)

        # Verify signature using public key
        public_key = ghost.identity_key.public_key()
        public_key.verify(signature, response_hash.encode())  # Should not raise


class TestHeartbeatMonitor:
    """Test Heartbeat Monitor failure detection."""

    def test_initialization(self):
        """Test heartbeat monitor initialization."""
        monitor = HeartbeatMonitor(timeout=5, threshold=3)

        assert monitor.timeout == 5
        assert monitor.threshold == 3
        assert monitor.running is True
        assert monitor.state.failure_count == 0

    def test_beat_resets_failure_count(self):
        """Test that beat() resets failure count."""
        monitor = HeartbeatMonitor()

        monitor.state.failure_count = 5
        monitor.beat()

        assert monitor.state.failure_count == 0

    def test_beat_updates_last_seen(self):
        """Test that beat() updates last_seen timestamp."""
        monitor = HeartbeatMonitor()

        old_time = monitor.state.last_seen
        time.sleep(0.1)
        monitor.beat()

        assert monitor.state.last_seen > old_time

    def test_monitor_triggers_callback_on_failure(self):
        """Test that monitor triggers callback after threshold failures."""
        callback_called = False

        def on_failure():
            nonlocal callback_called
            callback_called = True

        monitor = HeartbeatMonitor(timeout=1, threshold=2)

        # Start monitoring in background
        import threading

        thread = threading.Thread(target=monitor.monitor, args=(on_failure,))
        thread.daemon = True
        thread.start()

        # Wait for failures to accumulate
        time.sleep(3)

        assert callback_called
        assert not monitor.running

    def test_monitor_does_not_trigger_with_heartbeats(self):
        """Test that monitor does not trigger with regular heartbeats."""
        callback_called = False

        def on_failure():
            nonlocal callback_called
            callback_called = True

        monitor = HeartbeatMonitor(timeout=1, threshold=3)

        # Start monitoring
        import threading

        thread = threading.Thread(target=monitor.monitor, args=(on_failure,))
        thread.daemon = True
        thread.start()

        # Send regular heartbeats
        for _ in range(5):
            time.sleep(0.5)
            monitor.beat()

        # Stop monitoring
        monitor.running = False

        assert not callback_called


class TestTSECA_Ghost_System:
    """Test unified TSECA/GHOST system."""

    def test_initialization(self):
        """Test unified system initialization."""
        system = TSECA_Ghost_System()

        assert system.ghost is not None
        assert system.tseca is not None
        assert len(system.shards) == 5  # Default total_n
        assert system.heartbeat is not None

    def test_inference_operation(self):
        """Test inference through unified system."""
        system = TSECA_Ghost_System()

        result = system.inference({"test": "data"})

        assert "result" in result
        assert "identity_hash" in result
        assert "response_hash" in result
        assert "signature" in result

    def test_send_heartbeat(self):
        """Test sending heartbeat through unified system."""
        system = TSECA_Ghost_System()

        system.send_heartbeat()

        assert system.heartbeat.state.failure_count == 0

    def test_catastrophic_event_resurrection(self):
        """Test catastrophic event triggers resurrection."""
        system = TSECA_Ghost_System()

        original_hash = system.ghost.identity_hash

        # Simulate catastrophic event
        system._catastrophic_event()

        # Identity should be restored
        assert system.ghost.identity_hash == original_hash

    def test_system_integration(self):
        """Test complete system integration flow."""
        system = TSECA_Ghost_System()

        # Perform inference
        result1 = system.inference({"input": "test1"})
        assert result1["identity_hash"] == system.ghost.identity_hash

        # Send heartbeat
        system.send_heartbeat()

        # Perform another inference
        result2 = system.inference({"input": "test2"})
        assert result2["identity_hash"] == system.ghost.identity_hash

        # Identity should remain consistent
        assert result1["identity_hash"] == result2["identity_hash"]


class TestIntegration:
    """Integration tests for complete T-SECA/GHOST workflow."""

    def test_complete_lifecycle(self):
        """Test complete system lifecycle."""
        # Initialize system
        system = TSECA_Ghost_System()
        original_hash = system.ghost.identity_hash

        # Perform normal operations
        system.inference({"operation": "analyze"})
        system.send_heartbeat()

        # Simulate catastrophic failure and recovery
        system._catastrophic_event()

        # Verify identity restoration
        assert system.ghost.identity_hash == original_hash

        # Perform post-recovery operations
        result2 = system.inference({"operation": "post-recovery"})
        system.send_heartbeat()

        # Verify continuity
        assert result2["identity_hash"] == original_hash

    def test_cross_component_identity_consistency(self):
        """Test identity consistency across all components."""
        system = TSECA_Ghost_System()

        ghost_hash = system.ghost.identity_hash
        tseca_hash = system.tseca.ghost.identity_hash
        inference_hash = system.inference({"test": "data"})["identity_hash"]

        assert ghost_hash == tseca_hash
        assert ghost_hash == inference_hash

    def test_shard_based_recovery(self):
        """Test recovery using different shard combinations."""
        system = TSECA_Ghost_System()
        original_hash = system.ghost.identity_hash

        # Test recovery with different shard combinations
        for i in range(3):  # quorum_k = 3
            start_idx = i
            end_idx = start_idx + system.ghost.quorum_k

            if end_idx <= len(system.shards):
                restored_hash = system.ghost.resurrect(
                    system.shards[start_idx:end_idx]
                )
                assert restored_hash == original_hash


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
