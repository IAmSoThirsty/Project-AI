"""Arch Angel passive guardian for governance DOI link integrity.

The Arch Angel is not a chat agent. It watches the governance document graph,
repairs safe DOI/path drift, and reports risky drift to the Triumvirate.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


PROVENANCE_START = "<!-- ARCH_ANGEL:RESEARCH_PROVENANCE START -->"
PROVENANCE_END = "<!-- ARCH_ANGEL:RESEARCH_PROVENANCE END -->"
REFERENCES_START = "<!-- ARCH_ANGEL:REFERENCES START -->"
REFERENCES_END = "<!-- ARCH_ANGEL:REFERENCES END -->"
UTC = getattr(datetime, "UTC", timezone.utc)  # noqa: UP017


@dataclass(frozen=True)
class PublicationRecord:
    """Canonical DOI record protected by the Arch Angel."""

    number: int
    paper_id: str
    named_note: str
    title: str
    doi: str
    record_type: str
    domain: str
    era: str
    source_artifacts: tuple[str, ...] = ()

    @property
    def doi_id(self) -> str:
        return self.doi.removeprefix("https://doi.org/")

    @property
    def zenodo_id(self) -> str:
        return self.doi.rsplit(".", 1)[-1]

    @property
    def paper_path(self) -> str:
        return f"wiki/07_Research/Publications/{self.paper_id}.md"

    @property
    def named_path(self) -> str:
        return f"wiki/07_Research/Publications/{self.named_note}.md"

    @property
    def bibtex_key(self) -> str:
        stem = re.sub(r"[^a-z0-9]+", "_", self.title.lower()).strip("_")
        return f"karrick_{stem}_{self.zenodo_id}"


@dataclass
class Diagnostic:
    severity: str
    code: str
    message: str
    path: str | None = None
    doi: str | None = None


@dataclass
class RepairAction:
    action: str
    path: str
    reason: str
    changed: bool
    dry_run: bool
    digest_before: str | None = None
    digest_after: str | None = None


@dataclass
class ArchAngelReport:
    status: str
    generated_at: str
    diagnostics: list[Diagnostic]
    repairs: list[RepairAction]
    protected_paths: list[str]
    total_publications: int

    @property
    def has_issues(self) -> bool:
        return bool(self.diagnostics)

    @property
    def has_critical(self) -> bool:
        return any(item.severity == "critical" for item in self.diagnostics)


def _artifacts(*items: str) -> tuple[str, ...]:
    return tuple(items)


CATALOG: tuple[PublicationRecord, ...] = (
    PublicationRecord(
        1,
        "Paper-01",
        "OctoReflex-Report",
        "OctoReflex",
        "https://doi.org/10.5281/zenodo.18726064",
        "Report",
        "security",
        "2",
        _artifacts("c:/Users/Quencher/Desktop/Project-AI Wiki/OctoReflex.md"),
    ),
    PublicationRecord(
        2,
        "Paper-02",
        "Sovereign-Covenant",
        "The Sovereign Covenant",
        "https://doi.org/10.5281/zenodo.18726221",
        "Publication",
        "governance",
        "1",
    ),
    PublicationRecord(
        3,
        "Paper-03",
        "AGI-Charter",
        "AGI Charter for Project-AI",
        "https://doi.org/10.5281/zenodo.18763076",
        "Other",
        "governance",
        "1",
        _artifacts("c:/Users/Quencher/Documents/Docs/AGI Charter.pdf"),
    ),
    PublicationRecord(
        4,
        "Paper-04",
        "TSCG",
        "TSCG",
        "https://doi.org/10.5281/zenodo.18794292",
        "Technical Note",
        "architecture",
        "2",
        _artifacts(
            "c:/Users/Quencher/Desktop/Project-AI Wiki/TSCG.md",
            "c:/Users/Quencher/Desktop/Project-AI Wiki/TARL.md",
        ),
    ),
    PublicationRecord(
        5,
        "Paper-05",
        "Constitutional-Architectures",
        "Constitutional Architectures",
        "https://doi.org/10.5281/zenodo.18794646",
        "Technical Note",
        "architecture",
        "1",
    ),
    PublicationRecord(
        6,
        "Paper-06",
        "TSCG-B",
        "TSCG-B",
        "https://doi.org/10.5281/zenodo.18826409",
        "Report",
        "architecture",
        "2",
    ),
    PublicationRecord(
        7,
        "Paper-07",
        "The-Flat-Gap",
        "The Flat Gap",
        "https://doi.org/10.5281/zenodo.18827649",
        "Preprint",
        "governance",
        "3",
    ),
    PublicationRecord(
        8,
        "Paper-08",
        "User-Perception-Identity",
        "User Perception and Identity Problem",
        "https://doi.org/10.5281/zenodo.19055819",
        "Preprint",
        "research",
        "3",
    ),
    PublicationRecord(
        9,
        "Paper-09",
        "Directness-Doctrine",
        "The Directness Doctrine",
        "https://doi.org/10.5281/zenodo.19030041",
        "Preprint",
        "systems",
        "3",
        _artifacts("c:/Users/Quencher/Desktop/Project-AI Wiki/PSIA_Waterfall.md"),
    ),
    PublicationRecord(
        10,
        "Paper-10",
        "State-Register",
        "The State Register",
        "https://doi.org/10.5281/zenodo.19101877",
        "Report",
        "security",
        "2",
        _artifacts("c:/Users/Quencher/Documents/Docs/The_STATE_REGISTER_Karrick_Jeremy.docx"),
    ),
    PublicationRecord(
        11,
        "Paper-11",
        "Asymmetric-Security",
        "Project-AI Asymmetric Security",
        "https://doi.org/10.5281/zenodo.19162019",
        "Technical Note",
        "security",
        "4",
    ),
    PublicationRecord(
        12,
        "Paper-12",
        "Naive-Passive-Reviewer",
        "The Naive Passive Reviewer",
        "https://doi.org/10.5281/zenodo.19453224",
        "Publication",
        "research",
        "4",
    ),
    PublicationRecord(
        13,
        "Paper-13",
        "Information-Preservation",
        "The Universe Does not Preserve All Information",
        "https://doi.org/10.5281/zenodo.19481152",
        "Report",
        "research",
        "3",
    ),
    PublicationRecord(
        14,
        "Paper-14",
        "Genesis-MicroServices",
        "Genesis: MicroServices Generation",
        "https://doi.org/10.5281/zenodo.19488571",
        "Software",
        "systems",
        "4",
        _artifacts("c:/Users/Quencher/Documents/Docs/MicroServicesEatThis.txt"),
    ),
    PublicationRecord(
        15,
        "Paper-15",
        "Governing-Force-AGI",
        "Governing Force In AGI",
        "https://doi.org/10.5281/zenodo.19582420",
        "Report",
        "governance",
        "4",
        _artifacts("c:/Users/Quencher/Documents/Docs/On_the_Governance_of_Force_v4.txt"),
    ),
    PublicationRecord(
        16,
        "Paper-16",
        "Two-Species-Aligned",
        "Two Species Aligned",
        "https://doi.org/10.5281/zenodo.19582479",
        "Publication",
        "governance",
        "5",
    ),
    PublicationRecord(
        17,
        "Paper-17",
        "Sovereign-Constitutional-Ecosystem",
        "Project-AI: Sovereign Constitutional AGI Ecosystem",
        "https://doi.org/10.5281/zenodo.19582539",
        "Report",
        "systems",
        "5",
        _artifacts(
            "c:/Users/Quencher/Documents/Docs/Sovereign Monolith Temporal Dissonance & Onboarding Guide.pdf"
        ),
    ),
    PublicationRecord(
        18,
        "Paper-18",
        "Iron-Path-Executor",
        "The Iron Path Executor",
        "https://doi.org/10.5281/zenodo.19583170",
        "Report",
        "systems",
        "5",
        _artifacts(
            "c:/Users/Quencher/Documents/Docs/The Iron Path Executor_ Formal Technical Specification for Deterministic AI Governance.pdf"
        ),
    ),
    PublicationRecord(
        19,
        "Paper-19",
        "Yggdrasil-DNS",
        "Yggdrasil: A Constitutional DNS Layer",
        "https://doi.org/10.5281/zenodo.19591259",
        "Report",
        "architecture",
        "5",
        _artifacts("c:/Users/Quencher/Documents/Docs/yggdrasil_final.pdf"),
    ),
    PublicationRecord(
        20,
        "Paper-20",
        "Constitutional-Code-Store",
        "The Constitutional Code Store",
        "https://doi.org/10.5281/zenodo.19591660",
        "Technical Note",
        "architecture",
        "5",
        _artifacts("c:/Users/Quencher/Documents/Docs/Constitutional_Code_Store_v1.0_Karrick.pdf"),
    ),
    PublicationRecord(
        21,
        "Paper-21",
        "Why-I-Am-Doing-This",
        "Why I Am Doing This",
        "https://doi.org/10.5281/zenodo.19592336",
        "Report",
        "corpus",
        "Meta",
        _artifacts(
            "c:/Users/Quencher/Documents/Docs/ill show you complete.txt",
            "c:/Users/Quencher/Documents/Docs/Why I Am  Doing This.txt",
        ),
    ),
)


DEFAULT_GOVERNANCE_PAPERS = (2, 3, 5, 7, 15, 16, 17, 21)
DOC_PAPER_HINTS: dict[str, tuple[int, ...]] = {
    "AGI_CHARTER.md": (2, 3, 5, 15, 16, 21),
    "AGI_IDENTITY_SPECIFICATION.md": (3, 8, 16, 17, 21),
    "AI-INDIVIDUAL-ROLE-HUMANITY-ALIGNMENT.md": (3, 15, 16, 21),
    "CONSTITUTIONAL_RESONANCE.md": (2, 5, 7, 15, 16, 17),
    "IDENTITY_SYSTEM_FULL_SPEC.md": (3, 8, 16, 17, 21),
    "IRREVERSIBILITY_FORMALIZATION.md": (10, 18, 20),
    "LEGION_COMMISSION.md": (2, 3, 15, 16, 17),
    "LEGION_SYSTEM_CONTEXT.md": (2, 3, 15, 16, 17),
    "LICENSING_GUIDE.md": (2, 3, 20, 21),
    "LICENSING_SUMMARY.md": (2, 3, 20, 21),
    "CODEX_DEUS_QUICK_REF.md": (2, 5, 15, 17, 20),
    "CODEX_DEUS_ULTIMATE_SUMMARY.md": (2, 5, 15, 17, 20),
    "Governance Index.md": (2, 3, 5, 7, 15, 16, 17, 21),
    "Identity-System.md": (3, 8, 16, 17, 21),
    "Reviewer-Trap.md": (12, 15, 18, 20),
}


class ArchAngel:
    """Passive governance document guardian with safe repair capabilities."""

    protected_roots = (
        "wiki/07_Research/Publications/**",
        "wiki/01_Governance/**",
        "docs/governance/**",
        "CITATIONS.md",
        "docs/CITATIONS.md",
    )

    def __init__(self, project_root: str | Path = ".") -> None:
        self.project_root = Path(project_root).resolve()
        self.repairs: list[RepairAction] = []
        self.diagnostics: list[Diagnostic] = []

    @property
    def catalog(self) -> tuple[PublicationRecord, ...]:
        return CATALOG

    def check(self, write_report: bool = True) -> ArchAngelReport:
        """Validate the document graph without repairing it."""
        self.repairs = []
        self.diagnostics = []
        self._check_manifest()
        self._check_catalog_paths()
        self._check_doi_registry()
        self._check_citations()
        self._check_governance_provenance()
        self._check_paper_references()
        report = self._build_report()
        if write_report:
            self.write_report(report)
            if report.has_issues:
                self._write_triumvirate_notification(report, "check")
        return report

    def repair(
        self, dry_run: bool = False, write_report: bool = True
    ) -> ArchAngelReport:
        """Safely repair governance DOI and path linkage."""
        self.repairs = []
        self.diagnostics = []
        self._repair_manifest(dry_run=dry_run)
        self._repair_doi_registry(dry_run=dry_run)
        self._repair_publications_index(dry_run=dry_run)
        self._repair_citations(dry_run=dry_run)
        self._repair_governance_map(dry_run=dry_run)
        self._repair_governance_provenance(dry_run=dry_run)
        self._repair_paper_references(dry_run=dry_run)

        repair_actions = list(self.repairs)
        if not dry_run:
            self.check(write_report=False)
            self.repairs = repair_actions
        report = self._build_report()
        if write_report:
            self.write_report(report)
            if self.repairs or report.has_issues:
                self._write_triumvirate_notification(report, "repair")
            if self.repairs and not dry_run:
                self._write_repair_audit(report)
        return report

    def latest_report(self) -> dict[str, Any] | None:
        """Return the latest persisted report, if available."""
        path = self.project_root / "data/arch_angel/reports/latest.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def watch(self, repair: bool = False, interval: float = 1.0) -> None:
        """Continuously watch protected docs and run check or repair."""
        try:
            from watchdog.events import FileSystemEventHandler
            from watchdog.observers import Observer
        except ImportError as exc:  # pragma: no cover - exercised manually
            msg = "watchdog is required for watch mode. Install project-ai[taar]."
            raise RuntimeError(msg) from exc

        class Handler(FileSystemEventHandler):
            def __init__(self, angel: ArchAngel) -> None:
                self.angel = angel
                self.last_run = 0.0

            def on_any_event(self, event: Any) -> None:
                if event.is_directory:
                    return
                path = Path(event.src_path)
                if path.suffix.lower() not in {".md", ".yaml", ".yml"}:
                    return
                if not self.angel._is_protected_path(path):
                    return
                now = time.time()
                if now - self.last_run < interval:
                    return
                self.last_run = now
                self.angel.repair() if repair else self.angel.check()

        observer = Observer()
        observer.schedule(Handler(self), str(self.project_root), recursive=True)
        observer.start()
        try:  # pragma: no cover - exercised manually
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def _check_manifest(self) -> None:
        path = self.project_root / "docs/governance/arch_angel_manifest.yaml"
        if not path.exists():
            self._diag("warning", "manifest_missing", "Arch Angel manifest is missing", path)
            return
        if yaml is None:
            self._diag("critical", "yaml_unavailable", "PyYAML is unavailable", path)
            return
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            self._diag("critical", "manifest_invalid", f"Manifest cannot be parsed: {exc}", path)
            return
        if len(data.get("publications", [])) != len(self.catalog):
            self._diag("critical", "manifest_count", "Manifest publication count is not 21", path)

    def _check_catalog_paths(self) -> None:
        for record in self.catalog:
            for rel_path, code in (
                (record.paper_path, "paper_missing"),
                (record.named_path, "named_note_missing"),
            ):
                path = self.project_root / rel_path
                if not path.exists():
                    self._diag("critical", code, f"Missing protected file for {record.title}", path, record.doi)
                    continue
                text = path.read_text(encoding="utf-8")
                if record.doi not in text:
                    self._diag("critical", "doi_missing", f"Missing DOI for {record.title}", path, record.doi)

    def _check_doi_registry(self) -> None:
        path = self.project_root / "wiki/07_Research/Publications/DOI-Registry.md"
        text = self._read(path)
        for record in self.catalog:
            if record.paper_id not in text or record.named_note not in text or record.doi not in text:
                self._diag("critical", "registry_drift", f"Registry drift for {record.title}", path, record.doi)

    def _check_citations(self) -> None:
        for rel_path in ("CITATIONS.md", "docs/CITATIONS.md"):
            path = self.project_root / rel_path
            text = self._read(path)
            count = len(set(re.findall(r"10\.5281/zenodo\.\d+", text)))
            if count != len(self.catalog):
                self._diag("warning", "citation_count", f"{rel_path} cites {count} of 21 DOIs", path)
            for record in self.catalog:
                if record.doi_id not in text:
                    self._diag("warning", "citation_missing_doi", f"Missing citation for {record.title}", path, record.doi)

    def _check_governance_provenance(self) -> None:
        for path in self._governance_docs():
            if path.name == "GOVERNANCE_DOI_MAP.md":
                continue
            text = self._read(path)
            if PROVENANCE_START not in text or PROVENANCE_END not in text:
                self._diag("warning", "provenance_missing", "Missing Arch Angel provenance block", path)

    def _check_paper_references(self) -> None:
        for record in self.catalog:
            path = self.project_root / record.paper_path
            text = self._read(path)
            if REFERENCES_START not in text or REFERENCES_END not in text:
                self._diag("warning", "references_missing", f"Missing references block for {record.title}", path, record.doi)

    def _repair_manifest(self, dry_run: bool) -> None:
        path = self.project_root / "docs/governance/arch_angel_manifest.yaml"
        self._write_if_changed(path, self._render_manifest(), "refresh protected path manifest", dry_run)

    def _repair_doi_registry(self, dry_run: bool) -> None:
        path = self.project_root / "wiki/07_Research/Publications/DOI-Registry.md"
        self._write_if_changed(path, self._render_doi_registry(), "synchronize DOI registry", dry_run)

    def _repair_publications_index(self, dry_run: bool) -> None:
        path = self.project_root / "wiki/07_Research/Publications/Publications Index.md"
        self._write_if_changed(path, self._render_publications_index(), "synchronize publications index", dry_run)

    def _repair_citations(self, dry_run: bool) -> None:
        self._write_if_changed(
            self.project_root / "CITATIONS.md",
            self._render_citations("Research Citations and Publications"),
            "rebuild root citations",
            dry_run,
        )
        self._write_if_changed(
            self.project_root / "docs/CITATIONS.md",
            self._render_citations("Project-AI Scholarly Citations"),
            "rebuild docs citations",
            dry_run,
        )

    def _repair_governance_map(self, dry_run: bool) -> None:
        path = self.project_root / "docs/governance/GOVERNANCE_DOI_MAP.md"
        self._write_if_changed(path, self._render_governance_map(), "refresh governance DOI map", dry_run)

    def _repair_governance_provenance(self, dry_run: bool) -> None:
        for path in self._governance_docs():
            if path.name in {"GOVERNANCE_DOI_MAP.md"}:
                continue
            text = self._read(path)
            papers = DOC_PAPER_HINTS.get(path.name, DEFAULT_GOVERNANCE_PAPERS)
            block = self._render_provenance_block(papers, path)
            updated = self._insert_marked_block(text, block, PROVENANCE_START, PROVENANCE_END)
            self._write_if_changed(path, updated, "repair governance research provenance", dry_run)

    def _repair_paper_references(self, dry_run: bool) -> None:
        for record in self.catalog:
            path = self.project_root / record.paper_path
            text = self._read(path)
            block = self._render_references_block(record)
            updated = self._insert_marked_block(text, block, REFERENCES_START, REFERENCES_END)
            self._write_if_changed(path, updated, "repair paper references", dry_run)

    def _render_manifest(self) -> str:
        data = {
            "arch_angel": {
                "version": "1.0",
                "mode": "passive_non_conversational_guardian",
                "source_of_truth": "wiki/07_Research/Publications/DOI-Registry.md",
                "reports": {
                    "latest": "data/arch_angel/reports/latest.json",
                    "repairs": "data/arch_angel/repairs/",
                    "triumvirate_notifications": "data/triumvirate_notifications/",
                },
                "safe_repairs": [
                    "rewrite_doi_registry",
                    "rewrite_citation_tables",
                    "insert_governance_provenance_blocks",
                    "insert_publication_reference_blocks",
                    "refresh_publications_index",
                    "refresh_manifest",
                    "write_triumvirate_notifications",
                ],
                "risky_repairs_require_triumvirate": [
                    "delete_protected_documents",
                    "move_protected_documents",
                    "resolve_conflicting_doi_claims",
                    "modify_non_document_code",
                    "replace_large_document_sections",
                ],
            },
            "protected_roots": list(self.protected_roots),
            "publications": [
                {
                    **asdict(record),
                    "doi_id": record.doi_id,
                    "zenodo_id": record.zenodo_id,
                    "paper_path": record.paper_path,
                    "named_path": record.named_path,
                }
                for record in self.catalog
            ],
        }
        if yaml is None:
            return json.dumps(data, indent=2) + "\n"
        return yaml.safe_dump(data, sort_keys=False, allow_unicode=False)

    def _render_doi_registry(self) -> str:
        complete_rows = "\n".join(
            f"| [[{r.paper_id}]] | {r.doi} | {r.domain} |" for r in self.catalog
        )
        named_rows = "\n".join(
            f"| {r.number} | [[{r.named_note}]] | [{r.zenodo_id}]({r.doi}) | {r.record_type} | {r.era} |"
            for r in self.catalog
        )
        return f"""---
type: reference
priority: supporting
layer: research
status: active
tags:
  - type/reference
  - layer/research
---

# DOI Registry

> Complete Zenodo DOI catalog for Project-AI publications.
> Permanent archival records at https://doi.org/10.5281/zenodo/[ID]

---

## Complete Catalog

| Paper | DOI | Domain |
|------|-----|--------|
{complete_rows}

## Named Catalog

| # | Paper | DOI | Type | Era |
|---|-------|-----|------|-----|
{named_rows}

---

## Citation Format

```text
Karrick, J. (2026). [Title]. Zenodo. https://doi.org/10.5281/zenodo.[ID]
```

---

## Arch Angel Guard

This registry is protected by [[GOVERNANCE_DOI_MAP]] and `docs/governance/arch_angel_manifest.yaml`.

## Navigation

- ↑ [[Publications Index]] - Publications index
- → [[Sovereign-Journey]] - Timeline view
"""

    def _render_publications_index(self) -> str:
        by_domain: dict[str, list[PublicationRecord]] = {}
        for record in self.catalog:
            by_domain.setdefault(record.domain, []).append(record)
        domain_sections = []
        for domain in sorted(by_domain):
            rows = "\n".join(f"- [[{r.named_note}]] - {r.zenodo_id}" for r in by_domain[domain])
            domain_sections.append(f"### {domain.title()}\n{rows}")
        all_papers = "\n".join(f"- [[{r.paper_id}]]" for r in self.catalog)
        named = "\n".join(f"{r.number}. [[{r.named_note}]] - {r.zenodo_id}" for r in self.catalog)
        return f"""---
type: index
priority: canonical
layer: research
status: active
tags:
  - type/index
  - layer/research
---

# Publications Index

> 21 publications permanently archived on Zenodo.
> This is Project-AI's intellectual provenance.

---

## By Domain

{chr(10).join(domain_sections)}

---

## All Papers

{all_papers}

## Named Publication Notes

{named}

---

## DOI Registry

For complete DOI metadata: [[DOI-Registry]]

## Arch Angel Guard

This index is protected by `docs/governance/arch_angel_manifest.yaml`.

## Navigation

- ↑ [[Sovereign-Journey]] - Publications timeline
- → [[System-Map]] - Back to main navigation
"""

    def _render_citations(self, title: str) -> str:
        rows = "\n".join(
            f"| {r.number} | {r.title} | {r.record_type} | `{r.doi_id}` | [Link]({r.doi}) | [[{r.paper_id}]] / [[{r.named_note}]] |"
            for r in self.catalog
        )
        bibtex = "\n\n".join(
            f"""@misc{{{r.bibtex_key},
  author = {{Karrick, Jeremy}},
  title = {{{r.title}}},
  year = {{2026}},
  publisher = {{Zenodo}},
  doi = {{{r.doi_id}}},
  url = {{{r.doi}}}
}}"""
            for r in self.catalog
        )
        apa = "\n".join(
            f"- Karrick, J. (2026). *{r.title}*. Zenodo. {r.doi}" for r in self.catalog
        )
        return f"""# {title}

This document is maintained by the Arch Angel document guardian. The canonical source of truth is `wiki/07_Research/Publications/DOI-Registry.md`.

## Complete DOI Catalog

| # | Title | Type | DOI | Zenodo Link | Repo Notes |
|---|-------|------|-----|-------------|------------|
{rows}

## BibTeX

```bibtex
{bibtex}
```

## APA Style

{apa}

## Governance Linkage

- Canonical registry: `wiki/07_Research/Publications/DOI-Registry.md`
- Governance map: `docs/governance/GOVERNANCE_DOI_MAP.md`
- Protected manifest: `docs/governance/arch_angel_manifest.yaml`

**Last Updated:** 2026-04-16
**Total Publications:** 21
**Primary Archive:** Zenodo (https://zenodo.org)
"""

    def _render_governance_map(self) -> str:
        rows = "\n".join(
            f"| {r.number} | [[{r.paper_id}]] | [[{r.named_note}]] | {r.title} | {r.record_type} | [{r.zenodo_id}]({r.doi}) | {r.domain} |"
            for r in self.catalog
        )
        doc_rows = []
        for path in self._governance_docs():
            papers = DOC_PAPER_HINTS.get(path.name, DEFAULT_GOVERNANCE_PAPERS)
            links = ", ".join(f"[[Paper-{n:02d}]]" for n in papers)
            doc_rows.append(f"| `{self._rel(path)}` | {links} |")
        return f"""# Governance DOI Map

The Arch Angel ties governance documentation to the Project-AI Zenodo publication spine. `wiki/07_Research/Publications/DOI-Registry.md` remains the source of truth for DOI identity.

## Canonical Papers

| # | Paper | Named Note | Title | Type | DOI | Domain |
|---|-------|------------|-------|------|-----|--------|
{rows}

## Governance Document Coverage

| Governance Path | DOI Anchors |
|-----------------|-------------|
{chr(10).join(doc_rows)}

## Repair Contract

- Safe repairs: citation table rebuilds, provenance block insertion, paper reference block insertion, index regeneration, manifest refresh, and Triumvirate notification writes.
- Escalations: deletion, protected path moves, conflicting DOI claims, non-document code mutations, or broad section replacements.
- Reports: `data/arch_angel/reports/latest.json`
- Repair audit: `data/arch_angel/repairs/`
- Triumvirate notifications: `data/triumvirate_notifications/`
"""

    def _render_provenance_block(self, paper_numbers: tuple[int, ...], path: Path) -> str:
        records = [self.catalog[number - 1] for number in paper_numbers]
        links = "\n".join(
            f"- [{record.title}]({self._relative_link(path, self.project_root / record.paper_path)}) - {record.doi}"
            for record in records
        )
        registry = self._relative_link(
            path, self.project_root / "wiki/07_Research/Publications/DOI-Registry.md"
        )
        gov_map = self._relative_link(
            path, self.project_root / "docs/governance/GOVERNANCE_DOI_MAP.md"
        )
        return f"""{PROVENANCE_START}
## Research Provenance

Arch Angel protected linkage:
- Canonical DOI registry: [DOI-Registry]({registry})
- Governance DOI map: [GOVERNANCE_DOI_MAP]({gov_map})
- Primary DOI anchors:
{links}
{PROVENANCE_END}
"""

    def _render_references_block(self, record: PublicationRecord) -> str:
        previous = self.catalog[record.number - 2] if record.number > 1 else None
        next_record = self.catalog[record.number] if record.number < len(self.catalog) else None
        previous_line = f"- Previous paper: [[{previous.paper_id}]]" if previous else "- Previous paper: None"
        next_line = f"- Next paper: [[{next_record.paper_id}]]" if next_record else "- Next paper: None"
        source_lines = "".join(
            f"- Provided source artifact: `{artifact}`\n" for artifact in record.source_artifacts
        )
        return f"""{REFERENCES_START}
## References

- DOI: [{record.doi_id}]({record.doi})
- Canonical named note: [[{record.named_note}]]
- DOI registry: [[DOI-Registry]]
- Publications index: [[Publications Index]]
{previous_line}
{next_line}
{source_lines}{REFERENCES_END}
"""

    def _insert_marked_block(self, text: str, block: str, start: str, end: str) -> str:
        pattern = re.compile(re.escape(start) + r".*?" + re.escape(end) + r"\n?", re.DOTALL)
        if pattern.search(text):
            return pattern.sub(block.rstrip() + "\n", text)

        lines = text.splitlines()
        insert_at = 0
        if lines and lines[0].strip() == "---":
            for index, line in enumerate(lines[1:], start=1):
                if line.strip() == "---":
                    insert_at = index + 1
                    break
        else:
            for index, line in enumerate(lines):
                if line.startswith("# "):
                    insert_at = index + 1
                    break

        while insert_at < len(lines) and not lines[insert_at].strip():
            insert_at += 1
        lines[insert_at:insert_at] = ["", block.rstrip(), ""]
        return "\n".join(lines).rstrip() + "\n"

    def _governance_docs(self) -> list[Path]:
        roots = [
            self.project_root / "docs/governance",
            self.project_root / "wiki/01_Governance",
        ]
        docs: list[Path] = []
        for root in roots:
            if root.exists():
                docs.extend(path for path in root.rglob("*.md") if path.is_file())
        return sorted(docs)

    def _read(self, path: Path) -> str:
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def _write_if_changed(
        self, path: Path, content: str, reason: str, dry_run: bool
    ) -> None:
        old = self._read(path)
        if old == content:
            self.repairs.append(RepairAction("noop", self._rel(path), reason, False, dry_run))
            return
        before = self._digest(old) if old else None
        after = self._digest(content)
        self.repairs.append(
            RepairAction("write", self._rel(path), reason, True, dry_run, before, after)
        )
        if dry_run:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")

    def _build_report(self) -> ArchAngelReport:
        status = "critical" if any(d.severity == "critical" for d in self.diagnostics) else "ok"
        if self.diagnostics and status == "ok":
            status = "warnings"
        return ArchAngelReport(
            status=status,
            generated_at=datetime.now(UTC).isoformat(),
            diagnostics=list(self.diagnostics),
            repairs=list(self.repairs),
            protected_paths=list(self.protected_roots),
            total_publications=len(self.catalog),
        )

    def write_report(self, report: ArchAngelReport) -> Path:
        """Persist latest Arch Angel report."""
        path = self.project_root / "data/arch_angel/reports/latest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._report_payload(report), indent=2), encoding="utf-8")
        return path

    def _write_repair_audit(self, report: ArchAngelReport) -> Path:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        path = self.project_root / f"data/arch_angel/repairs/{stamp}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._report_payload(report), indent=2), encoding="utf-8")
        return path

    def _write_triumvirate_notification(self, report: ArchAngelReport, operation: str) -> Path:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        path = self.project_root / f"data/triumvirate_notifications/arch_angel-{operation}-{stamp}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        changed_paths = sorted({repair.path for repair in report.repairs if repair.changed})
        payload = {
            "source": "Arch Angel",
            "operation": operation,
            "status": report.status,
            "timestamp": report.generated_at,
            "requires_review": report.has_critical,
            "user_visible_follow_up_needed": report.has_issues,
            "affected_paths": changed_paths,
            "diagnostics": [asdict(item) for item in report.diagnostics],
            "repairs": [asdict(item) for item in report.repairs if item.changed],
            "doi_records": [
                {
                    "paper": record.paper_id,
                    "title": record.title,
                    "doi": record.doi,
                    "type": record.record_type,
                }
                for record in self.catalog
            ],
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def _report_payload(self, report: ArchAngelReport) -> dict[str, Any]:
        return {
            "status": report.status,
            "generated_at": report.generated_at,
            "diagnostics": [asdict(item) for item in report.diagnostics],
            "repairs": [asdict(item) for item in report.repairs],
            "protected_paths": report.protected_paths,
            "total_publications": report.total_publications,
        }

    def _diag(
        self,
        severity: str,
        code: str,
        message: str,
        path: Path | str | None = None,
        doi: str | None = None,
    ) -> None:
        rel = self._rel(path) if path is not None else None
        self.diagnostics.append(Diagnostic(severity, code, message, rel, doi))

    def _is_protected_path(self, path: Path) -> bool:
        try:
            rel = path.resolve().relative_to(self.project_root).as_posix()
        except ValueError:
            return False
        return (
            rel.startswith("wiki/07_Research/Publications/")
            or rel.startswith("wiki/01_Governance/")
            or rel.startswith("docs/governance/")
            or rel in {"CITATIONS.md", "docs/CITATIONS.md"}
        )

    def _relative_link(self, source: Path, target: Path) -> str:
        return Path(os.path.relpath(target, source.parent)).as_posix()

    def _rel(self, path: Path | str) -> str:
        path = Path(path)
        try:
            return path.resolve().relative_to(self.project_root).as_posix()
        except ValueError:
            return path.as_posix()

    def _digest(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
