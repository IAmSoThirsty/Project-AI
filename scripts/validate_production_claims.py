#!/usr/bin/env python3
"""
Security Validation Claims Checker

Scans documentation files for prohibited production claims per
.github/SECURITY_VALIDATION_POLICY.md

Usage:
    python scripts/validate_production_claims.py [files...]
    python scripts/validate_production_claims.py docs/whitepapers/*.md
    python scripts/validate_production_claims.py --all

Exit codes:
    0 - No violations found
    1 - Violations found
    2 - Script error
"""

import argparse
import glob
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# Prohibited claim patterns from SECURITY_VALIDATION_POLICY.md
PROHIBITED_PATTERNS = {
    "production_ready": {
        "pattern": r"production[\s-]ready",
        "description": '"Production-ready" claims',
        "severity": "HIGH",
    },
    "enterprise_best_practices": {
        "pattern": r"enterprise[\s-](?:best[\s-]practices|grade)",
        "description": '"Enterprise best practices" or "Enterprise-grade" claims',
        "severity": "HIGH",
    },
    "complete_forensic": {
        "pattern": r"(?:complete|full)[\s-]forensic[\s-](?:capability|trail|audit)",
        "description": '"Complete forensic capability" claims',
        "severity": "HIGH",
    },
    "runtime_enforcement": {
        "pattern": r"runtime[\s-]enforcement",
        "description": '"Runtime enforcement" claims',
        "severity": "HIGH",
    },
    "operational_security": {
        "pattern": r"operational[\s-](?:security|enforcement)",
        "description": '"Operational security/enforcement" claims',
        "severity": "MEDIUM",
    },
    "admission_control_enforcement": {
        "pattern": r"admission[\s-]control[\s-]enforcement",
        "description": '"Admission control enforcement" claims',
        "severity": "HIGH",
    },
    "policy_enforcement_validated": {
        "pattern": r"policy[\s-]enforcement[\s-]validated",
        "description": '"Policy enforcement validated" claims',
        "severity": "HIGH",
    },
    "security_hardening_complete": {
        "pattern": r"security[\s-]hardening[\s-]complete",
        "description": '"Security hardening complete" claims',
        "severity": "HIGH",
    },
}

# Status field patterns
STATUS_PATTERNS = {
    "production_status": {
        "pattern": r'\*\*Status:\*\*.*Production(?:\s+Implementation|\s+Integration)?',
        "description": 'Status field declares production status',
        "severity": "CRITICAL",
    }
}

# Specific metric patterns that imply production validation
METRIC_PATTERNS = {
    "uptime_claims": {
        "pattern": r'\d+\.\d+%\s+uptime',
        "description": "Specific uptime percentage claims",
        "severity": "MEDIUM",
    },
    "readiness_score": {
        "pattern": r'\d+/100\s+(?:readiness|production)\s+score',
        "description": "Numerical readiness score claims",
        "severity": "MEDIUM",
    },
}


class Violation:
    """Represents a single policy violation"""

    def __init__(self, filepath: str, line_num: int, line_text: str,
                 pattern_name: str, pattern_info: dict, match_text: str):
        self.filepath = filepath
        self.line_num = line_num
        self.line_text = line_text
        self.pattern_name = pattern_name
        self.pattern_info = pattern_info
        self.match_text = match_text

    def to_dict(self) -> dict:
        return {
            "file": self.filepath,
            "line": self.line_num,
            "text": self.line_text,
            "pattern": self.pattern_name,
            "description": self.pattern_info["description"],
            "severity": self.pattern_info["severity"],
            "match": self.match_text,
        }

    def __str__(self) -> str:
        return (
            f"{self.filepath}:{self.line_num} [{self.pattern_info['severity']}]\n"
            f"  Pattern: {self.pattern_info['description']}\n"
            f"  Match: '{self.match_text}'\n"
            f"  Line: {self.line_text[:100]}"
        )


def scan_file(filepath: str) -> List[Violation]:
    """Scan a single file for policy violations"""
    violations = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return violations

    # Check all pattern categories
    all_patterns = {**PROHIBITED_PATTERNS, **STATUS_PATTERNS, **METRIC_PATTERNS}

    for line_num, line in enumerate(lines, 1):
        for pattern_name, pattern_info in all_patterns.items():
            regex = re.compile(pattern_info["pattern"], re.IGNORECASE)
            for match in regex.finditer(line):
                violations.append(Violation(
                    filepath=filepath,
                    line_num=line_num,
                    line_text=line.strip(),
                    pattern_name=pattern_name,
                    pattern_info=pattern_info,
                    match_text=match.group()
                ))

    return violations


def generate_report(violations: List[Violation], output_format: str = "text") -> str:
    """Generate a formatted report"""

    if output_format == "json":
        return json.dumps([v.to_dict() for v in violations], indent=2)

    # Text format
    if not violations:
        return "✅ No policy violations found.\n"

    # Group by file
    by_file: Dict[str, List[Violation]] = {}
    for v in violations:
        if v.filepath not in by_file:
            by_file[v.filepath] = []
        by_file[v.filepath].append(v)

    # Generate report
    lines = []
    lines.append("=" * 80)
    lines.append("SECURITY VALIDATION CLAIMS POLICY - VIOLATION REPORT")
    lines.append("=" * 80)
    lines.append("")

    # Summary
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for v in violations:
        severity = v.pattern_info.get("severity", "MEDIUM")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    lines.append("SUMMARY:")
    lines.append(f"  Total Violations: {len(violations)}")
    lines.append(f"  Files Affected: {len(by_file)}")
    lines.append(f"  Severity Breakdown:")
    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = severity_counts.get(severity, 0)
        if count > 0:
            lines.append(f"    - {severity}: {count}")
    lines.append("")
    lines.append("=" * 80)
    lines.append("")

    # Detailed violations
    for filepath, file_violations in sorted(by_file.items()):
        lines.append(f"FILE: {filepath}")
        lines.append(f"  {len(file_violations)} violation(s) found")
        lines.append("")

        for v in sorted(file_violations, key=lambda x: x.line_num):
            lines.append(f"  Line {v.line_num} [{v.pattern_info['severity']}]")
            lines.append(f"    Pattern: {v.pattern_info['description']}")
            lines.append(f"    Match: '{v.match_text}'")
            lines.append(f"    Text: {v.line_text[:100]}")
            lines.append("")

        lines.append("-" * 80)
        lines.append("")

    # Required actions
    lines.append("=" * 80)
    lines.append("REQUIRED ACTIONS")
    lines.append("=" * 80)
    lines.append("")
    lines.append("Per .github/SECURITY_VALIDATION_POLICY.md, you have TWO OPTIONS:")
    lines.append("")
    lines.append("Option 1: Provide Complete Runtime Validation Evidence")
    lines.append("  - Execute ALL 5 runtime validation tests")
    lines.append("  - Attach timestamped logs/screenshots")
    lines.append("  - See policy document for specific requirements")
    lines.append("")
    lines.append("Option 2: Reframe Claims Using Safe Language")
    lines.append("  - Remove 'Production Implementation' status declarations")
    lines.append("  - Replace prohibited claims with approved framing:")
    lines.append("    ✅ 'Implementation aligns with enterprise hardening patterns'")
    lines.append("    ✅ 'Full adversarial validation is ongoing'")
    lines.append("    ✅ 'Configuration reviewed for compliance with best practices'")
    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate files against Security Validation Claims Policy"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to scan (supports glob patterns)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Scan all whitepapers in docs/whitepapers/"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error code 1 even for MEDIUM severity violations"
    )

    args = parser.parse_args()

    # Determine files to scan
    files_to_scan = []

    if args.all:
        files_to_scan.extend(glob.glob("docs/whitepapers/*.md"))

    if args.files:
        for pattern in args.files:
            if "*" in pattern or "?" in pattern:
                files_to_scan.extend(glob.glob(pattern))
            else:
                files_to_scan.append(pattern)

    if not files_to_scan:
        parser.print_help()
        return 2

    # Scan all files
    all_violations = []
    for filepath in files_to_scan:
        violations = scan_file(filepath)
        all_violations.extend(violations)

    # Generate report
    report = generate_report(all_violations, args.format)
    print(report)

    # Determine exit code
    if not all_violations:
        return 0

    # Check severity threshold
    has_critical_or_high = any(
        v.pattern_info.get("severity") in ["CRITICAL", "HIGH"]
        for v in all_violations
    )

    if has_critical_or_high or args.strict:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
