# Async & Concurrency Utilities

## Overview

Asynchronous programming and concurrency utilities for managing async operations, thread pools, and parallel processing in Project-AI.

**Purpose**: Async operations, thread management, parallel processing  
**Dependencies**: asyncio, threading, concurrent.futures

---

## Async Utilities

### 1. Async Decorators

#### @async_retry
```python
import asyncio
from functools import wraps

def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0
):
    """
    Retry async function on failure.
    
    Args:
        max_attempts: Maximum retry attempts
        delay: Initial delay between retries (seconds)
        backoff_factor: Multiply delay by this factor each retry
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff_factor
        
        return wrapper
    
    return decorator

# Usage
@async_retry(max_attempts=5, delay=1.0, backoff_factor=2.0)
async def fetch_data(url: str):
    """Fetch data with automatic retries."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

---

#### @async_timeout
```python
import asyncio

def async_timeout(seconds: float):
    """
    Add timeout to async function.
    
    Args:
        seconds: Timeout in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=seconds
                )
            except asyncio.TimeoutError:
                logger.error(f"{func.__name__} timed out after {seconds}s")
                raise
        
        return wrapper
    
    return decorator

# Usage
@async_timeout(10.0)
async def slow_operation():
    """Operation with 10-second timeout."""
    await asyncio.sleep(5)
    return "completed"
```

---

### 2. Async Context Managers

#### async_timer
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def async_timer(operation_name: str):
    """Time async operations."""
    start = time.time()
    logger.info(f"Starting {operation_name}")
    
    try:
        yield
    finally:
        duration = time.time() - start
        logger.info(f"{operation_name} completed in {duration:.2f}s")

# Usage
async with async_timer("data_fetch"):
    data = await fetch_large_dataset()
```

---

### 3. Async Task Management

#### AsyncTaskManager
```python
class AsyncTaskManager:
    """Manage multiple async tasks."""
    
    def __init__(self):
        self.tasks = set()
    
    def create_task(self, coro):
        """Create and track task."""
        task = asyncio.create_task(coro)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return task
    
    async def cancel_all(self):
        """Cancel all tasks."""
        for task in self.tasks:
            task.cancel()
        
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()
    
    async def wait_all(self):
        """Wait for all tasks to complete."""
        await asyncio.gather(*self.tasks, return_exceptions=True)

# Usage
manager = AsyncTaskManager()

manager.create_task(process_item(1))
manager.create_task(process_item(2))
manager.create_task(process_item(3))

await manager.wait_all()
```

---

### 4. Async Iteration

#### async_batch
```python
async def async_batch(
    items: list,
    batch_size: int,
    delay: float = 0
):
    """
    Process items in batches asynchronously.
    
    Args:
        items: Items to process
        batch_size: Batch size
        delay: Delay between batches (seconds)
    
    Yields:
        Batches of items
    """
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        yield batch
        
        if delay > 0 and i + batch_size < len(items):
            await asyncio.sleep(delay)

# Usage
async for batch in async_batch(items, batch_size=10, delay=0.5):
    await process_batch(batch)
```

---

## Thread Utilities

### 1. Thread Pool Management

#### ThreadPoolManager
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Any

class ThreadPoolManager:
    """Manage thread pool for parallel processing."""
    
    def __init__(self, max_workers: int = None):
        """
        Initialize thread pool.
        
        Args:
            max_workers: Max threads (default: CPU count)
        """
        self.max_workers = max_workers or os.cpu_count()
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
    
    def submit(self, func: Callable, *args, **kwargs):
        """Submit task to pool."""
        return self.executor.submit(func, *args, **kwargs)
    
    def map(
        self,
        func: Callable,
        items: list
    ) -> list:
        """
        Map function over items in parallel.
        
        Args:
            func: Function to apply
            items: Items to process
        
        Returns:
            List of results
        """
        futures = [
            self.executor.submit(func, item)
            for item in items
        ]
        
        results = []
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                logger.error(f"Task failed: {e}")
        
        return results
    
    def shutdown(self, wait: bool = True):
        """Shutdown thread pool."""
        self.executor.shutdown(wait=wait)

# Usage
pool = ThreadPoolManager(max_workers=4)

# Submit single task
future = pool.submit(process_item, item)
result = future.result()

# Process multiple items
results = pool.map(process_item, items)

# Cleanup
pool.shutdown()
```

---

### 2. Thread-Safe Utilities

#### ThreadSafeCounter
```python
import threading

class ThreadSafeCounter:
    """Thread-safe counter."""
    
    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = threading.Lock()
    
    def increment(self, amount: int = 1) -> int:
        """Increment counter."""
        with self._lock:
            self._value += amount
            return self._value
    
    def decrement(self, amount: int = 1) -> int:
        """Decrement counter."""
        with self._lock:
            self._value -= amount
            return self._value
    
    def get(self) -> int:
        """Get current value."""
        with self._lock:
            return self._value
    
    def reset(self) -> None:
        """Reset to zero."""
        with self._lock:
            self._value = 0

# Usage
counter = ThreadSafeCounter()

def worker():
    for _ in range(1000):
        counter.increment()

threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(counter.get())  # 10000
```

---

### 3. Thread-Safe Queue

#### ProducerConsumerQueue
```python
from queue import Queue
from threading import Thread

class ProducerConsumerQueue:
    """Producer-consumer pattern with threading."""
    
    def __init__(self, num_workers: int = 4):
        self.queue = Queue()
        self.num_workers = num_workers
        self.workers = []
        self.running = False
    
    def start(self, worker_func: Callable):
        """Start worker threads."""
        self.running = True
        
        for _ in range(self.num_workers):
            worker = Thread(
                target=self._worker_loop,
                args=(worker_func,)
            )
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
    
    def _worker_loop(self, worker_func: Callable):
        """Worker thread loop."""
        while self.running:
            try:
                item = self.queue.get(timeout=1.0)
                worker_func(item)
                self.queue.task_done()
            except:
                continue
    
    def add_task(self, item: Any):
        """Add task to queue."""
        self.queue.put(item)
    
    def wait_completion(self):
        """Wait for all tasks to complete."""
        self.queue.join()
    
    def stop(self):
        """Stop all workers."""
        self.running = False
        for worker in self.workers:
            worker.join()

# Usage
queue = ProducerConsumerQueue(num_workers=4)

def process_task(item):
    print(f"Processing {item}")
    time.sleep(1)

queue.start(process_task)

for i in range(20):
    queue.add_task(i)

queue.wait_completion()
queue.stop()
```

---

## Parallel Processing

### 1. Process Pool

#### ProcessPoolManager
```python
from concurrent.futures import ProcessPoolExecutor

class ProcessPoolManager:
    """Manage process pool for CPU-bound tasks."""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or os.cpu_count()
        self.executor = ProcessPoolExecutor(max_workers=self.max_workers)
    
    def map(
        self,
        func: Callable,
        items: list,
        chunksize: int = 1
    ) -> list:
        """
        Map function over items using processes.
        
        Args:
            func: Function to apply (must be picklable)
            items: Items to process
            chunksize: Items per process
        
        Returns:
            List of results
        """
        return list(self.executor.map(func, items, chunksize=chunksize))
    
    def shutdown(self):
        """Shutdown process pool."""
        self.executor.shutdown()

# Usage
pool = ProcessPoolManager()

def cpu_intensive_task(x):
    return x ** 2

results = pool.map(cpu_intensive_task, range(1000), chunksize=50)
pool.shutdown()
```

---

## Advanced Patterns

### 1. Rate Limiting

#### AsyncRateLimiter
```python
class AsyncRateLimiter:
    """Async rate limiter."""
    
    def __init__(self, max_calls: int, period: float):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum calls per period
            period: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Wait until call is allowed."""
        async with self.lock:
            now = time.time()
            
            # Remove old calls
            self.calls = [
                call_time for call_time in self.calls
                if now - call_time < self.period
            ]
            
            # Wait if limit reached
            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                await asyncio.sleep(sleep_time)
                self.calls.pop(0)
            
            self.calls.append(time.time())

# Usage
limiter = AsyncRateLimiter(max_calls=10, period=60.0)

async def make_api_call():
    await limiter.acquire()
    return await fetch_data()
```

---

### 2. Debouncing

#### debounce
```python
def debounce(wait_seconds: float):
    """
    Debounce decorator - only execute after wait period of inactivity.
    """
    def decorator(func):
        timer = None
        lock = threading.Lock()
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal timer
            
            def call_func():
                func(*args, **kwargs)
            
            with lock:
                if timer:
                    timer.cancel()
                timer = threading.Timer(wait_seconds, call_func)
                timer.start()
        
        return wrapper
    
    return decorator

# Usage
@debounce(wait_seconds=1.0)
def on_input_change(value):
    print(f"Processing: {value}")

# Rapid calls
on_input_change("a")
on_input_change("ab")
on_input_change("abc")
# Only last call executes after 1s of inactivity
```

---

## Best Practices

### DO ✅

- Use `asyncio` for I/O-bound tasks
- Use processes for CPU-bound tasks
- Handle task cancellation properly
- Set timeouts for async operations
- Use thread-safe data structures
- Clean up resources (shutdown pools)

### DON'T ❌

- Mix blocking and async code
- Use threads for CPU-bound tasks (use processes)
- Share mutable state without locks
- Forget to await async functions
- Create unbounded thread pools
- Ignore exceptions in background tasks

---

## Related Documentation

- **Caching**: `source-docs/utilities/016-caching-memoization.md`
- **Test Helpers**: `source-docs/utilities/007-test-helpers.md`

---

**Last Updated**: 2025-01-24  
**Status**: Best Practices Guide  
**Maintainer**: Performance & Concurrency Team
