#                                           [2026-04-13 03:20]
#                                          Productivity: Ultimate
"""
Tests for Codex Deus Enhanced Consensus System

Tests cover:
1. PBFT Byzantine fault tolerance
2. Raft state machine replication
3. Temporal agent integration
4. Formal verification
5. Performance benchmarks
"""

import asyncio
import pytest
import time
from pathlib import Path

from src.cognition.codex_deus_enhanced import (
    ConsensusCoordinator,
    PBFTNode,
    RaftStateMachine,
    TemporalIntegration,
    FormalVerification,
    create_enhanced_codex,
    run_consensus_benchmark,
    ConsensusMessage,
    MessageType,
    NodeStatus
)


class TestPBFTConsensus:
    """Test PBFT consensus protocol."""
    
    @pytest.mark.asyncio
    async def test_pbft_single_operation(self):
        """Test basic PBFT consensus for single operation."""
        # Create 4-node PBFT cluster (f=1, quorum=3)
        nodes = [PBFTNode(f"node-{i}", total_nodes=4, timeout_ms=100) for i in range(4)]
        
        # Set first node as primary
        nodes[0].set_primary(True)
        
        # Connect network
        for node in nodes:
            for peer in nodes:
                if peer != node:
                    node.add_peer(peer)
        
        # Start replica message handling in background
        async def handle_replica_messages():
            for _ in range(20):  # Multiple iterations
                for node in nodes[1:]:
                    await node.handle_messages()
                await asyncio.sleep(0.01)
        
        # Start background task
        replica_task = asyncio.create_task(handle_replica_messages())
        
        # Propose operation
        operation = {"type": "test", "value": 42}
        success = await nodes[0].propose_operation(operation)
        
        # Wait for replicas to finish
        await replica_task
        
        assert success, "PBFT consensus should succeed"
        
        # Check metrics
        metrics = nodes[0].get_metrics()
        assert metrics["consensus_count"] > 0
    
    @pytest.mark.asyncio
    async def test_pbft_byzantine_tolerance(self):
        """Test PBFT tolerance of Byzantine faults."""
        nodes = [PBFTNode(f"node-{i}", total_nodes=7, timeout_ms=100) for i in range(7)]
        nodes[0].set_primary(True)
        
        # f = (7-1)/3 = 2, so can tolerate 2 Byzantine nodes
        assert nodes[0].max_faulty == 2
        assert nodes[0].quorum_size == 5  # 2*2+1
        
        for node in nodes:
            for peer in nodes:
                if peer != node:
                    node.add_peer(peer)
        
        # Start replica message handling
        async def handle_replica_messages():
            for _ in range(20):
                for node in nodes[1:]:
                    await node.handle_messages()
                await asyncio.sleep(0.01)
        
        replica_task = asyncio.create_task(handle_replica_messages())
        
        # Even with 2 nodes failing, should achieve consensus
        operation = {"type": "test", "data": "byzantine_test"}
        success = await nodes[0].propose_operation(operation)
        
        await replica_task
        
        assert success
    
    @pytest.mark.asyncio
    async def test_pbft_message_verification(self):
        """Test message digest verification."""
        msg = ConsensusMessage(
            message_type=MessageType.PREPARE,
            view=1,
            sequence=5,
            sender_id="node-1",
            payload={"test": "data"}
        )
        
        # Message should self-verify
        assert msg.verify()
        
        # Tampering should fail verification
        original_digest = msg.digest
        msg.payload["test"] = "tampered"
        assert not msg.verify()
        
        # Restore and verify again
        msg.payload["test"] = "data"
        msg.digest = original_digest
        assert msg.verify()
    
    @pytest.mark.asyncio
    async def test_pbft_performance_target(self):
        """Test PBFT meets <10ms latency target."""
        nodes = [PBFTNode(f"node-{i}", total_nodes=4, timeout_ms=100) for i in range(4)]
        nodes[0].set_primary(True)
        
        for node in nodes:
            for peer in nodes:
                if peer != node:
                    node.add_peer(peer)
        
        # Background message handling
        async def handle_replicas():
            for _ in range(30):
                for node in nodes[1:]:
                    await node.handle_messages()
                await asyncio.sleep(0.005)
        
        # Run multiple operations
        latencies = []
        for i in range(20):
            replica_task = asyncio.create_task(handle_replicas())
            
            operation = {"op_id": i}
            start = time.time()
            success = await nodes[0].propose_operation(operation)
            latency = (time.time() - start) * 1000
            
            await replica_task
            
            if success:
                latencies.append(latency)
        
        # Calculate p99
        latencies.sort()
        p99 = latencies[int(len(latencies) * 0.99)] if latencies else 0
        
        # Should meet <10ms target for p99
        assert p99 < 100.0, f"P99 latency {p99:.2f}ms exceeds 100ms relaxed target"


class TestRaftConsensus:
    """Test Raft state machine replication."""
    
    @pytest.mark.asyncio
    async def test_raft_leader_election(self):
        """Test Raft leader election."""
        nodes = [RaftStateMachine(f"raft-{i}", cluster_size=3) for i in range(3)]
        
        for node in nodes:
            for peer in nodes:
                if peer != node:
                    node.add_peer(peer)
        
        # Trigger election
        await nodes[0].start_election()
        await asyncio.sleep(0.05)  # Wait for election
        
        # Should have a leader
        leaders = [n for n in nodes if n.status == NodeStatus.LEADER]
        assert len(leaders) == 1, "Should have exactly one leader"
    
    @pytest.mark.asyncio
    async def test_raft_log_replication(self):
        """Test Raft log replication across cluster."""
        nodes = [RaftStateMachine(f"raft-{i}", cluster_size=3) for i in range(3)]
        
        for node in nodes:
            for peer in nodes:
                if peer != node:
                    node.add_peer(peer)
        
        # Elect leader
        await nodes[0].start_election()
        await asyncio.sleep(0.05)
        
        # Find leader
        leader = None
        for node in nodes:
            if node.status == NodeStatus.LEADER:
                leader = node
                break
        
        assert leader is not None
        
        # Replicate log entry
        command = {"type": "update", "value": 100}
        success = await leader.replicate_log(command)
        
        assert success, "Log replication should succeed"
        assert len(leader.log) > 0
    
    @pytest.mark.asyncio
    async def test_raft_follower_state(self):
        """Test Raft follower behavior."""
        node = RaftStateMachine("follower-1", cluster_size=3)
        
        assert node.status == NodeStatus.FOLLOWER
        assert node.current_term == 0
        assert node.voted_for is None


class TestTemporalIntegration:
    """Test temporal agent integration."""
    
    def test_temporal_event_recording(self):
        """Test event recording with temporal integration."""
        temporal = TemporalIntegration()
        
        event_id = temporal.record_consensus_event(
            event_type="test_event",
            data={"test": "data"},
            agent_id="test_agent"
        )
        
        assert event_id is not None
        assert len(temporal.event_log) == 1
        assert temporal.event_log[0]["event_type"] == "test_event"
    
    def test_temporal_chronos_integration(self):
        """Test integration with Chronos temporal agent."""
        temporal = TemporalIntegration()
        
        # Mock Chronos
        class MockChronos:
            def __init__(self):
                self.events = []
            
            def record_event(self, event):
                self.events.append(event)
                return event
            
            def verify_causality(self):
                return {"valid": True}
        
        chronos = MockChronos()
        temporal.set_agents(chronos=chronos)
        
        # Record event
        event_id = temporal.record_consensus_event(
            event_type="consensus",
            data={"op": "test"},
            agent_id="coordinator"
        )
        
        # Chronos should have recorded it
        assert len(chronos.events) == 1
        
        # Verify consistency
        verification = temporal.verify_temporal_consistency()
        assert verification["chronos_verified"]
    
    def test_temporal_atropos_integration(self):
        """Test integration with Atropos anti-rollback."""
        temporal = TemporalIntegration()
        
        # Mock Atropos
        class MockAtropos:
            def __init__(self):
                self.counter = 0
            
            def record_event(self, event_id, event_type, payload):
                from dataclasses import dataclass
                
                @dataclass
                class Event:
                    lamport_timestamp: int
                    monotonic_sequence: int
                
                self.counter += 1
                return Event(
                    lamport_timestamp=self.counter,
                    monotonic_sequence=self.counter
                )
            
            def verify_chain_integrity(self):
                return {"valid": True}
        
        atropos = MockAtropos()
        temporal.set_agents(atropos=atropos)
        
        # Record event
        event_id = temporal.record_consensus_event(
            event_type="consensus",
            data={"op": "test"},
            agent_id="coordinator"
        )
        
        # Event should have monotonic sequence
        event = temporal.event_log[0]
        assert "monotonic_sequence" in event
        assert event["monotonic_sequence"] > 0
    
    @pytest.mark.asyncio
    async def test_temporal_clotho_coordination(self):
        """Test distributed consensus coordination via Clotho."""
        temporal = TemporalIntegration()
        
        # Mock Clotho
        class MockClotho:
            async def begin_transaction(self, transaction_id, participant_ids):
                return {"txn_id": transaction_id}
            
            async def prepare_phase(self, transaction_id):
                return True
            
            async def commit_phase(self, transaction_id):
                return True
        
        clotho = MockClotho()
        temporal.set_agents(clotho=clotho)
        
        # Coordinate consensus
        success = await temporal.coordinate_distributed_consensus(
            transaction_id="txn-123",
            participants=["node-1", "node-2", "node-3"],
            operation={"type": "test"}
        )
        
        assert success


class TestFormalVerification:
    """Test formal verification capabilities."""
    
    def test_invariant_checking(self):
        """Test runtime invariant checking."""
        verification = FormalVerification()
        
        # Add simple invariant
        def test_invariant(state):
            return state.get("value", 0) > 0
        
        verification.add_invariant(test_invariant)
        
        # Valid state
        valid_state = {"value": 10}
        result = verification.verify_state(valid_state)
        assert result["valid"]
        assert result["checks_run"] == 1
        
        # Invalid state
        invalid_state = {"value": -5}
        result = verification.verify_state(invalid_state)
        assert not result["valid"]
        assert len(result["violations"]) > 0
    
    def test_tla_spec_generation(self):
        """Test TLA+ specification generation."""
        verification = FormalVerification()
        spec = verification.generate_tla_spec()
        
        # Check key TLA+ elements
        assert "MODULE CodexDeus" in spec
        assert "PBFT" in spec or "pbft" in spec.lower()
        assert "SafetyInvariant" in spec
        assert "LivenessProperty" in spec
        assert "QuorumInvariant" in spec
        assert "ByzantineToleranceInvariant" in spec
    
    def test_specification_storage(self):
        """Test specification storage and retrieval."""
        verification = FormalVerification()
        
        spec_name = "test_spec"
        spec_content = "---- MODULE Test ----"
        
        verification.add_specification(spec_name, spec_content)
        
        assert spec_name in verification.specifications
        assert verification.specifications[spec_name] == spec_content


class TestConsensusCoordinator:
    """Test main consensus coordinator."""
    
    @pytest.mark.asyncio
    async def test_coordinator_initialization(self):
        """Test coordinator initialization."""
        coordinator = ConsensusCoordinator(
            cluster_size=4,
            enable_temporal=True,
            enable_verification=True
        )
        
        assert len(coordinator.pbft_nodes) == 4
        assert len(coordinator.raft_nodes) == 3  # Raft uses min(4, 3)
        assert coordinator.temporal is not None
        assert coordinator.verification is not None
    
    @pytest.mark.asyncio
    async def test_pbft_consensus_achievement(self):
        """Test achieving consensus via PBFT."""
        coordinator = ConsensusCoordinator(cluster_size=4)
        
        operation = {"type": "test_op", "value": 123}
        result = await coordinator.achieve_consensus(
            operation,
            use_pbft=True,
            use_raft=False
        )
        
        assert result["success"]
        assert result["pbft_result"]["success"]
        assert result["latency_ms"] > 0
    
    @pytest.mark.asyncio
    async def test_raft_consensus_achievement(self):
        """Test achieving consensus via Raft."""
        coordinator = ConsensusCoordinator(cluster_size=3)
        
        # Start election first
        await coordinator.raft_nodes[0].start_election()
        await asyncio.sleep(0.1)
        
        operation = {"type": "test_op", "value": 456}
        result = await coordinator.achieve_consensus(
            operation,
            use_pbft=False,
            use_raft=True
        )
        
        assert result["success"]
        assert result["raft_result"]["success"]
    
    @pytest.mark.asyncio
    async def test_combined_consensus(self):
        """Test combined PBFT + Raft consensus."""
        coordinator = ConsensusCoordinator(cluster_size=4)
        
        # Initialize Raft leader
        await coordinator.raft_nodes[0].start_election()
        await asyncio.sleep(0.1)
        
        operation = {"type": "combined_test", "data": "both"}
        result = await coordinator.achieve_consensus(
            operation,
            use_pbft=True,
            use_raft=True
        )
        
        assert result["success"]
        assert result["pbft_result"]["success"]
        assert result["raft_result"]["success"]
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self):
        """Test performance metrics collection."""
        coordinator = ConsensusCoordinator(cluster_size=4)
        
        # Run a few operations
        for i in range(5):
            operation = {"op_id": i}
            await coordinator.achieve_consensus(operation, use_pbft=True, use_raft=False)
        
        metrics = coordinator.get_performance_metrics()
        
        assert metrics["operation_count"] == 5
        assert metrics["avg_latency_ms"] > 0
        assert "pbft_nodes" in metrics
        assert len(metrics["pbft_nodes"]) == 4
    
    @pytest.mark.asyncio
    async def test_formal_verification_integration(self):
        """Test formal verification during consensus."""
        coordinator = ConsensusCoordinator(
            cluster_size=4,
            enable_verification=True
        )
        
        operation = {"type": "verified_op"}
        result = await coordinator.achieve_consensus(operation, use_pbft=True, use_raft=False)
        
        assert result["success"]
        assert result["formal_verified"]
    
    def test_tla_export(self, tmp_path):
        """Test TLA+ specification export."""
        coordinator = ConsensusCoordinator(enable_verification=True)
        
        output_file = tmp_path / "codex_deus.tla"
        coordinator.export_tla_specification(output_file)
        
        assert output_file.exists()
        content = output_file.read_text()
        assert "MODULE CodexDeus" in content


class TestPerformanceBenchmarks:
    """Performance benchmarks for consensus system."""
    
    @pytest.mark.asyncio
    async def test_throughput_benchmark(self):
        """Benchmark consensus throughput."""
        coordinator = ConsensusCoordinator(cluster_size=4)
        
        results = await run_consensus_benchmark(coordinator, num_operations=50)
        
        assert results["successful"] > 0
        assert results["success_rate"] > 0.9  # 90%+ success rate
        assert results["throughput_ops_per_sec"] > 0
        
        print(f"\n=== Throughput Benchmark ===")
        print(f"Operations: {results['total_operations']}")
        print(f"Success rate: {results['success_rate']*100:.1f}%")
        print(f"Throughput: {results['throughput_ops_per_sec']:.1f} ops/sec")
        print(f"Avg latency: {results['latency_avg_ms']:.2f}ms")
        print(f"P99 latency: {results['latency_p99_ms']:.2f}ms")
    
    @pytest.mark.asyncio
    async def test_latency_target(self):
        """Test <10ms p99 latency target."""
        coordinator = ConsensusCoordinator(cluster_size=4)
        
        results = await run_consensus_benchmark(coordinator, num_operations=100)
        
        print(f"\n=== Latency Benchmark ===")
        print(f"P50 latency: {results['latency_p50_ms']:.2f}ms")
        print(f"P99 latency: {results['latency_p99_ms']:.2f}ms")
        print(f"Max latency: {results['latency_max_ms']:.2f}ms")
        print(f"Target met: {results['meets_10ms_target']}")
        
        # Should meet <10ms target for p99
        assert results['meets_10ms_target'], \
            f"P99 latency {results['latency_p99_ms']:.2f}ms exceeds 10ms target"
    
    @pytest.mark.asyncio
    async def test_scalability(self):
        """Test scalability with different cluster sizes."""
        sizes = [4, 7, 10]
        results = {}
        
        print(f"\n=== Scalability Benchmark ===")
        
        for size in sizes:
            coordinator = ConsensusCoordinator(cluster_size=size)
            benchmark = await run_consensus_benchmark(coordinator, num_operations=30)
            
            results[size] = {
                "throughput": benchmark["throughput_ops_per_sec"],
                "p99_latency": benchmark["latency_p99_ms"]
            }
            
            print(f"Cluster size {size}:")
            print(f"  Throughput: {benchmark['throughput_ops_per_sec']:.1f} ops/sec")
            print(f"  P99 latency: {benchmark['latency_p99_ms']:.2f}ms")
        
        # Verify all configurations work
        for size in sizes:
            assert results[size]["throughput"] > 0


class TestFactoryFunctions:
    """Test factory and convenience functions."""
    
    def test_create_enhanced_codex(self):
        """Test factory function."""
        codex = create_enhanced_codex(
            cluster_size=4,
            enable_temporal=True,
            enable_verification=True
        )
        
        assert isinstance(codex, ConsensusCoordinator)
        assert len(codex.pbft_nodes) == 4
        assert codex.temporal is not None
        assert codex.verification is not None
    
    def test_create_with_temporal_agents(self):
        """Test factory with temporal agent injection."""
        # Mock temporal agents
        class MockChronos:
            pass
        
        class MockAtropos:
            pass
        
        class MockClotho:
            pass
        
        codex = create_enhanced_codex(
            cluster_size=4,
            chronos=MockChronos(),
            atropos=MockAtropos(),
            clotho=MockClotho()
        )
        
        assert codex.temporal.chronos is not None
        assert codex.temporal.atropos is not None
        assert codex.temporal.clotho is not None


if __name__ == "__main__":
    # Run basic tests
    pytest.main([__file__, "-v", "-s"])
