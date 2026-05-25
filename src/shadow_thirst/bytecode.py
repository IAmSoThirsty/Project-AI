"""Shadow Thirst bytecode generator — produces executable bytecode from IR."""
from __future__ import annotations

import json
import struct
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from shadow_thirst.ir_generator import IR, IRBasicBlock
from shadow_thirst.parser import (
    AssignStmt, BinOp, BoolLiteral, CallExpr, DrinkStmt,
    ExprStmt, FloatLiteral, IntLiteral, ReturnStmt, UnaryOp, Var,
)


class Op(Enum):
    LOAD_CONST = "LOAD_CONST"
    LOAD_VAR = "LOAD_VAR"
    STORE_VAR = "STORE_VAR"
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    EQ = "EQ"
    NE = "NE"
    LT = "LT"
    LE = "LE"
    GT = "GT"
    GE = "GE"
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    RETURN = "RETURN"
    POP = "POP"


@dataclass
class Instruction:
    op: Op
    arg: Any = None

    def __repr__(self) -> str:
        return f"{self.op.value}({self.arg!r})" if self.arg is not None else self.op.value


@dataclass
class BytecodeFunction:
    name: str
    primary_bytecode: list[Instruction] = field(default_factory=list)
    shadow_bytecode: list[Instruction] = field(default_factory=list)
    invariant_bytecode: list[Instruction] = field(default_factory=list)


@dataclass
class BytecodeModule:
    functions: list[BytecodeFunction] = field(default_factory=list)

    def encode(self) -> bytes:
        parts = [b"SHAD"]
        payload = json.dumps(
            [
                {
                    "name": f.name,
                    "primary": [[i.op.value, i.arg] for i in f.primary_bytecode],
                }
                for f in self.functions
            ]
        ).encode("utf-8")
        parts.append(struct.pack(">I", len(payload)))
        parts.append(payload)
        return b"".join(parts)


# ── Bytecode generation ───────────────────────────────────────────────────────

_BINOP_TO_OP: dict[str, Op] = {
    "+": Op.ADD, "-": Op.SUB, "*": Op.MUL, "/": Op.DIV,
    "==": Op.EQ, "!=": Op.NE, "<": Op.LT, "<=": Op.LE,
    ">": Op.GT, ">=": Op.GE, "&&": Op.AND, "||": Op.OR,
}


def _emit_expr(expr: Any, out: list[Instruction]) -> None:
    if isinstance(expr, IntLiteral):
        out.append(Instruction(Op.LOAD_CONST, expr.value))
    elif isinstance(expr, FloatLiteral):
        out.append(Instruction(Op.LOAD_CONST, expr.value))
    elif isinstance(expr, BoolLiteral):
        out.append(Instruction(Op.LOAD_CONST, expr.value))
    elif isinstance(expr, str):
        out.append(Instruction(Op.LOAD_CONST, expr))
    elif isinstance(expr, Var):
        out.append(Instruction(Op.LOAD_VAR, expr.name))
    elif isinstance(expr, BinOp):
        _emit_expr(expr.left, out)
        _emit_expr(expr.right, out)
        op = _BINOP_TO_OP.get(expr.op)
        if op:
            out.append(Instruction(op))
    elif isinstance(expr, UnaryOp):
        _emit_expr(expr.operand, out)
        if expr.op == "-":
            out.append(Instruction(Op.LOAD_CONST, -1))
            out.append(Instruction(Op.MUL))
        elif expr.op == "!":
            out.append(Instruction(Op.NOT))
    elif isinstance(expr, CallExpr):
        for arg in expr.args:
            _emit_expr(arg, out)
        out.append(Instruction(Op.LOAD_CONST, f"<call:{expr.func}>"))
    else:
        out.append(Instruction(Op.LOAD_CONST, None))


def _emit_block(bb: IRBasicBlock) -> list[Instruction]:
    instructions: list[Instruction] = []
    for stmt in bb.statements:
        if isinstance(stmt, DrinkStmt):
            _emit_expr(stmt.value, instructions)
            instructions.append(Instruction(Op.STORE_VAR, stmt.name))
        elif isinstance(stmt, ReturnStmt):
            if stmt.value is not None:
                _emit_expr(stmt.value, instructions)
            else:
                instructions.append(Instruction(Op.LOAD_CONST, None))
            instructions.append(Instruction(Op.RETURN))
        elif isinstance(stmt, AssignStmt):
            _emit_expr(stmt.value, instructions)
            instructions.append(Instruction(Op.STORE_VAR, stmt.name))
        elif isinstance(stmt, ExprStmt):
            _emit_expr(stmt.expr, instructions)
            instructions.append(Instruction(Op.POP))
        else:
            pass
    return instructions


def generate_bytecode(ir: IR) -> BytecodeModule:
    functions: list[BytecodeFunction] = []
    for func in ir.functions:
        primary_bc = []
        for bb in func.primary_blocks:
            primary_bc.extend(_emit_block(bb))

        shadow_bc = []
        for bb in func.shadow_blocks:
            shadow_bc.extend(_emit_block(bb))

        invariant_bc = []
        for bb in func.invariant_blocks:
            invariant_bc.extend(_emit_block(bb))

        functions.append(BytecodeFunction(
            name=func.name,
            primary_bytecode=primary_bc,
            shadow_bytecode=shadow_bc,
            invariant_bytecode=invariant_bc,
        ))
    return BytecodeModule(functions=functions)
