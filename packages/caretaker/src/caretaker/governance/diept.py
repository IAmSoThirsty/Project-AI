"""
caretaker.governance.diept — Dynamic Inference and Epistemic Phase Transition.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/governance/diept.py``.

θ = arctan(‖B‖ / ‖A‖)

A = grounded, verified content (evidence, facts, established knowledge)
B = speculative, unverified content (hypothesis, guess, speculation)

θ ≈ 0     → full determinism (verified content only)
θ ≈ π/4   → balanced hypothesis
θ ≈ π/2   → pure speculation

Words are classified grounded (A) vs speculative (B) via a lexicon-based
heuristic — a lightweight deterministic approach suitable for testing the
invariants (a production system would use a trained classifier).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

# Grounded (A) lexicon — verified, factual, deterministic language
GROUNDED_LEXICON: frozenset[str] = frozenset(
    {
        # verification
        "verified",
        "confirmed",
        "established",
        "proven",
        "evidence",
        "fact",
        "known",
        "certain",
        "deterministic",
        "measured",
        "observed",
        "recorded",
        "documented",
        "tested",
        "validated",
        "empirical",
        "demonstrated",
        # data
        "data",
        "result",
        "output",
        "value",
        "number",
        "integer",
        "float",
        "string",
        "boolean",
        "true",
        "false",
        "null",
        "none",
        "zero",
        # actions grounded in code
        "return",
        "assert",
        "raise",
        "import",
        "define",
        "class",
        "def",
        # determinism
        "always",
        "never",
        "must",
        "shall",
        "is",
        "are",
        "was",
        "were",
        "equal",
        "equals",
        "match",
        "matches",
        # mock markers (from MockProvider)
        "mock",
        "response",
    }
)

# Speculative (B) lexicon — uncertain, hypothetical, speculative language
SPECULATIVE_LEXICON: frozenset[str] = frozenset(
    {
        # uncertainty
        "maybe",
        "perhaps",
        "possibly",
        "probably",
        "likely",
        "unlikely",
        "could",
        "might",
        "may",
        "would",
        "suppose",
        "supposed",
        "assume",
        "assumption",
        "guess",
        "estimate",
        "approximate",
        "roughly",
        # hypothesis
        "hypothesis",
        "hypothetical",
        "theory",
        "theoretical",
        "conjecture",
        "speculate",
        "speculation",
        "speculative",
        "believe",
        "belief",
        "think",
        "suspect",
        "wonder",
        # hedging
        "seems",
        "appears",
        "suggests",
        "indicates",
        "imply",
        "implying",
        "tending",
        "tentative",
        "uncertain",
        "unclear",
        "ambiguous",
        "unknown",
        "unsure",
    }
)


@dataclass
class DIEPTState:
    """State of the epistemic phase at a point in time."""

    theta: float
    norm_a: float
    norm_b: float
    grounded_count: int
    speculative_count: int
    quarantined: bool = False

    @property
    def phase_label(self) -> str:
        """Human-readable phase label."""
        if self.theta < 0.1:
            return "deterministic"
        if self.theta < 0.52:
            return "grounded"
        if self.theta < 0.785:
            return "balanced-hypothesis"
        if self.theta < 1.2:
            return "speculative"
        return "pure-speculation"


def compute_diept_phase(text: str) -> DIEPTState:
    """Compute the DIEPT phase angle for a text response.

    Classifies words into grounded (A) vs speculative (B) using lexicons,
    then computes θ = arctan(‖B‖ / ‖A‖).
    """
    words = re.findall(r"[a-zA-Z_]+", text.lower())
    grounded = 0
    speculative = 0

    for w in words:
        if w in GROUNDED_LEXICON:
            grounded += 1
        elif w in SPECULATIVE_LEXICON:
            speculative += 1

    # Add baseline so empty text doesn't produce NaN
    norm_a = float(grounded + 1)
    norm_b = float(speculative)

    theta = math.atan2(norm_b, norm_a)

    return DIEPTState(
        theta=theta,
        norm_a=norm_a,
        norm_b=norm_b,
        grounded_count=grounded,
        speculative_count=speculative,
        quarantined=theta > 0.785,
    )


__all__ = ["GROUNDED_LEXICON", "SPECULATIVE_LEXICON", "DIEPTState", "compute_diept_phase"]
