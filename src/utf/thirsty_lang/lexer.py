
from __future__ import annotations

from dataclasses import dataclass

from .diagnostics import ThirstyError, nearest_word
from .token import KEYWORDS, Span, Token, TokenType


@dataclass
class Lexer:
    source: str
    file: str = "<memory>"

    def __post_init__(self) -> None:
        self.i = 0
        self.line = 1
        self.col = 1

    def lex(self) -> list[Token]:
        tokens: list[Token] = []
        while not self._at_end():
            ch = self._peek()
            if ch in " \t\r":
                self._advance()
                continue
            if ch == "\n":
                self._advance_line()
                continue
            if ch == "/" and self._peek_next() == "/":
                self._skip_comment()
                continue
            start_line, start_col = self.line, self.col
            if ch.isalpha() or ch == "_":
                tokens.append(self._identifier())
                continue
            if ch.isdigit():
                tokens.append(self._number())
                continue
            if ch == '"':
                tokens.append(self._string())
                continue
            tok = self._punct_or_op(start_line, start_col)
            if tok is None:
                raise ThirstyError(
                    "THIRSTY-E001",
                    f"unexpected character {ch!r}",
                    Span(self.file, start_line, start_col, start_line, start_col + 1),
                )
            tokens.append(tok)
        eof = Span(self.file, self.line, self.col, self.line, self.col)
        tokens.append(Token(TokenType.EOF, "", None, eof))
        return tokens

    def _skip_comment(self) -> None:
        while not self._at_end() and self._peek() != "\n":
            self._advance()

    def _identifier(self) -> Token:
        start = self._span_start()
        chars = []
        while not self._at_end() and (self._peek().isalnum() or self._peek() == "_"):
            chars.append(self._advance())
        lex = "".join(chars)
        kind = KEYWORDS.get(lex, TokenType.IDENT)
        val = lex if kind == TokenType.IDENT else None
        return Token(kind, lex, val, self._span_from_start(start))

    def _number(self) -> Token:
        start = self._span_start()
        chars = []
        while not self._at_end() and self._peek().isdigit():
            chars.append(self._advance())
        is_float = False
        if not self._at_end() and self._peek() == "." and self._peek_next().isdigit():
            is_float = True
            chars.append(self._advance())
            while not self._at_end() and self._peek().isdigit():
                chars.append(self._advance())
        lex = "".join(chars)
        kind = TokenType.FLOAT if is_float else TokenType.INT
        val = float(lex) if is_float else int(lex)
        return Token(kind, lex, val, self._span_from_start(start))

    def _string(self) -> Token:
        start = self._span_start()
        self._advance()
        chars = []
        while not self._at_end():
            ch = self._peek()
            if ch == '"':
                self._advance()
                return Token(TokenType.STRING, self.source_span_text(start), "".join(chars), self._span_from_start(start))
            if ch == "\\":
                self._advance()
                if self._at_end():
                    break
                esc = self._advance()
                mapping = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}
                chars.append(mapping.get(esc, esc))
                continue
            if ch == "\n":
                raise ThirstyError("THIRSTY-E002", "unterminated string literal", self._span_from_start(start))
            chars.append(self._advance())
        raise ThirstyError("THIRSTY-E002", "unterminated string literal", self._span_from_start(start))

    def _punct_or_op(self, line: int, col: int) -> Token | None:
        ch = self._advance()
        two = ch + self._peek()
        mapping2 = {
            "->": TokenType.ARROW,
            "==": TokenType.EQ,
            "!=": TokenType.NE,
            "<=": TokenType.LE,
            ">=": TokenType.GE,
            "&&": TokenType.AND,
            "||": TokenType.OR,
            "|>": TokenType.PIPE,
            "+=": TokenType.PLUS_EQ,
        }
        if two in mapping2:
            self._advance()
            return Token(mapping2[two], two, None, Span(self.file, line, col, self.line, self.col))
        mapping1 = {
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            "[": TokenType.LBRACKET,
            "]": TokenType.RBRACKET,
            ",": TokenType.COMMA,
            ":": TokenType.COLON,
            ";": TokenType.SEMICOLON,
            ".": TokenType.DOT,
            "?": TokenType.QUESTION,
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.STAR,
            "/": TokenType.SLASH,
            "%": TokenType.PERCENT,
            "!": TokenType.BANG,
            "=": TokenType.ASSIGN,
            "<": TokenType.LT,
            ">": TokenType.GT,
        }
        kind = mapping1.get(ch)
        if kind is None:
            return None
        return Token(kind, ch, None, Span(self.file, line, col, self.line, self.col))

    def source_span_text(self, start: tuple[int, int, int]) -> str:
        start_idx, _, _ = start
        return self.source[start_idx:self.i]

    def _span_start(self) -> tuple[int, int, int]:
        return self.i, self.line, self.col

    def _span_from_start(self, start: tuple[int, int, int]) -> Span:
        _, line, col = start
        return Span(self.file, line, col, self.line, self.col)

    def _peek(self) -> str:
        return self.source[self.i]

    def _peek_next(self) -> str:
        if self.i + 1 >= len(self.source):
            return "\0"
        return self.source[self.i + 1]

    def _advance(self) -> str:
        ch = self.source[self.i]
        self.i += 1
        self.col += 1
        return ch

    def _advance_line(self) -> None:
        self.i += 1
        self.line += 1
        self.col = 1

    def _at_end(self) -> bool:
        return self.i >= len(self.source)
