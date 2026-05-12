# Thirsty-Lang Type System v1.0

---

## 1. Primitive Types

| Type | Thirsty name | Python representation |
|------|-------------|----------------------|
| Integer | `Int` | `int` |
| Float | `Float` | `float` |
| Boolean | `Bool` | `bool` |
| String | `String` | `str` |
| Void | `Void` | `None` |
| Any | `Any` | unchecked |
| Error | `Error` | `ThirstyError` |

### Widening Rules

`Int` widens to `Float`. All types widen to `Any`. No other implicit widening occurs.

---

## 2. Generic Types (Phase 1 — implemented)

### Quenched[T] (Option/Maybe)
Represents a value that may be absent.
- `empty` is the null value of any `Quenched[T]`
- `condense(expr)` unwraps — raises if absent
- `thirst expr quench` is the guard expression form

### Reservoir[T] (Mutable Array)
Ordered mutable collection of `T`.
- `drink mut xs: Reservoir[Int] = [1, 2, 3];`
- Functions: `size`, `push`, `pop`, `get`, `flood` (via `thirst::reservoir` or global builtins)

### Task[T] (Async Result)
Returned by `cascade glass` functions. Unwrapped by `await`.

---

## 3. Generic Types (Phase 3 — planned)

### Result[T, E]
Represents either a success value `T` or an error `E`. Functions that call `throw` must declare `-> Result[T, E]`. `spillage/cleanup` unwraps Result values.

### Governed[T]
Return type for governance-annotated functions. Signals that the return value came from a governance-checked execution path. Only functions with `requires` clauses may return `Governed[T]`.

---

## 4. User-Defined Types (Phase 3 — planned)

### Enums
```
enum Status { Pending, Active, Closed }
```
The checker enforces exhaustive matching over enum values in `thirsty` blocks.

### Structs
```
struct Account { id: Int, balance: Float, owner: String }
```
All fields are required in the constructor. Field access is type-checked.

### Interfaces
```
interface Serializable { glass serialize() -> String }
```
`fountain` declarations that claim an interface must implement all declared methods.

### Generics
```
glass identity[T](value: T) -> T { return value; }
```
Type variables are resolved at call sites via substitution.

### Opaque Handle Types (Phase 3)
`ConnectionType` and `ServerType` — returned by `thirst::net` functions. These are opaque handles; their internal structure is not accessible to Thirsty programs.

---

## 5. Governance Types (Phase 3 — planned)

### AuthorityClass
```
AuthorityClass.AC1  # minimal
AuthorityClass.AC2
AuthorityClass.AC3
AuthorityClass.AC4
AuthorityClass.AC5  # maximum
```

### AuditTrail.Immutable
Marks that execution of the annotated function must produce an immutable audit record via the acceptance ledger.

### HumanAppealWindow[Nd]
Marks that the decision produced by the annotated function is appealable for N days.

---

## 6. Type Inference

`drink` declarations require explicit type annotations. The checker does not infer types from initializer expressions — the type annotation IS the declared type; the checker verifies the initializer is compatible.

Exception: when `Any` is used as the annotation, the checker accepts any initializer.

---

## 7. Function Type Signatures

```
glass name(p1: T1, p2: T2) -> ReturnType { ... }
```

The checker verifies:
- Argument count matches parameter count at every call site
- Each argument type is compatible with the declared parameter type
- The return expression type is compatible with the declared return type

---

## 8. Type Checker Architecture

The type checker (`src/utf/thirsty_lang/checker.py`, 613 lines) implements:
- Symbol table with lexical scope hierarchy
- Duplicate binding detection (THIRSTY-E010)
- Unknown identifier detection (THIRSTY-E011)
- Assignment to immutable binding (THIRSTY-E020)
- Type mismatch at assignment, function call, return (THIRSTY-E021/E022/E023)
- Condition type narrowing for `thirsty` blocks
- Array homogeneity enforcement
- Pipe expression type compatibility
- Class field and method resolution
- Call arity checking
- Module import member access

Phase 3 adds: enum exhaustiveness, struct field checking, interface implementation verification, generic type variable substitution, `requires` clause propagation.
