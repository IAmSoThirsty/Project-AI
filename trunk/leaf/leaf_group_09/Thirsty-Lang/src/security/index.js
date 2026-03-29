#!/usr/bin/env node

/**
 * Thirsty-lang Security Module
 * Enhanced security with T.A.R.L. integration
 */

const { SecurityBridge } = require('./bridge');
const { ThreatDetector } = require('./threat-detector');
const { CodeMorpher } = require('./code-morpher');
const { DefenseCompiler } = require('./defense-compiler');
const { PolicyEngine } = require('./policy-engine');

/**
 * SecurityManager - Provides HTML sanitization and variable protection
 * Enhanced with T.A.R.L. runtime integration
 */
class SecurityManager {
  constructor(options = {}) {
    this.enabled = options.enabled !== false;
    this.mode = options.mode || 'defensive';
    
    // Initialize T.A.R.L. bridge if enabled
    this.useTarl = options.useTarl !== false;
    this.bridge = null;
    this.threatDetector = null;
    this.codeMorpher = null;
    this.defenseCompiler = null;
    this.policyEngine = null;
    this.initialized = false;
  }

  /**
   * Initialize T.A.R.L. integration
   */
  async initialize() {
    if (this.initialized || !this.useTarl) {
      return;
    }

    try {
      this.bridge = new SecurityBridge();
      await this.bridge.initialize();
      
      this.threatDetector = new ThreatDetector(this.bridge);
      this.codeMorpher = new CodeMorpher(this.bridge);
      this.defenseCompiler = new DefenseCompiler(this.bridge);
      this.policyEngine = new PolicyEngine(this.bridge);
      
      this.initialized = true;
      console.log('T.A.R.L. security integration initialized');
    } catch (err) {
      console.error('Failed to initialize T.A.R.L. integration:', err);
      this.useTarl = false;
    }
  }

  /**
   * Sanitize input - HTML encoding to prevent XSS
   */
  secureInput(input, context = {}) {
    if (!this.enabled) {
      return input;
    }

    const sanitized = this.sanitizeHTML(String(input));
    
    return {
      original: input,
      sanitized,
      modified: input !== sanitized
    };
  }

  /**
   * HTML encoding - escapes special characters to prevent injection
   */
  sanitizeHTML(input) {
    return input
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/\//g, '&#x2F;');
  }

  /**
   * Set security mode (kept for compatibility)
   */
  setMode(mode) {
    this.mode = mode;
    return { mode: this.mode };
  }

  /**
   * Enable/disable security
   */
  setEnabled(enabled) {
    this.enabled = !!enabled;
    return { enabled: this.enabled };
  }

  /**
   * Detect threats using advanced detection
   */
  async detectThreats(input, context = {}) {
    if (!this.initialized || !this.threatDetector) {
      return { detected: false, threats: [] };
    }

    return await this.threatDetector.detect(input, context);
  }

  /**
   * Compile code with defensive measures
   */
  async compileSecure(code, options = {}) {
    if (!this.initialized || !this.defenseCompiler) {
      return { code, original: code };
    }

    return await this.defenseCompiler.compile(code, options);
  }

  /**
   * Load security policies
   */
  async loadPolicies(policyPath) {
    if (!this.initialized || !this.policyEngine) {
      throw new Error('Policy engine not initialized');
    }

    return await this.policyEngine.loadPolicies(policyPath);
  }

  /**
   * Shutdown security bridge
   */
  async shutdown() {
    if (this.bridge) {
      await this.bridge.shutdown();
    }
    if (this.policyEngine) {
      this.policyEngine.shutdown();
    }
  }
}

// Export security manager and components
module.exports = {
  SecurityManager,
  SecurityBridge,
  ThreatDetector,
  CodeMorpher,
  DefenseCompiler,
  PolicyEngine
};
