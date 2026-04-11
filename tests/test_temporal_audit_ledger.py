#                                           [2026-03-05 09:25]
#                                          Productivity: Active
"""
Temporal Audit Ledger Tests - Comprehensive tests including tamper detection.

Tests:
- Basic ledger operations
- Hash chain integrity
- Merkle tree construction and verification
- Ed25519 signature verification
- Tamper detection (hash, signature, chain modification)
- RFC 3161 timestamp integration
- Proof generation and verification
"""

import pytest
import json
import hashlib
import tempfile
from pathlib import Path
from datetime import datetime, timezone

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'governance'))

from temporal_audit_ledger import (
    TemporalAuditLedger,
    AuditEntry,
    AuditEventType,
    MerkleTree,
    RFC3161TimestampClient,
    create_ledger,
    generate_signing_keypair,
    save_keypair,
    load_private_key,
    load_public_key,
)


@pytest.fixture
def temp_ledger_path(tmp_path):
    """Create temporary ledger path."""
    return tmp_path / "test_ledger.json"


@pytest.fixture
def ledger(temp_ledger_path):
    """Create fresh ledger for testing."""
    return create_ledger(temp_ledger_path)


class TestBasicOperations:
    """Test basic ledger operations."""
    
    def test_create_ledger(self, temp_ledger_path):
        """Test ledger creation."""
        ledger = create_ledger(temp_ledger_path)
        
        assert ledger is not None
        assert len(ledger.entries) == 0
        assert ledger.signing_key is not None
        assert ledger.verify_key is not None
    
    def test_append_entry(self, ledger):
        """Test appending audit entry."""
        entry = ledger.append(
            event_type=AuditEventType.TEMPORAL_WORKFLOW_START,
            actor="test_actor",
            action="start_workflow",
            resource="workflow_123",
            metadata={"workflow_id": "123", "input": "test"},
        )
        
        assert entry.sequence_number == 0
        assert entry.event_type == AuditEventType.TEMPORAL_WORKFLOW_START.value
        assert entry.actor == "test_actor"
        assert entry.action == "start_workflow"
        assert entry.resource == "workflow_123"
        assert entry.metadata["workflow_id"] == "123"
        assert entry.entry_hash != ""
        assert entry.signature != ""
        assert entry.previous_hash == ""  # First entry
    
    def test_multiple_entries(self, ledger):
        """Test appending multiple entries."""
        for i in range(5):
            ledger.append(
                event_type=AuditEventType.GOVERNANCE_DECISION,
                actor=f"actor_{i}",
                action=f"action_{i}",
                resource=f"resource_{i}",
            )
        
        assert len(ledger.entries) == 5
        
        # Verify sequence numbers
        for i, entry in enumerate(ledger.entries):
            assert entry.sequence_number == i
    
    def test_persistence(self, temp_ledger_path):
        """Test ledger persistence."""
        # Create ledger and add entries
        ledger1 = create_ledger(temp_ledger_path)
        ledger1.append(
            event_type=AuditEventType.POLICY_CHANGE,
            actor="admin",
            action="update_policy",
            resource="policy_1",
        )
        
        # Load ledger from file
        ledger2 = create_ledger(temp_ledger_path)
        
        assert len(ledger2.entries) == 1
        assert ledger2.entries[0].actor == "admin"
        assert ledger2.entries[0].action == "update_policy"


class TestHashChain:
    """Test hash chain integrity."""
    
    def test_hash_computation(self, ledger):
        """Test entry hash computation."""
        entry = ledger.append(
            event_type=AuditEventType.AUTHENTICATION,
            actor="user1",
            action="login",
            resource="system",
        )
        
        # Recompute hash
        computed_hash = entry.compute_hash()
        
        assert computed_hash == entry.entry_hash
        assert len(entry.entry_hash) == 64  # SHA-256 hex
    
    def test_chain_linking(self, ledger):
        """Test hash chain linking."""
        entry1 = ledger.append(
            event_type=AuditEventType.DATA_ACCESS,
            actor="user1",
            action="read",
            resource="file1",
        )
        
        entry2 = ledger.append(
            event_type=AuditEventType.DATA_ACCESS,
            actor="user2",
            action="write",
            resource="file2",
        )
        
        # Verify chain link
        assert entry2.previous_hash == entry1.entry_hash
        assert entry2.previous_hash != ""
    
    def test_chain_verification(self, ledger):
        """Test chain verification."""
        # Add multiple entries
        for i in range(10):
            ledger.append(
                event_type=AuditEventType.CONFIGURATION_CHANGE,
                actor=f"user{i}",
                action="update",
                resource=f"config{i}",
            )
        
        # Verify chain
        is_valid, errors = ledger.verify_chain()
        
        assert is_valid is True
        assert len(errors) == 0


class TestSignatures:
    """Test Ed25519 signature verification."""
    
    def test_entry_signing(self, ledger):
        """Test entry signing."""
        entry = ledger.append(
            event_type=AuditEventType.SECURITY_EVENT,
            actor="system",
            action="alert",
            resource="firewall",
        )
        
        # Verify signature
        is_valid, errors = ledger.verify_entry(entry)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_signature_verification_failure(self, ledger):
        """Test signature verification fails for tampered entry."""
        entry = ledger.append(
            event_type=AuditEventType.SYSTEM_ERROR,
            actor="system",
            action="error",
            resource="component",
        )
        
        # Tamper with entry hash (but not signature)
        original_hash = entry.entry_hash
        entry.entry_hash = "tampered_hash_" + "0" * 48
        
        # Verification should fail
        is_valid, errors = ledger.verify_entry(entry)
        
        assert is_valid is False
        assert len(errors) > 0
        
        # Restore for cleanup
        entry.entry_hash = original_hash


class TestMerkleTree:
    """Test Merkle tree construction and verification."""
    
    def test_merkle_tree_construction(self):
        """Test Merkle tree construction."""
        leaves = [
            hashlib.sha256(f"leaf{i}".encode()).hexdigest()
            for i in range(8)
        ]
        
        tree = MerkleTree(leaves)
        
        assert tree.root != ""
        assert len(tree.root) == 64  # SHA-256 hex
    
    def test_merkle_proof_generation(self):
        """Test Merkle proof generation."""
        leaves = [
            hashlib.sha256(f"leaf{i}".encode()).hexdigest()
            for i in range(8)
        ]
        
        tree = MerkleTree(leaves)
        
        # Get proof for first leaf
        proof = tree.get_proof(0)
        
        assert len(proof) > 0
        assert all(isinstance(p, tuple) and len(p) == 2 for p in proof)
    
    def test_merkle_proof_verification(self):
        """Test Merkle proof verification."""
        leaves = [
            hashlib.sha256(f"leaf{i}".encode()).hexdigest()
            for i in range(8)
        ]
        
        tree = MerkleTree(leaves)
        
        # Verify proof for each leaf
        for i, leaf in enumerate(leaves):
            proof = tree.get_proof(i)
            is_valid = MerkleTree.verify_proof(leaf, proof, tree.root)
            
            assert is_valid is True
    
    def test_merkle_proof_invalid(self):
        """Test Merkle proof verification fails for wrong leaf."""
        leaves = [
            hashlib.sha256(f"leaf{i}".encode()).hexdigest()
            for i in range(8)
        ]
        
        tree = MerkleTree(leaves)
        
        # Get proof for leaf 0
        proof = tree.get_proof(0)
        
        # Try to verify with wrong leaf
        wrong_leaf = hashlib.sha256(b"wrong").hexdigest()
        is_valid = MerkleTree.verify_proof(wrong_leaf, proof, tree.root)
        
        assert is_valid is False


class TestMerkleCheckpoints:
    """Test Merkle checkpoint creation and verification."""
    
    def test_create_checkpoint(self, ledger):
        """Test checkpoint creation."""
        # Add entries
        for i in range(10):
            ledger.append(
                event_type=AuditEventType.CUSTOM,
                actor=f"user{i}",
                action="action",
                resource=f"res{i}",
            )
        
        # Create checkpoint
        root = ledger.create_merkle_checkpoint()
        
        assert root != ""
        assert len(root) == 64
        assert len(ledger.merkle_roots) > 0
    
    def test_get_merkle_proof(self, ledger):
        """Test getting Merkle proof from ledger."""
        # Add entries
        for i in range(10):
            ledger.append(
                event_type=AuditEventType.CUSTOM,
                actor=f"user{i}",
                action="action",
                resource=f"res{i}",
            )
        
        # Create checkpoint
        ledger.create_merkle_checkpoint()
        
        # Get proof for entry 5
        proof_data = ledger.get_merkle_proof(5)
        
        assert proof_data is not None
        assert proof_data["sequence_number"] == 5
        assert "proof" in proof_data
        assert "merkle_root" in proof_data
    
    def test_verify_merkle_proof(self, ledger):
        """Test verifying Merkle proof."""
        # Add entries
        for i in range(10):
            ledger.append(
                event_type=AuditEventType.CUSTOM,
                actor=f"user{i}",
                action="action",
                resource=f"res{i}",
            )
        
        # Create checkpoint
        ledger.create_merkle_checkpoint()
        
        # Verify proofs for all entries
        for i in range(10):
            proof_data = ledger.get_merkle_proof(i)
            is_valid = ledger.verify_merkle_proof(proof_data)
            
            assert is_valid is True


class TestTamperDetection:
    """Test tamper detection capabilities."""
    
    def test_detect_hash_tampering(self, ledger):
        """Test detection of hash tampering."""
        # Add entries
        for i in range(5):
            ledger.append(
                event_type=AuditEventType.CUSTOM,
                actor=f"user{i}",
                action="action",
                resource=f"res{i}",
            )
        
        # Tamper with hash
        original_hash = ledger.entries[2].entry_hash
        ledger.entries[2].entry_hash = "tampered_hash_" + "0" * 48
        
        # Detect tampering
        is_tampered, issues = ledger.detect_tampering()
        
        assert is_tampered is True
        assert len(issues) > 0
        
        # Restore
        ledger.entries[2].entry_hash = original_hash
    
    def test_detect_chain_break(self, ledger):
        """Test detection of chain break."""
        # Add entries
        for i in range(5):
            ledger.append(
                event_type=AuditEventType.CUSTOM,
                actor=f"user{i}",
                action="action",
                resource=f"res{i}",
            )
        
        # Break chain
        original_prev = ledger.entries[2].previous_hash
        ledger.entries[2].previous_hash = "broken_chain_" + "0" * 48
        
        # Detect tampering
        is_tampered, issues = ledger.detect_tampering()
        
        assert is_tampered is True
        assert len(issues) > 0
        
        # Restore
        ledger.entries[2].previous_hash = original_prev
    
    def test_detect_signature_tampering(self, ledger):
        """Test detection of signature tampering."""
        # Add entries
        for i in range(5):
            ledger.append(
                event_type=AuditEventType.CUSTOM,
                actor=f"user{i}",
                action="action",
                resource=f"res{i}",
            )
        
        # Tamper with signature
        original_sig = ledger.entries[2].signature
        ledger.entries[2].signature = "tampered_sig_" + "0" * 100
        
        # Detect tampering
        is_tampered, issues = ledger.detect_tampering()
        
        assert is_tampered is True
        assert len(issues) > 0
        
        # Restore
        ledger.entries[2].signature = original_sig
    
    def test_detect_content_modification(self, ledger):
        """Test detection of content modification."""
        # Add entries
        for i in range(5):
            ledger.append(
                event_type=AuditEventType.CUSTOM,
                actor=f"user{i}",
                action="action",
                resource=f"res{i}",
            )
        
        # Modify content (but keep hash)
        ledger.entries[2].actor = "TAMPERED_ACTOR"
        
        # Detect tampering (hash won't match content)
        is_tampered, issues = ledger.detect_tampering()
        
        assert is_tampered is True
        assert len(issues) > 0
    
    def test_detect_merkle_checkpoint_tampering(self, ledger):
        """Test detection of Merkle checkpoint tampering."""
        # Add entries
        for i in range(10):
            ledger.append(
                event_type=AuditEventType.CUSTOM,
                actor=f"user{i}",
                action="action",
                resource=f"res{i}",
            )
        
        # Create checkpoint
        ledger.create_merkle_checkpoint()
        
        # Tamper with checkpoint
        checkpoint_key = list(ledger.merkle_roots.keys())[0]
        original_root = ledger.merkle_roots[checkpoint_key]
        ledger.merkle_roots[checkpoint_key] = "tampered_root_" + "0" * 48
        
        # Detect tampering
        is_tampered, issues = ledger.detect_tampering()
        
        assert is_tampered is True
        assert len(issues) > 0
        
        # Restore
        ledger.merkle_roots[checkpoint_key] = original_root
    
    def test_instant_tamper_detection(self, ledger):
        """Test instant tamper detection."""
        # Add entries
        for i in range(100):
            ledger.append(
                event_type=AuditEventType.CUSTOM,
                actor=f"user{i}",
                action="action",
                resource=f"res{i}",
            )
        
        # Create checkpoint
        ledger.create_merkle_checkpoint()
        
        # Verify no tampering
        is_tampered, issues = ledger.detect_tampering()
        assert is_tampered is False
        
        # Tamper with middle entry
        ledger.entries[50].metadata["tampered"] = True
        
        # Should detect instantly
        is_tampered, issues = ledger.detect_tampering()
        assert is_tampered is True
        assert len(issues) > 0


class TestRFC3161Timestamps:
    """Test RFC 3161 timestamp integration."""
    
    def test_tsa_client_creation(self):
        """Test TSA client creation."""
        client = RFC3161TimestampClient()
        
        assert client.tsa_url is not None
        assert client.tsa_url in RFC3161TimestampClient.PUBLIC_TSA_URLS
    
    def test_timestamp_request(self):
        """Test timestamp request."""
        client = RFC3161TimestampClient()
        
        # Create test hash
        test_hash = hashlib.sha256(b"test_data").hexdigest()
        
        # Request timestamp
        result = client.get_timestamp(test_hash)
        
        assert result is not None
        assert "timestamp" in result
        assert "hash" in result
        assert result["hash"] == test_hash
    
    def test_ledger_entry_with_timestamp(self, ledger):
        """Test ledger entry with TSA timestamp."""
        entry = ledger.append(
            event_type=AuditEventType.GOVERNANCE_DECISION,
            actor="admin",
            action="critical_decision",
            resource="policy",
            request_tsa_timestamp=True,
        )
        
        assert entry.tsa_timestamp is not None
        assert entry.tsa_timestamp_dt is not None
    
    def test_merkle_checkpoint_with_timestamp(self, ledger):
        """Test Merkle checkpoint with TSA timestamp."""
        # Add entries
        for i in range(10):
            ledger.append(
                event_type=AuditEventType.CUSTOM,
                actor=f"user{i}",
                action="action",
                resource=f"res{i}",
            )
        
        # Create checkpoint (automatically gets timestamp)
        root = ledger.create_merkle_checkpoint()
        
        # Check for TSA timestamp in merkle_roots
        checkpoint_seq = len(ledger.entries) - 1
        checkpoint_key = f"checkpoint_{checkpoint_seq}_tsa"
        
        assert checkpoint_key in ledger.merkle_roots


class TestKeypairManagement:
    """Test keypair generation and management."""
    
    def test_generate_keypair(self):
        """Test keypair generation."""
        private_key, public_key = generate_signing_keypair()
        
        assert private_key is not None
        assert public_key is not None
    
    def test_save_and_load_keypair(self, tmp_path):
        """Test saving and loading keypair."""
        private_path = tmp_path / "private.pem"
        public_path = tmp_path / "public.pem"
        
        # Generate and save
        private_key, public_key = generate_signing_keypair()
        save_keypair(private_key, private_path, public_path)
        
        # Load
        loaded_private = load_private_key(private_path)
        loaded_public = load_public_key(public_path)
        
        assert loaded_private is not None
        assert loaded_public is not None
    
    def test_ledger_with_custom_keypair(self, temp_ledger_path):
        """Test ledger with custom keypair."""
        # Generate keypair
        private_key, public_key = generate_signing_keypair()
        
        # Create ledger with custom key
        ledger = create_ledger(temp_ledger_path, signing_key=private_key)
        
        # Add entry
        entry = ledger.append(
            event_type=AuditEventType.CUSTOM,
            actor="user",
            action="action",
            resource="resource",
        )
        
        # Verify signature
        is_valid, errors = ledger.verify_entry(entry)
        assert is_valid is True


class TestAuditReports:
    """Test audit report generation."""
    
    def test_export_audit_report(self, ledger, tmp_path):
        """Test exporting audit report."""
        # Add entries
        for i in range(10):
            ledger.append(
                event_type=AuditEventType.CUSTOM,
                actor=f"user{i}",
                action="action",
                resource=f"res{i}",
            )
        
        # Create checkpoint
        ledger.create_merkle_checkpoint()
        
        # Export report
        report_path = tmp_path / "audit_report.json"
        ledger.export_audit_report(report_path)
        
        assert report_path.exists()
        
        # Load and verify report
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        assert "ledger_info" in report
        assert "integrity_check" in report
        assert "entries" in report
        assert "merkle_roots" in report
        
        assert report["ledger_info"]["total_entries"] == 10
        assert report["integrity_check"]["is_tampered"] is False


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_ledger(self, ledger):
        """Test operations on empty ledger."""
        # Verify empty ledger
        is_valid, errors = ledger.verify_chain()
        assert is_valid is True
        
        # Detect tampering on empty ledger
        is_tampered, issues = ledger.detect_tampering()
        assert is_tampered is False
    
    def test_single_entry_ledger(self, ledger):
        """Test ledger with single entry."""
        ledger.append(
            event_type=AuditEventType.CUSTOM,
            actor="user",
            action="action",
            resource="resource",
        )
        
        is_valid, errors = ledger.verify_chain()
        assert is_valid is True
    
    def test_large_metadata(self, ledger):
        """Test entry with large metadata."""
        large_metadata = {
            f"key{i}": f"value{i}" * 100
            for i in range(100)
        }
        
        entry = ledger.append(
            event_type=AuditEventType.CUSTOM,
            actor="user",
            action="action",
            resource="resource",
            metadata=large_metadata,
        )
        
        assert entry.metadata == large_metadata
        
        is_valid, errors = ledger.verify_entry(entry)
        assert is_valid is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
