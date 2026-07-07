---
title: "Dashboard Utils - Utilities for Error Handling and Async Operations"
id: "gui-dashboard-utils"
type: "api_reference"
version: "2.0.0"
created_date: "2026-04-20"
updated_date: "2026-04-20"
status: "production"
author: "AGENT-034"
contributors: ["Architecture Team", "GUI Team"]
category: "gui-documentation"
tags: ["pyqt6", "gui", "utilities", "error-handling", "async", "validation"]
technologies: ["Python 3.11+", "PyQt6", "QRunnable", "QThreadPool"]
related_docs:
  - "gui-dashboard-handlers"
  - "gui-leather-book-dashboard"
  - "security-validation"
description: "Utility classes for dashboard operations: error handling, async workers, input validation, logging, and configuration management"
security_classification: "internal"
review_status: "peer-reviewed"
audience: ["developers", "gui-engineers"]
---

# Dashboard Utils - Utilities for Error Handling and Async Operations

**Module:** `src/app/gui/dashboard_utils.py`  
**Lines of Code:** 256  
**Classes:** 5 utility classes  
**Design Pattern:** Static utility classes and async workers

---

## Table of Contents

1. [Component Overview](#component-overview)
2. [Utility Classes](#utility-classes)
3. [Error Handling](#error-handling)
4. [Async Operations](#async-operations)
5. [Input Validation](#input-validation)
6. [Logging](#logging)
7. [Configuration Management](#configuration-management)
8. [Usage Examples](#usage-examples)
9. [Best Practices](#best-practices)

---

## Component Overview

### Purpose

`dashboard_utils.py` provides 5 utility classes for common dashboard operations:

1. **DashboardErrorHandler** - Centralized error handling
2. **AsyncWorker** - Thread-safe async operations
3. **DashboardAsyncManager** - Async task management
4. **DashboardValidationManager** - Input validation
5. **DashboardLogger** - Enhanced logging
6. **DashboardConfiguration** - Config management

### Key Features

- **Thread-safe async operations** via `QThreadPool`
- **Centralized error handling** with logging and optional dialogs
- **Input validation** (username, email, password)
- **Performance logging** (track operation duration)
- **Configuration defaults** (window size, timeouts, etc.)

---

## Utility Classes

### 1. DashboardErrorHandler

**Purpose:** Centralized error handling with logging and user notifications.

**Methods:**
- `handle_exception()` - Handle exceptions with logging and optional dialog
- `handle_warning()` - Handle warnings
- `validate_input()` - Validate user input types

---

### 2. AsyncWorker

**Purpose:** QRunnable worker for async operations in thread pool.

**Signals:**
- `finished` - Emitted when operation completes
- `error` - Emitted on exception
- `result` - Emitted with operation result

---

### 3. DashboardAsyncManager

**Purpose:** Manage async tasks in thread pool.

**Methods:**
- `run_async()` - Start async task
- `wait_for_task()` - Wait for task completion
- `cancel_all_tasks()` - Cancel all active tasks

---

### 4. DashboardValidationManager

**Purpose:** Input validation utilities.

**Methods:**
- `validate_username()` - Username format validation
- `validate_email()` - Email format validation
- `validate_password()` - Password strength validation
- `sanitize_string()` - String sanitization

---

### 5. DashboardLogger

**Purpose:** Enhanced logging for dashboard operations.

**Methods:**
- `log_operation()` - Log general operations
- `log_user_action()` - Log user-specific actions
- `log_performance()` - Log operation timing

---

### 6. DashboardConfiguration

**Purpose:** Configuration management with defaults.

**Methods:**
- `get()` - Get config value
- `set()` - Set config value
- `to_dict()` - Convert to dictionary

---

## Error Handling

### DashboardErrorHandler

#### `handle_exception(exception, context, show_dialog, parent)`

**Description:** Handle exception with logging and optional dialog.

**Parameters:**
- `exception` (Exception): Exception to handle
- `context` (str): Operation context (default: "Operation")
- `show_dialog` (bool): Show QMessageBox (default: True)
- `parent` (QWidget): Parent widget for dialog

**Behavior:**
```python
error_message = f"{context}: {str(exception)}"
logger.error(error_message, exc_info=True)

if show_dialog:
    QMessageBox.critical(parent, "Error", error_message)
```

**Example:**
```python
try:
    risky_operation()
except Exception as e:
    DashboardErrorHandler.handle_exception(
        e, context="Data loading", show_dialog=True, parent=self
    )
```

---

#### `handle_warning(message, context, show_dialog, parent)`

**Description:** Handle warning with logging and optional dialog.

**Parameters:**
- `message` (str): Warning message
- `context` (str): Warning context (default: "Warning")
- `show_dialog` (bool): Show QMessageBox (default: False)
- `parent` (QWidget): Parent widget for dialog

**Example:**
```python
DashboardErrorHandler.handle_warning(
    "File not found, using defaults",
    context="Config loading",
    show_dialog=False
)
```

---

#### `validate_input(value, input_type, required, context)`

**Description:** Validate user input type and presence.

**Parameters:**
- `value` (Any): Input value to validate
- `input_type` (type): Expected type (e.g., `str`, `int`)
- `required` (bool): Is input required? (default: True)
- `context` (str): Input context (default: "Input")

**Returns:** `bool` - True if valid, False otherwise

**Validation Rules:**
1. If `required=True` and value is empty: ❌ Invalid
2. If value type doesn't match `input_type`: ❌ Invalid
3. Otherwise: ✅ Valid

**Example:**
```python
username = input_field.text()
if DashboardErrorHandler.validate_input(username, str, required=True, context="Username"):
    # Proceed with valid username
    pass
```

---

## Async Operations

### AsyncWorker

**Purpose:** QRunnable worker for thread pool execution.

#### Constructor

```python
worker = AsyncWorker(func, *args, **kwargs)
```

**Parameters:**
- `func` (Callable): Function to run asynchronously
- `*args`: Positional arguments for function
- `**kwargs`: Keyword arguments for function

**Signals:**
- `finished = pyqtSignal()` - Emitted when function completes
- `error = pyqtSignal(Exception)` - Emitted on exception
- `result = pyqtSignal(object)` - Emitted with function result

---

#### `run()`

**Description:** Execute function in background thread.

**Behavior:**
```python
try:
    result = self.func(*self.args, **self.kwargs)
    self.signals.result.emit(result)
except Exception as e:
    logger.error("AsyncWorker error: %s", e)
    self.signals.error.emit(e)
finally:
    self.signals.finished.emit()
```

**Example:**
```python
def slow_operation(x, y):
    time.sleep(5)
    return x + y

worker = AsyncWorker(slow_operation, 10, 20)
worker.signals.result.connect(lambda result: print(f"Result: {result}"))
worker.signals.finished.connect(lambda: print("Done!"))

QThreadPool.globalInstance().start(worker)
```

---

### DashboardAsyncManager

**Purpose:** Manage multiple async tasks with tracking.

#### Constructor

```python
manager = DashboardAsyncManager()
```

**Attributes:**
- `thread_pool` (QThreadPool): Thread pool for workers
- `active_tasks` (dict): `{task_id: worker}` mapping

---

#### `run_async(task_id, func, on_result, on_error, *args, **kwargs)`

**Description:** Run function asynchronously with callbacks.

**Parameters:**
- `task_id` (str): Unique task identifier
- `func` (Callable): Function to run
- `on_result` (Callable | None): Callback for result
- `on_error` (Callable | None): Callback for error
- `*args, **kwargs`: Function arguments

**Example:**
```python
manager = DashboardAsyncManager()

def load_data(filepath):
    with open(filepath) as f:
        return f.read()

def on_result(data):
    print(f"Loaded: {data}")

def on_error(e):
    print(f"Error: {e}")

manager.run_async(
    "load_task",
    load_data,
    on_result=on_result,
    on_error=on_error,
    "data.txt"
)
```

---

#### `wait_for_task(task_id, timeout_ms)`

**Description:** Wait for specific task to complete.

**Parameters:**
- `task_id` (str): Task identifier
- `timeout_ms` (int): Timeout in milliseconds (default: 5000)

**Returns:** `bool` - True if completed, False if timeout

**Example:**
```python
manager.run_async("task1", long_operation)
if manager.wait_for_task("task1", timeout_ms=10000):
    print("Task completed")
else:
    print("Task timed out")
```

---

#### `cancel_all_tasks()`

**Description:** Cancel all active tasks.

**Behavior:**
```python
self.thread_pool.clear()
self.active_tasks.clear()
logger.info("All async tasks cancelled")
```

**Example:**
```python
# On window close
def closeEvent(self, event):
    self.async_manager.cancel_all_tasks()
    super().closeEvent(event)
```

---

## Input Validation

### DashboardValidationManager

#### `validate_username(username) -> tuple[bool, str]`

**Description:** Validate username format.

**Rules:**
1. Length: 3-50 characters
2. Characters: Alphanumeric + `-` + `_`

**Returns:** `(is_valid: bool, error_message: str)`

**Example:**
```python
is_valid, error = DashboardValidationManager.validate_username("alice_123")
if not is_valid:
    QMessageBox.warning(self, "Error", error)
```

**Test Cases:**
```python
# ✅ Valid
("alice", True, "")
("user_123", True, "")
("john-doe", True, "")

# ❌ Invalid
("ab", False, "Username must be at least 3 characters")
("x" * 51, False, "Username must be less than 50 characters")
("user@name", False, "Username can only contain alphanumeric characters, - and _")
```

---

#### `validate_email(email) -> tuple[bool, str]`

**Description:** Validate email format.

**Rules:**
1. Must contain `@`
2. Must contain `.` in domain
3. Local and domain parts must be non-empty

**Returns:** `(is_valid: bool, error_message: str)`

**Example:**
```python
is_valid, error = DashboardValidationManager.validate_email("user@example.com")
if not is_valid:
    QMessageBox.warning(self, "Error", error)
```

**Test Cases:**
```python
# ✅ Valid
("user@example.com", True, "")
("user.name@sub.example.com", True, "")

# ❌ Invalid
("userexample.com", False, "Invalid email format")  # Missing @
("user@example", False, "Invalid email format")     # Missing . in domain
("@example.com", False, "Invalid email format")     # Empty local
```

---

#### `validate_password(password) -> tuple[bool, str]`

**Description:** Validate password strength.

**Rules:**
1. Length: ≥8 characters
2. Must contain uppercase letter
3. Must contain digit

**Returns:** `(is_valid: bool, error_message: str)`

**Example:**
```python
is_valid, error = DashboardValidationManager.validate_password("SecurePass123")
if not is_valid:
    QMessageBox.warning(self, "Error", error)
```

**Test Cases:**
```python
# ✅ Valid
("SecurePass123", True, "")
("MyP@ssw0rd!", True, "")

# ❌ Invalid
("short1A", False, "Password must be at least 8 characters")
("lowercase123", False, "Password must contain uppercase letter")
("NoDigits", False, "Password must contain digit")
```

---

#### `sanitize_string(value, max_length) -> str`

**Description:** Sanitize string input.

**Parameters:**
- `value` (str): Input string
- `max_length` (int): Maximum length (default: 1000)

**Sanitization:**
1. Remove control characters (ASCII < 32, except `\n`)
2. Truncate to `max_length`

**Example:**
```python
raw_input = "Hello\x00World\x01!"
clean = DashboardValidationManager.sanitize_string(raw_input, max_length=50)
# Result: "HelloWorld!"
```

---

## Logging

### DashboardLogger

#### Constructor

```python
logger = DashboardLogger(name="Dashboard")
```

**Parameters:**
- `name` (str): Logger name (default: "Dashboard")

---

#### `log_operation(operation, details)`

**Description:** Log general operation.

**Parameters:**
- `operation` (str): Operation description
- `details` (dict, optional): Additional details

**Example:**
```python
logger = DashboardLogger("DataAnalysis")
logger.log_operation("Load CSV", details={"rows": 1000, "columns": 5})
# Output: "Operation: Load CSV | {'rows': 1000, 'columns': 5}"
```

---

#### `log_user_action(user, action, details)`

**Description:** Log user-specific action.

**Parameters:**
- `user` (str): Username
- `action` (str): Action performed
- `details` (dict, optional): Additional details

**Example:**
```python
logger.log_user_action("alice", "Generate learning path", details={"topic": "Python"})
# Output: "User 'alice' performed 'Generate learning path' | {'topic': 'Python'}"
```

---

#### `log_performance(operation, duration_ms)`

**Description:** Log operation performance.

**Parameters:**
- `operation` (str): Operation name
- `duration_ms` (float): Duration in milliseconds

**Logging Levels:**
- `duration_ms > 1000ms` → `WARNING`
- `duration_ms > 500ms` → `INFO`
- `duration_ms ≤ 500ms` → `DEBUG`

**Example:**
```python
import time

start = time.time()
# ... operation ...
end = time.time()
duration_ms = (end - start) * 1000

logger.log_performance("Data loading", duration_ms)
# If duration_ms = 1200: "Performance: Data loading took 1200ms"
```

---

## Configuration Management

### DashboardConfiguration

#### Constructor

```python
config = DashboardConfiguration(config_dict=None)
```

**Parameters:**
- `config_dict` (dict, optional): Override default settings

**Defaults:**
```python
DEFAULTS = {
    "window_width": 1400,
    "window_height": 900,
    "window_x": 80,
    "window_y": 60,
    "auto_save_interval": 300,  # seconds
    "async_timeout": 5000,      # ms
    "log_level": "INFO",
    "theme": "dark",
}
```

---

#### `get(key, default)`

**Description:** Get configuration value.

**Parameters:**
- `key` (str): Config key
- `default` (Any, optional): Default value if key not found

**Returns:** Configuration value or default

**Example:**
```python
config = DashboardConfiguration()
width = config.get("window_width")  # 1400
timeout = config.get("async_timeout")  # 5000
```

---

#### `set(key, value)`

**Description:** Set configuration value.

**Parameters:**
- `key` (str): Config key
- `value` (Any): New value

**Example:**
```python
config.set("window_width", 1920)
config.set("theme", "light")
```

---

#### `to_dict() -> dict`

**Description:** Convert configuration to dictionary.

**Returns:** Dictionary copy of config

**Example:**
```python
config_dict = config.to_dict()
# Save to JSON
import json
with open("dashboard_config.json", "w") as f:
    json.dump(config_dict, f)
```

---

## Usage Examples

### Example 1: Error Handling

```python
from app.gui.dashboard_utils import DashboardErrorHandler

try:
    result = risky_operation()
except Exception as e:
    DashboardErrorHandler.handle_exception(
        e,
        context="Data processing",
        show_dialog=True,
        parent=self
    )
```

---

### Example 2: Async Operation

```python
from app.gui.dashboard_utils import DashboardAsyncManager

manager = DashboardAsyncManager()

def load_large_file(path):
    # Simulated long operation
    time.sleep(10)
    with open(path) as f:
        return f.read()

def on_loaded(data):
    self.text_area.setText(data)
    QMessageBox.information(self, "Success", "File loaded!")

manager.run_async(
    "file_load",
    load_large_file,
    on_result=on_loaded,
    "large_data.txt"
)
```

---

### Example 3: Input Validation

```python
from app.gui.dashboard_utils import DashboardValidationManager

# Username validation
username = self.username_input.text()
is_valid, error = DashboardValidationManager.validate_username(username)
if not is_valid:
    QMessageBox.warning(self, "Validation Error", error)
    return

# Email validation
email = self.email_input.text()
is_valid, error = DashboardValidationManager.validate_email(email)
if not is_valid:
    QMessageBox.warning(self, "Validation Error", error)
    return

# Password validation
password = self.password_input.text()
is_valid, error = DashboardValidationManager.validate_password(password)
if not is_valid:
    QMessageBox.warning(self, "Validation Error", error)
    return

# All valid, proceed
self.create_account(username, email, password)
```

---

### Example 4: Performance Logging

```python
from app.gui.dashboard_utils import DashboardLogger
import time

logger = DashboardLogger("MyDashboard")

start = time.time()
result = expensive_operation()
duration_ms = (time.time() - start) * 1000

logger.log_performance("Expensive operation", duration_ms)
```

---

### Example 5: Configuration Management

```python
from app.gui.dashboard_utils import DashboardConfiguration

# Load defaults
config = DashboardConfiguration()

# Get values
width = config.get("window_width")  # 1400
height = config.get("window_height")  # 900

# Set window geometry
self.setGeometry(
    config.get("window_x"),
    config.get("window_y"),
    width,
    height
)

# Override defaults
custom_config = DashboardConfiguration({
    "window_width": 1920,
    "window_height": 1080,
    "theme": "light"
})
```

---

## Best Practices

### 1. Always Handle Exceptions

```python
# ✅ Good
try:
    operation()
except Exception as e:
    DashboardErrorHandler.handle_exception(e, context="Operation")

# ❌ Bad
operation()  # Unhandled exception crashes app
```

---

### 2. Validate All User Input

```python
# ✅ Good
is_valid, error = DashboardValidationManager.validate_username(username)
if not is_valid:
    show_error(error)
    return

# ❌ Bad
if len(username) > 0:  # Incomplete validation
    process(username)
```

---

### 3. Use Async for Long Operations

```python
# ✅ Good (non-blocking)
manager.run_async("task", long_operation, on_result=update_ui)

# ❌ Bad (blocks UI)
result = long_operation()  # UI freezes
update_ui(result)
```

---

### 4. Clean Up Async Tasks

```python
# ✅ Good
def closeEvent(self, event):
    self.async_manager.cancel_all_tasks()
    super().closeEvent(event)

# ❌ Bad (tasks continue running after window closes)
```

---

### 5. Log Important Operations

```python
# ✅ Good
logger.log_user_action(username, "Data export", {"format": "CSV"})

# ❌ Bad (no audit trail)
export_data()
```

---

## Performance Considerations

### Thread Pool Size

Default thread pool size: `QThreadPool.globalInstance().maxThreadCount()`  
Typically: Number of CPU cores

**Custom thread pool:**
```python
pool = QThreadPool()
pool.setMaxThreadCount(4)  # Limit to 4 threads
```

---

### Memory Usage

`AsyncWorker` instances are lightweight (~1KB each)

`DashboardAsyncManager` tracks tasks in dict (~200 bytes per task)

**Total overhead for 100 concurrent tasks:** ~120KB

---

## Related Documentation

- **[Dashboard Handlers](./dashboard_handlers.md)** - Event handlers
- **[Leather Book Dashboard](./leather_book_dashboard.md)** - Main dashboard
- **Security Validation** - `docs/SECURITY_VALIDATION.md`

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 2.0.0 | 2026-04-20 | Complete API documentation | AGENT-034 |
| 1.0.0 | 2026-02-15 | Initial implementation | GUI Team |

---

## License

**Copyright © 2026 Project-AI Team**  
Internal documentation - Not for public distribution

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

