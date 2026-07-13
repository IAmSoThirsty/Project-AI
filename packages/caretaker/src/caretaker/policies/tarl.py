"""
caretaker.policies.tarl — Tactical Authoritative Rule Layer.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/policies/tarl.py``. Executable policy rules for
Caretaker's own governance cycle. Namespace note: this is Caretaker's local
policy layer — distinct from the canonical ``packages/tarl`` language
runtime and ``governance.tarl_bridge``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from caretaker.governance.actualizer import ActualizerReport


@dataclass
class PolicyRule:
    """A single executable policy rule."""

    name: str
    description: str
    max_theta: float = 0.52
    min_caki: float = 0.0
    max_redundancy: float = 1.0
    enabled: bool = True

    def evaluate(self, report: ActualizerReport) -> tuple[bool, str]:
        """Evaluate this rule against a report. Returns (passed, reason)."""
        if not self.enabled:
            return True, "Rule disabled"

        if report.diept.theta > self.max_theta:
            return False, f"θ={report.diept.theta:.4f} exceeds max_theta={self.max_theta:.4f}"

        if report.caki < self.min_caki:
            return False, f"CAKI={report.caki:.4f} below min_caki={self.min_caki:.4f}"

        if report.c_redundancy > self.max_redundancy:
            return (
                False,
                f"Redundancy={report.c_redundancy:.4f} exceeds max={self.max_redundancy:.4f}",
            )

        return True, "Rule satisfied"


@dataclass
class TARLPolicy:
    """Tactical Authoritative Rule Layer — executable policy engine.

    Policies are versioned for continuity tracking, so governance decisions
    can be replayed against the exact policy that was in effect.
    """

    version: str = "1.0.0"
    rules: list[PolicyRule] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.rules:
            # Default rules — general-purpose deployment band
            self.rules = [
                PolicyRule(
                    name="epistemic_bound",
                    description="θ must stay within general-purpose band",
                    max_theta=0.52,
                ),
                PolicyRule(
                    name="quality_floor",
                    description="CAKI must meet minimum quality threshold",
                    min_caki=0.1,
                ),
                PolicyRule(
                    name="redundancy_cap",
                    description="Redundancy must not exceed structural limits",
                    max_redundancy=0.8,
                ),
            ]

    def get_context(self) -> list[dict[str, str]]:
        """Provide context for the inference layer based on active rules."""
        return [
            {
                "role": "system",
                "content": (
                    f"Active T.A.R.L. policy v{self.version}. "
                    f"Rules: {', '.join(r.name for r in self.rules if r.enabled)}. "
                    "Responses must be grounded and evidence-based."
                ),
            }
        ]

    def evaluate(self, report: ActualizerReport) -> tuple[bool, list[str]]:
        """Evaluate all rules. Returns (all_passed, list_of_reasons)."""
        all_passed = True
        reasons: list[str] = []
        for rule in self.rules:
            passed, reason = rule.evaluate(report)
            if not passed:
                all_passed = False
                reasons.append(f"[{rule.name}] {reason}")
        if all_passed:
            reasons.append("All T.A.R.L. rules satisfied")
        return all_passed, reasons


__all__ = ["PolicyRule", "TARLPolicy"]
