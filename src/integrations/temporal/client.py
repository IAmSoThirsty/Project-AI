"""
Temporal Client Connection Logic.

This module provides helpers for connecting to the Temporal server
and starting workflows from application code.
"""

import logging
import os
from typing import Any

from temporalio.client import Client

logger = logging.getLogger(__name__)


class TemporalClient:
    """
    Temporal client wrapper for Project-AI.

    Provides a simplified interface for connecting to Temporal server
    and starting workflows.

    Example:
        >>> client = TemporalClient()
        >>> await client.connect()
        >>> result = await client.start_workflow(
        ...     workflow_name="ExampleWorkflow",
        ...     workflow_id="example-123",
        ...     args={"data": "value"}
        ... )
    """

    def __init__(
        self,
        host: str | None = None,
        namespace: str | None = None,
        task_queue: str | None = None,
    ):
        """
        Initialize Temporal client.

        Args:
            host: Temporal server address (default: from TEMPORAL_HOST env or localhost:7233)
            namespace: Temporal namespace (default: from TEMPORAL_NAMESPACE env or 'default')
            task_queue: Default task queue (default: from TEMPORAL_TASK_QUEUE env or 'project-ai-tasks')
        """
        self.host = host or os.getenv("TEMPORAL_HOST", "localhost:7233")
        self.namespace = namespace or os.getenv("TEMPORAL_NAMESPACE", "default")
        self.task_queue = task_queue or os.getenv(
            "TEMPORAL_TASK_QUEUE", "project-ai-tasks"
        )
        self._client: Client | None = None

    async def connect(self) -> Client:
        """
        Connect to Temporal server.

        Returns:
            Connected Temporal client instance

        Raises:
            ConnectionError: If unable to connect to Temporal server
        """
        if self._client is not None:
            return self._client

        try:
            logger.info("Connecting to Temporal at %s, namespace=%s", self.host, self.namespace)
            self._client = await Client.connect(
                self.host,
                namespace=self.namespace,
            )
            logger.info("Successfully connected to Temporal server")
            return self._client

        except Exception as e:
            logger.error("Failed to connect to Temporal: %s", e)
            raise ConnectionError(f"Could not connect to Temporal server: {e}") from e

    async def start_workflow(
        self,
        workflow: Any,
        args: Any,
        workflow_id: str,
        task_queue: str | None = None,
    ) -> Any:
        """
        Start a Temporal workflow.

        Args:
            workflow: The workflow class or function to execute
            args: Arguments to pass to the workflow
            workflow_id: Unique identifier for this workflow execution
            task_queue: Task queue to use (default: self.task_queue)

        Returns:
            Workflow handle that can be used to query workflow state

        Example:
            >>> from integrations.temporal.workflows.example_workflow import ExampleWorkflow
            >>> handle = await client.start_workflow(
            ...     workflow=ExampleWorkflow.run,
            ...     args={"input": "test"},
            ...     workflow_id="example-123"
            ... )
            >>> result = await handle.result()
        """
        if self._client is None:
            await self.connect()

        task_queue = task_queue or self.task_queue

        try:
            logger.info("Starting workflow %s on queue %s", workflow_id, task_queue)
            handle = await self._client.start_workflow(
                workflow,
                args,
                id=workflow_id,
                task_queue=task_queue,
            )
            logger.info("Workflow %s started successfully", workflow_id)
            return handle

        except Exception as e:
            logger.error("Failed to start workflow %s: %s", workflow_id, e)
            raise

    async def close(self) -> None:
        """Close the Temporal client connection."""
        if self._client is not None:
            logger.info("Closing Temporal client connection")
            # Temporal client doesn't need explicit close in Python SDK
            self._client = None

    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
