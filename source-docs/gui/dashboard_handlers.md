# DashboardHandlers [[src/app/gui/dashboard_handlers.py]] - Governance-Routed Event Handlers

**Module:** `src/app/gui/dashboard_handlers.py`  
**Lines of Code:** 520  
**Type:** PyQt6 Event Handler Mixin Class  
**Last Updated:** 2025-01-20

---

## Overview

`DashboardHandlers` [[src/app/gui/dashboard_handlers.py]] implements governance-routed event handlers for dashboard features, transitioning from direct core system calls to adapter-based governance pipeline. It provides fallback mechanisms for legacy compatibility while enforcing the new Tier-1 governance architecture.

### Design Philosophy

- **Governance First:** All operations routed through DesktopAdapter
- **Fallback Safety:** Graceful degradation to direct calls if governance fails
- **Input Validation:** Sanitize and validate all user inputs before processing
- **Error Handling:** Comprehensive logging and user feedback

---

## Governance Architecture

### Old Pattern (Deprecated)

```python
# DEPRECATED: Direct core imports
from app.core.learning_paths import LearningRequestManager
from app.core.data_analysis import DataAnalyzer
from app.core.security_resources import SecurityResources

# DEPRECATED: Direct method calls
path = learning_manager.generate_path(interest, skill_level)
data = data_analyzer.load_data(file_path)
resources = security_manager.get_resources_by_category(category)
```

### New Pattern (Current)

```python
# NEW: Governance-routed adapter pattern
from app.interfaces.desktop.integration import get_desktop_adapter

adapter = get_desktop_adapter()
response = adapter.execute(
    "learning.generate_path",
    {
        "interest": interest,
        "skill_level": skill_level,
        "user": current_user,
    }
)

if response["status"] == "success":
    result = response["result"]
else:
    error_msg = response.get("error", "Unknown error")
    # Handle error or fallback
```

### Governance Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│  DashboardHandlers (GUI Layer)                                │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Event Handler (e.g., generate_learning_path)         │   │
│  │                                                       │   │
│  │ 1. Sanitize & validate inputs                        │   │
│  │ 2. Build request parameters                          │   │
│  └───────────────────┬──────────────────────────────────┘   │
│                      │                                       │
└──────────────────────┼───────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  DesktopAdapter (Interface Layer)                             │
│                                                               │
│  adapter.execute("learning.generate_path", params)            │
│                      │                                        │
└──────────────────────┼────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  Router (Governance Layer)                                    │
│                                                               │
│  router.route_request("learning.generate_path", params)       │
│                      │                                        │
│  1. Permission checks (Tier validation)                      │
│  2. Audit logging                                            │
│  3. Rate limiting                                            │
│  4. Context injection                                        │
└──────────────────────┼────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  Core Systems (Business Logic)                                │
│                                                               │
│  LearningRequestManager.generate_path()                       │
│  DataAnalyzer.load_data()                                     │
│  SecurityResources.get_resources()                            │
│                      │                                        │
└──────────────────────┼────────────────────────────────────────┘
                       ▼
                   [Result]
                       │
┌──────────────────────┼────────────────────────────────────────┐
│  Response Path (Reverse)                                      │
│                                                               │
│  Core → Router → Adapter → Handler → UI Update               │
└──────────────────────────────────────────────────────────────┘
```

---

## Implemented Handlers

### Learning Path Generation

#### `generate_learning_path(self)`

**Purpose:** Generate AI learning path based on user interest and skill level.

**UI Inputs:**
- `self.interest_input.text()` - Learning topic (1-200 chars)
- `self.skill_level.currentText()` - Skill level (beginner, intermediate, advanced)

**Governance Route:** `"learning.generate_path"`

**Implementation:**
```python
def generate_learning_path(self):
    """Generate a learning path based on user input (governance-routed)"""
    # 1. Sanitize and validate interest input
    interest = sanitize_input(self.interest_input.text(), max_length=200)
    if not validate_length(interest, min_len=1, max_len=200):
        QMessageBox.warning(
            self,
            "Input Error",
            "Interest must be 1-200 characters"
        )
        return
    
    skill_level = self.skill_level.currentText().lower()
    
    if interest:
        try:
            # 2. Execute through governance adapter
            adapter = get_desktop_adapter()
            response = adapter.execute(
                "learning.generate_path",
                {
                    "interest": interest,
                    "skill_level": skill_level,
                    "user": self.user_manager.current_user,
                }
            )
            
            # 3. Handle success
            if response["status"] == "success":
                path = response["result"]["path"]
                self.learning_path_display.setText(path)
            else:
                # 4. Handle governance error
                error_msg = response.get("error", "Unknown error")
                logger.error(f"Learning path generation failed: {error_msg}")
                self.learning_path_display.setText(f"Error: {error_msg}")
        
        except Exception as e:
            # 5. Fallback to direct call (legacy compatibility)
            logger.error(f"Failed to generate learning path: {e}")
            path = self.learning_manager.generate_path(interest, skill_level)
            self.learning_path_display.setText(path)
            self.learning_manager.save_path(
                self.user_manager.current_user, interest, path
            )
```

**Success Response:**
```python
{
    "status": "success",
    "result": {
        "path": "# Learning Path: Python\n\n1. Variables...\n2. Functions...",
        "duration": "4-6 weeks",
        "resources": [...]
    }
}
```

**Error Response:**
```python
{
    "status": "error",
    "error": "OpenAI API rate limit exceeded",
    "code": "RATE_LIMIT_ERROR"
}
```

---

### Data File Loading & Analysis

#### `load_data_file(self)`

**Purpose:** Load CSV/XLSX/JSON data file for analysis.

**UI Inputs:**
- File dialog selection (CSV, XLSX, JSON)

**Governance Route:** `"data.load_file"`

**Implementation:**
```python
def load_data_file(self):
    """Load a data file for analysis (governance-routed)"""
    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Select Data File",
        "",
        "Data Files (*.csv *.xlsx *.json);;All Files (*.*)",
    )
    
    if file_path:
        try:
            adapter = get_desktop_adapter()
            response = adapter.execute(
                "data.load_file",
                {
                    "file_path": file_path,
                    "user": self.user_manager.current_user,
                }
            )
            
            if response["status"] == "success":
                columns = response["result"]["columns"]
                self.column_selector.clear()
                self.column_selector.addItems(columns)
                self.show_basic_stats()
            else:
                error_msg = response.get("error", "Failed to load file")
                QMessageBox.warning(self, "Error", error_msg)
        
        except Exception as e:
            logger.error(f"Failed to load data file through governance: {e}")
            # Fallback to direct call
            if self.data_analyzer.load_data(file_path):
                self.column_selector.clear()
                self.column_selector.addItems(self.data_analyzer.data.columns)
                self.show_basic_stats()
```

#### `show_basic_stats(self)`

**Purpose:** Display summary statistics for loaded data.

**Governance Route:** `"data.get_stats"`

**Implementation:**
```python
def show_basic_stats(self):
    """Show basic statistical analysis (governance-routed)"""
    try:
        adapter = get_desktop_adapter()
        response = adapter.execute(
            "data.get_stats",
            {
                "user": self.user_manager.current_user,
            }
        )
        
        if response["status"] == "success":
            stats = response["result"]["stats"]
            self.analysis_display.setText(str(stats))
        else:
            logger.warning(f"Stats retrieval failed: {response.get('error')}")
            # Fallback to direct call
            stats = self.data_analyzer.get_summary_stats()
            self.analysis_display.setText(str(stats))
    
    except Exception as e:
        logger.error(f"Failed to get stats through governance: {e}")
        # Fallback to direct call
        stats = self.data_analyzer.get_summary_stats()
        self.analysis_display.setText(str(stats))
```

**Stats Display Format:**
```
Column: age
  count: 1000
  mean: 34.5
  std: 12.3
  min: 18
  max: 85
  25%: 26
  50%: 33
  75%: 42
```

---

### Security Resources Management

#### `update_security_resources(self)`

**Purpose:** Fetch GitHub security repositories by category.

**UI Inputs:**
- `self.security_category.currentText()` - Category (CTF, Exploit, Tools, etc.)

**Governance Route:** `"security.get_resources"`

**Implementation:**
```python
def update_security_resources(self):
    """Update the security resources list (governance-routed)"""
    category = self.security_category.currentText()
    
    try:
        adapter = get_desktop_adapter()
        response = adapter.execute(
            "security.get_resources",
            {
                "category": category,
                "user": self.user_manager.current_user,
            }
        )
        
        if response["status"] == "success":
            resources = response["result"]["resources"]
            self.resources_list.clear()
            for resource in resources:
                self.resources_list.addItem(
                    f"{resource['name']} ({resource['repo']})"
                )
        else:
            logger.warning(f"Security resources retrieval failed: {response.get('error')}")
            # Fallback to direct call
            resources = self.security_manager.get_resources_by_category(category)
            self.resources_list.clear()
            for resource in resources:
                self.resources_list.addItem(
                    f"{resource['name']} ({resource['repo']})"
                )
    
    except Exception as e:
        logger.error(f"Failed to get security resources through governance: {e}")
        # Fallback to direct call
        resources = self.security_manager.get_resources_by_category(category)
        self.resources_list.clear()
        for resource in resources:
            self.resources_list.addItem(
                f"{resource['name']} ({resource['repo']})"
            )
```

#### `add_security_favorite(self)`

**Purpose:** Add GitHub repo to user favorites.

**Governance Route:** `"security.add_favorite"`

**Implementation:**
```python
def add_security_favorite(self):
    """Add current security resource to favorites (governance-routed)"""
    if self.resources_list.currentItem():
        text = self.resources_list.currentItem().text()
        repo = text[text.find("(") + 1 : text.find(")")]
        
        try:
            adapter = get_desktop_adapter()
            response = adapter.execute(
                "security.add_favorite",
                {
                    "repo": repo,
                    "user": self.user_manager.current_user,
                }
            )
            
            if response["status"] == "success":
                QMessageBox.information(self, "Success", "Added to favorites")
            else:
                error_msg = response.get("error", "Failed to add favorite")
                QMessageBox.warning(self, "Error", error_msg)
        
        except Exception as e:
            logger.error(f"Failed to add favorite through governance: {e}")
            # Fallback to direct call
            self.security_manager.save_favorite(self.user_manager.current_user, repo)
            QMessageBox.information(self, "Success", "Added to favorites")
```

---

### Location Tracking Management

#### `toggle_location_tracking(self)`

**Purpose:** Start/stop IP-based location tracking.

**Governance Routes:** `"location.start"`, `"location.stop"`

**Implementation:**
```python
def toggle_location_tracking(self):
    """Toggle location tracking on/off (governance-routed)"""
    try:
        adapter = get_desktop_adapter()
        action = "location.start" if not self.location_tracker.active else "location.stop"
        
        response = adapter.execute(
            action,
            {
                "user": self.user_manager.current_user,
            }
        )
        
        if response["status"] == "success":
            self.location_tracker.active = response["result"]["active"]
            if self.location_tracker.active:
                self.location_toggle.setText("Stop Location Tracking")
                self.location_timer.start(300000)  # Update every 5 minutes
                self.update_location()
            else:
                self.location_toggle.setText("Start Location Tracking")
                self.location_timer.stop()
        else:
            logger.warning(f"Location tracking toggle failed: {response.get('error')}")
            # Fallback to direct control
            self._toggle_location_tracking_direct()
    
    except Exception as e:
        logger.error(f"Failed to toggle location tracking through governance: {e}")
        # Fallback to direct control
        self._toggle_location_tracking_direct()
```

#### `update_location(self)`

**Purpose:** Fetch current location from IP geolocation API.

**Governance Route:** `"location.update"`

**Implementation:**
```python
def update_location(self):
    """Update current location (governance-routed)"""
    if self.location_tracker.active:
        try:
            adapter = get_desktop_adapter()
            response = adapter.execute(
                "location.update",
                {
                    "user": self.user_manager.current_user,
                }
            )
            
            if response["status"] == "success":
                self.update_location_display()
            else:
                logger.warning(f"Location update failed: {response.get('error')}")
                # Fallback to direct call
                self._update_location_direct()
        
        except Exception as e:
            logger.error(f"Failed to update location through governance: {e}")
            # Fallback to direct call
            self._update_location_direct()
```

#### `clear_location_history(self)`

**Purpose:** Delete all stored location history.

**Governance Route:** `"location.clear_history"`

**Implementation:**
```python
def clear_location_history(self):
    """Clear the location history (governance-routed)"""
    if (
        QMessageBox.question(
            self,
            "Confirm Clear",
            "Are you sure you want to clear your location history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        == QMessageBox.StandardButton.Yes
    ):
        try:
            adapter = get_desktop_adapter()
            response = adapter.execute(
                "location.clear_history",
                {
                    "user": self.user_manager.current_user,
                }
            )
            
            if response["status"] == "success":
                self.location_history.clear()
            else:
                error_msg = response.get("error", "Failed to clear history")
                QMessageBox.warning(self, "Error", error_msg)
        
        except Exception as e:
            logger.error(f"Failed to clear location history through governance: {e}")
            # Fallback to direct call
            self.location_tracker.clear_location_history(self.user_manager.current_user)
            self.location_history.clear()
```

---

### Emergency Alert System

#### `save_emergency_contacts(self)`

**Purpose:** Save emergency contact email addresses.

**UI Inputs:**
- `self.contacts_input.text()` - Comma-separated email list

**Governance Route:** `"emergency.save_contacts"`

**Validation:**
```python
# Sanitize and validate contact emails
contacts_raw = sanitize_input(self.contacts_input.text(), max_length=500)
contacts = [email.strip() for email in contacts_raw.split(",")]

# Validate each email
invalid_emails = []
valid_contacts = []
for email in contacts:
    if email:  # Skip empty strings
        if validate_email(email):
            valid_contacts.append(email)
        else:
            invalid_emails.append(email)

if invalid_emails:
    QMessageBox.warning(
        self,
        "Invalid Email",
        f"Invalid email addresses: {', '.join(invalid_emails)}"
    )
    return
```

**Implementation:**
```python
def save_emergency_contacts(self):
    """Save emergency contact information (governance-routed)"""
    # ... (validation code above)
    
    try:
        adapter = get_desktop_adapter()
        response = adapter.execute(
            "emergency.save_contacts",
            {
                "contacts": valid_contacts,
                "user": self.user_manager.current_user,
            }
        )
        
        if response["status"] == "success":
            QMessageBox.information(self, "Success", "Emergency contacts saved")
        else:
            error_msg = response.get("error", "Failed to save contacts")
            QMessageBox.warning(self, "Error", error_msg)
    
    except Exception as e:
        logger.error(f"Failed to save emergency contacts through governance: {e}")
        # Fallback to direct call
        self.emergency_alert.add_emergency_contact(
            self.user_manager.current_user, {"emails": valid_contacts}
        )
        QMessageBox.information(self, "Success", "Emergency contacts saved")
```

#### `send_emergency_alert(self)`

**Purpose:** Send emergency alert email to all contacts.

**UI Inputs:**
- `self.emergency_message.toPlainText()` - Alert message (1-1000 chars)

**Governance Route:** `"emergency.send_alert"`

**Validation:**
```python
# Sanitize and validate emergency message
message = sanitize_input(
    self.emergency_message.toPlainText(),
    max_length=1000
)
if not validate_length(message, min_len=1, max_len=1000):
    QMessageBox.warning(
        self,
        "Input Error",
        "Emergency message must be 1-1000 characters"
    )
    return
```

**Implementation:**
```python
def send_emergency_alert(self):
    """Send emergency alert (governance-routed)"""
    if (
        QMessageBox.question(
            self,
            "Confirm Alert",
            "Are you sure you want to send an emergency alert?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        == QMessageBox.StandardButton.Yes
    ):
        try:
            # Get latest location
            history = self.location_tracker.get_location_history(
                self.user_manager.current_user
            )
            location = history[-1] if history else None
            
            # Sanitize and validate emergency message
            message = sanitize_input(
                self.emergency_message.toPlainText(),
                max_length=1000
            )
            # ... (validation code above)
            
            adapter = get_desktop_adapter()
            response = adapter.execute(
                "emergency.send_alert",
                {
                    "location": location,
                    "message": message,
                    "user": self.user_manager.current_user,
                }
            )
            
            if response["status"] == "success":
                QMessageBox.information(
                    self, "Alert Sent", "Emergency alert was sent successfully"
                )
                self.update_alert_history()
            else:
                error_msg = response.get("error", "Failed to send alert")
                QMessageBox.warning(
                    self, "Alert Failed", f"Failed to send alert: {error_msg}"
                )
        
        except Exception as e:
            logger.error(f"Failed to send emergency alert through governance: {e}")
            # Fallback to direct call
            self._send_emergency_alert_direct()
```

---

## Fallback Mechanism Pattern

### Design Rationale

**Why Fallbacks?**
1. **Legacy Compatibility:** Support systems without full governance implementation
2. **Graceful Degradation:** Continue functioning if governance layer fails
3. **Transition Period:** Allow gradual migration from old to new architecture
4. **Testing:** Enable testing of UI without full governance stack

### Fallback Implementation Pattern

```python
def handler_method(self):
    """Standard handler with fallback pattern."""
    try:
        # 1. Attempt governance route
        adapter = get_desktop_adapter()
        response = adapter.execute("system.action", params)
        
        if response["status"] == "success":
            # 2. Handle success
            result = response["result"]
            self.update_ui(result)
        else:
            # 3. Log governance error
            logger.warning(f"Governance failed: {response.get('error')}")
            # 4. Fallback to direct call
            self._fallback_direct_call()
    
    except Exception as e:
        # 5. Log exception
        logger.error(f"Governance exception: {e}")
        # 6. Fallback to direct call
        self._fallback_direct_call()

def _fallback_direct_call(self):
    """Legacy direct call (no governance)."""
    result = self.legacy_system.direct_method()
    self.update_ui(result)
```

### Fallback Methods Reference

| Handler | Fallback Method | Purpose |
|---------|----------------|---------|
| `toggle_location_tracking()` | `_toggle_location_tracking_direct()` | Direct tracker control |
| `update_location()` | `_update_location_direct()` | Direct IP geolocation |
| `send_emergency_alert()` | `_send_emergency_alert_direct()` | Direct email sending |

---

## Input Validation Patterns

### Sanitization Functions

```python
from app.security.data_validation import (
    sanitize_input,
    validate_length,
    validate_email
)

# Sanitize text input
sanitized = sanitize_input(user_input, max_length=200)

# Validate length
if not validate_length(sanitized, min_len=1, max_len=200):
    QMessageBox.warning(self, "Error", "Input must be 1-200 characters")
    return

# Validate email
if not validate_email(email_input):
    QMessageBox.warning(self, "Error", "Invalid email format")
    return
```

### Common Validation Scenarios

**Learning Path Interest:**
```python
interest = sanitize_input(self.interest_input.text(), max_length=200)
if not validate_length(interest, min_len=1, max_len=200):
    QMessageBox.warning(self, "Input Error", "Interest must be 1-200 characters")
    return
```

**Emergency Message:**
```python
message = sanitize_input(
    self.emergency_message.toPlainText(),
    max_length=1000
)
if not validate_length(message, min_len=1, max_len=1000):
    QMessageBox.warning(self, "Input Error", "Message must be 1-1000 characters")
    return
```

**Email List:**
```python
contacts_raw = sanitize_input(self.contacts_input.text(), max_length=500)
contacts = [email.strip() for email in contacts_raw.split(",")]

invalid_emails = []
valid_contacts = []
for email in contacts:
    if email:
        if validate_email(email):
            valid_contacts.append(email)
        else:
            invalid_emails.append(email)

if invalid_emails:
    QMessageBox.warning(self, "Invalid Email", f"Invalid: {', '.join(invalid_emails)}")
    return
```

---

## Error Handling Strategy

### Logging Levels

```python
# ERROR: Governance failures that trigger fallback
logger.error(f"Failed to generate learning path through governance: {e}")

# WARNING: Governance errors with successful fallback
logger.warning(f"Stats retrieval failed: {response.get('error')}")

# INFO: Successful operations
logger.info(f"Emergency contacts saved for user {current_user}")
```

### User Feedback

```python
# Success notification
QMessageBox.information(self, "Success", "Operation completed")

# Warning (non-critical)
QMessageBox.warning(self, "Warning", "Using fallback method")

# Error (critical failure)
QMessageBox.critical(self, "Error", "Operation failed: {error}")
```

---

## Testing Considerations

### Unit Tests

```python
def test_learning_path_governance():
    """Test learning path generation through governance."""
    handler = DashboardHandlers()
    handler.interest_input.setText("Python")
    handler.skill_level.setCurrentText("Beginner")
    
    handler.generate_learning_path()
    
    # Verify governance adapter called
    assert mock_adapter.execute.called_with(
        "learning.generate_path",
        {"interest": "Python", "skill_level": "beginner"}
    )

def test_learning_path_fallback():
    """Test fallback when governance fails."""
    handler = DashboardHandlers()
    
    # Mock governance failure
    mock_adapter.execute.side_effect = Exception("Governance down")
    
    handler.generate_learning_path()
    
    # Verify fallback called
    assert handler.learning_manager.generate_path.called
```

---

## Cross-References

- **Governance Architecture:** See `desktop_integration.md`
- **Security Validation:** See `data_validation.md`
- **Core Systems:** See `learning_paths.md`, `data_analysis.md`, `security_resources.md`
- **Dashboard UI:** See `leather_book_dashboard.md`

---

**Document Status:** ✅ Complete  
**Code Coverage:** 100% (all handlers documented)  
**Last Reviewed:** 2025-01-20 by AGENT-032


---


---

## 📚 Related Documentation

### Cross-References

- [[relationships/gui/03_HANDLER_RELATIONSHIPS.md|03 Handler Relationships]]

## 🔗 Source Code References

This documentation references the following GUI source files:

- [[src/app/gui/dashboard_handlers.py]] - Implementation file
