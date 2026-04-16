"""PACE Agent Template.

Source model: docs/architecture/AGENT_MODEL.md
Build guide: docs/templates/AGENT_BUILD_TEMPLATE.md

Copy this file when creating a new Project-AI/PACE agent, then replace the
template values with concrete names, capabilities, contracts, and tests.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

try:
    from app.core.cognition_kernel import CognitionKernel, ExecutionType
    from app.core.kernel_integration import KernelRoutedAgent
except ImportError:  # Allows this template to be imported outside the app runtime.
    CognitionKernel = None  # type: ignore[assignment]
    ExecutionType = None  # type: ignore[assignment]

    class KernelRoutedAgent:  # type: ignore[no-redef]
        """Fallback base for template linting outside the runtime package."""

        def __init__(self, *_: Any, **__: Any) -> None:
            pass


logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent operational states."""

    IDLE = "idle"
    BUSY = "busy"
    BLOCKED = "blocked"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class TaskStatus(str, Enum):
    """Task execution states."""

    SUCCESS = "success"
    FAILED = "failed"


@dataclass(frozen=True)
class AgentTask:
    """Task contract accepted by a PACE agent."""

    task_id: str
    task_type: str
    data: Any = None
    params: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TaskResult:
    """Stable result contract returned by a PACE agent."""

    task_id: str
    status: TaskStatus
    output: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class PaceAgentTemplate(KernelRoutedAgent):
    """Template for task, coordinator, monitor, or learning agents.

    Rename this class for the concrete agent.
    Keep the agent narrow: one purpose, explicit capabilities, audited effects.
    """

    agent_name = "PaceAgentTemplate"
    capabilities = {
        "template:execute",
    }

    def __init__(self, agent_id: str, kernel: CognitionKernel | None = None) -> None:
        execution_type = (
            ExecutionType.AGENT_ACTION if ExecutionType is not None else None
        )
        super().__init__(
            kernel=kernel,
            execution_type=execution_type,
            default_risk_level="low",
        )
        self.agent_id = agent_id
        self.status = AgentStatus.IDLE
        self.current_task: AgentTask | None = None
        self.metadata: dict[str, Any] = {}

    def can_execute(self, task: AgentTask) -> bool:
        """Return true only for declared capabilities."""
        return task.task_type in self.capabilities

    def execute(self, task: AgentTask) -> TaskResult:
        """Execute a task with stable status, failure, and cleanup behavior."""
        if not self.can_execute(task):
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=f"Unsupported task type: {task.task_type}",
            )

        self.status = AgentStatus.BUSY
        self.current_task = task

        try:
            if hasattr(self, "_execute_through_kernel"):
                output = self._execute_through_kernel(
                    action=self._do_execute,
                    action_name=f"{self.agent_name}.execute",
                    action_args=(task,),
                    requires_approval=False,
                    risk_level="low",
                    metadata={
                        "agent_id": self.agent_id,
                        "task_id": task.task_id,
                        "task_type": task.task_type,
                    },
                )
            else:
                output = self._do_execute(task)

            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.SUCCESS,
                output=output,
            )
        except Exception as exc:  # noqa: BLE001 - template records stable failure shape.
            logger.exception("Agent task failed: %s", task.task_id)
            self.status = AgentStatus.ERROR
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(exc),
            )
        finally:
            self.current_task = None
            if self.status != AgentStatus.ERROR:
                self.status = AgentStatus.IDLE

    def receive_message(self, message: dict[str, Any]) -> None:
        """Handle an incoming agent message."""
        logger.info("Received message for %s: %s", self.agent_id, message)

    def get_status(self) -> dict[str, Any]:
        """Return serializable operational status."""
        return {
            "agent_id": self.agent_id,
            "name": self.agent_name,
            "status": self.status.value,
            "current_task": self.current_task.task_id if self.current_task else None,
            "capabilities": sorted(self.capabilities),
            "utilization": self._calculate_utilization(),
        }

    def _do_execute(self, task: AgentTask) -> dict[str, Any]:
        """Concrete agent work goes here."""
        return {
            "handled": True,
            "task_type": task.task_type,
            "data": task.data,
        }

    def _calculate_utilization(self) -> float:
        if self.status == AgentStatus.BUSY:
            return 1.0
        if self.status == AgentStatus.IDLE:
            return 0.0
        return 0.5

