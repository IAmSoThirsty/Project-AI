"""
Operational Substructure Framework - Decision Contracts, Signals & Telemetry, Failure Semantics

This module provides the foundational infrastructure for extending all AGI components
with operational semantics that define:
1. What decisions each component can make (Decision Contracts)
2. What it emits upward and sideways (Signals & Telemetry)
3. What happens when it degrades or fails (Failure Semantics)

This transforms governance and architecture from philosophy into enforceable law.

=== OPERATIONAL SUBSTRUCTURE SPECIFICATION ===

## CORE PRINCIPLES

Every 3rd-row node in the architecture must answer three questions:
1. What decisions am I allowed to make?
2. What signals do I emit?
3. What happens when I fail?

## THREE PILLARS

### A. DECISION CONTRACTS
Formal specifications of decision-making authority and boundaries.
- Defines scope of autonomous decisions
- Establishes authorization requirements
- Specifies override conditions
- Documents decision rationale requirements

### B. SIGNALS & TELEMETRY
Observable outputs for monitoring and coordination.
- Upward signals: Status, health, alerts to parent systems
- Sideways signals: Coordination messages to peer systems
- Event emissions: Audit trail, decision logs, state changes
- Telemetry metrics: Performance, usage, resource consumption

### C. FAILURE SEMANTICS
Behavior specification for degraded or failed states.
- Graceful degradation paths
- Failover mechanisms
- Human escalation triggers
- Emergency protocols
- Recovery procedures

=== END SPECIFICATION ===
"""

import logging
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Type Definitions
# ============================================================================


class SignalType(Enum):
    """Types of signals that can be emitted."""

    STATUS = "status"  # Regular status update
    ALERT = "alert"  # Warning or concern
    EMERGENCY = "emergency"  # Critical situation
    AUDIT = "audit"  # Audit trail event
    METRIC = "metric"  # Performance/usage metric
    COORDINATION = "coordination"  # Peer-to-peer coordination
    ESCALATION = "escalation"  # Escalation to higher authority


class SeverityLevel(Enum):
    """Severity levels for signals and failures."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    FATAL = "fatal"


class FailureMode(Enum):
    """Types of failure modes."""

    DEGRADED = "degraded"  # Reduced functionality
    PARTIAL_FAILURE = "partial_failure"  # Some functions unavailable
    TOTAL_FAILURE = "total_failure"  # Complete failure
    CORRUPTED = "corrupted"  # Data/state corruption detected
    COMPROMISED = "compromised"  # Security compromise


class AuthorizationLevel(Enum):
    """Authorization levels for decision-making."""

    AUTONOMOUS = "autonomous"  # Can decide independently
    SUPERVISED = "supervised"  # Requires monitoring
    APPROVAL_REQUIRED = "approval_required"  # Must get approval
    HUMAN_ONLY = "human_only"  # Only humans can decide


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class DecisionAuthority:
    """
    Defines what decisions a component is authorized to make.

    Attributes:
        decision_type: Type of decision (e.g., "memory_write", "policy_enforcement")
        authorization_level: Level of autonomy for this decision
        constraints: Additional constraints or requirements
        override_conditions: Conditions under which decision can be overridden
        rationale_required: Whether decision must be explained
        audit_required: Whether decision must be logged
    """

    decision_type: str
    authorization_level: AuthorizationLevel
    constraints: dict[str, Any] = field(default_factory=dict)
    override_conditions: list[str] = field(default_factory=list)
    rationale_required: bool = True
    audit_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "decision_type": self.decision_type,
            "authorization_level": self.authorization_level.value,
            "constraints": self.constraints,
            "override_conditions": self.override_conditions,
            "rationale_required": self.rationale_required,
            "audit_required": self.audit_required,
        }


@dataclass
class Signal:
    """
    A signal emitted by a component.

    Attributes:
        signal_id: Unique identifier for this signal
        signal_type: Type of signal
        severity: Severity level
        source: Component that emitted the signal
        timestamp: When the signal was emitted
        payload: Signal data
        destination: Target component(s) for the signal
        correlation_id: ID for correlating related signals
    """

    signal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signal_type: SignalType = SignalType.STATUS
    severity: SeverityLevel = SeverityLevel.INFO
    source: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    payload: dict[str, Any] = field(default_factory=dict)
    destination: list[str] = field(default_factory=list)
    correlation_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "signal_id": self.signal_id,
            "signal_type": self.signal_type.value,
            "severity": self.severity.value,
            "source": self.source,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "destination": self.destination,
            "correlation_id": self.correlation_id,
        }


@dataclass
class FailureResponse:
    """
    Defines how a component responds to failure.

    Attributes:
        failure_mode: Type of failure
        detection_timestamp: When failure was detected
        degradation_path: Sequence of graceful degradation steps
        failover_target: Component to fail over to
        escalation_required: Whether to escalate to human
        recovery_procedure: Steps to attempt recovery
        emergency_protocol: Emergency actions if recovery fails
    """

    failure_mode: FailureMode
    detection_timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat()
    )
    degradation_path: list[str] = field(default_factory=list)
    failover_target: str | None = None
    escalation_required: bool = False
    recovery_procedure: list[str] = field(default_factory=list)
    emergency_protocol: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "failure_mode": self.failure_mode.value,
            "detection_timestamp": self.detection_timestamp,
            "degradation_path": self.degradation_path,
            "failover_target": self.failover_target,
            "escalation_required": self.escalation_required,
            "recovery_procedure": self.recovery_procedure,
            "emergency_protocol": self.emergency_protocol,
        }


# ============================================================================
# Base Classes
# ============================================================================


class DecisionContract(ABC):
    """
    Base class for decision contracts.

    A decision contract defines what decisions a component can make,
    under what conditions, and with what constraints.
    """

    def __init__(self, component_name: str):
        """
        Initialize decision contract.

        Args:
            component_name: Name of the component this contract governs
        """
        self.component_name = component_name
        self.authorities: dict[str, DecisionAuthority] = {}
        self.decision_log: list[dict[str, Any]] = []

    def register_authority(self, authority: DecisionAuthority) -> None:
        """
        Register a decision authority.

        Args:
            authority: DecisionAuthority to register
        """
        self.authorities[authority.decision_type] = authority
        logger.debug("[%s] Registered decision authority: %s", self.component_name, authority.decision_type)

    def check_authorization(
        self, decision_type: str, context: dict[str, Any] | None = None
    ) -> tuple[bool, str]:
        """
        Check if a decision is authorized.

        Args:
            decision_type: Type of decision to check
            context: Additional context for authorization check

        Returns:
            Tuple of (authorized: bool, reason: str)
        """
        if decision_type not in self.authorities:
            return False, f"No authority defined for decision type: {decision_type}"

        authority = self.authorities[decision_type]

        # Check authorization level
        if authority.authorization_level == AuthorizationLevel.HUMAN_ONLY:
            return False, "This decision requires human authorization"

        if authority.authorization_level == AuthorizationLevel.APPROVAL_REQUIRED:
            if not context or not context.get("approval_granted"):
                return False, "This decision requires approval before execution"

        # Check constraints
        if context:
            for constraint_key, constraint_value in authority.constraints.items():
                if constraint_key in context:
                    if context[constraint_key] != constraint_value:
                        return (
                            False,
                            f"Constraint violation: {constraint_key} must be {constraint_value}",
                        )

        return True, "Authorization granted"

    def log_decision(
        self,
        decision_type: str,
        decision_data: dict[str, Any],
        rationale: str | None = None,
    ) -> None:
        """
        Log a decision for audit trail.

        Args:
            decision_type: Type of decision made
            decision_data: Data about the decision
            rationale: Explanation of decision rationale
        """
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "component": self.component_name,
            "decision_type": decision_type,
            "decision_data": decision_data,
            "rationale": rationale,
        }
        self.decision_log.append(log_entry)

        if decision_type in self.authorities:
            if self.authorities[decision_type].audit_required:
                logger.info("[%s] Decision: %s - %s", self.component_name, decision_type, rationale)

    @abstractmethod
    def get_contract_specification(self) -> dict[str, Any]:
        """
        Get the full contract specification.

        Returns:
            Dictionary containing all contract details
        """
        pass


class SignalsTelemetry(ABC):
    """
    Base class for signals and telemetry.

    Manages emission of signals for monitoring, coordination, and audit.
    """

    def __init__(self, component_name: str):
        """
        Initialize signals and telemetry.

        Args:
            component_name: Name of the component emitting signals
        """
        self.component_name = component_name
        self.signal_history: list[Signal] = []
        self.signal_handlers: dict[SignalType, list[Callable]] = {}
        self.metrics: dict[str, Any] = {}

    def emit_signal(self, signal: Signal) -> None:
        """
        Emit a signal.

        Args:
            signal: Signal to emit
        """
        signal.source = self.component_name
        self.signal_history.append(signal)

        # Log based on severity
        log_msg = f"[{self.component_name}] Signal: {signal.signal_type.value} - {signal.payload.get('message', 'No message')}"

        if signal.severity == SeverityLevel.CRITICAL:
            logger.critical(log_msg)
        elif signal.severity == SeverityLevel.ERROR:
            logger.error(log_msg)
        elif signal.severity == SeverityLevel.WARNING:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        # Call registered handlers
        if signal.signal_type in self.signal_handlers:
            for handler in self.signal_handlers[signal.signal_type]:
                try:
                    handler(signal)
                except Exception as e:
                    logger.error(
                        f"[{self.component_name}] Signal handler error: {e}",
                        exc_info=True,
                    )

    def register_signal_handler(
        self, signal_type: SignalType, handler: Callable[[Signal], None]
    ) -> None:
        """
        Register a handler for a signal type.

        Args:
            signal_type: Type of signal to handle
            handler: Callback function for handling signal
        """
        if signal_type not in self.signal_handlers:
            self.signal_handlers[signal_type] = []
        self.signal_handlers[signal_type].append(handler)

    def record_metric(self, metric_name: str, value: Any) -> None:
        """
        Record a telemetry metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        self.metrics[metric_name] = {
            "value": value,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def get_metrics(self) -> dict[str, Any]:
        """
        Get current telemetry metrics.

        Returns:
            Dictionary of metrics
        """
        return self.metrics.copy()

    @abstractmethod
    def get_telemetry_specification(self) -> dict[str, Any]:
        """
        Get the full telemetry specification.

        Returns:
            Dictionary containing all telemetry details
        """
        pass


class FailureSemantics(ABC):
    """
    Base class for failure semantics.

    Defines how a component behaves when degraded or failed.
    """

    def __init__(self, component_name: str):
        """
        Initialize failure semantics.

        Args:
            component_name: Name of the component
        """
        self.component_name = component_name
        self.current_failure_mode: FailureMode | None = None
        self.failure_history: list[FailureResponse] = []
        self.recovery_callbacks: dict[FailureMode, list[Callable]] = {}

    def detect_failure(
        self, failure_mode: FailureMode, context: dict[str, Any] | None = None
    ) -> FailureResponse:
        """
        Detect and respond to failure.

        Args:
            failure_mode: Type of failure detected
            context: Additional failure context

        Returns:
            FailureResponse object
        """
        self.current_failure_mode = failure_mode

        response = self.create_failure_response(failure_mode, context or {})
        self.failure_history.append(response)

        logger.error("[%s] Failure detected: %s - Escalation: %s", self.component_name, failure_mode.value, response.escalation_required)

        # Execute recovery callbacks
        if failure_mode in self.recovery_callbacks:
            for callback in self.recovery_callbacks[failure_mode]:
                try:
                    callback(response)
                except Exception as e:
                    logger.error(
                        f"[{self.component_name}] Recovery callback error: {e}",
                        exc_info=True,
                    )

        return response

    def register_recovery_callback(
        self, failure_mode: FailureMode, callback: Callable[[FailureResponse], None]
    ) -> None:
        """
        Register a recovery callback for a failure mode.

        Args:
            failure_mode: Type of failure
            callback: Recovery callback function
        """
        if failure_mode not in self.recovery_callbacks:
            self.recovery_callbacks[failure_mode] = []
        self.recovery_callbacks[failure_mode].append(callback)

    def clear_failure(self) -> None:
        """Clear current failure state."""
        self.current_failure_mode = None
        logger.info("[%s] Failure cleared - returning to normal operation", self.component_name)

    @abstractmethod
    def create_failure_response(
        self, failure_mode: FailureMode, context: dict[str, Any]
    ) -> FailureResponse:
        """
        Create a failure response for a given failure mode.

        Args:
            failure_mode: Type of failure
            context: Failure context

        Returns:
            FailureResponse object
        """
        pass

    @abstractmethod
    def get_failure_specification(self) -> dict[str, Any]:
        """
        Get the full failure semantics specification.

        Returns:
            Dictionary containing all failure handling details
        """
        pass


# ============================================================================
# Operational Component Base Class
# ============================================================================


class OperationalComponent:
    """
    Base class for components with full operational substructure.

    Any component that extends this class automatically gets:
    - Decision contracts
    - Signals & telemetry
    - Failure semantics
    """

    def __init__(
        self,
        component_name: str,
        decision_contract: DecisionContract,
        signals_telemetry: SignalsTelemetry,
        failure_semantics: FailureSemantics,
    ):
        """
        Initialize operational component.

        Args:
            component_name: Name of the component
            decision_contract: Decision contract implementation
            signals_telemetry: Signals & telemetry implementation
            failure_semantics: Failure semantics implementation
        """
        self.component_name = component_name
        self.decision_contract = decision_contract
        self.signals_telemetry = signals_telemetry
        self.failure_semantics = failure_semantics

        logger.info("[%s] Operational component initialized with full substructure", component_name)

    def get_operational_status(self) -> dict[str, Any]:
        """
        Get complete operational status.

        Returns:
            Dictionary with decision contracts, telemetry, and failure state
        """
        return {
            "component": self.component_name,
            "timestamp": datetime.now(UTC).isoformat(),
            "decision_contract": self.decision_contract.get_contract_specification(),
            "telemetry": self.signals_telemetry.get_telemetry_specification(),
            "failure_semantics": self.failure_semantics.get_failure_specification(),
            "current_failure_mode": (
                self.failure_semantics.current_failure_mode.value
                if self.failure_semantics.current_failure_mode
                else None
            ),
            "metrics": self.signals_telemetry.get_metrics(),
        }


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    # Enums
    "SignalType",
    "SeverityLevel",
    "FailureMode",
    "AuthorizationLevel",
    # Data Classes
    "DecisionAuthority",
    "Signal",
    "FailureResponse",
    # Base Classes
    "DecisionContract",
    "SignalsTelemetry",
    "FailureSemantics",
    "OperationalComponent",
]
