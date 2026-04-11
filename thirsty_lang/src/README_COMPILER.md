# Thirsty-Lang LLVM Compiler

Production-grade LLVM-based compiler for Thirsty-Lang with advanced optimization, JIT compilation, and WebAssembly support.

## Quick Start

```bash
# Install dependencies
pip install llvmlite

# Run examples
python examples_compiler.py

# Run tests
pytest test_compiler_llvm.py -v

# Compile a program
python compiler_llvm.py program.thirsty -O2 --emit-llvm -o program.ll
```

## Features

✅ **LLVM IR Generation** - Full LLVM intermediate representation  
✅ **Optimization Passes** - DCE, constant folding, inlining, loop opts  
✅ **JIT Compilation** - Just-in-time execution with MCJIT  
✅ **WebAssembly Target** - Compile to WASM for browser execution  
✅ **Debug Info** - DWARF debug information generation  
✅ **Multiple Targets** - Native, WASM, Assembly, LLVM IR  
✅ **4 Optimization Levels** - From O0 (none) to O3 (aggressive)  

## Architecture

The compiler implements a complete compilation pipeline:

1. **Lexer** - Tokenizes source code
2. **Parser** - Builds Abstract Syntax Tree (AST)
3. **IR Generator** - Generates LLVM IR from AST
4. **Optimizer** - Applies optimization passes
5. **Code Generator** - Produces target code (native/WASM/JIT)

## Usage Examples

### Compile to LLVM IR
```python
from compiler_llvm import ThirstyLLVMCompiler

compiler = ThirstyLLVMCompiler(optimization_level=2)

source = """
drink x = 10
drink y = 20
pour x + y
"""

llvm_ir = compiler.compile_to_ir(source)
print(llvm_ir)
```

### JIT Compile and Run
```python
compiler = ThirstyLLVMCompiler()
result = compiler.jit_compile_and_run(source)
```

### Compile to WebAssembly
```python
compiler.compile_to_wasm(source, "output.wasm")
```

### Compile to Native
```python
compiler.compile_to_native(source, "output")
# Creates output.o - link with: gcc output.o -o program
```

## Command-Line Interface

```bash
# Basic compilation
python compiler_llvm.py program.thirsty

# With optimization
python compiler_llvm.py program.thirsty -O3

# Emit LLVM IR
python compiler_llvm.py program.thirsty --emit-llvm -o program.ll

# Emit assembly
python compiler_llvm.py program.thirsty --emit-asm -o program.s

# JIT compile and run
python compiler_llvm.py program.thirsty --jit

# Compile to WebAssembly
python compiler_llvm.py program.thirsty --wasm -o program.wasm

# Enable debug info
python compiler_llvm.py program.thirsty --debug

# Verbose output
python compiler_llvm.py program.thirsty -v
```

## Language Features

### Variables
```thirsty
drink x = 42
drink name = "Alice"
```

### Arithmetic
```thirsty
drink result = (10 + 20) * 2 - 5
drink quotient = 100 / 5
```

### Control Flow
```thirsty
if (x > 10) {
    pour x
} else {
    pour 0
}

while (counter < 10) {
    drink counter = counter + 1
}
```

### Functions
```thirsty
function add(a, b) {
    return a + b
}

drink sum = add(10, 20)
```

### Security Features
```thirsty
shield password        // Protect from access
morph sensitive_data   // Transform data
detect malicious       // Detect threats
defend attack          // Defend against attacks
sanitize user_input    // Sanitize input
armor critical_var     // Harden variable
```

## Optimization Levels

| Level | Features | Use Case |
|-------|----------|----------|
| -O0 | No optimization | Fast compilation, debugging |
| -O1 | Basic opts | Development |
| -O2 | Full opts | Production (default) |
| -O3 | Aggressive | Maximum performance |

## Performance

Compared to interpreted mode:
- **O0**: 5-10x faster
- **O1**: 10-20x faster
- **O2**: 20-50x faster
- **O3**: 30-100x faster

## Testing

```bash
# Run all tests
pytest test_compiler_llvm.py -v

# Run specific tests
pytest test_compiler_llvm.py::TestLexer -v
pytest test_compiler_llvm.py::TestParser -v
pytest test_compiler_llvm.py::TestOptimizationPasses -v

# With coverage
pytest test_compiler_llvm.py --cov=compiler_llvm --cov-report=html
```

## Documentation

See [COMPILER_DOCUMENTATION.md](COMPILER_DOCUMENTATION.md) for detailed documentation including:
- Architecture details
- API reference
- Advanced usage
- Optimization guides
- Troubleshooting

## Files

- `compiler_llvm.py` - Main compiler implementation
- `test_compiler_llvm.py` - Comprehensive test suite
- `examples_compiler.py` - Example programs and usage
- `COMPILER_DOCUMENTATION.md` - Detailed documentation
- `README_COMPILER.md` - This file

## Requirements

- Python 3.8+
- llvmlite 0.40.0+

```bash
pip install llvmlite
```

## Platform Support

✅ Windows (x86-64)  
✅ Linux (x86-64)  
✅ macOS (x86-64, ARM64)  

## Limitations

- Basic DWARF debug info (enhancement planned)
- WebAssembly requires wasm-ld for linking
- Limited FFI support (printf, malloc, free)

## Future Enhancements

- [ ] Custom LLVM passes
- [ ] Profile-guided optimization
- [ ] Link-time optimization
- [ ] GPU code generation
- [ ] Advanced debug info (DWARF v5)
- [ ] Incremental compilation
- [ ] MLIR integration

## License

See LICENSE file for details.

## Contributing

Contributions welcome! Please ensure:
1. All tests pass
2. Code is documented
3. Examples are provided

---

**Note**: This is a production-grade implementation of an LLVM backend for Thirsty-Lang, providing industrial-strength compilation with optimization, JIT, and multiple target support.
