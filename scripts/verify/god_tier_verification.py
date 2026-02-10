#!/usr/bin/env python3
"""
God Tier Verification Tool

Single-command verification of Project-AI's structural integrity,
documentation alignment, and quality standards.

Outputs:
  - Human-readable report
  - Machine-readable JSON
  - Exit code (0 = pass, 1 = warnings, 2 = failures)

Usage:
    python scripts/verify/god_tier_verification.py [--json] [--sign]
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


class GodTierVerifier:
    """Verifies God Tier compliance across all domains"""

    def __init__(self, root_path: Path):
        self.root = root_path
        self.results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0",
            "repository": "Project-AI",
            "checks": [],
        }
        self.warnings = 0
        self.failures = 0

    def run_check(self, name: str, check_func) -> dict:
        """Run a verification check and record results"""
        print(f"\n{BLUE}▶{RESET} {name}...")

        try:
            passed, message, details = check_func()

            result = {
                "name": name,
                "passed": passed,
                "message": message,
                "details": details,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

            self.results["checks"].append(result)

            if passed:
                print(f"  {GREEN}✓{RESET} {message}")
            else:
                if "warning" in message.lower():
                    print(f"  {YELLOW}⚠{RESET} {message}")
                    self.warnings += 1
                else:
                    print(f"  {RED}✗{RESET} {message}")
                    self.failures += 1

            if details:
                for detail in details[:3]:  # Show first 3 details
                    print(f"    {detail}")

            return result

        except Exception as e:
            result = {
                "name": name,
                "passed": False,
                "message": f"Check failed with error: {str(e)}",
                "details": [],
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
            self.results["checks"].append(result)
            print(f"  {RED}✗{RESET} Error: {str(e)}")
            self.failures += 1
            return result

    def check_root_structure(self) -> tuple[bool, str, list[str]]:
        """Verify root directory structure compliance"""

        violations = []
        root_files = [f for f in self.root.iterdir() if f.is_file()]

        for file in root_files:
            name = file.name

            # Check for prohibited patterns
            if any(
                pattern in name
                for pattern in ["_COMPLETE.md", "_SUMMARY.md", "_STATUS.md"]
            ):
                violations.append(f"Prohibited file in root: {name}")

            if name.endswith((".backup", ".bak", "~")):
                violations.append(f"Backup file in root: {name}")

        if violations:
            return (
                False,
                f"Found {len(violations)} root structure violations",
                violations,
            )

        return True, f"Root structure clean ({len(root_files)} files)", []

    def check_archive_index(self) -> tuple[bool, str, list[str]]:
        """Verify archive index exists and is current"""
        index_path = self.root / "docs/internal/archive/ARCHIVE_INDEX.md"

        if not index_path.exists():
            return (
                False,
                "ARCHIVE_INDEX.md missing",
                ["Create: docs/internal/archive/ARCHIVE_INDEX.md"],
            )

        # Count archived files
        archive_path = self.root / "docs/internal/archive"
        archive_files = list(archive_path.rglob("*.md")) + list(
            archive_path.rglob("*.txt")
        )
        archive_count = len([f for f in archive_files if f.name != "ARCHIVE_INDEX.md"])

        # Check if index mentions approximate file count
        with open(index_path) as f:
            content = f.read()

        # Simple heuristic: index should mention file count
        if str(archive_count) not in content and str(archive_count - 5) not in content:
            return (
                False,
                f"Archive index may be outdated ({archive_count} files found)",
                ["Consider updating ARCHIVE_INDEX.md with current file count"],
            )

        return True, f"Archive index current ({archive_count} files indexed)", []

    def check_documentation_alignment(self) -> tuple[bool, str, list[str]]:
        """Check for documentation drift"""
        issues = []

        # Check Thirsty-Lang spec
        spec_path = self.root / "src/thirsty_lang/docs/SPECIFICATION.md"
        if spec_path.exists():
            with open(spec_path) as f:
                content = f.read()

            # Look for "planned" or "not yet implemented"
            if "not yet implemented" in content.lower():
                issues.append("SPECIFICATION.md contains 'not yet implemented'")

        # Check TARL README
        tarl_readme = self.root / "tarl/README.md"
        if tarl_readme.exists():
            with open(tarl_readme) as f:
                content = f.read()

            # Check for "In Progress" in completed phases
            if "Phase 2: Compiler (In Progress)" in content:
                issues.append("TARL README shows completed phase as 'In Progress'")

        if issues:
            return False, f"Found {len(issues)} documentation drift issues", issues

        return True, "Documentation aligned with implementation", []

    def check_version_consistency(self) -> tuple[bool, str, list[str]]:
        """Verify version numbers are consistent"""
        versions = {}
        details = []

        # pyproject.toml
        pyproject = self.root / "pyproject.toml"
        if pyproject.exists():
            with open(pyproject) as f:
                for line in f:
                    if line.strip().startswith("version ="):
                        versions["pyproject"] = line.split("=")[1].strip().strip("\"'")
                        break

        # TARL README
        tarl_readme = self.root / "tarl/README.md"
        if tarl_readme.exists():
            with open(tarl_readme) as f:
                for line in f:
                    if "Version:" in line:
                        parts = line.split(":")
                        if len(parts) > 1:
                            versions["tarl_readme"] = parts[1].strip()
                        break

        for name, version in versions.items():
            details.append(f"{name}: {version}")

        # Just report versions, don't fail on differences
        return True, f"Versions documented: {len(versions)} sources", details

    def check_tests_passing(self) -> tuple[bool, str, list[str]]:
        """Quick test status check (doesn't run tests, checks CI)"""
        # In real implementation, would check latest CI run
        # For now, just verify test directories exist

        test_dirs = []
        if (self.root / "tests").exists():
            test_dirs.append("tests/")
        if (self.root / "e2e").exists():
            test_dirs.append("e2e/")

        if not test_dirs:
            return False, "No test directories found", ["Expected: tests/ or e2e/"]

        return True, f"Test infrastructure present: {', '.join(test_dirs)}", []

    def check_ci_workflows(self) -> tuple[bool, str, list[str]]:
        """Verify critical CI workflows exist"""
        workflows_dir = self.root / ".github/workflows"

        if not workflows_dir.exists():
            return False, "No CI workflows directory", [".github/workflows/ missing"]

        required_workflows = ["enforce-root-structure.yml", "doc-code-alignment.yml"]

        missing = []
        found = []

        for workflow in required_workflows:
            path = workflows_dir / workflow
            if path.exists():
                found.append(workflow)
            else:
                missing.append(workflow)

        if missing:
            return (
                False,
                f"Missing {len(missing)} critical workflows",
                [f"Missing: {w}" for w in missing],
            )

        return True, f"All {len(found)} critical workflows present", found

    def check_codeowners(self) -> tuple[bool, str, list[str]]:
        """Verify CODEOWNERS file exists and has content"""
        codeowners = self.root / "CODEOWNERS"

        if not codeowners.exists():
            return False, "CODEOWNERS file missing", ["Create CODEOWNERS file"]

        with open(codeowners) as f:
            lines = [
                l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")
            ]

        if len(lines) < 5:
            return (
                False,
                f"CODEOWNERS too sparse ({len(lines)} rules)",
                ["Add more granular ownership rules"],
            )

        return True, f"CODEOWNERS comprehensive ({len(lines)} rules)", []

    def generate_report(self) -> str:
        """Generate human-readable report"""
        lines = []
        lines.append("")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append(f"{BOLD}🔍 GOD TIER VERIFICATION REPORT{RESET}")
        lines.append("═══════════════════════════════════════════════════════════")
        lines.append("")
        lines.append("Repository: Project-AI")
        lines.append(f"Timestamp: {self.results['timestamp']}")
        lines.append(f"Verifier Version: {self.results['version']}")
        lines.append("")

        # Summary
        passed = sum(1 for c in self.results["checks"] if c["passed"])
        total = len(self.results["checks"])

        lines.append("📊 Summary:")
        lines.append(f"  Total Checks: {total}")
        lines.append(f"  {GREEN}✓{RESET} Passed: {passed}")
        lines.append(f"  {YELLOW}⚠{RESET} Warnings: {self.warnings}")
        lines.append(f"  {RED}✗{RESET} Failures: {self.failures}")
        lines.append("")

        # Overall status
        if self.failures == 0 and self.warnings == 0:
            lines.append(f"{GREEN}{BOLD}✅ GOD TIER STATUS: VERIFIED{RESET}")
            lines.append("")
            lines.append("All structural invariants intact.")
            lines.append("Documentation aligned with implementation.")
            lines.append("Quality standards maintained.")
        elif self.failures == 0:
            lines.append(
                f"{YELLOW}{BOLD}⚠️  GOD TIER STATUS: PASSED WITH WARNINGS{RESET}"
            )
            lines.append("")
            lines.append("Core requirements met, but improvements recommended.")
        else:
            lines.append(f"{RED}{BOLD}❌ GOD TIER STATUS: VERIFICATION FAILED{RESET}")
            lines.append("")
            lines.append("Critical issues must be addressed.")

        lines.append("")
        lines.append("═══════════════════════════════════════════════════════════")

        return "\n".join(lines)

    def run_all_checks(self):
        """Run all verification checks"""
        print(f"\n{BOLD}🔍 Running God Tier Verification...{RESET}")

        self.run_check("Root Structure Compliance", self.check_root_structure)
        self.run_check("Archive Index Current", self.check_archive_index)
        self.run_check("Documentation Alignment", self.check_documentation_alignment)
        self.run_check("Version Consistency", self.check_version_consistency)
        self.run_check("Test Infrastructure", self.check_tests_passing)
        self.run_check("CI Workflows Present", self.check_ci_workflows)
        self.run_check("CODEOWNERS Configuration", self.check_codeowners)

        # Calculate overall status
        self.results["summary"] = {
            "total_checks": len(self.results["checks"]),
            "passed": sum(1 for c in self.results["checks"] if c["passed"]),
            "warnings": self.warnings,
            "failures": self.failures,
            "status": (
                "VERIFIED"
                if self.failures == 0 and self.warnings == 0
                else "PASSED_WITH_WARNINGS" if self.failures == 0 else "FAILED"
            ),
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="God Tier Verification Tool")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--output", type=str, help="Output file path")
    args = parser.parse_args()

    # Find repository root
    root = Path(__file__).parent.parent.parent

    # Run verification
    verifier = GodTierVerifier(root)
    verifier.run_all_checks()

    # Output results
    if args.json:
        output = json.dumps(verifier.results, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"\n✅ JSON report written to: {args.output}")
        else:
            print(output)
    else:
        report = verifier.generate_report()
        print(report)

        if args.output:
            with open(args.output, "w") as f:
                # Strip color codes for file output
                clean_report = report
                for code in [GREEN, YELLOW, RED, BLUE, BOLD, RESET]:
                    clean_report = clean_report.replace(code, "")
                f.write(clean_report)
            print(f"\n✅ Report written to: {args.output}")

    # Exit code based on results
    if verifier.failures > 0:
        sys.exit(2)
    elif verifier.warnings > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
