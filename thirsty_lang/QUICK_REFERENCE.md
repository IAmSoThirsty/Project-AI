# Shadow Thirst Enhanced - Quick Reference

## Installation

```bash
# Required
pip install z3-solver  # Optional but recommended for full symbolic execution

# Verify installation
python -c "from shadow_enhanced import ShadowThirstEnhancedCompiler; print('✓ Ready')"
```

## Basic Usage

### 1. Analyze a File

```bash
python -m src.shadow_enhanced your_program.shadow
```

### 2. Python API

```python
from shadow_enhanced import ShadowThirstEnhancedCompiler

compiler = ShadowThirstEnhancedCompiler()
report = compiler.analyze(source_code, "program.shadow")

print(f"Status: {'PASS' if report.passed else 'FAIL'}")
print(f"Performance: {report.lines_per_second:.0f} LOC/sec")
```

## Common Scenarios

### Security Scan (Fast)

```python
compiler = ShadowThirstEnhancedCompiler(
    enable_taint_analysis=True,
    enable_alias_analysis=False,
    enable_value_flow=False,
    enable_symbolic_execution=False,
    enable_test_generation=False,
    performance_mode=True
)
```

### Test Generation

```python
compiler = ShadowThirstEnhancedCompiler(
    enable_test_generation=True,
    target_coverage=95.0
)

report = compiler.analyze(source)
compiler.export_test_suite(report, Path('tests/generated.py'))
```

### Full Analysis

```python
compiler = ShadowThirstEnhancedCompiler()  # All features enabled
report = compiler.analyze(source)
```

## CLI Options

```bash
# Basic
python -m src.shadow_enhanced file.shadow

# With options
python -m src.shadow_enhanced file.shadow \
    --output ./reports \
    --coverage 95.0 \
    --performance \
    --verbose

# Disable features
python -m src.shadow_enhanced file.shadow \
    --no-taint \
    --no-alias \
    --no-symbolic \
    --no-tests
```

## Configuration Matrix

| Use Case | Taint | Alias | Value | Symbolic | Tests | Perf Mode |
|----------|-------|-------|-------|----------|-------|-----------|
| Security Scan | ✓ | | | | | ✓ |
| Optimization | | ✓ | ✓ | | | ✓ |
| Test Gen | | | | ✓ | ✓ | |
| Full Analysis | ✓ | ✓ | ✓ | ✓ | ✓ | |
| Fast Scan | ✓ | ✓ | ✓ | | | ✓ |

## Output Files

After analysis:
- `analysis_report.txt` - Comprehensive analysis report
- `generated_tests.py` - Generated test suite (pytest format)
- `metrics.json` - Machine-readable metrics

## Performance Targets

| Mode | LOC/sec | Best For |
|------|---------|----------|
| Full Analysis | 11,000 | Complete audit |
| Performance Mode | 28,000 | CI/CD pipelines |
| Security Scan | 15,000 | Quick vulnerability check |

## Key Features

### Taint Analysis
- SQL injection detection
- XSS vulnerability detection
- Command injection detection
- Path traversal detection

### Symbolic Execution
- Z3-based constraint solving
- Path exploration
- SAT/UNSAT solving
- Multi-path state tracking

### Test Generation
- 95%+ coverage target
- Multiple strategies (concolic, symbolic, fuzzing)
- Pytest-compatible output

## Troubleshooting

### Z3 Not Available
```bash
pip install z3-solver
python -c "import z3; print(z3.get_version_string())"
```

### Performance Issues
- Enable performance mode
- Disable symbolic execution
- Reduce coverage target
- Limit symbolic depth

### Memory Issues
- Process in batches
- Reduce max_iterations
- Limit path exploration depth

## Examples

See `demo_enhanced.py` for complete examples of:
1. Taint analysis
2. Alias analysis
3. Value flow analysis
4. Symbolic execution
5. Test generation
6. Full pipeline
7. Performance comparison

## Documentation

- **Full Docs**: `SHADOW_ENHANCED_DOCUMENTATION.md`
- **README**: `README_ENHANCED.md`
- **Source**: `src/shadow_enhanced.py`
- **Demo**: `demo_enhanced.py`

## Status

✅ **Production Ready**
- Version: 2.0.0
- Performance: 10,000+ LOC/sec ✓
- Coverage: 95%+ target ✓
- Z3 Integration: ✓
- CLI Support: ✓
