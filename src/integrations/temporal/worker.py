"""
Temporal Worker Entrypoint.

This module provides the worker that executes Temporal workflows and activities.
Run this script to start a worker process.

Usage:
    python -m integrations.temporal.worker
"""

import asyncio
import logging
import os
import sys

from temporalio.client import Client
from temporalio.worker import Worker

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from integrations.temporal.activities.core_tasks import (process_ai_task,
                                                         simulate_ai_call,
                                                         validate_input)
from integrations.temporal.workflows.example_workflow import ExampleWorkflow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def run_worker():
    """
    Start a Temporal worker to process workflows and activities.

    The worker connects to the Temporal server and polls for work on the
    configured task queue. When workflows or activities are scheduled,
    they are executed by this worker.
    """
    # Get configuration from environment
    host = os.getenv("TEMPORAL_HOST", "localhost:7233")
    namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
    task_queue = os.getenv("TEMPORAL_TASK_QUEUE", "project-ai-tasks")

    logger.info(f"Starting Temporal worker for queue: {task_queue}")
    logger.info(f"Connecting to Temporal at: {host}")

    try:
        # Connect to Temporal server
        client = await Client.connect(host, namespace=namespace)
        logger.info("Successfully connected to Temporal server")

        # Create worker with workflows and activities
        worker = Worker(
            client,
            task_queue=task_queue,
            workflows=[ExampleWorkflow],
            activities=[
                validate_input,
                simulate_ai_call,
                process_ai_task,
            ],
        )

        logger.info("Worker registered with workflows and activities")
        logger.info("Available workflows: ExampleWorkflow")
        logger.info(
            "Available activities: validate_input, simulate_ai_call, process_ai_task"
        )
        logger.info("Worker is ready to process tasks...")

        # Run the worker (blocks until interrupted)
        await worker.run()

    except KeyboardInterrupt:
        logger.info("Worker shutdown requested")
    except Exception as e:
        logger.error(f"Worker error: {e}", exc_info=True)
        raise


def main():
    """Main entry point for the worker."""
    try:
        asyncio.run(run_worker())
    except KeyboardInterrupt:
        logger.info("Worker stopped")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
