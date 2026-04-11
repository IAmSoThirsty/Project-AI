"""
Deployment Workflow Example

Demonstrates a multi-environment deployment workflow with:
- Pre-deployment validation
- Database migrations
- Blue-green deployment
- Health checks
- Rollback capability
- Multi-environment promotion
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


# Deployment tasks

async def validate_prerequisites(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Validate deployment prerequisites"""
    logger.info("Validating prerequisites")
    await asyncio.sleep(0.5)
    
    environment = context.get("environment", "staging")
    
    return {
        "environment": environment,
        "prerequisites_met": True,
        "checks": {
            "config_valid": True,
            "secrets_available": True,
            "resources_sufficient": True,
        },
    }


async def backup_database(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Backup database before deployment"""
    logger.info("Backing up database")
    await asyncio.sleep(2.0)
    
    return {
        "backup_id": "backup_20260411_014800",
        "backup_size_gb": 12.5,
        "backup_location": "s3://backups/db-backup-20260411.sql.gz",
    }


async def run_database_migrations(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Run database migrations"""
    logger.info("Running database migrations")
    await asyncio.sleep(1.5)
    
    return {
        "migrations_applied": 5,
        "migration_ids": ["m001", "m002", "m003", "m004", "m005"],
        "success": True,
    }


async def deploy_blue_environment(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Deploy to blue environment (new version)"""
    logger.info("Deploying to blue environment")
    await asyncio.sleep(3.0)
    
    return {
        "environment": "blue",
        "version": context.get("version", "1.2.0"),
        "instances": 5,
        "deployment_time": 3.0,
    }


async def health_check_blue(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Health check blue environment"""
    logger.info("Health checking blue environment")
    await asyncio.sleep(1.0)
    
    return {
        "healthy": True,
        "instances_healthy": 5,
        "instances_total": 5,
        "response_time_ms": 45,
    }


async def smoke_tests(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Run smoke tests on new deployment"""
    logger.info("Running smoke tests")
    await asyncio.sleep(2.0)
    
    return {
        "total_tests": 25,
        "passed": 25,
        "failed": 0,
        "duration_seconds": 2.0,
    }


async def switch_traffic(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Switch traffic from green to blue"""
    logger.info("Switching traffic to blue environment")
    await asyncio.sleep(1.0)
    
    return {
        "traffic_percentage_blue": 100,
        "traffic_percentage_green": 0,
        "switch_complete": True,
    }


async def monitor_metrics(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Monitor metrics after traffic switch"""
    logger.info("Monitoring post-deployment metrics")
    await asyncio.sleep(2.0)
    
    return {
        "error_rate": 0.02,  # 0.02%
        "latency_p95_ms": 120,
        "latency_p99_ms": 250,
        "cpu_usage": 45,
        "memory_usage": 62,
        "metrics_healthy": True,
    }


async def decommission_green(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Decommission old green environment"""
    logger.info("Decommissioning green environment")
    await asyncio.sleep(1.5)
    
    return {
        "instances_terminated": 5,
        "environment": "green",
        "cleanup_complete": True,
    }


async def rollback_deployment(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Rollback to previous version"""
    logger.error("Rolling back deployment")
    await asyncio.sleep(2.0)
    
    return {
        "rollback_complete": True,
        "active_environment": "green",
        "version": context.get("previous_version", "1.1.0"),
    }


async def send_deployment_notification(context: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Send deployment notification"""
    logger.info("Sending deployment notification")
    await asyncio.sleep(0.3)
    
    return {
        "notification_sent": True,
        "channels": ["slack", "email"],
        "recipients": ["devops-team@example.com"],
    }


def create_deployment_workflow() -> WorkflowDefinition:
    """
    Create a blue-green deployment workflow
    
    Workflow stages:
    1. Validate prerequisites
    2. Backup database
    3. Run migrations
    4. Deploy to blue environment
    5. Health checks and smoke tests
    6. Switch traffic conditionally
    7. Monitor metrics
    8. Decommission old environment or rollback
    """
    
    # Create DAG
    dag = DAG(
        name="deployment",
        description="Blue-green deployment with rollback capability",
    )

    # Define nodes
    nodes = {
        "validate": DAGNode(
            id="validate",
            task=validate_prerequisites,
            dependencies=[],
            metadata={"stage": "pre-deployment"},
        ),
        "backup_db": DAGNode(
            id="backup_db",
            task=backup_database,
            dependencies=["validate"],
            metadata={"stage": "pre-deployment"},
        ),
        "migrate_db": DAGNode(
            id="migrate_db",
            task=run_database_migrations,
            dependencies=["backup_db"],
            metadata={"stage": "pre-deployment"},
        ),
        "deploy_blue": DAGNode(
            id="deploy_blue",
            task=deploy_blue_environment,
            dependencies=["migrate_db"],
            metadata={"stage": "deployment"},
        ),
        "health_check": DAGNode(
            id="health_check",
            task=health_check_blue,
            dependencies=["deploy_blue"],
            metadata={"stage": "validation"},
        ),
        "smoke_tests": DAGNode(
            id="smoke_tests",
            task=smoke_tests,
            dependencies=["health_check"],
            metadata={"stage": "validation"},
        ),
        "switch_traffic": DAGNode(
            id="switch_traffic",
            task=switch_traffic,
            dependencies=["smoke_tests"],
            metadata={"stage": "cutover"},
        ),
        "monitor": DAGNode(
            id="monitor",
            task=monitor_metrics,
            dependencies=["switch_traffic"],
            metadata={"stage": "post-deployment"},
        ),
        "decommission": DAGNode(
            id="decommission",
            task=decommission_green,
            dependencies=["monitor"],
            metadata={"stage": "cleanup"},
        ),
        "rollback": DAGNode(
            id="rollback",
            task=rollback_deployment,
            dependencies=["health_check"],
            metadata={"stage": "recovery"},
        ),
        "notify": DAGNode(
            id="notify",
            task=send_deployment_notification,
            dependencies=["decommission"],
            metadata={"stage": "notification"},
        ),
    }

    # Add nodes to DAG
    for node in nodes.values():
        dag.add_node(node)

    # Define retry policies
    retry_policies = {
        "validate": RetryPolicy(
            max_attempts=2,
            initial_interval_ms=1000,
        ),
        "backup_db": RetryPolicy(
            max_attempts=3,
            initial_interval_ms=5000,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
        ),
        "migrate_db": RetryPolicy(
            max_attempts=2,
            initial_interval_ms=3000,
        ),
        "deploy_blue": RetryPolicy(
            max_attempts=3,
            initial_interval_ms=10000,
            max_interval_ms=60000,
            backoff_strategy=BackoffStrategy.EXPONENTIAL_JITTER,
        ),
        "health_check": RetryPolicy(
            max_attempts=10,
            initial_interval_ms=2000,
            max_interval_ms=10000,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
        ),
        "switch_traffic": RetryPolicy(
            max_attempts=2,
            initial_interval_ms=5000,
        ),
    }

    # Define circuit breakers
    circuit_breakers = {
        "deploy_blue": CircuitBreaker(
            failure_threshold=3,
            success_threshold=1,
            timeout_seconds=300,
        ),
        "health_check": CircuitBreaker(
            failure_threshold=5,
            success_threshold=2,
            timeout_seconds=120,
        ),
    }

    # Define conditional logic
    conditional_logic = {
        "switch_traffic": ConditionalLogic(
            branches=[
                ConditionalBranch(
                    condition=Condition(
                        operator=ConditionOperator.AND,
                        conditions=[
                            Condition(
                                operator=ConditionOperator.EQ,
                                left="$health_check.healthy",
                                right=True,
                            ),
                            Condition(
                                operator=ConditionOperator.EQ,
                                left="$smoke_tests.failed",
                                right=0,
                            ),
                        ],
                    ),
                    action="switch_traffic",
                ),
            ],
            default_action="rollback",  # Rollback if conditions not met
        ),
        "decommission": ConditionalLogic(
            branches=[
                ConditionalBranch(
                    condition=Condition(
                        operator=ConditionOperator.EQ,
                        left="$monitor.metrics_healthy",
                        right=True,
                    ),
                    action="decommission",
                ),
            ],
            default_action="rollback",
        ),
    }

    # Define recovery strategies with compensating actions
    async def restore_database(context: Dict[str, Any]) -> Dict[str, Any]:
        """Compensating action to restore database"""
        logger.info("Restoring database from backup")
        await asyncio.sleep(3.0)
        return {"restored": True}

    recovery_strategies = {
        "migrate_db": RecoveryStrategy(
            name="restore_db_on_migration_failure",
            action=RecoveryAction.COMPENSATE,
            compensating_action=restore_database,
        ),
        "deploy_blue": RecoveryStrategy(
            name="rollback_on_deploy_failure",
            action=RecoveryAction.ROLLBACK,
            rollback_steps=["migrate_db", "backup_db"],
        ),
        "health_check": RecoveryStrategy(
            name="rollback_on_health_failure",
            action=RecoveryAction.FAIL,  # Critical failure, stop deployment
        ),
        "switch_traffic": RecoveryStrategy(
            name="rollback_on_switch_failure",
            action=RecoveryAction.ROLLBACK,
            rollback_steps=["deploy_blue"],
        ),
    }

    # Create workflow definition
    workflow_def = WorkflowDefinition(
        name="deployment",
        dag=dag,
        description="Blue-green deployment with health checks and rollback",
        retry_policies=retry_policies,
        circuit_breakers=circuit_breakers,
        conditional_logic=conditional_logic,
        recovery_strategies=recovery_strategies,
        max_parallel=2,  # Limit parallel operations during deployment
        fail_fast=True,  # Stop on critical failures
        checkpoint_enabled=True,
        checkpoint_frequency=2,
        metadata={
            "deployment_type": "blue-green",
            "rollback_enabled": True,
        },
    )

    return workflow_def


# Example usage
async def run_deployment_example():
    """Run the deployment example"""
    from ..workflow_engine import WorkflowEngine
    
    # Create engine
    engine = WorkflowEngine()
    
    # Create workflow
    workflow_def = create_deployment_workflow()
    
    # Execute deployment
    context = {
        "environment": "production",
        "version": "1.2.0",
        "previous_version": "1.1.0",
        "auto_rollback": True,
    }
    
    execution = await engine.execute(workflow_def, context)
    
    print(f"Deployment Status: {execution.status.value}")
    print(f"Metrics: {execution.metrics}")
    
    if execution.result:
        print(f"Results: {execution.result}")
    
    return execution


if __name__ == "__main__":
    asyncio.run(run_deployment_example())
