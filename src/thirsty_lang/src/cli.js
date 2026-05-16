#!/usr/bin/env node
'use strict';

/**
 * Thirsty-lang CLI
 * Command-line interface for the Thirsty-Lang interpreter
 *
 * Flags:
 *   --run <file>    Run a Thirsty program (default mode)
 *   --check <file>  Type-check only (no execution)
 *   --tokens <file> Lex only, print tokens as JSON
 *   --ast <file>    Parse only, print AST as JSON
 *   <file>          Shorthand for --run <file>
 */

const fs = require('fs');
const path = require('path');

// New AST-based pipeline
const { Lexer } = require('./lexer');
const { Parser } = require('./parser');
const { Checker } = require('./checker');
const { Interpreter, stringify } = require('./interpreter');

// Path validator (existing utility kept)
let validatePath, validateExtension, isValidFile;
try {
  const pv = require('./path-validator');
  validatePath = pv.validatePath;
  validateExtension = pv.validateExtension;
  isValidFile = pv.isValidFile;
} catch (_) {
  validatePath = (p) => path.resolve(p);
  validateExtension = (p, exts) => exts.some(e => p.endsWith(e));
  isValidFile = (p) => fs.existsSync(p) && fs.statSync(p).isFile();
}

function readSource(filePath) {
  const resolved = validatePath(filePath);
  if (!isValidFile(resolved)) {
    console.error(`Error: File '${filePath}' not found or is not a valid file`);
    process.exit(1);
  }
  return { source: fs.readFileSync(resolved, 'utf8'), resolved };
}

function lexSource(source, file) {
  const lexer = new Lexer(source, file);
  return lexer.lex();
}

function parseSource(source, file) {
  const tokens = lexSource(source, file);
  return new Parser(tokens).parseProgram();
}

function checkSource(source, file) {
  const program = parseSource(source, file);
  const checker = new Checker();
  checker.check(program);
  return program;
}

function runSource(source, file, opts = {}) {
  const tokens = lexSource(source, file);
  const program = new Parser(tokens).parseProgram();

  const interp = new Interpreter({
    currentFile: file,
    inputProvider: opts.inputProvider || (() => {
      // Synchronous readline for CLI
      try {
        const readline = require('readline-sync');
        return readline.question('');
      } catch (_) {
        return '';
      }
    }),
    trace: opts.trace || false,
    governanceContext: opts.governanceContext || {},
  });

  const output = interp.run(program, true);
  return { output, achievements: interp.achievements };
}

function cmdTokens(filePath) {
  const { source, resolved } = readSource(filePath);
  try {
    const tokens = lexSource(source, resolved);
    console.log(JSON.stringify(tokens.map(t => ({
      kind: t.kind,
      lexeme: t.lexeme,
      value: t.value,
      line: t.span.line,
      col: t.span.column,
    })), null, 2));
  } catch (err) {
    console.error(`Lex error: ${err.message}`);
    process.exit(1);
  }
}

function cmdAst(filePath) {
  const { source, resolved } = readSource(filePath);
  try {
    const program = parseSource(source, resolved);
    // Simple AST serializer — strip circular references
    function safeSerialize(obj, depth = 0) {
      if (depth > 30) return '[deep]';
      if (obj === null || obj === undefined) return obj;
      if (typeof obj !== 'object') return obj;
      if (Array.isArray(obj)) return obj.map(x => safeSerialize(x, depth + 1));
      const result = { _type: obj.constructor.name };
      for (const key of Object.keys(obj)) {
        if (key === 'span') continue; // omit spans for brevity
        result[key] = safeSerialize(obj[key], depth + 1);
      }
      return result;
    }
    console.log(JSON.stringify(safeSerialize(program), null, 2));
  } catch (err) {
    console.error(`Parse error: ${err.message}`);
    process.exit(1);
  }
}

function cmdCheck(filePath) {
  const { source, resolved } = readSource(filePath);
  try {
    checkSource(source, resolved);
    console.log(`ok: ${filePath}`);
  } catch (err) {
    if (err.errors) {
      for (const e of err.errors) {
        const span = e.thirstySpan;
        const loc = span ? `${span.file}:${span.line}:${span.column}` : '<unknown>';
        console.error(`${e.code || 'error'} at ${loc}: ${e.message}`);
      }
    } else {
      const span = err.thirstySpan;
      const loc = span ? `${span.file}:${span.line}:${span.column}` : '<unknown>';
      console.error(`${err.code || 'error'} at ${loc}: ${err.message}`);
    }
    process.exit(1);
  }
}

function cmdRun(filePath, opts = {}) {
  const { source, resolved } = readSource(filePath);
  if (!validateExtension(resolved, ['.thirsty', '.thirstofgods', '.tgl', '.js'])) {
    console.warn(`Warning: File '${filePath}' does not have a .thirsty extension`);
  }
  try {
    const { output } = runSource(source, resolved, opts);
    for (const line of output) {
      console.log(line);
    }
  } catch (err) {
    if (err.errors) {
      // DiagnosticBundle
      for (const e of err.errors) {
        const span = e.thirstySpan;
        const loc = span ? `${span.file}:${span.line}:${span.column}` : '<unknown>';
        console.error(`${e.code || 'error'} at ${loc}: ${e.message}`);
      }
    } else {
      const span = err.thirstySpan;
      if (span) {
        console.error(`${err.code || 'error'} at ${span.file}:${span.line}:${span.column}: ${err.message}`);
      } else {
        console.error(`Error: ${err.message}`);
      }
    }
    process.exit(1);
  }
}

function main() {
  const rawArgs = process.argv.slice(2);

  if (rawArgs.length === 0) {
    console.log('Thirsty-Lang Interpreter v2.0.0 (AST-based)');
    console.log('Usage:');
    console.log('  node src/cli.js <file.thirsty>          Run program');
    console.log('  node src/cli.js --run <file.thirsty>    Run program');
    console.log('  node src/cli.js --check <file.thirsty>  Type-check only');
    console.log('  node src/cli.js --tokens <file.thirsty> Print tokens as JSON');
    console.log('  node src/cli.js --ast <file.thirsty>    Print AST as JSON');
    process.exit(0);
  }

  const flag = rawArgs[0];

  if (flag === '--tokens' && rawArgs[1]) {
    return cmdTokens(rawArgs[1]);
  }
  if (flag === '--ast' && rawArgs[1]) {
    return cmdAst(rawArgs[1]);
  }
  if (flag === '--check' && rawArgs[1]) {
    return cmdCheck(rawArgs[1]);
  }
  if (flag === '--run' && rawArgs[1]) {
    return cmdRun(rawArgs[1]);
  }
  // Default: treat first arg as filename
  if (!flag.startsWith('--')) {
    return cmdRun(flag);
  }

  console.error(`Unknown flag: ${flag}`);
  process.exit(1);
}

if (require.main === module) {
  main();
}

module.exports = { main, runSource, parseSource, checkSource, lexSource };
