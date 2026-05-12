# Thirsty-Lang Error Code Registry

All errors raised by the Thirsty-Lang toolchain carry a `THIRSTY-Exxx` code. This document is the authoritative registry. Error objects are instances of `ThirstyError` (defined in `diagnostics.py`) with fields `code`, `message`, and `span`.

---

## E0xx — Syntax and Parse Errors

### THIRSTY-E001 — Syntax error
**Trigger**: The parser encountered a token it did not expect: missing closing delimiter, missing keyword, invalid assignment target, unknown statement form, invalid mode declaration value.  
**Fix**: Correct the syntax at the indicated line and column. The caret marker in the formatted error points to the offending token.

### THIRSTY-E002 — Lexer error
**Trigger**: The lexer encountered an unterminated string literal (no closing `"`) or an unrecognized character that cannot begin any valid token.  
**Fix**: Close the string literal or remove the unrecognized character.

---

## E01x — Scope and Binding Errors

### THIRSTY-E010 — Duplicate binding
**Trigger**: A `drink` declaration names an identifier that is already bound in the current scope.  
**Fix**: Choose a different name, or remove the duplicate declaration.  
**Example**:
```
drink x: Int = 1;
drink x: Int = 2;   # THIRSTY-E010: duplicate binding 'x'
```

### THIRSTY-E011 — Unknown identifier
**Trigger**: An identifier is referenced but not bound in any enclosing scope. Also raised when: `this` is used outside a class body; a `new` expression names an unknown class; an imported name is not exported by the target module.  
**Fix**: Check spelling (the error message suggests the nearest known name when one exists within edit distance 3). Ensure the binding is declared before use, or that the import is correct.

---

## E02x — Type Errors

### THIRSTY-E020 — Immutable assignment
**Trigger**: An assignment (`=` or `+=`) targets a binding declared without `mut`, or a `drip` statement targets an immutable binding.  
**Fix**: Add `mut` to the original `drink` declaration, or remove the assignment.

### THIRSTY-E021 — Type mismatch
**Trigger**: The type of an expression is incompatible with the expected type in the context:
- Right-hand side of assignment does not match declared variable type
- Function argument type does not match parameter type
- Arithmetic operands are not numeric
- Member access on a non-object type
- Pipe target argument type mismatch
- `await` applied to a non-`Task` value  
**Fix**: Ensure the expression type matches the expected type. Use explicit conversion where needed.

### THIRSTY-E022 — Condition type error
**Trigger**: The condition of a `thirsty` block is not `Bool`, or a guard expression (`thirst expr quench`) condition is not `Bool`, or at runtime a conditional value is not boolean.  
**Fix**: Ensure the condition evaluates to a boolean expression.

### THIRSTY-E023 — Loop count type error
**Trigger**: The count expression in a `refill N times` loop is not `Int`, or evaluates to a negative integer at runtime.  
**Fix**: Ensure the count expression is a non-negative integer.

### THIRSTY-E024 — Return type mismatch
**Trigger**: The expression in a `return` statement has a type incompatible with the declared return type of the enclosing function.  
**Fix**: Change the return expression to match the declared return type, or update the function's return type annotation.

---

## E03x — Call Errors

### THIRSTY-E030 — Arity mismatch
**Trigger**: A function is called with a different number of arguments than its parameter list declares. Also raised when a pipe expression passes the wrong number of additional arguments.  
**Fix**: Correct the argument count to match the function signature.

### THIRSTY-E031 — Not callable
**Trigger**: An expression is used as a function call target but its type is not a function or callable built-in.  
**Fix**: Ensure the call target is a function name, method, or callable expression.

### THIRSTY-E032 — Index type error
**Trigger**: A subscript expression (`xs[i]`) uses an index that is not `Int`.  
**Fix**: Ensure the index expression evaluates to an integer.

---

## E1xx — Runtime Errors

### THIRSTY-E100 — Index out of bounds
**Trigger**: A subscript access on a `Reservoir` fails at runtime because the index is out of range.  
**Fix**: Guard index access with a `size()` check, or use `get()` inside a `spillage` block.

### THIRSTY-E101 — Division by zero
**Trigger**: The `/` or `%` operator is applied with a zero right-hand operand at runtime.  
**Fix**: Guard division with a zero check before the operation.

---

## E5xx — Governance Errors (Phase 3)

### THIRSTY-E050 — Governance denial
**Trigger** (Phase 3): A governed function was called in `mode governed` and either no TARL policy file was found for the module, or the TARL evaluator returned `DENY` for the current execution context.  
**Fix**: Ensure the execution context carries the required `AuthorityClass` declared in the `requires` annotation, or set the module to `mode core` if governance is not intended.

---

## E9xx — Interpreter Limits

### THIRSTY-E900 — Recursion limit exceeded
**Trigger**: Non-tail recursion depth has exceeded 256 nested calls. (Tail-recursive functions are not subject to this limit — they reuse the call frame.)  
**Fix**: Refactor as a tail-recursive or iterative (`refill`) solution, or increase the interpreter's recursion limit via configuration.

### THIRSTY-E901 — Empty option unwrapped
**Trigger**: `condense(v)` or the `thirst expr quench` guard was applied to an `empty` value.  
**Fix**: Check for `empty` before unwrapping, or use a `spillage/cleanup` block to handle the failure case.

---

## Error Format

Errors are displayed using `format_error()` from `diagnostics.py`:

```
error[THIRSTY-E021]: type mismatch: expected Int, got String
  --> example.thirsty:5:3
   |
 5 |   drink x: Int = "hello";
   |              ^^^^^^^^^^^
```

Multiple errors collected during type checking are reported as a `DiagnosticBundle` — all errors are shown before the interpreter exits.
