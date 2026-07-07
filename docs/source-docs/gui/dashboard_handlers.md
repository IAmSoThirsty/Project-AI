---
title: "Dashboard Handlers - Event Handling with Governance Integration"
id: "gui-dashboard-handlers"
type: "api_reference"
version: "2.0.0"
created_date: "2026-04-20"
updated_date: "2026-04-20"
status: "production"
author: "AGENT-034"
contributors: ["Architecture Team", "GUI Team"]
category: "gui-documentation"
tags: ["pyqt6", "gui", "event-handlers", "governance", "desktop-adapter"]
technologies: ["Python 3.11+", "PyQt6", "Desktop Adapter", "Governance Pipeline"]
related_docs:
  - "gui-leather-book-dashboard"
  - "gui-dashboard-utils"
  - "desktop-integration"
  - "governance-pipeline"
description: "Event handler methods for dashboard operations, routing through governance pipeline with fallback to direct calls"
security_classification: "internal"
review_status: "peer-reviewed"
audience: ["developers", "gui-engineers", "security-engineers"]
---

# Dashboard Handlers - Event Handling with Governance Integration

**Module:** `src/app/gui/dashboard_handlers.py`  
**Lines of Code:** 454  
**Primary Class:** `DashboardHandlers` (mixin class)  
**Design Pattern:** Governance-first with graceful fallback

---

## Table of Contents

1. [Component Overview](#component-overview)
2. [Governance Integration Pattern](#governance-integration-pattern)
3. [Handler Methods](#handler-methods)
4. [Security Features](#security-features)
5. [Fallback Mechanism](#fallback-mechanism)
6. [Usage Examples](#usage-examples)
7. [Troubleshooting](#troubleshooting)

---

## Component Overview

### Purpose

`DashboardHandlers` provides event handling methods for dashboard operations with **mandatory governance routing**:

- Learning path generation
- Data analysis
- Security resource management
- Location tracking
- Emergency alerts
- Data visualization

### Architecture Change

**Old Pattern (Pre-Governance):**
```python
# Direct core imports and calls
path = self.learning_manager.generate_path(interest, skill_level)
```

**New Pattern (Post-Governance):**
```python
# Handler → Desktop Adapter → Router → Governance → Systems
adapter = get_desktop_adapter()
response = adapter.execute("learning.generate_path", {...})
```

### Key Benefits

1. **Centralized Validation**: All inputs validated at governance layer
2. **Audit Logging**: Every operation logged for compliance
3. **Graceful Degradation**: Falls back to direct calls if adapter unavailable
4. **Security**: Input sanitization before processing

---

## Governance Integration Pattern

### Standard Handler Structure

```python
def handler_method(self):
    """Description (governance-routed)"""
    
    # 1. INPUT SANITIZATION
    sanitized_input = sanitize_input(raw_input, max_length=X)
    if not validate_length(sanitized_input, min_len=Y, max_len=X):
        QMessageBox.warning(self, "Error", "Validation failed")
        return
    
    # 2. GOVERNANCE ROUTING
    try:
        adapter = get_desktop_adapter()
        response = adapter.execute(
            "domain.action",
            {"param": sanitized_input, "user": self.user_manager.current_user}
        )
        
        # 3. HANDLE SUCCESS
        if response["status"] == "success":
            result = response["result"]["data"]
            self.update_ui(result)
        else:
            # Handle governance rejection
            error = response.get("error", "Unknown error")
            logger.error(f"Operation failed: {error}")
            QMessageBox.warning(self, "Error", error)
    
    # 4. FALLBACK ON EXCEPTION
    except Exception as e:
        logger.error(f"Governance routing failed: {e}")
        self._fallback_direct_call()
```

### Governance Action Map

| Handler Method | Governance Action | Core System |
|----------------|-------------------|-------------|
| `generate_learning_path()` | `learning.generate_path` | `LearningRequestManager` |
| `load_data_file()` | `data.load_file` | `DataAnalysisManager` |
| `show_basic_stats()` | `data.get_stats` | `DataAnalysisManager` |
| `update_security_resources()` | `security.get_resources` | `SecurityResourceManager` |
| `add_security_favorite()` | `security.add_favorite` | `SecurityResourceManager` |
| `toggle_location_tracking()` | `location.start` / `location.stop` | `LocationTracker` |
| `update_location()` | `location.update` | `LocationTracker` |
| `clear_location_history()` | `location.clear_history` | `LocationTracker` |
| `save_emergency_contacts()` | `emergency.save_contacts` | `EmergencyAlert` |
| `send_emergency_alert()` | `emergency.send_alert` | `EmergencyAlert` |

---

## Handler Methods

### Learning Path Generation

#### `generate_learning_path()`

**Description:** Generate personalized learning path based on user interest and skill level.

**Inputs:**
- `interest` (str): Topic/skill (1-200 chars)
- `skill_level` (str): "beginner", "intermediate", "advanced"

**Security:**
```python
interest = sanitize_input(self.interest_input.text(), max_length=200)
if not validate_length(interest, min_len=1, max_len=200):
    QMessageBox.warning(self, "Input Error", "Interest must be 1-200 characters")
    return
```

**Governance Call:**
```python
response = adapter.execute(
    "learning.generate_path",
    {
        "interest": interest,
        "skill_level": skill_level,
        "user": self.user_manager.current_user
    }
)
```

**Success Handling:**
```python
if response["status"] == "success":
    path = response["result"]["path"]
    self.learning_path_display.setText(path)
```

**Fallback:**
```python
except Exception as e:
    logger.error(f"Failed to generate learning path: {e}")
    # Direct call
    path = self.learning_manager.generate_path(interest, skill_level)
    self.learning_path_display.setText(path)
```

---

### Data Analysis

#### `load_data_file()`

**Description:** Load CSV/XLSX/JSON file for analysis.

**File Types:** `.csv`, `.xlsx`, `.json`

**Governance Call:**
```python
response = adapter.execute(
    "data.load_file",
    {"file_path": file_path, "user": self.user_manager.current_user}
)
```

**Success Handling:**
```python
if response["status"] == "success":
    columns = response["result"]["columns"]
    self.column_selector.clear()
    self.column_selector.addItems(columns)
    self.show_basic_stats()
```

---

#### `show_basic_stats()`

**Description:** Display summary statistics (mean, median, std dev, etc.).

**Governance Call:**
```python
response = adapter.execute(
    "data.get_stats",
    {"user": self.user_manager.current_user}
)
```

**Display:**
```python
if response["status"] == "success":
    stats = response["result"]["stats"]
    self.analysis_display.setText(str(stats))
```

---

#### `perform_analysis()`

**Description:** Perform selected analysis type.

**Analysis Types:**
- Basic Stats
- Scatter Plot
- Histogram
- Box Plot
- Clustering

**Router:**
```python
analysis_type = self.analysis_type.currentText()
if analysis_type == "Basic Stats":
    self.show_basic_stats()
elif analysis_type in ["Scatter Plot", "Histogram", "Box Plot"]:
    self.create_visualization(analysis_type.lower().replace(" ", "_"))
elif analysis_type == "Clustering":
    self.perform_clustering()
```

---

### Security Resources

#### `update_security_resources()`

**Description:** Fetch security resources from GitHub by category.

**Categories:**
- CTF Challenges
- Penetration Testing
- Vulnerability Research
- Security Tools
- Bug Bounty

**Governance Call:**
```python
response = adapter.execute(
    "security.get_resources",
    {"category": category, "user": self.user_manager.current_user}
)
```

**Display:**
```python
if response["status"] == "success":
    resources = response["result"]["resources"]
    self.resources_list.clear()
    for resource in resources:
        self.resources_list.addItem(f"{resource['name']} ({resource['repo']})")
```

---

#### `open_security_resource(item)`

**Description:** Open selected GitHub repository in browser.

**Implementation:**
```python
import webbrowser

text = item.text()
repo = text[text.find("(") + 1 : text.find(")")]
webbrowser.open(f"https://github.com/{repo}")
```

---

#### `add_security_favorite()`

**Description:** Add current resource to favorites list.

**Governance Call:**
```python
response = adapter.execute(
    "security.add_favorite",
    {"repo": repo, "user": self.user_manager.current_user}
)
```

---

### Location Tracking

#### `toggle_location_tracking()`

**Description:** Start/stop location tracking.

**Governance Actions:**
- `location.start` - Enable tracking
- `location.stop` - Disable tracking

**Behavior:**
```python
action = "location.start" if not self.location_tracker.active else "location.stop"
response = adapter.execute(action, {"user": self.user_manager.current_user})

if response["status"] == "success":
    self.location_tracker.active = response["result"]["active"]
    if self.location_tracker.active:
        self.location_toggle.setText("Stop Location Tracking")
        self.location_timer.start(300000)  # Update every 5 minutes
    else:
        self.location_toggle.setText("Start Location Tracking")
        self.location_timer.stop()
```

---

#### `update_location()`

**Description:** Fetch current location from IP geolocation API.

**Frequency:** Every 5 minutes when tracking enabled

**Governance Call:**
```python
response = adapter.execute(
    "location.update",
    {"user": self.user_manager.current_user}
)
```

**Success:**
```python
if response["status"] == "success":
    self.update_location_display()
```

---

#### `clear_location_history()`

**Description:** Clear user's location history with confirmation.

**Confirmation:**
```python
reply = QMessageBox.question(
    self,
    "Confirm Clear",
    "Are you sure you want to clear your location history?",
    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
)
if reply == QMessageBox.StandardButton.Yes:
    # Proceed with clearing
```

**Governance Call:**
```python
response = adapter.execute(
    "location.clear_history",
    {"user": self.user_manager.current_user}
)
```

---

### Emergency Alerts

#### `save_emergency_contacts()`

**Description:** Save emergency contact email addresses.

**Security:**
```python
# Sanitize and validate contact emails
contacts_raw = sanitize_input(self.contacts_input.text(), max_length=500)
contacts = [email.strip() for email in contacts_raw.split(",")]

# Validate each email
invalid_emails = []
valid_contacts = []
for email in contacts:
    if email:
        if validate_email(email):
            valid_contacts.append(email)
        else:
            invalid_emails.append(email)

if invalid_emails:
    QMessageBox.warning(
        self, "Invalid Email",
        f"Invalid email addresses: {', '.join(invalid_emails)}"
    )
    return
```

**Governance Call:**
```python
response = adapter.execute(
    "emergency.save_contacts",
    {"contacts": valid_contacts, "user": self.user_manager.current_user}
)
```

---

#### `send_emergency_alert()`

**Description:** Send emergency alert to saved contacts with current location.

**Confirmation:**
```python
reply = QMessageBox.question(
    self, "Confirm Alert",
    "Are you sure you want to send an emergency alert?",
    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
)
```

**Message Validation:**
```python
message = sanitize_input(self.emergency_message.toPlainText(), max_length=1000)
if not validate_length(message, min_len=1, max_len=1000):
    QMessageBox.warning(
        self, "Input Error",
        "Emergency message must be 1-1000 characters"
    )
    return
```

**Governance Call:**
```python
response = adapter.execute(
    "emergency.send_alert",
    {
        "location": location,
        "message": message,
        "user": self.user_manager.current_user
    }
)
```

---

### Data Visualization

#### `create_visualization(plot_type)`

**Description:** Create matplotlib visualization in new window.

**Plot Types:**
- `scatter` - Scatter plot
- `histogram` - Histogram
- `boxplot` - Box plot

**Implementation:**
```python
canvas = self.data_analyzer.create_visualization(
    plot_type, self.column_selector.currentText()
)
if canvas:
    plot_window = QWidget()
    plot_layout = QVBoxLayout(plot_window)
    plot_layout.addWidget(canvas)
    plot_window.setWindowTitle(f"{plot_type.title()} Plot")
    plot_window.show()
```

---

#### `perform_clustering()`

**Description:** K-means clustering analysis with visualization.

**Requirements:**
- At least 2 numeric columns

**Validation:**
```python
numeric_cols = self.data_analyzer.data.select_dtypes(
    include=["float64", "int64"]
).columns
if len(numeric_cols) < 2:
    QMessageBox.warning(
        self, "Error", "Need at least 2 numeric columns for clustering"
    )
    return
```

**Visualization:**
```python
canvas, _ = self.data_analyzer.perform_clustering(numeric_cols)
if canvas:
    plot_window = QWidget()
    plot_layout = QVBoxLayout(plot_window)
    plot_layout.addWidget(canvas)
    plot_window.setWindowTitle("Clustering Results")
    plot_window.show()
```

---

## Security Features

### 1. Input Sanitization

**All text inputs sanitized:**
```python
from app.security.data_validation import sanitize_input

sanitized = sanitize_input(raw_input, max_length=1000)
```

**Removes:**
- Control characters (ASCII < 32, except `\n`)
- Excessive whitespace
- Potential injection payloads

---

### 2. Length Validation

**Enforce min/max lengths:**
```python
from app.security.data_validation import validate_length

if not validate_length(input_text, min_len=1, max_len=200):
    QMessageBox.warning(self, "Error", "Input must be 1-200 characters")
    return
```

---

### 3. Email Validation

**Regex-based validation:**
```python
from app.security.data_validation import validate_email

if not validate_email(email):
    QMessageBox.warning(self, "Error", "Invalid email format")
    return
```

---

### 4. Governance Logging

**All operations logged:**
```python
logger.info(f"User {user} executed {action} with params {params}")
```

---

## Fallback Mechanism

### When Fallback Triggers

1. **Desktop adapter unavailable**: Module not initialized
2. **Import error**: Governance pipeline not installed
3. **Network timeout**: Backend unreachable
4. **Governance rejection**: Action blocked by policy

### Fallback Implementation

```python
except Exception as e:
    logger.error(f"Governance routing failed: {e}")
    # Fallback to direct call to preserve functionality
    result = self.core_system.direct_method(*args)
    self.update_ui(result)
```

### Fallback Methods

| Primary Handler | Fallback Method |
|----------------|-----------------|
| `toggle_location_tracking()` | `_toggle_location_tracking_direct()` |
| `update_location()` | `_update_location_direct()` |
| `send_emergency_alert()` | `_send_emergency_alert_direct()` |

---

## Usage Examples

### Example 1: Connect Handler to Button

```python
from app.gui.dashboard_handlers import DashboardHandlers

class MyDashboard(QWidget, DashboardHandlers):
    def __init__(self):
        super().__init__()
        
        # Button
        self.generate_btn = QPushButton("Generate Learning Path")
        self.generate_btn.clicked.connect(self.generate_learning_path)
```

---

### Example 2: Testing Governance Routing

```python
# Mock desktop adapter unavailable
import app.interfaces.desktop.integration as integration
integration.get_desktop_adapter = lambda: None

# Handler will fall back to direct call
dashboard.generate_learning_path()
```

---

### Example 3: Validating Input

```python
from app.security.data_validation import sanitize_input, validate_length

# Get user input
raw_text = self.input_field.text()

# Sanitize
clean_text = sanitize_input(raw_text, max_length=500)

# Validate
if not validate_length(clean_text, min_len=5, max_len=500):
    QMessageBox.warning(self, "Error", "Input must be 5-500 characters")
    return
```

---

## Troubleshooting

### Issue 1: Governance Calls Always Fail

**Symptom:** All handlers fall back to direct calls

**Cause:** Desktop adapter not initialized

**Solution:**
```python
from app.interfaces.desktop.integration import get_desktop_adapter

try:
    adapter = get_desktop_adapter()
    print("Adapter available")
except Exception as e:
    print(f"Adapter unavailable: {e}")
    # Initialize adapter
    from app.interfaces.desktop.integration import init_desktop_adapter
    init_desktop_adapter()
```

---

### Issue 2: Validation Errors Not Showing

**Symptom:** Invalid inputs accepted

**Cause:** Validation calls missing

**Solution:**
```python
# Always validate before processing
if not validate_length(input_text, min_len=1, max_len=200):
    QMessageBox.warning(self, "Error", "Input length invalid")
    return  # ← Critical: Don't proceed
```

---

### Issue 3: Email Validation Rejects Valid Emails

**Symptom:** Legitimate emails marked invalid

**Cause:** Overly strict regex

**Debug:**
```python
from app.security.data_validation import validate_email

test_emails = ["user@example.com", "user+tag@example.com"]
for email in test_emails:
    is_valid = validate_email(email)
    print(f"{email}: {'✅' if is_valid else '❌'}")
```

---

## Best Practices

### 1. Always Sanitize First

```python
# ✅ Correct
sanitized = sanitize_input(raw_input, max_length=1000)
if validate_length(sanitized, min_len=1, max_len=1000):
    # Process
```

```python
# ❌ Wrong (processing unsanitized input)
if len(raw_input) > 0:
    process(raw_input)
```

---

### 2. Log All Governance Failures

```python
except Exception as e:
    logger.error(f"Governance routing failed for {action}: {e}")
    # Then fall back
```

---

### 3. Provide User Feedback

```python
# Always show message boxes for errors
QMessageBox.warning(self, "Error Title", "Descriptive error message")
```

---

### 4. Test Fallback Paths

```python
# Unit test both governance and fallback paths
def test_handler_with_governance():
    # Mock successful governance call
    pass

def test_handler_fallback():
    # Mock governance failure
    pass
```

---

## Related Documentation

- **[Dashboard Utils](./dashboard_utils.md)** - Utility functions
- **[Leather Book Dashboard](./leather_book_dashboard.md)** - Main dashboard
- **Desktop Integration** - `docs/DESKTOP_INTEGRATION.md`
- **Governance Pipeline** - `docs/GOVERNANCE_PIPELINE.md`

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 2.0.0 | 2026-04-20 | Governance integration, security hardening | AGENT-034 |
| 1.0.0 | 2026-02-10 | Initial direct-call implementation | GUI Team |

---

## License

**Copyright © 2026 Project-AI Team**  
Internal documentation - Not for public distribution

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

