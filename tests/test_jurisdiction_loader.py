"""Tests for JurisdictionLoader — compatibility checks and combined requirements."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from app.governance.jurisdiction_loader import JurisdictionLoader


class TestJurisdictionLoader:
    """Tests for JurisdictionLoader."""

    def _make_loader(self, tmp_path):
        """Create a loader with two test jurisdiction .md files."""
        j_dir = tmp_path / "docs" / "legal" / "jurisdictions"
        j_dir.mkdir(parents=True, exist_ok=True)

        # EU_GDPR jurisdiction
        (j_dir / "EU_GDPR.md").write_text(
            "---\n"
            "jurisdiction: European Union\n"
            "version: 1.0\n"
            "effective_date: 2018-05-25\n"
            "regulation: GDPR\n"
            "---\n"
            "## Requirements\n"
            "- Encryption of personal data\n"
            "- Right to erasure\n"
            "## Retention\n"
            "- Mandatory deletion after purpose fulfilled\n"
            "## Security\n"
            "- AES-256 encryption required\n",
            encoding="utf-8",
        )

        # US_CCPA jurisdiction
        (j_dir / "US_CCPA.md").write_text(
            "---\n"
            "jurisdiction: United States (California)\n"
            "version: 1.0\n"
            "effective_date: 2020-01-01\n"
            "regulation: CCPA\n"
            "---\n"
            "## Requirements\n"
            "- Notice at collection\n"
            "## Retention\n"
            "- Best-effort retention\n"
            "## Security\n"
            "- Reasonable security measures\n",
            encoding="utf-8",
        )

        return JurisdictionLoader(legal_docs_dir=str(tmp_path / "docs" / "legal"))

    # ── Basic loading ──

    def test_loads_jurisdictions(self, tmp_path):
        loader = self._make_loader(tmp_path)
        jcodes = loader.list_available_jurisdictions()
        assert "EU_GDPR" in jcodes
        assert "US_CCPA" in jcodes

    def test_get_jurisdiction(self, tmp_path):
        loader = self._make_loader(tmp_path)
        annex = loader.get_jurisdiction("EU_GDPR")
        assert annex is not None
        assert hasattr(annex, "document_hash")

    def test_get_unknown_jurisdiction(self, tmp_path):
        loader = self._make_loader(tmp_path)
        assert loader.get_jurisdiction("XX_FAKE") is None

    # ── Validation ──

    def test_validate_valid_selection(self, tmp_path):
        loader = self._make_loader(tmp_path)
        ok, msgs = loader.validate_jurisdiction_selection(["EU_GDPR"])
        assert ok is True

    def test_validate_unknown_code(self, tmp_path):
        loader = self._make_loader(tmp_path)
        ok, msgs = loader.validate_jurisdiction_selection(["XX_FAKE"])
        assert ok is False
        assert any("not found" in m.lower() for m in msgs)

    def test_validate_multi_jurisdiction(self, tmp_path):
        loader = self._make_loader(tmp_path)
        ok, msgs = loader.validate_jurisdiction_selection(["EU_GDPR", "US_CCPA"])
        # May have warnings but both codes are valid
        assert ok is True

    # ── Combined requirements ──

    def test_combined_requirements_single(self, tmp_path):
        loader = self._make_loader(tmp_path)
        combined = loader.get_combined_requirements(["EU_GDPR"])
        assert isinstance(combined, dict)
        assert "security_requirements" in combined

    def test_combined_requirements_multi(self, tmp_path):
        loader = self._make_loader(tmp_path)
        combined = loader.get_combined_requirements(["EU_GDPR", "US_CCPA"])
        assert isinstance(combined, dict)

    # ── Document hash ──

    def test_document_hash_deterministic(self, tmp_path):
        loader = self._make_loader(tmp_path)
        annex1 = loader.get_jurisdiction("EU_GDPR")
        annex2 = loader.get_jurisdiction("EU_GDPR")
        assert annex1.document_hash == annex2.document_hash

    # ── Empty directory ──

    def test_empty_jurisdiction_dir(self, tmp_path):
        j_dir = tmp_path / "docs" / "legal" / "jurisdictions"
        j_dir.mkdir(parents=True, exist_ok=True)
        loader = JurisdictionLoader(legal_docs_dir=str(tmp_path / "docs" / "legal"))
        assert loader.list_available_jurisdictions() == []
