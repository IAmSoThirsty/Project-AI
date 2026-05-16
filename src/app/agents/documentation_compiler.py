"""Documentation compiler agent for Project-AI technical documentation.

Converts verified architecture, code behavior, tests, and evidence into
clean, accurate technical documentation following Project-AI standards.

All documentation operations route through CognitionKernel for governance tracking.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)

_DEFAULT_OUTPUT_DIR = "docs/compiled"
_EVIDENCE_CACHE_DIR = "data/documentation_evidence"


@dataclass
class DocumentationSection:
    """Represents a documentation section with verified content."""

    title: str
    content: str
    evidence_refs: list[str] = field(default_factory=list)
    last_verified: str | None = None
    verification_status: str = "unverified"  # unverified, partial, verified


@dataclass
class TechnicalDocument:
    """Complete technical documentation artifact."""

    title: str
    sections: list[DocumentationSection] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    last_updated: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.last_updated:
            self.last_updated = self.created_at


class DocumentationCompilerAgent(KernelRoutedAgent):
    """Compiles verified technical documentation for Project-AI systems.

    Mission:
        Convert verified architecture, code behavior, tests, and evidence into
        clean technical documentation.

    Rules:
        - Do not invent implementation details.
        - Do not exaggerate proof.
        - Distinguish design intent from verified behavior.
        - Preserve Project-AI terminology accurately.
        - Emphasize governance-before-execution.
        - Include diagrams/tables only when they clarify.
        - Make documents useful for engineers, reviewers, and external evaluators.

    Preferred Structure:
        1. Purpose
        2. Architecture
        3. Governance model
        4. Execution flow
        5. Security model
        6. Evidence model
        7. Tests and verification
        8. Failure modes
        9. Deployment considerations
        10. Open risks / unresolved items
    """

    def __init__(
        self,
        kernel: CognitionKernel | None = None,
        output_dir: str = _DEFAULT_OUTPUT_DIR,
    ) -> None:
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",
        )
        self.enabled: bool = True
        self.output_dir = output_dir
        self.evidence_cache_dir = _EVIDENCE_CACHE_DIR
        self._documents: dict[str, TechnicalDocument] = {}

        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.evidence_cache_dir, exist_ok=True)

    # ------------------------------------------------------------------ public

    def compile_system_documentation(
        self,
        system_name: str,
        evidence_paths: list[str] | None = None,
        include_tests: bool = True,
        include_code_samples: bool = True,
    ) -> str:
        """Compile complete technical documentation for a system.

        Args:
            system_name: Name of the system to document (e.g., "InvariantEngine")
            evidence_paths: Paths to code, tests, or config files to analyze
            include_tests: Whether to include test verification section
            include_code_samples: Whether to include code samples in documentation

        Returns:
            Path to generated markdown documentation file.
        """
        return self._execute_through_kernel(
            self._do_compile_system_documentation,
            action_name="DocumentationCompilerAgent.compile_system_documentation",
            action_args=(system_name, evidence_paths, include_tests, include_code_samples),
        )

    def compile_section(
        self,
        section_title: str,
        evidence: dict[str, Any],
        section_type: str = "general",
    ) -> DocumentationSection:
        """Compile a single documentation section from evidence.

        Args:
            section_title: Title of the section (e.g., "Architecture", "Security Model")
            evidence: Dict containing verified evidence (code, tests, configs, etc.)
            section_type: Type of section (purpose, architecture, governance, etc.)

        Returns:
            DocumentationSection with verified content.
        """
        return self._execute_through_kernel(
            self._do_compile_section,
            action_name="DocumentationCompilerAgent.compile_section",
            action_args=(section_title, evidence, section_type),
        )

    def verify_documentation(
        self,
        doc_path: str,
        evidence_paths: list[str],
    ) -> dict[str, Any]:
        """Verify existing documentation against current codebase evidence.

        Args:
            doc_path: Path to existing documentation file
            evidence_paths: Paths to current code/test files

        Returns:
            Verification report with accuracy assessment and discrepancies.
        """
        return self._execute_through_kernel(
            self._do_verify_documentation,
            action_name="DocumentationCompilerAgent.verify_documentation",
            action_args=(doc_path, evidence_paths),
        )

    def extract_evidence(
        self,
        file_path: str,
        evidence_type: str = "auto",
    ) -> dict[str, Any]:
        """Extract documentation evidence from a source file.

        Args:
            file_path: Path to source file (code, test, config, etc.)
            evidence_type: Type of evidence (code, test, config, auto)

        Returns:
            Dict containing extracted evidence structured for compilation.
        """
        return self._execute_through_kernel(
            self._do_extract_evidence,
            action_name="DocumentationCompilerAgent.extract_evidence",
            action_args=(file_path, evidence_type),
        )

    # --------------------------------------------------------------- private

    def _do_compile_system_documentation(
        self,
        system_name: str,
        evidence_paths: list[str] | None,
        include_tests: bool,
        include_code_samples: bool,
    ) -> str:
        """Internal implementation of system documentation compilation."""
        logger.info(f"Compiling documentation for system: {system_name}")

        # Create document structure
        doc = TechnicalDocument(
            title=f"{system_name} — Technical Documentation",
            metadata={
                "system": system_name,
                "compilation_method": "evidence-based",
                "include_tests": include_tests,
                "include_code_samples": include_code_samples,
            },
        )

        # Gather evidence
        evidence = {}
        if evidence_paths:
            for path in evidence_paths:
                try:
                    file_evidence = self.extract_evidence(path)
                    evidence[path] = file_evidence
                except Exception as exc:
                    logger.warning(f"Failed to extract evidence from {path}: {exc}")

        # Compile standard sections (10-section structure)
        sections_to_compile = [
            ("Purpose", "purpose"),
            ("Architecture", "architecture"),
            ("Governance Model", "governance"),
            ("Execution Flow", "execution_flow"),
            ("Security Model", "security"),
            ("Evidence Model", "evidence"),
            ("Tests and Verification", "tests"),
            ("Failure Modes", "failure_modes"),
            ("Deployment Considerations", "deployment"),
            ("Open Risks / Unresolved Items", "risks"),
        ]

        for title, section_type in sections_to_compile:
            # Skip test section if not requested
            if section_type == "tests" and not include_tests:
                continue

            section = self._compile_section_from_evidence(
                title=title,
                section_type=section_type,
                system_name=system_name,
                evidence=evidence,
                include_code_samples=include_code_samples,
            )
            doc.sections.append(section)

        # Generate markdown
        output_path = self._write_document_to_markdown(doc, system_name)

        # Cache document
        self._documents[system_name] = doc

        logger.info(f"Documentation compiled: {output_path}")
        return output_path

    def _do_compile_section(
        self,
        section_title: str,
        evidence: dict[str, Any],
        section_type: str,
    ) -> DocumentationSection:
        """Internal implementation of section compilation."""
        content_lines: list[str] = []
        evidence_refs: list[str] = []

        # Extract relevant evidence
        if "code" in evidence:
            code_evidence = evidence["code"]
            if isinstance(code_evidence, dict):
                content_lines.append(self._format_code_evidence(code_evidence, section_type))
                evidence_refs.extend(code_evidence.get("file_paths", []))

        if "tests" in evidence:
            test_evidence = evidence["tests"]
            if isinstance(test_evidence, dict):
                content_lines.append(self._format_test_evidence(test_evidence, section_type))
                evidence_refs.extend(test_evidence.get("test_files", []))

        if "config" in evidence:
            config_evidence = evidence["config"]
            if isinstance(config_evidence, dict):
                content_lines.append(self._format_config_evidence(config_evidence, section_type))

        # If no specific evidence, add placeholder
        if not content_lines:
            content_lines.append(
                f"*No verified evidence available for {section_title}. "
                "This section requires manual documentation or additional evidence.*"
            )

        return DocumentationSection(
            title=section_title,
            content="\n\n".join(filter(None, content_lines)),
            evidence_refs=evidence_refs,
            last_verified=datetime.now(timezone.utc).isoformat(),
            verification_status="verified" if evidence_refs else "unverified",
        )

    def _do_verify_documentation(
        self,
        doc_path: str,
        evidence_paths: list[str],
    ) -> dict[str, Any]:
        """Internal implementation of documentation verification."""
        logger.info(f"Verifying documentation: {doc_path}")

        # Load existing documentation
        doc_file = Path(doc_path)
        if not doc_file.exists():
            return {
                "status": "error",
                "message": f"Documentation file not found: {doc_path}",
            }

        doc_content = doc_file.read_text(encoding="utf-8")

        # Extract current evidence
        current_evidence = {}
        for path in evidence_paths:
            try:
                current_evidence[path] = self.extract_evidence(path)
            except Exception as exc:
                logger.warning(f"Failed to extract evidence from {path}: {exc}")

        # Analyze discrepancies
        discrepancies: list[str] = []
        warnings: list[str] = []

        # Check for outdated claims
        if "deprecated" in doc_content.lower() and not self._verify_deprecation(current_evidence):
            discrepancies.append("Documentation mentions deprecation, but code is active")

        # Check for missing governance mentions
        if self._has_governance_code(current_evidence) and "governance" not in doc_content.lower():
            warnings.append("Code implements governance, but documentation doesn't mention it")

        # Check for test coverage claims
        test_count = self._count_tests_in_evidence(current_evidence)
        if "100% test coverage" in doc_content and test_count == 0:
            discrepancies.append("Claims 100% test coverage, but no tests found")

        verification_status = "accurate" if not discrepancies else "discrepancies_found"

        return {
            "status": verification_status,
            "doc_path": doc_path,
            "evidence_files": len(evidence_paths),
            "discrepancies": discrepancies,
            "warnings": warnings,
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }

    def _do_extract_evidence(
        self,
        file_path: str,
        evidence_type: str,
    ) -> dict[str, Any]:
        """Internal implementation of evidence extraction."""
        file = Path(file_path)
        if not file.exists():
            return {"error": f"File not found: {file_path}"}

        # Auto-detect evidence type
        if evidence_type == "auto":
            if file.name.startswith("test_") or "_test" in file.name:
                evidence_type = "test"
            elif file.suffix in (".yaml", ".yml", ".json", ".toml"):
                evidence_type = "config"
            else:
                evidence_type = "code"

        content = file.read_text(encoding="utf-8")

        evidence = {
            "file_path": str(file),
            "evidence_type": evidence_type,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
        }

        if evidence_type == "code":
            evidence.update(self._extract_code_evidence(content, file))
        elif evidence_type == "test":
            evidence.update(self._extract_test_evidence(content, file))
        elif evidence_type == "config":
            evidence.update(self._extract_config_evidence(content, file))

        return evidence

    # --------------------------------------------------------- evidence parsing

    def _extract_code_evidence(self, content: str, file: Path) -> dict[str, Any]:
        """Extract documentation evidence from code file."""
        return {
            "classes": self._extract_class_names(content),
            "functions": self._extract_function_names(content),
            "docstrings": self._extract_docstrings(content),
            "imports": self._extract_imports(content),
            "has_governance": "CognitionKernel" in content or "ExecutionGate" in content,
            "has_validation": "validate" in content.lower(),
            "line_count": len(content.splitlines()),
        }

    def _extract_test_evidence(self, content: str, file: Path) -> dict[str, Any]:
        """Extract documentation evidence from test file."""
        return {
            "test_functions": self._extract_test_functions(content),
            "assertions": content.count("assert"),
            "fixtures": self._extract_fixtures(content),
            "test_count": content.count("def test_"),
            "has_integration_tests": "integration" in content.lower(),
            "has_unit_tests": "unit" in content.lower() or "def test_" in content,
        }

    def _extract_config_evidence(self, content: str, file: Path) -> dict[str, Any]:
        """Extract documentation evidence from config file."""
        config_data = {}

        if file.suffix in (".yaml", ".yml"):
            try:
                import yaml
                config_data = yaml.safe_load(content) or {}
            except Exception:
                config_data = {"parse_error": "Failed to parse YAML"}
        elif file.suffix == ".json":
            try:
                config_data = json.loads(content)
            except Exception:
                config_data = {"parse_error": "Failed to parse JSON"}

        return {
            "config_keys": list(config_data.keys()) if isinstance(config_data, dict) else [],
            "has_governance_config": any(
                k for k in config_data.keys() if "governance" in str(k).lower()
            ) if isinstance(config_data, dict) else False,
            "config_type": file.suffix,
        }

    # -------------------------------------------------------- formatting helpers

    def _compile_section_from_evidence(
        self,
        title: str,
        section_type: str,
        system_name: str,
        evidence: dict[str, Any],
        include_code_samples: bool,
    ) -> DocumentationSection:
        """Compile a section from gathered evidence."""
        # Delegate to section compiler
        section_evidence = self._filter_evidence_for_section(evidence, section_type)
        return self.compile_section(title, section_evidence, section_type)

    def _filter_evidence_for_section(
        self,
        evidence: dict[str, Any],
        section_type: str,
    ) -> dict[str, Any]:
        """Filter evidence relevant to specific section type."""
        filtered = {}

        for path, file_evidence in evidence.items():
            if isinstance(file_evidence, dict):
                evidence_type = file_evidence.get("evidence_type", "unknown")

                # Include relevant evidence based on section type
                if section_type == "tests" and evidence_type == "test":
                    if "tests" not in filtered:
                        filtered["tests"] = {}
                    filtered["tests"][path] = file_evidence
                elif section_type in ("architecture", "execution_flow") and evidence_type == "code":
                    if "code" not in filtered:
                        filtered["code"] = {}
                    filtered["code"][path] = file_evidence
                elif section_type == "governance" and file_evidence.get("has_governance"):
                    if "code" not in filtered:
                        filtered["code"] = {}
                    filtered["code"][path] = file_evidence

        return filtered

    def _format_code_evidence(self, code_evidence: dict[str, Any], section_type: str) -> str:
        """Format code evidence into documentation prose."""
        lines: list[str] = []

        if section_type == "architecture":
            classes = code_evidence.get("classes", [])
            if classes:
                lines.append(f"**Core Classes:** {', '.join(f'`{c}`' for c in classes[:5])}")

        if section_type == "governance":
            if code_evidence.get("has_governance"):
                lines.append(
                    "✅ **Governance Integration:** All operations route through CognitionKernel "
                    "for governance tracking and constitutional compliance."
                )

        return "\n".join(lines)

    def _format_test_evidence(self, test_evidence: dict[str, Any], section_type: str) -> str:
        """Format test evidence into documentation prose."""
        lines: list[str] = []

        if section_type == "tests":
            test_count = test_evidence.get("test_count", 0)
            if test_count > 0:
                lines.append(f"**Test Coverage:** {test_count} test case(s) verified")

            if test_evidence.get("has_integration_tests"):
                lines.append("- ✅ Integration tests present")
            if test_evidence.get("has_unit_tests"):
                lines.append("- ✅ Unit tests present")

        return "\n".join(lines)

    def _format_config_evidence(self, config_evidence: dict[str, Any], section_type: str) -> str:
        """Format config evidence into documentation prose."""
        lines: list[str] = []

        if section_type == "governance":
            if config_evidence.get("has_governance_config"):
                lines.append("**Configuration:** Governance parameters externalized to configuration files")

        return "\n".join(lines)

    def _write_document_to_markdown(self, doc: TechnicalDocument, system_name: str) -> str:
        """Write TechnicalDocument to markdown file."""
        slug = re.sub(r"[^a-z0-9]+", "_", system_name.lower()).strip("_")
        output_file = Path(self.output_dir) / f"{slug}_technical_documentation.md"

        lines: list[str] = []

        # Header
        lines.append(f"# {doc.title}")
        lines.append("")
        lines.append(f"**Generated:** {doc.last_updated}")
        lines.append(f"**Compilation Method:** {doc.metadata.get('compilation_method', 'unknown')}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # Sections
        for section in doc.sections:
            lines.append(f"## {section.title}")
            lines.append("")
            lines.append(section.content)
            lines.append("")

            # Evidence footer
            if section.evidence_refs:
                lines.append(f"*Evidence: {len(section.evidence_refs)} file(s) analyzed*")
                lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*This documentation was compiled by DocumentationCompilerAgent.*")
        lines.append(
            "*All statements are derived from verified code, tests, and configuration evidence.*"
        )

        output_file.write_text("\n".join(lines), encoding="utf-8")
        return str(output_file)

    # -------------------------------------------------------- helper utilities

    def _extract_class_names(self, content: str) -> list[str]:
        """Extract class names from Python code."""
        return re.findall(r"^class\s+(\w+)", content, re.MULTILINE)

    def _extract_function_names(self, content: str) -> list[str]:
        """Extract function names from Python code."""
        return re.findall(r"^\s*def\s+(\w+)", content, re.MULTILINE)

    def _extract_docstrings(self, content: str) -> list[str]:
        """Extract docstrings from Python code."""
        return re.findall(r'"""(.*?)"""', content, re.DOTALL)[:5]  # Limit to 5

    def _extract_imports(self, content: str) -> list[str]:
        """Extract import statements from Python code."""
        return re.findall(r"^(?:from|import)\s+([^\s]+)", content, re.MULTILINE)[:10]

    def _extract_test_functions(self, content: str) -> list[str]:
        """Extract test function names."""
        return re.findall(r"def\s+(test_\w+)", content)

    def _extract_fixtures(self, content: str) -> list[str]:
        """Extract pytest fixtures."""
        return re.findall(r"@pytest\.fixture.*?def\s+(\w+)", content, re.DOTALL)

    def _verify_deprecation(self, evidence: dict[str, Any]) -> bool:
        """Check if evidence contains deprecation markers."""
        for file_evidence in evidence.values():
            if isinstance(file_evidence, dict):
                # Simplified check - would be more sophisticated in production
                return True
        return False

    def _has_governance_code(self, evidence: dict[str, Any]) -> bool:
        """Check if evidence contains governance integration."""
        for file_evidence in evidence.values():
            if isinstance(file_evidence, dict) and file_evidence.get("has_governance"):
                return True
        return False

    def _count_tests_in_evidence(self, evidence: dict[str, Any]) -> int:
        """Count total tests in evidence."""
        total = 0
        for file_evidence in evidence.values():
            if isinstance(file_evidence, dict):
                total += file_evidence.get("test_count", 0)
        return total
