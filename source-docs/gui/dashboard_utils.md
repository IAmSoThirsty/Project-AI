# DashboardUtils - Error Handling & Async Operations

**Module:** `src/app/gui/dashboard_utils.py`  
**Lines of Code:** 256  
**Type:** PyQt6 Utility Classes & Helpers  
**Last Updated:** 2025-01-20

---

## Overview

`DashboardUtils` provides centralized error handling, asynchronous operation management, input validation, enhanced logging, and configuration management for dashboard components. It implements reusable patterns to maintain consistency across GUI operations.

### Design Philosophy

- **Centralization:** Single source of truth for error handling
- **Consistency:** Unified patterns for async operations
- **Reusability:** Shared validation and logging utilities
- **Separation:** UI logic separate from utility concerns

---

## Core Utility Classes

### 1. DashboardErrorHandler [[src/app/gui/dashboard_utils.py]]

**Purpose:** Centralized exception handling with logging and optional dialogs.

#### Static Methods

##### `handle_exception(exception, context, show_dialog, parent)`

**Signature:**
```python
@staticmethod
def handle_exception(
    exception: Exception,
    context: str = "Operation",
    show_dialog: bool = True,
    parent=None,
) -> None
```

**Purpose:** Handle exceptions with logging and optional user notification.

**Parameters:**
- `exception`: Exception object to handle
- `context`: Descriptive context (e.g., "Learning Path Generation")
- `show_dialog`: Show QMessageBox to user if True
- `parent`: Parent widget for dialog positioning

**Implementation:**
```python
def handle_exception(
    exception: Exception,
    context: str = "Operation",
    show_dialog: bool = True,
    parent=None,
) -> None:
    """Handle an exception with logging and optional dialog."""
    error_message = f"{context}: {str(exception)}"
    logger.error(error_message, exc_info=True)  # Full traceback
    
    if show_dialog:
        QMessageBox.critical(parent, "Error", error_message)
```

**Usage Example:**
```python
try:
    result = risky_operation()
except Exception as e:
    DashboardErrorHandler.handle_exception(
        e,
        context="Data Loading",
        show_dialog=True,
        parent=self
    )
```

---

##### `handle_warning(message, context, show_dialog, parent)`

**Signature:**
```python
@staticmethod
def handle_warning(
    message: str,
    context: str = "Warning",
    show_dialog: bool = False,
    parent=None,
) -> None
```

**Purpose:** Log warnings with optional user notification.

**Parameters:**
- `message`: Warning message text
- `context`: Warning context/category
- `show_dialog`: Show QMessageBox to user if True
- `parent`: Parent widget for dialog

**Implementation:**
```python
def handle_warning(
    message: str,
    context: str = "Warning",
    show_dialog: bool = False,
    parent=None,
) -> None:
    """Handle a warning with logging and optional dialog."""
    logger.warning("%s: %s", context, message)
    if show_dialog:
        QMessageBox.warning(parent, context, message)
```

**Usage Example:**
```python
if data_quality < 0.8:
    DashboardErrorHandler.handle_warning(
        "Data quality below threshold (80%)",
        context="Data Validation",
        show_dialog=True,
        parent=self
    )
```

---

##### `validate_input(value, input_type, required, context)`

**Signature:**
```python
@staticmethod
def validate_input(
    value: Any,
    input_type: type,
    required: bool = True,
    context: str = "Input",
) -> bool
```

**Purpose:** Validate input value type and presence.

**Parameters:**
- `value`: Input value to validate
- `input_type`: Expected Python type (str, int, float, etc.)
- `required`: If True, value cannot be None or empty
- `context`: Input field name for error messages

**Returns:** `True` if valid, `False` otherwise (logs warning)

**Implementation:**
```python
def validate_input(
    value: Any,
    input_type: type,
    required: bool = True,
    context: str = "Input",
) -> bool:
    """Validate user input."""
    if required and (value is None or value == ""):
        DashboardErrorHandler.handle_warning(f"{context} is required", context)
        return False
    
    if value is not None and not isinstance(value, input_type):
        DashboardErrorHandler.handle_warning(
            f"{context} must be {input_type.__name__}",
            context,
        )
        return False
    
    return True
```

**Usage Example:**
```python
username = username_field.text()
if not DashboardErrorHandler.validate_input(
    username,
    str,
    required=True,
    context="Username"
):
    return  # Validation failed, error logged
```

---

### 2. AsyncWorker [[src/app/gui/dashboard_utils.py]]

**Purpose:** QRunnable-based worker thread for async operations.

#### Architecture

```
┌──────────────────────────────────────────┐
│  AsyncWorker(QRunnable)                  │
│                                          │
│  - func: Callable                        │
│  - args: tuple                           │
│  - kwargs: dict                          │
│  - signals: Signals                      │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ Signals (QObject)                  │ │
│  │                                    │ │
│  │ - finished: pyqtSignal()           │ │
│  │ - error: pyqtSignal(Exception)     │ │
│  │ - result: pyqtSignal(object)       │ │
│  └────────────────────────────────────┘ │
│                                          │
│  run() → Execute func in thread          │
└──────────────────────────────────────────┘
```

#### Signals Class

```python
class Signals(QObject):
    """Signals for AsyncWorker."""
    
    finished = pyqtSignal()             # Emitted when work completes
    error = pyqtSignal(Exception)       # Emitted on exception
    result = pyqtSignal(object)         # Emits function result
```

#### Implementation

```python
class AsyncWorker(QRunnable):
    """Worker thread for async operations."""
    
    def __init__(self, func: Callable, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = self.Signals()
    
    def run(self):
        """Run the async function."""
        try:
            result = self.func(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            logger.error("AsyncWorker error: %s", e)
            self.signals.error.emit(e)
        finally:
            self.signals.finished.emit()
```

#### Usage Example

```python
# Create worker
def expensive_computation(data):
    time.sleep(5)  # Simulate long operation
    return process_data(data)

worker = AsyncWorker(expensive_computation, my_data)

# Connect signals
worker.signals.result.connect(on_result_received)
worker.signals.error.connect(on_error_occurred)
worker.signals.finished.connect(on_computation_done)

# Start in thread pool
QThreadPool.globalInstance().start(worker)
```

---

### 3. DashboardAsyncManager [[src/app/gui/dashboard_utils.py]]

**Purpose:** Centralized manager for dashboard async operations.

#### Attributes

```python
class DashboardAsyncManager:
    def __init__(self):
        self.thread_pool = QThreadPool()
        self.active_tasks = {}  # task_id -> worker mapping
```

#### Methods

##### `run_async(task_id, func, on_result, on_error, *args, **kwargs)`

**Signature:**
```python
def run_async(
    self,
    task_id: str,
    func: Callable,
    on_result: Callable | None = None,
    on_error: Callable | None = None,
    *args,
    **kwargs,
) -> None
```

**Purpose:** Execute function asynchronously with callbacks.

**Parameters:**
- `task_id`: Unique task identifier (for tracking)
- `func`: Function to execute in thread
- `on_result`: Callback for successful result
- `on_error`: Callback for exceptions
- `*args, **kwargs`: Function arguments

**Implementation:**
```python
def run_async(
    self,
    task_id: str,
    func: Callable,
    on_result: Callable | None = None,
    on_error: Callable | None = None,
    *args,
    **kwargs,
) -> None:
    """Run a function asynchronously in thread pool."""
    worker = AsyncWorker(func, *args, **kwargs)
    
    if on_result:
        worker.signals.result.connect(on_result)
    if on_error:
        worker.signals.error.connect(on_error)
    
    def on_finished():
        self.active_tasks.pop(task_id, None)
        logger.debug("Async task %s finished", task_id)
    
    worker.signals.finished.connect(on_finished)
    self.active_tasks[task_id] = worker
    self.thread_pool.start(worker)
    logger.debug("Started async task %s", task_id)
```

**Usage Example:**
```python
# Initialize manager
async_manager = DashboardAsyncManager()

# Define callbacks
def on_result(result):
    self.display_result(result)

def on_error(exception):
    QMessageBox.critical(self, "Error", str(exception))

# Run async task
async_manager.run_async(
    task_id="learning_path_gen",
    func=generate_learning_path,
    on_result=on_result,
    on_error=on_error,
    interest="Python",
    skill_level="beginner"
)
```

---

##### `wait_for_task(task_id, timeout_ms)`

**Signature:**
```python
def wait_for_task(self, task_id: str, timeout_ms: int = 5000) -> bool
```

**Purpose:** Block until specific task completes or timeout.

**Parameters:**
- `task_id`: Task identifier to wait for
- `timeout_ms`: Maximum wait time in milliseconds

**Returns:** `True` if completed, `False` if timeout

**Implementation:**
```python
def wait_for_task(self, task_id: str, timeout_ms: int = 5000) -> bool:
    """Wait for a specific task to complete."""
    start_time = 0
    while task_id in self.active_tasks:
        if start_time > timeout_ms:
            logger.warning("Task %s timeout after %sms", task_id, timeout_ms)
            return False
        asyncio.sleep(0.1)
        start_time += 100
    return True
```

---

##### `cancel_all_tasks()`

**Purpose:** Cancel all active async tasks.

**Implementation:**
```python
def cancel_all_tasks(self) -> None:
    """Cancel all active tasks."""
    self.thread_pool.clear()
    self.active_tasks.clear()
    logger.info("All async tasks cancelled")
```

---

### 4. DashboardValidationManager

**Purpose:** Specialized input validation for common dashboard fields.

#### Static Methods

##### `validate_username(username)`

**Signature:**
```python
@staticmethod
def validate_username(username: str) -> tuple[bool, str]
```

**Purpose:** Validate username format and length.

**Rules:**
- Minimum 3 characters
- Maximum 50 characters
- Alphanumeric + hyphens + underscores only

**Returns:** `(is_valid, error_message)`

**Implementation:**
```python
def validate_username(username: str) -> tuple[bool, str]:
    """Validate username format."""
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 50:
        return False, "Username must be less than 50 characters"
    if not username.replace("_", "").replace("-", "").isalnum():
        return False, "Username can only contain alphanumeric characters, - and _"
    return True, ""
```

---

##### `validate_email [[src/app/security/data_validation.py]](email)`

**Signature:**
```python
@staticmethod
def validate_email(email: str) -> tuple[bool, str]
```

**Purpose:** Validate email format.

**Rules:**
- Must contain @ symbol
- Must have domain with .
- Local and domain parts required

**Returns:** `(is_valid, error_message)`

**Implementation:**
```python
def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format."""
    if "@" not in email or "." not in email:
        return False, "Invalid email format"
    local, domain = email.rsplit("@", 1)
    if not local or not domain or "." not in domain:
        return False, "Invalid email format"
    return True, ""
```

---

##### `validate_password(password)`

**Signature:**
```python
@staticmethod
def validate_password(password: str) -> tuple[bool, str]
```

**Purpose:** Validate password strength.

**Rules:**
- Minimum 8 characters
- Must contain uppercase letter
- Must contain digit

**Returns:** `(is_valid, error_message)`

**Implementation:**
```python
def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain uppercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain digit"
    return True, ""
```

---

##### `sanitize_string(value, max_length)`

**Signature:**
```python
@staticmethod
def sanitize_string(value: str, max_length: int = 1000) -> str
```

**Purpose:** Remove control characters and limit length.

**Parameters:**
- `value`: Input string
- `max_length`: Maximum allowed length

**Returns:** Sanitized string

**Implementation:**
```python
def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize string input."""
    if not value:
        return ""
    # Remove control characters (except newline)
    cleaned = "".join(char for char in value if ord(char) >= 32 or char == "\n")
    # Limit length
    return cleaned[:max_length]
```

---

### 5. DashboardLogger

**Purpose:** Enhanced logging with operation tracking and performance metrics.

#### Initialization

```python
class DashboardLogger:
    def __init__(self, name: str = "Dashboard"):
        self.logger = logging.getLogger(name)
```

#### Methods

##### `log_operation(operation, details)`

**Purpose:** Log dashboard operation with optional metadata.

```python
def log_operation(self, operation: str, details: dict = None) -> None:
    """Log a dashboard operation."""
    msg = f"Operation: {operation}"
    if details:
        msg += f" | {details}"
    self.logger.info(msg)
```

**Usage:**
```python
logger = DashboardLogger("Dashboard")
logger.log_operation("LoadDataFile", {"file": "data.csv", "rows": 1000})
```

---

##### `log_user_action(user, action, details)`

**Purpose:** Log user-initiated actions with context.

```python
def log_user_action(self, user: str, action: str, details: dict = None) -> None:
    """Log a user action."""
    msg = f"User '{user}' performed '{action}'"
    if details:
        msg += f" | {details}"
    self.logger.info(msg)
```

**Usage:**
```python
logger.log_user_action(
    "john_doe",
    "GenerateLearningPath",
    {"interest": "Python", "level": "beginner"}
)
```

---

##### `log_performance(operation, duration_ms)`

**Purpose:** Log operation performance with automatic severity.

**Severity Rules:**
- > 1000ms: WARNING (red flag)
- > 500ms: INFO (yellow flag)
- ≤ 500ms: DEBUG (acceptable)

```python
def log_performance(self, operation: str, duration_ms: float) -> None:
    """Log operation performance."""
    if duration_ms > 1000:
        level = self.logger.warning
    elif duration_ms > 500:
        level = self.logger.info
    else:
        level = self.logger.debug
    level(f"Performance: {operation} took {duration_ms:.0f}ms")
```

**Usage:**
```python
start = time.time()
result = expensive_operation()
duration = (time.time() - start) * 1000
logger.log_performance("DataAnalysis", duration)
```

---

### 6. DashboardConfiguration

**Purpose:** Centralized configuration management with defaults.

#### Default Settings

```python
DEFAULTS = {
    "window_width": 1400,
    "window_height": 900,
    "window_x": 80,
    "window_y": 60,
    "auto_save_interval": 300,  # seconds
    "async_timeout": 5000,  # ms
    "log_level": "INFO",
    "theme": "dark",
}
```

#### Methods

##### `get(key, default)`

**Purpose:** Get configuration value with fallback.

```python
def get(self, key: str, default=None):
    """Get configuration value."""
    return self.config.get(key, default)
```

##### `set(key, value)`

**Purpose:** Set configuration value.

```python
def set(self, key: str, value: Any) -> None:
    """Set configuration value."""
    self.config[key] = value
```

**Usage:**
```python
config = DashboardConfiguration()
width = config.get("window_width")  # 1400
config.set("window_width", 1920)
```

---

## Usage Patterns

### Pattern 1: Error-Safe Operation

```python
def load_data_file(self):
    """Load file with comprehensive error handling."""
    try:
        file_path = self.get_file_path()
        if not file_path:
            return
        
        # Validate input
        if not DashboardErrorHandler.validate_input(
            file_path,
            str,
            required=True,
            context="File Path"
        ):
            return
        
        # Perform operation
        data = self.data_analyzer.load_data(file_path)
        self.display_data(data)
        
    except Exception as e:
        DashboardErrorHandler.handle_exception(
            e,
            context="Data Loading",
            show_dialog=True,
            parent=self
        )
```

---

### Pattern 2: Async Operation with Progress

```python
def generate_learning_path(self):
    """Generate path asynchronously."""
    interest = self.interest_input.text()
    
    # Validate input
    if not DashboardErrorHandler.validate_input(interest, str, True, "Interest"):
        return
    
    # Progress callback
    def on_result(path):
        self.path_display.setText(path)
        QMessageBox.information(self, "Success", "Learning path generated")
    
    def on_error(exception):
        DashboardErrorHandler.handle_exception(
            exception,
            context="Learning Path Generation",
            show_dialog=True,
            parent=self
        )
    
    # Run async
    self.async_manager.run_async(
        task_id="learning_path",
        func=self.learning_manager.generate_path,
        on_result=on_result,
        on_error=on_error,
        interest=interest,
        skill_level="beginner"
    )
```

---

### Pattern 3: Performance Monitoring

```python
def perform_analysis(self):
    """Analyze data with performance logging."""
    logger = DashboardLogger("DataAnalysis")
    
    start = time.time()
    try:
        result = self.data_analyzer.analyze()
        duration = (time.time() - start) * 1000
        
        logger.log_performance("DataAnalysis", duration)
        logger.log_operation("Analysis Complete", {"rows": len(result)})
        
        return result
    except Exception as e:
        DashboardErrorHandler.handle_exception(e, "Analysis")
```

---

## Testing Considerations

### Unit Tests

```python
def test_error_handler_validation():
    """Test input validation."""
    assert DashboardErrorHandler.validate_input("test", str, True, "Test")
    assert not DashboardErrorHandler.validate_input("", str, True, "Required")
    assert not DashboardErrorHandler.validate_input(123, str, True, "String")

def test_async_worker_result():
    """Test async worker emits result."""
    def test_func():
        return 42
    
    worker = AsyncWorker(test_func)
    spy = QSignalSpy(worker.signals.result)
    
    worker.run()
    
    assert spy.count() == 1
    assert spy[0] == [42]

def test_validation_manager_username():
    """Test username validation."""
    is_valid, msg = DashboardValidationManager.validate_username("john_doe")
    assert is_valid
    
    is_valid, msg = DashboardValidationManager.validate_username("ab")
    assert not is_valid
    assert "3 characters" in msg
```

---

## Cross-References

- **Dashboard Handlers:** See `dashboard_handlers.md`
- **Error Handling:** See `DEVELOPER_QUICK_REFERENCE.md` (Section 5)
- **Async Patterns:** See PyQt6 documentation (QThreadPool)

---

**Document Status:** ✅ Complete  
**Code Coverage:** 100% (all utilities documented)  
**Last Reviewed:** 2025-01-20 by AGENT-032


---


---

## 📚 Related Documentation

### Cross-References

- [[relationships/gui/04_UTILS_RELATIONSHIPS.md|04 Utils Relationships]]

## 🔗 Source Code References

This documentation references the following GUI source files:

- [[src/app/gui/dashboard_utils.py]] - Implementation file
