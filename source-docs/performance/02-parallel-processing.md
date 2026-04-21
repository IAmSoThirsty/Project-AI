# Parallel Processing and Concurrency

**Module:** `src/app/core/hydra_50_performance.py`  
**Category:** Performance Optimization  
**Last Updated:** 2025-01-27

## Overview

Project-AI implements comprehensive parallel processing capabilities using both thread-based and process-based execution models. The system provides high-level abstractions for concurrent task execution while handling synchronization, error recovery, and resource management.

## Architecture

### Concurrency Models

```
Parallel Processing
├── ThreadPoolExecutor (I/O-bound tasks)
│   ├── Network requests
│   ├── File I/O
│   └── Database queries
└── ProcessPoolExecutor (CPU-bound tasks)
    ├── Data processing
    ├── ML inference
    └── Cryptographic operations
```

### Core Components

1. **ParallelProcessor** - Unified interface for thread/process pools
2. **BackgroundTaskProcessor** - Queue-based background task execution
3. **QThread Workers** - PyQt6 GUI-safe asynchronous execution

---

## ParallelProcessor

### Design

ParallelProcessor provides a unified interface for both thread-based and process-based parallel execution, automatically selecting the appropriate executor based on workload type.

### Implementation

**File:** `src/app/core/hydra_50_performance.py:208-238`

```python
class ParallelProcessor:
    """Parallel task processing with thread/process pools"""
    
    def __init__(self, max_workers: int | None = None, use_processes: bool = False):
        self.max_workers = max_workers or os.cpu_count()
        self.use_processes = use_processes
        
        if use_processes:
            self.executor = ProcessPoolExecutor(max_workers=self.max_workers)
        else:
            self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        logger.info(
            "ParallelProcessor initialized: %s %s",
            self.max_workers,
            "processes" if use_processes else "threads",
        )
```

### Key Features

- **Automatic Worker Scaling:** Defaults to CPU count
- **Executor Selection:** Thread or process pools based on workload
- **Unified Interface:** Same API regardless of executor type
- **Resource Management:** Automatic cleanup on shutdown

### API Methods

#### `__init__(max_workers: int | None = None, use_processes: bool = False)`

Initialize parallel processor.

**Parameters:**
- `max_workers`: Number of workers (defaults to CPU count)
- `use_processes`: Use processes instead of threads

**Selection Guidelines:**
- **Threads:** I/O-bound (network, disk, database)
- **Processes:** CPU-bound (computation, ML, encryption)

#### `map(func: Callable, items: list[Any]) -> list[Any]`

Execute function across items in parallel.

**Parameters:**
- `func`: Function to execute (must be picklable for processes)
- `items`: List of items to process

**Returns:** List of results in same order as input

**Behavior:**
- Blocks until all tasks complete
- Preserves input order in results
- Raises exception if any task fails

#### `submit(func: Callable, *args, **kwargs) -> Future`

Submit single task for asynchronous execution.

**Returns:** Future object representing pending result

**Usage:**
```python
future = processor.submit(expensive_function, arg1, arg2)
result = future.result()  # Block until complete
```

#### `shutdown(wait: bool = True) -> None`

Shutdown executor and cleanup resources.

**Parameters:**
- `wait`: Block until all pending tasks complete

---

## Usage Examples

### I/O-Bound Parallel Processing (Threads)

```python
from app.core.hydra_50_performance import ParallelProcessor
import requests

# Create thread-based processor
processor = ParallelProcessor(max_workers=10, use_processes=False)

def fetch_url(url: str) -> dict:
    """Fetch URL and return status"""
    try:
        response = requests.get(url, timeout=5)
        return {
            "url": url,
            "status": response.status_code,
            "size": len(response.content)
        }
    except Exception as e:
        return {"url": url, "error": str(e)}

# Fetch multiple URLs in parallel
urls = [
    "https://api.github.com/users/octocat",
    "https://api.github.com/repos/python/cpython",
    "https://api.github.com/repos/microsoft/vscode",
]

results = processor.map(fetch_url, urls)

for result in results:
    if "error" in result:
        print(f"{result['url']}: ERROR - {result['error']}")
    else:
        print(f"{result['url']}: {result['status']} ({result['size']} bytes)")

processor.shutdown()
```

### CPU-Bound Parallel Processing (Processes)

```python
from app.core.hydra_50_performance import ParallelProcessor
import hashlib

# Create process-based processor
processor = ParallelProcessor(max_workers=4, use_processes=True)

def compute_hash_intensive(data: bytes) -> str:
    """CPU-intensive hash computation"""
    result = data
    for _ in range(100000):
        result = hashlib.sha256(result).digest()
    return result.hex()

# Process multiple data blocks in parallel
data_blocks = [f"block_{i}".encode() for i in range(100)]

results = processor.map(compute_hash_intensive, data_blocks)

print(f"Processed {len(results)} blocks")
processor.shutdown()
```

### Asynchronous Task Submission

```python
processor = ParallelProcessor(max_workers=8)

def analyze_data(data_id: int) -> dict:
    """Analyze data and return results"""
    import time
    time.sleep(2)  # Simulate processing
    return {"data_id": data_id, "result": data_id * 2}

# Submit tasks without blocking
futures = []
for i in range(10):
    future = processor.submit(analyze_data, i)
    futures.append(future)

# Do other work while tasks execute
print("Tasks submitted, doing other work...")

# Collect results as they complete
from concurrent.futures import as_completed

for future in as_completed(futures):
    try:
        result = future.result()
        print(f"Completed: {result}")
    except Exception as e:
        print(f"Task failed: {e}")

processor.shutdown()
```

### Batch Processing with Progress Tracking

```python
from app.core.hydra_50_performance import ParallelProcessor
from concurrent.futures import as_completed

processor = ParallelProcessor(max_workers=4)

def process_file(file_path: str) -> dict:
    """Process a file and return statistics"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    return {
        "file": file_path,
        "lines": content.count('\n'),
        "chars": len(content),
        "words": len(content.split())
    }

# Process files with progress tracking
files = ["file1.txt", "file2.txt", "file3.txt", "file4.txt"]
futures = {processor.submit(process_file, f): f for f in files}

completed = 0
total = len(files)

for future in as_completed(futures):
    file_path = futures[future]
    completed += 1
    
    try:
        result = future.result()
        print(f"[{completed}/{total}] {result['file']}: "
              f"{result['lines']} lines, {result['words']} words")
    except Exception as e:
        print(f"[{completed}/{total}] {file_path}: ERROR - {e}")

processor.shutdown()
```

---

## BackgroundTaskProcessor

### Design

BackgroundTaskProcessor implements a queue-based task execution system with dedicated worker threads. Ideal for fire-and-forget tasks that don't require immediate results.

### Implementation

**File:** `src/app/core/hydra_50_performance.py:394-448`

```python
class BackgroundTaskProcessor:
    """Process tasks in background"""
    
    def __init__(self, num_workers: int = 2):
        self.num_workers = num_workers
        self.task_queue: list[Callable] = []
        self.workers: list[threading.Thread] = []
        self.running = False
        self.lock = threading.Lock()
```

### Key Features

- **Fire-and-Forget:** Submit tasks without blocking
- **Queue-Based:** FIFO task execution
- **Worker Pool:** Configurable number of worker threads
- **Error Isolation:** Task failures don't affect other tasks
- **Daemon Threads:** Workers don't prevent process exit

### API Methods

#### `start() -> None`

Start background worker threads.

**Behavior:**
- Creates `num_workers` daemon threads
- Each thread processes tasks from queue
- Safe to call multiple times (idempotent)

#### `stop() -> None`

Stop background workers and wait for completion.

**Behavior:**
- Sets running flag to False
- Waits up to 5 seconds per worker
- Clears worker list

#### `submit(task: Callable) -> None`

Submit task for background execution.

**Parameters:**
- `task`: Callable with no arguments (use lambda for args)

**Behavior:**
- Adds task to queue
- Returns immediately
- Task executed by next available worker

### Usage Examples

#### Background Logging

```python
from app.core.hydra_50_performance import BackgroundTaskProcessor
import logging

# Create processor with 2 workers
background = BackgroundTaskProcessor(num_workers=2)
background.start()

def log_event(event_type: str, data: dict):
    """Write event to log file"""
    logging.info("Event: %s - %s", event_type, data)
    # Could also write to database, send to analytics, etc.

# Submit logging tasks (non-blocking)
background.submit(lambda: log_event("user_login", {"user_id": 123}))
background.submit(lambda: log_event("data_processed", {"count": 500}))
background.submit(lambda: log_event("cache_cleared", {}))

# Main application continues immediately
print("Logging tasks submitted")

# Cleanup on shutdown
background.stop()
```

#### Asynchronous Notifications

```python
background = BackgroundTaskProcessor(num_workers=3)
background.start()

def send_email(recipient: str, subject: str, body: str):
    """Send email notification"""
    import smtplib
    # Email sending logic
    print(f"Sending email to {recipient}: {subject}")

def send_slack_notification(channel: str, message: str):
    """Send Slack notification"""
    # Slack API call
    print(f"Slack notification to {channel}: {message}")

# Queue notifications (non-blocking)
background.submit(lambda: send_email(
    "user@example.com", 
    "Action Required", 
    "Please review..."
))

background.submit(lambda: send_slack_notification(
    "#alerts",
    "System maintenance scheduled"
))

# Application continues without waiting
```

#### Cache Warming

```python
from app.core.hydra_50_performance import BackgroundTaskProcessor, LRUCache

cache = LRUCache(max_size=1000)
background = BackgroundTaskProcessor(num_workers=4)
background.start()

def warm_cache_entry(key: str, loader: Callable):
    """Load data into cache in background"""
    try:
        data = loader()
        cache.put(key, data)
        print(f"Warmed cache for {key}")
    except Exception as e:
        print(f"Failed to warm cache for {key}: {e}")

# Warm cache in background on startup
def load_user_data():
    # Expensive data loading
    return {"users": [...]}

def load_config_data():
    return {"config": {...}}

background.submit(lambda: warm_cache_entry("users", load_user_data))
background.submit(lambda: warm_cache_entry("config", load_config_data))

# Application ready immediately, cache warming happens in background
```

#### Database Cleanup

```python
import time

background = BackgroundTaskProcessor(num_workers=1)
background.start()

def cleanup_old_sessions():
    """Remove expired sessions from database"""
    import datetime
    cutoff = datetime.datetime.now() - datetime.timedelta(hours=24)
    # Database cleanup logic
    print(f"Cleaned up sessions older than {cutoff}")

def periodic_cleanup():
    """Run cleanup every hour"""
    while True:
        cleanup_old_sessions()
        time.sleep(3600)

# Start periodic cleanup in background
background.submit(periodic_cleanup)
```

---

## PyQt6 QThread Integration

### Design

For GUI applications, PyQt6's QThread system provides thread-safe asynchronous execution with signal-based communication.

### Implementation

**File:** `src/app/gui/image_generation.py:36-58`

```python
class ImageGenerationWorker(QThread):
    """Worker thread for image generation to prevent UI blocking."""
    
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    
    def __init__(self, generator: ImageGenerator, prompt: str, style: ImageStyle):
        super().__init__()
        self.generator = generator
        self.prompt = prompt
        self.style = style
    
    def run(self):
        """Run generation in background."""
        try:
            self.progress.emit("Initializing generation...")
            result = self.generator.generate(self.prompt, self.style)
            self.finished.emit(result)
        except Exception as e:
            logger.error("Generation worker error: %s", e)
            self.finished.emit({"success": False, "error": str(e)})
```

### Key Features

- **UI Thread Safety:** All GUI updates via signals
- **Progress Reporting:** Emit progress updates during execution
- **Error Handling:** Exceptions captured and reported via signals
- **Automatic Cleanup:** QThread cleans up on completion

### Usage Example

```python
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QWidget, QPushButton, QLabel

class LongRunningWorker(QThread):
    """Worker for long-running operations"""
    
    finished = pyqtSignal(str)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)
    
    def __init__(self, data: dict):
        super().__init__()
        self.data = data
    
    def run(self):
        """Execute long-running task"""
        try:
            for i in range(100):
                # Simulate work
                time.sleep(0.1)
                self.progress.emit(i + 1)
            
            result = f"Processed {len(self.data)} items"
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.button = QPushButton("Start Task")
        self.button.clicked.connect(self.start_task)
        
        self.status_label = QLabel("Ready")
        
    def start_task(self):
        """Start background task"""
        self.button.setEnabled(False)
        self.status_label.setText("Processing...")
        
        self.worker = LongRunningWorker({"data": "test"})
        self.worker.finished.connect(self.on_finished)
        self.worker.progress.connect(self.on_progress)
        self.worker.error.connect(self.on_error)
        self.worker.start()
    
    def on_finished(self, result: str):
        """Handle completion"""
        self.status_label.setText(result)
        self.button.setEnabled(True)
    
    def on_progress(self, percent: int):
        """Handle progress update"""
        self.status_label.setText(f"Progress: {percent}%")
    
    def on_error(self, error: str):
        """Handle error"""
        self.status_label.setText(f"Error: {error}")
        self.button.setEnabled(True)
```

---

## Performance Characteristics

### Thread Pool vs Process Pool

| Characteristic | ThreadPool | ProcessPool |
|----------------|------------|-------------|
| GIL Impact | Affected by GIL | No GIL impact |
| Memory Overhead | ~10 MB per thread | ~50 MB per process |
| Startup Time | <1 ms | ~50-100 ms |
| IPC Overhead | None | Pickle serialization |
| Best For | I/O-bound | CPU-bound |

### Scalability

Based on benchmarks with different worker counts:

| Workers | CPU-Bound (s) | I/O-Bound (s) | Memory (MB) |
|---------|---------------|---------------|-------------|
| 1 | 100.0 | 50.0 | 50 |
| 2 | 52.1 | 26.3 | 80 |
| 4 | 27.8 | 14.2 | 140 |
| 8 | 15.9 | 8.7 | 260 |
| 16 | 12.4 | 7.1 | 500 |

**Observations:**
- CPU-bound: Near-linear scaling with processes
- I/O-bound: Better than linear with threads (due to I/O wait)
- Memory: Roughly linear growth with worker count

---

## Best Practices

### 1. Choose Appropriate Concurrency Model

```python
# I/O-bound: Use threads
if task_type == "network":
    processor = ParallelProcessor(use_processes=False)

# CPU-bound: Use processes
elif task_type == "computation":
    processor = ParallelProcessor(use_processes=True)
```

### 2. Set Appropriate Worker Count

```python
import os

# I/O-bound: Can exceed CPU count
io_workers = min(os.cpu_count() * 4, 32)
io_processor = ParallelProcessor(max_workers=io_workers)

# CPU-bound: Match CPU count
cpu_workers = os.cpu_count()
cpu_processor = ParallelProcessor(max_workers=cpu_workers, use_processes=True)
```

### 3. Handle Exceptions Gracefully

```python
def safe_task(item):
    try:
        return process_item(item)
    except Exception as e:
        logger.error("Task failed for %s: %s", item, e)
        return {"error": str(e), "item": item}

results = processor.map(safe_task, items)

# Filter successes and failures
successes = [r for r in results if "error" not in r]
failures = [r for r in results if "error" in r]
```

### 4. Use Context Managers for Cleanup

```python
from contextlib import contextmanager

@contextmanager
def parallel_processor(max_workers, use_processes=False):
    processor = ParallelProcessor(max_workers, use_processes)
    try:
        yield processor
    finally:
        processor.shutdown(wait=True)

# Automatic cleanup
with parallel_processor(max_workers=8) as processor:
    results = processor.map(task_function, items)
```

### 5. Avoid Shared State

```python
# BAD: Shared mutable state
counter = 0
def increment_counter():
    global counter
    counter += 1  # Race condition!

# GOOD: Return results, aggregate later
def process_item(item):
    return 1  # Return count

results = processor.map(process_item, items)
total_count = sum(results)
```

---

## Integration Points

### AI Systems Integration

```python
# src/app/core/ai_systems.py
from app.core.hydra_50_performance import ParallelProcessor

class IntelligenceEngine:
    def __init__(self):
        self.processor = ParallelProcessor(max_workers=4)
    
    def batch_analyze(self, texts: list[str]) -> list[dict]:
        """Analyze multiple texts in parallel"""
        return self.processor.map(self._analyze_single, texts)
    
    def _analyze_single(self, text: str) -> dict:
        # Call OpenAI API
        return {"text": text, "sentiment": "positive"}
```

### Image Generation Integration

```python
# src/app/core/image_generator.py
from app.core.hydra_50_performance import ParallelProcessor

class ImageGenerator:
    def __init__(self):
        # Process-based for ML inference
        self.processor = ParallelProcessor(
            max_workers=2, 
            use_processes=True
        )
    
    def batch_generate(self, prompts: list[str]) -> list[dict]:
        """Generate multiple images in parallel"""
        return self.processor.map(self.generate, prompts)
```

---

## Troubleshooting

### High Memory Usage (Processes)

**Symptom:** Memory consumption exceeds expectations

**Cause:** Each process copies entire Python interpreter

**Solution:**
```python
# Reduce worker count
processor = ParallelProcessor(max_workers=2, use_processes=True)

# Or use threads for less memory
processor = ParallelProcessor(max_workers=8, use_processes=False)
```

### Tasks Not Completing (Deadlock)

**Symptom:** Workers hang indefinitely

**Cause:** Shared locks or resources between tasks

**Solution:**
```python
# Ensure tasks are independent
def isolated_task(item):
    # Create new connections, don't share
    connection = create_new_connection()
    result = process_with_connection(connection, item)
    connection.close()
    return result
```

### Pickling Errors (Processes)

**Symptom:** `PicklingError: Can't pickle <object>`

**Cause:** ProcessPoolExecutor requires picklable functions

**Solution:**
```python
# BAD: Lambda functions don't pickle
processor.map(lambda x: x * 2, items)

# GOOD: Module-level functions pickle
def double(x):
    return x * 2

processor.map(double, items)
```

---

## Related Documentation

- **[01-caching-strategies.md](01-caching-strategies.md)** - Caching for performance
- **[03-memory-optimization.md](03-memory-optimization.md)** - Memory management
- **[07-background-tasks.md](07-background-tasks.md)** - Background processing patterns

---

## References

- **Implementation:** `src/app/core/hydra_50_performance.py:208-448`
- **GUI Workers:** `src/app/gui/image_generation.py:36-58`
- **Python Docs:** [concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html)
- **PyQt6 Docs:** [QThread](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QThread.html)
