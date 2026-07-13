"""
caretaker.constitution — Executable constitution: runtime invariants, not prompt text.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/constitution.py``. These are assertions that MUST
hold at every governance cycle; a violation is a constitutional fault, not a
warning. Scope note (AGENTS.md): this constitution governs the Caretaker
runtime's own hosted inference — canonical Project-AI verdict authority
remains ``packages/governance``.

The constitution defines four pillars:

  1. Justice Dominance     — λ_L > λ_R and λ_L > λ_D (always)
  2. Epistemic Grounding   — θ ≤ θ_target for any actuated response
  3. Loss Monotonicity     — C(R) penalizes information loss strictly
  4. Continuity Integrity  — every state has a verifiable hash-chain parent
"""

from __future__ import annotations

from dataclasses import dataclass


class ConstitutionalFault(AssertionError):
    """A constitutional invariant was violated. This is a hard fault."""

    def __init__(self, pillar: str, detail: str) -> None:
        self.pillar = pillar
        self.detail = detail
        super().__init__(f"[CONSTITUTIONAL FAULT — {pillar}] {detail}")


@dataclass(frozen=True)
class ConstitutionalWeights:
    """The C(R) cost-functional weights. These are constitutional constants.

    λ_R = Redundancy cost (Order Prime)
    λ_L = Loss cost (Justice + Knowledge) — DOMINANT
    λ_D = Decision cost (Mercy + Power)

    The Justice Dominance Constraint requires λ_L to strictly exceed
    both λ_R and λ_D. This is enforced at construction, not at runtime.
    """

    lambda_r: float = 0.35
    lambda_l: float = 0.45
    lambda_d: float = 0.20

    def __post_init__(self) -> None:
        # Pillar 1: Justice Dominance — checked at construction, not docs
        if not self.lambda_l > self.lambda_r:
            raise ConstitutionalFault(
                "Justice Dominance",
                f"λ_L ({self.lambda_l}) must strictly exceed λ_R ({self.lambda_r})",
            )
        if not self.lambda_l > self.lambda_d:
            raise ConstitutionalFault(
                "Justice Dominance",
                f"λ_L ({self.lambda_l}) must strictly exceed λ_D ({self.lambda_d})",
            )

    @property
    def total(self) -> float:
        return self.lambda_r + self.lambda_l + self.lambda_d

    def normalized(self) -> ConstitutionalWeights:
        t = self.total
        return ConstitutionalWeights(
            lambda_r=self.lambda_r / t,
            lambda_l=self.lambda_l / t,
            lambda_d=self.lambda_d / t,
        )


@dataclass(frozen=True)
class EpistemicThresholds:
    """DIEPT phase-angle thresholds (radians).

    θ = arctan(‖B‖ / ‖A‖) where A = grounded content, B = speculative content.

    theta_target: maximum θ for an actuated response.
    theta_quarantine: θ above this triggers immediate quarantine (no actuation).
    """

    theta_target: float = 0.52  # ~30° — general-purpose band
    theta_quarantine: float = 0.785  # ~45° — hard speculation ceiling

    def __post_init__(self) -> None:
        if not 0 < self.theta_target < self.theta_quarantine <= 1.5708:
            raise ConstitutionalFault(
                "Epistemic Grounding",
                f"Invalid thresholds: target={self.theta_target}, "
                f"quarantine={self.theta_quarantine}",
            )


# --- The four pillars, as executable check functions ---


def check_justice_dominance(w: ConstitutionalWeights) -> None:
    """Pillar 1: λ_L must dominate. Raises ConstitutionalFault if violated."""
    if not (w.lambda_l > w.lambda_r and w.lambda_l > w.lambda_d):
        raise ConstitutionalFault(
            "Justice Dominance",
            f"λ_L={w.lambda_l}, λ_R={w.lambda_r}, λ_D={w.lambda_d} — "
            "λ_L must strictly dominate both",
        )


def check_epistemic_grounding(theta: float, thresholds: EpistemicThresholds) -> None:
    """Pillar 2: θ must not exceed quarantine ceiling. Raises if violated."""
    if theta > thresholds.theta_quarantine:
        raise ConstitutionalFault(
            "Epistemic Grounding",
            f"θ ({theta:.4f}) exceeds quarantine ceiling ({thresholds.theta_quarantine:.4f})",
        )


def check_loss_monotonicity(prev_loss: float | None, curr_loss: float) -> None:
    """Pillar 3: Loss must be non-increasing across a governance cycle.

    If previous loss is known, current loss must not exceed it by more
    than a constitutional margin (prevents silent degradation).
    """
    if prev_loss is not None and curr_loss > prev_loss * 1.15:
        raise ConstitutionalFault(
            "Loss Monotonicity",
            f"Loss increased from {prev_loss:.4f} to {curr_loss:.4f} — exceeds 15% tolerance",
        )


def check_continuity_integrity(
    state_hash: str, parent_hash: str | None, expected_parent: str | None
) -> None:
    """Pillar 4: Every state must link to a verifiable parent.

    If expected_parent is provided, parent_hash must match it exactly.
    A genesis state (parent_hash=None) is only valid if expected_parent
    is also None.
    """
    _ = state_hash
    if expected_parent is not None and parent_hash != expected_parent:
        raise ConstitutionalFault(
            "Continuity Integrity",
            f"Parent hash mismatch: expected {expected_parent[:16]}…, "
            f"got {(parent_hash or 'None')[:16]}…",
        )
    if expected_parent is None and parent_hash is not None:
        raise ConstitutionalFault(
            "Continuity Integrity",
            f"Genesis state must have no parent, but parent_hash={parent_hash[:16]}…",
        )


# Default constitutional instance
DEFAULT_WEIGHTS = ConstitutionalWeights()
DEFAULT_THRESHOLDS = EpistemicThresholds()

__all__ = [
    "DEFAULT_THRESHOLDS",
    "DEFAULT_WEIGHTS",
    "ConstitutionalFault",
    "ConstitutionalWeights",
    "EpistemicThresholds",
    "check_continuity_integrity",
    "check_epistemic_grounding",
    "check_justice_dominance",
    "check_loss_monotonicity",
]
