# Thirsty-Lang Conformance Specification v1.0

This document defines what it means for a Thirsty-Lang implementation to be conformant. A conformant implementation must pass all tests in the conformance suite at `conformance/` (relative to the repository root).

---

## 1. Test Descriptor Format

Each conformance test consists of:
1. A `.thirsty` source file
2. A `.json` descriptor file with the same name

**Descriptor schema:**

```json
{
  "file": "syntax/basic_conditionals.thirsty",
  "description": "thirsty/hydrated evaluates correct branch",
  "expected_stdout": "Adult\n",
  "expected_exit_code": 0,
  "expected_diagnostics": []
}
```

| Field | Type | Description |
|-------|------|-------------|
| `file` | string | Path to the `.thirsty` source file, relative to `conformance/` |
| `description` | string | Human-readable description of what is being tested |
| `expected_stdout` | string | Exact expected output on stdout (including newlines) |
| `expected_exit_code` | integer | Expected process exit code (0 = success, 1 = error) |
| `expected_diagnostics` | array | List of expected diagnostic objects (see below) |

**Diagnostic object:**
```json
{"code": "THIRSTY-E021", "message_contains": "type mismatch"}
```
- `code` is required and must match exactly
- `message_contains` is optional; if present, the error message must contain the substring

For tests that expect a runtime or check error, set `expected_exit_code` to `1` and list the expected diagnostics. `expected_stdout` may be `""` for error tests.

---

## 2. Runner Invocation

The conformance runner invokes the interpreter via subprocess. It must NOT assume `thirsty` is on PATH. Use:

```python
import subprocess, sys, os

result = subprocess.run(
    [sys.executable, "-m", "thirsty_lang.cli", "run", test_file],
    capture_output=True,
    text=True,
    env={**os.environ, "PYTHONPATH": "src/utf", "PYTHONIOENCODING": "utf-8"},
)
```

This ensures the test suite works in development mode without a pip install.

---

## 3. Pass Criteria

A test passes when ALL of the following hold:
1. `result.returncode == expected_exit_code`
2. `result.stdout == expected_stdout` (exact match, including trailing newlines)
3. For each diagnostic in `expected_diagnostics`:
   - The combined stderr output contains the diagnostic code
   - If `message_contains` is specified, the error message contains the substring

A test fails if any criterion is not met.

---

## 4. Suite Structure

```
conformance/
  runner.py               # Test runner (reads descriptors, runs interpreter, reports)
  runner_js.py            # JS runner (Phase 4 — runs Node.js implementation)
  syntax/                 # Tests for every grammar production
  types/                  # Type checker tests (valid programs + expected-error cases)
  modules/                # Import resolution, namespace access, module caching
  errors/                 # Error codes, spillage/cleanup/finally
  stdlib/                 # One test per stdlib function
  security/               # shield, sanitize, armor, morph, detect, defend
  governance/             # TARL allow/deny/escalate, mode governed (Phase 3)
  shadow_mutation/        # promote/reject tests for each Shadow Thirst analyzer
  tarl_policy/            # Policy eval: allow, deny, escalate, default deny
```

---

## 5. Minimum Coverage Requirements

A conformant implementation must pass at least **200 tests** covering:

| Category | Min tests |
|----------|-----------|
| Syntax (all grammar productions) | 40 |
| Type system (valid + error cases) | 40 |
| Standard library (per-function) | 25 |
| Error codes (per-code) | 20 |
| Module system | 15 |
| Error handling (spillage/cleanup/finally) | 15 |
| Security expressions | 10 |
| Shadow Thirst (per-analyzer) | 12 |
| TARL policy evaluation | 10 |
| Mode declaration (core/governed) | 5 |
| Miscellaneous | 8 |

---

## 6. Independence Requirement

To be recognized as an **independent conformant implementation**, an implementation must:
1. Be written in a different language than the Python reference interpreter
2. Pass the conformance suite using `runner_js.py` (or equivalent runner) without relying on any Python code
3. Achieve 200/200 pass rate against the same test descriptors used by the Python runner

The JS implementation at `src/thirsty_lang/` is the current conformance target for Phase 4 independence verification.

---

## 7. Conformance Versions

The conformance suite version is tied to the language specification version. A suite versioned `1.x` tests conformance to Thirsty-Lang Core v1.x. Breaking language changes require a new suite version.

Phase 3 governance features require separate governance conformance tests. These are gated on `mode governed` and are not required for Core 1.x conformance certification.
