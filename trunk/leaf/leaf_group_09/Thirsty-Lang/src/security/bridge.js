#!/usr/bin/env node

/**
 * Security Bridge - Connects JavaScript runtime to Python T.A.R.L. runtime
 * Provides bi-directional communication for policy enforcement
 * Enhanced with circuit breaker pattern for resilience
 */

const { spawn } = require('child_process');
const path = require('path');
const EventEmitter = require('events');
const { CircuitBreaker } = require('./circuit-breaker');

class SecurityBridge extends EventEmitter {
  constructor(options = {}) {
    super();
    this.pythonPath = options.pythonPath || 'python3';
    this.tarlPath = options.tarlPath || path.join(__dirname, '..', '..', 'tarl');
    this.pythonProcess = null;
    this.requestId = 0;
    this.pendingRequests = new Map();
    this.metrics = {
      requests: 0,
      successes: 0,
      failures: 0,
      avgResponseTime: 0
    };

    // Initialize circuit breaker with fallback
    this.circuitBreaker = new CircuitBreaker({
      name: 'SecurityBridge-TARL',
      failureThreshold: options.failureThreshold || 5,
      successThreshold: options.successThreshold || 2,
      timeout: options.timeout || 30000,
      resetTimeout: options.resetTimeout || 60000,
      halfOpenMaxCalls: options.halfOpenMaxCalls || 3,
      fallback: options.fallback || this._defaultFallback.bind(this)
    });

    // Forward circuit breaker events
    this.circuitBreaker.on('stateChange', (event) => {
      this.emit('circuitStateChange', event);
    });

    this.circuitBreaker.on('rejected', (event) => {
      this.emit('circuitRejected', event);
    });

    this.circuitBreaker.on('fallback', (event) => {
      this.emit('circuitFallback', event);
    });
  }

  /**
   * Default fallback when circuit is open
   * Returns a safe default policy decision (DENY)
   * @private
   */
  _defaultFallback() {
    return {
      verdict: 'DENY',
      reason: 'Security bridge circuit breaker is OPEN - failing safe',
      metadata: {
        circuitState: this.circuitBreaker.getState(),
        timestamp: new Date().toISOString()
      }
    };
  }

  /**
   * Initialize the bridge and start Python T.A.R.L. runtime
   */
  async initialize() {
    return new Promise((resolve, reject) => {
      const bridgeScriptPath = path.join(__dirname, 'tarl_bridge_server.py');
      
      this.pythonProcess = spawn(this.pythonPath, [bridgeScriptPath], {
        env: { ...process.env, PYTHONPATH: path.dirname(this.tarlPath) },
        stdio: ['pipe', 'pipe', 'pipe']
      });

      let buffer = '';

      this.pythonProcess.stdout.on('data', (data) => {
        buffer += data.toString();
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.trim()) {
            try {
              const response = JSON.parse(line);
              this._handleResponse(response);
            } catch (err) {
              console.error('Failed to parse response:', err, line);
            }
          }
        }
      });

      this.pythonProcess.stderr.on('data', (data) => {
        console.error('Python bridge error:', data.toString());
      });

      this.pythonProcess.on('exit', (code) => {
        console.warn(`Python bridge exited with code ${code}`);
        this.emit('disconnected', code);
      });

      // Wait for ready signal
      const onReady = (response) => {
        if (response.type === 'ready') {
          resolve();
        }
      };
      this.once('_raw_response', onReady);

      // Timeout after 5 seconds
      setTimeout(() => {
        this.off('_raw_response', onReady);
        reject(new Error('Bridge initialization timeout'));
      }, 5000);
    });
  }

  /**
   * Handle response from Python bridge
   */
  _handleResponse(response) {
    this.emit('_raw_response', response);

    if (response.type === 'response' && response.id !== undefined) {
      const pending = this.pendingRequests.get(response.id);
      if (pending) {
        this.pendingRequests.delete(response.id);
        
        const responseTime = Date.now() - pending.startTime;
        this._updateMetrics(responseTime, response.error ? 'failure' : 'success');

        if (response.error) {
          pending.reject(new Error(response.error));
        } else {
          pending.resolve(response.result);
        }
      }
    }
  }

  /**
   * Update bridge metrics
   */
  _updateMetrics(responseTime, status) {
    this.metrics.requests++;
    if (status === 'success') {
      this.metrics.successes++;
    } else {
      this.metrics.failures++;
    }
    
    // Running average
    this.metrics.avgResponseTime = (
      (this.metrics.avgResponseTime * (this.metrics.requests - 1) + responseTime) /
      this.metrics.requests
    );
  }

  /**
   * Send request to Python bridge
   */
  async _sendRequest(method, params = {}) {
    if (!this.pythonProcess || this.pythonProcess.killed) {
      throw new Error('Bridge not initialized or disconnected');
    }

    const id = this.requestId++;
    const request = { id, method, params };

    return new Promise((resolve, reject) => {
      this.pendingRequests.set(id, { 
        resolve, 
        reject, 
        startTime: Date.now() 
      });

      try {
        this.pythonProcess.stdin.write(JSON.stringify(request) + '\n');
      } catch (err) {
        this.pendingRequests.delete(id);
        reject(err);
      }

      // Timeout after 30 seconds
      setTimeout(() => {
        if (this.pendingRequests.has(id)) {
          this.pendingRequests.delete(id);
          reject(new Error('Request timeout'));
        }
      }, 30000);
    });
  }

  /**
   * Evaluate policy through T.A.R.L. runtime with circuit breaker protection
   */
  async evaluatePolicy(context) {
    return await this.circuitBreaker.execute(
      () => this._sendRequest('evaluate_policy', { context })
    );
  }

  /**
   * Load policies from file with circuit breaker protection
   */
  async loadPolicies(policyPath) {
    return await this.circuitBreaker.execute(
      () => this._sendRequest('load_policies', { path: policyPath })
    );
  }

  /**
   * Reload policies (hot-reload) with circuit breaker protection
   */
  async reloadPolicies() {
    return await this.circuitBreaker.execute(
      () => this._sendRequest('reload_policies', {})
    );
  }

  /**
   * Get runtime metrics with circuit breaker protection
   */
  async getRuntimeMetrics() {
    return await this.circuitBreaker.execute(
      () => this._sendRequest('get_metrics', {})
    );
  }

  /**
   * Get bridge metrics (includes circuit breaker metrics)
   */
  getBridgeMetrics() {
    return {
      bridge: { ...this.metrics },
      circuitBreaker: this.circuitBreaker.getMetrics()
    };
  }

  /**
   * Get circuit breaker health status
   */
  getCircuitHealth() {
    return this.circuitBreaker.getHealth();
  }

  /**
   * Force circuit breaker to open (for maintenance or emergencies)
   */
  openCircuit() {
    this.circuitBreaker.forceOpen();
  }

  /**
   * Force circuit breaker to close (use with caution)
   */
  closeCircuit() {
    this.circuitBreaker.forceClose();
  }

  /**
   * Reset circuit breaker metrics and state
   */
  resetCircuit() {
    this.circuitBreaker.reset();
  }

  /**
   * Shutdown the bridge
   */
  async shutdown() {
    if (this.pythonProcess && !this.pythonProcess.killed) {
      await this._sendRequest('shutdown', {});
      this.pythonProcess.kill();
      this.pythonProcess = null;
    }
  }
}

module.exports = { SecurityBridge };
