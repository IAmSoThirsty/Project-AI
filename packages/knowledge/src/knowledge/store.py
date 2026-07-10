"""The read-only knowledge store consulted by knowledge-aware governance.

``KnowledgeStore`` implements :class:`kernel.KnowledgeSource`: given an
``ActionRequest`` and the governance ``state`` mapping, it derives a query and
returns the most relevant, provenance-tagged passages from the corpus index. It
is deterministic and side-effect free — nothing is "searched" by an external
caller; governance simply becomes *aware* of what the corpus says about the
action at hand.
"""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path

from kernel import ActionRequest, KnowledgePassage
from knowledge.embedding import build_embedder
from knowledge.index import VectorIndex

_DATA_DIR_ENV = "PROJECT_AI_KNOWLEDGE_DIR"


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


def query_from_request(request: ActionRequest, state: Mapping[str, object]) -> str:
    """Build a retrieval query from the action being governed.

    Combines the operation, resource, and any string-ish payload/state values so
    the store surfaces knowledge about what the action actually concerns.
    """
    parts: list[str] = [request.operation, request.resource]
    for value in request.payload.values():
        if isinstance(value, str):
            parts.append(value)
    topic = state.get("topic")
    if isinstance(topic, str):
        parts.append(topic)
    return " ".join(part for part in parts if part)


class KnowledgeStore:
    """A ``KnowledgeSource`` backed by a :class:`VectorIndex`."""

    def __init__(self, index: VectorIndex, *, top_k: int = 5) -> None:
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        self._index = index
        self._top_k = top_k

    def __len__(self) -> int:
        return len(self._index)

    def relevant_to(
        self, request: ActionRequest, state: Mapping[str, object]
    ) -> tuple[KnowledgePassage, ...]:
        query = query_from_request(request, state)
        if not query.strip() or not len(self._index):
            return ()
        hits = self._index.search(query, self._top_k)
        return tuple(
            KnowledgePassage(
                passage_id=chunk.chunk_id,
                source=chunk.source,
                title=chunk.title,
                topic=chunk.topic,
                sensitivity=chunk.sensitivity,
                text=chunk.text,
                score=_clamp_unit(score),
            )
            for chunk, score in hits
        )

    @classmethod
    def load(cls, directory: Path, *, top_k: int = 5) -> KnowledgeStore:
        """Load a persisted index, reconstructing the embedder from its metadata."""
        meta = json.loads((directory / "meta.json").read_text(encoding="utf-8"))
        embedder = build_embedder(str(meta["embedder"]))
        return cls(VectorIndex.load(directory, embedder), top_k=top_k)


_store: KnowledgeStore | None = None


def get_knowledge_store(*, top_k: int = 5) -> KnowledgeStore:
    """Return the process-wide knowledge store, loading it from disk on first use.

    The index directory is taken from ``$PROJECT_AI_KNOWLEDGE_DIR`` (default
    ``data/knowledge``). Raises ``FileNotFoundError`` with a clear message if no
    index has been built yet.
    """
    global _store
    if _store is None:
        directory = Path(os.environ.get(_DATA_DIR_ENV, "data/knowledge"))
        if not (directory / "meta.json").exists():
            raise FileNotFoundError(
                f"no knowledge index at {directory} — run `python -m knowledge.ingest` "
                f"or set ${_DATA_DIR_ENV}"
            )
        _store = KnowledgeStore.load(directory, top_k=top_k)
    return _store


def reset_knowledge_store() -> None:
    """Drop the cached store (test hook / re-index)."""
    global _store
    _store = None
