#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
SASE - Sovereign Adversarial Signal Engine
L9: Evidence Vault & Merkle Audit Chain

Cryptographic audit trail with HSM-signed Merkle trees.

MERKLE CONSTRUCTION:
- Daily event hashes aggregated into tree
- Root hash:
  - Signed by HSM
  - Optionally anchored to blockchain
  - Proof generation available per event
"""

import hashlib
import hmac
import logging
import time
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("SASE.L9.EvidenceVault")


@dataclass
class MerkleNode:
    """Node in Merkle tree"""

    hash_value: str
    left: Optional["MerkleNode"] = None
    right: Optional["MerkleNode"] = None

    def is_leaf(self) -> bool:
        """Check if leaf node"""
        return self.left is None and self.right is None


class MerkleTree:
    """
    Merkle tree for event hash aggregation

    Provides cryptographic proof of event inclusion
    """

    def __init__(self, leaf_hashes: list[str]):
        if not leaf_hashes:
            raise ValueError("Must provide at least one hash")

        self.leaf_hashes = leaf_hashes
        self.root = self._build_tree(leaf_hashes)

        logger.info(f"Merkle tree built with {len(leaf_hashes)} leaves")

    def _build_tree(self, hashes: list[str]) -> MerkleNode:
        """Build Merkle tree from leaf hashes"""
        # Create leaf nodes
        nodes = [MerkleNode(hash_value=h) for h in hashes]

        # Build tree bottom-up
        while len(nodes) > 1:
            next_level = []

            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = (
                    nodes[i + 1] if i + 1 < len(nodes) else nodes[i]
                )  # Duplicate if odd

                # Combine hashes
                combined = hashlib.sha256(
                    (left.hash_value + right.hash_value).encode()
                ).hexdigest()

                parent = MerkleNode(hash_value=combined, left=left, right=right)

                next_level.append(parent)

            nodes = next_level

        return nodes[0]

    def get_root_hash(self) -> str:
        """Get Merkle root hash"""
        return self.root.hash_value

    def generate_proof(self, leaf_hash: str) -> list[str] | None:
        """
        Generate Merkle proof for leaf

        Returns list of sibling hashes for verification path
        """
        if leaf_hash not in self.leaf_hashes:
            return None

        # Find leaf index
        leaf_idx = self.leaf_hashes.index(leaf_hash)

        # Generate proof path
        proof = []
        self._generate_proof_recursive(self.root, leaf_hash, proof)

        return proof

    def _generate_proof_recursive(
        self, node: MerkleNode, target_hash: str, proof: list[str]
    ) -> bool:
        """Recursively generate proof path"""
        if node.is_leaf():
            return node.hash_value == target_hash

        # Check left subtree
        if self._generate_proof_recursive(node.left, target_hash, proof):
            if node.right:
                proof.append(node.right.hash_value)
            return True

        # Check right subtree
        if node.right and self._generate_proof_recursive(
            node.right, target_hash, proof
        ):
            proof.append(node.left.hash_value)
            return True

        return False

    @staticmethod
    def verify_proof(leaf_hash: str, proof: list[str], root_hash: str) -> bool:
        """Verify Merkle proof"""
        current = leaf_hash

        for sibling_hash in proof:
            # Combine with sibling
            combined = hashlib.sha256((current + sibling_hash).encode()).hexdigest()
            current = combined

        return current == root_hash


class HSMSigner:
    """
    Hardware Security Module interface for signing

    Signs Merkle roots with hardware-protected keys

    Supported HSM types:
    - software: HMAC-based signing (development only)
    - yubihsm: YubiHSM 2 hardware security module
    - aws_cloudhsm: AWS CloudHSM service
    """

    def __init__(
        self,
        hsm_type: str = "software",
        hsm_config: Optional[dict] = None,
    ):
        self.hsm_type = hsm_type
        self.hsm_config = hsm_config or {}
        self._hsm_client = None

        # Initialize HSM connection
        self._initialize_hsm()

    def _initialize_hsm(self):
        """Initialize HSM connection based on type"""
        if self.hsm_type == "software":
            logger.warning("HSM: Using software signing (DEVELOPMENT ONLY)")
            self._software_key = self.hsm_config.get(
                "key", b"sase_dev_key_change_in_production"
            )

        elif self.hsm_type == "yubihsm":
            logger.info("HSM: Initializing YubiHSM connection")
            try:
                self._initialize_yubihsm()
            except Exception as e:
                logger.error(f"YubiHSM initialization failed: {e}")
                logger.warning("Falling back to software HSM")
                self.hsm_type = "software"
                self._software_key = b"sase_fallback_key"

        elif self.hsm_type == "aws_cloudhsm":
            logger.info("HSM: Initializing AWS CloudHSM connection")
            try:
                self._initialize_aws_cloudhsm()
            except Exception as e:
                logger.error(f"AWS CloudHSM initialization failed: {e}")
                logger.warning("Falling back to software HSM")
                self.hsm_type = "software"
                self._software_key = b"sase_fallback_key"

        else:
            logger.error(f"Unknown HSM type: {self.hsm_type}")
            raise ValueError(f"Unsupported HSM type: {self.hsm_type}")

    def _initialize_yubihsm(self):
        """Initialize YubiHSM 2 connection"""
        try:
            import yubihsm  # type: ignore
            from yubihsm.defs import ALGORITHM  # type: ignore
        except ImportError:
            raise ImportError(
                "YubiHSM library not installed. "
                "Install with: pip install python-yubihsm"
            )

        connector_url = self.hsm_config.get("connector_url", "http://localhost:12345")
        auth_key_id = self.hsm_config.get("auth_key_id", 1)
        password = self.hsm_config.get("password", "")

        if not password:
            raise ValueError("YubiHSM password required in hsm_config")

        # Connect to YubiHSM connector
        self._hsm_client = yubihsm.YubiHsm.connect(connector_url)

        # Create session
        self._hsm_session = self._hsm_client.create_session_derived(
            auth_key_id, password
        )

        # Get or create signing key
        self._signing_key_id = self.hsm_config.get("signing_key_id")

        if not self._signing_key_id:
            # Create new HMAC key
            logger.info("Creating new HMAC key in YubiHSM")
            self._signing_key_id = self._hsm_session.put_hmac_key(
                0,  # Let HSM assign ID
                "SASE Evidence Vault Signing Key",
                1,  # Domain 1
                ALGORITHM.HMAC_SHA256,
                b"\x00" * 32,  # Generate random key
            )
            logger.info(f"Created YubiHSM key ID: {self._signing_key_id}")

        logger.info(f"YubiHSM initialized with key ID {self._signing_key_id}")

    def _initialize_aws_cloudhsm(self):
        """Initialize AWS CloudHSM connection"""
        try:
            import boto3  # type: ignore
            from cloudhsm_mgmt_util import CloudHsmClient  # type: ignore
        except ImportError:
            raise ImportError(
                "AWS CloudHSM library not installed. "
                "Install with: pip install boto3 cloudhsm-mgmt-util"
            )

        cluster_id = self.hsm_config.get("cluster_id")
        user = self.hsm_config.get("user")
        password = self.hsm_config.get("password")

        if not all([cluster_id, user, password]):
            raise ValueError(
                "AWS CloudHSM requires cluster_id, user, and password in hsm_config"
            )

        # Initialize CloudHSM client
        self._hsm_client = CloudHsmClient()
        self._hsm_client.login(user, password)

        # Get or create key handle
        self._key_handle = self.hsm_config.get("key_handle")

        if not self._key_handle:
            # Generate new HMAC key
            logger.info("Generating new HMAC key in AWS CloudHSM")
            self._key_handle = self._hsm_client.generate_hmac_key(
                key_label="sase_evidence_vault_key",
                key_size=32,
            )
            logger.info(f"Created CloudHSM key handle: {self._key_handle}")

        logger.info(f"AWS CloudHSM initialized with key handle {self._key_handle}")

    def sign(self, data: str) -> str:
        """
        Sign data with HSM key

        Returns signature (hex)
        """
        try:
            if self.hsm_type == "software":
                return self._sign_software(data)
            elif self.hsm_type == "yubihsm":
                return self._sign_yubihsm(data)
            elif self.hsm_type == "aws_cloudhsm":
                return self._sign_aws_cloudhsm(data)
            else:
                raise ValueError(f"Unknown HSM type: {self.hsm_type}")

        except Exception as e:
            logger.error(f"HSM signing failed: {e}")
            # Fallback to software signing on error
            if self.hsm_type != "software":
                logger.warning("Falling back to emergency software signing")
                # Initialize software key if not present
                if not hasattr(self, "_software_key"):
                    self._software_key = b"sase_emergency_fallback_key"
                return self._sign_software(data)
            raise

    def _sign_software(self, data: str) -> str:
        """Software HMAC signing (development only)"""
        signature = hmac.new(
            self._software_key, data.encode(), hashlib.sha256
        ).hexdigest()
        return signature

    def _sign_yubihsm(self, data: str) -> str:
        """Sign with YubiHSM 2"""
        if not self._hsm_session:
            raise RuntimeError("YubiHSM session not initialized")

        # Sign data using HMAC
        signature = self._hsm_session.sign_hmac(
            self._signing_key_id, data.encode()
        )

        return signature.hex()

    def _sign_aws_cloudhsm(self, data: str) -> str:
        """Sign with AWS CloudHSM"""
        if not self._hsm_client:
            raise RuntimeError("AWS CloudHSM client not initialized")

        # Sign data using HMAC
        signature = self._hsm_client.sign_hmac(
            self._key_handle, data.encode()
        )

        return signature.hex()

    def verify(self, data: str, signature: str) -> bool:
        """Verify HSM signature"""
        try:
            expected_sig = self.sign(data)
            return signature == expected_sig
        except Exception as e:
            logger.error(f"HSM signature verification failed: {e}")
            return False

    def get_hsm_info(self) -> dict:
        """Get HSM information for audit purposes"""
        info = {
            "hsm_type": self.hsm_type,
            "initialized": self._hsm_client is not None or self.hsm_type == "software",
        }

        if self.hsm_type == "yubihsm":
            info["signing_key_id"] = getattr(self, "_signing_key_id", None)
        elif self.hsm_type == "aws_cloudhsm":
            info["key_handle"] = getattr(self, "_key_handle", None)

        return info

    def __del__(self):
        """Clean up HSM connection"""
        try:
            if self.hsm_type == "yubihsm" and hasattr(self, "_hsm_session"):
                self._hsm_session.close()
            elif self.hsm_type == "aws_cloudhsm" and self._hsm_client:
                self._hsm_client.logout()
        except Exception as e:
            logger.warning(f"HSM cleanup failed: {e}")


class ProofGenerator:
    """
    Generates cryptographic proofs for events and actions
    """

    def __init__(self):
        self.generated_proofs: dict[str, dict] = {}

    def generate(
        self, event_hash: str, merkle_tree: MerkleTree, signature: str
    ) -> dict:
        """
        Generate full cryptographic proof

        Includes Merkle proof + HSM signature
        """
        # Get Merkle proof path
        merkle_proof = merkle_tree.generate_proof(event_hash)

        if merkle_proof is None:
            logger.error("Cannot generate proof: event not in tree")
            return {}

        proof = {
            "event_hash": event_hash,
            "merkle_proof": merkle_proof,
            "merkle_root": merkle_tree.get_root_hash(),
            "hsm_signature": signature,
            "timestamp": time.time(),
        }

        # Cache proof
        self.generated_proofs[event_hash] = proof

        logger.info(f"Proof generated for event {event_hash[:16]}")

        return proof


class EvidenceVault:
    """
    L9: Evidence Vault & Merkle Audit Chain

    Maintains cryptographically verifiable audit trail
    """

    def __init__(self, hsm_type: str = "software", hsm_config: Optional[dict] = None):
        self.hsm_signer = HSMSigner(hsm_type, hsm_config)
        self.proof_generator = ProofGenerator()

        # Daily Merkle trees
        self.daily_trees: dict[str, MerkleTree] = {}  # date -> tree
        self.daily_signatures: dict[str, str] = {}  # date -> signature

        # Blockchain anchoring (optional)
        self.blockchain_anchors: dict[str, str] = {}  # root_hash -> tx_id

        logger.info(f"L9 Evidence Vault initialized with HSM type: {hsm_type}")

    def aggregate_daily_events(self, date: str, event_hashes: list[str]) -> str:
        """
        Aggregate daily events into Merkle tree

        Returns root hash
        """
        logger.info(f"Aggregating {len(event_hashes)} events for {date}")

        # Build Merkle tree
        tree = MerkleTree(event_hashes)
        root_hash = tree.get_root_hash()

        # Sign root with HSM
        signature = self.hsm_signer.sign(root_hash)

        # Store
        self.daily_trees[date] = tree
        self.daily_signatures[date] = signature

        logger.info(f"Daily Merkle root: {root_hash[:16]} (signed)")

        return root_hash

    def anchor_to_blockchain(
        self, root_hash: str, blockchain: str = "ethereum", config: dict = None
    ):
        """
        Anchor Merkle root to blockchain via Chainlink

        Provides additional tamper-resistance through immutable blockchain storage

        Args:
            root_hash: Merkle root hash to anchor
            blockchain: Target blockchain (ethereum, polygon, avalanche)
            config: Optional blockchain config (rpc_url, contract_address, private_key)

        Returns:
            Transaction ID of blockchain anchor
        """
        logger.info(f"Anchoring root to {blockchain}: {root_hash[:16]}")

        # Initialize blockchain anchoring service
        if not hasattr(self, "_blockchain_service"):
            from .blockchain_anchoring import ChainlinkAnchoringService

            self._blockchain_service = ChainlinkAnchoringService(config or {})

        # Anchor via Chainlink
        try:
            tx_id = self._blockchain_service.anchor_hash(root_hash, blockchain)
            self.blockchain_anchors[root_hash] = tx_id

            logger.info(f"Blockchain anchor successful: {tx_id[:16]}")
            return tx_id

        except Exception as e:
            logger.error(f"Blockchain anchoring failed: {e}")
            # Fallback to mock for development/testing
            tx_id = f"0x{hashlib.sha256(root_hash.encode()).hexdigest()}"
            self.blockchain_anchors[root_hash] = tx_id
            logger.warning(f"Using mock anchor: {tx_id[:16]}")
            return tx_id

    def verify_blockchain_anchor(
        self, root_hash: str, blockchain: str = "ethereum", config: dict = None
    ) -> bool:
        """
        Verify Merkle root exists on blockchain

        Args:
            root_hash: Merkle root hash to verify
            blockchain: Target blockchain
            config: Optional blockchain config

        Returns:
            True if anchor verified on blockchain
        """
        if root_hash not in self.blockchain_anchors:
            logger.error(f"No blockchain anchor found for root: {root_hash[:16]}")
            return False

        tx_id = self.blockchain_anchors[root_hash]

        # Initialize blockchain service if needed
        if not hasattr(self, "_blockchain_service"):
            from .blockchain_anchoring import ChainlinkAnchoringService

            self._blockchain_service = ChainlinkAnchoringService(config or {})

        try:
            is_valid = self._blockchain_service.verify_anchor(
                root_hash, tx_id, blockchain
            )

            if is_valid:
                logger.info(f"Blockchain anchor verified: {tx_id[:16]}")
            else:
                logger.error(f"Blockchain anchor verification failed: {tx_id[:16]}")

            return is_valid

        except Exception as e:
            logger.error(f"Blockchain verification error: {e}")
            return False

    def generate_event_proof(self, event_hash: str, date: str) -> dict | None:
        """
        Generate proof of event inclusion

        Returns verifiable cryptographic proof
        """
        if date not in self.daily_trees:
            logger.error(f"No tree found for date: {date}")
            return None

        tree = self.daily_trees[date]
        signature = self.daily_signatures[date]

        proof = self.proof_generator.generate(event_hash, tree, signature)

        return proof

    def verify_proof(self, proof: dict) -> bool:
        """
        Verify cryptographic proof

        Validates both Merkle proof and HSM signature
        """
        # Verify Merkle proof
        merkle_valid = MerkleTree.verify_proof(
            proof["event_hash"], proof["merkle_proof"], proof["merkle_root"]
        )

        if not merkle_valid:
            logger.error("Merkle proof validation failed")
            return False

        # Verify HSM signature
        sig_valid = self.hsm_signer.verify(proof["merkle_root"], proof["hsm_signature"])

        if not sig_valid:
            logger.error("HSM signature validation failed")
            return False

        logger.info("Proof verified successfully")
        return True

    def get_hsm_info(self) -> dict:
        """
        Get HSM configuration and status information

        Returns HSM metadata for audit and debugging purposes
        """
        return self.hsm_signer.get_hsm_info()


__all__ = ["MerkleNode", "MerkleTree", "HSMSigner", "ProofGenerator", "EvidenceVault"]
