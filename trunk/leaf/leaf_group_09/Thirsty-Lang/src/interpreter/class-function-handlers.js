/**
 * Class and Function Handlers Module
 * Provides function definitions, class declarations, async functions, and module system
 */

const fs = require('fs');
const path = require('path');

/**
 * Class and function handlers class that needs access to interpreter context
 */
class ClassFunctionHandlers {
  constructor(interpreter) {
    this.interpreter = interpreter;
  }

  /**
   * Handle glass (function declaration) statement
   */
  handleGlass(lines, startIndex) {
    const line = lines[startIndex].trim();
    const match = line.match(/glass\s+(\w+)\s*\(([^)]*)\)\s*{/);

    if (!match) {
      throw new Error(`Invalid glass (function) statement: ${line}`);
    }

    const funcName = match[1];
    const params = match[2].split(',').map(p => p.trim()).filter(p => p);

    // Find the matching closing brace
    const blockEnd = this.interpreter.findMatchingBrace(lines, startIndex);

    if (blockEnd === -1) {
      throw new Error(`Unmatched opening brace for glass statement at line ${startIndex + 1}`);
    }

    // Store the function definition
    this.interpreter.functions[funcName] = {
      params: params,
      body: lines.slice(startIndex + 1, blockEnd),
      line: startIndex
    };

    return blockEnd + 1;
  }

  /**
   * Handle fountain (class declaration) statement
   */
  handleFountain(lines, startIndex) {
    const line = lines[startIndex].trim();
    const match = line.match(/fountain\s+(\w+)\s*{/);

    if (!match) {
      throw new Error(`Invalid fountain (class) statement: ${line}`);
    }

    const className = match[1];

    // Find the matching closing brace
    const blockEnd = this.interpreter.findMatchingBrace(lines, startIndex);

    if (blockEnd === -1) {
      throw new Error(`Unmatched opening brace for fountain statement at line ${startIndex + 1}`);
    }

    // Parse class body to extract methods and properties
    const classBody = lines.slice(startIndex + 1, blockEnd);
    const methods = {};
    const properties = [];

    let i = 0;
    while (i < classBody.length) {
      const bodyLine = classBody[i].trim();

      if (!bodyLine || bodyLine.startsWith('//')) {
        i++;
        continue;
      }

      // Check for method declaration
      if (bodyLine.startsWith('glass ')) {
        const methodMatch = bodyLine.match(/glass\s+(\w+)\s*\(([^)]*)\)\s*{/);
        if (methodMatch) {
          const methodName = methodMatch[1];
          const params = methodMatch[2].split(',').map(p => p.trim()).filter(p => p);

          // Find method body end by counting all braces
          let methodEnd = -1;
          let braceCount = 1;

          for (let j = i + 1; j < classBody.length; j++) {
            const currentLine = classBody[j];

            // Count all opening and closing braces in the line
            for (const char of currentLine) {
              if (char === '{') braceCount++;
              if (char === '}') braceCount--;
            }

            if (braceCount === 0) {
              methodEnd = j;
              break;
            }
          }

          if (methodEnd === -1 || braceCount !== 0) {
            throw new Error(`Unmatched opening brace for method ${methodName}`);
          }

          methods[methodName] = {
            params: params,
            body: classBody.slice(i + 1, methodEnd)
          };

          i = methodEnd + 1;
          continue;
        }
      }

      // Check for property declaration
      if (bodyLine.startsWith('drink ')) {
        const propMatch = bodyLine.match(/drink\s+(\w+)\s*=\s*(.+)/);
        if (propMatch) {
          properties.push({
            name: propMatch[1],
            defaultValue: propMatch[2]
          });
        }
      }

      i++;
    }

    // Store the class definition
    this.interpreter.classes[className] = {
      name: className,
      methods: methods,
      properties: properties,
      line: startIndex
    };

    return blockEnd + 1;
  }

  /**
   * Handle cascade (async function) statement
   * Syntax: cascade funcname(params) { ... }
   */
  handleCascade(lines, startIndex) {
    const line = lines[startIndex].trim();
    const match = line.match(/cascade\s+(\w+)\s*\(([^)]*)\)\s*{/);

    if (!match) {
      throw new Error(`Invalid cascade (async function) statement: ${line}`);
    }

    const funcName = match[1];
    const params = match[2].split(',').map(p => p.trim()).filter(p => p);

    // Find the matching closing brace
    const blockEnd = this.interpreter.findMatchingBrace(lines, startIndex);

    if (blockEnd === -1) {
      throw new Error(`Unmatched opening brace for cascade statement at line ${startIndex + 1}`);
    }

    // Store the async function definition
    this.interpreter.functions[funcName] = {
      params: params,
      body: lines.slice(startIndex + 1, blockEnd),
      line: startIndex,
      async: true  // Mark as async
    };

    this.interpreter.asyncFunctions.add(funcName);

    return blockEnd + 1;
  }

  /**
   * Handle import statement
   * Syntax: import ModuleName from "path/to/module.thirsty"
   *        import { func1, func2 } from "path/to/module.thirsty"
   */
  handleImport(line) {
    // Pattern 1: import ModuleName from "path"
    let match = line.match(/import\s+(\w+)\s+from\s+["']([^"']+)["']/);
    if (match) {
      const moduleName = match[1];
      const modulePath = match[2];
      const exports = this.loadModule(modulePath);
      this.interpreter.variables[moduleName] = exports;
      return;
    }

    // Pattern 2: import { name1, name2 } from "path"
    match = line.match(/import\s+{([^}]+)}\s+from\s+["']([^"']+)["']/);
    if (match) {
      const names = match[1].split(',').map(n => n.trim());
      const modulePath = match[2];
      const exports = this.loadModule(modulePath);

      names.forEach(name => {
        if (exports.hasOwnProperty(name)) {
          const exported = exports[name];
          // If it's a function definition, add to functions dictionary
          if (exported && typeof exported === 'object' && exported.params && exported.body) {
            this.interpreter.functions[name] = exported;
          } else {
            // Otherwise add to variables
            this.interpreter.variables[name] = exported;
          }
        } else {
          throw new Error(`Module does not export '${name}'`);
        }
      });
      return;
    }

    throw new Error(`Invalid import statement: ${line}`);
  }

  /**
   * Handle export statement
   * Syntax: export varname
   *        export glass funcname() { ... }
   */
  handleExport(line) {
    // Pattern: export varname
    const match = line.match(/export\s+(\w+)/);
    if (match) {
      const varName = match[1];
      if (this.interpreter.variables.hasOwnProperty(varName)) {
        this.interpreter.exports[varName] = this.interpreter.variables[varName];
      } else if (this.interpreter.functions.hasOwnProperty(varName)) {
        this.interpreter.exports[varName] = this.interpreter.functions[varName];
      } else {
        throw new Error(`Cannot export undefined identifier: ${varName}`);
      }
      return;
    }

    throw new Error(`Invalid export statement: ${line}`);
  }

  /**
   * Load a module from file
   */
  loadModule(modulePath) {
    // Resolve relative paths
    let absolutePath = modulePath;
    if (this.interpreter.currentFile && !path.isAbsolute(modulePath)) {
      absolutePath = path.resolve(path.dirname(this.interpreter.currentFile), modulePath);
    }

    // Check cache
    if (this.interpreter.modules[absolutePath]) {
      return this.interpreter.modules[absolutePath];
    }

    // Load and execute module
    if (!fs.existsSync(absolutePath)) {
      throw new Error(`Module not found: ${absolutePath}`);
    }

    const code = fs.readFileSync(absolutePath, 'utf8');

    // Create new interpreter instance for module
    const ThirstyInterpreter = require('../index');
    const moduleInterpreter = new ThirstyInterpreter({
      currentFile: absolutePath,
      security: this.interpreter.securityEnabled,
      securityMode: this.interpreter.securityManager.mode
    });

    // Execute module code
    moduleInterpreter.execute(code);

    // Cache and return exports
    this.interpreter.modules[absolutePath] = moduleInterpreter.exports;
    return moduleInterpreter.exports;
  }

  /**
   * Instantiate a class (new ClassName())
   */
  instantiateClass(className, args) {
    if (!this.interpreter.classes.hasOwnProperty(className)) {
      throw new Error(`Undefined class: ${className}`);
    }

    const classDef = this.interpreter.classes[className];

    // Create instance object
    const instance = {
      __class: className,
      __properties: {},
      __methods: {}
    };

    // Initialize properties with default values
    for (const prop of classDef.properties) {
      instance.__properties[prop.name] = this.interpreter.evaluateExpression(prop.defaultValue);
    }

    // Bind methods to the instance
    for (const methodName in classDef.methods) {
      instance.__methods[methodName] = classDef.methods[methodName];
    }

    // Call constructor if exists (constructor is a special method named 'fountain')
    if (classDef.methods.hasOwnProperty('fountain')) {
      this.callInstanceMethod(instance, 'fountain', args);
    }

    return instance;
  }

  /**
   * Call a method on a class instance
   */
  callInstanceMethod(instance, methodName, args) {
    if (!instance.__methods.hasOwnProperty(methodName)) {
      throw new Error(`Method '${methodName}' not found in class ${instance.__class}`);
    }

    const method = instance.__methods[methodName];

    // Check argument count
    if (args.length !== method.params.length) {
      throw new Error(`Method ${methodName} expects ${method.params.length} arguments, got ${args.length}`);
    }

    // Save current variable scope
    const savedVariables = { ...this.interpreter.variables };

    // Create new scope with method parameters and 'this' reference
    const methodScope = { ...this.interpreter.variables };
    for (let i = 0; i < method.params.length; i++) {
      methodScope[method.params[i]] = args[i];
    }

    // Add 'this' reference to instance properties
    methodScope.this = instance.__properties;

    this.interpreter.variables = methodScope;

    try {
      // Execute method body
      this.interpreter.executeBlock(method.body, 0);

      // Restore variable scope
      this.interpreter.variables = savedVariables;

      return undefined;
    } catch (e) {
      // Handle return statement
      if (e.type === 'return') {
        this.interpreter.variables = savedVariables;
        return e.value;
      }
      // Re-throw other errors
      throw e;
    }
  }

  /**
   * Call a user-defined function
   */
  callFunction(funcName, args) {
    if (!this.interpreter.functions.hasOwnProperty(funcName)) {
      // Check if it's a class name instead
      if (this.interpreter.classes.hasOwnProperty(funcName)) {
        throw new Error(`'${funcName}' is a class, not a function. Cannot call as function.`);
      }
      throw new Error(`Undefined function: ${funcName}`);
    }

    // Check call stack depth
    if (this.interpreter.callStack.length >= this.interpreter.MAX_CALL_DEPTH) {
      throw new Error(`Maximum call depth exceeded (${this.interpreter.MAX_CALL_DEPTH})`);
    }

    const func = this.interpreter.functions[funcName];

    // Check argument count
    if (args.length !== func.params.length) {
      throw new Error(`Function ${funcName} expects ${func.params.length} arguments, got ${args.length}`);
    }

    // If async function, return a promise
    if (func.async) {
      return this.callAsyncFunction(funcName, args);
    }

    // Save current variable scope
    const savedVariables = { ...this.interpreter.variables };

    // Create new scope with function parameters
    const funcScope = { ...this.interpreter.variables };
    for (let i = 0; i < func.params.length; i++) {
      funcScope[func.params[i]] = args[i];
    }
    this.interpreter.variables = funcScope;

    // Track call stack
    this.interpreter.callStack.push({ function: funcName, line: func.line });

    try {
      // Execute function body
      this.interpreter.executeBlock(func.body, 0);

      // Pop call stack
      this.interpreter.callStack.pop();

      // Restore variable scope
      this.interpreter.variables = savedVariables;

      return undefined;
    } catch (e) {
      // Handle return statement
      if (e.type === 'return') {
        this.interpreter.callStack.pop();
        this.interpreter.variables = savedVariables;
        return e.value;
      }
      // Re-throw other errors
      throw e;
    }
  }

  /**
   * Call an async function (cascade)
   */
  async callAsyncFunction(funcName, args) {
    const func = this.interpreter.functions[funcName];

    // Save current variable scope
    const savedVariables = { ...this.interpreter.variables };

    // Create new scope with function parameters
    const funcScope = { ...this.interpreter.variables };
    for (let i = 0; i < func.params.length; i++) {
      funcScope[func.params[i]] = args[i];
    }
    this.interpreter.variables = funcScope;

    // Track call stack
    this.interpreter.callStack.push({ function: funcName, line: func.line });

    try {
      // Execute function body asynchronously
      await this.interpreter.executeBlockAsync(func.body, 0);

      // Pop call stack
      this.interpreter.callStack.pop();

      // Restore variable scope
      this.interpreter.variables = savedVariables;

      return undefined;
    } catch (e) {
      // Handle return statement
      if (e.type === 'return') {
        this.interpreter.callStack.pop();
        this.interpreter.variables = savedVariables;
        return e.value;
      }
      // Re-throw other errors
      throw e;
    }
  }

  /**
   * Execute a block of code asynchronously
   */
  async executeBlockAsync(lines, startIndex) {
    let i = startIndex;

    while (i < lines.length) {
      const line = lines[i].trim();

      // Skip empty lines and comments
      if (!line || line.startsWith('//')) {
        i++;
        continue;
      }

      // Handle await keyword
      if (line.startsWith('await ')) {
        const expr = line.substring(6).trim();
        const result = await this.evaluateExpressionAsync(expr);
        i++;
        continue;
      }

      // Handle variable assignment with await
      if (line.startsWith('drink ') && line.includes('await ')) {
        const match = line.match(/drink\s+(\w+)\s*=\s*await\s+(.+)/);
        if (match) {
          const varName = match[1];
          const expr = match[2];
          const value = await this.evaluateExpressionAsync(expr);
          this.interpreter.variables[varName] = value;
          i++;
          continue;
        }
      }

      // For other statements, execute normally
      if (line.startsWith('thirsty ')) {
        i = this.interpreter.handleThirsty(lines, i);
      } else if (line.startsWith('refill ')) {
        i = this.interpreter.handleRefill(lines, i);
      } else if (line.startsWith('return ')) {
        const value = await this.evaluateExpressionAsync(line.substring(7).trim());
        throw { type: 'return', value: value };
      } else if (line === 'return') {
        throw { type: 'return', value: undefined };
      } else if (line === '}') {
        return i + 1;
      } else {
        this.interpreter.executeLine(line);
        i++;
      }
    }

    return i;
  }

  /**
   * Evaluate an expression asynchronously (for await)
   */
  async evaluateExpressionAsync(expr) {
    expr = expr.trim();

    // Check if it's a function call
    const funcCallMatch = expr.match(/^(\w+)\s*\(([^)]*)\)$/);
    if (funcCallMatch) {
      const funcName = funcCallMatch[1];
      const argsStr = funcCallMatch[2].trim();
      const args = argsStr ? this.interpreter.parseArguments(argsStr) : [];
      const evaluatedArgs = args.map(arg => this.interpreter.evaluateExpression(arg));

      // If it's an async function, await it
      if (this.interpreter.asyncFunctions.has(funcName)) {
        return await this.callAsyncFunction(funcName, evaluatedArgs);
      }

      // Otherwise call normally
      const result = this.callFunction(funcName, evaluatedArgs);

      // If result is a promise, await it
      if (result && typeof result.then === 'function') {
        return await result;
      }

      return result;
    }

    // Check if it's a method call (e.g., Http.get(...))
    const methodCallMatch = expr.match(/^(\w+)\.(\w+)\s*\(([^)]*)\)$/);
    if (methodCallMatch) {
      const objName = methodCallMatch[1];
      const methodName = methodCallMatch[2];
      const argsStr = methodCallMatch[3].trim();
      const args = argsStr ? this.interpreter.parseArguments(argsStr) : [];
      const evaluatedArgs = args.map(arg => this.interpreter.evaluateExpression(arg));

      if (this.interpreter.variables.hasOwnProperty(objName)) {
        const obj = this.interpreter.variables[objName];
        if (obj && typeof obj === 'object' && obj[methodName]) {
          const result = obj[methodName](...evaluatedArgs);

          // If result is a promise, await it
          if (result && typeof result.then === 'function') {
            return await result;
          }

          return result;
        }
      }
    }

    // For other expressions, evaluate synchronously
    return this.interpreter.evaluateExpression(expr);
  }
}

module.exports = { ClassFunctionHandlers };
