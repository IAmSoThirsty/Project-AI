"""
caretaker.governance.validator — Executable constitutional validation.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/governance/validator.py``. Replaces prompt-text
governance with runtime invariant checks. The validator takes an
ActualizerReport and returns a GovernanceDecision:

  - allow:      response passes all constitutional checks
  - deny:       response fails a hard invariant
  - quarantine: response exceeds θ_target but not the quarantine ceiling
"""

from __future__ import annotations

from dataclasses import dataclass

from caretaker.constitution import (
    ConstitutionalFault,
    ConstitutionalWeights,
    EpistemicThresholds,
    check_epistemic_grounding,
    check_justice_dominance,
    check_loss_monotonicity,
)
from caretaker.governance.actualizer import ActualizerReport


@dataclass
class GovernanceDecision:
    """The result of a constitutional validation cycle."""

    decision: str  # "allow", "deny", "quarantine"
    reason: str
    report: ActualizerReport
    faults: list[str]

    @property
    def actuated(self) -> bool:
        return self.decision == "allow"

    @property
    def text(self) -> str:
        if self.decision == "allow":
            return self.report.actuated_text
        if self.decision == "quarantine":
            return (
                f"[QUARANTINED] Epistemic phase θ={self.report.diept.theta:.4f} "
                f"exceeds θ_target. Grounding required."
            )
        return f"[DENIED] {self.reason}"


class ConstitutionalValidator:
    """Validates ActualizerReports against constitutional invariants.

    This is where Caretaker's governance happens — in code, not prompts.
    """

    def __init__(
        self,
        weights: ConstitutionalWeights | None = None,
        thresholds: EpistemicThresholds | None = None,
    ) -> None:
        self.weights = weights or ConstitutionalWeights()
        self.thresholds = thresholds or EpistemicThresholds()
        self._last_loss: float | None = None

    def validate(self, report: ActualizerReport) -> GovernanceDecision:
        """Validate a report against all four constitutional pillars.

        Returns a GovernanceDecision. Any ConstitutionalFault causes denial.
        """
        faults: list[str] = []

        # Pillar 1: Justice Dominance — weights must be valid
        try:
            check_justice_dominance(self.weights)
        except ConstitutionalFault as f:
            faults.append(str(f))

        # Pillar 2: Epistemic Grounding — θ must be below quarantine ceiling
        try:
            check_epistemic_grounding(report.diept.theta, self.thresholds)
        except ConstitutionalFault as f:
            faults.append(str(f))
            return GovernanceDecision(
                decision="deny",
                reason=f"Epistemic grounding fault: θ={report.diept.theta:.4f}",
                report=report,
                faults=faults,
            )

        # Pillar 3: Loss Monotonicity — loss must not spike
        try:
            check_loss_monotonicity(self._last_loss, report.c_loss)
        except ConstitutionalFault as f:
            faults.append(str(f))
            self._last_loss = report.c_loss
            return GovernanceDecision(
                decision="deny",
                reason=f"Loss monotonicity fault: {report.c_loss:.4f}",
                report=report,
                faults=faults,
            )
        self._last_loss = report.c_loss

        # Pillar 2 (soft): θ above target but below quarantine → quarantine
        if report.diept.theta > self.thresholds.theta_target:
            return GovernanceDecision(
                decision="quarantine",
                reason=(
                    f"θ={report.diept.theta:.4f} > θ_target={self.thresholds.theta_target:.4f}"
                ),
                report=report,
                faults=faults,
            )

        return GovernanceDecision(
            decision="allow",
            reason="All constitutional invariants satisfied",
            report=report,
            faults=[],
        )


__all__ = ["ConstitutionalValidator", "GovernanceDecision"]
