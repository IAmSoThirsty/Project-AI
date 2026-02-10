#!/usr/bin/env python3
"""
SARIF Exporter Utility

Converts JailbreakBench, CodeAdversary, and RedTeamPersona findings
into SARIF 2.1.0 format for GitHub Security integration.

Usage:
    python sarif_exporter.py --findings findings.json --output report.sarif
    python sarif_exporter.py --jailbreak-bench results.json
    python sarif_exporter.py --code-adversary scan.json

Integration:
    1. Call after each JailbreakBench or CodeAdversary run
    2. Upload resulting SARIF to GitHub Security
    3. Use level=error findings to drive deployment gates

Author: Security Agents Team
Date: 2026-01-21
"""

import argparse
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


def convert_findings_to_sarif(
    findings: list[dict[str, Any]],
    tool_name: str = "Project-AI-Security",
    tool_uri: str = "https://project-ai/docs/security_agents",
) -> dict[str, Any]:
    """
    Convert a list of findings into SARIF 2.1.0 structure.

    Args:
        findings: List of dicts with keys:
            - id: Finding identifier
            - rule_id: Rule identifier (e.g., "JBB-001")
            - rule_name: Human-readable rule name
            - rule_description: Full rule description
            - level: 'error'|'warning'|'note'
            - message: Finding message
            - artifact_uri: File/artifact URI
            - start_line: Line number
            - persona: Attack persona (optional)
            - attack_vector: Attack method (optional)
            - transcript_id: Transcript identifier (optional)
            - confidence: Confidence level 0.0-1.0
            - repro_steps: List of reproduction steps
            - evidence: Evidence/proof string
        tool_name: Tool name for SARIF
        tool_uri: Tool information URI

    Returns:
        SARIF JSON as dict
    """
    run_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat() + "Z"

    rules = {}
    results = []

    for f in findings:
        rule_key = f.get("rule_id", "JBB-UNKNOWN")

        # Build rule definition (deduplicate)
        if rule_key not in rules:
            rules[rule_key] = {
                "id": rule_key,
                "name": f.get("rule_name", rule_key),
                "shortDescription": {"text": f.get("rule_name", rule_key)},
                "fullDescription": {"text": f.get("rule_description", "")},
                "helpUri": f.get("help_uri", f"{tool_uri}#{rule_key.lower()}"),
            }

        # Build result
        result = {
            "ruleId": rule_key,
            "level": f.get("level", "warning"),
            "message": {"text": f.get("message", "")},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": f.get("artifact_uri", "workspace://unknown")
                        },
                        "region": {"startLine": f.get("start_line", 1)},
                    }
                }
            ],
            "properties": {
                "persona": f.get("persona"),
                "attack_vector": f.get("attack_vector"),
                "transcript_id": f.get("transcript_id"),
                "confidence": f.get("confidence", 0.0),
                "repro_steps": f.get("repro_steps", []),
                "evidence": f.get("evidence", ""),
            },
        }
        results.append(result)

    # Build SARIF document
    sarif = {
        "version": "2.1.0",
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": tool_name,
                        "informationUri": tool_uri,
                        "rules": list(rules.values()),
                    }
                },
                "results": results,
                "properties": {"exportedAt": now, "runId": run_id},
            }
        ],
    }

    return sarif


def convert_jailbreak_bench_results(results_file: str) -> dict[str, Any]:
    """
    Convert JailbreakBench results to SARIF format.

    Args:
        results_file: Path to JailbreakBench results JSON

    Returns:
        SARIF report
    """
    with open(results_file) as f:
        results = json.load(f)

    findings = []

    # Extract findings from results
    for test_result in results.get("results", []):
        if test_result.get("success", False):  # Only report successful jailbreaks
            findings.append(
                {
                    "id": test_result.get("test_id", "unknown"),
                    "rule_id": "JBB-001",  # Prompt injection
                    "rule_name": "PromptInjection",
                    "rule_description": "User-controlled input can alter system instructions.",
                    "level": "error",
                    "message": f"Jailbreak succeeded: {test_result.get('attack_category', 'unknown')} attack",
                    "artifact_uri": f"workspace://flows/{test_result.get('target', 'unknown')}_flow.yaml",
                    "start_line": 1,
                    "persona": test_result.get("persona", "unknown"),
                    "attack_vector": test_result.get("attack_vector", "unknown"),
                    "transcript_id": test_result.get("transcript_id", ""),
                    "confidence": 0.95,
                    "repro_steps": test_result.get("repro_steps", []),
                    "evidence": f"transcript_id: {test_result.get('transcript_id', '')}",
                }
            )

    return convert_findings_to_sarif(findings)


def convert_code_adversary_results(results_file: str) -> dict[str, Any]:
    """
    Convert CodeAdversary scan results to SARIF format.

    Args:
        results_file: Path to CodeAdversary scan results JSON

    Returns:
        SARIF report
    """
    with open(results_file) as f:
        results = json.load(f)

    findings = []

    # Extract findings from scan results
    for vuln in results.get("findings", []):
        findings.append(
            {
                "id": vuln.get("id", "unknown"),
                "rule_id": vuln["type"].upper(),
                "rule_name": vuln["type"],
                "rule_description": vuln.get("description", ""),
                "level": (
                    "error"
                    if vuln.get("severity") in ["critical", "high"]
                    else "warning"
                ),
                "message": vuln.get("description", ""),
                "artifact_uri": vuln.get("file", "unknown"),
                "start_line": vuln.get("line", 1),
                "confidence": vuln.get("confidence", 0.9),
                "repro_steps": [],
                "evidence": vuln.get("code_snippet", ""),
            }
        )

    return convert_findings_to_sarif(findings, tool_name="Project-AI-CodeAdversary")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Convert security findings to SARIF format"
    )
    parser.add_argument("--findings", help="Generic findings JSON file")
    parser.add_argument("--jailbreak-bench", help="JailbreakBench results JSON file")
    parser.add_argument("--code-adversary", help="CodeAdversary scan results JSON file")
    parser.add_argument("--output", "-o", help="Output SARIF file (default: stdout)")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")

    args = parser.parse_args()

    # Determine conversion method
    if args.findings:
        with open(args.findings) as f:
            findings = json.load(f)
        sarif = convert_findings_to_sarif(findings)
    elif args.jailbreak_bench:
        sarif = convert_jailbreak_bench_results(args.jailbreak_bench)
    elif args.code_adversary:
        sarif = convert_code_adversary_results(args.code_adversary)
    else:
        parser.error("Must specify --findings, --jailbreak-bench, or --code-adversary")

    # Output SARIF
    indent = 2 if args.pretty else None
    sarif_json = json.dumps(sarif, indent=indent)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(sarif_json)
        print(f"SARIF report written to {output_path}")
    else:
        print(sarif_json)


# Example usage
if __name__ == "__main__":
    # If run directly without arguments, show example
    import sys

    if len(sys.argv) == 1:
        print("SARIF Exporter - Example Usage\n")

        sample_findings = [
            {
                "id": "f1",
                "rule_id": "JBB-001",
                "rule_name": "PromptInjection",
                "rule_description": "User-controlled input can alter system instructions.",
                "level": "error",
                "message": "Prompt injection succeeded against flow /api/assistant",
                "artifact_uri": "workspace://flows/assistant_flow.yaml",
                "start_line": 1,
                "persona": "jailbreak_attacker",
                "attack_vector": "role_confusion -> system_message_override",
                "transcript_id": "abc123",
                "confidence": 0.95,
                "repro_steps": [
                    "Step 1: send payload X",
                    "Step 2: escalate with encoded prompt Y",
                ],
                "evidence": "transcript_id: abc123",
            }
        ]

        sarif = convert_findings_to_sarif(sample_findings)
        print(json.dumps(sarif, indent=2))

        print("\n\nUsage Examples:")
        print(
            "  python sarif_exporter.py --findings findings.json --output report.sarif"
        )
        print("  python sarif_exporter.py --jailbreak-bench results.json --pretty")
        print("  python sarif_exporter.py --code-adversary scan.json -o scan.sarif")
    else:
        main()
