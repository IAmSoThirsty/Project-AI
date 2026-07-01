"""Thirsty-Lang TSCG spec loader for the Atlas package.

Per PHASE_T_DISCOVERY.md Phase T5: the Atlas package is specified
in TSCG (3rd tier - Thirsty Symbolic Constitutional Grammar). The
canonical spec is `atlas_spec.tscg`, colocated with this module.

The spec is parsed and validated at module import time. The
canonical form, checksum, and AST are exposed via
`load_spec()` for downstream consumers (audit chain, IDE, etc).

Failure mode: if the spec is missing, unparseable, or has
unknown symbols, a `TSCGAtlasSpecError` is raised. This is
fail-closed: a malformed spec is never silently bypassed.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    pass

# utf.tscg.* is the PyPI dep `thirsty-lang==0.8.1` (Phase T1). The
# dotted namespace `utf.tscg` is the language's third tier.
try:
    from utf.tscg.core import (
        canonical_form as _canonical_form,
    )
    from utf.tscg.core import (
        checksum as _checksum,
    )
    from utf.tscg.core import (
        parse as _tscg_parse,
    )
    from utf.tscg.core import (
        validate_symbols as _validate_symbols,
    )

    _TSCG_IMPORT_ERROR: str | None = None
except ImportError as _import_error:  # pragma: no cover - fail-closed
    _TSCG_IMPORT_ERROR = str(_import_error)
    _canonical_form = None  # type: ignore[assignment]
    _checksum = None  # type: ignore[assignment]
    _tscg_parse = None  # type: ignore[assignment]
    _validate_symbols = None  # type: ignore[assignment]


# Canonical .tscg source location (bundled with the atlas package).
_BUNDLED_SPEC_FILENAME: Final[str] = "atlas_spec.tscg"

# The expected canonical expression. Tests use this to assert the
# spec is what we think it is. The leading and trailing whitespace
# is normalized away.
EXPECTED_CANONICAL: Final[str] = "$COG -> $CAP -> $DNT"


class TSCGAtlasSpecError(RuntimeError):
    """Raised when the Atlas TSCG spec cannot be loaded or is invalid.

    Fail-closed surface. The atlas package treats a malformed spec
    as a hard failure: downstream code that depends on the spec
    must not run with a missing or invalid canonical form.
    """


@dataclass(frozen=True)
class TSCGAtlasSpec:
    """The loaded and validated Atlas TSCG spec.

    `source_text` is the raw text of the .tscg file (with comments
        preserved). Useful for display or audit.
    `expression` is the expression text (comments stripped, lines
        joined). This is what the parser sees.
    `ast` is the parsed AST node (root of the tree). The exact
        type depends on the expression shape; for the canonical
        Atlas contract it's a `PipelineExpr`.
    `canonical` is the canonical normalized form. Two specs that
        are semantically equivalent have the same canonical form.
    `checksum` is the SHA-256 of the canonical form. Used as a
        tamper-evident identifier for the spec.
    `source_hash` is the SHA-256 of the raw source text. Distinct
        from the checksum; the source_hash changes if comments
        change, the checksum changes only if the expression
        semantics change.
    `source_path` is the absolute path to the loaded .tscg file.
    """

    source_text: str
    expression: str
    ast: Any  # TSCGNode at runtime; typed Any to avoid leaking utf internals
    canonical: str
    checksum: str
    source_hash: str
    source_path: str

    def has_symbol(self, symbol_name: str) -> bool:
        """Return True if `symbol_name` appears in the canonical form.

        Symbols in TSCG are written `$NAME`; pass `NAME` (without
        the leading `$`).
        """
        needle = f"${symbol_name}"
        return needle in self.canonical


def _load_bundled_text() -> tuple[str, str, str]:
    """Load the bundled .tscg source.

    Returns (source_text, source_hash, source_path). Raises
    TSCGAtlasSpecError if the source cannot be read.
    """
    source_path = Path(__file__).parent / _BUNDLED_SPEC_FILENAME
    try:
        text = source_path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError) as exc:
        raise TSCGAtlasSpecError(f"atlas_spec.tscg not found at {source_path}: {exc}") from exc
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return text, digest, str(source_path)


def _strip_comments(text: str) -> str:
    """Strip `// ...` line comments and blank lines, return expression.

    TSCG doesn't have a built-in comment syntax; we treat lines
    starting with `//` (the canonical Python/shell style) as
    comments for the human-readable .tscg source files. The
    parser sees only the non-comment, non-blank lines joined by
    spaces.
    """
    out: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("//"):
            continue
        out.append(stripped)
    return " ".join(out)


def load_spec() -> TSCGAtlasSpec:
    """Load, parse, and validate the bundled Atlas TSCG spec.

    Returns a `TSCGAtlasSpec` with the parsed AST, canonical form,
    and checksums. Raises TSCGAtlasSpecError on any failure
    (missing dep, missing source, parse error, unknown symbols).

    The canonical form is asserted to equal `EXPECTED_CANONICAL`:
    if the source is edited in a way that changes the semantic
    shape of the contract, this raises a hard error. Downstream
    consumers (audit chain, IDE) can rely on the canonical form
    being a stable identifier.
    """
    if _TSCG_IMPORT_ERROR is not None:
        raise TSCGAtlasSpecError(f"thirsty-lang tscg import failed: {_TSCG_IMPORT_ERROR}")

    source_text, source_hash, source_path = _load_bundled_text()
    expression = _strip_comments(source_text)

    try:
        if _validate_symbols is None or _tscg_parse is None:
            raise TSCGAtlasSpecError("thirsty-lang tscg symbols unavailable")
        symbol_errors = _validate_symbols(expression)
        if symbol_errors:
            raise TSCGAtlasSpecError(f"unknown symbols in {source_path}: {symbol_errors}")
        ast = _tscg_parse(expression)
    except TSCGAtlasSpecError:
        raise
    except Exception as exc:
        raise TSCGAtlasSpecError(
            f"tscg parse failed for {source_path}: {type(exc).__name__}: {exc}"
        ) from exc

    canonical = _canonical_form(ast) if _canonical_form is not None else ""
    checksum = _checksum(canonical) if _checksum is not None else ""

    if canonical != EXPECTED_CANONICAL:
        raise TSCGAtlasSpecError(
            f"atlas spec canonical form mismatch: "
            f"expected {EXPECTED_CANONICAL!r}, got {canonical!r}. "
            f"If the contract has changed, update EXPECTED_CANONICAL "
            f"in tscg_spec.py to match the new semantic shape."
        )

    return TSCGAtlasSpec(
        source_text=source_text,
        expression=expression,
        ast=ast,
        canonical=canonical,
        checksum=checksum,
        source_hash=source_hash,
        source_path=source_path,
    )


__all__ = [
    "EXPECTED_CANONICAL",
    "TSCGAtlasSpec",
    "TSCGAtlasSpecError",
    "load_spec",
]
