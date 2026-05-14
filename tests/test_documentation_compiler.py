"""Tests for DocumentationCompilerAgent.

Verifies evidence extraction, section compilation, documentation generation,
and verification capabilities.
"""

import json
import tempfile
from pathlib import Path

import pytest

from app.agents.documentation_compiler import (
    DocumentationCompilerAgent,
    DocumentationSection,
    TechnicalDocument,
)


@pytest.fixture
def temp_dir():
    """Provide temporary directory for test artifacts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def agent(temp_dir):
    """Create DocumentationCompilerAgent with temporary output directory."""
    return DocumentationCompilerAgent(
        kernel=None,  # No kernel for unit tests
        output_dir=str(Path(temp_dir) / "docs"),
    )


@pytest.fixture
def sample_code_file(temp_dir):
    """Create a sample Python code file for evidence extraction."""
    code_content = '''"""Sample module for testing."""

from app.core.cognition_kernel import CognitionKernel


class SampleSystem:
    """A sample system with governance integration."""

    def __init__(self, kernel: CognitionKernel):
        self.kernel = kernel

    def execute(self, action: str) -> str:
        """Execute an action through governance."""
        return self.kernel.process(action)

    def validate(self, data: dict) -> bool:
        """Validate input data."""
        return True
'''
    file_path = Path(temp_dir) / "sample_system.py"
    file_path.write_text(code_content, encoding="utf-8")
    return str(file_path)


@pytest.fixture
def sample_test_file(temp_dir):
    """Create a sample test file for evidence extraction."""
    test_content = '''"""Tests for sample system."""

import pytest


@pytest.fixture
def sample_fixture():
    """Provide sample fixture."""
    return {}


def test_initialization():
    """Test system initialization."""
    assert True


def test_execute():
    """Test execute method."""
    assert True


def test_validate():
    """Test validate method."""
    assert True
'''
    file_path = Path(temp_dir) / "test_sample_system.py"
    file_path.write_text(test_content, encoding="utf-8")
    return str(file_path)


@pytest.fixture
def sample_config_file(temp_dir):
    """Create a sample YAML config file for evidence extraction."""
    config_content = """governance:
  enabled: true
  threshold: 0.7

security:
  validation_required: true
  encryption: AES-256
"""
    file_path = Path(temp_dir) / "config.yaml"
    file_path.write_text(config_content, encoding="utf-8")
    return str(file_path)


class TestDocumentationCompilerAgent:
    """Test suite for DocumentationCompilerAgent."""

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.enabled is True
        assert Path(agent.output_dir).exists()
        assert Path(agent.evidence_cache_dir).exists()

    def test_extract_code_evidence(self, agent, sample_code_file):
        """Test evidence extraction from code file."""
        evidence = agent.extract_evidence(sample_code_file, evidence_type="code")

        assert evidence["evidence_type"] == "code"
        assert "SampleSystem" in evidence["classes"]
        assert "execute" in evidence["functions"]
        assert "validate" in evidence["functions"]
        assert evidence["has_governance"] is True
        assert evidence["has_validation"] is True
        assert evidence["line_count"] > 0

    def test_extract_test_evidence(self, agent, sample_test_file):
        """Test evidence extraction from test file."""
        evidence = agent.extract_evidence(sample_test_file, evidence_type="test")

        assert evidence["evidence_type"] == "test"
        assert evidence["test_count"] == 3
        assert "test_initialization" in evidence["test_functions"]
        assert "test_execute" in evidence["test_functions"]
        assert "test_validate" in evidence["test_functions"]
        assert evidence["has_unit_tests"] is True

    def test_extract_config_evidence(self, agent, sample_config_file):
        """Test evidence extraction from config file."""
        evidence = agent.extract_evidence(sample_config_file, evidence_type="config")

        assert evidence["evidence_type"] == "config"
        assert "governance" in evidence["config_keys"]
        assert "security" in evidence["config_keys"]
        assert evidence["has_governance_config"] is True
        assert evidence["config_type"] == ".yaml"

    def test_auto_detect_evidence_type(self, agent, sample_test_file):
        """Test automatic evidence type detection."""
        evidence = agent.extract_evidence(sample_test_file, evidence_type="auto")

        # Should auto-detect as test file
        assert evidence["evidence_type"] == "test"
        assert evidence["test_count"] > 0

    def test_compile_section(self, agent):
        """Test individual section compilation."""
        evidence = {
            "code": {
                "classes": ["SampleSystem"],
                "has_governance": True,
            },
            "tests": {
                "test_count": 5,
                "has_unit_tests": True,
            },
        }

        section = agent.compile_section(
            section_title="Architecture",
            evidence=evidence,
            section_type="architecture",
        )

        assert isinstance(section, DocumentationSection)
        assert section.title == "Architecture"
        assert section.verification_status in ("verified", "unverified")
        assert section.last_verified is not None

    def test_compile_system_documentation(
        self,
        agent,
        sample_code_file,
        sample_test_file,
        sample_config_file,
    ):
        """Test complete system documentation compilation."""
        evidence_paths = [sample_code_file, sample_test_file, sample_config_file]

        output_path = agent.compile_system_documentation(
            system_name="SampleSystem",
            evidence_paths=evidence_paths,
            include_tests=True,
            include_code_samples=True,
        )

        assert Path(output_path).exists()
        content = Path(output_path).read_text(encoding="utf-8")

        # Verify standard sections present
        assert "## Purpose" in content
        assert "## Architecture" in content
        assert "## Governance Model" in content
        assert "## Execution Flow" in content
        assert "## Security Model" in content
        assert "## Tests and Verification" in content
        assert "## Failure Modes" in content
        assert "## Deployment Considerations" in content
        assert "## Open Risks / Unresolved Items" in content

        # Verify metadata
        assert "SampleSystem — Technical Documentation" in content
        assert "Generated:" in content
        assert "DocumentationCompilerAgent" in content

    def test_compile_without_tests_section(self, agent, sample_code_file):
        """Test documentation compilation with tests section excluded."""
        output_path = agent.compile_system_documentation(
            system_name="MinimalSystem",
            evidence_paths=[sample_code_file],
            include_tests=False,
            include_code_samples=False,
        )

        content = Path(output_path).read_text(encoding="utf-8")

        # Tests section should be skipped
        assert "## Purpose" in content
        assert "## Architecture" in content
        # Would not have test-specific content since include_tests=False

    def test_verify_documentation_accurate(self, agent, sample_code_file, temp_dir):
        """Test documentation verification when docs are accurate."""
        # Create a simple documentation file
        doc_content = """# Sample System

## Architecture

Core Classes: `SampleSystem`

## Governance Model

✅ **Governance Integration:** All operations route through CognitionKernel.
"""
        doc_path = Path(temp_dir) / "sample_docs.md"
        doc_path.write_text(doc_content, encoding="utf-8")

        result = agent.verify_documentation(
            doc_path=str(doc_path),
            evidence_paths=[sample_code_file],
        )

        assert result["status"] in ("accurate", "discrepancies_found")
        assert "verified_at" in result
        assert isinstance(result["discrepancies"], list)
        assert isinstance(result["warnings"], list)

    def test_verify_documentation_discrepancies(self, agent, sample_code_file, temp_dir):
        """Test documentation verification with discrepancies."""
        # Create documentation with false claim
        doc_content = """# Sample System

This system is deprecated and should not be used.

100% test coverage verified.
"""
        doc_path = Path(temp_dir) / "inaccurate_docs.md"
        doc_path.write_text(doc_content, encoding="utf-8")

        result = agent.verify_documentation(
            doc_path=str(doc_path),
            evidence_paths=[sample_code_file],  # No test file provided
        )

        # Should detect test coverage claim without tests
        assert result["status"] == "discrepancies_found"
        assert len(result["discrepancies"]) > 0

    def test_verify_nonexistent_documentation(self, agent):
        """Test verification handles missing documentation file."""
        result = agent.verify_documentation(
            doc_path="/nonexistent/path/docs.md",
            evidence_paths=[],
        )

        assert result["status"] == "error"
        assert "not found" in result["message"]

    def test_technical_document_dataclass(self):
        """Test TechnicalDocument dataclass initialization."""
        doc = TechnicalDocument(title="Test Document")

        assert doc.title == "Test Document"
        assert doc.created_at != ""
        assert doc.last_updated != ""
        assert len(doc.sections) == 0
        assert isinstance(doc.metadata, dict)

    def test_documentation_section_dataclass(self):
        """Test DocumentationSection dataclass initialization."""
        section = DocumentationSection(
            title="Test Section",
            content="Test content",
            evidence_refs=["file1.py", "file2.py"],
        )

        assert section.title == "Test Section"
        assert section.content == "Test content"
        assert len(section.evidence_refs) == 2
        assert section.verification_status == "unverified"

    def test_extract_evidence_nonexistent_file(self, agent):
        """Test evidence extraction handles missing files."""
        evidence = agent.extract_evidence("/nonexistent/file.py")

        assert "error" in evidence
        assert "not found" in evidence["error"].lower()

    def test_governance_detection(self, agent, sample_code_file):
        """Test detection of governance integration in code."""
        evidence = agent.extract_evidence(sample_code_file, evidence_type="code")

        assert evidence["has_governance"] is True

    def test_validation_detection(self, agent, sample_code_file):
        """Test detection of validation patterns in code."""
        evidence = agent.extract_evidence(sample_code_file, evidence_type="code")

        assert evidence["has_validation"] is True

    def test_multiple_test_functions_extraction(self, agent, sample_test_file):
        """Test extraction of multiple test functions."""
        evidence = agent.extract_evidence(sample_test_file, evidence_type="test")

        assert evidence["test_count"] == 3
        assert len(evidence["test_functions"]) == 3

    def test_fixture_extraction(self, agent, sample_test_file):
        """Test extraction of pytest fixtures."""
        evidence = agent.extract_evidence(sample_test_file, evidence_type="test")

        assert "sample_fixture" in evidence["fixtures"]

    def test_output_directory_creation(self, temp_dir):
        """Test agent creates output directories if they don't exist."""
        output_dir = str(Path(temp_dir) / "custom_output")
        agent = DocumentationCompilerAgent(output_dir=output_dir)

        assert Path(output_dir).exists()
        assert Path(agent.evidence_cache_dir).exists()

    def test_markdown_output_format(self, agent, sample_code_file):
        """Test generated documentation is valid markdown."""
        output_path = agent.compile_system_documentation(
            system_name="MarkdownTest",
            evidence_paths=[sample_code_file],
            include_tests=True,
            include_code_samples=True,
        )

        content = Path(output_path).read_text(encoding="utf-8")

        # Check markdown formatting
        assert content.startswith("# ")
        assert "##" in content  # Has sections
        assert "**" in content  # Has bold text
        assert "---" in content  # Has horizontal rules

    def test_evidence_reference_tracking(self, agent, sample_code_file, sample_test_file):
        """Test that evidence references are tracked in sections."""
        evidence_paths = [sample_code_file, sample_test_file]

        output_path = agent.compile_system_documentation(
            system_name="ReferenceTest",
            evidence_paths=evidence_paths,
            include_tests=True,
            include_code_samples=False,
        )

        content = Path(output_path).read_text(encoding="utf-8")

        # Should have generated documentation with standard structure
        assert "ReferenceTest — Technical Documentation" in content
        assert "DocumentationCompilerAgent" in content
        assert "## Architecture" in content or "## Governance Model" in content

    def test_agent_caching(self, agent, sample_code_file):
        """Test that compiled documents are cached in agent."""
        system_name = "CachedSystem"

        agent.compile_system_documentation(
            system_name=system_name,
            evidence_paths=[sample_code_file],
        )

        # Document should be cached
        assert system_name in agent._documents
        cached_doc = agent._documents[system_name]
        assert isinstance(cached_doc, TechnicalDocument)
        assert cached_doc.title == f"{system_name} — Technical Documentation"
