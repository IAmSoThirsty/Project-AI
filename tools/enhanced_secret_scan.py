#!/usr/bin/env python3
"""
Enhanced Secret Scanner for Project-AI

Scans the entire repository for hardcoded secrets, API keys, passwords,
and other sensitive information.

Usage:
    python tools/enhanced_secret_scan.py [--fix] [--report report.json]

Options:
    --fix           Attempt to fix issues by replacing with env var references
    --report FILE   Output detailed report to JSON file
"""

import argparse
import json
import pathlib
import re
import sys
from typing import Any

# Extended patterns for secret detection
PATTERNS: list[tuple[str, str, str]] = [
    # API Keys
    ("openai_api_key", r"sk-(?:proj-)?[A-Za-z0-9_-]{20,200}", "OpenAI API Key"),
    ("huggingface_token", r"hf_[A-Za-z0-9]{34,}", "Hugging Face Token"),
    ("aws_access_key", r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    ("aws_secret_key", r"aws_secret_access_key\s*=\s*['\"][A-Za-z0-9/+=]{40}['\"]", "AWS Secret Key"),

    # Generic secrets
    ("generic_api_key", r"api[_-]?key\s*[=:]\s*['\"][A-Za-z0-9_-]{20,}['\"]", "Generic API Key"),
    ("bearer_token", r"bearer\s+[A-Za-z0-9_-]{20,}", "Bearer Token"),
    ("auth_token", r"auth[_-]?token\s*[=:]\s*['\"][A-Za-z0-9_-]{20,}['\"]", "Auth Token"),

    # Passwords
    ("password_assignment", r"password\s*[=:]\s*['\"][^'\"]{3,}['\"]", "Hardcoded Password"),
    ("smtp_password", r"SMTP_PASSWORD\s*=\s*['\"]?[^'\"\s]+['\"]?", "SMTP Password"),
    ("db_password", r"(?:DATABASE|DB)_PASSWORD\s*=\s*['\"][^'\"]+['\"]", "Database Password"),

    # Encryption keys
    ("fernet_key", r"FERNET_KEY\s*=\s*['\"]?[A-Za-z0-9+/=]{44}['\"]?", "Fernet Encryption Key"),
    ("jwt_secret", r"JWT_SECRET\s*=\s*['\"][^'\"]{10,}['\"]", "JWT Secret"),
    ("secret_key", r"SECRET_KEY\s*=\s*['\"][^'\"]{10,}['\"]", "Secret Key"),

    # Private keys
    ("rsa_private_key", r"-----BEGIN (?:RSA |)PRIVATE KEY-----", "RSA Private Key"),
    ("ssh_private_key", r"-----BEGIN OPENSSH PRIVATE KEY-----", "SSH Private Key"),
    ("pgp_private_key", r"-----BEGIN PGP PRIVATE KEY BLOCK-----", "PGP Private Key"),

    # Cloud credentials
    ("google_api_key", r"AIza[0-9A-Za-z_-]{35}", "Google API Key"),
    ("github_token", r"gh[pousr]_[A-Za-z0-9]{36,}", "GitHub Token"),
    ("slack_token", r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9]{24,}", "Slack Token"),

    # Connection strings
    ("connection_string", r"(?:mongodb|mysql|postgresql)://[^'\"\s]+:[^'\"\s]+@", "Database Connection String"),
]

# Files to exclude from scanning
EXCLUDE_PATTERNS = [
    r"\.git/",
    r"\.venv/",
    r"venv/",
    r"__pycache__/",
    r"node_modules/",
    r"\.egg-info/",
    r"build/",
    r"dist/",
    r"\.pyc$",
    r"\.min\.js$",
    r"\.lock$",
    r"\.png$",
    r"\.jpg$",
    r"\.gif$",
    r"\.ico$",
]

# Files that are allowed to reference secrets (for documentation)
ALLOWED_FILES = [
    ".env.example",
    "SECRET_MANAGEMENT.md",
    "enhanced_secret_scan.py",
    ".pre-commit-config.yaml",
    "SECURITY.md",
    "DEPLOYMENT.md",
    "SECURITY_FRAMEWORK.md",
    "README.md",
    "secret_scan_report.json",
    "CREDENTIAL_ROTATION.md",
    "SECURITY_REMEDIATION_PLAN.md",
]

# Directories that contain documentation/examples (more lenient checking)
DOCUMENTATION_DIRS = [
    "docs/",
    "examples/",
    ".github/",
]


def should_exclude(file_path: pathlib.Path) -> bool:
    """Check if file should be excluded from scanning."""
    path_str = str(file_path)

    # Check if file is in allowed list
    if file_path.name in ALLOWED_FILES:
        return True

    # Check if in documentation directory (more lenient for examples)
    for doc_dir in DOCUMENTATION_DIRS:
        if doc_dir in path_str:
            # Still scan, but with lenient interpretation
            return False

    # Check exclude patterns
    return any(re.search(pattern, path_str) for pattern in EXCLUDE_PATTERNS)


def scan_file(file_path: pathlib.Path) -> list[dict[str, Any]]:
    """Scan a single file for secrets."""
    findings = []

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")

        for pattern_name, pattern, description in PATTERNS:
            for line_num, line in enumerate(lines, start=1):
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    matched_text = match.group(0)
                    display_text = matched_text[:50] + "..." if len(matched_text) > 50 else matched_text
                    findings.append({
                        "file": str(file_path),
                        "line": line_num,
                        "type": pattern_name,
                        "description": description,
                        "matched_text": display_text,
                        "severity": get_severity(pattern_name),
                    })

    except Exception as e:
        print(f"Error scanning {file_path}: {e}", file=sys.stderr)

    return findings


def get_severity(pattern_name: str) -> str:
    """Determine severity level of finding."""
    critical = ["openai_api_key", "aws_access_key", "aws_secret_key", "rsa_private_key",
                "ssh_private_key", "connection_string"]
    high = ["huggingface_token", "fernet_key", "password_assignment", "bearer_token",
            "github_token", "google_api_key"]

    if pattern_name in critical:
        return "CRITICAL"
    elif pattern_name in high:
        return "HIGH"
    else:
        return "MEDIUM"


def scan_repository(root_path: pathlib.Path) -> list[dict[str, Any]]:
    """Scan entire repository for secrets."""
    all_findings = []

    print(f"Scanning repository: {root_path}")

    for file_path in root_path.rglob("*"):
        if not file_path.is_file():
            continue

        if should_exclude(file_path):
            continue

        findings = scan_file(file_path)
        all_findings.extend(findings)

    return all_findings


def generate_report(findings: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate summary report of findings."""
    report = {
        "total_findings": len(findings),
        "by_severity": {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
        },
        "by_type": {},
        "findings": findings,
    }

    for finding in findings:
        severity = finding["severity"]
        report["by_severity"][severity] += 1

        finding_type = finding["type"]
        if finding_type not in report["by_type"]:
            report["by_type"][finding_type] = 0
        report["by_type"][finding_type] += 1

    return report


def print_report(report: dict[str, Any]) -> None:
    """Print findings report to console."""
    print("\n" + "=" * 80)
    print("SECRET SCAN RESULTS")
    print("=" * 80)

    print(f"\nTotal findings: {report['total_findings']}")
    print(f"  CRITICAL: {report['by_severity']['CRITICAL']}")
    print(f"  HIGH:     {report['by_severity']['HIGH']}")
    print(f"  MEDIUM:   {report['by_severity']['MEDIUM']}")

    if report["total_findings"] == 0:
        print("\n✅ No secrets found! Repository is clean.")
        return

    print("\n" + "-" * 80)
    print("FINDINGS BY TYPE:")
    print("-" * 80)
    for finding_type, count in sorted(report["by_type"].items(), key=lambda x: x[1], reverse=True):
        print(f"  {finding_type}: {count}")

    print("\n" + "-" * 80)
    print("DETAILED FINDINGS:")
    print("-" * 80)

    # Group by severity
    for severity in ["CRITICAL", "HIGH", "MEDIUM"]:
        severity_findings = [f for f in report["findings"] if f["severity"] == severity]
        if not severity_findings:
            continue

        print(f"\n{severity} SEVERITY:")
        for finding in severity_findings[:20]:  # Limit to first 20 per severity
            print(f"\n  File: {finding['file']}")
            print(f"  Line: {finding['line']}")
            print(f"  Type: {finding['description']}")
            print(f"  Match: {finding['matched_text']}")

    if report["total_findings"] > 60:
        print(f"\n... and {report['total_findings'] - 60} more findings")


def main():
    parser = argparse.ArgumentParser(description="Enhanced secret scanner for Project-AI")
    parser.add_argument("--report", help="Output JSON report to file")
    parser.add_argument("--root", default=".", help="Root directory to scan")
    args = parser.parse_args()

    root_path = pathlib.Path(args.root).resolve()

    if not root_path.exists():
        print(f"Error: Path {root_path} does not exist", file=sys.stderr)
        return 1

    # Scan repository
    findings = scan_repository(root_path)

    # Generate report
    report = generate_report(findings)

    # Print to console
    print_report(report)

    # Save to file if requested
    if args.report:
        report_path = pathlib.Path(args.report)
        report_path.write_text(json.dumps(report, indent=2))
        print(f"\n📄 Detailed report saved to: {args.report}")

    # Exit with error code if secrets found
    if report["by_severity"]["CRITICAL"] > 0:
        print("\n❌ CRITICAL secrets found! Immediate action required.")
        return 2
    elif report["by_severity"]["HIGH"] > 0:
        print("\n⚠️  HIGH severity secrets found! Please review and remediate.")
        return 1
    elif report["total_findings"] > 0:
        print("\n⚠️  Secrets found. Please review findings.")
        return 1

    print("\n✅ Secret scan passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
