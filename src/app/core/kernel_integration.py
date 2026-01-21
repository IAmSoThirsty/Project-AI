"""
Kernel Integration Utilities - Wrappers for routing through CognitionKernel.

These utilities make it easy to route agent, tool, and system executions through
the CognitionKernel. All agents inherit from KernelRoutedAgent base class.

Updated for new ExecutionContext API:
- kernel.process(user_input, source="user", metadata={...})
- kernel.route(task, source="agent", metadata={...})
"""

import functools
import logging
from collections.abc import Callable
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType

logger = logging.getLogger(__name__)

# Global kernel instance (set by main.py during initialization)
_global_kernel: CognitionKernel | None = None


def set_global_kernel(kernel: CognitionKernel) -> None:
    """
    Set the global CognitionKernel instance.

    Should be called once during application initialization in main.py.

    Args:
        kernel: The CognitionKernel instance to use globally
    """
    global _global_kernel
    _global_kernel = kernel
    logger.info("Global CognitionKernel instance configured")


def get_global_kernel() -> CognitionKernel | None:
    """
    Get the global CognitionKernel instance.

    Returns:
        The global kernel instance, or None if not configured
    """
    return _global_kernel


def route_through_kernel(
    execution_type: ExecutionType,
    action_name: str | None = None,
    requires_approval: bool = False,
    risk_level: str = "low",
    user_id: str | None = None,
) -> Callable:
    """
    Decorator to route a method through the CognitionKernel.

    Usage:
        @route_through_kernel(
            execution_type=ExecutionType.AGENT_ACTION,
            action_name="ExpertAgent.execute",
            requires_approval=True,
            risk_level="medium"
        )
        def execute(self, *args, **kwargs):
            # Original implementation
            return result

    The decorated method will automatically route through kernel.process()
    if a global kernel is configured. If no kernel is available, it falls
    back to direct execution with a warning.

    Args:
        execution_type: Type of execution (AGENT_ACTION, TOOL_INVOCATION, etc.)
        action_name: Human-readable name (auto-generated if None)
        requires_approval: Whether governance approval is required
        risk_level: Risk level (low, medium, high, critical)
        user_id: User ID for governance tracking

    Returns:
        Decorated function that routes through kernel
    """

    def decorator(func: Callable) -> Callable:
        # Auto-generate action name if not provided
        actual_action_name = action_name or f"{func.__qualname__}"

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            kernel = get_global_kernel()

            # If no kernel available, fall back to direct execution
            if kernel is None:
                logger.warning(
                    f"No CognitionKernel configured for {actual_action_name}, "
                    "executing directly (BYPASS)"
                )
                return func(*args, **kwargs)

            # Route through kernel
            result = kernel.process(
                action=func,
                action_name=actual_action_name,
                execution_type=execution_type,
                action_args=args,
                action_kwargs=kwargs,
                user_id=user_id,
                requires_approval=requires_approval,
                risk_level=risk_level,
                metadata={
                    "function": func.__name__,
                    "module": func.__module__,
                },
            )

            # Return the actual result (unwrap from ExecutionResult)
            if result.success:
                return result.result
            else:
                # If execution failed, raise an exception
                error_msg = result.error or "Execution failed"
                if result.blocked_reason:
                    raise PermissionError(
                        f"Blocked by governance: {result.blocked_reason}"
                    )
                raise RuntimeError(error_msg)

        # Mark function as kernel-routed for introspection
        wrapper._kernel_routed = True
        wrapper._execution_type = execution_type
        wrapper._action_name = actual_action_name

        return wrapper

    return decorator


class KernelRoutedAgent:
    """
    Base class for agents that route all actions through CognitionKernel.

    Updated for new ExecutionContext API. Agents create Action objects that
    are routed through kernel.process() or kernel.route().

    Usage:
        class MyAgent(KernelRoutedAgent):
            def __init__(self, kernel: CognitionKernel = None):
                super().__init__(kernel, execution_type=ExecutionType.AGENT_ACTION)

            def execute(self, task):
                # This will automatically route through kernel
                return self._execute_through_kernel(
                    self._do_execute,
                    action_name="MyAgent.execute",
                    action_args=(task,)
                )

            def _do_execute(self, task):
                # Actual implementation
                return f"Executed: {task}"
    """

    def __init__(
        self,
        kernel: CognitionKernel | None = None,
        execution_type: ExecutionType = ExecutionType.AGENT_ACTION,
        default_risk_level: str = "low",
    ):
        """
        Initialize a kernel-routed agent.

        Args:
            kernel: CognitionKernel instance (uses global if None)
            execution_type: Default execution type for this agent
            default_risk_level: Default risk level for actions
        """
        self.kernel = kernel or get_global_kernel()
        self.execution_type = execution_type
        self.default_risk_level = default_risk_level

        if self.kernel is None:
            logger.warning(
                f"{self.__class__.__name__} initialized without CognitionKernel. "
                "Actions will bypass kernel governance (NOT RECOMMENDED)."
            )

    def _execute_through_kernel(
        self,
        action: Callable,
        action_name: str,
        action_args: tuple = (),
        action_kwargs: dict[str, Any] | None = None,
        requires_approval: bool = False,
        risk_level: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        mutation_targets: list | None = None,
    ) -> Any:
        """
        Execute an action through the CognitionKernel using new API.

        Creates an Action object and routes it through kernel.route().
        Automatically unwraps ExecutionResult.

        Args:
            action: The callable to execute
            action_name: Human-readable action name
            action_args: Positional arguments
            action_kwargs: Keyword arguments
            requires_approval: Whether approval is required
            risk_level: Risk level (uses default if None)
            user_id: User ID for tracking
            metadata: Additional metadata
            mutation_targets: List of mutation targets for governance

        Returns:
            The result of the action (unwrapped from ExecutionResult)

        Raises:
            PermissionError: If blocked by governance
            RuntimeError: If execution fails
        """
        action_kwargs = action_kwargs or {}
        metadata = metadata or {}
        mutation_targets = mutation_targets or []

        # If no kernel, fall back to direct execution
        if self.kernel is None:
            logger.warning(f"Bypassing kernel for {action_name} (no kernel available)")
            return action(*action_args, **action_kwargs)

        # Enrich metadata with execution details
        full_metadata = {
            **metadata,
            "agent_class": self.__class__.__name__,
            "action_name": action_name,
            "execution_type": self.execution_type.value,
            "requires_approval": requires_approval,
            "risk_level": risk_level or self.default_risk_level,
            "mutation_targets": mutation_targets,
            "user_id": user_id,
            # Create Action-like structure for kernel
            "_action_callable": action,
            "_action_args": action_args,
            "_action_kwargs": action_kwargs,
        }

        # Route through kernel using new API
        # kernel.route() expects a task (which can be the action itself or metadata)
        result = self.kernel.route(
            task=full_metadata,  # Pass full metadata as task
            source=self.__class__.__name__,
            metadata=full_metadata,
        )

        # Unwrap and return result
        if result.success:
            return result.result
        else:
            if result.blocked_reason:
                raise PermissionError(f"Blocked by governance: {result.blocked_reason}")
            raise RuntimeError(result.error or "Execution failed")


class KernelRoutedTool:
    """
    Base class for tools that route all invocations through CognitionKernel.

    Similar to KernelRoutedAgent but for tools/utilities.
    """

    def __init__(
        self,
        kernel: CognitionKernel | None = None,
        default_risk_level: str = "low",
    ):
        """
        Initialize a kernel-routed tool.

        Args:
            kernel: CognitionKernel instance (uses global if None)
            default_risk_level: Default risk level for tool invocations
        """
        self.kernel = kernel or get_global_kernel()
        self.default_risk_level = default_risk_level

        if self.kernel is None:
            logger.warning(
                f"{self.__class__.__name__} initialized without CognitionKernel. "
                "Invocations will bypass kernel governance."
            )

    def _invoke_through_kernel(
        self,
        action: Callable,
        action_name: str,
        action_args: tuple = (),
        action_kwargs: dict | None = None,
        requires_approval: bool = False,
        risk_level: str | None = None,
        metadata: dict | None = None,
    ) -> Any:
        """
        Invoke a tool action through the CognitionKernel.

        Similar to _execute_through_kernel but for tools.
        """
        action_kwargs = action_kwargs or {}
        metadata = metadata or {}

        # If no kernel, fall back to direct invocation
        if self.kernel is None:
            logger.warning(f"Bypassing kernel for {action_name} (no kernel available)")
            return action(*action_args, **action_kwargs)

        # Route through kernel
        result = self.kernel.process(
            action=action,
            action_name=action_name,
            execution_type=ExecutionType.TOOL_INVOCATION,
            action_args=action_args,
            action_kwargs=action_kwargs,
            requires_approval=requires_approval,
            risk_level=risk_level or self.default_risk_level,
            metadata=metadata,
        )

        # Unwrap and return result
        if result.success:
            return result.result
        else:
            if result.blocked_reason:
                raise PermissionError(f"Blocked by governance: {result.blocked_reason}")
            raise RuntimeError(result.error or "Invocation failed")


def kernel_safe_wrapper(
    func: Callable, kernel: CognitionKernel | None = None
) -> Callable:
    """
    Create a wrapper function that routes through kernel without modifying original.

    This is useful for wrapping existing functions/methods without changing their
    source code. Creates a new callable that routes through kernel.

    Usage:
        # Wrap an existing function
        original_func = some_agent.execute
        routed_func = kernel_safe_wrapper(original_func, kernel)

        # Replace the method
        some_agent.execute = routed_func

    Args:
        func: The function to wrap
        kernel: CognitionKernel instance (uses global if None)

    Returns:
        Wrapped function that routes through kernel
    """
    kernel = kernel or get_global_kernel()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if kernel is None:
            logger.warning(
                f"No kernel available for {func.__qualname__}, executing directly"
            )
            return func(*args, **kwargs)

        result = kernel.process(
            action=func,
            action_name=func.__qualname__,
            execution_type=ExecutionType.AGENT_ACTION,
            action_args=args,
            action_kwargs=kwargs,
            metadata={"wrapped": True, "original_function": func.__name__},
        )

        if result.success:
            return result.result
        else:
            if result.blocked_reason:
                raise PermissionError(f"Blocked: {result.blocked_reason}")
            raise RuntimeError(result.error or "Execution failed")

    wrapper._kernel_wrapped = True
    return wrapper


# Convenience function for dynamic kernel injection
def inject_kernel_into_object(
    obj: Any, kernel: CognitionKernel, method_names: list[str]
) -> None:
    """
    Inject kernel routing into specific methods of an object instance.

    This is useful for dynamically adding kernel routing to existing agent
    instances without modifying their class definitions.

    Usage:
        agent = ExpertAgent()
        inject_kernel_into_object(
            agent,
            kernel,
            method_names=["execute", "solve", "act"]
        )

        # Now agent.execute() will route through kernel

    Args:
        obj: The object instance to modify
        kernel: CognitionKernel instance
        method_names: List of method names to wrap
    """
    for method_name in method_names:
        if not hasattr(obj, method_name):
            logger.warning(f"Object {obj} does not have method {method_name}")
            continue

        original_method = getattr(obj, method_name)
        if callable(original_method):
            wrapped_method = kernel_safe_wrapper(original_method, kernel)
            setattr(obj, method_name, wrapped_method)
            logger.info(
                f"Injected kernel routing into {obj.__class__.__name__}.{method_name}"
            )
        else:
            logger.warning(f"{obj.__class__.__name__}.{method_name} is not callable")
