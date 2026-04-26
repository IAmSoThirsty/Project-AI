"""
God Tier Intent Compiler System - YAML/IR → Deterministic Execution
====================================================================

Compiles YAML intent specifications into deterministic intermediate representation (IR)
for provably correct execution with formal verification.

Components:
- ir_schema: Core IR data structures and type system
- compiler: YAML to IR compilation with semantic analysis
- ir_executor: Deterministic execution engine with tracing
- optimizer: Advanced optimization passes
- verifier: Static analysis and formal verification

Example:
    >>> from gradle_evolution.ir import IntentCompiler, IRExecutor, IROptimizer, IRVerifier
    >>>
    >>> # Compile YAML intent to IR
    >>> compiler = IntentCompiler()
    >>> graph = compiler.compile(yaml_content)
    >>>
    >>> # Optimize IR
    >>> optimizer = IROptimizer(optimization_level=2)
    >>> optimized_graph = optimizer.optimize(graph)
    >>>
    >>> # Verify correctness
    >>> verifier = IRVerifier()
    >>> verification = verifier.verify(optimized_graph)
    >>>
    >>> # Execute deterministically
    >>> executor = IRExecutor()
    >>> results = executor.execute(optimized_graph)
"""

from .compiler import CompilationError, IntentCompiler
from .ir_executor import (
    Checkpoint,
    ExecutionContext,
    ExecutionError,
    ExecutionTrace,
    IRExecutor,
    ResourceUsage,
)
from .ir_schema import (
    IRGraph,
    IRNode,
    IROpcode,
    IRSchema,
    IRType,
    IRTypeInfo,
)
from .optimizer import IROptimizer, OptimizationStats
from .verifier import IRVerifier, ResourceBounds, VerificationResult

__version__ = "1.0.0"

__all__ = [
    # Core IR structures
    "IRNode",
    "IRGraph",
    "IROpcode",
    "IRType",
    "IRTypeInfo",
    "IRSchema",
    # Compiler
    "IntentCompiler",
    "CompilationError",
    # Executor
    "IRExecutor",
    "ExecutionContext",
    "ExecutionTrace",
    "ExecutionError",
    "ResourceUsage",
    "Checkpoint",
    # Optimizer
    "IROptimizer",
    "OptimizationStats",
    # Verifier
    "IRVerifier",
    "VerificationResult",
    "ResourceBounds",
]
