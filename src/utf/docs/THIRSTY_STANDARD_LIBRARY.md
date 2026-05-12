# Thirsty-Lang Standard Library v1.0

**Status**: Phase 1 — 3 namespaces, 9 module functions, 16 global builtins  
**Phase 2 target**: 15 namespaces (see expansion plan)

---

## 1. Global Built-in Functions

These functions are always available without any import. They are registered directly in the interpreter and type checker.

| Function | Signature | Effect |
|----------|-----------|--------|
| `length(s)` | `String -> Int` | Returns string length |
| `contains(s, sub)` | `(String, String) -> Bool` | Returns true if `sub` is a substring of `s` |
| `split(s, sep)` | `(String, String) -> Reservoir[String]` | Splits `s` on `sep` |
| `abs(x)` | `Int -> Int` | Absolute value |
| `min(a, b)` | `(Int, Int) -> Int` | Returns the smaller of two integers |
| `max(a, b)` | `(Int, Int) -> Int` | Returns the larger of two integers |
| `push(xs, v)` | `(Reservoir[T], T) -> Void` | Appends `v` to `xs` in-place |
| `pop(xs)` | `Reservoir[T] -> T` | Removes and returns the last element of `xs` |
| `size(xs)` | `Reservoir[T] -> Int` | Returns the number of elements in `xs` |
| `get(xs, i)` | `(Reservoir[T], Int) -> T` | Returns element at index `i` |
| `flood(xs, p)` | `(Reservoir[T], T) -> Reservoir[T]` | Extends `xs` with `p` in-place; returns `xs` |
| `condense(v)` | `Quenched[T] -> T` | Unwraps option; raises THIRSTY-E901 if empty |
| `evaporate(v)` | `Any -> Void` | Discards a value (no-op, used for effect) |
| `strain(xs, fn)` | `(Reservoir[T], T->Bool) -> Reservoir[T]` | Returns new reservoir of elements where `fn(e)` is true |
| `transmute(xs, fn)` | `(Reservoir[T], T->U) -> Reservoir[U]` | Returns new reservoir of `fn(e)` for each element |
| `distill(xs, seed, fn)` | `(Reservoir[T], U, (U,T)->U) -> U` | Reduces reservoir to a single value using `fn` |

---

## 2. `thirst::time`

```
import thirst::time
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `now()` | `() -> Int` | Returns current Unix timestamp (seconds) |
| `epoch_ms()` | `() -> Int` | Returns current Unix timestamp (milliseconds) |

---

## 3. `thirst::crypto`

```
import thirst::crypto
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `sha256(text)` | `String -> String` | Returns hex-encoded SHA-256 hash of `text` |
| `bless(text)` | `String -> String` | Returns `"blessed:"` + first 16 hex chars of SHA-256 hash |

> **Phase 2 change**: `bless` will be renamed `sign` and 3 new functions will be added (`hmac`, `random_bytes`, `uuid4`). Programs using `bless` must be updated after Phase 2.

---

## 4. `thirst::reservoir`

```
import thirst::reservoir
```

The module-level reservoir functions mirror the global builtins but are accessible via namespace syntax when explicit namespacing is preferred.

| Function | Signature | Description |
|----------|-----------|-------------|
| `size(xs)` | `Reservoir[T] -> Int` | Number of elements |
| `push(xs, v)` | `(Reservoir[T], T) -> Void` | Append in-place |
| `pop(xs)` | `Reservoir[T] -> T` | Remove last element in-place |
| `get(xs, i)` | `(Reservoir[T], Int) -> T` | Index access |
| `flood(xs, p)` | `(Reservoir[T], T) -> Reservoir[T]` | Extend in-place |

> Note: `strain`, `transmute`, and `distill` appear in the type checker's module type table but are not implemented in the runtime module dict. Use the global builtin forms of these functions, which are always available without import.

---

## 5. Phase 2 Planned Namespaces

The following namespaces will be added in Phase 2. They are not available in Phase 1.

| Namespace | Functions |
|-----------|-----------|
| `thirst::fs` | read_file, write_file, exists, list_dir, mkdir, remove |
| `thirst::path` | join, dirname, basename, extension, absolute, relative |
| `thirst::json` | parse, stringify, get, set |
| `thirst::http` | get, post, put, delete |
| `thirst::env` | get, set, all |
| `thirst::process` | run, exit, args, pid |
| `thirst::log` | info, warn, error, debug |
| `thirst::test` | assert_eq, assert_ne, assert_true, assert_raises, describe, it |
| `thirst::collections` | map, filter, reduce, sort, unique, flatten, zip |
| `thirst::net` | tcp_connect, tcp_listen, udp_send |
| `thirst::sqlite` | connect, query, execute, close |
| `thirst::yaml` | parse, dump |
| `thirst::toml` | parse, dump |
