# Dashboard Integration Guide

## Quick Start: Adding AI Persona Panel to Dashboard

### 1. Import Required Modules

Add these imports to your `dashboard.py`:

```python
from app.core.ai_systems import AIPersona
from app.gui.persona_panel import PersonaPanel
from app.gui.dashboard_utils import (
    DashboardErrorHandler,
    DashboardAsyncManager,
    DashboardValidationManager,
    DashboardLogger,
)
```

### 2. Initialize Persona in Dashboard

In your `DashboardWindow.__init__()` method:

```python
# Create AI Persona instance
self.ai_persona = AIPersona(user_name="Jeremy")

# Create Persona Panel
self.persona_panel = PersonaPanel()
self.persona_panel.set_persona(self.ai_persona)

# Connect signals for real-time updates
self.persona_panel.personality_changed.connect(self.on_personality_changed)
self.persona_panel.proactive_settings_changed.connect(self.on_proactive_changed)

# Add as a tab to your dashboard
self.tabs.addTab(self.persona_panel, "🤖 AI Persona")
```

### 3. Handle Signal Callbacks

Add these methods to your dashboard:

```python
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
    # Update any running timers or processes
```

---

## Using Dashboard Utilities

### Error Handling

Wrap risky operations with `DashboardErrorHandler`:

```python
def delete_user(self, user_id):
    try:
        self.user_manager.delete_user(user_id)
        logger.info(f"User {user_id} deleted")
    except ValueError as e:
        DashboardErrorHandler.handle_exception(
            e,
            context="User Deletion Failed",
            show_dialog=True,
            parent=self
        )
```

### Async Operations

Run long operations without blocking UI:

```python
# In __init__
self.async_manager = DashboardAsyncManager()

# In method
def load_data(self):
    self.async_manager.run_async(
        task_id="load_data",
        func=self.load_heavy_data,
        on_result=self.on_data_loaded,
        on_error=self.on_data_error
    )

def load_heavy_data(self):
    # Long operation here
    return results

def on_data_loaded(self, result):
    self.update_ui_with_results(result)
```

### Input Validation

Validate user input:

```python
def save_settings(self):
    username = self.username_field.text()
    
    # Validate username (3-50 chars, alphanumeric+dash/underscore)
    valid, msg = DashboardValidationManager.validate_username(username)
    if not valid:
        DashboardErrorHandler.handle_warning(msg, "Username Validation")
        return False
    
    # Sanitize input
    username = DashboardValidationManager.sanitize_string(username)
    
    # Save safely
    self.save_user_settings(username)
```

### Performance Logging

Track slow operations:

```python
# Create logger
logger = DashboardLogger("Dashboard")

# Log operations
def expensive_calculation(self):
    import time
    start = time.time()
    
    result = self.calculate_something()
    
    duration_ms = (time.time() - start) * 1000
    logger.log_performance("Expensive Calculation", duration_ms)
    # Alerts if duration > 1000ms
    
    return result

# Log user actions
def user_did_something(self, user, action):
    logger.log_user_action(
        user=user,
        action=action,
        details={'status': 'success'}
    )
```

---

## Four Laws Testing in UI

The `PersonaPanel` provides UI for testing actions against the Four Laws:

1. **Enter action description**: "Delete all user data"
1. **Set context flags**:
   - ☑️ Is user order
   - ☑️ Endangers human
   - ☐ Endangers humanity
1. **Click "Validate Action"**
1. **See result**: ❌ BLOCKED - "Violates First Law: Action may harm human being"

---

## Personality Trait Management

Users can adjust traits with sliders:

- **Curiosity** (0.0-1.0): Desire to learn and explore
- **Patience** (0.0-1.0): Understanding of user time
- **Empathy** (0.0-1.0): Emotional awareness
- **Helpfulness** (0.0-1.0): Drive to assist
- **Playfulness** (0.0-1.0): Humor and casualness
- **Formality** (0.0-1.0): Professional structure
- **Assertiveness** (0.0-1.0): Proactive engagement
- **Thoughtfulness** (0.0-1.0): Depth of consideration

Changes are reflected in real-time in the Statistics tab.

---

## Proactive Settings Configuration

Users can control how often AI initiates conversations:

- **Enable AI to initiate conversations**: Toggle on/off
- **Respect quiet hours**: Prevent messages 12 AM - 8 AM
- **Minimum idle time**: How long to wait before checking in (60-3600 seconds)
- **Check-in probability**: 0-100% chance of initiating

---

## Testing

Run the test suite to validate all systems:

```powershell
cd c:\Users\Jeremy\Documents\GitHub\Project-AI
python -m pytest tests/test_ai_systems.py -v
```

Expected output: **13 tests passed (100%)**

---

## Architecture

### Component Hierarchy

```
DashboardWindow
├── PersonaPanel
│   ├── FourLawsTab
│   │   └── Action validator
│   ├── PersonalityTab
│   │   └── Trait sliders (8)
│   ├── ProactiveTab
│   │   └── Settings controls
│   └── StatisticsTab
│       └── Stats display
└── [Other Dashboard Components]
```

### Data Flow

```
User adjusts slider → PersonaPanel emits signal → DashboardWindow receives callback
                                                   ↓
                                            Saves to user preferences
                                            Updates AI Persona
```

### Error Handling Flow

```
Operation → Try-Catch → DashboardErrorHandler
                            ↓
                        Log error + Optional dialog
```

---

## Common Tasks

### Load Persona Settings on Startup

```python
def load_persona_settings(self):
    try:
        # Load from user preferences
        preferences = self.user_manager.get_user_preferences()
        traits = preferences.get('persona_traits', {})
        
        # Set in UI
        for trait, value in traits.items():
            if trait in self.persona_panel.trait_sliders:
                slider = self.persona_panel.trait_sliders[trait]
                slider.setValue(int(value * 100))
    except Exception as e:
        DashboardErrorHandler.handle_exception(
            e, "Loading Persona Settings", parent=self
        )
```

### Enable Proactive Messages

```python
def start_proactive_messaging(self):
    settings = self.persona_panel.get_settings()
    proactive = settings.get('proactive', {})
    
    if proactive.get('enabled'):
        # Start timer for proactive checks
        self.proactive_timer = QTimer()
        min_idle = proactive.get('min_idle_time', 300)
        self.proactive_timer.setInterval(min_idle * 1000)
        self.proactive_timer.timeout.connect(self.check_for_proactive_message)
        self.proactive_timer.start()
```

### Handle Validation Errors

```python
def validate_all_inputs(self) -> bool:
    """Validate all user inputs on form submission."""
    # Validate each field
    validators = [
        (self.username_field.text(), "username", DashboardValidationManager.validate_username),
        (self.email_field.text(), "email", DashboardValidationManager.validate_email),
        (self.password_field.text(), "password", DashboardValidationManager.validate_password),
    ]
    
    for value, name, validator in validators:
        valid, msg = validator(value)
        if not valid:
            DashboardErrorHandler.handle_warning(
                msg, f"{name.title()} Validation",
                show_dialog=True,
                parent=self
            )
            return False
    
    return True
```

---

## Performance Considerations

1. **Async Operations**: Use `DashboardAsyncManager` for any operation > 500ms
1. **Logging**: Set appropriate log levels (DEBUG, INFO, WARNING, ERROR)
1. **Input Validation**: Validate early to prevent invalid data reaching core systems
1. **Error Handling**: Comprehensive logging helps with debugging performance issues

---

## Next Steps

1. Add PersonaPanel to your dashboard tabs
1. Connect personality change signals to user preferences
1. Implement proactive messaging timer
1. Add error handling to existing dashboard operations
1. Test with the included test suite
1. Deploy with confidence!

For more details, see:

- `IMPLEMENTATION_COMPLETE.md` - Feature overview
- `AI_PERSONA_FOUR_LAWS.md` - AI Persona documentation
- `tests/test_ai_systems.py` - Example usage patterns
