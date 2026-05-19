#!/usr/bin/env python3
"""Archive the files listed by the repository audit workflow.

This maintenance helper consumes the audit result lists produced by
`audit_repo.py` and moves the referenced files into the archive tree.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

RESULT_DIR = Path(os.getenv("TMPDIR") or os.getenv("TEMP") or os.getenv("TMP") or ".")
SOURCE_RESULTS = RESULT_DIR / "audit_results_non_active.txt"
STUB_RESULTS = RESULT_DIR / "audit_results_stubs.txt"
ARCHIVE_DIR = Path("archive/history/timeline/outdated_audit")


def archive() -> None:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    to_archive: set[str] = set()
    for results_file in (SOURCE_RESULTS, STUB_RESULTS):
        if not results_file.exists():
            continue
        for line in results_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                to_archive.add(line)

    for path_text in sorted(to_archive):
        path = Path(path_text)
        if not path.exists():
            continue

        rel_path = Path(str(path).replace("\\", "/"))
        dest_path = ARCHIVE_DIR / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.move(str(path), str(dest_path))
            print(f"Archived: {path} -> {dest_path}")
        except Exception as exc:  # pragma: no cover - maintenance utility
            print(f"Error archiving {path}: {exc}")


if __name__ == "__main__":
    archive()
