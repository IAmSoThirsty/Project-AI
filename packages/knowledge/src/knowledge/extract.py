"""Text extraction for the corpus formats we ingest.

PDF (the overwhelming majority) is extracted with pypdf; HTML with the stdlib
parser. Legacy binary Office formats (.doc/.ppt) are not supported and raise
``UnsupportedFormatError`` so the caller can log and skip them honestly rather
than ingest garbage.
"""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

_SUPPORTED = frozenset({".pdf", ".html", ".htm"})
_TEXT_EXTENSIONS = frozenset(
    {
        ".md",
        ".markdown",
        ".txt",
        ".py",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".cfg",
        ".conf",
        ".sh",
        ".ps1",
        ".rst",
        ".csv",
        ".xml",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".css",
        ".scss",
        ".sass",
        ".sql",
    }
)
_SKIP_TAGS = frozenset({"script", "style"})


class ExtractionError(Exception):
    """Raised when a supported file cannot be read."""


class UnsupportedFormatError(ExtractionError):
    """Raised for file types we deliberately do not ingest."""


def is_supported(path: Path) -> bool:
    suffix = path.suffix.lower()
    return suffix in _SUPPORTED or suffix in _TEXT_EXTENSIONS


class _TextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self._parts.append(data)

    def text(self) -> str:
        return " ".join(self._parts)


def _extract_html(path: Path) -> str:
    parser = _TextHTMLParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    return parser.text()


def _extract_pdf(path: Path) -> str:
    import pypdf

    # Opening AND page-access are guarded together: pypdf resolves the document
    # root lazily on `.pages`, so a malformed file can raise there, not just at
    # construction. Any such failure becomes an ExtractionError the caller
    # skips.
    try:
        reader = pypdf.PdfReader(str(path))
        page_iter = list(reader.pages)
    except Exception as error:  # pypdf raises parse/decrypt errors
        raise ExtractionError(f"could not read PDF {path.name}: {error}") from error
    pages: list[str] = []
    for page in page_iter:
        try:
            pages.append(page.extract_text() or "")
        except Exception:  # a single bad page must not sink the document
            continue
    return "\n".join(pages)


def _extract_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def extract_text(path: Path) -> str:
    """Extract plain text from a supported file, else raise."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(path)
    if suffix in (".html", ".htm"):
        return _extract_html(path)
    if suffix in _TEXT_EXTENSIONS:
        return _extract_text_file(path)
    raise UnsupportedFormatError(f"unsupported format: {suffix or path.name}")
