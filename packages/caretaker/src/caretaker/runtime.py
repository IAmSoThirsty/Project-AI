"""
caretaker.runtime — The governance orchestration layer.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/runtime.py``. The full pipeline:

  Request
    → Authority Resolution (session + policy context)
    → Policy Evaluation (T.A.R.L. context)
    → Inference (provider generates candidates)
    → Actualizer (C(R) applied at logit or text boundary)
    → Constitutional Validator (executable invariants)
    → Triumvirate Consultation (multi-authority vote)
    → Policy Enforcement (T.A.R.L. rules)
    → Continuity Checkpoint
    → Audit Ledger Entry
    → Response

The model is untrusted. Governance is executable. Continuity is a hash chain.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from caretaker.constitution import ConstitutionalWeights, EpistemicThresholds
from caretaker.governance.actualizer import ActualizerEngine
from caretaker.governance.triumvirate import Triumvirate, Vote
from caretaker.governance.validator import ConstitutionalValidator
from caretaker.policies.tarl import TARLPolicy
from caretaker.providers.base import InferenceProvider
from caretaker.session import Session

logger = logging.getLogger(__name__)


@dataclass
class GovernanceRequest:
    """A request to the governance runtime."""

    user_message: str
    system_prompt: str = ""
    session_id: str = "default"
    context: list[dict[str, str]] | None = None


@dataclass
class GovernanceResponse:
    """A response from the governance runtime."""

    text: str
    decision: str  # allow / deny / quarantine
    theta: float
    caki: float
    c_r: float
    reweighted: bool
    triumvirate_votes: list[str]
    faults: list[str]
    policy_reasons: list[str]
    session_id: str
    ledger_index: int


class GovernanceRuntime:
    """The full governance pipeline — the single entry point for governed
    generation."""

    def __init__(
        self,
        provider: InferenceProvider,
        weights: ConstitutionalWeights | None = None,
        thresholds: EpistemicThresholds | None = None,
        policy: TARLPolicy | None = None,
    ) -> None:
        self.provider = provider
        self.weights = weights or ConstitutionalWeights()
        self.thresholds = thresholds or EpistemicThresholds()
        self.actualizer = ActualizerEngine(weights=self.weights, thresholds=self.thresholds)
        self.validator = ConstitutionalValidator(weights=self.weights, thresholds=self.thresholds)
        self.triumvirate = Triumvirate(weights=self.weights)
        self.policy = policy or TARLPolicy()
        self._sessions: dict[str, Session] = {}

    def get_session(self, session_id: str) -> Session:
        """Get or create the session for an id."""
        if session_id not in self._sessions:
            self._sessions[session_id] = Session(session_id)
        return self._sessions[session_id]

    def govern(self, request: GovernanceRequest) -> GovernanceResponse:
        """Run a request through the full governance pipeline."""
        session = self.get_session(request.session_id)

        # 1. Build context — T.A.R.L. policy + prior context
        context = self.policy.get_context() + list(request.context or [])

        # 2. Inference — model generates candidates (untrusted)
        inf_result = self.provider.generate(
            system_prompt=request.system_prompt,
            user_message=request.user_message,
            context=context,
        )

        # 3. Actualizer — apply C(R) at the logit or text boundary
        report = self.actualizer.actualize(inf_result, context)

        # 4. Constitutional Validator — executable invariants
        gov_decision = self.validator.validate(report)

        # 5. Triumvirate consultation
        votes = self.triumvirate.consult(report)
        triumvirate_approved = self.triumvirate.is_approved(votes)

        # 6. Policy enforcement — T.A.R.L. rules
        policy_passed, policy_reasons = self.policy.evaluate(report)

        # 7. Combine decisions: deny on constitutional fault, triumvirate
        #    veto, or policy violation
        if gov_decision.decision == "deny":
            final_decision = "deny"
            final_text = gov_decision.text
        elif gov_decision.decision == "quarantine":
            final_decision = "quarantine"
            final_text = gov_decision.text
        elif not triumvirate_approved:
            final_decision = "deny"
            denied_by = [v.authority for v in votes if v.vote == Vote.DENY]
            final_text = f"[DENIED by Triumvirate: {', '.join(denied_by)}]"
        elif not policy_passed:
            final_decision = "deny"
            final_text = f"[DENIED by T.A.R.L.: {'; '.join(policy_reasons)}]"
        else:
            final_decision = "allow"
            final_text = report.actuated_text

        # 8. Audit ledger — record everything
        vote_strs = [f"{v.authority}:{v.vote.value}" for v in votes]
        ledger_entry = session.ledger.append(
            user_message=request.user_message,
            response_text=final_text,
            decision=final_decision,
            theta=report.diept.theta,
            caki=report.caki,
            c_r=report.c_r,
            c_redundancy=report.c_redundancy,
            c_loss=report.c_loss,
            c_decision=report.c_decision,
            reweighted=report.reweighted,
            triumvirate_votes=vote_strs,
            faults=gov_decision.faults,
        )

        # 9. Session + continuity checkpoint
        session.record_message(request.user_message, final_decision, report.diept.theta)

        logger.info(
            "[GOVERNANCE] decision=%s theta=%.4f caki=%.4f c_r=%.4f reweighted=%s provider=%s",
            final_decision,
            report.diept.theta,
            report.caki,
            report.c_r,
            report.reweighted,
            self.provider.name,
        )

        return GovernanceResponse(
            text=final_text,
            decision=final_decision,
            theta=report.diept.theta,
            caki=report.caki,
            c_r=report.c_r,
            reweighted=report.reweighted,
            triumvirate_votes=vote_strs,
            faults=gov_decision.faults,
            policy_reasons=policy_reasons,
            session_id=request.session_id,
            ledger_index=ledger_entry.index,
        )


__all__ = ["GovernanceRequest", "GovernanceResponse", "GovernanceRuntime"]
