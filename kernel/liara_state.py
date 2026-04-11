#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Liara State Preservation Layer - Zero Data Loss Failover

Provides comprehensive state preservation for Triumvirate failover scenarios:
- Complete state snapshot capture
- Ed25519 cryptographic anchoring for integrity
- Formal recovery proofs
- Write-ahead logging (WAL) for crash recovery
- Sub-second state restoration (<1s target)

Thirst of Gods Level Architecture
"""

import hashlib
import json
import logging
import struct
import threading
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Ed25519 cryptography
try:
    from nacl.signing import SigningKey, VerifyKey
    from nacl.encoding import HexEncoder
    HAS_NACL = True
except ImportError:
    HAS_NACL = False
    logging.warning("PyNaCl not available - using mock Ed25519")

logger = logging.getLogger(__name__)


class SnapshotFormat(Enum):
    """Snapshot storage formats"""
    BINARY = "binary"  # Compact binary format
    JSON = "json"  # Human-readable JSON
    MSGPACK = "msgpack"  # MessagePack compressed


class StateType(Enum):
    """Types of state that can be preserved"""
    PROCESS = "process"
    MEMORY = "memory"
    SCHEDULER = "scheduler"
    NETWORK = "network"
    FILESYSTEM = "filesystem"
    GOVERNANCE = "governance"
    CUSTOM = "custom"


@dataclass
class StateSnapshot:
    """Complete state snapshot with cryptographic anchoring"""
    
    snapshot_id: str
    timestamp: float
    controller_id: str  # Which Triumvirate pillar this came from
    state_type: StateType
    
    # State data (nested dict of all state)
    state_data: Dict[str, Any] = field(default_factory=dict)
    
    # Cryptographic anchoring
    merkle_root: Optional[str] = None  # Root hash of state tree
    signature: Optional[str] = None  # Ed25519 signature
    public_key: Optional[str] = None  # Verification key
    
    # Metadata
    version: int = 1
    compression: Optional[str] = None
    size_bytes: int = 0
    
    # Recovery proof data
    recovery_proof: Optional[Dict[str, Any]] = None


@dataclass
class WALEntry:
    """Write-Ahead Log entry for crash recovery"""
    
    sequence_number: int
    timestamp: float
    operation: str  # "begin", "update", "commit", "rollback"
    
    # State mutation
    state_key: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    
    # Cryptographic verification
    checksum: Optional[str] = None
    signature: Optional[str] = None


@dataclass
class RecoveryProof:
    """Formal proof that state was preserved correctly"""
    
    snapshot_id: str
    proof_type: str  # "merkle", "signature", "checksum"
    
    # Merkle proof path
    merkle_path: List[str] = field(default_factory=list)
    
    # Verification data
    original_hash: Optional[str] = None
    restored_hash: Optional[str] = None
    signature_valid: bool = False
    
    # Proof generation metadata
    generated_at: float = 0.0
    verified_at: Optional[float] = None
    verification_status: str = "pending"


class CryptographicAnchor:
    """Ed25519 signature-based state anchoring"""
    
    def __init__(self, key_path: Optional[Path] = None):
        if not HAS_NACL:
            logger.warning("PyNaCl not available - using mock crypto")
            # Use deterministic mock values
            self.signing_key = None
            self.verify_key = None
            self._mock_seed = b"mock_signing_key_seed_for_testing_12345678"  # Deterministic
            return
            
        if key_path and key_path.exists():
            # Load existing key
            with open(key_path, 'rb') as f:
                seed = f.read()
                self.signing_key = SigningKey(seed)
        else:
            # Generate new key
            self.signing_key = SigningKey.generate()
            if key_path:
                key_path.parent.mkdir(parents=True, exist_ok=True)
                with open(key_path, 'wb') as f:
                    f.write(bytes(self.signing_key))
                    
        self.verify_key = self.signing_key.verify_key
    
    def sign(self, data: bytes) -> str:
        """Sign data with Ed25519"""
        if not HAS_NACL:
            # Mock signature - deterministic based on data + seed
            combined = self._mock_seed + data
            return hashlib.sha256(combined).hexdigest()
            
        signed = self.signing_key.sign(data)
        return signed.signature.hex()
    
    def verify(self, data: bytes, signature: str, public_key_hex: str) -> bool:
        """Verify Ed25519 signature"""
        if not HAS_NACL:
            # Mock verification - regenerate expected signature
            combined = self._mock_seed + data
            expected = hashlib.sha256(combined).hexdigest()
            return signature == expected
            
        try:
            verify_key = VerifyKey(bytes.fromhex(public_key_hex))
            verify_key.verify(data, bytes.fromhex(signature))
            return True
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def get_public_key_hex(self) -> str:
        """Get public key as hex string"""
        if not HAS_NACL:
            return "mock_public_key_deterministic"
        return self.verify_key.encode(encoder=HexEncoder).decode()


class MerkleTree:
    """Merkle tree for state integrity verification"""
    
    def __init__(self):
        self.leaves: List[str] = []
        self.tree: List[List[str]] = []
    
    def add_leaf(self, data: bytes) -> None:
        """Add a leaf to the tree"""
        leaf_hash = hashlib.sha256(data).hexdigest()
        self.leaves.append(leaf_hash)
    
    def build(self) -> str:
        """Build the Merkle tree and return root hash"""
        if not self.leaves:
            return hashlib.sha256(b"").hexdigest()
            
        # Build tree bottom-up
        current_level = self.leaves.copy()
        self.tree = [current_level]
        
        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left
                
                # Hash the concatenation
                combined = left + right
                parent_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(parent_hash)
            
            self.tree.append(next_level)
            current_level = next_level
        
        return current_level[0]
    
    def get_proof(self, leaf_index: int) -> List[str]:
        """Get Merkle proof path for a specific leaf"""
        if leaf_index >= len(self.leaves):
            return []
        
        proof = []
        index = leaf_index
        
        for level in self.tree[:-1]:  # Exclude root
            sibling_index = index + 1 if index % 2 == 0 else index - 1
            if sibling_index < len(level):
                proof.append(level[sibling_index])
            index //= 2
        
        return proof
    
    @staticmethod
    def verify_proof(leaf_hash: str, proof: List[str], root_hash: str) -> bool:
        """Verify a Merkle proof"""
        current_hash = leaf_hash
        
        for sibling in proof:
            # Determine order (smaller hash first for determinism)
            if current_hash < sibling:
                combined = current_hash + sibling
            else:
                combined = sibling + current_hash
            
            current_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        return current_hash == root_hash


class WriteAheadLog:
    """Write-Ahead Log for crash recovery"""
    
    def __init__(self, wal_path: Path):
        self.wal_path = wal_path
        self.wal_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.sequence_counter = 0
        self.lock = threading.RLock()
        self.crypto = CryptographicAnchor()
        
        # Open WAL file in append mode
        self.wal_file = open(self.wal_path, 'ab', buffering=0)  # Unbuffered for safety
    
    def write_entry(self, operation: str, state_key: str, 
                   old_value: Any = None, new_value: Any = None) -> WALEntry:
        """Write an entry to the WAL"""
        with self.lock:
            entry = WALEntry(
                sequence_number=self.sequence_counter,
                timestamp=time.time(),
                operation=operation,
                state_key=state_key,
                old_value=old_value,
                new_value=new_value
            )
            self.sequence_counter += 1
            
            # Serialize entry
            entry_data = self._serialize_entry(entry)
            
            # Add checksum
            entry.checksum = hashlib.sha256(entry_data).hexdigest()
            
            # Sign entry
            entry.signature = self.crypto.sign(entry_data)
            
            # Write to log with length prefix
            full_entry = self._serialize_entry(entry)
            entry_length = struct.pack('<I', len(full_entry))
            self.wal_file.write(entry_length + full_entry)
            
            return entry
    
    def _serialize_entry(self, entry: WALEntry) -> bytes:
        """Serialize WAL entry to bytes"""
        entry_dict = asdict(entry)
        return json.dumps(entry_dict).encode('utf-8')
    
    def _deserialize_entry(self, data: bytes) -> WALEntry:
        """Deserialize WAL entry from bytes"""
        entry_dict = json.loads(data.decode('utf-8'))
        return WALEntry(**entry_dict)
    
    def read_all_entries(self) -> List[WALEntry]:
        """Read all entries from the WAL"""
        entries = []
        
        with open(self.wal_path, 'rb') as f:
            while True:
                # Read length prefix
                length_data = f.read(4)
                if not length_data:
                    break
                
                entry_length = struct.unpack('<I', length_data)[0]
                
                # Read entry data
                entry_data = f.read(entry_length)
                if len(entry_data) != entry_length:
                    logger.error("Corrupted WAL entry detected")
                    break
                
                entry = self._deserialize_entry(entry_data)
                entries.append(entry)
        
        return entries
    
    def truncate(self) -> None:
        """Truncate the WAL after successful checkpoint"""
        with self.lock:
            self.wal_file.close()
            with open(self.wal_path, 'wb'):
                pass
            self.wal_file = open(self.wal_path, 'ab', buffering=0)
            self.sequence_counter = 0
    
    def close(self) -> None:
        """Close the WAL file"""
        self.wal_file.close()


class LiaraStatePreservation:
    """Main state preservation orchestrator for Liara failover"""
    
    def __init__(self, state_dir: Optional[Path] = None,
                 snapshot_format: SnapshotFormat = SnapshotFormat.BINARY):
        self.state_dir = state_dir or Path("./liara_state")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.snapshot_format = snapshot_format
        self.crypto = CryptographicAnchor(self.state_dir / "signing_key.bin")
        
        # WAL for each state type
        self.wals: Dict[StateType, WriteAheadLog] = {}
        
        # In-memory snapshot cache
        self.snapshot_cache: Dict[str, StateSnapshot] = {}
        self.lock = threading.RLock()
        
        # Performance metrics
        self.snapshot_times: List[float] = []
        self.restore_times: List[float] = []
    
    def _get_wal(self, state_type: StateType) -> WriteAheadLog:
        """Get or create WAL for a state type"""
        if state_type not in self.wals:
            wal_path = self.state_dir / f"wal_{state_type.value}.log"
            self.wals[state_type] = WriteAheadLog(wal_path)
        return self.wals[state_type]
    
    def capture_snapshot(self, controller_id: str, state_type: StateType,
                        state_data: Dict[str, Any]) -> StateSnapshot:
        """
        Capture complete state snapshot with cryptographic anchoring
        
        Returns:
            StateSnapshot with merkle root and signature
        """
        start_time = time.perf_counter()
        
        snapshot_id = f"{controller_id}_{state_type.value}_{int(time.time() * 1000)}"
        
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            timestamp=time.time(),
            controller_id=controller_id,
            state_type=state_type,
            state_data=state_data,
            version=1,
            public_key=self.crypto.get_public_key_hex()
        )
        
        # Build Merkle tree for state integrity
        merkle = MerkleTree()
        self._add_state_to_merkle(state_data, merkle)
        snapshot.merkle_root = merkle.build()
        
        # Serialize for signing (BEFORE setting size_bytes to avoid circular dependency)
        serialized = self._serialize_snapshot(snapshot)
        
        # Now set size_bytes AFTER serialization used for signing
        snapshot.size_bytes = len(serialized)
        
        # Sign the snapshot (using the serialization that doesn't have size_bytes)
        snapshot.signature = self.crypto.sign(serialized)
        
        # Write to WAL
        wal = self._get_wal(state_type)
        wal.write_entry("snapshot", snapshot_id, None, snapshot_id)
        
        # Persist snapshot to disk
        self._persist_snapshot(snapshot)
        
        # Cache in memory
        with self.lock:
            self.snapshot_cache[snapshot_id] = snapshot
        
        elapsed = time.perf_counter() - start_time
        self.snapshot_times.append(elapsed)
        
        logger.info(f"Snapshot {snapshot_id} captured in {elapsed:.4f}s "
                   f"(size: {snapshot.size_bytes} bytes)")
        
        return snapshot
    
    def _add_state_to_merkle(self, state_data: Dict[str, Any], merkle: MerkleTree) -> None:
        """Recursively add state data to Merkle tree"""
        for key, value in sorted(state_data.items()):
            # Create deterministic leaf data
            leaf_data = f"{key}:{json.dumps(value, sort_keys=True)}".encode()
            merkle.add_leaf(leaf_data)
    
    def _serialize_snapshot(self, snapshot: StateSnapshot) -> bytes:
        """Serialize snapshot to bytes"""
        # Create a copy without signature for signing
        snapshot_dict = asdict(snapshot)
        snapshot_dict['signature'] = None
        # CRITICAL: size_bytes must be 0 for signing to ensure deterministic serialization
        # (since size_bytes is calculated FROM the serialization)
        snapshot_dict['size_bytes'] = 0
        
        # CRITICAL: StateType enum must be converted to string for deterministic serialization
        # This ensures the serialization is the same whether we have an enum or string
        if isinstance(snapshot_dict['state_type'], StateType):
            snapshot_dict['state_type'] = snapshot_dict['state_type'].value
        
        if self.snapshot_format == SnapshotFormat.JSON:
            return json.dumps(snapshot_dict, sort_keys=True).encode('utf-8')
        elif self.snapshot_format == SnapshotFormat.BINARY:
            # Custom binary format: JSON with length prefix
            json_data = json.dumps(snapshot_dict, sort_keys=True).encode('utf-8')
            return struct.pack('<I', len(json_data)) + json_data
        else:
            # Default to JSON
            return json.dumps(snapshot_dict, sort_keys=True).encode('utf-8')
    
    def _persist_snapshot(self, snapshot: StateSnapshot) -> None:
        """Persist snapshot to disk"""
        snapshot_path = self.state_dir / f"{snapshot.snapshot_id}.snapshot"
        
        with open(snapshot_path, 'w') as f:
            snapshot_dict = asdict(snapshot)
            # CRITICAL: Convert StateType enum to string for JSON serialization
            # This ensures consistency between in-memory and disk representations
            if isinstance(snapshot_dict['state_type'], StateType):
                snapshot_dict['state_type'] = snapshot_dict['state_type'].value
            json.dump(snapshot_dict, f, indent=2)
    
    def restore_snapshot(self, snapshot_id: str) -> Tuple[StateSnapshot, RecoveryProof]:
        """
        Restore state from snapshot with verification
        
        Returns:
            Tuple of (StateSnapshot, RecoveryProof)
        """
        start_time = time.perf_counter()
        
        # Load snapshot
        snapshot = self._load_snapshot(snapshot_id)
        
        # Verify cryptographic integrity
        proof = self.generate_recovery_proof(snapshot)
        
        if not proof.signature_valid:
            raise ValueError(f"Snapshot {snapshot_id} signature verification failed!")
        
        # Verify Merkle tree
        if not self._verify_merkle_integrity(snapshot):
            raise ValueError(f"Snapshot {snapshot_id} Merkle tree verification failed!")
        
        elapsed = time.perf_counter() - start_time
        self.restore_times.append(elapsed)
        
        logger.info(f"Snapshot {snapshot_id} restored in {elapsed:.4f}s")
        
        if elapsed >= 1.0:
            logger.warning(f"Restoration time {elapsed:.4f}s exceeds 1s target!")
        
        return snapshot, proof
    
    def _load_snapshot(self, snapshot_id: str) -> StateSnapshot:
        """Load snapshot from disk or cache"""
        # Check cache first
        with self.lock:
            if snapshot_id in self.snapshot_cache:
                return self.snapshot_cache[snapshot_id]
        
        # Load from disk
        snapshot_path = self.state_dir / f"{snapshot_id}.snapshot"
        
        if not snapshot_path.exists():
            raise FileNotFoundError(f"Snapshot {snapshot_id} not found")
        
        with open(snapshot_path, 'r') as f:
            snapshot_dict = json.load(f)
        
        # Convert state_type back to enum
        snapshot_dict['state_type'] = StateType(snapshot_dict['state_type'])
        
        snapshot = StateSnapshot(**snapshot_dict)
        
        # Cache it
        with self.lock:
            self.snapshot_cache[snapshot_id] = snapshot
        
        return snapshot
    
    def generate_recovery_proof(self, snapshot: StateSnapshot) -> RecoveryProof:
        """
        Generate formal proof that state was preserved correctly
        """
        proof = RecoveryProof(
            snapshot_id=snapshot.snapshot_id,
            proof_type="signature+merkle",
            generated_at=time.time()
        )
        
        # Verify signature - create a copy for serialization without the signature
        snapshot_copy = StateSnapshot(
            snapshot_id=snapshot.snapshot_id,
            timestamp=snapshot.timestamp,
            controller_id=snapshot.controller_id,
            state_type=snapshot.state_type,
            state_data=snapshot.state_data,
            merkle_root=snapshot.merkle_root,
            signature=None,  # Exclude signature for verification
            public_key=snapshot.public_key,
            version=snapshot.version,
            compression=snapshot.compression,
            size_bytes=snapshot.size_bytes,
            recovery_proof=snapshot.recovery_proof
        )
        
        serialized = self._serialize_snapshot(snapshot_copy)
        proof.original_hash = hashlib.sha256(serialized).hexdigest()
        
        if snapshot.signature and snapshot.public_key:
            # Debug: log signature and data hash
            logger.debug(f"Verifying signature for {snapshot.snapshot_id}")
            logger.debug(f"Data hash: {proof.original_hash}")
            logger.debug(f"Signature: {snapshot.signature[:32]}...")
            
            proof.signature_valid = self.crypto.verify(
                serialized,
                snapshot.signature,
                snapshot.public_key
            )
            
            logger.debug(f"Signature valid: {proof.signature_valid}")
        else:
            proof.signature_valid = False
            logger.warning(f"No signature or public key for {snapshot.snapshot_id}")
        
        # Build Merkle tree from current state and compare
        merkle = MerkleTree()
        self._add_state_to_merkle(snapshot.state_data, merkle)
        computed_root = merkle.build()
        
        proof.restored_hash = computed_root
        
        # Verification status
        if proof.signature_valid and computed_root == snapshot.merkle_root:
            proof.verification_status = "verified"
        else:
            proof.verification_status = "failed"
        
        proof.verified_at = time.time()
        
        return proof
    
    def _verify_merkle_integrity(self, snapshot: StateSnapshot) -> bool:
        """Verify Merkle tree integrity of snapshot"""
        merkle = MerkleTree()
        self._add_state_to_merkle(snapshot.state_data, merkle)
        computed_root = merkle.build()
        
        return computed_root == snapshot.merkle_root
    
    def replay_wal(self, state_type: StateType) -> Dict[str, Any]:
        """
        Replay WAL to recover state after crash
        
        Returns:
            Reconstructed state dictionary
        """
        wal = self._get_wal(state_type)
        entries = wal.read_all_entries()
        
        logger.info(f"Replaying {len(entries)} WAL entries for {state_type.value}")
        
        reconstructed_state = {}
        
        for entry in entries:
            if entry.operation == "begin":
                # Start of transaction
                pass
            elif entry.operation == "update":
                # Apply state update
                reconstructed_state[entry.state_key] = entry.new_value
            elif entry.operation == "commit":
                # Transaction committed
                pass
            elif entry.operation == "rollback":
                # Rollback - restore old value
                if entry.state_key in reconstructed_state:
                    reconstructed_state[entry.state_key] = entry.old_value
        
        return reconstructed_state
    
    def checkpoint(self, state_type: StateType) -> None:
        """Checkpoint WAL - truncate after successful snapshot"""
        wal = self._get_wal(state_type)
        wal.truncate()
        logger.info(f"WAL checkpointed for {state_type.value}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {
            "snapshot_count": len(self.snapshot_times),
            "restore_count": len(self.restore_times),
            "avg_snapshot_time": 0.0,
            "avg_restore_time": 0.0,
            "max_snapshot_time": 0.0,
            "max_restore_time": 0.0,
            "sub_second_restores": 0,
            "restoration_target_met": False
        }
        
        if self.snapshot_times:
            stats["avg_snapshot_time"] = sum(self.snapshot_times) / len(self.snapshot_times)
            stats["max_snapshot_time"] = max(self.snapshot_times)
        
        if self.restore_times:
            stats["avg_restore_time"] = sum(self.restore_times) / len(self.restore_times)
            stats["max_restore_time"] = max(self.restore_times)
            stats["sub_second_restores"] = sum(1 for t in self.restore_times if t < 1.0)
            stats["restoration_target_met"] = stats["avg_restore_time"] < 1.0
        
        return stats
    
    def close(self) -> None:
        """Close all WAL files"""
        for wal in self.wals.values():
            wal.close()


# High-level API functions

def create_triumvirate_snapshot(controller_id: str, 
                                process_state: Dict[str, Any],
                                memory_state: Dict[str, Any],
                                scheduler_state: Dict[str, Any]) -> List[StateSnapshot]:
    """
    Create complete Triumvirate controller snapshot
    
    Args:
        controller_id: ID of the controller being snapshotted
        process_state: Process state dictionary
        memory_state: Memory state dictionary
        scheduler_state: Scheduler state dictionary
    
    Returns:
        List of StateSnapshot objects (one per state type)
    """
    preserver = LiaraStatePreservation()
    
    snapshots = [
        preserver.capture_snapshot(controller_id, StateType.PROCESS, process_state),
        preserver.capture_snapshot(controller_id, StateType.MEMORY, memory_state),
        preserver.capture_snapshot(controller_id, StateType.SCHEDULER, scheduler_state)
    ]
    
    preserver.close()
    
    return snapshots


def restore_triumvirate_state(snapshot_ids: List[str]) -> Dict[StateType, Dict[str, Any]]:
    """
    Restore complete Triumvirate state from snapshots
    
    Args:
        snapshot_ids: List of snapshot IDs to restore
    
    Returns:
        Dictionary mapping StateType to restored state data
    """
    preserver = LiaraStatePreservation()
    
    restored_states = {}
    
    for snapshot_id in snapshot_ids:
        snapshot, proof = preserver.restore_snapshot(snapshot_id)
        
        if proof.verification_status != "verified":
            raise ValueError(f"Failed to verify snapshot {snapshot_id}")
        
        restored_states[snapshot.state_type] = snapshot.state_data
    
    preserver.close()
    
    return restored_states
