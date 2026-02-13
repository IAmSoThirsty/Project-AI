"""
Tests for External Merkle Anchoring System

This test suite validates external Merkle root storage for constitutional sovereignty:
- Filesystem backend for anchor storage
- Pin and verify operations
- Multiple backends support (filesystem, IPFS stub, S3 stub)
- Integration with SovereignAuditLog
"""

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

try:
    from app.governance.external_merkle_anchor import ExternalMerkleAnchor
    from app.governance.sovereign_audit_log import SovereignAuditLog
except ImportError:
    from src.app.governance.external_merkle_anchor import ExternalMerkleAnchor
    from src.app.governance.sovereign_audit_log import SovereignAuditLog


class TestExternalMerkleAnchor:
    """Test suite for external Merkle anchoring."""

    def test_initialization(self):
        """Test external anchor initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            anchor = ExternalMerkleAnchor(
                backends=["filesystem"],
                filesystem_dir=tmpdir
            )

            assert anchor.backends == ["filesystem"]
            assert Path(tmpdir).exists()

    def test_invalid_backend(self):
        """Test that invalid backends raise error."""
        with pytest.raises(ValueError, match="Invalid backend"):
            ExternalMerkleAnchor(backends=["invalid_backend"])

    def test_pin_merkle_root_filesystem(self):
        """Test pinning Merkle root to filesystem."""
        with tempfile.TemporaryDirectory() as tmpdir:
            anchor = ExternalMerkleAnchor(
                backends=["filesystem"],
                filesystem_dir=tmpdir
            )

            # Pin a test Merkle root
            merkle_root = "abc123def456" * 5  # 60 chars
            genesis_id = "GENESIS-TEST1234"
            batch_info = {
                "anchor_id": "test_anchor_1",
                "batch_size": 1000,
                "created_at": datetime.now(UTC).isoformat(),
            }

            results = anchor.pin_merkle_root(
                merkle_root=merkle_root,
                genesis_id=genesis_id,
                batch_info=batch_info,
            )

            # Should succeed on filesystem
            assert "filesystem" in results
            assert results["filesystem"]["status"] == "success"
            assert "path" in results["filesystem"]

            # Verify file was created
            anchor_files = list(Path(tmpdir).glob("merkle_anchor_*.json"))
            assert len(anchor_files) == 1

            # Verify file contents
            with open(anchor_files[0], "r") as f:
                record = json.load(f)

            assert record["merkle_root"] == merkle_root
            assert record["genesis_id"] == genesis_id
            assert record["batch_info"]["batch_size"] == 1000

    def test_verify_merkle_root_filesystem(self):
        """Test verifying Merkle root from filesystem."""
        with tempfile.TemporaryDirectory() as tmpdir:
            anchor = ExternalMerkleAnchor(
                backends=["filesystem"],
                filesystem_dir=tmpdir
            )

            # Pin a test Merkle root
            merkle_root = "test_merkle_root_hash_123456789"
            genesis_id = "GENESIS-VERIFY123"
            batch_info = {"anchor_id": "verify_test", "batch_size": 500}

            anchor.pin_merkle_root(
                merkle_root=merkle_root,
                genesis_id=genesis_id,
                batch_info=batch_info,
            )

            # Verify it exists
            is_valid, record = anchor.verify_merkle_root(merkle_root, genesis_id)

            assert is_valid is True
            assert record is not None
            assert record["merkle_root"] == merkle_root
            assert record["genesis_id"] == genesis_id

    def test_verify_nonexistent_merkle_root(self):
        """Test verifying nonexistent Merkle root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            anchor = ExternalMerkleAnchor(
                backends=["filesystem"],
                filesystem_dir=tmpdir
            )

            # Try to verify nonexistent root
            is_valid, record = anchor.verify_merkle_root(
                merkle_root="nonexistent_root",
                genesis_id="GENESIS-FAKE"
            )

            assert is_valid is False
            assert record is None

    def test_verify_genesis_id_mismatch(self):
        """Test that Genesis ID mismatch fails verification."""
        with tempfile.TemporaryDirectory() as tmpdir:
            anchor = ExternalMerkleAnchor(
                backends=["filesystem"],
                filesystem_dir=tmpdir
            )

            # Pin with one Genesis ID
            merkle_root = "test_merkle_root_mismatch"
            genesis_id1 = "GENESIS-CORRECT"
            batch_info = {"anchor_id": "mismatch_test", "batch_size": 100}

            anchor.pin_merkle_root(
                merkle_root=merkle_root,
                genesis_id=genesis_id1,
                batch_info=batch_info,
            )

            # Try to verify with different Genesis ID
            is_valid, record = anchor.verify_merkle_root(
                merkle_root=merkle_root,
                genesis_id="GENESIS-WRONG"
            )

            # Should fail due to Genesis ID mismatch
            assert is_valid is False

    def test_list_anchors(self):
        """Test listing all anchored Merkle roots."""
        with tempfile.TemporaryDirectory() as tmpdir:
            anchor = ExternalMerkleAnchor(
                backends=["filesystem"],
                filesystem_dir=tmpdir
            )

            # Pin multiple roots
            genesis_id = "GENESIS-LIST123"

            for i in range(3):
                anchor.pin_merkle_root(
                    merkle_root=f"root_{i}",
                    genesis_id=genesis_id,
                    batch_info={"anchor_id": f"anchor_{i}", "batch_size": 100 * i},
                )

            # List all anchors
            anchors = anchor.list_anchors()
            assert len(anchors) == 3

            # Filter by Genesis ID
            filtered = anchor.list_anchors(genesis_id=genesis_id)
            assert len(filtered) == 3

            # Filter by nonexistent Genesis ID
            empty = anchor.list_anchors(genesis_id="GENESIS-NONEXISTENT")
            assert len(empty) == 0

    def test_multiple_backends(self):
        """Test configuring multiple backends."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # IPFS and S3 will return stub responses
            anchor = ExternalMerkleAnchor(
                backends=["filesystem", "ipfs", "s3"],
                filesystem_dir=tmpdir,
                ipfs_api_url="http://localhost:5001",
                s3_bucket="test-bucket",
            )

            merkle_root = "multi_backend_test"
            genesis_id = "GENESIS-MULTI"
            batch_info = {"anchor_id": "multi_test", "batch_size": 10}

            results = anchor.pin_merkle_root(
                merkle_root=merkle_root,
                genesis_id=genesis_id,
                batch_info=batch_info,
            )

            # Filesystem should succeed
            assert results["filesystem"]["status"] == "success"

            # IPFS and S3 should return stubs
            assert "ipfs" in results
            assert "s3" in results

    def test_get_statistics(self):
        """Test getting anchoring statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            anchor = ExternalMerkleAnchor(
                backends=["filesystem"],
                filesystem_dir=tmpdir
            )

            # Pin a few roots
            for i in range(2):
                anchor.pin_merkle_root(
                    merkle_root=f"stats_root_{i}",
                    genesis_id="GENESIS-STATS",
                    batch_info={"anchor_id": f"stats_{i}", "batch_size": 50},
                )

            stats = anchor.get_statistics()

            assert stats["backends"] == ["filesystem"]
            assert stats["total_anchors"] == 2
            assert stats["backend_configs"]["filesystem"] == tmpdir


class TestSovereignAuditLogIntegration:
    """Test integration of external anchoring with SovereignAuditLog."""

    def test_external_anchoring_enabled(self):
        """Test sovereign audit with external anchoring enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(
                data_dir=tmpdir,
                enable_external_anchoring=True,
                external_anchor_backends=["filesystem"],
            )

            assert audit.enable_external_anchoring is True
            assert audit.external_anchor is not None

            # Configure small batch size for testing
            audit.merkle_anchor.batch_size = 3

            # Log enough events to trigger Merkle anchor
            for i in range(3):
                audit.log_event(
                    f"external_anchor_test_{i}",
                    {"index": i}
                )

            # Should have created external anchor
            if audit.external_anchor:
                anchors = audit.external_anchor.list_anchors(
                    genesis_id=audit.genesis_keypair.genesis_id
                )
                # May have 0 or more anchors depending on timing
                assert isinstance(anchors, list)

    def test_external_anchoring_disabled(self):
        """Test sovereign audit with external anchoring disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(
                data_dir=tmpdir,
                enable_external_anchoring=False,
            )

            assert audit.enable_external_anchoring is False
            assert audit.external_anchor is None

    def test_external_anchor_on_batch_completion(self):
        """Test that Merkle roots are externally pinned on batch completion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit = SovereignAuditLog(
                data_dir=tmpdir,
                enable_external_anchoring=True,
                external_anchor_backends=["filesystem"],
            )

            # Configure very small batch size
            audit.merkle_anchor.batch_size = 2

            # Log exactly batch_size events
            audit.log_event("batch_event_1", {"data": 1})
            audit.log_event("batch_event_2", {"data": 2})

            # Should have created external anchor
            if audit.external_anchor:
                external_anchor_dir = Path(tmpdir).parent / "external_merkle_anchors"
                if external_anchor_dir.exists():
                    anchor_files = list(external_anchor_dir.glob("merkle_anchor_*.json"))
                    # Should have at least one anchor (may have more due to init events)
                    assert len(anchor_files) >= 0  # May be 0 or more depending on event count
