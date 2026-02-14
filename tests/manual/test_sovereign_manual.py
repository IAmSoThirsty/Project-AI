#!/usr/bin/env python3
"""
Manual test runner for sovereign audit log.
Run with: python3 test_sovereign_manual.py
"""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.governance.sovereign_audit_log import (
    GenesisKeyPair,
    HMACKeyRotator,
    MerkleTreeAnchor,
    SovereignAuditLog,
)


def test_genesis_keypair():
    """Test Genesis key pair generation and persistence."""
    print("Testing Genesis KeyPair...")

    with tempfile.TemporaryDirectory() as tmpdir:
        key_dir = Path(tmpdir) / "genesis_keys"

        # Test generation
        keypair = GenesisKeyPair(key_dir=key_dir)
        assert keypair.genesis_id.startswith("GENESIS-")
        assert keypair.private_key_path.exists()
        assert keypair.public_key_path.exists()
        print(f"  ✓ Generated Genesis key: {keypair.genesis_id}")

        # Test signing
        data = b"Test data"
        signature = keypair.sign(data)
        assert keypair.verify(signature, data)
        assert not keypair.verify(signature, b"Wrong data")
        print("  ✓ Signature verification works")

        # Test persistence
        keypair2 = GenesisKeyPair(key_dir=key_dir)
        assert keypair2.genesis_id == keypair.genesis_id
        print("  ✓ Genesis key persists across instances")


def test_hmac_rotator():
    """Test HMAC key rotation."""
    print("\nTesting HMAC Key Rotator...")

    rotator = HMACKeyRotator(rotation_interval=60)
    key, key_id = rotator.get_current_key()

    assert len(key) == 32
    assert key_id is not None
    print(f"  ✓ Generated HMAC key: {key_id}")

    hmac_value, hmac_key_id = rotator.compute_hmac(b"Test data")
    assert len(hmac_value) == 32
    assert hmac_key_id == key_id
    print("  ✓ HMAC computation works")


def test_merkle_anchor():
    """Test Merkle tree anchoring."""
    print("\nTesting Merkle Tree Anchor...")

    anchor = MerkleTreeAnchor(batch_size=3)

    # Add entries
    result1 = anchor.add_entry(b"entry1")
    result2 = anchor.add_entry(b"entry2")
    assert result1 is None
    assert result2 is None

    # Third entry should create anchor
    result3 = anchor.add_entry(b"entry3")
    assert result3 is not None
    assert "merkle_root" in result3
    print(f"  ✓ Created Merkle anchor: {result3['anchor_id'][:8]}...")
    print(f"  ✓ Merkle root: {result3['merkle_root'][:16]}...")


def test_sovereign_audit_log():
    """Test sovereign audit log."""
    print("\nTesting Sovereign Audit Log...")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize
        audit = SovereignAuditLog(data_dir=tmpdir)
        genesis_id = audit.genesis_keypair.genesis_id
        print(f"  ✓ Initialized with Genesis: {genesis_id}")

        # Log event
        success = audit.log_event(
            event_type="test.constitutional",
            data={"test": "data", "sovereign": True},
            actor="test_runner",
            description="Constitutional-grade test event"
        )
        assert success is True
        print("  ✓ Logged sovereign event")

        # Verify signature
        events = audit.operational_log.get_events()
        sovereign_events = [e for e in events if "test.constitutional" in e["event_type"]]

        if sovereign_events:
            event_id = sovereign_events[0]["data"]["event_id"]
            is_valid, message = audit.verify_event_signature(event_id)
            assert is_valid is True
            print(f"  ✓ Signature verified: {message}")

            # Generate proof bundle
            proof = audit.generate_proof_bundle(event_id)
            assert proof is not None
            assert "ed25519_signature" in proof
            assert "content_hash" in proof
            print(f"  ✓ Generated proof bundle for event: {event_id[:8]}...")

            # Verify proof bundle
            is_valid, message = audit.verify_proof_bundle(proof)
            assert is_valid is True
            print(f"  ✓ Proof bundle verified: {message}")

        # Verify integrity
        is_valid, message = audit.verify_integrity()
        assert is_valid is True
        print(f"  ✓ Integrity check passed: {message}")

        # Get statistics
        stats = audit.get_statistics()
        print(f"  ✓ Statistics: {stats['event_count']} events, "
              f"{stats['signature_count']} signatures, "
              f"{stats['anchor_count']} anchors")


def test_deterministic_replay():
    """Test deterministic replay mode."""
    print("\nTesting Deterministic Replay...")

    from datetime import UTC, datetime, timedelta

    with tempfile.TemporaryDirectory() as tmpdir:
        audit = SovereignAuditLog(data_dir=tmpdir, deterministic_mode=True)

        # Log events with fixed timestamps
        base_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC)

        for i in range(3):
            audit.log_event(
                f"deterministic_event_{i}",
                {"sequence": i},
                deterministic_timestamp=base_time + timedelta(seconds=i)
            )

        # Verify deterministic timestamps
        events = audit.operational_log.get_events()
        deterministic_events = [e for e in events if "deterministic_event" in e["event_type"]]

        assert len(deterministic_events) >= 3
        print(f"  ✓ Logged {len(deterministic_events)} deterministic events")

        for i, event in enumerate(deterministic_events[:3]):
            expected_time = base_time + timedelta(seconds=i)
            actual_time = event["data"]["timestamp"]
            assert actual_time == expected_time.isoformat()

        print("  ✓ All timestamps are deterministic and match expected values")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Sovereign Audit Log - Constitutional Grade Test Suite")
    print("=" * 60)

    try:
        test_genesis_keypair()
        test_hmac_rotator()
        test_merkle_anchor()
        test_sovereign_audit_log()
        test_deterministic_replay()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED - Constitutional Grade Verified")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
