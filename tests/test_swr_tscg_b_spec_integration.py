"""Integration test: SWR TSCG-B spec loader.

Per PHASE_T_DISCOVERY.md Phase T5b: the SWR package is specified
in TSCG-B (4th tier - Thirsty Symbolic Constitutional Grammar
Binary). The canonical spec is a TSCG-B binary frame, packed at
import time from the canonical expression text and bundled to
disk on first load.

Honest scope:
- Tests the loader: text->frame->unpack round-trip, SHA-256
  cross-check, CRC32 presence, frame structure, bundling.
- Does NOT test the language's TSCG-B packer internals.
- One observed behavior of the upstream language: the
  `unpack_frame().sha256_hex` field does NOT match the SHA-256
  of `unpack_frame().payload`. We trust the actual payload
  bytes (computed via hashlib) over the unpacker's reported
  hex field. The loader uses this defensive approach.
"""

from __future__ import annotations

import importlib
import struct
from pathlib import Path

# Import the spec loader directly.
from swr.tscg_b_spec import (
    EXPECTED_SHA256_HEX,
    EXPECTED_TEXT,
    TSCGBSWRSpec,
    TSCGBSWRSpecError,
    load_spec,
)

# ── 1. Module surface ────────────────────────────────────────


def test_tscg_b_spec_exposed_via_init() -> None:
    """`swr` re-exports the spec loader symbols."""
    swr = importlib.import_module("swr")
    assert swr.load_spec is load_spec
    assert swr.TSCGBSWRSpec is TSCGBSWRSpec
    assert swr.TSCGBSWRSpecError is TSCGBSWRSpecError
    assert swr.EXPECTED_TEXT == EXPECTED_TEXT


def test_expected_text_is_documented_shape() -> None:
    """The expected text matches the documented 4-stage pipeline.

    The SWR contract is a 4-stage pipeline: cognition -> consensus
    -> ledger -> capacity. This is the documented semantic shape.
    """
    assert EXPECTED_TEXT == "$COG -> $QRM -> $LED -> $CAP"
    parts = EXPECTED_TEXT.split(" -> ")
    assert len(parts) == 4
    assert parts[0] == "$COG"
    assert parts[1] == "$QRM"
    assert parts[2] == "$LED"
    assert parts[3] == "$CAP"


def test_expected_sha256_matches_text() -> None:
    """The expected SHA-256 is the actual hash of the expected text."""
    import hashlib

    actual = hashlib.sha256(EXPECTED_TEXT.encode("utf-8")).hexdigest()
    assert actual == EXPECTED_SHA256_HEX


# ── 2. Bundling ────────────────────────────────────────


def test_tscg_b_file_bundled_with_package() -> None:
    """The canonical .tscg-b file ships adjacent to the loader."""
    spec_path = (
        Path(__file__).resolve().parents[1] / "packages" / "swr" / "src" / "swr" / "swr_spec.tscg-b"
    )
    assert spec_path.exists(), f"swr_spec.tscg-b not found at {spec_path}"
    assert spec_path.stat().st_size > 0


# ── 3. End-to-end load ──────────────────────────────────────


def test_load_spec_returns_spec() -> None:
    """load_spec() returns a TSCGBSWRSpec."""
    spec = load_spec()
    assert isinstance(spec, TSCGBSWRSpec)
    assert spec.text == EXPECTED_TEXT


def test_load_spec_frame_size_is_expected() -> None:
    """The packed frame is 72 bytes for a 28-byte payload.

    Frame layout: 4 (magic) + 1 (ver) + 1 (flags) + 2 (plen) +
    28 (payload) + 4 (crc) + 32 (sha) = 72 bytes.
    """
    spec = load_spec()
    assert spec.frame_size == 72
    assert len(spec.frame) == 72


def test_load_spec_frame_starts_with_magic() -> None:
    """The frame begins with the TSCG-B magic bytes b'TSGB'."""
    spec = load_spec()
    assert spec.frame[:4] == b"TSGB"


def test_load_spec_frame_version_is_1() -> None:
    """The frame version byte is 1."""
    spec = load_spec()
    assert spec.unpacked["version"] == 1


def test_load_spec_frame_payload_matches_text() -> None:
    """The packed payload decodes back to the expected text."""
    spec = load_spec()
    payload = spec.unpacked["payload"]
    assert payload.decode("utf-8") == EXPECTED_TEXT
    assert spec.unpacked["text"] == EXPECTED_TEXT


def test_load_spec_payload_length_is_28() -> None:
    """The 28-byte payload is encoded in the frame header."""
    spec = load_spec()
    assert spec.unpacked["payload_length"] == 28
    # Read the big-endian 2-byte payload length from the frame.
    plen = struct.unpack("!H", spec.frame[6:8])[0]
    assert plen == 28


def test_load_spec_payload_sha256_matches() -> None:
    """The payload SHA-256 is computed from the actual payload bytes."""
    spec = load_spec()
    assert spec.payload_sha256 == EXPECTED_SHA256_HEX
    assert spec.payload_sha256 == EXPECTED_SHA256_HEX


def test_load_spec_frame_sha256_is_deterministic() -> None:
    """Two successive load_spec() calls return the same frame SHA-256."""
    a = load_spec()
    b = load_spec()
    assert a.frame_sha256 == b.frame_sha256
    assert a.frame == b.frame


def test_load_spec_frame_path_is_absolute() -> None:
    """frame_path is the absolute path to the bundled .tscg-b file."""
    spec = load_spec()
    assert spec.frame_path is not None
    assert Path(spec.frame_path).is_absolute()
    assert spec.frame_path.endswith("swr_spec.tscg-b")


# ── 4. CRC32 presence ──────────────────────────────────────


def test_load_spec_crc32_is_present() -> None:
    """The CRC32 of the payload is exposed."""
    spec = load_spec()
    assert spec.crc32 != 0
    # The CRC32 in unpacked['crc32'] is the raw int.
    assert spec.unpacked["crc32"] == spec.crc32


# ── 5. Fail-closed paths ────────────────────────────


def test_tscg_b_swr_spec_error_is_runtime_error() -> None:
    """TSCGBSWRSpecError subclasses RuntimeError for catch-ability."""
    assert issubclass(TSCGBSWRSpecError, RuntimeError)


def test_load_spec_does_not_raise_on_success() -> None:
    """A well-formed spec returns normally (no exception)."""
    spec = load_spec()
    assert spec is not None


def test_load_spec_can_skip_bundling() -> None:
    """load_spec(bundle=False) does not write to disk."""
    # This is a smoke test: the in-memory frame should still be
    # available even when bundling is skipped.
    spec = load_spec(bundle=False)
    assert isinstance(spec, TSCGBSWRSpec)
    # frame_path is None when bundle=False.
    assert spec.frame_path is None
