<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `taar/` — Thirsty-lang Aware Automated Runner

> **Sovereign build automation.** TAAR watches your source tree, detects changes, builds a dependency graph, and executes only what needs to run — deterministically and with full audit trail.

## Modules

| Module | Purpose |
|---|---|
| **`cli.py`** | Typer-based CLI — `taar run`, `taar watch`, `taar status` |
| **`watcher.py`** | File system watcher — detects source changes in real-time |
| **`change_detector.py`** | Determines which modules are affected by a file change |
| **`graph.py`** | Dependency graph — builds and traverses module relationships |
| **`scheduler.py`** | Task scheduler — orders execution based on dependency graph |
| **`executor.py`** | Task executor — runs build/test/deploy tasks with isolation |
| **`cache.py`** | Build cache — skips unchanged artifacts using content-hash |
| **`reporter.py`** | Execution reporter — produces build reports and audit entries |
| **`config.py`** | TAAR configuration — `taar.toml` parsing and defaults |
| **`__init__.py`** | Package exports |

## Architecture

```
File Change → [watcher] → [change_detector] → [graph]
                                                  │
                                                  ↓
                              [scheduler] → [executor] → [reporter]
                                  │               │
                                  ↓               ↓
                              [cache]        Build Output
```

## CLI Usage

```bash
# Run affected tasks
taar run

# Watch for changes and auto-run
taar watch

# Show dependency graph
taar status

# Force full rebuild (skip cache)
taar run --force
```

## Configuration

TAAR reads from `taar.toml` in the project root:

```toml
[taar]
watch_dirs = ["project_ai", "src", "tests"]
cache_dir = ".taar_cache"
parallel = true
max_workers = 4

[taar.tasks]
test = "pytest tests/ -v"
lint = "ruff check ."
build = "python -m build"
```

## Entry Point

Registered in `pyproject.toml`:

```toml
[project.scripts]
taar = "taar.cli:cli_main"
```
