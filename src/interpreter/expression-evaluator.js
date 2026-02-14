/* eslint-env node */
/* global module */
/**
 * Optimized Expression Evaluator for Thirsty-lang
 * Implements regex pattern caching and optimized string scanning
 */

class ExpressionEvaluator {
  constructor(variables = {}) {
    this.variables = variables;

    // Cache regex patterns (compiled once at initialization)
    this.patterns = {
      doubleQuoteString: /^".*"$/,
      singleQuoteString: /^'.*'$/,
      number: /^\d+(\.\d+)?$/,
      variable: /^[a-zA-Z_]\w*$/
    };
  }

  /**
   * Evaluate an expression (variable or literal)
   * Optimized with regex pattern caching
   */
  evaluateExpression(expr) {
    expr = expr.trim();

    // String literal (double quotes) - using cached pattern
    if (this.patterns.doubleQuoteString.test(expr)) {
      return expr.slice(1, -1);
    }

    // String literal (single quotes) - using cached pattern
    if (this.patterns.singleQuoteString.test(expr)) {
      return expr.slice(1, -1);
    }

    // Number literal - using cached pattern
    if (this.patterns.number.test(expr)) {
      return parseFloat(expr);
    }

    // Variable reference - using cached pattern
    if (this.patterns.variable.test(expr)) {
      if (Object.prototype.hasOwnProperty.call(this.variables, expr)) {
        return this.variables[expr];
      }
    }

    throw new Error(`Unknown expression: ${expr}`);
  }

  /**
   * Check if a position is inside a string literal
   * Optimized with early exit for position 0
   */
  isInString(str, pos) {
    // Early exit for common case
    if (pos === 0) return false;

    let inString = false;
    let quoteChar = null;

    for (let i = 0; i < pos; i++) {
      const char = str[i];
      if (char === '"' || char === "'") {
        if (!inString) {
          inString = true;
          quoteChar = char;
        } else if (char === quoteChar) {
          inString = false;
          quoteChar = null;
        }
      }
    }

    return inString;
  }

  /**
   * Find operators in expression, excluding those in strings
   * Optimized to reduce redundant string scanning
   */
  findOperator(expr, operators) {
    for (const op of operators) {
      const idx = expr.indexOf(op);
      if (idx !== -1 && !this.isInString(expr, idx)) {
        return { operator: op, index: idx };
      }
    }
    return null;
  }

  /**
   * Evaluate a binary expression
   * Example: "5 + 3", "x * 2"
   */
  evaluateBinaryExpression(expr, operator, index) {
    const left = this.evaluateExpression(expr.substring(0, index));
    const right = this.evaluateExpression(expr.substring(index + operator.length));

    switch (operator) {
      case '+': return left + right;
      case '-': return left - right;
      case '*': return left * right;
      case '/': return left / right;
      case '%': return left % right;
      default: throw new Error(`Unknown operator: ${operator}`);
    }
  }

  /**
   * Check if expression contains operators
   */
  hasOperators(expr) {
    const operators = ['+', '-', '*', '/', '%'];
    return this.findOperator(expr, operators) !== null;
  }

  /**
   * Evaluate complex expression with operators
   */
  evaluateComplexExpression(expr) {
    const operators = ['+', '-', '*', '/', '%'];
    const found = this.findOperator(expr, operators);

    if (found) {
      return this.evaluateBinaryExpression(expr, found.operator, found.index);
    }

    return this.evaluateExpression(expr);
  }
}

module.exports = ExpressionEvaluator;
