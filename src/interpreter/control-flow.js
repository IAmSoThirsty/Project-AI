/* eslint-env node */
/* global module */
/**
 * Optimized Control Flow for Thirsty-lang
 * Implements optimized condition evaluation with indexOf instead of includes+split
 */

class ControlFlow {
  constructor(variables = {}) {
    this.variables = variables;
  }

  /**
   * Evaluate a condition for thirsty (if) statements
   * Optimized: Single string scan with indexOf() instead of includes() + split()
   * Supports: var op value, e.g. temperature > 30
   */
  evaluateCondition(condition) {
    condition = condition.trim();

    // Try operators in order of specificity (longest first to avoid conflicts)
    const operators = ['==', '!=', '>=', '<=', '>', '<'];

    for (const op of operators) {
      const idx = condition.indexOf(op);
      if (idx !== -1) {
        // Single-pass extraction using indexOf and substring
        const left = condition.substring(0, idx).trim();
        const right = condition.substring(idx + op.length).trim();

        // Get left value (variable or literal)
        const leftValue = this.getValue(left);
        // Get right value (literal or variable)
        const rightValue = this.getValue(right);

        // Perform comparison
        return this.compare(leftValue, rightValue, op);
      }
    }

    throw new Error(`Invalid condition: ${condition}`);
  }

  /**
   * Get value from variable name or literal
   */
  getValue(expr) {
    expr = expr.trim();

    // String literal (double quotes)
    if (expr.startsWith('"') && expr.endsWith('"')) {
      return expr.slice(1, -1);
    }

    // String literal (single quotes)
    if (expr.startsWith("'") && expr.endsWith("'")) {
      return expr.slice(1, -1);
    }

    // Number literal
    if (!isNaN(expr)) {
      return parseFloat(expr);
    }

    // Variable reference
    if (Object.prototype.hasOwnProperty.call(this.variables, expr)) {
      return this.variables[expr];
    }

    // Undefined variable returns undefined
    return undefined;
  }

  /**
   * Compare two values based on operator
   */
  compare(left, right, operator) {
    switch (operator) {
      case '==': return left == right;  // Intentional loose equality
      case '!=': return left != right;  // Intentional loose inequality
      case '>': return left > right;
      case '<': return left < right;
      case '>=': return left >= right;
      case '<=': return left <= right;
      default: throw new Error(`Unknown operator: ${operator}`);
    }
  }

  /**
   * Parse and evaluate compound conditions (with AND/OR)
   * Future optimization target
   */
  evaluateCompoundCondition(condition) {
    // For now, delegate to simple condition
    // Future: implement AND (&&) and OR (||) logic
    return this.evaluateCondition(condition);
  }

  /**
   * Update variables reference
   */
  setVariables(variables) {
    this.variables = variables;
  }
}

module.exports = ControlFlow;
