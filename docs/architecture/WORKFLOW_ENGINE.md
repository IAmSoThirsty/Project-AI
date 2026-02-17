# Workflow Engine Specification

**Version:** 1.0 **Last Updated:** 2026-01-23 **Status:** Specification

______________________________________________________________________

## Overview

The Workflow Engine orchestrates complex, multi-step processes within the PACE system. It manages workflow definitions, executes workflow instances, handles state transitions, and ensures reliable execution with support for error handling, retries, and rollbacks.

## Core Concepts

### What is a Workflow?

A **workflow** is a structured sequence of steps that accomplishes a complex task. Workflows can:

- Execute steps sequentially or in parallel
- Make decisions based on conditions
- Handle errors and retry failed steps
- Maintain state across executions
- Be paused and resumed

### Workflow Components

1. **Workflow Definition**: Template defining steps and flow
1. **Workflow Instance**: Running execution of a workflow
1. **Workflow Step**: Individual unit of work in a workflow
1. **Workflow State**: Current execution state and data

## Architecture

```
┌──────────────────────────────────────────┐
│       Workflow Engine                     │
├──────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐         │
│  │  Workflow  │  │  Execution │         │
│  │  Registry  │  │   Manager  │         │
│  └────────────┘  └────────────┘         │
│                                          │
│  ┌────────────┐  ┌────────────┐         │
│  │   State    │  │   Event    │         │
│  │  Manager   │  │   Handler  │         │
│  └────────────┘  └────────────┘         │
└──────────────────────────────────────────┘
```

## Workflow Definition

### Workflow Class

```python
@dataclass
class Workflow:
    """
    Defines a workflow template.

    A workflow is a graph of steps with dependencies, conditions,
    and error handling logic.
    """
    workflow_id: str
    name: str
    description: str
    version: str
    steps: List[WorkflowStep]
    metadata: Dict[str, Any]

    def validate(self) -> Tuple[bool, str]:
        """
        Validate workflow definition.

        Returns:
            Tuple of (valid, error_message)
        """

        # Check for cycles

        if self._has_cycles():
            return False, "Workflow contains cycles"

        # Check all dependencies exist

        step_ids = {step.step_id for step in self.steps}
        for step in self.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    return False, f"Step '{step.step_id}' has invalid dependency '{dep}'"

        return True, ""

    def _has_cycles(self) -> bool:
        """Check if workflow has cycles using DFS."""

        # Implementation of cycle detection

        return False

@dataclass
class WorkflowStep:
    """
    Defines a single step in a workflow.
    """
    step_id: str
    name: str
    step_type: str  # agent, capability, decision, parallel, sequential
    parameters: Dict[str, Any]
    dependencies: List[str]  # step_ids this step depends on
    condition: Optional[str] = None  # Optional execution condition
    on_failure: str = "fail"  # fail, retry, skip, rollback
    retry_config: Optional[RetryConfig] = None
    timeout: Optional[int] = None  # seconds

@dataclass
class RetryConfig:
    """Configuration for step retries."""
    max_attempts: int = 3
    backoff_multiplier: float = 2.0
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
```

## Workflow Engine Implementation

### WorkflowEngine Class

```python
class WorkflowEngine:
    """
    Orchestrates workflow execution.

    The WorkflowEngine is responsible for:

    - Registering workflow definitions
    - Creating and managing workflow instances
    - Executing workflow steps in correct order
    - Handling errors and retries
    - Persisting workflow state
    - Providing workflow status and history

    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the workflow engine.

        Args:
            config: Configuration containing:

                - max_concurrent: Maximum concurrent workflows (default: 10)
                - persistence: Enable state persistence (default: True)
                - state_backend: State storage backend (json, db)
                - data_dir: Directory for persistent storage

        """
        self.config = config
        self.workflows: Dict[str, Workflow] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self.execution_manager = ExecutionManager(config)
        self.state_manager = WorkflowStateManager(config)
        self.event_handler = EventHandler()
        self.max_concurrent = config.get("max_concurrent", 10)

    def register_workflow(self, workflow: Workflow) -> None:
        """
        Register a workflow definition.

        Args:
            workflow: Workflow to register

        Raises:
            WorkflowError: If workflow validation fails
        """

        # Validate workflow

        valid, error = workflow.validate()
        if not valid:
            raise WorkflowError(f"Workflow validation failed: {error}")

        self.workflows[workflow.workflow_id] = workflow
        logger.info(f"Registered workflow: {workflow.name} ({workflow.workflow_id})")

    def unregister_workflow(self, workflow_id: str) -> None:
        """
        Unregister a workflow.

        Args:
            workflow_id: Workflow identifier
        """
        if workflow_id in self.workflows:

            # Check for running instances

            running = [
                i for i in self.instances.values()
                if i.workflow_id == workflow_id and i.status == "running"
            ]
            if running:
                raise WorkflowError(
                    f"Cannot unregister workflow with {len(running)} running instances"
                )

            del self.workflows[workflow_id]
            logger.info(f"Unregistered workflow: {workflow_id}")

    def execute_workflow(
        self,
        workflow_id: str,
        context: Dict[str, Any]
    ) -> WorkflowInstance:
        """
        Execute a workflow.

        Args:
            workflow_id: Workflow template identifier
            context: Execution context and input parameters

        Returns:
            WorkflowInstance: Running workflow instance

        Raises:
            WorkflowNotFoundError: If workflow not registered
            WorkflowError: If execution fails to start
        """

        # Get workflow definition

        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise WorkflowNotFoundError(f"Workflow '{workflow_id}' not found")

        # Check concurrent limit

        running_count = sum(
            1 for i in self.instances.values()
            if i.status == "running"
        )
        if running_count >= self.max_concurrent:
            raise WorkflowError(
                f"Maximum concurrent workflow limit ({self.max_concurrent}) reached"
            )

        # Create instance

        instance = WorkflowInstance(
            instance_id=self._generate_instance_id(),
            workflow_id=workflow_id,
            status="running",
            started_at=datetime.now(),
            completed_at=None,
            result=None,
            context=context,
            step_results={}
        )

        self.instances[instance.instance_id] = instance

        # Start execution in background

        self.execution_manager.execute(workflow, instance)

        return instance

    def get_workflow_status(self, instance_id: str) -> WorkflowStatus:
        """
        Get workflow instance status.

        Args:
            instance_id: Workflow instance identifier

        Returns:
            WorkflowStatus: Current workflow status

        Raises:
            WorkflowError: If instance not found
        """
        instance = self.instances.get(instance_id)
        if not instance:
            raise WorkflowError(f"Workflow instance '{instance_id}' not found")

        # Calculate progress

        workflow = self.workflows[instance.workflow_id]
        completed_steps = len(instance.step_results)
        total_steps = len(workflow.steps)
        progress = completed_steps / total_steps if total_steps > 0 else 0.0

        return WorkflowStatus(
            instance_id=instance.instance_id,
            status=instance.status,
            current_step=self._get_current_step(instance),
            progress=progress,
            metadata={
                "completed_steps": completed_steps,
                "total_steps": total_steps,
                "started_at": instance.started_at.isoformat(),
                "duration": (datetime.now() - instance.started_at).total_seconds()
            }
        )

    def cancel_workflow(self, instance_id: str) -> None:
        """
        Cancel a running workflow.

        Args:
            instance_id: Workflow instance identifier
        """
        instance = self.instances.get(instance_id)
        if not instance:
            raise WorkflowError(f"Workflow instance '{instance_id}' not found")

        if instance.status != "running":
            raise WorkflowError(
                f"Cannot cancel workflow in status '{instance.status}'"
            )

        # Request cancellation

        instance.status = "canceled"
        instance.completed_at = datetime.now()

        # Notify execution manager

        self.execution_manager.cancel(instance_id)

        logger.info(f"Canceled workflow instance: {instance_id}")

    def pause_workflow(self, instance_id: str) -> None:
        """Pause a running workflow."""
        instance = self.instances.get(instance_id)
        if instance and instance.status == "running":
            instance.status = "paused"
            self.execution_manager.pause(instance_id)

    def resume_workflow(self, instance_id: str) -> None:
        """Resume a paused workflow."""
        instance = self.instances.get(instance_id)
        if instance and instance.status == "paused":
            instance.status = "running"
            self.execution_manager.resume(instance_id)

    def get_workflow_history(self, workflow_id: str) -> List[WorkflowInstance]:
        """Get execution history for a workflow."""
        return [
            i for i in self.instances.values()
            if i.workflow_id == workflow_id
        ]

    def _get_current_step(self, instance: WorkflowInstance) -> Optional[str]:
        """Get the currently executing step."""

        # Implementation to find current step

        return None

    def _generate_instance_id(self) -> str:
        """Generate unique instance ID."""
        import uuid
        return f"workflow-{uuid.uuid4().hex[:8]}"
```

## Execution Manager

### ExecutionManager Class

```python
class ExecutionManager:
    """
    Manages workflow execution.

    Handles:

    - Step execution order (respecting dependencies)
    - Parallel execution of independent steps
    - Error handling and retries
    - State persistence

    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize execution manager.

        Args:
            config: Execution configuration
        """
        self.config = config
        self.active_executions: Dict[str, threading.Thread] = {}
        self.capability_invoker: Optional['CapabilityInvoker'] = None
        self.agent_coordinator: Optional['AgentCoordinator'] = None

    def execute(self, workflow: Workflow, instance: WorkflowInstance) -> None:
        """
        Execute a workflow instance.

        Args:
            workflow: Workflow definition
            instance: Workflow instance to execute
        """

        # Start execution thread

        thread = threading.Thread(
            target=self._execute_workflow,
            args=(workflow, instance)
        )
        thread.start()
        self.active_executions[instance.instance_id] = thread

    def _execute_workflow(self, workflow: Workflow, instance: WorkflowInstance) -> None:
        """Execute workflow steps."""
        try:

            # Build execution plan

            execution_plan = self._build_execution_plan(workflow)

            # Execute steps according to plan

            for step_group in execution_plan:
                if instance.status != "running":
                    break

                # Execute steps in parallel (if multiple in group)

                results = self._execute_step_group(workflow, instance, step_group)

                # Update instance with results

                for step_id, result in results.items():
                    instance.step_results[step_id] = result

                    # Check for failures

                    if not result.success:
                        step = self._get_step(workflow, step_id)
                        if step.on_failure == "fail":
                            instance.status = "failed"
                            break

            # Mark as completed if all steps succeeded

            if instance.status == "running":
                instance.status = "completed"
                instance.completed_at = datetime.now()

        except Exception as e:
            instance.status = "failed"
            instance.completed_at = datetime.now()
            logger.error(f"Workflow execution failed: {e}")

    def _build_execution_plan(self, workflow: Workflow) -> List[List[str]]:
        """
        Build execution plan respecting dependencies.

        Returns a list of step groups, where steps in each group
        can be executed in parallel.
        """

        # Topological sort to determine execution order

        steps_by_id = {step.step_id: step for step in workflow.steps}
        in_degree = {step.step_id: len(step.dependencies) for step in workflow.steps}
        plan = []

        while in_degree:

            # Find steps with no dependencies

            ready = [sid for sid, deg in in_degree.items() if deg == 0]
            if not ready:
                break

            plan.append(ready)

            # Remove ready steps and update in_degree

            for sid in ready:
                del in_degree[sid]

                # Decrement in_degree for dependents

                for other_sid, step in steps_by_id.items():
                    if other_sid in in_degree and sid in step.dependencies:
                        in_degree[other_sid] -= 1

        return plan

    def _execute_step_group(
        self,
        workflow: Workflow,
        instance: WorkflowInstance,
        step_ids: List[str]
    ) -> Dict[str, StepResult]:
        """Execute a group of steps in parallel."""
        results = {}

        # Execute steps (simplified - in reality use thread pool)

        for step_id in step_ids:
            step = self._get_step(workflow, step_id)
            result = self._execute_step(workflow, instance, step)
            results[step_id] = result

        return results

    def _execute_step(
        self,
        workflow: Workflow,
        instance: WorkflowInstance,
        step: WorkflowStep
    ) -> 'StepResult':
        """Execute a single workflow step."""

        # Check condition

        if step.condition and not self._evaluate_condition(step.condition, instance):
            return StepResult(
                step_id=step.step_id,
                success=True,
                result="skipped",
                error=None
            )

        # Execute based on step type

        if step.step_type == "capability":
            return self._execute_capability_step(step, instance)
        elif step.step_type == "agent":
            return self._execute_agent_step(step, instance)
        elif step.step_type == "decision":
            return self._execute_decision_step(step, instance)
        else:
            return StepResult(
                step_id=step.step_id,
                success=False,
                result=None,
                error=f"Unknown step type: {step.step_type}"
            )

    def _execute_capability_step(
        self,
        step: WorkflowStep,
        instance: WorkflowInstance
    ) -> 'StepResult':
        """Execute a capability step."""
        capability_id = step.parameters.get("capability_id")
        params = step.parameters.get("params", {})

        # Invoke capability

        result = self.capability_invoker.invoke(capability_id, params)

        return StepResult(
            step_id=step.step_id,
            success=result.success,
            result=result.result,
            error=result.error
        )

    def _execute_agent_step(
        self,
        step: WorkflowStep,
        instance: WorkflowInstance
    ) -> 'StepResult':
        """Execute an agent step."""
        task = Task(
            task_id=f"{instance.instance_id}-{step.step_id}",
            task_type=step.parameters.get("task_type"),
            description=step.name,
            parameters=step.parameters.get("params", {}),
            priority=1
        )

        # Execute via agent coordinator

        result = self.agent_coordinator.execute_task(task)

        return StepResult(
            step_id=step.step_id,
            success=result.success,
            result=result.result,
            error=result.error
        )

    def _execute_decision_step(
        self,
        step: WorkflowStep,
        instance: WorkflowInstance
    ) -> 'StepResult':
        """Execute a decision step."""

        # Evaluate decision condition

        condition = step.parameters.get("condition")
        result = self._evaluate_condition(condition, instance)

        return StepResult(
            step_id=step.step_id,
            success=True,
            result=result,
            error=None
        )

    def _evaluate_condition(self, condition: str, instance: WorkflowInstance) -> bool:
        """Evaluate a conditional expression."""

        # In real implementation, use safe eval or expression engine

        return True

    def _get_step(self, workflow: Workflow, step_id: str) -> WorkflowStep:
        """Get step by ID."""
        for step in workflow.steps:
            if step.step_id == step_id:
                return step
        raise WorkflowError(f"Step '{step_id}' not found")

    def cancel(self, instance_id: str) -> None:
        """Cancel workflow execution."""

        # Implementation to cancel execution

        pass

    def pause(self, instance_id: str) -> None:
        """Pause workflow execution."""
        pass

    def resume(self, instance_id: str) -> None:
        """Resume workflow execution."""
        pass

@dataclass
class StepResult:
    """Result of a workflow step execution."""
    step_id: str
    success: bool
    result: Any
    error: Optional[str]
```

## Workflow State Management

```python
class WorkflowStateManager:
    """
    Manages workflow state persistence.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize state manager.

        Args:
            config: State management configuration
        """
        self.config = config
        self.backend = config.get("state_backend", "json")
        self.data_dir = config.get("data_dir", "./data/workflows")
        os.makedirs(self.data_dir, exist_ok=True)

    def save_instance(self, instance: WorkflowInstance) -> None:
        """Save workflow instance state."""
        file_path = os.path.join(self.data_dir, f"{instance.instance_id}.json")
        with open(file_path, "w") as f:
            json.dump(self._serialize_instance(instance), f, indent=2)

    def load_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Load workflow instance state."""
        file_path = os.path.join(self.data_dir, f"{instance_id}.json")
        if not os.path.exists(file_path):
            return None

        with open(file_path, "r") as f:
            data = json.load(f)
            return self._deserialize_instance(data)

    def _serialize_instance(self, instance: WorkflowInstance) -> Dict[str, Any]:
        """Serialize instance to dict."""
        return {
            "instance_id": instance.instance_id,
            "workflow_id": instance.workflow_id,
            "status": instance.status,
            "started_at": instance.started_at.isoformat(),
            "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
            "result": instance.result,
            "context": instance.context,
            "step_results": {k: self._serialize_result(v) for k, v in instance.step_results.items()}
        }

    def _deserialize_instance(self, data: Dict[str, Any]) -> WorkflowInstance:
        """Deserialize instance from dict."""

        # Implementation

        pass

    def _serialize_result(self, result: StepResult) -> Dict[str, Any]:
        """Serialize step result."""
        return {
            "step_id": result.step_id,
            "success": result.success,
            "result": result.result,
            "error": result.error
        }
```

## Configuration

```yaml
workflow:
  max_concurrent: 10
  persistence: true
  state_backend: "json"  # json, postgresql, mongodb
  data_dir: "./data/workflows"

  execution:
    parallel_steps: true
    step_timeout: 300  # seconds

  retry:
    default_max_attempts: 3
    default_backoff: 2.0
    default_initial_delay: 1.0

  monitoring:
    track_metrics: true
    log_executions: true
```

## See Also

- [MODULE_CONTRACTS.md](MODULE_CONTRACTS.md) - WorkflowEngine interface
- [AGENT_MODEL.md](AGENT_MODEL.md) - Agent integration
- [CAPABILITY_MODEL.md](CAPABILITY_MODEL.md) - Capability integration
- [STATE_MODEL.md](STATE_MODEL.md) - State management
