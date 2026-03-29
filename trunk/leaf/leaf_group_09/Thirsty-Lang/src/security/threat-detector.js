#!/usr/bin/env node

/**
 * Threat Detector - Advanced threat detection with pattern matching
 * Integrates with T.A.R.L. runtime for policy-based threat assessment
 */

class ThreatDetector {
  constructor(securityBridge) {
    this.bridge = securityBridge;
    this.threatPatterns = {
      xss: [
        // Match script tags with any attributes and various closing tag formats
        /<script[\s\S]*?>[\s\S]*?<\/\s*script[\s\S]*?>/gi,
        /javascript:/gi,
        /on\w+\s*=\s*["'][^"']*["']/gi,
        /<iframe[^>]*>/gi
      ],
      sqlInjection: [
        // SQL keywords with context - must have SQL-like structure
        /(\b(union|select|insert|update|delete|drop|create|alter|exec)\b.*\bfrom\b)/gi,
        /(\bunion\b.*\bselect\b)/gi,
        /(--|\#|\/\*|\*\/).*\b(select|insert|update|delete|drop)\b/gi,
        // Multiple single quotes or SQL comment with keywords
        /'{2,}|;.*\b(select|drop|delete|update|insert)\b/gi
      ],
      commandInjection: [
        // Shell metacharacters with context - must have shell commands
        /[;&|`]\s*(rm|cat|ls|curl|wget|bash|sh|exec|chmod|chown)/gi,
        /\$\([^)]*\)/g,
        /\.\.\//g,
        /~\//g
      ],
      pathTraversal: [
        /\.\.[\/\\]/g,
        /[\/\\]\.\.[\/\\]/g
      ]
    };
    
    this.threatDatabase = new Map();
    this.detectionMetrics = {
      threatsDetected: 0,
      falsePositives: 0,
      policyEnforced: 0
    };
  }

  /**
   * Detect threats in input
   */
  async detect(input, context = {}) {
    const threats = [];
    
    // Pattern-based detection
    for (const [threatType, patterns] of Object.entries(this.threatPatterns)) {
      for (const pattern of patterns) {
        if (pattern.test(input)) {
          threats.push({
            type: threatType,
            severity: this._getSeverity(threatType),
            pattern: pattern.source,
            input: input.substring(0, 100) // Truncate for safety
          });
        }
      }
    }

    // If threats found, consult T.A.R.L. policy
    if (threats.length > 0 && this.bridge) {
      try {
        const policyContext = {
          action: 'threat_detected',
          threats: threats.map(t => ({ type: t.type, severity: t.severity })),
          source: context.source || 'unknown',
          ...context
        };
        
        const decision = await this.bridge.evaluatePolicy(policyContext);
        
        if (decision.verdict === 'deny') {
          this.detectionMetrics.policyEnforced++;
          return {
            detected: true,
            threats,
            action: 'blocked',
            reason: decision.reason
          };
        } else if (decision.verdict === 'escalate') {
          return {
            detected: true,
            threats,
            action: 'escalate',
            reason: decision.reason
          };
        }
      } catch (err) {
        console.error('Policy evaluation failed:', err);
        // Fail-safe: block on policy error
        return {
          detected: true,
          threats,
          action: 'blocked',
          reason: 'Policy evaluation error'
        };
      }
    }

    this.detectionMetrics.threatsDetected += threats.length;

    return {
      detected: threats.length > 0,
      threats,
      action: threats.length > 0 ? 'warn' : 'allow',
      reason: threats.length > 0 ? 'Threats detected' : 'No threats'
    };
  }

  /**
   * Get threat severity
   */
  _getSeverity(threatType) {
    const severityMap = {
      xss: 'high',
      sqlInjection: 'critical',
      commandInjection: 'critical',
      pathTraversal: 'high'
    };
    return severityMap[threatType] || 'medium';
  }

  /**
   * Add custom threat pattern
   */
  addPattern(threatType, pattern) {
    if (!this.threatPatterns[threatType]) {
      this.threatPatterns[threatType] = [];
    }
    this.threatPatterns[threatType].push(pattern);
  }

  /**
   * Get detection metrics
   */
  getMetrics() {
    return { ...this.detectionMetrics };
  }

  /**
   * Reset metrics
   */
  resetMetrics() {
    this.detectionMetrics = {
      threatsDetected: 0,
      falsePositives: 0,
      policyEnforced: 0
    };
  }
}

module.exports = { ThreatDetector };
