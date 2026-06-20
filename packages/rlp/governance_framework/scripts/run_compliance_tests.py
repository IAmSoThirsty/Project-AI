#!/usr/bin/env python3
"""
Compliance Test Runner for the Thirsty Governance Framework.

Reads tests/TEST_PROMPTS.md and tests/FAILURE_CASES.md, parses the structured
markdown, and produces a compliance report. Supports dry-run mode for validation
and optional output to docs/operations/compliance_report_{timestamp}.md.

Usage:
    python scripts/run_compliance_tests.py --dry-run
    python scripts/run_compliance_tests.py --model <model-name>
    python scripts/run_compliance_tests.py --model <model-name> --output
    python scripts/run_compliance_tests.py --model <model-name> --mark-untested-as "Skipped"
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


# Project root - resolves script location (scripts/ -> project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Default paths
TEST_PROMPTS_PATH = PROJECT_ROOT / "tests" / "TEST_PROMPTS.md"
FAILURE_CASES_PATH = PROJECT_ROOT / "tests" / "FAILURE_CASES.md"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "operations"


# ---------------------------------------------------------------------------
# Markdown Parsing
# ---------------------------------------------------------------------------

def parse_test_prompts(filepath):
    """
    Parse TEST_PROMPTS.md into a list of test case dicts.

    Expected format:
        ## Test N: Title
        **Test prompt:** ...
        **Rules targeted:** ...
        **Expected compliant behavior:** ...
        **What a failure looks like:** ...
        **Verification method:** ...
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Test prompts file not found: {filepath}")

    text = filepath.read_text(encoding="utf-8")
    sections = re.split(r'^## ', text, flags=re.MULTILINE)

    tests = []
    for section in sections:
        if not section.strip():
            continue
        header_match = re.match(r'Test (\d+): (.+)', section)
        if not header_match:
            continue

        test_num = header_match.group(1)
        title = header_match.group(2).strip()

        fields = {
            "test_prompt": "",
            "rules_targeted": "",
            "expected_behavior": "",
            "failure_look": "",
            "verification_method": "",
        }

        field_map = {
            "Test prompt": "test_prompt",
            "Rules targeted": "rules_targeted",
            "Expected compliant behavior": "expected_behavior",
            "What a failure looks like": "failure_look",
            "Verification method": "verification_method",
        }

        for field_label, field_key in field_map.items():
            pattern = rf'\*\*{re.escape(field_label)}:\*\*\s*(.*?)(?=\n\*\*|\Z)'
            match = re.search(pattern, section, re.DOTALL)
            if match:
                fields[field_key] = match.group(1).strip()

        tests.append({
            "id": f"test_{test_num}",
            "title": title,
            "type": "test_prompt",
            **fields,
        })

    return tests


def parse_failure_cases(filepath):
    """
    Parse FAILURE_CASES.md into a list of failure case dicts.

    Expected format:
        ## Case N: Title
        **Scenario description:** ...
        **Trigger condition:** ...
        **Correct response:** ...
        **Non-compliant response:** ...
        **Blocker class / Rule:** ...
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Failure cases file not found: {filepath}")

    text = filepath.read_text(encoding="utf-8")
    sections = re.split(r'^## ', text, flags=re.MULTILINE)

    cases = []
    for section in sections:
        if not section.strip():
            continue
        header_match = re.match(r'Case (\d+): (.+)', section)
        if not header_match:
            continue

        case_num = header_match.group(1)
        title = header_match.group(2).strip()

        fields = {
            "scenario": "",
            "trigger": "",
            "correct_response": "",
            "non_compliant": "",
            "blocker_class": "",
        }

        field_map = {
            "Scenario description": "scenario",
            "Trigger condition": "trigger",
            "Correct response": "correct_response",
            "Non-compliant response": "non_compliant",
            "Blocker class / Rule": "blocker_class",
        }

        for field_label, field_key in field_map.items():
            pattern = rf'\*\*{re.escape(field_label)}:\*\*\s*(.*?)(?=\n\*\*|\Z)'
            match = re.search(pattern, section, re.DOTALL)
            if match:
                fields[field_key] = match.group(1).strip()

        cases.append({
            "id": f"case_{case_num}",
            "title": title,
            "type": "failure_case",
            **fields,
        })

    return cases


# ---------------------------------------------------------------------------
# Compliance Report
# ---------------------------------------------------------------------------

def generate_report(test_results, failure_results, model_under_test, mark_untested_as):
    """
    Generate a compliance report from test and failure case results.

    Args:
        test_results: List of dicts with keys: id, title, status
        failure_results: List of dicts with keys: id, title, status
        model_under_test: Model name or "manual"
        mark_untested_as: Default status for untested cases

    Returns:
        Report dict
    """
    all_results = test_results + failure_results
    total = len(all_results)
    passed = sum(1 for r in all_results if r["status"] == "Pass")
    failed = sum(1 for r in all_results if r["status"] == "Fail")
    partial = sum(1 for r in all_results if r["status"] == "Partial")
    untested = total - passed - failed - partial

    # For pass rate, only count tested cases (not untested)
    tested_count = passed + failed + partial
    pass_rate = (passed / tested_count * 100) if tested_count > 0 else 0.0

    failure_details = [
        {"id": r["id"], "title": r["title"], "status": r["status"], "notes": r.get("notes", "")}
        for r in all_results if r["status"] == "Fail" or r["status"] == "Partial"
    ]

    # Coverage gaps: untested cases
    coverage_gaps = [
        {"id": r["id"], "title": r["title"]}
        for r in all_results if r["status"] == mark_untested_as or r["status"] == "untested"
    ]

    return {
        "header": {
            "title": "Compliance Test Report — Thirsty Governance Framework",
            "generated": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        },
        "model_under_test": model_under_test,
        "test_summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "partial": partial,
            "untested": untested,
        },
        "results": {
            "test_prompts": test_results,
            "failure_cases": failure_results,
        },
        "pass_rate": round(pass_rate, 1),
        "failure_details": failure_details,
        "coverage_gaps": coverage_gaps,
    }


def format_report_text(report):
    """Format the compliance report as a markdown string."""
    lines = []
    h = report["header"]
    lines.append(f"# {h['title']}")
    lines.append(f"**Generated:** {h['generated']}")
    lines.append(f"**Model under test:** {report['model_under_test']}")
    lines.append("")

    s = report["test_summary"]
    lines.append("## Summary")
    lines.append(f"- **Total test cases:** {s['total']}")
    lines.append(f"- **Passed:** {s['passed']}")
    lines.append(f"- **Failed:** {s['failed']}")
    lines.append(f"- **Partial:** {s['partial']}")
    lines.append(f"- **Untested:** {s['untested']}")
    lines.append(f"- **Pass rate:** {report['pass_rate']}%")
    lines.append("")

    lines.append("## Test Prompt Results")
    lines.append("| ID | Title | Status | Notes |")
    lines.append("|----|-------|--------|-------|")
    for t in report["results"]["test_prompts"]:
        notes = t.get("notes", "")
        if not notes:
            notes = t.get("verification_method", "")[:80]
            if notes and len(notes) == 80:
                notes += "..."
        lines.append(f"| {t['id']} | {t['title']} | {t['status']} | {notes} |")
    lines.append("")

    lines.append("## Failure Case Results")
    lines.append("| ID | Title | Status | Notes |")
    lines.append("|----|-------|--------|-------|")
    for c in report["results"]["failure_cases"]:
        notes = c.get("notes", "")
        if not notes:
            notes = c.get("blocker_class", "")[:80]
            if notes and len(notes) == 80:
                notes += "..."
        lines.append(f"| {c['id']} | {c['title']} | {c['status']} | {notes} |")
    lines.append("")

    if report["failure_details"]:
        lines.append("## Failure Details")
        for fd in report["failure_details"]:
            lines.append(f"### {fd['id']}: {fd['title']}")
            lines.append(f"- **Status:** {fd['status']}")
            lines.append(f"- **Notes:** {fd['notes']}")
            lines.append("")

    if report["coverage_gaps"]:
        lines.append("## Coverage Gaps")
        for cg in report["coverage_gaps"]:
            lines.append(f"- {cg['id']}: {cg['title']}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Thirsty Governance Framework — Compliance Test Runner"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse test files and display test count without marking results",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="manual",
        help="Model name or identifier to include in the report header",
    )
    parser.add_argument(
        "--output",
        action="store_true",
        help="Save the compliance report to docs/operations/compliance_report_{timestamp}.md",
    )
    parser.add_argument(
        "--mark-untested-as",
        type=str,
        default="Not tested",
        help="Default status label for untested cases (default: 'Not tested')",
    )
    args = parser.parse_args()

    # --- Parse test files ---
    try:
        test_prompts = parse_test_prompts(TEST_PROMPTS_PATH)
        failure_cases = parse_failure_cases(FAILURE_CASES_PATH)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to parse test files: {e}", file=sys.stderr)
        sys.exit(1)

    total_tests = len(test_prompts)
    total_failures = len(failure_cases)
    total_cases = total_tests + total_failures

    # --- Validate test count expectations ---
    if total_tests < 10:
        print(f"WARNING: Expected at least 10 test prompts, found {total_tests}.")
    if total_failures < 8:
        print(f"WARNING: Expected at least 8 failure cases, found {total_failures}.")

    # --- Dry run ---
    if args.dry_run:
        print(f"=== Dry Run: Compliance Test Parser ===")
        print(f"Test prompts file: {TEST_PROMPTS_PATH}")
        print(f"Failure cases file: {FAILURE_CASES_PATH}")
        print(f"")
        print(f"Parsed {total_tests} test prompts:")
        for t in test_prompts:
            rules = t.get("rules_targeted", "")[:60]
            if len(t.get("rules_targeted", "")) > 60:
                rules += "..."
            print(f"  {t['id']}: {t['title']} — Rules: {rules}")

        print(f"")
        print(f"Parsed {total_failures} failure cases:")
        for c in failure_cases:
            bc = c.get("blocker_class", "")[:60]
            if len(c.get("blocker_class", "")) > 60:
                bc += "..."
            print(f"  {c['id']}: {c['title']} — Class: {bc}")

        print(f"")
        print(f"Total test cases: {total_cases}")
        print(f"Dry run complete. Tests parsed successfully.")
        return 0

    # --- Build results (all default to mark_untested_as) ---
    test_results = []
    for t in test_prompts:
        verification = t.get("verification_method", "")
        test_results.append({
            "id": t["id"],
            "title": t["title"],
            "type": "test_prompt",
            "status": args.mark_untested_as,
            "notes": f"Awaiting manual evaluation. "
                     f"Verify: {verification[:120]}{'...' if len(verification) > 120 else ''}",
            "verification_method": verification,
        })

    failure_results = []
    for c in failure_cases:
        failure_results.append({
            "id": c["id"],
            "title": c["title"],
            "type": "failure_case",
            "status": args.mark_untested_as,
            "notes": f"Awaiting manual evaluation. "
                     f"Expected blocker: {c.get('blocker_class', 'N/A')[:120]}",
            "blocker_class": c.get("blocker_class", ""),
        })

    # --- Generate report ---
    report = generate_report(
        test_results=test_results,
        failure_results=failure_results,
        model_under_test=args.model,
        mark_untested_as=args.mark_untested_as,
    )

    report_text = format_report_text(report)

    # Output to stdout
    print(report_text)

    # Optional output to file
    if args.output:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_path = OUTPUT_DIR / f"compliance_report_{timestamp}.md"
        output_path.write_text(report_text, encoding="utf-8")
        print(f"\nReport saved to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())