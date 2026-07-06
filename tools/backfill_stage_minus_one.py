#!/usr/bin/env python3
"""Generate the missing Stage -1 evidence from read-only source material."""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OLD_REPO = Path(os.environ.get("PROJECT_AI_LEGACY_REPO", r"T:\00-Active\Project-AI-main"))
PAPERS = Path(
    os.environ.get(
        "PROJECT_AI_PAPERS_ROOT",
        r"C:\Users\Quencher\Documents\Thirsty's Projects LLC\Project-AI Papers",
    )
)
WIKI = OLD_REPO / "wiki"
PUBLICATIONS = WIKI / "07_Research" / "Publications"
INDEX = WIKI / "00_Index"
REFERENCE = REPO / "docs" / "reference"

DOI_RE = re.compile(r"(?:https://doi\.org/)?10\.5281/zenodo\.(\d+)", re.IGNORECASE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def source_header(title: str, source: Path) -> str:
    return (
        f"# {title}\n\n"
        f"> Source: `{source}`  \n"
        f"> SHA-256: `{sha256(source)}`  \n"
        "> Imported as Stage -1 evidence; the source remains unchanged.\n\n"
    )


def copy_markdown_evidence(source: Path, destination: Path, title: str) -> None:
    body = read_text(source)
    if body.startswith("---"):
        end = body.find("\n---", 3)
        if end >= 0:
            body = body[end + 4 :].lstrip()
    write_text(destination, source_header(title, source) + body)


def wiki_inventory() -> list[tuple[str, int, str, int]]:
    rows: list[tuple[str, int, str, int]] = []
    for path in sorted(p for p in WIKI.rglob("*") if p.is_file()):
        text = read_text(path) if path.suffix.lower() in {".md", ".txt", ".canvas", ".json"} else ""
        lines = len(text.splitlines())
        links = len(re.findall(r"\[\[[^]]+\]\]", text))
        kind = "substantial" if path.suffix.lower() == ".canvas" or lines >= 50 else "pointer"
        rows.append((path.relative_to(WIKI).as_posix(), lines, kind, links))
    return rows


def generate_wiki_evidence() -> None:
    rows = wiki_inventory()
    table = [
        "# Legacy Wiki Pointer Map",
        "",
        f"> Source: `{WIKI}` (read-only)",
        f"> Files indexed: {len(rows)}",
        "",
        "| Legacy path | Lines | Classification | Wiki links |",
        "|---|---:|---|---:|",
    ]
    table.extend(f"| `{path}` | {lines} | {kind} | {links} |" for path, lines, kind, links in rows)
    write_text(REPO / "docs" / "index" / "wiki-pointer-map.md", "\n".join(table))

    stubs = [row for row in rows if row[2] == "pointer"]
    stub_text = [
        "# Legacy Vault Stub Index",
        "",
        "Pointer files are retained as routing evidence, not copied as canonical content.",
        "",
        f"Pointer files: {len(stubs)} of {len(rows)} total wiki files.",
        "",
    ]
    stub_text.extend(
        f"- `{path}` ({lines} lines, {links} links)" for path, lines, _, links in stubs
    )
    write_text(REPO / "docs" / "internal" / "vault-stub-index.md", "\n".join(stub_text))


def extract_dois(text: str) -> set[str]:
    return {match.group(1) for match in DOI_RE.finditer(text)}


def generate_publication_evidence() -> None:
    timeline = INDEX / "Sovereign-Journey.md"
    registry = PUBLICATIONS / "DOI-Registry.md"
    copy_markdown_evidence(timeline, REFERENCE / "PUBLICATION_TIMELINE.md", "Publication Timeline")
    copy_markdown_evidence(registry, REFERENCE / "DOI_REGISTRY.md", "DOI Registry")

    wiki_dois = extract_dois(read_text(registry))
    corpus_dois: set[str] = set()
    for candidate in sorted((REFERENCE / "zenodo").rglob("*")):
        if candidate.is_file() and candidate.suffix.lower() in {".md", ".txt", ".csv", ".json"}:
            corpus_dois |= extract_dois(read_text(candidate))
    only_wiki = sorted(wiki_dois - corpus_dois)
    only_corpus = sorted(corpus_dois - wiki_dois)
    report = [
        "# Wiki Versus Paper Corpus DOI Audit",
        "",
        f"- Wiki DOI count: {len(wiki_dois)}",
        f"- Text-readable corpus DOI count: {len(corpus_dois)}",
        f"- Present only in wiki registry: {len(only_wiki)}",
        f"- Present only in corpus metadata: {len(only_corpus)}",
        "",
        "## Wiki-only identifiers",
        "",
    ]
    report.extend(f"- `10.5281/zenodo.{doi}`" for doi in only_wiki)
    report.extend(["", "## Corpus-only identifiers", ""])
    report.extend(f"- `10.5281/zenodo.{doi}`" for doi in only_corpus)
    if not only_wiki and not only_corpus:
        report.extend(["", "The two text-readable DOI sets agree."])
    write_text(REPO / "docs" / "audit" / "wiki-vs-papers-discrepancies.md", "\n".join(report))


def pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - environment diagnostic
        raise RuntimeError("pypdf is required to generate GENESIS.md") from exc
    return "\n\n".join(
        (page.extract_text() or "").strip() for page in PdfReader(path).pages
    ).strip()


def generate_genesis() -> None:
    main = PAPERS / "ill show you complete.txt"
    debt = PAPERS / "Zenodo" / "Submitted" / "Admissibility_Debt.pdf"
    tokens = PAPERS / "Zenodo" / "Submitted" / "Bye Bye Tokens.txt"
    sources = [main, debt, tokens]
    parts = [
        "# Genesis: Microservices Generation",
        "",
        "> Canonical development composite for DOI `10.5281/zenodo.19488571`.",
        "> The three source artifacts remain unchanged and are joined here in owner-defined order.",
        "",
        "## Source manifest",
        "",
    ]
    parts.extend(f"- `{path}` — SHA-256 `{sha256(path)}`" for path in sources)
    parts.extend(["", "## Part 1: Genesis", "", read_text(main)])
    parts.extend(["", "## Part 2: Admissibility Debt", "", pdf_text(debt)])
    parts.extend(["", "## Part 3: Bye Bye Tokens", "", read_text(tokens)])
    write_text(REFERENCE / "GENESIS.md", "\n".join(parts))


def generate_orphan_status() -> None:
    submitted = PAPERS / "Zenodo" / "Submitted"
    entries = [
        ("Admissibility_Debt.pdf", "Genesis continuation; incorporated into GENESIS.md"),
        ("Bye Bye Tokens.txt", "Genesis continuation; incorporated into GENESIS.md"),
        (
            "Project_AI_The_I_AM_Moment_and_the_Birth_of_Governed_Intelligence_Formal_Whitepaper (1).txt",
            "Separate paper; awaiting DOI",
        ),
        ("Thirsty\u2019s Standard v3.pdf", "Separate paper; awaiting DOI"),
    ]
    lines = ["# Submitted Paper Status", "", "No listed artifact is silently discarded.", ""]
    for name, status in entries:
        path = submitted / name
        lines.append(f"- `{name}` — {status}; SHA-256 `{sha256(path)}`")
    write_text(REFERENCE / "ORPHAN_PAPERS.md", "\n".join(lines))


def candidate_sources() -> dict[str, list[Path]]:
    by_name: dict[str, list[Path]] = defaultdict(list)
    for root in (PAPERS, OLD_REPO):
        for path in root.rglob("*"):
            if path.is_file() and ".git" not in path.parts:
                by_name[path.name].append(path)
    return by_name


def generate_provenance() -> None:
    candidates = candidate_sources()
    lines = [
        "# Merge Provenance",
        "",
        "Generated from byte hashes. `unresolved` means no same-name, same-byte source was found; it does not imply authorship.",
        "",
        "| Rebuild artifact | SHA-256 | Exact source |",
        "|---|---|---|",
    ]
    for artifact in sorted(
        path
        for path in REFERENCE.rglob("*")
        if path.is_file() and path.name != "MERGE_PROVENANCE.md"
    ):
        artifact_hash = sha256(artifact)
        matches = []
        for source in candidates.get(artifact.name, []):
            try:
                if (
                    source.stat().st_size == artifact.stat().st_size
                    and sha256(source) == artifact_hash
                ):
                    matches.append(str(source))
            except OSError:
                continue
        source_text = (
            "<br>".join(f"`{path}`" for path in matches) if matches else "unresolved/generated"
        )
        lines.append(
            f"| `{artifact.relative_to(REPO).as_posix()}` | `{artifact_hash}` | {source_text} |"
        )
    write_text(REFERENCE / "MERGE_PROVENANCE.md", "\n".join(lines))


def legacy_files() -> list[str]:
    output = subprocess.check_output(
        ["git", "-C", str(OLD_REPO), "ls-files", "-z"], stderr=subprocess.STDOUT
    )
    return sorted(path for path in output.decode("utf-8", errors="replace").split("\0") if path)


def disposition(path: str) -> str:
    lowered = path.lower()
    if lowered.startswith(("wiki/", "project-ai/", ".obsidian/")):
        return "indexed as legacy navigation; not copied verbatim"
    if any(
        part in lowered
        for part in ("__pycache__", "node_modules/", ".venv/", "data/runtime/", "data/logs/")
    ):
        return "excluded generated/runtime state"
    if lowered.startswith(
        (
            "src/",
            "governance/",
            "canonical/",
            "engines/",
            "atlas/",
            "sovereign-war-room/",
            "desktop/",
            "android/",
            "unity/",
        )
    ):
        return "scheduled for owning migration gate; retained in frozen history"
    if lowered.startswith("docs/"):
        return "reference candidate; retained in frozen history pending provenance selection"
    return "not selected for development baseline; retained in frozen history"


def generate_disposition_manifest() -> None:
    files = legacy_files()
    lines = [
        "# Legacy File Disposition Manifest",
        "",
        f"> Source: `{OLD_REPO}`",
        f"> Tracked paths classified: {len(files)}",
        "> This records disposition without deleting or modifying the source repository.",
        "",
        "| Legacy tracked path | Disposition |",
        "|---|---|",
    ]
    lines.extend(f"| `{path}` | {disposition(path)} |" for path in files)
    write_text(REFERENCE / "DROPPED_FILES_MANIFEST.md", "\n".join(lines))


def main() -> int:
    required = [OLD_REPO / ".git", WIKI, PAPERS, REFERENCE]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required Stage -1 sources: " + ", ".join(missing))
    generate_wiki_evidence()
    generate_publication_evidence()
    generate_genesis()
    generate_orphan_status()
    generate_disposition_manifest()
    generate_provenance()
    print("Stage -1 evidence backfill complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
