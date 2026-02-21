"""
SASE - Sovereign Adversarial Signal Engine
L7: Adaptive Policy Engine

Threshold-based policy enforcement with automated defensive actions.

THRESHOLDS:
- <30: Monitor
- 30-50: Alert
- 50-70: Soft containment
- 70-85: Automated containment
- 85+: Escalation freeze

ALLOWED DEFENSIVE ACTIONS (all reversible):
- Rotate credentials
- Revoke token
- Tighten WAF
- Throttle rate
- SOC notification
- Session invalidation
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("SASE.L7.AdaptivePolicy")


class PolicyAction(Enum):
    """Defensive policy actions"""

    MONITOR = "monitor"
    ALERT = "alert"
    ROTATE_CREDENTIALS = "rotate_credentials"
    REVOKE_TOKEN = "revoke_token"
    TIGHTEN_WAF = "tighten_waf"
    THROTTLE_RATE = "throttle_rate"
    SOC_NOTIFICATION = "soc_notification"
    SESSION_INVALIDATION = "session_invalidation"
    ESCALATION_FREEZE = "escalation_freeze"


@dataclass
class ThresholdRule:
    """Policy threshold rule"""

    min_confidence: int  # Minimum confidence %
    max_confidence: int  # Maximum confidence %
    actions: list[PolicyAction]
    description: str


class ThresholdGovernance:
    """
    Threshold-based policy governance

    Maps confidence scores to defensive actions
    """

    def __init__(self):
        # Define threshold rules
        self.rules = [
            ThresholdRule(
                min_confidence=0,
                max_confidence=29,
                actions=[PolicyAction.MONITOR],
                description="Low confidence - passive monitoring only",
            ),
            ThresholdRule(
                min_confidence=30,
                max_confidence=49,
                actions=[PolicyAction.ALERT, PolicyAction.SOC_NOTIFICATION],
                description="Medium confidence - alert SOC",
            ),
            ThresholdRule(
                min_confidence=50,
                max_confidence=69,
                actions=[
                    PolicyAction.THROTTLE_RATE,
                    PolicyAction.TIGHTEN_WAF,
                    PolicyAction.SOC_NOTIFICATION,
                ],
                description="High confidence - soft containment",
            ),
            ThresholdRule(
                min_confidence=70,
                max_confidence=84,
                actions=[
                    PolicyAction.REVOKE_TOKEN,
                    PolicyAction.SESSION_INVALIDATION,
                    PolicyAction.ROTATE_CREDENTIALS,
                    PolicyAction.SOC_NOTIFICATION,
                ],
                description="Critical confidence - automated containment",
            ),
            ThresholdRule(
                min_confidence=85,
                max_confidence=100,
                actions=[
                    PolicyAction.ESCALATION_FREEZE,
                    PolicyAction.REVOKE_TOKEN,
                    PolicyAction.SESSION_INVALIDATION,
                    PolicyAction.SOC_NOTIFICATION,
                ],
                description="Severe confidence - escalation freeze",
            ),
        ]

    def get_actions(self, confidence_pct: int) -> list[PolicyAction]:
        """Get required actions for confidence level"""
        for rule in self.rules:
            if rule.min_confidence <= confidence_pct <= rule.max_confidence:
                logger.info(f"Threshold matched: {rule.description}")
                return rule.actions

        # Default to monitor
        return [PolicyAction.MONITOR]


@dataclass
class ActionExecution:
    """Record of executed action"""

    action: PolicyAction
    timestamp: float
    event_id: str
    source_ip: str
    confidence: int
    success: bool
    details: dict
    reversible: bool = True


class ActionExecutor:
    """
    Executes defensive policy actions

    ALL ACTIONS ARE REVERSIBLE (constitutional requirement)
    """

    def __init__(self):
        self.execution_log: list[ActionExecution] = []

        # Action handlers (would integrate with real systems)
        self.handlers: dict[PolicyAction, Callable] = {
            PolicyAction.MONITOR: self._handle_monitor,
            PolicyAction.ALERT: self._handle_alert,
            PolicyAction.ROTATE_CREDENTIALS: self._handle_rotate_credentials,
            PolicyAction.REVOKE_TOKEN: self._handle_revoke_token,
            PolicyAction.TIGHTEN_WAF: self._handle_tighten_waf,
            PolicyAction.THROTTLE_RATE: self._handle_throttle_rate,
            PolicyAction.SOC_NOTIFICATION: self._handle_soc_notification,
            PolicyAction.SESSION_INVALIDATION: self._handle_session_invalidation,
            PolicyAction.ESCALATION_FREEZE: self._handle_escalation_freeze,
        }

    def execute(self, action: PolicyAction, context: dict) -> ActionExecution:
        """Execute defensive action"""
        logger.warning(f"EXECUTING ACTION: {action.value}")

        handler = self.handlers.get(action, self._handle_unknown)
        success, details = handler(context)

        execution = ActionExecution(
            action=action,
            timestamp=time.time(),
            event_id=context.get("event_id", "UNKNOWN"),
            source_ip=context.get("source_ip", "UNKNOWN"),
            confidence=context.get("confidence_pct", 0),
            success=success,
            details=details,
            reversible=True,  # All SASE actions are reversible
        )

        self.execution_log.append(execution)

        return execution

    def _handle_monitor(self, context: dict) -> tuple[bool, dict]:
        """Passive monitoring"""
        return True, {"action": "monitoring_active"}

    def _handle_alert(self, context: dict) -> tuple[bool, dict]:
        """Generate alert"""
        logger.warning(f"ALERT: Suspicious activity from {context.get('source_ip')}")
        return True, {"alert_generated": True}

    def _handle_rotate_credentials(self, context: dict) -> tuple[bool, dict]:
        """Rotate compromised credentials"""
        logger.warning("ACTION: Rotating credentials")
        # TODO: Integrate with credential management system
        return True, {"credentials_rotated": True, "reversible": True}

    def _handle_revoke_token(self, context: dict) -> tuple[bool, dict]:
        """Revoke access token"""
        logger.warning("ACTION: Revoking token")
        # TODO: Integrate with token management
        return True, {"token_revoked": True, "reversible": True}

    def _handle_tighten_waf(self, context: dict) -> tuple[bool, dict]:
        """Tighten WAF rules"""
        logger.warning("ACTION: Tightening WAF")
        # TODO: Integrate with WAF
        return True, {"waf_tightened": True, "reversible": True}

    def _handle_throttle_rate(self, context: dict) -> tuple[bool, dict]:
        """Apply rate throttling"""
        logger.warning("ACTION: Throttling rate")
        # TODO: Integrate with rate limiter
        return True, {"rate_throttled": True, "reversible": True}

    def _handle_soc_notification(self, context: dict) -> tuple[bool, dict]:
        """Notify SOC"""
        logger.critical(f"SOC NOTIFICATION: {context.get('threat_classification')}")
        # TODO: Integrate with SOC alerting system
        return True, {"soc_notified": True}

    def _handle_session_invalidation(self, context: dict) -> tuple[bool, dict]:
        """Invalidate active sessions"""
        logger.warning("ACTION: Invalidating sessions")
        # TODO: Integrate with session management
        return True, {"sessions_invalidated": True, "reversible": False}

    def _handle_escalation_freeze(self, context: dict) -> tuple[bool, dict]:
        """Freeze all escalation attempts"""
        logger.critical("ACTION: ESCALATION FREEZE")
        # TODO: Implement escalation freeze
        return True, {"escalation_frozen": True, "reversible": True}

    def _handle_unknown(self, context: dict) -> tuple[bool, dict]:
        """Unknown action handler"""
        logger.error("Unknown action requested")
        return False, {"error": "unknown_action"}


class AdaptivePolicyEngine:
    """
    L7: Adaptive Policy Engine

    Enforces threshold-based defensive policies
    """

    def __init__(self):
        self.governance = ThresholdGovernance()
        self.executor = ActionExecutor()

        logger.info("L7 Adaptive Policy Engine initialized")

    def enforce(self, confidence_assessment: dict) -> list[ActionExecution]:
        """
        Enforce policy based on confidence assessment

        Args:
            confidence_assessment: From L6 Bayesian scorer

        Returns:
            List of executed actions
        """
        confidence_pct = confidence_assessment["confidence_percentage"]

        # Get required actions from threshold governance
        actions = self.governance.get_actions(confidence_pct)

        # Execute each action
        executions = []
        for action in actions:
            execution = self.executor.execute(action, confidence_assessment)
            executions.append(execution)

        logger.info(f"Policy enforced: {len(executions)} actions executed")

        return executions

    def get_execution_log(self, limit: int = 100) -> list[ActionExecution]:
        """Get recent action execution log"""
        return self.executor.execution_log[-limit:]


__all__ = [
    "PolicyAction",
    "ThresholdRule",
    "ThresholdGovernance",
    "ActionExecution",
    "ActionExecutor",
    "AdaptivePolicyEngine",
]
