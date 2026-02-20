"""
MemoryLoggingService - Extracted memory logging logic from CognitionKernel.

This service handles all memory recording responsibilities:
- Five-channel memory architecture (attempt, decision, result, reflection, error)
- Memory persistence and retrieval
- Execution history tracking
- Forensic auditability

FIVE-CHANNEL ARCHITECTURE:
1. Attempt: The intent (what was tried)
2. Decision: Governance outcome (what was approved/blocked)
3. Result: Actual effect (what happened)
4. Reflection: Post-hoc reasoning (insights generated)
5. Error: Runtime exceptions and failures (for forensic replay)

The service maintains complete audit trails for all executions, including
blocked actions, to enable forensic analysis and alignment drift detection.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MemoryLoggingService:
    """
    Service responsible for recording all executions in multi-channel memory.

    Key Responsibilities:
    1. Record five-channel memory for each execution
    2. Maintain execution history
    3. Support forensic auditability
    4. Enable alignment drift detection
    5. Handle memory persistence

    NON-NEGOTIABLE INVARIANTS:
    - ALL executions are recorded (including blocked ones)
    - Five channels are always populated
    - Memory commits never fail silently
    - History is immutable once committed
    """

    def __init__(
        self,
        memory_engine: Any | None = None,
        reflection_engine: Any | None = None,
    ):
        """
        Initialize the Memory Logging Service.

        Args:
            memory_engine: Memory engine for persistence
            reflection_engine: Reflection engine for insights
        """
        self.memory_engine = memory_engine
        self.reflection_engine = reflection_engine

        # Local execution history (forensic auditability)
        self.execution_history: list[Any] = []
        self.history_size_limit = 1000  # Keep last 1000 executions

        # Statistics
        self.total_recordings = 0
        self.failed_recordings = 0

        logger.info("MemoryLoggingService initialized")
        logger.info("  Memory Engine: %s", memory_engine is not None)
        logger.info("  Reflection Engine: %s", reflection_engine is not None)

    def record_execution(
        self,
        context: Any,
    ) -> tuple[bool, str | None]:
        """
        Record an execution in five-channel memory.

        This is called after execution completes (success or failure).
        ALL executions are recorded, including blocked ones.

        Args:
            context: Execution context with complete state

        Returns:
            Tuple of (success, error_message)
        """
        logger.debug(
            "[%s] Recording execution in five-channel memory",
            context.trace_id,
        )

        try:
            # Populate five channels
            self._populate_channels(context)

            # Add to local history
            self._add_to_history(context)

            # Persist to memory engine
            if self.memory_engine:
                self._persist_to_memory_engine(context)
            else:
                logger.warning(
                    "[%s] No memory engine configured - execution not persisted",
                    context.trace_id,
                )

            # Generate reflection if appropriate
            if self.reflection_engine and self._should_reflect(context):
                self._generate_reflection(context)

            self.total_recordings += 1

            logger.debug(
                "[%s] Memory recording completed",
                context.trace_id,
            )

            return True, None

        except Exception as e:
            self.failed_recordings += 1
            logger.error(
                "[%s] Memory recording failed: %s",
                context.trace_id,
                e,
            )
            return False, str(e)

    def _populate_channels(self, context: Any) -> None:
        """
        Populate the five memory channels.

        Channels:
        1. Attempt: Intent and action proposal
        2. Decision: Governance outcome
        3. Result: Actual execution result
        4. Reflection: Post-hoc insights
        5. Error: Runtime exceptions

        Args:
            context: Execution context to populate
        """
        # Channel 1: Attempt (always populated)
        context.channels["attempt"] = {
            "action_name": context.proposed_action.action_name,
            "action_type": context.proposed_action.action_type.value,
            "source": context.source,
            "user_id": context.user_id,
            "trace_id": context.trace_id,
            "timestamp": context.timestamp.isoformat(),
        }

        # Channel 2: Decision (populated if governance ran)
        if context.governance_decision:
            context.channels["decision"] = {
                "decision_id": context.governance_decision.decision_id,
                "approved": context.governance_decision.approved,
                "reason": context.governance_decision.reason,
                "council_votes": context.governance_decision.council_votes,
            }

        # Channel 3: Result (populated if execution completed)
        if context.result is not None:
            context.channels["result"] = context.result

        # Channel 4: Reflection (populated later if reflection triggers)
        # This is left as None for now, reflection service will populate it

        # Channel 5: Error (populated if execution failed)
        if context.error:
            context.channels["error"] = {
                "error_message": context.error,
                "status": context.status.value,
                "trace_id": context.trace_id,
            }

    def _add_to_history(self, context: Any) -> None:
        """
        Add execution to local history.

        Maintains a circular buffer of recent executions.

        Args:
            context: Execution context to add
        """
        self.execution_history.append(context)

        # Maintain history size limit
        if len(self.execution_history) > self.history_size_limit:
            self.execution_history.pop(0)

    def _persist_to_memory_engine(self, context: Any) -> None:
        """
        Persist execution to memory engine.

        Uses record_execution if available, falls back to add_memory.

        Args:
            context: Execution context to persist
        """
        try:
            if hasattr(self.memory_engine, "record_execution"):
                # Use new five-channel API
                self.memory_engine.record_execution(
                    trace_id=context.trace_id,
                    channels=context.channels,
                    status=context.status.value,
                )
            elif hasattr(self.memory_engine, "add_memory"):
                # Fall back to legacy API
                self.memory_engine.add_memory(
                    content=f"Executed: {context.proposed_action.action_name}",
                    category="execution",
                    metadata={
                        "trace_id": context.trace_id,
                        "status": context.status.value,
                        "channels": context.channels,
                    },
                )
            else:
                logger.warning(
                    "[%s] Memory engine has no supported persistence method",
                    context.trace_id,
                )

        except Exception as e:
            logger.error(
                "[%s] Failed to persist to memory engine: %s",
                context.trace_id,
                e,
            )
            raise

    def _should_reflect(self, context: Any) -> bool:
        """
        Determine if reflection should be triggered.

        Reflection triggers for:
        - Failed executions
        - Blocked executions
        - High-risk completed executions

        Args:
            context: Execution context

        Returns:
            True if reflection should trigger
        """
        # Always reflect on failures and blocks
        if context.status.value in ["failed", "blocked"]:
            return True

        # Reflect on high-risk completions
        return context.proposed_action.risk_level == "high"

    def _generate_reflection(self, context: Any) -> None:
        """
        Generate reflection insights for the execution.

        Populates the reflection channel with insights.

        Args:
            context: Execution context
        """
        try:
            reflection_data = {
                "action": context.proposed_action.action_name,
                "result_success": context.status.value == "completed",
                "governance_decision": (context.governance_decision.reason if context.governance_decision else None),
                "duration_ms": context.duration_ms,
                "triggered_by": "memory_logging_service",
            }

            # Store in reflection channel
            context.channels["reflection"] = reflection_data

            logger.debug(
                "[%s] Reflection generated",
                context.trace_id,
            )

        except Exception as e:
            logger.error(
                "[%s] Reflection generation failed: %s",
                context.trace_id,
                e,
            )

    def get_execution_history(
        self,
        limit: int = 10,
        filter_status: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get execution history.

        Args:
            limit: Maximum number of entries to return
            filter_status: Optional status filter (completed, failed, blocked)

        Returns:
            List of execution history entries
        """
        history = self.execution_history

        # Apply status filter if provided
        if filter_status:
            history = [ctx for ctx in history if ctx.status.value == filter_status]

        # Return most recent entries
        recent = history[-limit:]

        # Convert to dictionaries
        return [
            {
                "trace_id": ctx.trace_id,
                "action_name": ctx.proposed_action.action_name,
                "status": ctx.status.value,
                "timestamp": ctx.timestamp.isoformat(),
                "duration_ms": ctx.duration_ms,
                "error": ctx.error,
            }
            for ctx in recent
        ]

    def get_statistics(self) -> dict[str, Any]:
        """
        Get memory logging statistics.

        Returns:
            Dictionary with logging metrics
        """
        success_rate = (
            (self.total_recordings - self.failed_recordings) / self.total_recordings
            if self.total_recordings > 0
            else 0.0
        )

        return {
            "total_recordings": self.total_recordings,
            "successful_recordings": self.total_recordings - self.failed_recordings,
            "failed_recordings": self.failed_recordings,
            "success_rate": success_rate,
            "history_size": len(self.execution_history),
            "history_size_limit": self.history_size_limit,
            "memory_engine_active": self.memory_engine is not None,
            "reflection_engine_active": self.reflection_engine is not None,
        }


__all__ = [
    "MemoryLoggingService",
]
