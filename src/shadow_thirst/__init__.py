"""
Shadow Thirst Compiler Package

Complete compiler infrastructure for Shadow Thirst dual-plane programming language.

Components:
- Lexer: Tokenization
- Parser: AST construction
- Static analyzers: 6 safety analyzers
- IR generator: Dual-plane intermediate representation
- Bytecode generator: Bytecode emission
- VM: Shadow-aware virtual machine
- Constitutional integration: Core sovereignty binding

Quick Start:
    from shadow_thirst import compile_source
    from shadow_thirst.vm import ShadowAwareVM

    result = compile_source(source_code)
    if result.success:
        vm = ShadowAwareVM()
        vm.load_program(result.bytecode)
        output = vm.execute("main")

STATUS: PRODUCTION
VERSION: 1.0.0
"""

from shadow_thirst.lexer import Token, TokenType, ShadowThirstLexer, tokenize
from shadow_thirst.parser import parse
from shadow_thirst.compiler import compile_source, compile_file, ShadowThirstCompiler
from shadow_thirst.vm import ShadowAwareVM
from shadow_thirst.constitutional import ConstitutionalIntegration

__version__ = "1.0.0"

__all__ = [
    # Lexer
    "Token",
    "TokenType",
    "ShadowThirstLexer",
    "tokenize",
    # Parser
    "parse",
    # Compiler
    "compile_source",
    "compile_file",
    "ShadowThirstCompiler",
    # VM
    "ShadowAwareVM",
    # Constitutional
    "ConstitutionalIntegration",
]
