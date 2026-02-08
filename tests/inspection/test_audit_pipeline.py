"""
Tests for AuditPipeline

Author: Project-AI Team
Date: 2026-02-08
"""

import tempfile
from pathlib import Path

import pytest

from app.inspection.audit_pipeline import AuditConfig, AuditPipeline, run_audit


@pytest.fixture
def temp_repo():
    """Create a temporary repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        # Create a simple project structure
        (repo_path / "src").mkdir()
        (repo_path / "src" / "__init__.py").write_text("")
        (repo_path / "src" / "module.py").write_text(
            '"""Test module."""\n\nclass TestClass:\n    def method(self):\n        pass\n'
        )
        (repo_path / "tests").mkdir()
        (repo_path / "tests" / "test_module.py").write_text(
            "def test_something():\n    assert True\n"
        )
        (repo_path / "README.md").write_text("# Test\n")

        yield repo_path


class TestAuditPipeline:
    """Test suite for AuditPipeline."""

    def test_pipeline_initialization(self, temp_repo):
        """Test pipeline initialization."""
        config = AuditConfig(repo_root=temp_repo)
        pipeline = AuditPipeline(config=config)

        assert pipeline.repo_root == temp_repo
        assert pipeline.config == config

    def test_full_audit_run(self, temp_repo):
        """Test full audit pipeline execution."""
        config = AuditConfig(
            repo_root=temp_repo,
            output_dir=temp_repo / "reports",
        )

        pipeline = AuditPipeline(config=config)
        results = pipeline.run()

        # Verify results structure
        assert results.success
        assert results.timestamp
        assert results.execution_time_seconds >= 0
        assert results.inspection is not None
        assert results.integrity is not None
        assert results.quality is not None

    def test_audit_with_lint_disabled(self, temp_repo):
        """Test audit with lint checking disabled."""
        config = AuditConfig(
            repo_root=temp_repo,
            output_dir=temp_repo / "reports",
            enable_lint=False,
        )

        pipeline = AuditPipeline(config=config)
        results = pipeline.run()

        assert results.success
        assert results.lint is None  # Lint should be skipped

    def test_audit_with_reports_disabled(self, temp_repo):
        """Test audit with report generation disabled."""
        config = AuditConfig(
            repo_root=temp_repo,
            output_dir=temp_repo / "reports",
            generate_reports=False,
            generate_catalog=False,
        )

        pipeline = AuditPipeline(config=config)
        results = pipeline.run()

        assert results.success
        assert results.reports is None
        assert results.catalog_path is None

    def test_audit_inspection_results(self, temp_repo):
        """Test inspection phase results."""
        config = AuditConfig(repo_root=temp_repo)
        pipeline = AuditPipeline(config=config)
        results = pipeline.run()

        inspection = results.inspection
        assert inspection is not None

        # Check statistics
        stats = inspection["statistics"]
        assert stats["total_files"] >= 4  # At least the files we created
        assert stats["total_lines"] > 0

        # Check files were discovered
        assert len(inspection["files"]) >= 4

    def test_audit_quality_analysis(self, temp_repo):
        """Test quality analysis results."""
        config = AuditConfig(repo_root=temp_repo)
        pipeline = AuditPipeline(config=config)
        results = pipeline.run()

        quality = results.quality
        assert quality is not None

        # Check aggregate metrics
        agg = quality["aggregate_metrics"]
        assert "average_documentation_coverage" in agg
        assert "average_maintainability_index" in agg
        assert "total_files_analyzed" in agg

    def test_audit_overall_assessment(self, temp_repo):
        """Test overall assessment computation."""
        config = AuditConfig(
            repo_root=temp_repo,
            generate_catalog=True,
        )

        pipeline = AuditPipeline(config=config)
        results = pipeline.run()

        assessment = results.overall_assessment
        assert assessment is not None

        # Check health score
        assert "health_score" in assessment
        assert 0 <= assessment["health_score"] <= 100

        # Check grade
        assert "grade" in assessment
        assert assessment["grade"] in ["A", "B", "C", "D", "F"]

        # Check factors
        assert "health_factors" in assessment
        assert "recommendations" in assessment

    def test_convenience_function(self, temp_repo):
        """Test run_audit convenience function."""
        results = run_audit(
            repo_root=temp_repo,
            output_dir=str(temp_repo / "reports"),
            enable_lint=False,  # Disable for speed
        )

        assert results.success
        assert results.inspection is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
