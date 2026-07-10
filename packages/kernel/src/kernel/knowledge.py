"""Knowledge-source interface for knowledge-aware governance.

Defines the minimal contract that lets the governance layer be *aware* of
relevant reference knowledge when evaluating an action, without importing any
concrete retrieval implementation. This preserves the downward-only dependency
graph: governance depends only on this kernel interface, and a concrete
``KnowledgeSource`` (which may pull in heavy retrieval machinery) is injected at
composition time by the top layer.

The contract is deliberately advisory. A ``KnowledgeSource`` surfaces passages
that are *relevant* to a decision; it never renders a verdict. Governance
retains sole authority over ALLOW / DENY / ESCALATE.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from kernel.types import ActionRequest


@dataclass(frozen=True)
class KnowledgePassage:
    """A single retrieved passage with provenance and sensitivity tagging.

    ``sensitivity`` is a coarse dual-use label ("educational" | "dual_use" |
    "offensive") the governance layer can gate on. ``score`` is a similarity in
    ``[0.0, 1.0]`` where higher is more relevant.
    """

    passage_id: str
    source: str
    title: str
    topic: str
    sensitivity: str
    text: str
    score: float

    def __post_init__(self) -> None:
        if not self.passage_id.strip():
            raise ValueError("passage_id must not be empty")
        if not self.source.strip():
            raise ValueError("source must not be empty")
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be within [0.0, 1.0]")


@runtime_checkable
class KnowledgeSource(Protocol):
    """Read-only, deterministic retrieval consulted during governance.

    Implementations MUST be side-effect free and deterministic for a given
    index: the same request/state must yield the same passages. Returned
    passages should be ordered most-relevant first.
    """

    def relevant_to(
        self, request: ActionRequest, state: Mapping[str, object]
    ) -> tuple[KnowledgePassage, ...]: ...
