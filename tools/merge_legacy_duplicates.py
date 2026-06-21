#!/usr/bin/env python3
"""Deterministically stage the selected SWR and Atlas legacy trees."""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from tools.legacy_source_guard import LegacySourceGuard, configured_guard

REPO = Path(__file__).resolve().parents[1]
STAGING_ROOT = REPO / "packages" / "_staging"
REPORT = REPO / "docs" / "internal" / "STAGE_4_MERGE_REPORT.json"
EXCLUDED_PARTS = {
    ".git",
    ".gradle",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}


@dataclass(frozen=True)
class MergeSpec:
    name: str
    canonical: str
    alternate: str


SPECS = (
    MergeSpec("swr", "engines/sovereign_war_room", "SOVEREIGN-WAR-ROOM"),
    MergeSpec("atlas", "engines/atlas", "atlas"),
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def inventory(root: Path) -> dict[str, Path]:
    """Return normalized relative paths for non-generated files."""
    files: dict[str, Path] = {}
    for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        files[relative.as_posix()] = path
    return files


def safe_reset(directory: Path) -> None:
    """Reset a generated staging target and reject every other directory."""
    resolved = directory.resolve()
    if resolved.parent != STAGING_ROOT.resolve():
        raise PermissionError(f"Refusing to reset non-staging directory: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def merge(spec: MergeSpec, guard: LegacySourceGuard) -> dict[str, Any]:
    canonical_root = guard.source(spec.canonical)
    alternate_root = guard.source(spec.alternate)
    output = guard.destination(STAGING_ROOT / spec.name)
    safe_reset(output)
    canonical = inventory(canonical_root)
    alternate = inventory(alternate_root)
    records: list[dict[str, str]] = []

    for relative, source in canonical.items():
        copy_file(source, output / relative)
        records.append(
            {
                "action": "canonical",
                "path": relative,
                "sha256": digest(source),
                "source": str(source),
            }
        )

    for relative, source in alternate.items():
        source_hash = digest(source)
        selected = canonical.get(relative)
        if selected is None:
            extra_path = output / "legacy_extras" / relative
            copy_file(source, extra_path)
            records.append(
                {
                    "action": "alternate-unique",
                    "path": relative,
                    "sha256": source_hash,
                    "source": str(source),
                }
            )
            continue
        selected_hash = digest(selected)
        records.append(
            {
                "action": "identical"
                if source_hash == selected_hash
                else "canonical-conflict-winner",
                "alternate_sha256": source_hash,
                "path": relative,
                "sha256": selected_hash,
                "source": str(selected),
            }
        )

    staged = inventory(output)
    return {
        "alternate": str(alternate_root),
        "alternate_files": len(alternate),
        "canonical": str(canonical_root),
        "canonical_files": len(canonical),
        "name": spec.name,
        "records": sorted(records, key=lambda record: (record["path"], record["action"])),
        "staged_files": len(staged),
        "staged_tree_sha256": tree_digest(output),
    }


def tree_digest(root: Path) -> str:
    """Hash relative names and bytes for a deterministic tree digest."""
    value = hashlib.sha256()
    for relative, path in sorted(inventory(root).items()):
        value.update(relative.encode("utf-8"))
        value.update(b"\0")
        value.update(bytes.fromhex(digest(path)))
    return value.hexdigest()


def main() -> int:
    guard = configured_guard()
    before = guard.snapshot()
    results = [merge(spec, guard) for spec in SPECS]
    after = guard.snapshot()
    if before != after:
        raise RuntimeError("Legacy repository changed during duplicate merge")
    report = {
        "legacy_head": before["head"],
        "legacy_unchanged": True,
        "merges": results,
        "policy": "canonical tree wins conflicts; alternate-only files are retained under legacy_extras",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    for result in results:
        print(
            f"{result['name']}: {result['canonical_files']} canonical, "
            f"{result['alternate_files']} alternate, {result['staged_files']} staged, "
            f"tree={result['staged_tree_sha256']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
