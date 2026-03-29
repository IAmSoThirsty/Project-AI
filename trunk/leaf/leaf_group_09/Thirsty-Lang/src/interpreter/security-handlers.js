/**
 * Security Handlers Module
 * Provides shield, sanitize, armor, morph, detect, and defend functionality
 */

/**
 * Security handlers class that needs access to interpreter context
 */
class SecurityHandlers {
  constructor(interpreter) {
    this.interpreter = interpreter;
  }

  /**
   * Handle shield (protected execution block) statement
   */
  handleShield(lines, startIndex) {
    const line = lines[startIndex].trim();
    const match = line.match(/shield\s+(\w+)\s*{/);

    if (!match) {
      throw new Error(`Invalid shield statement: ${line}`);
    }

    const shieldName = match[1];
    const blockEnd = this.interpreter.findMatchingBrace(lines, startIndex);

    if (blockEnd === -1) {
      throw new Error(`Unmatched opening brace for shield statement at line ${startIndex + 1}`);
    }

    // Activate shield protection
    const previousShieldState = this.interpreter.shieldActive;
    const previousContext = this.interpreter.shieldContext;

    this.interpreter.shieldActive = true;
    this.interpreter.shieldContext = {
      name: shieldName,
      startLine: startIndex,
      threats: [],
      protected: true
    };

    try {
      // Execute the protected block
      this.interpreter.executeBlock(lines.slice(startIndex + 1, blockEnd), 0);
    } finally {
      // Restore previous shield state
      this.interpreter.shieldActive = previousShieldState;
      this.interpreter.shieldContext = previousContext;
    }

    return blockEnd + 1;
  }

  /**
   * Handle sanitize (input cleaning) statement
   */
  handleSanitize(line) {
    const match = line.match(/sanitize\s+(\w+)/);
    if (!match) {
      throw new Error(`Invalid sanitize statement: ${line}`);
    }

    const varName = match[1];

    if (!this.interpreter.variables.hasOwnProperty(varName)) {
      throw new Error(`Cannot sanitize undefined variable: ${varName}`);
    }

    // Apply security sanitization
    const value = this.interpreter.variables[varName];
    if (this.interpreter.securityEnabled) {
      const result = this.interpreter.securityManager.secureInput(value, {
        variable: varName,
        shield: this.interpreter.shieldContext
      });
      // Extract the sanitized value from the result object
      this.interpreter.variables[varName] = result.sanitized || result;
    } else {
      // Basic sanitization without security manager
      this.interpreter.variables[varName] = this.basicSanitize(value);
    }

    this.interpreter.sanitizedVariables.add(varName);
  }

  /**
   * Handle armor (memory protection) statement
   */
  handleArmor(line) {
    const match = line.match(/armor\s+(\w+)/);
    if (!match) {
      throw new Error(`Invalid armor statement: ${line}`);
    }

    const varName = match[1];

    if (!this.interpreter.variables.hasOwnProperty(varName)) {
      throw new Error(`Cannot armor undefined variable: ${varName}`);
    }

    // Mark variable as armored (protected from modification)
    this.interpreter.armoredVariables.add(varName);

    // In production, this would use Object.freeze or similar mechanisms
    // For now, we'll check this in handleDrink
  }

  /**
   * Handle morph (code obfuscation) statement
   */
  handleMorph(line) {
    const match = line.match(/morph\s+on:\s*\[([^\]]+)\]/);
    if (match) {
      const threats = match[1].split(',').map(t => t.trim().replace(/["']/g, ''));
      // Enable morphing for specified threat types
      if (this.interpreter.shieldContext) {
        this.interpreter.shieldContext.morphEnabled = true;
        this.interpreter.shieldContext.morphThreats = threats;
      }
    }
  }

  /**
   * Handle detect (threat monitoring) statement
   */
  handleDetect(line) {
    const match = line.match(/detect\s+(\w+)/);
    if (match) {
      const detectType = match[1];
      if (this.interpreter.shieldContext) {
        this.interpreter.shieldContext.detectEnabled = true;
        this.interpreter.shieldContext.detectType = detectType;
      }
    }
  }

  /**
   * Handle defend (countermeasures) statement
   */
  handleDefend(line) {
    const match = line.match(/defend\s+with:\s*"(\w+)"/);
    if (match) {
      const strategy = match[1];
      if (this.interpreter.shieldContext) {
        this.interpreter.shieldContext.defendStrategy = strategy;
      }
      // Set defense strategy: passive, moderate, aggressive, paranoid
      if (this.interpreter.securityEnabled) {
        this.interpreter.securityManager.setMode(strategy === 'aggressive' ? 'offensive' : 'defensive');
      }
    }
  }

  /**
   * Basic sanitization (fallback when security manager not enabled)
   * Production-grade HTML encoding to prevent XSS
   */
  basicSanitize(value) {
    if (typeof value !== 'string') {
      return value;
    }

    // HTML encode all special characters to prevent injection
    return value
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#x27;')
      .replace(/\//g, '&#x2F;')
      .trim();
  }
}

module.exports = { SecurityHandlers };
