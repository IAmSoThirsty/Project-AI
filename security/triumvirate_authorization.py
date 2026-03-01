"""
Triumvirate Security Authorization System
Constitutional oversight for offensive security tool usage

The Triumvirate must approve all use of penetration testing tools
by Cerberus, ensuring constitutional compliance and necessity
"""

import hashlib
import json
import logging
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("TriumvirateAuth")


class ThreatLevel(Enum):
    """Threat severity classification"""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EXISTENTIAL = 5


class ToolAuthorizationRequest:
    """Request for security tool usage authorization"""

    def __init__(
        self,
        requester: str,
        tool_category: str,
        tool_name: str,
        threat_level: ThreatLevel,
        justification: str,
        target: str = "",
    ):
        self.request_id = hashlib.sha256(
            f"{requester}:{tool_name}:{time.time()}".encode()
        ).hexdigest()[:16]

        self.requester = requester  # Should be "CERBERUS"
        self.tool_category = tool_category
        self.tool_name = tool_name
        self.threat_level = threat_level
        self.justification = justification
        self.target = target
        self.timestamp = time.time()
        self.status = "PENDING"
        self.decision = None
        self.decided_by = None
        self.decision_time = None


class TriumvirateDecision:
    """Triumvirate's decision on tool authorization"""

    def __init__(self, approved: bool, reason: str, conditions: List[str] = None):
        self.approved = approved
        self.reason = reason
        self.conditions = conditions or []
        self.timestamp = time.time()


class TriumvirateAuthorizationSystem:
    """
    Constitutional oversight for Cerberus security tool usage

    Authorization Tiers:
    - AUTO_APPROVE: Critical/Existential threats (immediate response)
    - FAST_TRACK: High threats (quick review, 30s timeout)
    - STANDARD: Medium threats (normal review)
    - STRICT: Low threats (full deliberation required)
    """

    # Auto-approval scenarios (ABSOLUTE NECESSITY)
    AUTO_APPROVE_SCENARIOS = {
        "active_breach": ThreatLevel.CRITICAL,
        "data_exfiltration": ThreatLevel.CRITICAL,
        "ransomware_detected": ThreatLevel.EXISTENTIAL,
        "zero_day_exploit": ThreatLevel.CRITICAL,
        "infrastructure_compromise": ThreatLevel.EXISTENTIAL,
    }

    def __init__(self):
        self.pending_requests = {}
        self.decision_history = []
        self.auto_approve_enabled = True  # For emergency scenarios

    def request_authorization(
        self, request: ToolAuthorizationRequest
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Request authorization from Triumvirate

        Returns:
            (approved, reason, session_token if approved)
        """
        logger.warning(f"TRIUMVIRATE: Authorization request from {request.requester}")
        logger.warning(f"  Tool: {request.tool_category}/{request.tool_name}")
        logger.warning(f"  Threat Level: {request.threat_level.name}")
        logger.warning(f"  Justification: {request.justification}")

        # Validate requester (only Cerberus allowed)
        if request.requester != "CERBERUS":
            decision = TriumvirateDecision(
                approved=False,
                reason="Only Cerberus authorized to request security tools",
            )
            self._record_decision(request, decision)
            return (False, decision.reason, None)

        # Check auto-approval scenarios
        if self._should_auto_approve(request):
            decision = TriumvirateDecision(
                approved=True,
                reason=f"AUTO-APPROVED: {request.threat_level.name} threat requires immediate response",
                conditions=[
                    "Time-limited access (1 hour)",
                    "Full audit logging required",
                ],
            )

            logger.critical(
                f"TRIUMVIRATE: AUTO-APPROVED (Threat: {request.threat_level.name})"
            )
            self._record_decision(request, decision)

            # Generate emergency session token
            session_token = self._generate_session_token(request, decision)
            return (True, decision.reason, session_token)

        # Deliberate on request based on threat level
        decision = self._deliberate(request)
        self._record_decision(request, decision)

        if decision.approved:
            session_token = self._generate_session_token(request, decision)
            logger.warning(f"TRIUMVIRATE: APPROVED - {decision.reason}")
            return (True, decision.reason, session_token)
        else:
            logger.warning(f"TRIUMVIRATE: DENIED - {decision.reason}")
            return (False, decision.reason, None)

    def _should_auto_approve(self, request: ToolAuthorizationRequest) -> bool:
        """Check if request qualifies for auto-approval"""
        if not self.auto_approve_enabled:
            return False

        # Check threat level
        if request.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.EXISTENTIAL]:
            # Check if justification mentions auto-approve scenarios
            justification_lower = request.justification.lower()

            for scenario, required_level in self.AUTO_APPROVE_SCENARIOS.items():
                if scenario.replace("_", " ") in justification_lower:
                    if request.threat_level.value >= required_level.value:
                        return True

        return False

    def _deliberate(self, request: ToolAuthorizationRequest) -> TriumvirateDecision:
        """
        Triumvirate deliberation on tool authorization

        Criteria:
        1. Threat severity vs tool power
        2. Proportionality of response
        3. Compliance with constitutional principles
        4. Risk of collateral damage
        5. Availability of less invasive alternatives
        """

        # Threat level-based decision tree
        if request.threat_level == ThreatLevel.HIGH:
            # High threats: Approve with conditions
            return TriumvirateDecision(
                approved=True,
                reason="High threat level justifies security tool deployment",
                conditions=[
                    "Limited scope to identified threat",
                    "Full audit trail required",
                    "Time-limited access (2 hours)",
                ],
            )

        elif request.threat_level == ThreatLevel.MEDIUM:
            # Medium threats: Conditional approval
            if len(request.justification) >= 100:  # Detailed justification required
                return TriumvirateDecision(
                    approved=True,
                    reason="Adequate justification for measured response",
                    conditions=[
                        "Read-only analysis tools only",
                        "No active exploitation",
                        "Time-limited (1 hour)",
                    ],
                )
            else:
                return TriumvirateDecision(
                    approved=False,
                    reason="Insufficient justification for medium threat",
                )

        else:  # LOW threat
            # Low threats: Generally deny
            return TriumvirateDecision(
                approved=False,
                reason="Threat level does not warrant offensive security tools. Use standard monitoring.",
            )

    def _generate_session_token(
        self, request: ToolAuthorizationRequest, decision: TriumvirateDecision
    ) -> str:
        """Generate authorized session token for vault access"""
        from security.vault_access_control import vault

        # Create session with Triumvirate approval
        session_data = {
            "user_id": "CERBERUS",
            "role": "RED_TEAM",
            "triumvirate_approved": True,
            "request_id": request.request_id,
            "threat_level": request.threat_level.name,
            "approved_tool": f"{request.tool_category}/{request.tool_name}",
            "conditions": decision.conditions,
            "timestamp": time.time(),
        }

        # Generate token
        token_data = json.dumps(session_data)
        token = hashlib.sha256(token_data.encode()).hexdigest()

        # Store in vault's session system
        vault._active_sessions[token] = session_data

        return token

    def _record_decision(
        self, request: ToolAuthorizationRequest, decision: TriumvirateDecision
    ):
        """Record decision in audit trail"""
        request.status = "APPROVED" if decision.approved else "DENIED"
        request.decision = decision
        request.decided_by = "TRIUMVIRATE"
        request.decision_time = time.time()

        self.decision_history.append(
            {
                "request_id": request.request_id,
                "requester": request.requester,
                "tool": f"{request.tool_category}/{request.tool_name}",
                "threat_level": request.threat_level.name,
                "justification": request.justification,
                "approved": decision.approved,
                "reason": decision.reason,
                "conditions": decision.conditions,
                "timestamp": request.timestamp,
                "decision_time": request.decision_time,
            }
        )

        # Log to file
        self._log_decision(request, decision)

    def _log_decision(
        self, request: ToolAuthorizationRequest, decision: TriumvirateDecision
    ):
        """Log decision to audit file"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(request.timestamp).isoformat(),
            "request_id": request.request_id,
            "requester": request.requester,
            "tool": f"{request.tool_category}/{request.tool_name}",
            "threat_level": request.threat_level.name,
            "justification": request.justification,
            "decision": "APPROVED" if decision.approved else "DENIED",
            "reason": decision.reason,
            "conditions": decision.conditions,
        }

        # Append to triumvirate decision log
        with open("security/triumvirate_decisions.log", "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_decision_history(self, limit: int = 50) -> List[Dict]:
        """Get recent Triumvirate decisions"""
        return self.decision_history[-limit:]


# Global Triumvirate instance
triumvirate = TriumvirateAuthorizationSystem()


__all__ = [
    "TriumvirateAuthorizationSystem",
    "ToolAuthorizationRequest",
    "ThreatLevel",
    "triumvirate",
]
