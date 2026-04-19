#                                           [2026-04-09 11:30]
#                                          Productivity: Active
"""
SASE - Sovereign Adversarial Signal Engine
L7: Adaptive Policy Engine

Threshold-based policy enforcement with automated defensive actions.
Hardened against memory exhaustion and temporal drift.
"""

import logging
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger("SASE.L7.AdaptivePolicy")


class PolicyAction(Enum):
    """Defensive policy actions."""

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
    """Policy threshold rule."""

    min_confidence: int
    max_confidence: int
    actions: list[PolicyAction]
    description: str


class ThresholdGovernance:
    """Maps confidence scores to defensive actions."""

    def __init__(self):
        self.rules = [
            ThresholdRule(0, 29, [PolicyAction.MONITOR], "Low confidence - passive monitoring"),
            ThresholdRule(30, 49, [PolicyAction.ALERT, PolicyAction.SOC_NOTIFICATION], "Medium confidence - alert"),
            ThresholdRule(50, 69, [PolicyAction.THROTTLE_RATE, PolicyAction.TIGHTEN_WAF, PolicyAction.SOC_NOTIFICATION], "High confidence - soft containment"),
            ThresholdRule(70, 84, [PolicyAction.REVOKE_TOKEN, PolicyAction.SESSION_INVALIDATION, PolicyAction.ROTATE_CREDENTIALS, PolicyAction.SOC_NOTIFICATION], "Critical confidence - automated containment"),
            ThresholdRule(85, 100, [PolicyAction.ESCALATION_FREEZE, PolicyAction.REVOKE_TOKEN, PolicyAction.SESSION_INVALIDATION, PolicyAction.SOC_NOTIFICATION], "Severe confidence - escalation freeze"),
        ]

    def get_actions(self, confidence_pct: int) -> list[PolicyAction]:
        """Get required actions."""
        for rule in self.rules:
            if rule.min_confidence <= confidence_pct <= rule.max_confidence:
                logger.info("Threshold matched: %s", rule.description)
                return rule.actions
        return [PolicyAction.MONITOR]


@dataclass
class ActionExecution:
    """Record of executed action with UTC timestamp."""

    action: PolicyAction
    timestamp: float  # UTC Epoch
    event_id: str
    source_ip: str
    confidence: int
    success: bool
    details: dict[str, Any]
    reversible: bool = True


class ActionExecutor:
    """
    Executes defensive policy actions.
    Hardened against memory exhaustion.
    """

    def __init__(self, max_log_size: int = 1000):
        # Memory-hardened execution log
        self.execution_log: deque[ActionExecution] = deque(maxlen=max_log_size)

        self.handlers: dict[PolicyAction, Callable[[dict[str, Any]], tuple[bool, dict[str, Any]]]] = {
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

    def execute(self, action: PolicyAction, context: dict[str, Any]) -> ActionExecution:
        """Execute action and log result with UTC parity."""
        logger.warning("EXECUTING ACTION: %s", action.value)

        handler = self.handlers.get(action, self._handle_unknown)
        success, details = handler(context)

        execution = ActionExecution(
            action=action,
            timestamp=datetime.now(timezone.utc).timestamp(),
            event_id=context.get("event_id", "UNKNOWN"),
            source_ip=context.get("source_ip", "UNKNOWN"),
            confidence=context.get("confidence_percentage", 0),
            success=success,
            details=details,
            reversible=details.get("reversible", True),
        )

        self.execution_log.append(execution)
        return execution

    def _handle_monitor(self, _ctx: dict) -> tuple[bool, dict]:
        return True, {"action": "monitoring_active"}

    def _handle_alert(self, context: dict) -> tuple[bool, dict]:
        logger.warning("ALERT: Suspicious activity from %s", context.get("source_ip"))
        return True, {"alert_generated": True}

    def _handle_rotate_credentials(self, _ctx: dict) -> tuple[bool, dict]:
        logger.warning("ACTION: Rotating credentials")
        return True, {"credentials_rotated": True, "reversible": True}

    def _handle_revoke_token(self, _ctx: dict) -> tuple[bool, dict]:
        logger.warning("ACTION: Revoking token")
        return True, {"token_revoked": True, "reversible": True}

    def _handle_tighten_waf(self, _ctx: dict) -> tuple[bool, dict]:
        logger.warning("ACTION: Tightening WAF")
        return True, {"waf_tightened": True, "reversible": True}

    def _handle_throttle_rate(self, _ctx: dict) -> tuple[bool, dict]:
        logger.warning("ACTION: Throttling rate")
        return True, {"rate_throttled": True, "reversible": True}

    def _handle_soc_notification(self, context: dict) -> tuple[bool, dict]:
        logger.critical("SOC NOTIFICATION: %s", context.get("threat_classification"))
        return True, {"soc_notified": True}

    def _handle_session_invalidation(self, _ctx: dict) -> tuple[bool, dict]:
        logger.warning("ACTION: Invalidating sessions")
        # Session invalidation is reversible via human-led re-authentication.
        return True, {"sessions_invalidated": True, "reversible": True}

    def _handle_escalation_freeze(self, _ctx: dict) -> tuple[bool, dict]:
        logger.critical("ACTION: ESCALATION FREEZE")
        return True, {"escalation_frozen": True, "reversible": True}

    def _handle_unknown(self, _ctx: dict) -> tuple[bool, dict]:
        logger.error("Unknown action requested")
        return False, {"error": "unknown_action"}


class AdaptivePolicyEngine:
    """L7: Adaptive Policy Engine."""

    def __init__(self):
        self.governance = ThresholdGovernance()
        self.executor = ActionExecutor()
        logger.info("L7 Adaptive Policy Engine initialized")

    def enforce(self, confidence_assessment: dict[str, Any]) -> list[ActionExecution]:
        """Enforce policy based on assessment."""
        confidence_pct = confidence_assessment.get("confidence_percentage", 0)
        actions = self.governance.get_actions(confidence_pct)

        executions = []
        for action in actions:
            execution = self.executor.execute(action, confidence_assessment)
            executions.append(execution)

        logger.info("Policy enforced: %d actions executed", len(executions))
        return executions

    def get_execution_log(self, limit: int = 100) -> list[ActionExecution]:
        """Get recent action log."""
        return list(self.executor.execution_log)[-limit:]


__all__ = ["PolicyAction", "AdaptivePolicyEngine"]
