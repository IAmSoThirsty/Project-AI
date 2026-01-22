"""Code Adversary Agent - DARPA-grade MUSE-style vulnerability finder.

This agent performs automated security code review, vulnerability detection,
and patch generation for the codebase.

Features:
- Static code analysis for security vulnerabilities
- Pattern-based vulnerability detection
- Automated patch generation
- Integration with CI/CD workflows
- SARIF report generation
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class VulnerabilityType(Enum):
    """Types of security vulnerabilities."""

    SQL_INJECTION = "sql_injection"
    XSS = "cross_site_scripting"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    UNSAFE_DESERIALIZATION = "unsafe_deserialization"
    HARDCODED_SECRET = "hardcoded_secret"
    WEAK_CRYPTO = "weak_cryptography"
    INSECURE_RANDOMNESS = "insecure_randomness"
    AUTHENTICATION_BYPASS = "authentication_bypass"
    AUTHORIZATION_FLAW = "authorization_flaw"
    SENSITIVE_DATA_EXPOSURE = "sensitive_data_exposure"
    UNSAFE_REFLECTION = "unsafe_reflection"


class Severity(Enum):
    """Vulnerability severity levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    """A security vulnerability finding."""

    id: str
    type: str
    severity: str
    title: str
    description: str
    file_path: str
    line_number: int
    code_snippet: str
    recommendation: str
    cwe_id: str | None
    timestamp: str


@dataclass
class Patch:
    """A suggested security patch."""

    finding_id: str
    file_path: str
    line_number: int
    original_code: str
    patched_code: str
    rationale: str
    timestamp: str


class CodeAdversaryAgent(KernelRoutedAgent):
    """Agent for automated security code review and vulnerability detection.

    Performs DARPA-grade MUSE-style adversarial code analysis to find
    and fix security vulnerabilities before attackers do.

    All operations are routed through CognitionKernel for governance.
    """

    def __init__(
        self,
        repo_path: str = ".",
        scope_dirs: list[str] | None = None,
        kernel: CognitionKernel | None = None,
    ) -> None:
        """Initialize the code adversary agent.

        Args:
            repo_path: Path to repository root
            scope_dirs: Directories to scan (defaults to security-critical)
            kernel: CognitionKernel instance for routing operations
        """
        # Initialize kernel routing
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="high",  # Code security is high priority
        )

        self.repo_path = Path(repo_path)
        self.scope_dirs = scope_dirs or [
            "src/app/core",
            "src/app/agents",
            "src/app/security",
        ]

        # Statistics
        self.total_scans = 0
        self.vulnerabilities_found = 0
        self.patches_generated = 0

        # Vulnerability patterns
        self.patterns = self._initialize_patterns()

        logger.info(
            "CodeAdversaryAgent initialized: repo=%s, scope=%s",
            repo_path,
            self.scope_dirs,
        )

    def find_vulnerabilities(
        self,
        scope_files: list[str] | None = None,
    ) -> dict[str, Any]:
        """Find security vulnerabilities in codebase.

        This method is routed through CognitionKernel for governance approval.

        Args:
            scope_files: Specific files to scan (uses scope_dirs if None)

        Returns:
            Dictionary with findings
        """
        return self._execute_through_kernel(
            action=self._do_find_vulnerabilities,
            action_name="CodeAdversaryAgent.find_vulnerabilities",
            action_args=(scope_files,),
            requires_approval=True,
            risk_level="medium",
            metadata={
                "scan_type": "vulnerability_detection",
            },
        )

    def _do_find_vulnerabilities(
        self,
        scope_files: list[str] | None,
    ) -> dict[str, Any]:
        """Internal implementation of vulnerability finding."""
        try:
            self.total_scans += 1

            # Get files to scan
            files_to_scan = self._get_files_to_scan(scope_files)

            # Scan each file
            findings: list[Finding] = []
            for file_path in files_to_scan:
                file_findings = self._scan_file(file_path)
                findings.extend(file_findings)

            self.vulnerabilities_found += len(findings)

            # Group by severity
            by_severity = {
                "critical": [],
                "high": [],
                "medium": [],
                "low": [],
                "info": [],
            }
            for finding in findings:
                by_severity[finding.severity].append(finding)

            return {
                "success": True,
                "total_findings": len(findings),
                "by_severity": {k: len(v) for k, v in by_severity.items()},
                "findings": [asdict(f) for f in findings],
                "timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error("Error finding vulnerabilities: %s", e)
            return {"success": False, "error": str(e)}

    def propose_patches(
        self,
        findings: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Generate security patches for findings.

        This method is routed through CognitionKernel for governance approval.

        Args:
            findings: List of finding dictionaries

        Returns:
            Dictionary with proposed patches
        """
        return self._execute_through_kernel(
            action=self._do_propose_patches,
            action_name="CodeAdversaryAgent.propose_patches",
            action_args=(findings,),
            requires_approval=True,
            risk_level="high",  # Code changes are high risk
            metadata={
                "finding_count": len(findings),
            },
        )

    def _do_propose_patches(
        self,
        findings: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Internal implementation of patch generation."""
        try:
            patches: list[Patch] = []

            for finding in findings:
                patch = self._generate_patch(finding)
                if patch:
                    patches.append(patch)

            self.patches_generated += len(patches)

            return {
                "success": True,
                "total_patches": len(patches),
                "patches": [asdict(p) for p in patches],
                "timestamp": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error("Error proposing patches: %s", e)
            return {"success": False, "error": str(e)}

    def generate_sarif_report(
        self,
        findings: list[dict[str, Any]],
        output_path: str | None = None,
    ) -> dict[str, Any]:
        """Generate SARIF format report for findings.

        Args:
            findings: List of findings to report
            output_path: Optional output file path

        Returns:
            Dictionary with SARIF report
        """
        try:
            sarif = {
                "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
                "version": "2.1.0",
                "runs": [
                    {
                        "tool": {
                            "driver": {
                                "name": "CodeAdversaryAgent",
                                "version": "1.0.0",
                                "informationUri": "https://github.com/IAmSoThirsty/Project-AI",
                            }
                        },
                        "results": [self._finding_to_sarif(f) for f in findings],
                    }
                ],
            }

            if output_path:
                with open(output_path, "w") as f:
                    json.dump(sarif, f, indent=2)

            return {"success": True, "sarif": sarif}

        except Exception as e:
            logger.error("Error generating SARIF report: %s", e)
            return {"success": False, "error": str(e)}

    def get_statistics(self) -> dict[str, Any]:
        """Get code adversary statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_scans": self.total_scans,
            "vulnerabilities_found": self.vulnerabilities_found,
            "patches_generated": self.patches_generated,
            "repo_path": str(self.repo_path),
            "scope_dirs": self.scope_dirs,
        }

    def _initialize_patterns(self) -> dict[str, dict[str, Any]]:
        """Initialize vulnerability detection patterns.

        Returns:
            Dictionary of patterns by vulnerability type
        """
        return {
            VulnerabilityType.HARDCODED_SECRET.value: {
                "patterns": [
                    r'["\']?api[_-]?key["\']?\s*[:=]\s*["\'][^"\']{20,}["\']',
                    r'["\']?password["\']?\s*[:=]\s*["\'][^"\']+["\']',
                    r'["\']?secret["\']?\s*[:=]\s*["\'][^"\']{20,}["\']',
                    r'["\']?token["\']?\s*[:=]\s*["\'][^"\']{20,}["\']',
                ],
                "severity": Severity.CRITICAL.value,
                "cwe": "CWE-798",
            },
            VulnerabilityType.SQL_INJECTION.value: {
                "patterns": [
                    r'execute\s*\(\s*["\'].*%s.*["\']',
                    r'cursor\.execute\s*\(\s*f["\']',
                    r'\.query\s*\(\s*["\'].*\+',
                ],
                "severity": Severity.CRITICAL.value,
                "cwe": "CWE-89",
            },
            VulnerabilityType.COMMAND_INJECTION.value: {
                "patterns": [
                    r"os\.system\s*\(",
                    r"subprocess\..*shell\s*=\s*True",
                    r"eval\s*\(",
                    r"exec\s*\(",
                ],
                "severity": Severity.CRITICAL.value,
                "cwe": "CWE-78",
            },
            VulnerabilityType.PATH_TRAVERSAL.value: {
                "patterns": [
                    r"open\s*\([^)]*\+",
                    r"Path\s*\([^)]*\+",
                    r"\.\./",
                ],
                "severity": Severity.HIGH.value,
                "cwe": "CWE-22",
            },
            VulnerabilityType.UNSAFE_DESERIALIZATION.value: {
                "patterns": [
                    r"pickle\.loads?\s*\(",
                    r"yaml\.load\s*\([^,)]*\)",
                    r"json\.loads?\s*\([^,)]*untrusted",
                ],
                "severity": Severity.CRITICAL.value,
                "cwe": "CWE-502",
            },
        }

    def _get_files_to_scan(self, scope_files: list[str] | None) -> list[Path]:
        """Get list of files to scan.

        Args:
            scope_files: Specific files or None for all in scope_dirs

        Returns:
            List of file paths
        """
        if scope_files:
            return [Path(f) for f in scope_files]

        files = []
        for scope_dir in self.scope_dirs:
            dir_path = self.repo_path / scope_dir
            if dir_path.exists():
                files.extend(dir_path.rglob("*.py"))

        return files

    def _scan_file(self, file_path: Path) -> list[Finding]:
        """Scan a single file for vulnerabilities.

        Args:
            file_path: Path to file

        Returns:
            List of findings
        """
        findings = []

        try:
            with open(file_path) as f:
                content = f.read()
                lines = content.split("\n")

            # Check each pattern
            for vuln_type, pattern_info in self.patterns.items():
                for pattern in pattern_info["patterns"]:
                    for line_num, line in enumerate(lines, 1):
                        if re.search(pattern, line, re.IGNORECASE):
                            finding = Finding(
                                id=f"{file_path.name}_{line_num}_{vuln_type}",
                                type=vuln_type,
                                severity=pattern_info["severity"],
                                title=f"{vuln_type.replace('_', ' ').title()} detected",
                                description=f"Potential {vuln_type} vulnerability found",
                                file_path=str(file_path.relative_to(self.repo_path)),
                                line_number=line_num,
                                code_snippet=line.strip(),
                                recommendation=self._get_recommendation(vuln_type),
                                cwe_id=pattern_info.get("cwe"),
                                timestamp=datetime.now(UTC).isoformat(),
                            )
                            findings.append(finding)

        except Exception as e:
            logger.error("Error scanning file %s: %s", file_path, e)

        return findings

    def _get_recommendation(self, vuln_type: str) -> str:
        """Get remediation recommendation for vulnerability type.

        Args:
            vuln_type: Vulnerability type

        Returns:
            Recommendation string
        """
        recommendations = {
            VulnerabilityType.HARDCODED_SECRET.value: "Use environment variables or secure secret management",
            VulnerabilityType.SQL_INJECTION.value: "Use parameterized queries or ORM",
            VulnerabilityType.COMMAND_INJECTION.value: "Avoid shell=True, use subprocess with list args",
            VulnerabilityType.PATH_TRAVERSAL.value: "Validate and sanitize file paths",
            VulnerabilityType.UNSAFE_DESERIALIZATION.value: "Use safe deserializers (yaml.safe_load)",
        }
        return recommendations.get(vuln_type, "Review and fix security issue")

    def _generate_patch(self, finding: dict[str, Any]) -> Patch | None:
        """Generate a patch for a finding.

        Args:
            finding: Finding dictionary

        Returns:
            Patch object or None
        """
        # Simplified patch generation
        # In production, this would use more sophisticated analysis

        vuln_type = finding.get("type")
        original_code = finding.get("code_snippet", "")

        if vuln_type == VulnerabilityType.HARDCODED_SECRET.value:
            # Replace hardcoded secret with environment variable
            patched_code = re.sub(
                r'["\'][^"\']{20,}["\']',
                'os.getenv("SECRET_KEY")',
                original_code,
            )
            if patched_code != original_code:
                return Patch(
                    finding_id=finding.get("id", "unknown"),
                    file_path=finding.get("file_path", ""),
                    line_number=finding.get("line_number", 0),
                    original_code=original_code,
                    patched_code=patched_code,
                    rationale="Replaced hardcoded secret with environment variable",
                    timestamp=datetime.now(UTC).isoformat(),
                )

        return None

    def _finding_to_sarif(self, finding: dict[str, Any]) -> dict[str, Any]:
        """Convert finding to SARIF result format.

        Args:
            finding: Finding dictionary

        Returns:
            SARIF result dictionary
        """
        return {
            "ruleId": finding.get("type", "unknown"),
            "level": self._severity_to_sarif_level(finding.get("severity", "info")),
            "message": {
                "text": finding.get("description", ""),
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": finding.get("file_path", ""),
                        },
                        "region": {
                            "startLine": finding.get("line_number", 1),
                        },
                    }
                }
            ],
        }

    def _severity_to_sarif_level(self, severity: str) -> str:
        """Convert severity to SARIF level.

        Args:
            severity: Severity string

        Returns:
            SARIF level string
        """
        mapping = {
            "critical": "error",
            "high": "error",
            "medium": "warning",
            "low": "note",
            "info": "note",
        }
        return mapping.get(severity, "warning")
