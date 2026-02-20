#!/usr/bin/env python3
"""
Domain 4: Biomedical Defense Subsystem
Project-AI God Tier Zombie Apocalypse Defense Engine

Provides comprehensive biomedical defense including infection detection,
medical resource management, quarantine protocols, and research tracking.
"""

import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
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


class InfectionStatus(Enum):
    UNINFECTED = "uninfected"
    EXPOSED = "exposed"
    EARLY_INFECTION = "early_infection"
    ADVANCED_INFECTION = "advanced_infection"
    TERMINAL = "terminal"
    IMMUNE = "immune"


class QuarantineLevel(Enum):
    NONE = 0
    OBSERVATION = 2
    ISOLATION = 5
    STRICT_CONTAINMENT = 8
    TOTAL_LOCKDOWN = 10


@dataclass
class PatientRecord:
    patient_id: str
    name: str
    infection_status: InfectionStatus
    first_contact: datetime = field(default_factory=datetime.now)
    quarantine_level: QuarantineLevel = QuarantineLevel.NONE
    location: str | None = None


class BiomedicalDefenseSubsystem(BaseSubsystem, ICommandable, IMonitorable, IObservable):

    SUBSYSTEM_METADATA = {
        "id": "biomedical_defense",
        "name": "Biomedical Defense",
        "version": "1.0.0",
        "priority": "CRITICAL",
        "dependencies": ["situational_awareness"],
        "provides_capabilities": [
            "infection_detection",
            "medical_resource_management",
            "quarantine_protocols",
        ],
        "config": {"data_dir": "data"},
    }

    def __init__(self, data_dir: str = "data", **config):
        super().__init__(data_dir=data_dir, config=config)

        self.data_path = Path(data_dir) / "biomedical_defense"
        self.data_path.mkdir(parents=True, exist_ok=True)

        self._patients: dict[str, PatientRecord] = {}
        self._patient_lock = threading.Lock()
        self._subscriptions: dict[str, list[tuple[str, callable]]] = {}
        self._subscription_counter = 0
        self._subscription_lock = threading.Lock()
        self._processing_thread: threading.Thread | None = None
        self._processing_active = False

        self._metrics = {
            "patients_treated": 0,
            "infections_detected": 0,
            "recoveries": 0,
            "fatalities": 0,
        }
        self._metrics_lock = threading.Lock()

        self.logger.info("Biomedical Defense subsystem created")

    def initialize(self) -> bool:
        self.logger.info("Initializing Biomedical Defense subsystem...")

        try:
            self._load_state()

            self._processing_active = True
            self._processing_thread = threading.Thread(
                target=self._processing_loop, daemon=True, name="BiomedicalProcessing"
            )
            self._processing_thread.start()

            self._initialized = True
            self.logger.info("Biomedical Defense subsystem initialized successfully")
            return True

        except Exception as e:
            self.logger.error("Failed to initialize: %s", e)
            return False

    def shutdown(self) -> bool:
        self.logger.info("Shutting down Biomedical Defense subsystem...")

        try:
            self._processing_active = False
            if self._processing_thread:
                self._processing_thread.join(timeout=5.0)

            self._save_state()

            self._initialized = False
            return True

        except Exception as e:
            self.logger.error("Error during shutdown: %s", e)
            return False

    def health_check(self) -> bool:
        if not self._initialized:
            return False

        return not (
            not self._processing_active or not self._processing_thread or not self._processing_thread.is_alive()
        )

    def get_status(self) -> dict[str, Any]:
        status = super().get_status()

        with self._patient_lock:
            status["total_patients"] = len(self._patients)

        with self._metrics_lock:
            status["metrics"] = self._metrics.copy()

        return status

    def execute_command(self, command: SubsystemCommand) -> SubsystemResponse:
        start_time = time.time()

        try:
            if command.command_type == "register_patient":
                patient = self._register_patient(command.parameters)
                success = patient is not None
                result = {"patient_id": patient.patient_id} if patient else None
            else:
                success = False
                result = None
                error = f"Unknown command type: {command.command_type}"

                return SubsystemResponse(
                    command_id=command.command_id,
                    success=False,
                    error=error,
                    execution_time_ms=(time.time() - start_time) * 1000,
                )

            return SubsystemResponse(
                command_id=command.command_id,
                success=success,
                result=result,
                execution_time_ms=(time.time() - start_time) * 1000,
            )

        except Exception as e:
            return SubsystemResponse(
                command_id=command.command_id,
                success=False,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )

    def get_supported_commands(self) -> list[str]:
        return ["register_patient"]

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

            for subscription_id, callback in subscribers:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error("Error in event callback %s: %s", subscription_id, e)

            return len(subscribers)

    def _processing_loop(self):
        while self._processing_active:
            try:
                self._monitor_patients()
                time.sleep(10.0)
            except Exception as e:
                self.logger.error("Error in processing loop: %s", e)
                time.sleep(10.0)

    def _monitor_patients(self):
        pass

    def _register_patient(self, params: dict[str, Any]) -> PatientRecord | None:
        try:
            patient = PatientRecord(
                patient_id=str(uuid.uuid4()),
                name=params["name"],
                infection_status=InfectionStatus[params.get("infection_status", "UNINFECTED")],
                location=params.get("location"),
            )

            with self._patient_lock:
                self._patients[patient.patient_id] = patient

            with self._metrics_lock:
                self._metrics["patients_treated"] += 1

            self.emit_event("patient_registered", {"patient_id": patient.patient_id})

            return patient

        except Exception as e:
            self.logger.error("Failed to register patient: %s", e)
            return None

    def _save_state(self):
        try:
            state = {"timestamp": datetime.now().isoformat(), "metrics": self._metrics}

            state_file = self.data_path / "state.json"
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2, default=str)

        except Exception as e:
            self.logger.error("Failed to save state: %s", e)

    def _load_state(self):
        try:
            state_file = self.data_path / "state.json"
            if state_file.exists():
                with open(state_file) as f:
                    state = json.load(f)

                self._metrics = state.get("metrics", self._metrics)

        except Exception as e:
            self.logger.error("Failed to load state: %s", e)
