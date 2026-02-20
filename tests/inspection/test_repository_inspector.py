"""
Tests for RepositoryInspector

Author: Project-AI Team
Date: 2026-02-08
"""

import tempfile
from pathlib import Path

import pytest

from app.inspection.repository_inspector import (
    FileType,
    RepositoryInspector,
)


@pytest.fixture
def temp_repo():
    """Create a temporary repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        # Create some test files
        (repo_path / "src").mkdir()
        (repo_path / "src" / "main.py").write_text('"""Main module."""\n\ndef main():\n    print("Hello")\n')
        (repo_path / "src" / "utils.py").write_text("def helper():\n    pass\n")
        (repo_path / "tests").mkdir()
        (repo_path / "tests" / "test_main.py").write_text("def test_main():\n    assert True\n")
        (repo_path / "README.md").write_text("# Test Project\n")
        (repo_path / "config.yaml").write_text("key: value\n")

        yield repo_path


class TestRepositoryInspector:
    """Test suite for RepositoryInspector."""

    def test_initialization(self, temp_repo):
        """Test inspector initialization."""
        inspector = RepositoryInspector(temp_repo)

        assert inspector.repo_root == temp_repo
        assert len(inspector.files) == 0
        assert len(inspector.components) == 0

    def test_file_discovery(self, temp_repo):
        """Test file discovery."""
        inspector = RepositoryInspector(temp_repo)
        inspector._discover_files()

        assert len(inspector.files) >= 5  # At least the files we created

        # Check if expected files are discovered
        file_paths = [f.relative_path for f in inspector.files.values()]
        assert any("main.py" in p for p in file_paths)
        assert any("README.md" in p for p in file_paths)

    def test_file_type_detection(self, temp_repo):
        """Test file type detection."""
        inspector = RepositoryInspector(temp_repo)
        inspector._discover_files()

        for file_info in inspector.files.values():
            if file_info.name.endswith(".py"):
                assert file_info.file_type in [
                    FileType.PYTHON_MODULE,
                    FileType.PYTHON_TEST,
                ]
            elif file_info.name.endswith(".md"):
                assert file_info.file_type == FileType.MARKDOWN
            elif file_info.name.endswith(".yaml"):
                assert file_info.file_type == FileType.YAML

    def test_python_analysis(self, temp_repo):
        """Test Python file analysis."""
        inspector = RepositoryInspector(temp_repo)
        results = inspector.inspect()

        # Find main.py
        main_file = next(
            (f for f in results["files"].values() if "main.py" in f["relative_path"]),
            None,
        )

        assert main_file is not None
        assert main_file["lines_of_code"] > 0
        assert "main" in main_file["functions"]
        assert main_file["docstring"]  # Should have module docstring

    def test_test_file_detection(self, temp_repo):
        """Test test file detection."""
        inspector = RepositoryInspector(temp_repo)
        results = inspector.inspect()

        test_file = next(
            (f for f in results["files"].values() if "test_main.py" in f["relative_path"]),
            None,
        )

        assert test_file is not None
        assert test_file["is_test"]

    def test_component_identification(self, temp_repo):
        """Test component identification."""
        inspector = RepositoryInspector(temp_repo)
        results = inspector.inspect()

        assert len(results["components"]) > 0

        # Should have identified src and tests as components
        component_names = list(results["components"].keys())
        assert any("src" in name for name in component_names)
        assert any("tests" in name for name in component_names)

    def test_statistics_computation(self, temp_repo):
        """Test statistics computation."""
        inspector = RepositoryInspector(temp_repo)
        results = inspector.inspect()

        stats = results["statistics"]
        assert stats["total_files"] >= 5
        assert stats["total_lines"] > 0
        assert "by_type" in stats
        assert "by_status" in stats
        assert "by_component" in stats

    def test_exclusions(self, temp_repo):
        """Test file exclusions."""
        # Create some files that should be excluded
        (temp_repo / "__pycache__").mkdir()
        (temp_repo / "__pycache__" / "main.pyc").write_text("bytecode")

        inspector = RepositoryInspector(temp_repo)
        inspector._discover_files()

        # __pycache__ files should be excluded
        file_paths = [f.relative_path for f in inspector.files.values()]
        assert not any("__pycache__" in p for p in file_paths)

    def test_json_export(self, temp_repo):
        """Test JSON export functionality."""
        inspector = RepositoryInspector(temp_repo)
        inspector.inspect()

        output_file = temp_repo / "inspection_results.json"
        inspector.export_json(output_file)

        assert output_file.exists()

        # Verify JSON is valid
        import json

        with open(output_file) as f:
            data = json.load(f)

        assert "files" in data
        assert "components" in data
        assert "statistics" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
