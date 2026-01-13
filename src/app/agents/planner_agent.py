"""Planner / Scheduler Agent

Decomposes tasks to smaller agents and schedules them.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Any

logger = logging.getLogger(__name__)


class PlannerAgent:
    def __init__(self) -> None:
        self.queue: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def schedule(self, task: dict[str, Any]) -> None:
        with self._lock:
            self.queue.append(task)
        logger.info("Task scheduled: %s", task.get("name"))

    def run_next(self) -> dict[str, Any]:
        with self._lock:
            if not self.queue:
                return {"success": False, "error": "empty"}
            task = self.queue.pop(0)
        # naive execution: log and return
        logger.info("Executing task: %s", task.get("name"))
        time.sleep(0.01)
        return {"success": True, "task": task}
