# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_privacy_ledger.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_privacy_ledger.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Comprehensive tests for Privacy Accountability Ledger
Tests all production-grade features including encryption, integrity, and thread-safety
"""

import unittest
import tempfile
import time
import threading
import json
import os

from thirstys_waterfall.security.privacy_ledger import (
    PrivacyLedger,
    LedgerEntry,
    EventType,
    SeverityLevel,
    MerkleTree,
)


class TestLedgerEntry(unittest.TestCase):
    """Test LedgerEntry dataclass"""

    def test_entry_creation(self):
        """Test basic entry creation"""
        entry = LedgerEntry(
            event_type=EventType.USER_LOGIN,
            severity=SeverityLevel.INFO,
            user_id="user123",
            action="User logged in",
            resource="auth_system",
        )

        self.assertEqual(entry.event_type, EventType.USER_LOGIN)
        self.assertEqual(entry.severity, SeverityLevel.INFO)
        self.assertEqual(entry.user_id, "user123")
        self.assertIsNotNone(entry.entry_id)
        self.assertIsNotNone(entry.timestamp)
        self.assertIsNotNone(entry.hash)

    def test_entry_hash_computation(self):
        """Test cryptographic hash computation"""
        entry = LedgerEntry(
            event_type=EventType.DATA_ACCESS,
            user_id="user123",
            action="Accessed data",
            previous_hash="abc123",
        )

        hash1 = entry.compute_hash()
        hash2 = entry.compute_hash()

        # Hash should be deterministic
        self.assertEqual(hash1, hash2)

        # Hash should be SHA-512 (128 hex characters)
        self.assertEqual(len(hash1), 128)

    def test_entry_integrity_verification(self):
        """Test entry integrity verification"""
        entry = LedgerEntry(
            event_type=EventType.DATA_MODIFICATION,
            user_id="user123",
            action="Modified data",
        )

        # Should verify successfully
        self.assertTrue(entry.verify_integrity())

        # Tamper with entry
        entry.action = "Tampered action"

        # Should fail verification
        self.assertFalse(entry.verify_integrity())

    def test_entry_serialization(self):
        """Test entry serialization to/from dict"""
        original = LedgerEntry(
            event_type=EventType.SECURITY_ALERT,
            severity=SeverityLevel.CRITICAL,
            user_id="admin",
            action="Security breach detected",
            metadata={"ip": "1.2.3.4", "attempts": 5},
        )

        # Convert to dict
        entry_dict = original.to_dict()

        # Reconstruct from dict
        restored = LedgerEntry.from_dict(entry_dict)

        self.assertEqual(restored.entry_id, original.entry_id)
        self.assertEqual(restored.event_type, original.event_type)
        self.assertEqual(restored.severity, original.severity)
        self.assertEqual(restored.user_id, original.user_id)
        self.assertEqual(restored.action, original.action)
        self.assertEqual(restored.metadata, original.metadata)


class TestMerkleTree(unittest.TestCase):
    """Test Merkle tree implementation"""

    def test_merkle_tree_creation(self):
        """Test Merkle tree basic creation"""
        tree = MerkleTree()

        # Empty tree
        self.assertIsNone(tree.get_root())

        # Add leaves
        tree.add_leaf("hash1")
        self.assertIsNotNone(tree.get_root())

        tree.add_leaf("hash2")
        tree.add_leaf("hash3")

        self.assertEqual(len(tree.leaves), 3)
        self.assertIsNotNone(tree.get_root())

    def test_merkle_proof_generation(self):
        """Test Merkle proof generation"""
        tree = MerkleTree()

        # Add multiple leaves
        hashes = [f"hash{i}" for i in range(8)]
        for h in hashes:
            tree.add_leaf(h)

        # Generate proofs
        for i in range(len(hashes)):
            proof = tree.get_proof(i)
            self.assertIsInstance(proof, list)
            # Proof length should be log2(n)
            self.assertGreater(len(proof), 0)

    def test_merkle_proof_verification(self):
        """Test Merkle proof verification"""
        tree = MerkleTree()

        # Add leaves
        hashes = ["hash1", "hash2", "hash3", "hash4"]
        for h in hashes:
            tree.add_leaf(h)

        root = tree.get_root()

        # Verify each leaf
        for i, h in enumerate(hashes):
            proof = tree.get_proof(i)
            is_valid = tree.verify_proof(h, proof, root, i)  # Pass leaf index
            self.assertTrue(is_valid, f"Proof verification failed for leaf {i}")

    def test_merkle_tree_rebuild(self):
        """Test that Merkle tree rebuilds correctly"""
        tree = MerkleTree()

        # Add initial leaves
        tree.add_leaf("hash1")
        tree.add_leaf("hash2")
        root1 = tree.get_root()

        # Add more leaves
        tree.add_leaf("hash3")
        root2 = tree.get_root()

        # Roots should be different
        self.assertNotEqual(root1, root2)


class TestPrivacyLedger(unittest.TestCase):
    """Test PrivacyLedger main functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Create temporary storage
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = os.path.join(self.temp_dir, "test_ledger.dat")

    def tearDown(self):
        """Clean up test fixtures"""
        # Clean up temp files
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_ledger_initialization(self):
        """Test ledger initialization"""
        ledger = PrivacyLedger(self.storage_path)

        self.assertIsNotNone(ledger.encryption_key)
        self.assertEqual(len(ledger.entries), 0)
        self.assertTrue(ledger.chain_verified)

        ledger.close()

    def test_ledger_append_entry(self):
        """Test appending entries to ledger"""
        ledger = PrivacyLedger(self.storage_path)

        # Append entry
        entry = ledger.append(
            event_type=EventType.USER_LOGIN,
            user_id="testuser",
            action="User login successful",
            resource="auth_system",
            severity=SeverityLevel.INFO,
        )

        self.assertIsNotNone(entry)
        self.assertEqual(entry.event_type, EventType.USER_LOGIN)
        self.assertEqual(len(ledger.entries), 1)

        # Entry should be encrypted
        self.assertTrue(entry.encrypted)
        self.assertNotEqual(entry.user_id, "testuser")  # Should be encrypted

        ledger.close()

    def test_ledger_chain_integrity(self):
        """Test ledger chain integrity"""
        ledger = PrivacyLedger(self.storage_path)

        # Append multiple entries
        for i in range(5):
            ledger.append(
                event_type=EventType.DATA_ACCESS,
                user_id=f"user{i}",
                action=f"Action {i}",
                resource=f"resource{i}",
            )

        # Verify chain integrity
        is_valid, errors = ledger.verify_chain_integrity()

        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        ledger.close()

    def test_ledger_tamper_detection(self):
        """Test tamper detection"""
        ledger = PrivacyLedger(self.storage_path)

        # Append entries
        ledger.append(
            event_type=EventType.DATA_ACCESS, user_id="user1", action="Action 1"
        )
        ledger.append(
            event_type=EventType.DATA_ACCESS, user_id="user2", action="Action 2"
        )

        # Tamper with an entry
        ledger.entries[0].action = "TAMPERED"

        # Verify should fail
        is_valid, errors = ledger.verify_chain_integrity()

        self.assertFalse(is_valid)
        self.assertGreater(len(errors), 0)

        ledger.close()

    def test_ledger_encryption(self):
        """Test zero-knowledge encryption"""
        # Create ledger with specific key
        from cryptography.fernet import Fernet

        key = Fernet.generate_key()

        ledger = PrivacyLedger(self.storage_path, encryption_key=key)

        # Append entry
        entry = ledger.append(
            event_type=EventType.DATA_ACCESS,
            user_id="sensitive_user",
            action="Accessed sensitive data",
        )

        # User ID should be encrypted
        self.assertNotEqual(entry.user_id, "sensitive_user")

        # Should be able to decrypt
        decrypted = ledger._decrypt_field(entry.user_id)
        self.assertEqual(decrypted, "sensitive_user")

        ledger.close()

    def test_ledger_search(self):
        """Test ledger search functionality"""
        ledger = PrivacyLedger(self.storage_path)

        # Append various entries
        ledger.append(
            event_type=EventType.USER_LOGIN,
            user_id="user1",
            action="Login",
            severity=SeverityLevel.INFO,
        )
        ledger.append(
            event_type=EventType.DATA_ACCESS,
            user_id="user2",
            action="Data access",
            severity=SeverityLevel.WARNING,
        )
        ledger.append(
            event_type=EventType.USER_LOGIN,
            user_id="user1",
            action="Login again",
            severity=SeverityLevel.INFO,
        )

        # Search by user
        results = ledger.search(user_id="user1")
        self.assertEqual(len(results), 2)

        # Search by event type
        results = ledger.search(event_type=EventType.DATA_ACCESS)
        self.assertEqual(len(results), 1)

        # Search by severity
        results = ledger.search(severity=SeverityLevel.WARNING)
        self.assertEqual(len(results), 1)

        ledger.close()

    def test_ledger_time_range_search(self):
        """Test time range search"""
        ledger = PrivacyLedger(self.storage_path)

        start_time = time.time()

        # Append entry
        ledger.append(
            event_type=EventType.DATA_ACCESS, user_id="user1", action="Action 1"
        )

        time.sleep(0.1)
        mid_time = time.time()
        time.sleep(0.1)

        # Append another entry
        ledger.append(
            event_type=EventType.DATA_ACCESS, user_id="user2", action="Action 2"
        )

        end_time = time.time()

        # Search before mid_time
        results = ledger.search(start_time=start_time, end_time=mid_time)
        self.assertEqual(len(results), 1)

        # Search after mid_time
        results = ledger.search(start_time=mid_time, end_time=end_time)
        self.assertEqual(len(results), 1)

        ledger.close()

    def test_ledger_persistence(self):
        """Test ledger persistence and loading"""
        # Create ledger and add entries
        ledger1 = PrivacyLedger(self.storage_path)

        entry_id = ledger1.append(
            event_type=EventType.DATA_ACCESS, user_id="user1", action="Persisted action"
        ).entry_id

        ledger1.close()

        # Create new ledger instance (should load from disk)
        ledger2 = PrivacyLedger(
            self.storage_path, encryption_key=ledger1.encryption_key
        )

        self.assertEqual(len(ledger2.entries), 1)

        # Verify entry was loaded correctly
        loaded_entry = ledger2.get_entry(entry_id)
        self.assertIsNotNone(loaded_entry)

        ledger2.close()

    def test_ledger_thread_safety(self):
        """Test thread-safe operations"""
        ledger = PrivacyLedger(self.storage_path)

        errors = []

        def append_entries(thread_id):
            try:
                for i in range(10):
                    ledger.append(
                        event_type=EventType.DATA_ACCESS,
                        user_id=f"user_{thread_id}",
                        action=f"Action {i} from thread {thread_id}",
                    )
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=append_entries, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # No errors should occur
        self.assertEqual(len(errors), 0)

        # Should have all entries
        self.assertEqual(len(ledger.entries), 50)

        # Chain should still be valid
        is_valid, _ = ledger.verify_chain_integrity()
        self.assertTrue(is_valid)

        ledger.close()

    def test_ledger_retention_policy(self):
        """Test retention policy enforcement"""
        # Create ledger with short retention (1 second for testing)
        ledger = PrivacyLedger(
            self.storage_path,
            retention_days=0,  # Retention of 0 days = 1 second threshold
        )

        # Add entry with old timestamp (2 seconds ago)
        entry = LedgerEntry(
            event_type=EventType.DATA_ACCESS,
            user_id="old_user",
            action="Old action",
            timestamp=time.time() - 2,  # 2 seconds ago
        )
        entry.hash = entry.compute_hash()

        ledger.entries.append(entry)
        ledger.entry_index[entry.entry_id] = entry
        ledger.merkle_tree.add_leaf(entry.hash)

        initial_count = len(ledger.entries)

        # Enforce retention policy
        ledger._enforce_retention_policy()

        # Entry should be deleted
        self.assertLess(len(ledger.entries), initial_count)

        ledger.close()

    def test_ledger_merkle_tree_integration(self):
        """Test Merkle tree integration"""
        ledger = PrivacyLedger(self.storage_path)

        # Append entries
        entries = []
        for i in range(10):
            entry = ledger.append(
                event_type=EventType.DATA_ACCESS,
                user_id=f"user{i}",
                action=f"Action {i}",
            )
            entries.append(entry)

        # Verify Merkle proofs
        root = ledger.merkle_tree.get_root()
        self.assertIsNotNone(root)

        for i, entry in enumerate(entries):
            # Get the merkle index from metadata
            merkle_idx = entry.metadata.get("_merkle_index", i)

            # Generate fresh proof for current tree state
            fresh_proof = ledger.merkle_tree.get_proof(merkle_idx)

            # Verify proof
            is_valid = ledger.merkle_tree.verify_proof(
                entry.hash, fresh_proof, root, merkle_idx
            )
            self.assertTrue(is_valid, f"Merkle proof invalid for entry {i}")

        ledger.close()

    def test_ledger_statistics(self):
        """Test ledger statistics"""
        ledger = PrivacyLedger(self.storage_path)

        # Append some entries
        for i in range(5):
            ledger.append(
                event_type=EventType.DATA_ACCESS,
                user_id=f"user{i}",
                action=f"Action {i}",
            )

        stats = ledger.get_stats()

        self.assertEqual(stats["total_entries"], 5)
        self.assertEqual(stats["current_entries"], 5)
        self.assertEqual(stats["encrypted_entries"], 5)
        self.assertTrue(stats["chain_verified"])
        self.assertIsNotNone(stats["merkle_root"])

        ledger.close()

    def test_ledger_export_audit_log(self):
        """Test audit log export"""
        ledger = PrivacyLedger(self.storage_path)

        # Append entries
        ledger.append(event_type=EventType.USER_LOGIN, user_id="user1", action="Login")
        ledger.append(
            event_type=EventType.DATA_ACCESS, user_id="user2", action="Data access"
        )

        # Export audit log
        export_path = os.path.join(self.temp_dir, "audit_export.json")
        count = ledger.export_audit_log(export_path, decrypt_sensitive=True)

        self.assertEqual(count, 2)
        self.assertTrue(os.path.exists(export_path))

        # Verify export format
        with open(export_path, "r") as f:
            export_data = json.load(f)

        self.assertIn("export_time", export_data)
        self.assertIn("entry_count", export_data)
        self.assertIn("entries", export_data)
        self.assertEqual(export_data["entry_count"], 2)

        ledger.close()

    def test_ledger_secure_deletion(self):
        """Test secure deletion of entries"""
        ledger = PrivacyLedger(self.storage_path)

        # Append entries
        entries = []
        for i in range(5):
            entry = ledger.append(
                event_type=EventType.DATA_ACCESS,
                user_id=f"user{i}",
                action=f"Action {i}",
            )
            entries.append(entry)

        # Secure delete first 2 entries
        ledger._secure_delete_entries(entries[:2])

        # Should have 3 entries left
        self.assertEqual(len(ledger.entries), 3)

        # Deleted entries should not be in index
        self.assertNotIn(entries[0].entry_id, ledger.entry_index)
        self.assertNotIn(entries[1].entry_id, ledger.entry_index)

        ledger.close()

    def test_ledger_get_entry(self):
        """Test retrieving specific entry"""
        ledger = PrivacyLedger(self.storage_path)

        # Append entry
        entry = ledger.append(
            event_type=EventType.SECURITY_ALERT,
            user_id="admin",
            action="Security alert",
        )

        # Retrieve entry
        retrieved = ledger.get_entry(entry.entry_id)

        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.entry_id, entry.entry_id)
        self.assertEqual(retrieved.action, entry.action)

        # Non-existent entry
        non_existent = ledger.get_entry("nonexistent_id")
        self.assertIsNone(non_existent)

        ledger.close()


class TestPrivacyLedgerIntegration(unittest.TestCase):
    """Integration tests for complete workflows"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage_path = os.path.join(self.temp_dir, "test_ledger.dat")

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_complete_audit_workflow(self):
        """Test complete audit workflow"""
        ledger = PrivacyLedger(self.storage_path)

        # Simulate user session
        # 1. User login
        ledger.append(
            event_type=EventType.USER_LOGIN,
            user_id="john.doe",
            action="User logged in via OAuth",
            resource="auth_system",
            severity=SeverityLevel.INFO,
            metadata={"ip": "192.168.1.100", "device": "Chrome/Linux"},
        )

        # 2. Data access
        ledger.append(
            event_type=EventType.DATA_ACCESS,
            user_id="john.doe",
            action="Accessed customer records",
            resource="customer_db",
            severity=SeverityLevel.INFO,
            metadata={"records_accessed": 5},
        )

        # 3. Data modification
        ledger.append(
            event_type=EventType.DATA_MODIFICATION,
            user_id="john.doe",
            action="Updated customer address",
            resource="customer_db",
            severity=SeverityLevel.WARNING,
            metadata={"customer_id": "CUST-12345"},
        )

        # 4. Security alert
        ledger.append(
            event_type=EventType.SECURITY_ALERT,
            user_id="john.doe",
            action="Failed permission check",
            resource="admin_panel",
            severity=SeverityLevel.ERROR,
            metadata={"attempted_action": "delete_user"},
        )

        # 5. User logout
        ledger.append(
            event_type=EventType.USER_LOGOUT,
            user_id="john.doe",
            action="User logged out",
            resource="auth_system",
            severity=SeverityLevel.INFO,
        )

        # Verify chain integrity
        is_valid, errors = ledger.verify_chain_integrity()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

        # Search user activity
        user_activity = ledger.search(user_id="john.doe")
        self.assertEqual(len(user_activity), 5)

        # Search security alerts
        alerts = ledger.search(user_id="john.doe", event_type=EventType.SECURITY_ALERT)
        self.assertEqual(len(alerts), 1)

        # Export audit trail
        export_path = os.path.join(self.temp_dir, "audit_trail.json")
        count = ledger.export_audit_log(
            export_path, user_id="john.doe", decrypt_sensitive=True
        )
        self.assertEqual(count, 5)

        # Get statistics
        stats = ledger.get_stats()
        self.assertEqual(stats["total_entries"], 6)  # +1 for export action

        ledger.close()

    def test_multi_user_audit_workflow(self):
        """Test audit workflow with multiple users"""
        ledger = PrivacyLedger(self.storage_path)

        users = ["alice", "bob", "charlie"]

        # Each user performs actions
        for user in users:
            ledger.append(
                event_type=EventType.USER_LOGIN,
                user_id=user,
                action=f"{user} logged in",
            )

            ledger.append(
                event_type=EventType.DATA_ACCESS,
                user_id=user,
                action=f"{user} accessed data",
            )

            ledger.append(
                event_type=EventType.USER_LOGOUT,
                user_id=user,
                action=f"{user} logged out",
            )

        # Verify total entries
        self.assertEqual(len(ledger.entries), 9)

        # Search each user's activity
        for user in users:
            activity = ledger.search(user_id=user)
            self.assertEqual(len(activity), 3)

        # Verify chain integrity
        is_valid, _ = ledger.verify_chain_integrity()
        self.assertTrue(is_valid)

        ledger.close()


if __name__ == "__main__":
    unittest.main()
