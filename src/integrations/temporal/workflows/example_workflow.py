"""
Example Workflow - Multi-step AI Operation.

This workflow demonstrates orchestrating a multi-step AI operation using Temporal.
It shows how to:
- Validate input
- Execute AI processing tasks
- Handle errors with retries
- Return structured results

Extend this pattern for real AI use cases like:
- Learning request workflows
- Image generation pipelines
- Data analysis tasks
- Crisis response operations
"""

import logging
from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

# Import activities (use with_start_workflow to avoid circular imports)
with workflow.unsafe.imports_passed_through():
    from integrations.temporal.activities.core_tasks import (
        process_ai_task,
        simulate_ai_call,
        validate_input,
    )

logger = logging.getLogger(__name__)


@dataclass
class WorkflowInput:
    """Input data for the example workflow."""

    data: str
    user_id: str | None = None
    options: dict | None = None


@dataclass
class WorkflowOutput:
    """Output from the example workflow."""

    success: bool
    result: str | None = None
    error: str | None = None
    steps_completed: list[str] | None = None


@workflow.defn
class ExampleWorkflow:
    """
    Example workflow demonstrating a multi-step AI operation.

    This workflow coordinates three activities:
    1. Input validation
    2. Simulated AI call
    3. Task processing

    Each activity is retried on failure with exponential backoff.
    The workflow is durable and can survive process crashes.
    """

    @workflow.run
    async def run(self, input_data: WorkflowInput) -> WorkflowOutput:
        """
        Execute the multi-step AI workflow.

        Args:
            input_data: Input parameters for the workflow

        Returns:
            WorkflowOutput with success status and results
        """
        workflow.logger.info(
            "Starting ExampleWorkflow for user: %s", input_data.user_id or "anonymous"
        )

        steps_completed = []

        # Define retry policy for activities
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=10),
            maximum_attempts=3,
            backoff_coefficient=2.0,
        )

        try:
            # Step 1: Validate input
            workflow.logger.info("Step 1: Validating input...")
            is_valid = await workflow.execute_activity(
                validate_input,
                input_data.data,
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy,
            )

            if not is_valid:
                workflow.logger.warning("Input validation failed")
                return WorkflowOutput(
                    success=False,
                    error="Input validation failed",
                    steps_completed=["validation_failed"],
                )

            steps_completed.append("validation")
            workflow.logger.info("✓ Input validated successfully")

            # Step 2: Simulate AI call
            workflow.logger.info("Step 2: Calling AI system...")
            ai_response = await workflow.execute_activity(
                simulate_ai_call,
                input_data.data,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy,
            )
            steps_completed.append("ai_call")
            workflow.logger.info("✓ AI call completed: %s", ai_response)

            # Step 3: Process the task
            workflow.logger.info("Step 3: Processing AI task...")
            final_result = await workflow.execute_activity(
                process_ai_task,
                {
                    "input": input_data.data,
                    "ai_response": ai_response,
                    "user_id": input_data.user_id,
                },
                start_to_close_timeout=timedelta(seconds=20),
                retry_policy=retry_policy,
            )
            steps_completed.append("processing")
            workflow.logger.info("✓ Task processed successfully")

            # Return successful result
            workflow.logger.info("Workflow completed successfully")
            return WorkflowOutput(
                success=True,
                result=final_result,
                steps_completed=steps_completed,
            )

        except Exception as e:
            # Handle any workflow errors
            error_msg = f"Workflow failed: {str(e)}"
            workflow.logger.error(error_msg)
            return WorkflowOutput(
                success=False,
                error=error_msg,
                steps_completed=steps_completed,
            )
