#!/usr/bin/env python3
"""
Enhanced Bootstrap Orchestrator - Metadata-Driven Initialization
Project-AI God Tier Zombie Apocalypse Defense Engine

One file. One job.
- Reads all SUBSYSTEM_METADATA from domain modules
- Topologically sorts by dependencies
- Initializes in order
- Monitors health
- Can degrade / restart / isolate subsystems

This turns "domains" into a system with self-awareness and governance.
"""

import importlib
import inspect
import logging
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from .advanced_boot import BootProfile, get_advanced_boot
from .event_spine import EventCategory, EventPriority, get_event_spine
from .governance_graph import get_governance_graph
from .system_registry import SubsystemPriority, SystemRegistry

logger = logging.getLogger(__name__)


class SubsystemLifecycleState(Enum):
    """Subsystem lifecycle states."""

    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    RUNNING = "running"
    DEGRADED = "degraded"
    ISOLATED = "isolated"
    RESTARTING = "restarting"
    FAILED = "failed"
    TERMINATED = "terminated"


@dataclass
class SubsystemMetadataInfo:
    """Parsed subsystem metadata."""

    subsystem_id: str
    name: str
    version: str
    priority: str
    dependencies: list[str]
    provides_capabilities: list[str]
    module_path: str
    class_name: str
    class_ref: type
    metadata: dict[str, Any]


class EnhancedBootstrapOrchestrator:
    """
    Enhanced Bootstrap Orchestrator

    Metadata-driven initialization with governance awareness.
    """

    def __init__(
        self,
        data_dir: str = "data",
        domain_paths: list[str] | None = None,
        boot_profile: BootProfile | None = None,
    ):
        """
        Initialize orchestrator.

        Args:
            data_dir: Data directory
            domain_paths: Paths to search for domain modules
            boot_profile: Optional boot profile to use
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.domain_paths = domain_paths or ["src.app.domains"]

        # Core systems
        self.registry = SystemRegistry(data_dir=str(self.data_dir))
        self.event_spine = get_event_spine()
        self.governance = get_governance_graph()
        self.advanced_boot = get_advanced_boot()

        # Set boot profile if provided
        if boot_profile:
            self.advanced_boot.set_boot_profile(boot_profile)

        # Discovered subsystems
        self._subsystem_metadata: dict[str, SubsystemMetadataInfo] = {}
        self._subsystem_instances: dict[str, Any] = {}
        self._subsystem_lifecycle: dict[str, SubsystemLifecycleState] = {}

        # Initialization order
        self._init_order: list[str] = []

        # Health monitoring
        self._health_monitor_active = False
        self._health_monitor_thread: threading.Thread | None = None

        # Statistics
        self._stats = {
            "discovered": 0,
            "initialized": 0,
            "running": 0,
            "degraded": 0,
            "isolated": 0,
            "failed": 0,
        }

        # Thread safety
        self._lock = threading.RLock()

        logger.info("Enhanced Bootstrap Orchestrator initialized")

    def discover_subsystems(self) -> int:
        """
        Discover all subsystems by reading SUBSYSTEM_METADATA.

        Returns:
            Number of subsystems discovered
        """
        logger.info("Discovering subsystems...")

        discovered = 0

        for domain_path in self.domain_paths:
            try:
                # Import the domain package
                domain_module = importlib.import_module(domain_path)

                # Get the package directory
                domain_dir = Path(domain_module.__file__).parent

                # Find all Python files
                for py_file in domain_dir.glob("*.py"):
                    if py_file.name.startswith("_"):
                        continue

                    # Build module path
                    module_name = f"{domain_path}.{py_file.stem}"

                    try:
                        module = importlib.import_module(module_name)

                        # Look for classes with SUBSYSTEM_METADATA
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if not hasattr(obj, "SUBSYSTEM_METADATA"):
                                continue

                            metadata = obj.SUBSYSTEM_METADATA

                            subsystem_id = metadata.get("id", name.lower())

                            if subsystem_id in self._subsystem_metadata:
                                continue

                            # Parse metadata
                            info = SubsystemMetadataInfo(
                                subsystem_id=subsystem_id,
                                name=metadata.get("name", name),
                                version=metadata.get("version", "1.0.0"),
                                priority=metadata.get("priority", "MEDIUM"),
                                dependencies=metadata.get("dependencies", []),
                                provides_capabilities=metadata.get(
                                    "provides_capabilities", []
                                ),
                                module_path=module_name,
                                class_name=name,
                                class_ref=obj,
                                metadata=metadata,
                            )

                            self._subsystem_metadata[subsystem_id] = info
                            self._subsystem_lifecycle[subsystem_id] = (
                                SubsystemLifecycleState.UNINITIALIZED
                            )

                            discovered += 1

                            logger.info(f"Discovered: {info.name} ({subsystem_id})")

                    except Exception as e:
                        logger.error(f"Error loading module {module_name}: {e}")

            except Exception as e:
                logger.error(f"Error discovering from {domain_path}: {e}")

        with self._lock:
            self._stats["discovered"] = discovered

        logger.info(f"Discovery complete: {discovered} subsystems found")

        return discovered

    def topological_sort(self) -> list[str]:
        """
        Topologically sort subsystems by dependencies.

        Returns:
            List of subsystem IDs in initialization order
        """
        logger.info("Computing topological sort...")

        # Build dependency graph
        in_degree = {}
        graph = {}

        for subsystem_id, info in self._subsystem_metadata.items():
            in_degree[subsystem_id] = 0
            graph[subsystem_id] = []

        for subsystem_id, info in self._subsystem_metadata.items():
            for dep in info.dependencies:
                if dep in graph:
                    graph[dep].append(subsystem_id)
                    in_degree[subsystem_id] += 1

        # Kahn's algorithm
        queue = [sid for sid, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # Sort by priority for deterministic ordering
            queue.sort(key=lambda sid: self._get_priority_value(sid))

            current = queue.pop(0)
            result.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(result) != len(self._subsystem_metadata):
            remaining = set(self._subsystem_metadata.keys()) - set(result)
            logger.error(f"Circular dependency detected: {remaining}")
            # Add remaining in priority order
            result.extend(
                sorted(remaining, key=lambda sid: self._get_priority_value(sid))
            )

        self._init_order = result

        logger.info(f"Initialization order: {result}")

        return result

    def _get_priority_value(self, subsystem_id: str) -> int:
        """Get numeric priority value for sorting."""
        info = self._subsystem_metadata.get(subsystem_id)
        if not info:
            return 999

        priority_map = {
            "CRITICAL": 0,
            "HIGH": 1,
            "MEDIUM": 2,
            "LOW": 3,
            "BACKGROUND": 4,
        }

        return priority_map.get(info.priority.upper(), 2)

    def initialize_all(self, boot_profile: BootProfile | None = None) -> bool:
        """
        Initialize all subsystems in dependency order with advanced boot features.

        Args:
            boot_profile: Optional boot profile to use

        Returns:
            True if all critical subsystems initialized
        """
        # Start boot sequence
        self.advanced_boot.start_boot(boot_profile)

        logger.info("=" * 80)
        logger.info("INITIALIZING DEFENSE ENGINE")
        logger.info("=" * 80)

        if not self._init_order:
            self.topological_sort()

        success_count = 0
        failure_count = 0
        skipped_count = 0

        # Check for ethics-first mode
        ethics_priority_subsystems = {"ethics_governance", "agi_safeguards"}
        ethics_first = (
            self.advanced_boot.get_current_profile() == BootProfile.ETHICS_FIRST
        )

        for subsystem_id in self._init_order:
            info = self._subsystem_metadata.get(subsystem_id)
            if not info:
                continue

            # Check if should initialize based on boot profile
            should_init, reason = self.advanced_boot.should_initialize_subsystem(
                subsystem_id, info.metadata
            )

            if not should_init:
                logger.info(f"Skipping {info.name}: {reason}")
                skipped_count += 1
                self.advanced_boot.increment_subsystems_skipped()
                continue

            # Check for priority override
            priority_override = self.advanced_boot.get_priority_override(subsystem_id)
            if priority_override:
                info.priority = priority_override
                logger.info(
                    f"Priority override for {subsystem_id}: {priority_override}"
                )

            logger.info(f"Initializing: {info.name} ({subsystem_id})")

            if self._initialize_subsystem(subsystem_id):
                success_count += 1
                self.advanced_boot.increment_subsystems_initialized()

                # Mark ethics checkpoint if ethics subsystem initialized
                if ethics_first and subsystem_id in ethics_priority_subsystems:
                    # Check if all ethics subsystems are done
                    all_ethics_done = all(
                        self._subsystem_lifecycle.get(es)
                        == SubsystemLifecycleState.RUNNING
                        for es in ethics_priority_subsystems
                        if es in self._subsystem_lifecycle
                    )

                    if all_ethics_done:
                        self.advanced_boot.mark_ethics_checkpoint_passed()
            else:
                failure_count += 1

                # Check if critical
                if info.priority.upper() == "CRITICAL":
                    logger.error(f"Critical subsystem failed: {subsystem_id}")

                    # Check if should activate emergency mode
                    if not self.advanced_boot.is_emergency_mode():
                        logger.warning(
                            "Critical subsystem failure - considering emergency mode"
                        )

                    self.advanced_boot.finish_boot()
                    return False

        logger.info("=" * 80)
        logger.info(
            f"INITIALIZATION COMPLETE: {success_count} success, {failure_count} failed, {skipped_count} skipped"
        )
        logger.info("=" * 80)

        # Finish boot sequence
        self.advanced_boot.finish_boot()

        # Start health monitoring if enabled
        if (
            self.advanced_boot._current_profile_config
            and self.advanced_boot._current_profile_config.enable_health_monitoring
        ):
            self.start_health_monitoring()

        return True

    def _initialize_subsystem(self, subsystem_id: str) -> bool:
        """Initialize a single subsystem."""
        info = self._subsystem_metadata.get(subsystem_id)
        if not info:
            return False

        with self._lock:
            self._subsystem_lifecycle[subsystem_id] = (
                SubsystemLifecycleState.INITIALIZING
            )

        try:
            # Check dependencies
            for dep_id in info.dependencies:
                dep_state = self._subsystem_lifecycle.get(dep_id)

                if dep_state != SubsystemLifecycleState.RUNNING:
                    logger.error(
                        f"Dependency not running: {dep_id} (state: {dep_state})"
                    )
                    with self._lock:
                        self._subsystem_lifecycle[subsystem_id] = (
                            SubsystemLifecycleState.FAILED
                        )
                        self._stats["failed"] += 1
                    return False

            # Instantiate
            config = info.metadata.get("config", {})
            config["data_dir"] = str(self.data_dir)

            instance = info.class_ref(**config)

            # Initialize
            if hasattr(instance, "initialize"):
                success = instance.initialize()
                if not success:
                    raise Exception("Initialize method returned False")

            # Register with registry
            priority = SubsystemPriority[info.priority.upper()]

            self.registry.register_subsystem(
                name=info.name,
                subsystem_id=subsystem_id,
                version=info.version,
                priority=priority,
                instance=instance,
                dependencies=info.dependencies,
                provides_capabilities=info.provides_capabilities,
            )

            # Store instance
            with self._lock:
                self._subsystem_instances[subsystem_id] = instance
                self._subsystem_lifecycle[subsystem_id] = (
                    SubsystemLifecycleState.RUNNING
                )
                self._stats["running"] += 1
                self._stats["initialized"] += 1

            logger.info(f"✅ {info.name} initialized successfully")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to initialize {subsystem_id}: {e}")

            with self._lock:
                self._subsystem_lifecycle[subsystem_id] = SubsystemLifecycleState.FAILED
                self._stats["failed"] += 1

            return False

    def start_health_monitoring(self, interval: float = 30.0):
        """Start health monitoring."""
        if self._health_monitor_active:
            return

        self._health_monitor_active = True
        self._health_monitor_thread = threading.Thread(
            target=self._health_monitoring_loop,
            args=(interval,),
            daemon=True,
            name="HealthMonitor",
        )
        self._health_monitor_thread.start()

        logger.info(f"Health monitoring started (interval={interval}s)")

    def stop_health_monitoring(self):
        """Stop health monitoring."""
        self._health_monitor_active = False

        if self._health_monitor_thread:
            self._health_monitor_thread.join(timeout=5.0)

        logger.info("Health monitoring stopped")

    def _health_monitoring_loop(self, interval: float):
        """Health monitoring loop."""
        while self._health_monitor_active:
            try:
                self._check_all_health()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                time.sleep(interval)

    def _check_all_health(self):
        """Check health of all subsystems."""
        for subsystem_id, instance in self._subsystem_instances.items():
            try:
                is_healthy = True

                if hasattr(instance, "health_check"):
                    is_healthy = instance.health_check()

                current_state = self._subsystem_lifecycle.get(subsystem_id)

                if not is_healthy and current_state == SubsystemLifecycleState.RUNNING:
                    logger.warning(f"Health check failed: {subsystem_id}")
                    self.degrade_subsystem(subsystem_id)

                elif is_healthy and current_state == SubsystemLifecycleState.DEGRADED:
                    logger.info(f"Health recovered: {subsystem_id}")
                    self.restore_subsystem(subsystem_id)

            except Exception as e:
                logger.error(f"Error checking health of {subsystem_id}: {e}")

    def degrade_subsystem(self, subsystem_id: str):
        """
        Degrade a subsystem (reduce functionality but keep running).

        Args:
            subsystem_id: Subsystem to degrade
        """
        logger.info(f"Degrading subsystem: {subsystem_id}")

        with self._lock:
            self._subsystem_lifecycle[subsystem_id] = SubsystemLifecycleState.DEGRADED
            self._stats["degraded"] += 1
            self._stats["running"] -= 1

        # Publish event
        self.event_spine.publish(
            category=EventCategory.SYSTEM_HEALTH,
            source_domain="bootstrap_orchestrator",
            payload={
                "subsystem_id": subsystem_id,
                "action": "degraded",
                "reason": "health_check_failed",
            },
            priority=EventPriority.HIGH,
        )

    def restore_subsystem(self, subsystem_id: str):
        """
        Restore a degraded subsystem to full operation.

        Args:
            subsystem_id: Subsystem to restore
        """
        logger.info(f"Restoring subsystem: {subsystem_id}")

        with self._lock:
            self._subsystem_lifecycle[subsystem_id] = SubsystemLifecycleState.RUNNING
            self._stats["running"] += 1
            self._stats["degraded"] -= 1

        # Publish event
        self.event_spine.publish(
            category=EventCategory.SYSTEM_HEALTH,
            source_domain="bootstrap_orchestrator",
            payload={
                "subsystem_id": subsystem_id,
                "action": "restored",
                "reason": "health_recovered",
            },
            priority=EventPriority.NORMAL,
        )

    def restart_subsystem(self, subsystem_id: str) -> bool:
        """
        Restart a failed subsystem.

        Args:
            subsystem_id: Subsystem to restart

        Returns:
            True if restart successful
        """
        logger.info(f"Restarting subsystem: {subsystem_id}")

        with self._lock:
            self._subsystem_lifecycle[subsystem_id] = SubsystemLifecycleState.RESTARTING

        # Shutdown first
        instance = self._subsystem_instances.get(subsystem_id)
        if instance and hasattr(instance, "shutdown"):
            try:
                instance.shutdown()
            except Exception as e:
                logger.error(f"Error shutting down {subsystem_id}: {e}")

        # Reinitialize
        success = self._initialize_subsystem(subsystem_id)

        if success:
            logger.info(f"✅ Subsystem restarted: {subsystem_id}")
        else:
            logger.error(f"❌ Failed to restart: {subsystem_id}")

        return success

    def isolate_subsystem(self, subsystem_id: str):
        """
        Isolate a problematic subsystem (stop but don't remove).

        Args:
            subsystem_id: Subsystem to isolate
        """
        logger.info(f"Isolating subsystem: {subsystem_id}")

        instance = self._subsystem_instances.get(subsystem_id)

        if instance and hasattr(instance, "shutdown"):
            try:
                instance.shutdown()
            except Exception as e:
                logger.error(f"Error isolating {subsystem_id}: {e}")

        with self._lock:
            self._subsystem_lifecycle[subsystem_id] = SubsystemLifecycleState.ISOLATED
            self._stats["isolated"] += 1

            if subsystem_id in self._subsystem_lifecycle:
                old_state = self._subsystem_lifecycle[subsystem_id]
                if old_state == SubsystemLifecycleState.RUNNING:
                    self._stats["running"] -= 1
                elif old_state == SubsystemLifecycleState.DEGRADED:
                    self._stats["degraded"] -= 1

        # Publish event
        self.event_spine.publish(
            category=EventCategory.SYSTEM_HEALTH,
            source_domain="bootstrap_orchestrator",
            payload={
                "subsystem_id": subsystem_id,
                "action": "isolated",
                "reason": "manual_isolation",
            },
            priority=EventPriority.CRITICAL,
        )

    def get_status(self) -> dict[str, Any]:
        """Get orchestrator status."""
        with self._lock:
            return {
                "discovered": self._stats["discovered"],
                "initialized": self._stats["initialized"],
                "running": self._stats["running"],
                "degraded": self._stats["degraded"],
                "isolated": self._stats["isolated"],
                "failed": self._stats["failed"],
                "health_monitoring": self._health_monitor_active,
                "subsystem_states": {
                    sid: state.value for sid, state in self._subsystem_lifecycle.items()
                },
                "initialization_order": self._init_order,
            }

    def get_subsystem(self, subsystem_id: str) -> Any | None:
        """Get subsystem instance."""
        return self._subsystem_instances.get(subsystem_id)

    def shutdown(self):
        """Shutdown orchestrator and all subsystems."""
        logger.info("Shutting down Enhanced Bootstrap Orchestrator...")

        self.stop_health_monitoring()

        # Shutdown in reverse order
        for subsystem_id in reversed(self._init_order):
            instance = self._subsystem_instances.get(subsystem_id)

            if instance and hasattr(instance, "shutdown"):
                try:
                    logger.info(f"Shutting down: {subsystem_id}")
                    instance.shutdown()
                except Exception as e:
                    logger.error(f"Error shutting down {subsystem_id}: {e}")

        logger.info("Enhanced Bootstrap Orchestrator shutdown complete")
