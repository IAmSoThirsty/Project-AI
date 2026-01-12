"""UX Feedback / Telemetry Agent

Collects user interactions and produces prioritized suggestions.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class UxTelemetryAgent:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir
        self.telemetry_path = os.path.join(self.data_dir, "telemetry.json")
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.telemetry_path):
            with open(self.telemetry_path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def record_event(self, evt: dict[str, Any]) -> None:
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
