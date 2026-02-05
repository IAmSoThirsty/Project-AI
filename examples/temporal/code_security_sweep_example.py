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

    logger.info(f"✅ Workflow started: {handle.id}")
    logger.info(
        f"🔗 View in UI: http://localhost:8233/namespaces/default/workflows/{handle.id}"
    )

    # Wait for result
    logger.info("⏳ Scanning codebase...")
    result = await handle.result()

    # Display results
    logger.info("📊 Scan Results:")
    logger.info(f"   • Total findings: {result.total_findings}")

    if result.by_severity:
        logger.info("   • By severity:")
        for severity, count in result.by_severity.items():
            if count > 0:
                logger.info(f"     - {severity.upper()}: {count}")

    if result.findings:
        logger.info("\n📝 First 5 findings:")
        for i, finding in enumerate(result.findings[:5], 1):
            logger.info(f"\n   {i}. {finding.get('title', 'Unknown')}")
            logger.info(f"      Severity: {finding.get('severity', 'N/A')}")
            logger.info(
                f"      File: {finding.get('file_path', 'N/A')}:{finding.get('line_number', '?')}"
            )
            logger.info(f"      Code: {finding.get('code_snippet', 'N/A')[:60]}...")
            logger.info(f"      Fix: {finding.get('recommendation', 'N/A')}")

    if result.patches:
        logger.info(f"\n🔧 Generated {len(result.patches)} patches")

    if result.sarif_path:
        logger.info(f"\n📄 SARIF report: {result.sarif_path}")
        logger.info(
            f"   Upload to GitHub: gh api repos/{{owner}}/{{repo}}/code-scanning/sarifs -F sarif=@{result.sarif_path}"
        )

    # Check for critical vulnerabilities
    critical_count = result.by_severity.get("critical", 0)
    if critical_count > 0:
        logger.error(f"\n❌ CRITICAL: {critical_count} critical vulnerabilities found!")
        logger.error("   Deployment should be blocked until these are resolved.")
        sys.exit(1)
    else:
        logger.info("\n✅ No critical vulnerabilities found")

    return result


if __name__ == "__main__":
    try:
        asyncio.run(run_code_sweep())
    except Exception as e:
        logger.error(f"❌ Sweep failed: {e}", exc_info=True)
        sys.exit(1)
