"""
caretaker.governance.actualizer — C(R) cost functional at the inference boundary.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/governance/actualizer.py``.

C(R) = λ_R·Redundancy + λ_L·Loss + λ_D·DecisionCost

Subject to (Justice Dominance, enforced in constitution.py):
  λ_L > λ_R  and  λ_L > λ_D

TWO MODES:
  1. Logit re-weighting (provider exposes logits): per generation step,
     assign a C(R) cost to each token candidate, subtract from the logit,
     and re-rank. This IS real logit re-weighting.
  2. Post-generation scoring (no logits): score the generated text against
     C(R) and return a governance report. This is NOT logit re-weighting —
     it's candidate evaluation. The distinction is reported honestly via
     ``ActualizerReport.reweighted``.
"""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from dataclasses import dataclass

from caretaker.constitution import ConstitutionalWeights, EpistemicThresholds
from caretaker.governance.caki import compute_caki
from caretaker.governance.diept import SPECULATIVE_LEXICON, DIEPTState, compute_diept_phase
from caretaker.providers.base import InferenceResult, Message

_WORD_RE = re.compile(r"[a-zA-Z_]{2,}")


@dataclass
class ActualizerReport:
    """Full report from an Actualizer evaluation cycle."""

    c_r: float  # total cost
    c_redundancy: float  # λ_R · Redundancy
    c_loss: float  # λ_L · Loss
    c_decision: float  # λ_D · DecisionCost
    diept: DIEPTState
    caki: float
    reweighted: bool  # True if logits were re-weighted
    original_text: str
    actuated_text: str  # text after actualization (may differ)
    token_count: int


class ActualizerEngine:
    """The engine that applies C(R) at the logit or text boundary.

    Provider-independent: it receives an InferenceResult and applies the
    cost functional. If the result has logits, it re-weights them; if not,
    it scores the text.
    """

    def __init__(
        self,
        weights: ConstitutionalWeights | None = None,
        thresholds: EpistemicThresholds | None = None,
        alpha: float = 2.0,
        redundancy_decay: float = 0.85,
        redundancy_window: int = 512,
    ) -> None:
        self.weights = weights or ConstitutionalWeights()
        self.thresholds = thresholds or EpistemicThresholds()
        self.alpha = alpha
        self.redundancy_decay = redundancy_decay
        self.redundancy_window = redundancy_window

    def actualize(
        self,
        result: InferenceResult,
        context: Sequence[Message] | None = None,
    ) -> ActualizerReport:
        """Apply C(R) to an inference result.

        If logits are available, re-weights them (real logit re-weighting).
        If not, scores the text (post-generation evaluation, honestly labeled).
        """
        ctx = list(context or [])

        diept = compute_diept_phase(result.text)
        caki = compute_caki(result.text, ctx)
        redundancy = self._compute_redundancy(result.text)

        # Loss — inverse of CAKI (low alignment = high loss)
        loss = 1.0 - caki

        # Decision cost — proportional to θ (speculation = costly decisions)
        decision_cost = diept.theta / (math.pi / 2)

        # C(R) = λ_R·Redundancy + λ_L·Loss + λ_D·DecisionCost
        c_redundancy = self.weights.lambda_r * redundancy
        c_loss = self.weights.lambda_l * loss
        c_decision = self.weights.lambda_d * decision_cost
        c_r = c_redundancy + c_loss + c_decision

        reweighted = False
        actuated_text = result.text
        if result.provider_supports_reweighting:
            actuated_text = self._reweight_logits(result)
            reweighted = True

        return ActualizerReport(
            c_r=c_r,
            c_redundancy=c_redundancy,
            c_loss=c_loss,
            c_decision=c_decision,
            diept=diept,
            caki=caki,
            reweighted=reweighted,
            original_text=result.text,
            actuated_text=actuated_text,
            token_count=result.token_count,
        )

    def _compute_redundancy(self, text: str) -> float:
        """Compute redundancy — token repetition with exponential decay.

        Redundancy is high when the same words appear many times within
        the redundancy window; recent repetition counts more than distant.
        """
        words = _WORD_RE.findall(text.lower())
        if len(words) < 2:
            return 0.0

        seen: dict[str, float] = {}
        total_redundancy = 0.0
        for i, w in enumerate(words):
            if w in seen:
                distance = i - seen[w]
                if distance < self.redundancy_window:
                    total_redundancy += self.redundancy_decay**distance
            seen[w] = float(i)

        return min(1.0, total_redundancy / max(1, len(words)))

    def _reweight_logits(self, result: InferenceResult) -> str:
        """Apply C(R) costs to logits and re-rank.

        For each logit vector: assign a cost to each token candidate based
        on the C(R) components, subtract the cost from the logit, and
        re-rank (the top candidate may change). Redundancy: recently
        emitted tokens cost more. Loss: speculative tokens cost more
        (Justice Dominance — dominant weight). DecisionCost: ambiguous
        (very short) tokens cost more.
        """
        recent_tokens: list[str] = []

        for lv in result.logit_history:
            recent_lower = {t.lower() for t in recent_tokens[-self.redundancy_window :]}
            costs: dict[str, float] = {}
            for cand in lv.candidates:
                token_lower = cand.token.lower()

                redundancy_cost = 0.5 if token_lower in recent_lower else 0.0

                loss_cost = 0.0
                if token_lower in SPECULATIVE_LEXICON:
                    loss_cost = self.weights.lambda_l * 2.0  # dominant weight

                decision_cost = 0.0
                if len(token_lower) <= 2:
                    decision_cost = self.weights.lambda_d * 0.5

                costs[cand.token] = (
                    self.weights.lambda_r * redundancy_cost + loss_cost + decision_cost
                ) * self.alpha

            lv.reweight(costs)

            top = lv.top_k(1)
            if top:
                recent_tokens.append(top[0].token)

        # Build actuated text from re-weighted selections. (In a real
        # system, the model would re-sample; here the re-ranked token
        # sequence is the actuated text.)
        actuated_tokens = [top[0].token for lv in result.logit_history if (top := lv.top_k(1))]
        if actuated_tokens:
            return " ".join(actuated_tokens)
        return result.text


class Actualizer:
    """Convenience wrapper: ActualizerEngine with default config."""

    def __init__(
        self,
        weights: ConstitutionalWeights | None = None,
        thresholds: EpistemicThresholds | None = None,
    ) -> None:
        self.engine = ActualizerEngine(weights=weights, thresholds=thresholds)

    def actualize(
        self,
        result: InferenceResult,
        context: Sequence[Message] | None = None,
    ) -> ActualizerReport:
        return self.engine.actualize(result, context)


__all__ = ["Actualizer", "ActualizerEngine", "ActualizerReport"]
