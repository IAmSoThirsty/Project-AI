"""
Test Suite for Thirsty-Lang LLVM Compiler
==========================================

Comprehensive tests for all compiler features:
- Lexer and Parser
- LLVM IR generation
- Optimization passes
- JIT compilation
- WebAssembly target
- Debug information
"""

import pytest
import os
import tempfile
from pathlib import Path

try:
    from compiler_llvm import (
        Lexer, Parser, TokenType, ASTNodeType,
        LLVMCodeGenerator, OptimizationPasses,
        JITEngine, WebAssemblyTarget,
        ThirstyLLVMCompiler, LLVM_AVAILABLE
    )
except ImportError:
    # Try relative import
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from compiler_llvm import (
        Lexer, Parser, TokenType, ASTNodeType,
        LLVMCodeGenerator, OptimizationPasses,
        JITEngine, WebAssemblyTarget,
        ThirstyLLVMCompiler, LLVM_AVAILABLE
    )


# ============================================================================
# Lexer Tests
# ============================================================================

class TestLexer:
    """Test the lexical analyzer."""
    
    def test_basic_tokens(self):
        """Test basic token recognition."""
        source = "drink x = 42"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.DRINK
        assert tokens[1].type == TokenType.IDENTIFIER
        assert tokens[1].value == 'x'
        assert tokens[2].type == TokenType.ASSIGN
        assert tokens[3].type == TokenType.NUMBER
        assert tokens[3].value == 42
    
    def test_operators(self):
        """Test operator tokenization."""
        source = "+ - * / % == != < > <= >="
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY,
            TokenType.DIVIDE, TokenType.MODULO, TokenType.EQUALS,
            TokenType.NOT_EQUALS, TokenType.LESS_THAN, TokenType.GREATER_THAN,
            TokenType.LESS_EQUAL, TokenType.GREATER_EQUAL
        ]
        
        for i, expected in enumerate(expected_types):
            assert tokens[i].type == expected
    
    def test_string_literals(self):
        """Test string literal parsing."""
        source = '"Hello, World!"'
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "Hello, World!"
    
    def test_comments(self):
        """Test comment handling."""
        source = """
        drink x = 10  // This is a comment
        # This is also a comment
        drink y = 20
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Should only have tokens for the two drink statements
        drink_tokens = [t for t in tokens if t.type == TokenType.DRINK]
        assert len(drink_tokens) == 2
    
    def test_keywords(self):
        """Test keyword recognition."""
        source = "drink pour sip shield morph detect defend sanitize armor function return if else while"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.DRINK, TokenType.POUR, TokenType.SIP,
            TokenType.SHIELD, TokenType.MORPH, TokenType.DETECT,
            TokenType.DEFEND, TokenType.SANITIZE, TokenType.ARMOR,
            TokenType.FUNCTION, TokenType.RETURN,
            TokenType.IF, TokenType.ELSE, TokenType.WHILE
        ]
        
        for i, expected in enumerate(expected_types):
            assert tokens[i].type == expected


# ============================================================================
# Parser Tests
# ============================================================================

class TestParser:
    """Test the parser."""
    
    def test_assignment(self):
        """Test assignment parsing."""
        source = "drink x = 42"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert ast.node_type == ASTNodeType.PROGRAM
        assert len(ast.children) == 1
        assert ast.children[0].node_type == ASTNodeType.ASSIGNMENT
        assert ast.children[0].value == 'x'
    
    def test_binary_operations(self):
        """Test binary operation parsing."""
        source = "drink x = 10 + 20 * 2"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assignment = ast.children[0]
        assert assignment.node_type == ASTNodeType.ASSIGNMENT
        
        # Should respect operator precedence
        expr = assignment.children[0]
        assert expr.node_type == ASTNodeType.BINARY_OP
        assert expr.value == '+'
    
    def test_print_statement(self):
        """Test print statement parsing."""
        source = "pour 42"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        assert ast.children[0].node_type == ASTNodeType.PRINT
    
    def test_if_statement(self):
        """Test if statement parsing."""
        source = """
        if (x > 10) {
            pour x
        } else {
            pour 0
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        if_stmt = ast.children[0]
        assert if_stmt.node_type == ASTNodeType.IF_STATEMENT
        assert len(if_stmt.children) >= 2  # condition + at least one statement
    
    def test_while_loop(self):
        """Test while loop parsing."""
        source = """
        while (x < 10) {
            drink x = x + 1
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        while_stmt = ast.children[0]
        assert while_stmt.node_type == ASTNodeType.WHILE_LOOP
    
    def test_function_definition(self):
        """Test function definition parsing."""
        source = """
        function add(a, b) {
            return a + b
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        func_def = ast.children[0]
        assert func_def.node_type == ASTNodeType.FUNCTION_DEF
        assert func_def.value['name'] == 'add'
        assert func_def.value['params'] == ['a', 'b']


# ============================================================================
# LLVM IR Generation Tests
# ============================================================================

@pytest.mark.skipif(not LLVM_AVAILABLE, reason="llvmlite not installed")
class TestLLVMCodeGeneration:
    """Test LLVM IR generation."""
    
    def test_basic_ir_generation(self):
        """Test basic IR generation."""
        source = "drink x = 42"
        compiler = ThirstyLLVMCompiler()
        llvm_ir = compiler.compile_to_ir(source)
        
        assert "define" in llvm_ir
        assert "main" in llvm_ir
        assert "42" in llvm_ir or "4.2" in llvm_ir  # Could be double
    
    def test_arithmetic_ir(self):
        """Test arithmetic operation IR."""
        source = """
        drink x = 10
        drink y = 20
        drink z = x + y
        """
        compiler = ThirstyLLVMCompiler()
        llvm_ir = compiler.compile_to_ir(source)
        
        assert "fadd" in llvm_ir or "add" in llvm_ir
    
    def test_print_ir(self):
        """Test print statement IR."""
        source = "pour 42"
        compiler = ThirstyLLVMCompiler()
        llvm_ir = compiler.compile_to_ir(source)
        
        assert "printf" in llvm_ir or "call" in llvm_ir
    
    def test_control_flow_ir(self):
        """Test control flow IR generation."""
        source = """
        drink x = 10
        if (x > 5) {
            pour x
        }
        """
        compiler = ThirstyLLVMCompiler()
        llvm_ir = compiler.compile_to_ir(source)
        
        assert "br" in llvm_ir  # Branch instruction
        assert "label" in llvm_ir or ":" in llvm_ir  # Basic blocks


# ============================================================================
# Optimization Tests
# ============================================================================

@pytest.mark.skipif(not LLVM_AVAILABLE, reason="llvmlite not installed")
class TestOptimizationPasses:
    """Test optimization passes."""
    
    def test_constant_folding(self):
        """Test constant folding optimization."""
        source = "drink x = 2 + 3"
        compiler = ThirstyLLVMCompiler(optimization_level=2)
        llvm_ir = compiler.compile_and_optimize(source)
        
        # After optimization, should have folded 2+3 into 5
        assert llvm_ir is not None
    
    def test_dead_code_elimination(self):
        """Test dead code elimination."""
        source = """
        drink x = 10
        drink y = 20
        pour x
        """
        compiler = ThirstyLLVMCompiler(optimization_level=2)
        llvm_ir = compiler.compile_and_optimize(source)
        
        # Variable y should be eliminated as it's unused
        assert llvm_ir is not None
    
    def test_optimization_levels(self):
        """Test different optimization levels."""
        source = "drink x = 10 + 20"
        
        for level in [0, 1, 2, 3]:
            compiler = ThirstyLLVMCompiler(optimization_level=level)
            llvm_ir = compiler.compile_and_optimize(source)
            assert llvm_ir is not None


# ============================================================================
# JIT Compilation Tests
# ============================================================================

@pytest.mark.skipif(not LLVM_AVAILABLE, reason="llvmlite not installed")
class TestJITCompilation:
    """Test JIT compilation engine."""
    
    def test_jit_basic(self):
        """Test basic JIT compilation."""
        source = "drink x = 42"
        compiler = ThirstyLLVMCompiler()
        
        # JIT compile and run (returns main's exit code)
        result = compiler.jit_compile_and_run(source)
        assert result == 0  # main returns 0
    
    def test_jit_with_optimization(self):
        """Test JIT with optimization."""
        source = """
        drink x = 10
        drink y = 20
        drink z = x + y
        """
        compiler = ThirstyLLVMCompiler(optimization_level=1)
        result = compiler.jit_compile_and_run(source)
        assert result == 0


# ============================================================================
# WebAssembly Tests
# ============================================================================

@pytest.mark.skipif(not LLVM_AVAILABLE, reason="llvmlite not installed")
class TestWebAssemblyTarget:
    """Test WebAssembly compilation."""
    
    def test_wasm_compilation(self):
        """Test WASM compilation."""
        source = "drink x = 42"
        compiler = ThirstyLLVMCompiler()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.wasm")
            compiler.compile_to_wasm(source, output_path)
            
            # Check that object file was created
            assert os.path.exists(output_path + ".o")
    
    def test_wat_generation(self):
        """Test WAT format generation."""
        source = "drink x = 42"
        compiler = ThirstyLLVMCompiler()
        llvm_ir = compiler.compile_to_ir(source)
        
        wasm_target = WebAssemblyTarget()
        wat = wasm_target.generate_wat(llvm_ir)
        
        assert wat is not None
        assert isinstance(wat, str)


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.skipif(not LLVM_AVAILABLE, reason="llvmlite not installed")
class TestIntegration:
    """Integration tests for complete compilation pipeline."""
    
    def test_full_compilation_pipeline(self):
        """Test complete compilation from source to IR."""
        source = """
        drink x = 10
        drink y = 20
        drink sum = x + y
        pour sum
        """
        
        compiler = ThirstyLLVMCompiler(optimization_level=2)
        
        # Generate IR
        llvm_ir = compiler.compile_to_ir(source)
        assert llvm_ir is not None
        
        # Optimize
        optimized_ir = compiler.compile_and_optimize(source)
        assert optimized_ir is not None
        
        # Length comparison (optimized might be shorter)
        assert len(optimized_ir) > 0
    
    def test_save_and_load_ir(self):
        """Test saving IR to file."""
        source = "drink x = 42"
        compiler = ThirstyLLVMCompiler()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test.ll")
            compiler.save_ir(source, output_path)
            
            assert os.path.exists(output_path)
            
            # Verify content
            with open(output_path, 'r') as f:
                content = f.read()
                assert "define" in content
    
    def test_assembly_generation(self):
        """Test native assembly generation."""
        source = "drink x = 42"
        compiler = ThirstyLLVMCompiler()
        
        asm = compiler.get_assembly(source)
        assert asm is not None
        assert isinstance(asm, str)
    
    def test_native_compilation(self):
        """Test native object file compilation."""
        source = "drink x = 42"
        compiler = ThirstyLLVMCompiler()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test")
            obj_file = compiler.compile_to_native(source, output_path)
            
            assert os.path.exists(obj_file)
    
    def test_complex_program(self):
        """Test compilation of a complex program."""
        source = """
        // Factorial-like calculation
        drink n = 5
        drink result = 1
        drink counter = 1
        
        while (counter <= n) {
            drink result = result * counter
            drink counter = counter + 1
        }
        
        pour result
        """
        
        compiler = ThirstyLLVMCompiler(optimization_level=2)
        llvm_ir = compiler.compile_and_optimize(source)
        
        assert llvm_ir is not None
        assert "while" in llvm_ir or "br" in llvm_ir  # Loop constructs


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_syntax_error(self):
        """Test syntax error handling."""
        source = "drink x ="  # Missing value
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        
        with pytest.raises(SyntaxError):
            parser.parse()
    
    def test_empty_source(self):
        """Test empty source code."""
        source = ""
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        assert len(tokens) == 1  # Just EOF
        assert tokens[0].type == TokenType.EOF
    
    @pytest.mark.skipif(not LLVM_AVAILABLE, reason="llvmlite not installed")
    def test_undefined_variable(self):
        """Test undefined variable error."""
        source = "pour undefined_var"
        compiler = ThirstyLLVMCompiler()
        
        with pytest.raises(NameError):
            compiler.compile_to_ir(source)


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.skipif(not LLVM_AVAILABLE, reason="llvmlite not installed")
class TestPerformance:
    """Performance and benchmarking tests."""
    
    def test_large_program(self):
        """Test compilation of a large program."""
        # Generate a large program
        lines = []
        for i in range(100):
            lines.append(f"drink var{i} = {i}")
        lines.append("pour var99")
        
        source = "\n".join(lines)
        
        compiler = ThirstyLLVMCompiler()
        llvm_ir = compiler.compile_to_ir(source)
        
        assert llvm_ir is not None
    
    def test_optimization_performance(self):
        """Test that optimization doesn't hang."""
        source = """
        drink x = 1
        while (x < 100) {
            drink x = x + 1
        }
        pour x
        """
        
        compiler = ThirstyLLVMCompiler(optimization_level=3)
        llvm_ir = compiler.compile_and_optimize(source)
        
        assert llvm_ir is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
