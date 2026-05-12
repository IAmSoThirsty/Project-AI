# Thirsty-Lang Language Specification v1.0

**Status**: Stable — Core 1.x backward compatibility guaranteed (see STABILITY.md)  
**Implementation**: `src/utf/thirsty_lang/` (Python reference interpreter)  
**JS reference**: `src/thirsty_lang/` (conformance target)

---

## 1. Design Goals

Thirsty-Lang is a governance-first programming language. Its design hierarchy:

1. **Safety** — unauthorized, irreversible, or unauditable actions are blocked by default
2. **Clarity** — water-metaphor syntax is consistent and readable
3. **Correctness** — type checker prevents class of errors at parse time
4. **Adoptability** — `mode core` programs run without the governance stack

The language has two execution modes (set by module header):
- `mode core` — interpreter only; no TARL/Shadow Thirst/TSCG gates
- `mode governed` — all governance gates active before execution

---

## 2. Module Header

Every source file may begin with an optional module header:

```
module <name>
mode core | governed
```

Both lines are optional. Default mode is `core`. The header, if present, must appear before any declarations.

---

## 3. Token Categories

### 3.1 Literals
| Category | Examples |
|----------|---------|
| Integer | `0`, `42`, `-1` |
| Float | `3.14`, `0.0` |
| String | `"hello"`, `"it's fine"` |
| Boolean | `parched` (true), `quenched` (false) |
| Null | `empty` |

### 3.2 Operators
| Operator | Meaning |
|----------|---------|
| `+` `-` `*` `/` `%` | Arithmetic |
| `==` `!=` `<` `<=` `>` `>=` | Comparison |
| `and` `or` `!` | Boolean logic |
| `\|>` | Pipe (left-to-right function application) |
| `?` | Safe call (returns `empty` instead of erroring) |
| `.` | Member access |
| `=` `+=` | Assignment |
| `->` | Return type annotation |

### 3.3 Keywords

**Core language**:
`drink` `pour` `sip` `thirsty` `hydrated` `thirst` `quench` `refill` `times`
`glass` `reservoir` `well` `of` `return` `parched` `quenched` `empty` `mut`
`flood` `drip` `evaporate` `condense`

**Module system**:
`import` `from` `as` `module` `mode` `core` `governed`

**Classes**:
`fountain` `this` `new` `public` `private` `cascade`

**Errors**:
`spillage` `cleanup` `finally` `error` `throw`

**Security**:
`shield` `sanitize` `armor` `morph` `detect` `defend`

**Shadow Thirst**:
`mutation` `validated_canonical` `invariant` `shadow` `canonical` `promote` `reject`

**TARL/policy**:
`policy` `when` `ALLOW` `DENY` `ESCALATE`

**Control**:
`await`

---

## 4. Statement Reference

### 4.1 Variable Declaration
```
drink name: Type = expr;         # immutable
drink mut name: Type = expr;     # mutable
```
Type annotation is required at declaration.

### 4.2 Output
```
pour(expr);
```
Converts the value to string and appends to output.

### 4.3 Input
```
drink x: String = sip();         # blocks for user input
drink x: String = sip?();        # safe — returns empty if unavailable
```

### 4.4 Conditionals
```
thirsty (condition) {
    ...
} hydrated {
    ...
}
```
The `hydrated` branch is optional.

### 4.5 Loops
```
refill N times {
    ...
}
```
`N` must be a non-negative integer expression.

### 4.6 Functions
```
glass name(param: Type, ...) -> ReturnType {
    ...
    return expr;
}
```
Async functions use `cascade glass`. Tail calls are automatically optimized when the last expression is a direct recursive call.

### 4.7 Classes
```
fountain ClassName {
    drink field: Type = default;

    glass init(args) -> Void { ... }
    glass method() -> ReturnType { ... }
}
```

### 4.8 Error Handling
```
spillage {
    risky_call();
} cleanup (err: Error) {
    pour(err);
} finally {
    cleanup_resources();
}
```

### 4.9 Pipe Operator
```
expr |> function_name
```
Equivalent to `function_name(expr)`. Chains left-to-right.

### 4.10 Guard Expression
```
thirst expr quench
```
Unwraps a `Quenched[T]` option; raises if empty. Equivalent to `condense(expr)`.

### 4.11 Shadow Thirst Mutation
```
mutation validated_canonical fn_name(param: Type) {
    shadow { ... }      # simulation — read-only, deterministic
    invariant { ... }   # gate checks — must be pure
    canonical { ... }   # actual state write
}
```

### 4.12 Imports
```
import thirst::module
import thirst::module as alias
from "./path/file.thirsty" import name
```

### 4.13 Security Keywords
- `shield { ... }` — declares an authorized execution scope
- `sanitize(expr)` — sanitizes user input
- `armor(expr)` — wraps a value in a security boundary
- `morph(expr)` — transforms a value through security policy
- `detect(expr)` — inspects a value for known threat patterns
- `defend(expr)` — asserts a security invariant; halts if violated

---

## 5. Scoping Rules

- Scoping is **lexical** — functions close over the environment at definition time
- `drink` declarations without `mut` are **immutable** — assignment raises `THIRSTY-E020`
- Module boundary creates a fresh top-level scope
- Classes introduce a scope; `this` refers to the current instance

---

## 6. Error Model

All errors carry a `THIRSTY-Exxx` code. See `THIRSTY_ERROR_CODES.md` for the full registry.

Errors are raised as `ThirstyError` objects with `code`, `message`, and source `span`.
The `spillage/cleanup/finally` construct catches thrown values.

---

## 7. Mode Semantics

| Mode | Parser | Checker | Interpreter | TARL | Shadow Thirst | TSCG |
|------|--------|---------|-------------|------|---------------|------|
| `core` | ✓ | ✓ | ✓ | — | — | — |
| `governed` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

`governed` mode activates in Phase 3. In Phase 1, the mode flag is parsed and stored; governance routing is a Phase 3 addition.
