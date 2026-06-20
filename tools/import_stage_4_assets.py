#!/usr/bin/env python3
"""Import the explicitly approved Stage 4.7 and 4.8 source assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OMPT_TARGET = REPO / "apps" / "web-static" / "ompt-reference"
CHIMERA_TARGET = REPO / "packages" / "security" / "reference" / "chimera_v2_2.py"
GOVERNANCE_TARGET = REPO / "packages" / "rlp" / "governance_framework"
REPORT = REPO / "docs" / "internal" / "STAGE_4_7_4_8_IMPORT_REPORT.json"

DEFAULT_OMPT = Path(
    r"C:\Users\Quencher\Documents\Thirsty's Projects LLC\Project-AI Papers"
    r"\OMPT.md — the luxury-grade dark-mod.txt"
)
DEFAULT_CHIMERA = Path(
    r"C:\Users\Quencher\Desktop\Github\Personal Repo's\Zip Repo's"
    r"\chimera_bundle_proxy_fixed.zip"
)
DEFAULT_GOVERNANCE = Path(
    r"C:\Users\Quencher\Desktop\Github\Personal Repo's"
    r"\thirsty_governance_framework_0722"
)

OMPT_FILES = (
    "index.html",
    "architecture.html",
    "publications.html",
    "repository.html",
    "about.html",
    "styles.css",
    "app.js",
)

GOVERNANCE_FILES = (
    "README.md",
    "prompts/DEVELOPER_PROMPT.md",
    "prompts/SYSTEM_PROMPT.md",
    "policies/REFUSAL_BLOCKER_POLICY.md",
    "policies/VERIFICATION_POLICY.md",
    "templates/CONTINUITY_MAP_TEMPLATE.md",
    "templates/FINAL_REPORT_TEMPLATE.md",
    "checklists/GOVERNANCE_PROOF_CHECKLIST.md",
    "checklists/HOSTILE_SELF_REVIEW.md",
    "examples/COMPLIANT_RESPONSES.md",
    "examples/NON_COMPLIANT_RESPONSES.md",
    "tests/FAILURE_CASES.md",
    "tests/TEST_PROMPTS.md",
    "tests/test_governance_agent.py",
    "scripts/run_compliance_tests.py",
)


@dataclass(frozen=True)
class ImportedFile:
    destination: str
    sha256: str
    source: str
    source_sha256: str
    transformed: bool = False


def digest_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def digest(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def reset_generated_directory(path: Path, expected_parent: Path) -> None:
    resolved = path.resolve()
    if resolved.parent != expected_parent.resolve():
        raise PermissionError(f"Refusing to reset unexpected directory: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True)


def write_import(destination: Path, content: bytes, source: str, source_hash: str) -> ImportedFile:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return ImportedFile(
        destination=destination.relative_to(REPO).as_posix(),
        sha256=digest_bytes(content),
        source=source,
        source_sha256=source_hash,
        transformed=digest_bytes(content) != source_hash,
    )


def extract_ompt(source: Path) -> list[ImportedFile]:
    source_bytes = source.read_bytes()
    source_text = source_bytes.decode("utf-8-sig")
    marker = re.compile(
        r"^={20,}\r?\nFILE: ([^\r\n]+)\r?\n={20,}\r?\n",
        flags=re.MULTILINE,
    )
    matches = list(marker.finditer(source_text))
    declared = tuple(match.group(1).strip() for match in matches)
    if declared != OMPT_FILES:
        raise ValueError(f"OMPT file declaration changed: {declared!r}")
    reset_generated_directory(OMPT_TARGET, OMPT_TARGET.parent)
    records: list[ImportedFile] = []
    for index, match in enumerate(matches):
        name = declared[index]
        end = matches[index + 1].start() if index + 1 < len(matches) else len(source_text)
        content = source_text[match.end() : end].rstrip() + "\n"
        encoded = content.encode("utf-8")
        records.append(
            write_import(
                OMPT_TARGET / name,
                encoded,
                f"{source}#FILE:{name}",
                digest_bytes(encoded),
            )
        )
    return records


def normalize_chimera_license(content: str) -> str:
    old = (
        "# Copyright (c) 2026 Jeremy Karrick. All rights reserved.\n"
        "# Dual-licensed — see LICENSE for terms.\n"
    )
    new = "# Copyright (c) 2026 Jeremy Karrick. Licensed under MIT.\n"
    if old not in content:
        raise ValueError("Expected Chimera license header was not found")
    return content.replace(old, new, 1)


def extract_chimera(source: Path) -> list[ImportedFile]:
    member = "chimera_bundle/chimera.py"
    with zipfile.ZipFile(source) as archive:
        names = set(archive.namelist())
        if member not in names:
            raise ValueError(f"Missing required archive member: {member}")
        original = archive.read(member)
    normalized = normalize_chimera_license(original.decode("utf-8")).encode("utf-8")
    return [write_import(CHIMERA_TARGET, normalized, f"{source}!/{member}", digest_bytes(original))]


def import_governance(source: Path) -> list[ImportedFile]:
    reset_generated_directory(GOVERNANCE_TARGET, GOVERNANCE_TARGET.parent)
    records: list[ImportedFile] = []
    for relative_text in GOVERNANCE_FILES:
        relative = Path(relative_text)
        source_file = source / relative
        if not source_file.is_file():
            raise FileNotFoundError(f"Missing allowlisted governance file: {source_file}")
        content = source_file.read_bytes()
        records.append(
            write_import(
                GOVERNANCE_TARGET / relative,
                content,
                str(source_file),
                digest_bytes(content),
            )
        )
    return records


def serialize(records: list[ImportedFile]) -> list[dict[str, str | bool]]:
    return [record.__dict__ for record in records]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ompt", type=Path, default=DEFAULT_OMPT)
    parser.add_argument("--chimera", type=Path, default=DEFAULT_CHIMERA)
    parser.add_argument("--governance", type=Path, default=DEFAULT_GOVERNANCE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for source in (args.ompt, args.chimera, args.governance):
        if not source.exists():
            raise FileNotFoundError(source)
    ompt = extract_ompt(args.ompt)
    chimera = extract_chimera(args.chimera)
    governance = import_governance(args.governance)
    report = {
        "chimera": serialize(chimera),
        "governance": serialize(governance),
        "ompt": serialize(ompt),
        "policy": {
            "chimera_license": "Normalized to repository MIT license by current owner authority.",
            "excluded": "Environments, caches, secrets, reports, and non-allowlisted files are excluded.",
            "governance": "Explicit allowlist only; embedded governance_agent/venv is never traversed.",
            "ompt": "Only declared FILE blocks are extracted.",
        },
        "sources": {
            "chimera": {"path": str(args.chimera), "sha256": digest(args.chimera)},
            "governance": {"path": str(args.governance)},
            "ompt": {"path": str(args.ompt), "sha256": digest(args.ompt)},
        },
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(
        f"OMPT: {len(ompt)} files; Chimera: {len(chimera)} file; governance: {len(governance)} files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
