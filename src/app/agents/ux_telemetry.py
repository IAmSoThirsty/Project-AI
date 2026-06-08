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
    def __init__(
        self, data_dir: str = "data", kernel: CognitionKernel | None = None
    ) -> None:
        # Initialize kernel routing (COGNITION KERNEL INTEGRATION)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",
        )
        self.data_dir = data_dir
        self.telemetry_path = os.path.join(self.data_dir, "telemetry.jsonl")
        old_telemetry_path = os.path.join(self.data_dir, "telemetry.json")
        os.makedirs(self.data_dir, exist_ok=True)

        # Migrate old JSON array format to JSONL if it exists
        if os.path.exists(old_telemetry_path):
            try:
                with open(old_telemetry_path, "r", encoding="utf-8") as f:
                    old_data = json.load(f)
                with open(self.telemetry_path, "w", encoding="utf-8") as f:
                    for item in old_data:
                        f.write(json.dumps(item) + "\n")
                os.remove(old_telemetry_path)
            except Exception:
                logger.exception("Failed to migrate old telemetry.json")

        if not os.path.exists(self.telemetry_path):
            # Create an empty file
            open(self.telemetry_path, "w").close()

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
            with open(self.telemetry_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(evt) + "\n")
        except Exception:
            logger.exception("Failed to record telemetry")

    def get_summary(self) -> dict[str, Any]:
        try:
            count = 0
            with open(self.telemetry_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        count += 1
            return {"count": count}
        except Exception:
            return {"count": 0}
