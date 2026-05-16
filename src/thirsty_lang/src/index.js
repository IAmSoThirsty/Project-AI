#!/usr/bin/env node
'use strict';

/**
 * Thirsty-Lang Interpreter — AST-based production runtime
 *
 * This module is the public entry point for the JS/browser/edge runtime.
 * It replaces the old line-by-line pattern matcher with a full:
 *   Lexer → Parser → Checker → Interpreter pipeline.
 *
 * Governance annotations (mode governed / requires AuthorityClass.ACN) make
 * HTTP POST calls to the Python Triumvirate at port 8001 before executing
 * governed functions. Core language is handled entirely in JS.
 */

const { Lexer } = require('./lexer');
const { Parser } = require('./parser');
const { Checker } = require('./checker');
const {
  Interpreter,
  UserFunction,
  UserClass,
  UserInstance,
  ModuleValue,
  TaskValue,
  RuntimeFault,
  ThirstyGovernanceError,
  stringify,
} = require('./interpreter');

class ThirstyInterpreter {
  /**
   * @param {object} [options]
   * @param {function} [options.inputProvider]  Returns a string when called (sync sip())
   * @param {boolean}  [options.trace]          Enable trace output
   * @param {object}   [options.governanceContext]  { authority_class, caller_id, session_id }
   * @param {number}   [options.recursionLimit] Default 256
   */
  constructor(options = {}) {
    this._options = options;
    this._interp = null;
  }

  /**
   * Execute Thirsty-Lang source code.
   * Returns array of output lines (what pour() emits).
   * @param {string} code
   * @param {string} [file]
   * @returns {string[]}
   */
  execute(code, file = '<memory>') {
    const tokens = new Lexer(code, file).lex();
    const program = new Parser(tokens).parseProgram();

    this._interp = new Interpreter({
      currentFile: file,
      inputProvider: this._options.inputProvider || (() => ''),
      trace: this._options.trace || false,
      recursionLimit: this._options.recursionLimit || 256,
      governanceContext: this._options.governanceContext || {},
    });

    return this._interp.run(program, true);
  }

  /**
   * Type-check source code without executing it.
   * Throws on type errors.
   * @param {string} code
   * @param {string} [file]
   */
  check(code, file = '<memory>') {
    const tokens = new Lexer(code, file).lex();
    const program = new Parser(tokens).parseProgram();
    const checker = new Checker();
    checker.check(program);
  }

  /**
   * Lex only — returns token array.
   * @param {string} code
   * @param {string} [file]
   * @returns {import('./lexer').Token[]}
   */
  tokenize(code, file = '<memory>') {
    return new Lexer(code, file).lex();
  }

  /**
   * Parse only — returns Program AST node.
   * @param {string} code
   * @param {string} [file]
   * @returns {import('./ast').Program}
   */
  parse(code, file = '<memory>') {
    const tokens = new Lexer(code, file).lex();
    return new Parser(tokens).parseProgram();
  }

  /** Achievements unlocked during last run */
  get achievements() {
    return this._interp ? this._interp.achievements : new Set();
  }
}

module.exports = ThirstyInterpreter;

// Named exports for consumers that prefer them
module.exports.ThirstyInterpreter = ThirstyInterpreter;
module.exports.Lexer = Lexer;
module.exports.Parser = Parser;
module.exports.Checker = Checker;
module.exports.Interpreter = Interpreter;
module.exports.UserFunction = UserFunction;
module.exports.UserClass = UserClass;
module.exports.UserInstance = UserInstance;
module.exports.ModuleValue = ModuleValue;
module.exports.TaskValue = TaskValue;
module.exports.RuntimeFault = RuntimeFault;
module.exports.ThirstyGovernanceError = ThirstyGovernanceError;
module.exports.stringify = stringify;
