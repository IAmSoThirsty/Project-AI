#!/usr/bin/env python3
"""
Example Programs for Thirsty-Lang LLVM Compiler
================================================

This file contains example programs demonstrating various features
of the Thirsty-Lang LLVM compiler.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from compiler_llvm import ThirstyLLVMCompiler, LLVM_AVAILABLE


def print_separator(title):
    """Print a section separator."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def example_basic_arithmetic():
    """Example 1: Basic arithmetic operations."""
    print_separator("Example 1: Basic Arithmetic")
    
    source = """
    drink x = 10
    drink y = 20
    drink sum = x + y
    drink product = x * y
    drink quotient = y / x
    pour sum
    pour product
    pour quotient
    """
    
    print("Source Code:")
    print(source)
    print("\nCompiling to LLVM IR...")
    
    if LLVM_AVAILABLE:
        compiler = ThirstyLLVMCompiler(optimization_level=0)
        llvm_ir = compiler.compile_to_ir(source)
        print("\n--- Unoptimized LLVM IR (truncated) ---")
        print(llvm_ir[:800] + "\n...")
        
        print("\nOptimizing...")
        compiler_opt = ThirstyLLVMCompiler(optimization_level=2)
        optimized_ir = compiler_opt.compile_and_optimize(source)
        print("\n--- Optimized LLVM IR (truncated) ---")
        print(optimized_ir[:800] + "\n...")
    else:
        print("ERROR: llvmlite not installed. Install with: pip install llvmlite")


def example_control_flow():
    """Example 2: Control flow (if/else, loops)."""
    print_separator("Example 2: Control Flow")
    
    source = """
    drink n = 10
    drink counter = 1
    drink sum = 0
    
    while (counter <= n) {
        drink sum = sum + counter
        drink counter = counter + 1
    }
    
    pour sum
    
    if (sum > 50) {
        pour 1
    } else {
        pour 0
    }
    """
    
    print("Source Code:")
    print(source)
    print("\nCompiling with optimization level 2...")
    
    if LLVM_AVAILABLE:
        compiler = ThirstyLLVMCompiler(optimization_level=2)
        llvm_ir = compiler.compile_and_optimize(source)
        print("\n--- Optimized LLVM IR (truncated) ---")
        print(llvm_ir[:1000] + "\n...")
    else:
        print("ERROR: llvmlite not installed")


def example_functions():
    """Example 3: Function definitions."""
    print_separator("Example 3: Functions")
    
    source = """
    function square(x) {
        return x * x
    }
    
    function add(a, b) {
        return a + b
    }
    
    drink x = 5
    drink y = 10
    drink sq = square(x)
    drink total = add(sq, y)
    
    pour sq
    pour total
    """
    
    print("Source Code:")
    print(source)
    print("\nCompiling with function inlining...")
    
    if LLVM_AVAILABLE:
        compiler = ThirstyLLVMCompiler(optimization_level=3)
        llvm_ir = compiler.compile_and_optimize(source)
        print("\n--- Optimized LLVM IR (truncated) ---")
        print(llvm_ir[:1200] + "\n...")
    else:
        print("ERROR: llvmlite not installed")


def example_security_features():
    """Example 4: Security features."""
    print_separator("Example 4: Security Features")
    
    source = """
    drink user_input = 42
    sanitize user_input
    
    drink password = 12345
    shield password
    armor password
    
    drink suspicious_value = -1
    detect suspicious_value
    defend suspicious_value
    
    drink sensitive = 99
    morph sensitive
    
    pour user_input
    """
    
    print("Source Code:")
    print(source)
    print("\nCompiling with security metadata...")
    
    if LLVM_AVAILABLE:
        compiler = ThirstyLLVMCompiler(optimization_level=1)
        llvm_ir = compiler.compile_to_ir(source)
        print("\n--- LLVM IR (truncated) ---")
        print(llvm_ir[:1000] + "\n...")
        print("\nNote: Security features are currently compiled as metadata.")
        print("In a production compiler, these would trigger security passes.")
    else:
        print("ERROR: llvmlite not installed")


def example_optimization_comparison():
    """Example 5: Optimization comparison."""
    print_separator("Example 5: Optimization Comparison")
    
    source = """
    drink a = 5
    drink b = 10
    drink c = a + b
    drink d = c * 2
    drink e = d - a
    drink unused = 999
    pour e
    """
    
    print("Source Code:")
    print(source)
    
    if LLVM_AVAILABLE:
        for level in [0, 1, 2, 3]:
            print(f"\n--- Optimization Level {level} ---")
            compiler = ThirstyLLVMCompiler(optimization_level=level)
            llvm_ir = compiler.compile_and_optimize(source)
            lines = llvm_ir.count('\n')
            print(f"Lines of IR: {lines}")
            if level == 3:
                print("\nOptimized IR (truncated):")
                print(llvm_ir[:600] + "\n...")
    else:
        print("ERROR: llvmlite not installed")


def example_jit_execution():
    """Example 6: JIT compilation and execution."""
    print_separator("Example 6: JIT Execution")
    
    source = """
    drink result = 42
    pour result
    """
    
    print("Source Code:")
    print(source)
    print("\nJIT Compiling and Executing...")
    
    if LLVM_AVAILABLE:
        try:
            compiler = ThirstyLLVMCompiler()
            result = compiler.jit_compile_and_run(source)
            print(f"\nExecution Result (main return code): {result}")
            print("(Output from 'pour' statements goes to stdout)")
        except Exception as e:
            print(f"JIT Error: {e}")
    else:
        print("ERROR: llvmlite not installed")


def example_wasm_compilation():
    """Example 7: WebAssembly compilation."""
    print_separator("Example 7: WebAssembly Compilation")
    
    source = """
    drink x = 10
    drink y = 20
    drink sum = x + y
    pour sum
    """
    
    print("Source Code:")
    print(source)
    print("\nCompiling to WebAssembly...")
    
    if LLVM_AVAILABLE:
        try:
            import tempfile
            compiler = ThirstyLLVMCompiler(optimization_level=2)
            
            with tempfile.TemporaryDirectory() as tmpdir:
                output_path = os.path.join(tmpdir, "example.wasm")
                compiler.compile_to_wasm(source, output_path)
                
                obj_file = output_path + ".o"
                if os.path.exists(obj_file):
                    size = os.path.getsize(obj_file)
                    print(f"✓ WebAssembly object file created: {obj_file}")
                    print(f"  Size: {size} bytes")
                    print("\nNote: Use wasm-ld to link into final .wasm:")
                    print(f"  wasm-ld {obj_file} -o example.wasm --no-entry --export-all")
        except Exception as e:
            print(f"WASM Compilation Error: {e}")
    else:
        print("ERROR: llvmlite not installed")


def example_assembly_output():
    """Example 8: Native assembly generation."""
    print_separator("Example 8: Assembly Output")
    
    source = """
    drink x = 42
    pour x
    """
    
    print("Source Code:")
    print(source)
    print("\nGenerating native assembly...")
    
    if LLVM_AVAILABLE:
        try:
            compiler = ThirstyLLVMCompiler(optimization_level=2)
            asm = compiler.get_assembly(source)
            print("\n--- Assembly Code (first 40 lines) ---")
            lines = asm.split('\n')[:40]
            print('\n'.join(lines))
            if len(asm.split('\n')) > 40:
                print("\n... (truncated)")
        except Exception as e:
            print(f"Assembly Generation Error: {e}")
    else:
        print("ERROR: llvmlite not installed")


def example_complex_program():
    """Example 9: Complex program with all features."""
    print_separator("Example 9: Complex Program")
    
    source = """
    // Fibonacci-like sequence calculator
    function fib(n) {
        drink a = 0
        drink b = 1
        drink counter = 0
        
        while (counter < n) {
            drink temp = a + b
            drink a = b
            drink b = temp
            drink counter = counter + 1
        }
        
        return b
    }
    
    // Main program
    drink n = 10
    drink result = fib(n)
    
    shield result
    sanitize result
    
    if (result > 0) {
        pour result
    } else {
        pour 0
    }
    """
    
    print("Source Code:")
    print(source)
    print("\nCompiling with aggressive optimization...")
    
    if LLVM_AVAILABLE:
        compiler = ThirstyLLVMCompiler(optimization_level=3, enable_debug=True)
        llvm_ir = compiler.compile_and_optimize(source)
        print("\n--- Optimized LLVM IR (truncated) ---")
        print(llvm_ir[:1500] + "\n...")
    else:
        print("ERROR: llvmlite not installed")


def example_ir_and_native():
    """Example 10: Complete compilation pipeline."""
    print_separator("Example 10: Complete Compilation Pipeline")
    
    source = """
    drink greeting = 100
    pour greeting
    """
    
    print("Source Code:")
    print(source)
    
    if LLVM_AVAILABLE:
        import tempfile
        compiler = ThirstyLLVMCompiler(optimization_level=2)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Save LLVM IR
            ir_path = os.path.join(tmpdir, "program.ll")
            compiler.save_ir(source, ir_path)
            print(f"\n✓ LLVM IR saved to: {ir_path}")
            
            # Compile to native
            obj_path = compiler.compile_to_native(source, os.path.join(tmpdir, "program"))
            if os.path.exists(obj_path):
                size = os.path.getsize(obj_path)
                print(f"✓ Native object file created: {obj_path}")
                print(f"  Size: {size} bytes")
                print("\nTo create executable:")
                print(f"  gcc {obj_path} -o program")
            
            # Show IR
            print("\n--- LLVM IR Content (truncated) ---")
            with open(ir_path, 'r') as f:
                content = f.read()
                print(content[:800] + "\n...")
    else:
        print("ERROR: llvmlite not installed")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("  THIRSTY-LANG LLVM COMPILER - EXAMPLES")
    print("=" * 70)
    
    if not LLVM_AVAILABLE:
        print("\n⚠ WARNING: llvmlite is not installed!")
        print("Install it with: pip install llvmlite")
        print("\nExamples will show source code but cannot compile.\n")
    
    examples = [
        example_basic_arithmetic,
        example_control_flow,
        example_functions,
        example_security_features,
        example_optimization_comparison,
        example_jit_execution,
        example_wasm_compilation,
        example_assembly_output,
        example_complex_program,
        example_ir_and_native,
    ]
    
    for i, example in enumerate(examples, 1):
        try:
            example()
        except KeyboardInterrupt:
            print("\n\nExamples interrupted by user.")
            break
        except Exception as e:
            print(f"\nError in example {i}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("  All examples completed!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
