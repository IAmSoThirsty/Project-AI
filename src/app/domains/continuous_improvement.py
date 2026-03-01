#!/usr/bin/env python3
"""Domain 9: Continuous Improvement Subsystem"""

import json
import logging
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from ..core.interface_abstractions import (
    BaseSubsystem,
    ICommandable,
    IMonitorable,
    IObservable,
    SubsystemCommand,
    SubsystemResponse,
)

logger = logging.getLogger(__name__)


class ImprovementType(Enum):
    PERFORMANCE = "performance"
    EFFICIENCY = "efficiency"
    CAPABILITY = "capability"


@dataclass
class Improvement:
    improvement_id: str
    type: ImprovementType
    description: str
    impact_score: float


class ContinuousImprovementSubsystem(
    BaseSubsystem, ICommandable, IMonitorable, IObservable
):
    SUBSYSTEM_METADATA = {
        "id": "continuous_improvement",
        "name": "Continuous Improvement",
        "version": "1.0.0",
        "priority": "MEDIUM",
        "dependencies": [],
        "provides_capabilities": [
            "performance_analytics",
            "strategy_optimization",
            "learning",
        ],
        "config": {"data_dir": "data"},
    }

    def __init__(self, data_dir: str = "data", **config):
        super().__init__(data_dir=data_dir, config=config)
        self.data_path = Path(data_dir) / "continuous_improvement"
        self.data_path.mkdir(parents=True, exist_ok=True)
        self._improvements: dict[str, Improvement] = {}
        self._lock = threading.Lock()
        self._subscriptions: dict[str, list[tuple]] = {}
        self._subscription_counter = 0
        self._subscription_lock = threading.Lock()
        self._processing_thread: threading.Thread | None = None
        self._processing_active = False
        self._metrics = {"improvements_identified": 0, "optimizations_applied": 0}
        self._metrics_lock = threading.Lock()

    def initialize(self) -> bool:
        try:
            self._load_state()
            self._processing_active = True
            self._processing_thread = threading.Thread(
                target=self._processing_loop, daemon=True
            )
            self._processing_thread.start()
            self._initialized = True
            return True
        except:
            return False

    def shutdown(self) -> bool:
        self._processing_active = False
        if self._processing_thread:
            self._processing_thread.join(timeout=5.0)
        self._save_state()
        self._initialized = False
        return True

    def health_check(self) -> bool:
        return self._initialized and self._processing_active

    def get_status(self) -> dict[str, Any]:
        status = super().get_status()
        with self._lock:
            status["total_improvements"] = len(self._improvements)
        with self._metrics_lock:
            status["metrics"] = self._metrics.copy()
        return status

    def execute_command(self, command: SubsystemCommand) -> SubsystemResponse:
        start_time = time.time()
        try:
            if command.command_type == "analyze_performance":
                analysis = self._analyze_performance(command.parameters)
                return SubsystemResponse(
                    command.command_id,
                    True,
                    {"analysis": analysis},
                    execution_time_ms=(time.time() - start_time) * 1000,
                )
            return SubsystemResponse(command.command_id, False, error="Unknown command")
        except Exception as e:
            return SubsystemResponse(command.command_id, False, error=str(e))

    def get_supported_commands(self) -> list[str]:
        return ["analyze_performance", "suggest_optimization"]

    def get_metrics(self) -> dict[str, Any]:
        with self._metrics_lock:
            return self._metrics.copy()

    def get_metric(self, metric_name: str) -> Any:
        with self._metrics_lock:
            return self._metrics.get(metric_name)

    def reset_metrics(self) -> bool:
        with self._metrics_lock:
            for key in self._metrics:
                if isinstance(self._metrics[key], (int, float)):
                    self._metrics[key] = 0
        return True

    def subscribe(self, event_type: str, callback: callable) -> str:
        with self._subscription_lock:
            subscription_id = f"sub_{self._subscription_counter}"
            self._subscription_counter += 1
            if event_type not in self._subscriptions:
                self._subscriptions[event_type] = []
            self._subscriptions[event_type].append((subscription_id, callback))
            return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        return True

    def emit_event(self, event_type: str, data: Any) -> int:
        return 0

    def _processing_loop(self):
        while self._processing_active:
            time.sleep(10.0)

    def _analyze_performance(self, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "performance_score": 0.85,
            "bottlenecks": [],
            "recommendations": ["Optimize resource allocation"],
        }

    def _save_state(self):
        try:
            with open(self.data_path / "state.json", "w") as f:
                json.dump({"metrics": self._metrics}, f)
        except:
            pass

    def _load_state(self):
        try:
            state_file = self.data_path / "state.json"
            if state_file.exists():
                with open(state_file) as f:
                    self._metrics = json.load(f).get("metrics", self._metrics)
        except:
            pass
