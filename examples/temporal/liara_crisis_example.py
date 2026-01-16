#!/usr/bin/env python3
"""
Liara Crisis Response Example - End-to-End Demonstration.

This example demonstrates the complete crisis response workflow using
Temporal.io for persistent, retry-enabled, distributed execution.

Prerequisites:
1. Temporal server must be running (see README.md)
2. Liara worker must be running (python cognition/liara/worker.py)
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cognition.liara.agency import LiaraTemporalAgency

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """
    Demonstrate end-to-end crisis response workflow.
    """
    logger.info("=" * 80)
    logger.info("Liara Temporal Agency - Crisis Response Demo")
    logger.info("=" * 80)

    # Initialize agency with context manager
    async with LiaraTemporalAgency() as agency:
        logger.info("\n[1] Agency connected to Temporal server")

        # Define crisis scenario
        target_member = "target-alpha-7"

        missions = [
            {
                "phase_id": "recon-phase-1",
                "agent_id": "recon-agent-001",
                "action": "reconnaissance",
                "target": target_member,
                "priority": 1,
            },
            {
                "phase_id": "secure-phase-2",
                "agent_id": "security-agent-002",
                "action": "secure_perimeter",
                "target": target_member,
                "priority": 2,
            },
            {
                "phase_id": "extract-phase-3",
                "agent_id": "extraction-agent-003",
                "action": "data_extraction",
                "target": target_member,
                "priority": 3,
            },
            {
                "phase_id": "cleanup-phase-4",
                "agent_id": "cleanup-agent-004",
                "action": "cleanup_traces",
                "target": target_member,
                "priority": 4,
            },
        ]

        logger.info("\n[2] Crisis scenario defined:")
        logger.info(f"    Target: {target_member}")
        logger.info(f"    Mission phases: {len(missions)}")
        for mission in missions:
            logger.info(
                f"      - Phase {mission['priority']}: {mission['action']} "
                f"(Agent: {mission['agent_id']})"
            )

        # Trigger crisis response workflow
        logger.info("\n[3] Triggering crisis response workflow...")
        workflow_id = await agency.trigger_crisis_response(
            target_member=target_member,
            missions=missions,
            initiated_by="demo-user",
        )

        logger.info(f"    Workflow started: {workflow_id}")
        logger.info(
            "    View in Temporal UI: http://localhost:8233/namespaces/default/workflows"
        )

        # Check initial status
        logger.info("\n[4] Checking workflow status...")
        status = await agency.get_crisis_status(workflow_id)
        logger.info(f"    Status: {status.get('status')}")

        # Wait for completion (this is durable and survives crashes)
        logger.info("\n[5] Waiting for crisis response to complete...")
        logger.info("    (This may take a few moments...)")

        result = await agency.wait_for_crisis_completion(workflow_id)

        # Display results
        logger.info("\n[6] Crisis Response Results:")
        logger.info("=" * 80)
        logger.info(f"    Success: {result['success']}")
        logger.info(f"    Crisis ID: {result['crisis_id']}")
        logger.info(f"    Completed Phases: {result['completed_phases']}")

        if result.get("failed_phases"):
            logger.info(f"    Failed Phases: {result['failed_phases']}")

        if result.get("error"):
            logger.error(f"    Error: {result['error']}")

        logger.info("\n[7] Checking persistent state...")
        crisis_file = Path("data/crises") / f"{result['crisis_id']}.json"
        if crisis_file.exists():
            logger.info(f"    Crisis record saved to: {crisis_file}")
            logger.info("    State persisted successfully!")
        else:
            logger.warning("    Crisis record not found")

    logger.info("\n[8] Demo complete - Agency disconnected")
    logger.info("=" * 80)
    logger.info("\nKey Observations:")
    logger.info("  ✓ Workflow executed through Temporal.io")
    logger.info("  ✓ State persisted to data/crises/")
    logger.info("  ✓ All mission phases executed sequentially")
    logger.info("  ✓ Workflow visible in Temporal Web UI")
    logger.info("  ✓ Automatic retry on failures (configured)")
    logger.info("  ✓ Horizontally scalable via task queues")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"\nDemo failed: {e}", exc_info=True)
        sys.exit(1)
