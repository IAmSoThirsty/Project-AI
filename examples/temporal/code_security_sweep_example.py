#!/usr/bin/env python3
"""
Example: Run code security sweep workflow.

Scans codebase for vulnerabilities and generates reports.
"""

import asyncio
import logging
import sys
from datetime import timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from temporalio.client import Client

from temporal.workflows.security_agent_workflows import (
    CodeSecuritySweepRequest,
    CodeSecuritySweepWorkflow,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_code_sweep():
    """Run code security sweep."""
    logger.info("🔍 Starting code security sweep")

    # Connect to Temporal
    client = await Client.connect("localhost:7233")

    # Create request
    request = CodeSecuritySweepRequest(
        repo_path=".",
        scope_dirs=[
            "src/app/core",
            "src/app/agents",
            "src/app/security",
            "temporal/workflows",
        ],
        generate_patches=True,
        create_sarif=True,
        severity_threshold="medium",
        timeout_seconds=1800,
    )

    # Start workflow
    handle = await client.start_workflow(
        CodeSecuritySweepWorkflow.run,
        request,
        id=f"code-security-sweep-{asyncio.get_event_loop().time()}",
        task_queue="security-agents",
        execution_timeout=timedelta(minutes=45),
    )

    logger.info("✅ Workflow started: %s", handle.id)
    logger.info(
        "🔗 View in UI: http://localhost:8233/namespaces/default/workflows/%s",
        handle.id,
    )

    # Wait for result
    logger.info("⏳ Scanning codebase...")
    result = await handle.result()

    # Display results
    logger.info("📊 Scan Results:")
    logger.info("   • Total findings: %s", result.total_findings)

    if result.by_severity:
        logger.info("   • By severity:")
        for severity, count in result.by_severity.items():
            if count > 0:
                logger.info("     - %s: %s", severity.upper(), count)

    if result.findings:
        logger.info("\n📝 First 5 findings:")
        for i, finding in enumerate(result.findings[:5], 1):
            logger.info("\n   %s. %s", i, finding.get("title", "Unknown"))
            logger.info("      Severity: %s", finding.get("severity", "N/A"))
            logger.info(
                "      File: %s:%s",
                finding.get("file_path", "N/A"),
                finding.get("line_number", "?"),
            )
            logger.info("      Code: %s...", finding.get("code_snippet", "N/A")[:100])
            logger.info("      Fix: %s", finding.get("recommendation", "N/A"))

    if result.patches:
        logger.info("\n🔧 Generated %s patches", len(result.patches))

    if result.sarif_path:
        logger.info("\n📄 SARIF report: %s", result.sarif_path)
        logger.info(
            "   Upload to GitHub: gh api repos/{owner}/{repo}/code-scanning/sarifs -F sarif=@%s",
            result.sarif_path,
        )

    # Check for critical vulnerabilities
    critical_count = result.by_severity.get("critical", 0)
    if critical_count > 0:
        logger.error(
            "\n❌ CRITICAL: %s critical vulnerabilities found!", critical_count
        )
        logger.error("   Deployment should be blocked until these are resolved.")
        sys.exit(1)
    else:
        logger.info("\n✅ No critical vulnerabilities found")

    return result


if __name__ == "__main__":
    try:
        asyncio.run(run_code_sweep())
    except Exception as e:
        logger.error("❌ Sweep failed: %s", e, exc_info=True)
        sys.exit(1)
