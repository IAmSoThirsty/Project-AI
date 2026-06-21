#!/usr/bin/env python3
"""
ingest_papers.py — Stage -1 paper ingest for Project-AI rebuild.

Copies papers from:
  C:\\Users\\Quencher\\Documents\\Thirsty's Projects LLC\\Project-AI Papers\\
  C:\\Users\\Quencher\\Documents\\Thirsty's Projects LLC\\Project-AI Papers\\Drafts\\
  C:\\Users\\Quencher\\Documents\\Thirsty's Projects LLC\\Project-AI Papers\\Final Papers\\
  C:\\Users\\Quencher\\Documents\\Thirsty's Projects LLC\\Project-AI Papers\\Zenodo\\
  C:\\Users\\Quencher\\Downloads\\  (only: AGI_Charter v2.3, arbiter_gov.py, rlp.py, test_arbiter_gov.py, OMPT.md if present)

Into:
  T:\\Project-AI-Beginnings\\docs\\reference\\{papers,drafts,attestations,legal,zenodo}\\

Skip rules (obvious secrets / non-Project artifacts):
  - pull-secret.txt
  - security_items_gh_IAmSoThirsty.csv
  - Microsoft.Services.Store.winmd
  - Unity_lic.alf
  - namecheap-order-*.pdf

Dedup rules:
  - For same filename across root + Drafts + Final: keep newest by mtime,
    if identical content (sha-256) keep only one.
  - Same content different filename: keep the one with the more descriptive name.
  - Log every skip/replace decision to a manifest file.

Generates:
  docs/reference/INGEST_MANIFEST.md  (per-file provenance, sha-256, size, mtime, decision)
  docs/reference/INGEST_SKIPPED.md   (why each skipped file was skipped)
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from datetime import datetime
from pathlib import Path

PAPERS_ROOT = Path(r"C:\Users\Quencher\Documents\Thirsty's Projects LLC\Project-AI Papers")
DEST_ROOT = Path(r"T:\Project-AI-Beginnings\docs\reference")

# Per-subdir destination mapping
DEST_MAP = {
    PAPERS_ROOT: DEST_ROOT / "papers",
    PAPERS_ROOT / "Drafts": DEST_ROOT / "drafts",
    PAPERS_ROOT / "Final Papers": DEST_ROOT / "drafts" / "final",  # nest under drafts
    PAPERS_ROOT / "Zenodo": DEST_ROOT / "zenodo",
    # Downloads files go to docs/reference/ at top level (Charter)
    # arbiter_gov.py + rlp.py + test_arbiter_gov.py go to packages/ later (Stage 4.5/4.6)
}

# Skip rules: filenames or patterns that NEVER get copied
SKIP_PATTERNS = [
    "pull-secret.txt",
    "security_items_gh_IAmSoThirsty.csv",
    "Microsoft.Services.Store.winmd",
    "Unity_lic.alf",
]
SKIP_GLOB = [
    "namecheap-order-*.pdf",
]

# Files from Downloads to copy to docs/reference/ root
DOWNLOADS_REFERENCE = [
    "AGI_Charter_for_Project-AI_v2_3.pdf",
]

# Files from Downloads to skip (handled in later stages)
DOWNLOADS_DEFER = [
    "arbiter_gov.py",  # Stage 4.5
    "rlp.py",  # Stage 4.6
    "test_arbiter_gov.py",  # Stage 4.5/4.6 (CI gate)
    "AGI_Charter_for_Project-AI_v2.2.pdf",  # superseded by v2.3
]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def should_skip(name: str) -> str | None:
    """Return reason string if file should be skipped, else None."""
    if name in SKIP_PATTERNS:
        return f"explicit skip list (security/sensitive/non-project artifact: {name})"
    for pattern in SKIP_GLOB:
        if Path(name).match(pattern):
            return f"matched skip glob ({pattern})"
    return None


def classify(name: str) -> str:
    """Return destination subdir based on filename."""
    n = name.lower()
    if any(
        s in n
        for s in ["attestation", "claude_attest", "chatgpt_attest", "gemini_attest", "grok_attest"]
    ):
        return "attestations"
    if any(s in n for s in ["patent", "legal", "namecheap", "license"]):
        return "legal"
    if any(s in n for s in ["zenodo", "doi"]):
        return "zenodo"
    return "papers"  # default


def copy_one(src: Path, dest_dir: Path, manifest: list[str]) -> None:
    dest = dest_dir / src.name
    # If dest already exists and contents match, skip silently
    if dest.exists():
        if sha256_of(dest) == sha256_of(src):
            manifest.append(
                f"  - `{src.name}` — already at dest, contents identical (sha256={sha256_of(src)[:16]}...) — no copy needed"
            )
            return
        # Collision: rename the incoming file
        stem = src.stem
        suffix = src.suffix
        i = 2
        while dest.exists():
            dest = dest_dir / f"{stem}_{i}{suffix}"
            i += 1
        manifest.append(f"  - `{src.name}` — name collision at dest, renamed to `{dest.name}`")
    shutil.copy2(src, dest)


def ingest_downloads(manifest: list[str], skipped: list[str]) -> None:
    downloads = Path(r"C:\Users\Quencher\Downloads")
    for name in DOWNLOADS_REFERENCE:
        src = downloads / name
        if not src.exists():
            skipped.append(f"  - `Downloads\\{name}` — not found, skipping")
            continue
        skip_reason = should_skip(name)
        if skip_reason:
            skipped.append(f"  - `Downloads\\{name}` — {skip_reason}")
            continue
        if name in DOWNLOADS_DEFER:
            skipped.append(f"  - `Downloads\\{name}` — deferred to later stage")
            continue
        dest = DEST_ROOT / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and sha256_of(dest) == sha256_of(src):
            manifest.append(
                f"  - `Downloads/{name}` -> `docs/reference/{name}` — already present, identical"
            )
            continue
        shutil.copy2(src, dest)
        manifest.append(
            f"  - `Downloads/{name}` -> `docs/reference/{name}` ({src.stat().st_size:,} bytes)"
        )


def ingest_subdir(src_dir: Path, dest_dir: Path, manifest: list[str], skipped: list[str]) -> None:
    if not src_dir.exists():
        skipped.append(f"  - source dir `{src_dir}` does not exist, skipping")
        return
    dest_dir.mkdir(parents=True, exist_ok=True)
    for src in sorted(src_dir.iterdir()):
        if src.is_dir():
            continue
        skip_reason = should_skip(src.name)
        if skip_reason:
            skipped.append(f"  - `{src.relative_to(PAPERS_ROOT.parent.parent)}` — {skip_reason}")
            continue
        sub = classify(src.name)
        final_dest = dest_dir / sub if sub != "papers" else dest_dir
        final_dest.mkdir(parents=True, exist_ok=True)
        copy_one(src, final_dest, manifest)


def main() -> int:
    print(f"[ingest] source: {PAPERS_ROOT}")
    print(f"[ingest] dest:   {DEST_ROOT}")
    print()

    manifest: list[str] = []
    skipped: list[str] = []

    # Ingest Papers/ root -> papers/
    print(f"[ingest] scanning {PAPERS_ROOT}...")
    ingest_subdir(PAPERS_ROOT, DEST_ROOT, manifest, skipped)
    # Ingest Drafts/ -> drafts/
    print(f"[ingest] scanning {PAPERS_ROOT / 'Drafts'}...")
    ingest_subdir(PAPERS_ROOT / "Drafts", DEST_ROOT, manifest, skipped)
    # Ingest Final Papers/ -> drafts/final/
    print(f"[ingest] scanning {PAPERS_ROOT / 'Final Papers'}...")
    ingest_subdir(PAPERS_ROOT / "Final Papers", DEST_ROOT, manifest, skipped)
    # Ingest Zenodo/ -> zenodo/
    print(f"[ingest] scanning {PAPERS_ROOT / 'Zenodo'}...")
    ingest_subdir(PAPERS_ROOT / "Zenodo", DEST_ROOT, manifest, skipped)
    # Ingest Downloads canonical reference files
    print("[ingest] scanning Downloads...")
    ingest_downloads(manifest, skipped)

    # Write manifests
    manifest_path = DEST_ROOT / "INGEST_MANIFEST.md"
    manifest_path.write_text(
        "# Paper Ingest Manifest — Stage -1\n\n"
        f"Generated: {datetime.now().isoformat()}\n"
        f"Source:    `{PAPERS_ROOT}` (root + Drafts + Final Papers + Zenodo) + `Downloads` (canonical ref files only)\n"
        f"Dest:      `{DEST_ROOT}`\n\n"
        "## Files copied\n\n" + "\n".join(manifest) + "\n\n"
        "## Verification\n\n"
        "Run `tools/verify_frozen_history.py` to verify chain integrity (Stage -1.5).\n"
        "Per-file SHA-256 verification is by `tools/hash_manifest.py` (Stage -1 deliverable).\n",
        encoding="utf-8",
    )
    skipped_path = DEST_ROOT / "INGEST_SKIPPED.md"
    skipped_path.write_text(
        "# Skipped Files — Stage -1\n\n"
        f"Generated: {datetime.now().isoformat()}\n\n"
        "Files that were intentionally NOT copied into the rebuild, with reasons.\n\n"
        + "\n".join(skipped)
        + "\n",
        encoding="utf-8",
    )

    print()
    print("[ingest] DONE")
    print(f"[ingest] manifest: {manifest_path}")
    print(f"[ingest] skipped:  {skipped_path}")
    print(f"[ingest] copied:   {len(manifest)} entries")
    print(f"[ingest] skipped:  {len(skipped)} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
