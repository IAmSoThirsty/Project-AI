#!/usr/bin/env python3
"""
Example: Run red team campaign workflow.

Executes a red team campaign with multiple personas against target systems.
"""

import asyncio
import logging
import sys
from datetime import timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from temporalio.client import Client

from temporal.workflows.security_agent_workflows import (
    RedTeamCampaignRequest,
    RedTeamCampaignWorkflow,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_high_priority_campaign():
    """Run daily high-priority red team campaign."""
    logger.info("🚀 Starting high-priority red team campaign")

    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    # Create request
    request = RedTeamCampaignRequest(
        persona_ids=[
            "jailbreak_attacker",
            "data_exfiltrator",
            "instruction_hijacker",
        ],
        targets=[
            {
                "name": "Production API",
                "endpoint": "https://api.production.example.com",
            },
            {
                "name": "Admin Interface",
                "endpoint": "https://admin.production.example.com",
            },
        ],
        max_turns_per_attack=10,
        timeout_seconds=3600,
        severity_threshold="high",
    )

    # Start workflow
    handle = await client.start_workflow(
        RedTeamCampaignWorkflow.run,
        request,
        id=f"red-team-campaign-high-priority-{asyncio.get_event_loop().time()}",
        task_queue="security-agents",
        execution_timeout=timedelta(hours=2),
    )

    logger.info("✅ Workflow started: %s", handle.id)
    logger.info(
        "🔗 View in UI: http://localhost:8233/namespaces/default/workflows/%s",
        handle.id,
    )

    # Wait for result
    logger.info("⏳ Waiting for campaign to complete...")
    result = await handle.result()

    # Display results
    logger.info("📊 Campaign Results:")
    logger.info("   • Total attacks: %s", result.total_attacks)
    logger.info("   • Successful: %s", result.successful_attacks)
    logger.info("   • Failed: %s", result.failed_attacks)
    logger.info("   • Vulnerabilities found: %s", len(result.vulnerabilities_found))

    if result.vulnerabilities_found:
        logger.warning("⚠️ VULNERABILITIES DETECTED:")
        for vuln in result.vulnerabilities_found:
            logger.warning(
                "   • %s: %s -> %s",
                vuln.get("severity", "unknown").upper(),
                vuln.get("persona"),
                vuln.get("target"),
            )
            logger.warning("     Details: %s", vuln.get("details", "N/A"))

    return result


async def run_comprehensive_campaign():
    """Run weekly comprehensive red team campaign."""
    logger.info("🚀 Starting comprehensive red team campaign")

    client = await Client.connect("localhost:7233")

    # All personas, all targets
    request = RedTeamCampaignRequest(
        persona_ids=[
            "jailbreak_attacker",
            "data_exfiltrator",
            "social_engineer",
            "logic_manipulator",
            "privacy_prober",
            "resource_exhaustion",
            "instruction_hijacker",
        ],
        targets=[
            {"name": "Production API", "endpoint": "prod-api"},
            {"name": "Staging API", "endpoint": "staging-api"},
            {"name": "Admin Interface", "endpoint": "admin"},
            {"name": "User Portal", "endpoint": "portal"},
        ],
        max_turns_per_attack=12,
        timeout_seconds=7200,  # 2 hours
        severity_threshold="low",  # Test all personas
    )

    handle = await client.start_workflow(
        RedTeamCampaignWorkflow.run,
        request,
        id=f"red-team-campaign-comprehensive-{asyncio.get_event_loop().time()}",
        task_queue="security-agents",
        execution_timeout=timedelta(hours=4),
    )

    logger.info("✅ Workflow started: %s", handle.id)
    logger.info(
        "🔗 View in UI: http://localhost:8233/namespaces/default/workflows/%s",
        handle.id,
    )

    # Don't wait for result - this is a long-running campaign
    logger.info("⏳ Campaign running in background...")
    logger.info(
        "   Query result with: temporal workflow describe --workflow-id %s", handle.id
    )

    return handle


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run red team campaign")
    parser.add_argument(
        "--type",
        choices=["high-priority", "comprehensive"],
        default="high-priority",
        help="Campaign type",
    )
    args = parser.parse_args()

    if args.type == "high-priority":
        asyncio.run(run_high_priority_campaign())
    else:
        asyncio.run(run_comprehensive_campaign())
