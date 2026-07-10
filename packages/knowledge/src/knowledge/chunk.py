"""Deterministic text chunking with stable, content-addressed chunk IDs."""

from __future__ import annotations

import hashlib
import re

from knowledge.models import Chunk

_WHITESPACE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Collapse whitespace so chunking is stable across extraction quirks."""
    return _WHITESPACE.sub(" ", text).strip()


def compute_chunk_id(source_sha256: str, ordinal: int, text: str) -> str:
    """Content-address a chunk: SHA-256 of ``source | ordinal | text``."""
    digest = hashlib.sha256()
    digest.update(source_sha256.encode("utf-8"))
    digest.update(b"|")
    digest.update(str(ordinal).encode("utf-8"))
    digest.update(b"|")
    digest.update(text.encode("utf-8"))
    return digest.hexdigest()


def chunk_document(
    *,
    text: str,
    source: str,
    source_sha256: str,
    title: str,
    topic: str,
    sensitivity: str,
    chunk_size: int = 1000,
    overlap: int = 150,
) -> tuple[Chunk, ...]:
    """Split ``text`` into overlapping, deterministically-identified chunks.

    Chunking is character-based over normalized text. ``chunk_size`` and
    ``overlap`` are fixed so re-running ingestion yields identical chunk IDs.
    """
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")
    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap must satisfy 0 <= overlap < chunk_size")

    normalized = normalize_text(text)
    if not normalized:
        return ()

    stride = chunk_size - overlap
    chunks: list[Chunk] = []
    ordinal = 0
    start = 0
    length = len(normalized)
    while start < length:
        piece = normalized[start : start + chunk_size].strip()
        if piece:
            chunks.append(
                Chunk(
                    chunk_id=compute_chunk_id(source_sha256, ordinal, piece),
                    source=source,
                    title=title,
                    topic=topic,
                    sensitivity=sensitivity,
                    ordinal=ordinal,
                    text=piece,
                )
            )
            ordinal += 1
        start += stride
    return tuple(chunks)
