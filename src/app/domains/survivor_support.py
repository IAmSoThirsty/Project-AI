#!/usr/bin/env python3
"""Domain 6: Survivor Support Subsystem"""

import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
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


class SurvivorStatus(Enum):
    SAFE = "safe"
    AT_RISK = "at_risk"
    RESCUED = "rescued"


@dataclass
class Survivor:
    survivor_id: str
    name: str
    status: SurvivorStatus
    needs: list[str] = field(default_factory=list)


class SurvivorSupportSubsystem(BaseSubsystem, ICommandable, IMonitorable, IObservable):
    SUBSYSTEM_METADATA = {
        "id": "survivor_support",
        "name": "Survivor Support",
        "version": "1.0.0",
        "priority": "HIGH",
        "dependencies": [],
        "provides_capabilities": ["survivor_registry", "rescue_coordination"],
        "config": {"data_dir": "data"},
    }

    def __init__(self, data_dir: str = "data", **config):
        super().__init__(data_dir=data_dir, config=config)
        self.data_path = Path(data_dir) / "survivor_support"
        self.data_path.mkdir(parents=True, exist_ok=True)
        self._survivors: dict[str, Survivor] = {}
        self._lock = threading.Lock()
        self._subscriptions: dict[str, list[tuple]] = {}
        self._subscription_counter = 0
        self._subscription_lock = threading.Lock()
        self._processing_thread: threading.Thread | None = None
        self._processing_active = False
        self._metrics = {"survivors_registered": 0, "rescues_completed": 0}
        self._metrics_lock = threading.Lock()

    def initialize(self) -> bool:
        try:
            self._load_state()
            self._processing_active = True
            self._processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            self._processing_thread.start()
            self._initialized = True
            return True
        except Exception as e:
            logger.error("Init failed: %s", e)
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
            status["total_survivors"] = len(self._survivors)
        with self._metrics_lock:
            status["metrics"] = self._metrics.copy()
        return status

    def execute_command(self, command: SubsystemCommand) -> SubsystemResponse:
        start_time = time.time()
        try:
            if command.command_type == "register_survivor":
                survivor = self._register_survivor(command.parameters)
                return SubsystemResponse(
                    command.command_id,
                    survivor is not None,
                    {"survivor_id": survivor.survivor_id} if survivor else None,
                    execution_time_ms=(time.time() - start_time) * 1000,
                )
            return SubsystemResponse(command.command_id, False, error="Unknown command")
        except Exception as e:
            return SubsystemResponse(command.command_id, False, error=str(e))

    def get_supported_commands(self) -> list[str]:
        return ["register_survivor"]

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
        with self._subscription_lock:
            for event_type in self._subscriptions:
                self._subscriptions[event_type] = [
                    (sid, cb) for sid, cb in self._subscriptions[event_type] if sid != subscription_id
                ]
            return True

    def emit_event(self, event_type: str, data: Any) -> int:
        with self._subscription_lock:
            subscribers = self._subscriptions.get(event_type, [])
            for _, callback in subscribers:
                try:
                    callback(data)
                except:
                    pass
            return len(subscribers)

    def _processing_loop(self):
        while self._processing_active:
            time.sleep(5.0)

    def _register_survivor(self, params: dict[str, Any]) -> Survivor | None:
        try:
            survivor = Survivor(
                str(uuid.uuid4()),
                params["name"],
                SurvivorStatus[params.get("status", "AT_RISK")],
            )
            with self._lock:
                self._survivors[survivor.survivor_id] = survivor
            with self._metrics_lock:
                self._metrics["survivors_registered"] += 1
            return survivor
        except:
            return None

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
                    state = json.load(f)
                self._metrics = state.get("metrics", self._metrics)
        except:
            pass
