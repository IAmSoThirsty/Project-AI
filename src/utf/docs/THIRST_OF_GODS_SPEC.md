# Thirst of Gods — Full Language Specification

**Version:** 1.0  
**Dialect:** Thirst of Gods (ToG)  
**Base language:** Thirsty-Lang  
**Source extension:** `.thirstofgods` (also accepted: `.thirsty` with ToG constructs)

---

## 1. Design Philosophy

Thirst of Gods is the **object-oriented and asynchronous tier** of the Thirsty-Lang language family.

The governing design principles:

1. **Purely additive.** Every valid Thirsty-Lang program is a valid Thirst of Gods program.
   No Thirsty-Lang syntax is redefined or removed. Thirst of Gods adds keywords, constructs,
   and semantics on top of the base language without breaking backward compatibility.

2. **Same runtime.** Thirst of Gods source code is parsed by the same `Lexer`, `Parser`,
   `Checker`, and `Interpreter` pipeline as base Thirsty-Lang. There is no separate runtime,
   no separate bytecode, and no separate binary. The additional constructs lower directly into
   the existing tree-walking interpreter.

3. **Explicit concurrency.** Async is opt-in. A function must be declared `cascade glass`
   to run concurrently. All other functions are synchronous and run on the calling thread.
   `await` is the only way to observe an asynchronous result from synchronous code.

4. **Structural classes.** Classes (`fountain`) are structural: a class's public interface
   is defined by the methods and fields it declares. There is no nominal subtype hierarchy
   beyond the single `fountain` declaration form implemented in the current runtime.

5. **Governance interop.** Async functions may carry `requires` governance annotations
   (`GovernedFunctionDecl`). Governance enforcement happens at call time regardless of
   whether the function is synchronous or asynchronous.

---

## 2. Keyword Reference

The following keywords are exclusive to Thirst of Gods (not present in base Thirsty-Lang):

| Keyword     | Role                                            |
|-------------|-------------------------------------------------|
| `fountain`  | Declares a class                                |
| `this`      | Self-reference inside a method body             |
| `new`       | Instantiates a class                            |
| `public`    | Marks a field or method as externally visible   |
| `private`   | Marks a field or method as internal-only        |
| `cascade`   | Modifier that makes a `glass` function async    |
| `await`     | Unwraps a `Task[T]` value, blocking until ready |
| `spillage`  | Opens a protected block (try)                   |
| `cleanup`   | Introduces a catch (`error`) or finally clause  |
| `finally`   | Used after `cleanup` for guaranteed execution   |
| `error`     | Names the catch-binding type in `cleanup error` |
| `throw`     | Raises a value as a `ThrownSignal`              |

All of these are registered in `token.py` (`KEYWORDS` dict) and have corresponding
AST nodes or node fields in `ast.py`.

---

## 3. Class Declarations (`fountain`)

### 3.1 Syntax

```
fountain <ClassName> {
    [<visibility>] drink [mut] <field>: <Type> [= <initializer>];
    ...
    [<visibility>] glass <method>(<params>) [-> <ReturnType>] { <body> }
    ...
    [<visibility>] cascade glass <method>(<params>) [-> <ReturnType>] { <body> }
    ...
}
```

`<visibility>` is either `public` or `private` (optional; currently parsed and stored
in `VarDecl.visibility` and `FunctionDecl.visibility` respectively, but not enforced
at the access level by the runtime — the interpreter does not yet raise on private access
from outside the class).

### 3.2 Fields

Fields are declared with `drink` (and optionally `mut`) inside the `fountain` body.
They are treated as `VarDecl` nodes with `is_field = True`. The interpreter collects
them into `UserClass.fields` (initialised to `None`) during class construction.

```thirstofgods
fountain Counter {
    drink mut count: Int;
    drink label: String;
}
```

The `init` method (if present) is called automatically when `new ClassName(...)` is
evaluated. It receives all arguments passed to `new`.

### 3.3 Constructors (`glass init`)

The constructor is a regular method named `init`. It has no return type. It receives
the arguments passed to `new`. Inside the body, `this` refers to the freshly-allocated
instance.

```thirstofgods
fountain Counter {
    drink mut count: Int;

    glass init(start: Int) {
        this.count = start;
    }
}
```

If no `init` method is declared, the class is instantiated with all fields set to `empty`
(Thirsty's `None`). `new Counter()` is still valid.

### 3.4 Methods

Any `glass` declaration inside a `fountain` body becomes a method. The interpreter
wraps it as a `UserFunction` and stores it in `UserClass.methods`.

When a method is called on an instance (`tracker.add(4)`), the interpreter binds
`this` by calling `UserFunction.bind(instance)`, which produces a new `UserFunction`
with `bound_this` set to the instance. Inside `_run_fn_body`, `this` is defined in
the method's local `Env` before execution begins.

```thirstofgods
fountain Counter {
    drink mut count: Int;

    glass init(n: Int) {
        this.count = n;
    }

    glass increment() {
        this.count = this.count + 1;
    }

    glass value() -> Int {
        return this.count;
    }
}
```

### 3.5 `this`

`this` is a keyword (token `THIS`, expression node `ThisExpr`). The interpreter
resolves it via `env.get("this")` which returns the `UserInstance` bound to the
current method call. Writing `this.field = value` dispatches to `UserInstance.set(name, value)`.
Reading `this.field` dispatches to `UserInstance.get(name)`.

`this` is only valid inside a `fountain` method body. Using `this` in a top-level
function will raise a `RuntimeError("unknown binding 'this'")` at runtime.

### 3.6 `new`

The `new` expression instantiates a class:

```
new <ClassName>(<arg>, ...)
```

AST node: `NewExpr(class_name: str, args: list[Expr])`.

The interpreter evaluates `new` as follows:
1. Look up `class_name` in the current scope — must be a `UserClass`.
2. Evaluate all arguments.
3. Call `UserClass.instantiate(interpreter, args)`:
   a. Creates a `UserInstance` with a copy of `UserClass.fields`.
   b. If `init` is in `UserClass.methods`, binds and calls it with the given args.
4. Returns the `UserInstance`.

---

## 4. Async Functions (`cascade glass`)

### 4.1 Declaration

Any `glass` function (top-level or method) can be made asynchronous by prepending `cascade`:

```
cascade glass <name>(<params>) [-> <ReturnType>] {
    <body>
}
```

In the AST, `cascade glass` sets `FunctionDecl.is_async = True` (or
`GovernedFunctionDecl.is_async = True` when `requires` clauses are present).

### 4.2 Call Semantics — Returns `Task[T]`

Calling a `cascade glass` function **never blocks**. The interpreter submits the
function body to a module-level `ThreadPoolExecutor` (`_ASYNC_POOL`) and immediately
returns a `TaskValue` wrapping the resulting `concurrent.futures.Future`.

```thirstofgods
cascade glass fetchData() -> String {
    // runs in a thread-pool thread
    return "result";
}

glass main() -> Int {
    drink task: Task[String] = fetchData();
    // task is a TaskValue; program continues here while fetchData runs
    drink result: String = await task;
    pour(result);
    return 0;
}
```

The return type annotation `Task[T]` is conventional; the runtime does not enforce
it generically, but the `TaskValue` type is the actual return value of any `cascade glass` call.

### 4.3 `await`

```
await <expr>
```

AST node: `AwaitExpr(expr: Expr)`.

`await` blocks the calling thread until the `Task` resolves and returns the inner value.
If `<expr>` does not evaluate to a `TaskValue`, the interpreter raises:
`RuntimeFault("THIRSTY-E021", "await expects Task", span)`.

Default timeout is 60 seconds (`TaskValue._DEFAULT_TIMEOUT`). A `TimeoutError` is
raised as a Python `RuntimeError` if the future does not complete in time — this
propagates as an unhandled exception unless caught with `spillage/cleanup`.

`TaskValue.value` is a blocking property that calls `await_value()` internally.
It is accessible via member access: `task.value` is equivalent to `await task`.

### 4.4 Error Propagation from Async Context

If the body of a `cascade glass` function raises any exception (including `ThrownSignal`
or `RuntimeFault`), that exception is stored inside the `concurrent.futures.Future`.
When `await` calls `future.result(...)`, the stored exception is re-raised in the
`await`-ing thread.

This means errors thrown inside an async function propagate to the caller at the
`await` site, and can be caught with `spillage/cleanup` around the `await` expression.

### 4.5 Governance and Async

A governed async function uses `GovernedFunctionDecl` with `is_async = True`:

```thirstofgods
requires AuthorityClass.AC3
cascade glass runAuditedTask() -> Int {
    return 42;
}
```

The `_enforce_governance` check runs synchronously **before** the task is submitted
to the thread pool, in the calling thread. If governance fails, a `RuntimeFault` is
raised immediately and no `TaskValue` is created.

---

## 5. Error Handling (`spillage / cleanup / finally`)

### 5.1 Syntax

```
spillage {
    <protected-body>
} cleanup error (<binding>: <Type>) {
    <catch-body>
} [cleanup error (<binding>: <Type>) {
    <catch-body>
}] ... [cleanup finally {
    <finally-body>
}]
```

`spillage` is the opening keyword (maps to `try` in most languages).  
`cleanup error` introduces a catch clause.  
`cleanup finally` introduces a guaranteed-run block.

A `spillage` block requires at least one `cleanup error` or one `cleanup finally`
clause — the parser rejects bare `spillage { }` blocks without a handler.

### 5.2 AST Representation

```
TryStmt(
    try_block: BlockStmt,
    catches: list[CatchClause],   // may be empty if only cleanup finally
    finally_block: BlockStmt | None
)

CatchClause(
    name: str,          // binding name for the caught value
    type_name: str,     // "Error" matches any ThrownSignal
    block: BlockStmt
)
```

### 5.3 Execution Semantics

1. The interpreter executes `try_block`.
2. If `throw <expr>` is executed inside `try_block`, a `ThrownSignal(value)` is raised.
3. The interpreter walks `catches` in order:
   - If `catch.type_name == "Error"`, it matches any `ThrownSignal`.
   - Otherwise, `_match_catch` checks:
     - If the thrown value is a `UserInstance`, checks `instance.cls.name == type_name`.
     - Otherwise, checks `type_name == type(value).__name__`.
   - First match wins. The caught value is bound to `catch.name` in a new `Env`.
4. If no catch clause matches, the `ThrownSignal` propagates up the call stack.
5. `finally_block` (if present) runs unconditionally — whether or not an exception
   was thrown, and whether or not it was caught.

### 5.4 `throw`

```
throw <expr>;
```

AST node: `ThrowStmt(expr: Expr)`.

Evaluates `<expr>` and raises `ThrownSignal(value)`. Any Thirsty value may be thrown:
strings, numbers, class instances, or `empty`.

### 5.5 Re-throwing

A catch clause may re-throw by using `throw` inside its body:

```thirstofgods
spillage {
    throw "inner error";
} cleanup error (e: Error) {
    pour("caught: " + e);
    throw e;  // re-throw
}
```

The re-thrown `ThrownSignal` propagates normally to the enclosing scope.

### 5.6 `finally` Guarantee

The `cleanup finally` block runs even if:
- The protected body completed without error.
- An error was caught by an earlier `cleanup error` clause.
- An error was not caught (the `ThrownSignal` still propagates after `finally` executes).
- `return` exits the function from inside the protected body (Python's `finally`
  semantics apply at the interpreter level).

---

## 6. EBNF Grammar Extensions

The following grammar rules extend the base Thirsty-Lang grammar. Only the additions
are shown; base rules (`stmt`, `expr`, `type`, `glass-decl`, etc.) are unchanged.

```ebnf
(* Top-level declarations *)
declaration  ::= ... | class-decl

(* Class declaration *)
class-decl   ::= "fountain" IDENT "{" class-member* "}"

class-member ::= visibility? field-decl
               | visibility? method-decl
               | visibility? async-method-decl

visibility   ::= "public" | "private"

field-decl   ::= "drink" "mut"? IDENT ":" type ";"

method-decl  ::= "glass" IDENT "(" param-list? ")" ("->" type)? block

async-method-decl ::= "cascade" "glass" IDENT "(" param-list? ")" ("->" type)? block

(* Statements *)
stmt         ::= ... | spillage-stmt | throw-stmt

spillage-stmt ::= "spillage" block cleanup-clause+ 

cleanup-clause ::= "cleanup" "error" "(" IDENT ":" type ")" block
                 | "cleanup" "finally" block

throw-stmt   ::= "throw" expr ";"

(* Expressions *)
expr         ::= ... | await-expr | new-expr | this-expr

await-expr   ::= "await" expr

new-expr     ::= "new" IDENT "(" arg-list? ")"

this-expr    ::= "this"
```

---

## 7. Type System Additions

### 7.1 `Task[T]`

When a `cascade glass` function with return type `T` is called, the runtime returns
a `TaskValue` wrapping a `concurrent.futures.Future[T]`. The conventional annotation
is `Task[T]` (parsed as `GenericType(base="Task", args=[T])`).

The checker does not currently verify that `T` matches the actual return type of the
async function body; `Task[T]` is a documentation-level annotation in the current runtime.

`await` on a `Task[T]` yields a value of type `T`.

### 7.2 Error Types

The `error` keyword in a catch clause names a type used to match thrown values.
Currently recognised type names:

- `Error` — matches any `ThrownSignal` (wildcard catch).
- Any class name (e.g. `IOException`) — matches `UserInstance` whose class name equals
  the type name, or any Python value whose `type(value).__name__` equals the type name.

There is no base `Error` class that user-defined error classes must inherit from.
Instances of any `fountain` class may be thrown and caught by class name.

### 7.3 Class Instances

Variables holding class instances have the type name of their class (stored in
`Env.types[name]`). The interpreter does not perform static type checking on class
instances — all member accesses are resolved at runtime via `UserInstance.get`.

---

## 8. Integration with Governance

Thirst of Gods async functions participate fully in the UTF governance system.

### 8.1 Governed Async Functions

A `cascade glass` function that carries `requires` clauses is represented as a
`GovernedFunctionDecl` with `is_async = True`:

```thirstofgods
requires AuthorityClass.AC4
requires AuditTrail.Immutable
cascade glass sensitiveOperation() -> Int {
    return 0;
}
```

### 8.2 Enforcement Point

`_enforce_governance` is called inside `call_function`, **before** the thread-pool
submission. The sequence is:

1. `call_function(fn, args)` is entered.
2. `_enforce_governance(fn)` checks all `requires` clauses against `governance_context`.
3. If any clause fails, `RuntimeFault("THIRSTY-E050", ...)` is raised — no `TaskValue`
   is created and no thread is started.
4. Only if all clauses pass does the function body get submitted to `_ASYNC_POOL`.

### 8.3 `await` and Governance Errors

If the async body itself calls another governed function (without `await`'s
authority), the resulting `RuntimeFault` is captured inside the `Future` and
re-raised at the `await` site. Wrap the `await` in a `spillage` block to handle it.

### 8.4 `HumanAppealWindow` and `AuditTrail.Immutable`

These annotations are stored in `governance_context` at call time for audit logging:
- `HumanAppealWindow[N]` — recorded in `governance_context["appeal_windows"][fn_name]`.
- `AuditTrail.Immutable` — adds `fn_name` to `governance_context["audit_required"]`.

Neither annotation currently blocks execution; they are metadata for external audit systems.

---

## 9. Worked Examples

### 9.1 Counter Class

A simple stateful counter demonstrating `fountain`, `this`, `new`, and method calls.

```thirstofgods
fountain Counter {
    drink mut count: Int;
    drink label: String;

    glass init(start: Int, label: String) {
        this.count = start;
        this.label = label;
    }

    glass increment() {
        this.count = this.count + 1;
    }

    glass decrement() {
        thirsty (this.count > 0) {
            this.count = this.count - 1;
        }
    }

    glass value() -> Int {
        return this.count;
    }

    glass describe() -> String {
        return this.label + ": " + this.count;
    }
}

glass main() -> Int {
    drink mut c: Counter = new Counter(10, "hits");
    c.increment();
    c.increment();
    c.decrement();
    pour(c.describe());   // prints: hits: 11
    pour(c.value());      // prints: 11
    return 0;
}
```

### 9.2 Async HTTP-Calling Function with Error Handling

Demonstrates `cascade glass`, `await`, `spillage`, `cleanup error`, and `cleanup finally`.

```thirstofgods
// Simulates a network call that may fail.
cascade glass fetchRemote(url: String) -> String {
    thirsty (url == "") {
        throw "empty URL provided";
    }
    // Simulate async work (in real use, call a native module)
    return "data from " + url;
}

glass main() -> Int {
    // Breakpoints can be placed on any statement below
    drink task: Task[String] = fetchRemote("https://api.example.com/data");

    spillage {
        drink result: String = await task;
        pour("received: " + result);
    } cleanup error (e: Error) {
        pour("fetch failed: " + e);
    } cleanup finally {
        pour("fetch attempt complete");
    }

    // Bad call — will be caught
    drink bad: Task[String] = fetchRemote("");
    spillage {
        drink r2: String = await bad;
        pour(r2);
    } cleanup error (e: Error) {
        pour("caught: " + e);   // prints: caught: empty URL provided
    }

    return 0;
}
```

Expected output:
```
received: data from https://api.example.com/data
fetch attempt complete
caught: empty URL provided
```

### 9.3 Governed Async Task Runner

Demonstrates a governed `cascade glass` function, governance enforcement, and
the error path when authority is insufficient.

```thirstofgods
module governed_runner;
mode governed;

requires AuthorityClass.AC3
requires AuditTrail.Immutable
cascade glass runAuditedJob(jobId: String) -> String {
    pour("running job: " + jobId);
    return "done:" + jobId;
}

glass main() -> Int {
    // Assuming runtime is started with --authority AC3 or higher
    drink task: Task[String] = runAuditedJob("job-42");
    spillage {
        drink result: String = await task;
        pour("job result: " + result);
    } cleanup error (e: Error) {
        pour("governance error: " + e);
    }
    return 0;
}
```

To run with governance:
```
thirsty run governed_runner.thirsty --authority AC3
```

If the caller lacks `AC3` authority, `runAuditedJob(...)` raises a `RuntimeFault`
immediately (before the task starts), and the `spillage/cleanup error` block catches
the `THIRSTY-E050` fault message.

---

## 10. Relationship to Other UTF Tiers

Thirst of Gods sits within the Unified Thirst Framework (UTF) alongside:

| Tier                | File Extension     | Role                                          |
|---------------------|--------------------|-----------------------------------------------|
| Thirsty-Lang (core) | `.thirsty`         | Base language: declarations, flow, data       |
| Thirst of Gods      | `.thirstofgods`    | OOP + async additive layer                    |
| Shadow Thirst       | `.shadowthirst`    | Canonical promotion / impact analysis         |
| TARL                | `.tarl`            | Policy language (when/ALLOW/DENY/ESCALATE)    |
| TSCG                | (inline / `.tscg`) | Transition-state capability graph             |

All Thirst of Gods source compiles through the same pipeline:

```
Source text
  └─→ Lexer (produces Token list)
        └─→ Parser (produces AST with ClassDecl, TryStmt, AwaitExpr, etc.)
              └─→ Checker (static validation)
                    └─→ Interpreter (tree-walking evaluation)
```

The `cascade glass` concurrency model uses Python's `concurrent.futures.ThreadPoolExecutor`
directly — there is no event loop, no coroutines, and no separate async runtime.
`await` is a blocking call inside whichever thread executes it.

`GovernedFunctionDecl` is shared with the base Thirsty-Lang governed mode and is
not Thirst of Gods-exclusive; it becomes Thirst of Gods-relevant when combined with
`cascade` (async + governance).

---

## 11. Summary of AST Nodes Introduced by Thirst of Gods

| AST Node              | File     | Purpose                                        |
|-----------------------|----------|------------------------------------------------|
| `ClassDecl`           | `ast.py` | `fountain` class declaration                   |
| `VarDecl` (is_field)  | `ast.py` | Field declaration inside a `fountain`          |
| `FunctionDecl`        | `ast.py` | Method decl; `is_async=True` for `cascade glass` |
| `GovernedFunctionDecl`| `ast.py` | Method with `requires` clauses; `is_async` flag|
| `ThisExpr`            | `ast.py` | `this` keyword expression                      |
| `NewExpr`             | `ast.py` | `new ClassName(args)` expression               |
| `AwaitExpr`           | `ast.py` | `await <expr>` expression                      |
| `TryStmt`             | `ast.py` | `spillage { } cleanup ...` statement           |
| `CatchClause`         | `ast.py` | One `cleanup error (e: T) { }` arm             |
| `ThrowStmt`           | `ast.py` | `throw <expr>` statement                       |

---

## 12. Runtime Values Introduced by Thirst of Gods

| Value class     | Module          | Description                                     |
|-----------------|-----------------|-------------------------------------------------|
| `UserClass`     | `interpreter.py`| Built from `ClassDecl`; holds fields and methods|
| `UserInstance`  | `interpreter.py`| Live instance of a `UserClass`                  |
| `TaskValue`     | `interpreter.py`| Result of calling a `cascade glass` function    |

`TaskValue` wraps a `concurrent.futures.Future`. `.await_value()` blocks up to
`TaskValue._DEFAULT_TIMEOUT` seconds (default: 60 s). `.done` is a non-blocking
property that returns `True` if the future has completed.

---

*End of Thirst of Gods Specification v1.0*
