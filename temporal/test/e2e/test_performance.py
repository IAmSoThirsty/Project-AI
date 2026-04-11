"""
E2E Test: Performance and Load Testing
Tests system performance under various load conditions
"""

import asyncio
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from typing import List, Tuple

import pytest
from temporalio.client import Client
from temporalio.worker import Worker

from temporal.workflows.triumvirate_workflow import (
    TriumvirateWorkflow,
    TriumvirateRequest,
    TriumvirateResult,
)


class TestPerformance:
    """Performance and load testing for Temporal workflows."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_throughput_100_workflows(self, temporal_client, temporal_worker):
        """Test system throughput with 100 concurrent workflows."""
        num_workflows = 100
        start_time = time.time()
        
        handles = []
        for i in range(num_workflows):
            workflow_id = f"throughput-{i}-{uuid.uuid4().hex[:8]}"
            request = TriumvirateRequest(
                input_data={
                    "agent_id": f"agent-{i}",
                    "operation": "throughput_test",
                    "iteration": i,
                },
                context={"batch": "throughput-100"},
                timeout_seconds=30,
            )
            
            handle = await temporal_client.start_workflow(
                TriumvirateWorkflow.run,
                request,
                id=workflow_id,
                task_queue="test-task-queue",
            )
            handles.append(handle)
        
        # Wait for all to complete
        results = await asyncio.gather(*[h.result() for h in handles])
        
        end_time = time.time()
        duration = end_time - start_time
        throughput = num_workflows / duration
        
        # Verify all succeeded
        assert all(r.success for r in results)
        
        # Log performance metrics
        print(f"\nThroughput: {throughput:.2f} workflows/second")
        print(f"Total duration: {duration:.2f} seconds")
        
        # Performance threshold: should complete in under 60 seconds
        assert duration < 60, f"Throughput test too slow: {duration:.2f}s"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_latency_p95_p99(self, temporal_client, temporal_worker):
        """Test workflow latency P95 and P99."""
        num_workflows = 50
        latencies = []
        
        for i in range(num_workflows):
            workflow_id = f"latency-{i}-{uuid.uuid4().hex[:8]}"
            request = TriumvirateRequest(
                input_data={
                    "agent_id": f"agent-{i}",
                    "operation": "latency_test",
                },
                context={"test": "latency"},
                timeout_seconds=10,
            )
            
            start = time.time()
            handle = await temporal_client.start_workflow(
                TriumvirateWorkflow.run,
                request,
                id=workflow_id,
                task_queue="test-task-queue",
            )
            result = await handle.result()
            end = time.time()
            
            assert result.success
            latencies.append(end - start)
        
        # Calculate percentiles
        latencies.sort()
        p50 = latencies[int(len(latencies) * 0.50)]
        p95 = latencies[int(len(latencies) * 0.95)]
        p99 = latencies[int(len(latencies) * 0.99)]
        
        print(f"\nLatency P50: {p50*1000:.2f}ms")
        print(f"Latency P95: {p95*1000:.2f}ms")
        print(f"Latency P99: {p99*1000:.2f}ms")
        
        # Performance thresholds
        assert p95 < 2.0, f"P95 latency too high: {p95:.2f}s"
        assert p99 < 5.0, f"P99 latency too high: {p99:.2f}s"

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_sustained_load_1000_workflows(self, temporal_client, temporal_worker):
        """Test sustained load with 1000+ workflows over time."""
        total_workflows = 1000
        batch_size = 100
        batches = total_workflows // batch_size
        
        all_results = []
        start_time = time.time()
        
        for batch_num in range(batches):
            handles = []
            
            for i in range(batch_size):
                workflow_num = batch_num * batch_size + i
                workflow_id = f"sustained-{workflow_num}-{uuid.uuid4().hex[:8]}"
                
                request = TriumvirateRequest(
                    input_data={
                        "agent_id": f"agent-{workflow_num}",
                        "operation": "sustained_load",
                        "batch": batch_num,
                        "index": i,
                    },
                    context={"load_test": "sustained"},
                    timeout_seconds=30,
                )
                
                handle = await temporal_client.start_workflow(
                    TriumvirateWorkflow.run,
                    request,
                    id=workflow_id,
                    task_queue="test-task-queue",
                )
                handles.append(handle)
            
            # Wait for batch to complete
            batch_results = await asyncio.gather(*[h.result() for h in handles])
            all_results.extend(batch_results)
            
            print(f"Completed batch {batch_num + 1}/{batches}")
            
            # Small delay between batches to simulate sustained load
            await asyncio.sleep(0.5)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify all succeeded
        success_count = sum(1 for r in all_results if r.success)
        success_rate = (success_count / total_workflows) * 100
        
        print(f"\nSustained load test results:")
        print(f"Total workflows: {total_workflows}")
        print(f"Successful: {success_count}")
        print(f"Success rate: {success_rate:.2f}%")
        print(f"Duration: {duration:.2f}s")
        print(f"Throughput: {total_workflows/duration:.2f} workflows/s")
        
        # Should have >99% success rate
        assert success_rate > 99.0, f"Success rate too low: {success_rate:.2f}%"

    @pytest.mark.asyncio
    async def test_memory_leak_detection(self, temporal_client, temporal_worker):
        """Test for memory leaks in long-running workflows."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run many workflows
        num_workflows = 200
        for i in range(num_workflows):
            workflow_id = f"memory-{i}-{uuid.uuid4().hex[:8]}"
            request = TriumvirateRequest(
                input_data={
                    "agent_id": f"agent-{i}",
                    "operation": "memory_test",
                },
                context={"test": "memory"},
            )
            
            handle = await temporal_client.start_workflow(
                TriumvirateWorkflow.run,
                request,
                id=workflow_id,
                task_queue="test-task-queue",
            )
            await handle.result()
            
            if i % 50 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                print(f"Memory after {i} workflows: {current_memory:.2f} MB")
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory
        
        print(f"\nMemory growth: {memory_growth:.2f} MB")
        
        # Should not grow more than 100MB for 200 workflows
        assert memory_growth < 100, f"Possible memory leak: {memory_growth:.2f} MB growth"


@pytest.mark.stress
class TestStress:
    """Stress tests for extreme conditions."""

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_burst_traffic(self, temporal_client, temporal_worker):
        """Test system behavior under burst traffic."""
        # Simulate sudden burst of 500 workflows
        num_workflows = 500
        
        handles = []
        start_time = time.time()
        
        # Start all workflows simultaneously (burst)
        for i in range(num_workflows):
            workflow_id = f"burst-{i}-{uuid.uuid4().hex[:8]}"
            request = TriumvirateRequest(
                input_data={
                    "agent_id": f"agent-{i}",
                    "operation": "burst_test",
                },
                context={"test": "burst"},
                timeout_seconds=60,
            )
            
            handle = await temporal_client.start_workflow(
                TriumvirateWorkflow.run,
                request,
                id=workflow_id,
                task_queue="test-task-queue",
            )
            handles.append(handle)
        
        creation_time = time.time() - start_time
        print(f"Created {num_workflows} workflows in {creation_time:.2f}s")
        
        # Wait for all to complete
        results = await asyncio.gather(*[h.result() for h in handles], return_exceptions=True)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Count successes and failures
        successes = sum(1 for r in results if isinstance(r, TriumvirateResult) and r.success)
        failures = len(results) - successes
        
        print(f"\nBurst test results:")
        print(f"Total: {num_workflows}")
        print(f"Successes: {successes}")
        print(f"Failures: {failures}")
        print(f"Duration: {total_duration:.2f}s")
        
        # Should handle burst with minimal failures (<5%)
        failure_rate = (failures / num_workflows) * 100
        assert failure_rate < 5.0, f"Too many failures under burst: {failure_rate:.2f}%"

    @pytest.mark.asyncio
    async def test_workflow_with_large_payload(self, temporal_client, temporal_worker):
        """Test workflow with large input/output payloads."""
        # Create large payload (1MB of data)
        large_data = {
            "items": [
                {"id": i, "data": "x" * 1000}
                for i in range(1000)
            ]
        }
        
        workflow_id = f"large-payload-{uuid.uuid4().hex[:8]}"
        request = TriumvirateRequest(
            input_data={
                "agent_id": "payload-agent",
                "operation": "process_large_data",
                "data": large_data,
            },
            context={"test": "large_payload"},
            timeout_seconds=30,
        )
        
        handle = await temporal_client.start_workflow(
            TriumvirateWorkflow.run,
            request,
            id=workflow_id,
            task_queue="test-task-queue",
        )
        
        result = await handle.result()
        
        # Should handle large payloads
        assert result.success is True
