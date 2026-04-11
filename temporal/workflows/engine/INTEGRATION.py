"""
Integration Guide for Workflow Orchestration Engine

Shows how to integrate the workflow engine with existing Temporal workflows
and the Sovereign Governance Substrate.
"""

import asyncio
from datetime import timedelta
from typing import Any, Dict

from temporalio import workflow
from temporalio.common import RetryPolicy as TemporalRetryPolicy

from temporal.workflows.engine import (
    WorkflowEngine,
    WorkflowDefinition,
    DAG,
    DAGNode,
    RetryPolicy,
    BackoffStrategy,
    RecoveryStrategy,
    RecoveryAction,
)


# Example: Integrate with existing Triumvirate workflow

@workflow.defn
class EnhancedTriumvirateWorkflow:
    """
    Enhanced Triumvirate workflow using the orchestration engine
    
    Integrates the workflow engine for advanced orchestration capabilities.
    """

    def __init__(self):
        self.execution_id: str = ""

    @workflow.run
    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run Triumvirate workflow with orchestration engine
        
        Args:
            request: Workflow request with input data and configuration
            
        Returns:
            Execution result
        """
        self.execution_id = workflow.info().workflow_id
        
        # Create workflow definition
        workflow_def = self._create_triumvirate_workflow()
        
        # Create engine
        engine = WorkflowEngine()
        
        # Execute
        context = {
            "input_data": request.get("input_data"),
            "context": request.get("context", {}),
            "timeout_seconds": request.get("timeout_seconds", 300),
        }
        
        execution = await engine.execute(workflow_def, context, self.execution_id)
        
        return {
            "execution_id": execution.id,
            "status": execution.status.value,
            "result": execution.result,
            "metrics": execution.metrics,
        }

    def _create_triumvirate_workflow(self) -> WorkflowDefinition:
        """Create Triumvirate workflow definition"""
        
        # Define tasks
        async def validate_input(context: Dict[str, Any], metadata: Dict[str, Any]):
            """Validate input data"""
            input_data = context.get("input_data")
            if not input_data:
                raise ValueError("Input data is required")
            return {"validated": True}
        
        async def process_phase1(context: Dict[str, Any], metadata: Dict[str, Any]):
            """Phase 1: Initial processing"""
            # Call existing Triumvirate activities
            return {"phase": 1, "status": "completed"}
        
        async def process_phase2(context: Dict[str, Any], metadata: Dict[str, Any]):
            """Phase 2: Advanced processing"""
            return {"phase": 2, "status": "completed"}
        
        async def process_phase3(context: Dict[str, Any], metadata: Dict[str, Any]):
            """Phase 3: Final processing"""
            return {"phase": 3, "status": "completed"}
        
        async def aggregate_results(context: Dict[str, Any], metadata: Dict[str, Any]):
            """Aggregate all phase results"""
            return {"aggregated": True, "phases": 3}
        
        # Create DAG
        dag = DAG(name="triumvirate_workflow")
        
        dag.add_node(DAGNode(id="validate", task=validate_input))
        dag.add_node(DAGNode(id="phase1", task=process_phase1, dependencies=["validate"]))
        dag.add_node(DAGNode(id="phase2", task=process_phase2, dependencies=["phase1"]))
        dag.add_node(DAGNode(id="phase3", task=process_phase3, dependencies=["phase2"]))
        dag.add_node(DAGNode(id="aggregate", task=aggregate_results, dependencies=["phase3"]))
        
        # Define retry policies
        retry_policies = {
            "validate": RetryPolicy(
                max_attempts=2,
                initial_interval_ms=1000,
            ),
            "phase1": RetryPolicy(
                max_attempts=3,
                initial_interval_ms=2000,
                backoff_strategy=BackoffStrategy.EXPONENTIAL,
            ),
            "phase2": RetryPolicy(
                max_attempts=3,
                initial_interval_ms=2000,
                backoff_strategy=BackoffStrategy.EXPONENTIAL,
            ),
            "phase3": RetryPolicy(
                max_attempts=3,
                initial_interval_ms=2000,
                backoff_strategy=BackoffStrategy.EXPONENTIAL,
            ),
        }
        
        # Define recovery strategies
        recovery_strategies = {
            "phase1": RecoveryStrategy(
                name="retry_phase1",
                action=RecoveryAction.RETRY,
                max_retries=3,
            ),
            "phase2": RecoveryStrategy(
                name="rollback_on_phase2_failure",
                action=RecoveryAction.ROLLBACK,
                rollback_steps=["phase1"],
            ),
        }
        
        return WorkflowDefinition(
            name="triumvirate_workflow",
            dag=dag,
            retry_policies=retry_policies,
            recovery_strategies=recovery_strategies,
            checkpoint_enabled=True,
        )


# Example: Security workflow integration

@workflow.defn
class SecurityOrchestrationWorkflow:
    """
    Security workflow using orchestration engine
    
    Integrates with existing security workflows for enhanced capabilities.
    """

    @workflow.run
    async def run(self, scan_request: Dict[str, Any]) -> Dict[str, Any]:
        """Run security scan workflow"""
        from temporal.workflows.engine.examples import create_security_scan_workflow
        
        # Use pre-built security scan workflow
        workflow_def = create_security_scan_workflow()
        
        # Create engine
        engine = WorkflowEngine()
        
        # Execute
        context = {
            "target": scan_request.get("target"),
            "auto_remediate_enabled": scan_request.get("auto_remediate", True),
            "severity_threshold": scan_request.get("severity_threshold", "high"),
        }
        
        execution = await engine.execute(workflow_def, context)
        
        return {
            "scan_id": execution.id,
            "status": execution.status.value,
            "vulnerabilities": execution.result,
        }


# Example: Agent coordination workflow

async def create_agent_coordination_workflow() -> WorkflowDefinition:
    """
    Create workflow for coordinating multiple agents
    
    Demonstrates complex agent orchestration with the engine.
    """
    
    # Define agent tasks
    async def agent_analyze(context: Dict[str, Any], metadata: Dict[str, Any]):
        """Agent analyzes data"""
        agent_id = metadata.get("agent_id")
        return {
            "agent": agent_id,
            "analysis": "completed",
            "insights": ["insight1", "insight2"],
        }
    
    async def agent_decide(context: Dict[str, Any], metadata: Dict[str, Any]):
        """Agent makes decisions"""
        return {
            "decision": "proceed",
            "confidence": 0.95,
        }
    
    async def agent_execute(context: Dict[str, Any], metadata: Dict[str, Any]):
        """Agent executes actions"""
        return {
            "actions_executed": 5,
            "success": True,
        }
    
    async def coordinate_results(context: Dict[str, Any], metadata: Dict[str, Any]):
        """Coordinate results from all agents"""
        return {
            "coordination_complete": True,
            "consensus": "reached",
        }
    
    # Create DAG with parallel agent execution
    dag = DAG(name="agent_coordination")
    
    # Multiple agents analyze in parallel
    for i in range(1, 4):
        dag.add_node(DAGNode(
            id=f"agent_{i}_analyze",
            task=agent_analyze,
            metadata={"agent_id": f"agent_{i}"},
        ))
    
    # Decision phase depends on all analyses
    dag.add_node(DAGNode(
        id="decision",
        task=agent_decide,
        dependencies=[f"agent_{i}_analyze" for i in range(1, 4)],
    ))
    
    # Execute phase depends on decision
    dag.add_node(DAGNode(
        id="execute",
        task=agent_execute,
        dependencies=["decision"],
    ))
    
    # Coordination depends on execution
    dag.add_node(DAGNode(
        id="coordinate",
        task=coordinate_results,
        dependencies=["execute"],
    ))
    
    # Define retry policies for agent tasks
    retry_policies = {
        f"agent_{i}_analyze": RetryPolicy(
            max_attempts=3,
            initial_interval_ms=1000,
            backoff_strategy=BackoffStrategy.EXPONENTIAL_JITTER,
        )
        for i in range(1, 4)
    }
    
    # Define recovery strategies
    recovery_strategies = {
        "decision": RecoveryStrategy(
            name="skip_decision_on_failure",
            action=RecoveryAction.SKIP,
        ),
    }
    
    return WorkflowDefinition(
        name="agent_coordination",
        dag=dag,
        retry_policies=retry_policies,
        recovery_strategies=recovery_strategies,
        max_parallel=3,  # Run all 3 agents in parallel
        checkpoint_enabled=True,
    )


# Integration with existing activities

@workflow.defn
class IntegratedWorkflow:
    """
    Workflow that integrates engine with existing Temporal activities
    """

    @workflow.run
    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run integrated workflow
        
        Combines orchestration engine with existing Temporal activities.
        """
        
        # Import existing activities
        # from temporal.workflows.security_agent_activities import (
        #     scan_code,
        #     analyze_results,
        # )
        
        async def scan_wrapper(context: Dict[str, Any], metadata: Dict[str, Any]):
            """Wrapper for existing Temporal activity"""
            # Call existing activity
            # result = await workflow.execute_activity(
            #     scan_code,
            #     context.get("target"),
            #     start_to_close_timeout=timedelta(seconds=300),
            # )
            # return result
            return {"scan": "completed"}
        
        # Create workflow with existing activities
        dag = DAG(name="integrated")
        dag.add_node(DAGNode(id="scan", task=scan_wrapper))
        
        workflow_def = WorkflowDefinition(
            name="integrated",
            dag=dag,
        )
        
        engine = WorkflowEngine()
        execution = await engine.execute(workflow_def, request)
        
        return execution.result


# Example usage

async def example_usage():
    """Demonstrate integration examples"""
    
    # 1. Use with Temporal client
    from temporalio.client import Client
    
    client = await Client.connect("localhost:7233")
    
    # Execute enhanced Triumvirate workflow
    result = await client.execute_workflow(
        EnhancedTriumvirateWorkflow.run,
        {"input_data": "test"},
        id="triumvirate-123",
        task_queue="triumvirate-tasks",
    )
    print(f"Triumvirate result: {result}")
    
    # 2. Execute security scan
    result = await client.execute_workflow(
        SecurityOrchestrationWorkflow.run,
        {"target": "myapp:latest"},
        id="security-scan-123",
        task_queue="security-tasks",
    )
    print(f"Security scan result: {result}")
    
    # 3. Execute agent coordination
    workflow_def = await create_agent_coordination_workflow()
    engine = WorkflowEngine()
    execution = await engine.execute(workflow_def)
    print(f"Agent coordination result: {execution.result}")


if __name__ == "__main__":
    asyncio.run(example_usage())
