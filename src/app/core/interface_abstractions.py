#!/usr/bin/env python3
"""
Interface Abstractions - Subsystem Interface Layer
Project-AI God Tier Zombie Apocalypse Defense Engine

This module provides abstract base classes and interfaces for all defense engine
subsystems, enabling polymorphism, hot-swapping, and standardized interaction
patterns across all subsystems.

Features:
- Standard subsystem lifecycle interfaces
- Capability-based interface definitions
- Protocol-based communication abstractions
- Dependency injection support
- Mock/stub interfaces for testing
- Air-gapped operation support
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


class OperationalMode(Enum):
    """System operational modes"""

    NORMAL = "normal"  # Standard operation
    DEGRADED = "degraded"  # Reduced functionality
    AIR_GAPPED = "air_gapped"  # No external connectivity
    ADVERSARIAL = "adversarial"  # Under active attack
    RECOVERY = "recovery"  # Self-healing mode
    MAINTENANCE = "maintenance"  # Maintenance mode
    EMERGENCY = "emergency"  # Emergency protocols active


@dataclass
class SubsystemContext:
    """Context information for subsystem operations"""

    subsystem_id: str
    operational_mode: OperationalMode = OperationalMode.NORMAL
    air_gapped: bool = False
    adversarial_conditions: bool = False
    priority_override: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SubsystemCommand:
    """Command structure for subsystem operations"""

    command_id: str
    command_type: str
    parameters: dict[str, Any]
    timestamp: datetime
    priority: int = 5  # 0 (highest) to 10 (lowest)
    requires_ack: bool = False
    timeout_seconds: float = 30.0


@dataclass
class SubsystemResponse:
    """Response structure from subsystem operations"""

    command_id: str
    success: bool
    result: Any = None
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class ISubsystem(ABC):
    """
    Base interface for all defense engine subsystems.

    All subsystems must implement this interface to be managed by the
    bootstrap orchestrator and system registry.
    """

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the subsystem.

        Returns:
            bool: True if initialization successful
        """
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        """
        Gracefully shutdown the subsystem.

        Returns:
            bool: True if shutdown successful
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Perform health check on the subsystem.

        Returns:
            bool: True if subsystem is healthy
        """
        pass

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """
        Get current subsystem status.

        Returns:
            Dictionary containing status information
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> list[str]:
        """
        Get list of capabilities this subsystem provides.

        Returns:
            List of capability names
        """
        pass

    def recover(self) -> bool:
        """
        Attempt to recover from a failure state.

        Returns:
            bool: True if recovery successful
        """
        logger.info(f"Default recovery for {self.__class__.__name__}")
        return self.initialize()

    def set_operational_mode(self, mode: OperationalMode) -> bool:
        """
        Set operational mode for the subsystem.

        Args:
            mode: The operational mode to set

        Returns:
            bool: True if mode change successful
        """
        logger.info(
            f"Setting operational mode to {mode.value} for {self.__class__.__name__}"
        )
        return True


class ICommandable(ABC):
    """Interface for subsystems that accept commands"""

    @abstractmethod
    def execute_command(self, command: SubsystemCommand) -> SubsystemResponse:
        """
        Execute a command.

        Args:
            command: The command to execute

        Returns:
            Response from command execution
        """
        pass

    @abstractmethod
    def get_supported_commands(self) -> list[str]:
        """
        Get list of supported command types.

        Returns:
            List of supported command type names
        """
        pass


class IConfigurable(ABC):
    """Interface for subsystems with runtime configuration"""

    @abstractmethod
    def get_config(self) -> dict[str, Any]:
        """
        Get current configuration.

        Returns:
            Configuration dictionary
        """
        pass

    @abstractmethod
    def set_config(self, config: dict[str, Any]) -> bool:
        """
        Update configuration.

        Args:
            config: New configuration dictionary

        Returns:
            bool: True if configuration update successful
        """
        pass

    @abstractmethod
    def validate_config(self, config: dict[str, Any]) -> tuple[bool, str | None]:
        """
        Validate a configuration.

        Args:
            config: Configuration to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        pass


class IObservable(ABC):
    """Interface for subsystems that emit events"""

    @abstractmethod
    def subscribe(self, event_type: str, callback: callable) -> str:
        """
        Subscribe to events.

        Args:
            event_type: Type of event to subscribe to
            callback: Callback function to invoke on event

        Returns:
            Subscription ID
        """
        pass

    @abstractmethod
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.

        Args:
            subscription_id: The subscription ID to cancel

        Returns:
            bool: True if unsubscribe successful
        """
        pass

    @abstractmethod
    def emit_event(self, event_type: str, data: Any) -> int:
        """
        Emit an event to all subscribers.

        Args:
            event_type: Type of event
            data: Event data

        Returns:
            Number of subscribers notified
        """
        pass


class IMonitorable(ABC):
    """Interface for subsystems with monitoring capabilities"""

    @abstractmethod
    def get_metrics(self) -> dict[str, Any]:
        """
        Get current metrics.

        Returns:
            Dictionary of metric name -> value
        """
        pass

    @abstractmethod
    def get_metric(self, metric_name: str) -> Any:
        """
        Get a specific metric value.

        Args:
            metric_name: Name of the metric

        Returns:
            Metric value or None if not found
        """
        pass

    @abstractmethod
    def reset_metrics(self) -> bool:
        """
        Reset all metrics to initial state.

        Returns:
            bool: True if reset successful
        """
        pass


class ISecureSubsystem(ABC):
    """Interface for subsystems with security features"""

    @abstractmethod
    def authenticate(self, credentials: dict[str, Any]) -> bool:
        """
        Authenticate access to the subsystem.

        Args:
            credentials: Authentication credentials

        Returns:
            bool: True if authentication successful
        """
        pass

    @abstractmethod
    def authorize(self, action: str, context: dict[str, Any]) -> bool:
        """
        Authorize an action.

        Args:
            action: The action to authorize
            context: Context information

        Returns:
            bool: True if action authorized
        """
        pass

    @abstractmethod
    def audit_log(self, action: str, details: dict[str, Any]) -> bool:
        """
        Log an action to the audit trail.

        Args:
            action: Action description
            details: Action details

        Returns:
            bool: True if audit log successful
        """
        pass


@runtime_checkable
class ISensorFusion(Protocol):
    """Protocol for sensor fusion capabilities"""

    def ingest_sensor_data(self, sensor_id: str, data: Any) -> bool:
        """Ingest data from a sensor"""
        ...

    def get_fused_state(self) -> dict[str, Any]:
        """Get the current fused state estimate"""
        ...

    def register_sensor(
        self, sensor_id: str, sensor_type: str, metadata: dict[str, Any]
    ) -> bool:
        """Register a new sensor"""
        ...


@runtime_checkable
class IThreatDetection(Protocol):
    """Protocol for threat detection capabilities"""

    def detect_threats(self, data: Any) -> list[dict[str, Any]]:
        """Detect threats in data"""
        ...

    def classify_threat(self, threat_data: Any) -> str:
        """Classify a detected threat"""
        ...

    def get_threat_level(self) -> int:
        """Get current overall threat level (0-10)"""
        ...


@runtime_checkable
class IResourceManager(Protocol):
    """Protocol for resource management capabilities"""

    def allocate_resource(self, resource_type: str, amount: float) -> str | None:
        """Allocate a resource"""
        ...

    def release_resource(self, resource_id: str) -> bool:
        """Release an allocated resource"""
        ...

    def get_resource_availability(self, resource_type: str) -> float:
        """Get available amount of a resource"""
        ...


@runtime_checkable
class ICommunication(Protocol):
    """Protocol for communication capabilities"""

    def send_message(self, destination: str, message: Any, priority: int = 5) -> bool:
        """Send a message"""
        ...

    def receive_messages(self) -> list[Any]:
        """Receive pending messages"""
        ...

    def broadcast(self, message: Any, group: str | None = None) -> int:
        """Broadcast a message"""
        ...


class BaseSubsystem(ISubsystem):
    """
    Base implementation of ISubsystem with common functionality.

    Provides default implementations and utilities for concrete subsystems.
    """

    # Subsystem metadata (should be overridden by subclasses)
    SUBSYSTEM_METADATA = {
        "id": "base_subsystem",
        "name": "Base Subsystem",
        "version": "1.0.0",
        "priority": "MEDIUM",
        "dependencies": [],
        "provides_capabilities": [],
        "config": {},
    }

    def __init__(self, data_dir: str = "data", config: dict[str, Any] = None):
        """
        Initialize base subsystem.

        Args:
            data_dir: Directory for persistent data
            config: Configuration dictionary
        """
        self.data_dir = data_dir
        self.config = config or {}
        self.context = SubsystemContext(subsystem_id=self.SUBSYSTEM_METADATA["id"])
        self._initialized = False
        self._healthy = True
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def initialize(self) -> bool:
        """Initialize the subsystem."""
        self.logger.info(f"Initializing {self.__class__.__name__}")
        self._initialized = True
        return True

    def shutdown(self) -> bool:
        """Shutdown the subsystem."""
        self.logger.info(f"Shutting down {self.__class__.__name__}")
        self._initialized = False
        return True

    def health_check(self) -> bool:
        """Perform health check."""
        return self._initialized and self._healthy

    def get_status(self) -> dict[str, Any]:
        """Get subsystem status."""
        return {
            "initialized": self._initialized,
            "healthy": self._healthy,
            "operational_mode": self.context.operational_mode.value,
            "air_gapped": self.context.air_gapped,
            "subsystem_id": self.context.subsystem_id,
        }

    def get_capabilities(self) -> list[str]:
        """Get list of capabilities."""
        return self.SUBSYSTEM_METADATA.get("provides_capabilities", [])

    def set_operational_mode(self, mode: OperationalMode) -> bool:
        """Set operational mode."""
        self.logger.info(f"Setting operational mode to {mode.value}")
        self.context.operational_mode = mode
        self.context.air_gapped = mode == OperationalMode.AIR_GAPPED
        self.context.adversarial_conditions = mode == OperationalMode.ADVERSARIAL
        return True


class NullSubsystem(BaseSubsystem):
    """
    Null object pattern implementation for testing/mocking.

    Provides a no-op subsystem that always succeeds but does nothing.
    """

    SUBSYSTEM_METADATA = {
        "id": "null_subsystem",
        "name": "Null Subsystem",
        "version": "1.0.0",
        "priority": "LOW",
        "dependencies": [],
        "provides_capabilities": [],
        "config": {},
    }

    def initialize(self) -> bool:
        return True

    def shutdown(self) -> bool:
        return True

    def health_check(self) -> bool:
        return True

    def get_status(self) -> dict[str, Any]:
        return {"status": "null", "initialized": True, "healthy": True}

    def get_capabilities(self) -> list[str]:
        return []


# Utility functions


def validate_subsystem_interface(instance: Any) -> tuple[bool, list[str]]:
    """
    Validate that an instance implements the ISubsystem interface.

    Args:
        instance: The instance to validate

    Returns:
        Tuple of (is_valid, list_of_missing_methods)
    """
    required_methods = [
        "initialize",
        "shutdown",
        "health_check",
        "get_status",
        "get_capabilities",
    ]

    missing = []
    for method_name in required_methods:
        if not hasattr(instance, method_name) or not callable(
            getattr(instance, method_name)
        ):
            missing.append(method_name)

    return len(missing) == 0, missing


def create_subsystem_proxy(subsystem_id: str, registry) -> Any | None:
    """
    Create a proxy for accessing a subsystem through the registry.

    Args:
        subsystem_id: The subsystem to proxy
        registry: The system registry

    Returns:
        Proxy object or None if subsystem not found
    """

    class SubsystemProxy:
        def __init__(self, subsystem_id: str, registry):
            self.subsystem_id = subsystem_id
            self.registry = registry

        def __getattr__(self, name: str):
            subsystem = self.registry.get_subsystem(self.subsystem_id)
            if subsystem is None:
                raise AttributeError(
                    f"Subsystem {self.subsystem_id} not found in registry"
                )
            return getattr(subsystem, name)

    return SubsystemProxy(subsystem_id, registry)
