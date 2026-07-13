"""
caretaker.providers.mock — Deterministic mock provider with synthetic logits.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/providers/mock.py``. Produces deterministic text
AND synthetic logits, so the Actualizer's logit re-weighting path can be
fully exercised without a live model.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Sequence
from typing import ClassVar

from caretaker.providers.base import (
    InferenceProvider,
    InferenceResult,
    LogitVector,
    Message,
    TokenCandidate,
)


def _seed_hash(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


class MockProvider(InferenceProvider):
    """Deterministic mock provider for testing.

    Generates text seeded by the input, and produces synthetic logit
    vectors so the re-weighting path is exercised.
    """

    # A small vocabulary for synthetic logit generation
    _VOCAB: ClassVar[list[str]] = [
        "The",
        "answer",
        "is",
        "Paris",
        "France",
        "London",
        "Berlin",
        "Tokyo",
        "Yes",
        "No",
        "maybe",
        "I",
        "think",
        "know",
        "believe",
        "perhaps",
        "certainly",
        "definitely",
        "possibly",
        "uncertain",
        "grounded",
        "speculative",
        "verified",
        "unverified",
        "evidence",
        "claims",
        "facts",
        "hypothesis",
        "theory",
        "truth",
        "false",
    ]

    def __init__(self, vocab: list[str] | None = None, top_k: int = 8) -> None:
        self._vocab = vocab or self._VOCAB
        self._top_k = top_k

    @property
    def name(self) -> str:
        return "mock"

    @property
    def exposes_logits(self) -> bool:
        return True

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        context: Sequence[Message] | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> InferenceResult:
        _ = context, temperature
        # Deterministic text from input hash
        seed = _seed_hash(f"{system_prompt}|{user_message}")
        text = f"[mock:{seed[:8]}] Response to: {user_message[:60]}"

        # Generate synthetic logit vectors for each "step"
        steps = min(max_tokens // 8, 32)
        logit_history: list[LogitVector] = []

        for step in range(steps):
            # Pseudo-random but deterministic logits
            step_seed = int(_seed_hash(f"{seed}:{step}"), 16)
            candidates: list[TokenCandidate] = []
            for i, token in enumerate(self._vocab[: self._top_k]):
                raw_logit = ((step_seed >> i) & 0xFF) / 255.0 * 4.0 - 2.0
                prob = math.exp(raw_logit)
                candidates.append(TokenCandidate(token=token, logit=raw_logit, probability=prob))
            # Normalize probabilities
            total = sum(c.probability for c in candidates)
            for c in candidates:
                c.probability /= total
            logit_history.append(LogitVector(candidates=candidates))

        return InferenceResult(
            text=text,
            token_count=steps * self._top_k,
            logit_history=logit_history,
            has_logits=True,
        )

    def health_check(self) -> bool:
        return True


__all__ = ["MockProvider"]
