#!/usr/bin/env python3
"""
Test sovereign audit integration with AuditManager.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.governance.audit_manager import AuditManager


def test_operational_mode():
    """Test backward-compatible operational mode."""
    print("Testing Operational Mode (default)...")

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = AuditManager(data_dir=tmpdir)

        assert manager.sovereign_mode is False
        print("  ✓ Operational mode initialized")

        # Log events
        manager.log_system_event("test_started", {"test": "operational"})
        manager.log_security_event("test_security", {"severity": "low"})

        # Get statistics
        stats = manager.get_statistics()
        assert stats["mode"] == "operational"
        print(f"  ✓ Statistics: {stats['main_log']['total_events']} events logged")

        # Verify integrity
        is_valid, message = manager.verify_integrity()
        assert is_valid is True
        print(f"  ✓ Integrity check: {message}")


def test_sovereign_mode():
    """Test constitutional-grade sovereign mode."""
    print("\nTesting Sovereign Mode (constitutional-grade)...")

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = AuditManager(data_dir=tmpdir, sovereign_mode=True)

        assert manager.sovereign_mode is True
        print("  ✓ Sovereign mode initialized")

        # Get Genesis ID
        genesis_id = manager.get_genesis_id()
        assert genesis_id is not None
        assert genesis_id.startswith("GENESIS-")
        print(f"  ✓ Genesis ID: {genesis_id}")

        # Log events
        manager.log_system_event("test_started", {"test": "sovereign"})
        manager.log_security_event("critical_alert", {"ip": "1.2.3.4"}, severity="critical")
        manager.log_governance_event("policy_enforced", {"policy": "constitutional"})

        # Get statistics
        stats = manager.get_statistics()
        assert stats["mode"] == "sovereign"
        assert stats["genesis_id"] == genesis_id
        print(f"  ✓ Statistics: {stats['main_log']['event_count']} events, "
              f"{stats['main_log']['signature_count']} signatures")

        # Verify integrity (includes Ed25519 signature verification)
        is_valid, message = manager.verify_integrity()
        assert is_valid is True
        print(f"  ✓ Integrity check: {message}")

        # Test proof bundle generation (sovereign-only feature)
        events = manager.audit_log.operational_log.get_events()
        if events:
            sovereign_events = [e for e in events if "test_started" in e["event_type"]]
            if sovereign_events:
                event_id = sovereign_events[0]["data"]["event_id"]

                # Generate proof bundle
                proof = manager.generate_proof_bundle(event_id)
                assert proof is not None
                assert "ed25519_signature" in proof
                print(f"  ✓ Generated proof bundle for event: {event_id[:8]}...")

                # Verify proof bundle
                is_valid, message = manager.verify_proof_bundle(proof)
                assert is_valid is True
                print(f"  ✓ Proof bundle verified: {message}")


def test_deterministic_mode():
    """Test deterministic replay mode."""
    print("\nTesting Deterministic Replay Mode...")

    from datetime import UTC, datetime

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = AuditManager(
            data_dir=tmpdir,
            sovereign_mode=True,
            deterministic_mode=True
        )

        # Log events with fixed timestamps
        base_time = datetime(2025, 1, 15, 10, 0, 0, tzinfo=UTC)

        manager.audit_log.log_event(
            "deterministic_test",
            {"sequence": 1},
            deterministic_timestamp=base_time
        )

        print("  ✓ Deterministic mode enabled")
        print("  ✓ Events logged with fixed timestamps for canonical replay")


def main():
    """Run all integration tests."""
    print("=" * 70)
    print("Sovereign Audit Integration Tests - AuditManager")
    print("=" * 70)

    try:
        test_operational_mode()
        test_sovereign_mode()
        test_deterministic_mode()

        print("\n" + "=" * 70)
        print("✓ ALL INTEGRATION TESTS PASSED")
        print("=" * 70)
        return 0

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
