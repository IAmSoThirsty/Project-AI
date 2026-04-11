#!/usr/bin/env python3
"""Detect whether a blob is TSCG-B, gzip/tar, or unknown.

Usage:
    python scripts/detect_blob_format.py <path>
    python scripts/detect_blob_format.py <path> --json
"""

from __future__ import annotations

import argparse
import json
import tarfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

TSGB_MAGIC = b"TSGB"
GZIP_MAGIC = b"\x1f\x8b"
USTAR_OFFSET = 257
USTAR_MAGIC = b"ustar"


@dataclass(slots=True)
class DetectionResult:
    path: str
    size_bytes: int
    outer_magic_hex: str
    classification: str
    confidence: str
    notes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


def _hex_bytes(data: bytes) -> str:
    return " ".join(f"{byte:02X}" for byte in data)


def _parse_properties(text: str) -> dict[str, str]:
    """Parse Java-style .properties content into a dictionary."""
    props: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        props[key.strip()] = value.strip()
    return props


def _detect_tsgb(path: Path, size_bytes: int, outer_magic_hex: str) -> DetectionResult:
    header = path.read_bytes()[:10]
    proto_ver = header[4] if len(header) > 4 else None
    sd_ver = header[5] if len(header) > 5 else None
    const_ver = header[6] if len(header) > 6 else None
    flags = header[7] if len(header) > 7 else None
    payload_len = int.from_bytes(header[8:10], "big") if len(header) >= 10 else None

    metadata: dict[str, Any] = {
        "tsgb_proto_ver": proto_ver,
        "tsgb_sd_ver": sd_ver,
        "tsgb_const_ver": const_ver,
        "tsgb_flags": flags,
        "tsgb_payload_len": payload_len,
    }

    notes = ["Matched TSGB wire magic (0x54 53 47 42)."]
    confidence = "high"

    if payload_len is not None:
        expected_min_size = 10 + payload_len + 4 + 32  # header + payload + crc32 + sha256
        metadata["expected_min_frame_size"] = expected_min_size
        if size_bytes < expected_min_size:
            notes.append(
                "Frame appears truncated compared to declared payload length and integrity trailer."
            )
            confidence = "medium"

    return DetectionResult(
        path=str(path),
        size_bytes=size_bytes,
        outer_magic_hex=outer_magic_hex,
        classification="tsgb",
        confidence=confidence,
        notes=notes,
        metadata=metadata,
    )


def _detect_gzip_or_tar(path: Path, size_bytes: int, outer_magic_hex: str) -> DetectionResult:
    notes = ["Matched gzip magic (1F 8B)."]
    metadata: dict[str, Any] = {}

    try:
        with tarfile.open(path, mode="r:gz") as archive:
            names = archive.getnames()
            metadata["tar_entries_count"] = len(names)
            metadata["tar_entries_preview"] = names[:10]
            notes.append("Valid tar structure found inside gzip container.")

            if "METADATA" in names:
                metadata_member = archive.extractfile("METADATA")
                if metadata_member is not None:
                    metadata_text = metadata_member.read().decode("utf-8", errors="replace")
                    properties = _parse_properties(metadata_text)
                    if properties:
                        metadata["metadata_properties"] = {
                            "type": properties.get("type"),
                            "gradleVersion": properties.get("gradleVersion"),
                            "buildInvocationId": properties.get("buildInvocationId"),
                        }
                        if properties.get("type"):
                            notes.append(
                                "Archive contains Gradle cache metadata (task output artifact)."
                            )

            return DetectionResult(
                path=str(path),
                size_bytes=size_bytes,
                outer_magic_hex=outer_magic_hex,
                classification="gzip-tar",
                confidence="high",
                notes=notes,
                metadata=metadata,
            )
    except tarfile.ReadError:
        notes.append("Gzip payload is not a tar archive.")

    return DetectionResult(
        path=str(path),
        size_bytes=size_bytes,
        outer_magic_hex=outer_magic_hex,
        classification="unknown",
        confidence="low",
        notes=notes,
        metadata=metadata,
    )


def detect_blob(path: Path) -> DetectionResult:
    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    size_bytes = path.stat().st_size
    with path.open("rb") as handle:
        first_512 = handle.read(512)

    outer_magic_hex = _hex_bytes(first_512[:8])

    if first_512.startswith(TSGB_MAGIC):
        return _detect_tsgb(path, size_bytes, outer_magic_hex)

    if first_512.startswith(GZIP_MAGIC):
        return _detect_gzip_or_tar(path, size_bytes, outer_magic_hex)

    if len(first_512) >= USTAR_OFFSET + len(USTAR_MAGIC):
        if first_512[USTAR_OFFSET : USTAR_OFFSET + len(USTAR_MAGIC)] == USTAR_MAGIC:
            return DetectionResult(
                path=str(path),
                size_bytes=size_bytes,
                outer_magic_hex=outer_magic_hex,
                classification="gzip-tar",
                confidence="medium",
                notes=["Detected raw tar archive (ustar marker at offset 257)."],
                metadata={},
            )

    return DetectionResult(
        path=str(path),
        size_bytes=size_bytes,
        outer_magic_hex=outer_magic_hex,
        classification="unknown",
        confidence="low",
        notes=["No TSGB, gzip, or tar signature matched."],
        metadata={},
    )


def _render_human(result: DetectionResult) -> str:
    lines = [
        f"Path: {result.path}",
        f"Size: {result.size_bytes} bytes",
        f"Outer Magic: {result.outer_magic_hex}",
        f"Classification: {result.classification}",
        f"Confidence: {result.confidence}",
    ]

    if result.notes:
        lines.append("Notes:")
        lines.extend(f"  - {note}" for note in result.notes)

    if result.metadata:
        lines.append("Metadata:")
        for key, value in result.metadata.items():
            lines.append(f"  - {key}: {value}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect blob format: tsgb, gzip-tar, or unknown.")
    parser.add_argument("path", type=Path, help="Path to the blob/file to inspect")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output",
    )
    args = parser.parse_args()

    result = detect_blob(args.path)

    if args.json:
        print(json.dumps(asdict(result), indent=2))
    else:
        print(_render_human(result))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
