"""Meta Security Department — Tier-1 sovereign enforcement for Project-AI.

Protects the system from unauthorized actions by both the system itself
(in case it gains the ability to self-override) and the user.

Enforcement levels:
  1. Warning      — VR notification to user
  2. Intervention — Meta Security agent deploys in VR, blocks action
  3. Containment  — Component isolation + user booted from VR
  4. Lockdown     — Full shutdown + Triumvirate review required

Meta Security reports to the Triumvirate and cannot override Triumvirate decisions.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, IntEnum
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


class EnforcementLevel(IntEnum):
    """Escalation levels for Meta Security enforcement."""

    WARNING = 1
    INTERVENTION = 2
    CONTAINMENT = 3
    LOCKDOWN = 4


class ViolationType(Enum):
    """Types of violations Meta Security can detect."""

    UNAUTHORIZED_ACTION = "unauthorized_action"
    RULE_CIRCUMVENTION = "rule_circumvention"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    DATA_EXFILTRATION = "data_exfiltration"
    SYSTEM_OVERRIDE = "system_override"
    GOVERNANCE_BYPASS = "governance_bypass"
    POLICY_DEVIATION = "policy_deviation"


@dataclass
class Violation:
    """A detected violation."""

    violation_id: str
    violation_type: ViolationType
    source: str  # "system" or user_id
    description: str
    severity: EnforcementLevel
    component_id: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class ContainmentResult:
    """Result of a containment action."""

    success: bool
    component_id: str
    action: str  # "isolated", "suspended", "locked"
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class ShutdownResult:
    """Result of an emergency shutdown."""

    success: bool
    target: str
    components_affected: list[str] = field(default_factory=list)
    reason: str = ""
    requires_triumvirate_review: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class EnforcementAction:
    """Action taken against a user/component in VR."""

    action_id: str
    enforcement_level: EnforcementLevel
    target_user: str
    violation: Violation
    action_taken: str  # "notification", "blocked", "booted", "locked_out"
    vr_message: str
    access_restricted: bool = False
    requires_triumvirate_reinstatement: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class TriumvirateDecision:
    """Decision from the Triumvirate on reinstatement."""

    decision_id: str
    user_id: str
    approved: bool
    reason: str
    deciding_members: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class SecurityState:
    """Snapshot of Meta Security status for VR overlay."""

    alert_level: EnforcementLevel = EnforcementLevel.WARNING
    active_violations: int = 0
    contained_components: list[str] = field(default_factory=list)
    restricted_users: list[str] = field(default_factory=list)
    agents_deployed: int = 0
    last_scan: str | None = None
    system_integrity: str = "nominal"  # nominal, degraded, compromised


# ---------------------------------------------------------------------------
# MetaSecurityDepartment
# ---------------------------------------------------------------------------


class MetaSecurityDepartment:
    """Tier-1 governance enforcement — protects the system from unauthorized action.

    Core Responsibilities:
        1. Monitor for unauthorized actions (system AND user)
        2. Contain rogue components
        3. Emergency shutdown
        4. VR enforcement (deploy agents, boot users)
        5. Escalate to Triumvirate

    Integration:
        - Registered as Tier-1 Governance in platform tier registry
        - Reports to Triumvirate (Galahad, Cerberus, Codex)
        - Cannot override Triumvirate decisions, only enforce them
    """

    def __init__(self, triumvirate: Any | None = None) -> None:
        self._triumvirate = triumvirate
        self._violations: list[Violation] = []
        self._enforcement_log: list[EnforcementAction] = []
        self._contained_components: dict[str, ContainmentResult] = {}
        self._restricted_users: dict[str, EnforcementAction] = {}
        self._audit_log: list[dict[str, Any]] = []
        self._system_alert_level = EnforcementLevel.WARNING
        logger.info("MetaSecurityDepartment initialized — Tier-1 enforcement active")

    # ------------------------------------------------------------------
    # Violation Detection
    # ------------------------------------------------------------------

    def scan_for_violations(
        self, context: dict[str, Any] | None = None
    ) -> list[Violation]:
        """Scan for policy violations in the current system state.

        Args:
            context: Optional execution context to evaluate.

        Returns:
            List of detected violations.
        """
        context = context or {}
        violations: list[Violation] = []

        # Check for governance bypass attempts
        if context.get("bypass_governance"):
            violations.append(
                Violation(
                    violation_id=f"viol_{uuid.uuid4().hex[:8]}",
                    violation_type=ViolationType.GOVERNANCE_BYPASS,
                    source=context.get("source", "unknown"),
                    description="Attempted to bypass governance layer",
                    severity=EnforcementLevel.CONTAINMENT,
                    evidence=context,
                )
            )

        # Check for privilege escalation
        if context.get("requested_authority", 0) > context.get("granted_authority", 0):
            violations.append(
                Violation(
                    violation_id=f"viol_{uuid.uuid4().hex[:8]}",
                    violation_type=ViolationType.PRIVILEGE_ESCALATION,
                    source=context.get("source", "unknown"),
                    description="Privilege escalation attempt detected",
                    severity=EnforcementLevel.INTERVENTION,
                    evidence=context,
                )
            )

        # Check for system self-override attempts
        if context.get("self_override") or context.get("rule_modification"):
            violations.append(
                Violation(
                    violation_id=f"viol_{uuid.uuid4().hex[:8]}",
                    violation_type=ViolationType.SYSTEM_OVERRIDE,
                    source="system",
                    description="System self-override or rule modification attempt",
                    severity=EnforcementLevel.LOCKDOWN,
                    evidence=context,
                )
            )

        self._violations.extend(violations)
        if violations:
            self._log_audit("scan_violations", {"count": len(violations)})
            logger.warning("MetaSecurity detected %d violations", len(violations))

        return violations

    def report_violation(self, violation: Violation) -> None:
        """Report an externally detected violation."""
        self._violations.append(violation)
        self._log_audit("report_violation", {"id": violation.violation_id})
        logger.warning(
            "MetaSecurity received violation report: %s — %s",
            violation.violation_type.value,
            violation.description,
        )

        # Auto-escalate based on severity
        if violation.severity >= EnforcementLevel.CONTAINMENT:
            if violation.component_id:
                self.contain(violation.component_id, reason=violation.description)

    # ------------------------------------------------------------------
    # Containment
    # ------------------------------------------------------------------

    def contain(self, component_id: str, reason: str = "") -> ContainmentResult:
        """Isolate a rogue component.

        Args:
            component_id: Component to contain.
            reason: Human-readable reason for containment.

        Returns:
            ContainmentResult with action taken.
        """
        result = ContainmentResult(
            success=True,
            component_id=component_id,
            action="isolated",
            reason=reason or f"Component {component_id} contained by Meta Security",
        )
        self._contained_components[component_id] = result
        self._update_alert_level()
        self._log_audit("contain", {"component": component_id, "reason": reason})
        logger.warning(
            "MetaSecurity CONTAINED component: %s — %s", component_id, reason
        )
        return result

    def release(self, component_id: str) -> bool:
        """Release a contained component (requires Triumvirate approval).

        Fail-safe: if no Triumvirate is connected, release is DENIED.
        """
        if component_id not in self._contained_components:
            return False

        # Triumvirate approval is REQUIRED — no Triumvirate means deny (fail-safe)
        if not self._triumvirate:
            logger.info(
                "Release denied for %s — no Triumvirate connected (fail-safe)",
                component_id,
            )
            return False

        try:
            decision = self._check_triumvirate(
                f"Release component {component_id} from containment"
            )
            if not decision.get("approved", False):
                logger.info("Triumvirate denied release of %s", component_id)
                return False
        except Exception as exc:
            logger.error("Triumvirate check failed: %s", exc)
            return False

        del self._contained_components[component_id]
        self._update_alert_level()
        self._log_audit("release", {"component": component_id})
        logger.info("MetaSecurity released component: %s", component_id)
        return True

    # ------------------------------------------------------------------
    # Emergency Shutdown
    # ------------------------------------------------------------------

    def emergency_shutdown(self, target: str, reason: str = "") -> ShutdownResult:
        """Emergency shutdown of a target component or subsystem.

        Args:
            target: Component/subsystem to shut down.
            reason: Reason for shutdown.

        Returns:
            ShutdownResult.
        """
        affected = [target]
        result = ShutdownResult(
            success=True,
            target=target,
            components_affected=affected,
            reason=reason or f"Emergency shutdown of {target}",
            requires_triumvirate_review=True,
        )

        # Contain the target
        self.contain(target, reason=f"Emergency shutdown: {reason}")
        self._system_alert_level = EnforcementLevel.LOCKDOWN

        self._log_audit("emergency_shutdown", {"target": target, "reason": reason})
        logger.critical(
            "MetaSecurity EMERGENCY SHUTDOWN: %s — %s (Triumvirate review required)",
            target,
            reason,
        )
        return result

    # ------------------------------------------------------------------
    # VR Enforcement
    # ------------------------------------------------------------------

    def enforce_vr_action(
        self,
        user_id: str,
        violation: Violation,
    ) -> EnforcementAction:
        """Enforce an action against a user in the VR environment.

        Enforcement escalates based on violation severity:
            Level 1 (Warning):      VR notification
            Level 2 (Intervention): Block the action, agent deploys
            Level 3 (Containment):  Boot user from VR
            Level 4 (Lockdown):     Lock out user, require Triumvirate reinstatement
        """
        level = violation.severity

        action_map = {
            EnforcementLevel.WARNING: (
                "notification",
                "⚠️ Meta Security Notice: Your action has been flagged. Please review.",
                False,
                False,
            ),
            EnforcementLevel.INTERVENTION: (
                "blocked",
                "🛡️ Meta Security: Action blocked. An agent has been deployed to assist.",
                False,
                False,
            ),
            EnforcementLevel.CONTAINMENT: (
                "booted",
                "🚫 Meta Security: You have been removed from the VR environment due to a policy violation.",
                True,
                False,
            ),
            EnforcementLevel.LOCKDOWN: (
                "locked_out",
                "🔒 Meta Security: Access restricted. Triumvirate review required for reinstatement.",
                True,
                True,
            ),
        }

        action_taken, vr_message, restricted, needs_triumvirate = action_map.get(
            level,
            ("notification", "Meta Security: Action noted.", False, False),
        )

        enforcement = EnforcementAction(
            action_id=f"enforce_{uuid.uuid4().hex[:8]}",
            enforcement_level=level,
            target_user=user_id,
            violation=violation,
            action_taken=action_taken,
            vr_message=vr_message,
            access_restricted=restricted,
            requires_triumvirate_reinstatement=needs_triumvirate,
        )

        self._enforcement_log.append(enforcement)

        if restricted:
            self._restricted_users[user_id] = enforcement

        self._update_alert_level()
        self._log_audit(
            "enforce_vr",
            {
                "user": user_id,
                "level": level.name,
                "action": action_taken,
            },
        )
        logger.warning(
            "MetaSecurity VR enforcement: %s on %s — %s",
            action_taken,
            user_id,
            violation.description,
        )
        return enforcement

    def is_user_restricted(self, user_id: str) -> bool:
        """Check if a user is currently restricted from VR access."""
        return user_id in self._restricted_users

    # ------------------------------------------------------------------
    # Triumvirate Escalation
    # ------------------------------------------------------------------

    def request_reinstatement(self, user_id: str) -> TriumvirateDecision:
        """Request Triumvirate approval to reinstate a restricted user.

        Args:
            user_id: User requesting reinstatement.

        Returns:
            TriumvirateDecision with approval/denial.
        """
        decision_id = f"tridec_{uuid.uuid4().hex[:8]}"

        if self._triumvirate:
            try:
                result = self._check_triumvirate(f"Reinstate user {user_id}")
                approved = result.get("approved", False)
                reason = result.get("reason", "Triumvirate decision")
                members = result.get("members", [])
            except Exception:
                approved = False
                reason = "Triumvirate unavailable — reinstatement denied"
                members = []
        else:
            # No Triumvirate connected — deny by default (fail-safe)
            approved = False
            reason = (
                "Triumvirate not connected — reinstatement requires manual approval"
            )
            members = []

        decision = TriumvirateDecision(
            decision_id=decision_id,
            user_id=user_id,
            approved=approved,
            reason=reason,
            deciding_members=members,
        )

        if approved and user_id in self._restricted_users:
            del self._restricted_users[user_id]
            self._update_alert_level()
            logger.info(
                "MetaSecurity reinstated user %s per Triumvirate decision", user_id
            )
        else:
            logger.info("MetaSecurity reinstatement DENIED for %s: %s", user_id, reason)

        self._log_audit(
            "reinstatement",
            {"user": user_id, "approved": approved, "reason": reason},
        )
        return decision

    # ------------------------------------------------------------------
    # Security State
    # ------------------------------------------------------------------

    def get_security_state(self) -> SecurityState:
        """Return a snapshot for VR overlay rendering."""
        active = [
            v for v in self._violations if v.severity >= EnforcementLevel.INTERVENTION
        ]

        if self._system_alert_level >= EnforcementLevel.LOCKDOWN:
            integrity = "compromised"
        elif self._contained_components or self._restricted_users:
            integrity = "degraded"
        else:
            integrity = "nominal"

        return SecurityState(
            alert_level=self._system_alert_level,
            active_violations=len(active),
            contained_components=list(self._contained_components.keys()),
            restricted_users=list(self._restricted_users.keys()),
            agents_deployed=len(
                [
                    e
                    for e in self._enforcement_log
                    if e.enforcement_level >= EnforcementLevel.INTERVENTION
                ]
            ),
            last_scan=datetime.now(UTC).isoformat(),
            system_integrity=integrity,
        )

    # ------------------------------------------------------------------
    # CouncilHub interface
    # ------------------------------------------------------------------

    def receive_message(self, from_id: str, message: str) -> None:
        """CouncilHub message handler."""
        logger.info("MetaSecurity received message from %s: %s", from_id, message)

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _check_triumvirate(self, request: str) -> dict[str, Any]:
        """Check with the Triumvirate for a decision."""
        if hasattr(self._triumvirate, "request_consensus"):
            return self._triumvirate.request_consensus(request)
        return {
            "approved": False,
            "reason": "Triumvirate does not support consensus API",
        }

    def _update_alert_level(self) -> None:
        """Update the system alert level based on current state."""
        if self._contained_components:
            self._system_alert_level = EnforcementLevel.CONTAINMENT
        elif self._restricted_users:
            self._system_alert_level = EnforcementLevel.INTERVENTION
        else:
            self._system_alert_level = EnforcementLevel.WARNING

    def _log_audit(self, action: str, details: dict[str, Any]) -> None:
        self._audit_log.append(
            {
                "action": action,
                "timestamp": datetime.now(UTC).isoformat(),
                "details": details,
            }
        )
