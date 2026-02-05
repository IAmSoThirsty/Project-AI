"""
SuperKernel - Unified Orchestration Layer for All Kernels.

This module implements the SuperKernel that provides centralized orchestration,
governance, logging, and RBAC for all subordinate kernels in the system.

The SuperKernel maintains the separation between governance (decides what can be done)
and execution (does what was approved), while providing a single entrypoint for all
cognitive operations.
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .kernel_types import KernelInterface, KernelType

logger = logging.getLogger(__name__)


@dataclass
class RegisteredKernel:
    """
    Information about a registered kernel.

    Attributes:
        type: Kernel type (COGNITION, REFLECTION, etc.)
        instance: Kernel instance (must implement KernelInterface)
        metadata: Optional metadata about the kernel
    """

    type: KernelType
    instance: KernelInterface
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SuperKernelExecutionRecord:
    """
    Record of a SuperKernel execution.

    Provides five-channel logging for forensic auditability:
    - attempt: What was attempted
    - decision: Governance decision
    - result: Actual result
    - reflection: Post-hoc insights (optional)
    - error: Error information (if failed)
    """

    execution_id: str
    kernel_type: KernelType
    input_data: Any
    timestamp: datetime

    # Five-channel logging
    attempt: dict[str, Any] = field(default_factory=dict)
    decision: dict[str, Any] = field(default_factory=dict)
    result: Any = None
    reflection: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    # Metadata
    source: str = "unknown"
    duration_ms: float = 0.0
    governance_approved: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "execution_id": self.execution_id,
            "kernel_type": self.kernel_type.name,
            "timestamp": self.timestamp.isoformat(),
            "attempt": self.attempt,
            "decision": self.decision,
            "result": self.result,
            "reflection": self.reflection,
            "error": self.error,
            "source": self.source,
            "duration_ms": self.duration_ms,
            "governance_approved": self.governance_approved,
        }


class SuperKernel:
    """
    SuperKernel - Unified orchestration layer for all subordinate kernels.

    The SuperKernel provides:
    - Centralized kernel registration and routing
    - Unified governance checks (Triumvirate, Four Laws)
    - Five-channel logging for all executions
    - RBAC enforcement
    - Execution history and statistics

    NON-NEGOTIABLE INVARIANTS:
    - All execution flows through SuperKernel.process()
    - Governance checks happen before routing to subordinate kernels
    - All executions are logged (including blocked ones)
    - Subordinate kernels don't duplicate governance or logging

    Usage:
        super_kernel = SuperKernel(triumvirate=triumvirate, governance=governance)
        super_kernel.register_kernel(KernelType.COGNITION, cognition_kernel)
        super_kernel.register_kernel(KernelType.REFLECTION, reflection_adapter)

        result = super_kernel.process(
            user_input,
            kernel_type=KernelType.COGNITION,
            source="user",
        )
    """

    def __init__(
        self,
        triumvirate: Any | None = None,
        governance: Any | None = None,
        rbac_system: Any | None = None,
    ):
        """
        Initialize SuperKernel.

        Args:
            triumvirate: Triumvirate instance for governance decisions
            governance: Legacy governance system (optional)
            rbac_system: RBAC system for access control (optional)
        """
        self.kernels: dict[KernelType, RegisteredKernel] = {}
        self.triumvirate = triumvirate
        self.governance = governance
        self.rbac_system = rbac_system

        # Execution tracking
        self.execution_history: list[SuperKernelExecutionRecord] = []
        self.execution_count = 0
        self.blocked_count = 0

        logger.info("SuperKernel initialized")
        logger.info("  Triumvirate: %s", triumvirate is not None)
        logger.info("  Governance: %s", governance is not None)
        logger.info("  RBAC: %s", rbac_system is not None)

    def register_kernel(
        self,
        kernel_type: KernelType,
        instance: KernelInterface,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Register a subordinate kernel.

        Args:
            kernel_type: Type of kernel to register
            instance: Kernel instance (must implement KernelInterface)
            metadata: Optional metadata about the kernel

        Raises:
            ValueError: If kernel type already registered
            TypeError: If instance doesn't implement KernelInterface
        """
        if kernel_type in self.kernels:
            raise ValueError(f"{kernel_type.name} already registered")

        if not isinstance(instance, KernelInterface):
            raise TypeError(
                f"Kernel instance must implement KernelInterface, got {type(instance)}"
            )

        self.kernels[kernel_type] = RegisteredKernel(
            type=kernel_type,
            instance=instance,
            metadata=metadata or {},
        )

        logger.info("Registered kernel: %s", kernel_type.name)

    def unregister_kernel(self, kernel_type: KernelType) -> None:
        """
        Unregister a subordinate kernel.

        Args:
            kernel_type: Type of kernel to unregister
        """
        if kernel_type in self.kernels:
            del self.kernels[kernel_type]
            logger.info("Unregistered kernel: %s", kernel_type.name)

    def get_registered_kernels(self) -> list[KernelType]:
        """
        Get list of registered kernel types.

        Returns:
            List of registered kernel types
        """
        return list(self.kernels.keys())

    def process(
        self,
        input_data: Any,
        *,
        kernel_type: KernelType,
        source: str = "user",
        metadata: dict[str, Any] | None = None,
        **kwargs,
    ) -> Any:
        """
        Central entrypoint for processing through subordinate kernels.

        This method provides:
        1. Governance checks (Triumvirate, Four Laws)
        2. RBAC enforcement
        3. Routing to appropriate kernel
        4. Five-channel logging
        5. Execution history tracking

        Args:
            input_data: Input data to process
            kernel_type: Which kernel to route to
            source: Source of the request (user, agent, system)
            metadata: Optional metadata for execution
            **kwargs: Additional arguments passed to kernel

        Returns:
            Result from subordinate kernel

        Raises:
            RuntimeError: If kernel not registered or processing fails
            PermissionError: If governance blocks the execution
        """
        import time

        execution_id = f"super_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(UTC)
        metadata = metadata or {}

        logger.info(
            "[%s] Processing request for %s kernel from %s",
            execution_id,
            kernel_type.name,
            source,
        )

        # Create execution record
        record = SuperKernelExecutionRecord(
            execution_id=execution_id,
            kernel_type=kernel_type,
            input_data=input_data,
            timestamp=timestamp,
            source=source,
        )

        # Channel 1: Attempt (what was tried)
        record.attempt = {
            "kernel_type": kernel_type.name,
            "source": source,
            "metadata": metadata,
            "timestamp": timestamp.isoformat(),
        }

        start_time = time.time()

        try:
            # Step 1: Governance checks
            governance_decision = self._check_governance(
                kernel_type, input_data, source, metadata
            )

            # Channel 2: Decision (governance outcome)
            record.decision = governance_decision
            record.governance_approved = governance_decision.get("approved", True)

            if not governance_decision.get("approved", True):
                # Blocked by governance
                self.blocked_count += 1
                record.error = governance_decision.get("reason", "Blocked by governance")

                logger.warning(
                    "[%s] Blocked by governance: %s",
                    execution_id,
                    record.error,
                )

                raise PermissionError(record.error)

            # Step 2: RBAC checks (optional)
            if self.rbac_system:
                self._check_rbac(source, kernel_type, metadata)

            # Step 3: Route to subordinate kernel
            registered = self.kernels.get(kernel_type)
            if not registered:
                raise RuntimeError(f"No kernel registered for {kernel_type.name}")

            # Execute through subordinate kernel
            result = registered.instance.process(input_data, **kwargs)

            # Channel 3: Result (actual outcome)
            record.result = result

            # Success
            self.execution_count += 1
            record.duration_ms = (time.time() - start_time) * 1000

            logger.info(
                "[%s] Completed successfully in %.2fms",
                execution_id,
                record.duration_ms,
            )

            return result

        except Exception as e:
            # Channel 5: Error (for forensic replay)
            record.error = str(e)
            record.duration_ms = (time.time() - start_time) * 1000

            logger.error(
                "[%s] Failed after %.2fms: %s",
                execution_id,
                record.duration_ms,
                e,
            )

            raise

        finally:
            # Always log execution (including blocked/failed)
            self.execution_history.append(record)

    def route(
        self,
        task: Any,
        *,
        kernel_type: KernelType,
        source: str = "agent",
        **kwargs,
    ) -> Any:
        """
        Route agent-initiated tasks (similar to CognitionKernel.route()).

        This is a convenience method that delegates to process() with
        source defaulting to "agent".

        Args:
            task: Task to route
            kernel_type: Which kernel to route to
            source: Source of the task (default: "agent")
            **kwargs: Additional arguments

        Returns:
            Task result
        """
        return self.process(
            task,
            kernel_type=kernel_type,
            source=source,
            **kwargs,
        )

    def _check_governance(
        self,
        kernel_type: KernelType,
        input_data: Any,
        source: str,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Check governance policies before execution.

        Args:
            kernel_type: Type of kernel
            input_data: Input data
            source: Request source
            metadata: Request metadata

        Returns:
            Governance decision dict with 'approved' and 'reason' keys
        """
        # Auto-approve for low-risk operations
        low_risk_kernels = {KernelType.MEMORY, KernelType.PERSPECTIVE}

        if kernel_type in low_risk_kernels and source in ["system", "agent"]:
            return {
                "approved": True,
                "reason": f"Auto-approved: Low-risk {kernel_type.name} operation",
            }

        # Check with Triumvirate if available
        if self.triumvirate:
            try:
                # Call Triumvirate for high-risk operations
                triumvirate_result = self.triumvirate.process(
                    {
                        "kernel_type": kernel_type.name,
                        "source": source,
                        "metadata": metadata,
                    }
                )

                return {
                    "approved": triumvirate_result.get("success", True),
                    "reason": triumvirate_result.get("output", "Triumvirate evaluation"),
                }
            except Exception as e:
                logger.error("Triumvirate evaluation failed: %s", e)
                # Fail-safe: block on error
                return {
                    "approved": False,
                    "reason": f"Triumvirate evaluation error: {e}",
                }

        # Check with legacy governance if available
        if self.governance:
            try:
                gov_result = self.governance.validate_action(
                    action_name=f"{kernel_type.name}_operation",
                    action_type="system_operation",
                    metadata=metadata,
                )

                return {
                    "approved": gov_result.get("allowed", True),
                    "reason": gov_result.get("reason", "Governance evaluation"),
                }
            except Exception as e:
                logger.error("Governance evaluation failed: %s", e)
                return {
                    "approved": False,
                    "reason": f"Governance evaluation error: {e}",
                }

        # No governance configured - auto-approve with warning
        logger.warning("No governance configured - auto-approving")
        return {
            "approved": True,
            "reason": "Auto-approved: No governance configured",
        }

    def _check_rbac(
        self,
        source: str,
        kernel_type: KernelType,
        metadata: dict[str, Any],
    ) -> None:
        """
        Check RBAC permissions.

        Args:
            source: Request source
            kernel_type: Type of kernel
            metadata: Request metadata

        Raises:
            PermissionError: If RBAC check fails
        """
        # RBAC check implementation would go here
        # For now, this is a placeholder
        pass

    def get_execution_history(
        self,
        limit: int = 10,
        kernel_type: KernelType | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get execution history.

        Args:
            limit: Maximum number of records to return
            kernel_type: Filter by kernel type (optional)

        Returns:
            List of execution records as dictionaries
        """
        history = self.execution_history

        # Filter by kernel type if specified
        if kernel_type:
            history = [r for r in history if r.kernel_type == kernel_type]

        # Return most recent records
        return [r.to_dict() for r in history[-limit:]]

    def get_statistics(self) -> dict[str, Any]:
        """
        Get SuperKernel statistics.

        Returns:
            Dictionary with execution metrics
        """
        return {
            "total_executions": self.execution_count,
            "blocked_executions": self.blocked_count,
            "success_rate": (
                (self.execution_count - self.blocked_count) / self.execution_count
                if self.execution_count > 0
                else 0.0
            ),
            "registered_kernels": [k.name for k in self.kernels.keys()],
            "history_size": len(self.execution_history),
        }

    def get_kernel_statistics(self, kernel_type: KernelType) -> dict[str, Any]:
        """
        Get statistics for a specific kernel.

        Args:
            kernel_type: Kernel type

        Returns:
            Kernel statistics

        Raises:
            RuntimeError: If kernel not registered
        """
        registered = self.kernels.get(kernel_type)
        if not registered:
            raise RuntimeError(f"No kernel registered for {kernel_type.name}")

        return registered.instance.get_statistics()


__all__ = [
    "SuperKernel",
    "RegisteredKernel",
    "SuperKernelExecutionRecord",
]
