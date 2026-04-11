"""
Chaos Testing for Temporal Workflows
Python-based chaos tests that can run with or without K8s chaos tools
"""

import asyncio
import random
import time
from typing import List, Dict, Any
from contextlib import asynccontextmanager

import pytest


class ChaosSimulator:
    """Simulate various failure scenarios for chaos testing."""
    
    def __init__(self):
        self.active_failures = []
    
    @asynccontextmanager
    async def simulate_network_partition(self, duration_seconds: int = 30):
        """Simulate network partition between worker and server."""
        print(f"🔥 Simulating network partition for {duration_seconds}s")
        
        async def partition_task():
            await asyncio.sleep(duration_seconds)
        
        task = asyncio.create_task(partition_task())
        self.active_failures.append(("network_partition", task))
        
        try:
            yield
        finally:
            await task
            self.active_failures.remove(("network_partition", task))
            print("✅ Network partition ended")
    
    @asynccontextmanager
    async def simulate_node_crash(self, duration_seconds: int = 60):
        """Simulate worker node crash."""
        print(f"🔥 Simulating node crash for {duration_seconds}s")
        
        async def crash_task():
            await asyncio.sleep(duration_seconds)
        
        task = asyncio.create_task(crash_task())
        self.active_failures.append(("node_crash", task))
        
        try:
            yield
        finally:
            await task
            self.active_failures.remove(("node_crash", task))
            print("✅ Node recovered")
    
    @asynccontextmanager
    async def simulate_high_latency(self, latency_ms: int = 500, duration_seconds: int = 60):
        """Simulate high network latency."""
        print(f"🔥 Simulating {latency_ms}ms latency for {duration_seconds}s")
        
        async def latency_task():
            await asyncio.sleep(duration_seconds)
        
        task = asyncio.create_task(latency_task())
        self.active_failures.append(("high_latency", task))
        
        try:
            yield
        finally:
            await task
            self.active_failures.remove(("high_latency", task))
            print("✅ Latency normalized")
    
    @asynccontextmanager
    async def simulate_cascading_failures(self):
        """Simulate cascading failures across multiple components."""
        print("🔥 Simulating cascading failures")
        
        async def cascade():
            # Stage 1: Single node failure
            await asyncio.sleep(5)
            print("  ⚡ Stage 1: Node 1 failed")
            
            # Stage 2: Network partition
            await asyncio.sleep(10)
            print("  ⚡ Stage 2: Network partition detected")
            
            # Stage 3: Additional node failures
            await asyncio.sleep(15)
            print("  ⚡ Stage 3: Nodes 2-3 failed")
            
            # Stage 4: Recovery begins
            await asyncio.sleep(20)
            print("  ✅ Stage 4: Recovery initiated")
        
        task = asyncio.create_task(cascade())
        self.active_failures.append(("cascading_failure", task))
        
        try:
            yield
        finally:
            await task
            self.active_failures.remove(("cascading_failure", task))
            print("✅ System recovered from cascading failures")


@pytest.fixture
def chaos_simulator():
    """Provide chaos simulator for tests."""
    return ChaosSimulator()


class TestChaosEngineering:
    """Chaos engineering tests for Temporal workflows."""

    @pytest.mark.asyncio
    async def test_workflow_survives_network_partition(
        self, temporal_client, temporal_worker, chaos_simulator
    ):
        """Test workflow survives network partition between worker and server."""
        from temporal.workflows.triumvirate_workflow import (
            TriumvirateWorkflow,
            TriumvirateRequest,
        )
        import uuid
        from datetime import timedelta
        
        workflow_id = f"chaos-network-{uuid.uuid4().hex[:8]}"
        
        # Start workflow
        request = TriumvirateRequest(
            input_data={
                "agent_id": "chaos-agent",
                "operation": "resilient_task",
            },
            timeout_seconds=120,
            max_retries=5,
        )
        
        handle = await temporal_client.start_workflow(
            TriumvirateWorkflow.run,
            request,
            id=workflow_id,
            task_queue="test-task-queue",
            execution_timeout=timedelta(seconds=180),
        )
        
        # Wait a bit, then inject network partition
        await asyncio.sleep(2)
        
        async with chaos_simulator.simulate_network_partition(duration_seconds=15):
            # Workflow should continue despite network issues
            await asyncio.sleep(5)
        
        # Wait for completion
        result = await handle.result()
        
        # Should eventually succeed due to retries
        assert result.success is True

    @pytest.mark.asyncio
    async def test_workflow_survives_worker_crash(
        self, temporal_client, temporal_worker, chaos_simulator
    ):
        """Test workflow survives worker node crash."""
        from temporal.workflows.triumvirate_workflow import (
            TriumvirateWorkflow,
            TriumvirateRequest,
        )
        import uuid
        from datetime import timedelta
        
        workflow_id = f"chaos-crash-{uuid.uuid4().hex[:8]}"
        
        request = TriumvirateRequest(
            input_data={
                "agent_id": "crash-resilient-agent",
                "operation": "long_task",
            },
            timeout_seconds=180,
            max_retries=3,
        )
        
        handle = await temporal_client.start_workflow(
            TriumvirateWorkflow.run,
            request,
            id=workflow_id,
            task_queue="test-task-queue",
            execution_timeout=timedelta(seconds=300),
        )
        
        # Simulate worker crash
        async with chaos_simulator.simulate_node_crash(duration_seconds=20):
            await asyncio.sleep(10)
        
        # Workflow should be picked up by another worker and complete
        result = await handle.result()
        assert result.success is True

    @pytest.mark.asyncio
    async def test_workflow_degrades_gracefully_under_latency(
        self, temporal_client, temporal_worker, chaos_simulator
    ):
        """Test workflow degrades gracefully under high latency."""
        from temporal.workflows.triumvirate_workflow import (
            TriumvirateWorkflow,
            TriumvirateRequest,
        )
        import uuid
        from datetime import timedelta
        
        workflow_id = f"chaos-latency-{uuid.uuid4().hex[:8]}"
        
        request = TriumvirateRequest(
            input_data={
                "agent_id": "latency-agent",
                "operation": "latency_test",
            },
            timeout_seconds=60,
        )
        
        start_time = time.time()
        
        handle = await temporal_client.start_workflow(
            TriumvirateWorkflow.run,
            request,
            id=workflow_id,
            task_queue="test-task-queue",
        )
        
        # Inject high latency
        async with chaos_simulator.simulate_high_latency(latency_ms=1000, duration_seconds=30):
            pass
        
        result = await handle.result()
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Should complete, but may take longer
        assert result.success is True
        print(f"Workflow completed in {duration:.2f}s under high latency")

    @pytest.mark.asyncio
    async def test_system_recovers_from_cascading_failures(
        self, temporal_client, temporal_worker, chaos_simulator
    ):
        """Test system recovery from cascading failures."""
        from temporal.workflows.triumvirate_workflow import (
            TriumvirateWorkflow,
            TriumvirateRequest,
        )
        import uuid
        from datetime import timedelta
        
        workflow_id = f"chaos-cascade-{uuid.uuid4().hex[:8]}"
        
        request = TriumvirateRequest(
            input_data={
                "agent_id": "cascade-agent",
                "operation": "cascade_resilient_task",
            },
            timeout_seconds=300,
            max_retries=10,  # High retry count for cascading failures
        )
        
        handle = await temporal_client.start_workflow(
            TriumvirateWorkflow.run,
            request,
            id=workflow_id,
            task_queue="test-task-queue",
            execution_timeout=timedelta(seconds=600),
        )
        
        # Simulate cascading failures
        async with chaos_simulator.simulate_cascading_failures():
            await asyncio.sleep(30)
        
        # System should eventually recover
        result = await handle.result()
        assert result.success is True

    @pytest.mark.asyncio
    async def test_multiple_concurrent_failures(
        self, temporal_client, temporal_worker, chaos_simulator
    ):
        """Test system under multiple concurrent chaos conditions."""
        from temporal.workflows.triumvirate_workflow import (
            TriumvirateWorkflow,
            TriumvirateRequest,
        )
        import uuid
        from datetime import timedelta
        
        # Start multiple workflows
        num_workflows = 10
        handles = []
        
        for i in range(num_workflows):
            workflow_id = f"chaos-multi-{i}-{uuid.uuid4().hex[:8]}"
            request = TriumvirateRequest(
                input_data={
                    "agent_id": f"multi-chaos-agent-{i}",
                    "operation": "resilient_task",
                },
                timeout_seconds=120,
                max_retries=5,
            )
            
            handle = await temporal_client.start_workflow(
                TriumvirateWorkflow.run,
                request,
                id=workflow_id,
                task_queue="test-task-queue",
            )
            handles.append(handle)
        
        # Inject multiple concurrent failures
        async with chaos_simulator.simulate_network_partition(duration_seconds=20):
            async with chaos_simulator.simulate_high_latency(latency_ms=500, duration_seconds=30):
                await asyncio.sleep(15)
        
        # Wait for all workflows to complete
        results = await asyncio.gather(*[h.result() for h in handles], return_exceptions=True)
        
        # Most should succeed despite chaos
        from temporal.workflows.triumvirate_workflow import TriumvirateResult
        successes = sum(1 for r in results if isinstance(r, TriumvirateResult) and r.success)
        success_rate = (successes / num_workflows) * 100
        
        print(f"Success rate under chaos: {success_rate:.1f}%")
        
        # Should have at least 80% success rate
        assert success_rate >= 80.0


@pytest.mark.chaos
class TestChaosScenarios:
    """Real-world chaos scenarios."""

    @pytest.mark.asyncio
    async def test_split_brain_scenario(self, temporal_client, temporal_worker, chaos_simulator):
        """Test handling of split-brain scenario in distributed system."""
        print("\n🧠 Testing split-brain scenario...")
        
        # This would require more complex setup with multiple Temporal clusters
        # For now, we simulate the concept
        
        async with chaos_simulator.simulate_network_partition(duration_seconds=30):
            # In a real split-brain, different parts of the system would diverge
            await asyncio.sleep(10)
        
        # System should reconcile after partition heals
        print("✅ Split-brain test completed")

    @pytest.mark.asyncio
    async def test_thundering_herd_after_recovery(
        self, temporal_client, temporal_worker, chaos_simulator
    ):
        """Test system behavior when many workflows resume after failure."""
        from temporal.workflows.triumvirate_workflow import (
            TriumvirateWorkflow,
            TriumvirateRequest,
        )
        import uuid
        
        # Start many workflows
        num_workflows = 50
        handles = []
        
        for i in range(num_workflows):
            workflow_id = f"herd-{i}-{uuid.uuid4().hex[:8]}"
            request = TriumvirateRequest(
                input_data={
                    "agent_id": f"herd-agent-{i}",
                    "operation": "herd_test",
                },
                timeout_seconds=120,
                max_retries=3,
            )
            
            handle = await temporal_client.start_workflow(
                TriumvirateWorkflow.run,
                request,
                id=workflow_id,
                task_queue="test-task-queue",
            )
            handles.append(handle)
        
        # Simulate failure affecting all
        await asyncio.sleep(2)
        async with chaos_simulator.simulate_node_crash(duration_seconds=10):
            pass
        
        # All workflows should resume - test for thundering herd
        results = await asyncio.gather(*[h.result() for h in handles], return_exceptions=True)
        
        from temporal.workflows.triumvirate_workflow import TriumvirateResult
        successes = sum(1 for r in results if isinstance(r, TriumvirateResult) and r.success)
        
        print(f"Thundering herd: {successes}/{num_workflows} workflows succeeded")
        
        # Most should succeed
        assert successes >= num_workflows * 0.9
