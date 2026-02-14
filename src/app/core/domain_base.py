#!/usr/bin/env python3
"""
Domain Base Classes - Common functionality for domain subsystems
Provides reusable implementations for ICommandable, IMonitorable, IObservable patterns.

STATUS: PRODUCTION
"""

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any

from .interface_abstractions import (
    BaseSubsystem,
    ICommandable,
    IMonitorable,
    IObservable,
    SubsystemCommand,
    SubsystemResponse,
)

logger = logging.getLogger(__name__)


class DomainSubsystemBase(BaseSubsystem, ICommandable, IMonitorable, IObservable):
    """
    Enhanced base class for domain subsystems with common implementations.

    Provides reusable implementations for:
    - Command execution framework
    - Metrics tracking with thread-safety
    - Event subscription/emission system
    - State persistence (load/save)
    - Processing loop management

    Reduces code duplication across domain subsystems by 70%+.

    Usage:
        class MyDomainSubsystem(DomainSubsystemBase):
            def _execute_domain_command(self, command: SubsystemCommand) -> SubsystemResponse:
                # Handle domain-specific commands
                pass

            def get_supported_commands(self) -> list[str]:
                return ["my_command_1", "my_command_2"]
    """

    def __init__(self, data_dir: str = "data", subsystem_name: str = "unknown", **config):
        """
        Initialize domain subsystem with common infrastructure.

        Args:
            data_dir: Base directory for persistent data
            subsystem_name: Name of the subsystem (used for data path)
            **config: Additional configuration parameters
        """
        super().__init__(data_dir=data_dir, config=config)

        # Data persistence
        self.data_path = Path(data_dir) / subsystem_name
        self.data_path.mkdir(parents=True, exist_ok=True)

        # Thread safety
        self._lock = threading.Lock()
        self._metrics_lock = threading.Lock()
        self._subscription_lock = threading.Lock()

        # Event subscription system
        self._subscriptions: dict[str, list[tuple]] = {}
        self._subscription_counter = 0

        # Processing thread management
        self._processing_thread: threading.Thread | None = None
        self._processing_active = False

        # Metrics tracking
        self._metrics: dict[str, Any] = {}

    def initialize(self) -> bool:
        """
        Initialize subsystem with common setup.

        Override _custom_initialize() for domain-specific initialization.
        """
        try:
            self._load_state()

            # Start processing loop if needed
            if self._should_start_processing_loop():
                self._processing_active = True
                self._processing_thread = threading.Thread(
                    target=self._processing_loop, daemon=True
                )
                self._processing_thread.start()

            # Custom initialization
            if not self._custom_initialize():
                return False

            self._initialized = True
            self.logger.info(f"{self.__class__.__name__} initialized successfully")
            return True
        except Exception as error:
            self.logger.error(f"Failed to initialize {self.__class__.__name__}: {error}")
            return False

    def shutdown(self) -> bool:
        """
        Shutdown subsystem with cleanup.

        Override _custom_shutdown() for domain-specific cleanup.
        """
        self.logger.info(f"Shutting down {self.__class__.__name__}")

        # Stop processing loop
        self._processing_active = False
        if self._processing_thread:
            self._processing_thread.join(timeout=5.0)

        # Custom shutdown
        self._custom_shutdown()

        # Save state
        self._save_state()

        self._initialized = False
        return True

    def health_check(self) -> bool:
        """Check if subsystem is healthy."""
        is_healthy = self._initialized
        if self._should_start_processing_loop():
            is_healthy = is_healthy and self._processing_active
        return is_healthy

    def get_status(self) -> dict[str, Any]:
        """Get subsystem status with metrics."""
        status = super().get_status()
        status["processing_active"] = self._processing_active

        with self._metrics_lock:
            status["metrics"] = self._metrics.copy()

        # Add domain-specific status
        domain_status = self._get_domain_status()
        if domain_status:
            status.update(domain_status)

        return status

    # ICommandable implementation
    def execute_command(self, command: SubsystemCommand) -> SubsystemResponse:
        """
        Execute command with timing and error handling.

        Delegates to _execute_domain_command() for domain-specific logic.
        """
        start_time = time.time()
        try:
            response = self._execute_domain_command(command)
            if response:
                return response

            return SubsystemResponse(
                command.command_id,
                False,
                error=f"Unknown command: {command.command_type}"
            )
        except Exception as error:
            self.logger.error(f"Command execution failed: {error}")
            return SubsystemResponse(
                command.command_id,
                False,
                error=str(error),
                execution_time_ms=(time.time() - start_time) * 1000
            )

    # IMonitorable implementation
    def get_metrics(self) -> dict[str, Any]:
        """Get all metrics (thread-safe)."""
        with self._metrics_lock:
            return self._metrics.copy()

    def get_metric(self, metric_name: str) -> Any:
        """Get specific metric value (thread-safe)."""
        with self._metrics_lock:
            return self._metrics.get(metric_name)

    def reset_metrics(self) -> bool:
        """Reset all numeric metrics to zero."""
        with self._metrics_lock:
            for key in self._metrics:
                if isinstance(self._metrics[key], (int, float)):
                    self._metrics[key] = 0
        return True

    def _increment_metric(self, metric_name: str, amount: int = 1):
        """Helper to increment a metric (thread-safe)."""
        with self._metrics_lock:
            if metric_name not in self._metrics:
                self._metrics[metric_name] = 0
            self._metrics[metric_name] += amount

    def _set_metric(self, metric_name: str, value: Any):
        """Helper to set a metric value (thread-safe)."""
        with self._metrics_lock:
            self._metrics[metric_name] = value

    # IObservable implementation
    def subscribe(self, event_type: str, callback: callable) -> str:
        """Subscribe to events."""
        with self._subscription_lock:
            subscription_id = f"sub_{self._subscription_counter}"
            self._subscription_counter += 1

            if event_type not in self._subscriptions:
                self._subscriptions[event_type] = []

            self._subscriptions[event_type].append((subscription_id, callback))
            self.logger.debug(f"Subscription {subscription_id} added for event {event_type}")
            return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from events."""
        with self._subscription_lock:
            for event_type, subscribers in self._subscriptions.items():
                self._subscriptions[event_type] = [
                    (sub_id, callback)
                    for sub_id, callback in subscribers
                    if sub_id != subscription_id
                ]
            return True

    def emit_event(self, event_type: str, data: Any) -> int:
        """Emit event to all subscribers."""
        notified_count = 0
        with self._subscription_lock:
            if event_type in self._subscriptions:
                for sub_id, callback in self._subscriptions[event_type]:
                    try:
                        callback(data)
                        notified_count += 1
                    except Exception as error:
                        self.logger.error(f"Event callback error for {sub_id}: {error}")
        return notified_count

    # State persistence
    def _load_state(self):
        """Load persisted state from JSON file."""
        state_file = self.data_path / "state.json"
        if state_file.exists():
            try:
                with open(state_file) as file:
                    state = json.load(file)
                    self._restore_state(state)
                    self.logger.debug(f"State loaded from {state_file}")
            except Exception as error:
                self.logger.error(f"Failed to load state: {error}")

    def _save_state(self):
        """Save current state to JSON file."""
        state_file = self.data_path / "state.json"
        try:
            state = self._get_state_for_persistence()
            with open(state_file, 'w') as file:
                json.dump(state, file, indent=2, default=str)
            self.logger.debug(f"State saved to {state_file}")
        except Exception as error:
            self.logger.error(f"Failed to save state: {error}")

    def _processing_loop(self):
        """
        Default processing loop that runs in background thread.

        Override _process_iteration() for custom processing logic.
        """
        self.logger.info(f"Processing loop started for {self.__class__.__name__}")
        while self._processing_active:
            try:
                self._process_iteration()
                time.sleep(1.0)  # Adjust sleep time as needed
            except Exception as error:
                self.logger.error(f"Processing loop error: {error}")
        self.logger.info(f"Processing loop stopped for {self.__class__.__name__}")

    # Extension points for subclasses
    def _should_start_processing_loop(self) -> bool:
        """Override to enable/disable background processing loop."""
        return False

    def _custom_initialize(self) -> bool:
        """Override for domain-specific initialization logic."""
        return True

    def _custom_shutdown(self):
        """Override for domain-specific shutdown logic."""
        pass

    def _get_domain_status(self) -> dict[str, Any]:
        """Override to add domain-specific status information."""
        return {}

    def _execute_domain_command(self, command: SubsystemCommand) -> SubsystemResponse | None:
        """
        Override to handle domain-specific commands.

        Return SubsystemResponse if command is handled, None otherwise.
        """
        return None

    def _restore_state(self, state: dict[str, Any]):
        """Override to restore domain-specific state from loaded data."""
        pass

    def _get_state_for_persistence(self) -> dict[str, Any]:
        """Override to provide domain-specific state for persistence."""
        return {
            "metrics": self._metrics,
            "initialized": self._initialized
        }

    def _process_iteration(self):
        """Override to define one iteration of the processing loop."""
        pass
