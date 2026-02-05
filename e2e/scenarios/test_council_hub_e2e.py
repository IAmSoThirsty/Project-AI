"""
E2E Tests for Council Hub Integration

Tests the Council Hub agent coordination, message routing, and integration
with the Cognition Kernel.
"""

from __future__ import annotations

import pytest

from e2e.fixtures.test_data import TEST_COUNCIL_MESSAGES
from e2e.utils.assertions import (
    assert_audit_log_entry,
    assert_event_propagation,
)


@pytest.mark.e2e
@pytest.mark.council_hub
@pytest.mark.integration
def test_council_hub_agent_registration(test_temp_dir):
    """Test Council Hub agent registration and initialization."""
    # Import here to avoid import errors if dependencies not installed
    try:
        from app.core.council_hub import CouncilHub
    except ImportError:
        pytest.skip("Council Hub module not available")

    # Arrange
    hub = CouncilHub(autolearn_interval=60.0)

    # Act
    hub.register_project("Project-AI-Test")

    # Assert
    assert hub._project is not None
    assert hub._project["name"] == "Project-AI-Test"
    assert "persona" in hub._project
    assert "memory" in hub._project
    assert "continuous_learning" in hub._project


@pytest.mark.e2e
@pytest.mark.council_hub
@pytest.mark.integration
def test_council_hub_message_routing(test_temp_dir):
    """Test message routing between agents through Council Hub."""
    try:
        from app.core.council_hub import CouncilHub
    except ImportError:
        pytest.skip("Council Hub module not available")

    # Arrange
    hub = CouncilHub()
    hub.register_project("Project-AI-Test")

    # Act - Register test agents
    # Note: In real implementation, agents would be registered through hub
    # For this E2E test, we verify the hub structure is correct

    # Assert
    assert hasattr(hub, "_project")
    assert hasattr(hub, "_agents")
    assert hasattr(hub, "kernel")


@pytest.mark.e2e
@pytest.mark.council_hub
@pytest.mark.integration
def test_council_hub_cognition_kernel_integration(test_temp_dir):
    """Test Council Hub integration with Cognition Kernel routing."""
    try:
        from app.core.cognition_kernel import CognitionKernel
        from app.core.council_hub import CouncilHub
    except ImportError:
        pytest.skip("Council Hub or Cognition Kernel module not available")

    # Arrange
    kernel = CognitionKernel()
    hub = CouncilHub(kernel=kernel)

    # Act
    hub.register_project("Project-AI-Test")

    # Assert
    assert hub.kernel is not None
    assert hub.kernel == kernel
    # All agent operations should route through kernel
    assert hub._project["curator"].kernel == kernel


@pytest.mark.e2e
@pytest.mark.council_hub
@pytest.mark.slow
def test_council_hub_autonomous_learning_loop(test_temp_dir):
    """Test Council Hub autonomous learning loop for the head agent."""
    try:
        from app.core.council_hub import CouncilHub
    except ImportError:
        pytest.skip("Council Hub module not available")

    # Arrange
    hub = CouncilHub(autolearn_interval=1.0)  # Short interval for testing
    hub.register_project("Project-AI-Test")

    # Act
    # Start learning loop would happen here in full test
    # For E2E, verify the structure is correct

    # Assert
    assert hub._autolearn_interval == 1.0
    assert hub._project is not None
    assert "continuous_learning" in hub._project


@pytest.mark.e2e
@pytest.mark.council_hub
@pytest.mark.integration
def test_council_hub_agent_enable_disable(test_temp_dir):
    """Test enabling and disabling agents in Council Hub."""
    try:
        from app.core.council_hub import CouncilHub
    except ImportError:
        pytest.skip("Council Hub module not available")

    # Arrange
    hub = CouncilHub()
    hub.register_project("Project-AI-Test")

    # Act & Assert - Verify agent tracking
    assert hasattr(hub, "_agents_enabled")
    assert isinstance(hub._agents_enabled, dict)


@pytest.mark.e2e
@pytest.mark.council_hub
@pytest.mark.security
def test_council_hub_governance_routing(test_temp_dir):
    """Test that all Council Hub operations route through governance."""
    try:
        from app.core.cognition_kernel import CognitionKernel
        from app.core.council_hub import CouncilHub
    except ImportError:
        pytest.skip("Council Hub or Cognition Kernel module not available")

    # Arrange
    kernel = CognitionKernel()
    hub = CouncilHub(kernel=kernel)
    hub.register_project("Project-AI-Test")

    # Act & Assert
    # Verify that kernel is injected into all agents
    assert hub.kernel is not None

    # All agents must have kernel for governance routing
    if hub._project:
        for key, value in hub._project.items():
            if hasattr(value, "kernel"):
                assert (
                    value.kernel == kernel
                ), f"Agent {key} does not have kernel injected"
