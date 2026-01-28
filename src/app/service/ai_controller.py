"""
AI Controller Service.

This service integrates the Temporal workflow orchestration into the main
application, providing a high-level interface for starting and managing
AI workflows.
"""

import asyncio
import logging
from typing import Any

from integrations.temporal.client import TemporalClient
from integrations.temporal.workflows.example_workflow import (ExampleWorkflow,
                                                              WorkflowInput,
                                                              WorkflowOutput)

logger = logging.getLogger(__name__)


class AIController:
    """
    Main controller for AI operations using Temporal workflows.

    This controller provides a clean interface for the application to start
    and manage Temporal workflows without directly dealing with Temporal internals.

    Example:
        >>> controller = AIController()
        >>> result = await controller.process_ai_request(
        ...     data="Explain machine learning",
        ...     user_id="user123"
        ... )
        >>> print(result.success)
        True
    """

    def __init__(self, temporal_client: TemporalClient | None = None):
        """
        Initialize the AI controller.

        Args:
            temporal_client: Optional Temporal client instance.
                           If not provided, a new one will be created.
        """
        self.temporal_client = temporal_client or TemporalClient()
        self._connected = False

    async def connect(self) -> None:
        """Ensure connection to Temporal server."""
        if not self._connected:
            await self.temporal_client.connect()
            self._connected = True
            logger.info("AI Controller connected to Temporal")

    async def process_ai_request(
        self,
        data: str,
        user_id: str | None = None,
        options: dict | None = None,
        workflow_id: str | None = None,
    ) -> WorkflowOutput:
        """
        Process an AI request using a Temporal workflow.

        This method starts an ExampleWorkflow to process the request in a
        durable, fault-tolerant manner. The workflow will:
        1. Validate the input
        2. Call the AI system
        3. Process the results

        Args:
            data: Input data to process
            user_id: Optional user identifier
            options: Optional configuration options
            workflow_id: Optional workflow ID (auto-generated if not provided)

        Returns:
            WorkflowOutput containing the results

        Example:
            >>> controller = AIController()
            >>> result = await controller.process_ai_request(
            ...     data="What is quantum computing?",
            ...     user_id="user456"
            ... )
            >>> if result.success:
            ...     print(f"Result: {result.result}")
        """
        await self.connect()

        # Generate workflow ID if not provided
        if workflow_id is None:
            import uuid

            workflow_id = f"ai-request-{uuid.uuid4().hex[:8]}"

        # Prepare input
        workflow_input = WorkflowInput(
            data=data,
            user_id=user_id,
            options=options or {},
        )

        logger.info("Starting AI request workflow: %s", workflow_id)

        try:
            # Start the workflow
            handle = await self.temporal_client.start_workflow(
                workflow=ExampleWorkflow.run,
                args=workflow_input,
                workflow_id=workflow_id,
            )

            # Wait for workflow to complete and get result
            result = await handle.result()

            logger.info(
                f"Workflow {workflow_id} completed with success={result.success}"
            )
            return result

        except Exception as e:
            logger.error("Error processing AI request: %s", e)
            return WorkflowOutput(
                success=False,
                error=f"Failed to process request: {str(e)}",
                steps_completed=[],
            )

    async def get_workflow_status(self, workflow_id: str) -> dict[str, Any]:
        """
        Get the status of a running or completed workflow.

        Args:
            workflow_id: ID of the workflow to check

        Returns:
            Dictionary with workflow status information
        """
        await self.connect()

        try:
            handle = self.temporal_client._client.get_workflow_handle(workflow_id)

            # Try to get the current status
            description = await handle.describe()

            return {
                "workflow_id": workflow_id,
                "status": description.status.name,
                "start_time": (
                    description.start_time.isoformat()
                    if description.start_time
                    else None
                ),
                "execution_time": (
                    description.execution_time.isoformat()
                    if description.execution_time
                    else None
                ),
            }

        except Exception as e:
            logger.error("Error getting workflow status: %s", e)
            return {
                "workflow_id": workflow_id,
                "status": "UNKNOWN",
                "error": str(e),
            }

    async def close(self) -> None:
        """Close the Temporal connection."""
        if self._connected:
            await self.temporal_client.close()
            self._connected = False
            logger.info("AI Controller disconnected from Temporal")


# Convenience function for one-off requests
async def process_ai_request(
    data: str, user_id: str | None = None, options: dict | None = None
) -> WorkflowOutput:
    """
    Convenience function to process a single AI request.

    This is a simplified interface that handles connection lifecycle automatically.

    Args:
        data: Input data to process
        user_id: Optional user identifier
        options: Optional configuration options

    Returns:
        WorkflowOutput containing the results

    Example:
        >>> from app.service.ai_controller import process_ai_request
        >>> result = await process_ai_request("Explain neural networks")
        >>> print(result.result)
    """
    controller = AIController()
    try:
        return await controller.process_ai_request(data, user_id, options)
    finally:
        await controller.close()


# Example usage for testing
async def main():
    """Example usage of the AI controller."""
    print("=" * 60)
    print("AI Controller Example")
    print("=" * 60)

    controller = AIController()

    # Example 1: Simple request
    print("\n1. Processing simple AI request...")
    result = await controller.process_ai_request(
        data="Explain the concept of machine learning",
        user_id="demo_user",
    )

    print(f"   Success: {result.success}")
    if result.success:
        print(f"   Result: {result.result}")
        print(f"   Steps: {result.steps_completed}")
    else:
        print(f"   Error: {result.error}")

    # Example 2: Request with workflow ID
    print("\n2. Processing AI request with custom workflow ID...")
    result = await controller.process_ai_request(
        data="What are the applications of quantum computing?",
        user_id="demo_user",
        workflow_id="demo-workflow-123",
    )

    print(f"   Success: {result.success}")

    # Example 3: Check workflow status
    print("\n3. Checking workflow status...")
    status = await controller.get_workflow_status("demo-workflow-123")
    print(f"   Status: {status}")

    await controller.close()
    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
