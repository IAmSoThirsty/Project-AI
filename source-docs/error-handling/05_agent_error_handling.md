# Agent Error Handling Documentation

**Component**: AI Agent Error Recovery  
**Last Updated**: 2025-01-23  
**Maintainer**: Error Handling Documentation Specialist  

---

## Overview

AI agents in Project-AI operate with enhanced error handling through the **CognitionKernel** routing system. All agent operations flow through governance layers, risk assessment, and accountability tracking. This document covers agent-specific error patterns, oversight failure handling, and recovery mechanisms.

---

## Agent Architecture Error Flow

```
User Request
    ↓
Agent.execute_with_kernel()
    ↓
CognitionKernel.route_operation()
    ↓
├─ FourLaws.validate_action()
├─ SecurityEnforcementGateway.enforce()
├─ GovernanceEngine.check_policies()
└─ RiskAssessment.evaluate()
    ↓
[PASS] → Execute agent logic
[FAIL] → Raise AgentExecutionError
```

---

## CognitionKernel Integration

### KernelRoutedAgent Base Class

**Module**: `src/app/core/kernel_integration.py`  
**Purpose**: Base class for all agents requiring governance routing

```python
from app.core.cognition_kernel import CognitionKernel, ExecutionType

class KernelRoutedAgent:
    """Base class for agents that route operations through CognitionKernel."""
    
    def __init__(
        self,
        kernel: CognitionKernel | None = None,
        execution_type: ExecutionType = ExecutionType.AGENT_ACTION,
        default_risk_level: str = "medium",
    ):
        """Initialize kernel-routed agent.
        
        Args:
            kernel: CognitionKernel instance for routing (creates if None)
            execution_type: Type of execution for governance routing
            default_risk_level: Default risk level for operations
        """
        self.kernel = kernel or CognitionKernel()
        self.execution_type = execution_type
        self.default_risk_level = default_risk_level
    
    def execute_with_kernel(
        self,
        operation: str,
        context: dict,
        risk_level: str | None = None,
    ):
        """Execute operation through CognitionKernel with error handling."""
        risk_level = risk_level or self.default_risk_level
        
        try:
            # Route through kernel for governance checks
            result = self.kernel.route_operation(
                execution_type=self.execution_type,
                action=operation,
                context=context,
                user_id=context.get("user_id", "system"),
                risk_level=risk_level,
            )
            
            if not result.allowed:
                raise AgentExecutionError(
                    f"Operation blocked by kernel: {result.reason}",
                    operation=operation,
                    reason=result.reason,
                    risk_level=risk_level,
                )
            
            return result
        
        except Exception as e:
            logger.error(
                "Agent execution failed: %s (operation=%s)",
                e, operation
            )
            raise
```

**Key Features**:
- Automatic governance routing
- Risk level management
- Error propagation with context
- Audit trail integration

---

## Agent-Specific Exceptions

### AgentExecutionError

```python
class AgentExecutionError(Exception):
    """Raised when agent execution fails."""
    
    def __init__(
        self,
        message: str,
        operation: str,
        reason: str,
        risk_level: str,
        context: dict | None = None,
    ):
        self.operation = operation
        self.reason = reason
        self.risk_level = risk_level
        self.context = context or {}
        super().__init__(message)
```

**Usage Example**:
```python
try:
    result = agent.execute_with_kernel(
        operation="analyze_code",
        context={"file": "main.py", "user_id": "alice"},
    )
except AgentExecutionError as e:
    logger.error(
        "Agent execution blocked: %s (risk=%s)",
        e.reason, e.risk_level
    )
    # Record failure in agent metrics
    agent.metrics.record_failure(e.operation, e.reason)
```

---

### AgentTimeoutError

```python
import signal
from contextlib import contextmanager

class AgentTimeoutError(Exception):
    """Raised when agent operation times out."""
    pass

@contextmanager
def agent_timeout(seconds: int):
    """Context manager for agent operation timeout."""
    def timeout_handler(signum, frame):
        raise AgentTimeoutError(f"Operation timed out after {seconds}s")
    
    # Set timeout
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Restore original handler
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
```

**Usage Example**:
```python
try:
    with agent_timeout(30):
        result = agent.perform_long_operation()
except AgentTimeoutError as e:
    logger.warning("Agent operation timed out: %s", e)
    return {"status": "timeout", "partial_result": agent.get_partial_result()}
```

---

## Oversight Agent Error Handling

### OversightAgent Structure

**Module**: `src/app/agents/oversight.py`  
**Lines**: 13-42  

```python
class OversightAgent(KernelRoutedAgent):
    """Monitors system state and enforces compliance rules."""
    
    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        """Initialize the oversight agent with system monitors."""
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",
        )
        
        # Placeholder state (disabled by default)
        self.enabled: bool = False
        self.monitors: dict = {}
```

**Error Handling Pattern**:
```python
def monitor_system_health(self) -> dict:
    """Monitor system health with error isolation."""
    results = {
        "overall_status": "unknown",
        "monitors": {},
        "errors": [],
    }
    
    for monitor_name, monitor_func in self.monitors.items():
        try:
            status = monitor_func()
            results["monitors"][monitor_name] = status
        except Exception as e:
            logger.error(
                "Monitor '%s' failed: %s",
                monitor_name, e
            )
            results["errors"].append({
                "monitor": monitor_name,
                "error": str(e),
            })
            # Continue with other monitors (isolation)
    
    # Determine overall status
    if not results["errors"]:
        results["overall_status"] = "healthy"
    elif len(results["errors"]) < len(self.monitors) / 2:
        results["overall_status"] = "degraded"
    else:
        results["overall_status"] = "critical"
    
    return results
```

**Key Principle**: Monitor failures don't cascade
- Each monitor isolated in try-except
- Collect all errors for reporting
- Continue with remaining monitors
- Aggregate status at end

---

## Planner Agent Error Handling

### PlannerAgent Structure

**Module**: `src/app/agents/planner.py`  
**Purpose**: Task decomposition with error recovery

```python
class PlannerAgent(KernelRoutedAgent):
    """Decomposes complex tasks into executable steps."""
    
    def __init__(self, kernel: CognitionKernel | None = None):
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",  # Planning is low-risk
        )
    
    def decompose_task(self, task: str, context: dict) -> list[dict]:
        """Decompose task with error handling."""
        try:
            # Route through kernel
            result = self.execute_with_kernel(
                operation="decompose_task",
                context={"task": task, **context},
                risk_level="low",
            )
            
            # Perform decomposition
            steps = self._perform_decomposition(task, context)
            
            # Validate steps
            self._validate_plan_steps(steps)
            
            return steps
        
        except AgentExecutionError as e:
            logger.error("Task decomposition blocked: %s", e.reason)
            # Return empty plan with error indicator
            return [{
                "status": "error",
                "reason": "Task decomposition blocked by policy",
                "original_task": task,
            }]
        
        except Exception as e:
            logger.error("Task decomposition failed: %s", e)
            # Return simple single-step plan as fallback
            return [{
                "step": 1,
                "action": "manual_execution",
                "description": f"Execute task manually: {task}",
                "reason": f"Automatic decomposition failed: {str(e)}",
            }]
    
    def _validate_plan_steps(self, steps: list[dict]) -> None:
        """Validate plan steps for safety."""
        for i, step in enumerate(steps):
            # Check for required fields
            if "action" not in step:
                raise ValueError(f"Step {i} missing 'action' field")
            
            # Check for circular dependencies
            deps = step.get("depends_on", [])
            if i in deps:
                raise ValueError(f"Step {i} has circular dependency")
            
            # Check for invalid dependencies
            for dep in deps:
                if dep >= len(steps):
                    raise ValueError(
                        f"Step {i} depends on non-existent step {dep}"
                    )
```

**Recovery Strategy**: Graceful degradation
- Blocked by policy → Return error indicator
- Decomposition fails → Return manual execution step
- Validation fails → Raise exception (unsafe plan)

---

## Validator Agent Error Handling

### ValidatorAgent Structure

**Module**: `src/app/agents/validator.py`  
**Purpose**: Input/output validation with safe defaults

```python
class ValidatorAgent(KernelRoutedAgent):
    """Validates inputs and outputs for safety and correctness."""
    
    def __init__(self, kernel: CognitionKernel | None = None):
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",
        )
        self.validation_rules = {}
    
    def validate_input(
        self,
        input_data: Any,
        schema: dict,
        context: dict,
    ) -> tuple[bool, str]:
        """Validate input with comprehensive error handling."""
        try:
            # Route through kernel
            self.execute_with_kernel(
                operation="validate_input",
                context={"schema": schema, **context},
            )
            
            # Perform validation
            is_valid, errors = self._validate_against_schema(
                input_data, schema
            )
            
            if not is_valid:
                logger.warning("Input validation failed: %s", errors)
                return False, "; ".join(errors)
            
            return True, "Validation passed"
        
        except AgentExecutionError as e:
            logger.error("Validation blocked by policy: %s", e.reason)
            # SAFE DEFAULT: Reject input when validation blocked
            return False, "Validation service unavailable"
        
        except Exception as e:
            logger.error("Validation error: %s", e)
            # SAFE DEFAULT: Reject input on validation error
            return False, f"Validation error: {str(e)}"
    
    def _validate_against_schema(
        self,
        data: Any,
        schema: dict,
    ) -> tuple[bool, list[str]]:
        """Validate data against schema."""
        errors = []
        
        try:
            # Type validation
            expected_type = schema.get("type")
            if expected_type and not isinstance(data, expected_type):
                errors.append(
                    f"Expected {expected_type.__name__}, "
                    f"got {type(data).__name__}"
                )
            
            # Range validation
            if "min" in schema and data < schema["min"]:
                errors.append(f"Value {data} below minimum {schema['min']}")
            if "max" in schema and data > schema["max"]:
                errors.append(f"Value {data} above maximum {schema['max']}")
            
            # Pattern validation
            if "pattern" in schema:
                import re
                if not re.match(schema["pattern"], str(data)):
                    errors.append(
                        f"Value does not match pattern {schema['pattern']}"
                    )
            
            return len(errors) == 0, errors
        
        except Exception as e:
            logger.error("Schema validation error: %s", e)
            return False, [f"Validation error: {str(e)}"]
```

**Safety Principle**: Fail closed
- Validation error → Reject input (safe default)
- Policy blocks validation → Reject input
- Schema error → Reject input
- NEVER allow unvalidated input through

---

## Explainability Agent Error Handling

### ExplainabilityAgent Structure

**Module**: `src/app/agents/explainability.py`  
**Purpose**: Generate explanations for AI decisions

```python
class ExplainabilityAgent(KernelRoutedAgent):
    """Generates human-readable explanations for AI decisions."""
    
    def explain_decision(
        self,
        decision: dict,
        context: dict,
    ) -> str:
        """Generate explanation with error handling."""
        try:
            # Route through kernel
            self.execute_with_kernel(
                operation="generate_explanation",
                context={"decision": decision, **context},
            )
            
            # Generate explanation
            explanation = self._generate_explanation(decision, context)
            
            # Validate explanation quality
            if not self._is_explanation_adequate(explanation):
                logger.warning("Generated explanation is inadequate")
                return self._get_fallback_explanation(decision)
            
            return explanation
        
        except AgentExecutionError as e:
            logger.error("Explanation generation blocked: %s", e.reason)
            return self._get_fallback_explanation(decision)
        
        except Exception as e:
            logger.error("Explanation generation failed: %s", e)
            return self._get_fallback_explanation(decision)
    
    def _get_fallback_explanation(self, decision: dict) -> str:
        """Generate simple fallback explanation."""
        return (
            f"Decision: {decision.get('action', 'unknown')}. "
            f"Detailed explanation unavailable. "
            f"Reason: {decision.get('reason', 'not specified')}."
        )
    
    def _is_explanation_adequate(self, explanation: str) -> bool:
        """Check if explanation meets quality standards."""
        # Minimum length check
        if len(explanation) < 50:
            return False
        
        # Must contain key phrases
        required_phrases = ["because", "due to", "reason"]
        if not any(phrase in explanation.lower() for phrase in required_phrases):
            return False
        
        return True
```

**Error Handling Strategy**: Always provide explanation
- Primary generation fails → Use fallback
- Policy blocks generation → Use fallback
- Quality check fails → Use fallback
- NEVER return empty explanation

---

## Multi-Agent Error Coordination

### Agent Orchestra Pattern

```python
class AgentOrchestrator:
    """Coordinates multiple agents with error handling."""
    
    def __init__(self):
        self.kernel = CognitionKernel()
        self.planner = PlannerAgent(self.kernel)
        self.validator = ValidatorAgent(self.kernel)
        self.oversight = OversightAgent(self.kernel)
    
    def execute_task(self, task: str, context: dict) -> dict:
        """Execute task with multi-agent coordination."""
        results = {
            "task": task,
            "status": "unknown",
            "steps": [],
            "errors": [],
        }
        
        try:
            # Step 1: Validate input
            is_valid, validation_msg = self.validator.validate_input(
                task, {"type": str, "min": 10}, context
            )
            
            if not is_valid:
                results["status"] = "validation_failed"
                results["errors"].append(validation_msg)
                return results
            
            # Step 2: Decompose task
            steps = self.planner.decompose_task(task, context)
            results["steps"] = steps
            
            # Step 3: Execute steps with oversight
            for i, step in enumerate(steps):
                try:
                    # Check oversight before each step
                    oversight_status = self.oversight.monitor_system_health()
                    if oversight_status["overall_status"] == "critical":
                        raise AgentExecutionError(
                            "System health critical",
                            operation=step["action"],
                            reason="Critical system health status",
                            risk_level="high",
                        )
                    
                    # Execute step
                    step_result = self._execute_step(step, context)
                    results["steps"][i]["result"] = step_result
                    results["steps"][i]["status"] = "completed"
                
                except Exception as e:
                    logger.error("Step %d failed: %s", i, e)
                    results["steps"][i]["status"] = "failed"
                    results["steps"][i]["error"] = str(e)
                    results["errors"].append(f"Step {i}: {str(e)}")
                    
                    # Decide whether to continue or abort
                    if step.get("critical", False):
                        results["status"] = "aborted"
                        return results
                    # Non-critical step: continue
            
            # All steps completed
            results["status"] = "completed"
            return results
        
        except Exception as e:
            logger.error("Task execution failed: %s", e)
            results["status"] = "failed"
            results["errors"].append(str(e))
            return results
```

**Key Patterns**:
- **Validation first**: Validate before any work
- **Step isolation**: Each step in try-except
- **Critical vs non-critical**: Continue or abort based on step importance
- **Oversight monitoring**: Check health before each step
- **Comprehensive error collection**: Aggregate all errors for debugging

---

## Agent Retry Strategies

### Retry with Backoff

```python
def agent_retry_with_backoff(
    agent_func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    retryable_exceptions: tuple = (AgentTimeoutError, TransientError),
) -> Any:
    """Retry agent operation with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return agent_func()
        
        except retryable_exceptions as e:
            if attempt == max_attempts - 1:
                logger.error("Agent retry exhausted after %d attempts", max_attempts)
                raise
            
            delay = base_delay * (2 ** attempt)
            logger.warning(
                "Agent operation failed (attempt %d/%d): %s. Retrying in %.1fs",
                attempt + 1, max_attempts, e, delay
            )
            time.sleep(delay)
        
        except AgentExecutionError as e:
            # Security/policy violations should NOT be retried
            logger.error("Agent operation blocked by policy: %s", e.reason)
            raise
        
        except Exception as e:
            # Unknown errors - fail fast
            logger.error("Agent operation failed with unexpected error: %s", e)
            raise
```

**Retry Decision Matrix**:
- `AgentTimeoutError` → Retry (transient)
- `TransientError` → Retry (transient)
- `AgentExecutionError` → NO RETRY (policy violation)
- `SecurityViolationException` → NO RETRY (security)
- `ConstitutionalViolationError` → NO RETRY (ethics)
- Generic `Exception` → NO RETRY (unknown state)

---

## Agent Testing Error Scenarios

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch

class TestAgentErrorHandling:
    """Test agent error handling patterns."""
    
    def test_agent_execution_blocked_by_policy(self):
        """Test that policy violations prevent execution."""
        kernel = Mock()
        kernel.route_operation.return_value = Mock(
            allowed=False,
            reason="Policy violation: unauthorized action"
        )
        
        agent = MyAgent(kernel=kernel)
        
        with pytest.raises(AgentExecutionError) as exc_info:
            agent.execute_with_kernel(
                operation="risky_action",
                context={"user_id": "test"},
            )
        
        assert "Policy violation" in str(exc_info.value)
    
    def test_agent_timeout_recovery(self):
        """Test agent timeout with partial result recovery."""
        agent = MyAgent()
        
        # Mock long-running operation
        with patch.object(agent, 'perform_operation') as mock_op:
            mock_op.side_effect = AgentTimeoutError("Timeout after 30s")
            
            result = agent.execute_with_timeout(30)
            
            assert result["status"] == "timeout"
            assert "partial_result" in result
    
    def test_multi_agent_error_isolation(self):
        """Test that one agent's failure doesn't cascade."""
        orchestrator = AgentOrchestrator()
        
        # Make planner fail
        with patch.object(orchestrator.planner, 'decompose_task') as mock_plan:
            mock_plan.side_effect = Exception("Planner error")
            
            result = orchestrator.execute_task("test task", {})
            
            # Should return error result, not crash
            assert result["status"] == "failed"
            assert len(result["errors"]) > 0
```

---

## Best Practices

### ✅ Always Route Through CognitionKernel

```python
# GOOD: Uses kernel routing for governance
class MyAgent(KernelRoutedAgent):
    def my_operation(self, context):
        self.execute_with_kernel("operation", context)

# BAD: Bypasses governance
class MyAgent:
    def my_operation(self, context):
        self.direct_execution()  # No oversight!
```

### ✅ Isolate Agent Failures

```python
# GOOD: Each agent isolated
for agent in agents:
    try:
        agent.execute()
    except:
        logger.error("Agent failed")
        continue  # Other agents continue

# BAD: One failure kills all
for agent in agents:
    agent.execute()  # First failure aborts all
```

### ✅ Provide Fallback Mechanisms

```python
# GOOD: Always returns usable result
def explain_decision(self, decision):
    try:
        return self.generate_explanation(decision)
    except:
        return self.fallback_explanation(decision)

# BAD: May return nothing
def explain_decision(self, decision):
    return self.generate_explanation(decision)  # May crash
```

---

## References

- **Kernel Integration**: `src/app/core/kernel_integration.py`
- **Oversight Agent**: `src/app/agents/oversight.py`
- **Planner Agent**: `src/app/agents/planner.py`
- **Validator Agent**: `src/app/agents/validator.py`
- **Explainability Agent**: `src/app/agents/explainability.py`
- **CognitionKernel**: `src/app/core/cognition_kernel.py`

---

**Next Steps**:
1. Implement agent health monitoring dashboard
2. Add agent error metrics to telemetry
3. Create agent debugging CLI tool
4. Document agent coordination patterns
