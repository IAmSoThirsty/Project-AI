"""
Workflow Orchestration Engine

Main workflow engine that integrates DAG execution, conditional logic,
retry mechanisms, and failure recovery for complex agent coordination.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from temporalio import workflow
from temporalio.common import RetryPolicy as TemporalRetryPolicy

from .conditionals import ConditionalInterpreter, ConditionalLogic
from .dag import DAG, DAGExecutor, DAGNode
from .recovery import CheckpointManager, FailureRecovery, RecoveryStrategy
from .retry import CircuitBreaker, RetryExecutor, RetryPolicy

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Status of workflow execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class WorkflowDefinition:
    """
    Complete workflow definition
    
    Defines the structure and behavior of a workflow including:
    - DAG structure
    - Conditional branching
    - Retry policies
    - Recovery strategies
    """
    name: str
    dag: DAG
    description: Optional[str] = None
    conditional_logic: Optional[Dict[str, ConditionalLogic]] = None
    retry_policies: Optional[Dict[str, RetryPolicy]] = None
    recovery_strategies: Optional[Dict[str, RecoveryStrategy]] = None
    circuit_breakers: Optional[Dict[str, CircuitBreaker]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    max_parallel: int = 10
    fail_fast: bool = False
    checkpoint_enabled: bool = True
    checkpoint_frequency: int = 5

    def validate(self) -> bool:
        """Validate workflow definition"""
        # Validate DAG
        self.dag.validate()

        # Validate conditional logic references
        if self.conditional_logic:
            for node_id in self.conditional_logic.keys():
                if node_id not in self.dag.nodes:
                    raise ValueError(
                        f"Conditional logic references non-existent node: {node_id}"
                    )

        # Validate retry policies
        if self.retry_policies:
            for node_id in self.retry_policies.keys():
                if node_id not in self.dag.nodes:
                    raise ValueError(
                        f"Retry policy references non-existent node: {node_id}"
                    )

        # Validate recovery strategies
        if self.recovery_strategies:
            for node_id in self.recovery_strategies.keys():
                if node_id not in self.dag.nodes:
                    raise ValueError(
                        f"Recovery strategy references non-existent node: {node_id}"
                    )

        return True


@dataclass
class WorkflowExecution:
    """
    Runtime workflow execution state
    
    Tracks the execution of a workflow instance.
    """
    id: str
    workflow_name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    checkpoints: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class WorkflowEngine:
    """
    Complete workflow orchestration engine
    
    Integrates all workflow components for comprehensive orchestration:
    - DAG execution
    - Conditional branching
    - Retry logic with circuit breakers
    - Failure recovery with checkpoints
    - Temporal.io integration
    """

    def __init__(
        self,
        checkpoint_storage_path: Optional[Path] = None,
    ):
        """
        Initialize workflow engine
        
        Args:
            checkpoint_storage_path: Path for checkpoint storage
        """
        self.checkpoint_manager = CheckpointManager(checkpoint_storage_path)
        self.conditional_interpreter = ConditionalInterpreter()
        self.executions: Dict[str, WorkflowExecution] = {}
        self.execution_log: List[Dict[str, Any]] = []

    async def execute(
        self,
        workflow_def: WorkflowDefinition,
        input_context: Optional[Dict[str, Any]] = None,
        execution_id: Optional[str] = None,
    ) -> WorkflowExecution:
        """
        Execute a workflow
        
        Args:
            workflow_def: Workflow definition to execute
            input_context: Initial context/inputs
            execution_id: Optional execution ID (generated if not provided)
            
        Returns:
            Workflow execution result
        """
        # Validate workflow
        workflow_def.validate()

        # Create execution
        execution_id = execution_id or str(uuid.uuid4())
        execution = WorkflowExecution(
            id=execution_id,
            workflow_name=workflow_def.name,
            status=WorkflowStatus.RUNNING,
            start_time=datetime.utcnow(),
            context=input_context or {},
        )
        self.executions[execution_id] = execution

        logger.info(
            f"Starting workflow execution: {workflow_def.name} ({execution_id})"
        )

        try:
            # Initialize failure recovery
            failure_recovery = FailureRecovery(self.checkpoint_manager)
            
            # Register recovery strategies
            if workflow_def.recovery_strategies:
                for node_id, strategy in workflow_def.recovery_strategies.items():
                    failure_recovery.register_strategy(node_id, strategy)

            # Execute workflow
            result = await self._execute_workflow(
                workflow_def,
                execution,
                failure_recovery,
            )

            execution.result = result
            execution.status = WorkflowStatus.COMPLETED
            execution.end_time = datetime.utcnow()

            logger.info(
                f"Workflow completed: {workflow_def.name} ({execution_id})"
            )

        except Exception as e:
            execution.error = str(e)
            execution.status = WorkflowStatus.FAILED
            execution.end_time = datetime.utcnow()

            logger.error(
                f"Workflow failed: {workflow_def.name} ({execution_id}): {e}",
                exc_info=True,
            )

        return execution

    async def _execute_workflow(
        self,
        workflow_def: WorkflowDefinition,
        execution: WorkflowExecution,
        failure_recovery: FailureRecovery,
    ) -> Dict[str, Any]:
        """Execute workflow with all features"""
        context = execution.context.copy()
        checkpoint_counter = 0

        # Wrap tasks with retry and recovery
        wrapped_dag = await self._wrap_dag_nodes(
            workflow_def,
            execution.id,
            failure_recovery,
        )

        # Execute DAG
        executor = DAGExecutor(
            max_parallel=workflow_def.max_parallel,
            fail_fast=workflow_def.fail_fast,
        )

        result = await executor.execute(wrapped_dag, context)

        # Store final checkpoint
        if workflow_def.checkpoint_enabled:
            checkpoint = await self.checkpoint_manager.create_checkpoint(
                workflow_id=execution.id,
                state=context,
                completed_nodes=[
                    node_id for node_id, node in wrapped_dag.nodes.items()
                    if node.status.value == "completed"
                ],
                metadata={"final": True},
            )
            execution.checkpoints.append(checkpoint.id)

        # Collect metrics
        execution.metrics = self._collect_metrics(executor, result)

        return result

    async def _wrap_dag_nodes(
        self,
        workflow_def: WorkflowDefinition,
        execution_id: str,
        failure_recovery: FailureRecovery,
    ) -> DAG:
        """
        Wrap DAG nodes with retry, recovery, and conditional logic
        
        Creates a new DAG with enhanced node tasks.
        """
        wrapped_dag = DAG(
            name=workflow_def.dag.name,
            description=workflow_def.dag.description,
            metadata=workflow_def.dag.metadata.copy(),
        )

        for node_id, original_node in workflow_def.dag.nodes.items():
            # Get configurations
            retry_policy = (
                workflow_def.retry_policies.get(node_id)
                if workflow_def.retry_policies
                else None
            )
            circuit_breaker = (
                workflow_def.circuit_breakers.get(node_id)
                if workflow_def.circuit_breakers
                else None
            )
            conditional_logic = (
                workflow_def.conditional_logic.get(node_id)
                if workflow_def.conditional_logic
                else None
            )

            # Create wrapped task
            wrapped_task = self._create_wrapped_task(
                original_node.task,
                node_id,
                execution_id,
                retry_policy,
                circuit_breaker,
                conditional_logic,
                failure_recovery,
            )

            # Create wrapped node
            wrapped_node = DAGNode(
                id=node_id,
                task=wrapped_task,
                dependencies=original_node.dependencies.copy(),
                metadata=original_node.metadata.copy(),
            )

            wrapped_dag.add_node(wrapped_node)

        return wrapped_dag

    def _create_wrapped_task(
        self,
        original_task: Callable,
        node_id: str,
        execution_id: str,
        retry_policy: Optional[RetryPolicy],
        circuit_breaker: Optional[CircuitBreaker],
        conditional_logic: Optional[ConditionalLogic],
        failure_recovery: FailureRecovery,
    ) -> Callable:
        """Create wrapped task with all features"""

        async def wrapped_task(context: Dict[str, Any], metadata: Dict[str, Any]):
            logger.debug(f"Executing wrapped task: {node_id}")

            # Handle conditional logic
            if conditional_logic:
                action = self.conditional_interpreter.evaluate(
                    conditional_logic,
                    context,
                )
                if action != node_id:
                    logger.info(
                        f"Conditional logic redirected from {node_id} to {action}"
                    )
                    # Skip current task
                    return {"skipped": True, "redirected_to": action}

            # Execute with retry and circuit breaker
            if retry_policy:
                executor = RetryExecutor(retry_policy, circuit_breaker)
                try:
                    if asyncio.iscoroutinefunction(original_task):
                        result = await executor.execute(
                            original_task,
                            context,
                            metadata,
                        )
                    else:
                        result = await executor.execute(
                            lambda: original_task(context, metadata),
                        )
                    return result

                except Exception as e:
                    # Handle failure with recovery
                    recovery_result = await failure_recovery.handle_failure(
                        workflow_id=execution_id,
                        node_id=node_id,
                        error=e,
                        context=context,
                    )
                    
                    if recovery_result["action"] == "skip":
                        return {"skipped": True, "reason": str(e)}
                    else:
                        raise

            else:
                # Execute without retry
                try:
                    if asyncio.iscoroutinefunction(original_task):
                        return await original_task(context, metadata)
                    else:
                        return original_task(context, metadata)
                except Exception as e:
                    # Handle failure
                    recovery_result = await failure_recovery.handle_failure(
                        workflow_id=execution_id,
                        node_id=node_id,
                        error=e,
                        context=context,
                    )
                    
                    if recovery_result["action"] == "skip":
                        return {"skipped": True, "reason": str(e)}
                    else:
                        raise

        return wrapped_task

    def _collect_metrics(
        self,
        executor: DAGExecutor,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Collect execution metrics"""
        return {
            "execution_log_entries": len(executor.execution_log),
            "total_nodes": result.get("total_nodes", 0),
            "completed_nodes": result.get("completed", 0),
            "failed_nodes": result.get("failed", 0),
            "skipped_nodes": result.get("skipped", 0),
            "duration_seconds": result.get("duration_seconds", 0),
        }

    async def resume_from_checkpoint(
        self,
        workflow_def: WorkflowDefinition,
        checkpoint_id: str,
    ) -> WorkflowExecution:
        """
        Resume workflow execution from a checkpoint
        
        Args:
            workflow_def: Workflow definition
            checkpoint_id: Checkpoint to resume from
            
        Returns:
            Resumed workflow execution
        """
        checkpoint = await self.checkpoint_manager.restore_checkpoint(checkpoint_id)
        if not checkpoint:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")

        logger.info(f"Resuming workflow from checkpoint: {checkpoint_id}")

        # Create new execution with restored state
        execution = await self.execute(
            workflow_def,
            input_context=checkpoint.state,
            execution_id=f"{checkpoint.workflow_id}_resumed",
        )

        return execution

    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get workflow execution by ID"""
        return self.executions.get(execution_id)

    def list_executions(
        self,
        status: Optional[WorkflowStatus] = None,
    ) -> List[WorkflowExecution]:
        """List workflow executions, optionally filtered by status"""
        executions = list(self.executions.values())
        
        if status:
            executions = [e for e in executions if e.status == status]

        return sorted(executions, key=lambda e: e.start_time or datetime.min)


# Temporal.io Integration

@workflow.defn
class TemporalWorkflow:
    """
    Temporal workflow wrapper for the workflow engine
    
    Integrates workflow engine with Temporal.io for durable execution.
    """

    def __init__(self):
        self.execution_id: Optional[str] = None

    @workflow.run
    async def run(
        self,
        workflow_def_dict: Dict[str, Any],
        input_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run workflow in Temporal
        
        Args:
            workflow_def_dict: Serialized workflow definition
            input_context: Input context
            
        Returns:
            Execution result
        """
        self.execution_id = workflow.info().workflow_id

        logger.info(f"Temporal workflow started: {self.execution_id}")

        # Create workflow engine
        engine = WorkflowEngine()

        # Deserialize workflow definition
        workflow_def = self._deserialize_workflow_def(workflow_def_dict)

        # Execute workflow
        execution = await engine.execute(
            workflow_def,
            input_context,
            execution_id=self.execution_id,
        )

        # Return result
        return {
            "execution_id": execution.id,
            "status": execution.status.value,
            "result": execution.result,
            "error": execution.error,
            "metrics": execution.metrics,
            "duration_seconds": (
                (execution.end_time - execution.start_time).total_seconds()
                if execution.end_time and execution.start_time
                else None
            ),
        }

    def _deserialize_workflow_def(
        self,
        data: Dict[str, Any],
    ) -> WorkflowDefinition:
        """Deserialize workflow definition from dict"""
        # This is a simplified version - full implementation would
        # need to handle serialization of callables, etc.
        dag = DAG(name=data["dag"]["name"])
        
        # Rebuild DAG nodes (simplified)
        for node_data in data["dag"]["nodes"]:
            node = DAGNode(
                id=node_data["id"],
                task=lambda ctx, meta: {"placeholder": True},  # Would need proper deserialization
                dependencies=node_data.get("dependencies", []),
                metadata=node_data.get("metadata", {}),
            )
            dag.add_node(node)

        return WorkflowDefinition(
            name=data["name"],
            dag=dag,
            description=data.get("description"),
            max_parallel=data.get("max_parallel", 10),
            fail_fast=data.get("fail_fast", False),
        )
