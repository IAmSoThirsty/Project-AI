#!/usr/bin/env python3
"""
HYDRA-50 Integration Layer

Integrates HYDRA-50 Contingency Plan Engine with:
- Planetary Defense Monolith (constitutional compliance)
- Global Scenario Engine
- God-Tier Command Center
- GUI export hooks

Production-grade integration following Project-AI governance standards.
"""

import logging
from datetime import datetime
from typing import Any

from app.core.hydra_50_engine import (
    Hydra50Engine,
    SCENARIO_REGISTRY,
    ScenarioStatus,
    ControlPlane,
)

logger = logging.getLogger(__name__)


# ============================================================================
# PLANETARY DEFENSE INTEGRATION
# ============================================================================

class PlanetaryDefenseIntegration:
    """Integrate Hydra50 with Planetary Defense Constitutional Core"""

    def __init__(self, hydra_engine: Hydra50Engine):
        self.hydra = hydra_engine
        self.planetary_defense = None  # Lazy load to avoid circular import
        logger.info("PlanetaryDefenseIntegration initialized")

    def _get_planetary_defense(self):
        """Lazy load Planetary Defense Monolith"""
        if self.planetary_defense is None:
            try:
                from app.core.planetary_defense_monolith import PlanetaryDefenseMonolith
                self.planetary_defense = PlanetaryDefenseMonolith()
            except ImportError:
                logger.warning("Planetary Defense Monolith not available")
        return self.planetary_defense

    def validate_mitigation_action(
        self,
        scenario_id: str,
        mitigation_action: str
    ) -> tuple[bool, str]:
        """
        Validate mitigation action through Constitutional Core

        Args:
            scenario_id: Scenario identifier
            mitigation_action: Proposed mitigation action

        Returns:
            (is_allowed, reason) tuple
        """
        pd = self._get_planetary_defense()
        if pd is None:
            # Fallback: allow if no PD available
            return True, "Planetary Defense unavailable - action allowed by default"

        scenario = self.hydra.scenarios.get(scenario_id)
        if not scenario:
            return False, f"Unknown scenario: {scenario_id}"

        # Build context for constitutional validation
        context = {
            "scenario_id": scenario_id,
            "scenario_name": scenario.name,
            "scenario_category": scenario.category.value,
            "escalation_level": scenario.escalation_level.value,
            "is_emergency": scenario.escalation_level.value >= 4,
            "mitigation_type": "automated" if self.hydra.active_control_plane != ControlPlane.HUMAN_OVERRIDE else "human",
        }

        # Validate through Constitutional Core
        try:
            is_allowed, reason = pd.validate_action(
                action=mitigation_action,
                context=context
            )

            if not is_allowed:
                logger.warning(f"Mitigation blocked by Constitutional Core: {mitigation_action} - {reason}")

            return is_allowed, reason

        except Exception as e:
            logger.error(f"Constitutional validation failed: {e}")
            return False, f"Validation error: {e}"

    def feed_threat_assessment(self) -> None:
        """Feed Hydra threat assessments to Planetary Defense"""
        pd = self._get_planetary_defense()
        if pd is None:
            return

        # Get dashboard state
        state = self.hydra.get_dashboard_state()

        # Send threat summary to Planetary Defense
        threat_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "source": "hydra50_engine",
            "active_scenarios": state["active_count"],
            "critical_scenarios": state["critical_count"],
            "irreversible_states": state["irreversible_states"],
            "scenarios": state["active_scenarios"],
        }

        try:
            pd.receive_threat_assessment(threat_data)
            logger.info(f"Threat assessment sent to Planetary Defense: {state['active_count']} active scenarios")
        except Exception as e:
            logger.error(f"Failed to send threat assessment: {e}")

    def run_integrated_tick(self, user_id: str | None = None) -> dict[str, Any]:
        """
        Run Hydra tick with Planetary Defense integration

        Validates all proposed actions through Constitutional Core before execution.
        """
        # Run Hydra tick
        tick_result = self.hydra.run_tick(user_id=user_id)

        # Validate mitigation actions for critical scenarios
        validated_mitigations = []

        for scenario_info in tick_result.get("active_scenarios", []):
            scenario_id = scenario_info["id"]
            scenario = self.hydra.scenarios[scenario_id]

            # Get proposed mitigations from current escalation step
            if scenario.escalation_ladder:
                current_step = None
                for step in scenario.escalation_ladder:
                    if step.level == scenario.escalation_level and step.reached:
                        current_step = step
                        break

                if current_step:
                    for mitigation in current_step.mitigation_actions:
                        is_allowed, reason = self.validate_mitigation_action(scenario_id, mitigation)
                        validated_mitigations.append({
                            "scenario_id": scenario_id,
                            "mitigation": mitigation,
                            "allowed": is_allowed,
                            "reason": reason,
                        })

        # Add validation results to tick result
        tick_result["validated_mitigations"] = validated_mitigations

        # Feed threat assessment to Planetary Defense
        self.feed_threat_assessment()

        return tick_result


# ============================================================================
# GLOBAL SCENARIO ENGINE INTEGRATION
# ============================================================================

class GlobalScenarioEngineIntegration:
    """Integrate Hydra50 as a module within Global Scenario Engine"""

    def __init__(self, hydra_engine: Hydra50Engine):
        self.hydra = hydra_engine
        logger.info("GlobalScenarioEngineIntegration initialized")

    def get_module_info(self) -> dict[str, Any]:
        """Return module metadata for Global Scenario Engine"""
        return {
            "module_id": "hydra50",
            "module_name": "HYDRA-50 Contingency Plan Engine",
            "version": "1.0",
            "scenario_count": 50,
            "categories": ["digital_cognitive", "economic", "infrastructure", "biological_environmental", "societal"],
            "capabilities": [
                "event_sourcing",
                "time_travel_replay",
                "counterfactual_branching",
                "adversarial_modeling",
                "cross_scenario_coupling",
                "human_failure_emulation",
                "irreversibility_detection",
                "false_recovery_detection",
            ],
        }

    def query(self, query_type: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Handle queries from Global Scenario Engine

        Query Types:
        - get_dashboard_state: Return current state summary
        - get_scenario_detail: Return detailed scenario info
        - get_active_scenarios: Return list of active scenarios
        - get_critical_nodes: Return high-coupling scenarios
        - run_tick: Execute simulation tick
        """
        params = params or {}

        if query_type == "get_dashboard_state":
            return self.hydra.get_dashboard_state()

        elif query_type == "get_scenario_detail":
            scenario_id = params.get("scenario_id")
            if not scenario_id or scenario_id not in self.hydra.scenarios:
                return {"error": f"Invalid scenario_id: {scenario_id}"}

            scenario = self.hydra.scenarios[scenario_id]
            return {
                "id": scenario.scenario_id,
                "name": scenario.name,
                "category": scenario.category.value,
                "status": scenario.status.value,
                "escalation_level": scenario.escalation_level.value,
                "metrics": scenario.metrics,
                "active_triggers": [t.name for t in scenario.triggers if t.activated],
                "couplings": [
                    {"target": c.target_scenario_id, "strength": c.coupling_strength, "type": c.coupling_type}
                    for c in scenario.couplings
                ],
            }

        elif query_type == "get_active_scenarios":
            return {
                "active_scenarios": [
                    {"id": s.scenario_id, "name": s.name, "status": s.status.value}
                    for s in self.hydra.scenarios.values()
                    if s.status != ScenarioStatus.DORMANT
                ]
            }

        elif query_type == "get_critical_nodes":
            critical_nodes = self.hydra.adversarial_generator.identify_critical_nodes(
                list(self.hydra.scenarios.values())
            )
            return {"critical_nodes": critical_nodes}

        elif query_type == "run_tick":
            user_id = params.get("user_id")
            return self.hydra.run_tick(user_id=user_id)

        else:
            return {"error": f"Unknown query type: {query_type}"}

    def receive_external_metrics(self, external_data: dict[str, Any]) -> None:
        """
        Receive metrics from external sources via Global Scenario Engine

        Expected format:
        {
            "source": "external_system_name",
            "timestamp": "ISO8601",
            "metrics": {
                "scenario_id": {"metric_name": value, ...},
                ...
            }
        }
        """
        metrics_data = external_data.get("metrics", {})

        for scenario_id, metrics in metrics_data.items():
            if scenario_id in self.hydra.scenarios:
                try:
                    self.hydra.update_scenario_metrics(
                        scenario_id=scenario_id,
                        metrics=metrics,
                        user_id=external_data.get("source")
                    )
                    logger.info(f"Updated {scenario_id} from external source: {external_data.get('source')}")
                except Exception as e:
                    logger.error(f"Failed to update {scenario_id}: {e}")


# ============================================================================
# GOD-TIER COMMAND CENTER INTEGRATION
# ============================================================================

class CommandCenterIntegration:
    """Export Hydra50 widgets and controls to God-Tier Command Center"""

    def __init__(self, hydra_engine: Hydra50Engine):
        self.hydra = hydra_engine
        logger.info("CommandCenterIntegration initialized")

    def get_status_widget_data(self) -> dict[str, Any]:
        """Return data for Command Center status widget"""
        state = self.hydra.get_dashboard_state()

        return {
            "widget_type": "hydra50_status",
            "title": "HYDRA-50 Threat Status",
            "priority": "high" if state["critical_count"] > 0 else "normal",
            "data": {
                "total_scenarios": state["total_scenarios"],
                "active": state["active_count"],
                "critical": state["critical_count"],
                "irreversible": state["irreversible_states"],
                "control_plane": state["control_plane"],
                "human_override": state["human_override"],
            },
            "timestamp": state["timestamp"],
        }

    def get_scenario_list_widget_data(self) -> dict[str, Any]:
        """Return data for scenario list widget"""
        state = self.hydra.get_dashboard_state()

        # Group by category
        by_category = {}
        for scenario_info in state["active_scenarios"]:
            category = scenario_info["category"]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(scenario_info)

        return {
            "widget_type": "hydra50_scenario_list",
            "title": "Active Scenarios",
            "data": {
                "by_category": by_category,
                "total_active": state["active_count"],
            },
            "timestamp": state["timestamp"],
        }

    def get_threat_network_widget_data(self) -> dict[str, Any]:
        """Return data for threat network visualization"""
        active_scenarios = [
            s for s in self.hydra.scenarios.values()
            if s.status != ScenarioStatus.DORMANT
        ]

        # Build network graph
        nodes = []
        edges = []

        for scenario in active_scenarios:
            nodes.append({
                "id": scenario.scenario_id,
                "name": scenario.name,
                "category": scenario.category.value,
                "escalation_level": scenario.escalation_level.value,
            })

            for coupling in scenario.get_active_couplings():
                edges.append({
                    "source": scenario.scenario_id,
                    "target": coupling.target_scenario_id,
                    "strength": coupling.coupling_strength,
                    "type": coupling.coupling_type,
                })

        return {
            "widget_type": "hydra50_threat_network",
            "title": "Threat Coupling Network",
            "data": {
                "nodes": nodes,
                "edges": edges,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    def get_control_panel_data(self) -> dict[str, Any]:
        """Return data for Command Center control panel"""
        return {
            "widget_type": "hydra50_controls",
            "title": "HYDRA-50 Controls",
            "controls": [
                {
                    "id": "run_tick",
                    "label": "Run Simulation Tick",
                    "type": "button",
                    "action": "hydra50.run_tick",
                },
                {
                    "id": "activate_override",
                    "label": "Activate Human Override",
                    "type": "button",
                    "action": "hydra50.activate_human_override",
                    "requires_confirmation": True,
                },
                {
                    "id": "generate_compound",
                    "label": "Generate Compound Scenario",
                    "type": "button",
                    "action": "hydra50.generate_compound_scenario",
                },
                {
                    "id": "control_plane",
                    "label": "Control Plane",
                    "type": "dropdown",
                    "options": ["strategic", "operational", "tactical", "human_override"],
                    "current": self.hydra.active_control_plane.value,
                },
            ],
        }

    def handle_control_action(
        self,
        action: str,
        params: dict[str, Any] | None = None,
        user_id: str | None = None
    ) -> dict[str, Any]:
        """Handle control actions from Command Center"""
        params = params or {}

        try:
            if action == "run_tick":
                result = self.hydra.run_tick(user_id=user_id)
                return {"success": True, "result": result}

            elif action == "activate_human_override":
                reason = params.get("reason", "Manual override from Command Center")
                self.hydra.activate_human_override(user_id=user_id or "command_center", reason=reason)
                return {"success": True, "message": "Human override activated"}

            elif action == "generate_compound_scenario":
                active_scenarios = [
                    s for s in self.hydra.scenarios.values()
                    if s.status != ScenarioStatus.DORMANT
                ]
                compound = self.hydra.adversarial_generator.generate_compound_scenario(active_scenarios)
                return {"success": True, "compound_scenario": compound}

            elif action == "set_control_plane":
                plane_value = params.get("control_plane")
                self.hydra.active_control_plane = ControlPlane(plane_value)
                return {"success": True, "message": f"Control plane set to {plane_value}"}

            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            logger.error(f"Control action failed: {action} - {e}")
            return {"success": False, "error": str(e)}


# ============================================================================
# GUI EXPORT HOOKS
# ============================================================================

class GUIExportHooks:
    """Export functions for PyQt6 GUI integration"""

    def __init__(self, hydra_engine: Hydra50Engine):
        self.hydra = hydra_engine
        logger.info("GUIExportHooks initialized")

    def get_scenario_dropdown_list(self) -> list[dict[str, str]]:
        """Return list of all scenarios for GUI dropdown"""
        return [
            {"id": sid, "name": name}
            for sid, name in SCENARIO_REGISTRY.items()
        ]

    def get_scenario_detail_for_gui(self, scenario_id: str) -> dict[str, Any]:
        """Return full scenario state for GUI display"""
        if scenario_id not in self.hydra.scenarios:
            return {"error": f"Unknown scenario: {scenario_id}"}

        scenario = self.hydra.scenarios[scenario_id]

        return {
            "id": scenario.scenario_id,
            "name": scenario.name,
            "category": scenario.category.value,
            "status": scenario.status.value,
            "escalation_level": {
                "value": scenario.escalation_level.value,
                "name": scenario.escalation_level.name,
            },
            "triggers": [
                {
                    "name": t.name,
                    "description": t.description,
                    "activated": t.activated,
                    "current_value": t.current_value,
                    "threshold": t.threshold_value,
                    "activation_time": t.activation_time.isoformat() if t.activation_time else None,
                }
                for t in scenario.triggers
            ],
            "escalation_ladder": [
                {
                    "level": step.level.value,
                    "level_name": step.level.name,
                    "description": step.description,
                    "reached": step.reached,
                    "time_horizon_days": step.time_horizon.days,
                    "impact_severity": step.impact_severity,
                    "mitigation_actions": step.mitigation_actions,
                }
                for step in scenario.escalation_ladder
            ],
            "couplings": [
                {
                    "target_id": c.target_scenario_id,
                    "target_name": SCENARIO_REGISTRY.get(c.target_scenario_id, "Unknown"),
                    "strength": c.coupling_strength,
                    "type": c.coupling_type,
                    "description": c.description,
                }
                for c in scenario.couplings
            ],
            "collapse_modes": [
                {
                    "name": cm.name,
                    "description": cm.description,
                    "probability": cm.probability,
                    "time_to_collapse_days": cm.time_to_collapse.days,
                    "irreversibility_score": cm.irreversibility_score,
                }
                for cm in scenario.collapse_modes
            ],
            "recovery_poisons": [
                {
                    "name": rp.name,
                    "description": rp.description,
                    "apparent_improvement": rp.apparent_improvement,
                    "hidden_damage": rp.hidden_damage,
                    "detection_difficulty": rp.detection_difficulty,
                    "cost_multiplier": rp.long_term_cost_multiplier,
                }
                for rp in scenario.recovery_poisons
            ],
            "metrics": scenario.metrics,
        }

    def get_dashboard_summary_for_gui(self) -> dict[str, Any]:
        """Return dashboard summary optimized for GUI display"""
        state = self.hydra.get_dashboard_state()

        # Add additional GUI-friendly data
        active_by_category = {}
        critical_scenarios_details = []

        for scenario_info in state["active_scenarios"]:
            category = scenario_info["category"]
            if category not in active_by_category:
                active_by_category[category] = []
            active_by_category[category].append(scenario_info)

            if scenario_info["escalation_level"] >= 4:
                critical_scenarios_details.append(scenario_info)

        return {
            "timestamp": state["timestamp"],
            "totals": {
                "total_scenarios": state["total_scenarios"],
                "active": state["active_count"],
                "critical": state["critical_count"],
                "irreversible": state["irreversible_states"],
                "poison_deployments": state["poison_deployments"],
            },
            "control": {
                "plane": state["control_plane"],
                "human_override": state["human_override"],
            },
            "active_by_category": active_by_category,
            "critical_scenarios": critical_scenarios_details,
            "event_log_size": state["event_log_size"],
        }

    def update_scenario_from_gui(
        self,
        scenario_id: str,
        metric_name: str,
        metric_value: float,
        user_id: str = "gui_user"
    ) -> dict[str, Any]:
        """Update a single scenario metric from GUI"""
        try:
            self.hydra.update_scenario_metrics(
                scenario_id=scenario_id,
                metrics={metric_name: metric_value},
                user_id=user_id
            )
            return {
                "success": True,
                "scenario_id": scenario_id,
                "updated_metric": metric_name,
                "new_value": metric_value,
            }
        except Exception as e:
            logger.error(f"GUI metric update failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }


# ============================================================================
# UNIFIED INTEGRATION MANAGER
# ============================================================================

class Hydra50IntegrationManager:
    """Unified manager for all Hydra50 integrations"""

    def __init__(self, data_dir: str = "data/hydra50"):
        """Initialize Hydra50 engine and all integrations"""
        # Initialize core engine
        self.hydra = Hydra50Engine(data_dir=data_dir)

        # Initialize integration modules
        self.planetary_defense = PlanetaryDefenseIntegration(self.hydra)
        self.global_scenario_engine = GlobalScenarioEngineIntegration(self.hydra)
        self.command_center = CommandCenterIntegration(self.hydra)
        self.gui_hooks = GUIExportHooks(self.hydra)

        logger.info("Hydra50IntegrationManager fully initialized")

    def get_hydra_engine(self) -> Hydra50Engine:
        """Get direct access to Hydra50 engine"""
        return self.hydra

    def run_integrated_tick(self, user_id: str | None = None) -> dict[str, Any]:
        """
        Run a full integrated tick:
        1. Execute Hydra tick
        2. Validate through Planetary Defense
        3. Update Command Center widgets
        4. Return comprehensive results
        """
        # Run tick with PD integration
        tick_result = self.planetary_defense.run_integrated_tick(user_id=user_id)

        # Add Command Center widget data
        tick_result["command_center_widgets"] = {
            "status": self.command_center.get_status_widget_data(),
            "scenario_list": self.command_center.get_scenario_list_widget_data(),
            "threat_network": self.command_center.get_threat_network_widget_data(),
        }

        return tick_result

    def export_for_gui(self) -> dict[str, Any]:
        """Export all data needed for GUI"""
        return {
            "scenarios": self.gui_hooks.get_scenario_dropdown_list(),
            "dashboard": self.gui_hooks.get_dashboard_summary_for_gui(),
            "timestamp": datetime.utcnow().isoformat(),
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_integrated_hydra_instance(data_dir: str = "data/hydra50") -> Hydra50IntegrationManager:
    """
    Factory function to create fully integrated Hydra50 instance

    Usage:
        from app.core.hydra_50_integration import create_integrated_hydra_instance

        manager = create_integrated_hydra_instance()

        # Access engine directly
        engine = manager.get_hydra_engine()

        # Or use integrations
        tick_result = manager.run_integrated_tick()
        gui_data = manager.export_for_gui()
    """
    return Hydra50IntegrationManager(data_dir=data_dir)


def export_gui_hooks(hydra_engine: Hydra50Engine) -> GUIExportHooks:
    """
    Create GUI export hooks for an existing Hydra50 engine

    Usage:
        from app.core.hydra_50_engine import Hydra50Engine
        from app.core.hydra_50_integration import export_gui_hooks

        engine = Hydra50Engine()
        gui = export_gui_hooks(engine)

        scenarios = gui.get_scenario_dropdown_list()
        details = gui.get_scenario_detail_for_gui("S01")
    """
    return GUIExportHooks(hydra_engine)
