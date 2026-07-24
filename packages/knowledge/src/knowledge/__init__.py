"""Project-AI knowledge layer: reference-corpus and repository retrieval."""

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
from knowledge.repository import (
    IndexUnavailable,
    RepositoryChunk,
    RepositoryIndex,
    RepositoryIndexError,
    RepositoryStatus,
    build_repository_index,
    discover_repository,
)
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
    "IndexUnavailable",
    "IngestReport",
    "KnowledgeStore",
    "Model2VecEmbedder",
    "RepositoryChunk",
    "RepositoryIndex",
    "RepositoryIndexError",
    "RepositoryStatus",
    "SourceDocument",
    "VectorIndex",
    "build_embedder",
    "build_knowledge_governor",
    "build_repository_index",
    "classify_sensitivity",
    "classify_topic",
    "discover_repository",
    "get_knowledge_store",
    "ingest_corpus",
    "is_in_scope",
    "query_from_request",
    "render_manifest",
    "reset_knowledge_store",
]
