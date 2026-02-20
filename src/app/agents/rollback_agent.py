"""Rollback & Incident Responder

Monitors integrations and can automatically rollback if failures observed.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class RollbackAgent(KernelRoutedAgent):
    def __init__(self, data_dir: str = "data", kernel: CognitionKernel | None = None) -> None:
        # Initialize kernel routing (COGNITION KERNEL INTEGRATION)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="high",
        )
        self.data_dir = data_dir

    def monitor_and_rollback(self, integration_report: dict[str, Any]) -> dict[str, Any]:
        # Route through kernel (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            self._do_monitor_and_rollback,
            integration_report,
            operation_name="monitor_and_rollback",
            risk_level="high",
            metadata={"has_errors": bool(integration_report.get("report", {}).get("errors", []))},
        )

    def _do_monitor_and_rollback(self, integration_report: dict[str, Any]) -> dict[str, Any]:
        """Internal implementation of monitoring and rollback."""
        # If integration_report contains errors, attempt rollback
        try:
            errors = integration_report.get("report", {}).get("errors", [])
            if errors:
                # For simplicity assume we can restore backups listed in integrated
                restored = []
                for ent in integration_report.get("report", {}).get("integrated", []):
                    bak = ent.get("backup")
                    target = ent.get("target")
                    if bak and os.path.exists(bak):
                        os.replace(bak, target)
                        restored.append(target)
                return {"success": True, "restored": restored}
            return {"success": True, "restored": []}
        except Exception as e:
            logger.exception("Rollback failed: %s", e)
            return {"success": False, "error": str(e)}
