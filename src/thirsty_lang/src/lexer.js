'use strict';

/**
 * Thirsty-Lang Lexer
 * Full tokenizer matching Python lexer.py
 */

const TokenType = {
  EOF: 'EOF',
  IDENT: 'IDENT',
  INT: 'INT',
  FLOAT: 'FLOAT',
  STRING: 'STRING',

  LPAREN: 'LPAREN',
  RPAREN: 'RPAREN',
  LBRACE: 'LBRACE',
  RBRACE: 'RBRACE',
  LBRACKET: 'LBRACKET',
  RBRACKET: 'RBRACKET',
  COMMA: 'COMMA',
  COLON: 'COLON',
  SEMICOLON: 'SEMICOLON',
  DOT: 'DOT',
  ARROW: 'ARROW',
  QUESTION: 'QUESTION',

  PLUS: 'PLUS',
  MINUS: 'MINUS',
  STAR: 'STAR',
  SLASH: 'SLASH',
  PERCENT: 'PERCENT',
  BANG: 'BANG',
  ASSIGN: 'ASSIGN',
  EQ: 'EQ',
  NE: 'NE',
  LT: 'LT',
  LE: 'LE',
  GT: 'GT',
  GE: 'GE',
  AND: 'AND',
  OR: 'OR',
  PIPE: 'PIPE',
  PLUS_EQ: 'PLUS_EQ',

  // keywords
  DRINK: 'DRINK',
  POUR: 'POUR',
  SIP: 'SIP',
  THIRSTY: 'THIRSTY',
  HYDRATED: 'HYDRATED',
  THIRST: 'THIRST',
  QUENCH: 'QUENCH',
  REFILL: 'REFILL',
  TIMES: 'TIMES',
  GLASS: 'GLASS',
  RESERVOIR: 'RESERVOIR',
  WELL: 'WELL',
  OF: 'OF',
  FLOOD: 'FLOOD',
  DRIP: 'DRIP',
  EVAPORATE: 'EVAPORATE',
  CONDENSE: 'CONDENSE',
  FOUNTAIN: 'FOUNTAIN',
  RETURN: 'RETURN',
  PARCHED: 'PARCHED',
  QUENCHED: 'QUENCHED',
  EMPTY: 'EMPTY',
  MUT: 'MUT',
  IMPORT: 'IMPORT',
  FROM: 'FROM',
  AS: 'AS',
  SHIELD: 'SHIELD',
  SANITIZE: 'SANITIZE',
  ARMOR: 'ARMOR',
  MORPH: 'MORPH',
  DETECT: 'DETECT',
  DEFEND: 'DEFEND',

  CASCADE: 'CASCADE',
  THIS: 'THIS',
  NEW: 'NEW',
  PUBLIC: 'PUBLIC',
  PRIVATE: 'PRIVATE',
  AWAIT: 'AWAIT',
  SPILLAGE: 'SPILLAGE',
  CLEANUP: 'CLEANUP',
  FINALLY: 'FINALLY',
  ERROR: 'ERROR',
  THROW: 'THROW',

  POLICY: 'POLICY',
  WHEN: 'WHEN',
  ALLOW: 'ALLOW',
  DENY: 'DENY',
  ESCALATE: 'ESCALATE',

  MUTATION: 'MUTATION',
  VALIDATED_CANONICAL: 'VALIDATED_CANONICAL',
  INVARIANT: 'INVARIANT',
  SHADOW: 'SHADOW',
  CANONICAL: 'CANONICAL',
  PROMOTE: 'PROMOTE',
  REJECT: 'REJECT',

  MODULE: 'MODULE',
  MODE: 'MODE',
  CORE: 'CORE',
  GOVERNED: 'GOVERNED',

  ENUM: 'ENUM',
  STRUCT: 'STRUCT',
  INTERFACE: 'INTERFACE',
  REQUIRES: 'REQUIRES',
};

const KEYWORDS = {
  drink: TokenType.DRINK,
  pour: TokenType.POUR,
  sip: TokenType.SIP,
  thirsty: TokenType.THIRSTY,
  hydrated: TokenType.HYDRATED,
  thirst: TokenType.THIRST,
  quench: TokenType.QUENCH,
  refill: TokenType.REFILL,
  times: TokenType.TIMES,
  glass: TokenType.GLASS,
  reservoir: TokenType.RESERVOIR,
  well: TokenType.WELL,
  of: TokenType.OF,
  flood: TokenType.FLOOD,
  drip: TokenType.DRIP,
  evaporate: TokenType.EVAPORATE,
  condense: TokenType.CONDENSE,
  fountain: TokenType.FOUNTAIN,
  return: TokenType.RETURN,
  parched: TokenType.PARCHED,
  quenched: TokenType.QUENCHED,
  empty: TokenType.EMPTY,
  mut: TokenType.MUT,
  import: TokenType.IMPORT,
  from: TokenType.FROM,
  as: TokenType.AS,
  shield: TokenType.SHIELD,
  sanitize: TokenType.SANITIZE,
  armor: TokenType.ARMOR,
  morph: TokenType.MORPH,
  detect: TokenType.DETECT,
  defend: TokenType.DEFEND,
  cascade: TokenType.CASCADE,
  this: TokenType.THIS,
  new: TokenType.NEW,
  public: TokenType.PUBLIC,
  private: TokenType.PRIVATE,
  await: TokenType.AWAIT,
  spillage: TokenType.SPILLAGE,
  cleanup: TokenType.CLEANUP,
  finally: TokenType.FINALLY,
  error: TokenType.ERROR,
  throw: TokenType.THROW,
  policy: TokenType.POLICY,
  when: TokenType.WHEN,
  ALLOW: TokenType.ALLOW,
  DENY: TokenType.DENY,
  ESCALATE: TokenType.ESCALATE,
  mutation: TokenType.MUTATION,
  validated_canonical: TokenType.VALIDATED_CANONICAL,
  invariant: TokenType.INVARIANT,
  shadow: TokenType.SHADOW,
  canonical: TokenType.CANONICAL,
  promote: TokenType.PROMOTE,
  reject: TokenType.REJECT,
  module: TokenType.MODULE,
  mode: TokenType.MODE,
  core: TokenType.CORE,
  governed: TokenType.GOVERNED,
  enum: TokenType.ENUM,
  struct: TokenType.STRUCT,
  interface: TokenType.INTERFACE,
  requires: TokenType.REQUIRES,
};

class Span {
  constructor(file, line, column, endLine, endColumn) {
    this.file = file;
    this.line = line;
    this.column = column;
    this.endLine = endLine;
    this.endColumn = endColumn;
  }

  merge(other) {
    return new Span(this.file, this.line, this.column, other.endLine, other.endColumn);
  }
}

class Token {
  constructor(kind, lexeme, value, span) {
    this.kind = kind;
    this.lexeme = lexeme;
    this.value = value;
    this.span = span;
  }
}

class ThirstyLexError extends Error {
  constructor(code, message, span) {
    super(message);
    this.code = code;
    this.thirstySpan = span;
  }
}

class Lexer {
  constructor(source, file = '<memory>') {
    this.source = source;
    this.file = file;
    this.i = 0;
    this.line = 1;
    this.col = 1;
  }

  lex() {
    const tokens = [];
    while (!this._atEnd()) {
      const ch = this._peek();
      if (ch === ' ' || ch === '\t' || ch === '\r') {
        this._advance();
        continue;
      }
      if (ch === '\n') {
        this._advanceLine();
        continue;
      }
      if (ch === '/' && this._peekNext() === '/') {
        this._skipComment();
        continue;
      }
      const startLine = this.line;
      const startCol = this.col;
      if (/[a-zA-Z_]/.test(ch)) {
        tokens.push(this._identifier());
        continue;
      }
      if (/[0-9]/.test(ch)) {
        tokens.push(this._number());
        continue;
      }
      if (ch === '"') {
        tokens.push(this._string());
        continue;
      }
      const tok = this._punctOrOp(startLine, startCol);
      if (tok === null) {
        throw new ThirstyLexError(
          'THIRSTY-E001',
          `unexpected character ${JSON.stringify(ch)}`,
          new Span(this.file, startLine, startCol, startLine, startCol + 1)
        );
      }
      tokens.push(tok);
    }
    const eof = new Span(this.file, this.line, this.col, this.line, this.col);
    tokens.push(new Token(TokenType.EOF, '', null, eof));
    return tokens;
  }

  _skipComment() {
    while (!this._atEnd() && this._peek() !== '\n') {
      this._advance();
    }
  }

  _identifier() {
    const start = this._spanStart();
    const chars = [];
    while (!this._atEnd() && /[a-zA-Z0-9_]/.test(this._peek())) {
      chars.push(this._advance());
    }
    const lex = chars.join('');
    const kind = KEYWORDS[lex] || TokenType.IDENT;
    const val = kind === TokenType.IDENT ? lex : null;
    return new Token(kind, lex, val, this._spanFromStart(start));
  }

  _number() {
    const start = this._spanStart();
    const chars = [];
    while (!this._atEnd() && /[0-9]/.test(this._peek())) {
      chars.push(this._advance());
    }
    let isFloat = false;
    if (!this._atEnd() && this._peek() === '.' && /[0-9]/.test(this._peekNext())) {
      isFloat = true;
      chars.push(this._advance());
      while (!this._atEnd() && /[0-9]/.test(this._peek())) {
        chars.push(this._advance());
      }
    }
    const lex = chars.join('');
    const kind = isFloat ? TokenType.FLOAT : TokenType.INT;
    const val = isFloat ? parseFloat(lex) : parseInt(lex, 10);
    return new Token(kind, lex, val, this._spanFromStart(start));
  }

  _string() {
    const start = this._spanStart();
    this._advance(); // consume opening "
    const chars = [];
    while (!this._atEnd()) {
      const ch = this._peek();
      if (ch === '"') {
        this._advance();
        const spanEnd = this._spanFromStart(start);
        return new Token(TokenType.STRING, this._sourceSpanText(start), chars.join(''), spanEnd);
      }
      if (ch === '\\') {
        this._advance();
        if (this._atEnd()) break;
        const esc = this._advance();
        const mapping = { n: '\n', t: '\t', '"': '"', '\\': '\\' };
        chars.push(mapping[esc] !== undefined ? mapping[esc] : esc);
        continue;
      }
      if (ch === '\n') {
        throw new ThirstyLexError(
          'THIRSTY-E002',
          'unterminated string literal',
          this._spanFromStart(start)
        );
      }
      chars.push(this._advance());
    }
    throw new ThirstyLexError(
      'THIRSTY-E002',
      'unterminated string literal',
      this._spanFromStart(start)
    );
  }

  _punctOrOp(line, col) {
    const ch = this._advance();
    const two = ch + this._peek();
    const mapping2 = {
      '->': TokenType.ARROW,
      '==': TokenType.EQ,
      '!=': TokenType.NE,
      '<=': TokenType.LE,
      '>=': TokenType.GE,
      '&&': TokenType.AND,
      '||': TokenType.OR,
      '|>': TokenType.PIPE,
      '+=': TokenType.PLUS_EQ,
    };
    if (mapping2[two]) {
      this._advance();
      return new Token(mapping2[two], two, null, new Span(this.file, line, col, this.line, this.col));
    }
    const mapping1 = {
      '(': TokenType.LPAREN,
      ')': TokenType.RPAREN,
      '{': TokenType.LBRACE,
      '}': TokenType.RBRACE,
      '[': TokenType.LBRACKET,
      ']': TokenType.RBRACKET,
      ',': TokenType.COMMA,
      ':': TokenType.COLON,
      ';': TokenType.SEMICOLON,
      '.': TokenType.DOT,
      '?': TokenType.QUESTION,
      '+': TokenType.PLUS,
      '-': TokenType.MINUS,
      '*': TokenType.STAR,
      '/': TokenType.SLASH,
      '%': TokenType.PERCENT,
      '!': TokenType.BANG,
      '=': TokenType.ASSIGN,
      '<': TokenType.LT,
      '>': TokenType.GT,
    };
    const kind = mapping1[ch];
    if (!kind) return null;
    return new Token(kind, ch, null, new Span(this.file, line, col, this.line, this.col));
  }

  _sourceSpanText(start) {
    return this.source.slice(start[0], this.i);
  }

  _spanStart() {
    return [this.i, this.line, this.col];
  }

  _spanFromStart(start) {
    const [, line, col] = start;
    return new Span(this.file, line, col, this.line, this.col);
  }

  _peek() {
    if (this.i >= this.source.length) return '\0';
    return this.source[this.i];
  }

  _peekNext() {
    if (this.i + 1 >= this.source.length) return '\0';
    return this.source[this.i + 1];
  }

  _advance() {
    const ch = this.source[this.i];
    this.i++;
    this.col++;
    return ch;
  }

  _advanceLine() {
    this.i++;
    this.line++;
    this.col = 1;
  }

  _atEnd() {
    return this.i >= this.source.length;
  }
}

module.exports = { Lexer, Token, TokenType, KEYWORDS, Span, ThirstyLexError };
