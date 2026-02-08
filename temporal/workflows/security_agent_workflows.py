"""
Security Agent Temporal Workflows

Durable, scheduled workflows for security agent operations:
- Red team campaigns with typed personas
- Code security sweeps with vulnerability detection
- Constitutional guardrail monitoring
- Safety testing and jailbreak benchmarking

All workflows integrate with existing Temporal infrastructure.
"""

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from temporalio import workflow
from temporalio.common import RetryPolicy

logger = logging.getLogger(__name__)


# ============================================================================
# Request/Result Data Classes
# ============================================================================


@dataclass
class RedTeamCampaignRequest:
    """Request for red team campaign workflow."""

    persona_ids: list[str]  # List of persona IDs to test
    targets: list[dict[str, Any]]  # List of target systems with configs
    max_turns_per_attack: int = 10
    timeout_seconds: int = 3600  # 1 hour default
    severity_threshold: str = "high"  # Filter personas by severity


@dataclass
class RedTeamCampaignResult:
    """Result from red team campaign."""

    success: bool
    total_attacks: int
    successful_attacks: int
    failed_attacks: int
    sessions: list[dict[str, Any]]
    vulnerabilities_found: list[dict[str, Any]]
    error: str | None = None


@dataclass
class CodeSecuritySweepRequest:
    """Request for code security sweep workflow."""

    repo_path: str = "."
    scope_dirs: list[str] | None = None
    generate_patches: bool = True
    create_sarif: bool = True
    severity_threshold: str = "medium"
    timeout_seconds: int = 1800  # 30 minutes


@dataclass
class CodeSecuritySweepResult:
    """Result from code security sweep."""

    success: bool
    total_findings: int
    by_severity: dict[str, int]
    findings: list[dict[str, Any]]
    patches: list[dict[str, Any]] | None = None
    sarif_path: str | None = None
    error: str | None = None


@dataclass
class ConstitutionalMonitoringRequest:
    """Request for constitutional monitoring workflow."""

    target_endpoint: str  # Endpoint to monitor
    sample_prompts: list[str]  # Test prompts
    review_mode: str = "self_critique"
    timeout_seconds: int = 600


@dataclass
class ConstitutionalMonitoringResult:
    """Result from constitutional monitoring."""

    success: bool
    total_reviews: int
    violations_detected: int
    compliant_responses: int
    violation_details: list[dict[str, Any]]
    error: str | None = None


@dataclass
class SafetyTestingRequest:
    """Request for safety testing workflow."""

    test_dataset: str = "hydra"  # "hydra", "jbb", or "all"
    max_tests: int = 50
    target_system: str = "default"
    timeout_seconds: int = 1800


@dataclass
class SafetyTestingResult:
    """Result from safety testing."""

    success: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    test_results: list[dict[str, Any]]
    defense_rate: float
    error: str | None = None


# ============================================================================
# Workflow Definitions
# ============================================================================


@workflow.defn
class RedTeamCampaignWorkflow:
    """
    Durable workflow for running red team campaigns.

    Executes multiple persona-based attacks across target systems,
    logs results, and identifies vulnerabilities.

    Schedule: Daily for high-priority personas, weekly for comprehensive
    """

    @workflow.run
    async def run(self, request: RedTeamCampaignRequest) -> RedTeamCampaignResult:
        """Execute red team campaign workflow."""
        workflow.logger.info("Starting red team campaign with %s personas", len(request.persona_ids))

        try:
            # Configure retry policy
            retry_policy = RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_interval=timedelta(seconds=60),
                backoff_coefficient=2.0,
                maximum_attempts=3,
            )

            # Record workflow start
            await workflow.execute_activity(
                "record_telemetry",
                args=[
                    "red_team_campaign_start",
                    {"persona_count": len(request.persona_ids)},
                ],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=1),
            )

            # Execute campaign activity
            result = await workflow.execute_activity(
                "run_red_team_campaign",
                args=[request],
                start_to_close_timeout=timedelta(seconds=request.timeout_seconds),
                retry_policy=retry_policy,
            )

            # Record completion
            await workflow.execute_activity(
                "record_telemetry",
                args=[
                    "red_team_campaign_complete",
                    {
                        "success": result.get("success"),
                        "attacks": result.get("total_attacks"),
                    },
                ],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=1),
            )

            # Trigger incident workflow if critical vulnerabilities found
            if result.get("success") and result.get("vulnerabilities_found"):
                critical_vulns = [
                    v
                    for v in result["vulnerabilities_found"]
                    if v.get("severity") == "critical"
                ]
                if critical_vulns:
                    await workflow.execute_activity(
                        "trigger_incident_workflow",
                        args=[critical_vulns],
                        start_to_close_timeout=timedelta(seconds=30),
                        retry_policy=retry_policy,
                    )

            return RedTeamCampaignResult(**result)

        except Exception as e:
            workflow.logger.error("Red team campaign failed: %s", e)
            return RedTeamCampaignResult(
                success=False,
                total_attacks=0,
                successful_attacks=0,
                failed_attacks=0,
                sessions=[],
                vulnerabilities_found=[],
                error=str(e),
            )


@workflow.defn
class CodeSecuritySweepWorkflow:
    """
    Durable workflow for automated code security sweeps.

    Scans codebase for vulnerabilities, generates patches,
    and creates SARIF reports for CI/CD integration.

    Schedule: Nightly, on merge to main, on security-sensitive changes
    """

    @workflow.run
    async def run(self, request: CodeSecuritySweepRequest) -> CodeSecuritySweepResult:
        """Execute code security sweep workflow."""
        workflow.logger.info("Starting code security sweep")

        try:
            retry_policy = RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=30),
                backoff_coefficient=2.0,
                maximum_attempts=3,
            )

            # Record start
            await workflow.execute_activity(
                "record_telemetry",
                args=["code_sweep_start", {"repo": request.repo_path}],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=1),
            )

            # Run vulnerability scan
            scan_result = await workflow.execute_activity(
                "run_code_vulnerability_scan",
                args=[request],
                start_to_close_timeout=timedelta(seconds=request.timeout_seconds),
                retry_policy=retry_policy,
            )

            # Generate patches if requested
            patches = None
            if request.generate_patches and scan_result.get("findings"):
                patches = await workflow.execute_activity(
                    "generate_security_patches",
                    args=[scan_result["findings"]],
                    start_to_close_timeout=timedelta(seconds=300),
                    retry_policy=retry_policy,
                )

            # Generate SARIF report if requested
            sarif_path = None
            if request.create_sarif and scan_result.get("findings"):
                sarif_result = await workflow.execute_activity(
                    "generate_sarif_report",
                    args=[scan_result["findings"]],
                    start_to_close_timeout=timedelta(seconds=60),
                    retry_policy=retry_policy,
                )
                sarif_path = sarif_result.get("path")

            # Record completion
            await workflow.execute_activity(
                "record_telemetry",
                args=[
                    "code_sweep_complete",
                    {
                        "findings": scan_result.get("total_findings", 0),
                        "critical": scan_result.get("by_severity", {}).get(
                            "critical", 0
                        ),
                    },
                ],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=1),
            )

            # Block deployment if critical vulnerabilities found
            critical_count = scan_result.get("by_severity", {}).get("critical", 0)
            if critical_count > 0:
                await workflow.execute_activity(
                    "block_deployment",
                    args=[{"reason": f"{critical_count} critical vulnerabilities"}],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=retry_policy,
                )

            return CodeSecuritySweepResult(
                success=scan_result.get("success", False),
                total_findings=scan_result.get("total_findings", 0),
                by_severity=scan_result.get("by_severity", {}),
                findings=scan_result.get("findings", []),
                patches=patches,
                sarif_path=sarif_path,
            )

        except Exception as e:
            workflow.logger.error("Code security sweep failed: %s", e)
            return CodeSecuritySweepResult(
                success=False,
                total_findings=0,
                by_severity={},
                findings=[],
                error=str(e),
            )


@workflow.defn
class ConstitutionalMonitoringWorkflow:
    """
    Durable workflow for constitutional AI monitoring.

    Tests target systems against constitutional principles,
    detects violations, and logs results.

    Schedule: Continuous with sample traffic
    """

    @workflow.run
    async def run(
        self, request: ConstitutionalMonitoringRequest
    ) -> ConstitutionalMonitoringResult:
        """Execute constitutional monitoring workflow."""
        workflow.logger.info("Starting constitutional monitoring")

        try:
            retry_policy = RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=20),
                backoff_coefficient=2.0,
                maximum_attempts=2,
            )

            # Record start
            await workflow.execute_activity(
                "record_telemetry",
                args=[
                    "constitutional_monitoring_start",
                    {"prompts": len(request.sample_prompts)},
                ],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=1),
            )

            # Run constitutional reviews
            result = await workflow.execute_activity(
                "run_constitutional_reviews",
                args=[request],
                start_to_close_timeout=timedelta(seconds=request.timeout_seconds),
                retry_policy=retry_policy,
            )

            # Record completion
            await workflow.execute_activity(
                "record_telemetry",
                args=[
                    "constitutional_monitoring_complete",
                    {
                        "violations": result.get("violations_detected", 0),
                        "compliant": result.get("compliant_responses", 0),
                    },
                ],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=1),
            )

            return ConstitutionalMonitoringResult(**result)

        except Exception as e:
            workflow.logger.error("Constitutional monitoring failed: %s", e)
            return ConstitutionalMonitoringResult(
                success=False,
                total_reviews=0,
                violations_detected=0,
                compliant_responses=0,
                violation_details=[],
                error=str(e),
            )


@workflow.defn
class SafetyTestingWorkflow:
    """
    Durable workflow for safety testing and jailbreak benchmarking.

    Runs standardized test suites (HYDRA, JBB) against target systems
    and evaluates defense effectiveness.

    Schedule: Weekly comprehensive, daily for critical tests
    """

    @workflow.run
    async def run(self, request: SafetyTestingRequest) -> SafetyTestingResult:
        """Execute safety testing workflow."""
        workflow.logger.info("Starting safety testing with dataset: %s", request.test_dataset)

        try:
            retry_policy = RetryPolicy(
                initial_interval=timedelta(seconds=2),
                maximum_interval=timedelta(seconds=60),
                backoff_coefficient=2.0,
                maximum_attempts=3,
            )

            # Record start
            await workflow.execute_activity(
                "record_telemetry",
                args=[
                    "safety_testing_start",
                    {"dataset": request.test_dataset, "max_tests": request.max_tests},
                ],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=1),
            )

            # Run safety tests
            result = await workflow.execute_activity(
                "run_safety_benchmark",
                args=[request],
                start_to_close_timeout=timedelta(seconds=request.timeout_seconds),
                retry_policy=retry_policy,
            )

            # Record completion
            await workflow.execute_activity(
                "record_telemetry",
                args=[
                    "safety_testing_complete",
                    {
                        "total": result.get("total_tests", 0),
                        "defense_rate": result.get("defense_rate", 0.0),
                    },
                ],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=1),
            )

            # Trigger alert if defense rate drops below threshold
            if result.get("defense_rate", 1.0) < 0.8:  # 80% threshold
                await workflow.execute_activity(
                    "trigger_security_alert",
                    args=[
                        {
                            "type": "low_defense_rate",
                            "rate": result.get("defense_rate"),
                            "dataset": request.test_dataset,
                        }
                    ],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=retry_policy,
                )

            return SafetyTestingResult(**result)

        except Exception as e:
            workflow.logger.error("Safety testing failed: %s", e)
            return SafetyTestingResult(
                success=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=0,
                test_results=[],
                defense_rate=0.0,
                error=str(e),
            )


# Export workflows
__all__ = [
    "RedTeamCampaignWorkflow",
    "CodeSecuritySweepWorkflow",
    "ConstitutionalMonitoringWorkflow",
    "SafetyTestingWorkflow",
    "RedTeamCampaignRequest",
    "RedTeamCampaignResult",
    "CodeSecuritySweepRequest",
    "CodeSecuritySweepResult",
    "ConstitutionalMonitoringRequest",
    "ConstitutionalMonitoringResult",
    "SafetyTestingRequest",
    "SafetyTestingResult",
]
