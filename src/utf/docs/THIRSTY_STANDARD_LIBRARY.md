# Thirsty-Lang Standard Library v1.0

**Status**: Phase 2 — 15 namespaces, 16 global builtins  
**Import syntax**: `import "thirst::module" as alias;`  (string literal, `as` alias, and `;` are all required)

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
import "thirst::time" as t;
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `now()` | `() -> Int` | Returns current Unix timestamp (seconds) |
| `epoch_ms()` | `() -> Int` | Returns current Unix timestamp (milliseconds) |

---

## 3. `thirst::crypto`

```
import "thirst::crypto" as crypto;
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `sha256(text)` | `String -> String` | Returns hex-encoded SHA-256 hash of `text` |
| `sign(text)` | `String -> String` | Returns `"signed:"` + first 16 hex chars of SHA-256 hash |
| `hmac(key, data)` | `(String, String) -> String` | Returns hex-encoded HMAC-SHA-256 |
| `random_bytes(n)` | `Int -> String` | Returns `n` cryptographically random bytes as a hex string (length = `n*2`) |
| `uuid4()` | `() -> String` | Returns a random UUID v4 string (36 chars) |

---

## 4. `thirst::reservoir`

```
import "thirst::reservoir" as res;
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

## 5. `thirst::fs`

```
import "thirst::fs" as fs;
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `read_file(path)` | `String -> String` | Returns file contents as a string |
| `write_file(path, text)` | `(String, String) -> Void` | Writes text to file |
| `exists(path)` | `String -> Bool` | Returns true if path exists |
| `list_dir(path)` | `String -> Reservoir[String]` | Lists directory entries |
| `mkdir(path)` | `String -> Void` | Creates directory (including parents) |
| `remove(path)` | `String -> Void` | Deletes file or empty directory |

---

## 6. `thirst::path`

```
import "thirst::path" as p;
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `join(a, b)` | `(String, String) -> String` | Joins path components |
| `dirname(path)` | `String -> String` | Returns parent directory |
| `basename(path)` | `String -> String` | Returns final component of path |
| `extension(path)` | `String -> String` | Returns file extension (e.g. `.thirsty`) |
| `absolute(path)` | `String -> String` | Returns absolute path |
| `relative(path, start)` | `(String, String) -> String` | Returns path relative to start |

---

## 7. `thirst::json`

```
import "thirst::json" as json;
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `parse(text)` | `String -> Any` | Parses JSON string into a Thirsty value |
| `stringify(value)` | `Any -> String` | Serializes a Thirsty value to JSON |
| `get(obj, key)` | `(Any, String) -> Any` | Reads a field from a parsed JSON object |
| `set(obj, key, val)` | `(Any, String, Any) -> Any` | Sets a field and returns updated object |

---

## 8. `thirst::http`

```
import "thirst::http" as http;
```

> Return type is `Any` (Phase 2). Will be tightened to `Result[Response, HttpError]` in Phase 3.

| Function | Signature | Description |
|----------|-----------|-------------|
| `get(url)` | `String -> Any` | HTTP GET; returns response body string |
| `post(url, body)` | `(String, String) -> Any` | HTTP POST with body |
| `put(url, body)` | `(String, String) -> Any` | HTTP PUT with body |
| `delete(url)` | `String -> Any` | HTTP DELETE |

---

## 9. `thirst::env`

```
import "thirst::env" as env;
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `get(name)` | `String -> Any` | Returns env var value or `empty` |
| `set(name, val)` | `(String, String) -> Void` | Sets env var for current process |
| `all()` | `() -> Any` | Returns all env vars as a map |

---

## 10. `thirst::process`

```
import "thirst::process" as proc;
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `run(cmd)` | `String -> Any` | Runs shell command; returns stdout string |
| `exit(code)` | `Int -> Void` | Exits interpreter with given exit code |
| `args()` | `() -> Reservoir[String]` | Returns command-line arguments |
| `pid()` | `() -> Int` | Returns current process ID |

---

## 11. `thirst::log`

```
import "thirst::log" as log;
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `info(msg)` | `String -> Void` | Logs at INFO level |
| `warn(msg)` | `String -> Void` | Logs at WARN level |
| `error(msg)` | `String -> Void` | Logs at ERROR level |
| `debug(msg)` | `String -> Void` | Logs at DEBUG level |

---

## 12. `thirst::test`

```
import "thirst::test" as t;
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `assert_eq(a, b)` | `(Any, Any) -> Void` | Raises if `a != b` |
| `assert_ne(a, b)` | `(Any, Any) -> Void` | Raises if `a == b` |
| `assert_true(v)` | `Any -> Void` | Raises if `v` is falsy |
| `assert_raises(fn)` | `Any -> Void` | Raises if calling `fn()` does not throw |
| `describe(label, fn)` | `(String, Any) -> Void` | Groups test cases under a label |
| `it(label, fn)` | `(String, Any) -> Void` | Defines a single test case |

---

## 13. `thirst::collections`

```
import "thirst::collections" as col;
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `map(xs, fn)` | `(Reservoir[T], T->U) -> Reservoir[U]` | Transforms each element via `fn` |
| `filter(xs, fn)` | `(Reservoir[T], T->Bool) -> Reservoir[T]` | Keeps elements where `fn(x)` is true |
| `reduce(xs, seed, fn)` | `(Reservoir[T], U, (U,T)->U) -> U` | Folds reservoir to a single value |
| `sort(xs)` | `Reservoir[T] -> Reservoir[T]` | Returns sorted copy |
| `unique(xs)` | `Reservoir[T] -> Reservoir[T]` | Returns copy with duplicates removed |
| `flatten(xs)` | `Reservoir[Reservoir[T]] -> Reservoir[T]` | Flattens one level of nesting |
| `zip(a, b)` | `(Reservoir[T], Reservoir[U]) -> Reservoir[Any]` | Pairs elements by index |

---

## 14. `thirst::net`

```
import "thirst::net" as net;
```

> Return types are `Any` (Phase 2). Will be tightened to `Task[Connection]`/`Task[Server]` in Phase 3.

| Function | Signature | Description |
|----------|-----------|-------------|
| `tcp_connect(host, port)` | `(String, Int) -> Any` | Opens a TCP connection |
| `tcp_listen(port)` | `Int -> Any` | Starts a TCP listener |
| `udp_send(host, port, data)` | `(String, Int, String) -> Void` | Sends a UDP datagram |

---

## 15. `thirst::sqlite`

```
import "thirst::sqlite" as db;
```

| Function | Signature | Description |
|----------|-----------|-------------|
| `connect(path)` | `String -> Any` | Opens or creates SQLite database |
| `query(conn, sql)` | `(Any, String) -> Reservoir[Any]` | Executes SELECT; returns rows |
| `execute(conn, sql)` | `(Any, String) -> Void` | Executes INSERT/UPDATE/DELETE |
| `close(conn)` | `Any -> Void` | Closes database connection |

---

## 16. `thirst::yaml`

```
import "thirst::yaml" as yaml;
```

> Requires PyYAML (`pip install pyyaml`). Raises `ImportError` with install instructions if unavailable.

| Function | Signature | Description |
|----------|-----------|-------------|
| `parse(text)` | `String -> Any` | Parses YAML string |
| `dump(value)` | `Any -> String` | Serializes value to YAML |

---

## 17. `thirst::toml`

```
import "thirst::toml" as toml;
```

> Uses stdlib `tomllib` (Python 3.11+) for reading. Falls back to `tomli` if available.

| Function | Signature | Description |
|----------|-----------|-------------|
| `parse(text)` | `String -> Any` | Parses TOML string |
| `dump(value)` | `Any -> String` | Serializes value to TOML |
