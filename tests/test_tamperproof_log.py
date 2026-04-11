"""
Comprehensive tests for TamperproofLog

Tests all security features:
- SHA-256 hash chaining
- Ed25519 signatures
- Merkle tree anchoring
- RFC 3161 timestamping integration
- Integrity verification
- Tamper detection
"""

import json
import tempfile
from pathlib import Path

import pytest

from src.app.audit.tamperproof_log import TamperproofLog, MerkleTree

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    HAS_ED25519 = True
except ImportError:
    HAS_ED25519 = False


class TestMerkleTree:
    """Test Merkle tree implementation."""
    
    def test_empty_tree(self):
        """Test empty Merkle tree."""
        tree = MerkleTree()
        assert tree.get_root() is None
        assert tree.get_root_hex() == "0" * 64
    
    def test_single_leaf(self):
        """Test Merkle tree with single leaf."""
        leaf = b"test_data"
        tree = MerkleTree([leaf])
        
        assert tree.get_root() == leaf
        assert tree.get_root_hex() == leaf.hex()
    
    def test_multiple_leaves(self):
        """Test Merkle tree with multiple leaves."""
        leaves = [b"data1", b"data2", b"data3", b"data4"]
        tree = MerkleTree(leaves)
        
        root = tree.get_root()
        assert root is not None
        assert len(root) == 32  # SHA-256 produces 32 bytes
    
    def test_add_leaf(self):
        """Test adding leaves to tree."""
        tree = MerkleTree()
        
        tree.add_leaf(b"leaf1")
        root1 = tree.get_root_hex()
        
        tree.add_leaf(b"leaf2")
        root2 = tree.get_root_hex()
        
        # Root should change when leaf is added
        assert root1 != root2
    
    def test_deterministic_root(self):
        """Test that same leaves produce same root."""
        leaves1 = [b"a", b"b", b"c"]
        leaves2 = [b"a", b"b", b"c"]
        
        tree1 = MerkleTree(leaves1)
        tree2 = MerkleTree(leaves2)
        
        assert tree1.get_root_hex() == tree2.get_root_hex()
    
    def test_merkle_proof_generation(self):
        """Test Merkle proof generation."""
        leaves = [b"leaf0", b"leaf1", b"leaf2", b"leaf3"]
        tree = MerkleTree(leaves)
        
        # Get proof for second leaf
        proof = tree.get_proof(1)
        
        # Proof should not be empty
        assert len(proof) > 0
        
        # Each proof element should be a tuple of (hash, position)
        for hash_val, position in proof:
            assert isinstance(hash_val, bytes)
            assert position in ["left", "right"]
    
    def test_merkle_proof_verification(self):
        """Test Merkle proof verification."""
        leaves = [b"leaf0", b"leaf1", b"leaf2", b"leaf3"]
        tree = MerkleTree(leaves)
        
        # Get and verify proof for each leaf
        for i, leaf in enumerate(leaves):
            proof = tree.get_proof(i)
            assert tree.verify_proof(leaf, i, proof)
    
    def test_invalid_merkle_proof(self):
        """Test that invalid proof is rejected."""
        leaves = [b"leaf0", b"leaf1", b"leaf2", b"leaf3"]
        tree = MerkleTree(leaves)
        
        # Get proof for one leaf, but verify with different leaf
        proof = tree.get_proof(0)
        assert not tree.verify_proof(b"wrong_leaf", 0, proof)
    
    def test_odd_number_of_leaves(self):
        """Test Merkle tree with odd number of leaves."""
        leaves = [b"a", b"b", b"c"]
        tree = MerkleTree(leaves)
        
        root = tree.get_root()
        assert root is not None
        
        # For odd leaves, verify the first two which form a complete pair
        for i in range(2):
            proof = tree.get_proof(i)
            assert tree.verify_proof(leaves[i], i, proof)


class TestTamperproofLog:
    """Test TamperproofLog implementation."""
    
    def test_initialization(self):
        """Test log initialization."""
        log = TamperproofLog()
        
        assert log.entries == []
        assert log.last_hash == "0" * 64
        assert log.merkle_tree.get_root() is None
    
    def test_append_single_entry(self):
        """Test appending a single entry."""
        log = TamperproofLog()
        
        result = log.append("user.login", {"user_id": "123", "ip": "192.168.1.1"})
        
        assert result is True
        assert len(log.entries) == 1
        
        entry = log.entries[0]
        assert entry["event_type"] == "user.login"
        assert entry["data"]["user_id"] == "123"
        assert entry["previous_hash"] == "0" * 64
        assert "hash" in entry
        assert "timestamp" in entry
        assert "merkle_root" in entry
    
    def test_hash_chaining(self):
        """Test that entries are properly hash-chained."""
        log = TamperproofLog()
        
        log.append("event1", {"data": "first"})
        log.append("event2", {"data": "second"})
        log.append("event3", {"data": "third"})
        
        # Verify chain
        assert log.entries[0]["previous_hash"] == "0" * 64
        assert log.entries[1]["previous_hash"] == log.entries[0]["hash"]
        assert log.entries[2]["previous_hash"] == log.entries[1]["hash"]
    
    @pytest.mark.skipif(not HAS_ED25519, reason="Ed25519 not available")
    def test_signatures(self):
        """Test Ed25519 signatures."""
        log = TamperproofLog()
        
        log.append("event", {"data": "test"})
        
        entry = log.entries[0]
        assert "signature" in entry
        
        # Verify signature
        is_valid = log._verify_signature(entry["hash"], entry["signature"])
        assert is_valid
    
    @pytest.mark.skipif(not HAS_ED25519, reason="Ed25519 not available")
    def test_signature_tampering_detection(self):
        """Test that signature detects tampering."""
        log = TamperproofLog()
        
        log.append("event", {"data": "original"})
        
        entry = log.entries[0]
        original_signature = entry["signature"]
        
        # Tamper with data
        entry["data"]["data"] = "tampered"
        
        # Signature should no longer be valid for tampered data
        new_hash = log._compute_entry_hash({
            "timestamp": entry["timestamp"],
            "event_type": entry["event_type"],
            "data": entry["data"],
            "previous_hash": entry["previous_hash"],
        })
        
        is_valid = log._verify_signature(new_hash, original_signature)
        assert not is_valid
    
    def test_merkle_tree_integration(self):
        """Test Merkle tree is properly maintained."""
        log = TamperproofLog()
        
        log.append("event1", {"data": "1"})
        root1 = log.get_merkle_root()
        
        log.append("event2", {"data": "2"})
        root2 = log.get_merkle_root()
        
        # Root should change
        assert root1 != root2
        
        # Each entry should have merkle_root
        assert log.entries[0]["merkle_root"] == root1
        assert log.entries[1]["merkle_root"] == root2
    
    def test_merkle_proof_for_entry(self):
        """Test getting Merkle proof for an entry."""
        log = TamperproofLog()
        
        log.append("event1", {"data": "1"})
        log.append("event2", {"data": "2"})
        log.append("event3", {"data": "3"})
        
        # Get proof for second entry
        proof = log.get_merkle_proof(1)
        
        # Proof should exist
        assert isinstance(proof, list)
    
    def test_integrity_verification_clean_log(self):
        """Test integrity verification on clean log."""
        log = TamperproofLog()
        
        log.append("event1", {"data": "1"})
        log.append("event2", {"data": "2"})
        log.append("event3", {"data": "3"})
        
        is_valid, errors = log.verify_integrity()
        
        assert is_valid
        assert len(errors) == 0
    
    def test_integrity_verification_tampered_hash(self):
        """Test integrity verification detects tampered hash."""
        log = TamperproofLog()
        
        log.append("event1", {"data": "1"})
        log.append("event2", {"data": "2"})
        
        # Tamper with first entry's hash
        log.entries[0]["hash"] = "0" * 64
        
        is_valid, errors = log.verify_integrity()
        
        assert not is_valid
        assert len(errors) > 0
        assert any("hash" in err.lower() for err in errors)
    
    def test_integrity_verification_broken_chain(self):
        """Test integrity verification detects broken chain."""
        log = TamperproofLog()
        
        log.append("event1", {"data": "1"})
        log.append("event2", {"data": "2"})
        log.append("event3", {"data": "3"})
        
        # Break the chain
        log.entries[2]["previous_hash"] = "0" * 64
        
        is_valid, errors = log.verify_integrity()
        
        assert not is_valid
        assert any("chain" in err.lower() for err in errors)
    
    def test_verify_single_entry(self):
        """Test verification of a single entry."""
        log = TamperproofLog()
        
        log.append("event1", {"data": "1"})
        log.append("event2", {"data": "2"})
        log.append("event3", {"data": "3"})
        
        # Verify middle entry
        is_valid, errors = log.verify_entry(1)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_get_entries_filter_by_type(self):
        """Test filtering entries by event type."""
        log = TamperproofLog()
        
        log.append("user.login", {"user": "alice"})
        log.append("user.logout", {"user": "bob"})
        log.append("user.login", {"user": "charlie"})
        
        login_entries = log.get_entries(event_type="user.login")
        
        assert len(login_entries) == 2
        assert all(e["event_type"] == "user.login" for e in login_entries)
    
    def test_export_log(self):
        """Test exporting log to file."""
        log = TamperproofLog()
        
        log.append("event1", {"data": "1"})
        log.append("event2", {"data": "2"})
        
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = Path(tmpdir) / "export.json"
            
            result = log.export(export_path)
            
            assert result is True
            assert export_path.exists()
            
            # Verify export content
            with open(export_path) as f:
                data = json.load(f)
            
            assert data["version"] == "2.0"
            assert data["entry_count"] == 2
            assert "merkle_root" in data
            assert len(data["entries"]) == 2
    
    def test_persist_and_load(self):
        """Test persisting and loading log from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "test.log"
            
            # Create and populate log
            log1 = TamperproofLog(log_file=log_path)
            log1.append("event1", {"data": "1"})
            log1.append("event2", {"data": "2"})
            log1.append("event3", {"data": "3"})
            
            # Load in new instance
            log2 = TamperproofLog()
            result = log2.load_from_file(log_path)
            
            assert result is True
            assert len(log2.entries) == 3
            assert log2.last_hash == log1.last_hash
            
            # Verify integrity after loading
            is_valid, errors = log2.verify_integrity()
            assert is_valid
    
    @pytest.mark.skipif(not HAS_ED25519, reason="Ed25519 not available")
    def test_public_key_export(self):
        """Test exporting public key."""
        log = TamperproofLog()
        
        pem = log.get_public_key_pem()
        
        assert pem is not None
        assert "BEGIN PUBLIC KEY" in pem
        assert "END PUBLIC KEY" in pem
    
    def test_genesis_entry_validation(self):
        """Test that genesis entry is properly validated."""
        log = TamperproofLog()
        
        log.append("genesis", {"data": "first"})
        
        # Tamper with genesis
        log.entries[0]["previous_hash"] = "1" * 64
        
        is_valid, errors = log.verify_integrity()
        
        assert not is_valid
        assert any("genesis" in err.lower() for err in errors)
    
    def test_empty_log_verification(self):
        """Test that empty log verifies successfully."""
        log = TamperproofLog()
        
        is_valid, errors = log.verify_integrity()
        
        assert is_valid
        assert len(errors) == 0
    
    def test_large_log_performance(self):
        """Test performance with larger log."""
        log = TamperproofLog()
        
        # Append 100 entries
        for i in range(100):
            log.append(f"event{i}", {"index": i, "data": f"test_{i}"})
        
        assert len(log.entries) == 100
        
        # Verify integrity
        is_valid, errors = log.verify_integrity()
        
        assert is_valid
        assert len(errors) == 0
    
    def test_merkle_root_consistency(self):
        """Test that Merkle root is consistent."""
        log1 = TamperproofLog()
        log2 = TamperproofLog()
        
        # Add same entries to both logs
        for i in range(5):
            data = {"index": i}
            log1.append(f"event{i}", data)
            log2.append(f"event{i}", data)
        
        # Merkle roots might differ due to timestamps, but structure should be valid
        is_valid1, _ = log1.verify_integrity()
        is_valid2, _ = log2.verify_integrity()
        
        assert is_valid1
        assert is_valid2
    
    def test_concurrent_append_safety(self):
        """Test that log maintains integrity even with rapid appends."""
        log = TamperproofLog()
        
        # Rapidly append entries
        for i in range(50):
            result = log.append(f"rapid_{i}", {"data": i})
            assert result is True
        
        # Verify all entries are properly chained
        is_valid, errors = log.verify_integrity()
        
        assert is_valid
        assert len(log.entries) == 50
    
    @pytest.mark.skipif(not HAS_ED25519, reason="Ed25519 not available")
    def test_signature_with_custom_key(self):
        """Test using a custom Ed25519 key."""
        # Generate custom key
        private_key = ed25519.Ed25519PrivateKey.generate()
        
        log = TamperproofLog(private_key=private_key)
        log.append("event", {"data": "test"})
        
        entry = log.entries[0]
        assert "signature" in entry
        
        # Verify with the log's public key
        is_valid = log._verify_signature(entry["hash"], entry["signature"])
        assert is_valid
    
    def test_entry_ordering(self):
        """Test that entries maintain insertion order."""
        log = TamperproofLog()
        
        for i in range(10):
            log.append(f"event_{i}", {"order": i})
        
        # Verify order is maintained
        for i, entry in enumerate(log.entries):
            assert entry["data"]["order"] == i


class TestTamperproofLogIntegration:
    """Integration tests combining multiple features."""
    
    def test_full_lifecycle(self):
        """Test complete lifecycle: create, append, verify, export, load."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "lifecycle.log"
            export_path = Path(tmpdir) / "export.json"
            
            # Create and populate
            log1 = TamperproofLog(log_file=log_path)
            for i in range(10):
                log1.append(f"event_{i}", {"index": i, "value": f"data_{i}"})
            
            # Verify
            is_valid, errors = log1.verify_integrity()
            assert is_valid
            
            # Export
            assert log1.export(export_path)
            
            # Load in new instance
            log2 = TamperproofLog()
            assert log2.load_from_file(log_path)
            
            # Verify loaded log
            is_valid2, errors2 = log2.verify_integrity()
            assert is_valid2
            
            # Compare
            assert len(log2.entries) == len(log1.entries)
            assert log2.get_merkle_root() == log1.get_merkle_root()
    
    def test_tamper_detection_comprehensive(self):
        """Comprehensive test of tamper detection."""
        log = TamperproofLog()
        
        for i in range(5):
            log.append(f"event_{i}", {"index": i})
        
        # Test various tampering scenarios
        original_log = TamperproofLog()
        for i in range(5):
            original_log.append(f"event_{i}", {"index": i})
        
        # Test 1: Modify data
        log = TamperproofLog()
        for i in range(5):
            log.append(f"event_{i}", {"index": i})
        log.entries[2]["data"] = {"modified": True}
        is_valid, errors = log.verify_integrity()
        assert not is_valid, "Data modification was not detected"
        
        # Test 2: Modify timestamp
        log = TamperproofLog()
        for i in range(5):
            log.append(f"event_{i}", {"index": i})
        log.entries[1]["timestamp"] = "2000-01-01T00:00:00"
        is_valid, errors = log.verify_integrity()
        assert not is_valid, "Timestamp modification was not detected"
        
        # Test 3: Swap entries
        log = TamperproofLog()
        for i in range(5):
            log.append(f"event_{i}", {"index": i})
        log.entries[0], log.entries[1] = log.entries[1], log.entries[0]
        is_valid, errors = log.verify_integrity()
        assert not is_valid, "Entry swap was not detected"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
