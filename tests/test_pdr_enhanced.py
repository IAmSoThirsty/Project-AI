#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Test Suite for Enhanced PDR System

Tests:
- PDR creation and signing
- TSCG-B compression/decompression
- Merkle tree construction
- Signature verification
- Checkpoint creation
- Audit trail export
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone
import json

from src.cognition.pdr_enhanced import (
    PDRRegistry,
    PolicyDecisionRecord,
    PDRDecision,
    PDRSeverity,
    PDRMetadata,
    PDRSignature,
    MerkleCheckpoint,
    MerkleTree,
    CRYPTO_AVAILABLE,
    TSCGB_AVAILABLE,
)

if CRYPTO_AVAILABLE:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


@pytest.fixture
def temp_storage():
    """Create temporary storage directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def registry(temp_storage):
    """Create PDR registry for testing."""
    return PDRRegistry(
        storage_path=temp_storage,
        checkpoint_interval=5,
        auto_sign=True
    )


@pytest.fixture
def sample_pdr():
    """Create sample PDR for testing."""
    metadata = PDRMetadata(
        timestamp=datetime.now(timezone.utc).isoformat(),
        request_id="TEST-001",
        decision=PDRDecision.ALLOW,
        severity=PDRSeverity.LOW,
    )
    
    return PolicyDecisionRecord(
        pdr_id="PDR-TEST-001",
        metadata=metadata,
        decision_rationale="Test PDR",
        context={"test": True}
    )


class TestPDRCreation:
    """Test PDR creation and basic operations."""
    
    def test_create_pdr(self, registry):
        """Test basic PDR creation."""
        pdr = registry.create_pdr(
            request_id="REQ-001",
            decision=PDRDecision.ALLOW,
            severity=PDRSeverity.LOW,
            rationale="Test decision",
            context={"user": "test"}
        )
        
        assert pdr.pdr_id is not None
        assert pdr.metadata.request_id == "REQ-001"
        assert pdr.metadata.decision == PDRDecision.ALLOW
        assert pdr.metadata.severity == PDRSeverity.LOW
        assert pdr.decision_rationale == "Test decision"
        assert pdr.context["user"] == "test"
    
    def test_pdr_content_hash(self, sample_pdr):
        """Test content hash computation."""
        hash1 = sample_pdr.compute_hash()
        hash2 = sample_pdr.compute_hash()
        
        assert hash1 == hash2  # Deterministic
        assert len(hash1) == 64  # SHA-256 hex
    
    def test_pdr_serialization(self, sample_pdr):
        """Test PDR to/from JSON."""
        json_str = sample_pdr.to_json()
        reconstructed = PolicyDecisionRecord.from_json(json_str)
        
        assert reconstructed.pdr_id == sample_pdr.pdr_id
        assert reconstructed.metadata.request_id == sample_pdr.metadata.request_id
        assert reconstructed.decision_rationale == sample_pdr.decision_rationale


@pytest.mark.skipif(not CRYPTO_AVAILABLE, reason="cryptography not available")
class TestSignatures:
    """Test Ed25519 signature operations."""
    
    def test_sign_pdr(self, sample_pdr):
        """Test PDR signing."""
        private_key = Ed25519PrivateKey.generate()
        signature = sample_pdr.sign(private_key)
        
        assert signature is not None
        assert len(signature.public_key) == 32  # Ed25519 public key
        assert len(signature.signature) == 64  # Ed25519 signature
        assert signature.signed_at is not None
    
    def test_verify_signature(self, sample_pdr):
        """Test signature verification."""
        private_key = Ed25519PrivateKey.generate()
        sample_pdr.sign(private_key)
        
        assert sample_pdr.verify_signature() is True
    
    def test_invalid_signature(self, sample_pdr):
        """Test invalid signature detection."""
        private_key = Ed25519PrivateKey.generate()
        sample_pdr.sign(private_key)
        
        # Tamper with content
        sample_pdr.decision_rationale = "TAMPERED"
        
        assert sample_pdr.verify_signature() is False
    
    def test_auto_sign(self, registry):
        """Test automatic signing on creation."""
        pdr = registry.create_pdr(
            request_id="REQ-002",
            decision=PDRDecision.DENY,
            severity=PDRSeverity.HIGH,
            rationale="Auto-sign test"
        )
        
        assert pdr.signature is not None
        assert pdr.verify_signature() is True


@pytest.mark.skipif(not TSCGB_AVAILABLE, reason="TSCG-B not available")
class TestTSCGBCompression:
    """Test TSCG-B compression operations."""
    
    def test_compress_pdr(self, sample_pdr):
        """Test TSCG-B compression."""
        compressed = sample_pdr.compress_tscgb()
        
        assert compressed is not None
        assert len(compressed) > 0
        assert compressed[:4] == b'TSGB'  # Magic number
    
    def test_decompress_pdr(self, sample_pdr):
        """Test TSCG-B decompression."""
        compressed = sample_pdr.compress_tscgb()
        decompressed = sample_pdr.decompress_tscgb(compressed)
        
        assert decompressed is not None
        assert isinstance(decompressed, str)
        assert len(decompressed) > 0
    
    def test_compression_bijective(self, sample_pdr):
        """Test bijective compression (round-trip)."""
        compressed = sample_pdr.compress_tscgb()
        decompressed = sample_pdr.decompress_tscgb(compressed)
        recompressed = sample_pdr.compress_tscgb()
        
        # Compression should be deterministic
        assert compressed == recompressed


class TestMerkleTree:
    """Test Merkle tree operations."""
    
    def test_create_merkle_tree(self):
        """Test Merkle tree creation."""
        tree = MerkleTree(checkpoint_interval=5)
        assert len(tree.pdrs) == 0
        assert len(tree.checkpoints) == 0
    
    def test_add_pdrs(self, registry):
        """Test adding PDRs to Merkle tree."""
        for i in range(3):
            registry.create_pdr(
                request_id=f"REQ-{i}",
                decision=PDRDecision.ALLOW,
                severity=PDRSeverity.LOW,
                rationale=f"Test {i}"
            )
        
        assert len(registry.merkle_tree.pdrs) == 3
    
    def test_checkpoint_creation(self, registry):
        """Test automatic checkpoint creation."""
        # Create 5 PDRs (checkpoint_interval = 5)
        for i in range(5):
            registry.create_pdr(
                request_id=f"REQ-{i}",
                decision=PDRDecision.ALLOW,
                severity=PDRSeverity.LOW,
                rationale=f"Test {i}"
            )
        
        # Should have 1 checkpoint
        assert len(registry.merkle_tree.checkpoints) == 1
        
        checkpoint = registry.merkle_tree.checkpoints[0]
        assert checkpoint.pdr_count == 5
        assert checkpoint.root_hash is not None
    
    def test_multiple_checkpoints(self, registry):
        """Test multiple checkpoint creation."""
        # Create 12 PDRs (checkpoint_interval = 5)
        for i in range(12):
            registry.create_pdr(
                request_id=f"REQ-{i}",
                decision=PDRDecision.ALLOW,
                severity=PDRSeverity.LOW,
                rationale=f"Test {i}"
            )
        
        # Should have 2 checkpoints (at 5 and 10)
        assert len(registry.merkle_tree.checkpoints) == 2
    
    def test_merkle_proof_generation(self, registry):
        """Test Merkle proof generation."""
        # Create PDRs
        pdrs = []
        for i in range(5):
            pdr = registry.create_pdr(
                request_id=f"REQ-{i}",
                decision=PDRDecision.ALLOW,
                severity=PDRSeverity.LOW,
                rationale=f"Test {i}"
            )
            pdrs.append(pdr)
        
        # Get proof for first PDR
        proof = registry.merkle_tree.get_proof(pdrs[0].pdr_id)
        assert proof is not None
        assert len(proof) > 0


class TestPDRRegistry:
    """Test PDR registry operations."""
    
    def test_registry_initialization(self, temp_storage):
        """Test registry initialization."""
        registry = PDRRegistry(storage_path=temp_storage)
        
        assert registry.storage_path.exists()
        assert registry.checkpoint_interval == 100  # Default
    
    def test_pdr_persistence(self, registry):
        """Test PDR persistence to storage."""
        pdr = registry.create_pdr(
            request_id="REQ-PERSIST",
            decision=PDRDecision.ALLOW,
            severity=PDRSeverity.LOW,
            rationale="Persistence test"
        )
        
        # Verify file exists
        pdr_file = registry.storage_path / "pdrs" / f"{pdr.pdr_id}.json"
        assert pdr_file.exists()
    
    def test_pdr_retrieval(self, registry):
        """Test PDR retrieval from storage."""
        pdr = registry.create_pdr(
            request_id="REQ-RETRIEVE",
            decision=PDRDecision.ALLOW,
            severity=PDRSeverity.LOW,
            rationale="Retrieval test"
        )
        
        # Retrieve PDR
        retrieved = registry.get_pdr(pdr.pdr_id)
        
        assert retrieved is not None
        assert retrieved.pdr_id == pdr.pdr_id
        assert retrieved.metadata.request_id == pdr.metadata.request_id
    
    def test_pdr_verification(self, registry):
        """Test complete PDR verification."""
        pdr = registry.create_pdr(
            request_id="REQ-VERIFY",
            decision=PDRDecision.ALLOW,
            severity=PDRSeverity.LOW,
            rationale="Verification test"
        )
        
        results = registry.verify_pdr(pdr.pdr_id)
        
        assert results["exists"] is True
        assert results["hash_valid"] is True
    
    def test_audit_trail_export(self, registry):
        """Test audit trail export."""
        # Create some PDRs
        for i in range(3):
            registry.create_pdr(
                request_id=f"REQ-{i}",
                decision=PDRDecision.ALLOW,
                severity=PDRSeverity.LOW,
                rationale=f"Test {i}"
            )
        
        # Export audit trail
        export_path = registry.export_audit_trail()
        
        assert export_path.exists()
        
        # Verify content
        with open(export_path, 'r') as f:
            audit_data = json.load(f)
        
        assert audit_data["total_pdrs"] == 3
        assert len(audit_data["pdrs"]) == 3
    
    def test_statistics(self, registry):
        """Test registry statistics."""
        # Create diverse PDRs
        registry.create_pdr(
            request_id="REQ-1",
            decision=PDRDecision.ALLOW,
            severity=PDRSeverity.LOW,
            rationale="Test"
        )
        
        registry.create_pdr(
            request_id="REQ-2",
            decision=PDRDecision.DENY,
            severity=PDRSeverity.HIGH,
            rationale="Test"
        )
        
        stats = registry.get_statistics()
        
        assert stats["total_pdrs"] == 2
        assert stats["decisions"]["allow"] == 1
        assert stats["decisions"]["deny"] == 1
        assert stats["severities"]["low"] == 1
        assert stats["severities"]["high"] == 1


class TestDecisionTypes:
    """Test different decision types."""
    
    def test_allow_decision(self, registry):
        """Test ALLOW decision."""
        pdr = registry.create_pdr(
            request_id="REQ-ALLOW",
            decision=PDRDecision.ALLOW,
            severity=PDRSeverity.LOW,
            rationale="Access granted"
        )
        
        assert pdr.metadata.decision == PDRDecision.ALLOW
    
    def test_deny_decision(self, registry):
        """Test DENY decision."""
        pdr = registry.create_pdr(
            request_id="REQ-DENY",
            decision=PDRDecision.DENY,
            severity=PDRSeverity.HIGH,
            rationale="Access denied"
        )
        
        assert pdr.metadata.decision == PDRDecision.DENY
    
    def test_quarantine_decision(self, registry):
        """Test QUARANTINE decision."""
        pdr = registry.create_pdr(
            request_id="REQ-QUARANTINE",
            decision=PDRDecision.QUARANTINE,
            severity=PDRSeverity.MEDIUM,
            rationale="Suspicious activity"
        )
        
        assert pdr.metadata.decision == PDRDecision.QUARANTINE


class TestSeverityLevels:
    """Test severity level handling."""
    
    @pytest.mark.parametrize("severity", [
        PDRSeverity.LOW,
        PDRSeverity.MEDIUM,
        PDRSeverity.HIGH,
        PDRSeverity.CRITICAL,
        PDRSeverity.FATAL,
    ])
    def test_severity_levels(self, registry, severity):
        """Test all severity levels."""
        pdr = registry.create_pdr(
            request_id=f"REQ-{severity.value.upper()}",
            decision=PDRDecision.ALLOW,
            severity=severity,
            rationale=f"Test {severity.value}"
        )
        
        assert pdr.metadata.severity == severity


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_context(self, registry):
        """Test PDR with empty context."""
        pdr = registry.create_pdr(
            request_id="REQ-EMPTY",
            decision=PDRDecision.ALLOW,
            severity=PDRSeverity.LOW,
            rationale="Empty context test",
            context={}
        )
        
        assert pdr.context == {}
    
    def test_large_context(self, registry):
        """Test PDR with large context."""
        large_context = {f"key_{i}": f"value_{i}" for i in range(100)}
        
        pdr = registry.create_pdr(
            request_id="REQ-LARGE",
            decision=PDRDecision.ALLOW,
            severity=PDRSeverity.LOW,
            rationale="Large context test",
            context=large_context
        )
        
        assert len(pdr.context) == 100
    
    def test_nonexistent_pdr(self, registry):
        """Test retrieving non-existent PDR."""
        pdr = registry.get_pdr("PDR-NONEXISTENT")
        assert pdr is None
    
    def test_verification_nonexistent(self, registry):
        """Test verifying non-existent PDR."""
        results = registry.verify_pdr("PDR-NONEXISTENT")
        assert results["exists"] is False


@pytest.mark.integration
class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_workflow(self, registry):
        """Test complete PDR workflow."""
        # 1. Create PDRs
        pdrs = []
        for i in range(15):
            pdr = registry.create_pdr(
                request_id=f"REQ-{i:03d}",
                decision=PDRDecision.ALLOW if i % 2 == 0 else PDRDecision.DENY,
                severity=PDRSeverity.LOW if i % 3 == 0 else PDRSeverity.MEDIUM,
                rationale=f"Integration test {i}",
                context={"index": i}
            )
            pdrs.append(pdr)
        
        # 2. Verify checkpoints created
        assert len(registry.merkle_tree.checkpoints) >= 2
        
        # 3. Verify all PDRs
        for pdr in pdrs:
            results = registry.verify_pdr(pdr.pdr_id)
            assert results["hash_valid"] is True
        
        # 4. Export audit trail
        export_path = registry.export_audit_trail()
        assert export_path.exists()
        
        # 5. Verify statistics
        stats = registry.get_statistics()
        assert stats["total_pdrs"] == 15


if __name__ == '__main__':
    pytest.main([__file__, "-v"])
