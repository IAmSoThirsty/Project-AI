from __future__ import annotations

from pathlib import Path

import pytest
from knowledge.extract import (
    ExtractionError,
    UnsupportedFormatError,
    extract_text,
    is_supported,
)


def test_is_supported() -> None:
    assert is_supported(Path("a.pdf"))
    assert is_supported(Path("a.HTML"))
    assert not is_supported(Path("a.doc"))
    assert not is_supported(Path("a.ppt"))


def test_html_extraction_strips_tags_and_scripts(tmp_path: Path) -> None:
    f = tmp_path / "page.html"
    f.write_text(
        "<html><head><style>.x{}</style></head>"
        "<body><script>evil()</script><p>hello world</p></body></html>",
        encoding="utf-8",
    )
    text = extract_text(f)
    assert "hello world" in text
    assert "evil()" not in text
    assert ".x{}" not in text


def test_unsupported_format_raises(tmp_path: Path) -> None:
    f = tmp_path / "legacy.doc"
    f.write_text("stuff", encoding="utf-8")
    with pytest.raises(UnsupportedFormatError):
        extract_text(f)


def test_malformed_pdf_raises_extraction_error(tmp_path: Path) -> None:
    # A file with a .pdf suffix but no valid PDF structure must be skippable,
    # not fatal (this is the failure that crashed the first full ingestion run).
    f = tmp_path / "broken.pdf"
    f.write_bytes(b"%PDF-1.4\nnot really a pdf\n%%EOF")
    with pytest.raises(ExtractionError):
        extract_text(f)
