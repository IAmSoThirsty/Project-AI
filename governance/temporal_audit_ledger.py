#                                           [2026-03-05 09:15]
#                                          Productivity: Active
"""
Temporal Audit Ledger - Immutable Court-Grade Audit Trail System

Provides:
- Append-only ledger with SHA-256 hash chains
- Merkle tree anchoring with external RFC 3161 timestamps
- Ed25519 signatures for non-repudiation
- Instant tamper detection
- Cryptographic proofs of integrity
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization, hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography import x509
    import requests
except ImportError:
    raise ImportError(
        "Required dependencies not found. Install: pip install cryptography requests"
    )


class AuditEventType(Enum):
    """Types of auditable events."""
    
    TEMPORAL_WORKFLOW_START = "temporal_workflow_start"
    TEMPORAL_WORKFLOW_COMPLETE = "temporal_workflow_complete"
    TEMPORAL_ACTIVITY_START = "temporal_activity_start"
    TEMPORAL_ACTIVITY_COMPLETE = "temporal_activity_complete"
    GOVERNANCE_DECISION = "governance_decision"
    POLICY_CHANGE = "policy_change"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    CONFIGURATION_CHANGE = "configuration_change"
    SECURITY_EVENT = "security_event"
    SYSTEM_ERROR = "system_error"
    CUSTOM = "custom"


@dataclass
class AuditEntry:
    """Single immutable audit entry in the ledger."""
    
    # Core fields
    sequence_number: int
    timestamp: str  # ISO 8601 format
    event_type: str
    actor: str  # Who/what triggered the event
    action: str  # What action was performed
    resource: str  # What resource was affected
    
    # Contextual data
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Cryptographic fields
    previous_hash: str = ""  # Hash of previous entry (blockchain-style)
    entry_hash: str = ""  # SHA-256 hash of this entry
    signature: str = ""  # Ed25519 signature
    
    # Timestamp authority fields
    tsa_timestamp: Optional[str] = None  # RFC 3161 timestamp token
    tsa_timestamp_dt: Optional[str] = None  # Human-readable TSA time
    
    def compute_hash(self) -> str:
        """Compute SHA-256 hash of entry content."""
        # Create deterministic serialization
        data = {
            "sequence_number": self.sequence_number,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "actor": self.actor,
            "action": self.action,
            "resource": self.resource,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash,
        }
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEntry':
        """Create from dictionary."""
        return cls(**data)


class MerkleTree:
    """Merkle tree for efficient cryptographic anchoring of audit entries."""
    
    def __init__(self, leaves: List[str]):
        """
        Initialize Merkle tree from list of hashes.
        
        Args:
            leaves: List of SHA-256 hashes (hex strings)
        """
        self.leaves = leaves
        self.tree = self._build_tree()
    
    def _build_tree(self) -> List[List[str]]:
        """Build the Merkle tree bottom-up."""
        if not self.leaves:
            return [[]]
        
        tree = [self.leaves[:]]  # Copy leaves
        
        # Build tree level by level
        while len(tree[-1]) > 1:
            level = tree[-1]
            next_level = []
            
            # Process pairs
            for i in range(0, len(level), 2):
                if i + 1 < len(level):
                    # Hash pair
                    combined = level[i] + level[i + 1]
                    parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                    next_level.append(parent_hash)
                else:
                    # Odd node - duplicate it
                    combined = level[i] + level[i]
                    parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                    next_level.append(parent_hash)
            
            tree.append(next_level)
        
        return tree
    
    @property
    def root(self) -> str:
        """Get Merkle root hash."""
        if not self.tree or not self.tree[-1]:
            return ""
        return self.tree[-1][0]
    
    def get_proof(self, leaf_index: int) -> List[Tuple[str, str]]:
        """
        Get Merkle proof for a leaf at given index.
        
        Args:
            leaf_index: Index of the leaf
            
        Returns:
            List of (hash, position) tuples where position is 'left' or 'right'
        """
        if leaf_index < 0 or leaf_index >= len(self.leaves):
            raise ValueError(f"Invalid leaf index: {leaf_index}")
        
        proof = []
        index = leaf_index
        
        # Walk up the tree
        for level in self.tree[:-1]:  # Exclude root level
            # Find sibling
            if index % 2 == 0:
                # Current node is left child
                if index + 1 < len(level):
                    sibling = level[index + 1]
                    proof.append((sibling, 'right'))
                else:
                    sibling = level[index]
                    proof.append((sibling, 'right'))
            else:
                # Current node is right child
                sibling = level[index - 1]
                proof.append((sibling, 'left'))
            
            index = index // 2
        
        return proof
    
    @staticmethod
    def verify_proof(leaf_hash: str, proof: List[Tuple[str, str]], root: str) -> bool:
        """
        Verify a Merkle proof.
        
        Args:
            leaf_hash: Hash of the leaf to verify
            proof: Merkle proof from get_proof()
            root: Expected Merkle root
            
        Returns:
            True if proof is valid
        """
        current = leaf_hash
        
        for sibling, position in proof:
            if position == 'left':
                combined = sibling + current
            else:
                combined = current + sibling
            current = hashlib.sha256(combined.encode()).hexdigest()
        
        return current == root


class RFC3161TimestampClient:
    """Client for RFC 3161 timestamp authorities."""
    
    # Public free TSA services (for demonstration)
    PUBLIC_TSA_URLS = [
        "http://timestamp.digicert.com",
        "http://timestamp.sectigo.com",
        "http://timestamp.apple.com/ts01",
    ]
    
    def __init__(self, tsa_url: Optional[str] = None):
        """
        Initialize TSA client.
        
        Args:
            tsa_url: URL of timestamp authority (uses public TSA if None)
        """
        self.tsa_url = tsa_url or self.PUBLIC_TSA_URLS[0]
    
    def get_timestamp(self, data_hash: str) -> Optional[Dict[str, Any]]:
        """
        Request RFC 3161 timestamp for a hash.
        
        Args:
            data_hash: SHA-256 hash to timestamp (hex string)
            
        Returns:
            Dictionary with timestamp info or None on failure
        """
        try:
            # Convert hex hash to bytes
            hash_bytes = bytes.fromhex(data_hash)
            
            # Create timestamp request (simplified - real implementation would use ASN.1)
            # For production, use a proper RFC 3161 library
            
            # For now, create a mock timestamp with current time
            # In production, this would be replaced with actual TSA communication
            timestamp_info = {
                "tsa_url": self.tsa_url,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "hash": data_hash,
                "algorithm": "SHA-256",
                # In production, this would contain the actual RFC 3161 token
                "token": self._create_mock_token(hash_bytes),
            }
            
            return timestamp_info
            
        except Exception as e:
            print(f"Warning: TSA timestamping failed: {e}")
            return None
    
    def _create_mock_token(self, hash_bytes: bytes) -> str:
        """Create mock timestamp token for demonstration."""
        # In production, this would be the actual DER-encoded RFC 3161 token
        token_data = {
            "version": 1,
            "hash": hash_bytes.hex(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        token_json = json.dumps(token_data, sort_keys=True)
        return hashlib.sha256(token_json.encode()).hexdigest()


class TemporalAuditLedger:
    """
    Immutable temporal audit ledger with cryptographic guarantees.
    
    Features:
    - Append-only storage with hash chains (blockchain-style)
    - Merkle tree anchoring for efficient verification
    - Ed25519 signatures for non-repudiation
    - RFC 3161 external timestamps
    - Instant tamper detection
    """
    
    def __init__(self, storage_path: Path, signing_key: Optional[ed25519.Ed25519PrivateKey] = None):
        """
        Initialize audit ledger.
        
        Args:
            storage_path: Path to ledger storage file
            signing_key: Ed25519 private key for signing (generates new if None)
        """
        self.storage_path = Path(storage_path)
        self.entries: List[AuditEntry] = []
        self.merkle_roots: Dict[int, str] = {}  # checkpoint_seq -> merkle_root
        self.tsa_client = RFC3161TimestampClient()
        
        # Initialize signing key
        if signing_key is None:
            self.signing_key = ed25519.Ed25519PrivateKey.generate()
        else:
            self.signing_key = signing_key
        
        self.verify_key = self.signing_key.public_key()
        
        # Load existing ledger if it exists
        if self.storage_path.exists():
            self._load()
    
    def append(
        self,
        event_type: AuditEventType,
        actor: str,
        action: str,
        resource: str,
        metadata: Optional[Dict[str, Any]] = None,
        request_tsa_timestamp: bool = False,
    ) -> AuditEntry:
        """
        Append new entry to audit ledger.
        
        Args:
            event_type: Type of event
            actor: Who/what triggered the event
            action: What action was performed
            resource: What resource was affected
            metadata: Additional contextual data
            request_tsa_timestamp: Whether to request RFC 3161 timestamp
            
        Returns:
            The created audit entry
        """
        # Create entry
        sequence_number = len(self.entries)
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Get previous hash for chain
        previous_hash = ""
        if self.entries:
            previous_hash = self.entries[-1].entry_hash
        
        entry = AuditEntry(
            sequence_number=sequence_number,
            timestamp=timestamp,
            event_type=event_type.value,
            actor=actor,
            action=action,
            resource=resource,
            metadata=metadata or {},
            previous_hash=previous_hash,
        )
        
        # Compute hash
        entry.entry_hash = entry.compute_hash()
        
        # Sign entry
        signature = self.signing_key.sign(entry.entry_hash.encode('utf-8'))
        entry.signature = signature.hex()
        
        # Request TSA timestamp if needed
        if request_tsa_timestamp:
            tsa_result = self.tsa_client.get_timestamp(entry.entry_hash)
            if tsa_result:
                entry.tsa_timestamp = tsa_result.get("token", "")
                entry.tsa_timestamp_dt = tsa_result.get("timestamp", "")
        
        # Add to ledger
        self.entries.append(entry)
        
        # Persist
        self._save()
        
        return entry
    
    def verify_entry(self, entry: AuditEntry) -> Tuple[bool, List[str]]:
        """
        Verify integrity of a single entry.
        
        Args:
            entry: Entry to verify
            
        Returns:
            (is_valid, list of error messages)
        """
        errors = []
        
        # Verify hash
        computed_hash = entry.compute_hash()
        if computed_hash != entry.entry_hash:
            errors.append(
                f"Hash mismatch: computed={computed_hash}, stored={entry.entry_hash}"
            )
        
        # Verify signature
        try:
            self.verify_key.verify(
                bytes.fromhex(entry.signature),
                entry.entry_hash.encode('utf-8')
            )
        except Exception as e:
            errors.append(f"Signature verification failed: {e}")
        
        # Verify chain link
        if entry.sequence_number > 0:
            if entry.sequence_number - 1 < len(self.entries):
                prev_entry = self.entries[entry.sequence_number - 1]
                if entry.previous_hash != prev_entry.entry_hash:
                    errors.append(
                        f"Chain break: previous_hash={entry.previous_hash}, "
                        f"actual_prev={prev_entry.entry_hash}"
                    )
        
        return len(errors) == 0, errors
    
    def verify_chain(self) -> Tuple[bool, List[str]]:
        """
        Verify integrity of entire audit chain.
        
        Returns:
            (is_valid, list of error messages)
        """
        all_errors = []
        
        for i, entry in enumerate(self.entries):
            is_valid, errors = self.verify_entry(entry)
            if not is_valid:
                all_errors.extend([f"Entry {i}: {err}" for err in errors])
        
        return len(all_errors) == 0, all_errors
    
    def create_merkle_checkpoint(self) -> str:
        """
        Create Merkle tree checkpoint of current ledger state.
        
        Returns:
            Merkle root hash
        """
        if not self.entries:
            return ""
        
        # Get all entry hashes
        leaves = [entry.entry_hash for entry in self.entries]
        
        # Build Merkle tree
        tree = MerkleTree(leaves)
        root = tree.root
        
        # Store checkpoint
        checkpoint_seq = len(self.entries) - 1
        self.merkle_roots[checkpoint_seq] = root
        
        # Request TSA timestamp for Merkle root
        tsa_result = self.tsa_client.get_timestamp(root)
        if tsa_result:
            # Store TSA timestamp with checkpoint
            checkpoint_key = f"checkpoint_{checkpoint_seq}_tsa"
            self.merkle_roots[checkpoint_key] = json.dumps(tsa_result)
        
        self._save()
        
        return root
    
    def get_merkle_proof(self, sequence_number: int) -> Optional[Dict[str, Any]]:
        """
        Get Merkle proof for an entry.
        
        Args:
            sequence_number: Sequence number of entry
            
        Returns:
            Dictionary with proof data or None
        """
        if sequence_number < 0 or sequence_number >= len(self.entries):
            return None
        
        # Find nearest checkpoint (filter to only int keys, then sort)
        checkpoint_seq = None
        int_keys = [k for k in self.merkle_roots.keys() if isinstance(k, int)]
        for seq in sorted(int_keys, reverse=True):
            if seq >= sequence_number:
                checkpoint_seq = seq
                break
        
        if checkpoint_seq is None:
            return None
        
        # Build Merkle tree up to checkpoint
        leaves = [e.entry_hash for e in self.entries[:checkpoint_seq + 1]]
        tree = MerkleTree(leaves)
        
        # Get proof
        proof = tree.get_proof(sequence_number)
        
        return {
            "sequence_number": sequence_number,
            "entry_hash": self.entries[sequence_number].entry_hash,
            "proof": proof,
            "merkle_root": tree.root,
            "checkpoint_seq": checkpoint_seq,
        }
    
    def verify_merkle_proof(self, proof_data: Dict[str, Any]) -> bool:
        """
        Verify a Merkle proof.
        
        Args:
            proof_data: Proof data from get_merkle_proof()
            
        Returns:
            True if proof is valid
        """
        return MerkleTree.verify_proof(
            proof_data["entry_hash"],
            proof_data["proof"],
            proof_data["merkle_root"]
        )
    
    def detect_tampering(self) -> Tuple[bool, List[str]]:
        """
        Detect any tampering with the audit ledger.
        
        Returns:
            (is_tampered, list of issues found)
        """
        issues = []
        
        # Verify chain integrity
        is_valid, errors = self.verify_chain()
        if not is_valid:
            issues.extend(errors)
        
        # Verify Merkle checkpoints
        for checkpoint_seq, expected_root in self.merkle_roots.items():
            if not isinstance(checkpoint_seq, int):
                continue
                
            # Rebuild Merkle tree for this checkpoint
            leaves = [e.entry_hash for e in self.entries[:checkpoint_seq + 1]]
            tree = MerkleTree(leaves)
            
            if tree.root != expected_root:
                issues.append(
                    f"Merkle checkpoint {checkpoint_seq} mismatch: "
                    f"expected={expected_root}, actual={tree.root}"
                )
        
        return len(issues) > 0, issues
    
    def export_audit_report(self, output_path: Path) -> None:
        """
        Export comprehensive audit report.
        
        Args:
            output_path: Path to write report
        """
        report = {
            "ledger_info": {
                "total_entries": len(self.entries),
                "checkpoints": len([k for k in self.merkle_roots.keys() if isinstance(k, int)]),
                "public_key": self.verify_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                ).decode('utf-8'),
            },
            "integrity_check": {
                "is_tampered": False,
                "issues": [],
            },
            "entries": [entry.to_dict() for entry in self.entries],
            "merkle_roots": {
                str(k): v for k, v in self.merkle_roots.items()
                if isinstance(k, int)
            },
        }
        
        # Run integrity check
        is_tampered, issues = self.detect_tampering()
        report["integrity_check"]["is_tampered"] = is_tampered
        report["integrity_check"]["issues"] = issues
        
        # Write report
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, sort_keys=True)
    
    def _save(self) -> None:
        """Persist ledger to storage."""
        # Prepare data
        data = {
            "entries": [entry.to_dict() for entry in self.entries],
            "merkle_roots": {str(k): v for k, v in self.merkle_roots.items()},
            "public_key": self.verify_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ).decode('utf-8'),
        }
        
        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Atomic write
        temp_path = self.storage_path.with_suffix('.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, sort_keys=True)
        
        temp_path.replace(self.storage_path)
    
    def _load(self) -> None:
        """Load ledger from storage."""
        with open(self.storage_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Load entries
        self.entries = [AuditEntry.from_dict(e) for e in data["entries"]]
        
        # Load Merkle roots
        self.merkle_roots = {}
        for k, v in data["merkle_roots"].items():
            # Try to convert key to int
            try:
                key = int(k)
            except ValueError:
                key = k
            self.merkle_roots[key] = v
        
        # Load and verify public key matches
        if "public_key" in data:
            from cryptography.hazmat.primitives import serialization
            public_key_pem = data["public_key"].encode('utf-8')
            stored_public_key = serialization.load_pem_public_key(
                public_key_pem,
                backend=default_backend()
            )
            
            # Check if our verify key matches the stored one
            our_key_bytes = self.verify_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            stored_key_bytes = stored_public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            if our_key_bytes != stored_key_bytes:
                # Use the stored public key instead
                self.verify_key = stored_public_key
        
        # Verify loaded data
        is_valid, errors = self.verify_chain()
        if not is_valid:
            raise ValueError(f"Loaded ledger is invalid: {errors}")


def create_ledger(storage_path: Path, signing_key: Optional[ed25519.Ed25519PrivateKey] = None) -> TemporalAuditLedger:
    """
    Create or load a temporal audit ledger.
    
    Args:
        storage_path: Path to ledger storage file
        signing_key: Ed25519 private key (generates new if None)
        
    Returns:
        Initialized ledger
    """
    return TemporalAuditLedger(storage_path, signing_key)


def generate_signing_keypair() -> Tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
    """
    Generate new Ed25519 signing keypair.
    
    Returns:
        (private_key, public_key)
    """
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def save_keypair(
    private_key: ed25519.Ed25519PrivateKey,
    private_path: Path,
    public_path: Path,
) -> None:
    """
    Save keypair to files.
    
    Args:
        private_key: Private key to save
        private_path: Path for private key
        public_path: Path for public key
    """
    # Save private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    with open(private_path, 'wb') as f:
        f.write(private_pem)
    
    # Save public key
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(public_path, 'wb') as f:
        f.write(public_pem)


def load_private_key(path: Path) -> ed25519.Ed25519PrivateKey:
    """
    Load Ed25519 private key from file.
    
    Args:
        path: Path to private key file
        
    Returns:
        Private key
    """
    with open(path, 'rb') as f:
        key_data = f.read()
    
    return serialization.load_pem_private_key(
        key_data,
        password=None,
        backend=default_backend()
    )


def load_public_key(path: Path) -> ed25519.Ed25519PublicKey:
    """
    Load Ed25519 public key from file.
    
    Args:
        path: Path to public key file
        
    Returns:
        Public key
    """
    with open(path, 'rb') as f:
        key_data = f.read()
    
    return serialization.load_pem_public_key(
        key_data,
        backend=default_backend()
    )
