# GUI Error Handling Documentation

**Component**: PyQt6 GUI Error Handling  
**Last Updated**: 2025-01-23  
**Maintainer**: Error Handling Documentation Specialist  

---

## Overview

The GUI layer (`src/app/gui/`) implements a centralized error handling system for PyQt6 applications. This document covers exception handling patterns, user feedback mechanisms, async error recovery, and threading safety.

---

## Core Error Handling Components

### DashboardErrorHandler

**Module**: `src/app/gui/dashboard_utils.py`  
**Lines**: 14-62  
**Purpose**: Centralized error handling for all dashboard operations

```python
class DashboardErrorHandler:
    """Centralized error handling for dashboard operations."""
    
    @staticmethod
    def handle_exception(
        exception: Exception,
        context: str = "Operation",
        show_dialog: bool = True,
        parent=None,
    ) -> None:
        """Handle an exception with logging and optional dialog."""
        error_message = f"{context}: {str(exception)}"
        logger.error(error_message, exc_info=True)
        
        if show_dialog:
            QMessageBox.critical(parent, "Error", error_message)
```

**Key Features**:
- Logs all exceptions with full stack trace (`exc_info=True`)
- Optional user-facing dialog for critical errors
- Context-aware error messages
- Parent widget support for modal dialogs

---

### Usage Patterns

#### Pattern 1: Handle Exception with User Dialog

```python
from app.gui.dashboard_utils import DashboardErrorHandler

def on_button_clicked(self):
    """Handle button click with error handling."""
    try:
        result = self.perform_risky_operation()
        self.display_result(result)
    except Exception as e:
        DashboardErrorHandler.handle_exception(
            exception=e,
            context="Button Operation",
            show_dialog=True,
            parent=self
        )
```

**When to use**:
- User-initiated actions (button clicks, form submissions)
- Operations that directly affect visible UI state
- Critical errors that require user acknowledgment

---

#### Pattern 2: Silent Logging (No Dialog)

```python
def background_update(self):
    """Background update without interrupting user."""
    try:
        self.fetch_latest_data()
    except Exception as e:
        DashboardErrorHandler.handle_exception(
            exception=e,
            context="Background Data Sync",
            show_dialog=False  # Don't interrupt user
        )
```

**When to use**:
- Background tasks
- Periodic polling operations
- Non-critical feature updates

---

### Warning Handling

**Method**: `DashboardErrorHandler.handle_warning()`

```python
@staticmethod
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

**Usage Example**:
```python
# Validation warning
if len(username) < 3:
    DashboardErrorHandler.handle_warning(
        message="Username must be at least 3 characters",
        context="Input Validation",
        show_dialog=True,
        parent=self
    )
    return False
```

---

### Input Validation

**Method**: `DashboardErrorHandler.validate_input()`

```python
@staticmethod
def validate_input(
    value: Any,
    input_type: type,
    required: bool = True,
    context: str = "Input",
) -> bool:
    """Validate user input with automatic warning handling."""
    if required and (value is None or value == ""):
        DashboardErrorHandler.handle_warning(
            f"{context} is required", context
        )
        return False
    
    if value is not None and not isinstance(value, input_type):
        DashboardErrorHandler.handle_warning(
            f"{context} must be {input_type.__name__}",
            context,
        )
        return False
    
    return True
```

**Usage Example**:
```python
def submit_form(self):
    """Submit form with validation."""
    username = self.username_input.text()
    age = self.age_input.value()
    
    # Validate inputs
    if not DashboardErrorHandler.validate_input(
        username, str, required=True, context="Username"
    ):
        return
    
    if not DashboardErrorHandler.validate_input(
        age, int, required=True, context="Age"
    ):
        return
    
    # Proceed with submission
    self.user_manager.create_user(username, age)
```

---

## Async Error Handling

### AsyncWorker

**Module**: `src/app/gui/dashboard_utils.py`  
**Lines**: 65-92  
**Purpose**: Thread-safe async operations with error signaling

```python
class AsyncWorker(QRunnable):
    """Worker thread for async operations."""
    
    class Signals(QObject):
        """Signals for AsyncWorker."""
        finished = pyqtSignal()
        error = pyqtSignal(Exception)
        result = pyqtSignal(object)
    
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

**Key Features**:
- PyQt6 signal-based error propagation
- Prevents GUI freezing during long operations
- Thread-safe exception handling
- Automatic cleanup via `finished` signal

---

### DashboardAsyncManager

**Module**: `src/app/gui/dashboard_utils.py`  
**Lines**: 94-143  
**Purpose**: Manage multiple async tasks with error handling

```python
class DashboardAsyncManager:
    """Manager for async operations in dashboard."""
    
    def __init__(self):
        """Initialize async manager."""
        self.thread_pool = QThreadPool()
        self.active_tasks = {}
    
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
```

---

### Async Error Handling Example

```python
class MyDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.async_manager = DashboardAsyncManager()
    
    def load_data_async(self):
        """Load data asynchronously with error handling."""
        self.async_manager.run_async(
            task_id="data_load",
            func=self.fetch_data_from_api,
            on_result=self.handle_data_loaded,
            on_error=self.handle_data_error,
        )
    
    def fetch_data_from_api(self):
        """Fetch data (runs in worker thread)."""
        # This runs in background thread
        response = requests.get("https://api.example.com/data")
        response.raise_for_status()
        return response.json()
    
    def handle_data_loaded(self, data):
        """Handle successful data load (runs on main thread)."""
        self.data_table.populate(data)
        self.status_label.setText("Data loaded successfully")
    
    def handle_data_error(self, error: Exception):
        """Handle data load error (runs on main thread)."""
        DashboardErrorHandler.handle_exception(
            exception=error,
            context="Data Loading",
            show_dialog=True,
            parent=self
        )
        self.status_label.setText("Failed to load data")
```

**Critical Points**:
- `fetch_data_from_api()` runs in worker thread (can block)
- `handle_data_loaded()` runs on main thread (updates GUI)
- `handle_data_error()` runs on main thread (shows dialog)
- No direct GUI manipulation in worker thread

---

## Threading Safety Rules

### ⚠️ NEVER Update GUI from Worker Threads

```python
# ❌ WRONG: Direct GUI update from worker thread
def worker_function(self):
    data = fetch_data()
    self.label.setText(data)  # CRASH: Called from worker thread!

# ✅ CORRECT: Use signals to update GUI on main thread
def worker_function(self):
    data = fetch_data()
    return data  # Return via signal

def on_result(self, data):
    self.label.setText(data)  # Safe: Called on main thread
```

---

### ⚠️ Use QTimer for Delays (Not time.sleep)

```python
# ❌ WRONG: Blocks main thread
def delayed_action(self):
    time.sleep(2)  # Freezes entire GUI for 2 seconds!
    self.update_ui()

# ✅ CORRECT: Use QTimer.singleShot
from PyQt6.QtCore import QTimer

def delayed_action(self):
    QTimer.singleShot(2000, self.update_ui)  # Non-blocking delay
```

---

### ⚠️ Catch Exceptions in Signal Handlers

```python
# ❌ WRONG: Unhandled exception crashes event loop
def on_button_clicked(self):
    self.perform_risky_operation()  # May raise exception

# ✅ CORRECT: Wrap signal handlers in try-except
def on_button_clicked(self):
    try:
        self.perform_risky_operation()
    except Exception as e:
        DashboardErrorHandler.handle_exception(e, "Button Click", parent=self)
```

---

## Error Recovery Strategies

### Strategy 1: Retry with Exponential Backoff

```python
import time
from typing import Callable, Any

def retry_with_backoff(
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    on_retry: Callable | None = None,
) -> Any:
    """Retry function with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise  # Final attempt, re-raise exception
            
            delay = base_delay * (2 ** attempt)
            logger.warning(
                "Attempt %d failed: %s. Retrying in %.1fs",
                attempt + 1, e, delay
            )
            
            if on_retry:
                on_retry(attempt + 1, delay)
            
            time.sleep(delay)
```

**Usage in GUI**:
```python
def load_data_with_retry(self):
    """Load data with automatic retry."""
    try:
        data = retry_with_backoff(
            func=self.api_client.fetch_data,
            max_attempts=3,
            on_retry=lambda attempt, delay: self.status_label.setText(
                f"Retry attempt {attempt} in {delay:.0f}s..."
            )
        )
        self.display_data(data)
    except Exception as e:
        DashboardErrorHandler.handle_exception(
            e, "Data Loading", parent=self
        )
```

---

### Strategy 2: Graceful Degradation

```python
def load_dashboard_features(self):
    """Load dashboard features with graceful degradation."""
    # Core features (must succeed)
    try:
        self.load_user_profile()
        self.initialize_main_panels()
    except Exception as e:
        DashboardErrorHandler.handle_exception(
            e, "Dashboard Initialization", parent=self
        )
        # Cannot continue without core features
        self.close()
        return
    
    # Optional features (can fail gracefully)
    try:
        self.load_recent_activity()
    except Exception as e:
        logger.warning("Recent activity unavailable: %s", e)
        self.activity_panel.set_placeholder("Activity unavailable")
    
    try:
        self.load_statistics()
    except Exception as e:
        logger.warning("Statistics unavailable: %s", e)
        self.stats_panel.set_placeholder("Statistics unavailable")
```

---

### Strategy 3: User-Driven Recovery

```python
def save_document(self):
    """Save document with user-driven recovery."""
    try:
        self.document.save(self.file_path)
        self.status_bar.showMessage("Document saved", 3000)
    except PermissionError as e:
        # Offer to save in different location
        reply = QMessageBox.question(
            self,
            "Permission Denied",
            f"Cannot save to {self.file_path}. Save to different location?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.save_document_as()
    except Exception as e:
        DashboardErrorHandler.handle_exception(
            e, "Document Save", parent=self
        )
```

---

## Error Dialog Customization

### Custom Error Dialog

```python
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextEdit

class DetailedErrorDialog(QDialog):
    """Custom error dialog with expandable details."""
    
    def __init__(self, error: Exception, context: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Error")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Error summary
        summary = QLabel(f"{context}: {str(error)}")
        summary.setWordWrap(True)
        layout.addWidget(summary)
        
        # Expandable details
        self.details = QTextEdit()
        self.details.setReadOnly(True)
        self.details.setPlainText(
            f"Exception Type: {type(error).__name__}\n\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        self.details.setVisible(False)
        layout.addWidget(self.details)
        
        # Toggle details button
        self.toggle_btn = QPushButton("Show Details")
        self.toggle_btn.clicked.connect(self.toggle_details)
        layout.addWidget(self.toggle_btn)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def toggle_details(self):
        """Toggle visibility of error details."""
        visible = self.details.isVisible()
        self.details.setVisible(not visible)
        self.toggle_btn.setText("Hide Details" if not visible else "Show Details")
```

---

## Testing GUI Error Handling

### Test Structure

```python
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from unittest.mock import patch, MagicMock

@pytest.fixture
def app():
    """Create QApplication for tests."""
    return QApplication.instance() or QApplication([])

def test_error_dialog_shown_on_exception(app, qtbot):
    """Test that error dialog is shown when exception occurs."""
    from app.gui.my_widget import MyWidget
    
    widget = MyWidget()
    qtbot.addWidget(widget)
    
    # Mock the risky operation to raise exception
    with patch.object(widget, 'perform_operation') as mock_op:
        mock_op.side_effect = ValueError("Test error")
        
        # Trigger the operation
        with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_dialog:
            qtbot.mouseClick(widget.action_button, Qt.MouseButton.LeftButton)
            
            # Verify error dialog was shown
            mock_dialog.assert_called_once()
            args = mock_dialog.call_args[0]
            assert "Test error" in args[2]  # Error message
```

---

## Performance Considerations

### Avoid Synchronous Blocking

```python
# ❌ BAD: Blocks GUI for entire download
def download_large_file(self):
    data = requests.get(url).content  # Blocks for minutes!
    self.process_data(data)

# ✅ GOOD: Async download with progress
def download_large_file(self):
    self.progress_dialog = QProgressDialog("Downloading...", "Cancel", 0, 100, self)
    self.async_manager.run_async(
        task_id="download",
        func=self.download_with_progress,
        on_result=self.handle_download_complete,
        on_error=self.handle_download_error,
    )
```

---

## References

- **Main Implementation**: `src/app/gui/dashboard_utils.py`
- **Usage Examples**: `src/app/gui/leather_book_dashboard.py`
- **PyQt6 Threading**: [Qt Threading Basics](https://doc.qt.io/qt-6/thread-basics.html)
- **Signal/Slot Patterns**: `DEVELOPER_QUICK_REFERENCE.md` - GUI Component API section

---

**Next Steps**:
1. Implement centralized error reporting service
2. Add error analytics to track common failure patterns
3. Create user-friendly error message templates
4. Document error handling in GUI component style guide
