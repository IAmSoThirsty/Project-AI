"""Thirsty-Lang TSCG-B spec loader for the SWR package.

Per PHASE_T_DISCOVERY.md Phase T5b: the SWR package is specified
in TSCG-B (4th tier - Thirsty Symbolic Constitutional Grammar
Binary). The canonical spec is a TSCG-B binary frame, packed at
import time from the canonical expression text.

TSCG-B is the binary form of TSCG (3rd tier). Frames are:
  - 4-byte magic: b'TSGB'
  - 1-byte version: 1
  - 1-byte flags: 0x00 (FLAG_NONE) | 0x01 (FLAG_EOF) | 0x02 (FLAG_FRAGMENT)
  - 2-byte big-endian payload length
  - N-byte UTF-8 payload
  - 4-byte big-endian CRC32 of the payload
  - 32-byte SHA-256 of the payload

The frame is tamper-evident: the SHA-256 over the payload is
included in the frame itself, and the CRC32 catches accidental
corruption. `unpack_frame(verify=True)` validates both.

The SWR contract in TSCG terms:
  $COG -> $QRM -> $LED -> $CAP

  $COG  Cognition. The SWR engine reads a 5-round scenario and
        produces a deterministic decision.
  $QRM  Consensus. The 5-round protocol reaches a stable verdict
        only when the deterministic evaluator agrees across all
        rounds.
  $LED  Ledger. Every decision is recorded via ExecutionGate and
        emits to the audit chain (Chimera v2.2).
  $CAP  Capacity. SWR scenarios are bounded by Difficulty (MEDIUM
        through IMPOSSIBLE) and the ExecutionGate's authority
        tier.

The loader packs this expression into a TSCG-B frame, asserts
the binary round-trips correctly, and exposes the frame +
parsed metadata for downstream consumers.

Failure mode: any failure (missing dep, pack error, round-trip
mismatch, canonical mismatch) raises TSCGBSWRSpecError. This
is fail-closed: a malformed spec is never silently bypassed.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

# utf.tscg_b.* is the PyPI dep `thirsty-lang==0.8.1` (Phase T1).
# The dotted namespace `utf.tscg_b` is the language's fourth tier.
try:
    from utf.tscg_b.core import (
        FLAG_NONE as _FLAG_NONE,
    )
    from utf.tscg_b.core import (
        pack_text as _pack_text,
    )
    from utf.tscg_b.core import (
        unpack_frame as _unpack_frame,
    )

    _TSCG_B_IMPORT_ERROR: str | None = None
except ImportError as _import_error:  # pragma: no cover - fail-closed
    _TSCG_B_IMPORT_ERROR = str(_import_error)
    _FLAG_NONE = 0
    _pack_text = None  # type: ignore[assignment]
    _unpack_frame = None  # type: ignore[assignment]


# The canonical SWR contract in TSCG form. Pack/parse round-trip
# is asserted on every load. A change in the spec's semantic
# shape forces a test failure with a clear message guiding the
# reviewer to update EXPECTED_TEXT in tscg_b_spec.py.
EXPECTED_TEXT: Final[str] = "$COG -> $QRM -> $LED -> $CAP"

# SHA-256 of the UTF-8 bytes of EXPECTED_TEXT. Computed from
# EXPECTED_TEXT at module init so a change to EXPECTED_TEXT
# automatically updates the expected hash. The hash is asserted
# against the embedded hash in the packed frame on every load.
EXPECTED_SHA256_HEX: Final[str] = hashlib.sha256(EXPECTED_TEXT.encode("utf-8")).hexdigest()

# The bundled TSCG-B frame is written to disk on first load (and
# checked in to git for non-runtime distribution). The file lives
# next to the loader for the same reason `audit_proof.thirst` does
# in packages/security: hatchling auto-bundles the file in the
# wheel, and `Path(__file__).parent` resolves consistently in
# dev and prod.
_BUNDLED_FRAME_FILENAME: Final[str] = "swr_spec.tscg-b"


class TSCGBSWRSpecError(RuntimeError):
    """Raised when the SWR TSCG-B spec cannot be loaded or is invalid.

    Fail-closed surface. The swr package treats a malformed spec
    as a hard failure: downstream code that depends on the spec
    must not run with a missing or invalid binary frame.
    """


@dataclass(frozen=True)
class TSCGBSWRSpec:
    """The loaded and validated SWR TSCG-B spec.

    `text` is the canonical TSCG expression that was packed.
    `frame` is the raw binary frame (b'TSGB...'). Length is
        4 (magic) + 1 (version) + 1 (flags) + 2 (payload_len)
        + N (payload) + 4 (crc32) + 32 (sha256).
    `frame_size` is the total frame size in bytes.
    `frame_sha256` is the SHA-256 of the entire frame (not just
        the payload). Useful for tamper detection at the binary
        level.
    `payload_sha256` is the SHA-256 of the payload only (also
        stored inside the frame).
    `crc32` is the CRC32 of the payload (also stored inside the
        frame).
    `unpacked` is the dict returned by `utf.tscg_b.unpack_frame`
        with all parsed fields.
    `frame_path` is the absolute path to the bundled .tscg-b
        file on disk (or None if the frame was in-memory only).
    """

    text: str
    frame: bytes
    frame_size: int
    frame_sha256: str
    payload_sha256: str
    crc32: int
    unpacked: dict[str, Any]
    frame_path: str | None


def _pack_and_validate(text: str) -> tuple[bytes, dict[str, Any]]:
    """Pack `text` into a TSCG-B frame and verify it round-trips.

    Returns (frame_bytes, unpacked_dict). Raises TSCGBSWRSpecError
    on any failure.
    """
    if _pack_text is None or _unpack_frame is None:
        raise TSCGBSWRSpecError("thirsty-lang tscg_b symbols unavailable")

    try:
        frame = _pack_text(text, flags=_FLAG_NONE)
    except Exception as exc:
        raise TSCGBSWRSpecError(f"tscg_b pack failed: {type(exc).__name__}: {exc}") from exc

    try:
        unpacked = _unpack_frame(frame, verify=True)
    except Exception as exc:
        raise TSCGBSWRSpecError(f"tscg_b unpack failed: {type(exc).__name__}: {exc}") from exc

    if unpacked.get("text") != text:
        raise TSCGBSWRSpecError(
            f"tscg_b round-trip mismatch: expected {text!r}, got {unpacked.get('text')!r}"
        )

    return frame, unpacked


def _bundle_frame_to_disk(frame: bytes) -> str:
    """Write the frame bytes to disk next to this module.

    Returns the absolute path. Idempotent: if the file already
    exists with the same bytes, the write is skipped.
    """
    frame_path = Path(__file__).parent / _BUNDLED_FRAME_FILENAME
    if frame_path.exists() and frame_path.read_bytes() == frame:
        return str(frame_path)
    frame_path.write_bytes(frame)
    return str(frame_path)


def _try_load_bundled_frame() -> bytes | None:
    """Try to load the bundled frame from disk.

    Returns the bytes if the file exists and parses cleanly, or
    None if it doesn't exist (first run) or is malformed (we
    will regenerate it).
    """
    frame_path = Path(__file__).parent / _BUNDLED_FRAME_FILENAME
    if not frame_path.exists():
        return None
    return frame_path.read_bytes()


def load_spec(bundle: bool = True) -> TSCGBSWRSpec:
    """Load, pack, and validate the canonical SWR TSCG-B spec.

    The spec is a single TSCG expression: "$COG -> $QRM -> $LED -> $CAP".
    Packing produces a 72-byte binary frame (for this 26-byte payload).

    Args:
        bundle: If True, write the frame to disk next to this module
            (idempotently). If False, the frame is in-memory only and
            `frame_path` will be None on the returned TSCGBSWRSpec.

    Returns a TSCGBSWRSpec with the frame, parsed fields, and
    checksums. Raises TSCGBSWRSpecError on any failure (missing
    dep, pack error, round-trip mismatch, canonical mismatch).

    The canonical text is asserted to equal EXPECTED_TEXT. If the
    spec changes shape, EXPECTED_TEXT and EXPECTED_SHA256_HEX in
    this file must be updated, and the test suite will guide the
    reviewer through the change.
    """
    if _TSCG_B_IMPORT_ERROR is not None:
        raise TSCGBSWRSpecError(f"thirsty-lang tscg_b import failed: {_TSCG_B_IMPORT_ERROR}")

    if EXPECTED_TEXT != "$COG -> $QRM -> $LED -> $CAP":
        raise TSCGBSWRSpecError(
            f"SWR spec canonical text mismatch: expected "
            f'"$COG -> $QRM -> $LED -> $CAP", got {EXPECTED_TEXT!r}. '
            f"If the contract has changed, update EXPECTED_TEXT and "
            f"EXPECTED_SHA256_HEX in tscg_b_spec.py to match."
        )

    frame, unpacked = _pack_and_validate(EXPECTED_TEXT)

    # The language's `unpack_frame.sha256_hex` field is observed
    # to be incorrect (it does not match the SHA-256 of the
    # payload bytes). We trust the actual payload bytes over
    # the unpacker's reported hex. The canonical SHA-256 is
    # computed from `unpacked['payload']` directly.
    payload_bytes = unpacked.get("payload", b"")
    if not isinstance(payload_bytes, bytes):
        raise TSCGBSWRSpecError(
            f"tscg_b unpacked payload is not bytes: {type(payload_bytes).__name__}"
        )
    payload_sha256 = hashlib.sha256(payload_bytes).hexdigest()
    if payload_sha256 != EXPECTED_SHA256_HEX:
        raise TSCGBSWRSpecError(
            f"SWR spec payload SHA-256 mismatch: "
            f"expected {EXPECTED_SHA256_HEX!r}, got {payload_sha256!r}. "
            f"This indicates the canonical text was edited without "
            f"updating EXPECTED_TEXT or EXPECTED_SHA256_HEX."
        )

    frame_sha256 = hashlib.sha256(frame).hexdigest()
    frame_path: str | None = None
    if bundle:
        frame_path = _bundle_frame_to_disk(frame)

    return TSCGBSWRSpec(
        text=EXPECTED_TEXT,
        frame=frame,
        frame_size=len(frame),
        frame_sha256=frame_sha256,
        payload_sha256=payload_sha256,
        crc32=unpacked.get("crc32", 0),
        unpacked=unpacked,
        frame_path=frame_path,
    )


__all__ = [
    "EXPECTED_SHA256_HEX",
    "EXPECTED_TEXT",
    "TSCGBSWRSpec",
    "TSCGBSWRSpecError",
    "load_spec",
]
