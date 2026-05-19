
from __future__ import annotations

from dataclasses import dataclass, field

from . import ast
from .diagnostics import ThirstyError, nearest_word
from .token import KEYWORDS
from .module_system import resolve_import_type
from .typesys import (
    ANY,
    BOOL,
    ERROR,
    FLOAT,
    INT,
    STRING,
    VOID,
    Type,
    equals,
    from_type_node,
    is_option,
    option,
    option_inner,
    reservoir,
    task,
)


@dataclass
class Symbol:
    type_: Type
    mutable: bool = False


@dataclass
class ClassInfo:
    name: str
    fields: dict[str, Type] = field(default_factory=dict)
    methods: dict[str, tuple[list[Type], Type, bool]] = field(default_factory=dict)


class Scope:
    def __init__(self, parent: "Scope | None" = None) -> None:
        self.parent = parent
        self.symbols: dict[str, Symbol] = {}

    def define(self, name: str, sym: Symbol, span) -> None:
        if name in self.symbols:
            raise ThirstyError("THIRSTY-E010", f"duplicate binding '{name}'", span)
        self.symbols[name] = sym

    def get(self, name: str):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.get(name)
        return None

    def flatten_names(self) -> list[str]:
        seen = []
        cur: Scope | None = self
        while cur:
            seen.extend(cur.symbols.keys())
            cur = cur.parent
        return seen


class Checker:
    def __init__(self) -> None:
        self.globals = Scope()
        self.scope = self.globals
        self.current_return = VOID
        self.current_class: ClassInfo | None = None
        self.classes: dict[str, ClassInfo] = {}
        self.module_types: dict[str, dict[str, Type]] = {}
        self._install_builtins()

    def _install_builtins(self) -> None:
        builtins = {
            "length": Type("BuiltinFn", (STRING, INT)),
            "contains": Type("BuiltinFn", (STRING, STRING, BOOL)),
            "split": Type("BuiltinFn", (STRING, STRING, reservoir(STRING))),
            "abs": Type("BuiltinFn", (INT, INT)),
            "min": Type("BuiltinFn", (INT, INT, INT)),
            "max": Type("BuiltinFn", (INT, INT, INT)),
            "push": Type("BuiltinFn", (ANY, ANY, VOID)),
            "pop": Type("BuiltinFn", (ANY, ANY)),
            "size": Type("BuiltinFn", (ANY, INT)),
            "get": Type("BuiltinFn", (ANY, INT, ANY)),
            "strain": Type("BuiltinFn", (ANY, ANY, ANY)),
            "transmute": Type("BuiltinFn", (ANY, ANY, ANY)),
            "distill": Type("BuiltinFn", (ANY, ANY, ANY, ANY)),
            "flood": Type("BuiltinFn", (ANY, ANY, ANY)),
            "condense": Type("BuiltinFn", (ANY, ANY)),
            "evaporate": Type("BuiltinFn", (ANY, option(ANY))),
        }
        for name, ty in builtins.items():
            self.globals.define(name, Symbol(ty), None)

    def check(self, program: ast.Program) -> None:
        current_file = program.span.file
        for decl in program.declarations:
            if isinstance(decl, ast.ImportDecl):
                info = resolve_import_type(decl.module, current_file)
                alias = decl.alias or decl.module.split("::")[-1].split("/")[-1].split(".")[0]
                self.module_types[alias] = info.members
                self.globals.define(alias, Symbol(Type("Module", (Type(alias),))), decl.span)
        for decl in program.declarations:
            if isinstance(decl, ast.ClassDecl):
                info = ClassInfo(decl.name)
                self.classes[decl.name] = info
                self.globals.define(decl.name, Symbol(Type(decl.name)), decl.span)
        for decl in program.declarations:
            if isinstance(decl, ast.FunctionDecl):
                params = [from_type_node(p.type_node) for p in decl.params]
                result = VOID if decl.return_type is None else from_type_node(decl.return_type)
                fn_type = task(result) if decl.is_async else Type("Function", tuple(params + [result]))
                self.globals.define(decl.name, Symbol(fn_type), decl.span)
        for decl in program.declarations:
            if isinstance(decl, ast.ClassDecl):
                self._check_class(decl)
        for decl in program.declarations:
            if not isinstance(decl, ast.ClassDecl):
                self._check_stmt(decl)

    def _check_class(self, decl: ast.ClassDecl) -> None:
        info = self.classes[decl.name]
        prev_class = self.current_class
        self.current_class = info
        for member in decl.members:
            if isinstance(member, ast.VarDecl):
                info.fields[member.name] = from_type_node(member.type_node)
            elif isinstance(member, ast.FunctionDecl):
                params = [from_type_node(p.type_node) for p in member.params]
                result = VOID if member.return_type is None else from_type_node(member.return_type)
                info.methods[member.name] = (params, task(result) if member.is_async else result, member.is_async)
        inner = Scope(self.globals)
        inner.define("this", Symbol(Type(decl.name), mutable=True), decl.span)
        prev_scope = self.scope
        self.scope = inner
        for member in decl.members:
            self._check_stmt(member)
        self.scope = prev_scope
        self.current_class = prev_class

    def _check_stmt(self, stmt: ast.Stmt) -> None:
        if isinstance(stmt, ast.ImportDecl):
            return
        if isinstance(stmt, ast.VarDecl):
            t = from_type_node(stmt.type_node)
            if stmt.is_field and isinstance(stmt.initializer, ast.LiteralExpr) and stmt.initializer.value is None:
                init_t = t
            else:
                init_t = self._check_expr(stmt.initializer)
                if not self._assignable(t, init_t):
                    raise ThirstyError("THIRSTY-E021", f"type mismatch: expected {t}, got {init_t}", stmt.span)
            self.scope.define(stmt.name, Symbol(t, mutable=stmt.mutable and not stmt.is_field), stmt.span)
            return
        if isinstance(stmt, ast.FunctionDecl):
            fn_scope = Scope(self.scope)
            saved_return = self.current_return
            self.current_return = VOID if stmt.return_type is None else from_type_node(stmt.return_type)
            if stmt.is_method and self.current_class:
                fn_scope.define("this", Symbol(Type(self.current_class.name), mutable=True), stmt.span)
            prev_scope = self.scope
            self.scope = fn_scope
            for p in stmt.params:
                self.scope.define(p.name, Symbol(from_type_node(p.type_node)), p.span)
            self._check_stmt(stmt.body)
            self.scope = prev_scope
            self.current_return = saved_return
            return
        if isinstance(stmt, ast.ClassDecl):
            return
        if isinstance(stmt, ast.BlockStmt):
            prev = self.scope
            self.scope = Scope(self.scope)
            for s in stmt.statements:
                self._check_stmt(s)
            self.scope = prev
            return
        if isinstance(stmt, ast.PrintStmt):
            self._check_expr(stmt.expr)
            return
        if isinstance(stmt, ast.ExprStmt):
            self._check_expr(stmt.expr)
            return
        if isinstance(stmt, ast.ReturnStmt):
            value_t = VOID if stmt.expr is None else self._check_expr(stmt.expr)
            if not self._assignable(self.current_return, value_t):
                raise ThirstyError("THIRSTY-E024", f"return type mismatch: expected {self.current_return}, got {value_t}", stmt.span)
            return
        if isinstance(stmt, ast.ThrowStmt):
            self._check_expr(stmt.expr)
            return
        if isinstance(stmt, ast.DripStmt):
            sym = self.scope.get(stmt.name)
            if not sym:
                raise self._unknown_name(stmt.name, stmt.span)
            if not sym.mutable:
                raise ThirstyError("THIRSTY-E020", f"cannot drip immutable binding '{stmt.name}'", stmt.span)
            amt_t = INT if stmt.amount is None else self._check_expr(stmt.amount)
            if sym.type_ not in (INT, FLOAT) or amt_t not in (INT, FLOAT):
                raise ThirstyError("THIRSTY-E021", "drip requires numeric mutable bindings", stmt.span)
            return
        if isinstance(stmt, ast.IfStmt):
            cond_t = self._check_expr(stmt.condition)
            if not equals(cond_t, BOOL):
                raise ThirstyError("THIRSTY-E022", "if condition must be Bool", stmt.condition.span)
            then_narrow, else_narrow = self._narrowings(stmt.condition)
            self._check_branch(stmt.then_branch, then_narrow)
            if stmt.else_branch:
                self._check_branch(stmt.else_branch, else_narrow)
            return
        if isinstance(stmt, ast.LoopStmt):
            count_t = self._check_expr(stmt.count)
            if not equals(count_t, INT):
                raise ThirstyError("THIRSTY-E023", "loop count must be Int", stmt.count.span)
            self._check_stmt(stmt.body)
            return
        if isinstance(stmt, ast.TryStmt):
            self._check_stmt(stmt.try_block)
            for c in stmt.catches:
                prev = self.scope
                self.scope = Scope(self.scope)
                self.scope.define(c.name, Symbol(Type(c.type_name)), c.span)
                self._check_stmt(c.block)
                self.scope = prev
            if stmt.finally_block:
                self._check_stmt(stmt.finally_block)
            return
        raise RuntimeError(f"unhandled stmt {type(stmt)}")

    def _check_branch(self, block: ast.BlockStmt, narrow: dict[str, Type]) -> None:
        prev = self.scope
        self.scope = Scope(self.scope)
        for name, ty in narrow.items():
            existing = self.scope.parent.get(name) if self.scope.parent else None
            mutable = existing.mutable if existing else False
            self.scope.symbols[name] = Symbol(ty, mutable=mutable)
        for s in block.statements:
            self._check_stmt(s)
        self.scope = prev

    def _narrowings(self, expr: ast.Expr) -> tuple[dict[str, Type], dict[str, Type]]:
        if isinstance(expr, ast.BinaryExpr) and isinstance(expr.left, ast.VariableExpr) and isinstance(expr.right, ast.LiteralExpr) and expr.right.value is None:
            sym = self.scope.get(expr.left.name)
            if sym and is_option(sym.type_):
                inner = option_inner(sym.type_)
                if expr.op == "!=":
                    return ({expr.left.name: inner}, {})
                if expr.op == "==":
                    return ({}, {expr.left.name: inner})
        return ({}, {})

    def _unknown_name(self, name: str, span) -> ThirstyError:
        candidates = self.scope.flatten_names() + list(KEYWORDS.keys())
        suggestion = nearest_word(name, candidates)
        msg = f"unresolved identifier '{name}'"
        if suggestion:
            msg += f" (did you mean '{suggestion}'?)"
        return ThirstyError("THIRSTY-E011", msg, span)

    def _assignable(self, expect: Type, actual: Type) -> bool:
        if equals(expect, actual):
            return True
        if expect.name == actual.name and len(expect.args) == len(actual.args):
            if all(e == ANY or self._assignable(e, a) for e, a in zip(expect.args, actual.args)):
                return True
        if is_option(expect) and actual == option(ANY):
            return True
        if is_option(expect) and actual == option(option_inner(expect)):
            return True
        return False

    def _check_expr(self, expr: ast.Expr) -> Type:
        if isinstance(expr, ast.LiteralExpr):
            if expr.value is None:
                return option(ANY)
            if isinstance(expr.value, bool):
                return BOOL
            if isinstance(expr.value, int) and not isinstance(expr.value, bool):
                return INT
            if isinstance(expr.value, float):
                return FLOAT
            if isinstance(expr.value, str):
                return STRING
            return ANY
        if isinstance(expr, ast.VariableExpr):
            sym = self.scope.get(expr.name)
            if not sym:
                raise self._unknown_name(expr.name, expr.span)
            return sym.type_
        if isinstance(expr, ast.ThisExpr):
            sym = self.scope.get("this")
            if not sym:
                raise ThirstyError("THIRSTY-E011", "'this' outside of class context", expr.span)
            return sym.type_
        if isinstance(expr, ast.InputExpr):
            return option(STRING) if expr.safe else STRING
        if isinstance(expr, ast.ArrayExpr):
            if not expr.items:
                return reservoir(ANY)
            first = self._check_expr(expr.items[0])
            for item in expr.items[1:]:
                if not equals(first, self._check_expr(item)):
                    raise ThirstyError("THIRSTY-E021", "array items must share a common type", item.span)
            return reservoir(first)
        if isinstance(expr, ast.AssignExpr):
            target_t = self._check_expr(expr.target)
            value_t = self._check_expr(expr.value)
            if isinstance(expr.target, ast.VariableExpr):
                sym = self.scope.get(expr.target.name)
                if not sym:
                    raise self._unknown_name(expr.target.name, expr.span)
                if not sym.mutable:
                    raise ThirstyError("THIRSTY-E020", f"cannot assign to immutable binding '{expr.target.name}'", expr.span)
            if not self._assignable(target_t, value_t):
                raise ThirstyError("THIRSTY-E021", f"type mismatch: expected {target_t}, got {value_t}", expr.span)
            return target_t
        if isinstance(expr, ast.UnaryExpr):
            rt = self._check_expr(expr.right)
            if expr.op == "!" and equals(rt, BOOL):
                return BOOL
            if expr.op == "-" and (equals(rt, INT) or equals(rt, FLOAT)):
                return rt
            raise ThirstyError("THIRSTY-E021", f"invalid unary operator '{expr.op}' for {rt}", expr.span)
        if isinstance(expr, ast.BinaryExpr):
            lt = self._check_expr(expr.left)
            rt = self._check_expr(expr.right)
            if expr.op in {"+", "-", "*", "/", "%"}:
                if equals(lt, rt) and lt in (INT, FLOAT, STRING):
                    return lt
                raise ThirstyError("THIRSTY-E021", f"operator '{expr.op}' expects matching numeric/string operands", expr.span)
            if expr.op in {"==", "!=", "<", "<=", ">", ">="}:
                if equals(lt, rt) or rt == option(ANY) or lt == option(ANY):
                    return BOOL
                raise ThirstyError("THIRSTY-E021", f"cannot compare {lt} and {rt}", expr.span)
            if expr.op in {"&&", "||"}:
                if equals(lt, BOOL) and equals(rt, BOOL):
                    return BOOL
                raise ThirstyError("THIRSTY-E021", "logical operators expect Bool", expr.span)
        if isinstance(expr, ast.PipeExpr):
            left_t = self._check_expr(expr.left)
            return self._check_pipe(left_t, expr.right)
        if isinstance(expr, ast.GuardExpr):
            cond_t = self._check_expr(expr.condition)
            if not equals(cond_t, BOOL):
                raise ThirstyError("THIRSTY-E022", "guard condition must be Bool", expr.condition.span)
            tt = self._check_expr(expr.when_true)
            if expr.when_false is None:
                return tt
            ft = self._check_expr(expr.when_false)
            if equals(tt, ft):
                return tt
            return ANY
        if isinstance(expr, ast.CallExpr):
            return self._check_call(expr)
        if isinstance(expr, ast.MemberExpr):
            obj_t = self._check_expr(expr.obj)
            return self._check_member(obj_t, expr.name, expr.span)
        if isinstance(expr, ast.IndexExpr):
            obj_t = self._check_expr(expr.obj)
            idx_t = self._check_expr(expr.index)
            if not equals(idx_t, INT):
                raise ThirstyError("THIRSTY-E032", "index must be Int", expr.index.span)
            if obj_t.name == "Reservoir" and obj_t.args:
                return obj_t.args[0]
            return ANY
        if isinstance(expr, ast.NewExpr):
            if expr.class_name not in self.classes:
                raise ThirstyError("THIRSTY-E011", f"unknown class '{expr.class_name}'", expr.span)
            info = self.classes[expr.class_name]
            init = info.methods.get("init")
            if init:
                params, _, _ = init
                self._check_call_arity(expr.args, params, expr.span)
            return Type(expr.class_name)
        if isinstance(expr, ast.AwaitExpr):
            value_t = self._check_expr(expr.expr)
            if value_t.name == "Task" and value_t.args:
                return value_t.args[0]
            raise ThirstyError("THIRSTY-E021", "await expects Task", expr.span)
        if isinstance(expr, ast.CondenseExpr):
            value_t = self._check_expr(expr.expr)
            return option_inner(value_t) if is_option(value_t) else value_t
        if isinstance(expr, ast.EvaporateExpr):
            self._check_expr(expr.expr)
            return option(ANY)
        raise RuntimeError(f"unhandled expr {type(expr)}")

    def _check_pipe(self, left_t: Type, right: ast.Expr) -> Type:
        if isinstance(right, ast.VariableExpr):
            sym = self.scope.get(right.name)
            if sym and sym.type_.name in {"BuiltinFn", "Function"} and len(sym.type_.args) >= 2:
                first = sym.type_.args[0]
                if not self._assignable(first, left_t):
                    raise ThirstyError("THIRSTY-E021", f"pipe cannot feed {left_t} into {right.name}", right.span)
                return sym.type_.args[-1]
        if isinstance(right, ast.CallExpr):
            callee_t = self._check_expr(right.callee)
            if callee_t.name in {"BuiltinFn", "Function"} and len(callee_t.args) >= 2:
                expected = list(callee_t.args[:-1])
                result = callee_t.args[-1]
                if not expected:
                    return result
                if not self._assignable(expected[0], left_t):
                    raise ThirstyError("THIRSTY-E021", "pipe input type mismatch", right.span)
                if len(right.args) != len(expected) - 1:
                    raise ThirstyError("THIRSTY-E030", "pipe call arity mismatch", right.span)
                for arg_expr, exp in zip(right.args, expected[1:]):
                    if not self._assignable(exp, self._check_expr(arg_expr)):
                        raise ThirstyError("THIRSTY-E021", "pipe argument type mismatch", arg_expr.span)
                return result
        return ANY

    def _check_member(self, obj_t: Type, name: str, span) -> Type:
        if obj_t.name == "Module" and obj_t.args:
            mod_name = obj_t.args[0].name
            base = mod_name.split("::")[-1]
            members = self.module_types.get(base) or self.module_types.get(mod_name) or {}
            if name in members:
                return members[name]
        if obj_t.name == "Reservoir" and obj_t.args:
            inner = obj_t.args[0]
            method_returns = {
                "size": INT,
                "push": VOID,
                "get": inner,
                "strain": obj_t,
                "transmute": reservoir(ANY),
                "distill": ANY,
                "flood": obj_t,
            }
            if name in method_returns:
                return Type("BuiltinMethod", (obj_t, method_returns[name]))
        if obj_t.name == "Task" and name == "value":
            return obj_t.args[0]
        if obj_t.name in self.classes:
            info = self.classes[obj_t.name]
            if name in info.fields:
                return info.fields[name]
            if name in info.methods:
                params, result, is_async = info.methods[name]
                final = result
                if is_async and result.name != "Task":
                    final = task(result)
                return Type("Function", tuple(params + [final]))
        return ANY

    def _check_call(self, expr: ast.CallExpr) -> Type:
        callee_t = self._check_expr(expr.callee)
        if callee_t.name == "BuiltinMethod" and isinstance(expr.callee, ast.MemberExpr):
            obj_t = self._check_expr(expr.callee.obj)
            inner = obj_t.args[0] if obj_t.args else ANY
            name = expr.callee.name
            if name == "size":
                self._check_call_arity(expr.args, [], expr.span); return INT
            if name == "push":
                self._check_call_arity(expr.args, [inner], expr.span); return VOID
            if name == "get":
                self._check_call_arity(expr.args, [INT], expr.span); return inner
            if name == "strain":
                self._check_call_arity(expr.args, [ANY], expr.span); return obj_t
            if name == "transmute":
                self._check_call_arity(expr.args, [ANY], expr.span); return reservoir(ANY)
            if name == "distill":
                self._check_call_arity(expr.args, [ANY, ANY], expr.span); return ANY
            if name == "flood":
                self._check_call_arity(expr.args, [ANY], expr.span); return obj_t
        if callee_t.name == "BuiltinFn":
            params = list(callee_t.args[:-1])
            self._check_call_arity(expr.args, params, expr.span)
            for arg_expr, exp in zip(expr.args, params):
                got = self._check_expr(arg_expr)
                if not self._assignable(exp, got):
                    raise ThirstyError("THIRSTY-E021", f"expected {exp}, got {got}", arg_expr.span)
            result = callee_t.args[-1]
            return option(result) if expr.safe else result
        if callee_t.name == "Function":
            params = list(callee_t.args[:-1])
            self._check_call_arity(expr.args, params, expr.span)
            for arg_expr, exp in zip(expr.args, params):
                got = self._check_expr(arg_expr)
                if not self._assignable(exp, got):
                    raise ThirstyError("THIRSTY-E021", f"expected {exp}, got {got}", arg_expr.span)
            result = callee_t.args[-1]
            return option(result) if expr.safe else result
        raise ThirstyError("THIRSTY-E031", "expression is not callable", expr.span)

    def _check_call_arity(self, args: list[ast.Expr], params: list[Type], span) -> None:
        if len(args) != len(params):
            raise ThirstyError("THIRSTY-E030", f"arity mismatch: expected {len(params)}, got {len(args)}", span)
