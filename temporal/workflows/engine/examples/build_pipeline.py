"""
Build Pipeline Workflow Example

Demonstrates a complete CI/CD build pipeline with:
- Dependency installation
- Code compilation
- Unit tests
- Integration tests
- Docker build
- Artifact publishing
"""

import asyncio
import logging
from typing import Any, Dict

from ..conditionals import Condition, ConditionalBranch, ConditionalLogic, ConditionOperator
from ..dag import DAG, DAGNode
from ..recovery import RecoveryAction, RecoveryStrategy
from ..retry import BackoffStrategy, RetryPolicy
from ..workflow_engine import WorkflowDefinition

logger = logging.getLogger(__name__)


# Build tasks

async def checkout_code(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Checkout source code from repository"""
    logger.info("Checking out code")
    await asyncio.sleep(0.5)  # Simulate git clone
    
    return {
        "branch": context.get("branch", "main"),
        "commit": "abc123def456",
        "files_changed": 42,
    }


async def install_dependencies(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Install project dependencies"""
    logger.info("Installing dependencies")
    await asyncio.sleep(1.0)  # Simulate npm install / pip install
    
    return {
        "packages_installed": 156,
        "cache_hit": True,
    }


async def compile_code(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Compile source code"""
    logger.info("Compiling code")
    await asyncio.sleep(1.5)  # Simulate compilation
    
    return {
        "files_compiled": 234,
        "warnings": 3,
        "errors": 0,
    }


async def run_unit_tests(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Run unit tests"""
    logger.info("Running unit tests")
    await asyncio.sleep(2.0)  # Simulate test execution
    
    return {
        "total_tests": 342,
        "passed": 340,
        "failed": 2,
        "skipped": 0,
        "coverage": 87.5,
    }


async def run_integration_tests(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Run integration tests"""
    logger.info("Running integration tests")
    await asyncio.sleep(3.0)  # Simulate test execution
    
    return {
        "total_tests": 45,
        "passed": 45,
        "failed": 0,
        "skipped": 0,
    }


async def build_docker_image(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Build Docker image"""
    logger.info("Building Docker image")
    await asyncio.sleep(2.5)  # Simulate docker build
    
    return {
        "image_name": "myapp:latest",
        "image_size_mb": 456,
        "layers": 12,
    }


async def publish_artifacts(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Publish build artifacts"""
    logger.info("Publishing artifacts")
    await asyncio.sleep(1.0)  # Simulate artifact upload
    
    return {
        "artifacts": [
            "myapp-1.0.0.tar.gz",
            "myapp-1.0.0-docker.tar",
        ],
        "registry": "artifacts.example.com",
    }


async def send_notification(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Send build completion notification"""
    logger.info("Sending notification")
    await asyncio.sleep(0.3)
    
    return {
        "notification_sent": True,
        "channel": "slack",
    }


def create_build_pipeline() -> WorkflowDefinition:
    """
    Create a complete build pipeline workflow
    
    Pipeline stages:
    1. Checkout code
    2. Install dependencies
    3. Compile code
    4. Run unit tests (parallel with integration tests)
    5. Run integration tests
    6. Build Docker image
    7. Publish artifacts
    8. Send notification
    """
    
    # Create DAG
    dag = DAG(
        name="build_pipeline",
        description="Complete CI/CD build pipeline",
    )

    # Define nodes
    nodes = {
        "checkout": DAGNode(
            id="checkout",
            task=checkout_code,
            dependencies=[],
            metadata={"stage": "setup"},
        ),
        "install_deps": DAGNode(
            id="install_deps",
            task=install_dependencies,
            dependencies=["checkout"],
            metadata={"stage": "setup"},
        ),
        "compile": DAGNode(
            id="compile",
            task=compile_code,
            dependencies=["install_deps"],
            metadata={"stage": "build"},
        ),
        "unit_tests": DAGNode(
            id="unit_tests",
            task=run_unit_tests,
            dependencies=["compile"],
            metadata={"stage": "test"},
        ),
        "integration_tests": DAGNode(
            id="integration_tests",
            task=run_integration_tests,
            dependencies=["compile"],
            metadata={"stage": "test"},
        ),
        "docker_build": DAGNode(
            id="docker_build",
            task=build_docker_image,
            dependencies=["unit_tests", "integration_tests"],
            metadata={"stage": "package"},
        ),
        "publish": DAGNode(
            id="publish",
            task=publish_artifacts,
            dependencies=["docker_build"],
            metadata={"stage": "deploy"},
        ),
        "notify": DAGNode(
            id="notify",
            task=send_notification,
            dependencies=["publish"],
            metadata={"stage": "notify"},
        ),
    }

    # Add nodes to DAG
    for node in nodes.values():
        dag.add_node(node)

    # Define retry policies
    retry_policies = {
        "checkout": RetryPolicy(
            max_attempts=3,
            initial_interval_ms=1000,
            backoff_strategy=BackoffStrategy.EXPONENTIAL_JITTER,
        ),
        "install_deps": RetryPolicy(
            max_attempts=5,
            initial_interval_ms=2000,
            max_interval_ms=30000,
            backoff_strategy=BackoffStrategy.EXPONENTIAL_JITTER,
        ),
        "compile": RetryPolicy(
            max_attempts=2,
            initial_interval_ms=1000,
        ),
        "docker_build": RetryPolicy(
            max_attempts=3,
            initial_interval_ms=5000,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
        ),
        "publish": RetryPolicy(
            max_attempts=5,
            initial_interval_ms=3000,
            max_interval_ms=60000,
            backoff_strategy=BackoffStrategy.EXPONENTIAL_JITTER,
        ),
    }

    # Define recovery strategies
    recovery_strategies = {
        "unit_tests": RecoveryStrategy(
            name="skip_failing_tests",
            action=RecoveryAction.SKIP,  # Continue even if tests fail
        ),
        "integration_tests": RecoveryStrategy(
            name="skip_failing_integration",
            action=RecoveryAction.SKIP,
        ),
        "compile": RecoveryStrategy(
            name="retry_compile",
            action=RecoveryAction.RETRY,
            max_retries=3,
        ),
        "publish": RecoveryStrategy(
            name="rollback_on_publish_fail",
            action=RecoveryAction.ROLLBACK,
            rollback_steps=["docker_build"],
        ),
    }

    # Create workflow definition
    workflow_def = WorkflowDefinition(
        name="build_pipeline",
        dag=dag,
        description="Complete CI/CD build pipeline with parallel testing",
        retry_policies=retry_policies,
        recovery_strategies=recovery_strategies,
        max_parallel=4,  # Run up to 4 tasks in parallel
        fail_fast=False,  # Continue on non-critical failures
        checkpoint_enabled=True,
        checkpoint_frequency=3,  # Checkpoint every 3 nodes
    )

    return workflow_def


# Example usage
async def run_build_pipeline_example():
    """Run the build pipeline example"""
    from ..workflow_engine import WorkflowEngine
    
    # Create engine
    engine = WorkflowEngine()
    
    # Create workflow
    workflow_def = create_build_pipeline()
    
    # Execute
    context = {
        "branch": "main",
        "run_tests": True,
        "publish_to": "production",
    }
    
    execution = await engine.execute(workflow_def, context)
    
    print(f"Build Pipeline Status: {execution.status.value}")
    print(f"Metrics: {execution.metrics}")
    
    if execution.result:
        print(f"Results: {execution.result}")
    
    return execution


if __name__ == "__main__":
    asyncio.run(run_build_pipeline_example())
