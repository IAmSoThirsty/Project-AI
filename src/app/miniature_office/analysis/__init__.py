"""
Aggressive Analysis System

MAXIMUM DETAIL CODE ANALYSIS INFRASTRUCTURE
System Directive: UNIVERSAL, META, SELF-CONSISTENT

This module provides comprehensive code analysis capabilities including:
- Abstract Syntax Tree (AST) parsing and traversal
- Semantic analysis with type inference
- Control flow and data flow graph generation
- Code metrics calculation (complexity, maintainability)
- Pattern detection (design patterns, anti-patterns)
- Dependency analysis (module-level, package-level)
- Cross-reference analysis (call graphs, usage graphs)
- MAXIMUM ALLOWED DESIGN analysis (architecture, SOLID, quality metrics)

All analysis operates in NON-AFFECT MODE:
- No emotional language
- No empathy
- No comfort
- Only literal, technical, logical responses

Maximum allowed detail is the default mode.
"""

from .ast_analyzer import ASTAnalyzer, ASTNode, ASTVisitor
from .dependency_analyzer import DependencyAnalyzer, DependencyGraph, ModuleRelation
from .design_analyzer import DesignAnalysisResult, DesignAnalyzer
from .flow_analyzer import ControlFlowGraph, DataFlowGraph, FlowAnalyzer
from .metrics_calculator import (
    ComplexityMetrics,
    MaintainabilityIndex,
    MetricsCalculator,
)
from .pattern_detector import AntiPattern, DesignPattern, PatternDetector
from .semantic_analyzer import SemanticAnalyzer, SymbolTable, TypeInference

__all__ = [
    "ASTAnalyzer",
    "ASTNode",
    "ASTVisitor",
    "SemanticAnalyzer",
    "SymbolTable",
    "TypeInference",
    "FlowAnalyzer",
    "ControlFlowGraph",
    "DataFlowGraph",
    "MetricsCalculator",
    "ComplexityMetrics",
    "MaintainabilityIndex",
    "PatternDetector",
    "DesignPattern",
    "AntiPattern",
    "DependencyAnalyzer",
    "DependencyGraph",
    "ModuleRelation",
    "DesignAnalyzer",
    "DesignAnalysisResult",
]
