'use strict';

/**
 * Thirsty-Lang Tree-Walking Interpreter
 * Matching Python interpreter.py with hybrid governance support
 */

const ast = require('./ast');

// ─── Signals ──────────────────────────────────────────────────────────────────

class ReturnSignal {
  constructor(value) { this.value = value; }
}

class TailCallSignal {
  constructor(fn, args) { this.fn = fn; this.args = args; }
}

class ThrownSignal {
  constructor(value) { this.value = value; }
}

class RuntimeFault extends Error {
  constructor(code, message, span) {
    super(message);
    this.code = code;
    this.thirstySpan = span;
  }
}

class ThirstyGovernanceError extends Error {
  constructor(message) {
    super(message);
    this.code = 'THIRSTY-E050';
  }
}

// ─── Environment ──────────────────────────────────────────────────────────────

class Env {
  constructor(parent = null) {
    this.parent = parent;
    this.values = Object.create(null);
    this.mutable = Object.create(null);
    this.types = Object.create(null);
  }

  define(name, value, mutable = false, typeName = null) {
    this.values[name] = value;
    this.mutable[name] = mutable;
    if (typeName) this.types[name] = typeName;
  }

  assign(name, value) {
    if (name in this.values) {
      if (!this.mutable[name]) {
        throw new RuntimeFault('THIRSTY-E020', `cannot assign to immutable binding '${name}'`, null);
      }
      this.values[name] = value;
      return;
    }
    if (this.parent) {
      this.parent.assign(name, value);
      return;
    }
    throw new RuntimeFault('THIRSTY-E011', `unknown binding '${name}'`, null);
  }

  get(name) {
    if (name in this.values) return this.values[name];
    if (this.parent) return this.parent.get(name);
    throw new RuntimeFault('THIRSTY-E011', `unknown binding '${name}'`, null);
  }
}

// ─── Task (async wrapper) ─────────────────────────────────────────────────────

class TaskValue {
  constructor(value) {
    // In the JS runtime, async functions run synchronously and wrap their result.
    // This allows `await task` to work without real async infrastructure.
    this._resolved = value;
    this._done = true;
    this._error = null;
  }

  get value() {
    if (this._error) throw this._error;
    return this._resolved;
  }

  get done() {
    return this._done;
  }

  awaitValue() {
    if (this._error) return Promise.reject(this._error);
    return Promise.resolve(this._resolved);
  }
}

// ─── Runtime values ───────────────────────────────────────────────────────────

class UserFunction {
  constructor(decl, closure, interpreter, boundThis = null) {
    this.decl = decl;
    this.closure = closure;
    this.interpreter = interpreter;
    this.boundThis = boundThis;
  }

  bind(instance) {
    return new UserFunction(this.decl, this.closure, this.interpreter, instance);
  }

  call(args) {
    return this.interpreter.callFunction(this, args);
  }
}

class UserClass {
  constructor(name, fields, methods) {
    this.name = name;
    this.fields = fields; // {name: defaultValue}
    this.methods = methods; // {name: UserFunction}
  }

  instantiate(interpreter, args) {
    const inst = new UserInstance(this, Object.assign({}, this.fields));
    if ('init' in this.methods) {
      this.methods['init'].bind(inst).call(args);
    }
    return inst;
  }
}

class UserInstance {
  constructor(cls, fields) {
    this.cls = cls;
    this.fields = fields;
  }

  get(name) {
    if (name in this.fields) return this.fields[name];
    if (name in this.cls.methods) return this.cls.methods[name].bind(this);
    throw new RuntimeFault('THIRSTY-E011', `unknown property '${name}' on ${this.cls.name}`, null);
  }

  set(name, value) {
    this.fields[name] = value;
  }
}

class ModuleValue {
  constructor(name, members) {
    this.name = name;
    this.members = members;
  }
}

// ─── Module implementations ───────────────────────────────────────────────────

function buildBuiltinModules() {
  // thirst::time
  const timeModule = new ModuleValue('thirst::time', {
    now: () => Math.floor(Date.now() / 1000),
    epoch_ms: () => Date.now(),
    format: (ts, fmt) => {
      const d = new Date(ts * 1000);
      return fmt
        .replace('%Y', d.getFullYear())
        .replace('%m', String(d.getMonth() + 1).padStart(2, '0'))
        .replace('%d', String(d.getDate()).padStart(2, '0'))
        .replace('%H', String(d.getHours()).padStart(2, '0'))
        .replace('%M', String(d.getMinutes()).padStart(2, '0'))
        .replace('%S', String(d.getSeconds()).padStart(2, '0'));
    },
    sleep: (ms) => {
      const end = Date.now() + ms;
      while (Date.now() < end) { /* busy wait — not ideal but sync */ }
    },
    parse: (s) => Math.floor(new Date(s).getTime() / 1000),
  });

  // thirst::crypto
  let sha256Fn;
  try {
    const crypto = require('crypto');
    sha256Fn = (text) => crypto.createHash('sha256').update(String(text), 'utf8').digest('hex');
  } catch (_) {
    sha256Fn = (text) => {
      // djb2 fallback hash (not cryptographic, just for compatibility)
      let h = 5381;
      for (let i = 0; i < text.length; i++) h = (h * 33) ^ text.charCodeAt(i);
      return (h >>> 0).toString(16).padStart(8, '0').repeat(8).slice(0, 64);
    };
  }
  let randomBytesFn, uuidFn, hmacFn;
  try {
    const crypto = require('crypto');
    randomBytesFn = (n) => crypto.randomBytes(n).toString('hex');
    uuidFn = () => crypto.randomUUID ? crypto.randomUUID() : crypto.randomBytes(16).toString('hex').replace(/(.{8})(.{4})(.{4})(.{4})(.{12})/, '$1-$2-$3-$4-$5');
    hmacFn = (key, text) => crypto.createHmac('sha256', String(key)).update(String(text), 'utf8').digest('hex');
  } catch (_) {
    randomBytesFn = (n) => Array.from({ length: n }, () => Math.floor(Math.random() * 256).toString(16).padStart(2, '0')).join('');
    uuidFn = () => 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
      const r = Math.random() * 16 | 0;
      return (c === 'x' ? r : (r & 0x3 | 0x8)).toString(16);
    });
    hmacFn = (key, text) => sha256Fn(key + text);
  }
  const cryptoModule = new ModuleValue('thirst::crypto', {
    sha256: sha256Fn,
    sign: (text) => 'signed:' + sha256Fn(String(text)).slice(0, 16),
    hmac: hmacFn,
    random_bytes: randomBytesFn,
    uuid4: uuidFn,
  });

  // thirst::json
  const jsonModule = new ModuleValue('thirst::json', {
    parse: (s) => JSON.parse(String(s)),
    stringify: (v) => JSON.stringify(v),
    get: (obj, key) => (obj && typeof obj === 'object') ? obj[String(key)] : null,
    set: (obj, key, val) => { if (obj && typeof obj === 'object') obj[String(key)] = val; return obj; },
  });

  // thirst::log
  const logModule = new ModuleValue('thirst::log', {
    info: (msg) => console.log(`[thirst:info] ${msg}`),
    warn: (msg) => console.warn(`[thirst:warn] ${msg}`),
    error: (msg) => console.error(`[thirst:error] ${msg}`),
    debug: (msg) => console.debug(`[thirst:debug] ${msg}`),
  });

  // thirst::test
  class TestError extends Error {
    constructor(msg) { super(msg); this.name = 'TestError'; }
  }
  const testModule = new ModuleValue('thirst::test', {
    assert_eq: (a, b) => { if (!deepEqual(a, b)) throw new TestError(`assert_eq failed: ${stringify(a)} != ${stringify(b)}`); },
    assert_ne: (a, b) => { if (deepEqual(a, b)) throw new TestError(`assert_ne failed: ${stringify(a)} == ${stringify(b)}`); },
    assert_true: (v) => { if (!v) throw new TestError(`assert_true failed: ${stringify(v)} is falsy`); },
    assert_raises: (fn) => {
      try { callAny(fn, []); } catch (_) { return; }
      throw new TestError('assert_raises: no exception was raised');
    },
    describe: (name) => console.log(`  describe: ${name}`),
    it: (name, fn) => { callAny(fn, []); console.log(`    ok ${name}`); },
  });

  // thirst::collections
  const collectionsModule = new ModuleValue('thirst::collections', {
    map: (xs, fn) => xs.map(x => callAny(fn, [x])),
    filter: (xs, fn) => xs.filter(x => callAny(fn, [x])),
    reduce: (xs, seed, fn) => xs.reduce((acc, x) => callAny(fn, [acc, x]), seed),
    sort: (xs) => [...xs].sort((a, b) => (a < b ? -1 : a > b ? 1 : 0)),
    unique: (xs) => [...new Set(xs)],
    flatten: (xs) => xs.reduce((acc, x) => acc.concat(Array.isArray(x) ? x : [x]), []),
    zip: (xs, ys) => xs.map((x, i) => [x, ys[i]]),
  });

  // thirst::reservoir
  const reservoirModule = new ModuleValue('thirst::reservoir', {
    size: (items) => items.length,
    push: (items, value) => { items.push(value); return null; },
    pop: (items) => items.pop(),
    get: (items, idx) => items[idx],
    flood: (items, payload) => {
      if (Array.isArray(payload)) items.push(...payload);
      else items.push(payload);
      return items;
    },
  });

  // thirst::env
  const envModule = new ModuleValue('thirst::env', {
    get: (key) => process.env[String(key)] || null,
    set: (key, val) => { process.env[String(key)] = String(val); },
    all: () => Object.assign({}, process.env),
  });

  // thirst::process
  const processModule = new ModuleValue('thirst::process', {
    run: (cmd) => {
      try {
        const { execSync } = require('child_process');
        const result = execSync(Array.isArray(cmd) ? cmd.join(' ') : String(cmd), { encoding: 'utf8' });
        return { stdout: result, stderr: '', code: 0 };
      } catch (e) {
        return { stdout: e.stdout || '', stderr: e.stderr || '', code: e.status || 1 };
      }
    },
    exit: (code) => process.exit(Number(code)),
    args: () => process.argv.slice(2),
    pid: () => process.pid,
  });

  // thirst::fs
  let fsModule;
  try {
    const fs = require('fs');
    const path = require('path');
    fsModule = new ModuleValue('thirst::fs', {
      read_file: (p) => fs.readFileSync(String(p), 'utf8'),
      write_file: (p, t) => { fs.writeFileSync(String(p), String(t), 'utf8'); },
      exists: (p) => fs.existsSync(String(p)),
      list_dir: (p) => fs.readdirSync(String(p)),
      mkdir: (p) => fs.mkdirSync(String(p), { recursive: true }),
      remove: (p) => {
        const stat = fs.statSync(String(p));
        if (stat.isDirectory()) {
          const { execSync } = require('child_process');
          execSync(`rmdir /s /q "${p}"`, { stdio: 'ignore' });
        } else {
          fs.unlinkSync(String(p));
        }
      },
    });
  } catch (_) {
    fsModule = new ModuleValue('thirst::fs', {
      read_file: () => { throw new Error('fs not available'); },
      write_file: () => { throw new Error('fs not available'); },
      exists: () => false,
      list_dir: () => [],
      mkdir: () => {},
      remove: () => {},
    });
  }

  // thirst::path
  let pathModule;
  try {
    const path = require('path');
    pathModule = new ModuleValue('thirst::path', {
      join: (a, b) => path.join(String(a), String(b)),
      dirname: (p) => path.dirname(String(p)),
      basename: (p) => path.basename(String(p)),
      extension: (p) => path.extname(String(p)),
      absolute: (p) => path.resolve(String(p)),
      relative: (p, base) => path.relative(String(base), String(p)),
    });
  } catch (_) {
    pathModule = new ModuleValue('thirst::path', {
      join: (a, b) => `${a}/${b}`,
      dirname: (p) => String(p).split('/').slice(0, -1).join('/'),
      basename: (p) => String(p).split('/').pop(),
      extension: (p) => { const parts = String(p).split('.'); return parts.length > 1 ? '.' + parts.pop() : ''; },
      absolute: (p) => p,
      relative: (p, _) => p,
    });
  }

  // thirst::http (async-compatible in Node.js)
  const httpModule = new ModuleValue('thirst::http', {
    get: (url) => {
      try {
        const https = require(String(url).startsWith('https') ? 'https' : 'http');
        return new Promise((resolve, reject) => {
          https.get(String(url), (res) => {
            let body = '';
            res.on('data', c => body += c);
            res.on('end', () => {
              try { resolve(JSON.parse(body)); } catch (_) { resolve(body); }
            });
          }).on('error', reject);
        });
      } catch (_) {
        return null;
      }
    },
    post: (url, body) => {
      try {
        const https = require(String(url).startsWith('https') ? 'https' : 'http');
        const data = typeof body === 'string' ? body : JSON.stringify(body);
        return new Promise((resolve, reject) => {
          const u = new URL(String(url));
          const opts = { hostname: u.hostname, port: u.port, path: u.pathname + u.search, method: 'POST', headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) } };
          const req = https.request(opts, (res) => {
            let b = '';
            res.on('data', c => b += c);
            res.on('end', () => { try { resolve(JSON.parse(b)); } catch (_) { resolve(b); } });
          });
          req.on('error', reject);
          req.write(data);
          req.end();
        });
      } catch (_) {
        return null;
      }
    },
    put: (url, body) => null,
    delete: (url) => null,
  });

  return {
    'thirst::time': timeModule,
    'thirst::crypto': cryptoModule,
    'thirst::json': jsonModule,
    'thirst::log': logModule,
    'thirst::test': testModule,
    'thirst::collections': collectionsModule,
    'thirst::reservoir': reservoirModule,
    'thirst::env': envModule,
    'thirst::process': processModule,
    'thirst::fs': fsModule,
    'thirst::path': pathModule,
    'thirst::http': httpModule,
  };
}

function callAny(callee, args) {
  if (callee instanceof UserFunction) {
    return callee.call(args);
  }
  if (typeof callee === 'function') {
    return callee(...args);
  }
  throw new RuntimeFault('THIRSTY-E031', 'expression is not callable', null);
}

function deepEqual(a, b) {
  if (a === b) return true;
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) return false;
    return a.every((x, i) => deepEqual(x, b[i]));
  }
  if (a && b && typeof a === 'object' && typeof b === 'object') {
    const ka = Object.keys(a), kb = Object.keys(b);
    if (ka.length !== kb.length) return false;
    return ka.every(k => deepEqual(a[k], b[k]));
  }
  return false;
}

function stringify(value) {
  if (value === null || value === undefined) return 'empty';
  if (value === true) return 'parched';
  if (value === false) return 'quenched';
  if (Array.isArray(value)) return '[' + value.map(stringify).join(', ') + ']';
  if (value instanceof UserInstance) return `<${value.cls.name}>`;
  if (value instanceof UserClass) return `<class:${value.name}>`;
  if (value instanceof UserFunction) return `<function:${value.decl.name}>`;
  if (value instanceof ModuleValue) return `<module:${value.name}>`;
  if (value instanceof TaskValue) return `<task>`;
  return String(value);
}

// ─── HTML sanitizer ───────────────────────────────────────────────────────────

function sanitizeHtml(str) {
  return String(str)
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/on\w+\s*=\s*["'][^"']*["']/gi, '')
    .replace(/javascript:/gi, '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// ─── Governance HTTP call ─────────────────────────────────────────────────────

async function checkGovernanceIntent(fnName, requiresAnnotations, ctx) {
  try {
    const http = require('http');
    const body = JSON.stringify({
      function: fnName,
      requires: requiresAnnotations,
      context: ctx,
    });
    return await new Promise((resolve) => {
      const req = http.request({
        hostname: 'localhost',
        port: 8001,
        path: '/intent',
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
        timeout: 2000,
      }, (res) => {
        let data = '';
        res.on('data', c => data += c);
        res.on('end', () => {
          try {
            const result = JSON.parse(data);
            resolve(result);
          } catch (_) {
            resolve({ decision: 'ALLOW' });
          }
        });
      });
      req.on('error', () => resolve({ decision: 'ALLOW' }));
      req.on('timeout', () => { req.destroy(); resolve({ decision: 'ALLOW' }); });
      req.write(body);
      req.end();
    });
  } catch (_) {
    return { decision: 'ALLOW' };
  }
}

// ─── Interpreter ─────────────────────────────────────────────────────────────

class Interpreter {
  constructor(options = {}) {
    this.globals = new Env();
    this.output = [];
    this.inputProvider = options.inputProvider || (() => '');
    this.trace = options.trace || false;
    this.thirstLevel = options.thirstLevel || 1;
    this.recursionLimit = options.recursionLimit || 256;
    this.callDepth = 0;
    this.currentFile = options.currentFile || '<memory>';
    this.moduleCache = {};
    this.moduleName = null;
    this.executionMode = 'core';
    this.governanceContext = options.governanceContext || {};
    this.achievements = new Set();
    this._installBuiltins();
    this._installModules();
  }

  _installBuiltins() {
    const g = this.globals;
    g.define('length', (s) => (typeof s === 'string' ? s.length : (Array.isArray(s) ? s.length : 0)));
    g.define('contains', (s, n) => {
      if (typeof s === 'string') return s.includes(n);
      if (Array.isArray(s)) return s.includes(n);
      return false;
    });
    g.define('split', (s, sep) => String(s).split(String(sep)));
    g.define('abs', (x) => Math.abs(x));
    g.define('min', (a, b) => Math.min(a, b));
    g.define('max', (a, b) => Math.max(a, b));
    g.define('push', (items, value) => { items.push(value); return null; });
    g.define('pop', (items) => items.pop());
    g.define('size', (items) => {
      if (typeof items === 'string') return items.length;
      if (Array.isArray(items)) return items.length;
      if (items && typeof items === 'object') return Object.keys(items).length;
      return 0;
    });
    g.define('get', (items, index) => items[index]);
    g.define('flood', (items, payload) => {
      if (Array.isArray(payload)) items.push(...payload);
      else items.push(payload);
      return items;
    });
    g.define('condense', (value) => {
      if (value === null || value === undefined) {
        throw new RuntimeFault('THIRSTY-E901', 'cannot condense an empty spring', null);
      }
      return value;
    });
    g.define('evaporate', (value) => null);
    g.define('strain', (items, fn) => items.filter(x => callAny(fn, [x])));
    g.define('transmute', (items, fn) => items.map(x => callAny(fn, [x])));
    g.define('distill', (items, seed, fn) => items.reduce((acc, x) => callAny(fn, [acc, x]), seed));

    // Security builtins
    g.define('__sanitize__', (x) => sanitizeHtml(x));
    g.define('__armor__', (x) => {
      if (x && typeof x === 'object') return Object.freeze(Object.assign({}, x));
      return x;
    });
    g.define('__morph__', (x) => x); // identity - morphing is host-specific
    g.define('__detect__', (x) => x); // execute and return
    g.define('__defend__', (x) => {
      if (!x) throw new RuntimeFault('THIRSTY-E901', 'defend assertion failed', null);
      return null;
    });
    g.define('__shield__', (block) => {
      // block is an ast.BlockStmt — evaluated in the interpreter
      return block;
    });
  }

  _installModules() {
    const mods = buildBuiltinModules();
    for (const [name, mod] of Object.entries(mods)) {
      this.moduleCache[name] = mod;
    }
  }

  run(program, callMain = true) {
    this.currentFile = program.span.file;
    this.moduleName = program.header ? program.header.name : null;
    this.executionMode = program.header ? program.header.mode : 'core';

    // Pass 1: imports
    for (const decl of program.declarations) {
      if (decl instanceof ast.ImportDecl) {
        const alias = decl.alias || (decl.module.split('::').pop().split('/').pop().split('.')[0]);
        const mod = this._loadModule(decl.module);
        this.globals.define(alias, mod, false, `Module:${decl.module}`);
      }
    }
    // Pass 2: functions
    for (const decl of program.declarations) {
      if (decl instanceof ast.FunctionDecl || decl instanceof ast.GovernedFunctionDecl) {
        this.globals.define(decl.name, new UserFunction(decl, this.globals, this), false, 'Function');
      }
    }
    // Pass 3: classes, enums, structs, interfaces
    for (const decl of program.declarations) {
      if (decl instanceof ast.ClassDecl) {
        this.globals.define(decl.name, this._buildClass(decl), false, decl.name);
      } else if (decl instanceof ast.EnumDecl) {
        const ns = {};
        for (const v of decl.variants) ns[v] = v;
        this.globals.define(decl.name, ns, false, decl.name);
      } else if (decl instanceof ast.StructDecl) {
        const fieldNames = decl.fields.map(f => f.name);
        const ctor = (...args) => {
          const obj = {};
          fieldNames.forEach((fn, i) => { obj[fn] = i < args.length ? args[i] : null; });
          return obj;
        };
        this.globals.define(decl.name, ctor, false, decl.name);
      } else if (decl instanceof ast.InterfaceDecl) {
        this.globals.define(decl.name, null, false, decl.name);
      }
    }
    // Pass 4: top-level statements
    for (const decl of program.declarations) {
      if (decl instanceof ast.FunctionDecl || decl instanceof ast.GovernedFunctionDecl ||
          decl instanceof ast.ClassDecl || decl instanceof ast.ImportDecl ||
          decl instanceof ast.EnumDecl || decl instanceof ast.StructDecl ||
          decl instanceof ast.InterfaceDecl) {
        continue;
      }
      this._exec(decl, this.globals);
    }
    // Call main if present
    if (callMain && 'main' in this.globals.values) {
      const main = this.globals.values['main'];
      if (typeof main === 'function' || main instanceof UserFunction) {
        callAny(main, []);
      }
    }
    if (this.output.includes('thirsty')) {
      this.achievements.add('sacred_echo');
    }
    return this.output;
  }

  _loadModule(moduleSpec) {
    if (moduleSpec in this.moduleCache) {
      return this.moduleCache[moduleSpec];
    }
    if (moduleSpec.startsWith('thirst::')) {
      throw new RuntimeFault('THIRSTY-E011', `unknown builtin module '${moduleSpec}'`, null);
    }
    // Try to load file-based module
    try {
      const fs = require('fs');
      const path = require('path');
      const { Lexer } = require('./lexer');
      const { Parser } = require('./parser');
      let filePath;
      if (moduleSpec.startsWith('./') || moduleSpec.startsWith('../')) {
        filePath = path.resolve(path.dirname(this.currentFile), moduleSpec);
        if (!filePath.endsWith('.thirsty')) filePath += '.thirsty';
      } else {
        throw new Error('cannot resolve non-relative module');
      }
      const source = fs.readFileSync(filePath, 'utf8');
      const tokens = new Lexer(source, filePath).lex();
      const prog = new Parser(tokens).parseProgram();
      const child = new Interpreter({ currentFile: filePath });
      child.run(prog, false);
      const exports = {};
      for (const [k, v] of Object.entries(child.globals.values)) {
        if (!k.startsWith('_')) exports[k] = v;
      }
      const mod = new ModuleValue(moduleSpec, exports);
      this.moduleCache[moduleSpec] = mod;
      return mod;
    } catch (e) {
      throw new RuntimeFault('THIRSTY-E011', `cannot load module '${moduleSpec}': ${e.message}`, null);
    }
  }

  _buildClass(decl) {
    const fields = {};
    const methods = {};
    for (const member of decl.members) {
      if (member instanceof ast.VarDecl) {
        fields[member.name] = null;
      } else if (member instanceof ast.FunctionDecl || member instanceof ast.GovernedFunctionDecl) {
        methods[member.name] = new UserFunction(member, this.globals, this);
      }
    }
    return new UserClass(decl.name, fields, methods);
  }

  callFunction(fn, args) {
    if (fn.decl.isAsync) {
      // Run body synchronously so await can access the result immediately.
      // Governance check for governed async functions.
      if (this.executionMode === 'governed' && fn.decl instanceof ast.GovernedFunctionDecl && fn.decl.requires.length > 0) {
        this._enforceGovernanceSync(fn);
      }
      try {
        const result = this._runFnBody(fn, args);
        return new TaskValue(result);
      } catch (e) {
        // Wrap error in a rejected-like TaskValue (value stays undefined)
        const tv = new TaskValue(null);
        tv._error = e;
        return tv;
      }
    }

    // Governance check for sync governed functions
    if (this.executionMode === 'governed' && fn.decl instanceof ast.GovernedFunctionDecl && fn.decl.requires.length > 0) {
      this._enforceGovernanceSync(fn);
    }

    this.callDepth++;
    if (this.callDepth > this.recursionLimit) {
      this.callDepth--;
      throw new RuntimeFault('THIRSTY-E900', 'your recursion has run dry', fn.decl.span);
    }
    try {
      return this._runFnBody(fn, args);
    } finally {
      this.callDepth--;
    }
  }

  _enforceGovernanceSync(fn) {
    const ctxAc = this.governanceContext.authority_class || 'AC0';
    for (const clause of fn.decl.requires) {
      const ann = clause.annotation.trim();
      if (ann.startsWith('AuthorityClass.')) {
        const required = ann.split('.').pop();
        if (ctxAc < required) {
          throw new RuntimeFault('THIRSTY-E050',
            `governed function '${fn.decl.name}' requires ${ann} but caller has ${ctxAc}`,
            fn.decl.span);
        }
      }
    }
  }

  _runFnBody(fn, args) {
    let currentFn = fn;
    let currentArgs = [...args];
    while (true) {
      const env = new Env(currentFn.closure);
      if (currentFn.boundThis !== null) {
        env.define('this', currentFn.boundThis, true, currentFn.boundThis.cls.name);
      }
      const params = currentFn.decl.params;
      for (let i = 0; i < params.length; i++) {
        env.define(params[i].name, currentArgs[i] !== undefined ? currentArgs[i] : null, false, 'param');
      }
      try {
        this._exec(currentFn.decl.body, env);
        return null;
      } catch (e) {
        if (e instanceof TailCallSignal) {
          currentFn = e.fn;
          currentArgs = e.args;
          continue;
        }
        if (e instanceof ReturnSignal) {
          return e.value;
        }
        throw e;
      }
    }
  }

  _callAny(callee, args) {
    if (callee instanceof UserFunction) return callee.call(args);
    if (typeof callee === 'function') return callee(...args);
    throw new RuntimeFault('THIRSTY-E031', 'expression is not callable', null);
  }

  _exec(stmt, env) {
    if (stmt instanceof ast.ImportDecl) return;
    if (stmt instanceof ast.VarDecl) {
      const value = this._eval(stmt.initializer, env);
      env.define(stmt.name, value, stmt.mutable && !stmt.isField, stmt.typeNode && stmt.typeNode.name || 'Value');
      return;
    }
    if (stmt instanceof ast.FunctionDecl || stmt instanceof ast.GovernedFunctionDecl) {
      if (!(stmt.name in env.values)) {
        env.define(stmt.name, new UserFunction(stmt, env, this), false, 'Function');
      }
      return;
    }
    if (stmt instanceof ast.ClassDecl) {
      if (!(stmt.name in env.values)) {
        env.define(stmt.name, this._buildClass(stmt), false, stmt.name);
      }
      return;
    }
    if (stmt instanceof ast.EnumDecl) {
      const ns = {};
      for (const v of stmt.variants) ns[v] = v;
      env.define(stmt.name, ns, false, stmt.name);
      return;
    }
    if (stmt instanceof ast.StructDecl) {
      const fieldNames = stmt.fields.map(f => f.name);
      env.define(stmt.name, (...args) => {
        const obj = {};
        fieldNames.forEach((fn, i) => { obj[fn] = i < args.length ? args[i] : null; });
        return obj;
      }, false, stmt.name);
      return;
    }
    if (stmt instanceof ast.InterfaceDecl) {
      env.define(stmt.name, null, false, stmt.name);
      return;
    }
    if (stmt instanceof ast.BlockStmt) {
      const blockEnv = new Env(env);
      for (const s of stmt.statements) {
        this._exec(s, blockEnv);
      }
      return;
    }
    if (stmt instanceof ast.PrintStmt) {
      try {
        const val = this._eval(stmt.expr, env);
        this.output.push(stringify(val));
      } catch (e) {
        if (!stmt.safe) throw e;
        this.output.push('empty');
      }
      return;
    }
    if (stmt instanceof ast.ExprStmt) {
      this._eval(stmt.expr, env);
      return;
    }
    if (stmt instanceof ast.ReturnStmt) {
      // Tail call optimization
      if (stmt.expr instanceof ast.CallExpr) {
        const callee = this._eval(stmt.expr.callee, env);
        const args = stmt.expr.args.map(a => this._eval(a, env));
        if (callee instanceof UserFunction) {
          throw new TailCallSignal(callee, args);
        }
      }
      const value = stmt.expr === null ? null : this._eval(stmt.expr, env);
      throw new ReturnSignal(value);
    }
    if (stmt instanceof ast.ThrowStmt) {
      throw new ThrownSignal(this._eval(stmt.expr, env));
    }
    if (stmt instanceof ast.DripStmt) {
      const current = env.get(stmt.name);
      const amt = stmt.amount === null ? 1 : this._eval(stmt.amount, env);
      env.assign(stmt.name, current + amt);
      return;
    }
    if (stmt instanceof ast.IfStmt) {
      const cond = this._eval(stmt.condition, env);
      if (cond) {
        this._exec(stmt.thenBranch, env);
      } else if (stmt.elseBranch) {
        this._exec(stmt.elseBranch, env);
      }
      return;
    }
    if (stmt instanceof ast.LoopStmt) {
      const count = this._eval(stmt.count, env);
      if (typeof count !== 'number' || !Number.isInteger(count)) {
        throw new RuntimeFault('THIRSTY-E023', 'loop count must evaluate to Int', stmt.count.span);
      }
      if (count < 0) {
        throw new RuntimeFault('THIRSTY-E023', 'loop count must be non-negative', stmt.count.span);
      }
      for (let i = 0; i < count; i++) {
        this._exec(stmt.body, env);
      }
      return;
    }
    if (stmt instanceof ast.TryStmt) {
      try {
        this._exec(stmt.tryBlock, env);
      } catch (e) {
        if (e instanceof ThrownSignal) {
          let handled = false;
          for (const catchClause of stmt.catches) {
            if (catchClause.typeName === 'Error' || this._matchCatch(catchClause.typeName, e.value)) {
              const catchEnv = new Env(env);
              catchEnv.define(catchClause.name, e.value, false, catchClause.typeName);
              this._exec(catchClause.block, catchEnv);
              handled = true;
              break;
            }
          }
          if (!handled) throw e;
        } else if (!(e instanceof ReturnSignal) && !(e instanceof TailCallSignal)) {
          // Catch native JS errors as Thirsty Error
          let handled = false;
          for (const catchClause of stmt.catches) {
            if (catchClause.typeName === 'Error') {
              const catchEnv = new Env(env);
              catchEnv.define(catchClause.name, e.message || String(e), false, 'Error');
              this._exec(catchClause.block, catchEnv);
              handled = true;
              break;
            }
          }
          if (!handled) throw e;
        } else {
          throw e;
        }
      } finally {
        if (stmt.finallyBlock) {
          this._exec(stmt.finallyBlock, env);
        }
      }
      return;
    }
    if (stmt instanceof ast.MutationDecl) {
      // Shadow mutation: run shadow, check invariant, run canonical
      const shadowEnv = new Env(env);
      this._exec(stmt.shadowBlock, shadowEnv);
      // invariant check: execute invariant block and verify no throw
      try {
        this._exec(stmt.invariantBlock, shadowEnv);
      } catch (e) {
        if (e instanceof ThrownSignal) {
          throw new RuntimeFault('THIRSTY-E901', `mutation '${stmt.name}' invariant violated`, stmt.span);
        }
        throw e;
      }
      // If invariant passed, run canonical
      this._exec(stmt.canonicalBlock, env);
      return;
    }
    // Unknown statement — silently ignore
  }

  _matchCatch(typeName, value) {
    if (value instanceof UserInstance) return value.cls.name === typeName;
    return typeName === (value && value.constructor && value.constructor.name);
  }

  _eval(expr, env) {
    if (expr instanceof ast.LiteralExpr) {
      return expr.value;
    }
    if (expr instanceof ast.VariableExpr) {
      return env.get(expr.name);
    }
    if (expr instanceof ast.ThisExpr) {
      return env.get('this');
    }
    if (expr instanceof ast.InputExpr) {
      try {
        const value = this.inputProvider();
        if (expr.safe && (value === '' || value === null || value === undefined)) return null;
        return value;
      } catch (e) {
        if (expr.safe) return null;
        throw e;
      }
    }
    if (expr instanceof ast.ArrayExpr) {
      return expr.items.map(x => this._eval(x, env));
    }
    if (expr instanceof ast.AssignExpr) {
      const value = this._eval(expr.value, env);
      if (expr.target instanceof ast.VariableExpr) {
        env.assign(expr.target.name, value);
        return value;
      }
      if (expr.target instanceof ast.MemberExpr) {
        const obj = this._eval(expr.target.obj, env);
        if (obj instanceof UserInstance) {
          obj.set(expr.target.name, value);
          return value;
        }
        if (obj && typeof obj === 'object') {
          obj[expr.target.name] = value;
          return value;
        }
        throw new RuntimeFault('THIRSTY-E021', 'member assignment expects object instance', expr.span);
      }
      if (expr.target instanceof ast.IndexExpr) {
        const items = this._eval(expr.target.obj, env);
        const idx = this._eval(expr.target.index, env);
        items[idx] = value;
        return value;
      }
      throw new RuntimeFault('THIRSTY-E001', 'invalid assignment target', expr.span);
    }
    if (expr instanceof ast.UnaryExpr) {
      const right = this._eval(expr.right, env);
      if (expr.op === '!') return !right;
      if (expr.op === '-') return -right;
      return right;
    }
    if (expr instanceof ast.BinaryExpr) {
      const left = this._eval(expr.left, env);
      const right = this._eval(expr.right, env);
      return this._applyBinary(expr.op, left, right, expr.span);
    }
    if (expr instanceof ast.PipeExpr) {
      const left = this._eval(expr.left, env);
      return this._evalPipe(left, expr.right, env);
    }
    if (expr instanceof ast.GuardExpr) {
      const cond = this._eval(expr.condition, env);
      if (cond) {
        return this._eval(expr.whenTrue, env);
      }
      if (expr.whenFalse) {
        return this._eval(expr.whenFalse, env);
      }
      return null;
    }
    if (expr instanceof ast.CallExpr) {
      // Handle security builtins that need special treatment
      if (expr.callee instanceof ast.VariableExpr && expr.callee.name === '__shield__') {
        // shield { block } — execute block and return result
        const blockArg = expr.args[0];
        if (blockArg instanceof ast.LiteralExpr && blockArg.value instanceof ast.BlockStmt) {
          try {
            this._exec(blockArg.value, env);
          } catch (e) {
            if (e instanceof ReturnSignal) return e.value;
          }
          return null;
        }
      }
      try {
        const callee = this._eval(expr.callee, env);
        const args = expr.args.map(a => this._eval(a, env));
        return this._callAny(callee, args);
      } catch (e) {
        if (expr.safe) return null;
        throw e;
      }
    }
    if (expr instanceof ast.MemberExpr) {
      const obj = this._eval(expr.obj, env);
      if (obj instanceof ModuleValue) {
        if (!(expr.name in obj.members)) {
          throw new RuntimeFault('THIRSTY-E021', `unknown module member '${expr.name}'`, expr.span);
        }
        return obj.members[expr.name];
      }
      if (obj instanceof UserInstance) return obj.get(expr.name);
      if (obj instanceof TaskValue && expr.name === 'value') return obj.value;
      if (obj && typeof obj === 'object' && !Array.isArray(obj)) {
        if (expr.name in obj) return obj[expr.name];
      }
      if (Array.isArray(obj)) {
        return this._listMember(obj, expr.name, env);
      }
      if (typeof obj === 'string') {
        if (expr.name === 'length') return obj.length;
      }
      throw new RuntimeFault('THIRSTY-E021', `cannot access member '${expr.name}'`, expr.span);
    }
    if (expr instanceof ast.IndexExpr) {
      const obj = this._eval(expr.obj, env);
      const idx = this._eval(expr.index, env);
      try {
        return obj[idx];
      } catch (e) {
        throw new RuntimeFault('THIRSTY-E100', `indexing failed: ${e.message}`, expr.span);
      }
    }
    if (expr instanceof ast.NewExpr) {
      const cls = env.get(expr.className);
      const args = expr.args.map(a => this._eval(a, env));
      if (cls instanceof UserClass) {
        return cls.instantiate(this, args);
      }
      if (typeof cls === 'function') {
        return cls(...args);
      }
      throw new RuntimeFault('THIRSTY-E011', `unknown class '${expr.className}'`, expr.span);
    }
    if (expr instanceof ast.AwaitExpr) {
      const value = this._eval(expr.expr, env);
      if (value instanceof TaskValue) {
        return value.value; // synchronous wait (already resolved or resolved value)
      }
      if (value && typeof value.then === 'function') {
        throw new RuntimeFault('THIRSTY-E021', 'use cascade glass for async functions', expr.span);
      }
      return value;
    }
    if (expr instanceof ast.CondenseExpr) {
      const value = this._eval(expr.expr, env);
      if (value === null || value === undefined) {
        throw new RuntimeFault('THIRSTY-E901', 'cannot condense an empty spring', expr.span);
      }
      return value;
    }
    if (expr instanceof ast.EvaporateExpr) {
      this._eval(expr.expr, env);
      return null;
    }
    throw new RuntimeFault('THIRSTY-E001', `unhandled expression type: ${expr.constructor.name}`, null);
  }

  _evalPipe(left, right, env) {
    if (right instanceof ast.VariableExpr) {
      const callee = this._eval(right, env);
      return this._callAny(callee, [left]);
    }
    if (right instanceof ast.CallExpr) {
      const callee = this._eval(right.callee, env);
      const args = [left, ...right.args.map(a => this._eval(a, env))];
      return this._callAny(callee, args);
    }
    throw new RuntimeFault('THIRSTY-E021', 'pipe expects callable target', right.span);
  }

  _listMember(items, name, env) {
    const interp = this;
    if (name === 'size') return () => items.length;
    if (name === 'push') return (value) => { items.push(value); return null; };
    if (name === 'get') return (index) => items[index];
    if (name === 'pop') return () => items.pop();
    if (name === 'flood') return (payload) => {
      if (Array.isArray(payload)) items.push(...payload);
      else items.push(payload);
      return items;
    };
    if (name === 'strain') return (fn) => items.filter(x => interp._callAny(fn, [x]));
    if (name === 'transmute') return (fn) => items.map(x => interp._callAny(fn, [x]));
    if (name === 'distill') return (seed, fn) => items.reduce((acc, x) => interp._callAny(fn, [acc, x]), seed);
    throw new RuntimeFault('THIRSTY-E021', `unknown reservoir method '${name}'`, null);
  }

  _applyBinary(op, left, right, span) {
    try {
      if (op === '+') return left + right;
      if (op === '-') return left - right;
      if (op === '*') return left * right;
      if (op === '/') {
        if (right === 0) throw new RuntimeFault('THIRSTY-E101', 'division by zero', span);
        return left / right;
      }
      if (op === '%') return left % right;
      if (op === '==') return left === right;
      if (op === '!=') return left !== right;
      if (op === '<') return left < right;
      if (op === '<=') return left <= right;
      if (op === '>') return left > right;
      if (op === '>=') return left >= right;
      if (op === '&&') return Boolean(left) && Boolean(right);
      if (op === '||') return Boolean(left) || Boolean(right);
    } catch (e) {
      if (e instanceof RuntimeFault) throw e;
      throw new RuntimeFault('THIRSTY-E021', `operator '${op}' failed: ${e.message}`, span);
    }
    throw new RuntimeFault('THIRSTY-E021', `unsupported operator '${op}'`, span);
  }
}

module.exports = {
  Interpreter, UserFunction, UserClass, UserInstance, ModuleValue, TaskValue,
  ReturnSignal, ThrownSignal, RuntimeFault, ThirstyGovernanceError, Env, stringify,
};
