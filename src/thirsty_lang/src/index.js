#!/usr/bin/env node

/**
 * Thirsty-lang Interpreter
 * A fun programming language for the thirsty
 */

class ThirstyInterpreter {
  constructor() {
    this.variables = {};
  }

  /**
   * Parse and execute Thirsty-lang code
   * @param {string} code - The Thirsty-lang source code
   */
  execute(code) {
    const lines = code.split('\n').map(line => line.trim()).filter(line => line && !line.startsWith('//'));
    
    for (const line of lines) {
      this.executeLine(line);
    }
  }

  /**
   * Execute a single line of code
   * @param {string} line - A single line of Thirsty-lang code
   */
  executeLine(line) {
    // drink - Variable declaration
    if (line.startsWith('drink ')) {
      this.handleDrink(line);
    }
    // pour - Output statement
    else if (line.startsWith('pour ')) {
      this.handlePour(line);
    }
    // sip - Input statement (placeholder)
    else if (line.startsWith('sip ')) {
      this.handleSip(line);
    }
    else {
      throw new Error(`Unknown statement: ${line}`);
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
    const value = this.evaluateExpression(match[2]);
    this.variables[varName] = value;
  }

  /**
   * Handle output statement: pour expression
   */
  handlePour(line) {
    const expression = line.substring(5).trim(); // Remove 'pour '
    const value = this.evaluateExpression(expression);
    console.log(value);
  }

  /**
   * Handle input statement: sip varname
   */
  handleSip(line) {
    // Placeholder for input functionality
    console.log('Input functionality not yet implemented');
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
    
    throw new Error(`Unknown expression: ${expr}`);
  }
}

module.exports = ThirstyInterpreter;
