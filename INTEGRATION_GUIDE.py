"""
Quick Integration Guide for Dashboard Enhancements

This guide shows how to integrate the new AI Persona Panel and Dashboard Utilities
into your existing dashboard.
"""

import logging
import time

from app.core.ai_systems import AIPersona
from app.gui.dashboard_utils import (
    DashboardAsyncManager,
    DashboardConfiguration,
    DashboardErrorHandler,
    DashboardLogger,
    DashboardValidationManager,
)
from app.gui.persona_panel import PersonaPanel

logger = logging.getLogger(__name__)

# ============================================================================
# 1. INTEGRATING THE PERSONA PANEL INTO DASHBOARD
# ============================================================================

# In your dashboard.py, add to imports:
# from app.core.ai_systems import AIPersona
# from app.gui.persona_panel import PersonaPanel


# In DashboardWindow.__init__, after other core components:
def setup_ui(self):
    """Setup the user interface"""
    # ... existing code ...

    # Initialize AI Persona
    self.ai_persona = AIPersona(user_name="Jeremy")

    # Create Persona Panel
    self.persona_panel = PersonaPanel()
    self.persona_panel.set_persona(self.ai_persona)

    # Connect signals for real-time updates
    self.persona_panel.personality_changed.connect(self.on_personality_changed)
    self.persona_panel.proactive_settings_changed.connect(self.on_proactive_changed)

    # Add as a tab or dialog
    self.tabs.addTab(self.persona_panel, "🤖 AI Persona")

# Add event handlers:
def on_personality_changed(self, personality_traits):
    """Handle personality trait changes."""
    logger.info(f"Personality updated: {personality_traits}")
    # Save to user preferences
    self.user_manager.save_user_preferences({
        'persona_traits': personality_traits
    })

def on_proactive_changed(self, settings):
    """Handle proactive settings changes."""
    logger.info(f"Proactive settings updated: {settings}")
    # Apply settings
    if settings['enabled']:
        # Start proactive message timer
        pass
    else:
        # Stop proactive message timer
        pass


# ============================================================================
# 2. USING DASHBOARD ERROR HANDLER
# ============================================================================


# Handle exceptions gracefully:
def risky_operation(self):
    try:
        # Your operation here
        # result = perform_operation()  # Replace with your function
        result = None
        return result
    except ValueError as e:
        DashboardErrorHandler.handle_exception(
            e,
            context="Operation Failed",
            show_dialog=True,
            parent=self
        )
    except Exception as e:
        DashboardErrorHandler.handle_exception(
            e,
            context="Unexpected Error",
            show_dialog=True,
            parent=self
        )

# Validate user input:
def save_user_settings(self):
    username = self.username_input.text().strip()

    # Process valid username only
    return DashboardErrorHandler.validate_input(
        username,
        str,
        required=True,
        context="Username"
    )


# ============================================================================
# 3. RUNNING ASYNC OPERATIONS
# ============================================================================


def __init__(self):
    # ... existing code ...
    self.async_manager = DashboardAsyncManager()

def load_data_async(self):
    """Load data without blocking UI."""
    self.async_manager.run_async(
        task_id="load_data",
        func=self.load_heavy_data,
        on_result=self.on_data_loaded,
        on_error=self.on_data_error
    )

def load_heavy_data(self):
    """Simulate heavy data loading."""
    import time
    time.sleep(2)  # Heavy operation
    return {"status": "success", "data": []}

def on_data_loaded(self, result):
    """Handle loaded data."""
    logger.info(f"Data loaded: {result}")
    self.update_ui(result)

def on_data_error(self, error):
    """Handle loading error."""
    logger.error(f"Error loading data: {error}")
    DashboardErrorHandler.handle_exception(
        error,
        context="Data Loading Failed",
        show_dialog=True,
        parent=self
    )


# ============================================================================
# 4. INPUT VALIDATION
# ============================================================================


def validate_user_registration(self):
    """Validate user registration form."""
    username = self.username_field.text()
    email = self.email_field.text()
    password = self.password_field.text()

    # Validate username
    valid, msg = DashboardValidationManager.validate_username(username)
    if not valid:
        DashboardErrorHandler.handle_warning(msg, "Username", show_dialog=True)
        return False

    # Validate email
    valid, msg = DashboardValidationManager.validate_email(email)
    if not valid:
        DashboardErrorHandler.handle_warning(msg, "Email", show_dialog=True)
        return False

    # Validate password
    valid, msg = DashboardValidationManager.validate_password(password)
    if not valid:
        DashboardErrorHandler.handle_warning(msg, "Password", show_dialog=True)
        return False

    # All valid
    return True

# Sanitize user input
def save_user_comment(self):
    comment = self.comment_field.toPlainText()
    sanitized = DashboardValidationManager.sanitize_string(comment, max_length=1000)

    # Use sanitized comment
    self.user_manager.save_comment(sanitized)


# ============================================================================
# 5. PERFORMANCE LOGGING
# ============================================================================


def expensive_operation(self):
    """Track performance of expensive operations."""
    start = time.time()

    # Your operation
    # result = calculate_something_expensive()  # Replace with your function
    result = None

    duration_ms = (time.time() - start) * 1000
    logger.info(f"Expensive Calculation took {duration_ms:.2f}ms")

    return result

def user_action_performed(self, user, action):
    """Log user actions."""
    logger.info(f"User action: {user} performed {action}")


# ============================================================================
# 6. CONFIGURATION MANAGEMENT
# ============================================================================


def config_init(self):
    # ... existing code ...

    # Create or load configuration
    config = DashboardConfiguration({
        'window_width': 1600,
        'window_height': 1000,
        'theme': 'dark',
    })

    # Apply configuration
    self.setGeometry(
        config.get('window_x', 80),
        config.get('window_y', 60),
        config.get('window_width', 1400),
        config.get('window_height', 900),
    )

def save_window_state(self):
    """Save window state to configuration."""
    geom = self.geometry()
    self.config.set('window_width', geom.width())
    self.config.set('window_height', geom.height())
    self.config.set('window_x', geom.x())
    self.config.set('window_y', geom.y())


# ============================================================================
# 7. COMPLETE EXAMPLE: INTEGRATED FEATURE
# ============================================================================

class PersonaFeatureExample:
    """Complete example showing all components working together."""

    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.async_manager = DashboardAsyncManager()
        self.logger = DashboardLogger("PersonaFeature")
        self.config = DashboardConfiguration()
        self.ai_persona = AIPersona(user_name="User")

    def load_and_initialize_persona(self):
        """Load persona asynchronously with error handling."""
        self.logger.log_operation("Loading AI Persona")

        self.async_manager.run_async(
            task_id="load_persona",
            func=self._load_persona_data,
            on_result=self._on_persona_loaded,
            on_error=self._on_persona_error
        )

    def _load_persona_data(self):
        """Load persona data (potentially from file)."""
        # Simulate loading
        import time
        time.sleep(0.5)

        stats = self.ai_persona.get_statistics()
        return stats

    def _on_persona_loaded(self, result):
        """Handle persona loaded."""
        self.logger.log_operation("Persona loaded successfully", result)

        # Create and display panel
        panel = PersonaPanel()
        panel.set_persona(self.ai_persona)
        panel.personality_changed.connect(self._on_personality_changed)

        self.dashboard.tabs.addTab(panel, "🤖 AI Persona")

    def _on_persona_error(self, error):
        """Handle persona loading error."""
        self.logger.log_operation(f"Persona loading failed: {error}")

        DashboardErrorHandler.handle_exception(
            error,
            context="Failed to Load AI Persona",
            show_dialog=True,
            parent=self.dashboard
        )

    def _on_personality_changed(self, traits):
        """Handle personality change."""
        self.logger.log_user_action(
            user="User",
            action="Adjusted Personality",
            details=traits
        )

        # Save to configuration
        self.config.set('personality_traits', traits)

# Usage:
# feature = PersonaFeatureExample(dashboard_window)
# feature.load_and_initialize_persona()


# ============================================================================
# 8. TESTING THE NEW COMPONENTS
# ============================================================================

"""
# Test the new components in isolation:

from tests.test_ai_systems import TestFourLaws, TestAIPersona
import pytest

# Run persona panel tests
pytest.main([
    'tests/test_ai_systems.py::TestAIPersona',
    '-v'
])

# Or test utilities directly
from app.gui.dashboard_utils import DashboardValidationManager

# Valid username
valid, msg = DashboardValidationManager.validate_username("user123")
assert valid and msg == ""

# Invalid username (too short)
valid, msg = DashboardValidationManager.validate_username("ab")
assert not valid and "3 characters" in msg
"""

print("✅ Integration guide complete. See above for usage patterns.")
