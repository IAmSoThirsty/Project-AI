#!/usr/bin/env python3
"""Deterministic generator and verifier for this package's ``SHA256SUMS``.

``SHA256SUMS`` is the package's "release file checksums" record (README section
"Verification bundle"; ``docs/verification/VERIFICATION_REPORT.md``). Before
2026-07-20 it had no generator, no verifier, and no test, so it drifted from the
package: eight distributed files were never added to it and three recorded hashes
went stale after the files they cover were regenerated. Nothing detected either
problem because nothing checked.

Scope (decided 2026-07-20): **every distributed file in the package** except
``SHA256SUMS`` itself and gitignore-excluded private-key material. "Distributed"
means present on disk and not build/cache output -- the same set ``git`` tracks
plus the intentionally-untracked unsigned successor draft, minus secrets that must
never enter a checksum record.

Determinism is load-bearing. The repository ``.gitattributes`` pins every text
file to ``eol=lf``, so hashing on-disk bytes is stable across platforms. Entries
are sorted by POSIX path and the file is written with LF line endings, so
regeneration on any machine produces byte-identical output. The verifier treats a
CRLF ``SHA256SUMS`` as a problem rather than silently rehashing around it.

Usage:
    python tools/checksums.py            # verify (default); non-zero exit on drift
    python tools/checksums.py --check    # same as default
    python tools/checksums.py --write    # regenerate SHA256SUMS in place
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CHECKSUM_FILENAME = "SHA256SUMS"

# Directories that are build/cache output, never distributed. ``*.egg-info`` is
# matched by suffix below rather than listed here.
EXCLUDED_DIR_NAMES = frozenset(
    {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
)

# Private authority material. Mirrors the package .gitignore secret patterns so a
# private key can never be enrolled into the checksum record even if one is present
# on disk. ``*private*.json`` already covers owner-private.json / evaluator-private.json.
PRIVATE_KEY_GLOBS = ("*private*.json", "*private-key*.json", "trusted-keys.local.json")


class ChecksumError(ValueError):
    """Raised when the checksum record cannot be produced or does not verify."""


def _is_private(relative_posix: str) -> bool:
    name = relative_posix.rsplit("/", 1)[-1]
    return any(fnmatch.fnmatch(name, glob) for glob in PRIVATE_KEY_GLOBS)


def _is_excluded_dir(name: str) -> bool:
    return name in EXCLUDED_DIR_NAMES or name.endswith(".egg-info")


def iter_distributed_files(package_root: Path = PACKAGE_ROOT) -> list[str]:
    """Return the sorted POSIX paths of every distributed file in the package.

    Excludes ``SHA256SUMS`` itself, build/cache directories, and private-key
    material. The result is deterministic: sorted, forward-slash separated, and
    independent of filesystem walk order.
    """
    files: list[str] = []
    for path in package_root.rglob("*"):
        if path.is_dir():
            continue
        if any(_is_excluded_dir(part) for part in path.relative_to(package_root).parts[:-1]):
            continue
        relative = path.relative_to(package_root).as_posix()
        if relative == CHECKSUM_FILENAME:
            continue
        if _is_private(relative):
            continue
        files.append(relative)
    return sorted(files)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def generate(package_root: Path = PACKAGE_ROOT) -> str:
    """Return the canonical ``SHA256SUMS`` text for the package.

    Format matches ``sha256sum`` text mode with a ``./`` path prefix:
    ``<hex>  ./<posix-path>\\n``, LF-terminated, one line per file, sorted by path.
    """
    lines = [
        f"{sha256_file(package_root / relative)}  ./{relative}"
        for relative in iter_distributed_files(package_root)
    ]
    return "\n".join(lines) + "\n"


def parse(text: str) -> list[tuple[str, str]]:
    """Parse ``SHA256SUMS`` text into ``(hex_digest, posix_path)`` pairs.

    Raises on structurally malformed input so a corrupt record fails closed rather
    than silently verifying nothing.
    """
    entries: list[tuple[str, str]] = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        if not raw.strip():
            continue
        digest, separator, remainder = raw.partition("  ")
        if not separator or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ChecksumError(f"line {lineno}: not a valid '<sha256>  <path>' entry: {raw!r}")
        path = remainder[2:] if remainder.startswith("./") else remainder
        entries.append((digest, path))
    return entries


def verify(package_root: Path = PACKAGE_ROOT) -> list[str]:
    """Return a list of problems with the on-disk ``SHA256SUMS``; empty means clean.

    Detects, fail-closed: CRLF (nondeterministic line endings), duplicate paths,
    path traversal / absolute paths, a recorded private-key path, a self-reference,
    stale hashes, files recorded but missing, and distributed files not recorded.
    """
    checksum_path = package_root / CHECKSUM_FILENAME
    problems: list[str] = []
    try:
        raw_bytes = checksum_path.read_bytes()
    except OSError as error:
        return [f"cannot read {CHECKSUM_FILENAME}: {error}"]

    if b"\r\n" in raw_bytes:
        problems.append(
            f"{CHECKSUM_FILENAME} uses CRLF line endings; the record must be LF-only "
            "so hashes are reproducible across platforms"
        )

    try:
        entries = parse(raw_bytes.decode("utf-8"))
    except ChecksumError as error:
        return [*problems, str(error)]

    recorded: dict[str, str] = {}
    for digest, path in entries:
        if path in recorded:
            problems.append(f"duplicate path recorded: {path}")
            continue
        recorded[path] = digest
        if path == CHECKSUM_FILENAME:
            problems.append(f"{CHECKSUM_FILENAME} must not record itself")
            continue
        if path.startswith("/") or ".." in Path(path).parts:
            problems.append(f"path escapes the package or is absolute: {path}")
            continue
        if _is_private(path):
            problems.append(f"private-key material must never be recorded: {path}")
            continue
        target = package_root / path
        if not target.is_file():
            problems.append(f"recorded file is missing on disk: {path}")
            continue
        actual = sha256_file(target)
        if actual != digest:
            problems.append(f"stale hash for {path}: recorded {digest}, actual {actual}")

    for relative in iter_distributed_files(package_root):
        if relative not in recorded:
            problems.append(f"distributed file not recorded in {CHECKSUM_FILENAME}: {relative}")

    return problems


def write(package_root: Path = PACKAGE_ROOT) -> Path:
    checksum_path = package_root / CHECKSUM_FILENAME
    checksum_path.write_bytes(generate(package_root).encode("utf-8"))
    return checksum_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--check",
        action="store_true",
        help="verify SHA256SUMS against the package (default); non-zero exit on drift",
    )
    group.add_argument("--write", action="store_true", help="regenerate SHA256SUMS in place")
    args = parser.parse_args(argv)

    if args.write:
        path = write()
        print(f"wrote {path} ({len(iter_distributed_files())} files)")
        return 0

    problems = verify()
    if problems:
        print(f"FAIL: {CHECKSUM_FILENAME} does not match the package:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print(f"OK: {CHECKSUM_FILENAME} covers {len(iter_distributed_files())} files with no drift")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
