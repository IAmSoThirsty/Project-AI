"""
Temporal Worker for Project-AI.

Starts a worker that processes workflows and activities for the Project-AI application.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.temporal.activities import (
    crisis_activities,
    data_activities,
    image_activities,
    learning_activities,
    memory_activities,
)
from app.temporal.client import TemporalClientManager
from app.temporal.workflows import (
    AILearningWorkflow,
    CrisisResponseWorkflow,
    DataAnalysisWorkflow,
    ImageGenerationWorkflow,
    MemoryExpansionWorkflow,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """
    Main worker entry point.

    Connects to Temporal server, registers workflows and activities,
    and starts processing tasks.
    """
    logger.info("Starting Project-AI Temporal Worker")

    # Create client manager
    manager = TemporalClientManager()

    # Handle graceful shutdown
    shutdown_event = asyncio.Event()

    def signal_handler(signum, frame):
        logger.info("Received signal %s, initiating shutdown", signum)
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Connect to Temporal server
        await manager.connect()
        logger.info("Connected to Temporal server")

        # Collect all workflows and activities
        workflows = [
            AILearningWorkflow,
            ImageGenerationWorkflow,
            DataAnalysisWorkflow,
            MemoryExpansionWorkflow,
            CrisisResponseWorkflow,
        ]

        activities = learning_activities + image_activities + data_activities + memory_activities + crisis_activities

        # Create worker
        worker = manager.create_worker(
            workflows=workflows,
            activities=activities,
            max_concurrent_activities=50,
            max_concurrent_workflow_tasks=50,
        )

        logger.info(f"Worker created with {len(workflows)} workflows " f"and {len(activities)} activities")

        # Run worker
        logger.info("Worker is running. Press Ctrl+C to stop.")

        # Run worker in background
        worker_task = asyncio.create_task(manager.run_worker(worker))

        # Wait for shutdown signal
        await shutdown_event.wait()

        # Cancel worker
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            logger.info("Worker stopped")

    except Exception as e:
        logger.error("Worker error: %s", e)
        return 1
    finally:
        # Cleanup
        await manager.disconnect()
        logger.info("Worker shutdown complete")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
