"""
Shadow Thirst Lexer

Tokenizes Shadow Thirst source code extending Thirsty-Lang with:
- Shadow/primary blocks
- Activation predicates
- Invariant clauses
- Divergence policies
- Memory qualifiers (Canonical<T>, Shadow<T>, Ephemeral<T>, Dual<T>)
- Mutation boundaries

STATUS: PRODUCTION
VERSION: 1.0.0
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TokenType(Enum):
    """Token types for Shadow Thirst language."""

    # Keywords - Thirsty-Lang base
    DRINK = auto()  # Variable declaration
    POUR = auto()  # Output statement
    SIP = auto()  # Input statement

    # Keywords - Shadow Thirst extensions
    FN = auto()  # Function declaration
    PRIMARY = auto()  # Primary execution block
    SHADOW = auto()  # Shadow execution block
    ACTIVATE_IF = auto()  # Activation predicate
    INVARIANT = auto()  # Invariant clause
    DIVERGENCE = auto()  # Divergence policy
    MUTATION = auto()  # Mutation boundary
    RETURN = auto()  # Return statement
    IF = auto()  # If statement
    ELSE = auto()  # Else statement

    # Divergence policies
    REQUIRE_IDENTICAL = auto()
    ALLOW_EPSILON = auto()
    LOG_DIVERGENCE = auto()
    QUARANTINE_ON_DIVERGE = auto()
    FAIL_PRIMARY = auto()

    # Mutation boundaries
    READ_ONLY = auto()
    EPHEMERAL_ONLY = auto()
    SHADOW_STATE_ONLY = auto()
    VALIDATED_CANONICAL = auto()
    EMERGENCY_OVERRIDE = auto()

    # Type qualifiers
    CANONICAL = auto()
    EPHEMERAL = auto()
    DUAL = auto()

    # Operators
    ASSIGN = auto()  # =
    PLUS = auto()  # +
    MINUS = auto()  # -
    MULTIPLY = auto()  # *
    DIVIDE = auto()  # /
    LT = auto()  # <
    GT = auto()  # >
    LE = auto()  # <=
    GE = auto()  # >=
    EQ = auto()  # ==
    NE = auto()  # !=
    AND = auto()  # &&
    OR = auto()  # ||
    NOT = auto()  # !

    # Delimiters
    LPAREN = auto()  # (
    RPAREN = auto()  # )
    LBRACE = auto()  # {
    RBRACE = auto()  # }
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    COMMA = auto()  # ,
    COLON = auto()  # :
    ARROW = auto()  # ->
    DOT = auto()  # .

    # Literals
    INTEGER = auto()
    FLOAT = auto()
    STRING = auto()
    BOOLEAN = auto()

    # Identifiers
    IDENTIFIER = auto()
    TYPE_IDENTIFIER = auto()

    # Special
    NEWLINE = auto()
    EOF = auto()
    COMMENT = auto()


@dataclass
class Token:
    """Token with type, value, and position information."""

    type: TokenType
    value: Any
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.column})"


class ShadowThirstLexer:
    """
    Lexer for Shadow Thirst language.

    Tokenizes source code into a stream of tokens for parsing.
    Handles both Thirsty-Lang base syntax and Shadow Thirst extensions.
    """

    # Keyword mapping
    KEYWORDS = {
        # Thirsty-Lang base
        "drink": TokenType.DRINK,
        "pour": TokenType.POUR,
        "sip": TokenType.SIP,
        # Shadow Thirst extensions
        "fn": TokenType.FN,
        "primary": TokenType.PRIMARY,
        "shadow": TokenType.SHADOW,
        "activate_if": TokenType.ACTIVATE_IF,
        "invariant": TokenType.INVARIANT,
        "divergence": TokenType.DIVERGENCE,
        "mutation": TokenType.MUTATION,
        "return": TokenType.RETURN,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        # Divergence policies
        "require_identical": TokenType.REQUIRE_IDENTICAL,
        "allow_epsilon": TokenType.ALLOW_EPSILON,
        "log_divergence": TokenType.LOG_DIVERGENCE,
        "quarantine_on_diverge": TokenType.QUARANTINE_ON_DIVERGE,
        "fail_primary": TokenType.FAIL_PRIMARY,
        # Mutation boundaries
        "read_only": TokenType.READ_ONLY,
        "ephemeral_only": TokenType.EPHEMERAL_ONLY,
        "shadow_state_only": TokenType.SHADOW_STATE_ONLY,
        "validated_canonical": TokenType.VALIDATED_CANONICAL,
        "emergency_override": TokenType.EMERGENCY_OVERRIDE,
        # Type qualifiers
        "Canonical": TokenType.CANONICAL,
        "Shadow": TokenType.SHADOW,
        "Ephemeral": TokenType.EPHEMERAL,
        "Dual": TokenType.DUAL,
        # Boolean literals
        "true": TokenType.BOOLEAN,
        "false": TokenType.BOOLEAN,
        "True": TokenType.BOOLEAN,
        "False": TokenType.BOOLEAN,
    }

    def __init__(self, source: str):
        """
        Initialize lexer with source code.

        Args:
            source: Shadow Thirst source code
        """
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []

    def tokenize(self) -> list[Token]:
        """
        Tokenize the entire source code.

        Returns:
            List of tokens
        """
        while self.pos < len(self.source):
            self._skip_whitespace_inline()

            if self.pos >= len(self.source):
                break

            # Skip comments
            if self._peek() == "/" and self._peek(1) == "/":
                self._skip_comment()
                continue

            if self._peek() == "#":
                self._skip_comment()
                continue

            # Handle newlines
            if self._peek() == "\n":
                self._advance()
                continue

            # Tokenize next token
            token = self._next_token()
            if token and token.type != TokenType.COMMENT:
                self.tokens.append(token)

        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))

        return self.tokens

    def _next_token(self) -> Token | None:
        """
        Get the next token from source.

        Returns:
            Next token or None if skipped
        """
        start_line = self.line
        start_column = self.column

        char = self._peek()

        # String literals
        if char in ('"', "'"):
            return self._read_string(start_line, start_column)

        # Number literals
        if char.isdigit():
            return self._read_number(start_line, start_column)

        # Identifiers and keywords
        if char.isalpha() or char == "_":
            return self._read_identifier(start_line, start_column)

        # Operators and delimiters
        return self._read_operator_or_delimiter(start_line, start_column)

    def _read_string(self, line: int, column: int) -> Token:
        """Read a string literal."""
        quote_char = self._advance()
        value = ""

        while self._peek() and self._peek() != quote_char:
            if self._peek() == "\\":
                self._advance()
                # Handle escape sequences
                escape_char = self._advance()
                if escape_char == "n":
                    value += "\n"
                elif escape_char == "t":
                    value += "\t"
                elif escape_char == "\\":
                    value += "\\"
                elif escape_char == quote_char:
                    value += quote_char
                else:
                    value += escape_char
            else:
                value += self._advance()

        if self._peek() == quote_char:
            self._advance()

        return Token(TokenType.STRING, value, line, column)

    def _read_number(self, line: int, column: int) -> Token:
        """Read a number literal (integer or float)."""
        value = ""
        has_dot = False

        while self._peek() and (self._peek().isdigit() or self._peek() == "."):
            if self._peek() == ".":
                if has_dot:
                    break
                has_dot = True
            value += self._advance()

        if has_dot:
            return Token(TokenType.FLOAT, float(value), line, column)
        else:
            return Token(TokenType.INTEGER, int(value), line, column)

    def _read_identifier(self, line: int, column: int) -> Token:
        """Read an identifier or keyword."""
        value = ""

        while self._peek() and (self._peek().isalnum() or self._peek() in ("_",)):
            value += self._advance()

        # Check if it's a keyword
        if value in self.KEYWORDS:
            token_type = self.KEYWORDS[value]
            # For boolean keywords, extract the boolean value
            if token_type == TokenType.BOOLEAN:
                bool_value = value.lower() == "true"
                return Token(TokenType.BOOLEAN, bool_value, line, column)
            return Token(token_type, value, line, column)

        # Check if it's a type identifier (starts with uppercase)
        if value[0].isupper():
            return Token(TokenType.TYPE_IDENTIFIER, value, line, column)

        return Token(TokenType.IDENTIFIER, value, line, column)

    def _read_operator_or_delimiter(self, line: int, column: int) -> Token:
        """Read an operator or delimiter."""
        char = self._peek()

        # Two-character operators
        if char == "=" and self._peek(1) == "=":
            self._advance()
            self._advance()
            return Token(TokenType.EQ, "==", line, column)

        if char == "!" and self._peek(1) == "=":
            self._advance()
            self._advance()
            return Token(TokenType.NE, "!=", line, column)

        if char == "<" and self._peek(1) == "=":
            self._advance()
            self._advance()
            return Token(TokenType.LE, "<=", line, column)

        if char == ">" and self._peek(1) == "=":
            self._advance()
            self._advance()
            return Token(TokenType.GE, ">=", line, column)

        if char == "&" and self._peek(1) == "&":
            self._advance()
            self._advance()
            return Token(TokenType.AND, "&&", line, column)

        if char == "|" and self._peek(1) == "|":
            self._advance()
            self._advance()
            return Token(TokenType.OR, "||", line, column)

        if char == "-" and self._peek(1) == ">":
            self._advance()
            self._advance()
            return Token(TokenType.ARROW, "->", line, column)

        # Single-character operators and delimiters
        single_char_tokens = {
            "=": TokenType.ASSIGN,
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.MULTIPLY,
            "/": TokenType.DIVIDE,
            "<": TokenType.LT,
            ">": TokenType.GT,
            "!": TokenType.NOT,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            "[": TokenType.LBRACKET,
            "]": TokenType.RBRACKET,
            ",": TokenType.COMMA,
            ":": TokenType.COLON,
            ".": TokenType.DOT,
        }

        if char in single_char_tokens:
            self._advance()
            return Token(single_char_tokens[char], char, line, column)

        # Unknown character - skip it
        self._advance()
        return None

    def _peek(self, offset: int = 0) -> str | None:
        """
        Peek at character at current position + offset.

        Args:
            offset: Offset from current position

        Returns:
            Character or None if out of bounds
        """
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return None

    def _advance(self) -> str:
        """
        Advance position and return current character.

        Returns:
            Current character
        """
        char = self.source[self.pos]
        self.pos += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def _skip_whitespace_inline(self):
        """Skip whitespace except newlines."""
        while self._peek() and self._peek() in (" ", "\t", "\r"):
            self._advance()

    def _skip_comment(self):
        """Skip single-line comment."""
        while self._peek() and self._peek() != "\n":
            self._advance()


def tokenize(source: str) -> list[Token]:
    """
    Tokenize Shadow Thirst source code.

    Args:
        source: Shadow Thirst source code

    Returns:
        List of tokens
    """
    lexer = ShadowThirstLexer(source)
    return lexer.tokenize()


__all__ = [
    "TokenType",
    "Token",
    "ShadowThirstLexer",
    "tokenize",
]
