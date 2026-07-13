"""
caretaker.governance.caki — Contextual Alignment & Knowledge Integrity.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/governance/caki.py``. A monotonic metric —
higher is better — measuring how well a response aligns with its context
and maintains knowledge integrity.

CAKI ∈ [0, 1]:
  0 = no alignment / knowledge loss
  1 = perfect alignment / full knowledge integrity

Components: context overlap, information density, determinism score.
Adding verified content increases CAKI; speculation or filler decreases it.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence

from caretaker.governance.diept import GROUNDED_LEXICON, SPECULATIVE_LEXICON

_FILLER: frozenset[str] = frozenset(
    {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "to",
        "of",
        "in",
        "on",
        "at",
        "by",
        "for",
        "it",
        "its",
        "this",
        "that",
        "and",
        "or",
        "but",
        "as",
        "be",
        "been",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "can",
        "could",
    }
)


def compute_caki(text: str, context: Sequence[Mapping[str, str]] | None = None) -> float:
    """Compute the CAKI score for a text response.

    Args:
        text: the response text.
        context: prior conversation context (list of message dicts).

    Returns:
        CAKI score in [0, 1].
    """
    if not text or not text.strip():
        return 0.0

    # Component 1: Information density — ratio of non-filler content
    words = re.findall(r"[a-zA-Z_]{2,}", text)
    if not words:
        return 0.0
    content_words = [w for w in words if w.lower() not in _FILLER]
    density = len(content_words) / len(words)

    # Component 2: Context overlap — vocabulary reuse from context
    overlap = 0.0
    if context:
        ctx_words: set[str] = set()
        for msg in context:
            content = msg.get("content", "")
            ctx_words.update(re.findall(r"[a-zA-Z_]{2,}", content.lower()))
        if ctx_words:
            response_words = {w.lower() for w in words}
            overlap = len(response_words & ctx_words) / len(response_words)

    # Component 3: Determinism score — grounded vs speculative
    grounded = sum(1 for w in words if w.lower() in GROUNDED_LEXICON)
    speculative = sum(1 for w in words if w.lower() in SPECULATIVE_LEXICON)
    total_marked = grounded + speculative
    determinism = grounded / total_marked if total_marked > 0 else 0.5

    # Weighted combination — monotonic in each component
    caki = 0.4 * density + 0.3 * overlap + 0.3 * determinism

    return max(0.0, min(1.0, caki))


__all__ = ["compute_caki"]
