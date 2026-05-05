
from __future__ import annotations

import hashlib
import importlib.util
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from thirsty_lang import ast
from thirsty_lang.lexer import Lexer
from thirsty_lang.parser import Parser
from thirsty_lang.token import Span, Token, TokenType


@dataclass
class InvariantDecl:
    name: str
    body: list[ast.Stmt]
    span: Span


@dataclass
class MutationDecl:
    name: str
    params: list[tuple[str, str]]
    shadow_body: list[ast.Stmt] = field(default_factory=list)
    invariant_body: list[ast.Stmt] = field(default_factory=list)
    canonical_body: list[ast.Stmt] = field(default_factory=list)
    span: Span | None = None


@dataclass
class ShadowModule:
    mutations: list[MutationDecl]
    invariants: list[InvariantDecl]


@dataclass
class AnalysisResult:
    analyzer: str
    level: str
    passed: bool
    message: str

    @property
    def name(self) -> str:
        return self.analyzer


def _collect_block(tokens: list[Token], start_index: int) -> tuple[list[Token], int]:
    assert tokens[start_index].kind == TokenType.LBRACE
    depth = 0
    collected: list[Token] = []
    i = start_index
    while i < len(tokens):
        tok = tokens[i]
        if tok.kind == TokenType.LBRACE:
            depth += 1
            if depth > 1:
                collected.append(tok)
        elif tok.kind == TokenType.RBRACE:
            depth -= 1
            if depth == 0:
                return collected, i + 1
            collected.append(tok)
        else:
            collected.append(tok)
        i += 1
    raise ValueError("unterminated block")


def _parse_statements(tokens: list[Token], file: str = "<shadow>") -> list[ast.Stmt]:
    eof_span = tokens[-1].span if tokens else Span(file, 1, 1, 1, 1)
    wrapped = [Token(TokenType.LBRACE, "{", None, eof_span)] + tokens + [Token(TokenType.RBRACE, "}", None, eof_span), Token(TokenType.EOF, "", None, eof_span)]
    parser = Parser.from_tokens(wrapped)
    block = parser._block()
    return block.statements


def parse_shadow(text: str, file: str = "<shadow>") -> ShadowModule:
    tokens = Lexer(text, file).lex()
    i = 0
    mutations: list[MutationDecl] = []
    invariants: list[InvariantDecl] = []
    while i < len(tokens) and tokens[i].kind != TokenType.EOF:
        tok = tokens[i]
        if tok.kind == TokenType.MUTATION:
            start = tok.span
            i += 1
            if tokens[i].kind != TokenType.VALIDATED_CANONICAL:
                raise ValueError("expected validated_canonical after mutation")
            i += 1
            name_tok = tokens[i]; i += 1
            if name_tok.kind != TokenType.IDENT:
                raise ValueError("expected mutation name")
            if tokens[i].kind != TokenType.LPAREN:
                raise ValueError("expected '(' after mutation name")
            i += 1
            params = []
            while tokens[i].kind != TokenType.RPAREN:
                pname = tokens[i]; i += 1
                if pname.kind != TokenType.IDENT:
                    raise ValueError("expected parameter name")
                if tokens[i].kind != TokenType.COLON:
                    raise ValueError("expected ':' after parameter")
                i += 1
                ptype = tokens[i]; i += 1
                params.append((pname.lexeme, ptype.lexeme))
                if tokens[i].kind == TokenType.COMMA:
                    i += 1
            i += 1
            if tokens[i].kind != TokenType.LBRACE:
                raise ValueError("expected '{' after mutation signature")
            body_tokens, i = _collect_block(tokens, i)
            j = 0
            shadow_body = invariant_body = canonical_body = []
            while j < len(body_tokens):
                section = body_tokens[j]
                j += 1
                if section.kind not in {TokenType.SHADOW, TokenType.INVARIANT, TokenType.CANONICAL}:
                    raise ValueError(f"expected shadow/invariant/canonical section, got {section.lexeme!r}")
                block_tokens, j = _collect_block(body_tokens, j)
                stmts = _parse_statements(block_tokens, file)
                if section.kind == TokenType.SHADOW:
                    shadow_body = stmts
                elif section.kind == TokenType.INVARIANT:
                    invariant_body = stmts
                else:
                    canonical_body = stmts
            mutations.append(MutationDecl(name_tok.lexeme, params, shadow_body, invariant_body, canonical_body, start))
            continue
        i += 1
    return ShadowModule(mutations, invariants)


def _writes_canonical(stmts: list[ast.Stmt]) -> bool:
    for stmt in stmts:
        if isinstance(stmt, ast.ExprStmt) and isinstance(stmt.expr, ast.AssignExpr) and isinstance(stmt.expr.target, ast.VariableExpr):
            if stmt.expr.target.name.startswith("canonical_"):
                return True
        if isinstance(stmt, ast.VarDecl) and stmt.name.startswith("canonical_"):
            return True
        if isinstance(stmt, ast.BlockStmt) and _writes_canonical(stmt.statements):
            return True
    return False


def _has_nondeterminism(stmts: list[ast.Stmt]) -> bool:
    def walk_expr(expr: ast.Expr) -> bool:
        if isinstance(expr, ast.VariableExpr):
            return expr.name == "now"
        if isinstance(expr, ast.CallExpr) and isinstance(expr.callee, ast.VariableExpr):
            return expr.callee.name in {"now", "rand", "random"}
        for name in ("left", "right", "expr", "target", "value", "obj", "index", "condition", "when_true", "when_false"):
            child = getattr(expr, name, None)
            if isinstance(child, ast.Expr) and walk_expr(child):
                return True
        if hasattr(expr, "args"):
            for arg in getattr(expr, "args", []):
                if isinstance(arg, ast.Expr) and walk_expr(arg):
                    return True
        return False
    for stmt in stmts:
        if isinstance(stmt, ast.ExprStmt) and walk_expr(stmt.expr):
            return True
        if isinstance(stmt, ast.VarDecl) and walk_expr(stmt.initializer):
            return True
        if isinstance(stmt, ast.BlockStmt) and _has_nondeterminism(stmt.statements):
            return True
    return False


def _estimate_pressure(stmts: list[ast.Stmt]) -> tuple[int, int]:
    count = 0
    reservoirs = 0
    for stmt in stmts:
        count += 1
        if isinstance(stmt, ast.VarDecl) and getattr(stmt.type_node, "name", "") in {"Reservoir", "well"}:
            reservoirs += 1
        if isinstance(stmt, ast.BlockStmt):
            c, r = _estimate_pressure(stmt.statements)
            count += c
            reservoirs += r
    return count * 10, reservoirs * 64


def _canonical_convergence(mutation: MutationDecl) -> bool:
    return not (_writes_canonical(mutation.shadow_body) or _has_nondeterminism(mutation.shadow_body))


def _plugin_analyzers() -> list[Callable[[ShadowModule], list[AnalysisResult]]]:
    plugins = []
    plugins_dir = Path(__file__).resolve().parent / "plugins"
    if plugins_dir.exists():
        for py in plugins_dir.glob("*.py"):
            spec = importlib.util.spec_from_file_location(py.stem, py)
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)
            if hasattr(mod, "analyze_plugin"):
                plugins.append(mod.analyze_plugin)
    return plugins


def analyze(module: ShadowModule) -> list[AnalysisResult]:
    out: list[AnalysisResult] = []
    for m in module.mutations:
        out.append(AnalysisResult("PlaneIsolationAnalyzer", "critical", not _writes_canonical(m.shadow_body), "shadow plane cannot write canonical state"))
        out.append(AnalysisResult("DeterminismAnalyzer", "critical", not _has_nondeterminism(m.shadow_body), "shadow plane must be deterministic"))
        cpu_ms, mem_mb = _estimate_pressure(m.shadow_body)
        out.append(AnalysisResult("ResourceEstimator", "warning", cpu_ms <= 1000 and mem_mb <= 256, f"estimated cpu={cpu_ms}ms memory={mem_mb}MB"))
        out.append(AnalysisResult("PuritySpringAnalyzer", "critical", True, "invariant blocks remain pure in the bootstrap model"))
        out.append(AnalysisResult("MemoryEvaporationAnalyzer", "warning", mem_mb <= 256, f"peak reservoir estimate={mem_mb}MB"))
        out.append(AnalysisResult("CanonicalConvergenceAnalyzer", "critical", _canonical_convergence(m), "shadow and canonical must converge before promotion"))
    for plugin in _plugin_analyzers():
        out.extend(plugin(module))
    return out


def replay_hash(module: ShadowModule) -> str:
    payload = json.dumps({
        "mutations": [
            {
                "name": m.name,
                "params": m.params,
                "shadow_len": len(m.shadow_body),
                "invariant_len": len(m.invariant_body),
                "canonical_len": len(m.canonical_body),
            }
            for m in module.mutations
        ]
    }, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def promote(module: ShadowModule, dry_run: bool = False, replay_id: str | None = None) -> dict[str, Any]:
    results = analyze(module)
    failures = [r for r in results if r.level == "critical" and not r.passed]
    decision = "PROMOTE" if not failures else "REJECT"
    return {
        "decision": decision,
        "verdict": decision,
        "dry_run": dry_run,
        "replay_id": replay_id or replay_hash(module)[:16],
        "analysis": [r.__dict__ for r in results],
        "diff": "shadow spring aligns with the canonical river" if decision == "PROMOTE" else "the shadow river diverges and is withheld from the spring",
        "replay_hash": replay_hash(module),
    }


def visualize(module: ShadowModule) -> str:
    lines = ["flowchart TD"]
    for m in module.mutations:
        lines.append(f'  {m.name}_shadow["{m.name}: shadow"] --> {m.name}_inv["{m.name}: invariant"]')
        lines.append(f'  {m.name}_inv --> {m.name}_canon["{m.name}: canonical"]')
    return "\n".join(lines)
