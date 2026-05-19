from __future__ import annotations

from pathlib import Path

import yaml

from app.agents.arch_angel import (
    CATALOG,
    PROVENANCE_END,
    PROVENANCE_START,
    ArchAngel,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_catalog_has_21_unique_dois() -> None:
    assert len(CATALOG) == 21
    assert len({record.doi for record in CATALOG}) == 21
    assert [record.number for record in CATALOG] == list(range(1, 22))


def test_formal_source_artifacts_are_registered() -> None:
    artifacts = "\n".join(
        artifact for record in CATALOG for artifact in record.source_artifacts
    )
    assert "AGI Charter.pdf" in artifacts
    assert "Constitutional_Code_Store_v1.0_Karrick.pdf" in artifacts
    assert "Sovereign Monolith Temporal Dissonance" in artifacts
    assert "Project-AI Wiki/OctoReflex.md" in artifacts
    assert "Project-AI Wiki/TSCG.md" in artifacts


def test_manifest_loads_all_publications() -> None:
    manifest_path = PROJECT_ROOT / "docs/governance/arch_angel_manifest.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    assert data["arch_angel"]["mode"] == "passive_non_conversational_guardian"
    assert len(data["publications"]) == 21
    assert data["publications"][0]["doi"] == "https://doi.org/10.5281/zenodo.18726064"


def test_current_repo_arch_angel_check_is_clean() -> None:
    report = ArchAngel(PROJECT_ROOT).check(write_report=False)
    assert report.status == "ok"
    assert report.total_publications == 21
    assert report.diagnostics == []


def test_marked_block_insertion_is_idempotent(tmp_path: Path) -> None:
    angel = ArchAngel(tmp_path)
    text = "# Governance Doc\n\nBody\n"
    block = f"{PROVENANCE_START}\n## Research Provenance\n\nProtected.\n{PROVENANCE_END}\n"

    first = angel._insert_marked_block(text, block, PROVENANCE_START, PROVENANCE_END)
    second = angel._insert_marked_block(first, block, PROVENANCE_START, PROVENANCE_END)

    assert first == second
    assert first.count(PROVENANCE_START) == 1
    assert first.count(PROVENANCE_END) == 1
