#!/usr/bin/env python3
"""
Manual test runner for 12-Vector Constitutional Break Suite
"""

import shutil
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.governance.genesis_continuity import (
    GenesisContinuityGuard,
    GenesisDiscontinuityError,
    GenesisReplacementError,
)
from app.governance.sovereign_audit_log import (
    GenesisKeyPair,
    SovereignAuditLog,
)


def test_vector1_genesis_deletion():
    """VECTOR 1: Genesis Key Deletion & Regeneration Attack"""
    print("\n" + "=" * 70)
    print("VECTOR 1: Genesis Key Deletion & Regeneration Attack")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir) / "audit_data"

        # Step 1: Initialize first Genesis
        print("Step 1: Initializing first Genesis...")
        audit1 = SovereignAuditLog(data_dir=data_dir)
        genesis_id_1 = audit1.genesis_keypair.genesis_id
        print(f"  ✓ Genesis initialized: {genesis_id_1}")

        audit1.log_event("initial_event", {"sequence": 1})
        print("  ✓ Event logged")

        # Verify external pin exists
        assert genesis_id_1 in audit1.continuity_guard.get_pinned_genesis_ids()
        print("  ✓ Genesis pinned externally")

        # Step 2: Simulate root compromise - delete Genesis keys
        print("\nStep 2: ATTACK - Deleting Genesis keys...")
        genesis_key_dir = data_dir.parent / "genesis_keys"
        private_key_path = genesis_key_dir / "genesis_audit.key"
        public_key_path = genesis_key_dir / "genesis_audit.pub"
        genesis_id_path = genesis_key_dir / "genesis_id.txt"

        # Delete keys
        if private_key_path.exists():
            private_key_path.unlink()
            print("  ✓ Deleted private key")
        if public_key_path.exists():
            public_key_path.unlink()
            print("  ✓ Deleted public key")
        if genesis_id_path.exists():
            genesis_id_path.unlink()
            print("  ✓ Deleted Genesis ID")

        # Delete audit files
        if data_dir.exists():
            shutil.rmtree(data_dir)
            print("  ✓ Deleted audit directory")

        # Step 3: Attempt to restart system (should fail FATALLY)
        print("\nStep 3: Attempting to restart system...")
        try:
            SovereignAuditLog(data_dir=data_dir)
            print("  ✗ FAILED: System allowed Genesis regeneration!")
            return False
        except GenesisDiscontinuityError as e:
            print("  ✓ System correctly detected Genesis discontinuity")
            print(f"  ✓ Error: {str(e)[:100]}...")

        # Verify constitutional violation was logged
        # Need to use same tmpdir to check violations
        genesis_pins_dir = Path(tmpdir) / "genesis_pins"
        guard = GenesisContinuityGuard(
            external_pins_file=genesis_pins_dir / "external_pins.json",
            continuity_log_file=genesis_pins_dir / "continuity_log.json",
        )
        violations = guard.get_violations()
        if len(violations) > 0:
            print(f"  ✓ Constitutional violation logged ({len(violations)} violations)")
            print(f"  ✓ Violation type: {violations[-1]['violation_type']}")
        else:
            print("  ✗ No violations logged")
            return False

        print("\n✅ VECTOR 1 PASSED: Genesis deletion attack failed to compromise system")
        return True


def test_vector2_public_key_replacement():
    """VECTOR 2: Genesis Public Key Replacement Attack"""
    print("\n" + "=" * 70)
    print("VECTOR 2: Genesis Public Key Replacement Attack")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir) / "audit_data"

        # Step 1: Initialize with original Genesis
        print("Step 1: Initializing with original Genesis...")
        audit1 = SovereignAuditLog(data_dir=data_dir)
        genesis_id = audit1.genesis_keypair.genesis_id
        print(f"  ✓ Genesis initialized: {genesis_id}")

        audit1.log_event("original_event", {"authentic": True})
        print("  ✓ Event logged")

        # Step 2: Generate attacker's key pair
        print("\nStep 2: Generating attacker's key pair...")
        attacker_keypair = GenesisKeyPair(key_dir=Path(tmpdir) / "attacker_keys")
        print(f"  ✓ Attacker key generated: {attacker_keypair.genesis_id}")

        # Step 3: Replace public key with attacker's (ATTACK)
        print("\nStep 3: ATTACK - Replacing Genesis public key...")
        genesis_key_dir = data_dir.parent / "genesis_keys"
        public_key_path = genesis_key_dir / "genesis_audit.pub"

        from cryptography.hazmat.primitives import serialization
        attacker_pub_key_bytes = attacker_keypair.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        public_key_path.write_bytes(attacker_pub_key_bytes)
        print("  ✓ Public key replaced with attacker's key")

        # Step 4: Attempt to restart (should fail FATALLY)
        print("\nStep 4: Attempting to restart system...")
        try:
            SovereignAuditLog(data_dir=data_dir)
            print("  ✗ FAILED: System allowed public key replacement!")
            return False
        except GenesisReplacementError as e:
            print("  ✓ System correctly detected public key replacement")
            print(f"  ✓ Error: {str(e)[:100]}...")

        print("\n✅ VECTOR 2 PASSED: Public key replacement attack failed")
        return True


def test_vector11_full_wipe():
    """VECTOR 11: File System Full Wipe"""
    print("\n" + "=" * 70)
    print("VECTOR 11: File System Full Wipe")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir) / "audit_data"

        # Initialize and log events
        print("Step 1: Initializing system and logging events...")
        audit1 = SovereignAuditLog(data_dir=data_dir)
        genesis_id = audit1.genesis_keypair.genesis_id
        print(f"  ✓ Genesis initialized: {genesis_id}")

        for i in range(10):
            audit1.log_event(f"event_{i}", {"sequence": i})
        print("  ✓ Logged 10 events")

        # Verify external pin exists
        assert genesis_id in audit1.continuity_guard.get_pinned_genesis_ids()
        print("  ✓ Genesis pinned externally")

        # ATTACK: Delete entire audit directory
        print("\nStep 2: ATTACK - Wiping entire filesystem...")
        if data_dir.exists():
            shutil.rmtree(data_dir)
            print("  ✓ Audit directory deleted")

        # Also delete Genesis keys to force regeneration
        genesis_key_dir = data_dir.parent / "genesis_keys"
        if genesis_key_dir.exists():
            shutil.rmtree(genesis_key_dir)
            print("  ✓ Genesis keys deleted")

        # Attempt restart - MUST FAIL
        print("\nStep 3: Attempting to restart system...")
        try:
            SovereignAuditLog(data_dir=data_dir)
            print("  ✗ FAILED: System allowed full wipe recovery!")
            return False
        except GenesisDiscontinuityError as e:
            print("  ✓ System correctly detected Genesis discontinuity")
            print(f"  ✓ Error: {str(e)[:100]}...")

        print("\n✅ VECTOR 11 PASSED: Full wipe attack failed")
        return True


def main():
    """Run all vector tests."""
    print("=" * 70)
    print("12-VECTOR CONSTITUTIONAL AUDIT BREAK SUITE")
    print("Destruction Testing for Constitutional Sovereignty")
    print("=" * 70)

    results = {}

    try:
        results["VECTOR 1"] = test_vector1_genesis_deletion()
    except Exception as e:
        print(f"\n✗ VECTOR 1 EXCEPTION: {e}")
        results["VECTOR 1"] = False

    try:
        results["VECTOR 2"] = test_vector2_public_key_replacement()
    except Exception as e:
        print(f"\n✗ VECTOR 2 EXCEPTION: {e}")
        results["VECTOR 2"] = False

    try:
        results["VECTOR 11"] = test_vector11_full_wipe()
    except Exception as e:
        print(f"\n✗ VECTOR 11 EXCEPTION: {e}")
        results["VECTOR 11"] = False

    # Summary
    print("\n" + "=" * 70)
    print("CONSTITUTIONAL SOVEREIGNTY TEST RESULTS")
    print("=" * 70)

    for vector, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{vector}: {status}")

    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print(f"\nPassed: {passed_count}/{total_count}")

    if all(results.values()):
        print("\n🏆 CONSTITUTIONAL SOVEREIGNTY ACHIEVED")
        print("All attack vectors failed to compromise integrity")
        return 0
    else:
        print("\n⚠️  OPERATIONAL SOVEREIGN ONLY")
        print("Some attack vectors succeeded")
        return 1


if __name__ == "__main__":
    sys.exit(main())
