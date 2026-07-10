"""Seal the verification bundle: hash every file, write SEAL.json.

Run AFTER build_taar_bundle.py and after README/verifier are final.
SEAL.json is intentionally the one file not covered by itself.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

BUNDLE = Path(
    r"T:\00-Active\Project-AI-Beginnings\docs\internal\verification\taar-e2e-2026-07-10"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Ensure every text file (esp. bundle.json, written via write_text on Windows)
# is LF on disk BEFORE hashing, so committed==sealed==checkout everywhere.
_EXTS = {".py", ".md", ".json", ".yaml", ".yml", ".jsonl", ".toml", ".txt"}
for _p in BUNDLE.rglob("*"):
    if _p.is_file() and _p.suffix in _EXTS:
        _b = _p.read_bytes()
        if b"\r\n" in _b:
            _p.write_bytes(_b.replace(b"\r\n", b"\n"))

files: dict[str, str] = {}
for path in sorted(BUNDLE.rglob("*")):
    if path.is_file() and path.name != "SEAL.json":
        files[path.relative_to(BUNDLE).as_posix()] = sha256_file(path)

head = hashlib.sha256(
    "\n".join(f"{name}:{digest}" for name, digest in sorted(files.items())).encode("utf-8")
).hexdigest()

seal = {
    "schema": "taar-e2e-verification-bundle-seal/1",
    "sealed_utc": datetime.now(UTC).isoformat(),
    "file_count": len(files),
    "head_sha256": head,
    "head_algorithm": "sha256 of newline-joined 'relpath:sha256' lines, sorted by relpath, "
    "over every bundle file except SEAL.json",
    "files": files,
}
(BUNDLE / "SEAL.json").write_bytes(
    (json.dumps(seal, indent=2, sort_keys=True) + "\n").encode("utf-8")
)
print(f"sealed {len(files)} files")
print(f"head_sha256: {head}")
