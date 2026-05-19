
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from . import ast
from .module_system import builtin_modules, resolve_module_file, ModuleValue
from .token import Span


class RuntimeFault(Exception):
    def __init__(self, code: str, message: str, span: Span) -> None:
        self.code = code
        self.message = message
        self.span = span
        super().__init__(message)


class ReturnSignal(Exception):
    def __init__(self, value: Any) -> None:
        self.value = value


class TailCallSignal(Exception):
    def __init__(self, fn: "UserFunction", args: list[Any]) -> None:
        self.fn = fn
        self.args = args


class ThrownSignal(Exception):
    def __init__(self, value: Any) -> None:
        self.value = value


class Env:
    def __init__(self, parent: "Env | None" = None) -> None:
        self.parent = parent
        self.values: dict[str, Any] = {}
        self.mutable: dict[str, bool] = {}
        self.types: dict[str, str] = {}

    def define(self, name: str, value: Any, mutable: bool = False, type_name: str | None = None) -> None:
        self.values[name] = value
        self.mutable[name] = mutable
        if type_name:
            self.types[name] = type_name

    def assign(self, name: str, value: Any) -> None:
        if name in self.values:
            if not self.mutable.get(name, False):
                raise RuntimeError(f"cannot assign to immutable binding '{name}'")
            self.values[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise RuntimeError(f"unknown binding '{name}'")

    def get(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"unknown binding '{name}'")

    def describe(self) -> dict[str, str]:
        out: dict[str, str] = {}
        cur: Env | None = self
        while cur:
            for k, v in cur.values.items():
                if k not in out:
                    ty = cur.types.get(k, type(v).__name__)
                    out[k] = ty
            cur = cur.parent
        return dict(sorted(out.items()))


@dataclass
class TaskValue:
    value: Any

    def await_value(self) -> Any:
        return self.value


@dataclass
class UserFunction:
    decl: ast.FunctionDecl
    closure: Env
    interpreter: "Interpreter"
    bound_this: "UserInstance | None" = None

    def bind(self, instance: "UserInstance") -> "UserFunction":
        return UserFunction(self.decl, self.closure, self.interpreter, bound_this=instance)

    def __call__(self, args: list[Any]) -> Any:
        return self.interpreter.call_function(self, args)


@dataclass
class UserClass:
    name: str
    fields: dict[str, Any]
    methods: dict[str, UserFunction]

    def instantiate(self, interpreter: "Interpreter", args: list[Any]) -> "UserInstance":
        inst = UserInstance(self, dict(self.fields))
        if "init" in self.methods:
            self.methods["init"].bind(inst)(args)
        return inst


@dataclass
class UserInstance:
    cls: UserClass
    fields: dict[str, Any]

    def get(self, name: str) -> Any:
        if name in self.fields:
            return self.fields[name]
        if name in self.cls.methods:
            return self.cls.methods[name].bind(self)
        raise RuntimeError(f"unknown property '{name}' on {self.cls.name}")

    def set(self, name: str, value: Any) -> None:
        self.fields[name] = value


class Interpreter:
    def __init__(self, input_provider=None, trace: bool = False, thirst_level: int = 1, recursion_limit: int = 256, current_file: str = "<memory>", project_root: str | None = None) -> None:
        self.globals = Env()
        self.output: list[str] = []
        self.input_provider = input_provider or (lambda: input())
        self.trace = trace
        self.thirst_level = thirst_level
        self.recursion_limit = recursion_limit
        self.call_depth = 0
        self.achievements: set[str] = set()
        self.current_file = current_file
        self.project_root = Path(project_root).resolve() if project_root else Path(current_file).resolve().parent
        self.module_cache: dict[str, ModuleValue] = {}
        self._install_builtins()

    def _trace(self, message: str) -> None:
        if self.trace:
            prefix = "💧" * max(1, self.thirst_level)
            self.output.append(f"{prefix} {message}")

    def _install_builtins(self) -> None:
        self.globals.define("length", lambda s: len(s))
        self.globals.define("contains", lambda s, n: n in s)
        self.globals.define("split", lambda s, sep: s.split(sep))
        self.globals.define("abs", lambda x: abs(x))
        self.globals.define("min", lambda a, b: min(a, b))
        self.globals.define("max", lambda a, b: max(a, b))
        self.globals.define("push", lambda items, value: items.append(value))
        self.globals.define("pop", lambda items: items.pop())
        self.globals.define("size", lambda items: len(items))
        self.globals.define("get", lambda items, index: items[index])
        self.globals.define("flood", self._builtin_flood)
        self.globals.define("condense", self._builtin_condense)
        self.globals.define("evaporate", lambda value: None)
        self.globals.define("strain", self._builtin_strain)
        self.globals.define("transmute", self._builtin_transmute)
        self.globals.define("distill", self._builtin_distill)
        for name, mod in builtin_modules().items():
            self.module_cache[name] = mod

    def _builtin_flood(self, items, payload):
        if isinstance(payload, list):
            items.extend(payload)
        else:
            items.append(payload)
        return items

    def _builtin_condense(self, value):
        if value is None:
            raise RuntimeError("cannot condense empty value")
        return value

    def _builtin_strain(self, items, fn):
        return [x for x in items if self._call_any(fn, [x])]

    def _builtin_transmute(self, items, fn):
        return [self._call_any(fn, [x]) for x in items]

    def _builtin_distill(self, items, seed, fn):
        acc = seed
        for item in items:
            acc = self._call_any(fn, [acc, item])
        return acc

    def run(self, program: ast.Program, call_main: bool = True) -> list[str]:
        self.current_file = program.span.file
        self.project_root = Path(self.current_file).resolve().parent if self.current_file not in {"<memory>", "<repl>"} else self.project_root
        for decl in program.declarations:
            if isinstance(decl, ast.ImportDecl):
                alias = decl.alias or decl.module.split("::")[-1].split("/")[-1].split(".")[0]
                self.globals.define(alias, self._load_module_value(decl.module), type_name=f"Module:{decl.module}")
        for decl in program.declarations:
            if isinstance(decl, ast.FunctionDecl):
                self.globals.define(decl.name, UserFunction(decl, self.globals, self), type_name="Function")
        for decl in program.declarations:
            if isinstance(decl, ast.ClassDecl):
                self.globals.define(decl.name, self._build_class(decl), type_name=decl.name)
        for decl in program.declarations:
            if isinstance(decl, (ast.FunctionDecl, ast.ClassDecl, ast.ImportDecl)):
                continue
            self._exec(decl, self.globals)
        if call_main and "main" in self.globals.values:
            main = self.globals.get("main")
            if callable(main):
                main([])
        if any(item == "thirsty" for item in self.output):
            self.achievements.add("sacred_echo")
        return self.output

    def call_function(self, fn: UserFunction, args: list[Any]) -> Any:
        self.call_depth += 1
        if self.call_depth > self.recursion_limit:
            self.call_depth -= 1
            raise RuntimeFault("THIRSTY-E900", "your recursion has run dry", fn.decl.span)
        self._trace(f"calling {fn.decl.name} with {len(args)} sips taken")
        current_fn = fn
        current_args = list(args)
        try:
            while True:
                env = Env(current_fn.closure)
                if current_fn.bound_this is not None:
                    env.define("this", current_fn.bound_this, mutable=True, type_name=current_fn.bound_this.cls.name)
                for param, value in zip(current_fn.decl.params, current_args):
                    env.define(param.name, value, type_name="param")
                try:
                    self._exec(current_fn.decl.body, env)
                    result = None
                except TailCallSignal as tail:
                    current_fn = tail.fn
                    current_args = tail.args
                    continue
                except ReturnSignal as ret:
                    result = ret.value
                return TaskValue(result) if current_fn.decl.is_async else result
        finally:
            self.call_depth -= 1

    def _call_any(self, callee, args):
        if isinstance(callee, UserFunction):
            return callee(args)
        if callable(callee):
            return callee(*args)
        raise RuntimeError("expression is not callable")

    def _load_module_value(self, module_spec: str) -> ModuleValue:
        if module_spec in self.module_cache:
            return self.module_cache[module_spec]
        if module_spec.startswith("thirst::"):
            mod = builtin_modules()[module_spec]
            self.module_cache[module_spec] = mod
            return mod
        source_file = resolve_module_file(module_spec, Path(self.current_file).resolve().parent if self.current_file not in {"<memory>", "<repl>"} else self.project_root)
        from .cli import parse_source, check_source
        text = Path(source_file).read_text(encoding="utf-8")
        program = parse_source(text, str(source_file))
        check_source(text, str(source_file))
        child = Interpreter(input_provider=self.input_provider, trace=self.trace, thirst_level=self.thirst_level, recursion_limit=self.recursion_limit, current_file=str(source_file), project_root=str(Path(source_file).parent))
        child.run(program, call_main=False)
        exports = {k: v for k, v in child.globals.values.items() if not k.startswith("_")}
        mod = ModuleValue(module_spec, exports)
        self.module_cache[module_spec] = mod
        return mod

    def _build_class(self, decl: ast.ClassDecl) -> UserClass:
        fields: dict[str, Any] = {}
        methods: dict[str, UserFunction] = {}
        for member in decl.members:
            if isinstance(member, ast.VarDecl):
                fields[member.name] = None
            elif isinstance(member, ast.FunctionDecl):
                methods[member.name] = UserFunction(member, self.globals, self)
        return UserClass(decl.name, fields, methods)

    def _exec_block(self, statements: list[ast.Stmt], env: Env) -> None:
        for stmt in statements:
            self._exec(stmt, env)

    def _exec(self, stmt: ast.Stmt, env: Env) -> None:
        if isinstance(stmt, ast.ImportDecl):
            return
        if isinstance(stmt, ast.VarDecl):
            value = self._eval(stmt.initializer, env)
            env.define(stmt.name, value, mutable=stmt.mutable and not stmt.is_field, type_name=str(getattr(stmt.type_node, "name", "Value")))
            return
        if isinstance(stmt, ast.FunctionDecl):
            if stmt.name not in env.values:
                env.define(stmt.name, UserFunction(stmt, env, self), type_name="Function")
            return
        if isinstance(stmt, ast.ClassDecl):
            if stmt.name not in env.values:
                env.define(stmt.name, self._build_class(stmt), type_name=stmt.name)
            return
        if isinstance(stmt, ast.BlockStmt):
            self._exec_block(stmt.statements, Env(env))
            return
        if isinstance(stmt, ast.PrintStmt):
            try:
                self.output.append(self._stringify(self._eval(stmt.expr, env)))
            except Exception:
                if not stmt.safe:
                    raise
                self.output.append("empty")
            return
        if isinstance(stmt, ast.ExprStmt):
            self._eval(stmt.expr, env)
            return
        if isinstance(stmt, ast.ReturnStmt):
            if isinstance(stmt.expr, ast.CallExpr):
                callee = self._eval(stmt.expr.callee, env)
                args = [self._eval(a, env) for a in stmt.expr.args]
                if isinstance(callee, UserFunction):
                    raise TailCallSignal(callee, args)
            value = None if stmt.expr is None else self._eval(stmt.expr, env)
            raise ReturnSignal(value)
        if isinstance(stmt, ast.ThrowStmt):
            raise ThrownSignal(self._eval(stmt.expr, env))
        if isinstance(stmt, ast.DripStmt):
            current = env.get(stmt.name)
            amt = 1 if stmt.amount is None else self._eval(stmt.amount, env)
            env.assign(stmt.name, current + amt)
            return
        if isinstance(stmt, ast.IfStmt):
            cond = self._eval(stmt.condition, env)
            if not isinstance(cond, bool):
                raise RuntimeFault("THIRSTY-E022", "if condition must evaluate to Bool", stmt.condition.span)
            if cond:
                self._exec(stmt.then_branch, env)
            elif stmt.else_branch:
                self._exec(stmt.else_branch, env)
            return
        if isinstance(stmt, ast.LoopStmt):
            count = self._eval(stmt.count, env)
            if not isinstance(count, int):
                raise RuntimeFault("THIRSTY-E023", "loop count must evaluate to Int", stmt.count.span)
            if count < 0:
                raise RuntimeFault("THIRSTY-E023", "loop count must be non-negative", stmt.count.span)
            for _ in range(count):
                self._exec(stmt.body, env)
            return
        if isinstance(stmt, ast.TryStmt):
            try:
                self._exec(stmt.try_block, env)
            except ThrownSignal as thrown:
                handled = False
                for catch in stmt.catches:
                    if catch.type_name == "Error" or self._match_catch(catch.type_name, thrown.value):
                        catch_env = Env(env)
                        catch_env.define(catch.name, thrown.value, type_name=catch.type_name)
                        self._exec(catch.block, catch_env)
                        handled = True
                        break
                if not handled:
                    raise
            finally:
                if stmt.finally_block:
                    self._exec(stmt.finally_block, env)
            return
        raise RuntimeError(f"unhandled stmt {type(stmt)}")

    def _match_catch(self, type_name: str, value: Any) -> bool:
        if isinstance(value, UserInstance):
            return value.cls.name == type_name
        return type_name == type(value).__name__

    def _eval(self, expr: ast.Expr, env: Env) -> Any:
        if isinstance(expr, ast.LiteralExpr):
            return expr.value
        if isinstance(expr, ast.VariableExpr):
            return env.get(expr.name)
        if isinstance(expr, ast.ThisExpr):
            return env.get("this")
        if isinstance(expr, ast.InputExpr):
            try:
                value = self.input_provider()
                if expr.safe and value == "":
                    return None
                return value
            except Exception:
                if expr.safe:
                    return None
                raise
        if isinstance(expr, ast.ArrayExpr):
            return [self._eval(x, env) for x in expr.items]
        if isinstance(expr, ast.AssignExpr):
            value = self._eval(expr.value, env)
            if isinstance(expr.target, ast.VariableExpr):
                env.assign(expr.target.name, value)
                return value
            if isinstance(expr.target, ast.MemberExpr):
                obj = self._eval(expr.target.obj, env)
                if isinstance(obj, UserInstance):
                    obj.set(expr.target.name, value)
                    return value
                raise RuntimeFault("THIRSTY-E021", "member assignment expects object instance", expr.span)
            if isinstance(expr.target, ast.IndexExpr):
                items = self._eval(expr.target.obj, env)
                idx = self._eval(expr.target.index, env)
                items[idx] = value
                return value
            raise RuntimeFault("THIRSTY-E001", "invalid assignment target", expr.span)
        if isinstance(expr, ast.UnaryExpr):
            right = self._eval(expr.right, env)
            if expr.op == "!":
                return not right
            if expr.op == "-":
                return -right
        if isinstance(expr, ast.BinaryExpr):
            left = self._eval(expr.left, env)
            right = self._eval(expr.right, env)
            return self._apply_binary(expr.op, left, right, expr.span)
        if isinstance(expr, ast.PipeExpr):
            left = self._eval(expr.left, env)
            return self._eval_pipe(left, expr.right, env)
        if isinstance(expr, ast.GuardExpr):
            cond = self._eval(expr.condition, env)
            return self._eval(expr.when_true if cond else (expr.when_false or ast.LiteralExpr(expr.span, None)), env)
        if isinstance(expr, ast.CallExpr):
            try:
                callee = self._eval(expr.callee, env)
                args = [self._eval(a, env) for a in expr.args]
                return self._call_any(callee, args)
            except Exception:
                if expr.safe:
                    return None
                raise
        if isinstance(expr, ast.MemberExpr):
            obj = self._eval(expr.obj, env)
            if isinstance(obj, ModuleValue):
                if expr.name not in obj.members:
                    raise RuntimeFault("THIRSTY-E021", f"unknown module member '{expr.name}'", expr.span)
                return obj.members[expr.name]
            if isinstance(obj, UserInstance):
                return obj.get(expr.name)
            if isinstance(obj, TaskValue) and expr.name == "value":
                return obj.value
            if isinstance(obj, dict):
                return obj[expr.name]
            if isinstance(obj, list):
                return self._list_member(obj, expr.name)
            raise RuntimeFault("THIRSTY-E021", f"cannot access member '{expr.name}'", expr.span)
        if isinstance(expr, ast.IndexExpr):
            obj = self._eval(expr.obj, env)
            idx = self._eval(expr.index, env)
            try:
                return obj[idx]
            except Exception as exc:
                raise RuntimeFault("THIRSTY-E100", f"indexing failed: {exc}", expr.span)
        if isinstance(expr, ast.NewExpr):
            cls = env.get(expr.class_name)
            args = [self._eval(a, env) for a in expr.args]
            if not isinstance(cls, UserClass):
                raise RuntimeFault("THIRSTY-E011", f"unknown class '{expr.class_name}'", expr.span)
            return cls.instantiate(self, args)
        if isinstance(expr, ast.AwaitExpr):
            value = self._eval(expr.expr, env)
            if isinstance(value, TaskValue):
                return value.await_value()
            raise RuntimeFault("THIRSTY-E021", "await expects Task", expr.span)
        if isinstance(expr, ast.CondenseExpr):
            value = self._eval(expr.expr, env)
            if value is None:
                raise RuntimeFault("THIRSTY-E901", "cannot condense an empty spring", expr.span)
            return value
        if isinstance(expr, ast.EvaporateExpr):
            self._eval(expr.expr, env)
            return None
        raise RuntimeError(f"unhandled expr {type(expr)}")

    def _eval_pipe(self, left: Any, right: ast.Expr, env: Env) -> Any:
        if isinstance(right, ast.VariableExpr):
            callee = self._eval(right, env)
            return self._call_any(callee, [left])
        if isinstance(right, ast.CallExpr):
            callee = self._eval(right.callee, env)
            args = [left] + [self._eval(a, env) for a in right.args]
            return self._call_any(callee, args)
        raise RuntimeFault("THIRSTY-E021", "pipe expects callable target", right.span)

    def _list_member(self, items: list[Any], name: str):
        if name == "size":
            return lambda: len(items)
        if name == "push":
            return lambda value: items.append(value)
        if name == "get":
            return lambda index: items[index]
        if name == "flood":
            return lambda payload: self._builtin_flood(items, payload)
        if name == "strain":
            return lambda fn: self._builtin_strain(items, fn)
        if name == "transmute":
            return lambda fn: self._builtin_transmute(items, fn)
        if name == "distill":
            return lambda seed, fn: self._builtin_distill(items, seed, fn)
        raise RuntimeFault("THIRSTY-E021", f"unknown reservoir method '{name}'", Span("<runtime>", 1, 1, 1, 1))

    def _apply_binary(self, op: str, left: Any, right: Any, span: Span) -> Any:
        try:
            if op == "+": return left + right
            if op == "-": return left - right
            if op == "*": return left * right
            if op == "/": return left / right
            if op == "%": return left % right
            if op == "==": return left == right
            if op == "!=": return left != right
            if op == "<": return left < right
            if op == "<=": return left <= right
            if op == ">": return left > right
            if op == ">=": return left >= right
            if op == "&&": return bool(left) and bool(right)
            if op == "||": return bool(left) or bool(right)
        except ZeroDivisionError:
            raise RuntimeFault("THIRSTY-E101", "division by zero", span)
        raise RuntimeFault("THIRSTY-E021", f"unsupported operator '{op}'", span)

    def _stringify(self, value: Any) -> str:
        if value is None:
            return "empty"
        if isinstance(value, bool):
            return "parched" if value else "quenched"
        return str(value)
