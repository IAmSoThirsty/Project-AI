"""
E2E Test Configuration and Fixtures
Shared configuration and utilities for E2E tests
"""

import os
from typing import AsyncGenerator

import pytest
from temporalio.client import Client
from temporalio.worker import Worker
from temporalio.testing import WorkflowEnvironment

from temporal.workflows.triumvirate_workflow import TriumvirateWorkflow


# Test configuration
TEST_TASK_QUEUE = os.getenv("TEST_TASK_QUEUE", "test-task-queue")
TEMPORAL_ADDRESS = os.getenv("TEMPORAL_ADDRESS", "localhost:7233")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE", "default")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def temporal_client() -> AsyncGenerator[Client, None]:
    """
    Provide Temporal client for testing.
    Uses local test environment by default.
    """
    use_real_server = os.getenv("USE_REAL_TEMPORAL", "false").lower() == "true"
    
    if use_real_server:
        # Connect to real Temporal server
        client = await Client.connect(
            TEMPORAL_ADDRESS,
            namespace=TEMPORAL_NAMESPACE,
        )
        try:
            yield client
        finally:
            await client.close()
    else:
        # Use local test environment
        env = await WorkflowEnvironment.start_local()
        try:
            yield env.client
        finally:
            await env.shutdown()


@pytest.fixture(scope="function")
async def temporal_worker(temporal_client: Client) -> AsyncGenerator[Worker, None]:
    """
    Provide Temporal worker for testing.
    Automatically starts and stops worker.
    """
    import asyncio
    
    worker = Worker(
        temporal_client,
        task_queue=TEST_TASK_QUEUE,
        workflows=[TriumvirateWorkflow],
    )
    
    async def run_worker():
        await worker.run()
    
    worker_task = asyncio.create_task(run_worker())
    
    try:
        # Allow worker to start
        await asyncio.sleep(0.5)
        yield worker
    finally:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass


# Pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "stress: marks tests as stress tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
