#!/usr/bin/env python3
"""
TK8S Validation Script
Verifies that TK8S deployment meets all civilization-grade requirements
"""

import json
import subprocess
import sys


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def run_kubectl(args: list[str]) -> tuple[bool, str]:
    """Run kubectl command and return success status and output"""
    try:
        result = subprocess.run(
            ["kubectl"] + args, capture_output=True, text=True, timeout=30
        )
        return result.returncode == 0, result.stdout
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except FileNotFoundError:
        return False, "kubectl not found"


def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_check(name: str, passed: bool, details: str = ""):
    """Print check result"""
    status = (
        f"{Colors.GREEN}✓ PASS{Colors.END}"
        if passed
        else f"{Colors.RED}✗ FAIL{Colors.END}"
    )
    print(f"{status} {name}")
    if details:
        print(f"  {Colors.YELLOW}{details}{Colors.END}")


def check_namespaces() -> int:
    """Verify all required namespaces exist"""
    print_header("TK8S Namespace Verification")

    required_namespaces = [
        "project-ai-core",
        "project-ai-security",
        "project-ai-memory",
        "project-ai-eca",
        "project-ai-monitoring",
        "project-ai-system",
    ]

    success, output = run_kubectl(["get", "namespaces", "-o", "json"])
    if not success:
        print_check("Get namespaces", False, "Failed to query namespaces")
        return 0

    namespaces = json.loads(output)
    existing_ns = {ns["metadata"]["name"] for ns in namespaces["items"]}

    passed = 0
    for ns in required_namespaces:
        exists = ns in existing_ns
        print_check(f"Namespace {ns}", exists)
        if exists:
            passed += 1

    return passed


def check_network_policies() -> int:
    """Verify network policies are in place"""
    print_header("Network Policy Verification")

    policies_to_check = [
        ("project-ai-eca", "deny-all-default"),
        ("project-ai-eca", "eca-egress-only"),
        ("project-ai-core", "project-ai-core-policy"),
        ("project-ai-security", "project-ai-security-policy"),
        ("project-ai-monitoring", "project-ai-monitoring-policy"),
    ]

    passed = 0
    for namespace, policy_name in policies_to_check:
        success, _ = run_kubectl(
            ["get", "networkpolicy", policy_name, "-n", namespace, "-o", "json"]
        )
        print_check(f"NetworkPolicy {policy_name} in {namespace}", success)
        if success:
            passed += 1

    return passed


def check_rbac() -> int:
    """Verify RBAC is configured"""
    print_header("RBAC Verification")

    service_accounts = [
        ("project-ai-core", "project-ai-core"),
        ("project-ai-eca", "project-ai-eca"),
        ("project-ai-security", "project-ai-security"),
        ("project-ai-monitoring", "project-ai-monitoring"),
    ]

    passed = 0
    for namespace, sa_name in service_accounts:
        success, _ = run_kubectl(
            ["get", "serviceaccount", sa_name, "-n", namespace, "-o", "json"]
        )
        print_check(f"ServiceAccount {sa_name} in {namespace}", success)
        if success:
            passed += 1

    return passed


def check_kyverno_policies() -> int:
    """Verify Kyverno policies are installed"""
    print_header("Kyverno Policy Verification")

    required_policies = [
        "tk8s-verify-image-signatures",
        "tk8s-require-sbom-annotation",
        "tk8s-no-mutable-containers",
        "tk8s-no-shell-access",
        "tk8s-require-readonly-root-filesystem",
        "tk8s-eca-isolation-enforcement",
        "tk8s-require-resource-limits",
    ]

    passed = 0
    for policy_name in required_policies:
        success, _ = run_kubectl(["get", "clusterpolicy", policy_name, "-o", "json"])
        print_check(f"ClusterPolicy {policy_name}", success)
        if success:
            passed += 1

    return passed


def check_deployments() -> int:
    """Verify deployments are running"""
    print_header("Deployment Verification")

    deployments = [
        ("project-ai-core", "project-ai-core", 3),
        ("project-ai-eca", "project-ai-eca", 2),
    ]

    passed = 0
    for namespace, deployment_name, expected_replicas in deployments:
        success, output = run_kubectl(
            ["get", "deployment", deployment_name, "-n", namespace, "-o", "json"]
        )

        if not success:
            print_check(f"Deployment {deployment_name}", False, "Not found")
            continue

        deployment = json.loads(output)
        status = deployment.get("status", {})
        ready_replicas = status.get("readyReplicas", 0)
        desired_replicas = status.get("replicas", 0)

        is_ready = ready_replicas == desired_replicas == expected_replicas
        details = (
            f"{ready_replicas}/{desired_replicas} ready (expected {expected_replicas})"
        )

        print_check(f"Deployment {deployment_name} in {namespace}", is_ready, details)
        if is_ready:
            passed += 1

    return passed


def check_pod_security() -> int:
    """Verify pod security contexts"""
    print_header("Pod Security Context Verification")

    namespaces_to_check = ["project-ai-core", "project-ai-eca"]

    passed = 0
    total = 0

    for namespace in namespaces_to_check:
        success, output = run_kubectl(["get", "pods", "-n", namespace, "-o", "json"])

        if not success:
            continue

        pods = json.loads(output)
        for pod in pods["items"]:
            pod_name = pod["metadata"]["name"]
            security_context = pod["spec"].get("securityContext", {})

            total += 1

            # Check security context
            run_as_non_root = security_context.get("runAsNonRoot", False)

            # Check container security
            containers = pod["spec"].get("containers", [])
            all_readonly = True
            for container in containers:
                container_sc = container.get("securityContext", {})
                if not container_sc.get("readOnlyRootFilesystem", False):
                    all_readonly = False
                    break

            is_secure = run_as_non_root and all_readonly
            details = []
            if not run_as_non_root:
                details.append("runAsNonRoot not set")
            if not all_readonly:
                details.append("readOnlyRootFilesystem not set")

            print_check(
                f"Pod {pod_name} security",
                is_secure,
                ", ".join(details) if details else "",
            )

            if is_secure:
                passed += 1

    return passed


def check_argocd_apps() -> int:
    """Verify ArgoCD applications"""
    print_header("ArgoCD Application Verification")

    apps = [
        "project-ai-core",
        "project-ai-eca",
        "project-ai-security",
        "project-ai-network-policies",
        "project-ai-rbac",
    ]

    passed = 0
    for app_name in apps:
        success, output = run_kubectl(
            ["get", "application", app_name, "-n", "argocd", "-o", "json"]
        )

        if not success:
            print_check(f"ArgoCD Application {app_name}", False, "Not found")
            continue

        app = json.loads(output)
        status = app.get("status", {})
        sync_status = status.get("sync", {}).get("status", "Unknown")
        health_status = status.get("health", {}).get("status", "Unknown")

        is_healthy = sync_status == "Synced" and health_status == "Healthy"
        details = f"Sync: {sync_status}, Health: {health_status}"

        print_check(f"ArgoCD Application {app_name}", is_healthy, details)
        if is_healthy:
            passed += 1

    return passed


def main():
    """Main validation function"""
    print(f"\n{Colors.BOLD}TK8S Civilization-Grade Validation{Colors.END}")
    print(f"{Colors.BOLD}Thirsty's Kubernetes Deployment Verification{Colors.END}")

    results = {}

    # Run all checks
    results["namespaces"] = check_namespaces()
    results["network_policies"] = check_network_policies()
    results["rbac"] = check_rbac()
    results["kyverno_policies"] = check_kyverno_policies()
    results["deployments"] = check_deployments()
    results["pod_security"] = check_pod_security()
    results["argocd_apps"] = check_argocd_apps()

    # Print summary
    print_header("Validation Summary")

    total_passed = sum(results.values())

    # Expected counts
    expected = {
        "namespaces": 6,
        "network_policies": 5,
        "rbac": 4,
        "kyverno_policies": 7,
        "deployments": 2,
        "pod_security": 5,  # approximate
        "argocd_apps": 5,
    }

    for check, count in results.items():
        exp = expected.get(check, 0)
        percentage = (count / exp * 100) if exp > 0 else 0
        status = (
            f"{Colors.GREEN}✓{Colors.END}"
            if percentage >= 80
            else f"{Colors.RED}✗{Colors.END}"
        )
        print(f"{status} {check}: {count}/{exp} ({percentage:.0f}%)")

    total_expected = sum(expected.values())
    overall_percentage = (
        (total_passed / total_expected * 100) if total_expected > 0 else 0
    )

    print(
        f"\n{Colors.BOLD}Overall Score: {total_passed}/{total_expected} ({overall_percentage:.0f}%){Colors.END}"
    )

    if overall_percentage >= 90:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🏛️ CIVILIZATION GRADE ACHIEVED{Colors.END}")
        return 0
    elif overall_percentage >= 70:
        print(
            f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  APPROACHING CIVILIZATION GRADE{Colors.END}"
        )
        print(f"{Colors.YELLOW}Review failed checks and remediate{Colors.END}")
        return 1
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ BELOW CIVILIZATION GRADE{Colors.END}")
        print(f"{Colors.RED}Significant issues detected - review and fix{Colors.END}")
        return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Validation interrupted{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Validation error: {e}{Colors.END}")
        sys.exit(1)
