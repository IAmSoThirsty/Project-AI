"""Composition helper that binds the on-disk index into a knowledge-aware governor.

This is the opt-in activation seam. A composition site (an engine builder, the
CLI, or a service) calls :func:`build_knowledge_governor` and, if an index has
been built, adds the returned governor to its
``GovernanceEngine(governors=(...))`` tuple. When no index exists yet it returns
``None`` so wiring it in is non-breaking — the system simply runs without corpus
awareness until an index is present.
"""

from __future__ import annotations

from governance import KnowledgeAwareGovernor
from knowledge.store import get_knowledge_store


def build_knowledge_governor(
    *,
    top_k: int = 5,
    score_threshold: float = 0.35,
    escalate_sensitivities: frozenset[str] = frozenset({"offensive"}),
) -> KnowledgeAwareGovernor | None:
    """Return a governor over the built index, or ``None`` if none exists yet.

    The index directory is resolved from ``$PROJECT_AI_KNOWLEDGE_DIR`` (default
    ``data/knowledge``) by :func:`knowledge.store.get_knowledge_store`.
    """
    try:
        store = get_knowledge_store(top_k=top_k)
    except FileNotFoundError:
        return None
    return KnowledgeAwareGovernor(
        store,
        score_threshold=score_threshold,
        escalate_sensitivities=escalate_sensitivities,
    )
