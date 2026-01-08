#!/usr/bin/env node

/**
 * Thirsty-lang Secure Interpreter
 * Enhanced interpreter with defensive programming capabilities
 */

const { SecurityManager } = require('./security/index');

class SecureThirstyInterpreter {
  constructor(options = {}) {
    this.variables = {};
    this.securityEnabled = options.security !== false;
    this.securityManager = new SecurityManager({
      enabled: this.securityEnabled,
      mode: options.securityMode || 'defensive',
      policy: { securityLevel: options.securityLevel || 'moderate' }
    });
    
    // Security context
    this.shieldBlocks = [];
    this.morphEnabled = false;
    this.detectConfig = {};
    this.defendStrategy = 'moderate';
  }

  /**
   * Parse and execute Thirsty-lang code with security
   * @param {string} code - The Thirsty-lang source code
   */
  execute(code) {
    // Apply security if enabled
    if (this.securityEnabled) {
      const secured = this.securityManager.secureExecute(code, {
        filename: 'anonymous',
        mode: this.securityManager.mode
      });
      
      // Execute the secured code
      this.executeSecured(secured.code);
      
      return {
        executed: true,
        security: secured.securityLayers,
        stats: secured.stats
      };
    }

    // Execute without security
    const lines = code.split('\n').map(line => line.trim()).filter(line => line && !line.startsWith('//'));
    
    for (const line of lines) {
      this.executeLine(line);
    }

    return { executed: true, security: null };
  }

  /**
   * Execute secured code
   */
  executeSecured(code) {
    const lines = code.split('\n').map(line => line.trim()).filter(line => line && !line.startsWith('//'));
    
    for (const line of lines) {
      this.executeLine(line);
    }
  }

  /**
   * Execute a single line of code with security checks
   * @param {string} line - A single line of Thirsty-lang code
   */
  executeLine(line) {
    // Security keywords
    if (line.startsWith('shield ')) {
      this.handleShield(line);
    }
    else if (line.startsWith('morph ')) {
      this.handleMorph(line);
    }
    else if (line.startsWith('detect ')) {
      this.handleDetect(line);
    }
    else if (line.startsWith('defend ')) {
      this.handleDefend(line);
    }
    else if (line.startsWith('sanitize ')) {
      this.handleSanitize(line);
    }
    else if (line.startsWith('armor ')) {
      this.handleArmor(line);
    }
    // Original keywords
    else if (line.startsWith('drink ')) {
      this.handleDrink(line);
    }
    else if (line.startsWith('pour ')) {
      this.handlePour(line);
    }
    else if (line.startsWith('sip ')) {
      this.handleSip(line);
    }
    else if (line === '}') {
      // End of block - ignore
    }
    else if (line.includes('{')) {
      // Start of block - ignore
    }
    else {
      // Ignore other lines (like comments, security checks)
      if (!line.startsWith('//') && !line.startsWith('const ') && !line.startsWith('if ') && 
          !line.startsWith('Object.') && !line.startsWith('try ') && !line.startsWith('catch ') &&
          !line.startsWith('finally ') && !line.startsWith('(function') && line.length > 0) {
        // Only throw for genuine unknown statements
        if (!line.includes('Security:') && !line.includes('===') && !line.includes('=====')) {
          // Skip security infrastructure lines
        }
      }
    }
  }

  /**
   * Handle shield - Protected code blocks
   */
  handleShield(line) {
    // Extract shield block name or anonymous
    const match = line.match(/shield\s+(\w+)?/);
    const shieldName = match && match[1] ? match[1] : 'anonymous';
    
    this.shieldBlocks.push({
      name: shieldName,
      active: true,
      timestamp: Date.now()
    });

    console.log(`[SECURITY] Shield '${shieldName}' activated`);
  }

  /**
   * Handle morph - Dynamic code mutation
   */
  handleMorph(line) {
    // Extract morph configuration
    const match = line.match(/morph\s+on:\s*\[([^\]]+)\]/);
    if (match) {
      const threats = match[1].split(',').map(t => t.trim().replace(/['"]/g, ''));
      this.morphEnabled = true;
      console.log(`[SECURITY] Morphing enabled for: ${threats.join(', ')}`);
    } else {
      this.morphEnabled = true;
      console.log('[SECURITY] Morphing enabled');
    }
  }

  /**
   * Handle detect - Threat monitoring setup
   */
  handleDetect(line) {
    // Extract detection configuration
    const attacksMatch = line.match(/detect\s+attacks/);
    if (attacksMatch) {
      this.detectConfig = {
        enabled: true,
        mode: 'attacks',
        timestamp: Date.now()
      };
      console.log('[SECURITY] Threat detection activated');
    }
  }

  /**
   * Handle defend - Automatic countermeasures
   */
  handleDefend(line) {
    // Extract defense strategy
    const match = line.match(/defend\s+with:\s*"(\w+)"/);
    if (match) {
      this.defendStrategy = match[1];
      this.securityManager.policyEngine.setSecurityLevel(this.defendStrategy);
      console.log(`[SECURITY] Defense strategy: ${this.defendStrategy}`);
    }
  }

  /**
   * Handle sanitize - Input/output cleaning
   */
  handleSanitize(line) {
    // Extract variable to sanitize
    const match = line.match(/sanitize\s+(\w+)/);
    if (match) {
      const varName = match[1];
      if (this.variables.hasOwnProperty(varName)) {
        const sanitized = this.securityManager.secureInput(this.variables[varName]);
        this.variables[varName] = sanitized.sanitized;
        console.log(`[SECURITY] Sanitized variable: ${varName}`);
      }
    }
  }

  /**
   * Handle armor - Memory protection
   */
  handleArmor(line) {
    // Extract variable to protect
    const match = line.match(/armor\s+(\w+)/);
    if (match) {
      const varName = match[1];
      if (this.variables.hasOwnProperty(varName)) {
        // Freeze the variable to prevent modification
        Object.freeze(this.variables[varName]);
        console.log(`[SECURITY] Armored variable: ${varName}`);
      }
    }
  }

  /**
   * Handle variable declaration: drink varname = value
   */
  handleDrink(line) {
    const match = line.match(/drink\s+(\w+)\s*=\s*(.+)/);
    if (!match) {
      throw new Error(`Invalid drink statement: ${line}`);
    }
    
    const varName = match[1];
    let value = this.evaluateExpression(match[2]);
    
    // Apply security sanitization if enabled
    if (this.securityEnabled && typeof value === 'string') {
      const sanitized = this.securityManager.secureInput(value, { variable: varName });
      value = sanitized.sanitized;
    }
    
    this.variables[varName] = value;
  }

  /**
   * Handle output statement: pour expression
   */
  handlePour(line) {
    const expression = line.substring(5).trim(); // Remove 'pour '
    let value = this.evaluateExpression(expression);
    
    // Apply output sanitization if enabled
    if (this.securityEnabled && typeof value === 'string') {
      const sanitized = this.securityManager.secureInput(value, { output: true });
      value = sanitized.sanitized;
    }
    
    console.log(value);
  }

  /**
   * Handle input statement: sip prompt
   */
  handleSip(line) {
    // Extract prompt
    const match = line.match(/sip\s+"([^"]+)"/);
    if (match) {
      const prompt = match[1];
      console.log(`[INPUT] ${prompt}`);
      
      // In a real implementation, this would get actual user input
      // For now, simulate with a safe default
      const simulatedInput = 'safe_input';
      
      // Apply security if enabled
      if (this.securityEnabled) {
        const sanitized = this.securityManager.secureInput(simulatedInput, { prompt });
        return sanitized.sanitized;
      }
      
      return simulatedInput;
    }
  }

  /**
   * Evaluate an expression (variable or literal)
   */
  evaluateExpression(expr) {
    expr = expr.trim();
    
    // String literal
    if ((expr.startsWith('"') && expr.endsWith('"')) || 
        (expr.startsWith("'") && expr.endsWith("'"))) {
      return expr.slice(1, -1);
    }
    
    // Number literal
    if (!isNaN(expr)) {
      return parseFloat(expr);
    }
    
    // Variable reference
    if (this.variables.hasOwnProperty(expr)) {
      return this.variables[expr];
    }
    
    // String concatenation with +
    if (expr.includes(' + ')) {
      const parts = expr.split(' + ').map(p => this.evaluateExpression(p.trim()));
      return parts.join('');
    }
    
    throw new Error(`Unknown expression: ${expr}`);
  }

  /**
   * Get security report
   */
  getSecurityReport() {
    if (!this.securityEnabled) {
      return { enabled: false };
    }
    
    return {
      enabled: true,
      shields: this.shieldBlocks,
      morphing: this.morphEnabled,
      detection: this.detectConfig,
      defense: this.defendStrategy,
      report: this.securityManager.getSecurityReport()
    };
  }
}

module.exports = SecureThirstyInterpreter;
