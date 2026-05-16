# Thirsty-Lang Runtime Semantics v1.0

---

## 1. Evaluation Order

All expressions are evaluated strictly, left-to-right. There is no lazy evaluation. Function arguments are evaluated before the function is called.

---

## 2. Call Semantics

- **Primitive values** (`Int`, `Float`, `Bool`, `String`) are passed by value
- **Object values** (`Reservoir`, class instances) are passed by reference — mutations inside a function affect the caller's binding if the binding is `mut`
- **Closures** capture the environment at definition time (lexical scope)

---

## 3. Tail-Call Optimization

When the last expression in a function body is a direct recursive call to the same function, the interpreter replaces the call frame rather than nesting it. This allows unbounded recursion depth for tail-recursive programs without stack overflow.

Tail-call optimization is active when:
- The return expression is a call to the current function
- No cleanup or post-processing happens after the recursive call

Non-tail mutual recursion is subject to the recursion limit (default: 256 calls).

---

## 4. Error Propagation

Errors raised by `throw` or runtime faults propagate up the call stack until caught by a `spillage/cleanup` block. If uncaught at the top level, the interpreter reports the error code and message and exits with code 1.

`spillage/cleanup/finally` semantics:
- `spillage` body runs; if it throws, execution jumps to `cleanup`
- `cleanup` receives the thrown value as its named parameter
- `finally` always runs regardless of whether an error occurred

---

## 5. Async Execution

`cascade glass` functions return a `TaskValue` wrapping the computed result. `await expr` unwraps the `TaskValue`. The current implementation evaluates the async body synchronously and wraps the result — true async I/O is a future extension.

---

## 6. Mode-Dependent Execution Path

In `mode core` (default), the interpreter executes the AST directly without consulting any governance subsystems.

In `mode governed` (Phase 3), before each governed function call the interpreter:
1. Looks up the auto-generated TARL policy (`dist/<module>.auto.tarl`)
2. Calls `tarl.core.evaluate(policy_path, ctx)` with the current execution context
3. If TARL returns `DENY` or the policy file is absent, raises `ThirstyGovernanceError` (THIRSTY-E050)
4. If `ALLOW`, dispatches the function normally

The execution context (`ctx`) passed to TARL contains: `ctx.function` (name of function being called), `ctx.authority_class` (from interpreter context, default `AC1`).

---

## 7. Built-in Global Functions

These are always available without import:

| Function | Signature | Effect |
|----------|-----------|--------|
| `length(s)` | `String -> Int` | String length |
| `contains(s, n)` | `(String, String) -> Bool` | Substring check |
| `split(s, sep)` | `(String, String) -> Reservoir[String]` | Split string |
| `abs(x)` | `Int -> Int` | Absolute value |
| `min(a, b)` | `(Int, Int) -> Int` | Minimum |
| `max(a, b)` | `(Int, Int) -> Int` | Maximum |
| `push(xs, v)` | `(Reservoir[T], T) -> Void` | Append in-place |
| `pop(xs)` | `Reservoir[T] -> T` | Remove last in-place |
| `size(xs)` | `Reservoir[T] -> Int` | Length |
| `get(xs, i)` | `(Reservoir[T], Int) -> T` | Index access |
| `flood(xs, p)` | `(Reservoir[T], T) -> Reservoir[T]` | Extend in-place |
| `condense(v)` | `Quenched[T] -> T` | Unwrap option (raises if empty) |
| `evaporate(v)` | `Any -> Void` | Discard value |
| `strain(xs, fn)` | `(Reservoir[T], T->Bool) -> Reservoir[T]` | Filter |
| `transmute(xs, fn)` | `(Reservoir[T], T->U) -> Reservoir[U]` | Map |
| `distill(xs, seed, fn)` | `(Reservoir[T], U, (U,T)->U) -> U` | Reduce |

---

## 8. Output Collection

`pour(expr)` appends the string representation of `expr` to an internal output list. At program termination, the output list is joined with newlines and written to stdout. This allows the interpreter to buffer all output and the conformance runner to capture it cleanly via `subprocess`.
