"""
ExecutionService - Extracted execution logic from CognitionKernel.

This service handles all execution-related responsibilities:
- Action execution with TARL enforcement
- Execution status tracking
- Error handling and recovery
- Performance monitoring

The service maintains the principle: "Execution never governs"
All actions must be pre-approved by GovernanceService before execution.

THREE-TIER PLATFORM:
- Tier 2 (Infrastructure): This is a Tier-2 Infrastructure Controller
- Subordinate to Tier-1 governance
- Can be paused or constrained by governance
"""

import logging
import time
from enum import Enum
from typing import Any

from app.core.platform_tiers import (
    AuthorityLevel,
    ComponentRole,
    PlatformTier,
    get_tier_registry,
)

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Status of an execution."""

    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"  # Blocked by governance


class ExecutionService:
    """
    Service responsible for executing approved actions.

    Key Responsibilities:
    1. Execute actions within kernel context
    2. Track execution status and performance
    3. Handle execution errors
    4. Integrate with TARL enforcement (if available)
    5. Record execution timing and metrics

    NON-NEGOTIABLE INVARIANTS:
    - Only executes pre-approved actions
    - Never makes governance decisions
    - All executions are timed and tracked
    - Errors are captured for forensic analysis
    """

    def __init__(
        self,
        tarl_gate: Any | None = None,
    ):
        """
        Initialize the Execution Service.

        Args:
            tarl_gate: TARL gate for enforcement (optional)
        """
        self.tarl_gate = tarl_gate

        # Execution tracking
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_execution_time_ms = 0.0

        # Register in Tier Registry as Tier-2 Infrastructure Controller
        try:
            tier_registry = get_tier_registry()
            tier_registry.register_component(
                component_id="execution_service",
                component_name="ExecutionService",
                tier=PlatformTier.TIER_2_INFRASTRUCTURE,
                authority_level=AuthorityLevel.CONSTRAINED,
                role=ComponentRole.INFRASTRUCTURE_CONTROLLER,
                component_ref=self,
                dependencies=["cognition_kernel"],  # Depends on kernel for authority
                can_be_paused=True,  # Can be paused by Tier-1
                can_be_replaced=False,  # Core infrastructure
            )
            logger.info("ExecutionService registered as Tier-2 Infrastructure Controller")
        except Exception as e:
            logger.warning("Failed to register ExecutionService in tier registry: %s", e)

        logger.info("ExecutionService initialized")
        logger.info("  TARL Gate: %s", tarl_gate is not None)

    def execute_action(
        self,
        action: Any,
        context: Any,
    ) -> tuple[Any, ExecutionStatus, str | None]:
        """
        Execute an approved action.

        CRITICAL: This method assumes the action has been pre-approved by governance.
        It does not make governance decisions - it only executes.

        Args:
            action: The approved action to execute
            context: Execution context with metadata

        Returns:
            Tuple of (result, status, error_message)
        """
        logger.info(
            "[%s] Executing action: %s",
            context.trace_id,
            action.action_name,
        )

        # Start timing
        start_time = time.time()

        # Update context
        context.status = ExecutionStatus.EXECUTING
        context.start_time = start_time

        try:
            # Enforce TARL policies if available
            if self.tarl_gate:
                self._enforce_tarl(action, context)

            # Execute the action
            result = self._execute(action, context)

            # Success path
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            # Update context
            context.status = ExecutionStatus.COMPLETED
            context.result = result
            context.end_time = end_time
            context.duration_ms = duration_ms

            # Update statistics
            self.execution_count += 1
            self.success_count += 1
            self.total_execution_time_ms += duration_ms

            logger.info(
                "[%s] Execution completed in %.2fms",
                context.trace_id,
                duration_ms,
            )

            return result, ExecutionStatus.COMPLETED, None

        except Exception as e:
            # Failure path
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000

            # Update context
            context.status = ExecutionStatus.FAILED
            context.error = str(e)
            context.end_time = end_time
            context.duration_ms = duration_ms

            # Update statistics
            self.execution_count += 1
            self.failure_count += 1
            self.total_execution_time_ms += duration_ms

            logger.error(
                "[%s] Execution failed after %.2fms: %s",
                context.trace_id,
                duration_ms,
                e,
            )

            return None, ExecutionStatus.FAILED, str(e)

    def _execute(self, action: Any, context: Any) -> Any:
        """
        Internal execution method.

        Calls the action's callable with its arguments.

        Args:
            action: Action to execute
            context: Execution context

        Returns:
            Result of the action execution
        """
        # Execute the action's callable
        if hasattr(action, "callable") and callable(action.callable):
            return action.callable(*action.args, **action.kwargs)
        else:
            raise ValueError(
                f"Action {action.action_name} has no callable implementation"
            )

    def _enforce_tarl(self, action: Any, context: Any) -> None:
        """
        Enforce TARL (Temporal Action Runtime Lock) policies.

        TARL provides additional runtime constraints and temporal enforcement.

        Args:
            action: Action to enforce
            context: Execution context

        Raises:
            RuntimeError: If TARL enforcement fails
        """
        try:
            tarl_context = {
                "action_name": action.action_name,
                "action_type": action.action_type.value if hasattr(action, "action_type") else "unknown",
                "trace_id": context.trace_id,
                "timestamp": context.timestamp.isoformat() if hasattr(context.timestamp, "isoformat") else str(context.timestamp),
            }

            self.tarl_gate.enforce(tarl_context)

            logger.debug(
                "[%s] TARL enforcement passed",
                context.trace_id,
            )

        except Exception as e:
            logger.error(
                "[%s] TARL enforcement failed: %s",
                context.trace_id,
                e,
            )
            raise RuntimeError(f"TARL enforcement failed: {e}") from e

    def get_statistics(self) -> dict[str, Any]:
        """
        Get execution statistics.

        Returns:
            Dictionary with execution metrics
        """
        success_rate = (
            self.success_count / self.execution_count
            if self.execution_count > 0
            else 0.0
        )

        avg_execution_time = (
            self.total_execution_time_ms / self.execution_count
            if self.execution_count > 0
            else 0.0
        )

        return {
            "total_executions": self.execution_count,
            "successful": self.success_count,
            "failed": self.failure_count,
            "success_rate": success_rate,
            "average_execution_time_ms": avg_execution_time,
            "total_execution_time_ms": self.total_execution_time_ms,
            "tarl_gate_active": self.tarl_gate is not None,
        }

    def reset_statistics(self) -> None:
        """Reset execution statistics (useful for testing)."""
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_execution_time_ms = 0.0
        logger.info("Execution statistics reset")


__all__ = [
    "ExecutionService",
    "ExecutionStatus",
]
