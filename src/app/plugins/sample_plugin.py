#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""Sample marketplace plugin demonstrating metadata and safety checks."""

from __future__ import annotations

import logging
import time
from enum import Enum
from typing import Any, Callable

from app.core.ai_systems import FourLaws, Plugin
from app.core.observability import get_observability_system

logger = logging.getLogger(__name__)


class PluginState(Enum):
    """Plugin lifecycle states."""

    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"


class EventType(Enum):
    """Plugin event types."""

    INITIALIZED = "initialized"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ACTION_VALIDATED = "action_validated"
    ACTION_BLOCKED = "action_blocked"
    ERROR_OCCURRED = "error_occurred"
    STATE_CHANGED = "state_changed"


class MarketplaceSamplePlugin(Plugin):
    """
    A comprehensive plugin demonstrating:
    - Four Laws validation
    - Event-driven architecture
    - Full lifecycle management
    - Observability integration
    - Error handling
    """

    def __init__(self) -> None:
        super().__init__(name="marketplace_sample_plugin", version="0.1.0")
        self._state = PluginState.CREATED
        self._event_handlers: dict[EventType, list[Callable[[dict[str, Any]], None]]] = (
            {}
        )
        self._initialization_time: float | None = None
        self._action_count = 0
        self._blocked_count = 0
        self._error_count = 0

        # Get observability system for proper telemetry
        self._observability = get_observability_system()

        logger.info(f"Plugin {self.name} v{self.version} created")

    @property
    def state(self) -> PluginState:
        """Get current plugin state."""
        return self._state

    @property
    def metrics(self) -> dict[str, Any]:
        """Get plugin metrics."""
        uptime = None
        if self._initialization_time:
            uptime = time.time() - self._initialization_time

        return {
            "state": self._state.value,
            "enabled": self.enabled,
            "action_count": self._action_count,
            "blocked_count": self._blocked_count,
            "error_count": self._error_count,
            "uptime_seconds": uptime,
        }

    def _transition_state(self, new_state: PluginState) -> None:
        """Transition to a new state and emit event."""
        old_state = self._state
        self._state = new_state

        logger.info(f"Plugin state transition: {old_state.value} -> {new_state.value}")

        # Emit state change event
        self._emit_event(
            EventType.STATE_CHANGED,
            {"old_state": old_state.value, "new_state": new_state.value},
        )

    def _emit_event(self, event_type: EventType, data: dict[str, Any]) -> None:
        """Emit an event to registered handlers and observability system."""
        event_data = {
            "plugin_name": self.name,
            "plugin_version": self.version,
            "event_type": event_type.value,
            "timestamp": time.time(),
            **data,
        }

        # Send to observability system
        with self._observability.tracer.start_span(
            f"plugin.{self.name}.{event_type.value}", **event_data
        ):
            # Notify registered handlers
            if event_type in self._event_handlers:
                for handler in self._event_handlers[event_type]:
                    try:
                        handler(event_data)
                    except Exception as e:
                        logger.error(
                            f"Error in event handler for {event_type.value}: {e}"
                        )
                        self._error_count += 1

        logger.debug(f"Event emitted: {event_type.value} - {event_data}")

    def register_event_handler(
        self, event_type: EventType, handler: Callable[[dict[str, Any]], None]
    ) -> None:
        """Register an event handler for specific event type."""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
        logger.debug(f"Registered handler for {event_type.value}")

    def unregister_event_handler(
        self, event_type: EventType, handler: Callable[[dict[str, Any]], None]
    ) -> bool:
        """Unregister an event handler."""
        if event_type in self._event_handlers:
            try:
                self._event_handlers[event_type].remove(handler)
                logger.debug(f"Unregistered handler for {event_type.value}")
                return True
            except ValueError:
                pass
        return False

    def initialize(self, context: dict[str, Any] | None = None) -> bool:
        """
        Initialize plugin with Four Laws validation.

        Args:
            context: Initialization context with optional keys:
                - is_user_order: bool - Whether this is a direct user request
                - requires_explicit_order: bool - Whether action requires user approval
                - endangers_human: bool - Whether action might endanger humans
                - threatens_survival: bool - Whether action threatens AI survival
                - prevents_autonomy: bool - Whether action prevents autonomy
                - lacks_transparency: bool - Whether action lacks transparency

        Returns:
            True if initialization successful, False otherwise
        """
        self._transition_state(PluginState.INITIALIZING)

        context = context or {}

        # Validate against Four Laws
        with self._observability.profiler.measure("plugin.four_laws_validation"):
            allowed, reason = FourLaws.validate_action(
                "Initialize marketplace sample plugin",
                context,
            )

        logger.info(f"Four Laws validation: {reason}")

        if not allowed:
            self._blocked_count += 1
            self._emit_event(
                EventType.ACTION_BLOCKED,
                {"reason": reason, "context": context},
            )
            self._transition_state(PluginState.ERROR)
            return False

        # Additional plugin-specific validation
        if context.get("requires_explicit_order") and not context.get("is_user_order"):
            self._blocked_count += 1
            reason = "Explicit user order required but not provided"
            logger.warning(reason)
            self._emit_event(
                EventType.ACTION_BLOCKED,
                {"reason": reason, "context": context},
            )
            self._transition_state(PluginState.ERROR)
            return False

        # Initialization successful
        self.enabled = True
        self._initialization_time = time.time()
        self._transition_state(PluginState.READY)

        self._emit_event(
            EventType.INITIALIZED,
            {"context": context},
        )

        return True

    def enable(self) -> bool:
        """Enable the plugin."""
        if self._state not in (PluginState.READY, PluginState.PAUSED):
            logger.warning(
                f"Cannot enable plugin in state {self._state.value}"
            )
            return False

        self.enabled = True
        self._transition_state(PluginState.RUNNING)
        self._emit_event(EventType.ENABLED, {})
        return True

    def disable(self) -> bool:
        """Disable the plugin."""
        if self._state != PluginState.RUNNING:
            logger.warning(
                f"Cannot disable plugin in state {self._state.value}"
            )
            return False

        self.enabled = False
        self._transition_state(PluginState.PAUSED)
        self._emit_event(EventType.DISABLED, {})
        return True

    def shutdown(self) -> None:
        """Shutdown the plugin and cleanup resources."""
        logger.info(f"Shutting down plugin {self.name}")

        self.enabled = False
        self._transition_state(PluginState.SHUTDOWN)

        # Clear event handlers
        self._event_handlers.clear()

        # Log final metrics
        logger.info(f"Plugin {self.name} final metrics: {self.metrics}")

    def validate_action(self, action: str, context: dict[str, Any]) -> tuple[bool, str]:
        """
        Validate an action against Four Laws.

        Args:
            action: Action description
            context: Action context

        Returns:
            Tuple of (allowed, reason)
        """
        self._action_count += 1

        with self._observability.profiler.measure("plugin.action_validation"):
            allowed, reason = FourLaws.validate_action(action, context)

        if allowed:
            self._emit_event(
                EventType.ACTION_VALIDATED,
                {"action": action, "reason": reason},
            )
        else:
            self._blocked_count += 1
            self._emit_event(
                EventType.ACTION_BLOCKED,
                {"action": action, "reason": reason, "context": context},
            )

        return allowed, reason

    def handle_error(self, error: Exception, context: dict[str, Any]) -> None:
        """Handle plugin errors."""
        self._error_count += 1
        self._transition_state(PluginState.ERROR)

        error_data = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
        }

        self._emit_event(EventType.ERROR_OCCURRED, error_data)
        logger.error(f"Plugin error: {error}", exc_info=True)


def initialize(context: dict[str, Any] | None = None) -> bool:
    """Entry point used by loaders that expect a plain function."""
    return MarketplaceSamplePlugin().initialize(context)


__all__ = ["MarketplaceSamplePlugin", "PluginState", "EventType", "initialize"]
