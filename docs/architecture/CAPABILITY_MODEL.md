# Capability Model Specification

**Version:** 1.0 **Last Updated:** 2026-01-23 **Status:** Specification

______________________________________________________________________

## Overview

The Capability Model defines how discrete, executable units of functionality are registered, invoked, and managed within the PACE system. Capabilities are the building blocks for agent actions and workflow steps.

## Core Concepts

### What is a Capability?

A **capability** is a discrete, well-defined unit of functionality that:

- Has a clear interface (inputs and outputs)
- Can be invoked independently
- Executes in a sandboxed environment
- Is composable with other capabilities
- Can be validated and monitored

### Capability Types

1. **System Capabilities**: Core functionality (file I/O, network, etc.)
1. **Domain Capabilities**: Domain-specific operations (data analysis, ML inference, etc.)
1. **Integration Capabilities**: External system integrations (APIs, databases, etc.)
1. **Agent Capabilities**: Agent-specific skills and actions

## Architecture

```
┌──────────────────────────────────────────┐
│       Capability Invoker                  │
├──────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐         │
│  │ Capability │  │  Sandbox   │         │
│  │  Registry  │  │  Manager   │         │
│  └────────────┘  └────────────┘         │
│                                          │
│  ┌────────────┐  ┌────────────┐         │
│  │ Validation │  │ Monitoring │         │
│  │  Engine    │  │   Engine   │         │
│  └────────────┘  └────────────┘         │
└──────────────────────────────────────────┘
           │
           ├──→ System Capabilities
           ├──→ Domain Capabilities
           ├──→ Integration Capabilities
           └──→ Agent Capabilities
```

## Capability Interface

### Base Capability Class

```python
class Capability(ABC):
    """
    Base class for all capabilities.

    A capability represents a discrete unit of functionality that can be
    invoked with parameters and returns a result.
    """

    def __init__(self):
        """Initialize the capability."""
        self.capability_id = self._generate_id()
        self.name = self.__class__.__name__
        self.description = self.__doc__ or "No description"
        self.parameters = self._define_parameters()
        self.metadata = {}

    @abstractmethod
    def invoke(self, params: Dict[str, Any]) -> Any:
        """
        Execute the capability.

        Args:
            params: Parameters for capability execution

        Returns:
            Capability execution result

        Raises:
            CapabilityError: If execution fails
        """
        pass

    @abstractmethod
    def _define_parameters(self) -> List[ParameterInfo]:
        """
        Define capability parameters.

        Returns:
            List of parameter definitions
        """
        pass

    def validate_params(self, params: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate input parameters.

        Args:
            params: Parameters to validate

        Returns:
            Tuple of (valid, error_message)
        """
        for param_info in self.parameters:
            if param_info.required and param_info.name not in params:
                return False, f"Required parameter '{param_info.name}' missing"

            if param_info.name in params:
                value = params[param_info.name]
                if not self._validate_type(value, param_info.type):
                    return False, f"Parameter '{param_info.name}' has invalid type"

        return True, ""

    def get_info(self) -> CapabilityInfo:
        """
        Get capability information.

        Returns:
            CapabilityInfo: Capability metadata
        """
        return CapabilityInfo(
            capability_id=self.capability_id,
            name=self.name,
            description=self.description,
            parameters=self.parameters
        )
```

## Capability Invoker

### CapabilityInvoker Class

```python
class CapabilityInvoker:
    """
    Manages capability registration and invocation.

    The CapabilityInvoker is responsible for:

    - Registering and unregistering capabilities
    - Validating capability invocations
    - Executing capabilities in sandboxed environments
    - Monitoring capability performance
    - Enforcing resource limits

    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the capability invoker.

        Args:
            config: Configuration containing:

                - sandboxing_enabled: Enable/disable sandboxing (default: True)
                - max_execution_time: Max execution time in seconds (default: 30)
                - max_memory_mb: Max memory usage in MB (default: 512)
                - monitoring_enabled: Enable performance monitoring (default: True)

        """
        self.config = config
        self.capabilities: Dict[str, Capability] = {}
        self.sandbox_manager = SandboxManager(config)
        self.validation_engine = ValidationEngine()
        self.monitoring_engine = MonitoringEngine(config)

        # Resource limits

        self.max_execution_time = config.get("max_execution_time", 30)
        self.max_memory_mb = config.get("max_memory_mb", 512)

    def register_capability(self, capability: Capability) -> None:
        """
        Register a capability with the invoker.

        Args:
            capability: Capability to register

        Raises:
            CapabilityError: If capability_id already registered
        """
        if capability.capability_id in self.capabilities:
            raise CapabilityError(
                f"Capability '{capability.capability_id}' already registered"
            )

        # Validate capability

        if not self._validate_capability(capability):
            raise CapabilityError(f"Capability '{capability.name}' validation failed")

        self.capabilities[capability.capability_id] = capability
        logger.info(f"Registered capability: {capability.name} ({capability.capability_id})")

    def unregister_capability(self, capability_id: str) -> None:
        """
        Unregister a capability.

        Args:
            capability_id: Capability identifier
        """
        if capability_id in self.capabilities:
            del self.capabilities[capability_id]
            logger.info(f"Unregistered capability: {capability_id}")

    def invoke(self, capability_id: str, params: Dict[str, Any]) -> CapabilityResult:
        """
        Invoke a capability.

        Args:
            capability_id: Capability identifier
            params: Invocation parameters

        Returns:
            CapabilityResult: Execution result

        Raises:
            CapabilityNotFoundError: If capability not registered
            CapabilityError: If invocation fails
        """

        # Get capability

        capability = self.capabilities.get(capability_id)
        if not capability:
            raise CapabilityNotFoundError(f"Capability '{capability_id}' not found")

        # Validate parameters

        valid, error_msg = capability.validate_params(params)
        if not valid:
            raise CapabilityError(f"Parameter validation failed: {error_msg}")

        # Start monitoring

        execution_id = self.monitoring_engine.start_execution(capability_id)

        try:

            # Execute in sandbox

            if self.config.get("sandboxing_enabled", True):
                result = self._execute_sandboxed(capability, params)
            else:
                result = capability.invoke(params)

            # Record success

            self.monitoring_engine.record_success(execution_id)

            return CapabilityResult(
                success=True,
                result=result,
                error=None,
                execution_time=self.monitoring_engine.get_execution_time(execution_id)
            )

        except Exception as e:

            # Record failure

            self.monitoring_engine.record_failure(execution_id, str(e))

            return CapabilityResult(
                success=False,
                result=None,
                error=str(e),
                execution_time=self.monitoring_engine.get_execution_time(execution_id)
            )

    def list_capabilities(self) -> List[CapabilityInfo]:
        """
        List all registered capabilities.

        Returns:
            List of capability information
        """
        return [cap.get_info() for cap in self.capabilities.values()]

    def get_capability_metrics(self, capability_id: str) -> Dict[str, Any]:
        """
        Get performance metrics for a capability.

        Args:
            capability_id: Capability identifier

        Returns:
            Dictionary of performance metrics
        """
        return self.monitoring_engine.get_metrics(capability_id)

    def _execute_sandboxed(self, capability: Capability, params: Dict[str, Any]) -> Any:
        """
        Execute capability in sandboxed environment.

        Args:
            capability: Capability to execute
            params: Parameters

        Returns:
            Execution result
        """
        sandbox = self.sandbox_manager.create_sandbox(
            max_time=self.max_execution_time,
            max_memory=self.max_memory_mb
        )

        try:
            result = sandbox.execute(capability.invoke, params)
            return result
        finally:
            self.sandbox_manager.destroy_sandbox(sandbox)

    def _validate_capability(self, capability: Capability) -> bool:
        """Validate a capability before registration."""

        # Check required attributes

        if not capability.capability_id or not capability.name:
            return False

        # Check parameters are properly defined

        try:
            params = capability._define_parameters()
            if not isinstance(params, list):
                return False
        except Exception:
            return False

        return True
```

## Sandboxing

### SandboxManager Class

```python
class SandboxManager:
    """
    Manages sandboxed execution environments for capabilities.

    Provides isolation to prevent capabilities from:

    - Exceeding resource limits
    - Accessing unauthorized resources
    - Affecting other capabilities

    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize sandbox manager.

        Args:
            config: Sandbox configuration
        """
        self.config = config
        self.active_sandboxes: Dict[str, Sandbox] = {}

    def create_sandbox(self, max_time: int, max_memory: int) -> 'Sandbox':
        """
        Create a new sandbox.

        Args:
            max_time: Maximum execution time in seconds
            max_memory: Maximum memory in MB

        Returns:
            Sandbox: New sandbox instance
        """
        sandbox_id = self._generate_sandbox_id()
        sandbox = Sandbox(
            sandbox_id=sandbox_id,
            max_time=max_time,
            max_memory=max_memory
        )
        self.active_sandboxes[sandbox_id] = sandbox
        return sandbox

    def destroy_sandbox(self, sandbox: 'Sandbox') -> None:
        """
        Destroy a sandbox and release resources.

        Args:
            sandbox: Sandbox to destroy
        """
        if sandbox.sandbox_id in self.active_sandboxes:
            sandbox.cleanup()
            del self.active_sandboxes[sandbox.sandbox_id]

class Sandbox:
    """
    Isolated execution environment for capabilities.
    """

    def __init__(self, sandbox_id: str, max_time: int, max_memory: int):
        """
        Initialize sandbox.

        Args:
            sandbox_id: Unique sandbox identifier
            max_time: Maximum execution time
            max_memory: Maximum memory usage
        """
        self.sandbox_id = sandbox_id
        self.max_time = max_time
        self.max_memory = max_memory

    def execute(self, func: Callable, params: Dict[str, Any]) -> Any:
        """
        Execute a function in the sandbox.

        Args:
            func: Function to execute
            params: Function parameters

        Returns:
            Function result

        Raises:
            TimeoutError: If execution exceeds max_time
            MemoryError: If execution exceeds max_memory
        """

        # In a real implementation:

        # - Use multiprocessing/subprocess for isolation

        # - Set resource limits (ulimit, cgroups, etc.)

        # - Monitor resource usage

        # - Enforce timeouts

        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError(f"Execution exceeded {self.max_time}s")

        # Set timeout

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.max_time)

        try:
            result = func(params)
            signal.alarm(0)  # Cancel timeout
            return result
        except TimeoutError:
            raise
        except Exception as e:
            signal.alarm(0)
            raise

    def cleanup(self) -> None:
        """Clean up sandbox resources."""
        pass
```

## Example Capabilities

### File Reader Capability

```python
class FileReaderCapability(Capability):
    """Read contents of a file."""

    def _define_parameters(self) -> List[ParameterInfo]:
        return [
            ParameterInfo(
                name="file_path",
                type="string",
                required=True,
                description="Path to file to read"
            ),
            ParameterInfo(
                name="encoding",
                type="string",
                required=False,
                description="File encoding (default: utf-8)"
            )
        ]

    def invoke(self, params: Dict[str, Any]) -> Any:
        file_path = params["file_path"]
        encoding = params.get("encoding", "utf-8")

        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
```

### HTTP Request Capability

```python
class HTTPRequestCapability(Capability):
    """Make an HTTP request."""

    def _define_parameters(self) -> List[ParameterInfo]:
        return [
            ParameterInfo(
                name="url",
                type="string",
                required=True,
                description="URL to request"
            ),
            ParameterInfo(
                name="method",
                type="string",
                required=False,
                description="HTTP method (default: GET)"
            ),
            ParameterInfo(
                name="headers",
                type="dict",
                required=False,
                description="HTTP headers"
            ),
            ParameterInfo(
                name="body",
                type="string",
                required=False,
                description="Request body"
            )
        ]

    def invoke(self, params: Dict[str, Any]) -> Any:
        import requests

        url = params["url"]
        method = params.get("method", "GET")
        headers = params.get("headers", {})
        body = params.get("body")

        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=body
        )

        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.text
        }
```

### Data Analysis Capability

```python
class DataAnalysisCapability(Capability):
    """Analyze a dataset and generate statistics."""

    def _define_parameters(self) -> List[ParameterInfo]:
        return [
            ParameterInfo(
                name="data",
                type="list",
                required=True,
                description="List of numeric values"
            ),
            ParameterInfo(
                name="statistics",
                type="list",
                required=False,
                description="Statistics to compute (mean, median, std, etc.)"
            )
        ]

    def invoke(self, params: Dict[str, Any]) -> Any:
        import statistics

        data = params["data"]
        stats_to_compute = params.get("statistics", ["mean", "median", "stdev"])

        results = {}
        if "mean" in stats_to_compute:
            results["mean"] = statistics.mean(data)
        if "median" in stats_to_compute:
            results["median"] = statistics.median(data)
        if "stdev" in stats_to_compute:
            results["stdev"] = statistics.stdev(data)
        if "min" in stats_to_compute:
            results["min"] = min(data)
        if "max" in stats_to_compute:
            results["max"] = max(data)

        return results
```

## Capability Discovery

Capabilities can be discovered through:

1. **Static Registration**: Capabilities registered at startup
1. **Dynamic Discovery**: Capabilities discovered from plugins
1. **Remote Registration**: Capabilities from external services

## Resource Management

### Resource Limits

Per-capability resource limits:

- **Execution Time**: Maximum execution time
- **Memory**: Maximum memory usage
- **CPU**: CPU time limits
- **I/O**: I/O operation limits
- **Network**: Network bandwidth limits

### Resource Monitoring

```python
class MonitoringEngine:
    """Monitor capability execution metrics."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.executions: Dict[str, ExecutionMetrics] = {}

    def start_execution(self, capability_id: str) -> str:
        """Start monitoring an execution."""
        execution_id = self._generate_execution_id()
        self.executions[execution_id] = ExecutionMetrics(
            execution_id=execution_id,
            capability_id=capability_id,
            start_time=datetime.now()
        )
        return execution_id

    def record_success(self, execution_id: str) -> None:
        """Record successful execution."""
        if execution_id in self.executions:
            self.executions[execution_id].end_time = datetime.now()
            self.executions[execution_id].success = True

    def record_failure(self, execution_id: str, error: str) -> None:
        """Record failed execution."""
        if execution_id in self.executions:
            self.executions[execution_id].end_time = datetime.now()
            self.executions[execution_id].success = False
            self.executions[execution_id].error = error

    def get_execution_time(self, execution_id: str) -> float:
        """Get execution time in seconds."""
        if execution_id in self.executions:
            metrics = self.executions[execution_id]
            if metrics.end_time:
                return (metrics.end_time - metrics.start_time).total_seconds()
        return 0.0

    def get_metrics(self, capability_id: str) -> Dict[str, Any]:
        """Get aggregated metrics for a capability."""
        capability_executions = [
            m for m in self.executions.values()
            if m.capability_id == capability_id
        ]

        if not capability_executions:
            return {}

        total = len(capability_executions)
        successes = sum(1 for m in capability_executions if m.success)
        failures = total - successes

        execution_times = [
            (m.end_time - m.start_time).total_seconds()
            for m in capability_executions
            if m.end_time
        ]

        return {
            "total_executions": total,
            "successes": successes,
            "failures": failures,
            "success_rate": successes / total if total > 0 else 0.0,
            "avg_execution_time": sum(execution_times) / len(execution_times) if execution_times else 0.0,
            "min_execution_time": min(execution_times) if execution_times else 0.0,
            "max_execution_time": max(execution_times) if execution_times else 0.0
        }
```

## Configuration

```yaml
capabilities:
  sandboxing_enabled: true
  max_execution_time: 30  # seconds
  max_memory_mb: 512
  monitoring_enabled: true

  resource_limits:
    cpu_time: 30  # seconds
    memory: 512  # MB
    disk_io: 100  # MB/s
    network_io: 10  # MB/s

  discovery:
    enable_plugins: true
    plugin_directory: "./plugins/capabilities"
    enable_remote: false
```

## See Also

- [MODULE_CONTRACTS.md](MODULE_CONTRACTS.md) - CapabilityInvoker interface
- [AGENT_MODEL.md](AGENT_MODEL.md) - Agent-capability integration
- [WORKFLOW_ENGINE.md](WORKFLOW_ENGINE.md) - Workflow-capability integration
