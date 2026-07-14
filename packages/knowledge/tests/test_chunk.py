from __future__ import annotations

import pytest
from knowledge.chunk import chunk_document, compute_chunk_id, normalize_text


def test_normalize_collapses_whitespace() -> None:
    assert normalize_text("a\n\n  b\t c ") == "a b c"


def test_chunk_ids_are_deterministic_and_content_addressed() -> None:
    text = "word " * 100
    first = chunk_document(
        text=text,
        source="doc.pdf",
        source_sha256="f" * 64,
        title="Doc",
        topic="programming",
        sensitivity="educational",
        chunk_size=50,
        overlap=10,
    )
    second = chunk_document(
        text=text,
        source="doc.pdf",
        source_sha256="f" * 64,
        title="Doc",
        topic="programming",
        sensitivity="educational",
        chunk_size=50,
        overlap=10,
    )
    assert [c.chunk_id for c in first] == [c.chunk_id for c in second]
    assert first[0].chunk_id == compute_chunk_id("f" * 64, 0, first[0].text)
    assert first[0].ordinal == 0 and first[1].ordinal == 1


def test_chunk_overlap_and_coverage() -> None:
    text = "abcdefghij" * 10  # 100 chars, no whitespace
    chunks = chunk_document(
        text=text,
        source="d",
        source_sha256="a" * 64,
        title="t",
        topic="general",
        sensitivity="educational",
        chunk_size=40,
        overlap=10,
    )
    assert len(chunks) >= 3
    assert all(len(c.text) <= 40 for c in chunks)


def test_empty_text_yields_no_chunks() -> None:
    assert (
        chunk_document(
            text="   \n  ",
            source="d",
            source_sha256="a" * 64,
            title="t",
            topic="general",
            sensitivity="educational",
        )
        == ()
    )


def test_invalid_parameters_rejected() -> None:
    with pytest.raises(ValueError):
        chunk_document(
            text="x",
            source="d",
            source_sha256="a" * 64,
            title="t",
            topic="general",
            sensitivity="educational",
            chunk_size=0,
        )
    with pytest.raises(ValueError):
        chunk_document(
            text="x",
            source="d",
            source_sha256="a" * 64,
            title="t",
            topic="general",
            sensitivity="educational",
            chunk_size=10,
            overlap=10,
        )
