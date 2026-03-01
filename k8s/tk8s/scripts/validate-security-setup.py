#!/usr/bin/env python3
"""
TK8S Security Validation Script
Validates KMS setup, Kyverno policies, and network policies
"""

import json
import subprocess
import sys
from dataclasses import dataclass

# Color codes
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"


@dataclass
class ValidationResult:
    name: str
    passed: bool
    message: str
    details: str = ""


class SecurityValidator:
    def __init__(self):
        self.results: list[ValidationResult] = []

    def run_command(self, cmd: list[str], check: bool = True) -> tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=check)
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return e.returncode, e.stdout, e.stderr
        except Exception as e:
            return 1, "", str(e)

    def check_kubectl_access(self) -> ValidationResult:
        """Check if kubectl is accessible and authenticated"""
        code, stdout, stderr = self.run_command(
            ["kubectl", "version", "--client"], check=False
        )
        if code == 0:
            code2, stdout2, stderr2 = self.run_command(
                ["kubectl", "cluster-info"], check=False
            )
            if code2 == 0:
                return ValidationResult(
                    "kubectl Access",
                    True,
                    "kubectl is configured and cluster is reachable",
                    stdout2.split("\n")[0],
                )
            else:
                return ValidationResult(
                    "kubectl Access",
                    False,
                    "kubectl is installed but cannot reach cluster",
                    stderr2,
                )
        else:
            return ValidationResult(
                "kubectl Access",
                False,
                "kubectl is not installed or not in PATH",
                stderr,
            )

    def check_kyverno_installed(self) -> ValidationResult:
        """Check if Kyverno is installed"""
        code, stdout, stderr = self.run_command(
            ["kubectl", "get", "deployment", "-n", "kyverno", "kyverno"], check=False
        )
        if code == 0:
            return ValidationResult(
                "Kyverno Installation", True, "Kyverno is installed and running", stdout
            )
        else:
            return ValidationResult(
                "Kyverno Installation",
                False,
                "Kyverno is not installed in the cluster",
                "Run: kubectl apply -f https://github.com/kyverno/kyverno/releases/latest/download/install.yaml",
            )

    def check_cosign_secret(self) -> ValidationResult:
        """Check if cosign public key secret exists"""
        code, stdout, stderr = self.run_command(
            ["kubectl", "get", "secret", "cosign-public-key", "-n", "kyverno"],
            check=False,
        )
        if code == 0:
            return ValidationResult(
                "Cosign Public Key Secret",
                True,
                "cosign-public-key secret exists in kyverno namespace",
                stdout,
            )
        else:
            return ValidationResult(
                "Cosign Public Key Secret",
                False,
                "cosign-public-key secret not found in kyverno namespace",
                "Run: kubectl create secret generic cosign-public-key --from-file=cosign.pub=<path> -n kyverno",
            )

    def check_kyverno_policies(self) -> ValidationResult:
        """Check if critical Kyverno policies are deployed"""
        code, stdout, stderr = self.run_command(
            ["kubectl", "get", "clusterpolicy", "-o", "json"], check=False
        )
        if code != 0:
            return ValidationResult(
                "Kyverno Policies", False, "Cannot list ClusterPolicies", stderr
            )

        try:
            policies = json.loads(stdout)
            policy_names = [p["metadata"]["name"] for p in policies.get("items", [])]

            required_policies = ["require-kms-cosign-signatures", "protect-kyverno"]

            missing = [p for p in required_policies if p not in policy_names]

            if not missing:
                return ValidationResult(
                    "Kyverno Policies",
                    True,
                    f"All {len(required_policies)} critical policies are deployed",
                    f"Policies: {', '.join(policy_names)}",
                )
            else:
                return ValidationResult(
                    "Kyverno Policies",
                    False,
                    f"Missing {len(missing)} critical policies",
                    f"Missing: {', '.join(missing)}",
                )
        except json.JSONDecodeError:
            return ValidationResult(
                "Kyverno Policies",
                False,
                "Cannot parse ClusterPolicy JSON",
                stdout[:200],
            )

    def check_network_policies(self) -> ValidationResult:
        """Check if default-deny network policies are deployed"""
        code, stdout, stderr = self.run_command(
            ["kubectl", "get", "networkpolicy", "-A", "-o", "json"], check=False
        )
        if code != 0:
            return ValidationResult(
                "Network Policies", False, "Cannot list NetworkPolicies", stderr
            )

        try:
            netpols = json.loads(stdout)
            default_deny_count = 0

            for np in netpols.get("items", []):
                name = np["metadata"]["name"]
                if "default-deny" in name:
                    default_deny_count += 1

            if default_deny_count >= 3:  # Expecting at least 3 namespaces
                return ValidationResult(
                    "Network Policies",
                    True,
                    f"Found {default_deny_count} default-deny network policies",
                    "Zero-trust networking is enabled",
                )
            else:
                return ValidationResult(
                    "Network Policies",
                    default_deny_count != 0,
                    f"Found {default_deny_count} default-deny policies (expected 3+)",
                    "Some namespaces may not have default-deny policies",
                )
        except json.JSONDecodeError:
            return ValidationResult(
                "Network Policies",
                False,
                "Cannot parse NetworkPolicy JSON",
                stdout[:200],
            )

    def check_pod_security_admission(self) -> ValidationResult:
        """Check if namespaces have Pod Security Admission labels"""
        code, stdout, stderr = self.run_command(
            [
                "kubectl",
                "get",
                "namespace",
                "-l",
                "app.kubernetes.io/name=project-ai",
                "-o",
                "json",
            ],
            check=False,
        )
        if code != 0:
            return ValidationResult(
                "Pod Security Admission", False, "Cannot list namespaces", stderr
            )

        try:
            namespaces = json.loads(stdout)
            compliant_count = 0
            total_count = len(namespaces.get("items", []))

            for ns in namespaces.get("items", []):
                labels = ns["metadata"].get("labels", {})
                has_enforce = (
                    labels.get("pod-security.kubernetes.io/enforce") == "restricted"
                )
                has_audit = (
                    labels.get("pod-security.kubernetes.io/audit") == "restricted"
                )
                has_warn = labels.get("pod-security.kubernetes.io/warn") == "restricted"

                if has_enforce and has_audit and has_warn:
                    compliant_count += 1

            if compliant_count == total_count and total_count > 0:
                return ValidationResult(
                    "Pod Security Admission",
                    True,
                    f"All {total_count} project-ai namespaces have PSA labels",
                    "Restricted pod security standards enforced",
                )
            else:
                return ValidationResult(
                    "Pod Security Admission",
                    compliant_count != 0,
                    f"{compliant_count}/{total_count} namespaces have PSA labels",
                    "Some namespaces may not enforce restricted standards",
                )
        except json.JSONDecodeError:
            return ValidationResult(
                "Pod Security Admission",
                False,
                "Cannot parse namespace JSON",
                stdout[:200],
            )

    def check_gcp_kms(self) -> ValidationResult:
        """Check if GCP KMS key is accessible"""
        code, stdout, stderr = self.run_command(["which", "gcloud"], check=False)
        if code != 0:
            return ValidationResult(
                "GCP KMS Access",
                False,
                "gcloud CLI not found",
                "Install gcloud: https://cloud.google.com/sdk/docs/install",
            )

        # Try to list KMS keys (this will fail if not authenticated or key doesn't exist)
        code, stdout, stderr = self.run_command(
            [
                "gcloud",
                "kms",
                "keys",
                "list",
                "--location=us-central1",
                "--keyring=tk8s-keyring",
            ],
            check=False,
        )
        if code == 0 and "cosign-key" in stdout:
            return ValidationResult(
                "GCP KMS Access",
                True,
                "GCP KMS key is accessible",
                "Key: tk8s-keyring/cosign-key",
            )
        else:
            return ValidationResult(
                "GCP KMS Access",
                False,
                "Cannot access GCP KMS or key doesn't exist",
                "Run: ./k8s/tk8s/scripts/setup-gcp-kms.sh",
            )

    def run_all_checks(self):
        """Run all validation checks"""
        print(
            f"{BLUE}╔══════════════════════════════════════════════════════════════════════╗{NC}"
        )
        print(
            f"{BLUE}║           TK8S Security Validation                                   ║{NC}"
        )
        print(
            f"{BLUE}╚══════════════════════════════════════════════════════════════════════╝{NC}"
        )
        print()

        checks = [
            self.check_kubectl_access,
            self.check_kyverno_installed,
            self.check_cosign_secret,
            self.check_kyverno_policies,
            self.check_network_policies,
            self.check_pod_security_admission,
            self.check_gcp_kms,
        ]

        for check in checks:
            result = check()
            self.results.append(result)

            # Print result
            status = f"{GREEN}✅{NC}" if result.passed else f"{RED}❌{NC}"
            print(f"{status} {result.name}")
            print(f"   {result.message}")
            if result.details:
                print(f"   {YELLOW}{result.details}{NC}")
            print()

        # Summary
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        print(
            f"{BLUE}╔══════════════════════════════════════════════════════════════════════╗{NC}"
        )
        print(
            f"{BLUE}║           Validation Summary                                         ║{NC}"
        )
        print(
            f"{BLUE}╚══════════════════════════════════════════════════════════════════════╝{NC}"
        )
        print()

        if passed == total:
            print(f"{GREEN}✅ All {total} checks passed!{NC}")
            print(f"{GREEN}   Enterprise security is properly configured.{NC}")
            return 0
        else:
            print(f"{YELLOW}⚠️  {passed}/{total} checks passed{NC}")
            print(
                f"{YELLOW}   {total - passed} checks failed or require attention.{NC}"
            )
            print()
            print("Failed checks:")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.name}: {result.message}")
            return 1


def main():
    validator = SecurityValidator()
    exit_code = validator.run_all_checks()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
