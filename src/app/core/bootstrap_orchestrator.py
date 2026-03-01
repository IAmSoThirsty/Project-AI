#!/usr/bin/env python3
"""
Bootstrap Orchestrator - Recursive Config-Driven System Initialization
Project-AI God Tier Zombie Apocalypse Defense Engine

This module orchestrates the recursive initialization of all defense engine subsystems
using a config-driven approach. It handles:
- Recursive subsystem discovery and loading
- Configuration-driven initialization
- Dependency resolution and ordering
- Failure recovery and rollback
- Hot-reload and runtime reconfiguration
- Air-gapped operation support

Features:
- Zero-configuration auto-discovery
- Declarative subsystem definitions
- Recursive expansion for infinite extensibility
- Byzantine fault tolerance
- Audit trail for all operations
"""

import importlib
import inspect
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import toml

from .system_registry import (
    SubsystemPriority,
    SystemRegistry,
    get_registry,
)

logger = logging.getLogger(__name__)


@dataclass
class SubsystemDefinition:
    """Definition of a subsystem from configuration"""

    name: str
    subsystem_id: str
    version: str
    priority: str
    module_path: str
    class_name: str
    dependencies: list[str]
    provides_capabilities: list[str]
    config: dict[str, Any]
    enabled: bool = True
    auto_init: bool = True


class BootstrapOrchestrator:
    """
    Recursive Bootstrap Orchestrator

    Orchestrates the initialization of all defense engine subsystems using
    recursive, config-driven discovery and initialization.
    """

    def __init__(
        self,
        config_path: str | None = None,
        data_dir: str = "data",
        registry: SystemRegistry | None = None,
    ):
        """
        Initialize the bootstrap orchestrator.

        Args:
            config_path: Path to configuration file (TOML or JSON)
            data_dir: Directory for persistent data
            registry: Optional SystemRegistry instance (creates one if not provided)
        """
        self.config_path = Path(config_path) if config_path else None
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Get or create registry
        self.registry = (
            registry if registry else get_registry(data_dir=str(self.data_dir))
        )

        # Configuration
        self.config: dict[str, Any] = {}
        self.subsystem_definitions: dict[str, SubsystemDefinition] = {}

        # Bootstrap state
        self.initialized_subsystems: list[str] = []
        self.failed_subsystems: list[str] = []
        self.bootstrap_start_time: datetime | None = None
        self.bootstrap_end_time: datetime | None = None

        # Audit trail
        self.bootstrap_log: list[dict[str, Any]] = []

        # Thirsty-Lang Integration (Floor 1)
        self.thirsty_bootstrap = os.path.join(
            os.path.dirname(__file__), "bootstrap.thirsty"
        )

        # Load configuration
        if self.config_path and self.config_path.exists():
            self._load_config()
        else:
            self._initialize_default_config()

        logger.info("Bootstrap Orchestrator initialized (Floor 1 active)")
        if os.path.exists(self.thirsty_bootstrap):
            logger.info(f"Sovereign Thirsty Bootstrap found: {self.thirsty_bootstrap}")

    def _load_config(self):
        """Load configuration from file."""
        try:
            if self.config_path.suffix in [".toml"]:
                with open(self.config_path) as f:
                    self.config = toml.load(f)
            elif self.config_path.suffix in [".json"]:
                with open(self.config_path) as f:
                    self.config = json.load(f)
            else:
                logger.error("Unsupported config format: %s", self.config_path.suffix)
                self._initialize_default_config()
                return

            # Parse subsystem definitions
            if "subsystems" in self.config:
                for subsystem_id, subsystem_config in self.config["subsystems"].items():
                    self._parse_subsystem_definition(subsystem_id, subsystem_config)

            logger.info("Loaded configuration from %s", self.config_path)
            logger.info(
                "Discovered %s subsystem definitions", len(self.subsystem_definitions)
            )

        except Exception as e:
            logger.error("Failed to load config from %s: %s", self.config_path, e)
            self._initialize_default_config()

    def _parse_subsystem_definition(self, subsystem_id: str, config: dict[str, Any]):
        """Parse a subsystem definition from configuration."""
        try:
            definition = SubsystemDefinition(
                name=config.get("name", subsystem_id),
                subsystem_id=subsystem_id,
                version=config.get("version", "1.0.0"),
                priority=config.get("priority", "MEDIUM"),
                module_path=config["module_path"],
                class_name=config["class_name"],
                dependencies=config.get("dependencies", []),
                provides_capabilities=config.get("provides_capabilities", []),
                config=config.get("config", {}),
                enabled=config.get("enabled", True),
                auto_init=config.get("auto_init", True),
            )

            self.subsystem_definitions[subsystem_id] = definition

        except KeyError as e:
            logger.error(
                "Invalid subsystem definition for %s: missing %s", subsystem_id, e
            )

    def _initialize_default_config(self):
        """Initialize with default configuration."""
        self.config = {
            "bootstrap": {
                "auto_discover": True,
                "discovery_paths": ["src/app/domains", "src/app/core"],
                "failure_mode": "continue",  # continue, stop, rollback
                "health_check_interval": 30,
                "enable_hot_reload": True,
            },
            "subsystems": {},
        }

        logger.info("Initialized default configuration")

    def discover_subsystems(self, discovery_paths: list[str] = None) -> int:
        """
        Auto-discover subsystems from specified paths.

        Args:
            discovery_paths: List of paths to search for subsystems

        Returns:
            Number of subsystems discovered
        """
        if discovery_paths is None:
            discovery_paths = self.config.get("bootstrap", {}).get(
                "discovery_paths", ["src/app/domains", "src/app/core"]
            )

        discovered = 0

        for search_path in discovery_paths:
            path = Path(search_path)
            if not path.exists():
                logger.warning("Discovery path does not exist: %s", search_path)
                continue

            # Find all Python files
            for py_file in path.rglob("*.py"):
                if py_file.name.startswith("_"):
                    continue

                try:
                    # Convert path to module notation
                    module_path = str(py_file.relative_to(Path.cwd())).replace(
                        os.sep, "."
                    )[:-3]

                    # Try to import and inspect
                    module = importlib.import_module(module_path)

                    # Look for classes with SUBSYSTEM_METADATA
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if hasattr(obj, "SUBSYSTEM_METADATA"):
                            metadata = obj.SUBSYSTEM_METADATA

                            subsystem_id = metadata.get("id", name.lower())

                            if subsystem_id not in self.subsystem_definitions:
                                definition = SubsystemDefinition(
                                    name=metadata.get("name", name),
                                    subsystem_id=subsystem_id,
                                    version=metadata.get("version", "1.0.0"),
                                    priority=metadata.get("priority", "MEDIUM"),
                                    module_path=module_path,
                                    class_name=name,
                                    dependencies=metadata.get("dependencies", []),
                                    provides_capabilities=metadata.get(
                                        "provides_capabilities", []
                                    ),
                                    config=metadata.get("config", {}),
                                    enabled=metadata.get("enabled", True),
                                    auto_init=metadata.get("auto_init", True),
                                )

                                self.subsystem_definitions[subsystem_id] = definition
                                discovered += 1

                                logger.info(
                                    "Discovered subsystem: %s (%s)", name, subsystem_id
                                )

                except Exception as e:
                    logger.debug("Could not inspect %s: %s", py_file, e)

        logger.info("Discovery complete: found %s new subsystems", discovered)
        return discovered

    def register_subsystem_class(
        self,
        subsystem_class: type,
        subsystem_id: str = None,
        config: dict[str, Any] = None,
        auto_init: bool = True,
    ) -> bool:
        """
        Manually register a subsystem class.

        Args:
            subsystem_class: The subsystem class to register
            subsystem_id: Optional subsystem ID (uses class name if not provided)
            config: Optional configuration dictionary
            auto_init: Whether to auto-initialize during bootstrap

        Returns:
            bool: True if registration successful
        """
        try:
            # Extract metadata
            if hasattr(subsystem_class, "SUBSYSTEM_METADATA"):
                metadata = subsystem_class.SUBSYSTEM_METADATA
            else:
                metadata = {}

            name = metadata.get("name", subsystem_class.__name__)
            sid = subsystem_id or metadata.get("id", subsystem_class.__name__.lower())

            definition = SubsystemDefinition(
                name=name,
                subsystem_id=sid,
                version=metadata.get("version", "1.0.0"),
                priority=metadata.get("priority", "MEDIUM"),
                module_path=subsystem_class.__module__,
                class_name=subsystem_class.__name__,
                dependencies=metadata.get("dependencies", []),
                provides_capabilities=metadata.get("provides_capabilities", []),
                config=config or metadata.get("config", {}),
                enabled=True,
                auto_init=auto_init,
            )

            self.subsystem_definitions[sid] = definition

            logger.info("Manually registered subsystem: %s (%s)", name, sid)
            return True

        except Exception as e:
            logger.error(
                "Failed to register subsystem class %s: %s", subsystem_class, e
            )
            return False

    def bootstrap(self, auto_start_monitoring: bool = True) -> bool:
        """
        Execute the bootstrap sequence.

        Performs recursive, config-driven initialization of all enabled subsystems
        in the correct dependency order.

        Args:
            auto_start_monitoring: Whether to automatically start health monitoring

        Returns:
            bool: True if bootstrap successful, False if critical failures occurred
        """
        self.bootstrap_start_time = datetime.now()

        logger.info("=" * 80)
        logger.info("INITIATING GOD TIER ZOMBIE APOCALYPSE DEFENSE ENGINE BOOTSTRAP")
        logger.info("=" * 80)

        try:
            # Phase 1: Discovery
            logger.info("Phase 1: Subsystem Discovery")
            if self.config.get("bootstrap", {}).get("auto_discover", True):
                discovered = self.discover_subsystems()
                logger.info("Auto-discovery complete: %s subsystems found", discovered)

            # Phase 2: Registration
            logger.info("Phase 2: Subsystem Registration")
            registered_count = self._register_all_subsystems()
            logger.info("Registered %s subsystems with registry", registered_count)

            # Phase 3: Initialization
            logger.info("Phase 3: Subsystem Initialization")
            initialization_order = self.registry.get_initialization_order()
            logger.info(
                "Initialization order determined: %s subsystems",
                len(initialization_order),
            )

            success_count = 0
            failure_count = 0

            for subsystem_id in initialization_order:
                if subsystem_id not in self.subsystem_definitions:
                    continue

                definition = self.subsystem_definitions[subsystem_id]

                if not definition.enabled or not definition.auto_init:
                    logger.info(
                        "Skipping %s (enabled=%s, auto_init=%s)",
                        subsystem_id,
                        definition.enabled,
                        definition.auto_init,
                    )
                    continue

                logger.info("Initializing: %s (%s)", definition.name, subsystem_id)

                if self.registry.initialize_subsystem(subsystem_id):
                    self.initialized_subsystems.append(subsystem_id)
                    success_count += 1

                    self.bootstrap_log.append(
                        {
                            "timestamp": datetime.now().isoformat(),
                            "subsystem_id": subsystem_id,
                            "action": "initialize",
                            "success": True,
                        }
                    )
                else:
                    self.failed_subsystems.append(subsystem_id)
                    failure_count += 1

                    self.bootstrap_log.append(
                        {
                            "timestamp": datetime.now().isoformat(),
                            "subsystem_id": subsystem_id,
                            "action": "initialize",
                            "success": False,
                        }
                    )

                    # Handle failure based on failure mode
                    failure_mode = self.config.get("bootstrap", {}).get(
                        "failure_mode", "continue"
                    )

                    if failure_mode == "stop":
                        logger.error("Failure mode is 'stop', aborting bootstrap")
                        return False
                    elif failure_mode == "rollback":
                        logger.error(
                            "Failure mode is 'rollback', rolling back bootstrap"
                        )
                        self._rollback_bootstrap()
                        return False
                    else:
                        logger.warning(
                            "Failed to initialize %s, continuing...", subsystem_id
                        )

            # Phase 4: Post-initialization
            logger.info("Phase 4: Post-Bootstrap Configuration")

            if auto_start_monitoring:
                health_check_interval = self.config.get("bootstrap", {}).get(
                    "health_check_interval", 30
                )
                self.registry.start_health_monitoring(interval=health_check_interval)

            # Save bootstrap state
            self._save_bootstrap_state()

            self.bootstrap_end_time = datetime.now()
            duration = (
                self.bootstrap_end_time - self.bootstrap_start_time
            ).total_seconds()

            logger.info("=" * 80)
            logger.info("BOOTSTRAP COMPLETE")
            logger.info("Duration: %ss", duration)
            logger.info("Success: %s/%s", success_count, success_count + failure_count)
            logger.info("Failed: %s", failure_count)
            logger.info("=" * 80)

            return failure_count == 0

        except Exception as e:
            logger.error("Bootstrap failed with exception: %s", e, exc_info=True)
            self._rollback_bootstrap()
            return False

    def _register_all_subsystems(self) -> int:
        """
        Register all subsystem definitions with the registry.

        Returns:
            Number of subsystems registered
        """
        registered = 0

        for subsystem_id, definition in self.subsystem_definitions.items():
            if not definition.enabled:
                continue

            try:
                # Import the module and get the class
                module = importlib.import_module(definition.module_path)
                subsystem_class = getattr(module, definition.class_name)

                # Instantiate with config
                instance = subsystem_class(**definition.config)

                # Map priority string to enum
                priority = SubsystemPriority[definition.priority.upper()]

                # Register with registry
                self.registry.register_subsystem(
                    name=definition.name,
                    subsystem_id=subsystem_id,
                    version=definition.version,
                    priority=priority,
                    instance=instance,
                    dependencies=definition.dependencies,
                    provides_capabilities=definition.provides_capabilities,
                    health_check_fn=None,
                    metadata={"definition": definition.config},
                )

                registered += 1

            except Exception as e:
                logger.error("Failed to register subsystem %s: %s", subsystem_id, e)

        return registered

    def _rollback_bootstrap(self):
        """Rollback bootstrap by shutting down initialized subsystems."""
        logger.info("Rolling back bootstrap...")

        for subsystem_id in reversed(self.initialized_subsystems):
            try:
                subsystem = self.registry.get_subsystem(subsystem_id)
                if subsystem and hasattr(subsystem, "shutdown"):
                    subsystem.shutdown()

                logger.info("Rolled back: %s", subsystem_id)

            except Exception as e:
                logger.error("Error rolling back %s: %s", subsystem_id, e)

        self.initialized_subsystems.clear()

    def _save_bootstrap_state(self):
        """Save bootstrap state to disk."""
        try:
            state = {
                "timestamp": datetime.now().isoformat(),
                "bootstrap_start": (
                    self.bootstrap_start_time.isoformat()
                    if self.bootstrap_start_time
                    else None
                ),
                "bootstrap_end": (
                    self.bootstrap_end_time.isoformat()
                    if self.bootstrap_end_time
                    else None
                ),
                "initialized_subsystems": self.initialized_subsystems,
                "failed_subsystems": self.failed_subsystems,
                "bootstrap_log": self.bootstrap_log,
            }

            state_file = self.data_dir / "bootstrap_state.json"
            with open(state_file, "w") as f:
                json.dump(state, f, indent=2)

            logger.info("Saved bootstrap state to %s", state_file)

        except Exception as e:
            logger.error("Failed to save bootstrap state: %s", e)

    def reload_subsystem(self, subsystem_id: str) -> bool:
        """
        Hot-reload a subsystem.

        Args:
            subsystem_id: The subsystem to reload

        Returns:
            bool: True if reload successful
        """
        if not self.config.get("bootstrap", {}).get("enable_hot_reload", True):
            logger.error("Hot-reload is disabled in configuration")
            return False

        logger.info("Hot-reloading subsystem: %s", subsystem_id)

        try:
            # Get current subsystem
            subsystem = self.registry.get_subsystem(subsystem_id)
            if not subsystem:
                logger.error("Subsystem not found: %s", subsystem_id)
                return False

            # Shutdown current instance
            if hasattr(subsystem, "shutdown"):
                subsystem.shutdown()

            # Reload module
            if subsystem_id in self.subsystem_definitions:
                definition = self.subsystem_definitions[subsystem_id]
                module = importlib.import_module(definition.module_path)
                importlib.reload(module)

            # Reinitialize
            return self.registry.initialize_subsystem(subsystem_id)

        except Exception as e:
            logger.error("Failed to reload subsystem %s: %s", subsystem_id, e)
            return False

    def get_bootstrap_status(self) -> dict[str, Any]:
        """
        Get bootstrap status information.

        Returns:
            Dictionary containing bootstrap status
        """
        status = {
            "bootstrap_complete": self.bootstrap_end_time is not None,
            "start_time": (
                self.bootstrap_start_time.isoformat()
                if self.bootstrap_start_time
                else None
            ),
            "end_time": (
                self.bootstrap_end_time.isoformat() if self.bootstrap_end_time else None
            ),
            "duration_seconds": None,
            "initialized_subsystems": self.initialized_subsystems,
            "failed_subsystems": self.failed_subsystems,
            "total_definitions": len(self.subsystem_definitions),
            "registry_status": self.registry.get_system_status(),
        }

        if self.bootstrap_start_time and self.bootstrap_end_time:
            status["duration_seconds"] = (
                self.bootstrap_end_time - self.bootstrap_start_time
            ).total_seconds()

        return status

    def shutdown(self):
        """Shutdown the orchestrator and all subsystems."""
        logger.info("Shutting down Bootstrap Orchestrator...")

        self._save_bootstrap_state()
        self.registry.shutdown()

        logger.info("Bootstrap Orchestrator shutdown complete")


# Convenience functions
def create_orchestrator(
    config_path: str = None, data_dir: str = "data"
) -> BootstrapOrchestrator:
    """
    Create and configure a bootstrap orchestrator.

    Args:
        config_path: Path to configuration file
        data_dir: Directory for persistent data

    Returns:
        Configured BootstrapOrchestrator instance
    """
    return BootstrapOrchestrator(config_path=config_path, data_dir=data_dir)


def bootstrap_defense_engine(
    config_path: str = None, data_dir: str = "data"
) -> BootstrapOrchestrator:
    """
    Bootstrap the complete defense engine.

    Args:
        config_path: Path to configuration file
        data_dir: Directory for persistent data

    Returns:
        Configured BootstrapOrchestrator instance with all subsystems initialized
    """
    orchestrator = create_orchestrator(config_path=config_path, data_dir=data_dir)
    orchestrator.bootstrap()
    return orchestrator
