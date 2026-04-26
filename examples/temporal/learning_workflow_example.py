#!/usr/bin/env python3
"""
Example: AI Learning Workflow with Temporal.io

This example demonstrates how to use the AILearningWorkflow to process
learning requests with durable execution.
"""

import asyncio
import logging
from datetime import datetime

from app.temporal.client import TemporalClientManager
from app.temporal.workflows import AILearningWorkflow, LearningRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Run AI learning workflow example."""
    logger.info("Starting AI Learning Workflow example")

    # Create and connect client
    manager = TemporalClientManager()
    await manager.connect()

    try:
        # Create learning request
        request = LearningRequest(
            content="""
            Python Error Handling Best Practices:
            1. Use specific exception types rather than bare except
            2. Always log exceptions with context
            3. Use context managers for resource cleanup
            4. Consider custom exceptions for domain-specific errors
            5. Use finally blocks for cleanup that must always run
            """,
            source="best_practices_guide",
            category="programming",
            user_id="example_user",
        )

        # Generate unique workflow ID
        workflow_id = f"learning-{datetime.now().timestamp()}"

        logger.info("Starting workflow: %s", workflow_id)

        # Start workflow
        handle = await manager.client.start_workflow(
            AILearningWorkflow.run,
            request,
            id=workflow_id,
            task_queue="project-ai-tasks",
        )

        logger.info("Workflow started, waiting for result...")

        # Wait for result (this is durable - survives crashes)
        result = await handle.result()

        if result.success:
            logger.info("✓ Learning successful!")
            logger.info("  Knowledge ID: %s", result.knowledge_id)
        else:
            logger.error("✗ Learning failed: %s", result.error)

    finally:
        await manager.disconnect()

    logger.info("Example complete")


if __name__ == "__main__":
    asyncio.run(main())
