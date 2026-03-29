/**
 * Expression Evaluator Module
 * Handles expression parsing, evaluation, and operator precedence
 */

/**
 * Expression evaluator class that needs access to interpreter context
 */
class ExpressionEvaluator {
  constructor(interpreter) {
    this.interpreter = interpreter;
    // Cache compiled regex patterns for performance
    this.funcMatchRegex = /^(\w+)\s*\(/;
    this.arrayAccessRegex = /^(\w+)\[(.+)\]$/;
    this.methodMatchRegex = /^(\w+)\.(\w+)\s*\(([^)]*)\)$/;
    this.propertyMatchRegex = /^(\w+)\.(\w+)$/;
  }

  /**
   * Evaluate an expression
   */
  evaluateExpression(expr) {
    expr = expr.trim();

    // Handle addition and subtraction (lowest precedence)
    // Only split if there's a + or - NOT inside a higher precedence operation
    for (let i = expr.length - 1; i >= 0; i--) {
      if (this.isInString(expr, i)) continue;
      if (this.isInParentheses(expr, i)) continue;

      if (expr[i] === '+') {
        const left = expr.substring(0, i).trim();
        const right = expr.substring(i + 1).trim();
        if (left && right) {
          const leftVal = this.evaluateExpression(left);
          const rightVal = this.evaluateExpression(right);

          // If both are numbers, do numeric addition
          if (typeof leftVal === 'number' && typeof rightVal === 'number') {
            return leftVal + rightVal;
          }
          // Otherwise string concatenation
          return String(leftVal) + String(rightVal);
        }
      }

      if (expr[i] === '-' && i > 0 && !expr.startsWith('-')) {
        const left = expr.substring(0, i).trim();
        const right = expr.substring(i + 1).trim();
        if (left && right) {
          return this.evaluateExpression(left) - this.evaluateExpression(right);
        }
      }
    }

    // Handle multiplication and division (higher precedence)
    for (let i = expr.length - 1; i >= 0; i--) {
      if (this.isInString(expr, i)) continue;
      if (this.isInParentheses(expr, i)) continue;

      if (expr[i] === '*') {
        const left = expr.substring(0, i).trim();
        const right = expr.substring(i + 1).trim();
        if (left && right) {
          return this.evaluateExpression(left) * this.evaluateExpression(right);
        }
      }

      if (expr[i] === '/') {
        const left = expr.substring(0, i).trim();
        const right = expr.substring(i + 1).trim();
        if (left && right) {
          const divisor = this.evaluateExpression(right);
          if (divisor === 0) {
            throw new Error(`Division by zero in expression: ${expr}`);
          }
          return this.evaluateExpression(left) / divisor;
        }
      }
    }

    // String literal
    if ((expr.startsWith('"') && expr.endsWith('"')) ||
        (expr.startsWith("'") && expr.endsWith("'"))) {
      return expr.slice(1, -1);
    }

    // Boolean literals
    if (expr === 'true') return true;
    if (expr === 'false') return false;

    // Number literal (including negative numbers)
    if (!isNaN(expr)) {
      return parseFloat(expr);
    }

    // Function call or class instantiation - check for name(args) with nested parentheses
    const funcMatch = expr.match(this.funcMatchRegex);
    if (funcMatch) {
      const name = funcMatch[1];
      const startIdx = expr.indexOf('(');
      const argsStr = this.extractParenthesesContent(expr, startIdx);
      const args = argsStr ? this.parseArguments(argsStr) : [];
      const evaluatedArgs = args.map(arg => this.evaluateExpression(arg));

      // Check if it's a class (class names typically start with uppercase)
      if (this.interpreter.classes.hasOwnProperty(name)) {
        return this.interpreter.instantiateClass(name, evaluatedArgs);
      }

      // Check if it's a function
      if (this.interpreter.functions.hasOwnProperty(name)) {
        return this.interpreter.callFunction(name, evaluatedArgs);
      }

      // Neither class nor function
      throw new Error(`Undefined class or function: ${name}`);
    }

    // Array access - varname[index]
    const arrayAccessMatch = expr.match(this.arrayAccessRegex);
    if (arrayAccessMatch) {
      const varName = arrayAccessMatch[1];
      const indexExpr = arrayAccessMatch[2];

      if (!this.interpreter.variables.hasOwnProperty(varName)) {
        throw new Error(`Unknown variable: ${varName}`);
      }

      const arr = this.interpreter.variables[varName];
      if (!Array.isArray(arr)) {
        throw new Error(`Variable '${varName}' is not an array`);
      }

      const index = this.evaluateExpression(indexExpr);

      if (index < 0 || index >= arr.length) {
        throw new Error(`Array index out of bounds: ${index} (length: ${arr.length})`);
      }

      return arr[index];
    }

    // Array/string/instance method calls - varname.method(args)
    const methodMatch = expr.match(this.methodMatchRegex);
    if (methodMatch) {
      const varName = methodMatch[1];
      const methodName = methodMatch[2];
      const argsStr = methodMatch[3].trim();

      if (!this.interpreter.variables.hasOwnProperty(varName)) {
        throw new Error(`Unknown variable: ${varName}`);
      }

      const obj = this.interpreter.variables[varName];

      // Handle array methods
      if (Array.isArray(obj)) {
        return this.handleArrayMethod(varName, obj, methodName, argsStr);
      }

      // Handle class instance methods
      if (obj && typeof obj === 'object' && obj.__class && obj.__methods) {
        const args = argsStr ? this.parseArguments(argsStr) : [];
        const evaluatedArgs = args.map(arg => this.evaluateExpression(arg));
        return this.interpreter.callInstanceMethod(obj, methodName, evaluatedArgs);
      }

      // Handle built-in library methods (Math, String, etc.)
      if (obj && typeof obj === 'object' && obj.__builtin) {
        const args = argsStr ? this.parseArguments(argsStr) : [];
        const evaluatedArgs = args.map(arg => this.evaluateExpression(arg));
        if (typeof obj[methodName] === 'function') {
          return obj[methodName](...evaluatedArgs);
        }
        throw new Error(`Built-in method '${methodName}' not found in '${varName}'`);
      }

      throw new Error(`Method '${methodName}' not supported for variable '${varName}'`);
    }

    // Array/string/instance property access - varname.property
    const propertyMatch = expr.match(this.propertyMatchRegex);
    if (propertyMatch) {
      const varName = propertyMatch[1];
      const propName = propertyMatch[2];

      if (!this.interpreter.variables.hasOwnProperty(varName)) {
        throw new Error(`Unknown variable: ${varName}`);
      }

      const obj = this.interpreter.variables[varName];

      // Handle class instance properties
      if (obj && typeof obj === 'object' && obj.__class && obj.__properties) {
        if (obj.__properties.hasOwnProperty(propName)) {
          return obj.__properties[propName];
        }
        throw new Error(`Property '${propName}' not found in class ${obj.__class}`);
      }

      // Handle length property for arrays and strings
      if (propName === 'length') {
        if (Array.isArray(obj) || typeof obj === 'string') {
          return obj.length;
        }
      }

      // Handle generic object property access
      if (typeof obj === 'object' && obj !== null && obj.hasOwnProperty(propName)) {
        return obj[propName];
      }

      throw new Error(`Property '${propName}' not supported for variable '${varName}'`);
    }

    // Variable reference
    if (this.interpreter.variables.hasOwnProperty(expr)) {
      return this.interpreter.variables[expr];
    }

    throw new Error(`Unknown expression: ${expr}`);
  }

  /**
   * Handle array method calls (push, pop, etc.)
   */
  handleArrayMethod(varName, arr, methodName, argsStr) {
    const args = argsStr ? this.parseArguments(argsStr) : [];
    const evaluatedArgs = args.map(arg => this.evaluateExpression(arg));

    switch (methodName) {
      case 'push':
        // Add elements to the end of the array
        for (const arg of evaluatedArgs) {
          arr.push(arg);
        }
        return arr.length;

      case 'pop':
        // Remove and return the last element
        if (arr.length === 0) {
          throw new Error(`Cannot pop from empty array '${varName}'`);
        }
        return arr.pop();

      case 'shift':
        // Remove and return the first element
        if (arr.length === 0) {
          throw new Error(`Cannot shift from empty array '${varName}'`);
        }
        return arr.shift();

      case 'unshift':
        // Add elements to the beginning of the array
        for (const arg of evaluatedArgs) {
          arr.unshift(arg);
        }
        return arr.length;

      case 'slice':
        // Return a shallow copy of a portion of the array
        const start = evaluatedArgs[0] || 0;
        const end = evaluatedArgs[1];
        return arr.slice(start, end);

      case 'indexOf':
        // Find the index of an element
        if (evaluatedArgs.length === 0) {
          throw new Error(`indexOf requires at least one argument`);
        }
        return arr.indexOf(evaluatedArgs[0]);

      case 'includes':
        // Check if array contains an element
        if (evaluatedArgs.length === 0) {
          throw new Error(`includes requires at least one argument`);
        }
        return arr.includes(evaluatedArgs[0]);

      case 'join':
        // Join array elements into a string
        const separator = evaluatedArgs[0] !== undefined ? evaluatedArgs[0] : ',';
        return arr.join(separator);

      case 'reverse':
        // Reverse the array in place
        arr.reverse();
        return arr;

      case 'sort':
        // Sort the array in place
        arr.sort();
        return arr;

      default:
        throw new Error(`Unknown array method: ${methodName}`);
    }
  }

  /**
   * Extract content between parentheses, handling nested parentheses
   */
  extractParenthesesContent(expr, startIdx) {
    let depth = 0;
    let content = '';

    for (let i = startIdx; i < expr.length; i++) {
      const char = expr[i];

      if (char === '(') {
        if (depth > 0) {
          content += char;
        }
        depth++;
      } else if (char === ')') {
        depth--;
        if (depth > 0) {
          content += char;
        } else if (depth === 0) {
          return content;
        }
      } else if (depth > 0) {
        content += char;
      }
    }

    throw new Error('Unmatched parentheses in expression');
  }

  /**
   * Parse function call arguments, respecting nested parentheses and strings
   */
  parseArguments(argsStr) {
    const args = [];
    let current = '';
    let depth = 0;
    let inString = false;
    let stringChar = null;

    for (let i = 0; i < argsStr.length; i++) {
      const char = argsStr[i];

      if ((char === '"' || char === "'") && (i === 0 || argsStr[i-1] !== '\\')) {
        if (!inString) {
          inString = true;
          stringChar = char;
        } else if (char === stringChar) {
          inString = false;
          stringChar = null;
        }
        current += char;
      } else if (char === '(' && !inString) {
        depth++;
        current += char;
      } else if (char === ')' && !inString) {
        depth--;
        current += char;
      } else if (char === ',' && depth === 0 && !inString) {
        args.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }

    if (current.trim()) {
      args.push(current.trim());
    }

    return args;
  }

  /**
   * Check if a position is inside a string literal
   * Optimized to cache results for the same expression
   */
  isInString(expr, pos) {
    // Early exit for positions at start
    if (pos === 0) return false;

    let inString = false;
    let stringChar = null;
    let prevChar = '';

    for (let i = 0; i < pos; i++) {
      const currentChar = expr[i];
      if ((currentChar === '"' || currentChar === "'") && prevChar !== '\\') {
        if (!inString) {
          inString = true;
          stringChar = currentChar;
        } else if (currentChar === stringChar) {
          inString = false;
          stringChar = null;
        }
      }
      prevChar = currentChar;
    }
    return inString;
  }

  /**
   * Check if a position is inside parentheses
   */
  isInParentheses(expr, pos) {
    let depth = 0;
    for (let i = 0; i < pos; i++) {
      // Skip if in string
      if (this.isInString(expr, i)) continue;

      if (expr[i] === '(') {
        depth++;
      } else if (expr[i] === ')') {
        depth--;
      }
    }
    return depth > 0;
  }

  /**
   * Split expression by operator, respecting strings
   */
  splitExpression(expr, operator) {
    const parts = [];
    let current = '';
    let inString = false;
    let stringChar = null;

    for (let i = 0; i < expr.length; i++) {
      const char = expr[i];

      if ((char === '"' || char === "'") && (i === 0 || expr[i-1] !== '\\')) {
        if (!inString) {
          inString = true;
          stringChar = char;
        } else if (char === stringChar) {
          inString = false;
          stringChar = null;
        }
        current += char;
      } else if (char === operator && !inString) {
        const trimmed = current.trim();
        if (trimmed) { // Only add non-empty parts
          parts.push(trimmed);
        }
        current = '';
      } else {
        current += char;
      }
    }

    const trimmed = current.trim();
    if (trimmed) { // Only add non-empty parts
      parts.push(trimmed);
    }

    return parts.length > 0 ? parts : [''];
  }
}

module.exports = { ExpressionEvaluator };
