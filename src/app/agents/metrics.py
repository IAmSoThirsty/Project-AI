"""Metrics agent: record and query simple in-memory metrics."""

import time
from typing import Any, Dict, List, Optional


class MetricsAgent:
    """Collect simple numeric metrics with timestamps.

    This stores metrics in-memory and is suitable for local testing. A
    production version would flush to a time-series DB or monitoring system.
    """

    def __init__(self) -> None:
        self._metrics: List[Dict[str, Any]] = []

    def record(
        self, name: str, value: float, tags: Optional[Dict[str, str]] = None
    ) -> None:
        self._metrics.append(
            {"name": name, "value": float(value), "tags": tags or {}, "ts": time.time()}
        )

    def query(self, name: str) -> List[Dict[str, Any]]:
        return [m for m in self._metrics if m.get("name") == name]
