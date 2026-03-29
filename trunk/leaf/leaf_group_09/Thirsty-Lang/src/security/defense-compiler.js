#!/usr/bin/env node

/**
 * Defense Compiler - Compile code with defensive transformations
 * Integrates with T.A.R.L. for policy-driven compilation
 */

const { ThreatDetector } = require('./threat-detector');
const { CodeMorpher } = require('./code-morpher');

class DefenseCompiler {
  constructor(securityBridge) {
    this.bridge = securityBridge;
    this.threatDetector = new ThreatDetector(securityBridge);
    this.codeMorpher = new CodeMorpher(securityBridge);
    this.compileMetrics = {
      compilations: 0,
      threatsBlocked: 0,
      transformations: 0
    };
  }

  /**
   * Compile code with defensive measures
   */
  async compile(code, options = {}) {
    this.compileMetrics.compilations++;

    const context = {
      source: options.source || 'unknown',
      mode: options.mode || 'defensive',
      ...options
    };

    // Step 1: Threat detection
    const threatResult = await this.threatDetector.detect(code, context);
    
    if (threatResult.action === 'blocked') {
      this.compileMetrics.threatsBlocked++;
      throw new Error(`Compilation blocked: ${threatResult.reason}`);
    }

    if (threatResult.action === 'escalate') {
      console.warn('Security escalation:', threatResult.reason);
    }

    // Step 2: Check compilation policy
    if (this.bridge) {
      try {
        const policyContext = {
          action: 'compile',
          threats: threatResult.threats,
          mode: context.mode,
          ...context
        };
        
        const decision = await this.bridge.evaluatePolicy(policyContext);
        
        if (decision.verdict === 'deny') {
          throw new Error(`Compilation denied: ${decision.reason}`);
        }
      } catch (err) {
        if (err.message.includes('denied')) {
          throw err;
        }
        console.error('Policy check failed:', err);
      }
    }

    // Step 3: Apply code transformations
    let compiled = code;
    const transformations = [];

    if (options.morph !== false) {
      try {
        const morphResult = await this.codeMorpher.morph(code, context);
        compiled = morphResult.code;
        transformations.push(...morphResult.transformations);
        this.compileMetrics.transformations++;
      } catch (err) {
        console.error('Morphing failed:', err);
      }
    }

    // Step 4: Add runtime guards
    if (options.addGuards !== false) {
      compiled = this._addRuntimeGuards(compiled);
      transformations.push('runtime_guards');
    }

    return {
      code: compiled,
      original: code,
      threats: threatResult.threats,
      transformations,
      metrics: this.getMetrics()
    };
  }

  /**
   * Add runtime security guards
   */
  _addRuntimeGuards(code) {
    // Add security checks at runtime
    const guards = `
// Runtime Security Guards
const __SECURITY_CONTEXT__ = {
  enabled: true,
  checkViolations: function(varName) {
    if (this.protectedVars && this.protectedVars.has(varName)) {
      console.warn('Security: Attempted modification of protected variable:', varName);
      return false;
    }
    return true;
  },
  protectedVars: new Set()
};

`;
    return guards + code;
  }

  /**
   * Get compilation metrics
   */
  getMetrics() {
    return {
      ...this.compileMetrics,
      threatDetector: this.threatDetector.getMetrics(),
      codeMorpher: this.codeMorpher.getMetrics()
    };
  }

  /**
   * Reset metrics
   */
  resetMetrics() {
    this.compileMetrics = {
      compilations: 0,
      threatsBlocked: 0,
      transformations: 0
    };
    this.threatDetector.resetMetrics();
    this.codeMorpher.resetMetrics ? this.codeMorpher.resetMetrics() : null;
  }
}

module.exports = { DefenseCompiler };
