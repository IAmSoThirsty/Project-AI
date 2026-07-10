"""Internal data types for the knowledge corpus pipeline.

These describe documents and chunks as they flow through ingestion. The public
retrieval surface returns :class:`kernel.KnowledgePassage`; these types are the
on-disk / in-memory representation the store is built from.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceDocument:
    """A single source file selected for ingestion."""

    filename: str
    title: str
    sha256: str
    size_bytes: int
    topic: str
    sensitivity: str


@dataclass(frozen=True)
class Chunk:
    """A deterministic, embeddable slice of a source document.

    ``chunk_id`` is the SHA-256 of ``source_sha256 | ordinal | text`` so the
    identity of a chunk is fully determined by its content and position — no
    hash, no inclusion.
    """

    chunk_id: str
    source: str
    title: str
    topic: str
    sensitivity: str
    ordinal: int
    text: str

    def __post_init__(self) -> None:
        if not self.chunk_id.strip():
            raise ValueError("chunk_id must not be empty")
        if self.ordinal < 0:
            raise ValueError("ordinal must be >= 0")
        if not self.text.strip():
            raise ValueError("text must not be empty")
