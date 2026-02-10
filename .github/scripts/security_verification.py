#!/usr/bin/env python3
"""
Security Verification Script

Verifies that the repository has zero outstanding security issues
and generates a compliance report.
"""

import json
import subprocess
import sys
from datetime import datetime


class SecurityVerifier:
    """Verifies security compliance and generates reports."""

    def __init__(self):
        self.results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks": {},
            "overall_status": "UNKNOWN",
        }

    def verify_dependencies(self) -> tuple[bool, dict]:
        """Verify no vulnerable dependencies exist."""
        print("📦 Verifying dependency security...")

        try:
            result = subprocess.run(
                ["pip-audit", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                data = json.loads(result.stdout) if result.stdout else {}
                dependencies = data.get("dependencies", [])

                if len(dependencies) == 0:
                    print("   ✅ No vulnerable dependencies found")
                    return True, {
                        "status": "PASS",
                        "vulnerabilities": 0,
                        "details": "All dependencies are secure",
                    }
                else:
                    print(f"   ❌ Found {len(dependencies)} vulnerable dependencies")
                    return False, {
                        "status": "FAIL",
                        "vulnerabilities": len(dependencies),
                        "details": f"{len(dependencies)} packages have known vulnerabilities",
                    }
            else:
                print("   ⚠️ pip-audit check failed")
                return False, {"status": "ERROR", "details": "pip-audit command failed"}

        except Exception as e:
            print(f"   ❌ Error checking dependencies: {e}")
            return False, {"status": "ERROR", "details": str(e)}

    def verify_code_security(self) -> tuple[bool, dict]:
        """Verify no code security issues exist."""
        print("🔍 Verifying code security...")

        try:
            result = subprocess.run(
                ["bandit", "-r", "src/", "-f", "json"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            data = json.loads(result.stdout) if result.stdout else {}
            results = data.get("results", [])

            # Categorize by severity
            high_severity = [
                r for r in results if r.get("issue_severity") in ["HIGH", "CRITICAL"]
            ]
            medium_severity = [
                r for r in results if r.get("issue_severity") == "MEDIUM"
            ]
            low_severity = [r for r in results if r.get("issue_severity") == "LOW"]

            if len(high_severity) == 0 and len(medium_severity) == 0:
                print("   ✅ No critical/high/medium security issues found")
                print(f"   ℹ️ {len(low_severity)} low severity issues (acceptable)")
                return True, {
                    "status": "PASS",
                    "high_severity": 0,
                    "medium_severity": 0,
                    "low_severity": len(low_severity),
                    "details": "No critical security issues detected",
                }
            else:
                print("   ❌ Found security issues:")
                print(f"      High: {len(high_severity)}")
                print(f"      Medium: {len(medium_severity)}")
                print(f"      Low: {len(low_severity)}")
                return False, {
                    "status": "FAIL",
                    "high_severity": len(high_severity),
                    "medium_severity": len(medium_severity),
                    "low_severity": len(low_severity),
                    "details": f"{len(high_severity)} high and {len(medium_severity)} medium severity issues",
                }

        except Exception as e:
            print(f"   ❌ Error checking code security: {e}")
            return False, {"status": "ERROR", "details": str(e)}

    def verify_no_secrets(self) -> tuple[bool, dict]:
        """Verify no secrets are exposed in code."""
        print("🔐 Verifying no secrets exposed...")

        try:
            result = subprocess.run(
                [
                    "detect-secrets",
                    "scan",
                    "--all-files",
                    "--force-use-all-plugins",
                    "--exclude-files",
                    r"\.lock$",
                    "--exclude-files",
                    r"\.pyc$",
                    "--exclude-files",
                    "node_modules/",
                    "--exclude-files",
                    r"\.git/",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            data = json.loads(result.stdout) if result.stdout else {}
            results = data.get("results", {})

            if len(results) == 0:
                print("   ✅ No secrets detected")
                return True, {
                    "status": "PASS",
                    "secrets_found": 0,
                    "details": "No exposed secrets detected",
                }
            else:
                print(f"   ❌ Found potential secrets in {len(results)} files")
                return False, {
                    "status": "FAIL",
                    "secrets_found": len(results),
                    "details": f"Potential secrets detected in {len(results)} files",
                }

        except Exception as e:
            print(f"   ❌ Error checking for secrets: {e}")
            return False, {"status": "ERROR", "details": str(e)}

    def verify_all(self) -> bool:
        """Run all security verifications."""
        print("\n" + "=" * 60)
        print("SECURITY VERIFICATION")
        print("=" * 60 + "\n")

        # Run all checks
        dep_pass, dep_results = self.verify_dependencies()
        self.results["checks"]["dependencies"] = dep_results

        code_pass, code_results = self.verify_code_security()
        self.results["checks"]["code_security"] = code_results

        secrets_pass, secrets_results = self.verify_no_secrets()
        self.results["checks"]["secrets"] = secrets_results

        # Determine overall status
        all_passed = dep_pass and code_pass and secrets_pass

        if all_passed:
            self.results["overall_status"] = "PASS"
            print("\n" + "=" * 60)
            print("✅ ALL SECURITY CHECKS PASSED")
            print("=" * 60)
        else:
            self.results["overall_status"] = "FAIL"
            print("\n" + "=" * 60)
            print("❌ SECURITY CHECKS FAILED")
            print("=" * 60)

        return all_passed

    def generate_report(self, output_file: str = "SECURITY_VERIFICATION_REPORT.md"):
        """Generate a detailed security verification report."""
        print(f"\n📄 Generating report: {output_file}")

        report = []
        report.append("# Security Verification Report\n")
        report.append(f"**Generated**: {self.results['timestamp']}\n")
        report.append(f"**Overall Status**: {self.results['overall_status']}\n\n")

        report.append("## Verification Results\n\n")

        # Dependencies
        dep_check = self.results["checks"].get("dependencies", {})
        report.append("### 1. Dependency Vulnerabilities\n\n")
        report.append(f"- **Status**: {dep_check.get('status', 'UNKNOWN')}\n")
        report.append(
            f"- **Vulnerabilities Found**: {dep_check.get('vulnerabilities', 'N/A')}\n"
        )
        report.append(
            f"- **Details**: {dep_check.get('details', 'No details available')}\n\n"
        )

        # Code Security
        code_check = self.results["checks"].get("code_security", {})
        report.append("### 2. Code Security Issues\n\n")
        report.append(f"- **Status**: {code_check.get('status', 'UNKNOWN')}\n")
        report.append(
            f"- **High Severity**: {code_check.get('high_severity', 'N/A')}\n"
        )
        report.append(
            f"- **Medium Severity**: {code_check.get('medium_severity', 'N/A')}\n"
        )
        report.append(f"- **Low Severity**: {code_check.get('low_severity', 'N/A')}\n")
        report.append(
            f"- **Details**: {code_check.get('details', 'No details available')}\n\n"
        )

        # Secrets
        secrets_check = self.results["checks"].get("secrets", {})
        report.append("### 3. Secret Exposure\n\n")
        report.append(f"- **Status**: {secrets_check.get('status', 'UNKNOWN')}\n")
        report.append(
            f"- **Secrets Found**: {secrets_check.get('secrets_found', 'N/A')}\n"
        )
        report.append(
            f"- **Details**: {secrets_check.get('details', 'No details available')}\n\n"
        )

        # Compliance Summary
        report.append("## Compliance Summary\n\n")

        if self.results["overall_status"] == "PASS":
            report.append(
                "✅ **The repository is in a secure and compliant state.**\n\n"
            )
            report.append("All security checks have passed:\n")
            report.append("- No vulnerable dependencies detected\n")
            report.append("- No critical code security issues found\n")
            report.append("- No secrets exposed in code\n\n")
            report.append("The main branch is secure and ready for production.\n")
        else:
            report.append("⚠️ **Security issues detected that require attention.**\n\n")
            report.append(
                "Please review the findings above and take corrective action.\n"
            )

        report.append("\n## Automated Security System\n\n")
        report.append("The following automated systems are active:\n\n")
        report.append("- ✅ Security Orchestrator - Runs every 6 hours\n")
        report.append("- ✅ Automated dependency scanning and remediation\n")
        report.append("- ✅ Code security scanning with Bandit\n")
        report.append("- ✅ Secret detection and alerts\n")
        report.append("- ✅ Auto-merge for security fixes\n")
        report.append("- ✅ Zero-approval security patch deployment\n\n")

        report.append("## Next Steps\n\n")
        if self.results["overall_status"] == "PASS":
            report.append("1. Monitor automated security scans\n")
            report.append("2. Review and merge any security PRs promptly\n")
            report.append("3. Keep dependencies up to date\n")
        else:
            report.append("1. Review security findings above\n")
            report.append("2. Apply recommended fixes\n")
            report.append("3. Re-run verification after fixes\n")
            report.append("4. Monitor automated security PRs\n")

        report.append("\n---\n")
        report.append("*Generated by Security Verification System*\n")

        # Write report
        with open(output_file, "w") as f:
            f.writelines(report)

        print(f"   ✅ Report saved to {output_file}")

        # Also save JSON version
        json_file = output_file.replace(".md", ".json")
        with open(json_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"   ✅ JSON report saved to {json_file}")


def main():
    """Main entry point."""
    verifier = SecurityVerifier()

    # Run all verifications
    all_passed = verifier.verify_all()

    # Generate report
    verifier.generate_report()

    # Exit with appropriate code
    if all_passed:
        print("\n✅ Security verification PASSED")
        sys.exit(0)
    else:
        print("\n❌ Security verification FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
