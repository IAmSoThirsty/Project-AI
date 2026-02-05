#!/usr/bin/env python3
"""
Domain 5: Tactical Edge AI Subsystem
Project-AI God Tier Zombie Apocalypse Defense Engine

Provides real-time tactical decision making, threat response optimization,
combat effectiveness analysis, and adaptive strategy generation at the edge.
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


class TacticalDecisionType(Enum):
    ENGAGE = "engage"
    RETREAT = "retreat"
    FORTIFY = "fortify"
    EVACUATE = "evacuate"
    HOLD_POSITION = "hold_position"


class CombatEffectiveness(Enum):
    OVERWHELMING = 95
    SUPERIOR = 80
    ADEQUATE = 60
    MARGINAL = 40
    INADEQUATE = 20


@dataclass
class TacticalSituation:
    situation_id: str
    threat_level: int
    friendly_forces: int
    enemy_forces: int
    terrain_advantage: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TacticalDecision:
    decision_id: str
    situation_id: str
    decision_type: TacticalDecisionType
    confidence: float
    rationale: str
    timestamp: datetime = field(default_factory=datetime.now)


class TacticalEdgeAISubsystem(BaseSubsystem, ICommandable, IMonitorable, IObservable):

    SUBSYSTEM_METADATA = {
        "id": "tactical_edge_ai",
        "name": "Tactical Edge AI",
        "version": "1.0.0",
        "priority": "HIGH",
        "dependencies": ["situational_awareness"],
        "provides_capabilities": [
            "tactical_decision_making",
            "threat_response_optimization",
            "combat_effectiveness_analysis",
        ],
        "config": {"data_dir": "data"},
    }

    def __init__(self, data_dir: str = "data", **config):
        super().__init__(data_dir=data_dir, config=config)

        self.data_path = Path(data_dir) / "tactical_edge_ai"
        self.data_path.mkdir(parents=True, exist_ok=True)

        self._situations: dict[str, TacticalSituation] = {}
        self._decisions: dict[str, TacticalDecision] = {}
        self._lock = threading.Lock()

        self._subscriptions: dict[str, list[tuple]] = {}
        self._subscription_counter = 0
        self._subscription_lock = threading.Lock()

        self._processing_thread: threading.Thread | None = None
        self._processing_active = False

        self._metrics = {
            "decisions_made": 0,
            "successful_engagements": 0,
            "avoided_casualties": 0,
        }
        self._metrics_lock = threading.Lock()

        self.logger.info("Tactical Edge AI subsystem created")

    def initialize(self) -> bool:
        self.logger.info("Initializing Tactical Edge AI subsystem...")

        try:
            self._load_state()

            self._processing_active = True
            self._processing_thread = threading.Thread(
                target=self._processing_loop, daemon=True, name="TacticalProcessing"
            )
            self._processing_thread.start()

            self._initialized = True
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}")
            return False

    def shutdown(self) -> bool:
        try:
            self._processing_active = False
            if self._processing_thread:
                self._processing_thread.join(timeout=5.0)

            self._save_state()
            self._initialized = False
            return True

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            return False

    def health_check(self) -> bool:
        if not self._initialized:
            return False

        if (
            not self._processing_active
            or not self._processing_thread
            or not self._processing_thread.is_alive()
        ):
            return False

        return True

    def get_status(self) -> dict[str, Any]:
        status = super().get_status()

        with self._lock:
            status["active_situations"] = len(self._situations)
            status["decisions_made"] = len(self._decisions)

        with self._metrics_lock:
            status["metrics"] = self._metrics.copy()

        return status

    def execute_command(self, command: SubsystemCommand) -> SubsystemResponse:
        start_time = time.time()

        try:
            if command.command_type == "analyze_situation":
                decision = self._analyze_situation(command.parameters)
                success = decision is not None
                result = {"decision_id": decision.decision_id} if decision else None
            elif command.command_type == "assess_combat_effectiveness":
                effectiveness = self._assess_combat_effectiveness(command.parameters)
                success = True
                result = {"effectiveness": effectiveness}
            else:
                return SubsystemResponse(
                    command_id=command.command_id,
                    success=False,
                    error=f"Unknown command type: {command.command_type}",
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
        return ["analyze_situation", "assess_combat_effectiveness"]

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
                    (sid, cb)
                    for sid, cb in self._subscriptions[event_type]
                    if sid != subscription_id
                ]
            return True

    def emit_event(self, event_type: str, data: Any) -> int:
        with self._subscription_lock:
            subscribers = self._subscriptions.get(event_type, [])

            for subscription_id, callback in subscribers:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Error in event callback {subscription_id}: {e}")

            return len(subscribers)

    def _processing_loop(self):
        while self._processing_active:
            try:
                self._analyze_pending_situations()
                time.sleep(1.0)
            except Exception as e:
                self.logger.error(f"Error in processing loop: {e}")
                time.sleep(1.0)

    def _analyze_pending_situations(self):
        pass

    def _analyze_situation(self, params: dict[str, Any]) -> TacticalDecision | None:
        try:
            situation = TacticalSituation(
                situation_id=str(uuid.uuid4()),
                threat_level=params["threat_level"],
                friendly_forces=params["friendly_forces"],
                enemy_forces=params["enemy_forces"],
                terrain_advantage=params.get("terrain_advantage", 0.5),
            )

            with self._lock:
                self._situations[situation.situation_id] = situation

            # Make tactical decision
            force_ratio = situation.friendly_forces / max(situation.enemy_forces, 1)
            adjusted_ratio = force_ratio * (1 + situation.terrain_advantage)

            if adjusted_ratio >= 2.0:
                decision_type = TacticalDecisionType.ENGAGE
                confidence = 0.9
            elif adjusted_ratio >= 1.0:
                decision_type = TacticalDecisionType.HOLD_POSITION
                confidence = 0.7
            else:
                decision_type = TacticalDecisionType.RETREAT
                confidence = 0.8

            decision = TacticalDecision(
                decision_id=str(uuid.uuid4()),
                situation_id=situation.situation_id,
                decision_type=decision_type,
                confidence=confidence,
                rationale=f"Force ratio: {force_ratio:.2f}, Terrain: {situation.terrain_advantage:.2f}",
            )

            with self._lock:
                self._decisions[decision.decision_id] = decision

            with self._metrics_lock:
                self._metrics["decisions_made"] += 1

            self.emit_event(
                "tactical_decision",
                {
                    "decision_id": decision.decision_id,
                    "decision_type": decision_type.value,
                },
            )

            return decision

        except Exception as e:
            self.logger.error(f"Failed to analyze situation: {e}")
            return None

    def _assess_combat_effectiveness(self, params: dict[str, Any]) -> dict[str, Any]:
        friendly = params.get("friendly_forces", 0)
        enemy = params.get("enemy_forces", 0)

        ratio = friendly / max(enemy, 1)

        if ratio >= 3.0:
            effectiveness = CombatEffectiveness.OVERWHELMING
        elif ratio >= 2.0:
            effectiveness = CombatEffectiveness.SUPERIOR
        elif ratio >= 1.0:
            effectiveness = CombatEffectiveness.ADEQUATE
        elif ratio >= 0.5:
            effectiveness = CombatEffectiveness.MARGINAL
        else:
            effectiveness = CombatEffectiveness.INADEQUATE

        return {
            "effectiveness": effectiveness.name,
            "effectiveness_score": effectiveness.value,
            "force_ratio": ratio,
            "recommendation": self._get_effectiveness_recommendation(effectiveness),
        }

    def _get_effectiveness_recommendation(
        self, effectiveness: CombatEffectiveness
    ) -> str:
        recommendations = {
            CombatEffectiveness.OVERWHELMING: "Press advantage with aggressive tactics",
            CombatEffectiveness.SUPERIOR: "Maintain offensive posture",
            CombatEffectiveness.ADEQUATE: "Proceed with caution",
            CombatEffectiveness.MARGINAL: "Consider tactical withdrawal",
            CombatEffectiveness.INADEQUATE: "Immediate retreat recommended",
        }
        return recommendations.get(effectiveness, "Reassess situation")

    def _save_state(self):
        try:
            state = {"timestamp": datetime.now().isoformat(), "metrics": self._metrics}

            state_file = self.data_path / "state.json"
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")

    def _load_state(self):
        try:
            state_file = self.data_path / "state.json"
            if state_file.exists():
                with open(state_file) as f:
                    state = json.load(f)

                self._metrics = state.get("metrics", self._metrics)

        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
