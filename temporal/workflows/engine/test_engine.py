"""
Tests for Workflow Orchestration Engine

Validates the workflow engine components and example workflows.
"""

import asyncio
import pytest
from pathlib import Path

from temporal.workflows.engine import (
    WorkflowEngine,
    WorkflowDefinition,
    DAG,
    DAGNode,
    DAGExecutor,
    RetryPolicy,
    BackoffStrategy,
    RecoveryStrategy,
    RecoveryAction,
    CircuitBreaker,
    Condition,
    ConditionalBranch,
    ConditionalLogic,
    ConditionOperator,
    ConditionalInterpreter,
    CheckpointManager,
    FailureRecovery,
)


# Test tasks
async def simple_task(context, metadata):
    """Simple test task"""
    return {"status": "success"}


async def failing_task(context, metadata):
    """Task that always fails"""
    raise Exception("Task failed")


async def conditional_task(context, metadata):
    """Task that uses context"""
    return {"value": context.get("value", 0) * 2}


class TestDAG:
    """Test DAG functionality"""

    def test_dag_creation(self):
        """Test basic DAG creation"""
        dag = DAG(name="test_dag")
        node = DAGNode(id="task1", task=simple_task)
        dag.add_node(node)
        
        assert len(dag.nodes) == 1
        assert "task1" in dag.nodes

    def test_dag_dependencies(self):
        """Test DAG dependency management"""
        dag = DAG(name="test_dag")
        
        node1 = DAGNode(id="task1", task=simple_task)
        node2 = DAGNode(id="task2", task=simple_task, dependencies=["task1"])
        
        dag.add_node(node1)
        dag.add_node(node2)
        
        assert node2.dependencies == ["task1"]

    def test_dag_validation(self):
        """Test DAG validation"""
        dag = DAG(name="test_dag")
        
        node1 = DAGNode(id="task1", task=simple_task)
        node2 = DAGNode(id="task2", task=simple_task, dependencies=["task1"])
        
        dag.add_node(node1)
        dag.add_node(node2)
        
        assert dag.validate()

    def test_dag_cycle_detection(self):
        """Test cycle detection"""
        dag = DAG(name="test_dag")
        
        node1 = DAGNode(id="task1", task=simple_task, dependencies=["task2"])
        node2 = DAGNode(id="task2", task=simple_task, dependencies=["task1"])
        
        dag.add_node(node1)
        dag.add_node(node2)
        
        with pytest.raises(ValueError, match="cycle"):
            dag.validate()

    def test_topological_sort(self):
        """Test topological sorting"""
        dag = DAG(name="test_dag")
        
        dag.add_node(DAGNode(id="task1", task=simple_task))
        dag.add_node(DAGNode(id="task2", task=simple_task, dependencies=["task1"]))
        dag.add_node(DAGNode(id="task3", task=simple_task, dependencies=["task1"]))
        dag.add_node(DAGNode(id="task4", task=simple_task, dependencies=["task2", "task3"]))
        
        levels = dag.topological_sort()
        
        assert len(levels) == 3
        assert levels[0] == ["task1"]
        assert set(levels[1]) == {"task2", "task3"}
        assert levels[2] == ["task4"]


class TestDAGExecutor:
    """Test DAG executor"""

    @pytest.mark.asyncio
    async def test_simple_execution(self):
        """Test simple DAG execution"""
        dag = DAG(name="test_dag")
        dag.add_node(DAGNode(id="task1", task=simple_task))
        
        executor = DAGExecutor()
        result = await executor.execute(dag)
        
        assert result["status"] == "completed"
        assert result["completed"] == 1
        assert result["failed"] == 0

    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Test parallel task execution"""
        dag = DAG(name="test_dag")
        
        dag.add_node(DAGNode(id="task1", task=simple_task))
        dag.add_node(DAGNode(id="task2", task=simple_task))
        dag.add_node(DAGNode(id="task3", task=simple_task))
        
        executor = DAGExecutor()
        result = await executor.execute(dag)
        
        assert result["status"] == "completed"
        assert result["completed"] == 3


class TestConditionals:
    """Test conditional logic"""

    def test_condition_evaluation(self):
        """Test basic condition evaluation"""
        interpreter = ConditionalInterpreter()
        
        condition = Condition(
            operator=ConditionOperator.EQ,
            left="$value",
            right=10,
        )
        
        context = {"value": 10}
        result = interpreter._evaluate_condition(condition, context)
        
        assert result is True

    def test_conditional_logic(self):
        """Test conditional logic evaluation"""
        interpreter = ConditionalInterpreter()
        
        logic = ConditionalLogic(
            branches=[
                ConditionalBranch(
                    condition=Condition(
                        operator=ConditionOperator.GT,
                        left="$score",
                        right=80,
                    ),
                    action="high",
                ),
                ConditionalBranch(
                    condition=Condition(
                        operator=ConditionOperator.GT,
                        left="$score",
                        right=50,
                    ),
                    action="medium",
                ),
            ],
            default_action="low",
        )
        
        assert interpreter.evaluate(logic, {"score": 90}) == "high"
        assert interpreter.evaluate(logic, {"score": 60}) == "medium"
        assert interpreter.evaluate(logic, {"score": 30}) == "low"


class TestRetry:
    """Test retry mechanisms"""

    @pytest.mark.asyncio
    async def test_retry_success(self):
        """Test successful retry"""
        policy = RetryPolicy(
            max_attempts=3,
            initial_interval_ms=10,
        )
        
        from temporal.workflows.engine.retry import RetryStrategy
        strategy = RetryStrategy(policy)
        
        call_count = 0
        
        async def flaky_task():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Temporary failure")
            return "success"
        
        result = await strategy.execute(flaky_task)
        
        assert result == "success"
        assert call_count == 2

    def test_backoff_calculation(self):
        """Test backoff calculation"""
        policy = RetryPolicy(
            max_attempts=5,
            initial_interval_ms=100,
            backoff_coefficient=2.0,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
        )
        
        from temporal.workflows.engine.retry import RetryStrategy
        strategy = RetryStrategy(policy)
        
        # Test exponential backoff
        assert strategy._calculate_backoff(1) == 100
        assert strategy._calculate_backoff(2) == 200
        assert strategy._calculate_backoff(3) == 400


class TestRecovery:
    """Test failure recovery"""

    @pytest.mark.asyncio
    async def test_checkpoint_creation(self):
        """Test checkpoint creation"""
        manager = CheckpointManager()
        
        checkpoint = await manager.create_checkpoint(
            workflow_id="test_workflow",
            state={"value": 42},
            completed_nodes=["task1", "task2"],
        )
        
        assert checkpoint.workflow_id == "test_workflow"
        assert checkpoint.state["value"] == 42
        assert len(checkpoint.completed_nodes) == 2

    @pytest.mark.asyncio
    async def test_checkpoint_restore(self):
        """Test checkpoint restoration"""
        manager = CheckpointManager()
        
        checkpoint = await manager.create_checkpoint(
            workflow_id="test_workflow",
            state={"value": 42},
            completed_nodes=["task1"],
        )
        
        restored = await manager.restore_checkpoint(checkpoint.id)
        
        assert restored is not None
        assert restored.workflow_id == "test_workflow"
        assert restored.state["value"] == 42


class TestWorkflowEngine:
    """Test workflow engine"""

    @pytest.mark.asyncio
    async def test_simple_workflow_execution(self):
        """Test simple workflow execution"""
        dag = DAG(name="test_workflow")
        dag.add_node(DAGNode(id="task1", task=simple_task))
        
        workflow_def = WorkflowDefinition(
            name="test_workflow",
            dag=dag,
        )
        
        engine = WorkflowEngine()
        execution = await engine.execute(workflow_def)
        
        assert execution.status.value == "completed"
        assert execution.result is not None

    @pytest.mark.asyncio
    async def test_workflow_with_retry(self):
        """Test workflow with retry policy"""
        dag = DAG(name="test_workflow")
        dag.add_node(DAGNode(id="task1", task=simple_task))
        
        workflow_def = WorkflowDefinition(
            name="test_workflow",
            dag=dag,
            retry_policies={
                "task1": RetryPolicy(max_attempts=3),
            },
        )
        
        engine = WorkflowEngine()
        execution = await engine.execute(workflow_def)
        
        assert execution.status.value == "completed"


class TestExampleWorkflows:
    """Test example workflows"""

    @pytest.mark.asyncio
    async def test_build_pipeline(self):
        """Test build pipeline workflow"""
        from temporal.workflows.engine.examples import create_build_pipeline
        
        workflow_def = create_build_pipeline()
        workflow_def.validate()
        
        assert workflow_def.name == "build_pipeline"
        assert len(workflow_def.dag.nodes) == 8

    @pytest.mark.asyncio
    async def test_security_scan(self):
        """Test security scan workflow"""
        from temporal.workflows.engine.examples import create_security_scan_workflow
        
        workflow_def = create_security_scan_workflow()
        workflow_def.validate()
        
        assert workflow_def.name == "security_scan"
        assert len(workflow_def.dag.nodes) == 9

    @pytest.mark.asyncio
    async def test_deployment(self):
        """Test deployment workflow"""
        from temporal.workflows.engine.examples import create_deployment_workflow
        
        workflow_def = create_deployment_workflow()
        workflow_def.validate()
        
        assert workflow_def.name == "deployment"
        assert len(workflow_def.dag.nodes) == 11


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
