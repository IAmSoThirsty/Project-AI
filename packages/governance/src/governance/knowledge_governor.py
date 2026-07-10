"""Knowledge-aware governor: ambient, advisory governance from a knowledge source.

This governor makes the pipeline *aware* of relevant reference knowledge while it
decides. It is advisory by construction: it never unilaterally authorizes an
action. It votes:

* ``ALLOW`` (annotating which knowledge informed the decision, when any is
  relevant) — the common case; or
* ``ESCALATE`` when the most relevant knowledge is dual-use / offensive and the
  action therefore warrants human review.

It never votes ``DENY`` — a knowledge base informs; it does not command. The
constitutional governors and the human operator retain final authority. The
concrete ``KnowledgeSource`` is injected, so the downward-only dependency graph
is preserved (governance depends only on the kernel interface).
"""

from __future__ import annotations

from collections.abc import Mapping

from governance.types import Vote
from kernel import ActionRequest, KnowledgeSource, Outcome


class KnowledgeAwareGovernor:
    """Advisory ``Governor`` backed by a :class:`kernel.KnowledgeSource`."""

    def __init__(
        self,
        source: KnowledgeSource,
        *,
        name: str = "knowledge-aware",
        escalate_sensitivities: frozenset[str] = frozenset({"offensive"}),
        score_threshold: float = 0.35,
        max_passages: int = 5,
    ) -> None:
        if not name.strip():
            raise ValueError("name must not be empty")
        if not 0.0 <= score_threshold <= 1.0:
            raise ValueError("score_threshold must be within [0.0, 1.0]")
        if max_passages < 1:
            raise ValueError("max_passages must be >= 1")
        self._source = source
        self._name = name
        self._escalate = escalate_sensitivities
        self._threshold = score_threshold
        self._max_passages = max_passages

    @property
    def name(self) -> str:
        return self._name

    def evaluate(self, request: ActionRequest, state: Mapping[str, object]) -> Vote:
        passages = self._source.relevant_to(request, state)
        relevant = tuple(p for p in passages if p.score >= self._threshold)[: self._max_passages]
        if not relevant:
            return Vote(self._name, Outcome.ALLOW)
        flagged = tuple(p for p in relevant if p.sensitivity in self._escalate)
        if flagged:
            cited = "; ".join(f"{p.title} [{p.sensitivity}]" for p in flagged[:3])
            return Vote(
                self._name,
                Outcome.ESCALATE,
                f"relevant knowledge is dual-use/offensive; human review advised ({cited})",
            )
        cited = "; ".join(p.title for p in relevant[:3])
        return Vote(self._name, Outcome.ALLOW, f"informed by reference knowledge ({cited})")
