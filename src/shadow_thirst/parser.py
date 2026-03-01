"""
Shadow Thirst Parser

Parses Shadow Thirst tokens into Abstract Syntax Tree (AST).
Implements recursive descent parsing for Shadow Thirst grammar.

STATUS: PRODUCTION
VERSION: 1.0.0
"""

import logging

from shadow_thirst.ast_nodes import (
    ActivationPredicate,
    Assignment,
    BinaryOp,
    DivergencePolicy,
    DivergencePolicyType,
    Expression,
    ExpressionStatement,
    FunctionCall,
    FunctionDefinition,
    Identifier,
    InputStatement,
    InvariantClause,
    Literal,
    MemberAccess,
    MutationBoundary,
    MutationBoundaryType,
    OutputStatement,
    Parameter,
    PlaneQualifier,
    PrimaryBlock,
    Program,
    ReturnStatement,
    ShadowBlock,
    Statement,
    TypeAnnotation,
    UnaryOp,
    VariableDeclaration,
)
from shadow_thirst.lexer import Token, TokenType

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """Parse error with position information."""

    def __init__(self, message: str, token: Token | None = None):
        """
        Initialize parse error.

        Args:
            message: Error message
            token: Token where error occurred
        """
        self.message = message
        self.token = token

        if token:
            super().__init__(f"{message} at line {token.line}, column {token.column}")
        else:
            super().__init__(message)


class ShadowThirstParser:
    """
    Recursive descent parser for Shadow Thirst language.

    Parses token stream into AST according to Shadow Thirst grammar.
    """

    def __init__(self, tokens: list[Token]):
        """
        Initialize parser with tokens.

        Args:
            tokens: List of tokens from lexer
        """
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> Program:
        """
        Parse tokens into Program AST.

        Returns:
            Program AST node

        Raises:
            ParseError: If parsing fails
        """
        program = Program()

        while not self._is_at_end():
            # Try to parse function definition
            if self._check(TokenType.FN):
                function = self._parse_function_definition()
                program.functions.append(function)
            else:
                # Parse top-level statement
                stmt = self._parse_statement()
                if stmt:
                    program.statements.append(stmt)

        return program

    # ========================================================================
    # Function Definition Parsing
    # ========================================================================

    def _parse_function_definition(self) -> FunctionDefinition:
        """Parse function definition."""
        start_token = self._consume(TokenType.FN, "Expected 'fn'")

        # Function name
        name_token = self._consume(TokenType.IDENTIFIER, "Expected function name")
        name = name_token.value

        # Parameters
        self._consume(TokenType.LPAREN, "Expected '(' after function name")
        parameters = self._parse_parameter_list()
        self._consume(TokenType.RPAREN, "Expected ')' after parameters")

        # Return type (optional)
        return_type = None
        if self._match(TokenType.ARROW):
            return_type = self._parse_type_annotation()

        # Function body
        self._consume(TokenType.LBRACE, "Expected '{' to start function body")

        function = FunctionDefinition(
            name=name,
            parameters=parameters,
            return_type=return_type,
            line=start_token.line,
            column=start_token.column,
        )

        # Parse function body blocks
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            if self._check(TokenType.PRIMARY):
                function.primary_block = self._parse_primary_block()
            elif self._check(TokenType.SHADOW):
                function.shadow_block = self._parse_shadow_block()
            elif self._check(TokenType.ACTIVATE_IF):
                function.activation_predicate = self._parse_activation_predicate()
            elif self._check(TokenType.INVARIANT):
                function.invariants = self._parse_invariant_clause()
            elif self._check(TokenType.DIVERGENCE):
                function.divergence_policy = self._parse_divergence_policy()
            elif self._check(TokenType.MUTATION):
                function.mutation_boundary = self._parse_mutation_boundary()
            else:
                # Unknown construct in function body
                token = self._peek()
                raise ParseError(
                    f"Unexpected token in function body: {token.type.name}", token
                )

        self._consume(TokenType.RBRACE, "Expected '}' to end function body")

        return function

    def _parse_parameter_list(self) -> list[Parameter]:
        """Parse function parameter list."""
        parameters = []

        if self._check(TokenType.RPAREN):
            return parameters

        while True:
            param = self._parse_parameter()
            parameters.append(param)

            if not self._match(TokenType.COMMA):
                break

        return parameters

    def _parse_parameter(self) -> Parameter:
        """Parse a single parameter."""
        name_token = self._consume(TokenType.IDENTIFIER, "Expected parameter name")
        name = name_token.value

        type_annotation = None
        if self._match(TokenType.COLON):
            type_annotation = self._parse_type_annotation()

        return Parameter(
            name=name,
            type_annotation=type_annotation,
            line=name_token.line,
            column=name_token.column,
        )

    def _parse_type_annotation(self) -> TypeAnnotation:
        """Parse type annotation with optional plane qualifier."""
        # Check for plane qualifier
        qualifier = None
        if self._check(TokenType.CANONICAL):
            self._advance()
            qualifier = PlaneQualifier.CANONICAL
        elif self._check(TokenType.SHADOW):
            self._advance()
            qualifier = PlaneQualifier.SHADOW
        elif self._check(TokenType.EPHEMERAL):
            self._advance()
            qualifier = PlaneQualifier.EPHEMERAL
        elif self._check(TokenType.DUAL):
            self._advance()
            qualifier = PlaneQualifier.DUAL

        # Type name
        type_token = self._consume(TokenType.TYPE_IDENTIFIER, "Expected type name")
        type_name = type_token.value

        # Type parameters (optional)
        type_params = []
        if self._match(TokenType.LT):
            while True:
                param = self._parse_type_annotation()
                type_params.append(param)

                if not self._match(TokenType.COMMA):
                    break

            self._consume(TokenType.GT, "Expected '>' after type parameters")

        return TypeAnnotation(
            name=type_name,
            qualifier=qualifier,
            type_params=type_params,
            line=type_token.line,
            column=type_token.column,
        )

    # ========================================================================
    # Shadow Thirst Block Parsing
    # ========================================================================

    def _parse_primary_block(self) -> PrimaryBlock:
        """Parse primary execution block."""
        start_token = self._consume(TokenType.PRIMARY, "Expected 'primary'")
        self._consume(TokenType.LBRACE, "Expected '{' after 'primary'")

        statements = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

        self._consume(TokenType.RBRACE, "Expected '}' to end primary block")

        return PrimaryBlock(
            statements=statements,
            line=start_token.line,
            column=start_token.column,
        )

    def _parse_shadow_block(self) -> ShadowBlock:
        """Parse shadow execution block."""
        start_token = self._consume(TokenType.SHADOW, "Expected 'shadow'")
        self._consume(TokenType.LBRACE, "Expected '{' after 'shadow'")

        statements = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

        self._consume(TokenType.RBRACE, "Expected '}' to end shadow block")

        return ShadowBlock(
            statements=statements,
            line=start_token.line,
            column=start_token.column,
        )

    def _parse_activation_predicate(self) -> ActivationPredicate:
        """Parse activation predicate."""
        start_token = self._consume(TokenType.ACTIVATE_IF, "Expected 'activate_if'")
        condition = self._parse_expression()

        return ActivationPredicate(
            condition=condition,
            line=start_token.line,
            column=start_token.column,
        )

    def _parse_invariant_clause(self) -> InvariantClause:
        """Parse invariant clause."""
        start_token = self._consume(TokenType.INVARIANT, "Expected 'invariant'")
        self._consume(TokenType.LBRACE, "Expected '{' after 'invariant'")

        conditions = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            condition = self._parse_expression()
            conditions.append(condition)

            # Allow optional && between conditions
            self._match(TokenType.AND)

        self._consume(TokenType.RBRACE, "Expected '}' to end invariant clause")

        return InvariantClause(
            conditions=conditions,
            line=start_token.line,
            column=start_token.column,
        )

    def _parse_divergence_policy(self) -> DivergencePolicy:
        """Parse divergence policy."""
        start_token = self._consume(TokenType.DIVERGENCE, "Expected 'divergence'")

        # Parse policy type
        policy_type = None
        epsilon = None

        if self._match(TokenType.REQUIRE_IDENTICAL):
            policy_type = DivergencePolicyType.REQUIRE_IDENTICAL
        elif self._match(TokenType.ALLOW_EPSILON):
            policy_type = DivergencePolicyType.ALLOW_EPSILON
            # Parse epsilon value
            self._consume(TokenType.LPAREN, "Expected '(' after 'allow_epsilon'")
            epsilon_token = self._advance()
            if epsilon_token.type in (TokenType.FLOAT, TokenType.INTEGER):
                epsilon = float(epsilon_token.value)
            else:
                raise ParseError("Expected numeric epsilon value", epsilon_token)
            self._consume(TokenType.RPAREN, "Expected ')' after epsilon value")
        elif self._match(TokenType.LOG_DIVERGENCE):
            policy_type = DivergencePolicyType.LOG_DIVERGENCE
        elif self._match(TokenType.QUARANTINE_ON_DIVERGE):
            policy_type = DivergencePolicyType.QUARANTINE_ON_DIVERGE
        elif self._match(TokenType.FAIL_PRIMARY):
            policy_type = DivergencePolicyType.FAIL_PRIMARY
        else:
            token = self._peek()
            raise ParseError("Expected divergence policy type", token)

        return DivergencePolicy(
            policy_type=policy_type,
            epsilon=epsilon,
            line=start_token.line,
            column=start_token.column,
        )

    def _parse_mutation_boundary(self) -> MutationBoundary:
        """Parse mutation boundary."""
        start_token = self._consume(TokenType.MUTATION, "Expected 'mutation'")

        # Parse boundary type
        boundary_type = None

        if self._match(TokenType.READ_ONLY):
            boundary_type = MutationBoundaryType.READ_ONLY
        elif self._match(TokenType.EPHEMERAL_ONLY):
            boundary_type = MutationBoundaryType.EPHEMERAL_ONLY
        elif self._match(TokenType.SHADOW_STATE_ONLY):
            boundary_type = MutationBoundaryType.SHADOW_STATE_ONLY
        elif self._match(TokenType.VALIDATED_CANONICAL):
            boundary_type = MutationBoundaryType.VALIDATED_CANONICAL
        elif self._match(TokenType.EMERGENCY_OVERRIDE):
            boundary_type = MutationBoundaryType.EMERGENCY_OVERRIDE
        else:
            token = self._peek()
            raise ParseError("Expected mutation boundary type", token)

        return MutationBoundary(
            boundary_type=boundary_type,
            line=start_token.line,
            column=start_token.column,
        )

    # ========================================================================
    # Statement Parsing
    # ========================================================================

    def _parse_statement(self) -> Statement | None:
        """Parse a statement."""
        # Variable declaration (drink x = value)
        if self._check(TokenType.DRINK):
            return self._parse_variable_declaration()

        # Output statement (pour x)
        if self._check(TokenType.POUR):
            return self._parse_output_statement()

        # Input statement (sip x)
        if self._check(TokenType.SIP):
            return self._parse_input_statement()

        # Return statement
        if self._check(TokenType.RETURN):
            return self._parse_return_statement()

        # Expression statement or assignment
        return self._parse_expression_or_assignment()

    def _parse_variable_declaration(self) -> VariableDeclaration:
        """Parse variable declaration."""
        start_token = self._consume(TokenType.DRINK, "Expected 'drink'")
        name_token = self._consume(TokenType.IDENTIFIER, "Expected variable name")
        name = name_token.value

        type_annotation = None
        if self._match(TokenType.COLON):
            type_annotation = self._parse_type_annotation()

        initializer = None
        if self._match(TokenType.ASSIGN):
            initializer = self._parse_expression()

        return VariableDeclaration(
            name=name,
            type_annotation=type_annotation,
            initializer=initializer,
            line=start_token.line,
            column=start_token.column,
        )

    def _parse_output_statement(self) -> OutputStatement:
        """Parse output statement."""
        start_token = self._consume(TokenType.POUR, "Expected 'pour'")
        expression = self._parse_expression()

        return OutputStatement(
            expression=expression,
            line=start_token.line,
            column=start_token.column,
        )

    def _parse_input_statement(self) -> InputStatement:
        """Parse input statement."""
        start_token = self._consume(TokenType.SIP, "Expected 'sip'")
        var_token = self._consume(TokenType.IDENTIFIER, "Expected variable name")

        return InputStatement(
            variable=var_token.value,
            line=start_token.line,
            column=start_token.column,
        )

    def _parse_return_statement(self) -> ReturnStatement:
        """Parse return statement."""
        start_token = self._consume(TokenType.RETURN, "Expected 'return'")

        value = None
        if not self._check(TokenType.RBRACE) and not self._is_at_end():
            value = self._parse_expression()

        return ReturnStatement(
            value=value,
            line=start_token.line,
            column=start_token.column,
        )

    def _parse_expression_or_assignment(self) -> Statement | None:
        """Parse expression or assignment statement."""
        # Look ahead to determine if this is an assignment
        if self._check(TokenType.IDENTIFIER):
            checkpoint = self.pos
            self._advance()  # Consume identifier

            if self._check(TokenType.ASSIGN):
                # This is an assignment
                self.pos = checkpoint
                return self._parse_assignment()
            else:
                # This is an expression
                self.pos = checkpoint

        # Parse as expression statement
        expr = self._parse_expression()
        if expr:
            return ExpressionStatement(expression=expr)

        return None

    def _parse_assignment(self) -> Assignment:
        """Parse assignment statement."""
        target_token = self._consume(TokenType.IDENTIFIER, "Expected identifier")
        target = target_token.value

        self._consume(TokenType.ASSIGN, "Expected '='")

        value = self._parse_expression()

        return Assignment(
            target=target,
            value=value,
            line=target_token.line,
            column=target_token.column,
        )

    # ========================================================================
    # Expression Parsing
    # ========================================================================

    def _parse_expression(self) -> Expression:
        """Parse expression (lowest precedence)."""
        return self._parse_logical_or()

    def _parse_logical_or(self) -> Expression:
        """Parse logical OR expression."""
        left = self._parse_logical_and()

        while self._match(TokenType.OR):
            operator = "||"
            right = self._parse_logical_and()
            left = BinaryOp(operator=operator, left=left, right=right)

        return left

    def _parse_logical_and(self) -> Expression:
        """Parse logical AND expression."""
        left = self._parse_equality()

        while self._match(TokenType.AND):
            operator = "&&"
            right = self._parse_equality()
            left = BinaryOp(operator=operator, left=left, right=right)

        return left

    def _parse_equality(self) -> Expression:
        """Parse equality expression."""
        left = self._parse_comparison()

        while self._match(TokenType.EQ, TokenType.NE):
            operator = self._previous().value
            right = self._parse_comparison()
            left = BinaryOp(operator=operator, left=left, right=right)

        return left

    def _parse_comparison(self) -> Expression:
        """Parse comparison expression."""
        left = self._parse_addition()

        while self._match(TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE):
            operator = self._previous().value
            right = self._parse_addition()
            left = BinaryOp(operator=operator, left=left, right=right)

        return left

    def _parse_addition(self) -> Expression:
        """Parse addition/subtraction expression."""
        left = self._parse_multiplication()

        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._previous().value
            right = self._parse_multiplication()
            left = BinaryOp(operator=operator, left=left, right=right)

        return left

    def _parse_multiplication(self) -> Expression:
        """Parse multiplication/division expression."""
        left = self._parse_unary()

        while self._match(TokenType.MULTIPLY, TokenType.DIVIDE):
            operator = self._previous().value
            right = self._parse_unary()
            left = BinaryOp(operator=operator, left=left, right=right)

        return left

    def _parse_unary(self) -> Expression:
        """Parse unary expression."""
        if self._match(TokenType.NOT, TokenType.MINUS):
            operator = self._previous().value
            operand = self._parse_unary()
            return UnaryOp(operator=operator, operand=operand)

        return self._parse_postfix()

    def _parse_postfix(self) -> Expression:
        """Parse postfix expression (member access, function calls)."""
        expr = self._parse_primary()

        while True:
            if self._match(TokenType.DOT):
                # Member access
                member_token = self._consume(
                    TokenType.IDENTIFIER, "Expected member name"
                )
                expr = MemberAccess(object=expr, member=member_token.value)
            elif self._match(TokenType.LPAREN):
                # Function call
                if isinstance(expr, Identifier):
                    arguments = self._parse_argument_list()
                    self._consume(TokenType.RPAREN, "Expected ')' after arguments")
                    expr = FunctionCall(function=expr.name, arguments=arguments)
                else:
                    raise ParseError("Invalid function call")
            else:
                break

        return expr

    def _parse_argument_list(self) -> list[Expression]:
        """Parse function argument list."""
        arguments = []

        if self._check(TokenType.RPAREN):
            return arguments

        while True:
            arg = self._parse_expression()
            arguments.append(arg)

            if not self._match(TokenType.COMMA):
                break

        return arguments

    def _parse_primary(self) -> Expression:
        """Parse primary expression (literals, identifiers, parenthesized)."""
        # Literals
        if self._match(TokenType.INTEGER, TokenType.FLOAT):
            return Literal(value=self._previous().value)

        if self._match(TokenType.STRING):
            return Literal(value=self._previous().value)

        if self._match(TokenType.BOOLEAN):
            return Literal(value=self._previous().value)

        # Identifiers
        if self._match(TokenType.IDENTIFIER):
            return Identifier(name=self._previous().value)

        # Parenthesized expression
        if self._match(TokenType.LPAREN):
            expr = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr

        # Error
        token = self._peek()
        raise ParseError(f"Unexpected token: {token.type.name}", token)

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _match(self, *types: TokenType) -> bool:
        """
        Check if current token matches any of the given types and advance.

        Args:
            *types: Token types to match

        Returns:
            True if matched and advanced
        """
        for token_type in types:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _check(self, token_type: TokenType) -> bool:
        """
        Check if current token matches given type without advancing.

        Args:
            token_type: Token type to check

        Returns:
            True if current token matches
        """
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _advance(self) -> Token:
        """
        Advance to next token.

        Returns:
            Previous token
        """
        if not self._is_at_end():
            self.pos += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        """
        Check if at end of token stream.

        Returns:
            True if at EOF
        """
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        """
        Get current token without advancing.

        Returns:
            Current token
        """
        return self.tokens[self.pos]

    def _previous(self) -> Token:
        """
        Get previous token.

        Returns:
            Previous token
        """
        return self.tokens[self.pos - 1]

    def _consume(self, token_type: TokenType, message: str) -> Token:
        """
        Consume token of given type or raise error.

        Args:
            token_type: Expected token type
            message: Error message if not matched

        Returns:
            Consumed token

        Raises:
            ParseError: If token doesn't match
        """
        if self._check(token_type):
            return self._advance()

        raise ParseError(message, self._peek())


def parse(tokens: list[Token]) -> Program:
    """
    Parse Shadow Thirst tokens into AST.

    Args:
        tokens: List of tokens from lexer

    Returns:
        Program AST

    Raises:
        ParseError: If parsing fails
    """
    parser = ShadowThirstParser(tokens)
    return parser.parse()


__all__ = [
    "ParseError",
    "ShadowThirstParser",
    "parse",
]
