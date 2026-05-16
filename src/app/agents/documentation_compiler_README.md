# DocumentationCompilerAgent

Evidence-based technical documentation compiler for Project-AI systems.

## Quick Start

```python
from app.agents.documentation_compiler import DocumentationCompilerAgent
from app.core.cognition_kernel import CognitionKernel

# Initialize with governance
kernel = CognitionKernel()
doc_agent = DocumentationCompilerAgent(kernel=kernel)

# Compile documentation for a system
doc_path = doc_agent.compile_system_documentation(
    system_name="MySystem",
    evidence_paths=[
        "src/app/core/my_system.py",
        "tests/test_my_system.py",
        "config/my_system.yaml"
    ]
)

print(f"✅ Documentation: {doc_path}")
```

## What It Does

Converts **verified code, tests, and configuration** into clean technical documentation.

**Rules:**
- ✅ No invented details
- ✅ No exaggerated claims
- ✅ Distinguishes design from verified behavior
- ✅ Preserves Project-AI terminology
- ✅ Emphasizes governance-before-execution

## Features

### 1. Evidence Extraction

```python
# Extract from code
evidence = doc_agent.extract_evidence("src/my_module.py")
# Returns: classes, functions, docstrings, governance markers

# Extract from tests
evidence = doc_agent.extract_evidence("tests/test_my_module.py")
# Returns: test functions, fixtures, assertions, coverage type

# Extract from config
evidence = doc_agent.extract_evidence("config/settings.yaml")
# Returns: config keys, governance settings
```

### 2. Documentation Compilation

Generates 10-section technical documentation:

1. Purpose
2. Architecture
3. Governance Model
4. Execution Flow
5. Security Model
6. Evidence Model
7. Tests and Verification
8. Failure Modes
9. Deployment Considerations
10. Open Risks / Unresolved Items

### 3. Documentation Verification

```python
# Verify existing docs against current code
result = doc_agent.verify_documentation(
    doc_path="docs/my_system.md",
    evidence_paths=["src/my_system.py", "tests/test_my_system.py"]
)

if result["status"] == "discrepancies_found":
    for issue in result["discrepancies"]:
        print(f"⚠️  {issue}")
```

## Installation

Already included in Project-AI. No additional installation needed.

**Dependencies:**
- Python 3.10+
- `pyyaml`
- Project-AI core (CognitionKernel, KernelRoutedAgent)

## Tests

```bash
# Run all tests (22 test cases)
pytest tests/test_documentation_compiler.py -v

# Run with coverage
pytest tests/test_documentation_compiler.py --cov=app.agents.documentation_compiler --cov-report=html
```

All 22 tests pass ✅

## Example Output

**Input:**
```python
doc_agent.compile_system_documentation(
    system_name="InvariantEngine",
    evidence_paths=["src/app/core/invariant_engine.py"]
)
```

**Output:** `docs/compiled/invariant_engine_technical_documentation.md`

```markdown
# InvariantEngine — Technical Documentation

## Purpose
[Extracted from docstrings and evidence]

## Architecture
**Core Classes:** `InvariantEngine`, `Invariant`, `InvariantResult`
✅ **Governance Integration:** All operations route through CognitionKernel

## Tests and Verification
**Test Coverage:** 15 test case(s) verified
- ✅ Unit tests present
- ✅ Integration tests present
```

## Configuration

```python
# Custom output directory
doc_agent = DocumentationCompilerAgent(
    kernel=kernel,
    output_dir="custom/docs/path"
)

# Skip tests section
doc_path = doc_agent.compile_system_documentation(
    system_name="MySystem",
    evidence_paths=["src/my_system.py"],
    include_tests=False
)

# Skip code samples
doc_path = doc_agent.compile_system_documentation(
    system_name="MySystem",
    evidence_paths=["src/my_system.py"],
    include_code_samples=False
)
```

## Governance Integration

All operations route through CognitionKernel:

```python
# When agent method is called...
doc_agent.compile_system_documentation(...)
           ↓
    _execute_through_kernel()
           ↓
    CognitionKernel.process()
           ↓
   [Governance validation]
           ↓
    _do_compile_system_documentation()
           ↓
        [Result]
```

**Risk Level:** `low` (read-only operations)

## Supported File Types

| Type | Extensions | Evidence Extracted |
|------|------------|-------------------|
| **Code** | `.py` | Classes, functions, docstrings, imports, governance markers |
| **Tests** | `test_*.py`, `*_test.py` | Test functions, fixtures, assertions, coverage type |
| **Config** | `.yaml`, `.yml`, `.json` | Config keys, governance settings, security config |

## Known Limitations

- Python-only code analysis (no JS/Go/etc.)
- Regex-based extraction (no AST analysis)
- No automatic diagram generation
- Basic verification (keyword matching only)

## Future Enhancements

- AST-based code analysis
- Multi-language support (JS, Go, Rust)
- Auto-generated architecture diagrams
- Incremental documentation updates
- CI/CD integration for continuous verification

## Documentation

- **Technical Docs:** `docs/compiled/documentation_compiler_agent_technical_documentation.md`
- **Source Code:** `src/app/agents/documentation_compiler.py`
- **Tests:** `tests/test_documentation_compiler.py`

## License

Part of Project-AI. See repository LICENSE.

---

**Agent Type:** Documentation Compiler  
**Governance:** ✅ Full CognitionKernel routing  
**Test Coverage:** 22/22 tests pass  
**Status:** Production-ready
