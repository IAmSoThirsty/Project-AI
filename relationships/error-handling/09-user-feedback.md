# User Feedback Relationship Map

**System:** User Feedback  
**Mission:** Document user notification systems, error messages, and user-facing error communication  
**Agent:** AGENT-068 Error Handling Relationship Mapping Specialist

---

## User Feedback Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ User Feedback Hierarchy (Severity → Intrusiveness)          │
│                                                               │
│  Level 1: Passive Feedback (Low Intrusiveness)              │
│  ├─ Status bar messages (5s auto-dismiss)                   │
│  ├─ Icon/color changes (visual indicators)                  │
│  ├─ Tooltip updates                                         │
│  └─ Log entries (visible in debug panel)                    │
│                                                               │
│  Level 2: Active Feedback (Medium Intrusiveness)            │
│  ├─ Toast notifications (auto-dismiss)                      │
│  ├─ Banner messages (dismissible)                           │
│  ├─ Form validation errors                                  │
│  └─ Disabled UI elements with explanations                  │
│                                                               │
│  Level 3: Blocking Feedback (High Intrusiveness)            │
│  ├─ Warning dialogs (QMessageBox.warning)                   │
│  ├─ Confirmation dialogs (require user action)              │
│  ├─ Error dialogs (QMessageBox.critical)                    │
│  └─ Modal error panels                                      │
│                                                               │
│  Level 4: Critical Feedback (Maximum Intrusiveness)         │
│  ├─ Full-screen error pages                                 │
│  ├─ System shutdown notifications                           │
│  ├─ Data loss warnings                                      │
│  └─ Security violation alerts                               │
└──────────────────────────────────────────────────────────────┘
```

---

## GUI Feedback Mechanisms

### 1. QMessageBox Dialogs

**Primary Tool:** PyQt6 `QMessageBox`  
**Locations:** 80+ usage sites across GUI modules

#### Critical Errors (QMessageBox.critical)

**Visual:**
```
┌────────────────────────────────────────┐
│ ⛔ Error                                │
├────────────────────────────────────────┤
│ Failed to save configuration:          │
│                                         │
│ [Errno 13] Permission denied:          │
│ '/etc/projectai/config.json'          │
│                                         │
│ Please check file permissions and      │
│ try again.                             │
│                                         │
│              [   OK   ]                │
└────────────────────────────────────────┘
```

**Implementation:**
```python
QMessageBox.critical(
    self,  # parent widget
    "Error",  # dialog title
    f"Failed to save configuration:\n\n{str(e)}\n\n"
    "Please check file permissions and try again."
)
```

**When to Use:**
- Operation failure requiring user awareness
- Data loss risk
- Configuration errors
- Network failures preventing core functionality

**Examples:**
```python
# From dashboard.py
QMessageBox.critical(
    self,
    "Image Generation Failed",
    f"Could not generate image: {error_msg}"
)

# From login.py
QMessageBox.critical(
    self,
    "Authentication Failed",
    "Invalid credentials. Please try again."
)

# From dashboard_handlers.py
QMessageBox.critical(
    self,
    "Save Failed",
    f"Could not save data: {str(e)}"
)
```

---

#### Warnings (QMessageBox.warning)

**Visual:**
```
┌────────────────────────────────────────┐
│ ⚠️ Warning                              │
├────────────────────────────────────────┤
│ You must be logged in to perform       │
│ this action.                           │
│                                         │
│ Please log in and try again.           │
│                                         │
│              [   OK   ]                │
└────────────────────────────────────────┘
```

**Implementation:**
```python
QMessageBox.warning(
    self,
    "Warning",
    "You must be logged in to perform this action.\n\n"
    "Please log in and try again."
)
```

**When to Use:**
- Invalid user input
- Missing required fields
- Operations requiring authentication
- Potentially destructive actions (before confirmation)

**Examples:**
```python
# Input validation
if not username or not password:
    QMessageBox.warning(
        self,
        "Missing Credentials",
        "Please enter both username and password."
    )

# State validation
if not self.persona:
    QMessageBox.warning(
        self,
        "Persona Not Initialized",
        "AI Persona must be initialized first."
    )

# Permission check
if user_role != "admin":
    QMessageBox.warning(
        self,
        "Insufficient Permissions",
        "Only administrators can perform this action."
    )
```

---

#### Information (QMessageBox.information)

**Visual:**
```
┌────────────────────────────────────────┐
│ ℹ️ Success                              │
├────────────────────────────────────────┤
│ Configuration saved successfully!      │
│                                         │
│ Changes will take effect immediately.  │
│                                         │
│              [   OK   ]                │
└────────────────────────────────────────┘
```

**Implementation:**
```python
QMessageBox.information(
    self,
    "Success",
    "Configuration saved successfully!\n\n"
    "Changes will take effect immediately."
)
```

**When to Use:**
- Successful operation completion
- Important status updates
- Non-error informational messages

**Examples:**
```python
# Operation success
QMessageBox.information(
    self,
    "Image Generated",
    f"Image saved to: {output_path}"
)

# Status update
QMessageBox.information(
    self,
    "Sync Complete",
    "Data synchronized to cloud successfully."
)
```

---

#### Confirmation (QMessageBox.question)

**Visual:**
```
┌────────────────────────────────────────┐
│ ❓ Confirm Action                       │
├────────────────────────────────────────┤
│ Are you sure you want to delete        │
│ user "john_doe"?                       │
│                                         │
│ This action cannot be undone.          │
│                                         │
│         [ Yes ]    [ No ]              │
└────────────────────────────────────────┘
```

**Implementation:**
```python
reply = QMessageBox.question(
    self,
    "Confirm Delete",
    f"Are you sure you want to delete user '{username}'?\n\n"
    "This action cannot be undone.",
    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    QMessageBox.StandardButton.No  # Default button
)

if reply == QMessageBox.StandardButton.Yes:
    # Proceed with deletion
    delete_user(username)
```

**When to Use:**
- Destructive operations
- Irreversible actions
- Important state changes
- Data modifications

**Examples:**
```python
# From dashboard_handlers.py
if QMessageBox.question(
    self,
    "Clear Override",
    "Remove all override configurations?",
    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
) == QMessageBox.StandardButton.Yes:
    self.command_override.clear_all()

# From user_management.py
confirm = QMessageBox.question(
    self,
    "Delete User",
    f"Delete user '{selected_user}'?",
    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
)

if confirm == QMessageBox.StandardButton.Yes:
    self.user_manager.delete_user(selected_user)
```

---

### 2. Status Bar Notifications

**Tool:** `QStatusBar`  
**Purpose:** Non-intrusive, temporary notifications

**Implementation:**
```python
# Temporary message (auto-dismiss after 5 seconds)
self.statusBar().showMessage(
    "⚠️ Image generation service temporarily unavailable",
    5000  # milliseconds
)

# Permanent status
self.statusBar().showMessage("🔴 DEGRADED MODE")

# Clear status
self.statusBar().clearMessage()
```

**Message Types:**

#### Success Messages
```python
self.statusBar().showMessage("✅ Configuration saved", 3000)
self.statusBar().showMessage("✅ User authenticated", 2000)
self.statusBar().showMessage("✅ Sync complete", 3000)
```

#### Warning Messages
```python
self.statusBar().showMessage("⚠️ Using cached data", 5000)
self.statusBar().showMessage("⚠️ API rate limit approaching", 5000)
self.statusBar().showMessage("⚠️ High memory usage detected", 10000)
```

#### Error Messages
```python
self.statusBar().showMessage("❌ Connection lost", 5000)
self.statusBar().showMessage("❌ File save failed", 5000)
```

#### Status Indicators
```python
# Operating mode indicators
self.statusBar().showMessage("🟢 NORMAL MODE")
self.statusBar().showMessage("🟡 DEGRADED MODE")
self.statusBar().showMessage("🔴 CRITICAL MODE")
self.statusBar().showMessage("⚪ SAFE MODE")
```

---

### 3. UI Element States

**Tool:** Enable/Disable + Tooltips  
**Purpose:** Prevent invalid actions + explain why

**Implementation:**
```python
class FeatureAvailabilityFeedback:
    def update_ui_for_degraded_mode(self):
        """Update UI to reflect degraded operation."""
        
        # Disable unavailable features
        if not self.is_feature_available("image_generation"):
            self.image_gen_button.setEnabled(False)
            self.image_gen_button.setToolTip(
                "Image generation temporarily unavailable.\n"
                "The service will be restored automatically."
            )
        
        if not self.is_feature_available("ai_chat"):
            self.chat_input.setEnabled(False)
            self.chat_input.setPlaceholderText(
                "Chat unavailable - service degraded"
            )
            self.chat_send_button.setEnabled(False)
        
        # Show degradation indicator
        self.status_label.setText("⚠️ DEGRADED MODE")
        self.status_label.setStyleSheet("color: orange;")
```

**Visual Feedback Patterns:**

#### Disabled Button with Explanation
```python
self.save_button.setEnabled(False)
self.save_button.setToolTip(
    "Save is disabled in read-only mode.\n"
    "Write operations will be restored when the system recovers."
)
```

#### Placeholder Text for Disabled Input
```python
self.chat_input.setPlaceholderText(
    "Chat service offline - please try again later"
)
self.chat_input.setEnabled(False)
```

#### Visual State Indicators
```python
# Normal state
self.connection_indicator.setStyleSheet("background-color: green;")
self.connection_label.setText("🟢 Connected")

# Degraded state
self.connection_indicator.setStyleSheet("background-color: orange;")
self.connection_label.setText("🟡 Degraded")

# Error state
self.connection_indicator.setStyleSheet("background-color: red;")
self.connection_label.setText("🔴 Disconnected")
```

---

### 4. Form Validation Feedback

**Pattern:** Real-time validation with inline messages

**Implementation:**
```python
class FormValidationFeedback:
    def validate_username(self, username: str):
        """Validate username and show feedback."""
        if not username:
            self.username_error_label.setText("❌ Username required")
            self.username_error_label.setVisible(True)
            self.username_input.setStyleSheet("border: 1px solid red;")
            return False
        
        if len(username) < 3:
            self.username_error_label.setText(
                "❌ Username must be at least 3 characters"
            )
            self.username_error_label.setVisible(True)
            self.username_input.setStyleSheet("border: 1px solid red;")
            return False
        
        # Valid
        self.username_error_label.setVisible(False)
        self.username_input.setStyleSheet("border: 1px solid green;")
        return True
    
    def on_username_changed(self, text: str):
        """Real-time validation as user types."""
        self.validate_username(text)
```

**Visual:**
```
┌────────────────────────────────────┐
│ Username: [john_______________]   │ ← Green border (valid)
│                                    │
│ Password: [___________________]   │ ← Red border (invalid)
│ ❌ Password must be at least      │
│    8 characters                   │
│                                    │
│           [ Sign In ]             │ ← Disabled until valid
└────────────────────────────────────┘
```

---

## DashboardErrorHandler Integration

**Location:** `src/app/gui/dashboard_utils.py`

**Centralized User Feedback:**
```python
class DashboardErrorHandler:
    @staticmethod
    def handle_exception(
        exception: Exception,
        context: str = "Operation",
        show_dialog: bool = True,
        parent=None,
    ) -> None:
        """
        Unified error handling with consistent user feedback.
        
        Args:
            exception: The exception to handle
            context: Context string for error message
            show_dialog: Whether to show dialog to user
            parent: Parent widget for dialog
        """
        error_message = f"{context}: {str(exception)}"
        logger.error(error_message, exc_info=True)
        
        if show_dialog:
            QMessageBox.critical(parent, "Error", error_message)
    
    @staticmethod
    def handle_warning(
        message: str,
        context: str = "Warning",
        show_dialog: bool = False,
        parent=None,
    ) -> None:
        """Handle warnings with optional user notification."""
        logger.warning("%s: %s", context, message)
        if show_dialog:
            QMessageBox.warning(parent, context, message)
```

**Consistent Usage:**
```python
# Throughout codebase
try:
    perform_operation()
except Exception as e:
    DashboardErrorHandler.handle_exception(
        e,
        context="Image Generation",
        show_dialog=True,
        parent=self
    )
```

---

## User Feedback Best Practices

### 1. Message Clarity

**Good:**
```python
QMessageBox.critical(
    self,
    "Save Failed",
    "Could not save configuration file.\n\n"
    "Error: Permission denied\n"
    "Location: /etc/projectai/config.json\n\n"
    "Please check file permissions or contact your administrator."
)
```

**Bad:**
```python
QMessageBox.critical(self, "Error", str(e))
# Just shows: "[Errno 13] Permission denied"
```

---

### 2. Actionable Messages

**Good:**
```python
QMessageBox.warning(
    self,
    "Connection Lost",
    "Lost connection to server.\n\n"
    "What you can do:\n"
    "1. Check your network connection\n"
    "2. Verify server is running\n"
    "3. Click 'Reconnect' to try again"
)
```

**Bad:**
```python
QMessageBox.warning(self, "Error", "Connection lost")
# No guidance on what to do
```

---

### 3. Appropriate Severity

**Matching severity to impact:**

| Situation | Dialog Type | Rationale |
|-----------|------------|-----------|
| Invalid input | Warning | User can correct |
| File not found | Warning | Non-critical, has fallback |
| Permission denied | Critical | Blocks operation |
| Network timeout | Warning | Transient, may recover |
| Data corruption | Critical | Data integrity at risk |
| Security violation | Critical | Security concern |

---

### 4. Progressive Disclosure

**Example: Multi-stage error handling**

```python
def handle_save_error(self, error: Exception):
    """Progressive error feedback."""
    
    # Stage 1: Status bar (least intrusive)
    self.statusBar().showMessage("❌ Auto-save failed", 3000)
    
    # Stage 2: If user tries manual save
    if user_initiated:
        QMessageBox.warning(
            self,
            "Save Failed",
            f"Could not save: {str(error)}\n\n"
            "Your work is stored in memory.\n"
            "Click 'Details' for more information."
        )
    
    # Stage 3: If repeated failures
    if consecutive_failures >= 3:
        QMessageBox.critical(
            self,
            "Persistent Save Failure",
            "Unable to save your work after multiple attempts.\n\n"
            "Recommended actions:\n"
            "1. Copy your work to clipboard\n"
            "2. Save to alternate location\n"
            "3. Contact support\n\n"
            f"Error details: {str(error)}"
        )
```

---

## Feedback for Different Error Categories

### Network Errors
```python
def handle_network_error(self, error):
    """User-friendly network error feedback."""
    if isinstance(error, requests.Timeout):
        QMessageBox.warning(
            self,
            "Request Timeout",
            "The server is taking too long to respond.\n\n"
            "This may be due to:\n"
            "• Slow network connection\n"
            "• High server load\n"
            "• Service temporarily unavailable\n\n"
            "The system will retry automatically."
        )
    elif isinstance(error, requests.ConnectionError):
        QMessageBox.critical(
            self,
            "Connection Failed",
            "Could not connect to server.\n\n"
            "Please check:\n"
            "• Network connection is active\n"
            "• Server address is correct\n"
            "• Firewall is not blocking connection"
        )
```

### Permission Errors
```python
def handle_permission_error(self, path: str):
    """User-friendly permission error feedback."""
    QMessageBox.critical(
        self,
        "Permission Denied",
        f"Cannot access file:\n{path}\n\n"
        "Possible solutions:\n"
        "• Run application as administrator\n"
        "• Check file/folder permissions\n"
        "• Ensure file is not open in another program"
    )
```

### Resource Exhaustion
```python
def handle_resource_error(self, resource_type: str):
    """User-friendly resource error feedback."""
    if resource_type == "memory":
        QMessageBox.warning(
            self,
            "Low Memory",
            "System is running low on memory.\n\n"
            "Recommended actions:\n"
            "• Close unused applications\n"
            "• Save your work\n"
            "• Restart application if issues persist\n\n"
            "Some features may be disabled temporarily."
        )
```

---

## User Feedback Metrics

### Tracking User Interactions
```python
class FeedbackMetrics:
    def __init__(self):
        self.dialog_shown_count = 0
        self.user_dismissed_count = 0
        self.avg_time_to_dismiss = []
    
    def on_dialog_shown(self):
        self.dialog_shown_count += 1
        self.show_timestamp = time.time()
    
    def on_dialog_dismissed(self):
        self.user_dismissed_count += 1
        dismiss_time = time.time() - self.show_timestamp
        self.avg_time_to_dismiss.append(dismiss_time)
    
    def get_statistics(self) -> dict:
        return {
            "dialogs_shown": self.dialog_shown_count,
            "user_dismissals": self.user_dismissed_count,
            "avg_time_to_dismiss": (
                sum(self.avg_time_to_dismiss) / 
                len(self.avg_time_to_dismiss)
                if self.avg_time_to_dismiss else 0
            )
        }
```

---

## Related Systems

**Dependencies:**
- [Error Handlers](#02-error-handlers.md) - Generate feedback
- [Error Reporting](#08-error-reporting.md) - Backend for reports
- [Graceful Degradation](#06-graceful-degradation.md) - Status communication
- [Error Logging](#07-error-logging.md) - Detailed logging

**Integration Points:**
- All GUI modules use QMessageBox for feedback
- DashboardErrorHandler provides centralized feedback
- Status bar shows non-critical notifications
- UI element states prevent invalid actions

---

**Document Version:** 1.0  
**Last Updated:** 2025-06-15  
**Analyst:** AGENT-068
