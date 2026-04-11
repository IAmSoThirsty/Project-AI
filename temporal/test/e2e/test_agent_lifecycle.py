"""
E2E Test: Agent Lifecycle
Tests complete flow: agent registration → task assignment → execution → completion
"""

import asyncio
import uuid
from datetime import timedelta
from typing import Dict, Any

import pytest
from temporalio import workflow
from temporalio.client import Client, WorkflowFailureError
from temporalio.worker import Worker
from temporalio.testing import WorkflowEnvironment

from temporal.workflows.triumvirate_workflow import (
    TriumvirateWorkflow,
    TriumvirateRequest,
    TriumvirateResult,
)


@pytest.fixture
async def temporal_client():
    """Fixture to provide Temporal client for testing."""
    env = await WorkflowEnvironment.start_local()
    try:
        yield env.client
    finally:
        await env.shutdown()


@pytest.fixture
async def temporal_worker(temporal_client):
    """Fixture to start a Temporal worker."""
    worker = Worker(
        temporal_client,
        task_queue="test-task-queue",
        workflows=[TriumvirateWorkflow],
    )
    
    async def run_worker():
        await worker.run()
    
    worker_task = asyncio.create_task(run_worker())
    try:
        await asyncio.sleep(0.5)  # Allow worker to start
        yield worker
    finally:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass


class TestAgentLifecycle:
    """End-to-end tests for complete agent lifecycle."""

    @pytest.mark.asyncio
    async def test_agent_registration_to_completion(self, temporal_client, temporal_worker):
        """Test full flow: agent registration → task execution → completion."""
        # Step 1: Simulate agent registration
        agent_id = f"agent-{uuid.uuid4().hex[:8]}"
        workflow_id = f"agent-lifecycle-{agent_id}"
        
        request = TriumvirateRequest(
            input_data={
                "agent_id": agent_id,
                "operation": "register_and_execute",
                "task": {
                    "type": "analysis",
                    "data": "test data",
                }
            },
            context={"correlation_id": workflow_id},
            timeout_seconds=60,
            max_retries=2,
        )
        
        # Step 2: Execute workflow
        handle = await temporal_client.start_workflow(
            TriumvirateWorkflow.run,
            request,
            id=workflow_id,
            task_queue="test-task-queue",
            execution_timeout=timedelta(seconds=120),
        )
        
        # Step 3: Wait for completion
        result: TriumvirateResult = await handle.result()
        
        # Step 4: Verify result
        assert result.success is True
        assert result.correlation_id == workflow_id
        assert result.error is None
        assert result.output is not None

    @pytest.mark.asyncio
    async def test_multiple_agents_concurrent_execution(self, temporal_client, temporal_worker):
        """Test concurrent execution of multiple agents."""
        num_agents = 5
        workflow_handles = []
        
        # Start multiple agent workflows concurrently
        for i in range(num_agents):
            agent_id = f"agent-{i}-{uuid.uuid4().hex[:8]}"
            workflow_id = f"concurrent-agent-{agent_id}"
            
            request = TriumvirateRequest(
                input_data={
                    "agent_id": agent_id,
                    "operation": "concurrent_test",
                    "iteration": i,
                },
                context={"correlation_id": workflow_id},
                timeout_seconds=60,
            )
            
            handle = await temporal_client.start_workflow(
                TriumvirateWorkflow.run,
                request,
                id=workflow_id,
                task_queue="test-task-queue",
                execution_timeout=timedelta(seconds=120),
            )
            workflow_handles.append((agent_id, handle))
        
        # Wait for all to complete
        results = []
        for agent_id, handle in workflow_handles:
            result = await handle.result()
            results.append((agent_id, result))
        
        # Verify all succeeded
        assert len(results) == num_agents
        for agent_id, result in results:
            assert result.success is True, f"Agent {agent_id} failed"

    @pytest.mark.asyncio
    async def test_agent_task_retry_on_failure(self, temporal_client, temporal_worker):
        """Test agent task retry mechanism on transient failures."""
        workflow_id = f"retry-test-{uuid.uuid4().hex[:8]}"
        
        request = TriumvirateRequest(
            input_data={
                "agent_id": "retry-agent",
                "operation": "flaky_task",
                "fail_count": 2,  # Fail twice, succeed on third
            },
            context={"correlation_id": workflow_id},
            timeout_seconds=120,
            max_retries=3,
        )
        
        handle = await temporal_client.start_workflow(
            TriumvirateWorkflow.run,
            request,
            id=workflow_id,
            task_queue="test-task-queue",
            execution_timeout=timedelta(seconds=180),
        )
        
        result = await handle.result()
        
        # Should succeed after retries
        assert result.success is True

    @pytest.mark.asyncio
    async def test_agent_timeout_handling(self, temporal_client, temporal_worker):
        """Test agent task timeout handling."""
        workflow_id = f"timeout-test-{uuid.uuid4().hex[:8]}"
        
        request = TriumvirateRequest(
            input_data={
                "agent_id": "timeout-agent",
                "operation": "long_running_task",
                "duration_seconds": 100,
            },
            context={"correlation_id": workflow_id},
            timeout_seconds=5,  # Short timeout
            max_retries=1,
        )
        
        handle = await temporal_client.start_workflow(
            TriumvirateWorkflow.run,
            request,
            id=workflow_id,
            task_queue="test-task-queue",
            execution_timeout=timedelta(seconds=30),
        )
        
        # Expect timeout or failure
        with pytest.raises((WorkflowFailureError, asyncio.TimeoutError)):
            await asyncio.wait_for(handle.result(), timeout=10)

    @pytest.mark.asyncio
    async def test_agent_state_persistence(self, temporal_client, temporal_worker):
        """Test agent state persistence across workflow executions."""
        agent_id = f"stateful-agent-{uuid.uuid4().hex[:8]}"
        
        # First execution - store state
        workflow_id_1 = f"state-test-1-{agent_id}"
        request_1 = TriumvirateRequest(
            input_data={
                "agent_id": agent_id,
                "operation": "store_state",
                "state_data": {"counter": 1, "status": "initialized"},
            },
            context={"correlation_id": workflow_id_1},
        )
        
        handle_1 = await temporal_client.start_workflow(
            TriumvirateWorkflow.run,
            request_1,
            id=workflow_id_1,
            task_queue="test-task-queue",
        )
        result_1 = await handle_1.result()
        assert result_1.success is True
        
        # Second execution - retrieve and verify state
        workflow_id_2 = f"state-test-2-{agent_id}"
        request_2 = TriumvirateRequest(
            input_data={
                "agent_id": agent_id,
                "operation": "retrieve_state",
            },
            context={"correlation_id": workflow_id_2},
        )
        
        handle_2 = await temporal_client.start_workflow(
            TriumvirateWorkflow.run,
            request_2,
            id=workflow_id_2,
            task_queue="test-task-queue",
        )
        result_2 = await handle_2.result()
        
        assert result_2.success is True
        assert result_2.output is not None

    @pytest.mark.asyncio
    async def test_workflow_cancellation(self, temporal_client, temporal_worker):
        """Test graceful workflow cancellation."""
        workflow_id = f"cancel-test-{uuid.uuid4().hex[:8]}"
        
        request = TriumvirateRequest(
            input_data={
                "agent_id": "cancel-agent",
                "operation": "long_running_task",
                "duration_seconds": 300,
            },
            context={"correlation_id": workflow_id},
            timeout_seconds=600,
        )
        
        handle = await temporal_client.start_workflow(
            TriumvirateWorkflow.run,
            request,
            id=workflow_id,
            task_queue="test-task-queue",
        )
        
        # Wait a bit, then cancel
        await asyncio.sleep(1)
        await handle.cancel()
        
        # Verify cancellation
        with pytest.raises(WorkflowFailureError):
            await handle.result()


@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests for agent workflows with external services."""

    @pytest.mark.asyncio
    async def test_agent_with_external_api(self, temporal_client, temporal_worker):
        """Test agent workflow with external API calls."""
        workflow_id = f"api-integration-{uuid.uuid4().hex[:8]}"
        
        request = TriumvirateRequest(
            input_data={
                "agent_id": "api-agent",
                "operation": "external_api_call",
                "api_endpoint": "https://api.example.com/data",
                "method": "GET",
            },
            context={"correlation_id": workflow_id},
            timeout_seconds=30,
        )
        
        handle = await temporal_client.start_workflow(
            TriumvirateWorkflow.run,
            request,
            id=workflow_id,
            task_queue="test-task-queue",
        )
        
        result = await handle.result()
        assert result.success is True

    @pytest.mark.asyncio
    async def test_agent_data_pipeline(self, temporal_client, temporal_worker):
        """Test end-to-end data pipeline with multiple agents."""
        pipeline_id = f"pipeline-{uuid.uuid4().hex[:8]}"
        
        # Stage 1: Data ingestion
        request_1 = TriumvirateRequest(
            input_data={
                "agent_id": "ingest-agent",
                "operation": "ingest_data",
                "source": "test_source",
            },
            context={"pipeline_id": pipeline_id, "stage": 1},
        )
        
        handle_1 = await temporal_client.start_workflow(
            TriumvirateWorkflow.run,
            request_1,
            id=f"{pipeline_id}-stage1",
            task_queue="test-task-queue",
        )
        result_1 = await handle_1.result()
        assert result_1.success is True
        
        # Stage 2: Data processing (uses output from stage 1)
        request_2 = TriumvirateRequest(
            input_data={
                "agent_id": "process-agent",
                "operation": "process_data",
                "input_data": result_1.output,
            },
            context={"pipeline_id": pipeline_id, "stage": 2},
        )
        
        handle_2 = await temporal_client.start_workflow(
            TriumvirateWorkflow.run,
            request_2,
            id=f"{pipeline_id}-stage2",
            task_queue="test-task-queue",
        )
        result_2 = await handle_2.result()
        assert result_2.success is True
        
        # Stage 3: Data export
        request_3 = TriumvirateRequest(
            input_data={
                "agent_id": "export-agent",
                "operation": "export_data",
                "input_data": result_2.output,
                "destination": "test_destination",
            },
            context={"pipeline_id": pipeline_id, "stage": 3},
        )
        
        handle_3 = await temporal_client.start_workflow(
            TriumvirateWorkflow.run,
            request_3,
            id=f"{pipeline_id}-stage3",
            task_queue="test-task-queue",
        )
        result_3 = await handle_3.result()
        assert result_3.success is True
        assert "exported" in str(result_3.output).lower()
