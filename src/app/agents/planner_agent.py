"""Planner / Scheduler Agent

Decomposes tasks to smaller agents and schedules them.

All task scheduling and execution routes through CognitionKernel.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class PlannerAgent(KernelRoutedAgent):
    """Plans and schedules task execution.

    All planning and scheduling operations route through CognitionKernel.
    """

    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        """Initialize the planner agent.

        Args:
            kernel: CognitionKernel instance for routing operations
        """
        # Initialize kernel routing (COGNITION KERNEL INTEGRATION)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low"  # Planning is typically low risk
        )

        self.queue: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def schedule(self, task: dict[str, Any]) -> None:
        """Schedule a task for execution.

        Routes through kernel for tracking and governance.
        """
        # Route through kernel (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            action=self._do_schedule,
            action_name="PlannerAgent.schedule",
            action_args=(task,),
            requires_approval=False,
            risk_level="low",
            metadata={"task_name": task.get("name"), "operation": "schedule"}
        )

    def _do_schedule(self, task: dict[str, Any]) -> None:
        """Internal implementation of task scheduling."""
        with self._lock:
            self.queue.append(task)
        logger.info("Task scheduled: %s", task.get("name"))

    def run_next(self) -> dict[str, Any]:
        """Execute the next task in the queue.

        Routes through kernel for governance and tracking.
        """
        # Route through kernel (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            action=self._do_run_next,
            action_name="PlannerAgent.run_next",
            requires_approval=False,
            risk_level="medium",  # Task execution has moderate risk
            metadata={"operation": "run_next"}
        )

    def _do_run_next(self) -> dict[str, Any]:
        """Internal implementation of task execution."""
        with self._lock:
            if not self.queue:
                return {"success": False, "error": "empty"}
            task = self.queue.pop(0)
        # naive execution: log and return
        logger.info("Executing task: %s", task.get("name"))
        time.sleep(0.01)
        return {"success": True, "task": task}
