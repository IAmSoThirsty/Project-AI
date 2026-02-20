"""
Cathedral Infrastructure Adapter for Project-AI.

This module integrates the cathedral-level infrastructure components
(integration bus, observability, security, etc.) into the existing
Project-AI architecture without requiring major refactoring.

It acts as a glue layer that wraps existing systems with enhanced
capabilities while maintaining backward compatibility.
"""

import logging
from collections.abc import Callable
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from .config_validator import ConfigValidator
from .observability import ObservabilitySystem, get_observability_system
from .secrets_manager import SecretsManager, get_secrets_manager
from .security_validator import SecurityValidator, get_security_validator
from .unified_integration_bus import (
    CircuitBreakerConfig,
    ServicePriority,
    UnifiedIntegrationBus,
    get_integration_bus,
)

logger = logging.getLogger(__name__)


class CathedralInfrastructureAdapter:
    """
    Adapter that integrates cathedral-level infrastructure into existing systems.

    This adapter provides:
    - Transparent integration bus wrapping
    - Automatic observability injection
    - Security validation layers
    - Config validation
    - Secrets management
    """

    def __init__(
        self,
        data_dir: str | None = None,
        service_name: str = "project-ai",
        enable_all: bool = True,
    ):
        """
        Initialize cathedral infrastructure adapter.

        Args:
            data_dir: Data directory for persistence
            service_name: Service name for observability
            enable_all: Enable all features by default
        """
        self.data_dir = Path(data_dir or "data")
        self.service_name = service_name

        # Initialize core components
        self.integration_bus: UnifiedIntegrationBus = get_integration_bus()
        self.observability: ObservabilitySystem = get_observability_system(service_name)
        self.config_validator: ConfigValidator = ConfigValidator()
        self.security_validator: SecurityValidator = get_security_validator()

        # Initialize secrets manager
        secrets_path = self.data_dir / "secrets.enc"
        self.secrets_manager: SecretsManager = get_secrets_manager(storage_path=secrets_path)

        # Track wrapped components
        self._wrapped_components: dict[str, Any] = {}

        logger.info(f"CathedralInfrastructureAdapter initialized for {service_name}")

    def wrap_subsystem(
        self,
        subsystem_id: str,
        instance: Any,
        priority: str = "NORMAL",
        health_check: Callable[[], bool] | None = None,
        enable_circuit_breaker: bool = True,
        enable_tracing: bool = True,
    ) -> Any:
        """
        Wrap a subsystem with cathedral infrastructure.

        Args:
            subsystem_id: Unique subsystem identifier
            instance: Subsystem instance
            priority: Priority level (CRITICAL, HIGH, NORMAL, LOW, BACKGROUND)
            health_check: Optional health check function
            enable_circuit_breaker: Enable circuit breaker protection
            enable_tracing: Enable distributed tracing

        Returns:
            Wrapped subsystem (or original if wrapping not needed)
        """
        try:
            # Convert priority string to enum
            priority_map = {
                "CRITICAL": ServicePriority.CRITICAL,
                "HIGH": ServicePriority.HIGH,
                "NORMAL": ServicePriority.NORMAL,
                "LOW": ServicePriority.LOW,
                "BACKGROUND": ServicePriority.BACKGROUND,
            }
            service_priority = priority_map.get(priority, ServicePriority.NORMAL)

            # Register with integration bus
            self.integration_bus.register_service(
                service_id=subsystem_id,
                instance=instance,
                health_check=health_check or self._default_health_check(instance),
                priority=service_priority,
                enable_circuit_breaker=enable_circuit_breaker,
                circuit_breaker_config=(
                    CircuitBreakerConfig(failure_threshold=5, timeout=60.0) if enable_circuit_breaker else None
                ),
                metadata={
                    "wrapped_at": "cathedral_adapter",
                    "tracing_enabled": enable_tracing,
                },
            )

            # Store wrapped component
            self._wrapped_components[subsystem_id] = instance

            logger.info(
                f"Wrapped subsystem: {subsystem_id} " f"(priority={priority}, circuit_breaker={enable_circuit_breaker})"
            )

            return instance

        except Exception as e:
            logger.error(f"Failed to wrap subsystem {subsystem_id}: {e}")
            return instance

    def _default_health_check(self, instance: Any) -> Callable[[], bool] | None:
        """Create a default health check function for an instance."""
        # Try to find a health_check method
        if hasattr(instance, "health_check"):
            return instance.health_check
        elif hasattr(instance, "is_healthy"):
            return instance.is_healthy
        elif hasattr(instance, "get_status"):
            # Create a wrapper that checks if status is "healthy"
            def health_wrapper():
                status = instance.get_status()
                if isinstance(status, dict):
                    return status.get("healthy", True)
                return True

            return health_wrapper
        else:
            # No health check available
            return None

    @contextmanager
    def traced_operation(self, operation_name: str, **attributes):
        """
        Context manager for traced operations.

        Usage:
            with adapter.traced_operation("initialize_subsystem", subsystem="example"):
                # ... operation code ...
        """
        with self.observability.trace_request(operation_name, **attributes):
            yield

    def validate_config(self, config: dict[str, Any], config_type: str = "subsystem", **kwargs) -> bool:
        """
        Validate configuration.

        Args:
            config: Configuration to validate
            config_type: Type of configuration
            **kwargs: Additional validation parameters

        Returns:
            True if valid

        Raises:
            ConfigurationError if validation fails
        """
        from .config_validator import validate_config as validate_cfg

        result = validate_cfg(config, config_type=config_type, **kwargs)
        result.raise_if_invalid()
        return True

    def validate_input(self, value: Any, input_type: str = "generic", strict: bool = True) -> Any:
        """
        Validate and sanitize input.

        Args:
            value: Input value
            input_type: Type of input
            strict: Whether to use strict validation

        Returns:
            Sanitized value

        Raises:
            ValidationError or SecurityError if validation fails
        """
        result = self.security_validator.validate_input(value, input_type, strict=strict)

        if strict:
            result.raise_if_invalid()

        return result.sanitized_value if result.sanitized_value is not None else value

    def get_secret(self, key: str, default: str | None = None) -> str | None:
        """
        Get a secret value.

        Args:
            key: Secret key
            default: Default value if not found

        Returns:
            Secret value or default
        """
        return self.secrets_manager.get_secret(key, default)

    def get_service(self, service_id: str) -> Any:
        """
        Get a registered service.

        Args:
            service_id: Service identifier

        Returns:
            Service instance

        Raises:
            DependencyNotFoundError if service not found
        """
        return self.integration_bus.get_service(service_id)

    def request_service(
        self,
        service_id: str,
        request: Any,
        timeout: float = 30.0,
    ) -> Any:
        """
        Make a request to a service with resilience.

        Args:
            service_id: Service identifier
            request: Request data
            timeout: Timeout in seconds

        Returns:
            Service response
        """
        return self.integration_bus.request_service(service_id, request, timeout=timeout)

    def publish_event(self, event_type: str, data: Any, **metadata) -> None:
        """
        Publish an event.

        Args:
            event_type: Event type
            data: Event data
            **metadata: Additional metadata
        """
        self.integration_bus.publish_event(event_type, data, metadata=metadata)

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Subscribe to events.

        Args:
            event_type: Event type to subscribe to
            handler: Event handler function
        """

        # Create subscriber wrapper
        class HandlerSubscriber:
            def __init__(self, handler_func):
                self.handler = handler_func

            def handle_event(self, event):
                self.handler(event)

        subscriber = HandlerSubscriber(handler)
        self.integration_bus.subscribe(event_type, subscriber)

    def health_check_all(self) -> dict[str, bool]:
        """Run health checks on all wrapped subsystems."""
        return self.integration_bus.health_check_all()

    def get_health_report(self) -> dict[str, Any]:
        """Get comprehensive health report."""
        return self.observability.get_health_report()

    def record_metric(
        self,
        metric_name: str,
        value: float,
        metric_type: str = "gauge",
        labels: dict[str, str] | None = None,
    ) -> None:
        """
        Record a metric.

        Args:
            metric_name: Metric name
            value: Metric value
            metric_type: Type of metric (counter, gauge, histogram)
            labels: Optional labels
        """
        if metric_type == "counter":
            self.observability.metrics.inc_counter(metric_name, value, labels)
        elif metric_type == "gauge":
            self.observability.metrics.set_gauge(metric_name, value, labels)
        elif metric_type == "histogram":
            self.observability.metrics.observe_histogram(metric_name, value, labels)

    def shutdown(self) -> None:
        """Graceful shutdown of all infrastructure."""
        logger.info("Shutting down cathedral infrastructure adapter")

        # Shutdown integration bus
        self.integration_bus.shutdown()

        # Clear wrapped components
        self._wrapped_components.clear()

        logger.info("Cathedral infrastructure adapter shutdown complete")


# Global singleton instance
_cathedral_adapter: CathedralInfrastructureAdapter | None = None


def get_cathedral_adapter(
    data_dir: str | None = None, service_name: str = "project-ai"
) -> CathedralInfrastructureAdapter:
    """Get or create the global cathedral adapter instance."""
    global _cathedral_adapter

    if _cathedral_adapter is None:
        _cathedral_adapter = CathedralInfrastructureAdapter(data_dir=data_dir, service_name=service_name)

    return _cathedral_adapter


def reset_cathedral_adapter() -> None:
    """Reset the global cathedral adapter (primarily for testing)."""
    global _cathedral_adapter

    if _cathedral_adapter is not None:
        _cathedral_adapter.shutdown()
    _cathedral_adapter = None


# Convenience decorators for existing code


def with_observability(operation_name: str | None = None):
    """
    Decorator to add observability to a function.

    Usage:
        @with_observability("process_data")
        def process_data(data):
            # ... processing code ...
    """

    def decorator(func):
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            adapter = get_cathedral_adapter()
            name = operation_name or func.__name__

            with adapter.traced_operation(name):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def with_circuit_breaker(service_id: str):
    """
    Decorator to add circuit breaker protection to a function.

    Usage:
        @with_circuit_breaker("external_api")
        def call_external_api():
            # ... API call ...
    """

    def decorator(func):
        import functools

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            adapter = get_cathedral_adapter()

            # Get service descriptor
            try:
                descriptor = adapter.integration_bus._services.get(service_id)
                if descriptor and descriptor.circuit_breaker:
                    return descriptor.circuit_breaker.call(lambda: func(*args, **kwargs))
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Circuit breaker error for {service_id}: {e}")
                return func(*args, **kwargs)

        return wrapper

    return decorator


def with_input_validation(input_type: str = "generic", strict: bool = True):
    """
    Decorator to add input validation to a function.

    Usage:
        @with_input_validation("sql", strict=True)
        def execute_query(query):
            # ... execute query ...
    """

    def decorator(func):
        import functools

        @functools.wraps(func)
        def wrapper(input_value, *args, **kwargs):
            adapter = get_cathedral_adapter()

            # Validate first argument
            validated_value = adapter.validate_input(input_value, input_type, strict)

            return func(validated_value, *args, **kwargs)

        return wrapper

    return decorator
