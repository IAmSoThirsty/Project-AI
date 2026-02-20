"""UX Feedback / Telemetry Agent

Collects user interactions and produces prioritized suggestions.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class UxTelemetryAgent(KernelRoutedAgent):
    def __init__(self, data_dir: str = "data", kernel: CognitionKernel | None = None) -> None:
        # Initialize kernel routing (COGNITION KERNEL INTEGRATION)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",
        )
        self.data_dir = data_dir
        self.telemetry_path = os.path.join(self.data_dir, "telemetry.json")
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.telemetry_path):
            with open(self.telemetry_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def record_event(self, evt: dict[str, Any]) -> None:
        # Route through kernel (COGNITION KERNEL ROUTING)
        self._execute_through_kernel(
            self._do_record_event,
            evt,
            operation_name="record_telemetry_event",
            risk_level="low",
            metadata={"event_type": evt.get("type", "unknown")},
        )

    def _do_record_event(self, evt: dict[str, Any]) -> None:
        """Internal implementation of event recording."""
        try:
            with open(self.telemetry_path, encoding="utf-8") as f:
                data = json.load(f)
            data.append(evt)
            with open(self.telemetry_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            logger.exception("Failed to record telemetry")

    def get_summary(self) -> dict[str, Any]:
        try:
            with open(self.telemetry_path, encoding="utf-8") as f:
                data = json.load(f)
            return {"count": len(data)}
        except Exception:
            return {"count": 0}
