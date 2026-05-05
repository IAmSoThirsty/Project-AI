
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .token import Span


@dataclass
class Node:
    span: Span


@dataclass
class TypeNode(Node):
    pass


@dataclass
class NamedType(TypeNode):
    name: str


@dataclass
class GenericType(TypeNode):
    base: str
    args: list[TypeNode]


@dataclass
class FunctionType(TypeNode):
    params: list[TypeNode]
    result: TypeNode


@dataclass
class Expr(Node):
    pass


@dataclass
class LiteralExpr(Expr):
    value: Any


@dataclass
class VariableExpr(Expr):
    name: str


@dataclass
class ThisExpr(Expr):
    pass


@dataclass
class InputExpr(Expr):
    safe: bool = False


@dataclass
class ArrayExpr(Expr):
    items: list[Expr]


@dataclass
class AssignExpr(Expr):
    target: Expr
    value: Expr


@dataclass
class UnaryExpr(Expr):
    op: str
    right: Expr


@dataclass
class BinaryExpr(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass
class PipeExpr(Expr):
    left: Expr
    right: Expr


@dataclass
class GuardExpr(Expr):
    condition: Expr
    when_true: Expr
    when_false: Expr | None


@dataclass
class CallExpr(Expr):
    callee: Expr
    args: list[Expr]
    safe: bool = False


@dataclass
class MemberExpr(Expr):
    obj: Expr
    name: str


@dataclass
class IndexExpr(Expr):
    obj: Expr
    index: Expr


@dataclass
class NewExpr(Expr):
    class_name: str
    args: list[Expr]


@dataclass
class AwaitExpr(Expr):
    expr: Expr


@dataclass
class CondenseExpr(Expr):
    expr: Expr


@dataclass
class EvaporateExpr(Expr):
    expr: Expr


@dataclass
class Stmt(Node):
    pass


@dataclass
class BlockStmt(Stmt):
    statements: list[Stmt]


@dataclass
class ExprStmt(Stmt):
    expr: Expr


@dataclass
class PrintStmt(Stmt):
    expr: Expr
    safe: bool = False


@dataclass
class ReturnStmt(Stmt):
    expr: Expr | None


@dataclass
class ThrowStmt(Stmt):
    expr: Expr


@dataclass
class DripStmt(Stmt):
    name: str
    amount: Expr | None = None


@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_branch: BlockStmt
    else_branch: BlockStmt | None


@dataclass
class LoopStmt(Stmt):
    count: Expr
    body: BlockStmt


@dataclass
class CatchClause(Node):
    name: str
    type_name: str
    block: BlockStmt


@dataclass
class TryStmt(Stmt):
    try_block: BlockStmt
    catches: list[CatchClause]
    finally_block: BlockStmt | None = None


@dataclass
class Param(Node):
    name: str
    type_node: TypeNode


@dataclass
class VarDecl(Stmt):
    name: str
    type_node: TypeNode
    initializer: Expr
    mutable: bool = False
    visibility: str | None = None
    is_field: bool = False


@dataclass
class FunctionDecl(Stmt):
    name: str
    params: list[Param]
    return_type: TypeNode | None
    body: BlockStmt
    is_async: bool = False
    visibility: str | None = None
    is_method: bool = False


@dataclass
class ClassDecl(Stmt):
    name: str
    members: list[Stmt]


@dataclass
class ImportDecl(Stmt):
    module: str
    alias: str | None = None


@dataclass
class Program(Node):
    declarations: list[Stmt] = field(default_factory=list)
