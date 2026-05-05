
from __future__ import annotations

from dataclasses import dataclass

from . import ast
from .diagnostics import DiagnosticBundle, ThirstyError, nearest_word
from .token import KEYWORDS, Span, Token, TokenType


@dataclass
class Parser:
    tokens: list[Token]

    def __post_init__(self) -> None:
        self.i = 0
        self.errors: list[ThirstyError] = []

    @classmethod
    def from_tokens(cls, tokens: list[Token]) -> "Parser":
        return cls(tokens)

    def parse_program(self) -> ast.Program:
        decls: list[ast.Stmt] = []
        while not self._check(TokenType.EOF):
            try:
                decls.append(self._declaration(in_class=False))
            except ThirstyError as err:
                self.errors.append(err)
                self._synchronize()
        start = self.tokens[0].span if self.tokens else Span("<memory>", 1, 1, 1, 1)
        end = self.tokens[-1].span if self.tokens else start
        program = ast.Program(start.merge(end), decls)
        if self.errors:
            raise DiagnosticBundle(self.errors)
        return program

    def parse_block_statements(self) -> list[ast.Stmt]:
        items = []
        while not self._check(TokenType.RBRACE) and not self._check(TokenType.EOF):
            try:
                items.append(self._declaration(in_class=False))
            except ThirstyError as err:
                self.errors.append(err)
                self._synchronize()
        return items

    def _declaration(self, in_class: bool) -> ast.Stmt:
        vis = None
        if self._match(TokenType.PUBLIC):
            vis = "public"
        elif self._match(TokenType.PRIVATE):
            vis = "private"
        if self._match(TokenType.IMPORT):
            return self._import_decl()
        if self._match(TokenType.FOUNTAIN):
            return self._class_decl()
        if self._match(TokenType.CASCADE):
            self._consume(TokenType.GLASS, "expected 'glass' after 'cascade'")
            return self._function_decl(is_async=True, visibility=vis, is_method=in_class)
        if self._match(TokenType.GLASS):
            return self._function_decl(is_async=False, visibility=vis, is_method=in_class)
        if self._match(TokenType.DRINK):
            return self._var_decl(visibility=vis, is_field=in_class)
        return self._statement()

    def _import_decl(self) -> ast.ImportDecl:
        mod = self._consume(TokenType.STRING, "expected string module path after import")
        alias = None
        if self._match(TokenType.AS):
            alias = self._consume(TokenType.IDENT, "expected alias after 'as'").lexeme
        semi = self._consume(TokenType.SEMICOLON, "expected ';' after import")
        return ast.ImportDecl(mod.span.merge(semi.span), mod.value, alias)

    def _class_decl(self) -> ast.ClassDecl:
        name = self._consume(TokenType.IDENT, "expected class name")
        self._consume(TokenType.LBRACE, "expected '{' after class name")
        members: list[ast.Stmt] = []
        while not self._check(TokenType.RBRACE) and not self._check(TokenType.EOF):
            members.append(self._declaration(in_class=True))
        end = self._consume(TokenType.RBRACE, "expected '}' after class body")
        return ast.ClassDecl(name.span.merge(end.span), name.lexeme, members)

    def _function_decl(self, is_async: bool, visibility: str | None, is_method: bool) -> ast.FunctionDecl:
        name = self._consume(TokenType.IDENT, "expected function name")
        self._consume(TokenType.LPAREN, "expected '(' after function name")
        params: list[ast.Param] = []
        if not self._check(TokenType.RPAREN):
            while True:
                pname = self._consume(TokenType.IDENT, "expected parameter name")
                self._consume(TokenType.COLON, "expected ':' after parameter name")
                ptype = self._type_node()
                params.append(ast.Param(pname.span.merge(ptype.span), pname.lexeme, ptype))
                if not self._match(TokenType.COMMA):
                    break
        self._consume(TokenType.RPAREN, "expected ')' after parameters")
        return_type = None
        if self._match(TokenType.ARROW):
            return_type = self._type_node()
        body = self._block()
        span = name.span.merge(body.span)
        return ast.FunctionDecl(span, name.lexeme, params, return_type, body, is_async=is_async, visibility=visibility, is_method=is_method)

    def _var_decl(self, visibility: str | None, is_field: bool) -> ast.VarDecl:
        mutable = self._match(TokenType.MUT)
        name = self._consume(TokenType.IDENT, "expected variable name")
        self._consume(TokenType.COLON, "expected ':' after variable name")
        tnode = self._type_node()
        if is_field and self._match(TokenType.SEMICOLON):
            init = ast.LiteralExpr(name.span, None)
            return ast.VarDecl(name.span.merge(tnode.span), name.lexeme, tnode, init, mutable, visibility, is_field=True)
        self._consume(TokenType.ASSIGN, "expected '=' after type annotation")
        init = self._expression()
        semi = self._consume(TokenType.SEMICOLON, "expected ';' after declaration")
        return ast.VarDecl(name.span.merge(semi.span), name.lexeme, tnode, init, mutable, visibility, is_field=is_field)

    def _statement(self) -> ast.Stmt:
        if self._match(TokenType.POUR):
            start = self._previous().span
            safe = self._match(TokenType.QUESTION)
            self._consume(TokenType.LPAREN, "expected '(' after pour")
            expr = self._expression()
            self._consume(TokenType.RPAREN, "expected ')' after print expression")
            semi = self._consume(TokenType.SEMICOLON, "expected ';' after pour")
            return ast.PrintStmt(start.merge(semi.span), expr, safe=safe)
        if self._match(TokenType.THIRSTY):
            start = self._previous().span
            self._consume(TokenType.LPAREN, "expected '(' after thirsty")
            cond = self._expression()
            self._consume(TokenType.RPAREN, "expected ')' after condition")
            then_branch = self._block()
            else_branch = None
            end_span = then_branch.span
            if self._match(TokenType.HYDRATED):
                else_branch = self._block()
                end_span = else_branch.span
            return ast.IfStmt(start.merge(end_span), cond, then_branch, else_branch)
        if self._match(TokenType.REFILL):
            start = self._previous().span
            count = self._expression()
            self._consume(TokenType.TIMES, "expected 'times' after loop count")
            body = self._block()
            return ast.LoopStmt(start.merge(body.span), count, body)
        if self._match(TokenType.DRIP):
            start = self._previous().span
            name = self._consume(TokenType.IDENT, "expected variable name after drip")
            amount = None
            if self._match(TokenType.PLUS_EQ):
                amount = self._expression()
            semi = self._consume(TokenType.SEMICOLON, "expected ';' after drip")
            return ast.DripStmt(start.merge(semi.span), name.lexeme, amount)
        if self._match(TokenType.RETURN):
            start = self._previous().span
            expr = None if self._check(TokenType.SEMICOLON) else self._expression()
            semi = self._consume(TokenType.SEMICOLON, "expected ';' after return")
            return ast.ReturnStmt(start.merge(semi.span), expr)
        if self._match(TokenType.SPILLAGE):
            start = self._previous().span
            try_block = self._block()
            catches = []
            finally_block = None
            while self._match(TokenType.CLEANUP):
                if self._match(TokenType.FINALLY):
                    finally_block = self._block()
                    break
                self._consume(TokenType.ERROR, "expected 'error' after cleanup")
                self._consume(TokenType.LPAREN, "expected '(' after cleanup error")
                name = self._consume(TokenType.IDENT, "expected catch binding name")
                self._consume(TokenType.COLON, "expected ':' in catch clause")
                typ = self._consume_any((TokenType.IDENT, TokenType.ERROR), "expected catch type")
                self._consume(TokenType.RPAREN, "expected ')' after catch clause")
                block = self._block()
                catches.append(ast.CatchClause(name.span.merge(block.span), name.lexeme, typ.lexeme, block))
            if not catches and finally_block is None:
                raise ThirstyError("THIRSTY-E001", "spillage requires cleanup error or cleanup finally", start)
            end_span = finally_block.span if finally_block else catches[-1].span
            return ast.TryStmt(start.merge(end_span), try_block, catches, finally_block)
        if self._match(TokenType.THROW):
            start = self._previous().span
            expr = self._expression()
            semi = self._consume(TokenType.SEMICOLON, "expected ';' after throw")
            return ast.ThrowStmt(start.merge(semi.span), expr)
        if self._match(TokenType.LBRACE):
            self.i -= 1
            return self._block()
        expr = self._expression()
        semi = self._consume(TokenType.SEMICOLON, "expected ';' after expression")
        return ast.ExprStmt(expr.span.merge(semi.span), expr)

    def _block(self) -> ast.BlockStmt:
        start = self._consume(TokenType.LBRACE, "expected '{' to start block")
        items = self.parse_block_statements()
        end = self._consume(TokenType.RBRACE, "expected '}' after block")
        return ast.BlockStmt(start.span.merge(end.span), items)

    def _type_node(self) -> ast.TypeNode:
        if self._match(TokenType.RESERVOIR):
            base_tok = self._previous()
            self._consume(TokenType.LBRACKET, "expected '[' after reservoir")
            arg = self._type_node()
            end = self._consume(TokenType.RBRACKET, "expected ']' after reservoir type")
            return ast.GenericType(base_tok.span.merge(end.span), "Reservoir", [arg])
        if self._match(TokenType.WELL):
            base_tok = self._previous()
            self._consume(TokenType.LBRACKET, "expected '[' after well")
            if self._match(TokenType.OF):
                self._consume(TokenType.COLON, "expected ':' after 'of'")
            arg = self._type_node()
            end = self._consume(TokenType.RBRACKET, "expected ']' after well type")
            return ast.GenericType(base_tok.span.merge(end.span), "Reservoir", [arg])
        name = self._consume_any((TokenType.IDENT, TokenType.QUENCHED, TokenType.ERROR), "expected type name")
        if self._match(TokenType.LBRACKET):
            args = [self._type_node()]
            while self._match(TokenType.COMMA):
                args.append(self._type_node())
            end = self._consume(TokenType.RBRACKET, "expected ']' after generic args")
            return ast.GenericType(name.span.merge(end.span), name.lexeme, args)
        return ast.NamedType(name.span, name.lexeme)

    def _expression(self) -> ast.Expr:
        return self._guard()

    def _guard(self) -> ast.Expr:
        if self._match(TokenType.THIRST):
            start = self._previous().span
            cond = self._expression()
            self._consume(TokenType.QUENCH, "expected 'quench' after thirst guard condition")
            when_true = self._expression()
            when_false = None
            if self._match(TokenType.HYDRATED):
                when_false = self._expression()
            span = start.merge((when_false or when_true).span)
            return ast.GuardExpr(span, cond, when_true, when_false)
        return self._assignment()

    def _assignment(self) -> ast.Expr:
        expr = self._pipe()
        if self._match(TokenType.ASSIGN):
            eq = self._previous()
            value = self._assignment()
            if isinstance(expr, (ast.VariableExpr, ast.MemberExpr, ast.IndexExpr)):
                return ast.AssignExpr(expr.span.merge(value.span), expr, value)
            raise ThirstyError("THIRSTY-E001", "invalid assignment target", eq.span)
        return expr

    def _pipe(self) -> ast.Expr:
        expr = self._or()
        while self._match(TokenType.PIPE):
            op = self._previous()
            right = self._or()
            expr = ast.PipeExpr(expr.span.merge(right.span), expr, right)
        return expr

    def _or(self) -> ast.Expr:
        expr = self._and()
        while self._match(TokenType.OR):
            op = self._previous()
            right = self._and()
            expr = ast.BinaryExpr(expr.span.merge(right.span), expr, op.lexeme, right)
        return expr

    def _and(self) -> ast.Expr:
        expr = self._equality()
        while self._match(TokenType.AND):
            op = self._previous()
            right = self._equality()
            expr = ast.BinaryExpr(expr.span.merge(right.span), expr, op.lexeme, right)
        return expr

    def _equality(self) -> ast.Expr:
        expr = self._comparison()
        while self._match(TokenType.EQ, TokenType.NE):
            op = self._previous()
            right = self._comparison()
            expr = ast.BinaryExpr(expr.span.merge(right.span), expr, op.lexeme, right)
        return expr

    def _comparison(self) -> ast.Expr:
        expr = self._term()
        while self._match(TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE):
            op = self._previous()
            right = self._term()
            expr = ast.BinaryExpr(expr.span.merge(right.span), expr, op.lexeme, right)
        return expr

    def _term(self) -> ast.Expr:
        expr = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous()
            right = self._factor()
            expr = ast.BinaryExpr(expr.span.merge(right.span), expr, op.lexeme, right)
        return expr

    def _factor(self) -> ast.Expr:
        expr = self._unary()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self._previous()
            right = self._unary()
            expr = ast.BinaryExpr(expr.span.merge(right.span), expr, op.lexeme, right)
        return expr

    def _unary(self) -> ast.Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            op = self._previous()
            right = self._unary()
            return ast.UnaryExpr(op.span.merge(right.span), op.lexeme, right)
        if self._match(TokenType.AWAIT):
            op = self._previous()
            expr = self._unary()
            return ast.AwaitExpr(op.span.merge(expr.span), expr)
        if self._match(TokenType.CONDENSE):
            op = self._previous()
            expr = self._unary()
            return ast.CondenseExpr(op.span.merge(expr.span), expr)
        if self._match(TokenType.EVAPORATE):
            op = self._previous()
            expr = self._unary()
            return ast.EvaporateExpr(op.span.merge(expr.span), expr)
        return self._call()

    def _call(self) -> ast.Expr:
        expr = self._primary()
        while True:
            if self._match(TokenType.QUESTION):
                safe = True
                self._consume(TokenType.LPAREN, "expected '(' after safe call")
                args = self._arguments()
                end = self._consume(TokenType.RPAREN, "expected ')' after arguments")
                expr = ast.CallExpr(expr.span.merge(end.span), expr, args, safe=safe)
            elif self._match(TokenType.LPAREN):
                args = self._arguments()
                end = self._consume(TokenType.RPAREN, "expected ')' after arguments")
                expr = ast.CallExpr(expr.span.merge(end.span), expr, args)
            elif self._match(TokenType.DOT):
                name = self._consume(TokenType.IDENT, "expected member name after '.'")
                expr = ast.MemberExpr(expr.span.merge(name.span), expr, name.lexeme)
            elif self._match(TokenType.LBRACKET):
                index = self._expression()
                end = self._consume(TokenType.RBRACKET, "expected ']' after index")
                expr = ast.IndexExpr(expr.span.merge(end.span), expr, index)
            else:
                break
        return expr

    def _arguments(self) -> list[ast.Expr]:
        args = []
        if not self._check(TokenType.RPAREN):
            args.append(self._expression())
            while self._match(TokenType.COMMA):
                args.append(self._expression())
        return args

    def _primary(self) -> ast.Expr:
        if self._match(TokenType.INT):
            return ast.LiteralExpr(self._previous().span, self._previous().value)
        if self._match(TokenType.FLOAT):
            return ast.LiteralExpr(self._previous().span, self._previous().value)
        if self._match(TokenType.STRING):
            return ast.LiteralExpr(self._previous().span, self._previous().value)
        if self._match(TokenType.PARCHED):
            return ast.LiteralExpr(self._previous().span, True)
        if self._match(TokenType.QUENCHED):
            return ast.LiteralExpr(self._previous().span, False)
        if self._match(TokenType.EMPTY):
            return ast.LiteralExpr(self._previous().span, None)
        if self._match(TokenType.THIS):
            return ast.ThisExpr(self._previous().span)
        if self._match(TokenType.SIP):
            start = self._previous().span
            safe = self._match(TokenType.QUESTION)
            self._consume(TokenType.LPAREN, "expected '(' after sip")
            end = self._consume(TokenType.RPAREN, "expected ')' after sip")
            return ast.InputExpr(start.merge(end.span), safe=safe)
        if self._match(TokenType.NEW):
            start = self._previous().span
            name = self._consume(TokenType.IDENT, "expected class name after new")
            self._consume(TokenType.LPAREN, "expected '(' after class name")
            args = self._arguments()
            end = self._consume(TokenType.RPAREN, "expected ')' after constructor args")
            return ast.NewExpr(start.merge(end.span), name.lexeme, args)
        if self._match(TokenType.LBRACKET):
            start = self._previous().span
            items = []
            if not self._check(TokenType.RBRACKET):
                items.append(self._expression())
                while self._match(TokenType.COMMA):
                    items.append(self._expression())
            end = self._consume(TokenType.RBRACKET, "expected ']' after array literal")
            return ast.ArrayExpr(start.merge(end.span), items)
        if self._match(TokenType.IDENT):
            prev = self._previous()
            return ast.VariableExpr(prev.span, prev.lexeme)
        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "expected ')' after expression")
            return expr
        tok = self._peek()
        raise ThirstyError("THIRSTY-E001", f"unexpected token '{tok.lexeme or tok.kind.name}'", tok.span)

    def _consume(self, kind: TokenType, message: str) -> Token:
        if self._check(kind):
            return self._advance()
        tok = self._peek()
        if tok.kind == TokenType.IDENT:
            suggestion = nearest_word(tok.lexeme, [k for k in KEYWORDS if k.islower()])
            if suggestion:
                message += f" (did you mean '{suggestion}'?)"
        raise ThirstyError("THIRSTY-E001", message, tok.span)

    def _consume_any(self, kinds: tuple[TokenType, ...], message: str) -> Token:
        for kind in kinds:
            if self._check(kind):
                return self._advance()
        tok = self._peek()
        raise ThirstyError("THIRSTY-E001", message, tok.span)

    def _synchronize(self) -> None:
        while not self._check(TokenType.EOF):
            if self._previous().kind == TokenType.SEMICOLON:
                return
            if self._peek().kind in {
                TokenType.DRINK,
                TokenType.GLASS,
                TokenType.FOUNTAIN,
                TokenType.RETURN,
                TokenType.THIRSTY,
                TokenType.REFILL,
                TokenType.SPILLAGE,
                TokenType.DRIP,
                TokenType.IMPORT,
            }:
                return
            self._advance()

    def _match(self, *kinds: TokenType) -> bool:
        for kind in kinds:
            if self._check(kind):
                self._advance()
                return True
        return False

    def _check(self, kind: TokenType) -> bool:
        return self._peek().kind == kind

    def _advance(self) -> Token:
        tok = self.tokens[self.i]
        self.i += 1
        return tok

    def _peek(self) -> Token:
        return self.tokens[self.i]

    def _previous(self) -> Token:
        return self.tokens[self.i - 1]
