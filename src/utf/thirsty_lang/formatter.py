"""
AST-based pretty-printer for Thirsty-Lang.

Usage:
    from thirsty_lang.formatter import Formatter
    from thirsty_lang.lexer import Lexer
    from thirsty_lang.parser import Parser

    tokens = Lexer(source).tokenize()
    tree   = Parser(tokens).parse()
    output = Formatter().format(tree)
"""

from __future__ import annotations

from typing import Any

from .ast import (
    ArrayExpr,
    AssignExpr,
    AwaitExpr,
    BinaryExpr,
    BlockStmt,
    CallExpr,
    CatchClause,
    ClassDecl,
    CondenseExpr,
    DripStmt,
    EnumDecl,
    EvaporateExpr,
    Expr,
    ExprStmt,
    FunctionDecl,
    FunctionType,
    GenericType,
    GovernedFunctionDecl,
    GuardExpr,
    IfStmt,
    ImportDecl,
    IndexExpr,
    InterfaceDecl,
    LiteralExpr,
    LoopStmt,
    MemberExpr,
    ModuleHeader,
    NamedType,
    NewExpr,
    Param,
    PipeExpr,
    PrintStmt,
    Program,
    ReturnStmt,
    Stmt,
    StructDecl,
    ThrowStmt,
    TryStmt,
    TypeNode,
    UnaryExpr,
    VarDecl,
    VariableExpr,
)

_INDENT = "  "  # 2-space indent


class Formatter:
    """Walk a Thirsty-Lang AST and emit normalised, correctly-indented source."""

    def format(self, program: Program) -> str:
        parts: list[str] = []
        if program.header is not None:
            parts.append(self._header(program.header))
            parts.append("")  # blank line after header
        for decl in program.declarations:
            parts.append(self._stmt(decl, 0))
        text = "\n".join(parts)
        if not text.endswith("\n"):
            text += "\n"
        return text

    # ------------------------------------------------------------------
    # Module header
    # ------------------------------------------------------------------

    def _header(self, h: ModuleHeader) -> str:
        lines = [f"module {h.name}"]
        if h.mode and h.mode != "core":
            lines.append(f"mode {h.mode}")
        else:
            lines.append("mode core")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Types
    # ------------------------------------------------------------------

    def _type(self, t: TypeNode) -> str:
        if isinstance(t, NamedType):
            return t.name
        if isinstance(t, GenericType):
            args = ", ".join(self._type(a) for a in t.args)
            return f"{t.base}[{args}]"
        if isinstance(t, FunctionType):
            params = ", ".join(self._type(p) for p in t.params)
            ret = self._type(t.result)
            return f"glass({params}) -> {ret}"
        return "Any"

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------

    def _expr(self, e: Expr) -> str:
        if isinstance(e, LiteralExpr):
            return self._literal(e.value)
        if isinstance(e, VariableExpr):
            return e.name
        if isinstance(e, ArrayExpr):
            items = ", ".join(self._expr(i) for i in e.items)
            return f"[{items}]"
        if isinstance(e, AssignExpr):
            return f"{self._expr(e.target)} = {self._expr(e.value)}"
        if isinstance(e, UnaryExpr):
            return f"{e.op}{self._expr(e.right)}"
        if isinstance(e, BinaryExpr):
            return f"{self._expr(e.left)} {e.op} {self._expr(e.right)}"
        if isinstance(e, PipeExpr):
            return f"{self._expr(e.left)} |> {self._expr(e.right)}"
        if isinstance(e, GuardExpr):
            base = f"thirst {self._expr(e.condition)} quench"
            if e.when_false is not None:
                return f"{base} hydrated {self._expr(e.when_false)}"
            return base
        if isinstance(e, CallExpr):
            callee = self._expr(e.callee)
            args = ", ".join(self._expr(a) for a in e.args)
            safe = "?" if e.safe else ""
            return f"{callee}{safe}({args})"
        if isinstance(e, MemberExpr):
            return f"{self._expr(e.obj)}.{e.name}"
        if isinstance(e, IndexExpr):
            return f"{self._expr(e.obj)}[{self._expr(e.index)}]"
        if isinstance(e, NewExpr):
            args = ", ".join(self._expr(a) for a in e.args)
            return f"new {e.class_name}({args})"
        if isinstance(e, AwaitExpr):
            return f"await {self._expr(e.expr)}"
        if isinstance(e, CondenseExpr):
            return f"condense({self._expr(e.expr)})"
        if isinstance(e, EvaporateExpr):
            return f"evaporate({self._expr(e.expr)})"
        # FunctionDecl used as expression (anonymous glass)
        if isinstance(e, FunctionDecl):
            return self._fn_expr(e)
        return repr(e)

    def _literal(self, value: Any) -> str:
        if value is None:
            return "empty"
        if isinstance(value, bool):
            return "quenched" if value else "parched"
        if isinstance(value, str):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{escaped}"'
        return str(value)

    def _fn_expr(self, f: FunctionDecl) -> str:
        """Format an anonymous function expression (closure)."""
        params = ", ".join(
            f"{p.name}: {self._type(p.type_node)}" for p in f.params
        )
        ret = f" -> {self._type(f.return_type)}" if f.return_type else ""
        body = self._inline_block(f.body)
        return f"glass({params}){ret} {body}"

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    def _stmt(self, s: Stmt, depth: int) -> str:
        pad = _INDENT * depth

        if isinstance(s, ImportDecl):
            alias = f" as {s.alias}" if s.alias else ""
            return f'{pad}import "{s.module}"{alias};'

        if isinstance(s, VarDecl):
            mut = "mut " if s.mutable else ""
            typ = self._type(s.type_node)
            val = self._expr(s.initializer)
            vis = f"{s.visibility} " if s.visibility else ""
            return f"{pad}{vis}drink {mut}{s.name}: {typ} = {val};"

        if isinstance(s, PrintStmt):
            safe = "?" if s.safe else ""
            return f"{pad}pour{safe}({self._expr(s.expr)});"

        if isinstance(s, ReturnStmt):
            if s.expr is None:
                return f"{pad}return;"
            return f"{pad}return {self._expr(s.expr)};"

        if isinstance(s, ThrowStmt):
            return f"{pad}throw {self._expr(s.expr)};"

        if isinstance(s, DripStmt):
            if s.amount is not None:
                return f"{pad}drip {s.name} {self._expr(s.amount)};"
            return f"{pad}drip {s.name};"

        if isinstance(s, ExprStmt):
            return f"{pad}{self._expr(s.expr)};"

        if isinstance(s, IfStmt):
            return self._if_stmt(s, depth)

        if isinstance(s, LoopStmt):
            return self._loop_stmt(s, depth)

        if isinstance(s, TryStmt):
            return self._try_stmt(s, depth)

        if isinstance(s, (FunctionDecl, GovernedFunctionDecl)):
            return self._fn_decl(s, depth)

        if isinstance(s, ClassDecl):
            return self._class_decl(s, depth)

        if isinstance(s, EnumDecl):
            variants = ", ".join(s.variants)
            return f"{pad}enum {s.name} {{ {variants} }}"

        if isinstance(s, StructDecl):
            fields = ", ".join(
                f"{f.name}: {self._type(f.type_node)}" for f in s.fields
            )
            return f"{pad}struct {s.name} {{ {fields} }}"

        if isinstance(s, InterfaceDecl):
            pad_inner = _INDENT * (depth + 1)
            lines = [f"{pad}interface {s.name} {{"]
            for method in s.methods:
                lines.append(self._fn_decl(method, depth + 1))
            lines.append(f"{pad}}}")
            return "\n".join(lines)

        if isinstance(s, BlockStmt):
            lines = [self._stmt(st, depth) for st in s.statements]
            return "\n".join(lines)

        return f"{pad}/* unknown node: {type(s).__name__} */"

    def _block(self, block: BlockStmt, depth: int) -> str:
        """Format a block as indented lines between braces."""
        pad = _INDENT * depth
        inner = _INDENT * (depth + 1)
        if not block.statements:
            return "{}"
        lines = ["{"]
        for st in block.statements:
            lines.append(self._stmt(st, depth + 1))
        lines.append(f"{pad}}}")
        return "\n".join(lines)

    def _inline_block(self, block: BlockStmt) -> str:
        """One-line block for anonymous functions.  Falls back to multi-line."""
        stmts = block.statements
        if len(stmts) == 1:
            inner = self._stmt(stmts[0], 0).strip()
            return "{ " + inner + " }"
        lines = ["{\n"]
        for st in stmts:
            lines.append(_INDENT + self._stmt(st, 1).strip() + "\n")
        lines.append("}")
        return "".join(lines)

    def _if_stmt(self, s: IfStmt, depth: int) -> str:
        pad = _INDENT * depth
        cond = self._expr(s.condition)
        then = self._block(s.then_branch, depth)
        out = f"{pad}thirsty ({cond}) {then}"
        if s.else_branch is not None:
            else_b = self._block(s.else_branch, depth)
            out += f" hydrated {else_b}"
        return out

    def _loop_stmt(self, s: LoopStmt, depth: int) -> str:
        pad = _INDENT * depth
        count = self._expr(s.count)
        body = self._block(s.body, depth)
        return f"{pad}refill {count} times {body}"

    def _try_stmt(self, s: TryStmt, depth: int) -> str:
        pad = _INDENT * depth
        parts = [f"{pad}spillage {self._block(s.try_block, depth)}"]
        for catch in s.catches:
            cb = self._block(catch.block, depth)
            parts.append(f" cleanup ({catch.name}: {catch.type_name}) {cb}")
        if s.finally_block is not None:
            fb = self._block(s.finally_block, depth)
            parts.append(f" finally {fb}")
        return "".join(parts)

    def _fn_decl(self, f: FunctionDecl | GovernedFunctionDecl, depth: int) -> str:
        pad = _INDENT * depth
        async_ = "async " if f.is_async else ""
        vis = f"{f.visibility} " if f.visibility else ""
        params = ", ".join(
            f"{p.name}: {self._type(p.type_node)}" for p in f.params
        )
        ret = f" -> {self._type(f.return_type)}" if f.return_type else ""
        body = self._block(f.body, depth)
        sig = f"{pad}{vis}{async_}glass {f.name}({params}){ret}"
        if isinstance(f, GovernedFunctionDecl) and f.requires:
            req_pad = _INDENT * (depth + 1)
            req_lines = "\n".join(
                f"{req_pad}requires {c.annotation}" for c in f.requires
            )
            return f"{sig}\n{req_lines}\n{pad}{body.lstrip()}"
        return f"{sig} {body}"

    def _class_decl(self, c: ClassDecl, depth: int) -> str:
        pad = _INDENT * depth
        inner_pad = _INDENT * (depth + 1)
        lines = [f"{pad}fountain {c.name} {{"]
        for member in c.members:
            lines.append(self._stmt(member, depth + 1))
        lines.append(f"{pad}}}")
        return "\n".join(lines)
