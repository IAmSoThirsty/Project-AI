# JS / Python Thirsty-Lang Implementation Parity Analysis

**Date**: 2026-05-12  
**Python reference**: `src/utf/thirsty_lang/` (tree-walking AST interpreter, ~900 lines)  
**JS implementation**: `src/thirsty_lang/src/index.js` (line-by-line tokenizer, ~218 lines)

---

## Executive Summary

The JS implementation is a proof-of-concept tokenizer, not a production interpreter. It does not parse or execute the Thirsty-Lang grammar as defined in `THIRSTY_EBNF_GRAMMAR.md`. The two implementations share a superficial keyword vocabulary but implement fundamentally different languages.

**Parity status: ~8% of conformance suite features supported in JS.**

---

## Feature Matrix

| Feature | Python | JS | Notes |
|---------|--------|-----|-------|
| `drink x: T = v;` variable declaration | ✅ | ❌ | JS: `drink x = v` (no type, no `;`) |
| `pour(expr);` output | ✅ | ❌ | JS: `pour expr` (no parens, no `;`) |
| `sip(x)` input | ✅ | Stub | JS: prints "not yet implemented" |
| `glass fn(p: T) -> R { }` function decl | ✅ | ❌ | JS: `glass fn(p)` + `endglass` sentinel (no braces, no return type) |
| `return expr;` | ✅ | ❌ | Not in JS |
| `thirsty cond { } hydrated { }` if/else | ✅ | Partial | JS: `thirsty cond` + single next-line body; no `hydrated`, no braces, no else |
| `refill` loop | ✅ | ❌ | Not in JS |
| `spillage/cleanup/finally` error handling | ✅ | ❌ | Not in JS |
| `glass main() -> Int { return 0; }` entry | ✅ | ❌ | JS has no `main()` convention; no return type |
| `fountain ClassName { }` class | ✅ | Partial | JS: `fountain Name` + body lines + `endfountain`; no methods/fields |
| `module` header | ✅ | ❌ | Not in JS |
| `mode core\|governed` | ✅ | ❌ | Not in JS |
| `import "thirst::module" as alias;` | ✅ | ❌ | Not in JS |
| Type annotations (`Int`, `String`, etc.) | ✅ | ❌ | Not in JS |
| `GovernedFunctionDecl` + `requires` | ✅ | ❌ | Not in JS |
| Enum/Struct/Interface declarations | ✅ | ❌ | Not in JS |
| `Result[T, E]` / `Governed[T]` types | ✅ | ❌ | Not in JS |
| Binary expressions (`x + y`, `x * y`) | ✅ | Partial | JS: only in conditions (`evaluateCondition`), not in general expressions |
| String concatenation | ✅ | ❌ | Not in JS |
| Arithmetic in `drink` assignments | ✅ | ❌ | JS `evaluateExpression` handles only literals and variable references |
| Nested function calls | ✅ | ❌ | Not in JS |
| Closures / first-class functions | ✅ | ❌ | Not in JS |
| `shield/sanitize/armor/morph/detect/defend` | ✅ | ❌ | Not in JS |
| `mutation/validated_canonical` | ✅ | ❌ | Not in JS |
| `await` / `cascade` async | ✅ | ❌ | Not in JS |
| Pipe operator `\|>` | ✅ | ❌ | Not in JS |
| Safe-call `?` | ✅ | ❌ | Not in JS |
| Multi-line programs | ✅ | Partial | JS splits on `\n`, strips whitespace — multi-line works only for simple statements |
| Braces-delimited blocks | ✅ | ❌ | JS uses `endglass`/`endfountain` sentinels |
| Semicolons as statement terminators | ✅ | ❌ | JS strips semicolons by stripping all lines; conformance tests require `;` |

---

## Root Cause of Divergence

The JS implementation uses a **line-by-line pattern matching** approach (`code.split('\n').map(line => line.trim())`). Each line is matched by regex against a fixed set of patterns. There is no:
- Lexer (no tokenization)
- Parser (no AST)
- Type system
- Scope resolution
- Error reporting with span information

The Python reference uses a proper **Lexer → Parser → AST → Checker → Interpreter** pipeline with 9 interconnected modules and a defined EBNF grammar.

The two implementations cannot achieve parity by extending the JS line-matcher. The JS implementation requires a complete rewrite as an AST-based interpreter to match the Python reference.

---

## Conformance Suite Outcome (Predicted)

Against the 9 conformance suites (`conformance/*.json`, total ≈ 200 tests):

| Suite | JS Pass Rate | Reason |
|-------|-------------|--------|
| `syntax.json` | ~0% | All tests use `-> Int`, braces, semicolons — none match JS |
| `types.json` | ~0% | All use type annotations |
| `errors.json` | ~0% | Error handling (`spillage`) not in JS |
| `stdlib.json` | ~0% | `import "thirst::module"` not in JS |
| `modules.json` | ~0% | Module system not in JS |
| `advanced.json` | ~0% | Closures, pipes, generics not in JS |
| `security.json` | ~0% | `shield`/`sanitize`/`armor` not in JS |
| `governance.json` | ~0% | `mode governed`, `requires`, `GovernedFunctionDecl` not in JS |
| `shadow_mutation.json` | ~0% | Unrelated subsystem |
| **Total** | **~0%** | JS cannot parse any conformance test source |

The single narrow case where JS might pass: a one-line program consisting of only `pour "hello"` (no parentheses, no semicolon, no `main()` function) — but conformance tests all use the Python-style syntax, so none would pass.

---

## Path to Parity

Full JS parity requires building a complete JS interpreter with the same grammar as the Python reference. Estimated scope:

### Option A — JS Rewrite (recommended for true parity)

1. **Lexer** (`lexer.js`): tokenize Thirsty source into token objects with type, lexeme, span
2. **Parser** (`parser.js`): recursive-descent parser implementing `THIRSTY_EBNF_GRAMMAR.md`
3. **AST** (`ast.js`): already exists as a skeleton — extend to match Python `ast.py` nodes
4. **Checker** (`checker.js`): type checker validating against the Python checker's rules
5. **Interpreter** (`interpreter.js`): tree-walking interpreter with the same stdlib functions
6. **CLI** (`cli.js`): already exists — wire to new interpreter instead of `index.js`

Effort: ~4–6 weeks for a single developer targeting 200/200 conformance.

### Option B — Node.js wrapper around Python interpreter (expedient)

Use Node.js `child_process.spawn` to invoke the Python interpreter, pass source via stdin, capture stdout. The JS "implementation" becomes a thin wrapper.

This achieves 200/200 conformance immediately but is not a true independent implementation — it does not satisfy the independence requirement (Point 13 of the plan).

### Current Status

The `conformance/runner_js.py` script is ready to measure JS conformance at any time:
```
python conformance/runner_js.py --all
```

Until a proper JS rewrite is completed, expected output is approximately:
```
JS conformance: 0/200 passed
```

---

## What the JS Implementation Does Well

Despite the parity gap, the JS codebase has valuable infrastructure:

| Component | Location | Value |
|-----------|----------|-------|
| VS Code extension | `src/thirsty_lang/vscode-extension/` | Syntax highlighting + snippets already work |
| Formatter | `src/thirsty_lang/src/formatter.js` | Useful reference for formatting rules |
| Linter | `src/thirsty_lang/src/linter.js` | Security-check heuristics |
| Profiler | `src/thirsty_lang/src/profiler.js` | Timing hooks |
| Transpiler | `src/thirsty_lang/src/transpiler.js` | JS→Thirsty transpilation skeleton |
| Test runner | `src/thirsty_lang/src/test/runner.js` | Framework for JS-side tests |

These components should be preserved and extended in a JS rewrite, not replaced.

---

## Conclusion

**Current parity: 0/200 conformance tests pass in JS.**

The JS implementation needs a complete rewrite to reach parity. The infrastructure (VS Code extension, CLI shell, test framework, AST skeleton) is worth preserving. The core interpreter (`index.js`) should be replaced with an AST-based implementation following `THIRSTY_EBNF_GRAMMAR.md`.

Until the rewrite, the claim "two independent implementations" should not be made in public documentation.
