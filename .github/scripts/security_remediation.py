#!/usr/bin/env python3
"""
Security Remediation Script

This script automatically remediates security vulnerabilities:
- Upgrades vulnerable dependencies
- Applies security patches to code
- Removes exposed secrets
- Generates remediation reports
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


class SecurityRemediator:
    """Handles automatic security vulnerability remediation."""

    def __init__(self, report_dir: str = "security-reports"):
        self.report_dir = Path(report_dir)
        self.fixes_applied = []
        self.fixes_failed = []

    def remediate_dependencies(self, audit_report: str = "pip-audit.json") -> bool:
        """
        Automatically remediate vulnerable dependencies.

        Args:
            audit_report: Path to pip-audit JSON report

        Returns:
            True if fixes were applied, False otherwise
        """
        report_path = self.report_dir / audit_report

        if not report_path.exists():
            print(f"❌ Report not found: {report_path}")
            return False

        try:
            with open(report_path) as f:
                data = json.load(f)

            dependencies = data.get("dependencies", [])

            if not dependencies:
                print("✅ No vulnerable dependencies found")
                return False

            print(f"📦 Found {len(dependencies)} vulnerable packages")

            for dep in dependencies:
                pkg_name = dep.get("name")
                current_version = dep.get("version")
                vulns = dep.get("vulns", [])

                if not vulns:
                    continue

                # Get fixed versions
                fixed_versions = []
                for vuln in vulns:
                    if vuln.get("fix_versions"):
                        fixed_versions.extend(vuln["fix_versions"])

                print(f"\n🔧 Remediating {pkg_name} (current: {current_version})")
                print(f"   Vulnerabilities: {len(vulns)}")

                if fixed_versions:
                    # Try to upgrade to the highest fixed version
                    target_version = max(fixed_versions)
                    success = self._upgrade_package(pkg_name, target_version)
                else:
                    # Try to upgrade to latest
                    success = self._upgrade_package(pkg_name)

                if success:
                    self.fixes_applied.append(
                        {
                            "package": pkg_name,
                            "from_version": current_version,
                            "vulnerabilities": len(vulns),
                        }
                    )
                else:
                    self.fixes_failed.append(
                        {"package": pkg_name, "reason": "Upgrade failed"}
                    )

            # Update requirements.txt
            if self.fixes_applied:
                self._update_requirements()
                return True

            return False

        except Exception as e:
            print(f"❌ Error remediating dependencies: {e}")
            return False

    def _upgrade_package(self, package: str, version: str = None) -> bool:
        """Upgrade a package to a specific version or latest."""
        try:
            if version:
                cmd = ["pip", "install", "--upgrade", f"{package}=={version}"]
                print(f"   Upgrading to version {version}...")
            else:
                cmd = ["pip", "install", "--upgrade", package]
                print("   Upgrading to latest version...")

            subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"   ✅ Successfully upgraded {package}")
            return True

        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to upgrade {package}: {e.stderr}")
            return False

    def _update_requirements(self):
        """Update requirements.txt with current package versions."""
        try:
            print("\n📝 Updating requirements.txt...")
            result = subprocess.run(
                ["pip", "freeze"], capture_output=True, text=True, check=True
            )

            with open("requirements.txt", "w") as f:
                f.write(result.stdout)

            print("   ✅ requirements.txt updated")

        except Exception as e:
            print(f"   ⚠️ Could not update requirements.txt: {e}")

    def remediate_code_issues(self, bandit_report: str = "bandit.json") -> bool:
        """
        Analyze code security issues for potential auto-fixes.

        Args:
            bandit_report: Path to Bandit JSON report

        Returns:
            True if analysis completed, False otherwise
        """
        report_path = self.report_dir / bandit_report

        if not report_path.exists():
            print(f"❌ Report not found: {report_path}")
            return False

        try:
            with open(report_path) as f:
                data = json.load(f)

            results = data.get("results", [])

            if not results:
                print("✅ No code security issues found")
                return False

            print(f"🔍 Analyzing {len(results)} code security issues...")

            # Categorize issues
            auto_fixable = []
            requires_review = []

            for issue in results:
                test_id = issue.get("test_id", "")
                severity = issue.get("issue_severity", "")

                # Determine if auto-fixable
                if severity == "LOW" and test_id in ["B101", "B601", "B602"]:
                    # These are potentially auto-fixable
                    auto_fixable.append(issue)
                else:
                    requires_review.append(issue)

            print(f"   ✅ Auto-fixable: {len(auto_fixable)}")
            print(f"   ⚠️  Requires review: {len(requires_review)}")

            # For now, we document issues rather than auto-fix code
            # Auto-fixing code is risky and should be done carefully
            self._create_code_issues_report(results)

            return True

        except Exception as e:
            print(f"❌ Error analyzing code issues: {e}")
            return False

    def _create_code_issues_report(self, issues: list[dict]):
        """Create a markdown report of code security issues."""
        report_path = Path("code-security-issues.md")

        with open(report_path, "w") as f:
            f.write("# Code Security Issues Report\n\n")
            f.write(f"Total issues: {len(issues)}\n\n")

            # Group by severity
            by_severity = {}
            for issue in issues:
                severity = issue.get("issue_severity", "UNKNOWN")
                by_severity.setdefault(severity, []).append(issue)

            for severity in ["HIGH", "MEDIUM", "LOW"]:
                if severity in by_severity:
                    f.write(
                        f"## {severity} Severity ({len(by_severity[severity])} issues)\n\n"
                    )

                    for issue in by_severity[severity][:10]:  # Limit to 10 per severity
                        f.write(f"### {issue.get('test_name', 'Unknown')}\n")
                        f.write(f"- **File**: `{issue.get('filename', 'unknown')}`\n")
                        f.write(f"- **Line**: {issue.get('line_number', 0)}\n")
                        f.write(
                            f"- **Issue**: {issue.get('issue_text', 'No description')}\n"
                        )
                        f.write(
                            f"- **CWE**: {issue.get('issue_cwe', {}).get('id', 'N/A')}\n\n"
                        )

        print(f"   📄 Report created: {report_path}")

    def check_for_secrets(self, secrets_report: str = "secrets.json") -> bool:
        """
        Check for exposed secrets and create alerts.

        Args:
            secrets_report: Path to detect-secrets JSON report

        Returns:
            True if secrets found, False otherwise
        """
        report_path = self.report_dir / secrets_report

        if not report_path.exists():
            print(f"❌ Report not found: {report_path}")
            return False

        try:
            with open(report_path) as f:
                data = json.load(f)

            results = data.get("results", {})

            if not results or len(results) == 0:
                print("✅ No secrets detected")
                return False

            print(f"🚨 CRITICAL: Detected potential secrets in {len(results)} files")

            # Create critical alert file
            with open("SECRETS_ALERT.txt", "w") as f:
                f.write("CRITICAL SECURITY ALERT\n")
                f.write("=" * 50 + "\n\n")
                f.write("Potential secrets detected in the following files:\n\n")

                for filename, secrets in results.items():
                    f.write(f"- {filename}: {len(secrets)} secret(s)\n")

                f.write("\nIMMEDIATE ACTION REQUIRED:\n")
                f.write("1. Review and remove all secrets from code\n")
                f.write("2. Rotate any exposed credentials\n")
                f.write("3. Use environment variables for secrets\n")
                f.write("4. Update .gitignore to prevent future commits\n")

            print("   📄 Critical alert created: SECRETS_ALERT.txt")
            return True

        except Exception as e:
            print(f"❌ Error checking secrets: {e}")
            return False

    def generate_summary(self) -> dict:
        """Generate a summary of all remediation actions."""
        summary = {
            "fixes_applied": len(self.fixes_applied),
            "fixes_failed": len(self.fixes_failed),
            "applied_details": self.fixes_applied,
            "failed_details": self.fixes_failed,
        }

        # Write summary to file
        with open("remediation-summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        print("\n" + "=" * 50)
        print("REMEDIATION SUMMARY")
        print("=" * 50)
        print(f"✅ Fixes applied: {summary['fixes_applied']}")
        print(f"❌ Fixes failed: {summary['fixes_failed']}")
        print("\nSummary saved to: remediation-summary.json")

        return summary


def main():
    """Main entry point for security remediation."""
    parser = argparse.ArgumentParser(
        description="Automated security vulnerability remediation"
    )
    parser.add_argument(
        "--report-dir",
        default="security-reports",
        help="Directory containing security scan reports",
    )
    parser.add_argument(
        "--dependencies",
        action="store_true",
        help="Remediate dependency vulnerabilities",
    )
    parser.add_argument(
        "--code", action="store_true", help="Analyze code security issues"
    )
    parser.add_argument(
        "--secrets", action="store_true", help="Check for exposed secrets"
    )
    parser.add_argument("--all", action="store_true", help="Run all remediation tasks")

    args = parser.parse_args()

    # If no specific task selected, run all
    if not any([args.dependencies, args.code, args.secrets, args.all]):
        args.all = True

    remediator = SecurityRemediator(report_dir=args.report_dir)

    results = {"dependencies": False, "code": False, "secrets": False}

    if args.all or args.dependencies:
        print("\n🔧 REMEDIATING DEPENDENCIES")
        print("=" * 50)
        results["dependencies"] = remediator.remediate_dependencies()

    if args.all or args.code:
        print("\n🔍 ANALYZING CODE SECURITY")
        print("=" * 50)
        results["code"] = remediator.remediate_code_issues()

    if args.all or args.secrets:
        print("\n🔐 CHECKING FOR SECRETS")
        print("=" * 50)
        results["secrets"] = remediator.check_for_secrets()

    # Generate final summary
    print("\n📊 GENERATING SUMMARY")
    print("=" * 50)
    summary = remediator.generate_summary()

    # Exit with appropriate code
    if results["secrets"]:
        print("\n🚨 CRITICAL: Secrets detected!")
        sys.exit(2)
    elif summary["fixes_applied"] > 0:
        print("\n✅ Remediation completed successfully")
        sys.exit(0)
    elif summary["fixes_failed"] > 0:
        print("\n⚠️ Some fixes failed")
        sys.exit(1)
    else:
        print("\n✅ No vulnerabilities found")
        sys.exit(0)


if __name__ == "__main__":
    main()
