/**
 * TARL Bridge - JavaScript to Python TARL Runtime Bridge
 * 
 * Provides seamless integration between Thirsty-Lang JavaScript runtime
 * and TARL Python security engine via JSON-based IPC.
 * 
 * @module tarl-bridge
 * @version 1.0.0
 * @license MIT
 */

const { spawn } = require('child_process');
const { EventEmitter } = require('events');
const crypto = require('crypto');

/**
 * Bridge configuration options
 * @typedef {Object} BridgeOptions
 * @property {string} pythonPath - Path to Python interpreter
 * @property {string} tarlModule - TARL module name
 * @property {string} policyDir - Directory containing policy files
 * @property {string} logLevel - Logging level (debug|info|warn|error)
 * @property {number} timeout - Request timeout in milliseconds
 * @property {number} retryAttempts - Maximum retry attempts on failure
 * @property {number} maxMessageSize - Maximum message size in bytes
 * @property {string} logFile - Path to log file
 */

/**
 * Security decision result
 * @typedef {Object} Decision
 * @property {boolean} allowed - Whether operation is allowed
 * @property {string} [reason] - Denial reason if not allowed
 * @property {string} [policyId] - ID of matched policy rule
 * @property {string[]} [conditions] - Additional conditions to satisfy
 * @property {number} [expiresAt] - Timestamp when decision expires
 * @property {Object} [metadata] - Additional metadata
 */

/**
 * Runtime metrics
 * @typedef {Object} Metrics
 * @property {number} uptime - Runtime uptime in seconds
 * @property {number} requestsProcessed - Total requests processed
 * @property {number} policiesLoaded - Number of loaded policies
 * @property {number} cacheHitRate - Cache hit rate (0-1)
 * @property {number} avgResponseTime - Average response time in ms
 * @property {number} memoryUsageMb - Current memory usage in MB
 * @property {number} cpuPercent - Current CPU usage percentage
 */

/**
 * TARL Bridge - Manages communication with Python TARL runtime
 * 
 * @class TARLBridge
 * @extends EventEmitter
 * @example
 * const bridge = new TARLBridge({
 *   pythonPath: 'python3',
 *   policyDir: './policies'
 * });
 * await bridge.initialize();
 * const decision = await bridge.evaluatePolicy({
 *   operation: 'file_read',
 *   resource: '/etc/passwd'
 * });
 */
class TARLBridge extends EventEmitter {
  /**
   * Create a new TARL bridge instance
   * @param {BridgeOptions} options - Configuration options
   */
  constructor(options = {}) {
    super();
    
    this.options = {
      pythonPath: options.pythonPath || 'python3',
      tarlModule: options.tarlModule || 'tarl.runtime',
      policyDir: options.policyDir || './policies',
      logLevel: options.logLevel || 'info',
      timeout: options.timeout || 5000,
      retryAttempts: options.retryAttempts || 3,
      maxMessageSize: options.maxMessageSize || 10 * 1024 * 1024, // 10MB
      logFile: options.logFile || null
    };
    
    this.process = null;
    this.initialized = false;
    this.pendingRequests = new Map();
    this.messageBuffer = '';
    this.requestIdCounter = 0;
    this.metrics = {
      startTime: Date.now(),
      requestsProcessed: 0,
      requestsFailed: 0,
      totalResponseTime: 0
    };
    
    this._setupLogging();
  }
  
  /**
   * Initialize the bridge and spawn Python runtime
   * @returns {Promise<void>}
   * @throws {Error} If initialization fails
   */
  async initialize() {
    if (this.initialized) {
      this._log('warn', 'Bridge already initialized');
      return;
    }
    
    this._log('info', 'Initializing TARL bridge...');
    
    try {
      await this._spawnPythonRuntime();
      await this._waitForReady(10000); // 10 second timeout
      this.initialized = true;
      this._log('info', 'TARL bridge initialized successfully');
      this.emit('ready');
    } catch (error) {
      this._log('error', 'Failed to initialize bridge', error);
      throw new Error(`Bridge initialization failed: ${error.message}`);
    }
  }
  
  /**
   * Spawn Python TARL runtime process
   * @private
   * @returns {Promise<void>}
   */
  async _spawnPythonRuntime() {
    return new Promise((resolve, reject) => {
      const args = [
        '-m', this.options.tarlModule,
        '--policy-dir', this.options.policyDir,
        '--log-level', this.options.logLevel.toUpperCase(),
        '--mode', 'bridge'
      ];
      
      this._log('debug', `Spawning Python: ${this.options.pythonPath} ${args.join(' ')}`);
      
      this.process = spawn(this.options.pythonPath, args, {
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, PYTHONUNBUFFERED: '1' }
      });
      
      // Handle stdout (JSON responses)
      this.process.stdout.on('data', (data) => {
        this._handleStdout(data);
      });
      
      // Handle stderr (logs and errors)
      this.process.stderr.on('data', (data) => {
        this._handleStderr(data);
      });
      
      // Handle process exit
      this.process.on('exit', (code, signal) => {
        this._handleExit(code, signal);
      });
      
      // Handle process errors
      this.process.on('error', (error) => {
        this._log('error', 'Python process error', error);
        reject(error);
      });
      
      // Wait for process to start
      setTimeout(() => {
        if (this.process && this.process.pid) {
          resolve();
        } else {
          reject(new Error('Python process failed to start'));
        }
      }, 1000);
    });
  }
  
  /**
   * Wait for runtime ready signal
   * @private
   * @param {number} timeout - Timeout in milliseconds
   * @returns {Promise<void>}
   */
  async _waitForReady(timeout) {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error('Runtime ready timeout'));
      }, timeout);
      
      const readyHandler = () => {
        clearTimeout(timeoutId);
        this.removeListener('runtime_ready', readyHandler);
        resolve();
      };
      
      this.once('runtime_ready', readyHandler);
      
      // Send ping to trigger ready response
      this._sendMessage({ method: 'ping' }).catch(reject);
    });
  }
  
  /**
   * Handle stdout data from Python process
   * @private
   * @param {Buffer} data - Raw data from stdout
   */
  _handleStdout(data) {
    this.messageBuffer += data.toString();
    
    // Process complete JSON messages (newline-delimited)
    const lines = this.messageBuffer.split('\n');
    this.messageBuffer = lines.pop() || '';
    
    for (const line of lines) {
      if (!line.trim()) continue;
      
      try {
        const message = JSON.parse(line);
        this._handleMessage(message);
      } catch (error) {
        this._log('error', 'Failed to parse JSON message', { line, error });
      }
    }
  }
  
  /**
   * Handle stderr data from Python process
   * @private
   * @param {Buffer} data - Raw data from stderr
   */
  _handleStderr(data) {
    const text = data.toString().trim();
    if (!text) return;
    
    // Python logs come through stderr
    const lines = text.split('\n');
    for (const line of lines) {
      // Try to parse structured logs
      if (line.includes('{') && line.includes('}')) {
        try {
          const logData = JSON.parse(line.substring(line.indexOf('{')));
          this._log(logData.level || 'info', logData.message, logData.data);
        } catch {
          this._log('info', `[Python] ${line}`);
        }
      } else {
        this._log('info', `[Python] ${line}`);
      }
    }
  }
  
  /**
   * Handle message from Python runtime
   * @private
   * @param {Object} message - Parsed JSON message
   */
  _handleMessage(message) {
    this.emit('message', message);
    
    // Handle special messages
    if (message.type === 'ready') {
      this.emit('runtime_ready');
      return;
    }
    
    if (message.type === 'log') {
      this._log(message.level, message.message, message.data);
      return;
    }
    
    // Handle request responses
    if (message.id && this.pendingRequests.has(message.id)) {
      const request = this.pendingRequests.get(message.id);
      clearTimeout(request.timeoutId);
      this.pendingRequests.delete(message.id);
      
      // Update metrics
      const responseTime = Date.now() - request.startTime;
      this.metrics.requestsProcessed++;
      this.metrics.totalResponseTime += responseTime;
      
      if (message.error) {
        this.metrics.requestsFailed++;
        this._log('error', 'Request failed', { id: message.id, error: message.error });
        request.reject(new Error(message.error.message || 'Unknown error'));
      } else {
        request.resolve(message.result);
      }
    }
  }
  
  /**
   * Handle Python process exit
   * @private
   * @param {number} code - Exit code
   * @param {string} signal - Exit signal
   */
  _handleExit(code, signal) {
    this._log('warn', 'Python process exited', { code, signal });
    this.initialized = false;
    this.process = null;
    
    // Reject all pending requests
    for (const [id, request] of this.pendingRequests.entries()) {
      clearTimeout(request.timeoutId);
      request.reject(new Error('Python process exited'));
    }
    this.pendingRequests.clear();
    
    this.emit('exit', { code, signal });
  }
  
  /**
   * Send message to Python runtime
   * @private
   * @param {Object} message - Message to send
   * @returns {Promise<any>} Response from runtime
   */
  async _sendMessage(message) {
    if (!this.process || !this.initialized) {
      throw new Error('Bridge not initialized');
    }
    
    return new Promise((resolve, reject) => {
      const id = `req_${++this.requestIdCounter}_${crypto.randomBytes(4).toString('hex')}`;
      const request = { method: message.method, params: message.params || {}, id };
      
      const timeoutId = setTimeout(() => {
        this.pendingRequests.delete(id);
        reject(new Error(`Request timeout after ${this.options.timeout}ms`));
      }, this.options.timeout);
      
      this.pendingRequests.set(id, {
        resolve,
        reject,
        timeoutId,
        startTime: Date.now()
      });
      
      const json = JSON.stringify(request) + '\n';
      
      if (Buffer.byteLength(json) > this.options.maxMessageSize) {
        clearTimeout(timeoutId);
        this.pendingRequests.delete(id);
        reject(new Error('Message size exceeds maximum'));
        return;
      }
      
      this.process.stdin.write(json, (error) => {
        if (error) {
          clearTimeout(timeoutId);
          this.pendingRequests.delete(id);
          reject(error);
        }
      });
    });
  }
  
  /**
   * Evaluate security policy for given context
   * @param {Object} context - Security context
   * @param {string} context.operation - Operation being performed
   * @param {string} context.resource - Resource being accessed
   * @param {string} [context.user] - User performing operation
   * @param {number} [context.timestamp] - Timestamp of operation
   * @returns {Promise<Decision>} Security decision
   * @throws {Error} If evaluation fails
   */
  async evaluatePolicy(context) {
    if (!context || !context.operation) {
      throw new Error('Invalid context: operation required');
    }
    
    // Add timestamp if not provided
    if (!context.timestamp) {
      context.timestamp = Date.now();
    }
    
    this._log('debug', 'Evaluating policy', context);
    
    try {
      const result = await this._sendMessage({
        method: 'evaluatePolicy',
        params: { context }
      });
      
      this._log('debug', 'Policy decision', result);
      return result;
    } catch (error) {
      // Retry logic
      if (this.options.retryAttempts > 0) {
        this._log('warn', 'Retrying policy evaluation', { error: error.message });
        return this._retryWithBackoff(
          () => this.evaluatePolicy(context),
          this.options.retryAttempts
        );
      }
      throw error;
    }
  }
  
  /**
   * Evaluate multiple policies in batch
   * @param {Object[]} contexts - Array of security contexts
   * @returns {Promise<Decision[]>} Array of security decisions
   */
  async evaluatePolicyBatch(contexts) {
    if (!Array.isArray(contexts) || contexts.length === 0) {
      throw new Error('Invalid contexts: non-empty array required');
    }
    
    this._log('debug', `Evaluating ${contexts.length} policies in batch`);
    
    const result = await this._sendMessage({
      method: 'evaluatePolicyBatch',
      params: { contexts }
    });
    
    return result;
  }
  
  /**
   * Reload policies from disk
   * @returns {Promise<void>}
   */
  async reloadPolicies() {
    this._log('info', 'Reloading policies...');
    await this._sendMessage({ method: 'reloadPolicies' });
    this._log('info', 'Policies reloaded successfully');
  }
  
  /**
   * Load policy from object
   * @param {Object} policy - Policy definition
   * @returns {Promise<void>}
   */
  async loadPolicy(policy) {
    if (!policy || !policy.version) {
      throw new Error('Invalid policy: version required');
    }
    
    this._log('info', 'Loading policy', { name: policy.name });
    await this._sendMessage({
      method: 'loadPolicy',
      params: { policy }
    });
  }
  
  /**
   * Set resource limits
   * @param {Object} limits - Resource limits
   * @returns {Promise<void>}
   */
  async setResourceLimits(limits) {
    this._log('info', 'Setting resource limits', limits);
    await this._sendMessage({
      method: 'setResourceLimits',
      params: { limits }
    });
  }
  
  /**
   * Get runtime metrics
   * @returns {Promise<Metrics>} Runtime metrics
   */
  async getMetrics() {
    const pythonMetrics = await this._sendMessage({ method: 'getMetrics' });
    
    return {
      ...pythonMetrics,
      bridge: {
        uptime: Math.floor((Date.now() - this.metrics.startTime) / 1000),
        requestsProcessed: this.metrics.requestsProcessed,
        requestsFailed: this.metrics.requestsFailed,
        avgResponseTime: this.metrics.requestsProcessed > 0
          ? Math.floor(this.metrics.totalResponseTime / this.metrics.requestsProcessed)
          : 0,
        pendingRequests: this.pendingRequests.size
      }
    };
  }
  
  /**
   * Shutdown bridge and Python runtime
   * @returns {Promise<void>}
   */
  async shutdown() {
    if (!this.initialized) {
      this._log('warn', 'Bridge not initialized, nothing to shutdown');
      return;
    }
    
    this._log('info', 'Shutting down TARL bridge...');
    
    try {
      // Send shutdown command
      await this._sendMessage({ method: 'shutdown' });
      
      // Wait for graceful exit
      await new Promise((resolve) => {
        const timeoutId = setTimeout(() => {
          if (this.process) {
            this.process.kill('SIGTERM');
          }
          resolve();
        }, 5000);
        
        if (this.process) {
          this.process.once('exit', () => {
            clearTimeout(timeoutId);
            resolve();
          });
        } else {
          clearTimeout(timeoutId);
          resolve();
        }
      });
    } catch (error) {
      this._log('error', 'Error during shutdown', error);
      if (this.process) {
        this.process.kill('SIGKILL');
      }
    }
    
    this.initialized = false;
    this.process = null;
    this._log('info', 'TARL bridge shutdown complete');
  }
  
  /**
   * Retry operation with exponential backoff
   * @private
   * @param {Function} operation - Operation to retry
   * @param {number} attempts - Number of attempts remaining
   * @returns {Promise<any>} Operation result
   */
  async _retryWithBackoff(operation, attempts) {
    try {
      return await operation();
    } catch (error) {
      if (attempts <= 0) {
        throw error;
      }
      
      const delay = Math.min(1000 * Math.pow(2, this.options.retryAttempts - attempts), 5000);
      this._log('debug', `Retrying in ${delay}ms (${attempts} attempts remaining)`);
      
      await new Promise(resolve => setTimeout(resolve, delay));
      return this._retryWithBackoff(operation, attempts - 1);
    }
  }
  
  /**
   * Setup logging
   * @private
   */
  _setupLogging() {
    this.logLevels = { debug: 0, info: 1, warn: 2, error: 3 };
    this.currentLogLevel = this.logLevels[this.options.logLevel] || 1;
  }
  
  /**
   * Log message
   * @private
   * @param {string} level - Log level
   * @param {string} message - Log message
   * @param {any} [data] - Additional data
   */
  _log(level, message, data) {
    if (this.logLevels[level] < this.currentLogLevel) {
      return;
    }
    
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level: level.toUpperCase(),
      message,
      ...(data && { data })
    };
    
    // Emit log event
    this.emit('log', logEntry);
    
    // Console output
    const prefix = `[${timestamp}] [TARL Bridge] [${level.toUpperCase()}]`;
    const output = data ? `${prefix} ${message} ${JSON.stringify(data)}` : `${prefix} ${message}`;
    
    if (level === 'error') {
      console.error(output);
    } else if (level === 'warn') {
      console.warn(output);
    } else {
      console.log(output);
    }
    
    // File logging if configured
    if (this.options.logFile) {
      const fs = require('fs');
      fs.appendFileSync(this.options.logFile, output + '\n');
    }
  }
  
  /**
   * Check if bridge is initialized
   * @returns {boolean} True if initialized
   */
  isInitialized() {
    return this.initialized;
  }
  
  /**
   * Static method to check installation
   * @returns {Promise<boolean>} True if TARL is installed
   */
  static async checkInstallation() {
    const { spawn } = require('child_process');
    
    return new Promise((resolve) => {
      const proc = spawn('python3', ['-c', 'import tarl; print("OK")'], {
        stdio: ['ignore', 'pipe', 'ignore']
      });
      
      let output = '';
      proc.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      proc.on('close', (code) => {
        resolve(code === 0 && output.includes('OK'));
      });
      
      setTimeout(() => {
        proc.kill();
        resolve(false);
      }, 5000);
    });
  }
}

// Export
module.exports = { TARLBridge };
