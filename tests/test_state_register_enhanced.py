"""
Tests for Enhanced STATE_REGISTER with Distributed Synchronization

Test Coverage:
- Basic state operations (put, get, delete)
- Vector clock integration and causality tracking
- Distributed synchronization and gossip protocol
- Conflict resolution strategies
- Causal consistency verification
- Merkle tree anchoring
- Audit trail integration
- Multi-node scenarios
"""

import json
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from state_register_enhanced import (
    DistributedStateRegister,
    DistributedStateRegisterCluster,
    StateValue,
    StateValueType,
    ConflictResolutionStrategy,
    SyncMessage,
)
from temporal_audit_ledger import TemporalAuditLedger
from cognition.temporal.vector_clock import VectorClock


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def audit_ledger(temp_dir):
    """Create audit ledger for testing."""
    ledger_path = temp_dir / "audit.json"
    return TemporalAuditLedger(ledger_path)


@pytest.fixture
def state_register(temp_dir, audit_ledger):
    """Create single state register instance."""
    storage_path = temp_dir / "state_node1.json"
    return DistributedStateRegister(
        node_id="node1",
        storage_path=storage_path,
        audit_ledger=audit_ledger,
        checkpoint_interval=5,
    )


class TestBasicStateOperations:
    """Test basic state operations."""
    
    def test_put_and_get(self, state_register):
        """Test storing and retrieving state."""
        # Put a value
        state_value = state_register.put(
            key="config.timeout",
            value=30,
            value_type=StateValueType.INTEGER,
        )
        
        assert state_value.key == "config.timeout"
        assert state_value.value == 30
        assert state_value.version == 1
        assert state_value.node_id == "node1"
        
        # Get the value
        retrieved = state_register.get("config.timeout")
        assert retrieved is not None
        assert retrieved.value == 30
        assert retrieved.version == 1
    
    def test_put_updates_version(self, state_register):
        """Test that updates increment version."""
        state_register.put("key1", "value1", StateValueType.STRING)
        state_register.put("key1", "value2", StateValueType.STRING)
        state_register.put("key1", "value3", StateValueType.STRING)
        
        current = state_register.get("key1")
        assert current.value == "value3"
        assert current.version == 3
    
    def test_put_creates_hash_chain(self, state_register):
        """Test that updates create valid hash chain."""
        v1 = state_register.put("key1", "value1", StateValueType.STRING)
        v2 = state_register.put("key1", "value2", StateValueType.STRING)
        v3 = state_register.put("key1", "value3", StateValueType.STRING)
        
        # Verify hash chain
        assert v1.prev_hash == ""
        assert v2.prev_hash == v1.compute_hash()
        assert v3.prev_hash == v2.compute_hash()
    
    def test_delete_creates_tombstone(self, state_register):
        """Test that delete creates tombstone."""
        state_register.put("key1", "value1", StateValueType.STRING)
        
        result = state_register.delete("key1")
        assert result is True
        
        current = state_register.get("key1")
        assert current is not None
        assert current.value is None
        assert current.metadata.get("tombstone") is True
    
    def test_get_version(self, state_register):
        """Test retrieving specific version."""
        state_register.put("key1", "value1", StateValueType.STRING)
        state_register.put("key1", "value2", StateValueType.STRING)
        state_register.put("key1", "value3", StateValueType.STRING)
        
        v1 = state_register.get_version("key1", 1)
        v2 = state_register.get_version("key1", 2)
        v3 = state_register.get_version("key1", 3)
        
        assert v1.value == "value1"
        assert v2.value == "value2"
        assert v3.value == "value3"
    
    def test_different_value_types(self, state_register):
        """Test storing different value types."""
        # String
        state_register.put("str_key", "hello", StateValueType.STRING)
        assert state_register.get("str_key").value == "hello"
        
        # Integer
        state_register.put("int_key", 42, StateValueType.INTEGER)
        assert state_register.get("int_key").value == 42
        
        # Float
        state_register.put("float_key", 3.14, StateValueType.FLOAT)
        assert state_register.get("float_key").value == 3.14
        
        # Boolean
        state_register.put("bool_key", True, StateValueType.BOOLEAN)
        assert state_register.get("bool_key").value is True
        
        # JSON
        json_value = {"nested": {"data": [1, 2, 3]}}
        state_register.put("json_key", json_value, StateValueType.JSON)
        retrieved = state_register.get("json_key")
        assert retrieved.value == json_value
        
        # Binary
        binary_value = b"binary data"
        state_register.put("bin_key", binary_value, StateValueType.BINARY)
        assert state_register.get("bin_key").value == binary_value


class TestVectorClockIntegration:
    """Test vector clock integration."""
    
    def test_vector_clock_increments(self, state_register):
        """Test that vector clock increments with operations."""
        initial_time = state_register.vector_clock.clock[state_register.node_id]
        
        state_register.put("key1", "value1", StateValueType.STRING)
        time1 = state_register.vector_clock.clock[state_register.node_id]
        assert time1 == initial_time + 1
        
        state_register.put("key2", "value2", StateValueType.STRING)
        time2 = state_register.vector_clock.clock[state_register.node_id]
        assert time2 == initial_time + 2
    
    def test_state_values_capture_vector_clock(self, state_register):
        """Test that state values capture vector clock snapshots."""
        v1 = state_register.put("key1", "value1", StateValueType.STRING)
        v2 = state_register.put("key2", "value2", StateValueType.STRING)
        
        # Each should have different vector clock values
        clock1 = v1.vector_clock.clock[state_register.node_id]
        clock2 = v2.vector_clock.clock[state_register.node_id]
        
        assert clock2 > clock1
    
    def test_happens_before_verification(self, state_register):
        """Test happens-before relationship verification."""
        state_register.put("key1", "value1", StateValueType.STRING)
        time.sleep(0.01)  # Small delay
        state_register.put("key2", "value2", StateValueType.STRING)
        
        # key1 should happen before key2
        result = state_register.verify_happens_before("key1", "key2")
        assert result is True
        
        # key2 should not happen before key1
        result = state_register.verify_happens_before("key2", "key1")
        assert result is False


class TestDistributedSynchronization:
    """Test distributed synchronization."""
    
    def test_two_node_sync(self, temp_dir, audit_ledger):
        """Test synchronization between two nodes."""
        # Create two nodes
        node1 = DistributedStateRegister(
            node_id="node1",
            storage_path=temp_dir / "state_node1.json",
            audit_ledger=audit_ledger,
        )
        node2 = DistributedStateRegister(
            node_id="node2",
            storage_path=temp_dir / "state_node2.json",
            audit_ledger=audit_ledger,
        )
        
        # Node1 writes some data
        node1.put("shared_key", "value_from_node1", StateValueType.STRING)
        
        # Create sync message from node1
        sync_msg = node1.create_sync_message()
        
        # Node2 processes sync message
        updated = node2.process_sync_message(sync_msg)
        
        # Node2 should now have the data
        assert "shared_key" in updated
        retrieved = node2.get("shared_key")
        assert retrieved is not None
        assert retrieved.value == "value_from_node1"
    
    def test_bidirectional_sync(self, temp_dir, audit_ledger):
        """Test bidirectional synchronization."""
        node1 = DistributedStateRegister(
            node_id="node1",
            storage_path=temp_dir / "state_node1.json",
            audit_ledger=audit_ledger,
        )
        node2 = DistributedStateRegister(
            node_id="node2",
            storage_path=temp_dir / "state_node2.json",
            audit_ledger=audit_ledger,
        )
        
        # Node1 writes key1
        node1.put("key1", "from_node1", StateValueType.STRING)
        
        # Node2 writes key2
        node2.put("key2", "from_node2", StateValueType.STRING)
        
        # Sync node1 -> node2
        msg1 = node1.create_sync_message()
        node2.process_sync_message(msg1)
        
        # Sync node2 -> node1
        msg2 = node2.create_sync_message()
        node1.process_sync_message(msg2)
        
        # Both nodes should have both keys
        assert node1.get("key1").value == "from_node1"
        assert node1.get("key2").value == "from_node2"
        assert node2.get("key1").value == "from_node1"
        assert node2.get("key2").value == "from_node2"
    
    def test_sync_message_serialization(self, state_register):
        """Test sync message serialization."""
        state_register.put("key1", "value1", StateValueType.STRING)
        
        # Create sync message
        msg = state_register.create_sync_message()
        
        # Serialize to dict
        msg_dict = msg.to_dict()
        assert msg_dict["sender_node_id"] == "node1"
        assert len(msg_dict["state_values"]) == 1
        
        # Deserialize
        msg_restored = SyncMessage.from_dict(msg_dict)
        assert msg_restored.sender_node_id == msg.sender_node_id
        assert len(msg_restored.state_values) == len(msg.state_values)


class TestConflictResolution:
    """Test conflict resolution strategies."""
    
    def test_lww_vector_clock_resolution(self, temp_dir, audit_ledger):
        """Test LWW conflict resolution using vector clocks."""
        node1 = DistributedStateRegister(
            node_id="node1",
            storage_path=temp_dir / "state_node1.json",
            audit_ledger=audit_ledger,
            conflict_strategy=ConflictResolutionStrategy.LWW_VECTOR_CLOCK,
        )
        node2 = DistributedStateRegister(
            node_id="node2",
            storage_path=temp_dir / "state_node2.json",
            audit_ledger=audit_ledger,
            conflict_strategy=ConflictResolutionStrategy.LWW_VECTOR_CLOCK,
        )
        
        # Create concurrent updates
        node1.put("conflict_key", "value_from_node1", StateValueType.STRING)
        node2.put("conflict_key", "value_from_node2", StateValueType.STRING)
        
        # Sync - node2 should win (lexicographically larger node_id)
        msg2 = node2.create_sync_message()
        updated = node1.process_sync_message(msg2)
        
        assert "conflict_key" in updated
        assert node1.get("conflict_key").value == "value_from_node2"
        assert node1.conflict_count == 1
    
    def test_lww_timestamp_resolution(self, temp_dir, audit_ledger):
        """Test LWW conflict resolution using timestamps."""
        node1 = DistributedStateRegister(
            node_id="node1",
            storage_path=temp_dir / "state_node1.json",
            audit_ledger=audit_ledger,
            conflict_strategy=ConflictResolutionStrategy.LWW_TIMESTAMP,
        )
        node2 = DistributedStateRegister(
            node_id="node2",
            storage_path=temp_dir / "state_node2.json",
            audit_ledger=audit_ledger,
            conflict_strategy=ConflictResolutionStrategy.LWW_TIMESTAMP,
        )
        
        # Node1 writes first
        node1.put("conflict_key", "first_write", StateValueType.STRING)
        time.sleep(0.01)  # Ensure different timestamps
        
        # Node2 writes second (later)
        node2.put("conflict_key", "second_write", StateValueType.STRING)
        
        # Sync - node2 should win (later timestamp)
        msg2 = node2.create_sync_message()
        node1.process_sync_message(msg2)
        
        assert node1.get("conflict_key").value == "second_write"
    
    def test_max_value_resolution(self, temp_dir, audit_ledger):
        """Test MAX_VALUE conflict resolution."""
        node1 = DistributedStateRegister(
            node_id="node1",
            storage_path=temp_dir / "state_node1.json",
            audit_ledger=audit_ledger,
            conflict_strategy=ConflictResolutionStrategy.MAX_VALUE,
        )
        node2 = DistributedStateRegister(
            node_id="node2",
            storage_path=temp_dir / "state_node2.json",
            audit_ledger=audit_ledger,
            conflict_strategy=ConflictResolutionStrategy.MAX_VALUE,
        )
        
        # Create concurrent updates with different values
        node1.put("number", 100, StateValueType.INTEGER)
        node2.put("number", 200, StateValueType.INTEGER)
        
        # Sync - should choose max value (200)
        msg2 = node2.create_sync_message()
        node1.process_sync_message(msg2)
        
        assert node1.get("number").value == 200
    
    def test_min_value_resolution(self, temp_dir, audit_ledger):
        """Test MIN_VALUE conflict resolution."""
        node1 = DistributedStateRegister(
            node_id="node1",
            storage_path=temp_dir / "state_node1.json",
            audit_ledger=audit_ledger,
            conflict_strategy=ConflictResolutionStrategy.MIN_VALUE,
        )
        node2 = DistributedStateRegister(
            node_id="node2",
            storage_path=temp_dir / "state_node2.json",
            audit_ledger=audit_ledger,
            conflict_strategy=ConflictResolutionStrategy.MIN_VALUE,
        )
        
        # Create concurrent updates with different values
        node1.put("number", 100, StateValueType.INTEGER)
        node2.put("number", 50, StateValueType.INTEGER)
        
        # Sync - should choose min value (50)
        msg2 = node2.create_sync_message()
        node1.process_sync_message(msg2)
        
        assert node1.get("number").value == 50


class TestCausalConsistency:
    """Test causal consistency verification."""
    
    def test_consistency_verification_passes(self, state_register):
        """Test that valid state passes consistency check."""
        state_register.put("key1", "value1", StateValueType.STRING)
        state_register.put("key2", "value2", StateValueType.STRING)
        state_register.put("key1", "value1_updated", StateValueType.STRING)
        
        is_consistent, violations = state_register.verify_causal_consistency()
        assert is_consistent is True
        assert len(violations) == 0
    
    def test_hash_chain_integrity(self, state_register):
        """Test that hash chain is verified."""
        # Create valid state
        v1 = state_register.put("key1", "value1", StateValueType.STRING)
        v2 = state_register.put("key1", "value2", StateValueType.STRING)
        
        # Manually break hash chain
        v2.prev_hash = "invalid_hash"
        
        is_consistent, violations = state_register.verify_causal_consistency()
        assert is_consistent is False
        assert len(violations) > 0
        assert "Hash chain broken" in violations[0]


class TestMerkleTreeAnchoring:
    """Test Merkle tree anchoring."""
    
    def test_checkpoint_creation(self, state_register):
        """Test that checkpoints are created at interval."""
        # Checkpoint interval is 5
        for i in range(6):
            state_register.put(f"key{i}", f"value{i}", StateValueType.STRING)
        
        # Should have created at least one checkpoint
        assert len(state_register.checkpoints) >= 1
        
        # All state values should have merkle_root
        for state_value in state_register.state.values():
            if state_value.metadata.get("tombstone"):
                continue
            # Last checkpoint should have set merkle_root
            if state_register.checkpoints:
                # At least some should have merkle roots
                pass
    
    def test_checkpoint_logged_to_audit(self, state_register, audit_ledger):
        """Test that checkpoints are logged to audit ledger."""
        initial_entries = len(audit_ledger.entries)
        
        # Trigger checkpoint
        for i in range(5):
            state_register.put(f"key{i}", f"value{i}", StateValueType.STRING)
        
        # Check audit log has checkpoint entry
        checkpoint_entries = [
            e for e in audit_ledger.entries
            if e.action == "checkpoint_created"
        ]
        assert len(checkpoint_entries) >= 1


class TestAuditTrailIntegration:
    """Test audit trail integration."""
    
    def test_state_changes_logged(self, state_register, audit_ledger):
        """Test that state changes are logged to audit."""
        initial_count = len(audit_ledger.entries)
        
        state_register.put("key1", "value1", StateValueType.STRING)
        
        # Should have logged the put operation
        assert len(audit_ledger.entries) > initial_count
        
        # Find the entry
        put_entries = [
            e for e in audit_ledger.entries
            if e.action == "put" and e.resource == "state:key1"
        ]
        assert len(put_entries) >= 1
    
    def test_sync_operations_logged(self, temp_dir, audit_ledger):
        """Test that sync operations are logged."""
        node1 = DistributedStateRegister(
            node_id="node1",
            storage_path=temp_dir / "state_node1.json",
            audit_ledger=audit_ledger,
        )
        node2 = DistributedStateRegister(
            node_id="node2",
            storage_path=temp_dir / "state_node2.json",
            audit_ledger=audit_ledger,
        )
        
        # Node1 writes
        node1.put("shared_key", "value", StateValueType.STRING)
        
        initial_count = len(audit_ledger.entries)
        
        # Sync to node2
        msg = node1.create_sync_message()
        node2.process_sync_message(msg)
        
        # Should have logged sync operation
        sync_entries = [
            e for e in audit_ledger.entries[initial_count:]
            if "sync" in e.action
        ]
        assert len(sync_entries) > 0


class TestPersistence:
    """Test state persistence."""
    
    def test_state_persists_across_restarts(self, temp_dir, audit_ledger):
        """Test that state is saved and loaded correctly."""
        storage_path = temp_dir / "state_persist.json"
        
        # Create node and write data
        node1 = DistributedStateRegister(
            node_id="node1",
            storage_path=storage_path,
            audit_ledger=audit_ledger,
        )
        node1.put("persist_key", "persist_value", StateValueType.STRING)
        node1.save()
        
        # Create new instance with same storage
        node2 = DistributedStateRegister(
            node_id="node1",
            storage_path=storage_path,
            audit_ledger=audit_ledger,
        )
        
        # Should have loaded the data
        retrieved = node2.get("persist_key")
        assert retrieved is not None
        assert retrieved.value == "persist_value"
    
    def test_vector_clock_persists(self, temp_dir, audit_ledger):
        """Test that vector clock state persists."""
        storage_path = temp_dir / "state_clock.json"
        
        node1 = DistributedStateRegister(
            node_id="node1",
            storage_path=storage_path,
            audit_ledger=audit_ledger,
        )
        
        # Perform operations to advance clock
        for i in range(5):
            node1.put(f"key{i}", f"value{i}", StateValueType.STRING)
        
        clock_value = node1.vector_clock.clock["node1"]
        node1.save()
        
        # Reload
        node2 = DistributedStateRegister(
            node_id="node1",
            storage_path=storage_path,
            audit_ledger=audit_ledger,
        )
        
        # Clock should be restored
        assert node2.vector_clock.clock["node1"] == clock_value


class TestClusterManagement:
    """Test cluster management."""
    
    def test_cluster_creation(self, temp_dir, audit_ledger):
        """Test creating a cluster."""
        cluster = DistributedStateRegisterCluster(audit_ledger)
        
        node1 = DistributedStateRegister(
            node_id="node1",
            storage_path=temp_dir / "state_node1.json",
            audit_ledger=audit_ledger,
        )
        node2 = DistributedStateRegister(
            node_id="node2",
            storage_path=temp_dir / "state_node2.json",
            audit_ledger=audit_ledger,
        )
        
        cluster.add_node(node1)
        cluster.add_node(node2)
        
        assert len(cluster.nodes) == 2
        assert "node1" in node2.peer_nodes
        assert "node2" in node1.peer_nodes
    
    def test_gossip_round(self, temp_dir, audit_ledger):
        """Test gossip synchronization round."""
        cluster = DistributedStateRegisterCluster(audit_ledger)
        
        node1 = DistributedStateRegister(
            node_id="node1",
            storage_path=temp_dir / "state_node1.json",
            audit_ledger=audit_ledger,
        )
        node2 = DistributedStateRegister(
            node_id="node2",
            storage_path=temp_dir / "state_node2.json",
            audit_ledger=audit_ledger,
        )
        node3 = DistributedStateRegister(
            node_id="node3",
            storage_path=temp_dir / "state_node3.json",
            audit_ledger=audit_ledger,
        )
        
        cluster.add_node(node1)
        cluster.add_node(node2)
        cluster.add_node(node3)
        
        # Each node writes unique data
        node1.put("key1", "from_node1", StateValueType.STRING)
        node2.put("key2", "from_node2", StateValueType.STRING)
        node3.put("key3", "from_node3", StateValueType.STRING)
        
        # Perform gossip round
        updates = cluster.gossip_round()
        
        # All nodes should have all keys
        assert node1.get("key1") is not None
        assert node1.get("key2") is not None
        assert node1.get("key3") is not None
        
        assert node2.get("key1") is not None
        assert node2.get("key2") is not None
        assert node2.get("key3") is not None
        
        assert node3.get("key1") is not None
        assert node3.get("key2") is not None
        assert node3.get("key3") is not None
    
    def test_cluster_consistency_verification(self, temp_dir, audit_ledger):
        """Test cluster-wide consistency verification."""
        cluster = DistributedStateRegisterCluster(audit_ledger)
        
        node1 = DistributedStateRegister(
            node_id="node1",
            storage_path=temp_dir / "state_node1.json",
            audit_ledger=audit_ledger,
        )
        node2 = DistributedStateRegister(
            node_id="node2",
            storage_path=temp_dir / "state_node2.json",
            audit_ledger=audit_ledger,
        )
        
        cluster.add_node(node1)
        cluster.add_node(node2)
        
        # Write valid data
        node1.put("key1", "value1", StateValueType.STRING)
        
        is_consistent, violations = cluster.verify_cluster_consistency()
        assert is_consistent is True
        assert len(violations) == 0
    
    def test_cluster_statistics(self, temp_dir, audit_ledger):
        """Test cluster statistics."""
        cluster = DistributedStateRegisterCluster(audit_ledger)
        
        node1 = DistributedStateRegister(
            node_id="node1",
            storage_path=temp_dir / "state_node1.json",
            audit_ledger=audit_ledger,
        )
        
        cluster.add_node(node1)
        node1.put("key1", "value1", StateValueType.STRING)
        
        stats = cluster.get_cluster_statistics()
        
        assert stats["cluster_size"] == 1
        assert "nodes" in stats
        assert "node1" in stats["nodes"]
        assert stats["total_operations"] >= 1


class TestComplexScenarios:
    """Test complex multi-node scenarios."""
    
    def test_multi_node_convergence(self, temp_dir, audit_ledger):
        """Test that multiple nodes converge to same state."""
        cluster = DistributedStateRegisterCluster(audit_ledger)
        
        # Create 5 nodes
        nodes = []
        for i in range(5):
            node = DistributedStateRegister(
                node_id=f"node{i}",
                storage_path=temp_dir / f"state_node{i}.json",
                audit_ledger=audit_ledger,
            )
            cluster.add_node(node)
            nodes.append(node)
        
        # Each node writes some unique data
        for i, node in enumerate(nodes):
            node.put(f"key_from_node{i}", f"value{i}", StateValueType.STRING)
        
        # Perform multiple gossip rounds
        for _ in range(3):
            cluster.gossip_round()
        
        # All nodes should have all keys
        expected_keys = {f"key_from_node{i}" for i in range(5)}
        
        for node in nodes:
            actual_keys = set(node.state.keys())
            assert expected_keys.issubset(actual_keys)
    
    def test_partition_and_merge(self, temp_dir, audit_ledger):
        """Test partition healing scenario."""
        # Create two partitions
        partition1 = [
            DistributedStateRegister(
                node_id="node1",
                storage_path=temp_dir / "state_node1.json",
                audit_ledger=audit_ledger,
            ),
            DistributedStateRegister(
                node_id="node2",
                storage_path=temp_dir / "state_node2.json",
                audit_ledger=audit_ledger,
            ),
        ]
        
        partition2 = [
            DistributedStateRegister(
                node_id="node3",
                storage_path=temp_dir / "state_node3.json",
                audit_ledger=audit_ledger,
            ),
        ]
        
        # Each partition operates independently
        partition1[0].put("key1", "from_partition1", StateValueType.STRING)
        partition2[0].put("key2", "from_partition2", StateValueType.STRING)
        
        # Sync within partition1
        msg = partition1[0].create_sync_message()
        partition1[1].process_sync_message(msg)
        
        # Now merge partitions
        msg1 = partition1[0].create_sync_message()
        msg2 = partition2[0].create_sync_message()
        
        partition2[0].process_sync_message(msg1)
        partition1[0].process_sync_message(msg2)
        
        # All nodes should converge
        assert partition1[0].get("key2") is not None
        assert partition2[0].get("key1") is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
