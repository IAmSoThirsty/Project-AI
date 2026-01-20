#!/usr/bin/env node

/**
 * Thirsty-lang Interpreter
 * A fun programming language for the thirsty
 */

class ThirstyInterpreter {
  constructor() {
    this.variables = {};
    this.functions = {};
    this.classes = {};
  }

  /**
   * Parse and execute Thirsty-lang code
   * @param {string} code - The Thirsty-lang source code
   */
  execute(code) {
    /* eslint-env node */
    /* global module, console */
    const lines = code.split('\n').map(line => line.trim()).filter(line => line && !line.startsWith('//'));
    let i = 0;
    while (i < lines.length) {
      const line = lines[i];
      // Control flow: thirsty (if statement)
      if (line.startsWith('thirsty ')) {
        const condMatch = line.match(/thirsty\s+(.+)/);
        if (!condMatch) throw new Error(`Invalid thirsty statement: ${line}`);
        const condition = condMatch[1];
        const bodyLine = lines[i + 1];
        if (this.evaluateCondition(condition)) {
          this.executeLine(bodyLine);
        }
        i += 2;
        continue;
      }
      // Function definition: glass name(args)
      if (line.startsWith('glass ')) {
        const fnMatch = line.match(/glass\s+(\w+)\(([^)]*)\)/);
        if (!fnMatch) throw new Error(`Invalid glass statement: ${line}`);
        const fnName = fnMatch[1];
        const argList = fnMatch[2].split(',').map(a => a.trim()).filter(Boolean);
        // Function body: next line(s) until 'endglass'
        let body = [];
        i++;
        while (i < lines.length && !lines[i].startsWith('endglass')) {
          body.push(lines[i]);
          i++;
        }
        this.functions[fnName] = { args: argList, body };
        i++; // skip 'endglass'
        continue;
      }
      // Function call: fnName(args)
      const fnCallMatch = line.match(/^(\w+)\(([^)]*)\)$/);
      if (fnCallMatch && this.functions[fnCallMatch[1]]) {
        const fnName = fnCallMatch[1];
        const argVals = fnCallMatch[2].split(',').map(a => this.evaluateExpression(a.trim()));
        this.callFunction(fnName, argVals);
        i++;
        continue;
      }
      // Class definition: fountain ClassName
      if (line.startsWith('fountain ')) {
        const classMatch = line.match(/fountain\s+(\w+)/);
        if (!classMatch) throw new Error(`Invalid fountain statement: ${line}`);
        const className = classMatch[1];
        let body = [];
        i++;
        while (i < lines.length && !lines[i].startsWith('endfountain')) {
          body.push(lines[i]);
          i++;
        }
        this.classes[className] = { body };
        i++; // skip 'endfountain'
        continue;
      }
      // Class instantiation: new ClassName
      const newClassMatch = line.match(/^new\s+(\w+)/);
      if (newClassMatch && this.classes[newClassMatch[1]]) {
        const className = newClassMatch[1];
        // For simplicity, just execute class body
        for (const classLine of this.classes[className].body) {
          this.executeLine(classLine);
        }
        i++;
        continue;
      }
      this.executeLine(line);
      i++;
    }
    /**
     * Call a Thirsty-lang function
     */
    callFunction(fnName, argVals) {
      const fn = this.functions[fnName];
      if (!fn) throw new Error(`Function not found: ${fnName}`);
      // Save current variables
      const oldVars = { ...this.variables };
      // Set args
      fn.args.forEach((name, idx) => {
        this.variables[name] = argVals[idx];
      });
      // Execute body
      for (const line of fn.body) {
        this.executeLine(line);
      }
      // Restore variables
      this.variables = oldVars;
    }
  }
  /**
   * Evaluate a simple condition for thirsty (if) statements
   * Supports: var op value, e.g. temperature > 30
   */
  evaluateCondition(cond) {
    // Only support: <var> <op> <value>
    const match = cond.match(/(\w+)\s*(==|!=|>=|<=|>|<)\s*(.+)/);
    if (!match) throw new Error(`Invalid condition: ${cond}`);
    const varName = match[1];
    const op = match[2];
    let value = match[3];
    const left = this.variables[varName];
    // Try to parse value as number, else string
    if (!isNaN(value)) value = parseFloat(value);
    switch (op) {
      case '==': return left == value;
      case '!=': return left != value;
      case '>': return left > value;
      case '<': return left < value;
      case '>=': return left >= value;
      case '<=': return left <= value;
      default: throw new Error(`Unknown operator: ${op}`);
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
    if (Object.prototype.hasOwnProperty.call(this.variables, expr)) {
      return this.variables[expr];
    }

    throw new Error(`Unknown expression: ${expr}`);
  }
}

module.exports = ThirstyInterpreter;
