"""
Enhanced STATE_REGISTER Demonstration

This demo showcases the distributed state register capabilities:
1. Multi-node state synchronization
2. Vector clock causal tracking
3. Conflict resolution
4. Audit trail anchoring
5. Consistency verification
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

# Add paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "governance"))

from state_register_enhanced import (
    DistributedStateRegister,
    DistributedStateRegisterCluster,
    StateValueType,
    ConflictResolutionStrategy,
)
from temporal_audit_ledger import TemporalAuditLedger


def demo_basic_operations():
    """Demonstrate basic state operations."""
    print("=" * 70)
    print("DEMO 1: Basic State Operations")
    print("=" * 70)
    
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create audit ledger
        audit_ledger = TemporalAuditLedger(tmpdir / "audit.json")
        
        # Create state register
        state_register = DistributedStateRegister(
            node_id="demo_node",
            storage_path=tmpdir / "state.json",
            audit_ledger=audit_ledger,
            checkpoint_interval=3,
        )
        
        # Store different types of values
        print("\n1. Storing various value types...")
        state_register.put("config.timeout", 30, StateValueType.INTEGER)
        state_register.put("config.enabled", True, StateValueType.BOOLEAN)
        state_register.put("config.api_url", "https://api.example.com", StateValueType.STRING)
        state_register.put("config.metadata", {"version": "1.0", "env": "prod"}, StateValueType.JSON)
        
        # Retrieve values
        print("\n2. Retrieving values...")
        timeout = state_register.get("config.timeout")
        print(f"   Timeout: {timeout.value} (version {timeout.version})")
        print(f"   Vector clock: {timeout.vector_clock}")
        
        # Update value
        print("\n3. Updating value (creates new version)...")
        state_register.put("config.timeout", 60, StateValueType.INTEGER)
        updated = state_register.get("config.timeout")
        print(f"   New timeout: {updated.value} (version {updated.version})")
        
        # View history
        print("\n4. Version history...")
        v1 = state_register.get_version("config.timeout", 1)
        v2 = state_register.get_version("config.timeout", 2)
        print(f"   Version 1: {v1.value}")
        print(f"   Version 2: {v2.value}")
        print(f"   Hash chain: v1={v1.compute_hash()[:16]}... -> v2 (prev={v2.prev_hash[:16]}...)")
        
        # Statistics
        print("\n5. Statistics...")
        stats = state_register.get_statistics()
        print(f"   Total operations: {stats['operation_count']}")
        print(f"   State size: {stats['state_size']} keys")
        print(f"   Checkpoints: {stats['checkpoint_count']}")


def demo_distributed_sync():
    """Demonstrate distributed synchronization."""
    print("\n" + "=" * 70)
    print("DEMO 2: Distributed Synchronization")
    print("=" * 70)
    
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create shared audit ledger
        audit_ledger = TemporalAuditLedger(tmpdir / "audit.json")
        
        # Create three nodes
        print("\n1. Creating 3-node cluster...")
        node1 = DistributedStateRegister(
            node_id="node1",
            storage_path=tmpdir / "state_node1.json",
            audit_ledger=audit_ledger,
        )
        node2 = DistributedStateRegister(
            node_id="node2",
            storage_path=tmpdir / "state_node2.json",
            audit_ledger=audit_ledger,
        )
        node3 = DistributedStateRegister(
            node_id="node3",
            storage_path=tmpdir / "state_node3.json",
            audit_ledger=audit_ledger,
        )
        
        # Each node writes unique data
        print("\n2. Each node writes unique data...")
        node1.put("database.host", "db1.example.com", StateValueType.STRING)
        print(f"   Node1: database.host = db1.example.com")
        
        node2.put("database.port", 5432, StateValueType.INTEGER)
        print(f"   Node2: database.port = 5432")
        
        node3.put("database.replicas", 3, StateValueType.INTEGER)
        print(f"   Node3: database.replicas = 3")
        
        # Sync node1 -> node2
        print("\n3. Syncing node1 -> node2...")
        msg1 = node1.create_sync_message()
        updated = node2.process_sync_message(msg1)
        print(f"   Node2 updated keys: {updated}")
        
        # Sync node2 -> node3
        print("\n4. Syncing node2 -> node3...")
        msg2 = node2.create_sync_message()
        updated = node3.process_sync_message(msg2)
        print(f"   Node3 updated keys: {updated}")
        
        # Sync node3 -> node1
        print("\n5. Syncing node3 -> node1...")
        msg3 = node3.create_sync_message()
        updated = node1.process_sync_message(msg3)
        print(f"   Node1 updated keys: {updated}")
        
        # Verify convergence
        print("\n6. Verifying convergence...")
        print(f"   Node1 has {len(node1.state)} keys: {set(node1.state.keys())}")
        print(f"   Node2 has {len(node2.state)} keys: {set(node2.state.keys())}")
        print(f"   Node3 has {len(node3.state)} keys: {set(node3.state.keys())}")


def demo_conflict_resolution():
    """Demonstrate conflict resolution."""
    print("\n" + "=" * 70)
    print("DEMO 3: Conflict Resolution")
    print("=" * 70)
    
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        audit_ledger = TemporalAuditLedger(tmpdir / "audit.json")
        
        # Create two nodes with LWW strategy
        print("\n1. Creating nodes with LWW-VectorClock conflict resolution...")
        node1 = DistributedStateRegister(
            node_id="node1",
            storage_path=tmpdir / "state_node1.json",
            audit_ledger=audit_ledger,
            conflict_strategy=ConflictResolutionStrategy.LWW_VECTOR_CLOCK,
        )
        node2 = DistributedStateRegister(
            node_id="node2",
            storage_path=tmpdir / "state_node2.json",
            audit_ledger=audit_ledger,
            conflict_strategy=ConflictResolutionStrategy.LWW_VECTOR_CLOCK,
        )
        
        # Create concurrent conflicting writes
        print("\n2. Creating concurrent conflicting writes...")
        node1.put("feature_flag.new_ui", False, StateValueType.BOOLEAN)
        node2.put("feature_flag.new_ui", True, StateValueType.BOOLEAN)
        
        print(f"   Node1 value: {node1.get('feature_flag.new_ui').value}")
        print(f"   Node2 value: {node2.get('feature_flag.new_ui').value}")
        
        # Sync and resolve conflict
        print("\n3. Syncing and resolving conflict...")
        msg2 = node2.create_sync_message()
        updated = node1.process_sync_message(msg2)
        
        print(f"   Conflict detected: {node1.conflict_count > 0}")
        print(f"   Resolution: node2 wins (lexicographically larger node_id)")
        print(f"   Node1 final value: {node1.get('feature_flag.new_ui').value}")
        
        # Try with MAX_VALUE strategy
        print("\n4. Testing MAX_VALUE resolution strategy...")
        node3 = DistributedStateRegister(
            node_id="node3",
            storage_path=tmpdir / "state_node3.json",
            audit_ledger=audit_ledger,
            conflict_strategy=ConflictResolutionStrategy.MAX_VALUE,
        )
        node4 = DistributedStateRegister(
            node_id="node4",
            storage_path=tmpdir / "state_node4.json",
            audit_ledger=audit_ledger,
            conflict_strategy=ConflictResolutionStrategy.MAX_VALUE,
        )
        
        node3.put("priority", 5, StateValueType.INTEGER)
        node4.put("priority", 10, StateValueType.INTEGER)
        
        msg4 = node4.create_sync_message()
        node3.process_sync_message(msg4)
        
        print(f"   Node3 had priority=5, Node4 had priority=10")
        print(f"   After sync, Node3 priority={node3.get('priority').value} (max wins)")


def demo_causal_consistency():
    """Demonstrate causal consistency verification."""
    print("\n" + "=" * 70)
    print("DEMO 4: Causal Consistency Verification")
    print("=" * 70)
    
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        audit_ledger = TemporalAuditLedger(tmpdir / "audit.json")
        
        state_register = DistributedStateRegister(
            node_id="demo_node",
            storage_path=tmpdir / "state.json",
            audit_ledger=audit_ledger,
        )
        
        # Create sequence of operations
        print("\n1. Creating sequence of causally ordered operations...")
        state_register.put("step1", "init", StateValueType.STRING)
        time.sleep(0.01)
        state_register.put("step2", "process", StateValueType.STRING)
        time.sleep(0.01)
        state_register.put("step3", "complete", StateValueType.STRING)
        
        # Verify happens-before relationships
        print("\n2. Verifying happens-before relationships...")
        hb_12 = state_register.verify_happens_before("step1", "step2")
        hb_23 = state_register.verify_happens_before("step2", "step3")
        hb_13 = state_register.verify_happens_before("step1", "step3")
        
        print(f"   step1 -> step2: {hb_12}")
        print(f"   step2 -> step3: {hb_23}")
        print(f"   step1 -> step3: {hb_13}")
        
        # Verify overall consistency
        print("\n3. Verifying overall causal consistency...")
        is_consistent, violations = state_register.verify_causal_consistency()
        print(f"   Is consistent: {is_consistent}")
        if violations:
            print(f"   Violations: {violations}")
        else:
            print("   No violations found [OK]")
        
        # Show vector clock progression
        print("\n4. Vector clock progression...")
        v1 = state_register.get("step1").vector_clock
        v2 = state_register.get("step2").vector_clock
        v3 = state_register.get("step3").vector_clock
        
        print(f"   step1 clock: {v1}")
        print(f"   step2 clock: {v2}")
        print(f"   step3 clock: {v3}")


def demo_cluster_gossip():
    """Demonstrate cluster with gossip protocol."""
    print("\n" + "=" * 70)
    print("DEMO 5: Cluster Gossip Protocol")
    print("=" * 70)
    
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        audit_ledger = TemporalAuditLedger(tmpdir / "audit.json")
        
        # Create cluster
        print("\n1. Creating 4-node cluster...")
        cluster = DistributedStateRegisterCluster(audit_ledger)
        
        for i in range(1, 5):
            node = DistributedStateRegister(
                node_id=f"node{i}",
                storage_path=tmpdir / f"state_node{i}.json",
                audit_ledger=audit_ledger,
            )
            cluster.add_node(node)
        
        print(f"   Cluster size: {len(cluster.nodes)} nodes")
        
        # Each node writes unique data
        print("\n2. Each node writes unique configuration...")
        cluster.nodes["node1"].put("service.node1.status", "active", StateValueType.STRING)
        cluster.nodes["node2"].put("service.node2.status", "active", StateValueType.STRING)
        cluster.nodes["node3"].put("service.node3.status", "standby", StateValueType.STRING)
        cluster.nodes["node4"].put("service.node4.status", "active", StateValueType.STRING)
        
        # Perform gossip rounds
        print("\n3. Performing gossip synchronization...")
        for round_num in range(1, 4):
            print(f"\n   Round {round_num}:")
            updates = cluster.gossip_round()
            for node_id, updated_keys in updates.items():
                if updated_keys:
                    print(f"      {node_id}: received {len(updated_keys)} updates")
        
        # Verify convergence
        print("\n4. Verifying cluster convergence...")
        expected_keys = {
            "service.node1.status",
            "service.node2.status",
            "service.node3.status",
            "service.node4.status",
        }
        
        all_converged = True
        for node_id, node in cluster.nodes.items():
            actual_keys = set(node.state.keys())
            converged = expected_keys.issubset(actual_keys)
            print(f"   {node_id}: {len(actual_keys)} keys, converged={converged}")
            all_converged = all_converged and converged
        
        print(f"\n   All nodes converged: {all_converged} [OK]")
        
        # Cluster statistics
        print("\n5. Cluster statistics...")
        stats = cluster.get_cluster_statistics()
        print(f"   Total operations: {stats['total_operations']}")
        print(f"   Total syncs: {stats['total_syncs']}")
        print(f"   Total conflicts: {stats['total_conflicts']}")


def demo_audit_anchoring():
    """Demonstrate audit trail anchoring."""
    print("\n" + "=" * 70)
    print("DEMO 6: Audit Trail Anchoring")
    print("=" * 70)
    
    with TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create audit ledger
        audit_ledger = TemporalAuditLedger(tmpdir / "audit.json")
        
        state_register = DistributedStateRegister(
            node_id="secure_node",
            storage_path=tmpdir / "state.json",
            audit_ledger=audit_ledger,
            checkpoint_interval=3,
        )
        
        # Perform operations
        print("\n1. Performing state operations...")
        state_register.put("security.encryption", "AES-256", StateValueType.STRING)
        state_register.put("security.auth_method", "OAuth2", StateValueType.STRING)
        state_register.put("security.mfa_enabled", True, StateValueType.BOOLEAN)
        state_register.put("security.session_timeout", 3600, StateValueType.INTEGER)
        
        # Check audit log
        print("\n2. Examining audit trail...")
        audit_entries = audit_ledger.entries
        print(f"   Total audit entries: {len(audit_entries)}")
        
        # Show state change entries
        state_entries = [
            e for e in audit_entries
            if e.resource.startswith("state:")
        ]
        print(f"   State change entries: {len(state_entries)}")
        
        for entry in state_entries[:3]:
            print(f"\n   Entry {entry.sequence_number}:")
            print(f"      Action: {entry.action}")
            print(f"      Resource: {entry.resource}")
            print(f"      Hash: {entry.entry_hash[:16]}...")
            print(f"      Previous: {entry.previous_hash[:16] if entry.previous_hash else 'genesis'}...")
        
        # Show checkpoint
        print("\n3. Checkpoint information...")
        checkpoints = [
            e for e in audit_entries
            if e.action == "checkpoint_created"
        ]
        if checkpoints:
            cp = checkpoints[0]
            print(f"   Checkpoint created at operation {cp.metadata['operation_count']}")
            print(f"   Merkle root: {cp.metadata['merkle_root'][:16]}...")
            print(f"   State size: {cp.metadata['state_size']} keys")
        
        # Verify audit integrity
        print("\n4. Verifying audit trail integrity...")
        is_valid, violations = audit_ledger.verify_chain()
        print(f"   Audit trail valid: {is_valid}")
        if is_valid:
            print("   All hash chains verified [OK]")
        else:
            print(f"   Violations: {violations}")


def main():
    """Run all demonstrations."""
    print("\n")
    print("=" * 70)
    print("  Enhanced STATE_REGISTER - Distributed Synchronization Demo  ".center(70))
    print("=" * 70)
    
    try:
        demo_basic_operations()
        demo_distributed_sync()
        demo_conflict_resolution()
        demo_causal_consistency()
        demo_cluster_gossip()
        demo_audit_anchoring()
        
        print("\n" + "=" * 70)
        print("All demonstrations completed successfully! [OK]")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n[X] Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
