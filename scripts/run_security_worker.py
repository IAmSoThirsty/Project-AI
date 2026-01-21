#!/usr/bin/env python3
"""
Temporal worker for security agent workflows.

Starts a worker that executes security agent workflows and activities.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

from temporalio.client import Client
from temporalio.worker import Worker

# Import workflows and activities
from temporal.workflows.security_agent_activities import (
    block_deployment,
    generate_sarif_report,
    generate_security_patches,
    run_code_vulnerability_scan,
    run_constitutional_reviews,
    run_red_team_campaign,
    run_safety_benchmark,
    trigger_incident_workflow,
    trigger_security_alert,
)
from temporal.workflows.security_agent_workflows import (
    CodeSecuritySweepWorkflow,
    ConstitutionalMonitoringWorkflow,
    RedTeamCampaignWorkflow,
    SafetyTestingWorkflow,
)

# Import shared activities
from temporal.workflows.activities import record_telemetry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class SecurityWorker:
    """Security agent Temporal worker."""

    def __init__(self, temporal_address: str = "localhost:7233", task_queue: str = "security-agents"):
        """Initialize security worker.

        Args:
            temporal_address: Temporal server address
            task_queue: Task queue name
        """
        self.temporal_address = temporal_address
        self.task_queue = task_queue
        self.worker = None
        self.client = None
        self.shutdown_event = asyncio.Event()

    async def start(self):
        """Start the worker."""
        try:
            # Connect to Temporal server
            logger.info(f"🔌 Connecting to Temporal server at {self.temporal_address}")
            self.client = await Client.connect(self.temporal_address)
            logger.info("✅ Connected to Temporal server")

            # Create worker
            logger.info(f"🛡️ Creating security agent worker on queue: {self.task_queue}")
            self.worker = Worker(
                self.client,
                task_queue=self.task_queue,
                workflows=[
                    RedTeamCampaignWorkflow,
                    CodeSecuritySweepWorkflow,
                    ConstitutionalMonitoringWorkflow,
                    SafetyTestingWorkflow,
                ],
                activities=[
                    # Security activities
                    run_red_team_campaign,
                    run_code_vulnerability_scan,
                    generate_security_patches,
                    generate_sarif_report,
                    run_constitutional_reviews,
                    run_safety_benchmark,
                    trigger_incident_workflow,
                    block_deployment,
                    trigger_security_alert,
                    # Shared activities
                    record_telemetry,
                ],
            )

            logger.info("✅ Worker created successfully")
            logger.info("📋 Registered workflows:")
            logger.info("   • RedTeamCampaignWorkflow")
            logger.info("   • CodeSecuritySweepWorkflow")
            logger.info("   • ConstitutionalMonitoringWorkflow")
            logger.info("   • SafetyTestingWorkflow")
            logger.info("📋 Registered activities: 10")

            # Run worker
            logger.info(f"🚀 Starting worker (task queue: {self.task_queue})")
            logger.info("Press Ctrl+C to stop")

            # Run worker until shutdown event is set
            await self.worker.run(self.shutdown_event.wait())

        except KeyboardInterrupt:
            logger.info("⚠️ Received interrupt signal")
        except Exception as e:
            logger.error(f"❌ Worker error: {e}", exc_info=True)
            raise
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Gracefully shutdown the worker."""
        logger.info("🛑 Shutting down worker...")

        if self.worker:
            self.shutdown_event.set()
            logger.info("✅ Worker shutdown complete")

        if self.client:
            # Note: Temporal client doesn't have an explicit close method
            pass

        logger.info("👋 Goodbye!")


def handle_signal(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}")
    # Let asyncio handle the shutdown
    raise KeyboardInterrupt()


async def main():
    """Main entry point."""
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Create and start worker
    worker = SecurityWorker()
    await worker.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
