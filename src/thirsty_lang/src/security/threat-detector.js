#!/usr/bin/env node

/**
 * Thirsty-lang Threat Detection Engine
 * Identifies and classifies security threats across all attack models
 */

class ThreatDetector {
  constructor(options = {}) {
    this.sensitivity = options.sensitivity || 'high';
    this.threatLog = [];
    this.attackPatterns = this.initializeAttackPatterns();
  }

  /**
   * Initialize comprehensive attack pattern database
   */
  initializeAttackPatterns() {
    return {
      // White Box Attacks (Source Code Analysis)
      whiteBox: {
        sqlInjection: /('|"|\b(OR|AND|UNION|SELECT|DROP|INSERT|UPDATE|DELETE)\b)/gi,
        xssInjection: /(<script|javascript:|onerror=|onload=|<iframe|<object)/gi,
        commandInjection: /(;|\||&|`|\$\(|&&|\|\|)/g,
        pathTraversal: /(\.\.\/|\.\.\\)/g,
        codeInjection: /(eval\(|Function\(|setTimeout\(|setInterval\()/gi,
        prototypePollution: /(__proto__|constructor\[|prototype\[)/gi,
        xxeInjection: /(<!DOCTYPE|<!ENTITY|SYSTEM|PUBLIC)/gi
      },
      
      // Grey Box Attacks (Partial Knowledge)
      greyBox: {
        timingAttack: { threshold: 1000, variance: 100 }, // ms
        sideChannel: { memoryPattern: true, cachePattern: true },
        bruteForce: { threshold: 10, timeWindow: 60000 }, // attempts per minute
        enumeration: { threshold: 50, timeWindow: 60000 }
      },
      
      // Black Box Attacks (Behavioral)
      blackBox: {
        bufferOverflow: { maxLength: 8192, patterns: [/A{100,}/, /(.)\1{100,}/] },
        dosAttack: { requestThreshold: 100, timeWindow: 1000 },
        formatString: /%[nsx]/gi,
        integerOverflow: { min: -2147483648, max: 2147483647 },
        typeConfusion: { strictTypes: true }
      },
      
      // Red Team Attacks (Penetration Testing)
      redTeam: {
        reverseEngineering: { obfuscationLevel: 'high' },
        memoryDump: { antiDebug: true, antiDump: true },
        dynamicAnalysis: { antiVM: true, antiSandbox: true },
        staticAnalysis: { antiDecompile: true, codeIntegrity: true }
      }
    };
  }

  /**
   * Detect threats in input data
   */
  detectInputThreats(input, context = {}) {
    const threats = [];
    const inputStr = String(input);

    // White Box Detection
    Object.entries(this.attackPatterns.whiteBox).forEach(([type, pattern]) => {
      if (pattern.test(inputStr)) {
        threats.push({
          type: 'whiteBox',
          attack: type,
          severity: this.calculateSeverity(type),
          input: this.sanitizeForLog(inputStr),
          timestamp: Date.now(),
          context
        });
      }
    });

    // Black Box Detection
    if (inputStr.length > this.attackPatterns.blackBox.bufferOverflow.maxLength) {
      threats.push({
        type: 'blackBox',
        attack: 'bufferOverflow',
        severity: 'critical',
        input: this.sanitizeForLog(inputStr.substring(0, 100) + '...'),
        timestamp: Date.now(),
        context
      });
    }

    this.attackPatterns.blackBox.bufferOverflow.patterns.forEach((pattern) => {
      if (pattern.test(inputStr)) {
        threats.push({
          type: 'blackBox',
          attack: 'bufferOverflow',
          severity: 'critical',
          input: this.sanitizeForLog(inputStr.substring(0, 100)),
          timestamp: Date.now(),
          context
        });
      }
    });

    // Log detected threats
    if (threats.length > 0) {
      this.threatLog.push(...threats);
    }

    return threats;
  }

  /**
   * Detect runtime behavioral threats
   */
  detectRuntimeThreats(metrics) {
    const threats = [];
    
    // Timing attack detection
    if (metrics.executionTime && metrics.expectedTime) {
      const variance = Math.abs(metrics.executionTime - metrics.expectedTime);
      if (variance > this.attackPatterns.greyBox.timingAttack.variance) {
        threats.push({
          type: 'greyBox',
          attack: 'timingAttack',
          severity: 'medium',
          variance,
          timestamp: Date.now()
        });
      }
    }

    // DoS attack detection
    if (metrics.requestRate && metrics.requestRate > this.attackPatterns.blackBox.dosAttack.requestThreshold) {
      threats.push({
        type: 'blackBox',
        attack: 'dosAttack',
        severity: 'critical',
        requestRate: metrics.requestRate,
        timestamp: Date.now()
      });
    }

    // Brute force detection
    if (metrics.failedAttempts && metrics.failedAttempts > this.attackPatterns.greyBox.bruteForce.threshold) {
      threats.push({
        type: 'greyBox',
        attack: 'bruteForce',
        severity: 'high',
        attempts: metrics.failedAttempts,
        timestamp: Date.now()
      });
    }

    return threats;
  }

  /**
   * Detect reverse engineering attempts
   */
  detectReverseEngineering(context) {
    const threats = [];

    // Check for debugger
    if (this.isDebuggerPresent()) {
      threats.push({
        type: 'redTeam',
        attack: 'debuggerDetected',
        severity: 'high',
        timestamp: Date.now()
      });
    }

    // Check for VM/Sandbox
    if (this.isVirtualEnvironment()) {
      threats.push({
        type: 'redTeam',
        attack: 'virtualEnvironment',
        severity: 'medium',
        timestamp: Date.now()
      });
    }

    return threats;
  }

  /**
   * Calculate threat severity
   */
  calculateSeverity(attackType) {
    const criticalAttacks = ['sqlInjection', 'commandInjection', 'codeInjection', 'bufferOverflow'];
    const highAttacks = ['xssInjection', 'pathTraversal', 'prototypePollution'];
    const mediumAttacks = ['xxeInjection', 'timingAttack'];

    if (criticalAttacks.includes(attackType)) return 'critical';
    if (highAttacks.includes(attackType)) return 'high';
    if (mediumAttacks.includes(attackType)) return 'medium';
    return 'low';
  }

  /**
   * Check if debugger is present
   */
  isDebuggerPresent() {
    // In Node.js, check for debugger flags
    if (typeof process !== 'undefined') {
      return process.execArgv.some(arg => 
        arg.includes('--inspect') || arg.includes('--debug')
      );
    }
    return false;
  }

  /**
   * Check if running in virtual environment
   */
  isVirtualEnvironment() {
    if (typeof process !== 'undefined') {
      // Check for common VM indicators
      const platform = process.platform;
      const env = process.env;
      
      return !!(
        env.VM_DETECTED ||
        env.DOCKER_CONTAINER ||
        env.KUBERNETES_SERVICE_HOST
      );
    }
    return false;
  }

  /**
   * Sanitize input for logging
   */
  sanitizeForLog(input) {
    return input.substring(0, 100).replace(/[^\x20-\x7E]/g, '?');
  }

  /**
   * Get threat statistics
   */
  getThreatStats() {
    const stats = {
      total: this.threatLog.length,
      byType: {},
      bySeverity: {},
      recent: this.threatLog.slice(-10)
    };

    this.threatLog.forEach(threat => {
      stats.byType[threat.type] = (stats.byType[threat.type] || 0) + 1;
      stats.bySeverity[threat.severity] = (stats.bySeverity[threat.severity] || 0) + 1;
    });

    return stats;
  }

  /**
   * Clear threat log
   */
  clearLog() {
    this.threatLog = [];
  }

  /**
   * Export threat log
   */
  exportLog() {
    return JSON.stringify(this.threatLog, null, 2);
  }
}

module.exports = ThreatDetector;
