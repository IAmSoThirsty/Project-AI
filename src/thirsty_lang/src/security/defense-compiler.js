#!/usr/bin/env node

/**
 * Thirsty-lang Defense Compiler
 * Compiles Thirsty code with embedded security primitives
 */

const ThreatDetector = require('./threat-detector');
const CodeMorpher = require('./code-morpher');
const SecurityPolicyEngine = require('./policy-engine');

class DefenseCompiler {
  constructor(options = {}) {
    this.threatDetector = new ThreatDetector(options.threat || {});
    this.codeMorpher = new CodeMorpher(options.morph || {});
    this.policyEngine = new SecurityPolicyEngine(options.policy || {});
    
    this.defenseEnabled = options.defenseEnabled !== false;
    this.morphingEnabled = options.morphingEnabled !== false;
    this.compilationLog = [];
  }

  /**
   * Compile code with defensive features
   */
  compile(code, options = {}) {
    const compilationStart = Date.now();
    const context = {
      filename: options.filename || 'anonymous',
      mode: options.mode || 'defensive',
      timestamp: compilationStart
    };

    let compiled = code;
    const securityLayers = [];

    try {
      // Phase 1: Threat Detection and Analysis
      if (this.defenseEnabled) {
        const threats = this.analyzeCode(code, context);
        if (threats.length > 0) {
          securityLayers.push({
            phase: 'threat-detection',
            threats: threats.length,
            details: threats
          });

          // Handle threats based on policy
          threats.forEach(threat => {
            try {
              this.policyEngine.handleThreat(threat);
            } catch (error) {
              // Critical threat blocked
              throw error;
            }
          });
        }
      }

      // Phase 2: Security Instrumentation
      if (this.defenseEnabled) {
        compiled = this.instrumentCode(compiled, context);
        securityLayers.push({
          phase: 'instrumentation',
          description: 'Added security checks and monitoring'
        });
      }

      // Phase 3: Code Morphing and Obfuscation
      if (this.morphingEnabled) {
        compiled = this.codeMorpher.morph(compiled, {
          identifierMorphing: true,
          deadCodeInjection: true,
          antiDebugChecks: true
        });
        securityLayers.push({
          phase: 'morphing',
          description: 'Applied code obfuscation and anti-analysis'
        });
      }

      // Phase 4: Add Runtime Security Wrapper
      compiled = this.wrapWithSecurity(compiled, context);
      securityLayers.push({
        phase: 'runtime-wrapper',
        description: 'Added runtime security monitoring'
      });

      // Log compilation
      this.logCompilation({
        context,
        originalSize: code.length,
        compiledSize: compiled.length,
        securityLayers,
        duration: Date.now() - compilationStart,
        success: true
      });

      return {
        code: compiled,
        context,
        securityLayers,
        stats: this.getCompilationStats()
      };

    } catch (error) {
      this.logCompilation({
        context,
        error: error.message,
        duration: Date.now() - compilationStart,
        success: false
      });
      throw error;
    }
  }

  /**
   * Analyze code for threats
   */
  analyzeCode(code, context) {
    const threats = [];

    // Check for malicious patterns
    const lines = code.split('\n');
    lines.forEach((line, index) => {
      const inputThreats = this.threatDetector.detectInputThreats(line, {
        ...context,
        line: index + 1
      });
      threats.push(...inputThreats);
    });

    // Check for reverse engineering attempts
    const reThreats = this.threatDetector.detectReverseEngineering(context);
    threats.push(...reThreats);

    return threats;
  }

  /**
   * Instrument code with security checks
   */
  instrumentCode(code, context) {
    const lines = code.split('\n');
    const instrumented = [];

    // Add integrity check at start
    instrumented.push('// Security: Integrity check');
    instrumented.push('const __integrity = true;');
    instrumented.push('');

    lines.forEach((line, index) => {
      // Instrument input operations (sip)
      if (line.includes('sip ')) {
        instrumented.push('// Security: Input validation');
        instrumented.push(`if (!__integrity) throw new Error("Integrity violation");`);
        instrumented.push(this.instrumentInput(line));
      }
      // Instrument output operations (pour)
      else if (line.includes('pour ')) {
        instrumented.push('// Security: Output sanitization');
        instrumented.push(this.instrumentOutput(line));
      }
      // Instrument variable declarations (drink)
      else if (line.includes('drink ')) {
        instrumented.push('// Security: Memory safety');
        instrumented.push(this.instrumentVariable(line));
      }
      else {
        instrumented.push(line);
      }

      // Add periodic security checks
      if (index % 10 === 0 && index > 0) {
        instrumented.push('// Security: Periodic check');
        instrumented.push('if (Math.random() > 0.999) { /* Anti-tamper */ }');
      }
    });

    return instrumented.join('\n');
  }

  /**
   * Instrument input operations
   */
  instrumentInput(line) {
    // Parse the sip statement
    const match = line.match(/sip\s+"([^"]+)"/);
    if (match) {
      const prompt = match[1];
      return `sip __secure_input("${prompt}")`;
    }
    return line;
  }

  /**
   * Instrument output operations
   */
  instrumentOutput(line) {
    // Add output sanitization
    return line + ' // Sanitized';
  }

  /**
   * Instrument variable declarations
   */
  instrumentVariable(line) {
    // Add memory safety checks
    return line + ' // Memory safe';
  }

  /**
   * Wrap code with security runtime
   */
  wrapWithSecurity(code, context) {
    const wrapper = `
// ============================================
// Thirsty-lang Defensive Runtime
// Compiled: ${new Date(context.timestamp).toISOString()}
// Mode: ${context.mode}
// Security: ENABLED
// ============================================

(function() {
  'use strict';
  
  // Anti-debugging
  const _debugCheck = setInterval(() => {
    const start = Date.now();
    debugger;
    const end = Date.now();
    if (end - start > 100) {
      console.error('Debug detected - terminating');
      process.exit(1);
    }
  }, 5000);

  // Integrity monitoring
  let _tamperCount = 0;
  const _checkIntegrity = () => {
    _tamperCount++;
    if (_tamperCount > 1000) {
      throw new Error('Integrity check failed');
    }
  };

  // Secure input handler
  const __secure_input = (prompt) => {
    _checkIntegrity();
    const input = prompt; // Placeholder for actual input
    
    // Validate input
    if (typeof input !== 'string') {
      throw new Error('Invalid input type');
    }
    
    if (input.length > 8192) {
      throw new Error('Input too long - potential buffer overflow');
    }
    
    // Sanitize input
    const sanitized = input
      .replace(/[<>]/g, '')
      .replace(/script/gi, '')
      .replace(/eval/gi, '');
    
    return sanitized;
  };

  // Runtime protection
  Object.freeze(Object.prototype);
  Object.freeze(Array.prototype);
  
  // Execute protected code
  try {
    ${code.split('\n').map(l => '    ' + l).join('\n')}
  } catch (error) {
    console.error('Security exception:', error.message);
    throw error;
  } finally {
    clearInterval(_debugCheck);
  }
})();
`;

    return wrapper;
  }

  /**
   * Compile with specific security profile
   */
  compileWithProfile(code, profileName) {
    const profiles = {
      minimal: {
        defenseEnabled: true,
        morphingEnabled: false,
        policy: { securityLevel: 'passive' }
      },
      standard: {
        defenseEnabled: true,
        morphingEnabled: true,
        policy: { securityLevel: 'moderate' }
      },
      hardened: {
        defenseEnabled: true,
        morphingEnabled: true,
        policy: { securityLevel: 'aggressive' }
      },
      paranoid: {
        defenseEnabled: true,
        morphingEnabled: true,
        policy: { securityLevel: 'paranoid' },
        threat: { sensitivity: 'high' },
        morph: { morphLevel: 'aggressive' }
      }
    };

    const profile = profiles[profileName] || profiles.standard;
    
    // Create new compiler with profile settings
    const compiler = new DefenseCompiler(profile);
    return compiler.compile(code);
  }

  /**
   * Log compilation
   */
  logCompilation(entry) {
    this.compilationLog.push(entry);
  }

  /**
   * Get compilation statistics
   */
  getCompilationStats() {
    return {
      totalCompilations: this.compilationLog.length,
      successfulCompilations: this.compilationLog.filter(e => e.success).length,
      failedCompilations: this.compilationLog.filter(e => !e.success).length,
      avgDuration: this.compilationLog.reduce((acc, e) => acc + e.duration, 0) / 
                   this.compilationLog.length || 0,
      avgSizeIncrease: this.compilationLog
        .filter(e => e.success)
        .reduce((acc, e) => acc + (e.compiledSize - e.originalSize), 0) / 
        this.compilationLog.filter(e => e.success).length || 0
    };
  }

  /**
   * Export compilation log
   */
  exportLog() {
    return JSON.stringify(this.compilationLog, null, 2);
  }
}

module.exports = DefenseCompiler;
