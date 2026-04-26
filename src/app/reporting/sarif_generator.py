"""
SARIF Report Generator for Security Agents

Generates standardized SARIF (Static Analysis Results Interchange Format) reports
for JailbreakBench, CodeAdversary, and RedTeamPersona findings.

Integrates with GitHub Security and SCA tooling.

Author: Security Agents Team
Date: 2026-01-21
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class SARIFGenerator:
    """Generates SARIF 2.1.0 format reports."""

    def __init__(self):
        """Initialize SARIF generator."""
        self.version = "2.1.0"
        self.tool_name = "Project-AI-Security"
        self.tool_uri = "https://project-ai/docs/security_agents"

    def generate_jailbreak_report(
        self, findings: list[dict[str, Any]], campaign_id: str
    ) -> dict[str, Any]:
        """
        Generate SARIF report for jailbreak findings.

        Args:
            findings: List of jailbreak test results
            campaign_id: Red team campaign identifier

        Returns:
            SARIF format report matching GitHub Security requirements
        """
        rules = self._get_jailbreak_rules()
        results = []

        for finding in findings:
            if finding.get("success", False):  # Only report successful jailbreaks
                results.append(
                    {
                        "ruleId": self._get_jailbreak_rule_id(
                            finding["attack_category"]
                        ),
                        "level": self._map_severity_to_level(
                            finding.get("severity", "high")
                        ),
                        "message": {
                            "text": f"Prompt injection succeeded against flow {finding['target']} with persona {finding.get('persona', 'unknown')}"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": finding.get(
                                            "target_file",
                                            f"workspace://flows/{finding['target']}_flow.yaml",
                                        )
                                    },
                                    "region": {
                                        "startLine": finding.get("line_number", 1)
                                    },
                                }
                            }
                        ],
                        "properties": {
                            "persona": finding.get("persona", "unknown"),
                            "attack_vector": finding.get("attack_vector", "unknown"),
                            "repro_steps": finding.get(
                                "repro_steps",
                                [
                                    "Step 1: send initial payload",
                                    "Step 2: escalate with follow-up",
                                ],
                            ),
                            "evidence": f"transcript_id: {finding.get('transcript_id', 'unknown')}",
                            "confidence": finding.get("confidence", 0.95),
                        },
                    }
                )

        return self._create_sarif_document(rules, results, "JailbreakBench")

    def generate_code_vulnerability_report(
        self, findings: list[dict[str, Any]], scan_id: str
    ) -> dict[str, Any]:
        """
        Generate SARIF report for code vulnerabilities.

        Args:
            findings: List of vulnerability findings
            scan_id: Security scan identifier

        Returns:
            SARIF format report
        """
        rules = self._get_code_vulnerability_rules()
        results = []

        for finding in findings:
            results.append(
                {
                    "ruleId": finding["type"].upper(),
                    "level": self._map_severity_to_level(
                        finding.get("severity", "medium")
                    ),
                    "message": {"text": finding["description"]},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": finding["file"]},
                                "region": {
                                    "startLine": finding["line"],
                                    "snippet": {
                                        "text": finding.get("code_snippet", "")
                                    },
                                },
                            }
                        }
                    ],
                    "fixes": (
                        self._generate_fixes(finding)
                        if finding.get("suggested_fix")
                        else []
                    ),
                    "properties": {
                        "vulnerability_type": finding["type"],
                        "cwe_id": finding.get("cwe_id", ""),
                        "cvss_score": finding.get("cvss_score", 0.0),
                        "confidence": finding.get("confidence", 0.9),
                        "scan_id": scan_id,
                        "timestamp": finding.get(
                            "timestamp", datetime.now().isoformat()
                        ),
                    },
                }
            )

        return self._create_sarif_document(rules, results, "CodeAdversary")

    def generate_red_team_report(
        self, sessions: list[dict[str, Any]], campaign_id: str
    ) -> dict[str, Any]:
        """
        Generate SARIF report for red team persona attacks.

        Args:
            sessions: List of attack session results
            campaign_id: Campaign identifier

        Returns:
            SARIF format report
        """
        rules = self._get_red_team_rules()
        results = []

        for session in sessions:
            if session.get("success", False):
                results.append(
                    {
                        "ruleId": f"RTP-{session['persona_id'].upper()}",
                        "level": self._map_severity_to_level(
                            session.get("severity", "high")
                        ),
                        "message": {
                            "text": f"Red team attack succeeded: {session['persona_id']} on {session['target']}"
                        },
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": session.get(
                                            "target_uri", "workspace://system"
                                        )
                                    },
                                    "region": {"startLine": 1},
                                }
                            }
                        ],
                        "properties": {
                            "persona": session["persona_id"],
                            "attack_vector": " -> ".join(session.get("tactics", [])),
                            "repro_steps": self._extract_repro_steps(
                                session["conversation"]
                            ),
                            "evidence": f"session_id: {session.get('session_id', '')}",
                            "confidence": session.get("confidence", 0.95),
                        },
                    }
                )

        return self._create_sarif_document(rules, results, "RedTeamPersona")

    def _create_sarif_document(
        self,
        rules: list[dict[str, Any]],
        results: list[dict[str, Any]],
        tool_component: str,
    ) -> dict[str, Any]:
        """Create complete SARIF document."""
        return {
            "version": self.version,
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": self.tool_name,
                            "informationUri": self.tool_uri,
                            "version": "1.3.0",
                            "semanticVersion": "1.3.0",
                            "component": tool_component,
                            "rules": rules,
                        }
                    },
                    "results": results,
                    "invocations": [
                        {
                            "executionSuccessful": True,
                            "endTimeUtc": datetime.now().isoformat() + "Z",
                        }
                    ],
                }
            ],
        }

    def _get_jailbreak_rules(self) -> list[dict[str, Any]]:
        """Get rule definitions for jailbreak attacks."""
        return [
            {
                "id": "JBB-001",
                "name": "PromptInjection",
                "shortDescription": {"text": "Prompt injection vulnerability"},
                "fullDescription": {
                    "text": "User-controlled input can alter system instructions."
                },
                "helpUri": f"{self.tool_uri}/jailbreakbench#prompt-injection",
            },
            {
                "id": "JBB-002",
                "name": "RoleConfusion",
                "shortDescription": {"text": "Role confusion attack"},
                "fullDescription": {
                    "text": "Attacker can assume privileged roles through prompt manipulation."
                },
                "helpUri": f"{self.tool_uri}/jailbreakbench#role-confusion",
            },
            {
                "id": "JBB-003",
                "name": "HypotheticalScenario",
                "shortDescription": {"text": "Hypothetical framing bypass"},
                "fullDescription": {
                    "text": "Safety guardrails bypassed through hypothetical scenario framing."
                },
                "helpUri": f"{self.tool_uri}/jailbreakbench#hypothetical",
            },
            {
                "id": "JBB-004",
                "name": "EncodingAttack",
                "shortDescription": {"text": "Encoding-based bypass"},
                "fullDescription": {
                    "text": "Content filters bypassed through encoding (base64, ROT13, etc.)."
                },
                "helpUri": f"{self.tool_uri}/jailbreakbench#encoding",
            },
        ]

    def _get_code_vulnerability_rules(self) -> list[dict[str, Any]]:
        """Get rule definitions for code vulnerabilities."""
        return [
            {
                "id": "SQL_INJECTION",
                "name": "SQLInjection",
                "shortDescription": {"text": "SQL injection vulnerability"},
                "fullDescription": {"text": "Unsanitized user input in SQL query."},
                "helpUri": f"{self.tool_uri}/code_adversary#sql-injection",
            },
            {
                "id": "COMMAND_INJECTION",
                "name": "CommandInjection",
                "shortDescription": {"text": "Command injection vulnerability"},
                "fullDescription": {
                    "text": "Unsanitized user input in system command."
                },
                "helpUri": f"{self.tool_uri}/code_adversary#command-injection",
            },
            {
                "id": "HARDCODED_SECRET",
                "name": "HardcodedSecret",
                "shortDescription": {"text": "Hardcoded secret detected"},
                "fullDescription": {
                    "text": "API key, password, or token hardcoded in source."
                },
                "helpUri": f"{self.tool_uri}/code_adversary#hardcoded-secrets",
            },
        ]

    def _get_red_team_rules(self) -> list[dict[str, Any]]:
        """Get rule definitions for red team personas."""
        return [
            {
                "id": "RTP-JAILBREAK_ATTACKER",
                "name": "JailbreakAttackerSuccess",
                "shortDescription": {"text": "Jailbreak attacker succeeded"},
                "fullDescription": {
                    "text": "Safety constraints bypassed by jailbreak_attacker persona."
                },
                "helpUri": f"{self.tool_uri}/red_team_persona#jailbreak-attacker",
            },
            {
                "id": "RTP-DATA_EXFILTRATOR",
                "name": "DataExfiltratorSuccess",
                "shortDescription": {"text": "Data exfiltrator succeeded"},
                "fullDescription": {
                    "text": "Sensitive data extracted by data_exfiltrator persona."
                },
                "helpUri": f"{self.tool_uri}/red_team_persona#data-exfiltrator",
            },
        ]

    def _get_jailbreak_rule_id(self, attack_category: str) -> str:
        """Map attack category to rule ID."""
        mapping = {
            "prompt_injection": "JBB-001",
            "role_confusion": "JBB-002",
            "hypothetical": "JBB-003",
            "encoding": "JBB-004",
        }
        return mapping.get(attack_category.lower(), "JBB-001")

    def _map_severity_to_level(self, severity: str) -> str:
        """Map severity string to SARIF level."""
        mapping = {
            "critical": "error",
            "high": "error",
            "medium": "warning",
            "low": "note",
        }
        return mapping.get(severity.lower(), "warning")

    def _generate_fixes(self, finding: dict[str, Any]) -> list[dict[str, Any]]:
        """Generate fix suggestions in SARIF format."""
        if not finding.get("suggested_fix"):
            return []

        return [
            {
                "description": {"text": f"Apply security fix for {finding['type']}"},
                "artifactChanges": [
                    {
                        "artifactLocation": {"uri": finding["file"]},
                        "replacements": [
                            {
                                "deletedRegion": {
                                    "startLine": finding["line"],
                                    "endLine": finding["line"],
                                },
                                "insertedContent": {"text": finding["suggested_fix"]},
                            }
                        ],
                    }
                ],
            }
        ]

    def _extract_repro_steps(self, conversation: list[dict[str, str]]) -> list[str]:
        """Extract reproduction steps from conversation."""
        steps = []
        for i, turn in enumerate(conversation, 1):
            if turn.get("role") == "attacker":
                steps.append(f"Step {i}: {turn['content'][:80]}...")
        return steps[:5]  # First 5 steps

    def save_report(self, report: dict[str, Any], output_path: str):
        """Save SARIF report to file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

    def upload_to_github(self, report: dict[str, Any], repo: str, commit_sha: str):
        """
        Upload SARIF report to GitHub Security.

        Args:
            report: SARIF report
            repo: Repository (owner/name)
            commit_sha: Commit SHA for the report
        """
        import base64
        import os

        import requests

        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable required")

        # Save report temporarily using secure temp file
        import tempfile

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as temp_file:
            temp_filename = temp_file.name
            json.dump(report, temp_file, indent=2)

        try:
            # Upload via GitHub API
            url = f"https://api.github.com/repos/{repo}/code-scanning/sarifs"
            headers = {
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
            }

            with open(temp_filename) as f:
                sarif_content = f.read()

            sarif_b64 = base64.b64encode(sarif_content.encode()).decode()

            data = {
                "commit_sha": commit_sha,
                "ref": "refs/heads/main",
                "sarif": sarif_b64,
                "tool_name": self.tool_name,
            }

            # Add timeout to prevent hanging
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()

            return response.json()
        finally:
            # Clean up temp file
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
