# Test Helpers & Utilities

## Overview

The Test Helpers module (`e2e/utils/test_helpers.py`) provides common utility functions for end-to-end testing, including condition waiting, file operations, JSON handling, retries, and comparison utilities.

**Location**: `e2e/utils/test_helpers.py`  
**Lines of Code**: ~200  
**Purpose**: Simplify E2E test scenarios and reduce test boilerplate  
**Dependencies**: json, time, pathlib, logging

---

## Core Utilities

### 1. Condition Waiting

#### wait_for_condition()
```python
def wait_for_condition(
    condition: Callable[[], bool],
    timeout: float = 30.0,
    check_interval: float = 0.5,
    error_message: str = "Condition not met within timeout",
) -> bool:
```

**Purpose**: Wait for a condition to become true with timeout.

**Parameters**:
- `condition`: Callable that returns `True` when condition met
- `timeout`: Maximum wait time in seconds (default: 30)
- `check_interval`: Time between checks in seconds (default: 0.5)
- `error_message`: Error message if timeout occurs

**Returns**: `True` if condition met, `False` if timeout

**Example**:
```python
# Wait for file to exist
def file_exists():
    return Path("output.txt").exists()

success = wait_for_condition(
    file_exists,
    timeout=10.0,
    error_message="Output file not created"
)

assert success, "File should be created within 10 seconds"
```

**Advanced Usage**:
```python
# Wait for API to be ready
def api_ready():
    try:
        response = requests.get("http://localhost:5000/health")
        return response.status_code == 200
    except:
        return False

wait_for_condition(api_ready, timeout=60.0, check_interval=1.0)
```

---

### 2. JSON File Operations

#### load_json_file()
```python
def load_json_file(file_path: Path) -> dict[str, Any] | list[Any]:
```

**Purpose**: Load and parse a JSON file with error handling.

**Returns**: Parsed JSON data (dict or list)

**Raises**:
- `FileNotFoundError`: If file doesn't exist
- `json.JSONDecodeError`: If invalid JSON

**Example**:
```python
# Load test configuration
config = load_json_file(Path("tests/fixtures/config.json"))
assert config["version"] == "1.0.0"

# Load test data
test_data = load_json_file(Path("tests/data/users.json"))
for user in test_data:
    validate_user(user)
```

---

#### save_json_file()
```python
def save_json_file(
    data: dict[str, Any] | list[Any],
    file_path: Path,
    indent: int = 2,
) -> None:
```

**Purpose**: Save data to JSON file with automatic directory creation.

**Parameters**:
- `data`: Data to save (dict or list)
- `file_path`: Target path
- `indent`: JSON indentation (default: 2)

**Example**:
```python
# Save test results
results = {
    "test_name": "user_authentication",
    "status": "passed",
    "duration_ms": 1250
}

save_json_file(results, Path("tests/results/test_1.json"))
```

---

### 3. File Management

#### create_test_file()
```python
def create_test_file(
    directory: Path,
    filename: str,
    content: str,
) -> Path:
```

**Purpose**: Create a test file with content, creating directories as needed.

**Returns**: Path to created file

**Example**:
```python
# Create test input file
test_dir = Path("tests/temp")
input_file = create_test_file(
    test_dir,
    "input.txt",
    "Test data line 1\nTest data line 2"
)

# Use in test
process_file(input_file)

# Verify
output_file = test_dir / "output.txt"
assert output_file.exists()
```

---

#### cleanup_test_files()
```python
def cleanup_test_files(*file_paths: Path) -> None:
```

**Purpose**: Clean up test files and directories.

**Parameters**: Variable number of paths (files or directories)

**Example**:
```python
# Create test files
f1 = create_test_file(temp_dir, "test1.txt", "data")
f2 = create_test_file(temp_dir, "test2.txt", "data")

try:
    # Run test
    run_test()
finally:
    # Always cleanup
    cleanup_test_files(f1, f2, temp_dir)
```

---

### 4. Performance Measurement

#### measure_execution_time()
```python
def measure_execution_time(func: Callable) -> Callable:
```

**Purpose**: Decorator to measure and log function execution time.

**Returns**: Wrapped function

**Example**:
```python
@measure_execution_time
def slow_operation():
    time.sleep(2)
    return "done"

result = slow_operation()
# Logs: "slow_operation executed in 2.001234s"
```

**Usage in Tests**:
```python
def test_performance():
    @measure_execution_time
    def data_processing():
        return process_large_dataset()
    
    start = time.time()
    result = data_processing()
    duration = time.time() - start
    
    assert duration < 5.0, "Processing should complete in under 5 seconds"
```

---

### 5. Retry Logic

#### retry_on_failure()
```python
def retry_on_failure(
    func: Callable,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    exceptions: tuple = (Exception,),
) -> Any:
```

**Purpose**: Retry a function on failure with exponential backoff.

**Parameters**:
- `func`: Function to retry
- `max_retries`: Maximum retry attempts (default: 3)
- `retry_delay`: Base delay between retries (default: 1.0s)
- `exceptions`: Tuple of exceptions to catch (default: all)

**Returns**: Function result if successful

**Raises**: Last exception if all retries fail

**Example**:
```python
# Retry flaky network operation
def fetch_data():
    response = requests.get("http://api.example.com/data")
    return response.json()

data = retry_on_failure(
    fetch_data,
    max_retries=5,
    retry_delay=2.0,
    exceptions=(requests.RequestException,)
)
```

**Test Usage**:
```python
def test_api_with_retries():
    """Test API with automatic retries for transient failures."""
    
    def make_request():
        return api_client.create_user(username="test")
    
    # Retry up to 3 times if server temporarily unavailable
    user = retry_on_failure(
        make_request,
        max_retries=3,
        retry_delay=1.0,
        exceptions=(ConnectionError, Timeout)
    )
    
    assert user["username"] == "test"
```

---

### 6. JSON Comparison

#### compare_json_objects()
```python
def compare_json_objects(
    obj1: dict[str, Any] | list[Any],
    obj2: dict[str, Any] | list[Any],
    ignore_keys: list[str] | None = None,
) -> tuple[bool, list[str]]:
```

**Purpose**: Deep comparison of JSON objects with ability to ignore specific keys.

**Parameters**:
- `obj1`: First object
- `obj2`: Second object
- `ignore_keys`: Keys to exclude from comparison (e.g., timestamps, IDs)

**Returns**: `(is_equal, list_of_differences)`

**Example**:
```python
expected = {
    "user_id": 123,
    "name": "Alice",
    "created_at": "2025-01-24T10:00:00Z",
    "email": "alice@example.com"
}

actual = {
    "user_id": 123,
    "name": "Alice",
    "created_at": "2025-01-24T10:05:23Z",  # Different timestamp
    "email": "alice@example.com"
}

# Ignore timestamp in comparison
is_equal, diffs = compare_json_objects(
    expected,
    actual,
    ignore_keys=["created_at"]
)

assert is_equal, f"Objects should match (ignoring timestamps): {diffs}"
```

**Complex Comparison**:
```python
# Compare lists of objects
expected_users = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
]

actual_users = [
    {"id": 1, "name": "Alice", "last_login": "2025-01-24"},
    {"id": 2, "name": "Bob", "last_login": "2025-01-23"}
]

is_equal, diffs = compare_json_objects(
    expected_users,
    actual_users,
    ignore_keys=["last_login"]
)
```

---

## Testing Patterns

### Pattern 1: Database Test Setup

```python
def setup_test_database():
    """Setup test database with fixtures."""
    db_file = Path("tests/temp/test.db")
    
    # Create test file
    create_test_file(
        db_file.parent,
        db_file.name,
        ""  # Empty file, will be initialized by DB
    )
    
    # Initialize database
    db = Database(db_file)
    db.initialize()
    
    # Load fixtures
    fixtures = load_json_file(Path("tests/fixtures/users.json"))
    for user_data in fixtures:
        db.create_user(**user_data)
    
    return db

def teardown_test_database(db):
    """Cleanup test database."""
    db.close()
    cleanup_test_files(Path("tests/temp/test.db"))
```

**Usage**:
```python
def test_user_authentication():
    db = setup_test_database()
    try:
        user = db.authenticate("alice", "password123")
        assert user is not None
        assert user["username"] == "alice"
    finally:
        teardown_test_database(db)
```

---

### Pattern 2: API Integration Test

```python
def test_api_workflow():
    """Test complete API workflow with retries and conditions."""
    
    # Wait for API to be ready
    def api_ready():
        try:
            response = requests.get("http://localhost:5000/health")
            return response.status_code == 200
        except:
            return False
    
    assert wait_for_condition(api_ready, timeout=30.0), "API should start"
    
    # Create user with retry
    def create_user():
        response = requests.post(
            "http://localhost:5000/users",
            json={"username": "testuser", "email": "test@example.com"}
        )
        response.raise_for_status()
        return response.json()
    
    user = retry_on_failure(create_user, max_retries=3)
    
    # Verify response structure
    expected = {
        "username": "testuser",
        "email": "test@example.com"
    }
    
    is_equal, diffs = compare_json_objects(
        expected,
        user,
        ignore_keys=["id", "created_at"]
    )
    
    assert is_equal, f"User data mismatch: {diffs}"
```

---

### Pattern 3: File Processing Test

```python
def test_file_processing():
    """Test file processing with automatic cleanup."""
    test_dir = Path("tests/temp/processing")
    
    try:
        # Create input files
        input1 = create_test_file(test_dir, "input1.txt", "data1\ndata2")
        input2 = create_test_file(test_dir, "input2.txt", "data3\ndata4")
        
        # Process files
        @measure_execution_time
        def process():
            processor = FileProcessor(test_dir)
            processor.process_all()
        
        process()
        
        # Wait for output
        output_file = test_dir / "output.txt"
        
        def output_exists():
            return output_file.exists()
        
        assert wait_for_condition(output_exists, timeout=5.0)
        
        # Verify output
        with open(output_file) as f:
            output = f.read()
        assert "data1" in output
        assert "data4" in output
        
    finally:
        # Cleanup
        cleanup_test_files(test_dir)
```

---

### Pattern 4: State Machine Test

```python
def test_state_machine():
    """Test state machine transitions with condition waiting."""
    state_file = Path("tests/temp/state.json")
    
    try:
        # Initialize state
        initial_state = {"status": "idle", "value": 0}
        save_json_file(initial_state, state_file)
        
        # Start state machine
        machine = StateMachine(state_file)
        machine.start()
        
        # Wait for processing state
        def is_processing():
            state = load_json_file(state_file)
            return state["status"] == "processing"
        
        assert wait_for_condition(is_processing, timeout=5.0)
        
        # Wait for completion
        def is_complete():
            state = load_json_file(state_file)
            return state["status"] == "complete"
        
        assert wait_for_condition(is_complete, timeout=10.0)
        
        # Verify final state
        final_state = load_json_file(state_file)
        expected = {"status": "complete", "value": 100}
        
        is_equal, diffs = compare_json_objects(
            expected,
            final_state,
            ignore_keys=["timestamp"]
        )
        
        assert is_equal
        
    finally:
        cleanup_test_files(state_file)
```

---

## Advanced Usage

### Context Manager for Test Cleanup

```python
from contextlib import contextmanager

@contextmanager
def temporary_test_files(*files):
    """Context manager for automatic test file cleanup."""
    file_paths = []
    try:
        for directory, filename, content in files:
            path = create_test_file(Path(directory), filename, content)
            file_paths.append(path)
        yield file_paths
    finally:
        cleanup_test_files(*file_paths)

# Usage
def test_with_context_manager():
    with temporary_test_files(
        ("tests/temp", "input1.txt", "data1"),
        ("tests/temp", "input2.txt", "data2"),
    ) as files:
        input1, input2 = files
        # Files automatically cleaned up after block
        process_files(input1, input2)
```

---

### Parametrized Retry

```python
def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
) -> Any:
    """Retry with exponential backoff."""
    last_exception = None
    delay = base_delay
    
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            last_exception = e
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                time.sleep(min(delay, max_delay))
                delay *= backoff_factor
    
    raise last_exception

# Usage
def flaky_api_call():
    # ...

result = retry_with_backoff(
    flaky_api_call,
    max_retries=5,
    base_delay=0.5,
    backoff_factor=2.0
)
```

---

## Best Practices

### 1. Always Use Cleanup

```python
# BAD: No cleanup
def test_without_cleanup():
    f = create_test_file(Path("temp"), "test.txt", "data")
    process(f)
    # File left behind!

# GOOD: With cleanup
def test_with_cleanup():
    f = create_test_file(Path("temp"), "test.txt", "data")
    try:
        process(f)
    finally:
        cleanup_test_files(f)

# BETTER: Context manager
def test_with_context():
    with temporary_test_files(("temp", "test.txt", "data")) as [f]:
        process(f)
```

---

### 2. Set Appropriate Timeouts

```python
# BAD: Too short timeout
wait_for_condition(lambda: api.ready(), timeout=0.5)  # May flake

# GOOD: Reasonable timeout
wait_for_condition(lambda: api.ready(), timeout=30.0)

# BETTER: Configurable timeout
TIMEOUT = int(os.getenv("TEST_TIMEOUT", "30"))
wait_for_condition(lambda: api.ready(), timeout=TIMEOUT)
```

---

### 3. Meaningful Error Messages

```python
# BAD: Generic message
assert wait_for_condition(check, timeout=10.0)

# GOOD: Specific message
assert wait_for_condition(
    check,
    timeout=10.0,
    error_message="Database should be ready within 10 seconds"
)
```

---

## Related Documentation

- **E2E Testing Guide**: `docs/testing/e2e-testing.md`
- **Test Fixtures**: `tests/fixtures/README.md`
- **CI/CD Pipeline**: `.github/workflows/ci.yml`

---

**Last Updated**: 2025-01-24  
**Status**: Stable - Production Ready  
**Maintainer**: QA & Testing Team
