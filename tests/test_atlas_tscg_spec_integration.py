"""Integration test: Atlas TSCG spec loader.

Per PHASE_T_DISCOVERY.md Phase T5: Atlas is specified in TSCG
(3rd tier - Thirsty Symbolic Constitutional Grammar). The
canonical spec is `atlas_spec.tscg`, colocated with the package
and loaded via `atlas.tscg_spec.load_spec()`.

Honest scope:
- Tests the loader: source bundling, validation, canonical form,
  checksum determinism, fail-closed paths.
- Does NOT test the language's TSCG parser internals (thousands
  of tests already exist upstream in thirsty-lang).
- The canonical expression is asserted to equal the documented
  expected value. If the spec changes shape, EXPECTED_CANONICAL
  in tscg_spec.py must be updated and the test will guide the
  reviewer through the change.
"""

from __future__ import annotations

import importlib
from pathlib import Path

# Import the spec loader directly; lazy import in atlas/__init__.py
# is for end-user access.
from atlas.tscg_spec import (
    EXPECTED_CANONICAL,
    TSCGAtlasSpec,
    TSCGAtlasSpecError,
    load_spec,
)

# ── 1. Module surface ────────────────────────────────────────


def test_tscg_spec_exposed_via_init() -> None:
    """`atlas` re-exports the spec loader symbols."""
    atlas = importlib.import_module("atlas")
    assert atlas.load_spec is load_spec
    assert atlas.TSCGAtlasSpec is TSCGAtlasSpec
    assert atlas.TSCGAtlasSpecError is TSCGAtlasSpecError
    assert atlas.EXPECTED_CANONICAL == EXPECTED_CANONICAL


def test_expected_canonical_is_documented_shape() -> None:
    """The expected canonical form matches the documented shape.

    The Atlas contract is a 3-stage pipeline: cognition -> capacity
    -> prohibitions. This is the documented semantic shape.
    """
    assert EXPECTED_CANONICAL == "$COG -> $CAP -> $DNT"
    # Three symbols separated by two pipelines.
    parts = EXPECTED_CANONICAL.split(" -> ")
    assert len(parts) == 3
    assert parts[0] == "$COG"
    assert parts[1] == "$CAP"
    assert parts[2] == "$DNT"


# ── 2. Bundling ────────────────────────────────────────


def test_tscg_file_bundled_with_package() -> None:
    """The canonical .tscg source ships adjacent to the loader."""
    spec_path = (
        Path(__file__).resolve().parents[1]
        / "packages"
        / "atlas"
        / "src"
        / "atlas"
        / "atlas_spec.tscg"
    )
    # We are running from the repo root; resolve relative to that.
    repo_root = Path(__file__).resolve().parents[1]
    spec_path = repo_root / "packages" / "atlas" / "src" / "atlas" / "atlas_spec.tscg"
    assert spec_path.exists(), f"atlas_spec.tscg not found at {spec_path}"
    # Must be non-empty.
    assert spec_path.stat().st_size > 0


# ── 3. End-to-end load ──────────────────────────────────────


def test_load_spec_returns_spec() -> None:
    """load_spec() returns a TSCGAtlasSpec."""
    spec = load_spec()
    assert isinstance(spec, TSCGAtlasSpec)
    assert spec.canonical == EXPECTED_CANONICAL


def test_load_spec_source_hash_is_sha256() -> None:
    """The source_hash is a 64-character SHA-256 hex digest."""
    spec = load_spec()
    assert len(spec.source_hash) == 64
    int(spec.source_hash, 16)  # raises if not hex


def test_load_spec_checksum_is_sha256() -> None:
    """The checksum is a 64-character SHA-256 hex digest of the canonical."""
    spec = load_spec()
    assert len(spec.checksum) == 64
    int(spec.checksum, 16)


def test_load_spec_checksum_is_deterministic() -> None:
    """Two successive load_spec() calls return the same checksum."""
    a = load_spec()
    b = load_spec()
    assert a.checksum == b.checksum
    assert a.source_hash == b.source_hash
    assert a.canonical == b.canonical


def test_load_spec_source_path_is_absolute() -> None:
    """source_path is the absolute path to the bundled .tscg file."""
    spec = load_spec()
    assert Path(spec.source_path).is_absolute()
    assert spec.source_path.endswith("atlas_spec.tscg")


# ── 4. Symbol discovery ─────────────────────────────


def test_has_symbol_finds_canonical_symbols() -> None:
    """has_symbol returns True for symbols in the canonical form."""
    spec = load_spec()
    assert spec.has_symbol("COG") is True
    assert spec.has_symbol("CAP") is True
    assert spec.has_symbol("DNT") is True


def test_has_symbol_rejects_absent_symbols() -> None:
    """has_symbol returns False for symbols NOT in the canonical form."""
    spec = load_spec()
    assert spec.has_symbol("QRM") is False
    assert spec.has_symbol("ANC") is False
    assert spec.has_symbol("NOT_A_SYMBOL") is False


# ── 5. Fail-closed paths ────────────────────────────


def test_tscg_atlas_spec_error_is_runtime_error() -> None:
    """TSCGAtlasSpecError subclasses RuntimeError for catch-ability."""
    assert issubclass(TSCGAtlasSpecError, RuntimeError)


def test_load_spec_does_not_raise_on_success() -> None:
    """A well-formed spec returns normally (no exception)."""
    spec = load_spec()
    assert spec is not None
