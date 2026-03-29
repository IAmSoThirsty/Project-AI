#!/usr/bin/env node

/**
 * Thirsty-lang Interpreter
 * Enterprise-grade programming language with defensive security capabilities
 */

const { SecurityManager } = require('./security/index');
const { initializeStandardLibrary } = require('./interpreter/stdlib');
const { SecurityHandlers } = require('./interpreter/security-handlers');
const { ControlFlowHandlers } = require('./interpreter/control-flow');
const { ClassFunctionHandlers } = require('./interpreter/class-function-handlers');
const { ExpressionEvaluator } = require('./interpreter/expression-evaluator');
const { ExceptionHandlers, ThirstyError } = require('./interpreter/exception-handlers');
const fs = require('fs');
const path = require('path');

class ThirstyInterpreter {
  constructor(options = {}) {
    this.variables = {};
    this.functions = {}; // Store user-defined functions
    this.classes = {}; // Store class definitions
    this.arrays = {}; // Store arrays (reservoirs)
    this.callStack = []; // Track function calls for debugging
    this.MAX_LOOP_ITERATIONS = 10000; // Safety limit for loops
    this.MAX_CALL_DEPTH = 100; // Prevent stack overflow
    
    // Module system
    this.modules = {}; // Cache for loaded modules
    this.exports = {}; // Exports from current module
    this.currentFile = options.currentFile || null; // Current file being executed
    
    // Async/await support
    this.asyncFunctions = new Set(); // Track async functions
    this.pendingPromises = []; // Track pending promises
    
    // Security features
    this.securityEnabled = options.security !== false;
    this.securityManager = new SecurityManager({
      enabled: this.securityEnabled,
      mode: options.securityMode || 'defensive',
      policy: { securityLevel: options.securityLevel || 'moderate' }
    });
    this.shieldActive = false;
    this.shieldContext = null;
    this.armoredVariables = new Set();
    this.sanitizedVariables = new Set();

    // Initialize security handlers
    this.securityHandlers = new SecurityHandlers(this);

    // Initialize control flow handlers
    this.controlFlowHandlers = new ControlFlowHandlers(this);

    // Initialize class/function handlers
    this.classFunctionHandlers = new ClassFunctionHandlers(this);

    // Initialize expression evaluator
    this.expressionEvaluator = new ExpressionEvaluator(this);

    // Initialize exception handlers
    this.exceptionHandlers = new ExceptionHandlers(this);

    // Initialize standard library
    this.initializeStandardLibrary();
  }
  
  /**
   * Initialize the standard library with built-in functions
   */
  initializeStandardLibrary() {
    const stdlib = initializeStandardLibrary();

    // Add all stdlib objects to variables
    this.variables.Math = stdlib.Math;
    this.variables.String = stdlib.String;
    this.variables.File = stdlib.File;
    this.variables.Http = stdlib.Http;
    this.variables.JSON = stdlib.JSON;

    // Add the fetch method that needs access to this.variables
    this.variables.Http.fetch = stdlib.Http._createFetch(this.variables.Http);
  }

  /**
   * Parse and execute Thirsty-lang code
   * @param {string} code - The Thirsty-lang source code
   */
  execute(code) {
    const lines = code.split('\n');
    this.executeBlock(lines, 0);
  }

  /**
   * Execute a block of code starting from a given index
   * Returns the index after the block ends
   */
  executeBlock(lines, startIndex) {
    let i = startIndex;

    while (i < lines.length) {
      const line = lines[i].trim();

      // Skip empty lines and comments
      if (!line || line.startsWith('//')) {
        i++;
        continue;
      }
      
      // Handle module imports/exports
      if (line.startsWith('import ')) {
        this.handleImport(line);
        i++;
        continue;
      } else if (line.startsWith('export ')) {
        this.handleExport(line);
        i++;
        continue;
      }
      
      // Handle async function declarations (cascade keyword)
      if (line.startsWith('cascade ')) {
        i = this.handleCascade(lines, i);
        continue;
      }
      
      // Handle control flow
      if (line === 'try {' || line.startsWith('try {')) {
        i = this.handleTry(lines, i);
      } else if (line.startsWith('thirsty ')) {
        i = this.handleThirsty(lines, i);
      } else if (line.startsWith('refill ')) {
        i = this.handleRefill(lines, i);
      } else if (line.startsWith('shield ')) {
        i = this.handleShield(lines, i);
      } else if (line.startsWith('glass ')) {
        i = this.handleGlass(lines, i);
      } else if (line.startsWith('fountain ')) {
        i = this.handleFountain(lines, i);
      } else if (line.startsWith('throw ')) {
        this.handleThrow(line);
        i++;
      } else if (line.startsWith('return ')) {
        throw { type: 'return', value: this.evaluateExpression(line.substring(7).trim()) };
      } else if (line === 'return') {
        throw { type: 'return', value: undefined };
      } else if (line === '}') {
        // End of block
        return i + 1;
      } else {
        this.executeLine(line);
        i++;
      }
    }
    
    return i;
  }

  /**
   * Execute a single line of code
   * @param {string} line - A single line of Thirsty-lang code
   * Optimized with first-character checks to reduce string comparisons
   */
  executeLine(line) {
    // Get first character for quick dispatch
    const firstChar = line[0];

    // Security keywords (s, a, m, d)
    if (firstChar === 's') {
      if (line.startsWith('sanitize ')) {
        this.handleSanitize(line);
        return;
      } else if (line.startsWith('sip ')) {
        this.handleSip(line);
        return;
      }
    } else if (firstChar === 'a' && line.startsWith('armor ')) {
      this.handleArmor(line);
      return;
    } else if (firstChar === 'm' && line.startsWith('morph ')) {
      this.handleMorph(line);
      return;
    } else if (firstChar === 'd') {
      if (line.startsWith('detect ')) {
        this.handleDetect(line);
        return;
      } else if (line.startsWith('defend ')) {
        this.handleDefend(line);
        return;
      } else if (line.startsWith('drink ')) {
        this.handleDrink(line);
        return;
      }
    }
    // Core keywords
    else if (firstChar === 'r' && line.startsWith('reservoir ')) {
      this.handleReservoir(line);
      return;
    }
    // pour - Output statement
    else if (firstChar === 'p' && line.startsWith('pour ')) {
      this.handlePour(line);
      return;
    }

    // Check if it's a method call (varname.method(...))
    const methodCallMatch = line.match(/^(\w+)\.(\w+)\s*\(([^)]*)\)$/);
    if (methodCallMatch) {
      const varName = methodCallMatch[1];
      const methodName = methodCallMatch[2];
      const argsStr = methodCallMatch[3].trim();

      if (!this.variables.hasOwnProperty(varName)) {
        throw new Error(`Unknown variable: ${varName}`);
      }

      const obj = this.variables[varName];

      // Handle array methods
      if (Array.isArray(obj)) {
        this.handleArrayMethod(varName, obj, methodName, argsStr);
        return;
      }

      // Handle class instance methods
      if (obj && typeof obj === 'object' && obj.__class && obj.__methods) {
        const args = argsStr ? this.parseArguments(argsStr) : [];
        const evaluatedArgs = args.map(arg => this.evaluateExpression(arg));
        this.callInstanceMethod(obj, methodName, evaluatedArgs);
        return;
      }

      throw new Error(`Method '${methodName}' not supported for variable '${varName}'`);
    }

    // Check if it's a function call (function_name(...))
    const funcCallMatch = line.match(/^(\w+)\s*\(([^)]*)\)$/);
    if (funcCallMatch) {
      const funcName = funcCallMatch[1];
      const argsStr = funcCallMatch[2].trim();
      const args = argsStr ? this.parseArguments(argsStr) : [];
      const evaluatedArgs = args.map(arg => this.evaluateExpression(arg));
      this.callFunction(funcName, evaluatedArgs);
    } else {
      throw new Error(`Unknown statement: ${line}`);
    }
  }

  /**
   * Find matching closing brace for a control flow block
   * Returns the index of the closing brace or -1 if not found
   */
  findMatchingBrace(lines, startIndex) {
    let braceCount = 1;
    let i = startIndex + 1;

    while (i < lines.length && braceCount > 0) {
      const currentLine = lines[i].trim();
      // Count braces only for control flow statements and class/function declarations
      if (currentLine.startsWith('thirsty ') && currentLine.endsWith('{')) {
        braceCount++;
      } else if (currentLine.startsWith('refill ') && currentLine.endsWith('{')) {
        braceCount++;
      } else if (currentLine === 'hydrated {') {
        braceCount++;
      } else if (currentLine === 'try {' || currentLine.startsWith('try {')) {
        braceCount++;
      } else if (currentLine.startsWith('glass ') && currentLine.endsWith('{')) {
        braceCount++;
      } else if (currentLine.startsWith('fountain ') && currentLine.endsWith('{')) {
        braceCount++;
      } else if (currentLine.startsWith('shield ') && currentLine.endsWith('{')) {
        braceCount++;
      } else if (currentLine === '}') {
        braceCount--;
        if (braceCount === 0) {
          return i;
        }
      } else if (currentLine.includes('} catch') || currentLine.includes('} finally')) {
        // Line has both closing and opening brace - these balance out
        // but we still count the close for the current block
        braceCount--;
        if (braceCount === 0) {
          return i;
        }
        braceCount++; // Add back for the opening brace on same line
      }
      i++;
    }

    return -1; // No matching brace found
  }

  /**
   * Handle thirsty (if) statement
   */
  handleThirsty(lines, startIndex) {
    return this.controlFlowHandlers.handleThirsty(lines, startIndex);
  }

  /**
   * Evaluate a condition for if statements
   */
  evaluateCondition(condition) {
    return this.controlFlowHandlers.evaluateCondition(condition);
  }

  /**
   * Handle refill (loop) statement
   */
  handleRefill(lines, startIndex) {
    return this.controlFlowHandlers.handleRefill(lines, startIndex);
  }

  /**
   * Handle try/catch/finally statement
   */
  handleTry(lines, startIndex) {
    return this.exceptionHandlers.handleTry(lines, startIndex);
  }

  /**
   * Handle throw statement
   */
  handleThrow(line) {
    return this.exceptionHandlers.handleThrow(line);
  }

  /**
   * Handle variable declaration: drink varname = value
   * Also handles array element assignment: drink arr[index] = value
   * Also handles property assignment: drink obj.property = value
   */
  handleDrink(line) {
    // Check for property assignment (this.property = value)
    const propMatch = line.match(/drink\s+(\w+)\.(\w+)\s*=\s*(.+)/);
    if (propMatch) {
      const objName = propMatch[1];
      const propName = propMatch[2];
      const valueExpr = propMatch[3];
      
      if (!this.variables.hasOwnProperty(objName)) {
        throw new Error(`Unknown variable: ${objName}`);
      }
      
      const obj = this.variables[objName];
      const value = this.evaluateExpression(valueExpr);
      
      // Handle 'this' reference (which is mapped to instance properties)
      if (typeof obj === 'object' && obj !== null) {
        obj[propName] = value;
      } else {
        throw new Error(`Cannot set property '${propName}' on non-object variable '${objName}'`);
      }
      
      return;
    }
    
    // Check for array element assignment
    const arrayMatch = line.match(/drink\s+(\w+)\[(.+)\]\s*=\s*(.+)/);
    if (arrayMatch) {
      const varName = arrayMatch[1];
      const indexExpr = arrayMatch[2];
      const valueExpr = arrayMatch[3];
      
      const index = this.evaluateExpression(indexExpr);
      const value = this.evaluateExpression(valueExpr);
      
      if (!this.variables.hasOwnProperty(varName) || !Array.isArray(this.variables[varName])) {
        throw new Error(`Variable '${varName}' is not an array`);
      }
      
      this.variables[varName][index] = value;
      return;
    }
    
    // Regular variable assignment
    const match = line.match(/drink\s+(\w+)\s*=\s*(.+)/);
    if (!match) {
      throw new Error(`Invalid drink statement: ${line}`);
    }
    
    const varName = match[1];
    
    // Check if variable is armored (protected)
    if (this.armoredVariables.has(varName) && this.variables.hasOwnProperty(varName)) {
      console.warn(`Warning: Attempt to modify armored variable '${varName}' blocked`);
      return;
    }
    
    const value = this.evaluateExpression(match[2]);
    this.variables[varName] = value;
  }

  /**
   * Handle reservoir (array) declaration: reservoir name = [elements]
   */
  handleReservoir(line) {
    const match = line.match(/reservoir\s+(\w+)\s*=\s*\[([^\]]*)\]/);
    if (!match) {
      throw new Error(`Invalid reservoir statement: ${line}`);
    }
    
    const varName = match[1];
    const elementsStr = match[2].trim();
    
    // Parse array elements
    const elements = elementsStr ? this.parseArguments(elementsStr) : [];
    const evaluatedElements = elements.map(elem => this.evaluateExpression(elem));
    
    // Store as a regular variable with array value
    this.variables[varName] = evaluatedElements;
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
   * Handle input statement: sip varname or sip "prompt"
   */
  handleSip(line) {
    const match = line.match(/sip\s+"([^"]+)"/);
    if (match) {
      // For now, return empty string - in production this would use readline
      return "";
    }
    // Placeholder for input functionality
    console.log('Input functionality not yet implemented');
  }

  /**
   * Handle glass (function declaration) statement
   */
  handleGlass(lines, startIndex) {
    return this.classFunctionHandlers.handleGlass(lines, startIndex);
  }

  /**
   * Handle fountain (class declaration) statement
   */
  handleFountain(lines, startIndex) {
    return this.classFunctionHandlers.handleFountain(lines, startIndex);
  }

  /**
   * Handle import statement
   * Syntax: import ModuleName from "path/to/module.thirsty"
   *        import { func1, func2 } from "path/to/module.thirsty"
   */
  handleImport(line) {
    return this.classFunctionHandlers.handleImport(line);
  }

  /**
   * Handle export statement
   * Syntax: export varname
   *        export glass funcname() { ... }
   */
  handleExport(line) {
    return this.classFunctionHandlers.handleExport(line);
  }

  /**
   * Load a module from file
   */
  loadModule(modulePath) {
    return this.classFunctionHandlers.loadModule(modulePath);
  }

  /**
   * Handle cascade (async function) statement
   * Syntax: cascade funcname(params) { ... }
   */
  handleCascade(lines, startIndex) {
    return this.classFunctionHandlers.handleCascade(lines, startIndex);
  }

  /**
   * Instantiate a class (new ClassName())
   */
  instantiateClass(className, args) {
    return this.classFunctionHandlers.instantiateClass(className, args);
  }

  /**
   * Call a method on a class instance
   */
  callInstanceMethod(instance, methodName, args) {
    return this.classFunctionHandlers.callInstanceMethod(instance, methodName, args);
  }

  /**
   * Call a user-defined function
   */
  callFunction(funcName, args) {
    return this.classFunctionHandlers.callFunction(funcName, args);
  }

  /**
   * Call an async function (cascade)
   */
  async callAsyncFunction(funcName, args) {
    return await this.classFunctionHandlers.callAsyncFunction(funcName, args);
  }

  /**
   * Execute a block of code asynchronously
   */
  async executeBlockAsync(lines, startIndex) {
    return await this.classFunctionHandlers.executeBlockAsync(lines, startIndex);
  }

  /**
   * Evaluate an expression asynchronously (for await)
   */
  async evaluateExpressionAsync(expr) {
    return await this.classFunctionHandlers.evaluateExpressionAsync(expr);
  }

  /**
   * Handle shield (security block) statement
   */
  handleShield(lines, startIndex) {
    return this.securityHandlers.handleShield(lines, startIndex);
  }

  /**
   * Handle sanitize (input cleaning) statement
   */
  handleSanitize(line) {
    return this.securityHandlers.handleSanitize(line);
  }

  /**
   * Handle armor (memory protection) statement
   */
  handleArmor(line) {
    return this.securityHandlers.handleArmor(line);
  }

  /**
   * Handle morph (code obfuscation) statement
   */
  handleMorph(line) {
    return this.securityHandlers.handleMorph(line);
  }

  /**
   * Handle detect (threat monitoring) statement
   */
  handleDetect(line) {
    return this.securityHandlers.handleDetect(line);
  }

  /**
   * Handle defend (countermeasures) statement
   */
  handleDefend(line) {
    return this.securityHandlers.handleDefend(line);
  }

  /**
   * Basic sanitization (fallback when security manager not enabled)
   * Production-grade HTML encoding to prevent XSS
   */
  basicSanitize(value) {
    return this.securityHandlers.basicSanitize(value);
  }

  /**
   * Evaluate an expression (variable or literal) with proper operator precedence
   */
  evaluateExpression(expr) {
    return this.expressionEvaluator.evaluateExpression(expr);
  }

  /**
   * Handle array method calls (push, pop, etc.)
   */
  handleArrayMethod(varName, arr, methodName, argsStr) {
    return this.expressionEvaluator.handleArrayMethod(varName, arr, methodName, argsStr);
  }

  /**
   * Extract content between parentheses, handling nested parentheses
   */
  extractParenthesesContent(expr, startIdx) {
    return this.expressionEvaluator.extractParenthesesContent(expr, startIdx);
  }

  /**
   * Parse function call arguments, respecting nested parentheses and strings
   */
  parseArguments(argsStr) {
    return this.expressionEvaluator.parseArguments(argsStr);
  }

  /**
   * Check if a position is inside a string literal
   */
  isInString(expr, pos) {
    return this.expressionEvaluator.isInString(expr, pos);
  }

  /**
   * Check if a position is inside parentheses
   */
  isInParentheses(expr, pos) {
    return this.expressionEvaluator.isInParentheses(expr, pos);
  }

  /**
   * Split expression by operator, respecting strings
   */
  splitExpression(expr, operator) {
    return this.expressionEvaluator.splitExpression(expr, operator);
  }
}

module.exports = { ThirstyInterpreter, ThirstyError };
