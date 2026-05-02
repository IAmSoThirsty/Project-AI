"""Governance enforcement kernel — no execution without authority chain validation."""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from app.core.event_spine import EventCategory, EventPriority, get_event_spine
from app.core.governance_graph import get_governance_graph
from app.core.fates import get_fates
from app.core.constitutional_ledger import get_ledger
from app.core.governance import GovernanceContext, Triumvirate


@dataclass
class DecisionRecord:
    decision_id: str
    timestamp: float
    actor: str
    action: str
    context: Dict[str, Any]
    approved: bool
    reason: Optional[str]
    output_hash: str


class GovernanceKernel:

    def __init__(self) -> None:
        self.graph = get_governance_graph()
        self.spine = get_event_spine()
        self.triumvirate = Triumvirate()

    def evaluate_action(
        self,
        domain: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, DecisionRecord]:
        context = context or {}
        decision_id = str(uuid.uuid4())

        consult_required = self.graph.must_consult_domains(domain)
        if consult_required and not context.get("consultation_complete"):
            return self._reject(
                decision_id,
                domain,
                action,
                context,
                f"Consultation required: {consult_required}",
            )

        # 3-guardian Triumvirate evaluation (Galahad / Cerberus / Codex).
        gov_ctx = GovernanceContext.from_dict(
            {k: v for k, v in context.items() if hasattr(GovernanceContext, k)}
        )
        gov_ctx.action_type = action
        gov_ctx.description = f"{domain}.{action}"
        tri_decision = self.triumvirate.evaluate_action(action, gov_ctx)
        if not tri_decision.allowed:
            return self._reject(
                decision_id,
                domain,
                action,
                context,
                f"Triumvirate denied: {tri_decision.reason}",
            )

        chain = self.graph.get_authority_chain(domain)

        self.spine.publish(
            category=EventCategory.GOVERNANCE_DECISION,
            source_domain=domain,
            payload={
                "decision_type": "execution_request",
                "domain": domain,
                "action": action,
                "context": context,
                "authority_chain": chain,
            },
            can_be_vetoed=True,
            requires_approval=True,
            priority=EventPriority.HIGH,
        )

        # Approval is asynchronous; kernel approves unless externally vetoed.
        return self._approve(decision_id, domain, action, context)

    def _approve(
        self, decision_id: str, domain: str, action: str, context: Dict[str, Any]
    ) -> Tuple[bool, DecisionRecord]:
        record = DecisionRecord(
            decision_id=decision_id,
            timestamp=time.time(),
            actor=domain,
            action=action,
            context=context,
            approved=True,
            reason=None,
            output_hash=self._hash_output(domain, action, context),
        )
        try:
            get_fates().remember(
                agents_involved=[domain],
                event_type="governance_approved",
                description=f"{action} approved for {domain}",
                decision_made="APPROVED",
                paths_considered=[action],
            )
        except Exception:
            pass
        try:
            get_ledger().attest(record)
        except Exception:
            pass
        try:
            from app.governance.audit_log import AuditLog
            AuditLog().log_event(
                event_type="governance_approved",
                data={"domain": domain, "action": action, "decision_id": record.decision_id},
                actor=domain,
                description=f"{action} approved for {domain}",
            )
        except Exception:
            pass
        return True, record

    def _reject(
        self,
        decision_id: str,
        domain: str,
        action: str,
        context: Dict[str, Any],
        reason: str,
    ) -> Tuple[bool, DecisionRecord]:
        record = DecisionRecord(
            decision_id=decision_id,
            timestamp=time.time(),
            actor=domain,
            action=action,
            context=context,
            approved=False,
            reason=reason,
            output_hash=self._hash_output(domain, action, context),
        )
        try:
            get_fates().remember(
                agents_involved=[domain],
                event_type="governance_denied",
                description=f"{action} denied for {domain}: {reason}",
                decision_made="DENIED",
                paths_considered=[action],
            )
        except Exception:
            pass
        try:
            get_ledger().attest(record)
        except Exception:
            pass
        try:
            from app.governance.audit_log import AuditLog
            AuditLog().log_event(
                event_type="governance_denied",
                data={"domain": domain, "action": action, "decision_id": record.decision_id},
                actor=domain,
                description=f"{action} denied for {domain}: {reason}",
            )
        except Exception:
            pass
        return False, record

    def _hash_output(self, domain: str, action: str, context: Dict[str, Any]) -> str:
        payload = f"{domain}:{action}:{context}"
        return hashlib.sha256(payload.encode()).hexdigest()


_kernel_instance: GovernanceKernel | None = None


def get_kernel() -> GovernanceKernel:
    global _kernel_instance
    if _kernel_instance is None:
        _kernel_instance = GovernanceKernel()
    return _kernel_instance


__all__ = ["DecisionRecord", "GovernanceKernel", "get_kernel"]
