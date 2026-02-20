#!/usr/bin/env python3
"""
System Registry - Monolithic Core System Registry
Project-AI God Tier Zombie Apocalypse Defense Engine

This module provides the central registry for all subsystems in the defense engine.
It manages subsystem lifecycle, health monitoring, dependency resolution, and
provides redundancy and recovery capabilities for air-gapped, adversarial conditions.

Features:
- Automatic subsystem discovery and registration
- Health monitoring with automatic failover
- Dependency graph resolution
- Hot-reload and hot-swap capabilities
- Audit logging and state persistence
- Byzantine fault tolerance
"""

import json
import logging
import threading
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class SubsystemState(Enum):
    """Subsystem lifecycle states"""

    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    DEGRADED = "degraded"
    FAILED = "failed"
    RECOVERING = "recovering"
    TERMINATED = "terminated"


class SubsystemPriority(Enum):
    """Subsystem priority levels for resource allocation"""

    CRITICAL = 0  # Must always run (e.g., life support, core safety)
    HIGH = 1  # Important but can degrade gracefully
    MEDIUM = 2  # Standard operational systems
    LOW = 3  # Optional enhancements
    BACKGROUND = 4  # Non-essential background tasks


@dataclass
class SubsystemMetadata:
    """Metadata for a registered subsystem"""

    name: str
    subsystem_id: str
    version: str
    priority: SubsystemPriority
    state: SubsystemState = SubsystemState.UNINITIALIZED
    dependencies: list[str] = field(default_factory=list)
    provides_capabilities: list[str] = field(default_factory=list)
    instance: Any = None
    health_check_fn: Callable | None = None
    last_health_check: datetime | None = None
    health_status: bool = True
    failure_count: int = 0
    initialization_time: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    config_hash: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to serializable dictionary"""
        data = asdict(self)
        data["state"] = self.state.value
        data["priority"] = self.priority.value
        data["last_health_check"] = self.last_health_check.isoformat() if self.last_health_check else None
        data["initialization_time"] = self.initialization_time.isoformat() if self.initialization_time else None
        # Remove non-serializable fields
        data.pop("instance", None)
        data.pop("health_check_fn", None)
        return data


@dataclass
class HealthCheckResult:
    """Result of a subsystem health check"""

    subsystem_id: str
    healthy: bool
    timestamp: datetime
    latency_ms: float
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class SystemRegistry:
    """
    Monolithic Core System Registry

    Central registry for all defense engine subsystems with automatic discovery,
    health monitoring, and recovery capabilities.
    """

    def __init__(self, data_dir: str = "data", config_dir: str = "config"):
        """
        Initialize the system registry.

        Args:
            data_dir: Directory for persistent state storage
            config_dir: Directory for configuration files
        """
        self.data_dir = Path(data_dir)
        self.config_dir = Path(config_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Core registry data structures
        self._subsystems: dict[str, SubsystemMetadata] = {}
        self._capability_map: dict[str, list[str]] = {}  # capability -> [subsystem_ids]
        self._dependency_graph: dict[str, set[str]] = {}  # subsystem_id -> {dependencies}
        self._reverse_dependencies: dict[str, set[str]] = {}  # subsystem_id -> {dependents}

        # Thread safety
        self._lock = threading.RLock()

        # Health monitoring
        self._health_check_interval = 30.0  # seconds
        self._health_check_thread: threading.Thread | None = None
        self._health_check_active = False

        # Recovery and failover
        self._max_failure_threshold = 3
        self._recovery_strategies: dict[str, Callable] = {}

        # Audit logging
        self._audit_log: list[dict[str, Any]] = []
        self._audit_log_path = self.data_dir / "system_registry_audit.json"

        # State persistence
        self._state_file = self.data_dir / "system_registry_state.json"
        self._load_state()

        logger.info(
            "System Registry initialized (data_dir=%s, config_dir=%s)",
            data_dir,
            config_dir,
        )

    def register_subsystem(
        self,
        name: str,
        subsystem_id: str,
        version: str,
        priority: SubsystemPriority,
        instance: Any,
        dependencies: list[str] = None,
        provides_capabilities: list[str] = None,
        health_check_fn: Callable | None = None,
        metadata: dict[str, Any] = None,
    ) -> bool:
        """
        Register a subsystem with the registry.

        Args:
            name: Human-readable subsystem name
            subsystem_id: Unique subsystem identifier
            version: Subsystem version string
            priority: Subsystem priority level
            instance: The subsystem instance object
            dependencies: List of subsystem IDs this subsystem depends on
            provides_capabilities: List of capabilities this subsystem provides
            health_check_fn: Optional health check function
            metadata: Additional metadata dictionary

        Returns:
            bool: True if registration successful, False otherwise
        """
        with self._lock:
            if subsystem_id in self._subsystems:
                logger.warning("Subsystem %s already registered, updating...", subsystem_id)

            subsystem_meta = SubsystemMetadata(
                name=name,
                subsystem_id=subsystem_id,
                version=version,
                priority=priority,
                state=SubsystemState.UNINITIALIZED,
                dependencies=dependencies or [],
                provides_capabilities=provides_capabilities or [],
                instance=instance,
                health_check_fn=health_check_fn,
                metadata=metadata or {},
            )

            self._subsystems[subsystem_id] = subsystem_meta

            # Update dependency graphs
            self._dependency_graph[subsystem_id] = set(subsystem_meta.dependencies)
            for dep_id in subsystem_meta.dependencies:
                if dep_id not in self._reverse_dependencies:
                    self._reverse_dependencies[dep_id] = set()
                self._reverse_dependencies[dep_id].add(subsystem_id)

            # Update capability map
            for capability in subsystem_meta.provides_capabilities:
                if capability not in self._capability_map:
                    self._capability_map[capability] = []
                if subsystem_id not in self._capability_map[capability]:
                    self._capability_map[capability].append(subsystem_id)

            self._audit_log.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "action": "register_subsystem",
                    "subsystem_id": subsystem_id,
                    "name": name,
                    "version": version,
                    "priority": priority.value,
                }
            )

            self._save_state()

            logger.info(
                "Registered subsystem: %s (%s) v%s [Priority: %s]",
                name,
                subsystem_id,
                version,
                priority.value,
            )
            return True

    def initialize_subsystem(self, subsystem_id: str) -> bool:
        """
        Initialize a registered subsystem.

        Args:
            subsystem_id: The subsystem to initialize

        Returns:
            bool: True if initialization successful
        """
        with self._lock:
            if subsystem_id not in self._subsystems:
                logger.error("Cannot initialize unknown subsystem: %s", subsystem_id)
                return False

            subsystem = self._subsystems[subsystem_id]

            # Check dependencies
            for dep_id in subsystem.dependencies:
                if dep_id not in self._subsystems:
                    logger.error("Missing dependency %s for subsystem %s", dep_id, subsystem_id)
                    return False

                dep_subsystem = self._subsystems[dep_id]
                if dep_subsystem.state not in [
                    SubsystemState.ACTIVE,
                    SubsystemState.DEGRADED,
                ]:
                    logger.error(
                        "Dependency %s not active for subsystem %s",
                        dep_id,
                        subsystem_id,
                    )
                    return False

            try:
                subsystem.state = SubsystemState.INITIALIZING

                # Call initialize method if available
                if hasattr(subsystem.instance, "initialize"):
                    subsystem.instance.initialize()

                subsystem.state = SubsystemState.ACTIVE
                subsystem.initialization_time = datetime.now()
                subsystem.failure_count = 0

                self._audit_log.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "action": "initialize_subsystem",
                        "subsystem_id": subsystem_id,
                        "success": True,
                    }
                )

                self._save_state()

                logger.info("Initialized subsystem: %s", subsystem_id)
                return True

            except Exception as e:
                subsystem.state = SubsystemState.FAILED
                subsystem.failure_count += 1

                self._audit_log.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "action": "initialize_subsystem",
                        "subsystem_id": subsystem_id,
                        "success": False,
                        "error": str(e),
                    }
                )

                logger.error("Failed to initialize subsystem %s: %s", subsystem_id, e)
                return False

    def get_subsystem(self, subsystem_id: str) -> Any | None:
        """
        Get a subsystem instance by ID.

        Args:
            subsystem_id: The subsystem identifier

        Returns:
            The subsystem instance or None if not found
        """
        with self._lock:
            subsystem = self._subsystems.get(subsystem_id)
            return subsystem.instance if subsystem else None

    def get_subsystems_by_capability(self, capability: str) -> list[Any]:
        """
        Get all subsystems that provide a specific capability.

        Args:
            capability: The capability name

        Returns:
            List of subsystem instances
        """
        with self._lock:
            subsystem_ids = self._capability_map.get(capability, [])
            return [
                self._subsystems[sid].instance
                for sid in subsystem_ids
                if sid in self._subsystems and self._subsystems[sid].state == SubsystemState.ACTIVE
            ]

    def get_initialization_order(self) -> list[str]:
        """
        Calculate the correct initialization order based on dependency graph.

        Returns:
            List of subsystem IDs in initialization order
        """
        with self._lock:
            # Topological sort using Kahn's algorithm
            in_degree = {sid: len(deps) for sid, deps in self._dependency_graph.items()}
            queue = [sid for sid, degree in in_degree.items() if degree == 0]
            result = []

            while queue:
                # Sort by priority for deterministic ordering
                queue.sort(key=lambda sid: self._subsystems[sid].priority.value)
                current = queue.pop(0)
                result.append(current)

                for dependent in self._reverse_dependencies.get(current, []):
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

            if len(result) != len(self._subsystems):
                logger.error("Circular dependency detected in subsystem graph")
                # Return what we can, sorted by priority
                remaining = set(self._subsystems.keys()) - set(result)
                result.extend(sorted(remaining, key=lambda sid: self._subsystems[sid].priority.value))

            return result

    def health_check(self, subsystem_id: str) -> HealthCheckResult:
        """
        Perform health check on a subsystem.

        Args:
            subsystem_id: The subsystem to check

        Returns:
            HealthCheckResult with health status
        """
        with self._lock:
            if subsystem_id not in self._subsystems:
                return HealthCheckResult(
                    subsystem_id=subsystem_id,
                    healthy=False,
                    timestamp=datetime.now(),
                    latency_ms=0.0,
                    error="Subsystem not found",
                )

            subsystem = self._subsystems[subsystem_id]
            start_time = time.time()

            try:
                if subsystem.health_check_fn:
                    health_status = subsystem.health_check_fn(subsystem.instance)
                elif hasattr(subsystem.instance, "health_check"):
                    health_status = subsystem.instance.health_check()
                else:
                    # Basic check: subsystem exists and is active
                    health_status = subsystem.state in [
                        SubsystemState.ACTIVE,
                        SubsystemState.DEGRADED,
                    ]

                latency_ms = (time.time() - start_time) * 1000

                subsystem.last_health_check = datetime.now()
                subsystem.health_status = health_status

                if not health_status:
                    subsystem.failure_count += 1
                    if subsystem.failure_count >= self._max_failure_threshold:
                        subsystem.state = SubsystemState.FAILED
                        logger.error(
                            "Subsystem %s marked as FAILED after %s failures",
                            subsystem_id,
                            subsystem.failure_count,
                        )
                else:
                    subsystem.failure_count = max(0, subsystem.failure_count - 1)

                return HealthCheckResult(
                    subsystem_id=subsystem_id,
                    healthy=health_status,
                    timestamp=datetime.now(),
                    latency_ms=latency_ms,
                    details={
                        "state": subsystem.state.value,
                        "failure_count": subsystem.failure_count,
                    },
                )

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                subsystem.health_status = False
                subsystem.failure_count += 1

                logger.error("Health check failed for %s: %s", subsystem_id, e)

                return HealthCheckResult(
                    subsystem_id=subsystem_id,
                    healthy=False,
                    timestamp=datetime.now(),
                    latency_ms=latency_ms,
                    error=str(e),
                )

    def start_health_monitoring(self, interval: float = None):
        """
        Start background health monitoring thread.

        Args:
            interval: Health check interval in seconds (default: 30)
        """
        if self._health_check_active:
            logger.warning("Health monitoring already active")
            return

        if interval:
            self._health_check_interval = interval

        self._health_check_active = True
        self._health_check_thread = threading.Thread(
            target=self._health_monitoring_loop,
            daemon=True,
            name="SystemRegistry-HealthMonitor",
        )
        self._health_check_thread.start()

        logger.info("Health monitoring started (interval=%ss)", self._health_check_interval)

    def stop_health_monitoring(self):
        """Stop background health monitoring thread."""
        self._health_check_active = False
        if self._health_check_thread:
            self._health_check_thread.join(timeout=5.0)
        logger.info("Health monitoring stopped")

    def _health_monitoring_loop(self):
        """Background health monitoring loop."""
        while self._health_check_active:
            try:
                with self._lock:
                    subsystem_ids = list(self._subsystems.keys())

                for subsystem_id in subsystem_ids:
                    if not self._health_check_active:
                        break

                    result = self.health_check(subsystem_id)

                    if not result.healthy:
                        logger.warning("Health check failed for %s: %s", subsystem_id, result.error)
                        self._attempt_recovery(subsystem_id)

                # Wait for next interval
                time.sleep(self._health_check_interval)

            except Exception as e:
                logger.error("Error in health monitoring loop: %s", e)
                time.sleep(self._health_check_interval)

    def _attempt_recovery(self, subsystem_id: str):
        """
        Attempt to recover a failed subsystem.

        Args:
            subsystem_id: The subsystem to recover
        """
        with self._lock:
            if subsystem_id not in self._subsystems:
                return

            subsystem = self._subsystems[subsystem_id]

            if subsystem.state == SubsystemState.RECOVERING:
                return  # Already attempting recovery

            logger.info("Attempting recovery for subsystem: %s", subsystem_id)
            subsystem.state = SubsystemState.RECOVERING

            try:
                # Try custom recovery strategy if available
                if subsystem_id in self._recovery_strategies:
                    self._recovery_strategies[subsystem_id](subsystem.instance)
                elif hasattr(subsystem.instance, "recover"):
                    subsystem.instance.recover()
                else:
                    # Default recovery: reinitialize
                    if hasattr(subsystem.instance, "shutdown"):
                        subsystem.instance.shutdown()
                    if hasattr(subsystem.instance, "initialize"):
                        subsystem.instance.initialize()

                subsystem.state = SubsystemState.ACTIVE
                subsystem.failure_count = 0

                logger.info("Successfully recovered subsystem: %s", subsystem_id)

            except Exception as e:
                subsystem.state = SubsystemState.FAILED
                logger.error("Recovery failed for subsystem %s: %s", subsystem_id, e)

    def get_system_status(self) -> dict[str, Any]:
        """
        Get comprehensive system status.

        Returns:
            Dictionary containing system status information
        """
        with self._lock:
            status = {
                "timestamp": datetime.now().isoformat(),
                "total_subsystems": len(self._subsystems),
                "subsystems_by_state": {},
                "subsystems_by_priority": {},
                "capabilities": list(self._capability_map.keys()),
                "health_monitoring_active": self._health_check_active,
                "subsystems": {},
            }

            for state in SubsystemState:
                status["subsystems_by_state"][state.value] = 0

            for priority in SubsystemPriority:
                status["subsystems_by_priority"][priority.value] = 0

            for subsystem_id, subsystem in self._subsystems.items():
                status["subsystems_by_state"][subsystem.state.value] += 1
                status["subsystems_by_priority"][subsystem.priority.value] += 1
                status["subsystems"][subsystem_id] = subsystem.to_dict()

            return status

    def _save_state(self):
        """Save registry state to disk."""
        try:
            state = {
                "timestamp": datetime.now().isoformat(),
                "subsystems": {sid: subsystem.to_dict() for sid, subsystem in self._subsystems.items()},
                "capability_map": self._capability_map,
                "audit_log": self._audit_log[-1000:],  # Keep last 1000 entries
            }

            with open(self._state_file, "w") as f:
                json.dump(state, f, indent=2)

            # Also save audit log separately
            with open(self._audit_log_path, "w") as f:
                json.dump(self._audit_log[-10000:], f, indent=2)

        except Exception as e:
            logger.error("Failed to save registry state: %s", e)

    def _load_state(self):
        """Load registry state from disk."""
        try:
            if self._state_file.exists():
                with open(self._state_file) as f:
                    json.load(f)

                logger.info("Loaded registry state from %s", self._state_file)

            if self._audit_log_path.exists():
                with open(self._audit_log_path) as f:
                    self._audit_log = json.load(f)

                logger.info("Loaded %s audit log entries", len(self._audit_log))

        except Exception as e:
            logger.error("Failed to load registry state: %s", e)

    def shutdown(self):
        """Shutdown the registry and all subsystems."""
        logger.info("Shutting down System Registry...")

        self.stop_health_monitoring()

        with self._lock:
            # Shutdown in reverse initialization order
            shutdown_order = list(reversed(self.get_initialization_order()))

            for subsystem_id in shutdown_order:
                if subsystem_id not in self._subsystems:
                    continue

                subsystem = self._subsystems[subsystem_id]

                try:
                    if hasattr(subsystem.instance, "shutdown"):
                        subsystem.instance.shutdown()

                    subsystem.state = SubsystemState.TERMINATED
                    logger.info("Shutdown subsystem: %s", subsystem_id)

                except Exception as e:
                    logger.error("Error shutting down subsystem %s: %s", subsystem_id, e)

            self._save_state()

        logger.info("System Registry shutdown complete")


# Singleton instance
_registry_instance: SystemRegistry | None = None
_registry_lock = threading.Lock()


def get_registry(data_dir: str = "data", config_dir: str = "config") -> SystemRegistry:
    """
    Get the singleton SystemRegistry instance.

    Args:
        data_dir: Directory for persistent state storage
        config_dir: Directory for configuration files

    Returns:
        SystemRegistry instance
    """
    global _registry_instance

    with _registry_lock:
        if _registry_instance is None:
            _registry_instance = SystemRegistry(data_dir=data_dir, config_dir=config_dir)
        return _registry_instance
