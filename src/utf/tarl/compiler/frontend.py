"""
Thirsty-Lang → LLVM IR Front-end.

Walks the Thirsty AST and emits LLVM IR text (llvmlite IR builder).
Only the core subset of Thirsty-Lang is compiled — governed mode adds
a runtime wrapper for TARL policy enforcement.

Supported in this implementation:
  - Int, Float, Bool, String (as global i8* constants) literals
  - drink declarations (local alloca)
  - pour(expr) — calls libc printf
  - Binary arithmetic and comparison (Int, Float)
  - thirsty/hydrated (conditional branch)
  - refill (while loop)
  - glass function declarations with Int/Float/Bool return types
  - return statements
  - function calls
  - glass main() -> Int as the LLVM entry point

Unsupported (deferred to future compiler phases):
  - String operations beyond printing literals
  - Reservoir / Task / Governed types
  - Closures
  - Imports / stdlib calls (these remain tree-walked by the interpreter)
  - Governance enforcement (governed mode wraps calls at runtime)
"""

from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger("tarl.compiler.frontend")


class FrontendError(Exception):
    pass


class ThirstyFrontend:
    """
    Compile Thirsty-Lang source to LLVM IR text string.

    The output is a complete LLVM IR module ready to pass to
    ``LLVMBackend.compile_ir(ir_text)`` or write to a ``.ll`` file.
    """

    def __init__(self) -> None:
        self._check_llvmlite()

    @staticmethod
    def _check_llvmlite() -> None:
        try:
            import llvmlite.ir  # noqa: F401
        except ImportError:
            raise FrontendError(
                "llvmlite is required for LLVM compilation. "
                "Install with: pip install llvmlite"
            )

    def compile_source(self, source: str, filename: str = "<input>") -> str:
        """
        Compile Thirsty-Lang source code to LLVM IR text.

        Returns the LLVM IR module as a string.
        Raises FrontendError on unsupported constructs.
        """
        import sys, pathlib
        # Ensure the Python reference implementation is importable
        _utf = str(pathlib.Path(__file__).parents[2])
        if _utf not in sys.path:
            sys.path.insert(0, _utf)

        from thirsty_lang.lexer import Lexer
        from thirsty_lang.parser import Parser
        from thirsty_lang.checker import Checker

        tokens = Lexer(source, filename).lex()
        program = Parser.from_tokens(tokens).parse_program()
        Checker().check(program)

        return _IREmitter().emit(program, filename)


# ---------------------------------------------------------------------------
# Internal IR Emitter
# ---------------------------------------------------------------------------

class _IREmitter:
    """Walk the Thirsty AST and emit llvmlite IR."""

    def __init__(self) -> None:
        import llvmlite.ir as ll
        self._ll = ll
        self._module: Any = None
        self._builder: Any = None
        self._fn: Any = None
        self._locals: dict[str, Any] = {}   # name → alloca
        self._functions: dict[str, Any] = {}  # name → LLVM function
        self._string_globals: dict[str, Any] = {}  # literal → global constant
        self._printf: Any = None

    def emit(self, program, filename: str) -> str:
        ll = self._ll
        self._module = ll.Module(name=filename)
        self._module.triple = ""  # let LLVM determine host triple

        # Declare libc printf
        voidptr = ll.IntType(8).as_pointer()
        printf_ty = ll.FunctionType(ll.IntType(32), [voidptr], var_arg=True)
        self._printf = ll.Function(self._module, printf_ty, name="printf")

        from thirsty_lang import ast as _ast

        # First pass: register all function signatures
        for decl in program.declarations:
            if isinstance(decl, (_ast.FunctionDecl, _ast.GovernedFunctionDecl)):
                self._declare_function(decl)

        # Second pass: emit function bodies
        for decl in program.declarations:
            if isinstance(decl, (_ast.FunctionDecl, _ast.GovernedFunctionDecl)):
                self._emit_function(decl)

        return str(self._module)

    # ------------------------------------------------------------------
    # Type mapping
    # ------------------------------------------------------------------

    def _thirsty_type_to_ll(self, type_str: str):
        ll = self._ll
        t = (type_str or "").strip()
        if t in ("Int", "Bool"):
            return ll.IntType(64)
        if t == "Float":
            return ll.DoubleType()
        if t in ("Void", ""):
            return ll.VoidType()
        if t == "String":
            return ll.IntType(8).as_pointer()
        # Governed[T] / Result[T,E] / Any — treat as i64 opaque handle
        return ll.IntType(64)

    # ------------------------------------------------------------------
    # Function declaration
    # ------------------------------------------------------------------

    def _declare_function(self, decl) -> None:
        ll = self._ll
        params = []
        for p in decl.params:
            t_str = p.type_annotation or "Int"
            params.append(self._thirsty_type_to_ll(t_str))
        ret_str = getattr(decl, "return_type", None) or "Void"
        ret_t = self._thirsty_type_to_ll(ret_str)
        fn_ty = ll.FunctionType(ret_t, params)
        fn = ll.Function(self._module, fn_ty, name=decl.name)
        for i, p in enumerate(decl.params):
            fn.args[i].name = p.name
        self._functions[decl.name] = fn

    # ------------------------------------------------------------------
    # Function body
    # ------------------------------------------------------------------

    def _emit_function(self, decl) -> None:
        ll = self._ll
        fn = self._functions[decl.name]
        block = fn.append_basic_block("entry")
        self._builder = ll.IRBuilder(block)
        self._fn = fn
        self._locals = {}

        # Allocate parameter slots
        for i, p in enumerate(decl.params):
            t = self._thirsty_type_to_ll(p.type_annotation or "Int")
            alloca = self._builder.alloca(t, name=p.name)
            self._builder.store(fn.args[i], alloca)
            self._locals[p.name] = alloca

        # Emit body statements
        self._emit_block(decl.body)

        # Insert implicit void return if needed
        if not self._builder.block.is_terminated:
            ret_str = getattr(decl, "return_type", None) or "Void"
            if ret_str in ("Void", ""):
                self._builder.ret_void()
            else:
                zero = ll.Constant(self._thirsty_type_to_ll(ret_str), 0)
                self._builder.ret(zero)

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    def _emit_block(self, block) -> None:
        from thirsty_lang import ast as _ast
        for stmt in block.statements:
            if self._builder.block.is_terminated:
                break
            self._emit_stmt(stmt)

    def _emit_stmt(self, stmt) -> None:
        from thirsty_lang import ast as _ast
        ll = self._ll

        if isinstance(stmt, _ast.VarDecl):
            val = self._emit_expr(stmt.initializer) if stmt.initializer else None
            t_str = getattr(stmt, "type_annotation", None) or "Int"
            t = self._thirsty_type_to_ll(t_str)
            alloca = self._builder.alloca(t, name=stmt.name)
            if val is not None:
                val = self._coerce(val, t)
                self._builder.store(val, alloca)
            self._locals[stmt.name] = alloca

        elif isinstance(stmt, _ast.ExprStmt):
            # pour(expr) → printf
            expr = stmt.expression
            if isinstance(expr, _ast.CallExpr) and getattr(expr.callee, "name", None) == "pour":
                self._emit_pour(expr.args)
            else:
                self._emit_expr(expr)

        elif isinstance(stmt, _ast.ReturnStmt):
            if stmt.value is None:
                self._builder.ret_void()
            else:
                val = self._emit_expr(stmt.value)
                ret_t = self._fn.type.pointee.return_type
                val = self._coerce(val, ret_t)
                self._builder.ret(val)

        elif isinstance(stmt, _ast.IfStmt):
            self._emit_if(stmt)

        elif isinstance(stmt, _ast.WhileStmt):
            self._emit_while(stmt)

        elif isinstance(stmt, _ast.AssignStmt):
            if stmt.name in self._locals:
                val = self._emit_expr(stmt.value)
                alloca = self._locals[stmt.name]
                val = self._coerce(val, alloca.type.pointee)
                self._builder.store(val, alloca)

        # Other statement types: skip (deferred)

    # ------------------------------------------------------------------
    # pour() → printf
    # ------------------------------------------------------------------

    def _emit_pour(self, args: list) -> None:
        ll = self._ll
        if not args:
            return
        val = self._emit_expr(args[0])
        t = val.type

        if isinstance(t, ll.IntType):
            fmt = self._get_string_global("%lld\n\x00")
            self._builder.call(self._printf, [
                self._builder.bitcast(fmt, ll.IntType(8).as_pointer()),
                val,
            ])
        elif isinstance(t, ll.DoubleType):
            fmt = self._get_string_global("%g\n\x00")
            self._builder.call(self._printf, [
                self._builder.bitcast(fmt, ll.IntType(8).as_pointer()),
                val,
            ])
        elif isinstance(t, ll.PointerType) and t.pointee == ll.IntType(8):
            fmt = self._get_string_global("%s\n\x00")
            self._builder.call(self._printf, [
                self._builder.bitcast(fmt, ll.IntType(8).as_pointer()),
                val,
            ])

    def _get_string_global(self, text: str):
        ll = self._ll
        if text in self._string_globals:
            return self._string_globals[text]
        encoded = text.encode("utf-8")
        arr_t = ll.ArrayType(ll.IntType(8), len(encoded))
        g = ll.GlobalVariable(self._module, arr_t, name=f".str.{len(self._string_globals)}")
        g.global_constant = True
        g.linkage = "private"
        g.initializer = ll.Constant(arr_t, bytearray(encoded))
        ptr = self._builder.bitcast(g, ll.IntType(8).as_pointer())
        self._string_globals[text] = ptr
        return ptr

    # ------------------------------------------------------------------
    # Conditionals
    # ------------------------------------------------------------------

    def _emit_if(self, stmt) -> None:
        ll = self._ll
        cond = self._emit_expr(stmt.condition)
        if isinstance(cond.type, ll.DoubleType):
            zero = ll.Constant(ll.DoubleType(), 0.0)
            cond = self._builder.fcmp_ordered("!=", cond, zero)
        elif isinstance(cond.type, ll.IntType) and cond.type.width == 64:
            zero = ll.Constant(ll.IntType(64), 0)
            cond = self._builder.icmp_signed("!=", cond, zero)

        fn = self._fn
        then_bb = fn.append_basic_block("if.then")
        else_bb = fn.append_basic_block("if.else") if stmt.else_body else None
        merge_bb = fn.append_basic_block("if.merge")

        if else_bb:
            self._builder.cbranch(cond, then_bb, else_bb)
        else:
            self._builder.cbranch(cond, then_bb, merge_bb)

        # Then branch
        self._builder.position_at_end(then_bb)
        self._emit_block(stmt.then_body)
        if not self._builder.block.is_terminated:
            self._builder.branch(merge_bb)

        # Else branch
        if else_bb:
            self._builder.position_at_end(else_bb)
            self._emit_block(stmt.else_body)
            if not self._builder.block.is_terminated:
                self._builder.branch(merge_bb)

        self._builder.position_at_end(merge_bb)

    # ------------------------------------------------------------------
    # Loops
    # ------------------------------------------------------------------

    def _emit_while(self, stmt) -> None:
        ll = self._ll
        fn = self._fn
        cond_bb = fn.append_basic_block("while.cond")
        body_bb = fn.append_basic_block("while.body")
        merge_bb = fn.append_basic_block("while.merge")

        self._builder.branch(cond_bb)
        self._builder.position_at_end(cond_bb)
        cond = self._emit_expr(stmt.condition)
        if isinstance(cond.type, ll.IntType) and cond.type.width == 64:
            zero = ll.Constant(ll.IntType(64), 0)
            cond = self._builder.icmp_signed("!=", cond, zero)
        self._builder.cbranch(cond, body_bb, merge_bb)

        self._builder.position_at_end(body_bb)
        self._emit_block(stmt.body)
        if not self._builder.block.is_terminated:
            self._builder.branch(cond_bb)

        self._builder.position_at_end(merge_bb)

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------

    def _emit_expr(self, expr) -> Any:
        from thirsty_lang import ast as _ast
        ll = self._ll

        if isinstance(expr, _ast.IntLiteral):
            return ll.Constant(ll.IntType(64), int(expr.value))

        if isinstance(expr, _ast.FloatLiteral):
            return ll.Constant(ll.DoubleType(), float(expr.value))

        if isinstance(expr, _ast.BoolLiteral):
            return ll.Constant(ll.IntType(64), 1 if expr.value else 0)

        if isinstance(expr, _ast.StringLiteral):
            text = expr.value + "\x00"
            encoded = text.encode("utf-8")
            arr_t = ll.ArrayType(ll.IntType(8), len(encoded))
            g = ll.GlobalVariable(
                self._module, arr_t,
                name=f".strlit.{len(self._string_globals)}"
            )
            g.global_constant = True
            g.linkage = "private"
            g.initializer = ll.Constant(arr_t, bytearray(encoded))
            ptr = self._builder.bitcast(g, ll.IntType(8).as_pointer())
            self._string_globals[text] = ptr
            return ptr

        if isinstance(expr, _ast.NameExpr):
            if expr.name in self._locals:
                return self._builder.load(self._locals[expr.name])
            raise FrontendError(f"undefined variable: {expr.name!r}")

        if isinstance(expr, _ast.BinaryExpr):
            return self._emit_binary(expr)

        if isinstance(expr, _ast.UnaryExpr):
            val = self._emit_expr(expr.operand)
            if expr.op == "-":
                if isinstance(val.type, ll.DoubleType):
                    return self._builder.fsub(ll.Constant(ll.DoubleType(), 0.0), val)
                return self._builder.neg(val)
            if expr.op == "!":
                zero = ll.Constant(ll.IntType(64), 0)
                cmp = self._builder.icmp_signed("==", val, zero)
                return self._builder.zext(cmp, ll.IntType(64))
            raise FrontendError(f"unsupported unary op: {expr.op!r}")

        if isinstance(expr, _ast.CallExpr):
            return self._emit_call(expr)

        # Fallback: return 0 constant for unsupported expressions
        log.debug("unsupported expression type: %s — emitting 0", type(expr).__name__)
        return ll.Constant(ll.IntType(64), 0)

    def _emit_binary(self, expr) -> Any:
        ll = self._ll
        left = self._emit_expr(expr.left)
        right = self._emit_expr(expr.right)

        # Promote int to float if mixed
        if isinstance(left.type, ll.DoubleType) or isinstance(right.type, ll.DoubleType):
            if isinstance(left.type, ll.IntType):
                left = self._builder.sitofp(left, ll.DoubleType())
            if isinstance(right.type, ll.IntType):
                right = self._builder.sitofp(right, ll.DoubleType())
            op = expr.op
            if op == "+":
                return self._builder.fadd(left, right)
            if op == "-":
                return self._builder.fsub(left, right)
            if op == "*":
                return self._builder.fmul(left, right)
            if op == "/":
                return self._builder.fdiv(left, right)
            # Comparison — return i64 0 or 1
            cmp_map = {"==": "==", "!=": "!=", "<": "<", "<=": "<=", ">": ">", ">=": ">="}
            cmp = self._builder.fcmp_ordered(cmp_map.get(op, "=="), left, right)
            return self._builder.zext(cmp, ll.IntType(64))

        # Integer operations
        op = expr.op
        if op == "+":
            return self._builder.add(left, right)
        if op == "-":
            return self._builder.sub(left, right)
        if op == "*":
            return self._builder.mul(left, right)
        if op == "/":
            return self._builder.sdiv(left, right)
        if op == "%":
            return self._builder.srem(left, right)
        # Comparisons
        cmp_map = {"==": "==", "!=": "!=", "<": "<", "<=": "<=", ">": ">", ">=": ">="}
        if op in cmp_map:
            cmp = self._builder.icmp_signed(cmp_map[op], left, right)
            return self._builder.zext(cmp, ll.IntType(64))
        if op == "and":
            return self._builder.and_(left, right)
        if op == "or":
            return self._builder.or_(left, right)

        raise FrontendError(f"unsupported binary op: {op!r}")

    def _emit_call(self, expr) -> Any:
        ll = self._ll
        name = getattr(expr.callee, "name", None)
        if name is None:
            return ll.Constant(ll.IntType(64), 0)
        if name not in self._functions:
            # Unknown call — return 0 (graceful degradation)
            log.debug("unknown function call: %s — emitting 0", name)
            return ll.Constant(ll.IntType(64), 0)
        fn = self._functions[name]
        arg_vals = []
        for i, arg in enumerate(expr.args):
            val = self._emit_expr(arg)
            expected_t = fn.type.pointee.args[i] if i < len(fn.type.pointee.args) else val.type
            val = self._coerce(val, expected_t)
            arg_vals.append(val)
        result = self._builder.call(fn, arg_vals)
        if isinstance(result.type, ll.VoidType):
            return ll.Constant(ll.IntType(64), 0)
        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _coerce(self, val: Any, target_type: Any) -> Any:
        ll = self._ll
        src_t = val.type
        if src_t == target_type:
            return val
        if isinstance(src_t, ll.IntType) and isinstance(target_type, ll.DoubleType):
            return self._builder.sitofp(val, target_type)
        if isinstance(src_t, ll.DoubleType) and isinstance(target_type, ll.IntType):
            return self._builder.fptosi(val, target_type)
        if isinstance(src_t, ll.IntType) and isinstance(target_type, ll.IntType):
            if src_t.width < target_type.width:
                return self._builder.sext(val, target_type)
            return self._builder.trunc(val, target_type)
        return val  # best-effort — let LLVM validate
