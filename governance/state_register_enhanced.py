"""
Enhanced STATE_REGISTER with Distributed Synchronization

Provides:
- Multi-node STATE_REGISTER synchronization using gossip protocol
- Vector clock integration for causal consistency
- Causal consistency verification with happens-before relationships
- Audit trail anchoring with Merkle roots
- Deterministic conflict resolution using LWW-Element-Set CRDT

Architecture:
- Each node maintains local state with vector clocks
- Synchronization uses anti-entropy gossip protocol
- Conflicts resolved using Last-Writer-Wins with vector clock ordering
- All state changes anchored to temporal audit ledger
- Merkle trees ensure cryptographic integrity
"""

import hashlib
import json
import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Imports will work when conftest.py sets up paths or when running standalone with PYTHONPATH
from cognition.temporal.vector_clock import VectorClock
from temporal_audit_ledger import TemporalAuditLedger, AuditEventType, MerkleTree

logger = logging.getLogger(__name__)


class StateValueType(Enum):
    """Types of state values that can be stored."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    BINARY = "binary"


class ConflictResolutionStrategy(Enum):
    """Strategies for resolving conflicting updates."""
    LWW_VECTOR_CLOCK = "lww_vector_clock"  # Last-writer-wins using vector clocks
    LWW_TIMESTAMP = "lww_timestamp"  # Last-writer-wins using wall-clock time
    MAX_VALUE = "max_value"  # Choose maximum value
    MIN_VALUE = "min_value"  # Choose minimum value
    CUSTOM = "custom"  # Custom resolution function


@dataclass
class StateValue:
    """
    A versioned state value with causality tracking.
    
    Attributes:
        key: State key
        value: Current value
        value_type: Type of the value
        version: Logical version number
        vector_clock: Vector clock at time of write
        node_id: ID of node that wrote this value
        timestamp: Wall-clock timestamp
        prev_hash: Hash of previous version (hash chain)
        merkle_root: Merkle root of audit trail at this point
    """
    key: str
    value: Any
    value_type: StateValueType
    version: int
    vector_clock: VectorClock
    node_id: str
    timestamp: datetime
    prev_hash: str = ""
    merkle_root: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def compute_hash(self) -> str:
        """Compute SHA-256 hash of this state value."""
        data = {
            "key": self.key,
            "value": self._serialize_value(),
            "value_type": self.value_type.value,
            "version": self.version,
            "vector_clock": self.vector_clock.to_dict(),
            "node_id": self.node_id,
            "timestamp": self.timestamp.isoformat(),
            "prev_hash": self.prev_hash,
        }
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def _serialize_value(self) -> Any:
        """Serialize value based on type."""
        if self.value_type == StateValueType.BINARY:
            if isinstance(self.value, bytes):
                return self.value.hex()
            return self.value
        elif self.value_type == StateValueType.JSON:
            if not isinstance(self.value, str):
                return json.dumps(self.value)
            return self.value
        return self.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "value": self._serialize_value(),
            "value_type": self.value_type.value,
            "version": self.version,
            "vector_clock": self.vector_clock.to_dict(),
            "node_id": self.node_id,
            "timestamp": self.timestamp.isoformat(),
            "prev_hash": self.prev_hash,
            "merkle_root": self.merkle_root,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateValue":
        """Create from dictionary."""
        value_type = StateValueType(data["value_type"])
        value = data["value"]
        
        # Deserialize based on type
        if value_type == StateValueType.BINARY:
            if isinstance(value, str):
                value = bytes.fromhex(value)
        elif value_type == StateValueType.JSON:
            if isinstance(value, str):
                value = json.loads(value)
        
        return cls(
            key=data["key"],
            value=value,
            value_type=value_type,
            version=data["version"],
            vector_clock=VectorClock.from_dict(data["vector_clock"]),
            node_id=data["node_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            prev_hash=data.get("prev_hash", ""),
            merkle_root=data.get("merkle_root", ""),
            metadata=data.get("metadata", {}),
        )


@dataclass
class SyncMessage:
    """Message for state synchronization between nodes."""
    message_id: str
    sender_node_id: str
    message_type: str  # "state_update", "sync_request", "sync_response"
    vector_clock: VectorClock
    state_values: List[StateValue]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "message_id": self.message_id,
            "sender_node_id": self.sender_node_id,
            "message_type": self.message_type,
            "vector_clock": self.vector_clock.to_dict(),
            "state_values": [sv.to_dict() for sv in self.state_values],
            "timestamp": self.timestamp.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SyncMessage":
        """Create from dictionary."""
        return cls(
            message_id=data["message_id"],
            sender_node_id=data["sender_node_id"],
            message_type=data["message_type"],
            vector_clock=VectorClock.from_dict(data["vector_clock"]),
            state_values=[StateValue.from_dict(sv) for sv in data["state_values"]],
            timestamp=datetime.fromisoformat(data["timestamp"]),
        )


class DistributedStateRegister:
    """
    Distributed state register with causal consistency guarantees.
    
    Features:
    - Multi-node synchronization using gossip protocol
    - Vector clocks for causal ordering
    - LWW-Element-Set CRDT for conflict resolution
    - Merkle tree anchoring for integrity
    - Integration with temporal audit ledger
    - Happens-before relationship verification
    
    Architecture:
    - Each node maintains local state with version history
    - Synchronization via anti-entropy gossip
    - All updates logged to audit ledger
    - Periodic checkpointing with Merkle roots
    """
    
    def __init__(
        self,
        node_id: str,
        storage_path: Path,
        audit_ledger: TemporalAuditLedger,
        conflict_strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.LWW_VECTOR_CLOCK,
        checkpoint_interval: int = 100,
        sync_interval_seconds: float = 30.0,
    ):
        """
        Initialize distributed state register.
        
        Args:
            node_id: Unique identifier for this node
            storage_path: Path to persistent storage
            audit_ledger: Temporal audit ledger for anchoring
            conflict_strategy: Strategy for resolving conflicts
            checkpoint_interval: Create checkpoint every N operations
            sync_interval_seconds: Gossip sync interval
        """
        self.node_id = node_id
        self.storage_path = Path(storage_path)
        self.audit_ledger = audit_ledger
        self.conflict_strategy = conflict_strategy
        self.checkpoint_interval = checkpoint_interval
        self.sync_interval = sync_interval_seconds
        
        # Core state storage
        self.state: Dict[str, StateValue] = {}  # key -> current state value
        self.history: Dict[str, List[StateValue]] = defaultdict(list)  # key -> version history
        
        # Vector clock for this node
        self.vector_clock = VectorClock(node_id)
        
        # Known nodes and their clocks
        self.peer_nodes: Set[str] = set()
        self.peer_clocks: Dict[str, VectorClock] = {}
        
        # Checkpointing
        self.operation_count = 0
        self.last_checkpoint_seq = 0
        self.checkpoints: List[Tuple[int, str]] = []  # (seq, merkle_root)
        
        # Statistics
        self.sync_count = 0
        self.conflict_count = 0
        self.last_sync_time = datetime.now(timezone.utc)
        
        # Load persisted state
        self._load_state()
        
        logger.info(
            "DistributedStateRegister initialized: node=%s, strategy=%s",
            node_id, conflict_strategy.value
        )
    
    def put(
        self,
        key: str,
        value: Any,
        value_type: StateValueType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> StateValue:
        """
        Store or update a state value.
        
        This operation:
        1. Increments local vector clock
        2. Creates versioned state value
        3. Resolves conflicts if key exists
        4. Logs to audit ledger
        5. Updates Merkle root
        6. Triggers checkpoint if needed
        
        Args:
            key: State key
            value: Value to store
            value_type: Type of value
            metadata: Optional metadata
            
        Returns:
            StateValue that was stored
        """
        # Increment vector clock
        self.vector_clock.tick()
        
        # Get previous value for hash chaining
        prev_hash = ""
        version = 1
        if key in self.state:
            prev_value = self.state[key]
            prev_hash = prev_value.compute_hash()
            version = prev_value.version + 1
        
        # Create new state value
        state_value = StateValue(
            key=key,
            value=value,
            value_type=value_type,
            version=version,
            vector_clock=self.vector_clock.copy(),
            node_id=self.node_id,
            timestamp=datetime.now(timezone.utc),
            prev_hash=prev_hash,
            metadata=metadata or {},
        )
        
        # Store state
        self.state[key] = state_value
        self.history[key].append(state_value)
        self.operation_count += 1
        
        # Log to audit ledger
        self._audit_state_change("put", key, state_value)
        
        # Checkpoint if needed
        if self.operation_count % self.checkpoint_interval == 0:
            self._create_checkpoint()
        
        logger.debug(
            "State PUT: node=%s, key=%s, version=%d, vclock=%s",
            self.node_id, key, version, self.vector_clock
        )
        
        return state_value
    
    def get(self, key: str) -> Optional[StateValue]:
        """
        Retrieve current state value.
        
        Args:
            key: State key
            
        Returns:
            Current StateValue or None if not found
        """
        return self.state.get(key)
    
    def get_version(self, key: str, version: int) -> Optional[StateValue]:
        """
        Retrieve specific version of state value.
        
        Args:
            key: State key
            version: Version number
            
        Returns:
            StateValue at that version or None
        """
        if key not in self.history:
            return None
        
        for state_value in self.history[key]:
            if state_value.version == version:
                return state_value
        
        return None
    
    def delete(self, key: str) -> bool:
        """
        Mark a key as deleted (tombstone).
        
        Args:
            key: State key
            
        Returns:
            True if key existed
        """
        if key not in self.state:
            return False
        
        # Create tombstone
        self.vector_clock.tick()
        
        tombstone = StateValue(
            key=key,
            value=None,
            value_type=StateValueType.STRING,
            version=self.state[key].version + 1,
            vector_clock=self.vector_clock.copy(),
            node_id=self.node_id,
            timestamp=datetime.now(timezone.utc),
            prev_hash=self.state[key].compute_hash(),
            metadata={"tombstone": True},
        )
        
        self.state[key] = tombstone
        self.history[key].append(tombstone)
        self.operation_count += 1
        
        self._audit_state_change("delete", key, tombstone)
        
        return True
    
    def sync_with_peer(self, peer_state: Dict[str, StateValue], peer_clock: VectorClock) -> List[str]:
        """
        Synchronize state with a peer node.
        
        This implements anti-entropy gossip protocol:
        1. Compare vector clocks to find divergence
        2. Merge conflicting updates using resolution strategy
        3. Update local vector clock
        4. Return list of keys that were updated
        
        Args:
            peer_state: State from peer node
            peer_clock: Vector clock from peer
            
        Returns:
            List of keys that were updated due to sync
        """
        updated_keys = []
        
        # Merge peer's vector clock
        self.vector_clock.merge(peer_clock)
        
        # Process each key from peer
        for key, peer_value in peer_state.items():
            if key not in self.state:
                # New key - adopt it
                self.state[key] = peer_value
                self.history[key].append(peer_value)
                updated_keys.append(key)
                self._audit_state_change("sync_new", key, peer_value)
            else:
                local_value = self.state[key]
                
                # Check for conflict using vector clock
                comparison = local_value.vector_clock.compare(peer_value.vector_clock)
                
                if comparison == "before":
                    # Peer value is causally after local - accept it
                    self.state[key] = peer_value
                    self.history[key].append(peer_value)
                    updated_keys.append(key)
                    self._audit_state_change("sync_update", key, peer_value)
                
                elif comparison == "concurrent":
                    # Concurrent updates - resolve conflict
                    resolved = self._resolve_conflict(local_value, peer_value)
                    if resolved != local_value:
                        self.state[key] = resolved
                        self.history[key].append(resolved)
                        updated_keys.append(key)
                        self.conflict_count += 1
                        self._audit_state_change("sync_conflict_resolved", key, resolved)
                
                # If "after" or "equal", keep local value
        
        self.sync_count += 1
        self.last_sync_time = datetime.now(timezone.utc)
        
        logger.info(
            "Sync completed: node=%s, updated=%d, conflicts=%d",
            self.node_id, len(updated_keys), self.conflict_count
        )
        
        return updated_keys
    
    def _resolve_conflict(self, local: StateValue, remote: StateValue) -> StateValue:
        """
        Resolve conflict between concurrent updates.
        
        Args:
            local: Local state value
            remote: Remote state value
            
        Returns:
            Winning state value
        """
        if self.conflict_strategy == ConflictResolutionStrategy.LWW_VECTOR_CLOCK:
            # Use node_id as tiebreaker if clocks are truly concurrent
            # Choose node with lexicographically larger ID
            if local.node_id > remote.node_id:
                return local
            else:
                return remote
        
        elif self.conflict_strategy == ConflictResolutionStrategy.LWW_TIMESTAMP:
            # Use wall-clock timestamp
            if local.timestamp >= remote.timestamp:
                return local
            else:
                return remote
        
        elif self.conflict_strategy == ConflictResolutionStrategy.MAX_VALUE:
            # Choose maximum value
            try:
                if local.value >= remote.value:
                    return local
                else:
                    return remote
            except (TypeError, AttributeError):
                # Fall back to LWW if values not comparable
                return local if local.timestamp >= remote.timestamp else remote
        
        elif self.conflict_strategy == ConflictResolutionStrategy.MIN_VALUE:
            # Choose minimum value
            try:
                if local.value <= remote.value:
                    return local
                else:
                    return remote
            except (TypeError, AttributeError):
                return local if local.timestamp >= remote.timestamp else remote
        
        # Default: keep local
        return local
    
    def verify_happens_before(self, key1: str, key2: str) -> Optional[bool]:
        """
        Verify happens-before relationship between two state updates.
        
        Args:
            key1: First state key
            key2: Second state key
            
        Returns:
            True if key1 -> key2 (key1 happens before key2)
            False if key2 -> key1
            None if concurrent or keys don't exist
        """
        if key1 not in self.state or key2 not in self.state:
            return None
        
        value1 = self.state[key1]
        value2 = self.state[key2]
        
        if value1.vector_clock.happens_before(value2.vector_clock):
            return True
        elif value2.vector_clock.happens_before(value1.vector_clock):
            return False
        else:
            return None  # Concurrent
    
    def verify_causal_consistency(self) -> Tuple[bool, List[str]]:
        """
        Verify causal consistency of entire state.
        
        Checks:
        1. Hash chain integrity
        2. Vector clock monotonicity
        3. No causality violations
        
        Returns:
            (is_consistent, list of violation descriptions)
        """
        violations = []
        
        # Check each key's history
        for key, history in self.history.items():
            if not history:
                continue
            
            # Verify hash chain
            for i in range(1, len(history)):
                prev = history[i - 1]
                curr = history[i]
                
                expected_prev_hash = prev.compute_hash()
                if curr.prev_hash != expected_prev_hash:
                    violations.append(
                        f"Hash chain broken for key={key}, version={curr.version}"
                    )
                
                # Verify vector clock monotonicity
                if not prev.vector_clock.happens_before(curr.vector_clock):
                    if not prev.vector_clock.equals(curr.vector_clock):
                        violations.append(
                            f"Vector clock not monotonic for key={key}, "
                            f"version {prev.version} -> {curr.version}"
                        )
        
        is_consistent = len(violations) == 0
        
        logger.info(
            "Causal consistency check: node=%s, consistent=%s, violations=%d",
            self.node_id, is_consistent, len(violations)
        )
        
        return is_consistent, violations
    
    def create_sync_message(self, message_type: str = "state_update") -> SyncMessage:
        """
        Create synchronization message for sending to peers.
        
        Args:
            message_type: Type of sync message
            
        Returns:
            SyncMessage containing current state
        """
        return SyncMessage(
            message_id=str(uuid.uuid4()),
            sender_node_id=self.node_id,
            message_type=message_type,
            vector_clock=self.vector_clock.copy(),
            state_values=list(self.state.values()),
            timestamp=datetime.now(timezone.utc),
        )
    
    def process_sync_message(self, message: SyncMessage) -> List[str]:
        """
        Process incoming synchronization message.
        
        Args:
            message: Sync message from peer
            
        Returns:
            List of keys updated
        """
        # Update known peers
        self.peer_nodes.add(message.sender_node_id)
        self.peer_clocks[message.sender_node_id] = message.vector_clock
        
        # Convert state values to dict
        peer_state = {sv.key: sv for sv in message.state_values}
        
        # Sync with peer state
        return self.sync_with_peer(peer_state, message.vector_clock)
    
    def _create_checkpoint(self):
        """Create Merkle tree checkpoint of current state."""
        # Collect all current state hashes
        state_hashes = []
        for key in sorted(self.state.keys()):
            state_value = self.state[key]
            state_hashes.append(state_value.compute_hash())
        
        if not state_hashes:
            return
        
        # Build Merkle tree
        merkle_tree = MerkleTree(state_hashes)
        merkle_root = merkle_tree.root
        
        # Update merkle_root in all current state values
        for state_value in self.state.values():
            state_value.merkle_root = merkle_root
        
        # Store checkpoint
        self.checkpoints.append((self.operation_count, merkle_root))
        self.last_checkpoint_seq = self.operation_count
        
        # Log to audit ledger
        self.audit_ledger.append(
            event_type=AuditEventType.CONFIGURATION_CHANGE,
            actor=self.node_id,
            action="checkpoint_created",
            resource="state_register",
            metadata={
                "operation_count": self.operation_count,
                "merkle_root": merkle_root,
                "state_size": len(self.state),
                "checkpoint_number": len(self.checkpoints),
            }
        )
        
        logger.info(
            "Checkpoint created: node=%s, seq=%d, root=%s, keys=%d",
            self.node_id, self.operation_count, merkle_root[:16], len(self.state)
        )
    
    def _audit_state_change(self, action: str, key: str, state_value: StateValue):
        """Log state change to audit ledger."""
        self.audit_ledger.append(
            event_type=AuditEventType.CONFIGURATION_CHANGE,
            actor=self.node_id,
            action=action,
            resource=f"state:{key}",
            metadata={
                "key": key,
                "version": state_value.version,
                "value_type": state_value.value_type.value,
                "vector_clock": state_value.vector_clock.to_dict(),
                "timestamp": state_value.timestamp.isoformat(),
                "prev_hash": state_value.prev_hash,
                "current_hash": state_value.compute_hash(),
                "merkle_root": state_value.merkle_root,
            }
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the state register."""
        return {
            "node_id": self.node_id,
            "state_size": len(self.state),
            "total_history": sum(len(h) for h in self.history.values()),
            "operation_count": self.operation_count,
            "sync_count": self.sync_count,
            "conflict_count": self.conflict_count,
            "peer_count": len(self.peer_nodes),
            "checkpoint_count": len(self.checkpoints),
            "last_checkpoint_seq": self.last_checkpoint_seq,
            "vector_clock": self.vector_clock.to_dict(),
            "last_sync_time": self.last_sync_time.isoformat(),
        }
    
    def _save_state(self):
        """Persist state to disk."""
        state_data = {
            "node_id": self.node_id,
            "vector_clock": self.vector_clock.to_dict(),
            "state": {k: v.to_dict() for k, v in self.state.items()},
            "history": {
                k: [v.to_dict() for v in versions]
                for k, versions in self.history.items()
            },
            "peer_nodes": list(self.peer_nodes),
            "peer_clocks": {k: v.to_dict() for k, v in self.peer_clocks.items()},
            "operation_count": self.operation_count,
            "checkpoints": self.checkpoints,
            "sync_count": self.sync_count,
            "conflict_count": self.conflict_count,
        }
        
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(state_data, f, indent=2)
        
        logger.debug("State saved: node=%s, path=%s", self.node_id, self.storage_path)
    
    def _load_state(self):
        """Load persisted state from disk."""
        if not self.storage_path.exists():
            logger.debug("No persisted state found: node=%s", self.node_id)
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                state_data = json.load(f)
            
            self.vector_clock = VectorClock.from_dict(state_data["vector_clock"])
            self.state = {
                k: StateValue.from_dict(v)
                for k, v in state_data["state"].items()
            }
            self.history = defaultdict(list)
            for k, versions in state_data["history"].items():
                self.history[k] = [StateValue.from_dict(v) for v in versions]
            
            self.peer_nodes = set(state_data.get("peer_nodes", []))
            self.peer_clocks = {
                k: VectorClock.from_dict(v)
                for k, v in state_data.get("peer_clocks", {}).items()
            }
            
            self.operation_count = state_data.get("operation_count", 0)
            self.checkpoints = state_data.get("checkpoints", [])
            self.sync_count = state_data.get("sync_count", 0)
            self.conflict_count = state_data.get("conflict_count", 0)
            
            logger.info(
                "State loaded: node=%s, keys=%d, operations=%d",
                self.node_id, len(self.state), self.operation_count
            )
        except Exception as e:
            logger.error("Failed to load state: %s", e, exc_info=True)
    
    def save(self):
        """Explicitly save state to disk."""
        self._save_state()
    
    def __del__(self):
        """Save state on cleanup."""
        try:
            self._save_state()
        except Exception:
            pass


class DistributedStateRegisterCluster:
    """
    Manages a cluster of distributed state registers.
    
    Provides:
    - Automatic peer discovery
    - Periodic gossip synchronization
    - Cluster-wide consistency verification
    - Aggregate statistics
    """
    
    def __init__(self, audit_ledger: TemporalAuditLedger):
        """
        Initialize cluster manager.
        
        Args:
            audit_ledger: Shared audit ledger
        """
        self.audit_ledger = audit_ledger
        self.nodes: Dict[str, DistributedStateRegister] = {}
    
    def add_node(self, node: DistributedStateRegister):
        """Add node to cluster."""
        self.nodes[node.node_id] = node
        
        # Make all existing nodes aware of each other
        for existing_node_id in self.nodes:
            if existing_node_id != node.node_id:
                node.peer_nodes.add(existing_node_id)
                self.nodes[existing_node_id].peer_nodes.add(node.node_id)
    
    def gossip_round(self) -> Dict[str, List[str]]:
        """
        Perform one round of gossip synchronization.
        
        Each node syncs with all peers.
        
        Returns:
            Dict mapping node_id to list of updated keys
        """
        updates = {}
        
        for node_id, node in self.nodes.items():
            node_updates = []
            
            # Sync with each peer
            for peer_id in node.peer_nodes:
                if peer_id in self.nodes:
                    peer = self.nodes[peer_id]
                    
                    # Create sync message from peer
                    sync_msg = peer.create_sync_message()
                    
                    # Process sync message
                    updated = node.process_sync_message(sync_msg)
                    node_updates.extend(updated)
            
            updates[node_id] = list(set(node_updates))
        
        return updates
    
    def verify_cluster_consistency(self) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Verify consistency across all nodes.
        
        Returns:
            (all_consistent, violations per node)
        """
        all_consistent = True
        violations_by_node = {}
        
        for node_id, node in self.nodes.items():
            is_consistent, violations = node.verify_causal_consistency()
            if not is_consistent:
                all_consistent = False
                violations_by_node[node_id] = violations
        
        return all_consistent, violations_by_node
    
    def get_cluster_statistics(self) -> Dict[str, Any]:
        """Get aggregate cluster statistics."""
        return {
            "cluster_size": len(self.nodes),
            "nodes": {
                node_id: node.get_statistics()
                for node_id, node in self.nodes.items()
            },
            "total_operations": sum(n.operation_count for n in self.nodes.values()),
            "total_syncs": sum(n.sync_count for n in self.nodes.values()),
            "total_conflicts": sum(n.conflict_count for n in self.nodes.values()),
        }
