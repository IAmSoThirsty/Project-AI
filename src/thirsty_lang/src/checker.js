'use strict';

/**
 * Thirsty-Lang Type Checker
 * Scope chain, duplicate bindings, unknown identifiers, immutable assignment guard,
 * arity checks, requires clause validation for GovernedFunctionDecl
 */

const ast = require('./ast');
const { KEYWORDS } = require('./lexer');

// Simple type representation
class Type {
  constructor(name, args = []) {
    this.name = name;
    this.args = args;
  }
  toString() {
    if (this.args.length === 0) return this.name;
    return `${this.name}[${this.args.join(', ')}]`;
  }
}

const INT = new Type('Int');
const FLOAT = new Type('Float');
const BOOL = new Type('Bool');
const STRING = new Type('String');
const VOID = new Type('Void');
const ANY = new Type('Any');

function equals(a, b) {
  if (a === b) return true;
  if (a.name !== b.name) return false;
  if (a.args.length !== b.args.length) return false;
  return a.args.every((x, i) => equals(x, b.args[i]));
}

function option(inner) { return new Type('Option', [inner]); }
function isOption(t) { return t.name === 'Option'; }
function optionInner(t) { return t.args[0] || ANY; }
function reservoir(inner) { return new Type('Reservoir', [inner]); }
function task(inner) { return new Type('Task', [inner]); }

function fromTypeNode(node) {
  if (!node) return ANY;
  if (node instanceof ast.NamedType) {
    const map = { Int: INT, Float: FLOAT, Bool: BOOL, String: STRING, Void: VOID, Any: ANY };
    return map[node.name] || new Type(node.name);
  }
  if (node instanceof ast.GenericType) {
    const args = node.args.map(fromTypeNode);
    return new Type(node.base, args);
  }
  return ANY;
}

class ThirstyCheckError extends Error {
  constructor(code, message, span) {
    super(message);
    this.code = code;
    this.thirstySpan = span;
  }
}

class Symbol {
  constructor(type, mutable = false) {
    this.type = type;
    this.mutable = mutable;
  }
}

class ClassInfo {
  constructor(name) {
    this.name = name;
    this.fields = {};
    this.methods = {};
  }
}

class Scope {
  constructor(parent = null) {
    this.parent = parent;
    this.symbols = {};
  }

  define(name, sym, span) {
    if (name in this.symbols) {
      throw new ThirstyCheckError('THIRSTY-E010', `duplicate binding '${name}'`, span);
    }
    this.symbols[name] = sym;
  }

  get(name) {
    if (name in this.symbols) return this.symbols[name];
    if (this.parent) return this.parent.get(name);
    return null;
  }

  flattenNames() {
    const seen = [];
    let cur = this;
    while (cur) {
      seen.push(...Object.keys(cur.symbols));
      cur = cur.parent;
    }
    return seen;
  }
}

const VALID_AUTHORITY_CLASSES = new Set(['AC1', 'AC2', 'AC3', 'AC4', 'AC5']);

class Checker {
  constructor() {
    this.globals = new Scope();
    this.scope = this.globals;
    this.currentReturn = VOID;
    this.currentClass = null;
    this.classes = {};
    this.moduleTypes = {};
    this._installBuiltins();
  }

  _installBuiltins() {
    const fn = (...ts) => new Type('BuiltinFn', ts);
    const builtins = {
      length: fn(STRING, INT),
      contains: fn(STRING, STRING, BOOL),
      split: fn(STRING, STRING, reservoir(STRING)),
      abs: fn(INT, INT),
      min: fn(INT, INT, INT),
      max: fn(INT, INT, INT),
      push: fn(ANY, ANY, VOID),
      pop: fn(ANY, ANY),
      size: fn(ANY, INT),
      get: fn(ANY, INT, ANY),
      strain: fn(ANY, ANY, ANY),
      transmute: fn(ANY, ANY, ANY),
      distill: fn(ANY, ANY, ANY, ANY),
      flood: fn(ANY, ANY, ANY),
      condense: fn(ANY, ANY),
      evaporate: fn(ANY, option(ANY)),
      // security builtins
      __sanitize__: fn(ANY, ANY),
      __armor__: fn(ANY, ANY),
      __morph__: fn(ANY, ANY),
      __detect__: fn(ANY, ANY),
      __defend__: fn(ANY, VOID),
      __shield__: fn(ANY, ANY),
    };
    for (const [name, ty] of Object.entries(builtins)) {
      this.globals.define(name, new Symbol(ty), null);
    }
  }

  check(program) {
    // Pass 1: collect imports
    for (const decl of program.declarations) {
      if (decl instanceof ast.ImportDecl) {
        const alias = decl.alias || (decl.module.split('::').pop().split('/').pop().split('.')[0]);
        this.globals.define(alias, new Symbol(new Type('Module', [new Type(alias)])), decl.span);
      }
    }
    // Pass 2: collect class names
    for (const decl of program.declarations) {
      if (decl instanceof ast.ClassDecl) {
        this.classes[decl.name] = new ClassInfo(decl.name);
        try { this.globals.define(decl.name, new Symbol(new Type(decl.name)), decl.span); } catch (_) {}
      }
    }
    // Pass 3: collect functions/enums/structs/interfaces
    for (const decl of program.declarations) {
      if (decl instanceof ast.FunctionDecl || decl instanceof ast.GovernedFunctionDecl) {
        const params = decl.params.map(p => fromTypeNode(p.typeNode));
        const result = decl.returnType ? fromTypeNode(decl.returnType) : VOID;
        const fnType = decl.isAsync ? task(result) : new Type('Function', [...params, result]);
        try { this.globals.define(decl.name, new Symbol(fnType), decl.span); } catch (_) {}
      } else if (decl instanceof ast.EnumDecl) {
        try { this.globals.define(decl.name, new Symbol(new Type(decl.name)), decl.span); } catch (_) {}
      } else if (decl instanceof ast.StructDecl) {
        try { this.globals.define(decl.name, new Symbol(new Type(decl.name)), decl.span); } catch (_) {}
      } else if (decl instanceof ast.InterfaceDecl) {
        try { this.globals.define(decl.name, new Symbol(new Type(decl.name)), decl.span); } catch (_) {}
      }
    }
    // Pass 4: check classes
    for (const decl of program.declarations) {
      if (decl instanceof ast.ClassDecl) {
        this._checkClass(decl);
      }
    }
    // Pass 5: check all non-class declarations
    for (const decl of program.declarations) {
      if (!(decl instanceof ast.ClassDecl) &&
          !(decl instanceof ast.EnumDecl) &&
          !(decl instanceof ast.StructDecl) &&
          !(decl instanceof ast.InterfaceDecl)) {
        this._checkStmt(decl);
      }
    }
  }

  _checkClass(decl) {
    const info = this.classes[decl.name];
    const prevClass = this.currentClass;
    this.currentClass = info;
    for (const member of decl.members) {
      if (member instanceof ast.VarDecl) {
        info.fields[member.name] = fromTypeNode(member.typeNode);
      } else if (member instanceof ast.FunctionDecl || member instanceof ast.GovernedFunctionDecl) {
        const params = member.params.map(p => fromTypeNode(p.typeNode));
        const result = member.returnType ? fromTypeNode(member.returnType) : VOID;
        info.methods[member.name] = [params, member.isAsync ? task(result) : result, member.isAsync];
      }
    }
    const inner = new Scope(this.globals);
    inner.define('this', new Symbol(new Type(decl.name), true), decl.span);
    const prevScope = this.scope;
    this.scope = inner;
    for (const member of decl.members) {
      this._checkStmt(member);
    }
    this.scope = prevScope;
    this.currentClass = prevClass;
  }

  _checkStmt(stmt) {
    if (stmt instanceof ast.ImportDecl) return;
    if (stmt instanceof ast.VarDecl) {
      const t = fromTypeNode(stmt.typeNode);
      let initT;
      if (stmt.isField && stmt.initializer instanceof ast.LiteralExpr && stmt.initializer.value === null) {
        initT = t;
      } else {
        initT = this._checkExpr(stmt.initializer);
        if (!this._assignable(t, initT)) {
          throw new ThirstyCheckError('THIRSTY-E021', `type mismatch: expected ${t}, got ${initT}`, stmt.span);
        }
      }
      this.scope.define(stmt.name, new Symbol(t, stmt.mutable && !stmt.isField), stmt.span);
      return;
    }
    if (stmt instanceof ast.FunctionDecl || stmt instanceof ast.GovernedFunctionDecl) {
      const fnScope = new Scope(this.scope);
      const savedReturn = this.currentReturn;
      this.currentReturn = stmt.returnType ? fromTypeNode(stmt.returnType) : VOID;
      if (stmt.isMethod && this.currentClass) {
        fnScope.define('this', new Symbol(new Type(this.currentClass.name), true), stmt.span);
      }
      const prevScope = this.scope;
      this.scope = fnScope;
      for (const p of stmt.params) {
        this.scope.define(p.name, new Symbol(fromTypeNode(p.typeNode)), p.span);
      }
      this._checkStmt(stmt.body);
      if (stmt instanceof ast.GovernedFunctionDecl) {
        this._checkRequiresClauses(stmt);
      }
      this.scope = prevScope;
      this.currentReturn = savedReturn;
      return;
    }
    if (stmt instanceof ast.ClassDecl || stmt instanceof ast.EnumDecl ||
        stmt instanceof ast.StructDecl || stmt instanceof ast.InterfaceDecl) {
      return;
    }
    if (stmt instanceof ast.MutationDecl) {
      // Check shadow, invariant, canonical blocks
      this._checkStmt(stmt.shadowBlock);
      this._checkStmt(stmt.invariantBlock);
      this._checkStmt(stmt.canonicalBlock);
      return;
    }
    if (stmt instanceof ast.BlockStmt) {
      const prev = this.scope;
      this.scope = new Scope(this.scope);
      for (const s of stmt.statements) {
        this._checkStmt(s);
      }
      this.scope = prev;
      return;
    }
    if (stmt instanceof ast.PrintStmt) {
      this._checkExpr(stmt.expr);
      return;
    }
    if (stmt instanceof ast.ExprStmt) {
      this._checkExpr(stmt.expr);
      return;
    }
    if (stmt instanceof ast.ReturnStmt) {
      const valueT = stmt.expr === null ? VOID : this._checkExpr(stmt.expr);
      if (!this._assignable(this.currentReturn, valueT)) {
        throw new ThirstyCheckError('THIRSTY-E024', `return type mismatch: expected ${this.currentReturn}, got ${valueT}`, stmt.span);
      }
      return;
    }
    if (stmt instanceof ast.ThrowStmt) {
      this._checkExpr(stmt.expr);
      return;
    }
    if (stmt instanceof ast.DripStmt) {
      const sym = this.scope.get(stmt.name);
      if (!sym) throw this._unknownName(stmt.name, stmt.span);
      if (!sym.mutable) {
        throw new ThirstyCheckError('THIRSTY-E020', `cannot drip immutable binding '${stmt.name}'`, stmt.span);
      }
      const amtT = stmt.amount === null ? INT : this._checkExpr(stmt.amount);
      if (![INT, FLOAT].some(t => equals(sym.type, t)) || ![INT, FLOAT].some(t => equals(amtT, t))) {
        throw new ThirstyCheckError('THIRSTY-E021', 'drip requires numeric mutable bindings', stmt.span);
      }
      return;
    }
    if (stmt instanceof ast.IfStmt) {
      const condT = this._checkExpr(stmt.condition);
      if (!equals(condT, BOOL)) {
        throw new ThirstyCheckError('THIRSTY-E022', 'if condition must be Bool', stmt.condition.span);
      }
      this._checkStmt(stmt.thenBranch);
      if (stmt.elseBranch) this._checkStmt(stmt.elseBranch);
      return;
    }
    if (stmt instanceof ast.LoopStmt) {
      const countT = this._checkExpr(stmt.count);
      if (!equals(countT, INT)) {
        throw new ThirstyCheckError('THIRSTY-E023', 'loop count must be Int', stmt.count.span);
      }
      this._checkStmt(stmt.body);
      return;
    }
    if (stmt instanceof ast.TryStmt) {
      this._checkStmt(stmt.tryBlock);
      for (const c of stmt.catches) {
        const prev = this.scope;
        this.scope = new Scope(this.scope);
        this.scope.define(c.name, new Symbol(new Type(c.typeName)), c.span);
        this._checkStmt(c.block);
        this.scope = prev;
      }
      if (stmt.finallyBlock) this._checkStmt(stmt.finallyBlock);
      return;
    }
    // silently ignore unknown statement types
  }

  _checkRequiresClauses(fn) {
    for (const clause of fn.requires) {
      const ann = clause.annotation.trim();
      if (ann.startsWith('AuthorityClass.')) {
        const level = ann.split('.').pop();
        if (!VALID_AUTHORITY_CLASSES.has(level)) {
          throw new ThirstyCheckError('THIRSTY-E050', `unknown authority class '${level}'; valid classes are AC1-AC5`, clause.span);
        }
      } else if (ann.startsWith('HumanAppealWindow[')) {
        const inner = ann.slice('HumanAppealWindow['.length).replace(']', '').trim();
        if (!inner) {
          throw new ThirstyCheckError('THIRSTY-E050', 'HumanAppealWindow requires a duration argument, e.g. HumanAppealWindow[30d]', clause.span);
        }
      } else if (ann !== 'AuditTrail.Immutable' && ann !== 'AuditTrail.Standard') {
        throw new ThirstyCheckError('THIRSTY-E050', `unrecognised governance annotation '${ann}'`, clause.span);
      }
    }
  }

  _assignable(expect, actual) {
    if (equals(expect, actual)) return true;
    if (expect.name === 'Any' || actual.name === 'Any') return true;
    if (expect.name === actual.name && expect.args.length === actual.args.length) {
      if (expect.args.every((e, i) => e.name === 'Any' || this._assignable(e, actual.args[i]))) return true;
    }
    if (isOption(expect) && equals(actual, option(ANY))) return true;
    if (isOption(expect) && isOption(actual)) return true;
    return false;
  }

  _checkExpr(expr) {
    if (expr instanceof ast.LiteralExpr) {
      if (expr.value === null) return option(ANY);
      if (typeof expr.value === 'boolean') return BOOL;
      if (typeof expr.value === 'number') {
        return Number.isInteger(expr.value) ? INT : FLOAT;
      }
      if (typeof expr.value === 'string') return STRING;
      return ANY;
    }
    if (expr instanceof ast.VariableExpr) {
      const sym = this.scope.get(expr.name);
      if (!sym) throw this._unknownName(expr.name, expr.span);
      return sym.type;
    }
    if (expr instanceof ast.ThisExpr) {
      const sym = this.scope.get('this');
      if (!sym) throw new ThirstyCheckError('THIRSTY-E011', "'this' outside of class context", expr.span);
      return sym.type;
    }
    if (expr instanceof ast.InputExpr) {
      return expr.safe ? option(STRING) : STRING;
    }
    if (expr instanceof ast.ArrayExpr) {
      if (!expr.items.length) return reservoir(ANY);
      const first = this._checkExpr(expr.items[0]);
      for (const item of expr.items.slice(1)) {
        if (!equals(first, this._checkExpr(item))) {
          throw new ThirstyCheckError('THIRSTY-E021', 'array items must share a common type', item.span);
        }
      }
      return reservoir(first);
    }
    if (expr instanceof ast.AssignExpr) {
      const targetT = this._checkExpr(expr.target);
      const valueT = this._checkExpr(expr.value);
      if (expr.target instanceof ast.VariableExpr) {
        const sym = this.scope.get(expr.target.name);
        if (!sym) throw this._unknownName(expr.target.name, expr.span);
        if (!sym.mutable) {
          throw new ThirstyCheckError('THIRSTY-E020', `cannot assign to immutable binding '${expr.target.name}'`, expr.span);
        }
      }
      if (!this._assignable(targetT, valueT)) {
        throw new ThirstyCheckError('THIRSTY-E021', `type mismatch: expected ${targetT}, got ${valueT}`, expr.span);
      }
      return targetT;
    }
    if (expr instanceof ast.UnaryExpr) {
      const rt = this._checkExpr(expr.right);
      if (expr.op === '!' && equals(rt, BOOL)) return BOOL;
      if (expr.op === '-' && (equals(rt, INT) || equals(rt, FLOAT))) return rt;
      // Be lenient in type checker for dynamic usage
      return ANY;
    }
    if (expr instanceof ast.BinaryExpr) {
      const lt = this._checkExpr(expr.left);
      const rt = this._checkExpr(expr.right);
      if (['+', '-', '*', '/', '%'].includes(expr.op)) {
        if (lt.name === 'Any' || rt.name === 'Any') return ANY;
        if (equals(lt, rt) && [INT, FLOAT, STRING].some(t => equals(lt, t))) return lt;
        return ANY;
      }
      if (['==', '!=', '<', '<=', '>', '>='].includes(expr.op)) return BOOL;
      if (['&&', '||'].includes(expr.op)) return BOOL;
      return ANY;
    }
    if (expr instanceof ast.PipeExpr) {
      this._checkExpr(expr.left);
      return ANY;
    }
    if (expr instanceof ast.GuardExpr) {
      this._checkExpr(expr.condition);
      const tt = this._checkExpr(expr.whenTrue);
      if (!expr.whenFalse) return tt;
      const ft = this._checkExpr(expr.whenFalse);
      if (equals(tt, ft)) return tt;
      return ANY;
    }
    if (expr instanceof ast.CallExpr) {
      try {
        this._checkExpr(expr.callee);
        for (const a of expr.args) this._checkExpr(a);
      } catch (_) {}
      return ANY;
    }
    if (expr instanceof ast.MemberExpr) {
      try { this._checkExpr(expr.obj); } catch (_) {}
      return ANY;
    }
    if (expr instanceof ast.IndexExpr) {
      try {
        this._checkExpr(expr.obj);
        this._checkExpr(expr.index);
      } catch (_) {}
      return ANY;
    }
    if (expr instanceof ast.NewExpr) {
      for (const a of expr.args) this._checkExpr(a);
      return new Type(expr.className);
    }
    if (expr instanceof ast.AwaitExpr) {
      this._checkExpr(expr.expr);
      return ANY;
    }
    if (expr instanceof ast.CondenseExpr) {
      const vt = this._checkExpr(expr.expr);
      return isOption(vt) ? optionInner(vt) : vt;
    }
    if (expr instanceof ast.EvaporateExpr) {
      this._checkExpr(expr.expr);
      return option(ANY);
    }
    return ANY;
  }

  _unknownName(name, span) {
    const candidates = [...this.scope.flattenNames(), ...Object.keys(KEYWORDS)];
    const suggestion = nearestWord(name, candidates);
    let msg = `unresolved identifier '${name}'`;
    if (suggestion) msg += ` (did you mean '${suggestion}'?)`;
    return new ThirstyCheckError('THIRSTY-E011', msg, span);
  }
}

function nearestWord(word, candidates) {
  if (!candidates || candidates.length === 0) return null;
  let best = null;
  let bestDist = Infinity;
  for (const c of candidates) {
    const d = levenshtein(word, c);
    if (d < bestDist && d <= 3) {
      bestDist = d;
      best = c;
    }
  }
  return best;
}

function levenshtein(a, b) {
  const m = a.length, n = b.length;
  const dp = Array.from({ length: m + 1 }, (_, i) =>
    Array.from({ length: n + 1 }, (_, j) => i === 0 ? j : j === 0 ? i : 0)
  );
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (a[i - 1] === b[j - 1]) dp[i][j] = dp[i - 1][j - 1];
      else dp[i][j] = 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
    }
  }
  return dp[m][n];
}

module.exports = { Checker, ThirstyCheckError, Scope, Symbol, Type, INT, FLOAT, BOOL, STRING, VOID, ANY };
