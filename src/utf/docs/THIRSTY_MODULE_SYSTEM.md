# Thirsty-Lang Module System v1.0

---

## 1. Overview

Thirsty-Lang programs are organized into modules. A module is a single source file. The module system handles import resolution, namespace access, module caching, and package discovery.

---

## 2. Module Header

Every source file may begin with an optional module header:

```
module <name>
mode core | governed
```

Both lines are optional. When absent, the module name defaults to the filename stem and the mode defaults to `core`. The header, if present, must appear before any declarations.

---

## 3. Import Forms

### 3.1 Namespace Import

```
import thirst::module
import thirst::module as alias
```

Imports a built-in standard library namespace. After import, members are accessed via `module.name` (or `alias.name` if aliased). Namespace imports do not consume disk I/O — they resolve to built-in Python dicts registered in `module_system.py`.

**Available built-in namespaces (Phase 1):**
- `thirst::time` — `now`, `epoch_ms`
- `thirst::crypto` — `sha256`, `bless`
- `thirst::reservoir` — `size`, `push`, `pop`, `get`, `flood`

### 3.2 Relative Import

```
from "./path/to/file.thirsty" import name
from "../sibling.thirsty" import name
```

Resolves relative to the importing file's directory. The path must begin with `./` or `../`. Only `.thirsty` and `.thirstofgods` files are valid targets.

### 3.3 Package Import

```
import pkg_name
import pkg_name::subpath
```

Resolves against the package registry. The package registry is a file-based store managed by `package_manager.py`. The interpreter walks `project_search_roots()` to find the package directory, then reads its manifest (`thirsty.toml` or `thirsty.json`) to locate the entry file.

If `::subpath` is given, the interpreter looks for `src/<subpath>.thirsty` within the package directory.

---

## 4. Module Caching

Each module path (resolved to an absolute file path) is cached after first load. Subsequent imports of the same path return the cached `ModuleValue` without re-parsing or re-executing. This ensures:
- Circular imports do not cause infinite loops (the first import begins execution; the second import hits the cache)
- Side effects in module-level code execute exactly once

---

## 5. Name Resolution at Import

For file-based imports (`from "..." import name`), the checker:
1. Parses the target file
2. Extracts all top-level `glass`, `fountain`, and `drink` declarations as the exported symbol table
3. Verifies the imported name exists in that table (THIRSTY-E011 if absent)
4. Binds the imported name in the current scope with the resolved type

For built-in namespace imports, the type information comes from `builtin_module_types()` in `module_system.py`.

---

## 6. Mode Interaction

| Importing module | Imported module | Permitted? |
|-----------------|-----------------|-----------|
| `mode core` | `mode core` | Yes |
| `mode core` | `mode governed` | Yes — governance gates inactive for the importer |
| `mode governed` | `mode core` | Yes — core modules run without governance gates |
| `mode governed` | `mode governed` | Yes — both modules subject to governance routing |

`mode` is a per-module property. Importing a `governed` module from a `core` module does not activate governance gates for the importing module. The governance context propagates only when the root program declares `mode governed`.

---

## 7. Module Search Path

Resolution priority (highest first):
1. Built-in namespaces (`thirst::*`)
2. Relative paths (`./`, `../`)
3. Package registry (file-based, project-local)

There is no global install path. Packages are always project-local. `thirsty.lock.json` pins exact resolved paths and hashes for reproducible builds.

---

## 8. Errors

| Code | Trigger |
|------|---------|
| THIRSTY-E001 | Malformed module path syntax |
| THIRSTY-E011 | Imported name not found in target module |
| FileNotFoundError | Module file not found on disk (propagated as THIRSTY-E001 at parse time) |
