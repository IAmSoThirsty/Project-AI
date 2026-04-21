# Utils Relationships Map

## Component: DashboardUtils
**File:** `src/app/gui/dashboard_utils.py`  
**Lines:** 150+  
**Role:** Error handling, async operations, validation utilities

---

## 1. ARCHITECTURE OVERVIEW

### Three Core Utility Classes
```
dashboard_utils.py
├── DashboardErrorHandler (Static methods)
│   ├── handle_exception()
│   ├── handle_warning()
│   └── validate_input()
│
├── AsyncWorker (QRunnable)
│   ├── Signals (QObject)
│   │   ├── finished
│   │   ├── error
│   │   └── result
│   └── run()
│
└── DashboardAsyncManager
    ├── thread_pool (QThreadPool)
    ├── active_tasks (dict)
    ├── run_async()
    ├── cancel_task()
    └── cancel_all_tasks()
```

---

## 2. DASHBOARDERRORHANDLER RELATIONSHIPS

### Class Definition
```python
class DashboardErrorHandler:
    """Centralized error handling for dashboard operations."""
    # Lines 14-63
```

### Static Methods Inventory

#### 2.1 handle_exception()
```python
@staticmethod
def handle_exception(
    exception: Exception,
    context: str = "Operation",
    show_dialog: bool = True,
    parent=None,
) -> None:
    """Handle an exception with logging and optional dialog."""
    # Lines 18-29
```

**Flow:**
```
Exception occurs in dashboard operation
        ↓
Call handle_exception(e, context="Learning Path Generation")
        ↓
Format error message: f"{context}: {str(exception)}"
        ↓
Log error with traceback: logger.error(error_message, exc_info=True)
        ↓
If show_dialog == True:
└── QMessageBox.critical(parent, "Error", error_message)
```

**Usage Examples:**
```python
# In handlers
try:
    result = adapter.execute("learning.generate_path", params)
except Exception as e:
    DashboardErrorHandler.handle_exception(
        e,
        context="Learning Path Generation",
        show_dialog=True,
        parent=self,
    )
```

---

#### 2.2 handle_warning()
```python
@staticmethod
def handle_warning(
    message: str,
    context: str = "Warning",
    show_dialog: bool = False,
    parent=None,
) -> None:
    """Handle a warning with logging and optional dialog."""
    # Lines 31-42
```

**Flow:**
```
Warning condition detected
        ↓
Call handle_warning(message, context="Input Validation")
        ↓
Log warning: logger.warning("%s: %s", context, message)
        ↓
If show_dialog == True:
└── QMessageBox.warning(parent, context, message)
```

**Usage Examples:**
```python
# Input validation warnings
if len(user_input) > MAX_LENGTH:
    DashboardErrorHandler.handle_warning(
        f"Input exceeds {MAX_LENGTH} characters",
        context="User Input",
        show_dialog=True,
        parent=self,
    )
```

---

#### 2.3 validate_input()
```python
@staticmethod
def validate_input(
    value: Any,
    input_type: type,
    required: bool = True,
    context: str = "Input",
) -> bool:
    """Validate user input."""
    # Lines 44-63
```

**Flow:**
```
User input received
        ↓
Call validate_input(value, str, required=True, context="Username")
        ↓
Check 1: If required and (value is None or value == ""):
    ├── handle_warning(f"{context} is required", context)
    └── return False
        ↓
Check 2: If value is not None and not isinstance(value, input_type):
    ├── handle_warning(f"{context} must be {input_type.__name__}", context)
    └── return False
        ↓
All checks passed:
└── return True
```

**Usage Examples:**
```python
# Validate string input
if not DashboardErrorHandler.validate_input(
    username,
    str,
    required=True,
    context="Username",
):
    return  # Invalid, don't proceed

# Validate integer input
if not DashboardErrorHandler.validate_input(
    age,
    int,
    required=False,
    context="Age",
):
    return
```

---

### Error Handler Integration Pattern

#### In Handlers
```python
from app.gui.dashboard_utils import DashboardErrorHandler

def generate_learning_path(self):
    try:
        # Validate input
        interest = self.interest_input.text()
        if not DashboardErrorHandler.validate_input(
            interest, str, required=True, context="Interest"
        ):
            return
        
        # Execute operation
        result = self.adapter.execute("learning.generate_path", {})
        
    except Exception as e:
        DashboardErrorHandler.handle_exception(
            e,
            context="Learning Path Generation",
            parent=self,
        )
```

#### In Panels
```python
def _send_message(self):
    try:
        message = self.chat_input.toPlainText()
        
        # Validate before processing
        if not DashboardErrorHandler.validate_input(
            message, str, required=True, context="Message"
        ):
            return
        
        self.message_sent.emit(message)
        
    except Exception as e:
        DashboardErrorHandler.handle_exception(
            e,
            context="Message Sending",
            parent=self,
        )
```

---

## 3. ASYNCWORKER RELATIONSHIPS

### Class Definition
```python
class AsyncWorker(QRunnable):
    """Worker thread for async operations."""
    # Lines 65-92
```

### Signal Definitions
```python
class Signals(QObject):
    """Signals for AsyncWorker."""
    finished = pyqtSignal()
    error = pyqtSignal(Exception)
    result = pyqtSignal(object)
```

### Execution Flow
```
Dashboard initiates async operation
        ↓
Create AsyncWorker(func, *args, **kwargs)
        ↓
Connect signals:
├── worker.signals.result.connect(on_success)
├── worker.signals.error.connect(on_error)
└── worker.signals.finished.connect(on_complete)
        ↓
QThreadPool.start(worker)
        ↓
Worker.run() executes in background thread
        ↓
If success:
    ├── signals.result.emit(result)
    └── signals.finished.emit()
If error:
    ├── logger.error("AsyncWorker error: %s", e)
    ├── signals.error.emit(exception)
    └── signals.finished.emit()
```

### Usage Pattern
```python
from app.gui.dashboard_utils import AsyncWorker

def generate_learning_path_async(self):
    def worker_func():
        # Long-running operation
        return self.learning_manager.generate_path(interest, skill_level)
    
    def on_result(result):
        self.learning_path_display.setText(result)
    
    def on_error(exception):
        DashboardErrorHandler.handle_exception(
            exception,
            context="Async Learning Path Generation",
            parent=self,
        )
    
    def on_finished():
        self.generate_button.setEnabled(True)
    
    # Create worker
    worker = AsyncWorker(worker_func)
    worker.signals.result.connect(on_result)
    worker.signals.error.connect(on_error)
    worker.signals.finished.connect(on_finished)
    
    # Disable button during processing
    self.generate_button.setEnabled(False)
    
    # Start async execution
    QThreadPool.globalInstance().start(worker)
```

---

## 4. DASHBOARDASYNCMANAGER RELATIONSHIPS

### Class Definition
```python
class DashboardAsyncManager:
    """Manager for async operations in dashboard."""
    # Lines 94-150+
```

### Instance Variables
```python
self.thread_pool: QThreadPool  # Managed thread pool
self.active_tasks: dict  # {task_id: worker_reference}
```

### Methods

#### 4.1 run_async()
```python
def run_async(
    self,
    func: Callable,
    on_result: Callable | None = None,
    on_error: Callable | None = None,
    on_finished: Callable | None = None,
    task_id: str | None = None,
) -> str:
    """Run function asynchronously with callbacks."""
```

**Flow:**
```
Call run_async(func, on_result, on_error, on_finished, task_id)
        ↓
Generate task_id if not provided: f"task_{uuid.uuid4()}"
        ↓
Create AsyncWorker(func)
        ↓
Connect signals if callbacks provided:
├── If on_result: worker.signals.result.connect(on_result)
├── If on_error: worker.signals.error.connect(on_error)
└── If on_finished: worker.signals.finished.connect(on_finished)
        ↓
Store in active_tasks: self.active_tasks[task_id] = worker
        ↓
Start worker: self.thread_pool.start(worker)
        ↓
Return task_id
```

**Usage:**
```python
async_manager = DashboardAsyncManager()

task_id = async_manager.run_async(
    func=lambda: self.learning_manager.generate_path("Python", "beginner"),
    on_result=lambda result: self.display.setText(result),
    on_error=lambda e: print(f"Error: {e}"),
    on_finished=lambda: self.button.setEnabled(True),
    task_id="learning_path_gen",
)
```

---

#### 4.2 cancel_task()
```python
def cancel_task(self, task_id: str) -> bool:
    """Cancel a specific async task."""
```

**Flow:**
```
Call cancel_task("learning_path_gen")
        ↓
Check if task_id in self.active_tasks:
├── If yes:
│   ├── Remove from active_tasks
│   ├── Note: Worker may still complete (no hard interrupt)
│   └── return True
└── If no:
    └── return False
```

---

#### 4.3 cancel_all_tasks()
```python
def cancel_all_tasks(self) -> int:
    """Cancel all active async tasks."""
```

**Flow:**
```
Call cancel_all_tasks()
        ↓
Count active tasks: count = len(self.active_tasks)
        ↓
Clear all tasks: self.active_tasks.clear()
        ↓
Return count of cancelled tasks
```

**Usage:**
```python
# On dashboard close
def closeEvent(self, event):
    cancelled = self.async_manager.cancel_all_tasks()
    logger.info(f"Cancelled {cancelled} async tasks")
    event.accept()
```

---

## 5. INTEGRATION WITH HANDLERS

### Handler Using Error Handler
```python
# In dashboard_handlers.py
from app.gui.dashboard_utils import DashboardErrorHandler

class DashboardHandlers:
    def load_data_file(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(...)
            
            # Validate file path
            if not DashboardErrorHandler.validate_input(
                file_path, str, required=True, context="File Path"
            ):
                return
            
            # Load file
            if not self.data_analyzer.load_data(file_path):
                DashboardErrorHandler.handle_warning(
                    "Failed to load data file",
                    context="Data Loading",
                    show_dialog=True,
                    parent=self,
                )
                return
            
            # Success
            self.show_basic_stats()
            
        except Exception as e:
            DashboardErrorHandler.handle_exception(
                e,
                context="Data File Loading",
                parent=self,
            )
```

---

### Handler Using AsyncWorker
```python
# In dashboard_handlers.py
from app.gui.dashboard_utils import AsyncWorker, DashboardErrorHandler

class DashboardHandlers:
    def generate_learning_path_async(self):
        interest = self.interest_input.text()
        skill_level = self.skill_level.currentText()
        
        # Validate input
        if not DashboardErrorHandler.validate_input(
            interest, str, required=True, context="Interest"
        ):
            return
        
        # Define worker function
        def worker_func():
            return self.learning_manager.generate_path(interest, skill_level)
        
        # Define callbacks
        def on_result(result):
            self.learning_path_display.setText(result)
        
        def on_error(exception):
            DashboardErrorHandler.handle_exception(
                exception,
                context="Learning Path Generation",
                parent=self,
            )
        
        def on_finished():
            self.generate_button.setEnabled(True)
            self.progress_bar.setVisible(False)
        
        # Create and start worker
        worker = AsyncWorker(worker_func)
        worker.signals.result.connect(on_result)
        worker.signals.error.connect(on_error)
        worker.signals.finished.connect(on_finished)
        
        # Update UI
        self.generate_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        # Start
        QThreadPool.globalInstance().start(worker)
```

---

### Handler Using AsyncManager
```python
# In dashboard class
from app.gui.dashboard_utils import DashboardAsyncManager, DashboardErrorHandler

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.async_manager = DashboardAsyncManager()
    
    def generate_learning_path(self):
        interest = self.interest_input.text()
        
        if not DashboardErrorHandler.validate_input(
            interest, str, required=True
        ):
            return
        
        task_id = self.async_manager.run_async(
            func=lambda: self.learning_manager.generate_path(interest, "beginner"),
            on_result=lambda r: self.learning_path_display.setText(r),
            on_error=lambda e: DashboardErrorHandler.handle_exception(e, parent=self),
            on_finished=lambda: self.generate_button.setEnabled(True),
            task_id="learning_path_gen",
        )
        
        self.current_task_id = task_id
        self.generate_button.setEnabled(False)
    
    def cancel_generation(self):
        if hasattr(self, 'current_task_id'):
            self.async_manager.cancel_task(self.current_task_id)
    
    def closeEvent(self, event):
        self.async_manager.cancel_all_tasks()
        event.accept()
```

---

## 6. RELATIONSHIPS WITH OTHER COMPONENTS

### Error Handler → Handlers
```
Handlers import DashboardErrorHandler
        ↓
Use for:
├── Input validation before processing
├── Exception handling in try/except blocks
├── Warning messages for non-critical issues
└── Consistent error logging
```

### AsyncWorker → Handlers
```
Handlers create AsyncWorker instances
        ↓
Use for:
├── Long-running operations (OpenAI calls, file processing)
├── Preventing UI freezing during computation
├── Progress feedback via signals
└── Error handling in background threads
```

### AsyncManager → Dashboard
```
Dashboard creates DashboardAsyncManager instance
        ↓
Use for:
├── Managing multiple concurrent async tasks
├── Task cancellation (user-initiated or on close)
├── Task tracking and monitoring
└── Cleanup on dashboard destruction
```

---

## 7. SIGNAL/SLOT ARCHITECTURE

### AsyncWorker Signals
```python
# Signal definitions
finished = pyqtSignal()  # Always emitted
error = pyqtSignal(Exception)  # On exception
result = pyqtSignal(object)  # On success

# Connection pattern
worker.signals.result.connect(on_success)
worker.signals.error.connect(on_error)
worker.signals.finished.connect(on_complete)
```

### Signal Flow Example
```
AsyncWorker.run() starts
        ↓
Try to execute self.func(*args, **kwargs)
        ↓
PATH 1: Success
    ├── result = func(*args)
    ├── signals.result.emit(result)  → on_result callback
    └── signals.finished.emit()      → on_finished callback

PATH 2: Exception
    ├── exception caught
    ├── logger.error("AsyncWorker error: %s", e)
    ├── signals.error.emit(e)         → on_error callback
    └── signals.finished.emit()       → on_finished callback
```

---

## 8. THREAD SAFETY CONSIDERATIONS

### QThreadPool Usage
```python
# Thread pool is thread-safe
QThreadPool.globalInstance()  # Singleton, safe to call from any thread
thread_pool.start(worker)     # Thread-safe enqueue
```

### Signal Emission (Thread-Safe)
```python
# PyQt6 signals are thread-safe
self.signals.result.emit(result)  # Safe from worker thread
# Signal delivered to main thread via event loop
```

### UI Updates (Main Thread Only)
```python
# CORRECT: Update UI in signal callback (main thread)
worker.signals.result.connect(lambda r: self.label.setText(r))

# WRONG: Update UI directly in worker thread
def run(self):
    result = self.func()
    self.parent.label.setText(result)  # UNSAFE!
```

---

## 9. ERROR HANDLING BEST PRACTICES

### Pattern 1: Validate → Execute → Handle
```python
def handler_method(self):
    # 1. Validate
    if not DashboardErrorHandler.validate_input(
        value, str, required=True
    ):
        return
    
    # 2. Execute
    try:
        result = self.execute_operation(value)
    except Exception as e:
        # 3. Handle
        DashboardErrorHandler.handle_exception(
            e, context="Operation", parent=self
        )
        return
    
    # 4. Update UI
    self.display.setText(result)
```

### Pattern 2: Async Error Propagation
```python
def async_operation(self):
    def on_error(exception):
        DashboardErrorHandler.handle_exception(
            exception,
            context="Async Operation",
            parent=self,
        )
    
    worker = AsyncWorker(self.long_running_task)
    worker.signals.error.connect(on_error)
    worker.signals.result.connect(self.on_success)
    QThreadPool.globalInstance().start(worker)
```

---

## 10. LOGGING INTEGRATION

### Error Handler Logging
```python
# In handle_exception()
logger.error(error_message, exc_info=True)
# Logs full traceback for debugging

# In handle_warning()
logger.warning("%s: %s", context, message)
# Logs warning with context
```

### AsyncWorker Logging
```python
# In AsyncWorker.run()
except Exception as e:
    logger.error("AsyncWorker error: %s", e)
    self.signals.error.emit(e)
```

### Usage in Application
```python
import logging
logger = logging.getLogger(__name__)

# All errors logged automatically via DashboardErrorHandler
# Additional context logging:
logger.info("Starting learning path generation for user: %s", username)
logger.debug("Adapter response: %s", response)
```

---

## 11. TESTING STRATEGIES

### Unit Tests for Error Handler
```python
def test_handle_exception_logging(caplog):
    """Test exception logging."""
    exception = ValueError("Test error")
    DashboardErrorHandler.handle_exception(
        exception,
        context="Test Context",
        show_dialog=False,
    )
    assert "Test Context: Test error" in caplog.text

def test_validate_input_required():
    """Test required input validation."""
    assert not DashboardErrorHandler.validate_input(None, str, required=True)
    assert not DashboardErrorHandler.validate_input("", str, required=True)
    assert DashboardErrorHandler.validate_input("value", str, required=True)

def test_validate_input_type():
    """Test type validation."""
    assert not DashboardErrorHandler.validate_input("123", int)
    assert DashboardErrorHandler.validate_input(123, int)
```

### Unit Tests for AsyncWorker
```python
def test_async_worker_success():
    """Test successful async execution."""
    def worker_func():
        return "Success"
    
    worker = AsyncWorker(worker_func)
    
    result_received = []
    worker.signals.result.connect(result_received.append)
    
    worker.run()
    assert result_received == ["Success"]

def test_async_worker_error():
    """Test error handling in async execution."""
    def worker_func():
        raise ValueError("Test error")
    
    worker = AsyncWorker(worker_func)
    
    errors_received = []
    worker.signals.error.connect(errors_received.append)
    
    worker.run()
    assert len(errors_received) == 1
    assert isinstance(errors_received[0], ValueError)
```

---

## 12. PERFORMANCE CONSIDERATIONS

### Thread Pool Configuration
```python
# Default thread pool (auto-sized)
QThreadPool.globalInstance()  # maxThreadCount() = CPU cores

# Custom thread pool
custom_pool = QThreadPool()
custom_pool.setMaxThreadCount(4)  # Limit concurrent tasks

# In DashboardAsyncManager
self.thread_pool = QThreadPool()
self.thread_pool.setMaxThreadCount(8)  # Configure as needed
```

### Task Cleanup
```python
# Always clean up on close
def closeEvent(self, event):
    # Cancel all async tasks
    self.async_manager.cancel_all_tasks()
    
    # Wait for thread pool to finish (with timeout)
    self.async_manager.thread_pool.waitForDone(5000)  # 5 seconds
    
    event.accept()
```

---

## SUMMARY

**DashboardUtils** provides 3 essential utility systems:

1. **DashboardErrorHandler** [[src/app/gui/dashboard_utils.py]]: Centralized error handling
   - Static methods for exception/warning handling
   - Input validation with type checking
   - Consistent logging and UI feedback
   - Used by: All handlers and panels

2. **AsyncWorker** [[src/app/gui/dashboard_utils.py]]: Background task execution
   - Thread-safe async operations
   - Signal-based result/error propagation
   - Prevents UI freezing during long operations
   - Used by: Handlers for OpenAI calls, file I/O

3. **DashboardAsyncManager** [[src/app/gui/dashboard_utils.py]]: Async task management
   - Managed thread pool
   - Task tracking and cancellation
   - Lifecycle management (start → cancel → cleanup)
   - Used by: Dashboard for concurrent operations

**Key Design Principles:**
- **Separation of Concerns**: Utilities don't depend on UI specifics
- **Thread Safety**: All cross-thread communication via signals
- **Consistent Error Handling**: Single error handling pattern for entire dashboard
- **Resource Management**: Proper cleanup on close

**Integration Points:**
- **Handlers**: Import and use all 3 utility classes
- **Panels**: Use DashboardErrorHandler for validation
- **Dashboard**: Creates DashboardAsyncManager instance
- **Main Interface**: No direct usage (utilities are dashboard-level)

**Total Utilities:** 3 classes with 10+ methods
**Signal Count:** 3 (finished, error, result)
**Thread Pool:** Managed via QThreadPool (configurable)


---


---

## 📚 Related Documentation

### Cross-References

- [[source-docs/gui/dashboard_utils.md|Dashboard Utils]]

## 🔗 Source Code References

This documentation references the following GUI source files:

- [[src/app/gui/dashboard_utils.py]] - Implementation file


---

## RELATED SYSTEMS

### Agent System Integration

| Utility Class | Agent System | Integration Point | Reference |
|---------------|--------------|-------------------|-----------|
| **DashboardErrorHandler** | [[../agents/VALIDATION_CHAINS#layer-1-validatoragent-data-validation\|ValidatorAgent]] | validate_input() delegates to agent | Section 2 (error handler) |
| **AsyncWorker** | [[../agents/AGENT_ORCHESTRATION#lifecycle-state-management\|Agent Lifecycle]] | Background tasks for agent operations | Section 3 (async worker) |
| **DashboardAsyncManager** | [[../agents/PLANNING_HIERARCHIES#resource-allocation\|Resource Allocation]] | Thread pool management | Section 4 (async manager) |

### Core AI Integration

| Utility Class | Core AI System | Purpose | Reference |
|---------------|----------------|---------|-----------|
| **DashboardErrorHandler** | [[../core-ai/01-FourLaws-Relationship-Map\|FourLaws]] | Validates error handling actions | Via governance |
| **AsyncWorker** | [[../core-ai/02-AIPersona-Relationship-Map\|AIPersona]] | Background personality updates | Section 3 (signals) |
| **AsyncWorker** | [[../core-ai/04-LearningRequestManager-Relationship-Map\|Learning]] | Async learning path generation | Section 3 (usage) |

### Validation Chain Integration

```
User Input → DashboardErrorHandler.validate_input() → 
sanitize_input(text, max_length) → 
validate_length(text, min, max) → 
[[../agents/VALIDATION_CHAINS#layer-1-validatoragent-data-validation|ValidatorAgent.validate_schema()]] → 
[[../agents/VALIDATION_CHAINS#layer-3-cognitionkernel-four-laws-validation|Four Laws Check]] → 
Process or Reject
```

### Thread Safety Pattern

```
GUI Thread → AsyncWorker.run() → 
[[../agents/AGENT_ORCHESTRATION#centralized-kernel-architecture|CognitionKernel.route()]] (Worker Thread) → 
Core System Processing → 
AsyncWorker.result.emit() → 
GUI Thread Update
```

See [[../agents/AGENT_ORCHESTRATION#operational-extensions|Agent Thread Safety]] for kernel threading model.

---

**Enhanced by:** AGENT-078: GUI & Agent Cross-Links Specialist  
**Status:** ✅ Cross-linked with Core AI and Agent systems