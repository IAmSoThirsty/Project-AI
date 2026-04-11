#!/usr/bin/env python3
"""
Pre-Deployment Validation Script
Sovereign Governance Substrate

MISSION: Comprehensive pre-flight validation before production deployment

FEATURES:
- Environment configuration validation
- Image verification
- Kubernetes resource validation
- Database connectivity checks
- Secret and ConfigMap validation
- Resource quota verification
- Network policy validation
- Security compliance checks
- Dependency validation

USAGE:
    python pre_deploy_check.py --environment production
    python pre_deploy_check.py --environment staging --comprehensive
    python pre_deploy_check.py --environment production --json

AUTHOR: Deployment Architect
DATE: 2026-04-09
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


class Color:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'


class PreDeploymentValidator:
    """Comprehensive pre-deployment validation"""
    
    def __init__(
        self,
        environment: str,
        namespace: str = None,
        image: str = None,
        comprehensive: bool = False,
        json_output: bool = False,
        verbose: bool = False
    ):
        self.environment = environment
        self.namespace = namespace or f"project-ai-{environment}"
        self.image = image or "ghcr.io/iamsothirsty/project-ai:latest"
        self.comprehensive = comprehensive
        self.json_output = json_output
        self.verbose = verbose
        
        self.results = {
            "environment": environment,
            "namespace": self.namespace,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {},
            "warnings": [],
            "errors": [],
            "overall": "UNKNOWN"
        }
        
        self.check_count = 0
        self.passed_count = 0
        self.failed_count = 0
        self.warning_count = 0
    
    def log(self, level: str, message: str):
        """Log message with color coding"""
        if self.json_output:
            return
        
        prefix = {
            "INFO": f"{Color.GREEN}✓{Color.NC}",
            "WARN": f"{Color.YELLOW}⚠{Color.NC}",
            "ERROR": f"{Color.RED}✗{Color.NC}",
            "DEBUG": f"{Color.CYAN}→{Color.NC}",
            "STEP": f"{Color.MAGENTA}▶{Color.NC}"
        }.get(level, "·")
        
        print(f"{prefix} {message}")
    
    def run_command(self, cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
        """Run shell command and return result"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timeout"
        except Exception as e:
            return 1, "", str(e)
    
    def record_check(self, name: str, passed: bool, message: str, details: Dict[str, Any] = None):
        """Record check result"""
        self.check_count += 1
        
        if passed:
            self.passed_count += 1
            level = "INFO"
        else:
            self.failed_count += 1
            level = "ERROR"
            self.results["errors"].append(message)
        
        self.results["checks"][name] = {
            "passed": passed,
            "message": message,
            "details": details or {}
        }
        
        self.log(level, f"{name}: {message}")
    
    def record_warning(self, message: str):
        """Record warning"""
        self.warning_count += 1
        self.results["warnings"].append(message)
        self.log("WARN", message)
    
    # ========================================================================
    # Prerequisites Checks
    # ========================================================================
    
    def check_prerequisites(self) -> bool:
        """Check required tools are installed"""
        self.log("STEP", "Checking prerequisites...")
        
        required_tools = ["kubectl", "docker", "jq"]
        all_found = True
        
        for tool in required_tools:
            returncode, stdout, stderr = self.run_command(["which", tool])
            passed = returncode == 0
            
            if not passed:
                all_found = False
            
            self.record_check(
                f"Tool: {tool}",
                passed,
                "Available" if passed else "Not found",
                {"path": stdout.strip() if passed else None}
            )
        
        return all_found
    
    # ========================================================================
    # Kubernetes Cluster Checks
    # ========================================================================
    
    def check_cluster_connectivity(self) -> bool:
        """Check Kubernetes cluster connectivity"""
        self.log("STEP", "Checking Kubernetes cluster connectivity...")
        
        returncode, stdout, stderr = self.run_command(["kubectl", "cluster-info"])
        passed = returncode == 0
        
        self.record_check(
            "Kubernetes cluster",
            passed,
            "Connected" if passed else f"Not accessible: {stderr}",
            {"cluster_info": stdout if passed else None}
        )
        
        return passed
    
    def check_namespace_exists(self) -> bool:
        """Check namespace exists"""
        self.log("STEP", "Checking namespace exists...")
        
        returncode, stdout, stderr = self.run_command([
            "kubectl", "get", "namespace", self.namespace
        ])
        
        passed = returncode == 0
        
        self.record_check(
            "Namespace exists",
            passed,
            f"Namespace '{self.namespace}' exists" if passed else f"Namespace not found",
            {"namespace": self.namespace}
        )
        
        return passed
    
    def check_resource_quotas(self) -> bool:
        """Check resource quotas are sufficient"""
        self.log("STEP", "Checking resource quotas...")
        
        returncode, stdout, stderr = self.run_command([
            "kubectl", "get", "resourcequota",
            "-n", self.namespace,
            "-o", "json"
        ])
        
        if returncode != 0:
            self.record_warning("No resource quotas configured")
            return True  # Not a failure, just a warning
        
        try:
            quotas = json.loads(stdout)
            if quotas.get("items"):
                self.record_check(
                    "Resource quotas",
                    True,
                    f"Found {len(quotas['items'])} quota(s)",
                    {"quotas": quotas["items"]}
                )
            else:
                self.record_warning("No resource quotas found")
        except json.JSONDecodeError:
            self.record_warning("Failed to parse resource quotas")
        
        return True
    
    # ========================================================================
    # Configuration Checks
    # ========================================================================
    
    def check_secrets_exist(self) -> bool:
        """Check required secrets exist"""
        self.log("STEP", "Checking secrets exist...")
        
        required_secrets = ["project-ai-secrets"]
        all_exist = True
        
        for secret_name in required_secrets:
            returncode, stdout, stderr = self.run_command([
                "kubectl", "get", "secret", secret_name,
                "-n", self.namespace
            ])
            
            passed = returncode == 0
            if not passed:
                all_exist = False
            
            self.record_check(
                f"Secret: {secret_name}",
                passed,
                "Exists" if passed else "Not found"
            )
        
        return all_exist
    
    def check_configmaps_exist(self) -> bool:
        """Check required ConfigMaps exist"""
        self.log("STEP", "Checking ConfigMaps exist...")
        
        required_configmaps = ["project-ai-config"]
        all_exist = True
        
        for cm_name in required_configmaps:
            returncode, stdout, stderr = self.run_command([
                "kubectl", "get", "configmap", cm_name,
                "-n", self.namespace
            ])
            
            passed = returncode == 0
            if not passed:
                all_exist = False
            
            self.record_check(
                f"ConfigMap: {cm_name}",
                passed,
                "Exists" if passed else "Not found"
            )
        
        return all_exist
    
    # ========================================================================
    # Image Checks
    # ========================================================================
    
    def check_image_exists(self) -> bool:
        """Check Docker image exists and is pullable"""
        self.log("STEP", "Checking Docker image exists...")
        
        returncode, stdout, stderr = self.run_command([
            "docker", "pull", self.image
        ])
        
        passed = returncode == 0
        
        self.record_check(
            "Docker image",
            passed,
            f"Image '{self.image}' is pullable" if passed else f"Cannot pull image: {stderr}",
            {"image": self.image}
        )
        
        return passed
    
    def check_image_security(self) -> bool:
        """Check image for security vulnerabilities (if trivy available)"""
        if not self.comprehensive:
            return True
        
        self.log("STEP", "Checking image security...")
        
        # Check if trivy is available
        returncode, _, _ = self.run_command(["which", "trivy"])
        if returncode != 0:
            self.record_warning("Trivy not available - skipping security scan")
            return True
        
        # Run trivy scan
        returncode, stdout, stderr = self.run_command([
            "trivy", "image", "--severity", "HIGH,CRITICAL",
            "--format", "json", self.image
        ])
        
        if returncode != 0:
            self.record_warning(f"Image security scan failed: {stderr}")
            return True  # Don't fail deployment
        
        try:
            scan_results = json.loads(stdout)
            critical_count = 0
            high_count = 0
            
            for result in scan_results.get("Results", []):
                for vuln in result.get("Vulnerabilities", []):
                    severity = vuln.get("Severity", "")
                    if severity == "CRITICAL":
                        critical_count += 1
                    elif severity == "HIGH":
                        high_count += 1
            
            if critical_count > 0 or high_count > 0:
                self.record_warning(
                    f"Image has {critical_count} CRITICAL and {high_count} HIGH vulnerabilities"
                )
            else:
                self.record_check(
                    "Image security",
                    True,
                    "No HIGH or CRITICAL vulnerabilities found"
                )
        except json.JSONDecodeError:
            self.record_warning("Failed to parse security scan results")
        
        return True
    
    # ========================================================================
    # Database Checks
    # ========================================================================
    
    def check_database_connectivity(self) -> bool:
        """Check database is accessible from cluster"""
        self.log("STEP", "Checking database connectivity...")
        
        # Try to find database service
        returncode, stdout, stderr = self.run_command([
            "kubectl", "get", "service", "postgres",
            "-n", self.namespace
        ])
        
        if returncode != 0:
            self.record_warning("Database service not found - skipping connectivity check")
            return True
        
        # Create a test pod to check connectivity
        test_pod_yaml = f"""
apiVersion: v1
kind: Pod
metadata:
  name: db-connectivity-test
  namespace: {self.namespace}
spec:
  restartPolicy: Never
  containers:
  - name: test
    image: busybox:1.36
    command: ['sh', '-c', 'nc -zv postgres.{self.namespace}.svc.cluster.local 5432']
"""
        
        # Apply test pod
        returncode, stdout, stderr = self.run_command(
            ["kubectl", "apply", "-f", "-"],
        )
        
        if returncode != 0:
            self.record_warning("Cannot create database connectivity test pod")
            return True
        
        # Wait for pod to complete
        self.run_command([
            "kubectl", "wait", "--for=condition=complete",
            "--timeout=30s", "pod/db-connectivity-test",
            "-n", self.namespace
        ])
        
        # Check pod status
        returncode, stdout, stderr = self.run_command([
            "kubectl", "get", "pod", "db-connectivity-test",
            "-n", self.namespace,
            "-o", "jsonpath={.status.phase}"
        ])
        
        passed = stdout.strip() == "Succeeded"
        
        self.record_check(
            "Database connectivity",
            passed,
            "Database is accessible" if passed else "Database not accessible"
        )
        
        # Cleanup test pod
        self.run_command([
            "kubectl", "delete", "pod", "db-connectivity-test",
            "-n", self.namespace,
            "--grace-period=0", "--force"
        ])
        
        return passed
    
    # ========================================================================
    # Node Resource Checks
    # ========================================================================
    
    def check_node_resources(self) -> bool:
        """Check cluster nodes have sufficient resources"""
        if not self.comprehensive:
            return True
        
        self.log("STEP", "Checking node resources...")
        
        returncode, stdout, stderr = self.run_command([
            "kubectl", "top", "nodes"
        ])
        
        if returncode != 0:
            self.record_warning("Metrics server not available - skipping resource check")
            return True
        
        # Parse output
        lines = stdout.strip().split('\n')[1:]  # Skip header
        high_cpu_nodes = []
        high_mem_nodes = []
        
        for line in lines:
            parts = line.split()
            if len(parts) >= 5:
                node_name = parts[0]
                cpu_usage = parts[2]
                mem_usage = parts[4]
                
                # Check if usage is high (>80%)
                if cpu_usage.endswith('%') and int(cpu_usage[:-1]) > 80:
                    high_cpu_nodes.append(node_name)
                if mem_usage.endswith('%') and int(mem_usage[:-1]) > 80:
                    high_mem_nodes.append(node_name)
        
        if high_cpu_nodes or high_mem_nodes:
            self.record_warning(
                f"High resource usage detected - CPU: {high_cpu_nodes}, Memory: {high_mem_nodes}"
            )
        else:
            self.record_check(
                "Node resources",
                True,
                "Sufficient resources available"
            )
        
        return True
    
    # ========================================================================
    # Deployment State Checks
    # ========================================================================
    
    def check_current_deployment_healthy(self) -> bool:
        """Check current deployment is healthy before updating"""
        self.log("STEP", "Checking current deployment health...")
        
        returncode, stdout, stderr = self.run_command([
            "kubectl", "get", "deployment", "project-ai-app",
            "-n", self.namespace,
            "-o", "json"
        ])
        
        if returncode != 0:
            # No existing deployment - this is a new deployment
            self.record_check(
                "Current deployment",
                True,
                "No existing deployment (new deployment)"
            )
            return True
        
        try:
            deployment = json.loads(stdout)
            status = deployment.get("status", {})
            
            replicas = status.get("replicas", 0)
            ready_replicas = status.get("readyReplicas", 0)
            updated_replicas = status.get("updatedReplicas", 0)
            available_replicas = status.get("availableReplicas", 0)
            
            healthy = (
                replicas > 0 and
                ready_replicas == replicas and
                updated_replicas == replicas and
                available_replicas == replicas
            )
            
            self.record_check(
                "Current deployment health",
                healthy,
                f"{ready_replicas}/{replicas} replicas ready" if healthy else "Deployment not fully healthy",
                {
                    "replicas": replicas,
                    "ready": ready_replicas,
                    "updated": updated_replicas,
                    "available": available_replicas
                }
            )
            
            return healthy
        except json.JSONDecodeError:
            self.record_warning("Failed to parse deployment status")
            return True
    
    # ========================================================================
    # Network Policy Checks
    # ========================================================================
    
    def check_network_policies(self) -> bool:
        """Check network policies are configured"""
        if not self.comprehensive:
            return True
        
        self.log("STEP", "Checking network policies...")
        
        returncode, stdout, stderr = self.run_command([
            "kubectl", "get", "networkpolicy",
            "-n", self.namespace,
            "-o", "json"
        ])
        
        if returncode != 0:
            self.record_warning("Failed to get network policies")
            return True
        
        try:
            policies = json.loads(stdout)
            policy_count = len(policies.get("items", []))
            
            if policy_count == 0:
                self.record_warning("No network policies configured")
            else:
                self.record_check(
                    "Network policies",
                    True,
                    f"Found {policy_count} network policy(ies)",
                    {"count": policy_count}
                )
        except json.JSONDecodeError:
            self.record_warning("Failed to parse network policies")
        
        return True
    
    # ========================================================================
    # Main Execution
    # ========================================================================
    
    def run_all_checks(self) -> bool:
        """Run all validation checks"""
        if not self.json_output:
            print("=" * 80)
            print("PRE-DEPLOYMENT VALIDATION")
            print("=" * 80)
            print(f"Environment: {self.environment}")
            print(f"Namespace:   {self.namespace}")
            print(f"Image:       {self.image}")
            print("=" * 80)
            print()
        
        # Run all checks
        checks = [
            self.check_prerequisites,
            self.check_cluster_connectivity,
            self.check_namespace_exists,
            self.check_secrets_exist,
            self.check_configmaps_exist,
            self.check_image_exists,
            self.check_image_security,
            self.check_database_connectivity,
            self.check_current_deployment_healthy,
            self.check_resource_quotas,
            self.check_node_resources,
            self.check_network_policies,
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.record_check(
                    check.__name__,
                    False,
                    f"Check failed with exception: {str(e)}"
                )
        
        # Determine overall result
        overall_passed = self.failed_count == 0
        self.results["overall"] = "PASS" if overall_passed else "FAIL"
        
        # Print summary
        if not self.json_output:
            print()
            print("=" * 80)
            print("VALIDATION SUMMARY")
            print("=" * 80)
            print(f"Total Checks:  {self.check_count}")
            print(f"{Color.GREEN}Passed:        {self.passed_count}{Color.NC}")
            print(f"{Color.RED}Failed:        {self.failed_count}{Color.NC}")
            print(f"{Color.YELLOW}Warnings:      {self.warning_count}{Color.NC}")
            print()
            
            if overall_passed:
                print(f"{Color.GREEN}✓ VALIDATION PASSED{Color.NC}")
                print("Deployment can proceed.")
            else:
                print(f"{Color.RED}✗ VALIDATION FAILED{Color.NC}")
                print("Fix the errors before deploying.")
                print()
                print("Errors:")
                for error in self.results["errors"]:
                    print(f"  - {error}")
            
            if self.warning_count > 0:
                print()
                print("Warnings:")
                for warning in self.results["warnings"]:
                    print(f"  - {warning}")
            
            print("=" * 80)
        
        return overall_passed
    
    def output_json(self):
        """Output results as JSON"""
        print(json.dumps(self.results, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Pre-deployment validation for Sovereign Governance Substrate"
    )
    
    parser.add_argument(
        "--environment",
        required=True,
        choices=["dev", "staging", "production"],
        help="Target environment"
    )
    
    parser.add_argument(
        "--namespace",
        help="Kubernetes namespace (default: project-ai-{environment})"
    )
    
    parser.add_argument(
        "--image",
        help="Docker image to validate (default: ghcr.io/iamsothirsty/project-ai:latest)"
    )
    
    parser.add_argument(
        "--comprehensive",
        action="store_true",
        help="Run comprehensive checks (slower but more thorough)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    validator = PreDeploymentValidator(
        environment=args.environment,
        namespace=args.namespace,
        image=args.image,
        comprehensive=args.comprehensive,
        json_output=args.json,
        verbose=args.verbose
    )
    
    success = validator.run_all_checks()
    
    if args.json:
        validator.output_json()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
