"""
Triumvirate Workflow - Durable AI Pipeline Orchestration

Provides fault-tolerant, configurable workflow for the Triumvirate
AI system with:
- Highly configurable timeouts and retries
- Deterministic execution
- Rich event payloads with correlation IDs
- Telemetry integration
"""

import logging
from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

logger = logging.getLogger(__name__)


@dataclass
class TriumvirateRequest:
    """Input for Triumvirate workflow."""

    input_data: str | dict
    context: dict | None = None
    skip_validation: bool = False
    timeout_seconds: int = 300
    max_retries: int = 3


@dataclass
class TriumvirateResult:
    """Result from Triumvirate workflow."""

    success: bool
    output: dict | None = None
    error: str | None = None
    correlation_id: str | None = None
    duration_ms: float | None = None
    pipeline_details: dict | None = None


@workflow.defn
class TriumvirateWorkflow:
    """
    Durable workflow for Triumvirate AI pipeline.

    Features:
    - Configurable timeouts for each stage
    - Automatic retries with exponential backoff
    - Telemetry event recording
    - Correlation ID tracking
    - Graceful degradation
    """

    @workflow.run
    async def run(self, request: TriumvirateRequest) -> TriumvirateResult:
        """
        Execute the Triumvirate workflow.

        Args:
            request: Workflow request with input and configuration

        Returns:
            Workflow result with processing output
        """
        workflow.logger.info("Starting Triumvirate workflow")

        try:
            # Configure retry policy
            retry_policy = RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=30),
                backoff_coefficient=2.0,
                maximum_attempts=request.max_retries,
            )

            # Configure timeout
            timeout = timedelta(seconds=request.timeout_seconds)

            # Prepare activity request
            activity_request = {
                "input_data": request.input_data,
                "context": request.context or {},
                "skip_validation": request.skip_validation,
            }

            # Record start telemetry
            await workflow.execute_activity(
                "record_telemetry",
                args=["workflow_start", {"request": str(request)[:200]}],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=1),  # Don't retry telemetry
            )

            # Execute main pipeline activity
            result = await workflow.execute_activity(
                "run_triumvirate_pipeline",
                activity_request,
                start_to_close_timeout=timeout,
                retry_policy=retry_policy,
            )

            # Record completion telemetry
            await workflow.execute_activity(
                "record_telemetry",
                args=[
                    "workflow_complete",
                    {
                        "correlation_id": result.get("correlation_id"),
                        "success": result.get("success"),
                    },
                ],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=RetryPolicy(maximum_attempts=1),
            )

            # Build result
            workflow.logger.info(
                f"Triumvirate workflow completed: {result.get('correlation_id')}"
            )

            return TriumvirateResult(
                success=result.get("success", False),
                output=result.get("output"),
                error=result.get("error"),
                correlation_id=result.get("correlation_id"),
                duration_ms=result.get("duration_ms"),
                pipeline_details=result.get("pipeline"),
            )

        except Exception as e:
            workflow.logger.error(f"Triumvirate workflow failed: {e}")

            # Record failure telemetry
            try:
                await workflow.execute_activity(
                    "record_telemetry",
                    args=["workflow_error", {"error": str(e)}],
                    start_to_close_timeout=timedelta(seconds=10),
                    retry_policy=RetryPolicy(maximum_attempts=1),
                )
            except Exception:
                pass  # Don't fail workflow if telemetry fails

            return TriumvirateResult(success=False, error=str(e))


@workflow.defn
class TriumvirateStepWorkflow:
    """
    Step-by-step Triumvirate workflow with individual activity calls.

    This workflow breaks down the pipeline into separate activities,
    providing more granular control and observability.
    """

    @workflow.run
    async def run(self, request: TriumvirateRequest) -> TriumvirateResult:
        """
        Execute Triumvirate pipeline step-by-step.

        Args:
            request: Workflow request

        Returns:
            Workflow result
        """
        workflow.logger.info("Starting step-by-step Triumvirate workflow")

        correlation_id = None

        try:
            # Standard retry policy
            retry_policy = RetryPolicy(
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=30),
                backoff_coefficient=2.0,
                maximum_attempts=request.max_retries,
            )

            input_data = request.input_data
            context = request.context or {}

            # Step 1: Input Validation (unless skipped)
            if not request.skip_validation:
                workflow.logger.info("Step 1: Input validation")
                validation_result = await workflow.execute_activity(
                    "validate_input_activity",
                    args=[input_data, context],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=retry_policy,
                )

                if not validation_result.get("valid", False):
                    return TriumvirateResult(
                        success=False,
                        error="Input validation failed",
                        pipeline_details={"validation": validation_result},
                    )

                input_data = validation_result.get("input", input_data)

            # Step 2: Codex Inference
            workflow.logger.info("Step 2: Codex inference")
            codex_result = await workflow.execute_activity(
                "run_codex_inference",
                args=[input_data, context],
                start_to_close_timeout=timedelta(seconds=120),
                retry_policy=retry_policy,
            )

            if not codex_result.get("success", False):
                return TriumvirateResult(
                    success=False,
                    error="Codex inference failed",
                    pipeline_details={"codex": codex_result},
                )

            # Step 3: Galahad Reasoning
            workflow.logger.info("Step 3: Galahad reasoning")
            reasoning_inputs = [input_data, codex_result.get("output")]
            galahad_result = await workflow.execute_activity(
                "run_galahad_reasoning",
                args=[reasoning_inputs, context],
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=retry_policy,
            )

            if not galahad_result.get("success", False):
                return TriumvirateResult(
                    success=False,
                    error="Galahad reasoning failed",
                    pipeline_details={"galahad": galahad_result},
                )

            # Step 4: Output Enforcement
            workflow.logger.info("Step 4: Output enforcement")
            conclusion = galahad_result.get("conclusion")
            enforcement_result = await workflow.execute_activity(
                "enforce_output_policy",
                args=[conclusion, context],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy,
            )

            if not enforcement_result.get("allowed", False):
                return TriumvirateResult(
                    success=False,
                    error="Output enforcement blocked",
                    pipeline_details={"cerberus": enforcement_result},
                )

            # Success
            workflow.logger.info("Step-by-step workflow completed successfully")

            return TriumvirateResult(
                success=True,
                output=enforcement_result.get("output"),
                correlation_id=correlation_id,
                pipeline_details={
                    "validation": (
                        validation_result if not request.skip_validation else None
                    ),
                    "codex": codex_result,
                    "galahad": galahad_result,
                    "cerberus": enforcement_result,
                },
            )

        except Exception as e:
            workflow.logger.error(f"Step-by-step workflow failed: {e}")
            return TriumvirateResult(success=False, error=str(e))
