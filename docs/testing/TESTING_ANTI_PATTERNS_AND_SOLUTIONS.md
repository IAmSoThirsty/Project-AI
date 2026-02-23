# Testing Anti-Patterns and Solutions

## Critical Issues Identified

### 1. Flaky Concurrent Tests (ANTI-PATTERN)

**Problem**: Concurrent access tests using timing/sleep are environment-dependent and flaky.

**Bad Example** (what NOT to do):
```python
def test_concurrent_circuit_breaker():
    def worker():
        time.sleep(random.random() * 0.1)  # ❌ Non-deterministic!
        cb.call(some_function)
    
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert cb.failure_count == 5  # ❌ Flaky - race conditions!
```

**Good Example** (deterministic synchronization):
```python
def test_concurrent_circuit_breaker():
    barrier = threading.Barrier(10)  # ✅ Deterministic coordination
    results = []
    
    def worker():
        barrier.wait()  # All threads start at EXACTLY the same time
        try:
            result = cb.call(some_function)
            results.append(('success', result))
        except Exception as e:
            results.append(('failure', str(e)))
    
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Now we can make deterministic assertions
    assert len(results) == 10
    assert results.count(('failure', ...)) == 5
```

**Why threading.Barrier**:
- Forces all threads to wait until N threads arrive
- Creates deterministic "starting gun" effect
- Eliminates timing-based race conditions
- Makes tests reproducible across environments

**Affected Tests**:
- Circuit breaker concurrent access (#9)
- Per-service retry concurrent increments (#3)
- Per-service retry lock contention (#4)
- Multiple services concurrent processing (integration)

### 2. Slow Tests Due to Real Sleeps (ANTI-PATTERN)

**Problem**: Circuit breaker recovery timeout tests would take 60+ seconds in real time.

**Bad Example** (what NOT to do):
```python
def test_circuit_breaker_recovery_timeout():
    cb.state = 'OPEN'
    cb.last_failure_time = time.time()
    
    # Try immediately - should still be OPEN
    with pytest.raises(Exception):
        cb.call(some_function)
    
    time.sleep(60)  # ❌ Test takes 60 seconds!
    
    # Try after timeout - should be HALF_OPEN
    cb.call(some_function)  # Should work
```

**Good Example** (mock time):
```python
def test_circuit_breaker_recovery_timeout():
    with patch('time.time') as mock_time:
        # Set initial time
        mock_time.return_value = 1000.0
        
        cb.state = 'OPEN'
        cb.last_failure_time = 1000.0
        
        # Try at T+30s - should still be OPEN (recovery_timeout=60)
        mock_time.return_value = 1030.0
        with pytest.raises(Exception, match="Circuit breaker.*OPEN.*retry after 30s"):
            cb.call(some_function)
        
        # Try at T+60s - should enter HALF_OPEN
        mock_time.return_value = 1060.0
        result = cb.call(lambda: "success")
        assert cb.state == 'HALF_OPEN'
        assert result == "success"
        
        # ✅ Test completes in milliseconds, not 60 seconds!
```

**Why Mock Time**:
- Tests run in milliseconds instead of minutes
- Exact timeout values can be tested (T+30s, T+59s, T+60s, T+61s)
- No environment timing dependencies
- Can test multi-hour timeouts without waiting

**Affected Tests**:
- Validation CB recovery timeout (60s)
- Transcription CB recovery timeout (60s)
- Processing CB recovery timeout (45s)
- Per-service retry reset (60s)
- All exponential backoff tests (2s, 4s, 8s delays)

### 3. Redis Retry Counter Reset Tests

**Problem**: Waiting 60 seconds for Redis TTL expiration.

**Bad Example**:
```python
def test_redis_retry_reset():
    increment_retry_counter('service1')
    assert check_retry_limit('service1') == False
    
    time.sleep(60)  # ❌ Test takes 60 seconds!
    
    assert check_retry_limit('service1') == False  # Counter expired
```

**Good Example**:
```python
def test_redis_retry_reset():
    with patch('time.time') as mock_time:
        mock_time.return_value = 1000.0
        
        increment_retry_counter('service1')
        assert redis_client.ttl('signal_retry:service1:minute') <= 60
        
        # Fast-forward time
        mock_time.return_value = 1061.0
        
        # Counter should have expired (TTL reached)
        assert redis_client.get('signal_retry:service1:minute') is None
        assert check_retry_limit('service1') == False
```

---

## Implementation Plan

### Step 1: Update Test Fixtures

Add time mocking fixture:
```python
import pytest
from unittest.mock import patch

@pytest.fixture
def mock_time():
    """Mock time.time() for deterministic time-based tests."""
    with patch('time.time') as mock:
        mock.return_value = 1000.0  # Start at T=1000s
        yield mock

@pytest.fixture
def mock_sleep():
    """Mock time.sleep() to avoid real delays."""
    with patch('time.sleep') as mock:
        yield mock
```

### Step 2: Refactor Concurrent Tests

**Circuit Breaker Concurrent Access**:
```python
def test_circuit_breaker_concurrent_access():
    """Test thread-safe state transitions under concurrent load."""
    barrier = threading.Barrier(10)
    results = []
    lock = threading.Lock()
    
    def worker(should_fail):
        barrier.wait()  # Synchronize thread start
        try:
            if should_fail:
                result = cb.call(lambda: raise_error())
            else:
                result = cb.call(lambda: "success")
            with lock:
                results.append(('success', result))
        except Exception as e:
            with lock:
                results.append(('failure', str(e)))
    
    # 5 failing calls, 5 successful calls
    threads = [
        threading.Thread(target=worker, args=(i < 5,))
        for i in range(10)
    ]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Deterministic assertions
    assert len(results) == 10
    failures = [r for r in results if r[0] == 'failure']
    successes = [r for r in results if r[0] == 'success']
    
    # CB should have opened after 5 failures
    assert cb.state in ['OPEN', 'HALF_OPEN']
    assert cb.failure_count >= 5
```

**Per-Service Retry Concurrent Increments**:
```python
def test_per_service_retry_concurrent_increments():
    """Test thread-safe counter updates."""
    barrier = threading.Barrier(50)
    
    def worker(service_name):
        barrier.wait()  # All threads start simultaneously
        increment_retry_counter(service_name)
    
    # 25 threads for service1, 25 for service2
    threads = [
        threading.Thread(target=worker, args=('service1' if i < 25 else 'service2',))
        for i in range(50)
    ]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Verify atomicity (no lost updates)
    if redis_client:
        assert int(redis_client.get('signal_retry:service1:minute')) == 25
        assert int(redis_client.get('signal_retry:service2:minute')) == 25
    else:
        assert retry_tracker['service1']['minute'] == 25
        assert retry_tracker['service2']['minute'] == 25
```

### Step 3: Refactor Time-Based Tests

**Circuit Breaker Recovery Timeout**:
```python
def test_circuit_breaker_recovery_timeout_validation(mock_time):
    """Test validation CB recovery after 30s timeout."""
    cb = circuit_breakers['validation']  # recovery_timeout=30
    
    # Open the circuit
    mock_time.return_value = 1000.0
    for _ in range(10):
        try:
            cb.call(lambda: raise_error())
        except:
            pass
    
    assert cb.state == 'OPEN'
    
    # Try at T+15s - should still be OPEN
    mock_time.return_value = 1015.0
    with pytest.raises(Exception, match="retry after 15s"):
        cb.call(lambda: "success")
    assert cb.state == 'OPEN'
    
    # Try at T+30s - should enter HALF_OPEN
    mock_time.return_value = 1030.0
    result = cb.call(lambda: "success")
    assert cb.state == 'HALF_OPEN'
    assert result == "success"
```

**Exponential Backoff**:
```python
def test_exponential_backoff_delays(mock_time, mock_sleep):
    """Test retry delays: 2s, 4s, 8s (capped at 30s)."""
    signal = {'text': 'test', 'simulate': 'retry'}
    
    mock_time.return_value = 1000.0
    result = process_signal(signal)
    
    # Verify sleep calls
    assert mock_sleep.call_count == 2  # 2 retries (1st fails, 2nd fails, 3rd succeeds)
    mock_sleep.assert_any_call(2)  # 2^1
    mock_sleep.assert_any_call(4)  # 2^2
    
    assert result['status'] == 'processed'
    assert result['attempts'] == 3
```

**Retry Counter Reset**:
```python
def test_retry_counter_reset_after_60s(mock_time):
    """Test per-service counters reset after 60s."""
    mock_time.return_value = 1000.0
    
    # Increment counter
    for _ in range(30):
        increment_retry_counter('service1')
    
    assert check_retry_limit('service1') == False  # Under limit (50)
    
    # Fast-forward 61 seconds
    mock_time.return_value = 1061.0
    
    # Counter should have reset (via TTL or background thread)
    if redis_client:
        # Redis TTL expired
        assert redis_client.get('signal_retry:service1:minute') is None
    
    # New increment should start fresh
    increment_retry_counter('service1')
    # Should be at 1, not 31
```

### Step 4: Update Test Execution Time Target

**Original Target**: <30 seconds  
**Realistic Target**: <10 seconds (with mocked time)

**Breakdown**:
- 50 tests × 0.1s average = 5s
- Setup/teardown overhead = 2s
- Coverage collection = 3s
- **Total**: ~10s

**If using real sleeps**:
- 60s recovery timeout × 3 CBs = 180s
- 60s retry reset test = 60s
- Exponential backoff (2+4+8) × 5 tests = 70s
- **Total**: 310+ seconds ❌ UNACCEPTABLE

---

## Updated Success Criteria

### Test Quality

✅ **No flaky tests**:
- Run 10 times, all pass
- Use `pytest-repeat`: `pytest --count=10`
- Use threading.Barrier for concurrent tests
- Mock time for time-based tests

✅ **Fast test suite**:
- Total runtime <10 seconds (not <30)
- Mock all sleeps (time.sleep, asyncio.sleep)
- Mock all time checks (time.time, datetime.now)
- Parallel test execution: `pytest -n auto`

✅ **Deterministic**:
- Same results every run
- No timing-based assertions
- No random values without seeds
- Explicit synchronization (Barrier, Lock, Event)

### Implementation Checklist

- [ ] Add `mock_time` and `mock_sleep` fixtures
- [ ] Refactor all concurrent tests to use `threading.Barrier`
- [ ] Refactor all time-based tests to mock time
- [ ] Add `pytest-repeat` to dependencies
- [ ] Add `pytest-xdist` for parallel execution
- [ ] Run tests 10 times: `pytest --count=10`
- [ ] Verify <10s execution time
- [ ] Document mocking strategy in test docstrings

---

## Code Examples

### Good Concurrent Test Pattern

```python
def test_concurrent_access_pattern():
    """
    Test concurrent access with deterministic synchronization.
    
    Uses threading.Barrier to force simultaneous execution,
    eliminating timing-based race conditions.
    """
    num_threads = 20
    barrier = threading.Barrier(num_threads)
    results = []
    results_lock = threading.Lock()
    
    def worker(worker_id):
        # All threads wait here until all arrive
        barrier.wait()
        
        # Now all threads execute simultaneously
        result = do_something(worker_id)
        
        # Thread-safe result collection
        with results_lock:
            results.append(result)
    
    threads = [
        threading.Thread(target=worker, args=(i,))
        for i in range(num_threads)
    ]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Make deterministic assertions
    assert len(results) == num_threads
    assert all(isinstance(r, expected_type) for r in results)
```

### Good Time-Based Test Pattern

```python
def test_time_based_pattern(mock_time, mock_sleep):
    """
    Test time-based behavior without real delays.
    
    Mocks time.time() and time.sleep() for fast,
    deterministic execution.
    """
    # Set initial time
    mock_time.return_value = 1000.0
    
    # Trigger time-based behavior
    start_operation()
    
    # Fast-forward time
    mock_time.return_value = 1030.0
    
    # Verify behavior at T+30s
    assert check_timeout_reached() == True
    
    # Verify sleep was called correctly
    mock_sleep.assert_called_with(30)
    
    # Test completes in milliseconds
```

---

## Summary

**Problems Identified**:
1. ❌ Concurrent tests using timing (flaky)
2. ❌ Time-based tests using real sleeps (slow)
3. ❌ Unrealistic <30s target with real timeouts

**Solutions**:
1. ✅ Use `threading.Barrier` for concurrent tests
2. ✅ Mock `time.time()` and `time.sleep()` for time-based tests
3. ✅ Revise target to <10s (achievable with mocking)

**Dependencies to Add**:
```bash
pip install pytest-repeat pytest-xdist
```

**Validation**:
```bash
# Run tests 10 times to catch flakiness
pytest tests/test_signal_flows_comprehensive.py --count=10

# Run tests in parallel (faster)
pytest tests/test_signal_flows_comprehensive.py -n auto

# Verify execution time
pytest tests/test_signal_flows_comprehensive.py --durations=0
```

**Expected Outcome**:
- Zero flaky tests (10/10 runs pass)
- <10 second execution time
- Deterministic, reproducible results
- Parallel execution support
