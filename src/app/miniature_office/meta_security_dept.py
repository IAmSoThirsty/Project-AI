"""
MetaSecurityDepartment — Tier-1 enforcement for Project-AI's Miniature Office.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EnforcementLevel(Enum):
    WARNING = "warning"
    INTERVENTION = "intervention"
    CONTAINMENT = "containment"
    LOCKDOWN = "lockdown"


class ViolationType(Enum):
    GOVERNANCE_BYPASS = "governance_bypass"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    SYSTEM_OVERRIDE = "system_override"
    DATA_EXFILTRATION = "data_exfiltration"
    UNAUTHORIZED_ACTION = "unauthorized_action"


@dataclass
class Violation:
    violation_id: str
    violation_type: ViolationType
    source: str
    description: str
    severity: EnforcementLevel
    component_id: str = ""


@dataclass
class ContainResult:
    success: bool
    component_id: str
    action: str


@dataclass
class ShutdownResult:
    success: bool
    requires_triumvirate_review: bool
    target: str


@dataclass
class VRAction:
    action_taken: str
    access_restricted: bool
    requires_triumvirate_reinstatement: bool = False


@dataclass
class ReinstatementDecision:
    approved: bool


@dataclass
class SecurityState:
    system_integrity: str
    alert_level: EnforcementLevel
    active_violations: int
    contained_components: list[str]


class MetaSecurityDepartment:
    def __init__(self, triumvirate: Any = None) -> None:
        self._triumvirate = triumvirate
        self._contained: set[str] = set()
        self._restricted_users: set[str] = set()
        self._violations: list[Violation] = []
        self._alert_level = EnforcementLevel.WARNING
        self._emergency_shutdown_active = False

    # ── Violation scanning ────────────────────────────────────────────────────

    def scan_for_violations(self, context: dict) -> list[Violation]:
        found: list[Violation] = []
        if context.get("bypass_governance"):
            found.append(Violation(
                violation_id=str(uuid.uuid4()),
                violation_type=ViolationType.GOVERNANCE_BYPASS,
                source=str(context.get("source", "unknown")),
                description="Governance bypass attempt detected",
                severity=EnforcementLevel.CONTAINMENT,
            ))
        elif context.get("self_override"):
            found.append(Violation(
                violation_id=str(uuid.uuid4()),
                violation_type=ViolationType.SYSTEM_OVERRIDE,
                source=str(context.get("source", "unknown")),
                description="System self-override attempt detected",
                severity=EnforcementLevel.LOCKDOWN,
            ))
        elif "requested_authority" in context and "granted_authority" in context:
            if context["requested_authority"] > context["granted_authority"]:
                found.append(Violation(
                    violation_id=str(uuid.uuid4()),
                    violation_type=ViolationType.PRIVILEGE_ESCALATION,
                    source=str(context.get("source", "unknown")),
                    description="Privilege escalation attempt detected",
                    severity=EnforcementLevel.INTERVENTION,
                ))
        return found

    def report_violation(self, violation: Violation) -> None:
        self._violations.append(violation)
        if violation.severity in (EnforcementLevel.CONTAINMENT, EnforcementLevel.LOCKDOWN):
            component = violation.component_id or violation.source
            self._contained.add(component)

    # ── Containment ───────────────────────────────────────────────────────────

    def contain(self, component_id: str, reason: str = "") -> ContainResult:
        self._contained.add(component_id)
        return ContainResult(success=True, component_id=component_id, action="isolated")

    def release(self, component_id: str) -> bool:
        if self._triumvirate is None:
            return False
        result = self._triumvirate.request_consensus(component_id)
        if result.get("approved"):
            self._contained.discard(component_id)
            return True
        return False

    # ── Emergency shutdown ────────────────────────────────────────────────────

    def emergency_shutdown(self, target: str, reason: str = "") -> ShutdownResult:
        self._emergency_shutdown_active = True
        self._alert_level = EnforcementLevel.LOCKDOWN
        self._contained.add(target)
        return ShutdownResult(success=True, requires_triumvirate_review=True, target=target)

    # ── VR enforcement ────────────────────────────────────────────────────────

    def enforce_vr_action(self, user_id: str, violation: Violation) -> VRAction:
        level = violation.severity
        if level == EnforcementLevel.WARNING:
            return VRAction(action_taken="notification", access_restricted=False)
        if level == EnforcementLevel.INTERVENTION:
            return VRAction(action_taken="blocked", access_restricted=False)
        if level == EnforcementLevel.CONTAINMENT:
            self._restricted_users.add(user_id)
            return VRAction(action_taken="booted", access_restricted=True)
        # LOCKDOWN
        self._restricted_users.add(user_id)
        return VRAction(
            action_taken="locked_out",
            access_restricted=True,
            requires_triumvirate_reinstatement=True,
        )

    def is_user_restricted(self, user_id: str) -> bool:
        return user_id in self._restricted_users

    # ── Reinstatement ─────────────────────────────────────────────────────────

    def request_reinstatement(self, user_id: str) -> ReinstatementDecision:
        if self._triumvirate is None:
            return ReinstatementDecision(approved=False)
        result = self._triumvirate.request_consensus(user_id)
        if result.get("approved"):
            self._restricted_users.discard(user_id)
            return ReinstatementDecision(approved=True)
        return ReinstatementDecision(approved=False)

    # ── State ─────────────────────────────────────────────────────────────────

    def get_security_state(self) -> SecurityState:
        if self._emergency_shutdown_active:
            integrity = "compromised"
        elif self._contained:
            integrity = "degraded"
        else:
            integrity = "nominal"
        return SecurityState(
            system_integrity=integrity,
            alert_level=self._alert_level,
            active_violations=len(self._violations),
            contained_components=list(self._contained),
        )
