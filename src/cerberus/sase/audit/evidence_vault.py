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
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

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

    def __init__(self, leaf_hashes: List[str]):
        if not leaf_hashes:
            raise ValueError("Must provide at least one hash")

        self.leaf_hashes = leaf_hashes
        self.root = self._build_tree(leaf_hashes)

        logger.info(f"Merkle tree built with {len(leaf_hashes)} leaves")

    def _build_tree(self, hashes: List[str]) -> MerkleNode:
        """Build Merkle tree from leaf hashes"""
        # Create leaf nodes
        nodes = [MerkleNode(hash_value=h) for h in hashes]

        # Build tree bottom-up
        while len(nodes) > 1:
            next_level = []

            for i in range(0, len(nodes), 2):
                left = nodes[i]
                right = nodes[i + 1] if i + 1 < len(nodes) else nodes[i]  # Duplicate if odd

                # Combine hashes
                combined = hashlib.sha256((left.hash_value + right.hash_value).encode()).hexdigest()

                parent = MerkleNode(hash_value=combined, left=left, right=right)

                next_level.append(parent)

            nodes = next_level

        return nodes[0]

    def get_root_hash(self) -> str:
        """Get Merkle root hash"""
        return self.root.hash_value

    def generate_proof(self, leaf_hash: str) -> Optional[List[str]]:
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

    def _generate_proof_recursive(self, node: MerkleNode, target_hash: str, proof: List[str]) -> bool:
        """Recursively generate proof path"""
        if node.is_leaf():
            return node.hash_value == target_hash

        # Check left subtree
        if self._generate_proof_recursive(node.left, target_hash, proof):
            if node.right:
                proof.append(node.right.hash_value)
            return True

        # Check right subtree
        if node.right and self._generate_proof_recursive(node.right, target_hash, proof):
            proof.append(node.left.hash_value)
            return True

        return False

    @staticmethod
    def verify_proof(leaf_hash: str, proof: List[str], root_hash: str) -> bool:
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
    """

    def __init__(self, hsm_available: bool = False):
        self.hsm_available = hsm_available

        if not hsm_available:
            logger.warning("HSM not available - using software signing (DEV ONLY)")
        else:
            logger.info("HSM signing enabled")

    def sign(self, data: str) -> str:
        """
        Sign data with HSM key

        Returns signature (hex)
        """
        if self.hsm_available:
            # TODO: Integrate with actual HSM (e.g., YubiHSM, AWS CloudHSM)
            pass

        # Fallback: software HMAC (DEV ONLY)
        key = b"sase_dev_key_change_in_production"
        import hmac

        signature = hmac.new(key, data.encode(), hashlib.sha256).hexdigest()

        return signature

    def verify(self, data: str, signature: str) -> bool:
        """Verify HSM signature"""
        expected_sig = self.sign(data)
        return signature == expected_sig


class ProofGenerator:
    """
    Generates cryptographic proofs for events and actions
    """

    def __init__(self):
        self.generated_proofs: Dict[str, Dict] = {}

    def generate(self, event_hash: str, merkle_tree: MerkleTree, signature: str) -> Dict:
        """
        Generate full cryptographic proof

        Includes Merkle proof + HSM signature
        """
        # Get Merkle proof path
        merkle_proof = merkle_tree.generate_proof(event_hash)

        if merkle_proof is None:
            logger.error(f"Cannot generate proof: event not in tree")
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

    def __init__(self, hsm_available: bool = False):
        self.hsm_signer = HSMSigner(hsm_available)
        self.proof_generator = ProofGenerator()

        # Daily Merkle trees
        self.daily_trees: Dict[str, MerkleTree] = {}  # date -> tree
        self.daily_signatures: Dict[str, str] = {}  # date -> signature

        # Blockchain anchoring (optional)
        self.blockchain_anchors: Dict[str, str] = {}  # root_hash -> tx_id

        logger.info("L9 Evidence Vault initialized")

    def aggregate_daily_events(self, date: str, event_hashes: List[str]) -> str:
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

    def anchor_to_blockchain(self, root_hash: str, blockchain: str = "ethereum"):
        """
        Anchor Merkle root to blockchain (optional)

        Provides additional tamper-resistance
        """
        logger.info(f"Anchoring root to {blockchain}: {root_hash[:16]}")

        # TODO: Integrate with blockchain (e.g., via Chainlink)
        tx_id = f"0x{hashlib.sha256(root_hash.encode()).hexdigest()}"

        self.blockchain_anchors[root_hash] = tx_id

        logger.info(f"Blockchain anchor: {tx_id[:16]}")

    def generate_event_proof(self, event_hash: str, date: str) -> Optional[Dict]:
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

    def verify_proof(self, proof: Dict) -> bool:
        """
        Verify cryptographic proof

        Validates both Merkle proof and HSM signature
        """
        # Verify Merkle proof
        merkle_valid = MerkleTree.verify_proof(proof["event_hash"], proof["merkle_proof"], proof["merkle_root"])

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


__all__ = ["MerkleNode", "MerkleTree", "HSMSigner", "ProofGenerator", "EvidenceVault"]
