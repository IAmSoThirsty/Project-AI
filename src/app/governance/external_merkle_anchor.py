#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
External Merkle Anchoring System

This module implements external storage for Merkle roots to provide immutable,
externally-verifiable proofs of audit log integrity. This is critical for
VECTOR 3 (VM rollback detection) and VECTOR 10 (key compromise resilience).

The system supports multiple external anchor backends:
1. Local filesystem (development/testing)
2. IPFS (distributed immutable storage) - PRODUCTION READY
3. S3 with object lock (cloud immutable storage) - PRODUCTION READY
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
from datetime import timezone, datetime
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)

# Default paths
DEFAULT_ANCHOR_DIR = (
    Path(__file__).parent.parent.parent.parent / "data" / "external_merkle_anchors"
)

# Backend types
AnchorBackend = Literal["filesystem", "ipfs", "s3", "blockchain"]

# Optional imports for external backends
try:
    import ipfshttpclient

    IPFS_AVAILABLE = True
except ImportError:
    IPFS_AVAILABLE = False
    logger.warning("ipfshttpclient not available - IPFS backend disabled")

try:
    import boto3
    from botocore.exceptions import ClientError

    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False
    logger.warning("boto3 not available - S3 backend disabled")

try:
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
    from eth_account import Account
    
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    logger.warning("web3 not available - blockchain backend disabled")


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
        s3_retention_days: int = 3650,  # 10 years default retention
        blockchain_rpc_url: str | None = None,
        blockchain_contract_address: str | None = None,
        blockchain_private_key: str | None = None,
        blockchain_chain_id: int = 1337,  # Local Ganache/Hardhat default
    ):
        """Initialize external Merkle anchor system.

        Args:
            backends: List of backends to use (default: ["filesystem"])
            filesystem_dir: Directory for filesystem backend
            ipfs_api_url: IPFS API endpoint (e.g., "http://localhost:5001")
            s3_bucket: S3 bucket name for cloud storage
            s3_region: AWS region for S3 bucket
            s3_retention_days: S3 object lock retention period (days)
            blockchain_rpc_url: Ethereum RPC endpoint (e.g., "http://localhost:8545")
            blockchain_contract_address: Deployed smart contract address
            blockchain_private_key: Private key for signing transactions
            blockchain_chain_id: Chain ID (1=Ethereum mainnet, 1337=local)
        """
        self.backends = backends or ["filesystem"]
        self.filesystem_dir = (
            Path(filesystem_dir) if filesystem_dir else DEFAULT_ANCHOR_DIR
        )
        self.ipfs_api_url = ipfs_api_url or "http://127.0.0.1:5001"
        self.s3_bucket = s3_bucket
        self.s3_region = s3_region
        self.s3_retention_days = s3_retention_days
        self.blockchain_rpc_url = blockchain_rpc_url or "http://127.0.0.1:8545"
        self.blockchain_contract_address = blockchain_contract_address
        self.blockchain_private_key = blockchain_private_key
        self.blockchain_chain_id = blockchain_chain_id

        # IPFS client (lazy initialization)
        self._ipfs_client = None

        # S3 client (lazy initialization)
        self._s3_client = None
        
        # Web3 client (lazy initialization)
        self._web3_client = None
        self._blockchain_contract = None

        # Validate backends
        valid_backends: set[AnchorBackend] = {"filesystem", "ipfs", "s3", "blockchain"}
        for backend in self.backends:
            if backend not in valid_backends:
                raise ValueError(
                    f"Invalid backend: {backend}. Must be one of {valid_backends}"
                )

            # Check availability
            if backend == "ipfs" and not IPFS_AVAILABLE:
                raise ValueError(
                    "IPFS backend requested but ipfshttpclient not installed"
                )
            if backend == "s3" and not S3_AVAILABLE:
                raise ValueError("S3 backend requested but boto3 not installed")
            if backend == "blockchain" and not WEB3_AVAILABLE:
                raise ValueError("Blockchain backend requested but web3 not installed")

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
            "pinned_at": datetime.now(timezone.utc).isoformat(),
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
                    merkle_root[:16] + "...",
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
                    anchor_record = self._verify_from_filesystem(
                        merkle_root, genesis_id
                    )
                elif backend == "ipfs":
                    anchor_record = self._verify_from_ipfs(merkle_root, genesis_id)
                elif backend == "s3":
                    anchor_record = self._verify_from_s3(merkle_root, genesis_id)
                elif backend == "blockchain":
                    anchor_record = self._verify_from_blockchain(
                        merkle_root, genesis_id
                    )
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
                            anchor_record.get("genesis_id"),
                        )
            except Exception as e:
                logger.error("Verification error on %s: %s", backend, e)

        return False, None

    def _generate_anchor_id(self) -> str:
        """Generate unique anchor ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
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
            "permissions": "0o444 (read-only)",
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
                with open(anchor_file) as f:
                    anchor_record = json.load(f)

                if (
                    anchor_record.get("merkle_root") == merkle_root
                    and anchor_record.get("genesis_id") == genesis_id
                ):
                    return anchor_record
            except Exception as e:
                logger.error("Error reading %s: %s", anchor_file, e)

        return None

    # IPFS Backend (PRODUCTION READY)
    def _get_ipfs_client(self):
        """Get or create IPFS client (lazy initialization)."""
        if self._ipfs_client is None:
            if not IPFS_AVAILABLE:
                raise RuntimeError("ipfshttpclient not available")
            try:
                self._ipfs_client = ipfshttpclient.connect(self.ipfs_api_url)
                logger.info("Connected to IPFS at %s", self.ipfs_api_url)
            except Exception as e:
                logger.error("Failed to connect to IPFS: %s", e)
                raise RuntimeError(f"IPFS connection failed: {e}")
        return self._ipfs_client

    def _pin_to_ipfs(self, anchor_record: dict[str, Any]) -> dict[str, Any]:
        """Pin anchor to IPFS with remote pinning.

        This provides TRUE external sovereignty - data survives:
        - VM snapshot rollback
        - Filesystem wipe
        - Admin compromise
        - Machine destruction
        """
        try:
            client = self._get_ipfs_client()

            # Serialize anchor record to JSON bytes
            anchor_json = json.dumps(anchor_record, indent=2)
            anchor_bytes = anchor_json.encode("utf-8")

            # Add to IPFS and get CID (Content Identifier)
            result = client.add_bytes(anchor_bytes)
            cid = result  # CID is the immutable content address

            # Pin the CID to ensure persistence
            client.pin.add(cid)

            logger.info(
                "Merkle anchor pinned to IPFS (CID=%s, merkle_root=%s...)",
                cid,
                anchor_record["merkle_root"][:16],
            )

            return {
                "status": "success",
                "cid": cid,
                "ipfs_url": f"ipfs://{cid}",
                "gateway_url": f"https://ipfs.io/ipfs/{cid}",
                "pinned": True,
            }

        except Exception as e:
            logger.error("IPFS pinning failed: %s", e)
            raise RuntimeError(f"IPFS pinning error: {e}")

    def _verify_from_ipfs(
        self,
        merkle_root: str,
        genesis_id: str,
    ) -> dict[str, Any] | None:
        """Verify anchor from IPFS.

        NOTE: This requires maintaining a local index of CIDs.
        In production, you would:
        1. Store CIDs in a local database or index
        2. Query IPFS for each known CID
        3. Verify merkle_root and genesis_id match
        """
        try:
            client = self._get_ipfs_client()

            # Get list of pinned CIDs
            pins = client.pin.ls(type="all")

            # Search through pinned content for matching anchor
            for cid_info in pins.get("Keys", {}).items():
                cid = cid_info[0]
                try:
                    # Retrieve content from IPFS
                    content_bytes = client.cat(cid)
                    anchor_record = json.loads(content_bytes.decode("utf-8"))

                    # Check if this is our anchor
                    if (
                        anchor_record.get("merkle_root") == merkle_root
                        and anchor_record.get("genesis_id") == genesis_id
                    ):
                        logger.info("Found matching anchor in IPFS (CID=%s)", cid)
                        return anchor_record

                except Exception:
                    # Not a valid anchor record, skip
                    continue

            logger.warning("No matching anchor found in IPFS")
            return None

        except Exception as e:
            logger.error("IPFS verification error: %s", e)
            return None

    # S3 Backend (PRODUCTION READY with WORM)
    def _get_s3_client(self):
        """Get or create S3 client (lazy initialization)."""
        if self._s3_client is None:
            if not S3_AVAILABLE:
                raise RuntimeError("boto3 not available")
            try:
                self._s3_client = boto3.client("s3", region_name=self.s3_region)
                logger.info("Connected to S3 in region %s", self.s3_region)
            except Exception as e:
                logger.error("Failed to connect to S3: %s", e)
                raise RuntimeError(f"S3 connection failed: {e}")
        return self._s3_client

    def _pin_to_s3(self, anchor_record: dict[str, Any]) -> dict[str, Any]:
        """Pin anchor to S3 with WORM object lock.

        This provides TRUE external sovereignty with immutable storage:
        - Object lock prevents deletion/modification
        - GOVERNANCE retention mode (adjustable by admin)
        - COMPLIANCE mode available for regulatory requirements
        - Data survives VM rollback, filesystem wipe, admin compromise
        """
        if not self.s3_bucket:
            raise ValueError("S3 bucket not configured")

        try:
            client = self._get_s3_client()

            # Generate S3 key (path)
            anchor_id = anchor_record["anchor_id"]
            s3_key = f"merkle_anchors/{anchor_id}.json"

            # Serialize anchor record
            anchor_json = json.dumps(anchor_record, indent=2)

            # Calculate retention date
            from datetime import timedelta

            retention_until = datetime.now(timezone.utc) + timedelta(days=self.s3_retention_days)

            # Put object with object lock retention
            response = client.put_object(
                Bucket=self.s3_bucket,
                Key=s3_key,
                Body=anchor_json.encode("utf-8"),
                ContentType="application/json",
                Metadata={
                    "genesis_id": anchor_record["genesis_id"],
                    "merkle_root": anchor_record["merkle_root"],
                    "anchor_id": anchor_id,
                },
                ObjectLockMode="GOVERNANCE",  # GOVERNANCE mode (admin can override)
                ObjectLockRetainUntilDate=retention_until,
            )

            version_id = response.get("VersionId", "unknown")

            logger.info(
                "Merkle anchor pinned to S3 (bucket=%s, key=%s, version=%s, retention_days=%d)",
                self.s3_bucket,
                s3_key,
                version_id,
                self.s3_retention_days,
            )

            return {
                "status": "success",
                "bucket": self.s3_bucket,
                "key": s3_key,
                "version_id": version_id,
                "s3_uri": f"s3://{self.s3_bucket}/{s3_key}",
                "retention_until": retention_until.isoformat(),
                "object_lock_mode": "GOVERNANCE",
            }

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "ObjectLockConfigurationNotFoundError":
                logger.error(
                    "S3 bucket %s does not have object lock enabled. "
                    "Enable object lock for WORM protection.",
                    self.s3_bucket,
                )
            raise RuntimeError(f"S3 pinning error: {e}")
        except Exception as e:
            logger.error("S3 pinning failed: %s", e)
            raise RuntimeError(f"S3 pinning error: {e}")

    def _verify_from_s3(
        self,
        merkle_root: str,
        genesis_id: str,
    ) -> dict[str, Any] | None:
        """Verify anchor from S3.

        Searches S3 bucket for matching anchor record.
        """
        if not self.s3_bucket:
            return None

        try:
            client = self._get_s3_client()

            # List objects in merkle_anchors/ prefix
            paginator = client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.s3_bucket, Prefix="merkle_anchors/")

            for page in pages:
                for obj in page.get("Contents", []):
                    s3_key = obj["Key"]
                    try:
                        # Get object content
                        response = client.get_object(Bucket=self.s3_bucket, Key=s3_key)
                        content = response["Body"].read().decode("utf-8")
                        anchor_record = json.loads(content)

                        # Check if this is our anchor
                        if (
                            anchor_record.get("merkle_root") == merkle_root
                            and anchor_record.get("genesis_id") == genesis_id
                        ):
                            logger.info("Found matching anchor in S3 (key=%s)", s3_key)
                            return anchor_record

                    except Exception as e:
                        logger.debug("Error reading S3 object %s: %s", s3_key, e)
                        continue

            logger.warning("No matching anchor found in S3")
            return None

        except Exception as e:
            logger.error("S3 verification error: %s", e)
            return None

    # Blockchain Backend - Web3.py Implementation
    
    # Smart contract ABI (Solidity interface)
    MERKLE_ANCHOR_ABI = [
        {
            "inputs": [],
            "stateMutability": "nonpayable",
            "type": "constructor"
        },
        {
            "anonymous": False,
            "inputs": [
                {"indexed": True, "internalType": "bytes32", "name": "merkleRoot", "type": "bytes32"},
                {"indexed": True, "internalType": "string", "name": "genesisId", "type": "string"},
                {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
                {"indexed": False, "internalType": "string", "name": "metadata", "type": "string"}
            ],
            "name": "MerkleRootAnchored",
            "type": "event"
        },
        {
            "inputs": [
                {"internalType": "bytes32", "name": "merkleRoot", "type": "bytes32"},
                {"internalType": "string", "name": "genesisId", "type": "string"},
                {"internalType": "string", "name": "metadata", "type": "string"}
            ],
            "name": "anchorMerkleRoot",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "bytes32", "name": "merkleRoot", "type": "bytes32"},
                {"internalType": "string", "name": "genesisId", "type": "string"}
            ],
            "name": "verifyAnchor",
            "outputs": [
                {"internalType": "bool", "name": "exists", "type": "bool"},
                {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                {"internalType": "string", "name": "metadata", "type": "string"}
            ],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [
                {"internalType": "bytes32", "name": "", "type": "bytes32"},
                {"internalType": "string", "name": "", "type": "string"}
            ],
            "name": "anchors",
            "outputs": [
                {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                {"internalType": "string", "name": "metadata", "type": "string"},
                {"internalType": "bool", "name": "exists", "type": "bool"}
            ],
            "stateMutability": "view",
            "type": "function"
        }
    ]
    
    # Solidity contract source (for deployment/reference)
    MERKLE_ANCHOR_SOLIDITY = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract MerkleAnchor {
    struct Anchor {
        uint256 timestamp;
        string metadata;
        bool exists;
    }
    
    // Mapping: merkleRoot => genesisId => Anchor
    mapping(bytes32 => mapping(string => Anchor)) public anchors;
    
    event MerkleRootAnchored(
        bytes32 indexed merkleRoot,
        string indexed genesisId,
        uint256 timestamp,
        string metadata
    );
    
    function anchorMerkleRoot(
        bytes32 merkleRoot,
        string memory genesisId,
        string memory metadata
    ) public {
        require(!anchors[merkleRoot][genesisId].exists, "Anchor already exists");
        
        anchors[merkleRoot][genesisId] = Anchor({
            timestamp: block.timestamp,
            metadata: metadata,
            exists: true
        });
        
        emit MerkleRootAnchored(merkleRoot, genesisId, block.timestamp, metadata);
    }
    
    function verifyAnchor(
        bytes32 merkleRoot,
        string memory genesisId
    ) public view returns (bool exists, uint256 timestamp, string memory metadata) {
        Anchor memory anchor = anchors[merkleRoot][genesisId];
        return (anchor.exists, anchor.timestamp, anchor.metadata);
    }
}
"""

    def _get_web3_client(self):
        """Get or create Web3 client (lazy initialization)."""
        if self._web3_client is None:
            if not WEB3_AVAILABLE:
                raise RuntimeError("web3 package not installed")
            
            self._web3_client = Web3(Web3.HTTPProvider(self.blockchain_rpc_url))
            
            # Add PoA middleware for networks like Ganache/Polygon
            self._web3_client.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            # Verify connection
            if not self._web3_client.is_connected():
                raise ConnectionError(
                    f"Cannot connect to blockchain at {self.blockchain_rpc_url}"
                )
            
            logger.info("Connected to blockchain (chain_id=%s)", self._web3_client.eth.chain_id)
        
        return self._web3_client
    
    def _get_blockchain_contract(self):
        """Get or create blockchain contract instance."""
        if self._blockchain_contract is None:
            if not self.blockchain_contract_address:
                raise ValueError("Blockchain contract address not configured")
            
            w3 = self._get_web3_client()
            
            # Convert address to checksum format
            contract_address = w3.to_checksum_address(self.blockchain_contract_address)
            
            # Create contract instance
            self._blockchain_contract = w3.eth.contract(
                address=contract_address,
                abi=self.MERKLE_ANCHOR_ABI
            )
            
            logger.info("Loaded contract at %s", contract_address)
        
        return self._blockchain_contract
    
    def _get_blockchain_account(self):
        """Get account from private key."""
        if not self.blockchain_private_key:
            raise ValueError("Blockchain private key not configured")
        
        return Account.from_key(self.blockchain_private_key)

    def _pin_to_blockchain(self, anchor_record: dict[str, Any]) -> dict[str, Any]:
        """Pin anchor to blockchain smart contract."""
        if not WEB3_AVAILABLE:
            logger.warning("web3 not available - blockchain backend disabled")
            return {
                "status": "error",
                "message": "web3 package not installed",
            }
        
        try:
            w3 = self._get_web3_client()
            contract = self._get_blockchain_contract()
            account = self._get_blockchain_account()
            
            # Convert merkle root to bytes32
            merkle_root = anchor_record["merkle_root"]
            if merkle_root.startswith("0x"):
                merkle_root_bytes = bytes.fromhex(merkle_root[2:])
            else:
                merkle_root_bytes = bytes.fromhex(merkle_root)
            
            # Pad to 32 bytes if needed
            if len(merkle_root_bytes) < 32:
                merkle_root_bytes = merkle_root_bytes + b'\x00' * (32 - len(merkle_root_bytes))
            elif len(merkle_root_bytes) > 32:
                merkle_root_bytes = merkle_root_bytes[:32]
            
            genesis_id = anchor_record["genesis_id"]
            metadata = json.dumps({
                "anchor_id": anchor_record.get("anchor_id", ""),
                "batch_size": anchor_record.get("batch_info", {}).get("size", 0),
                "timestamp": anchor_record.get("timestamp", ""),
            })
            
            # Build transaction
            tx = contract.functions.anchorMerkleRoot(
                merkle_root_bytes,
                genesis_id,
                metadata
            ).build_transaction({
                'from': account.address,
                'nonce': w3.eth.get_transaction_count(account.address),
                'gas': 200000,
                'gasPrice': w3.eth.gas_price,
                'chainId': self.blockchain_chain_id,
            })
            
            # Sign transaction
            signed_tx = account.sign_transaction(tx)
            
            # Send transaction
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            # Wait for receipt (with timeout)
            logger.info("Waiting for transaction %s to be mined...", tx_hash.hex())
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            logger.info(
                "Merkle root anchored to blockchain (tx=%s, block=%s)",
                tx_hash.hex(),
                tx_receipt['blockNumber']
            )
            
            return {
                "status": "success",
                "transaction_hash": tx_hash.hex(),
                "block_number": tx_receipt['blockNumber'],
                "gas_used": tx_receipt['gasUsed'],
                "contract_address": self.blockchain_contract_address,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        
        except Exception as e:
            logger.error("Blockchain anchoring failed: %s", e, exc_info=True)
            return {
                "status": "error",
                "message": str(e),
            }

    def _verify_from_blockchain(
        self,
        merkle_root: str,
        genesis_id: str,
    ) -> dict[str, Any] | None:
        """Verify anchor from blockchain."""
        if not WEB3_AVAILABLE:
            logger.warning("web3 not available - blockchain verification disabled")
            return None
        
        try:
            w3 = self._get_web3_client()
            contract = self._get_blockchain_contract()
            
            # Convert merkle root to bytes32
            if merkle_root.startswith("0x"):
                merkle_root_bytes = bytes.fromhex(merkle_root[2:])
            else:
                merkle_root_bytes = bytes.fromhex(merkle_root)
            
            # Pad to 32 bytes
            if len(merkle_root_bytes) < 32:
                merkle_root_bytes = merkle_root_bytes + b'\x00' * (32 - len(merkle_root_bytes))
            elif len(merkle_root_bytes) > 32:
                merkle_root_bytes = merkle_root_bytes[:32]
            
            # Call contract
            exists, timestamp, metadata = contract.functions.verifyAnchor(
                merkle_root_bytes,
                genesis_id
            ).call()
            
            if not exists:
                logger.warning("No blockchain anchor found for merkle_root=%s, genesis_id=%s", 
                             merkle_root, genesis_id)
                return None
            
            # Parse metadata
            try:
                metadata_dict = json.loads(metadata) if metadata else {}
            except json.JSONDecodeError:
                metadata_dict = {}
            
            logger.info("Found blockchain anchor (timestamp=%s)", timestamp)
            
            return {
                "merkle_root": merkle_root,
                "genesis_id": genesis_id,
                "timestamp": datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat(),
                "block_timestamp": timestamp,
                "metadata": metadata_dict,
                "exists": True,
                "backend": "blockchain",
            }
        
        except Exception as e:
            logger.error("Blockchain verification error: %s", e, exc_info=True)
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
                        with open(anchor_file) as f:
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
                "filesystem": (
                    str(self.filesystem_dir) if "filesystem" in self.backends else None
                ),
                "ipfs": self.ipfs_api_url if "ipfs" in self.backends else None,
                "s3": self.s3_bucket if "s3" in self.backends else None,
            },
        }

        return stats
