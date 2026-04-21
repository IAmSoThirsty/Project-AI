# Dashboard Utilities Module

## Overview

The Dashboard Utilities module (`src/app/gui/dashboard_utils.py`) provides centralized utilities for PyQt6 dashboard operations, including error handling, async task management, input validation, and configuration management.

**Location**: `src/app/gui/dashboard_utils.py`  
**Lines of Code**: 256  
**Dependencies**: PyQt6, asyncio, logging

## Architecture

### Component Hierarchy

```
DashboardErrorHandler (Static Methods)
    ├── Exception handling with logging
    ├── Warning management
    └── Input validation

AsyncWorker (QRunnable)
    ├── Signals (QObject)
    │   ├── finished: pyqtSignal()
    │   ├── error: pyqtSignal(Exception)
    │   └── result: pyqtSignal(object)
    └── Thread execution

DashboardAsyncManager
    ├── Thread pool management
    ├── Task lifecycle tracking
    └── Timeout handling

DashboardValidationManager (Static Methods)
    ├── Username validation
    ├── Email validation
    ├── Password strength checking
    └── String sanitization

DashboardLogger
    └── Structured logging for dashboard operations

DashboardConfiguration
    └── Configuration management with defaults
```

## Core Components

### 1. DashboardErrorHandler

**Purpose**: Centralized error handling for dashboard operations with logging and optional user dialogs.

#### Methods

##### handle_exception()
```python
@staticmethod
def handle_exception(
    exception: Exception,
    context: str = "Operation",
    show_dialog: bool = True,
    parent=None,
) -> None
```

**Function**: Logs and optionally displays exception errors.

**Parameters**:
- `exception`: Exception to handle
- `context`: Contextual description (e.g., "Login", "Data Save")
- `show_dialog`: Whether to show QMessageBox.critical
- `parent`: Parent widget for dialog

**Example**:
```python
try:
    user_manager.authenticate(username, password)
except AuthError as e:
    DashboardErrorHandler.handle_exception(e, "Login", parent=self)
```

##### handle_warning()
```python
@staticmethod
def handle_warning(
    message: str,
    context: str = "Warning",
    show_dialog: bool = False,
    parent=None,
) -> None
```

**Function**: Logs warnings with optional user notification.

##### validate_input()
```python
@staticmethod
def validate_input(
    value: Any,
    input_type: type,
    required: bool = True,
    context: str = "Input",
) -> bool
```

**Function**: Validates user input against type and requirement constraints.

**Returns**: `True` if valid, `False` otherwise

**Example**:
```python
if not DashboardErrorHandler.validate_input(username, str, required=True, context="Username"):
    return  # Validation failed, warning already logged
```

---

### 2. AsyncWorker

**Purpose**: Thread-based worker for async operations in PyQt6 GUI.

**Pattern**: QRunnable with signal-based communication to avoid blocking the main thread.

#### Signals

```python
class Signals(QObject):
    finished = pyqtSignal()           # Emitted when task completes
    error = pyqtSignal(Exception)      # Emitted on error
    result = pyqtSignal(object)        # Emitted with result data
```

#### Usage Example

```python
# Define a long-running function
def fetch_data():
    time.sleep(5)
    return {"data": "fetched"}

# Create worker
worker = AsyncWorker(fetch_data)
worker.signals.result.connect(on_data_received)
worker.signals.error.connect(on_error)

# Start worker
QThreadPool.globalInstance().start(worker)
```

**Critical Note**: AsyncWorker is for synchronous functions that need to run in a background thread. For truly async functions, use QTimer or asyncio integration.

---

### 3. DashboardAsyncManager

**Purpose**: Manages multiple async tasks with lifecycle tracking and timeout support.

#### Key Methods

##### run_async()
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

**Function**: Runs a function asynchronously in the thread pool.

**Parameters**:
- `task_id`: Unique identifier for task tracking
- `func`: Function to execute
- `on_result`: Callback for successful result
- `on_error`: Callback for errors
- `*args, **kwargs`: Passed to func

**Example**:
```python
async_manager = DashboardAsyncManager()

def on_analysis_done(result):
    print(f"Analysis result: {result}")

async_manager.run_async(
    "analyze_data",
    data_analysis.analyze_csv,
    on_result=on_analysis_done,
    filepath="data.csv"
)
```

##### wait_for_task()
```python
def wait_for_task(self, task_id: str, timeout_ms: int = 5000) -> bool
```

**Function**: Blocks until task completes or timeout.

**Returns**: `True` if completed, `False` if timeout

**Warning**: This uses `asyncio.sleep()` which may not be correct for PyQt6. Consider using `QEventLoop` instead.

##### cancel_all_tasks()
```python
def cancel_all_tasks(self) -> None
```

**Function**: Clears thread pool and active task tracking.

**Use Case**: Application shutdown, page navigation

---

### 4. DashboardValidationManager

**Purpose**: Input validation and sanitization utilities.

#### Validation Methods

##### validate_username()
```python
@staticmethod
def validate_username(username: str) -> tuple[bool, str]
```

**Rules**:
- Minimum 3 characters
- Maximum 50 characters
- Alphanumeric + `-` and `_` only

**Returns**: `(is_valid, error_message)`

##### validate_email()
```python
@staticmethod
def validate_email(email: str) -> tuple[bool, str]
```

**Rules**:
- Contains `@` and `.`
- Non-empty local and domain parts
- Domain contains `.`

**Note**: This is basic validation. Production should use `email-validator` library.

##### validate_password()
```python
@staticmethod
def validate_password(password: str) -> tuple[bool, str]
```

**Rules**:
- Minimum 8 characters
- Contains uppercase letter
- Contains digit

**Security Note**: Missing lowercase, special character, and breach check. Consider upgrading.

##### sanitize_string()
```python
@staticmethod
def sanitize_string(value: str, max_length: int = 1000) -> str
```

**Function**: Removes control characters (except `\n`) and truncates to `max_length`.

**Example**:
```python
user_input = sanitize_string(raw_input, max_length=500)
```

---

### 5. DashboardLogger

**Purpose**: Enhanced logging with structured formats for dashboard operations.

#### Methods

##### log_operation()
```python
def log_operation(self, operation: str, details: dict = None) -> None
```

**Example**:
```python
logger = DashboardLogger("Dashboard")
logger.log_operation("UserLogin", {"username": "alice", "status": "success"})
# Output: Operation: UserLogin | {'username': 'alice', 'status': 'success'}
```

##### log_user_action()
```python
def log_user_action(self, user: str, action: str, details: dict = None) -> None
```

**Example**:
```python
logger.log_user_action("bob", "DeleteData", {"file": "test.csv"})
# Output: User 'bob' performed 'DeleteData' | {'file': 'test.csv'}
```

##### log_performance()
```python
def log_performance(self, operation: str, duration_ms: float) -> None
```

**Function**: Logs with severity based on duration:
- `debug` if < 500ms
- `info` if 500-1000ms
- `warning` if > 1000ms

---

### 6. DashboardConfiguration

**Purpose**: Configuration management with defaults and runtime updates.

#### Default Configuration

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

#### Methods

##### get()
```python
def get(self, key: str, default=None)
```

##### set()
```python
def set(self, key: str, value: Any) -> None
```

##### to_dict()
```python
def to_dict(self) -> dict
```

**Example**:
```python
config = DashboardConfiguration()
window_width = config.get("window_width")  # 1400
config.set("theme", "light")
config_dict = config.to_dict()
```

---

## Design Patterns

### 1. Static Utility Pattern
- `DashboardErrorHandler` and `DashboardValidationManager` use static methods
- No state needed
- Easy to use without instantiation

### 2. Signal-Slot Pattern (PyQt6)
- `AsyncWorker` uses signals for thread-safe communication
- Decouples worker from UI updates
- Follows Qt best practices

### 3. Manager Pattern
- `DashboardAsyncManager` manages lifecycle of multiple workers
- Tracks active tasks with dictionary
- Provides cleanup and cancellation

### 4. Configuration Object Pattern
- `DashboardConfiguration` encapsulates settings
- Allows runtime modification
- Provides defaults

---

## Integration Points

### With Main Dashboard
```python
from app.gui.dashboard_utils import (
    DashboardErrorHandler,
    DashboardAsyncManager,
    DashboardValidationManager,
)

class LeatherBookDashboard(QWidget):
    def __init__(self):
        self.async_manager = DashboardAsyncManager()
        
    def on_login_clicked(self):
        username = self.username_input.text()
        is_valid, msg = DashboardValidationManager.validate_username(username)
        if not is_valid:
            DashboardErrorHandler.handle_warning(msg, show_dialog=True, parent=self)
            return
```

### With Data Operations
```python
def load_large_dataset(filepath):
    # This will block for 10s
    time.sleep(10)
    return pd.read_csv(filepath)

self.async_manager.run_async(
    "load_csv",
    load_large_dataset,
    on_result=self.on_dataset_loaded,
    on_error=lambda e: DashboardErrorHandler.handle_exception(e, "Dataset Load"),
    filepath="large.csv"
)
```

---

## Testing Considerations

### Unit Tests

```python
def test_validate_username():
    # Valid
    assert DashboardValidationManager.validate_username("alice123") == (True, "")
    
    # Too short
    is_valid, msg = DashboardValidationManager.validate_username("ab")
    assert not is_valid
    assert "at least 3" in msg
    
    # Invalid characters
    is_valid, msg = DashboardValidationManager.validate_username("alice@home")
    assert not is_valid
```

### Integration Tests

```python
def test_async_manager():
    manager = DashboardAsyncManager()
    result_holder = []
    
    def task():
        return 42
    
    def on_result(r):
        result_holder.append(r)
    
    manager.run_async("test", task, on_result=on_result)
    assert manager.wait_for_task("test", timeout_ms=2000)
    assert result_holder[0] == 42
```

---

## Known Issues & Improvements

### Current Issues

1. **wait_for_task() uses asyncio.sleep()**:
   - Problem: May not work correctly in PyQt6 event loop
   - Fix: Use `QEventLoop` or `QTimer`

2. **Password validation is basic**:
   - Missing lowercase requirement
   - Missing special characters
   - No breach database check

3. **Email validation is regex-free**:
   - Only checks for `@` and `.`
   - Use `email-validator` library

### Suggested Improvements

```python
# Better wait_for_task implementation
def wait_for_task(self, task_id: str, timeout_ms: int = 5000) -> bool:
    from PyQt6.QtCore import QEventLoop, QTimer
    loop = QEventLoop()
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(loop.quit)
    timer.start(timeout_ms)
    
    while task_id in self.active_tasks and timer.isActive():
        loop.processEvents()
    
    return task_id not in self.active_tasks
```

---

## Performance Considerations

### Thread Pool Sizing

- Default `QThreadPool.globalInstance()` uses `QThread.idealThreadCount()` (typically 8-16)
- Consider custom pool for heavy workloads:

```python
self.thread_pool = QThreadPool()
self.thread_pool.setMaxThreadCount(4)  # Limit concurrent tasks
```

### Memory Management

- AsyncWorker instances are automatically deleted after completion
- DashboardAsyncManager holds references in `active_tasks`
- Call `cancel_all_tasks()` on application exit

---

## Security Considerations

1. **Input Sanitization**:
   - `sanitize_string()` only removes control characters
   - Does NOT prevent SQL injection (use parameterized queries)
   - Does NOT prevent XSS (not applicable to desktop app)

2. **Password Handling**:
   - Validation only checks strength
   - Actual password hashing is in `UserManager` (bcrypt)
   - Never log passwords

3. **Error Messages**:
   - Be careful with exception messages in dialogs
   - May expose internal paths or logic
   - Consider sanitizing error messages for production

---

## Usage Guidelines

### DO

✅ Use `DashboardErrorHandler.handle_exception()` for all exception handling  
✅ Validate all user input with `DashboardValidationManager`  
✅ Use `DashboardAsyncManager` for long-running operations (>100ms)  
✅ Call `cancel_all_tasks()` before page navigation or shutdown  
✅ Log user actions with `DashboardLogger`

### DON'T

❌ Don't use AsyncWorker for truly async (asyncio) functions  
❌ Don't forget to connect error signals  
❌ Don't show exception stack traces in dialogs (security risk)  
❌ Don't use `wait_for_task()` in production (broken implementation)  
❌ Don't rely on email validation for production (too basic)

---

## Related Documentation

- **LeatherBookDashboard**: Main dashboard implementation
- **LeatherBookInterface**: Main window and page management
- **UserManager**: Authentication and user management
- **PyQt6 Threading Guide**: https://doc.qt.io/qt-6/threads-qobject.html

---

## Version History

- **v1.0** (Current): Initial implementation with 5 utility classes
- **v0.9**: Added AsyncWorker and DashboardAsyncManager
- **v0.8**: Initial error handling and validation

---

## Contributors & Maintenance

**Primary Maintainer**: Desktop UI Team  
**Code Review**: Required for changes to error handling patterns  
**Testing**: Manual + automated (see `tests/test_dashboard_utils.py`)

---

**Last Updated**: 2025-01-24  
**Status**: Stable - Production Ready
