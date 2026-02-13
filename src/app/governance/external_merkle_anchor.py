"""
External Merkle Anchoring System

This module implements external storage for Merkle roots to provide immutable,
externally-verifiable proofs of audit log integrity. This is critical for
VECTOR 3 (VM rollback detection) and VECTOR 10 (key compromise resilience).

The system supports multiple external anchor backends:
1. Local filesystem (development/testing)
2. IPFS (distributed immutable storage)
3. S3 with object lock (cloud immutable storage)
4. Blockchain smart contracts (future enhancement)

Architecture:
    Merkle roots are generated every N events (default 1000) by MerkleTreeAnchor.
    This module takes those roots and stores them to external, tamper-proof locations
    that survive VM rollback, filesystem wipe, and admin compromise.

Threat Model:
    Protects against:
    - VM snapshot rollback (VECTOR 3)
    - Filesystem wipe and restoration (VECTOR 11)
    - Key compromise with historical rewrite (VECTOR 10)
    - Admin privilege abuse

Example:
    >>> from src.app.governance.external_merkle_anchor import ExternalMerkleAnchor
    >>> anchor = ExternalMerkleAnchor(backends=["filesystem", "ipfs"])
    >>> anchor.pin_merkle_root(
    ...     merkle_root="abc123...",
    ...     genesis_id="GENESIS-1234",
    ...     batch_info={"size": 1000, "timestamp": "2025-01-01T00:00:00Z"}
    ... )
    {"filesystem": {"status": "success", "path": "..."}, "ipfs": {"status": "success", "cid": "..."}}
"""

import hashlib
import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)

# Default paths
DEFAULT_ANCHOR_DIR = Path(__file__).parent.parent.parent.parent / "data" / "external_merkle_anchors"

# Backend types
AnchorBackend = Literal["filesystem", "ipfs", "s3", "blockchain"]


class ExternalMerkleAnchor:
    """External Merkle root anchoring system.

    Stores Merkle roots to external, tamper-proof locations for constitutional
    sovereignty. Each Merkle root is stored with:
    - Genesis ID (binds to Genesis identity)
    - Merkle root hash (immutable audit log state)
    - Batch metadata (size, timestamp, anchor ID)
    - Backend confirmation (path, CID, transaction hash, etc.)
    """

    def __init__(
        self,
        backends: list[AnchorBackend] | None = None,
        filesystem_dir: Path | str | None = None,
        ipfs_api_url: str | None = None,
        s3_bucket: str | None = None,
        s3_region: str = "us-east-1",
    ):
        """Initialize external Merkle anchor system.

        Args:
            backends: List of backends to use (default: ["filesystem"])
            filesystem_dir: Directory for filesystem backend
            ipfs_api_url: IPFS API endpoint (e.g., "http://localhost:5001")
            s3_bucket: S3 bucket name for cloud storage
            s3_region: AWS region for S3 bucket
        """
        self.backends = backends or ["filesystem"]
        self.filesystem_dir = Path(filesystem_dir) if filesystem_dir else DEFAULT_ANCHOR_DIR
        self.ipfs_api_url = ipfs_api_url
        self.s3_bucket = s3_bucket
        self.s3_region = s3_region

        # Validate backends
        valid_backends: set[AnchorBackend] = {"filesystem", "ipfs", "s3", "blockchain"}
        for backend in self.backends:
            if backend not in valid_backends:
                raise ValueError(f"Invalid backend: {backend}. Must be one of {valid_backends}")

        # Setup filesystem backend
        if "filesystem" in self.backends:
            self.filesystem_dir.mkdir(parents=True, exist_ok=True)

        logger.info("ExternalMerkleAnchor initialized (backends=%s)", self.backends)

    def pin_merkle_root(
        self,
        merkle_root: str,
        genesis_id: str,
        batch_info: dict[str, Any],
        anchor_id: str | None = None,
    ) -> dict[str, dict[str, Any]]:
        """Pin Merkle root to external storage.

        Args:
            merkle_root: Hex-encoded Merkle root hash
            genesis_id: Genesis ID for identity binding
            batch_info: Batch metadata (size, timestamp, entry hashes)
            anchor_id: Optional anchor ID (generated if not provided)

        Returns:
            Dict mapping backend names to their confirmation data

        Example:
            {
                "filesystem": {"status": "success", "path": "/path/to/anchor"},
                "ipfs": {"status": "success", "cid": "QmXyz..."}
            }
        """
        anchor_id = anchor_id or batch_info.get("anchor_id", self._generate_anchor_id())

        # Create anchor record
        anchor_record = {
            "anchor_id": anchor_id,
            "merkle_root": merkle_root,
            "genesis_id": genesis_id,
            "batch_info": batch_info,
            "pinned_at": datetime.now(UTC).isoformat(),
            "backends": self.backends,
        }

        # Pin to each backend
        results: dict[str, dict[str, Any]] = {}

        for backend in self.backends:
            try:
                if backend == "filesystem":
                    results[backend] = self._pin_to_filesystem(anchor_record)
                elif backend == "ipfs":
                    results[backend] = self._pin_to_ipfs(anchor_record)
                elif backend == "s3":
                    results[backend] = self._pin_to_s3(anchor_record)
                elif backend == "blockchain":
                    results[backend] = self._pin_to_blockchain(anchor_record)

                logger.info(
                    "Merkle root pinned to %s (anchor_id=%s, merkle_root=%s)",
                    backend,
                    anchor_id,
                    merkle_root[:16] + "..."
                )
            except Exception as e:
                logger.error("Failed to pin to %s: %s", backend, e)
                results[backend] = {"status": "error", "error": str(e)}

        return results

    def verify_merkle_root(
        self,
        merkle_root: str,
        genesis_id: str,
    ) -> tuple[bool, dict[str, Any] | None]:
        """Verify Merkle root exists in external storage.

        Args:
            merkle_root: Hex-encoded Merkle root hash
            genesis_id: Genesis ID for identity verification

        Returns:
            Tuple of (is_valid, anchor_record_or_none)
        """
        # Check each backend
        for backend in self.backends:
            try:
                if backend == "filesystem":
                    anchor_record = self._verify_from_filesystem(merkle_root, genesis_id)
                elif backend == "ipfs":
                    anchor_record = self._verify_from_ipfs(merkle_root, genesis_id)
                elif backend == "s3":
                    anchor_record = self._verify_from_s3(merkle_root, genesis_id)
                elif backend == "blockchain":
                    anchor_record = self._verify_from_blockchain(merkle_root, genesis_id)
                else:
                    continue

                if anchor_record:
                    # Verify Genesis ID matches
                    if anchor_record.get("genesis_id") == genesis_id:
                        return True, anchor_record
                    else:
                        logger.warning(
                            "Genesis ID mismatch: expected %s, got %s",
                            genesis_id,
                            anchor_record.get("genesis_id")
                        )
            except Exception as e:
                logger.error("Verification error on %s: %s", backend, e)

        return False, None

    def _generate_anchor_id(self) -> str:
        """Generate unique anchor ID."""
        timestamp = datetime.now(UTC).isoformat()
        random_bytes = os.urandom(8)
        return hashlib.sha256(timestamp.encode() + random_bytes).hexdigest()[:16]

    # Filesystem Backend
    def _pin_to_filesystem(self, anchor_record: dict[str, Any]) -> dict[str, Any]:
        """Pin anchor to local filesystem."""
        anchor_id = anchor_record["anchor_id"]
        filename = f"merkle_anchor_{anchor_id}.json"
        filepath = self.filesystem_dir / filename

        # Write anchor record
        with open(filepath, "w") as f:
            json.dump(anchor_record, f, indent=2)

        # Set read-only permissions
        os.chmod(filepath, 0o444)

        return {
            "status": "success",
            "path": str(filepath),
            "permissions": "0o444 (read-only)"
        }

    def _verify_from_filesystem(
        self,
        merkle_root: str,
        genesis_id: str,
    ) -> dict[str, Any] | None:
        """Verify anchor from filesystem."""
        # Search for matching anchor
        for anchor_file in self.filesystem_dir.glob("merkle_anchor_*.json"):
            try:
                with open(anchor_file, "r") as f:
                    anchor_record = json.load(f)

                if (anchor_record.get("merkle_root") == merkle_root and
                    anchor_record.get("genesis_id") == genesis_id):
                    return anchor_record
            except Exception as e:
                logger.error("Error reading %s: %s", anchor_file, e)

        return None

    # IPFS Backend (stub implementation)
    def _pin_to_ipfs(self, anchor_record: dict[str, Any]) -> dict[str, Any]:
        """Pin anchor to IPFS."""
        if not self.ipfs_api_url:
            raise ValueError("IPFS API URL not configured")

        # TODO: Implement IPFS pinning via HTTP API
        # 1. POST anchor_record to /api/v0/add
        # 2. Pin the returned CID with /api/v0/pin/add
        # 3. Return CID as confirmation

        logger.warning("IPFS backend not fully implemented - returning stub response")
        return {
            "status": "stub",
            "message": "IPFS integration pending",
            "todo": "Implement ipfshttpclient integration"
        }

    def _verify_from_ipfs(
        self,
        merkle_root: str,
        genesis_id: str,
    ) -> dict[str, Any] | None:
        """Verify anchor from IPFS."""
        # TODO: Implement IPFS retrieval
        # 1. Query IPFS for known CIDs
        # 2. Retrieve and parse anchor records
        # 3. Match merkle_root and genesis_id

        logger.warning("IPFS verification not implemented")
        return None

    # S3 Backend (stub implementation)
    def _pin_to_s3(self, anchor_record: dict[str, Any]) -> dict[str, Any]:
        """Pin anchor to S3 with object lock."""
        if not self.s3_bucket:
            raise ValueError("S3 bucket not configured")

        # TODO: Implement S3 pinning via boto3
        # 1. Put object to S3 with object lock enabled
        # 2. Set retention policy (GOVERNANCE mode)
        # 3. Return S3 URI and version ID

        logger.warning("S3 backend not fully implemented - returning stub response")
        return {
            "status": "stub",
            "message": "S3 integration pending",
            "todo": "Implement boto3 S3 with object lock"
        }

    def _verify_from_s3(
        self,
        merkle_root: str,
        genesis_id: str,
    ) -> dict[str, Any] | None:
        """Verify anchor from S3."""
        # TODO: Implement S3 retrieval
        # 1. List objects in S3 bucket
        # 2. Download and parse anchor records
        # 3. Match merkle_root and genesis_id

        logger.warning("S3 verification not implemented")
        return None

    # Blockchain Backend (stub implementation)
    def _pin_to_blockchain(self, anchor_record: dict[str, Any]) -> dict[str, Any]:
        """Pin anchor to blockchain smart contract."""
        # TODO: Implement blockchain anchoring
        # Options:
        # 1. Ethereum smart contract
        # 2. Polygon (cheaper gas fees)
        # 3. Custom blockchain

        logger.warning("Blockchain backend not implemented - returning stub response")
        return {
            "status": "stub",
            "message": "Blockchain integration pending",
            "todo": "Implement Web3.py smart contract interaction"
        }

    def _verify_from_blockchain(
        self,
        merkle_root: str,
        genesis_id: str,
    ) -> dict[str, Any] | None:
        """Verify anchor from blockchain."""
        # TODO: Implement blockchain verification
        logger.warning("Blockchain verification not implemented")
        return None

    def list_anchors(
        self,
        genesis_id: str | None = None,
        backend: AnchorBackend | None = None,
    ) -> list[dict[str, Any]]:
        """List all anchored Merkle roots.

        Args:
            genesis_id: Filter by Genesis ID
            backend: Filter by specific backend

        Returns:
            List of anchor records
        """
        anchors: list[dict[str, Any]] = []

        backends_to_check = [backend] if backend else self.backends

        for backend_name in backends_to_check:
            if backend_name == "filesystem":
                for anchor_file in self.filesystem_dir.glob("merkle_anchor_*.json"):
                    try:
                        with open(anchor_file, "r") as f:
                            anchor_record = json.load(f)

                        # Filter by genesis_id if provided
                        if genesis_id and anchor_record.get("genesis_id") != genesis_id:
                            continue

                        anchors.append(anchor_record)
                    except Exception as e:
                        logger.error("Error reading %s: %s", anchor_file, e)
            # TODO: Implement listing for other backends

        return anchors

    def get_statistics(self) -> dict[str, Any]:
        """Get anchoring statistics.

        Returns:
            Dict with counts and info about anchored roots
        """
        stats = {
            "backends": self.backends,
            "total_anchors": len(self.list_anchors()),
            "backend_configs": {
                "filesystem": str(self.filesystem_dir) if "filesystem" in self.backends else None,
                "ipfs": self.ipfs_api_url if "ipfs" in self.backends else None,
                "s3": self.s3_bucket if "s3" in self.backends else None,
            }
        }

        return stats
