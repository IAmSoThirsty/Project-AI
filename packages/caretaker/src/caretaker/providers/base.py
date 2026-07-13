"""
caretaker.providers.base — Provider abstraction for the Actualizer.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/providers/base.py`` (an unused ``numpy`` import
was dropped — the module is pure stdlib).

A provider that exposes logits can be re-weighted BEFORE generation
completes. A provider that doesn't (like Ollama) falls back to candidate
re-ranking after generation. The Actualizer handles both.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

# A conversation message: {"role": ..., "content": ...}
Message = Mapping[str, str]


@dataclass
class TokenCandidate:
    """A single token candidate at a generation step.

    token: the token string
    logit: raw logit from the model
    probability: softmax probability
    cost: C(R) cost assigned by the Actualizer (filled during re-weighting)
    """

    token: str
    logit: float
    probability: float
    cost: float = 0.0

    @property
    def reweighted_logit(self) -> float:
        """Logit after C(R) cost subtraction. Used for re-sampling."""
        return self.logit - self.cost


@dataclass
class LogitVector:
    """Logits for a single generation step (one position in the sequence)."""

    candidates: list[TokenCandidate] = field(default_factory=list)

    @property
    def has_logits(self) -> bool:
        return len(self.candidates) > 0

    def top_k(self, k: int) -> list[TokenCandidate]:
        """Return the top-k candidates by reweighted logit."""
        ranked = sorted(self.candidates, key=lambda c: c.reweighted_logit, reverse=True)
        return ranked[:k]

    def reweight(self, costs: Mapping[str, float]) -> None:
        """Apply C(R) costs to candidates by token string."""
        for c in self.candidates:
            c.cost = costs.get(c.token, 0.0)


@dataclass
class InferenceResult:
    """Result of a single inference call."""

    text: str
    token_count: int
    logit_history: list[LogitVector] = field(default_factory=list)
    has_logits: bool = False

    @property
    def provider_supports_reweighting(self) -> bool:
        """True if this result contains real logit data for re-weighting."""
        return self.has_logits and len(self.logit_history) > 0


class InferenceProvider(ABC):
    """Abstract inference provider. The model is untrusted — it produces
    candidates, governance authorizes execution.

    Providers that expose logits fill logit_history. Providers that don't
    leave it empty, and the Actualizer falls back to post-generation scoring.
    """

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def exposes_logits(self) -> bool: ...

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_message: str,
        context: Sequence[Message] | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> InferenceResult: ...

    @abstractmethod
    def health_check(self) -> bool: ...


__all__ = [
    "InferenceProvider",
    "InferenceResult",
    "LogitVector",
    "Message",
    "TokenCandidate",
]
