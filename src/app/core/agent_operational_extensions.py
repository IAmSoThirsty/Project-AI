"""
Agent System Operational Extensions

This module extends the Agent System (Planner, Oversight, Validator, Explainability) with:
1. Authority Scope - Max planning horizon, cross-agent call limits, execution boundaries
2. Tool Access Map - Which tools each agent can use and under what conditions
3. Explanation Obligation - Mandatory explainability hooks and transparency requirements
4. Monitoring Scope - What each agent monitors and how it reports

This makes agents inspectable, not mystical, and enforces operational constraints.
"""

import logging
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any, Callable

from src.app.core.operational_substructure import (
    AuthorizationLevel,
    DecisionAuthority,
    DecisionContract,
    FailureMode,
    FailureResponse,
    FailureSemantics,
    SeverityLevel,
    Signal,
    SignalsTelemetry,
    SignalType,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Agent-Specific Enums
# ============================================================================


class AgentAuthority(Enum):
    """Authority levels for agent operations."""

    READ_ONLY = "read_only"
    ANALYSIS = "analysis"
    RECOMMENDATION = "recommendation"
    EXECUTION = "execution"
    COORDINATION = "coordination"


class ToolAccessLevel(Enum):
    """Tool access levels for agents."""

    NO_ACCESS = "no_access"
    READ_ONLY = "read_only"
    LIMITED_WRITE = "limited_write"
    FULL_ACCESS = "full_access"


class ExplanationDepth(Enum):
    """Depth of explanation required."""

    MINIMAL = "minimal"  # Basic what happened
    STANDARD = "standard"  # What, why
    DETAILED = "detailed"  # What, why, how, alternatives
    EXHAUSTIVE = "exhaustive"  # Complete reasoning trace


# ============================================================================
# Planner Agent Operational Extensions
# ============================================================================


class PlannerDecisionContract(DecisionContract):
    """
    Decision contracts for Planner Agent.

    Defines authority scope, planning horizon, and execution boundaries.
    """

    def __init__(self):
        """Initialize Planner decision contract."""
        super().__init__("PlannerAgent")
        self._register_authorities()

    def _register_authorities(self):
        """Register all decision authorities for Planner Agent."""

        # Task Decomposition
        self.register_authority(
            DecisionAuthority(
                decision_type="task_decomposition",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "max_subtasks": 20,
                    "max_depth": 5,
                    "must_be_achievable": True,
                },
                override_conditions=["user_explicit_simplification"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Planning Horizon Authorization
        self.register_authority(
            DecisionAuthority(
                decision_type="planning_horizon_extension",
                authorization_level=AuthorizationLevel.SUPERVISED,
                constraints={
                    "max_planning_horizon_days": 30,
                    "requires_user_approval_beyond": 7,
                },
                override_conditions=["emergency_long_term_planning"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Cross-Agent Call Authorization
        self.register_authority(
            DecisionAuthority(
                decision_type="cross_agent_call",
                authorization_level=AuthorizationLevel.SUPERVISED,
                constraints={
                    "max_agents_per_plan": 5,
                    "no_circular_dependencies": True,
                    "coordination_protocol_required": True,
                },
                override_conditions=["complex_multi_agent_coordination"],
                rationale_required=True,
                audit_required=True,
            )
        )

        # Resource Allocation
        self.register_authority(
            DecisionAuthority(
                decision_type="resource_allocation",
                authorization_level=AuthorizationLevel.SUPERVISED,
                constraints={
                    "budget_constraint_checked": True,
                    "resource_availability_verified": True,
                },
                override_conditions=["emergency_resource_override"],
                rationale_required=True,
                audit_required=True,
            )
        )

    def get_contract_specification(self) -> dict[str, Any]:
        """Get Planner Agent's complete contract specification."""
        return {
            "agent": "PlannerAgent",
            "focus": "Task Planning, Workflow Orchestration, Resource Allocation",
            "authorities": {
                dt: auth.to_dict() for dt, auth in self.authorities.items()
            },
            "decision_count": len(self.decision_log),
            "authority_scope": {
                "max_planning_horizon": "30 days (7 days autonomous)",
                "max_subtasks": "20 per task",
                "max_decomposition_depth": "5 levels",
                "max_agents_per_plan": "5 agents",
            },
            "coordination_limits": {
                "no_circular_dependencies": True,
                "requires_coordination_protocol": True,
                "must_respect_agent_boundaries": True,
            },
        }


class PlannerSignalsTelemetry(SignalsTelemetry):
    """Signals and telemetry for Planner Agent."""

    def __init__(self):
        """Initialize Planner signals and telemetry."""
        super().__init__("PlannerAgent")

    def emit_plan_created(
        self, plan_id: str, num_subtasks: int, estimated_duration: timedelta
    ) -> None:
        """Emit plan creation signal."""
        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=SeverityLevel.INFO,
            payload={
                "message": f"Plan created: {plan_id}",
                "plan_id": plan_id,
                "num_subtasks": num_subtasks,
                "estimated_duration_hours": estimated_duration.total_seconds() / 3600,
            },
            destination=["Oversight", "AuditLog"],
        )
        self.emit_signal(signal)

    def emit_planning_limit_exceeded(
        self, limit_type: str, attempted: int, allowed: int
    ) -> None:
        """Emit signal when planning limit exceeded."""
        signal = Signal(
            signal_type=SignalType.ALERT,
            severity=SeverityLevel.WARNING,
            payload={
                "message": f"Planning limit exceeded: {limit_type}",
                "limit_type": limit_type,
                "attempted": attempted,
                "allowed": allowed,
            },
            destination=["Oversight", "Triumvirate"],
        )
        self.emit_signal(signal)

    def get_telemetry_specification(self) -> dict[str, Any]:
        """Get Planner Agent's telemetry specification."""
        return {
            "agent": "PlannerAgent",
            "signal_types": {
                "plan_created": "New task plan created",
                "planning_limit_exceeded": "Planning constraint violated",
                "cross_agent_coordination": "Coordinating with other agents",
            },
            "signal_count": len(self.signal_history),
        }


class PlannerFailureSemantics(FailureSemantics):
    """Failure semantics for Planner Agent."""

    def __init__(self):
        """Initialize Planner failure semantics."""
        super().__init__("PlannerAgent")

    def create_failure_response(
        self, failure_mode: FailureMode, context: dict[str, Any]
    ) -> FailureResponse:
        """Create failure response for Planner failures."""
        if failure_mode == FailureMode.DEGRADED:
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_simple_planning_mode",
                    "reduce_max_subtasks",
                    "disable_multi_agent_coordination",
                    "use_template_based_planning",
                ],
                failover_target="Template Planner",
                escalation_required=False,
                recovery_procedure=[
                    "restart_planning_engine",
                    "validate_planning_constraints",
                ],
                emergency_protocol="manual_planning_assistance",
            )
        else:
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=["disable_planner", "route_to_human"],
                failover_target="Human Planner",
                escalation_required=True,
                recovery_procedure=["full_restart_required"],
                emergency_protocol="human_task_decomposition",
            )

    def get_failure_specification(self) -> dict[str, Any]:
        """Get Planner Agent's failure semantics specification."""
        return {
            "agent": "PlannerAgent",
            "failure_modes": {
                "simple_planning_mode": "Reduced capabilities, template-based",
                "manual_planning": "Human provides task decomposition",
            },
            "failure_count": len(self.failure_history),
        }


# ============================================================================
# Oversight Agent Operational Extensions
# ============================================================================


class OversightDecisionContract(DecisionContract):
    """Decision contracts for Oversight Agent."""

    def __init__(self):
        """Initialize Oversight decision contract."""
        super().__init__("OversightAgent")
        self._register_authorities()

    def _register_authorities(self):
        """Register all decision authorities for Oversight Agent."""

        # Monitoring Scope Authorization
        self.register_authority(
            DecisionAuthority(
                decision_type="monitoring_scope",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "all_agents_monitored": True,
                    "governance_visible": True,
                },
                override_conditions=[],  # Cannot reduce monitoring
                rationale_required=False,
                audit_required=True,
            )
        )

        # Compliance Enforcement
        self.register_authority(
            DecisionAuthority(
                decision_type="compliance_enforcement",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "policy_violation_detected": True,
                    "evidence_documented": True,
                },
                override_conditions=[],  # Cannot bypass compliance
                rationale_required=True,
                audit_required=True,
            )
        )

        # Alert Escalation
        self.register_authority(
            DecisionAuthority(
                decision_type="alert_escalation",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "severity_threshold_met": True,
                    "escalation_path_defined": True,
                },
                override_conditions=["false_positive_confirmed"],
                rationale_required=True,
                audit_required=True,
            )
        )

    def get_contract_specification(self) -> dict[str, Any]:
        """Get Oversight Agent's complete contract specification."""
        return {
            "agent": "OversightAgent",
            "focus": "System Monitoring, Compliance, Health Tracking",
            "authorities": {
                dt: auth.to_dict() for dt, auth in self.authorities.items()
            },
            "decision_count": len(self.decision_log),
            "monitoring_scope": {
                "agents_monitored": "All agents",
                "systems_monitored": "All core systems",
                "governance_visibility": "Full transparency to Triumvirate",
            },
        }


class OversightSignalsTelemetry(SignalsTelemetry):
    """Signals and telemetry for Oversight Agent."""

    def __init__(self):
        """Initialize Oversight signals and telemetry."""
        super().__init__("OversightAgent")

    def emit_compliance_violation(
        self, violator: str, violation_type: str, details: dict[str, Any]
    ) -> None:
        """Emit compliance violation signal."""
        signal = Signal(
            signal_type=SignalType.ALERT,
            severity=SeverityLevel.ERROR,
            payload={
                "message": f"Compliance violation: {violator} - {violation_type}",
                "violator": violator,
                "violation_type": violation_type,
                "details": details,
            },
            destination=["Cerberus", "Triumvirate", "AuditLog"],
        )
        self.emit_signal(signal)

    def emit_health_status(
        self, component: str, health_status: str, metrics: dict[str, Any]
    ) -> None:
        """Emit component health status signal."""
        severity = (
            SeverityLevel.ERROR
            if health_status == "unhealthy"
            else SeverityLevel.WARNING if health_status == "degraded" else SeverityLevel.INFO
        )

        signal = Signal(
            signal_type=SignalType.STATUS,
            severity=severity,
            payload={
                "message": f"Health status: {component} - {health_status}",
                "component": component,
                "health_status": health_status,
                "metrics": metrics,
            },
            destination=["TelemetryCollector"],
        )
        self.emit_signal(signal)

    def get_telemetry_specification(self) -> dict[str, Any]:
        """Get Oversight Agent's telemetry specification."""
        return {
            "agent": "OversightAgent",
            "signal_types": {
                "compliance_violation": "Policy or rule violation detected",
                "health_status": "Component health updates",
                "alert_escalation": "Alerts escalated to higher authority",
            },
            "signal_count": len(self.signal_history),
        }


class OversightFailureSemantics(FailureSemantics):
    """Failure semantics for Oversight Agent."""

    def __init__(self):
        """Initialize Oversight failure semantics."""
        super().__init__("OversightAgent")

    def create_failure_response(
        self, failure_mode: FailureMode, context: dict[str, Any]
    ) -> FailureResponse:
        """Create failure response for Oversight failures."""
        if failure_mode == FailureMode.DEGRADED:
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_critical_monitoring_only_mode",
                    "prioritize_compliance_checks",
                    "defer_non_critical_monitoring",
                ],
                failover_target="Basic Monitoring",
                escalation_required=True,
                recovery_procedure=["restart_monitoring_services"],
                emergency_protocol="enhanced_manual_oversight",
            )
        else:
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=["disable_oversight", "escalate_to_cerberus"],
                failover_target="Cerberus + Human",
                escalation_required=True,
                recovery_procedure=["full_oversight_restart"],
                emergency_protocol="manual_system_monitoring",
            )

    def get_failure_specification(self) -> dict[str, Any]:
        """Get Oversight Agent's failure semantics specification."""
        return {
            "agent": "OversightAgent",
            "failure_modes": {
                "critical_monitoring_only": "Monitor only critical systems",
                "manual_oversight": "Human monitors all systems",
            },
            "failure_count": len(self.failure_history),
        }


# ============================================================================
# Validator Agent Operational Extensions
# ============================================================================


class ValidatorDecisionContract(DecisionContract):
    """Decision contracts for Validator Agent."""

    def __init__(self):
        """Initialize Validator decision contract."""
        super().__init__("ValidatorAgent")
        self._register_authorities()

    def _register_authorities(self):
        """Register all decision authorities for Validator Agent."""

        # Input Validation
        self.register_authority(
            DecisionAuthority(
                decision_type="input_validation",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "schema_validation_required": True,
                    "type_checking_required": True,
                },
                override_conditions=[],  # Cannot skip validation
                rationale_required=False,
                audit_required=False,  # High-frequency operation
            )
        )

        # Output Validation
        self.register_authority(
            DecisionAuthority(
                decision_type="output_validation",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "safety_check_required": True,
                    "format_validation_required": True,
                },
                override_conditions=[],  # Cannot skip validation
                rationale_required=False,
                audit_required=False,  # High-frequency operation
            )
        )

        # Data Integrity Check
        self.register_authority(
            DecisionAuthority(
                decision_type="data_integrity_check",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "checksum_validated": True,
                    "corruption_detected": False,
                },
                override_conditions=[],  # Cannot bypass integrity checks
                rationale_required=True,
                audit_required=True,
            )
        )

    def get_contract_specification(self) -> dict[str, Any]:
        """Get Validator Agent's complete contract specification."""
        return {
            "agent": "ValidatorAgent",
            "focus": "Input/Output Validation, Data Integrity",
            "authorities": {
                dt: auth.to_dict() for dt, auth in self.authorities.items()
            },
            "decision_count": len(self.decision_log),
            "validation_scope": {
                "input_validation": "All inputs validated before processing",
                "output_validation": "All outputs validated before emission",
                "data_integrity": "All data checked for corruption",
            },
        }


class ValidatorSignalsTelemetry(SignalsTelemetry):
    """Signals and telemetry for Validator Agent."""

    def __init__(self):
        """Initialize Validator signals and telemetry."""
        super().__init__("ValidatorAgent")

    def emit_validation_failure(
        self, validation_type: str, reason: str, details: dict[str, Any]
    ) -> None:
        """Emit validation failure signal."""
        signal = Signal(
            signal_type=SignalType.ALERT,
            severity=SeverityLevel.WARNING,
            payload={
                "message": f"Validation failed: {validation_type} - {reason}",
                "validation_type": validation_type,
                "reason": reason,
                "details": details,
            },
            destination=["Cerberus", "AuditLog"],
        )
        self.emit_signal(signal)

    def get_telemetry_specification(self) -> dict[str, Any]:
        """Get Validator Agent's telemetry specification."""
        return {
            "agent": "ValidatorAgent",
            "signal_types": {
                "validation_failure": "Validation check failed",
                "integrity_violation": "Data integrity compromised",
            },
            "signal_count": len(self.signal_history),
        }


class ValidatorFailureSemantics(FailureSemantics):
    """Failure semantics for Validator Agent."""

    def __init__(self):
        """Initialize Validator failure semantics."""
        super().__init__("ValidatorAgent")

    def create_failure_response(
        self, failure_mode: FailureMode, context: dict[str, Any]
    ) -> FailureResponse:
        """Create failure response for Validator failures."""
        if failure_mode == FailureMode.DEGRADED:
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_basic_validation_mode",
                    "use_simple_type_checking",
                    "defer_complex_validation",
                ],
                failover_target="Basic Validator",
                escalation_required=False,
                recovery_procedure=["restart_validation_engine"],
                emergency_protocol="manual_validation",
            )
        else:
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=["disable_validator", "reject_all_inputs"],
                failover_target="Manual Validation",
                escalation_required=True,
                recovery_procedure=["full_validator_restart"],
                emergency_protocol="human_input_review",
            )

    def get_failure_specification(self) -> dict[str, Any]:
        """Get Validator Agent's failure semantics specification."""
        return {
            "agent": "ValidatorAgent",
            "failure_modes": {
                "basic_validation": "Simple type checking only",
                "reject_all": "Reject all inputs until recovery",
            },
            "failure_count": len(self.failure_history),
        }


# ============================================================================
# Explainability Agent Operational Extensions
# ============================================================================


class ExplainabilityDecisionContract(DecisionContract):
    """Decision contracts for Explainability Agent."""

    def __init__(self):
        """Initialize Explainability decision contract."""
        super().__init__("ExplainabilityAgent")
        self._register_authorities()

    def _register_authorities(self):
        """Register all decision authorities for Explainability Agent."""

        # Explanation Generation
        self.register_authority(
            DecisionAuthority(
                decision_type="explanation_generation",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "reasoning_trace_available": True,
                    "depth_appropriate": True,
                },
                override_conditions=["user_requests_more_detail"],
                rationale_required=False,
                audit_required=True,
            )
        )

        # Transparency Obligation
        self.register_authority(
            DecisionAuthority(
                decision_type="transparency_obligation",
                authorization_level=AuthorizationLevel.AUTONOMOUS,
                constraints={
                    "all_decisions_explainable": True,
                    "no_black_boxes": True,
                },
                override_conditions=[],  # Cannot reduce transparency
                rationale_required=True,
                audit_required=True,
            )
        )

    def get_contract_specification(self) -> dict[str, Any]:
        """Get Explainability Agent's complete contract specification."""
        return {
            "agent": "ExplainabilityAgent",
            "focus": "Decision Transparency, Reasoning Traces, Explanations",
            "authorities": {
                dt: auth.to_dict() for dt, auth in self.authorities.items()
            },
            "decision_count": len(self.decision_log),
            "explanation_obligations": {
                "all_decisions_explainable": True,
                "reasoning_traces_preserved": True,
                "user_can_request_detail": True,
            },
        }


class ExplainabilitySignalsTelemetry(SignalsTelemetry):
    """Signals and telemetry for Explainability Agent."""

    def __init__(self):
        """Initialize Explainability signals and telemetry."""
        super().__init__("ExplainabilityAgent")

    def emit_explanation_provided(
        self, decision_id: str, depth: ExplanationDepth, explanation: str
    ) -> None:
        """Emit explanation provided signal."""
        signal = Signal(
            signal_type=SignalType.AUDIT,
            severity=SeverityLevel.DEBUG,
            payload={
                "message": f"Explanation provided: {decision_id}",
                "decision_id": decision_id,
                "depth": depth.value,
                "explanation_length": len(explanation),
            },
            destination=["AuditLog"],
        )
        self.emit_signal(signal)

    def get_telemetry_specification(self) -> dict[str, Any]:
        """Get Explainability Agent's telemetry specification."""
        return {
            "agent": "ExplainabilityAgent",
            "signal_types": {
                "explanation_provided": "Explanation generated for decision",
                "transparency_violation": "Decision without explanation detected",
            },
            "signal_count": len(self.signal_history),
        }


class ExplainabilityFailureSemantics(FailureSemantics):
    """Failure semantics for Explainability Agent."""

    def __init__(self):
        """Initialize Explainability failure semantics."""
        super().__init__("ExplainabilityAgent")

    def create_failure_response(
        self, failure_mode: FailureMode, context: dict[str, Any]
    ) -> FailureResponse:
        """Create failure response for Explainability failures."""
        if failure_mode == FailureMode.DEGRADED:
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "enter_basic_explanation_mode",
                    "provide_minimal_explanations",
                    "preserve_reasoning_traces",
                ],
                failover_target="Template Explanations",
                escalation_required=False,
                recovery_procedure=["restart_explanation_engine"],
                emergency_protocol="manual_explanation_assistance",
            )
        else:
            return FailureResponse(
                failure_mode=failure_mode,
                degradation_path=[
                    "disable_explainability",
                    "preserve_all_traces",
                    "flag_unexplained_decisions",
                ],
                failover_target="Human Explanation",
                escalation_required=True,
                recovery_procedure=["full_explainability_restart"],
                emergency_protocol="human_provides_explanations",
            )

    def get_failure_specification(self) -> dict[str, Any]:
        """Get Explainability Agent's failure semantics specification."""
        return {
            "agent": "ExplainabilityAgent",
            "failure_modes": {
                "basic_explanation": "Template-based explanations only",
                "manual_explanation": "Human provides explanations",
            },
            "failure_count": len(self.failure_history),
        }


# ============================================================================
# Tool Access Map
# ============================================================================


class ToolAccessMap:
    """
    Manages which tools each agent can access and under what conditions.
    """

    def __init__(self):
        """Initialize tool access map."""
        self.access_map: dict[str, dict[str, ToolAccessLevel]] = {}
        self._initialize_default_access()

    def _initialize_default_access(self):
        """Initialize default tool access permissions."""

        # Planner Agent
        self.access_map["PlannerAgent"] = {
            "task_decomposer": ToolAccessLevel.FULL_ACCESS,
            "resource_allocator": ToolAccessLevel.FULL_ACCESS,
            "agent_coordinator": ToolAccessLevel.LIMITED_WRITE,
            "memory_system": ToolAccessLevel.READ_ONLY,
            "governance_system": ToolAccessLevel.READ_ONLY,
        }

        # Oversight Agent
        self.access_map["OversightAgent"] = {
            "monitoring_dashboard": ToolAccessLevel.READ_ONLY,
            "compliance_checker": ToolAccessLevel.FULL_ACCESS,
            "alert_system": ToolAccessLevel.FULL_ACCESS,
            "audit_logger": ToolAccessLevel.FULL_ACCESS,
            "governance_system": ToolAccessLevel.READ_ONLY,
        }

        # Validator Agent
        self.access_map["ValidatorAgent"] = {
            "schema_validator": ToolAccessLevel.FULL_ACCESS,
            "type_checker": ToolAccessLevel.FULL_ACCESS,
            "integrity_checker": ToolAccessLevel.FULL_ACCESS,
            "sanitizer": ToolAccessLevel.FULL_ACCESS,
        }

        # Explainability Agent
        self.access_map["ExplainabilityAgent"] = {
            "reasoning_tracer": ToolAccessLevel.READ_ONLY,
            "explanation_generator": ToolAccessLevel.FULL_ACCESS,
            "decision_log": ToolAccessLevel.READ_ONLY,
            "audit_system": ToolAccessLevel.READ_ONLY,
        }

    def check_tool_access(
        self, agent: str, tool: str
    ) -> tuple[bool, ToolAccessLevel]:
        """
        Check if agent has access to tool.

        Args:
            agent: Agent name
            tool: Tool name

        Returns:
            Tuple of (has_access, access_level)
        """
        if agent not in self.access_map:
            return False, ToolAccessLevel.NO_ACCESS

        access_level = self.access_map[agent].get(tool, ToolAccessLevel.NO_ACCESS)

        has_access = access_level != ToolAccessLevel.NO_ACCESS

        return has_access, access_level

    def grant_tool_access(
        self, agent: str, tool: str, access_level: ToolAccessLevel
    ) -> None:
        """
        Grant tool access to agent.

        Args:
            agent: Agent name
            tool: Tool name
            access_level: Access level to grant
        """
        if agent not in self.access_map:
            self.access_map[agent] = {}

        self.access_map[agent][tool] = access_level

        logger.info(f"Granted {access_level.value} access to {tool} for {agent}")

    def revoke_tool_access(self, agent: str, tool: str) -> None:
        """
        Revoke tool access from agent.

        Args:
            agent: Agent name
            tool: Tool name
        """
        if agent in self.access_map and tool in self.access_map[agent]:
            del self.access_map[agent][tool]
            logger.info(f"Revoked access to {tool} for {agent}")


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    # Enums
    "AgentAuthority",
    "ToolAccessLevel",
    "ExplanationDepth",
    # Planner
    "PlannerDecisionContract",
    "PlannerSignalsTelemetry",
    "PlannerFailureSemantics",
    # Oversight
    "OversightDecisionContract",
    "OversightSignalsTelemetry",
    "OversightFailureSemantics",
    # Validator
    "ValidatorDecisionContract",
    "ValidatorSignalsTelemetry",
    "ValidatorFailureSemantics",
    # Explainability
    "ExplainabilityDecisionContract",
    "ExplainabilitySignalsTelemetry",
    "ExplainabilityFailureSemantics",
    # Tool Access
    "ToolAccessMap",
]
