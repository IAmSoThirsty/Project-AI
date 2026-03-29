/**
 * Circuit Breaker Pattern Implementation
 * Provides fault tolerance and resilience for external service calls
 *
 * STATES:
 * - CLOSED: Normal operation, requests pass through
 * - OPEN: Failures exceeded threshold, requests fail fast
 * - HALF_OPEN: Testing if service recovered, limited requests allowed
 *
 * FEATURES:
 * - Automatic state transitions based on failure/success rates
 * - Configurable thresholds and timeouts
 * - Metrics tracking for monitoring
 * - Event emission for observability
 * - Graceful degradation with fallback support
 */

const EventEmitter = require('events');

// Circuit breaker states
const CircuitState = {
  CLOSED: 'CLOSED',       // Normal operation
  OPEN: 'OPEN',           // Circuit is open, failing fast
  HALF_OPEN: 'HALF_OPEN'  // Testing if service recovered
};

/**
 * Circuit Breaker implementation for resilient service calls
 */
class CircuitBreaker extends EventEmitter {
  /**
   * Create a circuit breaker
   * @param {Object} options - Configuration options
   * @param {number} options.failureThreshold - Number of failures before opening (default: 5)
   * @param {number} options.successThreshold - Number of successes to close from half-open (default: 2)
   * @param {number} options.timeout - Request timeout in ms (default: 30000)
   * @param {number} options.resetTimeout - Time to wait before half-open in ms (default: 60000)
   * @param {number} options.halfOpenMaxCalls - Max calls in half-open state (default: 3)
   * @param {Function} options.fallback - Optional fallback function when circuit is open
   * @param {string} options.name - Optional name for identification
   */
  constructor(options = {}) {
    super();

    // Configuration
    this.name = options.name || 'unnamed';
    this.failureThreshold = options.failureThreshold || 5;
    this.successThreshold = options.successThreshold || 2;
    this.timeout = options.timeout || 30000;
    this.resetTimeout = options.resetTimeout || 60000;
    this.halfOpenMaxCalls = options.halfOpenMaxCalls || 3;
    this.fallback = options.fallback || null;

    // State management
    this.state = CircuitState.CLOSED;
    this.failureCount = 0;
    this.successCount = 0;
    this.halfOpenAttempts = 0;
    this.nextAttempt = Date.now();

    // Metrics
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      rejectedRequests: 0,
      timeouts: 0,
      fallbackCalls: 0,
      stateTransitions: {
        [CircuitState.CLOSED]: 0,
        [CircuitState.OPEN]: 0,
        [CircuitState.HALF_OPEN]: 0
      },
      lastStateChange: Date.now(),
      totalDowntime: 0,
      averageResponseTime: 0
    };

    // Request tracking for timeout calculation
    this.requestTimes = [];
    this.maxRequestTracking = 100;
  }

  /**
   * Execute a function with circuit breaker protection
   * @param {Function} fn - Async function to execute
   * @param {...any} args - Arguments to pass to the function
   * @returns {Promise<any>} Result of the function or fallback
   */
  async execute(fn, ...args) {
    this.metrics.totalRequests++;

    // Check if circuit is open
    if (this.state === CircuitState.OPEN) {
      // Check if it's time to transition to half-open
      if (Date.now() >= this.nextAttempt) {
        this._transitionTo(CircuitState.HALF_OPEN);
      } else {
        // Circuit is still open, fail fast
        this.metrics.rejectedRequests++;
        this.emit('rejected', {
          name: this.name,
          state: this.state,
          nextAttempt: this.nextAttempt
        });

        // Use fallback if available
        if (this.fallback) {
          this.metrics.fallbackCalls++;
          this.emit('fallback', { name: this.name });
          return await this.fallback(...args);
        }

        throw new Error(`Circuit breaker [${this.name}] is OPEN - failing fast`);
      }
    }

    // Check if we should allow the request in half-open state
    if (this.state === CircuitState.HALF_OPEN) {
      if (this.halfOpenAttempts >= this.halfOpenMaxCalls) {
        // Too many concurrent requests in half-open
        this.metrics.rejectedRequests++;
        this.emit('rejected', {
          name: this.name,
          state: this.state,
          reason: 'half-open-limit'
        });

        if (this.fallback) {
          this.metrics.fallbackCalls++;
          this.emit('fallback', { name: this.name });
          return await this.fallback(...args);
        }

        throw new Error(`Circuit breaker [${this.name}] is HALF_OPEN - max concurrent requests reached`);
      }
      this.halfOpenAttempts++;
    }

    // Execute the function with timeout
    const startTime = Date.now();
    try {
      const result = await this._executeWithTimeout(fn, args);
      const responseTime = Date.now() - startTime;

      // Success - update metrics and state
      this._recordSuccess(responseTime);

      return result;
    } catch (error) {
      const responseTime = Date.now() - startTime;

      // Check if it was a timeout
      if (error.message && error.message.includes('timeout')) {
        this.metrics.timeouts++;
      }

      // Failure - update metrics and state
      this._recordFailure(responseTime, error);

      // Use fallback if available
      if (this.fallback) {
        this.metrics.fallbackCalls++;
        this.emit('fallback', { name: this.name, error: error.message });
        return await this.fallback(...args);
      }

      throw error;
    } finally {
      if (this.state === CircuitState.HALF_OPEN) {
        this.halfOpenAttempts--;
      }
    }
  }

  /**
   * Execute function with timeout protection
   * @private
   */
  async _executeWithTimeout(fn, args) {
    return Promise.race([
      fn(...args),
      new Promise((_, reject) => {
        setTimeout(() => {
          reject(new Error(`Circuit breaker [${this.name}] timeout after ${this.timeout}ms`));
        }, this.timeout);
      })
    ]);
  }

  /**
   * Record successful execution
   * @private
   */
  _recordSuccess(responseTime) {
    this.metrics.successfulRequests++;
    this._updateResponseTime(responseTime);

    this.emit('success', {
      name: this.name,
      state: this.state,
      responseTime
    });

    if (this.state === CircuitState.HALF_OPEN) {
      this.successCount++;

      // Check if we should close the circuit
      if (this.successCount >= this.successThreshold) {
        this._transitionTo(CircuitState.CLOSED);
      }
    } else if (this.state === CircuitState.CLOSED) {
      // Reset failure count on success
      this.failureCount = 0;
    }
  }

  /**
   * Record failed execution
   * @private
   */
  _recordFailure(responseTime, error) {
    this.metrics.failedRequests++;
    this._updateResponseTime(responseTime);

    this.emit('failure', {
      name: this.name,
      state: this.state,
      error: error.message,
      responseTime
    });

    if (this.state === CircuitState.HALF_OPEN) {
      // Immediate transition to open on failure in half-open
      this._transitionTo(CircuitState.OPEN);
    } else if (this.state === CircuitState.CLOSED) {
      this.failureCount++;

      // Check if we should open the circuit
      if (this.failureCount >= this.failureThreshold) {
        this._transitionTo(CircuitState.OPEN);
      }
    }
  }

  /**
   * Update average response time
   * @private
   */
  _updateResponseTime(responseTime) {
    this.requestTimes.push(responseTime);

    // Keep only recent request times
    if (this.requestTimes.length > this.maxRequestTracking) {
      this.requestTimes.shift();
    }

    // Calculate average
    const sum = this.requestTimes.reduce((a, b) => a + b, 0);
    this.metrics.averageResponseTime = sum / this.requestTimes.length;
  }

  /**
   * Transition to a new state
   * @private
   */
  _transitionTo(newState) {
    const oldState = this.state;
    this.state = newState;

    // Update metrics
    this.metrics.stateTransitions[newState]++;
    const now = Date.now();

    // Track downtime when entering open state
    if (oldState === CircuitState.OPEN && newState !== CircuitState.OPEN) {
      this.metrics.totalDowntime += now - this.metrics.lastStateChange;
    }

    this.metrics.lastStateChange = now;

    // Reset counters based on state
    if (newState === CircuitState.CLOSED) {
      this.failureCount = 0;
      this.successCount = 0;
      this.halfOpenAttempts = 0;
    } else if (newState === CircuitState.OPEN) {
      this.successCount = 0;
      this.halfOpenAttempts = 0;
      this.nextAttempt = now + this.resetTimeout;
    } else if (newState === CircuitState.HALF_OPEN) {
      this.successCount = 0;
      this.failureCount = 0;
      this.halfOpenAttempts = 0;
    }

    this.emit('stateChange', {
      name: this.name,
      from: oldState,
      to: newState,
      timestamp: now
    });
  }

  /**
   * Get current state
   * @returns {string} Current circuit breaker state
   */
  getState() {
    return this.state;
  }

  /**
   * Get comprehensive metrics
   * @returns {Object} Metrics object
   */
  getMetrics() {
    return {
      ...this.metrics,
      state: this.state,
      failureCount: this.failureCount,
      successCount: this.successCount,
      halfOpenAttempts: this.halfOpenAttempts,
      nextAttempt: this.nextAttempt,
      successRate: this.metrics.totalRequests > 0
        ? (this.metrics.successfulRequests / this.metrics.totalRequests * 100).toFixed(2) + '%'
        : '0%',
      failureRate: this.metrics.totalRequests > 0
        ? (this.metrics.failedRequests / this.metrics.totalRequests * 100).toFixed(2) + '%'
        : '0%',
      rejectionRate: this.metrics.totalRequests > 0
        ? (this.metrics.rejectedRequests / this.metrics.totalRequests * 100).toFixed(2) + '%'
        : '0%'
    };
  }

  /**
   * Manually force the circuit to open
   * Useful for maintenance or when external monitoring detects issues
   */
  forceOpen() {
    if (this.state !== CircuitState.OPEN) {
      this.emit('forced', { name: this.name, action: 'open' });
      this._transitionTo(CircuitState.OPEN);
    }
  }

  /**
   * Manually force the circuit to close
   * Use with caution - should only be done when service is confirmed healthy
   */
  forceClose() {
    if (this.state !== CircuitState.CLOSED) {
      this.emit('forced', { name: this.name, action: 'close' });
      this._transitionTo(CircuitState.CLOSED);
    }
  }

  /**
   * Manually transition to half-open
   * Useful for testing or gradual recovery
   */
  forceHalfOpen() {
    if (this.state !== CircuitState.HALF_OPEN) {
      this.emit('forced', { name: this.name, action: 'half-open' });
      this._transitionTo(CircuitState.HALF_OPEN);
    }
  }

  /**
   * Reset all metrics and state
   */
  reset() {
    this._transitionTo(CircuitState.CLOSED);
    this.failureCount = 0;
    this.successCount = 0;
    this.halfOpenAttempts = 0;
    this.requestTimes = [];

    // Reset metrics but keep configuration
    this.metrics = {
      totalRequests: 0,
      successfulRequests: 0,
      failedRequests: 0,
      rejectedRequests: 0,
      timeouts: 0,
      fallbackCalls: 0,
      stateTransitions: {
        [CircuitState.CLOSED]: 0,
        [CircuitState.OPEN]: 0,
        [CircuitState.HALF_OPEN]: 0
      },
      lastStateChange: Date.now(),
      totalDowntime: 0,
      averageResponseTime: 0
    };

    this.emit('reset', { name: this.name });
  }

  /**
   * Check if the circuit is currently allowing requests
   * @returns {boolean} True if requests are allowed
   */
  isRequestAllowed() {
    if (this.state === CircuitState.CLOSED) {
      return true;
    }

    if (this.state === CircuitState.HALF_OPEN) {
      return this.halfOpenAttempts < this.halfOpenMaxCalls;
    }

    if (this.state === CircuitState.OPEN) {
      return Date.now() >= this.nextAttempt;
    }

    return false;
  }

  /**
   * Get health status
   * @returns {Object} Health status with state and metrics
   */
  getHealth() {
    const metrics = this.getMetrics();

    return {
      name: this.name,
      state: this.state,
      healthy: this.state === CircuitState.CLOSED,
      degraded: this.state === CircuitState.HALF_OPEN,
      unavailable: this.state === CircuitState.OPEN,
      nextCheckTime: this.state === CircuitState.OPEN ? new Date(this.nextAttempt).toISOString() : null,
      metrics: {
        successRate: metrics.successRate,
        failureRate: metrics.failureRate,
        averageResponseTime: Math.round(metrics.averageResponseTime),
        totalDowntime: metrics.totalDowntime
      }
    };
  }
}

module.exports = {
  CircuitBreaker,
  CircuitState
};
