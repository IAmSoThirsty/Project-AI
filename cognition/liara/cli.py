#!/usr/bin/env python3
"""
Liara CLI - Crisis Response Management Tool.

Command-line interface for triggering and monitoring crisis response workflows.

Usage:
    python cognition/liara/cli.py trigger <target> <mission1> <mission2> ...
    python cognition/liara/cli.py status <workflow_id>
    python cognition/liara/cli.py wait <workflow_id>

Examples:
    # Trigger crisis response
    python cognition/liara/cli.py trigger target-alpha recon secure extract

    # Check workflow status
    python cognition/liara/cli.py status crisis-workflow-crisis-target-alpha-1234567890

    # Wait for workflow completion
    python cognition/liara/cli.py wait crisis-workflow-crisis-target-alpha-1234567890
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cognition.liara.agency import LiaraTemporalAgency

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def trigger_crisis(target: str, mission_actions: list[str]):
    """
    Trigger a crisis response workflow.

    Args:
        target: Target member identifier
        mission_actions: List of action names for mission phases
    """
    logger.info("Triggering crisis response for target: %s", target)

    # Build mission list from action names
    missions = []
    for idx, action in enumerate(mission_actions, start=1):
        missions.append(
            {
                "phase_id": f"phase-{idx}",
                "agent_id": f"agent-{action}-{idx:03d}",
                "action": action,
                "target": target,
                "priority": idx,
            }
        )

    logger.info("Configured %s mission phases", len(missions))

    async with LiaraTemporalAgency() as agency:
        workflow_id = await agency.trigger_crisis_response(
            target_member=target,
            missions=missions,
            initiated_by="cli-user",
        )

        logger.info("✓ Crisis response workflow triggered")
        logger.info("  Workflow ID: %s", workflow_id)
        logger.info("  View in UI: http://localhost:8233/namespaces/default/workflows")
        return workflow_id


async def check_status(workflow_id: str):
    """
    Check status of a crisis response workflow.

    Args:
        workflow_id: Workflow ID to check
    """
    logger.info("Checking status of workflow: %s", workflow_id)

    async with LiaraTemporalAgency() as agency:
        status = await agency.get_crisis_status(workflow_id)

        logger.info("✓ Workflow status retrieved")
        logger.info("  Status: %s", status.get('status'))

        if status.get("status") == "completed":
            logger.info("  Success: %s", status.get('success'))
            logger.info("  Crisis ID: %s", status.get('crisis_id'))
            logger.info("  Completed phases: %s", status.get('completed_phases'))

            if status.get("failed_phases"):
                logger.warning("  Failed phases: %s", status.get('failed_phases'))

        return status


async def wait_for_completion(workflow_id: str):
    """
    Wait for workflow to complete and display results.

    Args:
        workflow_id: Workflow ID to wait for
    """
    logger.info("Waiting for workflow completion: %s", workflow_id)

    async with LiaraTemporalAgency() as agency:
        result = await agency.wait_for_crisis_completion(workflow_id)

        logger.info("\n%s", '='*60)
        logger.info("CRISIS RESPONSE COMPLETED")
        logger.info("%s", '='*60)
        logger.info("Success: %s", result['success'])
        logger.info("Crisis ID: %s", result['crisis_id'])
        logger.info("Completed phases: %s", result['completed_phases'])

        if result.get("failed_phases"):
            logger.warning("Failed phases: %s", result['failed_phases'])

        if result.get("error"):
            logger.error("Error: %s", result['error'])

        # Show persistent state location
        crisis_file = Path("data/crises") / f"{result['crisis_id']}.json"
        if crisis_file.exists():
            logger.info("\nPersistent state saved to: %s", crisis_file)

        return result


def print_usage():
    """Print usage information."""
    print(__doc__)


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == "trigger":
            if len(sys.argv) < 4:
                logger.error("Usage: trigger <target> <mission1> [mission2] ...")
                sys.exit(1)

            target = sys.argv[2]
            mission_actions = sys.argv[3:]

            workflow_id = asyncio.run(trigger_crisis(target, mission_actions))
            print(f"\nWorkflow ID: {workflow_id}")

        elif command == "status":
            if len(sys.argv) != 3:
                logger.error("Usage: status <workflow_id>")
                sys.exit(1)

            workflow_id = sys.argv[2]
            status = asyncio.run(check_status(workflow_id))
            print(f"\nStatus: {json.dumps(status, indent=2)}")

        elif command == "wait":
            if len(sys.argv) != 3:
                logger.error("Usage: wait <workflow_id>")
                sys.exit(1)

            workflow_id = sys.argv[2]
            result = asyncio.run(wait_for_completion(workflow_id))
            sys.exit(0 if result["success"] else 1)

        else:
            logger.error("Unknown command: %s", command)
            print_usage()
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
