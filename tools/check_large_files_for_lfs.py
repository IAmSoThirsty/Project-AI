"""Pre-commit helper to warn about large files not tracked by Git LFS.

Usage:
    python tools/check_large_files_for_lfs.py

Recommended: add to a pre-commit hook by creating .githooks/pre-commit and setting:
    git config core.hooksPath .githooks

The script scans the repository for files > 2MB that are not matched by
known LFS patterns (*.pt, *.pth, *.onnx, *.bin, *.ckpt, *.npy) and not already
Git LFS pointer files. It prints warnings so you can decide whether to add
new patterns or move artifacts elsewhere.

This does NOT auto-track files (avoids accidental pointer churn), it is a guardrail.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Size threshold in bytes (2 MB)
THRESHOLD = 2 * 1024 * 1024
LFS_PATTERNS = {".pt", ".pth", ".onnx", ".bin", ".ckpt", ".npy"}
POINTER_HEADER = b"version https://git-lfs.github.com/spec/v1"  # first line marker


def is_lfs_pointer(file_path: Path) -> bool:
    try:
        with file_path.open("rb") as fh:
            first_line = fh.readline(200)
            return POINTER_HEADER in first_line
    except OSError:
        return False


def _should_skip_dir(dirpath: str) -> bool:
    """Return True if directory should be skipped during scan."""
    return any(
        skip in dirpath for skip in (".git", "__pycache__", "node_modules", "htmlcov")
    )


def _should_warn(path: Path) -> bool:
    """Decide if a path should trigger a large-file warning."""
    suffix = path.suffix.lower()
    if suffix in LFS_PATTERNS:
        return False
    try:
        size = path.stat().st_size
    except OSError:
        return False
    return size >= THRESHOLD and not is_lfs_pointer(path)


def scan_large_untracked(root: Path) -> list[Path]:
    warnings: list[Path] = []
    for dirpath, _, filenames in os.walk(root):
        if _should_skip_dir(dirpath):
            continue
        for name in filenames:
            path = Path(dirpath) / name
            if _should_warn(path):
                warnings.append(path)
    return warnings


def main(argv: list[str]) -> int:
    repo_root = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    large_files = scan_large_untracked(repo_root)
    if not large_files:
        print("[LFS CHECK] OK: No large untracked files above threshold.")
        return 0
    print(
        "[LFS CHECK] WARNING: The following files exceed 2MB and are not covered by LFS patterns:"
    )
    for f in large_files:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  - {f} ({size_mb:.2f} MB)")
    print(
        "Consider adding a pattern to .gitattributes or relocating large generated artifacts."
    )
    return 0  # non-fatal, informational


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv))
