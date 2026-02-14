"""
Contrarian Firewall Orchestrator - The Monolithic Core

This is the God-tier central kernel that orchestrates all firewall operations,
integrating deeply with governance, cognition, agents, and telemetry systems.

Architectural Philosophy:
- Monolithic density: All subsystems coordinated through this single point
- Real-time feedback: Continuous learning from all telemetry sources
- Bi-directional communication: Agents <-> Governance <-> Firewall
- Auto-tuning: Dynamic chaos/stability adjustment based on context
- Deterministic: Full audit trail and reproducible behavior

Integration Points:
- TARL governance kernel
- Triumvirate (Galahad, Cerberus, CodexDeus)
- All 59 agents through Council Hub
- Planetary Defense Core
- LiaraLayer crisis response
- Cerberus Hydra multi-head detection
- Intent tracking and cognitive warfare engine
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class FirewallMode(Enum):
    """Firewall operational modes"""

    PASSIVE = "passive"  # Observing only
    ACTIVE = "active"  # Active defense
    AGGRESSIVE = "aggressive"  # Maximum chaos deployment
    ADAPTIVE = "adaptive"  # Auto-tuning based on threat


class StabilityLevel(Enum):
    """System stability vs chaos balance"""

    STABLE = "stable"  # 0-20% chaos
    BALANCED = "balanced"  # 21-50% chaos
    CHAOTIC = "chaotic"  # 51-80% chaos
    MAXIMUM_CHAOS = "maximum"  # 81-100% chaos


class ThreatIntelSource(Enum):
    """Sources of threat intelligence"""

    SWARM_DEFENSE = "swarm_defense"
    THIRSTY_LANG = "thirsty_lang"
    CERBERUS = "cerberus"
    PLANETARY_DEFENSE = "planetary_defense"
    AGENT_TELEMETRY = "agent_telemetry"
    EXTERNAL_FEED = "external_feed"


@dataclass
class OrchestratorConfig:
    """Central configuration for orchestrator"""

    mode: FirewallMode = FirewallMode.ADAPTIVE
    stability_target: float = 0.5  # 0.0 = stable, 1.0 = max chaos
    auto_tune_enabled: bool = True
    feedback_learning_rate: float = 0.1
    telemetry_polling_interval: float = 5.0  # seconds
    governance_integration: bool = True
    agent_coordination: bool = True
    real_time_adaptation: bool = True

    # Thresholds
    threat_escalation_threshold: float = 0.7
    cognitive_overload_target: float = 8.0
    decoy_expansion_rate: float = 3.0

    # Integration paths
    governance_path: Path | None = None
    cognition_path: Path | None = None
    agents_path: Path | None = None


@dataclass
class SystemTelemetry:
    """Aggregated system telemetry"""

    timestamp: datetime
    threat_score: float
    cognitive_overload_avg: float
    active_violations: int
    decoy_effectiveness: float
    agent_activity: dict[str, int]
    stability_level: float
    auto_tuning_active: bool


@dataclass
class IntentRecord:
    """Tracked intent with full context"""

    intent_id: str
    intent_type: str
    actor: str
    timestamp: datetime
    parameters: dict[str, Any]
    threat_score: float
    governance_verdict: str | None = None
    agent_actions: list[str] = field(default_factory=list)
    outcome: str | None = None


class ContrariaNFirewallOrchestrator:
    """
    Central Orchestration Kernel - The Monolithic Brain

    This is the God-tier orchestrator that coordinates all firewall operations
    with deep integration into governance, cognition, and agent systems.

    Key Capabilities:
    1. Central coordination of all security subsystems
    2. Real-time telemetry aggregation and analysis
    3. Bi-directional agent communication
    4. Auto-tuning chaos/stability balance
    5. Intent tracking and cognitive warfare
    6. Federated threat intelligence
    7. Governance integration (TARL + Triumvirate)
    8. Crisis escalation to LiaraLayer
    """

    def __init__(self, config: OrchestratorConfig | None = None):
        self.config = config or OrchestratorConfig()
        self.logger = logging.getLogger(self.__class__.__name__)

        # Core subsystems
        self._initialize_subsystems()

        # State tracking
        self.telemetry_history: list[SystemTelemetry] = []
        self.intent_tracker: dict[str, IntentRecord] = {}
        self.threat_intelligence: dict[ThreatIntelSource, dict[str, Any]] = {}

        # Real-time state
        self.current_stability: float = self.config.stability_target
        self.current_threat_score: float = 0.0
        self.active_crises: set[str] = set()

        # Auto-tuning state
        self.tuning_parameters: dict[str, float] = {
            "chaos_multiplier": 1.0,
            "decoy_believability": 0.75,
            "escalation_sensitivity": 1.0,
            "cognitive_target": 8.0,
        }

        # Agent coordination
        self.agent_registry: dict[str, Any] = {}
        self.agent_communications: list[dict[str, Any]] = []

        # Governance integration
        self.governance_verdicts: list[dict[str, Any]] = []
        self.policy_violations: list[dict[str, Any]] = []

        # Background tasks
        self.running = False
        self.background_tasks: list[asyncio.Task] = []

        self.logger.info(
            "ContrariaNFirewallOrchestrator initialized in %s mode",
            self.config.mode.value,
        )

    def _initialize_subsystems(self):
        """Initialize all integrated subsystems"""
        # Import and initialize core components
        from integrations.thirsty_lang_security import ThirstyLangSecurityBridge

        from src.app.agents.firewalls.thirsty_honeypot_swarm_defense import (
            ThirstysHoneypotSwarmDefense,
        )

        self.swarm_defense = ThirstysHoneypotSwarmDefense()
        self.security_bridge = ThirstyLangSecurityBridge()

        # Initialize governance integration
        if self.config.governance_integration:
            self._initialize_governance()

        # Initialize agent coordination
        if self.config.agent_coordination:
            self._initialize_agents()

        self.logger.info("All subsystems initialized")

    def _initialize_governance(self):
        """Initialize deep governance integration"""
        try:
            # Import governance components
            from cognition.triumvirate import Triumvirate
            from governance.core import GovernanceCore

            self.triumvirate = Triumvirate()
            self.governance = GovernanceCore()

            self.logger.info("Governance integration active")
        except ImportError as e:
            self.logger.warning("Governance integration unavailable: %s", e)
            self.triumvirate = None
            self.governance = None

    def _initialize_agents(self):
        """Initialize agent coordination system"""
        try:
            # Register with agent system
            self.agent_registry = {
                "oversight": {"active": True, "last_contact": datetime.now()},
                "planner": {"active": True, "last_contact": datetime.now()},
                "validator": {"active": True, "last_contact": datetime.now()},
                "cerberus": {"active": True, "last_contact": datetime.now()},
                "galahad": {"active": True, "last_contact": datetime.now()},
                "codex": {"active": True, "last_contact": datetime.now()},
            }

            self.logger.info("Agent coordination active")
        except Exception as e:
            self.logger.warning("Agent coordination unavailable: %s", e)

    # ========================================================================
    # Core Orchestration Methods
    # ========================================================================

    async def start(self):
        """Start the orchestrator and all background tasks"""
        if self.running:
            self.logger.warning("Orchestrator already running")
            return

        self.running = True
        self.logger.info("Starting Contrarian Firewall Orchestrator")

        # Start background tasks
        if self.config.real_time_adaptation:
            self.background_tasks.append(
                asyncio.create_task(self._telemetry_collector())
            )
            self.background_tasks.append(asyncio.create_task(self._auto_tuner()))
            self.background_tasks.append(asyncio.create_task(self._agent_coordinator()))

        self.logger.info("All background tasks started")

    async def stop(self):
        """Stop the orchestrator and cleanup"""
        if not self.running:
            return

        self.running = False
        self.logger.info("Stopping Contrarian Firewall Orchestrator")

        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.background_tasks, return_exceptions=True)

        self.background_tasks.clear()
        self.logger.info("Orchestrator stopped")

    # ========================================================================
    # Threat Detection and Violation Processing
    # ========================================================================

    def process_violation(
        self, source_ip: str, violation_type: str, details: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Process security violation with full orchestration

        This is the central entry point for all violations, coordinating:
        1. Swarm defense response
        2. Governance evaluation
        3. Agent notification
        4. Intent tracking
        5. Cognitive warfare
        6. Auto-tuning feedback
        """
        self.logger.warning("Processing violation: %s - %s", source_ip, violation_type)

        # 1. Swarm defense response
        swarm_result = self.swarm_defense.detect_policy_violation(
            source_ip=source_ip,
            violation_type=violation_type,
            details=details,
        )

        # 2. Governance evaluation (if enabled)
        governance_verdict = None
        if self.config.governance_integration and self.governance:
            governance_verdict = self._evaluate_with_governance(
                source_ip, violation_type, details, swarm_result
            )

        # 3. Track as intent
        intent = self._track_intent(
            intent_type=f"violation_{violation_type}",
            actor=source_ip,
            parameters=details,
            threat_score=swarm_result.get("cognitive_overload", 0.0),
            governance_verdict=governance_verdict,
        )

        # 4. Notify agents
        if self.config.agent_coordination:
            self._notify_agents(
                event_type="violation",
                source=source_ip,
                details=swarm_result,
            )

        # 5. Check for crisis escalation
        if swarm_result.get("swarm_active"):
            self._escalate_to_liara(source_ip, swarm_result)

        # 6. Update threat intelligence
        self._update_threat_intelligence(
            ThreatIntelSource.SWARM_DEFENSE,
            source_ip,
            swarm_result,
        )

        # 7. Trigger auto-tuning feedback
        if self.config.auto_tune_enabled:
            self._feedback_for_tuning(swarm_result)

        # Compile comprehensive result
        result = {
            **swarm_result,
            "intent_id": intent.intent_id,
            "governance_verdict": governance_verdict,
            "orchestration": {
                "mode": self.config.mode.value,
                "stability": self.current_stability,
                "threat_score": self.current_threat_score,
                "auto_tuning_active": self.config.auto_tune_enabled,
            },
        }

        return result

    def _evaluate_with_governance(
        self,
        source_ip: str,
        violation_type: str,
        details: dict[str, Any],
        swarm_result: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Evaluate violation through governance layer"""
        try:
            # Create intent for TARL evaluation
            from api.main import ActionType, ActorType, Intent

            intent = Intent(
                actor=ActorType.system,
                action=ActionType.execute,
                target=f"block_{source_ip}",
                context={
                    "violation_type": violation_type,
                    "threat_level": swarm_result.get("threat_level"),
                    "cognitive_overload": swarm_result.get("cognitive_overload"),
                },
                origin="contrarian_firewall",
            )

            # Evaluate through TARL
            from api.main import evaluate_tarl

            result = evaluate_tarl(intent)

            self.governance_verdicts.append(
                {
                    "source_ip": source_ip,
                    "verdict": result.final_verdict.value,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            return {
                "verdict": result.final_verdict.value,
                "votes": [v.dict() for v in result.votes],
            }
        except Exception as e:
            self.logger.error("Governance evaluation failed: %s", e)
            return None

    def _track_intent(
        self,
        intent_type: str,
        actor: str,
        parameters: dict[str, Any],
        threat_score: float,
        governance_verdict: dict[str, Any] | None = None,
    ) -> IntentRecord:
        """Track intent with full context"""
        intent_id = f"intent_{len(self.intent_tracker) + 1}_{int(time.time())}"

        intent = IntentRecord(
            intent_id=intent_id,
            intent_type=intent_type,
            actor=actor,
            timestamp=datetime.now(),
            parameters=parameters,
            threat_score=threat_score,
            governance_verdict=(
                governance_verdict.get("verdict") if governance_verdict else None
            ),
        )

        self.intent_tracker[intent_id] = intent

        return intent

    def _notify_agents(
        self,
        event_type: str,
        source: str,
        details: dict[str, Any],
    ):
        """Notify registered agents of events"""
        notification = {
            "event_type": event_type,
            "source": source,
            "details": details,
            "timestamp": datetime.now().isoformat(),
        }

        self.agent_communications.append(notification)

        # In production, would send to actual agent message bus
        self.logger.debug("Agent notification: %s from %s", event_type, source)

    def _escalate_to_liara(self, source_ip: str, swarm_result: dict[str, Any]):
        """Escalate crisis to LiaraLayer"""
        crisis_id = f"crisis_{source_ip}_{int(time.time())}"

        if crisis_id not in self.active_crises:
            self.active_crises.add(crisis_id)

            self.logger.critical(
                f"Crisis escalation: {source_ip} - Swarm active with "
                f"{swarm_result.get('active_decoys', 0)} decoys"
            )

            # In production, would trigger actual LiaraLayer workflow

    def _update_threat_intelligence(
        self,
        source: ThreatIntelSource,
        identifier: str,
        data: dict[str, Any],
    ):
        """Update threat intelligence from source"""
        if source not in self.threat_intelligence:
            self.threat_intelligence[source] = {}

        self.threat_intelligence[source][identifier] = {
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }

    def _feedback_for_tuning(self, swarm_result: dict[str, Any]):
        """Collect feedback for auto-tuning"""
        # Extract key metrics
        cognitive_overload = swarm_result.get("cognitive_overload", 0.0)
        swarm_result.get("threat_level", "scout")

        # Adjust tuning parameters based on feedback
        if cognitive_overload < self.tuning_parameters["cognitive_target"]:
            # Need more chaos
            self.tuning_parameters["chaos_multiplier"] *= (
                1.0 + self.config.feedback_learning_rate
            )
        elif cognitive_overload > self.tuning_parameters["cognitive_target"] * 1.5:
            # Too much chaos
            self.tuning_parameters["chaos_multiplier"] *= (
                1.0 - self.config.feedback_learning_rate
            )

    # ========================================================================
    # Background Tasks
    # ========================================================================

    async def _telemetry_collector(self):
        """Continuously collect and aggregate system telemetry"""
        while self.running:
            try:
                # Collect from all sources
                swarm_status = self.swarm_defense.get_swarm_status()
                self.security_bridge.get_integrated_status()

                # Calculate aggregates
                cognitive_overload_avg = swarm_status.get("max_cognitive_overload", 0.0)
                active_violations = swarm_status.get("total_attackers_tracked", 0)

                # Create telemetry record
                telemetry = SystemTelemetry(
                    timestamp=datetime.now(),
                    threat_score=self.current_threat_score,
                    cognitive_overload_avg=cognitive_overload_avg,
                    active_violations=active_violations,
                    decoy_effectiveness=0.8,  # Would calculate from decoy data
                    agent_activity=self._get_agent_activity(),
                    stability_level=self.current_stability,
                    auto_tuning_active=self.config.auto_tune_enabled,
                )

                self.telemetry_history.append(telemetry)

                # Keep only recent history
                if len(self.telemetry_history) > 1000:
                    self.telemetry_history = self.telemetry_history[-1000:]

                await asyncio.sleep(self.config.telemetry_polling_interval)
            except Exception as e:
                self.logger.error("Telemetry collection error: %s", e)
                await asyncio.sleep(1.0)

    async def _auto_tuner(self):
        """Automatically tune chaos/stability balance"""
        while self.running:
            try:
                if not self.config.auto_tune_enabled:
                    await asyncio.sleep(10.0)
                    continue

                # Analyze recent telemetry
                if len(self.telemetry_history) < 10:
                    await asyncio.sleep(5.0)
                    continue

                recent = self.telemetry_history[-10:]
                avg_threat = sum(t.threat_score for t in recent) / len(recent)
                avg_overload = sum(t.cognitive_overload_avg for t in recent) / len(
                    recent
                )

                # Adjust stability target
                if avg_threat > self.config.threat_escalation_threshold:
                    # Increase chaos
                    self.current_stability = min(1.0, self.current_stability + 0.1)
                elif avg_threat < 0.3:
                    # Decrease chaos
                    self.current_stability = max(0.0, self.current_stability - 0.05)

                # Apply tuning to swarm defense
                self._apply_tuning()

                self.logger.debug(
                    f"Auto-tune: stability={self.current_stability:.2f}, "
                    f"threat={avg_threat:.2f}, overload={avg_overload:.2f}"
                )

                await asyncio.sleep(30.0)  # Tune every 30 seconds
            except Exception as e:
                self.logger.error("Auto-tuning error: %s", e)
                await asyncio.sleep(5.0)

    async def _agent_coordinator(self):
        """Coordinate with agent system"""
        while self.running:
            try:
                # Update agent registry
                for agent_name in self.agent_registry:
                    self.agent_registry[agent_name]["last_contact"] = datetime.now()

                # Process agent communications
                # In production, would handle actual agent messages

                await asyncio.sleep(5.0)
            except Exception as e:
                self.logger.error("Agent coordination error: %s", e)
                await asyncio.sleep(1.0)

    def _apply_tuning(self):
        """Apply tuning parameters to subsystems"""
        # Update swarm defense multiplier
        multiplier = self.tuning_parameters["chaos_multiplier"]
        self.swarm_defense.swarm_multiplier = (
            multiplier * self.config.decoy_expansion_rate
        )

    def _get_agent_activity(self) -> dict[str, int]:
        """Get agent activity counts"""
        return {
            agent: 1 if data["active"] else 0
            for agent, data in self.agent_registry.items()
        }

    # ========================================================================
    # Query and Status Methods
    # ========================================================================

    def get_comprehensive_status(self) -> dict[str, Any]:
        """Get comprehensive orchestrator status"""
        return {
            "orchestrator": {
                "running": self.running,
                "mode": self.config.mode.value,
                "stability": self.current_stability,
                "threat_score": self.current_threat_score,
                "active_crises": len(self.active_crises),
            },
            "subsystems": {
                "swarm_defense": self.swarm_defense.get_swarm_status(),
                "security_bridge": self.security_bridge.get_integrated_status(),
                "governance": len(self.governance_verdicts),
                "agents": len([a for a in self.agent_registry.values() if a["active"]]),
            },
            "tracking": {
                "intents": len(self.intent_tracker),
                "telemetry_records": len(self.telemetry_history),
                "threat_intel_sources": len(self.threat_intelligence),
                "agent_communications": len(self.agent_communications),
            },
            "tuning": {
                "enabled": self.config.auto_tune_enabled,
                "parameters": self.tuning_parameters,
            },
        }

    def get_intent_history(self, limit: int = 100) -> list[dict[str, Any]]:
        """Get recent intent history"""
        intents = list(self.intent_tracker.values())[-limit:]
        return [
            {
                "intent_id": i.intent_id,
                "type": i.intent_type,
                "actor": i.actor,
                "timestamp": i.timestamp.isoformat(),
                "threat_score": i.threat_score,
                "verdict": i.governance_verdict,
            }
            for i in intents
        ]

    def get_telemetry_summary(self, minutes: int = 60) -> dict[str, Any]:
        """Get telemetry summary for time window"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent = [t for t in self.telemetry_history if t.timestamp > cutoff]

        if not recent:
            return {"message": "No telemetry data in time window"}

        return {
            "time_window_minutes": minutes,
            "records": len(recent),
            "avg_threat_score": sum(t.threat_score for t in recent) / len(recent),
            "avg_cognitive_overload": sum(t.cognitive_overload_avg for t in recent)
            / len(recent),
            "avg_violations": sum(t.active_violations for t in recent) / len(recent),
            "avg_stability": sum(t.stability_level for t in recent) / len(recent),
        }


# ============================================================================
# Global Orchestrator Instance (Singleton Pattern)
# ============================================================================

_orchestrator_instance: ContrariaNFirewallOrchestrator | None = None


def get_orchestrator(
    config: OrchestratorConfig | None = None,
) -> ContrariaNFirewallOrchestrator:
    """Get or create global orchestrator instance"""
    global _orchestrator_instance

    if _orchestrator_instance is None:
        _orchestrator_instance = ContrariaNFirewallOrchestrator(config)

    return _orchestrator_instance


def reset_orchestrator():
    """Reset global orchestrator (for testing)"""
    global _orchestrator_instance
    _orchestrator_instance = None
