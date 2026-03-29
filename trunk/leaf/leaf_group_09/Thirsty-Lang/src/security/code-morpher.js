#!/usr/bin/env node

/**
 * Code Morpher - Dynamic code transformation for defense
 * Implements code obfuscation and mutation strategies
 */

class CodeMorpher {
  constructor(securityBridge) {
    this.bridge = securityBridge;
    this.morphStrategies = {
      rename: true,
      shuffle: true,
      encrypt: false,
      obfuscate: true
    };
    this.morphMetrics = {
      transformations: 0,
      policyChecks: 0
    };
  }

  /**
   * Morph code based on security policy
   */
  async morph(code, context = {}) {
    // Check policy before morphing
    if (this.bridge) {
      try {
        const policyContext = {
          action: 'code_morph',
          codeLength: code.length,
          ...context
        };
        
        const decision = await this.bridge.evaluatePolicy(policyContext);
        this.morphMetrics.policyChecks++;
        
        if (decision.verdict === 'deny') {
          throw new Error(`Morphing denied: ${decision.reason}`);
        }
      } catch (err) {
        console.error('Policy check failed:', err);
      }
    }

    let morphed = code;

    // Apply transformations
    if (this.morphStrategies.obfuscate) {
      morphed = this._obfuscateStrings(morphed);
    }

    if (this.morphStrategies.rename) {
      morphed = this._renameVariables(morphed);
    }

    if (this.morphStrategies.shuffle) {
      morphed = this._shuffleStatements(morphed);
    }

    this.morphMetrics.transformations++;

    return {
      code: morphed,
      original: code,
      transformations: Object.keys(this.morphStrategies).filter(
        k => this.morphStrategies[k]
      ),
      metrics: this.morphMetrics
    };
  }

  /**
   * Obfuscate string literals
   */
  _obfuscateStrings(code) {
    return code.replace(/"([^"]*)"/g, (match, str) => {
      // Simple string encoding
      const encoded = Buffer.from(str).toString('base64');
      return `Buffer.from("${encoded}", "base64").toString()`;
    });
  }

  /**
   * Rename variables (simple implementation)
   */
  _renameVariables(code) {
    // This is a simplified version
    // A real implementation would use AST transformation
    const varNames = new Map();
    let counter = 0;

    return code.replace(/\b([a-zA-Z_][a-zA-Z0-9_]*)\b/g, (match) => {
      // Don't rename keywords
      const keywords = ['drink', 'pour', 'sip', 'thirsty', 'hydrated', 'refill', 'shield'];
      if (keywords.includes(match)) {
        return match;
      }

      if (!varNames.has(match)) {
        varNames.set(match, `_v${counter++}`);
      }
      return varNames.get(match);
    });
  }

  /**
   * Shuffle statement order (safe operations only)
   */
  _shuffleStatements(code) {
    // Simple implementation - just return code
    // Real implementation would analyze dependencies and reorder
    return code;
  }

  /**
   * Configure morph strategies
   */
  setStrategy(strategy, enabled) {
    if (strategy in this.morphStrategies) {
      this.morphStrategies[strategy] = enabled;
    }
  }

  /**
   * Get morph metrics
   */
  getMetrics() {
    return { ...this.morphMetrics };
  }

  /**
   * Reset metrics
   */
  resetMetrics() {
    this.morphMetrics = {
      transformations: 0,
      policyChecks: 0
    };
  }
}

module.exports = { CodeMorpher };
