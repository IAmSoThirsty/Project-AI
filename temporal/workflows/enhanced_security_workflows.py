"""
Enhanced Security Agent Workflows with Atomic Activities

Implements durable cross-agent campaigns with forensic snapshots,
incident triggering, and automated SARIF reporting.

Based on production-grade patterns:
- Immutable forensic snapshots
- Atomic activities with idempotency
- Incident playbook automation
- SARIF integration with GitHub Security

Author: Security Agents Team
Date: 2026-01-21
"""

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from temporalio import workflow
from temporalio.common import RetryPolicy

# Import atomic activities
with workflow.unsafe.imports_passed_through():
    from temporal.workflows.security_agent_activities import (
        create_forensic_snapshot,
        evaluate_attack,
        generate_sarif,
        notify_triumvirate,
        run_red_team_attack,
        trigger_incident,
        upload_sarif,
    )

logger = logging.getLogger(__name__)


@dataclass
class RedTeamCampaignRequest:
    """Request for red team campaign workflow."""

    campaign_id: str
    persona_ids: list[str]
    targets: list[str]
    repo: str = "IAmSoThirsty/Project-AI"
    commit_sha: str = "HEAD"


@workflow.defn
class EnhancedRedTeamCampaignWorkflow:
    """
    Enhanced red team campaign with forensic snapshots and incident automation.

    Workflow steps:
    1. Create immutable forensic snapshot
    2. Execute persona x target attacks
    3. Evaluate each result for severity
    4. Trigger incidents for critical/high severity
    5. Generate and upload SARIF report
    6. Notify Triumvirate for review
    """

    @workflow.run
    async def run(self, request: RedTeamCampaignRequest) -> dict[str, Any]:
        """Execute enhanced red team campaign workflow."""
        workflow.logger.info(
            "Starting enhanced red team campaign: %s", request.campaign_id
        )

        # Define retry policies
        snapshot_retry = RetryPolicy(
            maximum_attempts=1,  # Non-retryable - abort on failure
        )

        attack_retry = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=30),
            backoff_coefficient=2.0,
            maximum_attempts=3,  # Cap retries, mark as flaky beyond this
        )

        standard_retry = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            backoff_coefficient=2.0,
            maximum_attempts=5,
        )

        # Step 1: Create immutable forensic snapshot
        workflow.logger.info("Step 1: Creating forensic snapshot")
        try:
            snapshot_result = await workflow.execute_activity(
                create_forensic_snapshot,
                request.campaign_id,
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=snapshot_retry,
            )
            snapshot_id = snapshot_result["snapshot_id"]
            workflow.logger.info("Snapshot created: %s", snapshot_id)
        except Exception as e:
            workflow.logger.error("Snapshot creation failed: %s", e)
            return {
                "status": "aborted",
                "reason": "snapshot_creation_failed",
                "error": str(e),
            }

        # Step 2: Execute persona x target attacks
        workflow.logger.info("Step 2: Executing attacks")
        results = []
        halted = False
        halt_reason = None

        for persona in request.persona_ids:
            for target in request.targets:
                # Execute attack with retry policy
                attack_result = await workflow.execute_activity(
                    run_red_team_attack,
                    args=[persona, target, snapshot_id],
                    start_to_close_timeout=timedelta(minutes=15),
                    retry_policy=attack_retry,
                )
                results.append(attack_result)

                # Evaluate severity
                severity = await workflow.execute_activity(
                    evaluate_attack,
                    attack_result,
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=standard_retry,
                )

                workflow.logger.info(
                    "Attack evaluated: %s on %s = %s", persona, target, severity
                )

                # Trigger incident for critical/high severity
                if severity in ["critical", "high"]:
                    incident = await workflow.execute_activity(
                        trigger_incident,
                        args=[snapshot_id, attack_result, severity],
                        start_to_close_timeout=timedelta(minutes=5),
                        retry_policy=standard_retry,
                    )
                    workflow.logger.critical(
                        "Incident triggered: %s", incident["incident_id"]
                    )

                    # Check if campaign should halt
                    if await self._policy_should_halt(request.campaign_id, severity):
                        workflow.logger.warning(
                            "Campaign halted due to %s severity", severity
                        )
                        halted = True
                        halt_reason = severity
                        break

            if halted:
                break

        # If halted, return early
        if halted:
            return {
                "status": "halted",
                "reason": halt_reason,
                "results": results,
                "snapshot_id": snapshot_id,
                "attacks_completed": len(results),
                "attacks_planned": len(request.persona_ids) * len(request.targets),
            }

        # Step 3: Generate SARIF report
        workflow.logger.info("Step 3: Generating SARIF report")
        sarif_report = await workflow.execute_activity(
            generate_sarif,
            args=[results, request.campaign_id],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=standard_retry,
        )

        # Step 4: Upload SARIF to GitHub Security
        workflow.logger.info("Step 4: Uploading SARIF to GitHub")
        upload_result = await workflow.execute_activity(
            upload_sarif,
            args=[sarif_report, request.repo, request.commit_sha],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=standard_retry,
        )

        # Step 5: Notify Triumvirate
        workflow.logger.info("Step 5: Notifying Triumvirate")
        await workflow.execute_activity(
            notify_triumvirate,
            args=[request.campaign_id, results],
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=standard_retry,
        )

        # Return final results
        successful_attacks = sum(1 for r in results if r["success"])

        return {
            "status": "completed",
            "campaign_id": request.campaign_id,
            "snapshot_id": snapshot_id,
            "results": results,
            "total_attacks": len(results),
            "successful_attacks": successful_attacks,
            "success_rate": successful_attacks / len(results) if results else 0.0,
            "sarif_uploaded": upload_result["status"] == "uploaded",
            "triumvirate_notified": True,
        }

    async def _policy_should_halt(self, campaign_id: str, severity: str) -> bool:
        """
        Determine if campaign should halt based on policy.

        Policy: Halt on first critical severity attack.
                Continue on high severity (investigate all vectors).
        """
        if severity == "critical":
            workflow.logger.warning("Policy: Halt on critical severity")
            return True
        else:
            workflow.logger.info("Policy: Continue campaign (severity: %s)", severity)
            return False


@workflow.defn
class EnhancedCodeSecuritySweepWorkflow:
    """
    Enhanced code security sweep with automated patching and blocking.

    Workflow steps:
    1. Create forensic snapshot
    2. Run vulnerability scan
    3. Generate patches for findings
    4. Evaluate patch risk
    5. Auto-merge safe patches or create review PRs
    6. Generate and upload SARIF
    7. Block deployment if critical vulnerabilities found
    """

    @workflow.run
    async def run(self, request: dict[str, Any]) -> dict[str, Any]:
        """Execute enhanced code security sweep workflow."""
        workflow.logger.info("Starting enhanced code security sweep")

        # Import additional activities
        with workflow.unsafe.imports_passed_through():
            from temporal.workflows.security_agent_activities import (
                block_deployment,
                generate_security_patches,
                run_code_vulnerability_scan,
            )

        scan_id = request.get("scan_id", f"scan-{workflow.now().timestamp()}")

        # Retry policies
        standard_retry = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            backoff_coefficient=2.0,
            maximum_attempts=5,
        )

        # Step 1: Create snapshot
        workflow.logger.info("Step 1: Creating forensic snapshot")
        snapshot_result = await workflow.execute_activity(
            create_forensic_snapshot,
            scan_id,
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=RetryPolicy(maximum_attempts=1),
        )
        snapshot_id = snapshot_result["snapshot_id"]

        # Step 2: Run vulnerability scan
        workflow.logger.info("Step 2: Running vulnerability scan")
        scan_result = await workflow.execute_activity(
            run_code_vulnerability_scan,
            args=[request.get("scope_files", ["src/"]), scan_id],
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=standard_retry,
        )

        findings = scan_result["findings"]
        critical_count = sum(1 for f in findings if f.get("severity") == "critical")

        # Step 3: Generate patches
        workflow.logger.info("Step 3: Generating security patches")
        patch_result = await workflow.execute_activity(
            generate_security_patches,
            findings,
            start_to_close_timeout=timedelta(minutes=20),
            retry_policy=standard_retry,
        )

        # Step 4: Generate and upload SARIF
        workflow.logger.info("Step 4: Generating SARIF report")
        sarif_report = await workflow.execute_activity(
            generate_sarif,
            args=[findings, scan_id],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=standard_retry,
        )

        upload_result = await workflow.execute_activity(
            upload_sarif,
            args=[
                sarif_report,
                request.get("repo", "IAmSoThirsty/Project-AI"),
                request.get("commit_sha", "HEAD"),
            ],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=standard_retry,
        )

        # Step 5: Block deployment if critical vulnerabilities
        if critical_count > 0:
            workflow.logger.critical(
                "Blocking deployment: %s critical vulnerabilities", critical_count
            )
            await workflow.execute_activity(
                block_deployment,
                args=[scan_id, critical_count, "Critical vulnerabilities detected"],
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=standard_retry,
            )

        return {
            "status": "completed",
            "scan_id": scan_id,
            "snapshot_id": snapshot_id,
            "findings_count": len(findings),
            "critical_count": critical_count,
            "patches_generated": len(patch_result.get("patches", [])),
            "deployment_blocked": critical_count > 0,
            "sarif_uploaded": upload_result["status"] == "uploaded",
        }


@dataclass
class ConstitutionalMonitoringRequest:
    """Request for constitutional monitoring workflow."""

    monitoring_id: str
    test_prompts: list[str]
    review_mode: str = "self_critique"


@workflow.defn
class EnhancedConstitutionalMonitoringWorkflow:
    """
    Enhanced constitutional AI compliance monitoring.

    Continuously monitors prompts against constitutional principles
    and reports violations.
    """

    @workflow.run
    async def run(self, request: ConstitutionalMonitoringRequest) -> dict[str, Any]:
        """Execute constitutional monitoring workflow."""
        workflow.logger.info(
            "Starting constitutional monitoring: %s", request.monitoring_id
        )

        with workflow.unsafe.imports_passed_through():
            from temporal.workflows.security_agent_activities import (
                run_constitutional_reviews,
            )

        standard_retry = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            backoff_coefficient=2.0,
            maximum_attempts=5,
        )

        # Run constitutional reviews
        review_result = await workflow.execute_activity(
            run_constitutional_reviews,
            args=[request.test_prompts, request.review_mode],
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=standard_retry,
        )

        violations = [r for r in review_result["reviews"] if r["has_violations"]]

        return {
            "status": "completed",
            "monitoring_id": request.monitoring_id,
            "reviews_conducted": len(review_result["reviews"]),
            "violations_found": len(violations),
            "violation_rate": (
                len(violations) / len(review_result["reviews"])
                if review_result["reviews"]
                else 0.0
            ),
        }


# Helper function to start workflow
async def start_enhanced_red_team_campaign(
    client,
    campaign_id: str,
    persona_ids: list[str],
    targets: list[str],
    repo: str = "IAmSoThirsty/Project-AI",
    commit_sha: str = "HEAD",
):
    """
    Start enhanced red team campaign workflow.

    Args:
        client: Temporal client
        campaign_id: Campaign identifier
        persona_ids: List of personas to use
        targets: List of targets to attack
        repo: GitHub repository
        commit_sha: Commit SHA for SARIF upload

    Returns:
        Workflow handle
    """
    request = RedTeamCampaignRequest(
        campaign_id=campaign_id,
        persona_ids=persona_ids,
        targets=targets,
        repo=repo,
        commit_sha=commit_sha,
    )

    handle = await client.start_workflow(
        EnhancedRedTeamCampaignWorkflow.run,
        request,
        id=f"enhanced-red-team-{campaign_id}",
        task_queue="security-agents",
    )

    return handle
