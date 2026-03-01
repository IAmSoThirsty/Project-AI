"""Tests for RepairCrew — self-healing diagnostics and repair for Project-AI."""

from __future__ import annotations

import os
import tempfile

import pytest

from app.miniature_office.repair_crew import (
    DiagnosticReport,
    IssueSeverity,
    RepairCrew,
)


@pytest.fixture
def crew():
    return RepairCrew()


@pytest.fixture
def sample_py_file(tmp_path):
    """Create a sample Python file with known issues."""
    code = """\
import os

password="hardcoded_secret"  # noqa: S105

def foo():
    try:
        pass
    except:
        pass

# TODO: fix this later
"""
    fpath = tmp_path / "sample.py"
    fpath.write_text(code)
    return str(fpath)


class TestRepairCrewDiagnose:
    def test_diagnose_returns_report(self, crew, tmp_path):
        (tmp_path / "clean.py").write_text("import os\n")
        report = crew.diagnose(str(tmp_path))
        assert isinstance(report, DiagnosticReport)
        assert report.files_scanned >= 1
        assert report.report_id.startswith("diag_")

    def test_diagnose_detects_bare_except(self, crew, sample_py_file):
        report = crew.diagnose(os.path.dirname(sample_py_file))
        bare_excepts = [i for i in report.issues if i.category == "style"]
        assert len(bare_excepts) >= 1
        assert bare_excepts[0].severity == IssueSeverity.WARNING

    def test_diagnose_detects_hardcoded_secret(self, crew, sample_py_file):
        report = crew.diagnose(os.path.dirname(sample_py_file))
        secrets = [i for i in report.issues if i.category == "security"]
        assert len(secrets) >= 1
        assert secrets[0].severity == IssueSeverity.CRITICAL

    def test_diagnose_detects_todo(self, crew, sample_py_file):
        report = crew.diagnose(os.path.dirname(sample_py_file))
        todos = [i for i in report.issues if i.category == "technical_debt"]
        assert len(todos) >= 1


class TestRepairCrewRepair:
    def test_repair_produces_patches(self, crew, sample_py_file):
        report = crew.diagnose(os.path.dirname(sample_py_file))
        repair_report = crew.repair(report)
        # Should produce patches for critical/error issues with suggested_fix
        assert repair_report.repair_id.startswith("repair_")
        assert repair_report.diagnostic_report_id == report.report_id

    def test_repair_patches_have_confidence(self, crew, sample_py_file):
        report = crew.diagnose(os.path.dirname(sample_py_file))
        repair_report = crew.repair(report)
        for patch in repair_report.patches:
            assert 0.0 <= patch.confidence <= 1.0


class TestRepairCrewHealth:
    def test_health_report_before_scan(self, crew):
        health = crew.get_health_report()
        assert health["last_diagnosis"]["report_id"] is None
        assert health["last_diagnosis"]["summary"] == "No scan run yet"

    def test_health_report_after_scan(self, crew, sample_py_file):
        crew.diagnose(os.path.dirname(sample_py_file))
        health = crew.get_health_report()
        assert health["last_diagnosis"]["report_id"] is not None
        assert health["last_diagnosis"]["issue_count"] > 0
