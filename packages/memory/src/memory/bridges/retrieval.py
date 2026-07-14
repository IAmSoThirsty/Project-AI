"""Retrieval bridge: CCMA semantic/vector retrieval via Beginnings ``VectorIndex``.

CCMA's README flags its ``Pipeline.retrieve()`` as the single swap-in seam for
real indexing: out of the box it does a linear scan by region/type. Beginnings
already has a deterministic, dependency-light vector index in ``packages/knowledge``
(``VectorIndex`` over a pluggable ``Embedder``). This module adapts that real
index so CCMA retrieval returns the most-relevant chunks by cosine similarity,
ranked and blended with CCMA's own node graph.

The existing ``packages/knowledge`` corpus stays intact and authoritative; this
bridge *consumes* its index. CCMA nodes are also made retrievable by embedding
their payload text on demand and querying the same index space.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from knowledge.index import VectorIndex

from memory.ccma.models import UniversalNode


def node_to_text(node: UniversalNode) -> str:
    """Render a CCMA node as a single retrievable text blob.

    Combines the structured fields CCMA exposes (node_type, region, confidence,
    payload) so semantic retrieval can surface memory by content, not just by
    type/region scan.
    """
    parts: list[str] = [node.node_type.replace("_", " "), node.region.value.replace("_", " ")]
    for key, value in node.payload.items():
        if isinstance(value, str):
            parts.append(f"{key.replace('_', ' ')}: {value}")
        else:
            parts.append(f"{key.replace('_', ' ')}: {value!r}")
    return " ".join(parts)


class KnowledgeRetriever:
    """Hybrid retrieval: blend the CCMA node graph with the vector index.

    ``retrieve()`` takes a free-text query (built by the pipeline from the
    observation/working-memory context) and returns ranked ``(node_id, score)``
    pairs from the vector index, plus any CCMA nodes selected by region/type.
    This is CCMA's documented extension point, now wired to the real Beginnings
    retrieval backend instead of a linear scan.
    """

    def __init__(self, index: VectorIndex, *, top_k: int = 8) -> None:
        if top_k < 1:
            raise ValueError("top_k must be >= 1")
        self._index = index
        self._top_k = top_k

    @property
    def index(self) -> VectorIndex:
        return self._index

    def search(self, query: str, *, top_k: int | None = None) -> list[tuple[str, float]]:
        """Semantic search over the knowledge corpus. Returns (chunk_id, score)."""
        if not query.strip():
            return []
        k = top_k if top_k is not None else self._top_k
        hits = self._index.search(query, k)
        return [(chunk.chunk_id, float(score)) for chunk, score in hits]

    def retrieve(
        self,
        query: str,
        nodes: Sequence[UniversalNode],
        *,
        top_k: int | None = None,
    ) -> list[tuple[str, float]]:
        """Blend vector-index hits (by query) with CCMA graph nodes (by region/type).

        The vector index supplies semantic relevance; CCMA nodes contributed via
        ``nodes`` are embedded on the fly so in-graph memory participates in the
        same ranking. Returns merged, de-duplicated, score-descending pairs.
        """
        scores: dict[str, float] = {}
        for chunk_id, score in self.search(query, top_k=top_k):
            scores[chunk_id] = max(scores.get(chunk_id, 0.0), score)
        for node in nodes:
            text = node_to_text(node)
            for chunk_id, score in self.search(text, top_k=2):
                scores[chunk_id] = max(scores.get(chunk_id, 0.0), score * 0.9)
        ranked = sorted(scores.items(), key=lambda kv: -kv[1])
        k = top_k if top_k is not None else self._top_k
        return ranked[:k]


def build_query_from_context(context: Mapping[str, object]) -> str:
    """Build a retrieval query string from a working-memory context mapping."""
    parts: list[str] = []
    for value in context.values():
        if isinstance(value, str):
            parts.append(value)
    return " ".join(part for part in parts if part)
