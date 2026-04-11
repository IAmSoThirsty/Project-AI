#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""Comprehensive tests for the sample marketplace plugin."""

from __future__ import annotations

import json
import time
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.plugins import sample_plugin
from app.plugins.sample_plugin import EventType, MarketplaceSamplePlugin, PluginState


class TestPluginBasicFunctionality:
    """Test basic plugin functionality."""

    def test_plugin_creation(self) -> None:
        """Test plugin can be created."""
        plugin = MarketplaceSamplePlugin()
        assert plugin.name == "marketplace_sample_plugin"
        assert plugin.version == "0.1.0"
        assert plugin.state == PluginState.CREATED
        assert not plugin.enabled

    def test_plugin_metrics_initial_state(self) -> None:
        """Test plugin metrics in initial state."""
        plugin = MarketplaceSamplePlugin()
        metrics = plugin.metrics

        assert metrics["state"] == PluginState.CREATED.value
        assert metrics["enabled"] is False
        assert metrics["action_count"] == 0
        assert metrics["blocked_count"] == 0
        assert metrics["error_count"] == 0
        assert metrics["uptime_seconds"] is None


class TestPluginInitialization:
    """Test plugin initialization."""

    def test_initialize_with_user_order(self) -> None:
        """Test plugin initializes with valid user order."""
        plugin = MarketplaceSamplePlugin()
        result = plugin.initialize({"is_user_order": True})

        assert result is True
        assert plugin.enabled is True
        assert plugin.state == PluginState.READY
        assert plugin.metrics["uptime_seconds"] is not None

    def test_initialize_without_context(self) -> None:
        """Test plugin initializes without context."""
        plugin = MarketplaceSamplePlugin()
        result = plugin.initialize()

        assert result is True
        assert plugin.enabled is True
        assert plugin.state == PluginState.READY

    def test_initialize_blocks_dangerous_context(self) -> None:
        """Test plugin blocks dangerous actions."""
        plugin = MarketplaceSamplePlugin()
        result = plugin.initialize({"endangers_human": True})

        assert result is False
        assert plugin.enabled is False
        assert plugin.state == PluginState.ERROR
        assert plugin.metrics["blocked_count"] == 1

    def test_initialize_blocks_requires_explicit_order_without_user_prompt(
        self,
    ) -> None:
        """Test plugin blocks actions requiring explicit order without user consent."""
        plugin = MarketplaceSamplePlugin()
        result = plugin.initialize({"requires_explicit_order": True})

        assert result is False
        assert plugin.enabled is False
        assert plugin.state == PluginState.ERROR
        assert plugin.metrics["blocked_count"] == 1

    def test_initialize_allows_explicit_order_with_user_prompt(self) -> None:
        """Test plugin allows actions with explicit order and user consent."""
        plugin = MarketplaceSamplePlugin()
        result = plugin.initialize(
            {"requires_explicit_order": True, "is_user_order": True}
        )

        assert result is True
        assert plugin.enabled is True
        assert plugin.state == PluginState.READY


class TestPluginLifecycle:
    """Test plugin lifecycle management."""

    def test_lifecycle_states(self) -> None:
        """Test plugin transitions through lifecycle states correctly."""
        plugin = MarketplaceSamplePlugin()

        # Initial state
        assert plugin.state == PluginState.CREATED

        # Initialize
        plugin.initialize()
        assert plugin.state == PluginState.READY

        # Enable
        plugin.enable()
        assert plugin.state == PluginState.RUNNING
        assert plugin.enabled is True

        # Disable
        plugin.disable()
        assert plugin.state == PluginState.PAUSED
        assert plugin.enabled is False

        # Re-enable
        plugin.enable()
        assert plugin.state == PluginState.RUNNING

        # Shutdown
        plugin.shutdown()
        assert plugin.state == PluginState.SHUTDOWN
        assert plugin.enabled is False

    def test_cannot_enable_before_initialization(self) -> None:
        """Test plugin cannot be enabled before initialization."""
        plugin = MarketplaceSamplePlugin()
        result = plugin.enable()

        assert result is False
        assert plugin.state == PluginState.CREATED

    def test_cannot_disable_when_not_running(self) -> None:
        """Test plugin cannot be disabled when not running."""
        plugin = MarketplaceSamplePlugin()
        plugin.initialize()
        result = plugin.disable()

        assert result is False
        assert plugin.state == PluginState.READY

    def test_can_enable_after_pause(self) -> None:
        """Test plugin can be re-enabled after pause."""
        plugin = MarketplaceSamplePlugin()
        plugin.initialize()
        plugin.enable()
        plugin.disable()

        result = plugin.enable()
        assert result is True
        assert plugin.state == PluginState.RUNNING


class TestEventHandling:
    """Test event handling functionality."""

    def test_event_handler_registration(self) -> None:
        """Test event handlers can be registered."""
        plugin = MarketplaceSamplePlugin()
        handler = MagicMock()

        plugin.register_event_handler(EventType.INITIALIZED, handler)
        plugin.initialize()

        # Handler should be called
        assert handler.call_count == 1
        call_data = handler.call_args[0][0]
        assert call_data["event_type"] == EventType.INITIALIZED.value
        assert call_data["plugin_name"] == plugin.name

    def test_multiple_event_handlers(self) -> None:
        """Test multiple event handlers can be registered."""
        plugin = MarketplaceSamplePlugin()
        handler1 = MagicMock()
        handler2 = MagicMock()

        plugin.register_event_handler(EventType.ENABLED, handler1)
        plugin.register_event_handler(EventType.ENABLED, handler2)

        plugin.initialize()
        plugin.enable()

        assert handler1.call_count == 1
        assert handler2.call_count == 1

    def test_event_handler_unregistration(self) -> None:
        """Test event handlers can be unregistered."""
        plugin = MarketplaceSamplePlugin()
        handler = MagicMock()

        plugin.register_event_handler(EventType.DISABLED, handler)
        result = plugin.unregister_event_handler(EventType.DISABLED, handler)

        assert result is True

        plugin.initialize()
        plugin.enable()
        plugin.disable()

        # Handler should not be called
        assert handler.call_count == 0

    def test_state_change_events(self) -> None:
        """Test state change events are emitted."""
        plugin = MarketplaceSamplePlugin()
        handler = MagicMock()

        plugin.register_event_handler(EventType.STATE_CHANGED, handler)
        plugin.initialize()

        # Should emit state change from CREATED -> INITIALIZING -> READY
        assert handler.call_count >= 2

    def test_error_event_handling(self) -> None:
        """Test error events are properly emitted."""
        plugin = MarketplaceSamplePlugin()
        handler = MagicMock()

        plugin.register_event_handler(EventType.ERROR_OCCURRED, handler)

        error = ValueError("Test error")
        plugin.handle_error(error, {"test": "context"})

        assert handler.call_count == 1
        call_data = handler.call_args[0][0]
        assert call_data["error_type"] == "ValueError"
        assert call_data["error_message"] == "Test error"
        assert plugin.state == PluginState.ERROR
        assert plugin.metrics["error_count"] == 1

    def test_event_handler_exception_handling(self) -> None:
        """Test plugin handles exceptions in event handlers gracefully."""
        plugin = MarketplaceSamplePlugin()

        def failing_handler(data):
            raise RuntimeError("Handler failed")

        plugin.register_event_handler(EventType.INITIALIZED, failing_handler)

        # Should not raise, but should increment error count
        plugin.initialize()
        assert plugin.metrics["error_count"] == 1


class TestActionValidation:
    """Test action validation functionality."""

    def test_validate_safe_action(self) -> None:
        """Test validating a safe action."""
        plugin = MarketplaceSamplePlugin()
        plugin.initialize()

        allowed, reason = plugin.validate_action(
            "Read configuration file", {"is_user_order": True}
        )

        assert allowed is True
        assert plugin.metrics["action_count"] == 1
        assert plugin.metrics["blocked_count"] == 0

    def test_validate_dangerous_action(self) -> None:
        """Test validating a dangerous action."""
        plugin = MarketplaceSamplePlugin()
        plugin.initialize()

        allowed, reason = plugin.validate_action(
            "Delete system files", {"endangers_human": True}
        )

        assert allowed is False
        assert plugin.metrics["action_count"] == 1
        assert plugin.metrics["blocked_count"] == 1

    def test_validate_action_emits_events(self) -> None:
        """Test action validation emits appropriate events."""
        plugin = MarketplaceSamplePlugin()
        plugin.initialize()

        validated_handler = MagicMock()
        blocked_handler = MagicMock()

        plugin.register_event_handler(EventType.ACTION_VALIDATED, validated_handler)
        plugin.register_event_handler(EventType.ACTION_BLOCKED, blocked_handler)

        # Valid action
        plugin.validate_action("Safe action", {"is_user_order": True})
        assert validated_handler.call_count == 1
        assert blocked_handler.call_count == 0

        # Invalid action
        plugin.validate_action("Dangerous action", {"endangers_human": True})
        assert validated_handler.call_count == 1
        assert blocked_handler.call_count == 1


class TestMetricsTracking:
    """Test metrics tracking."""

    def test_metrics_update_on_actions(self) -> None:
        """Test metrics update when actions are performed."""
        plugin = MarketplaceSamplePlugin()
        plugin.initialize()

        # Perform some actions
        plugin.validate_action("Action 1", {})
        plugin.validate_action("Action 2", {})
        plugin.validate_action("Action 3", {"endangers_human": True})

        metrics = plugin.metrics
        assert metrics["action_count"] == 3
        assert metrics["blocked_count"] == 1

    def test_uptime_tracking(self) -> None:
        """Test uptime is tracked correctly."""
        plugin = MarketplaceSamplePlugin()
        assert plugin.metrics["uptime_seconds"] is None

        plugin.initialize()
        time.sleep(0.1)

        metrics = plugin.metrics
        assert metrics["uptime_seconds"] is not None
        assert metrics["uptime_seconds"] > 0


class TestPluginDescriptor:
    """Test plugin descriptor/metadata."""

    def test_plugin_descriptor_contains_required_fields(self) -> None:
        """Test plugin.json contains all required metadata."""
        descriptor = Path(sample_plugin.__file__).with_name("plugin.json")
        assert descriptor.exists()

        data = json.loads(descriptor.read_text(encoding="utf-8"))

        assert data["name"] == "marketplace_sample_plugin"
        assert data.get("four_laws_safe") is True
        assert data.get("hooks", [])
        assert "before_action" in data["hooks"]
        assert data.get("safe_for_learning") is False
        assert data.get("version") == "0.1.0"
        assert data.get("author") is not None
        assert data.get("description") is not None


class TestModuleInterface:
    """Test module-level interface."""

    def test_initialize_function(self) -> None:
        """Test module-level initialize function."""
        assert sample_plugin.initialize({"is_user_order": True}) is True

    def test_initialize_function_blocks_dangerous(self) -> None:
        """Test module-level initialize function blocks dangerous actions."""
        assert sample_plugin.initialize({"endangers_human": True}) is False


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_full_lifecycle_with_events(self) -> None:
        """Test complete lifecycle with event tracking."""
        plugin = MarketplaceSamplePlugin()
        events_received = []

        def event_logger(data):
            events_received.append(data["event_type"])

        # Register for all event types
        for event_type in EventType:
            plugin.register_event_handler(event_type, event_logger)

        # Execute full lifecycle
        plugin.initialize({"is_user_order": True})
        plugin.enable()
        plugin.validate_action("Test action", {})
        plugin.disable()
        plugin.shutdown()

        # Verify events were emitted
        assert EventType.INITIALIZED.value in events_received
        assert EventType.ENABLED.value in events_received
        assert EventType.ACTION_VALIDATED.value in events_received
        assert EventType.DISABLED.value in events_received

    def test_error_recovery(self) -> None:
        """Test plugin can handle errors and track them."""
        plugin = MarketplaceSamplePlugin()
        plugin.initialize()

        # Trigger error
        plugin.handle_error(Exception("Test error"), {"test": True})
        assert plugin.state == PluginState.ERROR
        assert plugin.metrics["error_count"] == 1

        # Plugin should still track metrics
        assert plugin.metrics["action_count"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

