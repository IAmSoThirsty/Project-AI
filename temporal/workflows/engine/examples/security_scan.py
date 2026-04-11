"""
Security Scan Workflow Example

Demonstrates a comprehensive security scanning workflow with:
- SAST (Static Application Security Testing)
- DAST (Dynamic Application Security Testing)
- Dependency vulnerability scanning
- Container image scanning
- License compliance checking
- Conditional remediation
"""

import asyncio
import logging
from typing import Any, Dict

from ..conditionals import Condition, ConditionalBranch, ConditionalLogic, ConditionOperator
from ..dag import DAG, DAGNode
from ..recovery import RecoveryAction, RecoveryStrategy
from ..retry import BackoffStrategy, CircuitBreaker, RetryPolicy
from ..workflow_engine import WorkflowDefinition

logger = logging.getLogger(__name__)


# Security scan tasks

async def sast_scan(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Run static application security testing"""
    logger.info("Running SAST scan")
    await asyncio.sleep(2.0)
    
    return {
        "vulnerabilities": {
            "critical": 0,
            "high": 2,
            "medium": 5,
            "low": 12,
        },
        "files_scanned": 456,
        "issues": [
            {"type": "sql_injection", "severity": "high", "file": "app/db.py"},
            {"type": "xss", "severity": "high", "file": "app/views.py"},
        ],
    }


async def dast_scan(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Run dynamic application security testing"""
    logger.info("Running DAST scan")
    await asyncio.sleep(3.0)
    
    return {
        "vulnerabilities": {
            "critical": 1,
            "high": 1,
            "medium": 3,
            "low": 8,
        },
        "endpoints_tested": 78,
        "issues": [
            {"type": "csrf", "severity": "critical", "endpoint": "/api/admin"},
            {"type": "insecure_headers", "severity": "high", "endpoint": "/"},
        ],
    }


async def dependency_scan(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Scan dependencies for known vulnerabilities"""
    logger.info("Scanning dependencies")
    await asyncio.sleep(1.5)
    
    return {
        "total_dependencies": 234,
        "vulnerable_dependencies": 3,
        "vulnerabilities": {
            "critical": 1,
            "high": 2,
            "medium": 0,
            "low": 0,
        },
        "issues": [
            {
                "package": "requests",
                "version": "2.25.0",
                "severity": "critical",
                "cve": "CVE-2023-12345",
            },
        ],
    }


async def container_scan(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Scan container images for vulnerabilities"""
    logger.info("Scanning container image")
    await asyncio.sleep(2.5)
    
    return {
        "image": "myapp:latest",
        "vulnerabilities": {
            "critical": 0,
            "high": 1,
            "medium": 4,
            "low": 15,
        },
        "base_image_issues": 8,
        "issues": [
            {
                "package": "openssl",
                "severity": "high",
                "cve": "CVE-2023-54321",
            },
        ],
    }


async def license_check(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Check license compliance"""
    logger.info("Checking license compliance")
    await asyncio.sleep(1.0)
    
    return {
        "total_dependencies": 234,
        "license_issues": 2,
        "non_compliant": [
            {"package": "gpl-lib", "license": "GPL-3.0"},
            {"package": "unknown-pkg", "license": "unknown"},
        ],
    }


async def aggregate_results(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Aggregate all security scan results"""
    logger.info("Aggregating security results")
    await asyncio.sleep(0.5)
    
    # In real implementation, would aggregate from previous node results
    total_critical = 2
    total_high = 6
    
    return {
        "total_vulnerabilities": {
            "critical": total_critical,
            "high": total_high,
            "medium": 12,
            "low": 35,
        },
        "risk_score": 78,  # 0-100
        "compliance_status": "fail",
        "requires_remediation": total_critical > 0 or total_high > 3,
    }


async def create_remediation_plan(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Create automated remediation plan"""
    logger.info("Creating remediation plan")
    await asyncio.sleep(1.0)
    
    return {
        "remediation_items": [
            {
                "issue": "CVE-2023-12345",
                "action": "upgrade_package",
                "package": "requests",
                "from_version": "2.25.0",
                "to_version": "2.31.0",
            },
            {
                "issue": "sql_injection",
                "action": "apply_patch",
                "file": "app/db.py",
                "patch_id": "patch-001",
            },
        ],
        "estimated_time_hours": 2,
    }


async def execute_auto_remediation(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Execute automated remediation"""
    logger.info("Executing auto-remediation")
    await asyncio.sleep(2.0)
    
    return {
        "remediated": 2,
        "failed": 0,
        "manual_review_required": 4,
    }


async def generate_report(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Generate security scan report"""
    logger.info("Generating security report")
    await asyncio.sleep(0.5)
    
    return {
        "report_url": "https://security.example.com/reports/scan-12345",
        "format": "pdf",
        "recipients": ["security-team@example.com"],
    }


def create_security_scan_workflow() -> WorkflowDefinition:
    """
    Create a comprehensive security scanning workflow
    
    Workflow stages:
    1. Parallel security scans (SAST, DAST, dependency, container, license)
    2. Aggregate results
    3. Conditional remediation based on severity
    4. Generate report
    """
    
    # Create DAG
    dag = DAG(
        name="security_scan",
        description="Comprehensive security scanning workflow",
    )

    # Define nodes
    nodes = {
        "sast": DAGNode(
            id="sast",
            task=sast_scan,
            dependencies=[],
            metadata={"scan_type": "static"},
        ),
        "dast": DAGNode(
            id="dast",
            task=dast_scan,
            dependencies=[],
            metadata={"scan_type": "dynamic"},
        ),
        "dependency": DAGNode(
            id="dependency",
            task=dependency_scan,
            dependencies=[],
            metadata={"scan_type": "dependency"},
        ),
        "container": DAGNode(
            id="container",
            task=container_scan,
            dependencies=[],
            metadata={"scan_type": "container"},
        ),
        "license": DAGNode(
            id="license",
            task=license_check,
            dependencies=[],
            metadata={"scan_type": "compliance"},
        ),
        "aggregate": DAGNode(
            id="aggregate",
            task=aggregate_results,
            dependencies=["sast", "dast", "dependency", "container", "license"],
            metadata={"stage": "analysis"},
        ),
        "remediation_plan": DAGNode(
            id="remediation_plan",
            task=create_remediation_plan,
            dependencies=["aggregate"],
            metadata={"stage": "remediation"},
        ),
        "auto_remediate": DAGNode(
            id="auto_remediate",
            task=execute_auto_remediation,
            dependencies=["remediation_plan"],
            metadata={"stage": "remediation"},
        ),
        "report": DAGNode(
            id="report",
            task=generate_report,
            dependencies=["aggregate"],
            metadata={"stage": "reporting"},
        ),
    }

    # Add nodes to DAG
    for node in nodes.values():
        dag.add_node(node)

    # Define retry policies with circuit breakers
    retry_policies = {
        "sast": RetryPolicy(
            max_attempts=3,
            initial_interval_ms=2000,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
        ),
        "dast": RetryPolicy(
            max_attempts=3,
            initial_interval_ms=2000,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            timeout_ms=60000,  # 60 second timeout
        ),
        "dependency": RetryPolicy(
            max_attempts=5,
            initial_interval_ms=1000,
            backoff_strategy=BackoffStrategy.EXPONENTIAL_JITTER,
        ),
        "container": RetryPolicy(
            max_attempts=3,
            initial_interval_ms=3000,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
        ),
        "auto_remediate": RetryPolicy(
            max_attempts=2,
            initial_interval_ms=5000,
        ),
    }

    # Define circuit breakers for external scan services
    circuit_breakers = {
        "dast": CircuitBreaker(
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=120,
        ),
        "dependency": CircuitBreaker(
            failure_threshold=5,
            success_threshold=2,
            timeout_seconds=60,
        ),
    }

    # Define conditional logic for remediation
    conditional_logic = {
        "remediation_plan": ConditionalLogic(
            branches=[
                ConditionalBranch(
                    condition=Condition(
                        operator=ConditionOperator.EQ,
                        left="$aggregate.requires_remediation",
                        right=True,
                    ),
                    action="remediation_plan",
                ),
            ],
            default_action="report",  # Skip remediation if not required
        ),
    }

    # Define recovery strategies
    recovery_strategies = {
        "sast": RecoveryStrategy(
            name="skip_sast_on_failure",
            action=RecoveryAction.SKIP,  # Continue without SAST if it fails
        ),
        "dast": RecoveryStrategy(
            name="skip_dast_on_failure",
            action=RecoveryAction.SKIP,
        ),
        "license": RecoveryStrategy(
            name="skip_license_check",
            action=RecoveryAction.SKIP,
        ),
        "auto_remediate": RecoveryStrategy(
            name="manual_remediation",
            action=RecoveryAction.SKIP,  # Fall back to manual remediation
        ),
    }

    # Create workflow definition
    workflow_def = WorkflowDefinition(
        name="security_scan",
        dag=dag,
        description="Comprehensive security scanning with auto-remediation",
        retry_policies=retry_policies,
        circuit_breakers=circuit_breakers,
        conditional_logic=conditional_logic,
        recovery_strategies=recovery_strategies,
        max_parallel=5,  # Run all scans in parallel
        fail_fast=False,  # Continue even if individual scans fail
        checkpoint_enabled=True,
        checkpoint_frequency=3,
    )

    return workflow_def


# Example usage
async def run_security_scan_example():
    """Run the security scan example"""
    from ..workflow_engine import WorkflowEngine
    
    # Create engine
    engine = WorkflowEngine()
    
    # Create workflow
    workflow_def = create_security_scan_workflow()
    
    # Execute
    context = {
        "target": "myapp:latest",
        "auto_remediate_enabled": True,
        "severity_threshold": "high",
    }
    
    execution = await engine.execute(workflow_def, context)
    
    print(f"Security Scan Status: {execution.status.value}")
    print(f"Metrics: {execution.metrics}")
    
    if execution.result:
        print(f"Results: {execution.result}")
    
    return execution


if __name__ == "__main__":
    asyncio.run(run_security_scan_example())
