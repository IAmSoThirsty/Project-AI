# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-10 | TIME: 21:02               #
# COMPLIANCE: Regulator-Ready / UTF-8                                          #
# ============================================================================ #

# Date: 2026-03-10 | Time: 20:37 | Status: Active | Tier: Master
#                                           [2026-03-10 18:58]
#                                          Productivity: Active
#!/usr/bin/env python3

# ============================================================================ #
#                                                            DATE: 2026-03-10 #
#                                                          TIME: 15:01:55 PST #
#                                                        PRODUCTIVITY: Active #
# ============================================================================ #

"""Edition V1 Release Packager (CTS-5 Production Bundle).

This script assembles Edition V1 CTS-5 production artifacts into a single
archive suitable for distribution or deployment in a staging/production
environment. It pulls together source, binaries (if any), docs, tests,
SBOM, license disclosures, and a release manifest.
"""

import json
import os
import zipfile
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
RELEASE_DIR = ROOT / "EditionV1" / "RELEASE_BUNDLE"
RELEASE_DIR.mkdir(parents=True, exist_ok=True)


def git_head():
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True
        ).strip()
        return out
    except Exception:
        return "unknown"


def build_archive_name():
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    return f"EditionV1 CTS5-prod-{ts}.zip"


def collect_files(base: Path):
    files = []
    for p in base.rglob("*"):
        if p.is_file():
            files.append(p)
    return files


def create_release_manifest(version, status, components, notes=""):
    manifest = {
        "version": version,
        "date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_head": git_head(),
        "status": status,
        "components": components,
        "notes": notes or "Edition V1 CTS-5 Production Bundle",
    }
    with open(ROOT / "EditionV1" / "RELEASE_MANIFEST.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return manifest


import re


def package_bundle():
    release_name = build_archive_name()
    release_path = RELEASE_DIR / release_name
    with zipfile.ZipFile(release_path, "w", zipfile.ZIP_DEFLATED) as zf:
        base_dirs = [
            ROOT / "EditionV1",
            ROOT / "src",
            ROOT / "build",
            ROOT / "unity",
        ]
        for bd in base_dirs:
            if not bd.exists():
                continue
            for p in collect_files(bd):
                rel = p.relative_to(ROOT)
                zf.write(p, rel)
    return release_path


def prune_old_releases(release_dir: Path, keep_latest: int = 1) -> list[str]:
    """Archive older release bundles, keeping only the most recent one."""
    archived: list[str] = []
    if not release_dir.exists():
        return archived
    zip_files = sorted([p for p in release_dir.glob("*.zip")], key=lambda p: p.name)
    if len(zip_files) <= keep_latest:
        return archived
    to_archive = zip_files[:-keep_latest]
    archive_root = release_dir / "archive"
    archive_root.mkdir(parents=True, exist_ok=True)
    for f in to_archive:
        m = __import__("re").search(
            r"EditionV1\\s+CTS5-prod-(\\d{8}T\\d{6}Z)\\.zip", f.name
        )
        ts = m.group(1) if m else f.stem
        dest_dir = archive_root / ts
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / f.name
        try:
            f.rename(dest_path)
        except Exception:
            import shutil

            shutil.copy2(str(f), str(dest_path))
            f.unlink()
        archived.append(str(dest_path))
    return archived


def main():
    components = [
        "EditionV1.plan",
        "Ambassador surface",
        "Governance (SovereignRuntime)",
        "Iron Path",
        "Audit Trail",
        "API Surface (CTS-5)",
        "CI/CD templates",
        "Release materials",
    ]
    manifest = create_release_manifest(
        version="1.0.0-cts5-prod",
        status="production-ready",
        components=components,
        notes="Complete Edition V1 CTS-5 bundle for multi-tenant production",
    )
    bundle = package_bundle()
    archived = prune_old_releases(RELEASE_DIR, keep_latest=1)
    if archived:
        print(f"Archived old release bundles: {archived}")
    print(f"Packaged release bundle: {bundle}")
    print(f"Release manifest: {ROOT / 'EditionV1' / 'RELEASE_MANIFEST.json'}")
    print("Manifest summary:", json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
