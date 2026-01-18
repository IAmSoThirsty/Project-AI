

/**
 * Thirsty-lang Security Module
 * Defensive programming features for threat detection and mitigation
 */

const ThreatDetector = require('./threat-detector');
const CodeMorpher = require('./code-morpher');
const SecurityPolicyEngine = require('./policy-engine');
const DefenseCompiler = require('./defense-compiler');

/**
 * Security Manager - Central coordination of all security features
 */
class SecurityManager {
  constructor(options = {}) {
    this.threatDetector = new ThreatDetector(options.threat);
    this.codeMorpher = new CodeMorpher(options.morph);
    this.policyEngine = new SecurityPolicyEngine(options.policy);
    this.defenseCompiler = new DefenseCompiler(options);

    this.enabled = options.enabled !== false;
    this.mode = options.mode || 'defensive'; // defensive, offensive, adaptive
  }

  /**
   * Secure execution wrapper
   */
  secureExecute(code, context = {}) {
    if (!this.enabled) {
      return { code: code, secure: false };
    }

    // Compile with security features
    const compiled = this.defenseCompiler.compile(code, {
      ...context,
      mode: this.mode
    });

    return compiled;
  }

  /**
   * Validate and sanitize input
   */
  secureInput(input, context = {}) {
    // Detect threats
    const threats = this.threatDetector.detectInputThreats(input, context);

    // Apply policy
    const sanitized = this.policyEngine.applyInputPolicy(input, context);

    // Handle threats if found
    if (threats.length > 0) {
      threats.forEach(threat => {
        this.policyEngine.handleThreat(threat);
      });
    }

    return sanitized;
  }

  /**
   * Get comprehensive security report
   */
  getSecurityReport() {
    return {
      timestamp: Date.now(),
      mode: this.mode,
      enabled: this.enabled,
      threats: this.threatDetector.getThreatStats(),
      responses: this.policyEngine.getResponseStats(),
      morphing: this.codeMorpher.getMorphStats(),
      compilation: this.defenseCompiler.getCompilationStats(),
      policy: this.policyEngine.getPolicyConfig()
    };
  }

  /**
   * Set security mode
   */
  setMode(mode) {
    const validModes = ['defensive', 'offensive', 'adaptive'];
    if (!validModes.includes(mode)) {
      throw new Error(`Invalid security mode: ${mode}`);
    }
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
}

// Export all security modules
module.exports = {
  SecurityManager,
  ThreatDetector: ThreatDetector,
  CodeMorpher,
  SecurityPolicyEngine,
  DefenseCompiler
};
