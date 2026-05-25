"""Shadow Thirst recursive-descent parser — produces an AST Program."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shadow_thirst.lexer import Token, TokenType


# ── AST nodes ────────────────────────────────────────────────────────────────


@dataclass
class IntLiteral:
    value: int


@dataclass
class FloatLiteral:
    value: float


@dataclass
class BoolLiteral:
    value: bool


@dataclass
class Var:
    name: str


@dataclass
class BinOp:
    op: str
    left: Any
    right: Any


@dataclass
class UnaryOp:
    op: str
    operand: Any


@dataclass
class CallExpr:
    func: str
    args: list[Any] = field(default_factory=list)


@dataclass
class TypeAnnotation:
    name: str
    type_args: list[str] = field(default_factory=list)

    def is_canonical(self) -> bool:
        return self.name.lower() == "canonical"


@dataclass
class DrinkStmt:
    name: str
    type_annotation: TypeAnnotation | None
    value: Any


@dataclass
class ReturnStmt:
    value: Any


@dataclass
class AssignStmt:
    name: str
    value: Any


@dataclass
class ExprStmt:
    expr: Any


@dataclass
class Block:
    statements: list[Any] = field(default_factory=list)


@dataclass
class Parameter:
    name: str
    type_name: str


@dataclass
class FunctionDef:
    name: str
    parameters: list[Parameter]
    return_type: str
    primary_block: Block | None
    shadow_block: Block | None
    activation_predicate: Any | None
    invariants: Block | None
    divergence_policy: str | None
    mutation_boundary: str | None


@dataclass
class Program:
    functions: list[FunctionDef] = field(default_factory=list)


# ── Parser ───────────────────────────────────────────────────────────────────


class ParseError(Exception):
    pass


_BLOCK_STARTERS = {
    TokenType.FN, TokenType.PRIMARY, TokenType.SHADOW,
    TokenType.ACTIVATE_IF, TokenType.INVARIANT,
    TokenType.DIVERGENCE, TokenType.MUTATION,
    TokenType.RBRACE, TokenType.EOF,
}

_BINOP_PRECEDENCE = [
    ({TokenType.OR}, "||"),
    ({TokenType.AND}, "&&"),
    ({TokenType.EQ, TokenType.NE, TokenType.LT, TokenType.LE,
      TokenType.GT, TokenType.GE}, None),
    ({TokenType.PLUS, TokenType.MINUS}, None),
    ({TokenType.STAR, TokenType.SLASH}, None),
]

_OP_SYMBOL: dict[TokenType, str] = {
    TokenType.OR: "||", TokenType.AND: "&&",
    TokenType.EQ: "==", TokenType.NE: "!=",
    TokenType.LT: "<", TokenType.LE: "<=",
    TokenType.GT: ">", TokenType.GE: ">=",
    TokenType.PLUS: "+", TokenType.MINUS: "-",
    TokenType.STAR: "*", TokenType.SLASH: "/",
}


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        if idx >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[idx]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def expect(self, tt: TokenType) -> Token:
        tok = self.current()
        if tok.type != tt:
            raise ParseError(
                f"Expected {tt.name} but got {tok.type.name} ({tok.value!r}) at line {tok.line}"
            )
        return self.advance()

    # ── Expressions ──────────────────────────────────────────────────────────

    def parse_expr(self) -> Any:
        return self._parse_binop(0)

    def _parse_binop(self, level: int) -> Any:
        if level >= len(_BINOP_PRECEDENCE):
            return self._parse_unary()
        ops_set, _ = _BINOP_PRECEDENCE[level]
        left = self._parse_binop(level + 1)
        while self.current().type in ops_set:
            op_tok = self.advance()
            op = _OP_SYMBOL[op_tok.type]
            right = self._parse_binop(level + 1)
            left = BinOp(op, left, right)
        return left

    def _parse_unary(self) -> Any:
        if self.current().type == TokenType.MINUS:
            self.advance()
            return UnaryOp("-", self._parse_primary())
        if self.current().type == TokenType.NOT:
            self.advance()
            return UnaryOp("!", self._parse_primary())
        return self._parse_primary()

    def _parse_primary(self) -> Any:
        tok = self.current()

        if tok.type == TokenType.INTEGER:
            self.advance()
            return IntLiteral(tok.value)

        if tok.type == TokenType.FLOAT:
            self.advance()
            return FloatLiteral(tok.value)

        if tok.type == TokenType.TRUE:
            self.advance()
            return BoolLiteral(True)

        if tok.type == TokenType.FALSE:
            self.advance()
            return BoolLiteral(False)

        if tok.type == TokenType.STRING:
            self.advance()
            return tok.value

        if tok.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expr()
            self.expect(TokenType.RPAREN)
            return expr

        if tok.type == TokenType.IDENTIFIER:
            self.advance()
            name = str(tok.value)
            if self.current().type == TokenType.LPAREN:
                self.advance()
                args = []
                while self.current().type != TokenType.RPAREN:
                    args.append(self.parse_expr())
                    if self.current().type == TokenType.COMMA:
                        self.advance()
                self.expect(TokenType.RPAREN)
                return CallExpr(name, args)
            return Var(name)

        raise ParseError(f"Unexpected token in expression: {tok.type.name}({tok.value!r}) at line {tok.line}")

    # ── Type annotation ───────────────────────────────────────────────────────

    def parse_type_annotation(self) -> TypeAnnotation:
        tok = self.current()
        name = str(tok.value)
        self.advance()
        type_args: list[str] = []
        if self.current().type == TokenType.LT:
            self.advance()
            while self.current().type not in (TokenType.GT, TokenType.EOF):
                type_args.append(str(self.current().value))
                self.advance()
                if self.current().type == TokenType.COMMA:
                    self.advance()
            if self.current().type == TokenType.GT:
                self.advance()
        return TypeAnnotation(name=name, type_args=type_args)

    # ── Statements ────────────────────────────────────────────────────────────

    def parse_drink(self) -> DrinkStmt:
        self.expect(TokenType.DRINK)
        name_tok = self.expect(TokenType.IDENTIFIER)
        name = str(name_tok.value)
        type_annotation = None
        if self.current().type == TokenType.COLON:
            self.advance()
            type_annotation = self.parse_type_annotation()
        self.expect(TokenType.ASSIGN)
        value = self.parse_expr()
        if self.current().type == TokenType.SEMICOLON:
            self.advance()
        return DrinkStmt(name=name, type_annotation=type_annotation, value=value)

    def parse_statement(self) -> Any:
        tok = self.current()

        if tok.type == TokenType.DRINK:
            return self.parse_drink()

        if tok.type == TokenType.RETURN:
            self.advance()
            if self.current().type in (TokenType.RBRACE, TokenType.EOF):
                return ReturnStmt(None)
            value = self.parse_expr()
            if self.current().type == TokenType.SEMICOLON:
                self.advance()
            return ReturnStmt(value)

        if tok.type == TokenType.IDENTIFIER and self.peek().type == TokenType.ASSIGN:
            name = str(tok.value)
            self.advance()  # consume identifier
            self.advance()  # consume =
            value = self.parse_expr()
            if self.current().type == TokenType.SEMICOLON:
                self.advance()
            return AssignStmt(name=name, value=value)

        expr = self.parse_expr()
        if self.current().type == TokenType.SEMICOLON:
            self.advance()
        return ExprStmt(expr)

    # ── Blocks ────────────────────────────────────────────────────────────────

    def parse_block(self) -> Block:
        self.expect(TokenType.LBRACE)
        stmts = []
        while self.current().type not in (TokenType.RBRACE, TokenType.EOF):
            stmts.append(self.parse_statement())
        self.expect(TokenType.RBRACE)
        return Block(statements=stmts)

    def parse_policy_string(self) -> str:
        parts = []
        while self.current().type not in _BLOCK_STARTERS:
            parts.append(str(self.current().value))
            self.advance()
        return " ".join(parts)

    # ── Function ──────────────────────────────────────────────────────────────

    def parse_parameters(self) -> list[Parameter]:
        self.expect(TokenType.LPAREN)
        params: list[Parameter] = []
        while self.current().type != TokenType.RPAREN:
            name_tok = self.expect(TokenType.IDENTIFIER)
            self.expect(TokenType.COLON)
            type_tok = self.current()
            self.advance()
            # absorb generics if present
            if self.current().type == TokenType.LT:
                self.advance()
                while self.current().type not in (TokenType.GT, TokenType.EOF):
                    self.advance()
                if self.current().type == TokenType.GT:
                    self.advance()
            params.append(Parameter(name=str(name_tok.value), type_name=str(type_tok.value)))
            if self.current().type == TokenType.COMMA:
                self.advance()
        self.expect(TokenType.RPAREN)
        return params

    def parse_function(self) -> FunctionDef:
        self.expect(TokenType.FN)
        name_tok = self.expect(TokenType.IDENTIFIER)
        name = str(name_tok.value)
        params = self.parse_parameters()
        return_type = "Any"
        if self.current().type == TokenType.ARROW:
            self.advance()
            return_type = str(self.current().value)
            self.advance()

        self.expect(TokenType.LBRACE)

        primary_block = shadow_block = invariants = None
        activation_predicate = divergence_policy = mutation_boundary = None

        while self.current().type not in (TokenType.RBRACE, TokenType.EOF):
            tok = self.current()
            if tok.type == TokenType.PRIMARY:
                self.advance()
                primary_block = self.parse_block()
            elif tok.type == TokenType.SHADOW:
                self.advance()
                shadow_block = self.parse_block()
            elif tok.type == TokenType.ACTIVATE_IF:
                self.advance()
                activation_predicate = self.parse_expr()
            elif tok.type == TokenType.INVARIANT:
                self.advance()
                invariants = self.parse_block()
            elif tok.type == TokenType.DIVERGENCE:
                self.advance()
                divergence_policy = self.parse_policy_string()
            elif tok.type == TokenType.MUTATION:
                self.advance()
                mutation_boundary = self.parse_policy_string()
            else:
                self.advance()  # skip unexpected token inside function body

        self.expect(TokenType.RBRACE)

        return FunctionDef(
            name=name,
            parameters=params,
            return_type=return_type,
            primary_block=primary_block,
            shadow_block=shadow_block,
            activation_predicate=activation_predicate,
            invariants=invariants,
            divergence_policy=divergence_policy,
            mutation_boundary=mutation_boundary,
        )

    # ── Program ───────────────────────────────────────────────────────────────

    def parse_program(self) -> Program:
        functions = []
        while self.current().type not in (TokenType.EOF,):
            if self.current().type == TokenType.FN:
                functions.append(self.parse_function())
            else:
                self.advance()
        return Program(functions=functions)


def parse(tokens: list[Token]) -> Program:
    return Parser(tokens).parse_program()
