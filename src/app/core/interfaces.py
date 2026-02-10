"""
Interface abstractions for pluggable governance and memory engines.

This module provides abstract base classes (interfaces) that allow users to
implement custom governance and memory engines without modifying the core kernel.

Key Interfaces:
- GovernanceEngineInterface: For custom governance implementations
- MemoryEngineInterface: For custom memory storage implementations
- PluginInterface: For general plugin development

Benefits:
- Dependency inversion: Core kernel depends on abstractions, not concrete implementations
- Extensibility: Users can plug in custom engines without rewriting the kernel
- Testability: Easy to mock and test with different implementations
- Flexibility: Mix and match different governance and memory strategies
"""

from abc import ABC, abstractmethod
from typing import Any


class GovernanceEngineInterface(ABC):
    """
    Abstract interface for governance engines.

    Implement this interface to create custom governance strategies that can be
    plugged into the CognitionKernel without modifying core code.

    Example:
        >>> class MyGovernance(GovernanceEngineInterface):
        ...     def evaluate_action(self, action, context):
        ...         # Custom governance logic
        ...         return Decision(approved=True, reason="Custom logic")
        ...
        >>> kernel = CognitionKernel(governance_engine=MyGovernance())
    """

    @abstractmethod
    def evaluate_action(
        self,
        action: Any,
        context: Any,
    ) -> Any:
        """
        Evaluate whether an action should be allowed.

        This is the primary governance entrypoint. The kernel will call this
        method before executing any action.

        Args:
            action: The proposed action (contains action_name, type, risk_level, etc.)
            context: Execution context (contains trace_id, timestamp, metadata, etc.)

        Returns:
            Decision object with approved (bool), reason (str), and optional metadata

        Example:
            >>> decision = engine.evaluate_action(action, context)
            >>> if decision.approved:
            ...     # Execute action
            ... else:
            ...     # Block action
        """
        pass

    @abstractmethod
    def get_statistics(self) -> dict[str, Any]:
        """
        Get governance engine statistics.

        Returns:
            Dictionary with metrics like total_evaluations, approvals, blocks, etc.
        """
        pass

    def initialize(self) -> None:
        """
        Initialize the governance engine (optional hook).

        Override this method if your engine needs initialization logic.
        """
        pass

    def shutdown(self) -> None:
        """
        Shutdown the governance engine (optional hook).

        Override this method if your engine needs cleanup logic.
        """
        pass


class MemoryEngineInterface(ABC):
    """
    Abstract interface for memory engines.

    Implement this interface to create custom memory storage strategies that can be
    plugged into the CognitionKernel without modifying core code.

    Example:
        >>> class MyMemory(MemoryEngineInterface):
        ...     def record_execution(self, trace_id, channels, status):
        ...         # Custom memory logic
        ...         return "mem_123"
        ...
        >>> kernel = CognitionKernel(memory_engine=MyMemory())
    """

    @abstractmethod
    def record_execution(
        self,
        trace_id: str,
        channels: dict[str, Any],
        status: str,
    ) -> str:
        """
        Record an execution in memory.

        This is called after every execution (success or failure) to store
        the execution in memory for later retrieval.

        Args:
            trace_id: Unique execution trace identifier
            channels: Five-channel memory data (attempt, decision, result, reflection, error)
            status: Execution status (completed, failed, blocked)

        Returns:
            Memory record ID

        Example:
            >>> memory_id = engine.record_execution(
            ...     trace_id="trace_123",
            ...     channels={"attempt": {...}, "result": {...}},
            ...     status="completed"
            ... )
        """
        pass

    @abstractmethod
    def query_executions(
        self,
        filters: dict[str, Any] | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Query execution history.

        Args:
            filters: Optional filter conditions (e.g., {"status": "completed"})
            limit: Maximum number of records to return

        Returns:
            List of execution records

        Example:
            >>> executions = engine.query_executions(
            ...     filters={"status": "completed"},
            ...     limit=10
            ... )
        """
        pass

    @abstractmethod
    def get_statistics(self) -> dict[str, Any]:
        """
        Get memory engine statistics.

        Returns:
            Dictionary with metrics like total_records, storage_size, etc.
        """
        pass

    def initialize(self) -> None:
        """
        Initialize the memory engine (optional hook).

        Override this method if your engine needs initialization logic.
        """
        pass

    def shutdown(self) -> None:
        """
        Shutdown the memory engine (optional hook).

        Override this method if your engine needs cleanup logic.
        """
        pass

    def add_memory(
        self,
        content: str,
        category: str = "general",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Add a memory (legacy API, optional).

        Some older code may call this method instead of record_execution.
        Provide a default implementation that delegates to record_execution.

        Args:
            content: Memory content
            category: Memory category
            metadata: Optional metadata

        Returns:
            Memory record ID
        """
        # Default implementation - can be overridden
        trace_id = metadata.get("trace_id", "unknown") if metadata else "unknown"
        channels = metadata.get("channels", {}) if metadata else {}
        status = metadata.get("status", "completed") if metadata else "completed"

        return self.record_execution(trace_id, channels, status)


class PluginInterface(ABC):
    """
    Abstract interface for general plugins.

    Implement this interface to create plugins that can be loaded and executed
    by the plugin manager.

    Example:
        >>> class MyPlugin(PluginInterface):
        ...     def get_name(self):
        ...         return "my_plugin"
        ...
        ...     def execute(self, context):
        ...         return {"result": "success"}
        ...
        >>> plugin_manager.register(MyPlugin())
    """

    @abstractmethod
    def get_name(self) -> str:
        """
        Get the plugin name.

        Returns:
            Unique plugin identifier
        """
        pass

    @abstractmethod
    def get_version(self) -> str:
        """
        Get the plugin version.

        Returns:
            Version string (e.g., "1.0.0")
        """
        pass

    @abstractmethod
    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the plugin.

        Args:
            context: Execution context with input data

        Returns:
            Dictionary with execution results
        """
        pass

    def get_metadata(self) -> dict[str, Any]:
        """
        Get plugin metadata (optional).

        Returns:
            Dictionary with plugin description, author, etc.
        """
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "description": "No description provided",
        }

    def validate_context(self, context: dict[str, Any]) -> bool:
        """
        Validate execution context (optional).

        Override this method to perform context validation before execution.

        Args:
            context: Execution context

        Returns:
            True if context is valid, False otherwise
        """
        return True


class PluginRegistry:
    """
    Registry for managing plugins.

    Provides plugin registration, discovery, and execution management.
    """

    def __init__(self):
        """Initialize plugin registry."""
        self.plugins: dict[str, PluginInterface] = {}

    def register(self, plugin: PluginInterface) -> None:
        """
        Register a plugin.

        Args:
            plugin: Plugin instance to register

        Raises:
            ValueError: If plugin with same name already registered
        """
        name = plugin.get_name()
        if name in self.plugins:
            raise ValueError(f"Plugin '{name}' already registered")

        self.plugins[name] = plugin

    def unregister(self, name: str) -> None:
        """
        Unregister a plugin.

        Args:
            name: Plugin name to unregister
        """
        if name in self.plugins:
            del self.plugins[name]

    def get_plugin(self, name: str) -> PluginInterface | None:
        """
        Get a plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(name)

    def list_plugins(self) -> list[str]:
        """
        List all registered plugins.

        Returns:
            List of plugin names
        """
        return list(self.plugins.keys())

    def execute_plugin(
        self,
        name: str,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute a plugin.

        Args:
            name: Plugin name
            context: Execution context

        Returns:
            Plugin execution results

        Raises:
            ValueError: If plugin not found
            RuntimeError: If plugin execution fails
        """
        plugin = self.get_plugin(name)
        if not plugin:
            raise ValueError(f"Plugin '{name}' not found")

        if not plugin.validate_context(context):
            raise RuntimeError(f"Invalid context for plugin '{name}'")

        return plugin.execute(context)


__all__ = [
    "GovernanceEngineInterface",
    "MemoryEngineInterface",
    "PluginInterface",
    "PluginRegistry",
]
