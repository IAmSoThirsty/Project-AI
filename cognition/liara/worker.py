"""
Liara Temporal Agency Worker.

Dedicated worker process for Liara crisis response and agent mission
orchestration workflows.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.temporal.activities import crisis_activities
from app.temporal.client import TemporalClientManager
from app.temporal.workflows import CrisisResponseWorkflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """
    Liara worker entry point.

    Connects to Temporal server and processes crisis response workflows.
    """
    logger.info("Starting Liara Temporal Agency Worker")

    # Create client manager
    manager = TemporalClientManager(task_queue="liara-crisis-tasks")

    # Handle graceful shutdown
    shutdown_event = asyncio.Event()

    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating shutdown")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Connect to Temporal server
        await manager.connect()
        logger.info("Connected to Temporal server")

        # Register crisis response workflows and activities
        workflows = [CrisisResponseWorkflow]
        activities = crisis_activities

        # Create worker
        worker = manager.create_worker(
            workflows=workflows,
            activities=activities,
            max_concurrent_activities=20,
            max_concurrent_workflow_tasks=10,
        )

        logger.info(
            f"Liara worker created with {len(workflows)} workflows "
            f"and {len(activities)} activities"
        )
        logger.info("Task queue: liara-crisis-tasks")

        # Run worker
        logger.info("Liara worker is running. Press Ctrl+C to stop.")

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
        logger.error(f"Worker error: {e}", exc_info=True)
        return 1
    finally:
        # Cleanup
        await manager.disconnect()
        logger.info("Liara worker shutdown complete")

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
