"""Shadow Thirst compiler — full pipeline: source → bytecode."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CompileResult:
    success: bool
    bytecode: Any = None
    ast: Any = None
    ir: Any = None
    analysis_report: Any = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def compile_source(
    source: str,
    strict_mode: bool = True,
    enable_optimizations: bool = True,
) -> CompileResult:
    from shadow_thirst.lexer import tokenize
    from shadow_thirst.parser import parse, ParseError
    from shadow_thirst.ir_generator import generate_ir
    from shadow_thirst.static_analysis import analyze, AnalysisSeverity
    from shadow_thirst.bytecode import generate_bytecode

    try:
        tokens = tokenize(source)
    except Exception as exc:
        return CompileResult(success=False, errors=[f"Lex error: {exc}"])

    try:
        ast = parse(tokens)
    except Exception as exc:
        return CompileResult(success=False, errors=[f"Parse error: {exc}"])

    if not ast.functions:
        return CompileResult(
            success=False,
            errors=["No functions defined in source"],
        )

    try:
        ir = generate_ir(ast)
    except Exception as exc:
        return CompileResult(success=False, ast=ast, errors=[f"IR error: {exc}"])

    try:
        report = analyze(ir)
    except Exception as exc:
        return CompileResult(success=False, ast=ast, ir=ir, errors=[f"Analysis error: {exc}"])

    warnings = [f.message for f in report.get_warnings()]
    errors = [f.message for f in report.get_errors()]

    if errors and strict_mode:
        return CompileResult(
            success=False,
            ast=ast,
            ir=ir,
            analysis_report=report,
            errors=errors,
            warnings=warnings,
        )

    try:
        bytecode = generate_bytecode(ir)
    except Exception as exc:
        return CompileResult(
            success=False, ast=ast, ir=ir, analysis_report=report,
            errors=errors + [f"Codegen error: {exc}"], warnings=warnings,
        )

    return CompileResult(
        success=True,
        bytecode=bytecode,
        ast=ast,
        ir=ir,
        analysis_report=report,
        errors=errors,
        warnings=warnings,
    )
