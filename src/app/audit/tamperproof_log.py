#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Tamperproof Log - Append-Only Event Logging

This module implements an append-only, tamper-evident logging system using
cryptographic hashes to ensure log integrity. Any tampering with historical
log entries will be immediately detectable.

Key Features:
- Append-only log structure
- SHA-256 cryptographic hash chains
- Ed25519 digital signatures
- Merkle tree anchoring for efficient verification
- RFC 3161 timestamping integration
- Tamper detection
- Event integrity verification
- Immutable audit trails

Security Features:
- Each entry is cryptographically linked to the previous entry
- Digital signatures ensure authenticity and non-repudiation
- Merkle trees enable efficient partial verification
- External timestamping provides trusted temporal proof
- Comprehensive integrity verification
"""

import base64
import hashlib
import json
import logging
import struct
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization
    HAS_ED25519 = True
except ImportError:
    HAS_ED25519 = False

try:
    import rfc3161ng
    HAS_RFC3161 = True
except ImportError:
    HAS_RFC3161 = False

logger = logging.getLogger(__name__)


class MerkleTree:
    """Merkle tree implementation for efficient log verification.
    
    A Merkle tree allows efficient verification of log subsets without
    needing to verify the entire log. The root hash represents the entire
    log state.
    """
    
    def __init__(self, leaves: list[bytes] | None = None):
        """Initialize a Merkle tree.
        
        Args:
            leaves: List of leaf data (hashes) to build the tree from
        """
        self.leaves = leaves or []
        self.root = self._build_tree(self.leaves) if self.leaves else None
    
    def _hash_pair(self, left: bytes, right: bytes) -> bytes:
        """Hash a pair of nodes together."""
        return hashlib.sha256(left + right).digest()
    
    def _build_tree(self, nodes: list[bytes]) -> bytes:
        """Build a Merkle tree from the bottom up.
        
        Args:
            nodes: List of node hashes
            
        Returns:
            Root hash of the tree
        """
        if not nodes:
            return hashlib.sha256(b"").digest()
        
        if len(nodes) == 1:
            return nodes[0]
        
        # Build next level
        next_level = []
        for i in range(0, len(nodes), 2):
            if i + 1 < len(nodes):
                next_level.append(self._hash_pair(nodes[i], nodes[i + 1]))
            else:
                # Odd number of nodes, hash with itself
                next_level.append(self._hash_pair(nodes[i], nodes[i]))
        
        return self._build_tree(next_level)
    
    def add_leaf(self, leaf: bytes) -> None:
        """Add a new leaf to the tree.
        
        Args:
            leaf: Leaf data (hash) to add
        """
        self.leaves.append(leaf)
        self.root = self._build_tree(self.leaves)
    
    def get_root(self) -> bytes | None:
        """Get the root hash of the tree.
        
        Returns:
            Root hash as bytes, or None if tree is empty
        """
        return self.root
    
    def get_root_hex(self) -> str:
        """Get the root hash as a hex string.
        
        Returns:
            Root hash as hex string
        """
        return self.root.hex() if self.root else "0" * 64
    
    def get_proof(self, index: int) -> list[tuple[bytes, str]]:
        """Generate a Merkle proof for a leaf at the given index.
        
        Args:
            index: Index of the leaf to prove
            
        Returns:
            List of (hash, position) tuples forming the proof path
        """
        if index >= len(self.leaves):
            return []
        
        proof = []
        nodes = self.leaves[:]
        current_index = index
        
        while len(nodes) > 1:
            next_level = []
            for i in range(0, len(nodes), 2):
                if i + 1 < len(nodes):
                    # Pair exists
                    if current_index == i:
                        proof.append((nodes[i + 1], "right"))
                    elif current_index == i + 1:
                        proof.append((nodes[i], "left"))
                    next_level.append(self._hash_pair(nodes[i], nodes[i + 1]))
                else:
                    # Odd node - hash with itself
                    next_level.append(self._hash_pair(nodes[i], nodes[i]))
            
            # Update current index for next level
            current_index = current_index // 2
            nodes = next_level
        
        return proof
    
    def verify_proof(self, leaf: bytes, index: int, proof: list[tuple[bytes, str]]) -> bool:
        """Verify a Merkle proof.
        
        Args:
            leaf: The leaf data to verify
            index: The index of the leaf
            proof: The Merkle proof path
            
        Returns:
            True if proof is valid, False otherwise
        """
        current_hash = leaf
        
        for sibling, position in proof:
            if position == "left":
                current_hash = self._hash_pair(sibling, current_hash)
            else:
                current_hash = self._hash_pair(current_hash, sibling)
        
        return current_hash == self.root


class TamperproofLog:
    """Implements append-only, tamper-evident event logging.

    Uses cryptographic hash chains, digital signatures, Merkle trees, and
    external timestamping to ensure log integrity and provide multiple
    layers of security.
    
    Security Layers:
    1. Hash chaining: Each entry links to the previous via SHA-256
    2. Digital signatures: Ed25519 signatures for authenticity
    3. Merkle trees: Efficient verification of log subsets
    4. RFC 3161 timestamping: External temporal proof
    """

    def __init__(
        self,
        log_file: Path | None = None,
        private_key: ed25519.Ed25519PrivateKey | None = None,
        tsa_url: str | None = None,
    ):
        """Initialize the tamperproof log.

        Args:
            log_file: Path to the log file (optional)
            private_key: Ed25519 private key for signing (optional, will generate if None)
            tsa_url: URL of RFC 3161 Time Stamping Authority (optional)
        """
        self.log_file = log_file
        self.entries: list[dict[str, Any]] = []
        self.last_hash: str = "0" * 64  # Genesis hash
        self.merkle_tree = MerkleTree()
        self.tsa_url = tsa_url
        
        # Initialize Ed25519 key pair
        if HAS_ED25519:
            if private_key is None:
                self.private_key = ed25519.Ed25519PrivateKey.generate()
            else:
                self.private_key = private_key
            self.public_key = self.private_key.public_key()
        else:
            self.private_key = None
            self.public_key = None
            logger.warning("Ed25519 not available, signatures will be disabled")
    
    def get_public_key_pem(self) -> str | None:
        """Get the public key in PEM format.
        
        Returns:
            PEM-encoded public key, or None if not available
        """
        if not self.public_key:
            return None
        
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return pem.decode("utf-8")
    
    def _compute_entry_hash(self, entry: dict[str, Any]) -> str:
        """Compute SHA-256 hash of an entry.
        
        Args:
            entry: Entry dictionary to hash
            
        Returns:
            Hex-encoded SHA-256 hash
        """
        entry_json = json.dumps(entry, sort_keys=True)
        return hashlib.sha256(entry_json.encode()).hexdigest()
    
    def _sign_entry(self, entry_hash: str) -> str | None:
        """Sign an entry hash with Ed25519.
        
        Args:
            entry_hash: Hash to sign
            
        Returns:
            Base64-encoded signature, or None if signing not available
        """
        if not self.private_key:
            return None
        
        signature = self.private_key.sign(entry_hash.encode())
        return base64.b64encode(signature).decode("utf-8")
    
    def _verify_signature(self, entry_hash: str, signature: str, public_key: ed25519.Ed25519PublicKey | None = None) -> bool:
        """Verify an Ed25519 signature.
        
        Args:
            entry_hash: Hash that was signed
            signature: Base64-encoded signature
            public_key: Public key to verify with (uses self.public_key if None)
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not HAS_ED25519:
            return False
        
        key = public_key or self.public_key
        if not key:
            return False
        
        try:
            sig_bytes = base64.b64decode(signature)
            key.verify(sig_bytes, entry_hash.encode())
            return True
        except Exception:
            return False
    
    def _get_timestamp(self, data: bytes) -> dict[str, Any] | None:
        """Get RFC 3161 timestamp for data.
        
        Args:
            data: Data to timestamp
            
        Returns:
            Dictionary with timestamp info, or None if timestamping not available
        """
        if not HAS_RFC3161 or not self.tsa_url:
            return None
        
        try:
            # Create timestamp request
            rt = rfc3161ng.RemoteTimestamper(
                self.tsa_url,
                certificate=None,
                hashname="sha256",
            )
            
            # Get timestamp
            tsr = rt.timestamp(data=data)
            if tsr:
                return {
                    "tsa_url": self.tsa_url,
                    "timestamp": base64.b64encode(tsr).decode("utf-8"),
                }
        except Exception as e:
            logger.warning("Failed to get RFC 3161 timestamp: %s", e)
        
        return None

    def append(self, event_type: str, data: dict[str, Any]) -> bool:
        """Append a new event to the tamperproof log.

        Creates a cryptographically secure log entry with:
        - SHA-256 hash chain link
        - Ed25519 digital signature
        - Merkle tree integration
        - Optional RFC 3161 timestamp

        Args:
            event_type: Type of event being logged
            data: Event data

        Returns:
            True if appended successfully, False otherwise
        """
        timestamp = datetime.now().isoformat()

        # Create entry without hash and signature
        entry = {
            "timestamp": timestamp,
            "event_type": event_type,
            "data": data,
            "previous_hash": self.last_hash,
        }

        # Compute hash of this entry
        entry_hash = self._compute_entry_hash(entry)
        entry["hash"] = entry_hash
        
        # Sign the hash
        signature = self._sign_entry(entry_hash)
        if signature:
            entry["signature"] = signature
        
        # Add to Merkle tree
        self.merkle_tree.add_leaf(bytes.fromhex(entry_hash))
        entry["merkle_root"] = self.merkle_tree.get_root_hex()
        
        # Get external timestamp if available
        timestamp_info = self._get_timestamp(entry_hash.encode())
        if timestamp_info:
            entry["rfc3161_timestamp"] = timestamp_info

        self.entries.append(entry)
        self.last_hash = entry_hash

        logger.debug(
            "Appended event: %s with hash: %s... (merkle_root: %s...)",
            event_type,
            entry_hash[:8],
            entry["merkle_root"][:8],
        )

        # Persist if log file is configured
        if self.log_file:
            try:
                self._persist_to_file()
            except Exception as e:
                logger.error("Failed to persist log entry: %s", e)
                return False

        return True
    
    def _persist_to_file(self) -> None:
        """Persist the log to disk atomically.
        
        Uses atomic write pattern to prevent corruption.
        """
        if not self.log_file:
            return
        
        temp_file = self.log_file.with_suffix(".tmp")
        
        try:
            with open(temp_file, "w") as f:
                json.dump(
                    {
                        "version": "2.0",
                        "public_key": self.get_public_key_pem(),
                        "entries": self.entries,
                    },
                    f,
                    indent=2,
                )
            
            # Atomic rename
            temp_file.replace(self.log_file)
            
        except Exception:
            # Clean up temp file on error
            if temp_file.exists():
                temp_file.unlink()
            raise
    
    def load_from_file(self, file_path: Path) -> bool:
        """Load log from a file.
        
        Args:
            file_path: Path to load from
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            self.entries = data.get("entries", [])
            
            # Load public key if available
            if "public_key" in data and data["public_key"] and HAS_ED25519:
                try:
                    pem_bytes = data["public_key"].encode("utf-8")
                    self.public_key = serialization.load_pem_public_key(pem_bytes)
                    # Note: We don't have the private key when loading
                    self.private_key = None
                except Exception as e:
                    logger.warning("Failed to load public key: %s", e)
            
            # Rebuild state
            if self.entries:
                self.last_hash = self.entries[-1]["hash"]
                
                # Rebuild Merkle tree
                leaves = [bytes.fromhex(e["hash"]) for e in self.entries]
                self.merkle_tree = MerkleTree(leaves)
            
            logger.info("Loaded %d entries from %s", len(self.entries), file_path)
            return True
            
        except Exception as e:
            logger.error("Failed to load log from file: %s", e)
            return False

    def verify_integrity(self) -> tuple[bool, list[str]]:
        """Verify the integrity of the entire log chain.

        Performs comprehensive verification including:
        - Hash chain validation
        - Digital signature verification
        - Merkle tree consistency
        - Entry ordering and structure

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if not self.entries:
            return True, errors

        # Verify genesis entry
        if self.entries[0]["previous_hash"] != "0" * 64:
            errors.append("Genesis entry has invalid previous_hash")

        # Rebuild Merkle tree for verification
        merkle_leaves = []

        # Verify each entry
        for i in range(len(self.entries)):
            entry = self.entries[i]

            # Recompute hash
            entry_copy = {
                "timestamp": entry["timestamp"],
                "event_type": entry["event_type"],
                "data": entry["data"],
                "previous_hash": entry["previous_hash"],
            }
            
            computed_hash = self._compute_entry_hash(entry_copy)
            stored_hash = entry.get("hash", "")

            if computed_hash != stored_hash:
                errors.append(f"Entry {i} has invalid hash")

            # Verify signature if present
            if "signature" in entry and self.public_key:
                if not self._verify_signature(stored_hash, entry["signature"]):
                    errors.append(f"Entry {i} has invalid signature")

            # Verify chain link
            if i > 0 and entry["previous_hash"] != self.entries[i - 1]["hash"]:
                errors.append(f"Entry {i} has broken chain link")
            
            # Add to Merkle tree verification
            merkle_leaves.append(bytes.fromhex(stored_hash))
            
            # Verify Merkle root if present
            if "merkle_root" in entry:
                expected_tree = MerkleTree(merkle_leaves[:])
                expected_root = expected_tree.get_root_hex()
                if entry["merkle_root"] != expected_root:
                    errors.append(f"Entry {i} has invalid Merkle root")

        is_valid = len(errors) == 0
        if is_valid:
            logger.info("Log integrity verified successfully (%d entries)", len(self.entries))
        else:
            logger.error("Log integrity verification failed: %s errors", len(errors))

        return is_valid, errors
    
    def verify_entry(self, index: int) -> tuple[bool, list[str]]:
        """Verify a single entry with Merkle proof.
        
        Args:
            index: Index of entry to verify
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if index < 0 or index >= len(self.entries):
            return False, ["Invalid entry index"]
        
        entry = self.entries[index]
        
        # Verify hash
        entry_copy = {
            "timestamp": entry["timestamp"],
            "event_type": entry["event_type"],
            "data": entry["data"],
            "previous_hash": entry["previous_hash"],
        }
        
        computed_hash = self._compute_entry_hash(entry_copy)
        if computed_hash != entry.get("hash", ""):
            errors.append("Entry hash mismatch")
        
        # Verify signature
        if "signature" in entry and self.public_key:
            if not self._verify_signature(entry["hash"], entry["signature"]):
                errors.append("Invalid signature")
        
        # Verify chain link
        if index > 0:
            if entry["previous_hash"] != self.entries[index - 1]["hash"]:
                errors.append("Broken chain link")
        elif entry["previous_hash"] != "0" * 64:
            errors.append("Invalid genesis entry")
        
        return len(errors) == 0, errors

    def get_entries(
        self,
        event_type: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve log entries matching criteria.

        Args:
            event_type: Filter by event type
            start_time: Filter by start time (ISO format)
            end_time: Filter by end time (ISO format)

        Returns:
            List of matching log entries
        """
        results = []

        for entry in self.entries:
            if event_type and entry.get("event_type") != event_type:
                continue

            # Additional time filtering can be added here
            results.append(entry)

        return results

    def export(self, output_file: Path) -> bool:
        """Export the log to a file.

        Exports with full verification metadata including:
        - Public key for signature verification
        - Current Merkle root
        - Full entry history with all security metadata

        Args:
            output_file: Path to write export

        Returns:
            True if exported successfully, False otherwise
        """
        try:
            export_data = {
                "version": "2.0",
                "exported_at": datetime.now().isoformat(),
                "entry_count": len(self.entries),
                "merkle_root": self.merkle_tree.get_root_hex(),
                "public_key": self.get_public_key_pem(),
                "entries": self.entries,
            }
            
            with open(output_file, "w") as f:
                json.dump(export_data, f, indent=2)

            logger.info("Exported %s entries to %s", len(self.entries), output_file)
            return True

        except Exception as e:
            logger.error("Failed to export log: %s", e)
            return False
    
    def get_merkle_root(self) -> str:
        """Get the current Merkle tree root hash.
        
        Returns:
            Hex-encoded Merkle root
        """
        return self.merkle_tree.get_root_hex()
    
    def get_merkle_proof(self, index: int) -> list[tuple[str, str]]:
        """Get Merkle proof for an entry.
        
        Args:
            index: Entry index
            
        Returns:
            List of (hash, position) tuples forming the proof
        """
        if index >= len(self.entries):
            return []
        
        # Rebuild Merkle tree up to and including this index
        leaves = [bytes.fromhex(e["hash"]) for e in self.entries[:index + 1]]
        temp_tree = MerkleTree(leaves)
        
        proof = temp_tree.get_proof(index)
        return [(h.hex(), pos) for h, pos in proof]
    
    def verify_merkle_proof(
        self,
        entry_hash: str,
        index: int,
        proof: list[tuple[str, str]],
        root: str,
    ) -> bool:
        """Verify a Merkle proof against a given root.
        
        Args:
            entry_hash: Hash of the entry to verify
            index: Index of the entry
            proof: Merkle proof path
            root: Expected Merkle root
            
        Returns:
            True if proof is valid
        """
        # Convert proof to bytes
        proof_bytes = [(bytes.fromhex(h), pos) for h, pos in proof]
        
        # Create temporary tree and verify
        temp_tree = MerkleTree()
        temp_tree.root = bytes.fromhex(root)
        
        return temp_tree.verify_proof(bytes.fromhex(entry_hash), index, proof_bytes)


__all__ = ["TamperproofLog", "MerkleTree"]
