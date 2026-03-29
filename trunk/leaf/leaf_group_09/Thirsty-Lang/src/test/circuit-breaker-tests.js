/**
 * Circuit Breaker Tests
 * Comprehensive test suite for circuit breaker pattern implementation
 */

const { CircuitBreaker, CircuitState } = require('../security/circuit-breaker');

const tests = [];
let passed = 0;
let failed = 0;

function test(name, fn) {
  tests.push({ name, fn });
}

function runTests() {
  console.log('Running Circuit Breaker Tests...\n');

  for (const { name, fn } of tests) {
    try {
      fn();
      console.log(`✓ ${name}`);
      passed++;
    } catch (error) {
      console.log(`✗ ${name}`);
      console.log(`  Error: ${error.message}`);
      failed++;
    }
  }

  console.log(`\n${tests.length} tests, ${passed} passed, ${failed} failed`);
  process.exit(failed > 0 ? 1 : 0);
}

// Helper function to sleep
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Helper function for async test execution
async function asyncTest(name, fn) {
  test(name, async () => await fn());
}

// ============================================================================
// Basic Circuit Breaker Tests
// ============================================================================

// Test 1: Initial state is CLOSED
test('Circuit breaker starts in CLOSED state', () => {
  const cb = new CircuitBreaker();

  if (cb.getState() !== CircuitState.CLOSED) {
    throw new Error(`Expected CLOSED state, got: ${cb.getState()}`);
  }
});

// Test 2: Successful execution
test('Successful execution increments success count', async () => {
  const cb = new CircuitBreaker();
  const fn = async () => 'success';

  const result = await cb.execute(fn);

  if (result !== 'success') {
    throw new Error(`Expected 'success', got: ${result}`);
  }

  const metrics = cb.getMetrics();
  if (metrics.successfulRequests !== 1) {
    throw new Error(`Expected 1 successful request, got: ${metrics.successfulRequests}`);
  }
});

// Test 3: Failed execution increments failure count
test('Failed execution increments failure count', async () => {
  const cb = new CircuitBreaker({ failureThreshold: 10 });
  const fn = async () => { throw new Error('test error'); };

  try {
    await cb.execute(fn);
    throw new Error('Expected error to be thrown');
  } catch (e) {
    if (!e.message.includes('test error')) {
      throw new Error(`Wrong error message: ${e.message}`);
    }
  }

  const metrics = cb.getMetrics();
  if (metrics.failedRequests !== 1) {
    throw new Error(`Expected 1 failed request, got: ${metrics.failedRequests}`);
  }
});

// Test 4: Circuit opens after threshold failures
test('Circuit opens after threshold failures', async () => {
  const cb = new CircuitBreaker({ failureThreshold: 3 });
  const fn = async () => { throw new Error('failure'); };

  // Execute 3 failures
  for (let i = 0; i < 3; i++) {
    try {
      await cb.execute(fn);
    } catch (e) {
      // Expected
    }
  }

  if (cb.getState() !== CircuitState.OPEN) {
    throw new Error(`Expected OPEN state, got: ${cb.getState()}`);
  }
});

// Test 5: Circuit rejects requests when OPEN
test('Circuit rejects requests when OPEN', async () => {
  const cb = new CircuitBreaker({ failureThreshold: 2, resetTimeout: 10000 });
  const fn = async () => { throw new Error('failure'); };

  // Open the circuit
  for (let i = 0; i < 2; i++) {
    try {
      await cb.execute(fn);
    } catch (e) {
      // Expected
    }
  }

  // Try to execute when open
  try {
    await cb.execute(fn);
    throw new Error('Expected circuit to reject request');
  } catch (e) {
    if (!e.message.includes('OPEN')) {
      throw new Error(`Expected OPEN error, got: ${e.message}`);
    }
  }

  const metrics = cb.getMetrics();
  if (metrics.rejectedRequests === 0) {
    throw new Error('Expected at least 1 rejected request');
  }
});

// Test 6: Circuit transitions to HALF_OPEN after reset timeout
test('Circuit transitions to HALF_OPEN after reset timeout', async () => {
  const cb = new CircuitBreaker({
    failureThreshold: 2,
    resetTimeout: 100  // 100ms for testing
  });
  const fn = async () => { throw new Error('failure'); };

  // Open the circuit
  for (let i = 0; i < 2; i++) {
    try {
      await cb.execute(fn);
    } catch (e) {
      // Expected
    }
  }

  if (cb.getState() !== CircuitState.OPEN) {
    throw new Error('Circuit should be OPEN');
  }

  // Wait for reset timeout
  await sleep(150);

  // Next request should transition to HALF_OPEN
  const successFn = async () => 'success';
  await cb.execute(successFn);

  // After successful execution in HALF_OPEN, should transition to CLOSED
  if (cb.getState() !== CircuitState.HALF_OPEN && cb.getState() !== CircuitState.CLOSED) {
    throw new Error(`Expected HALF_OPEN or CLOSED, got: ${cb.getState()}`);
  }
});

// Test 7: Successful requests in HALF_OPEN close the circuit
test('Successful requests in HALF_OPEN close the circuit', async () => {
  const cb = new CircuitBreaker({
    failureThreshold: 2,
    successThreshold: 2,
    resetTimeout: 50
  });

  // Open the circuit
  const failFn = async () => { throw new Error('failure'); };
  for (let i = 0; i < 2; i++) {
    try {
      await cb.execute(failFn);
    } catch (e) {
      // Expected
    }
  }

  // Wait for reset
  await sleep(100);

  // Execute successful requests
  const successFn = async () => 'success';
  await cb.execute(successFn); // Transitions to HALF_OPEN
  await cb.execute(successFn); // Should close circuit

  if (cb.getState() !== CircuitState.CLOSED) {
    throw new Error(`Expected CLOSED state, got: ${cb.getState()}`);
  }
});

// Test 8: Failure in HALF_OPEN reopens circuit
test('Failure in HALF_OPEN reopens circuit', async () => {
  const cb = new CircuitBreaker({
    failureThreshold: 2,
    resetTimeout: 50
  });

  // Open the circuit
  const failFn = async () => { throw new Error('failure'); };
  for (let i = 0; i < 2; i++) {
    try {
      await cb.execute(failFn);
    } catch (e) {
      // Expected
    }
  }

  // Wait for reset
  await sleep(100);

  // Execute one failure in HALF_OPEN
  try {
    await cb.execute(failFn);
  } catch (e) {
    // Expected
  }

  if (cb.getState() !== CircuitState.OPEN) {
    throw new Error(`Expected OPEN state, got: ${cb.getState()}`);
  }
});

// ============================================================================
// Timeout Tests
// ============================================================================

// Test 9: Timeout detection
test('Circuit breaker detects timeouts', async () => {
  const cb = new CircuitBreaker({ timeout: 100, failureThreshold: 10 });
  const slowFn = async () => {
    await sleep(200);
    return 'should not reach here';
  };

  try {
    await cb.execute(slowFn);
    throw new Error('Expected timeout error');
  } catch (e) {
    if (!e.message.includes('timeout')) {
      throw new Error(`Expected timeout error, got: ${e.message}`);
    }
  }

  const metrics = cb.getMetrics();
  if (metrics.timeouts === 0) {
    throw new Error('Expected at least 1 timeout');
  }
});

// ============================================================================
// Fallback Tests
// ============================================================================

// Test 10: Fallback is called when circuit is OPEN
test('Fallback is called when circuit is OPEN', async () => {
  let fallbackCalled = false;
  const fallback = async () => {
    fallbackCalled = true;
    return 'fallback result';
  };

  const cb = new CircuitBreaker({
    failureThreshold: 2,
    resetTimeout: 10000,
    fallback
  });

  // Open the circuit
  const failFn = async () => { throw new Error('failure'); };
  for (let i = 0; i < 2; i++) {
    try {
      await cb.execute(failFn);
    } catch (e) {
      // Expected
    }
  }

  // Execute when circuit is open - should use fallback
  const result = await cb.execute(async () => 'original');

  if (!fallbackCalled) {
    throw new Error('Fallback was not called');
  }

  if (result !== 'fallback result') {
    throw new Error(`Expected fallback result, got: ${result}`);
  }
});

// Test 11: Fallback is called on failure
test('Fallback is called on failure', async () => {
  let fallbackCalled = false;
  const fallback = async () => {
    fallbackCalled = true;
    return 'fallback';
  };

  const cb = new CircuitBreaker({ failureThreshold: 10, fallback });
  const failFn = async () => { throw new Error('failure'); };

  const result = await cb.execute(failFn);

  if (!fallbackCalled) {
    throw new Error('Fallback was not called');
  }

  if (result !== 'fallback') {
    throw new Error(`Expected fallback result, got: ${result}`);
  }
});

// ============================================================================
// Metrics Tests
// ============================================================================

// Test 12: Metrics are tracked correctly
test('Metrics are tracked correctly', async () => {
  const cb = new CircuitBreaker({ failureThreshold: 10 });

  // Execute 5 successful, 3 failed
  const successFn = async () => 'success';
  const failFn = async () => { throw new Error('failure'); };

  for (let i = 0; i < 5; i++) {
    await cb.execute(successFn);
  }

  for (let i = 0; i < 3; i++) {
    try {
      await cb.execute(failFn);
    } catch (e) {
      await cb.execute(successFn); // Use fallback
    }
  }

  const metrics = cb.getMetrics();

  if (metrics.totalRequests < 8) {
    throw new Error(`Expected at least 8 requests, got: ${metrics.totalRequests}`);
  }

  if (metrics.successfulRequests < 5) {
    throw new Error(`Expected at least 5 successful requests, got: ${metrics.successfulRequests}`);
  }
});

// Test 13: Average response time is calculated
test('Average response time is calculated', async () => {
  const cb = new CircuitBreaker();
  const fn = async () => {
    await sleep(10);
    return 'success';
  };

  await cb.execute(fn);
  await cb.execute(fn);

  const metrics = cb.getMetrics();

  if (metrics.averageResponseTime === 0) {
    throw new Error('Expected non-zero average response time');
  }

  if (metrics.averageResponseTime < 10) {
    throw new Error(`Expected response time >= 10ms, got: ${metrics.averageResponseTime}`);
  }
});

// ============================================================================
// Manual Control Tests
// ============================================================================

// Test 14: Force open
test('Can manually force circuit open', () => {
  const cb = new CircuitBreaker();

  if (cb.getState() !== CircuitState.CLOSED) {
    throw new Error('Circuit should start CLOSED');
  }

  cb.forceOpen();

  if (cb.getState() !== CircuitState.OPEN) {
    throw new Error('Circuit should be OPEN after forceOpen()');
  }
});

// Test 15: Force close
test('Can manually force circuit close', async () => {
  const cb = new CircuitBreaker({ failureThreshold: 2 });
  const failFn = async () => { throw new Error('failure'); };

  // Open the circuit
  for (let i = 0; i < 2; i++) {
    try {
      await cb.execute(failFn);
    } catch (e) {
      // Expected
    }
  }

  if (cb.getState() !== CircuitState.OPEN) {
    throw new Error('Circuit should be OPEN');
  }

  cb.forceClose();

  if (cb.getState() !== CircuitState.CLOSED) {
    throw new Error('Circuit should be CLOSED after forceClose()');
  }
});

// Test 16: Reset clears metrics
test('Reset clears metrics and state', async () => {
  const cb = new CircuitBreaker({ failureThreshold: 2 });
  const failFn = async () => { throw new Error('failure'); };

  // Generate some metrics
  for (let i = 0; i < 2; i++) {
    try {
      await cb.execute(failFn);
    } catch (e) {
      // Expected
    }
  }

  const metricsBefore = cb.getMetrics();
  if (metricsBefore.totalRequests === 0) {
    throw new Error('Expected some requests before reset');
  }

  cb.reset();

  const metricsAfter = cb.getMetrics();
  if (metricsAfter.totalRequests !== 0) {
    throw new Error(`Expected 0 requests after reset, got: ${metricsAfter.totalRequests}`);
  }

  if (cb.getState() !== CircuitState.CLOSED) {
    throw new Error('Circuit should be CLOSED after reset');
  }
});

// ============================================================================
// Health Check Tests
// ============================================================================

// Test 17: Health check returns correct status
test('Health check returns correct status', () => {
  const cb = new CircuitBreaker();
  const health = cb.getHealth();

  if (!health.healthy) {
    throw new Error('Expected healthy status when circuit is CLOSED');
  }

  if (health.state !== CircuitState.CLOSED) {
    throw new Error(`Expected CLOSED state in health, got: ${health.state}`);
  }
});

// Test 18: Health check shows degraded in HALF_OPEN
test('Health check shows degraded in HALF_OPEN', () => {
  const cb = new CircuitBreaker();
  cb.forceHalfOpen();

  const health = cb.getHealth();

  if (!health.degraded) {
    throw new Error('Expected degraded status when circuit is HALF_OPEN');
  }
});

// Test 19: Health check shows unavailable when OPEN
test('Health check shows unavailable when OPEN', () => {
  const cb = new CircuitBreaker();
  cb.forceOpen();

  const health = cb.getHealth();

  if (!health.unavailable) {
    throw new Error('Expected unavailable status when circuit is OPEN');
  }
});

// Test 20: isRequestAllowed returns correct values
test('isRequestAllowed returns correct values', async () => {
  const cb = new CircuitBreaker({ failureThreshold: 2, resetTimeout: 50 });

  // CLOSED - should allow
  if (!cb.isRequestAllowed()) {
    throw new Error('Should allow requests when CLOSED');
  }

  // Open the circuit
  const failFn = async () => { throw new Error('failure'); };
  for (let i = 0; i < 2; i++) {
    try {
      await cb.execute(failFn);
    } catch (e) {
      // Expected
    }
  }

  // OPEN - should not allow (immediately after opening)
  if (cb.isRequestAllowed()) {
    throw new Error('Should not allow requests immediately after opening');
  }

  // Wait for reset timeout
  await sleep(100);

  // OPEN (after timeout) - should allow (to test recovery)
  if (!cb.isRequestAllowed()) {
    throw new Error('Should allow requests after reset timeout');
  }
});

// Run all tests
runTests();
