"""Project-AI knowledge layer: reference-corpus retrieval for governance.

Public surface:

* :class:`KnowledgeStore` — a :class:`kernel.KnowledgeSource` backed by a vector
  index; ``get_knowledge_store()`` / ``reset_knowledge_store()`` follow the
  repo's singleton convention.
* :class:`VectorIndex` — deterministic in-memory index with on-disk persistence.
* Embedders — :class:`HashingEmbedder` (dependency-free, deterministic) and
  :class:`Model2VecEmbedder` (semantic, torch-free static embeddings).
* Ingestion — :func:`ingest_corpus` and the ``knowledge.ingest`` CLI.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version

from knowledge.binding import build_knowledge_governor
from knowledge.classify import classify_sensitivity, classify_topic, is_in_scope
from knowledge.embedding import (
    Embedder,
    HashingEmbedder,
    Model2VecEmbedder,
    build_embedder,
)
from knowledge.index import VectorIndex
from knowledge.ingest import DocRecord, IngestReport, ingest_corpus, render_manifest
from knowledge.models import Chunk, SourceDocument
from knowledge.store import (
    KnowledgeStore,
    get_knowledge_store,
    query_from_request,
    reset_knowledge_store,
)

try:
    __version__ = _pkg_version("project-ai-knowledge")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0.dev0"

__all__ = [
    "Chunk",
    "DocRecord",
    "Embedder",
    "HashingEmbedder",
    "IngestReport",
    "KnowledgeStore",
    "Model2VecEmbedder",
    "SourceDocument",
    "VectorIndex",
    "build_embedder",
    "build_knowledge_governor",
    "classify_sensitivity",
    "classify_topic",
    "get_knowledge_store",
    "ingest_corpus",
    "is_in_scope",
    "query_from_request",
    "render_manifest",
    "reset_knowledge_store",
]
