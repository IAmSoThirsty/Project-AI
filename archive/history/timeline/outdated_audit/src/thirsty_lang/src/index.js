//                                           [2026-03-03 13:45]
//                                          Productivity: Active
#!/usr/bin/env node

/**
 * Thirsty-lang Interpreter - Sovereign Edition (UTF-v1.0)
 * Final Maturation | Priority-Safe Evaluation
 * 
 * Date: 2026-03-03 15:40 UTC | Status: Active
 */

class ThirstyInstance {
  constructor(className, members) {
    this.className = className;
    this.fields = { ...members.fields };
    this.methods = { ...members.methods };
  }
}

class ThirstyInterpreter {
  constructor() {
    this.variables = {};
    this.functions = {};
    this.classes = {};
    this.instances = [];
    this._thisContext = null;
  }

  get thisContext() { return this._thisContext; }
  set thisContext(val) { this._thisContext = val; }

  async execute(code) {
    const lines = code.split('\n').map(line => line.trim()).filter(line => line && !line.startsWith('//'));
    await this.executeBlock(lines);
  }

  async executeBlock(lines) {
    let i = 0;
    while (i < lines.length) {
      const line = lines[i];

      if (line === 'spillage') {
        let tryBody = []; i++;
        while (i < lines.length && !lines[i].startsWith('cleanup ')) { tryBody.push(lines[i]); i++; }
        const catchHeader = lines[i] || 'cleanup err'; i++;
        let catchBody = [];
        while (i < lines.length && !lines[i].startsWith('endcleanup')) { catchBody.push(lines[i]); i++; }
        try {
          await this.executeBlock(tryBody);
        } catch (err) {
          const varName = catchHeader.split(' ')[1] || 'err';
          this.variables[varName] = err.message;
          await this.executeBlock(catchBody);
        }
        i++; continue;
      }

      if (line.startsWith('thirsty ')) {
        const condMatch = line.match(/thirsty\s+(.+)/);
        if (condMatch) {
          const condition = condMatch[1];
          const bodyLine = lines[i + 1];
          if (this.evaluateCondition(condition)) await this.executeLine(bodyLine);
        }
        i += 2; continue;
      }

      if (line.startsWith('glass ') || line.startsWith('cascade glass ')) {
        const isAsync = line.startsWith('cascade ');
        const pattern = isAsync ? /cascade glass\s+(\w+)\(([^)]*)\)/ : /glass\s+(\w+)\(([^)]*)\)/;
        const fnMatch = line.match(pattern);
        if (fnMatch) {
          const fnName = fnMatch[1];
          const argList = fnMatch[2].split(',').map(a => a.trim()).filter(Boolean);
          let body = []; i++;
          while (i < lines.length && !lines[i].startsWith('endglass')) { body.push(lines[i]); i++; }
          this.functions[fnName] = { args: argList, body, isAsync };
        }
        i++; continue;
      }

      if (line.startsWith('fountain ')) {
        const className = line.match(/fountain\s+(\w+)/)[1];
        let members = { fields: {}, methods: {} };
        i++;
        while (i < lines.length && !lines[i].startsWith('endfountain')) {
          const cl = lines[i];
          if (cl.startsWith('drink ')) {
            const m = cl.match(/drink\s+(\w+)\s*=\s*(.+)/);
            if (m) members.fields[m[1]] = m[2].trim();
          } else if (cl.startsWith('glass ') || cl.startsWith('cascade glass ')) {
            const isAsync = cl.startsWith('cascade ');
            const pattern = isAsync ? /cascade glass\s+(\w+)\(([^)]*)\)/ : /glass\s+(\w+)\(([^)]*)\)/;
            const mMatch = cl.match(pattern);
            if (mMatch) {
              const mName = mMatch[1];
              const mArgs = mMatch[2].split(',').map(a => a.trim()).filter(Boolean);
              let mBody = []; i++;
              while (i < lines.length && !lines[i].startsWith('endglass')) { mBody.push(lines[i]); i++; }
              members.methods[mName] = { args: mArgs, body: mBody, isAsync };
            }
          }
          i++;
        }
        this.classes[className] = members;
        i++; continue;
      }

      if (line) await this.executeLine(line);
      i++;
    }
  }

  async callFunction(fnName, argVals) {
    const fn = this.functions[fnName];
    if (!fn) throw new Error(`Function not found: ${fnName}`);
    const oldVars = { ...this.variables };
    fn.args.forEach((name, idx) => { this.variables[name] = argVals[idx]; });
    await this.executeBlock(fn.body);
    this.variables = oldVars;
  }

  evaluateCondition(cond) {
    const match = cond.match(/(\w+)\s*(==|!=|>=|<=|>|<)\s*(.+)/);
    if (!match) throw new Error(`Invalid condition: ${cond}`);
    const varName = match[1];
    const op = match[2];
    let val = match[3];
    const left = this.variables[varName];
    if (!isNaN(val)) val = parseFloat(val);
    switch (op) {
      case '==': return left == val;
      case '!=': return left != val;
      case '>': return left > val;
      case '<': return left < val;
      case '>=': return left >= val;
      case '<=': return left <= val;
      default: return false;
    }
  }

  async executeLine(line) {
    if (line.startsWith('drink ')) await this.handleDrink(line);
    else if (line.startsWith('pour ')) await this.handlePour(line);
    else if (line.includes('(') && line.includes(')')) await this.evaluateExpression(line);
    else if (!line.includes('=')) { } // ignore
    else throw new Error(`Unknown statement: ${line}`);
  }

  async handleDrink(line) {
    const match = line.match(/drink\s+([\w.]+)\s*=\s*(.+)/);
    if (!match) return;
    const target = match[1];
    const val = await this.evaluateExpression(match[2]);
    if (target.startsWith('this.')) {
      if (this.thisContext) this.thisContext.fields[target.slice(5)] = val;
    } else if (target.includes('.')) {
      const parts = target.split('.');
      const obj = this.variables[parts[0]];
      if (obj instanceof ThirstyInstance) obj.fields[parts[1]] = val;
    } else {
      this.variables[target] = val;
    }
  }

  async handlePour(line) {
    console.log(await this.evaluateExpression(line.substring(5).trim()));
  }

  async evaluateExpression(expr) {
    if (!expr) return undefined;
    expr = expr.trim();

    // Priority 1: Strings
    if ((expr.startsWith('"') && expr.endsWith('"')) || (expr.startsWith("'") && expr.endsWith("'"))) {
      return expr.slice(1, -1);
    }

    // Priority 2: Numbers (Avoid dot confusion)
    if (!isNaN(expr) && expr !== "" && !expr.includes(' ')) return parseFloat(expr);

    // Priority 3: Await
    if (expr.startsWith('await ')) return await this.evaluateExpression(expr.slice(6));

    // Priority 4: Arithmetic
    if (/^[\d.+\-*/\s()]+$/.test(expr)) {
      try {
        const result = eval(expr.replace(/(\w+)/g, (m) => this.variables[m] || m));
        if (!isNaN(result)) return result;
      } catch { /* proceed */ }
    }

    // Priority 5: New Instance
    const newMatch = expr.match(/^new\s+(\w+)\((.*)\)$/);
    if (newMatch) {
      const className = newMatch[1];
      const args = newMatch[2] ? newMatch[2].split(',').map(a => a.trim()).filter(Boolean) : [];
      const argVals = await Promise.all(args.map(a => this.evaluateExpression(a)));
      const cls = this.classes[className];
      if (!cls) throw new Error(`Class not found: ${className}`);
      const instance = new ThirstyInstance(className, cls);
      for (const [k, e] of Object.entries(cls.fields)) instance.fields[k] = await this.evaluateExpression(e);
      if (cls.methods.init) {
        const oldThis = this.thisContext;
        this.thisContext = instance;
        await this.callMethod(instance, 'init', argVals);
        this.thisContext = oldThis;
      }
      return instance;
    }

    // Priority 6: Member Access
    if (expr.includes('.')) {
      const parts = expr.split('.');
      let current = (parts[0] === 'this') ? this.thisContext : this.variables[parts[0]];
      for (let j = 1; j < parts.length; j++) {
        if (!current) throw new Error(`Cannot read property '${parts[j]}' of undefined`);
        const part = parts[j].trim();
        const mCall = part.match(/^(\w+)\((.*)\)$/);
        if (mCall) {
          const mName = mCall[1];
          const mArgs = mCall[2] ? mCall[2].split(',').map(a => a.trim()).filter(Boolean) : [];
          const mArgVals = await Promise.all(mArgs.map(a => this.evaluateExpression(a)));
          if (current instanceof ThirstyInstance && current.methods[mName]) {
            const oldThis = this.thisContext;
            this.thisContext = current;
            const res = await this.callMethod(current, mName, mArgVals);
            this.thisContext = oldThis;
            return res;
          }
        } else {
          current = (current instanceof ThirstyInstance) ? current.fields[part] : current[part];
        }
      }
      return current;
    }

    // Priority 7: Function Calls
    const fnMatch = expr.match(/^(\w+)\((.*)\)$/);
    if (fnMatch && this.functions[fnMatch[1]]) {
      const args = fnMatch[2] ? fnMatch[2].split(',').map(a => a.trim()).filter(Boolean) : [];
      const argVals = await Promise.all(args.map(a => this.evaluateExpression(a)));
      return await this.callFunction(fnMatch[1], argVals);
    }

    // Priority 8: Variables
    if (Object.prototype.hasOwnProperty.call(this.variables, expr)) return this.variables[expr];

    throw new Error(`Unknown expression: ${expr}`);
  }

  async callMethod(instance, methodName, argVals) {
    const method = instance.methods[methodName];
    const oldVars = { ...this.variables };
    method.args.forEach((name, idx) => { this.variables[name] = argVals[idx]; });
    await this.executeBlock(method.body);
    this.variables = oldVars;
  }
}

module.exports = ThirstyInterpreter;
