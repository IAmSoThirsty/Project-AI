'use strict';

/**
 * Thirsty-Lang Recursive Descent Parser
 * Matching Python parser.py exactly
 */

const ast = require('./ast');
const { TokenType, KEYWORDS } = require('./lexer');

class ThirstyParseError extends Error {
  constructor(code, message, span) {
    super(message);
    this.code = code;
    this.thirstySpan = span;
  }
}

class DiagnosticBundle extends Error {
  constructor(errors) {
    super(errors.map(e => e.message).join('\n'));
    this.errors = errors;
  }
}

function nearestWord(word, candidates) {
  if (!candidates || candidates.length === 0) return null;
  let best = null;
  let bestDist = Infinity;
  for (const c of candidates) {
    const d = levenshtein(word, c);
    if (d < bestDist && d <= 3) {
      bestDist = d;
      best = c;
    }
  }
  return best;
}

function levenshtein(a, b) {
  const m = a.length, n = b.length;
  const dp = Array.from({ length: m + 1 }, (_, i) => Array.from({ length: n + 1 }, (_, j) => i === 0 ? j : j === 0 ? i : 0));
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (a[i - 1] === b[j - 1]) dp[i][j] = dp[i - 1][j - 1];
      else dp[i][j] = 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
    }
  }
  return dp[m][n];
}

class Parser {
  constructor(tokens) {
    this.tokens = tokens;
    this.i = 0;
    this.errors = [];
  }

  static fromTokens(tokens) {
    return new Parser(tokens);
  }

  parseProgram() {
    const header = this._moduleHeader();
    const decls = [];
    while (!this._check(TokenType.EOF)) {
      try {
        decls.push(this._declaration(false));
      } catch (err) {
        if (err instanceof ThirstyParseError) {
          this.errors.push(err);
          this._synchronize();
        } else {
          throw err;
        }
      }
    }
    const startSpan = this.tokens.length > 0 ? this.tokens[0].span : { file: '<memory>', line: 1, column: 1, endLine: 1, endColumn: 1 };
    const endSpan = this.tokens.length > 0 ? this.tokens[this.tokens.length - 1].span : startSpan;
    const span = startSpan.merge(endSpan);
    const program = new ast.Program(span, decls, header);
    if (this.errors.length > 0) {
      throw new DiagnosticBundle(this.errors);
    }
    return program;
  }

  _moduleHeader() {
    if (!this._check(TokenType.MODULE)) return null;
    const span = this._peek().span;
    this._advance();
    const nameTok = this._consume(TokenType.IDENT, "expected module name after 'module'");
    let mode = 'core';
    if (this._match(TokenType.MODE)) {
      if (this._match(TokenType.GOVERNED)) {
        mode = 'governed';
      } else if (this._match(TokenType.CORE)) {
        mode = 'core';
      } else {
        throw new ThirstyParseError('THIRSTY-E001', "expected 'core' or 'governed' after 'mode'", this._peek().span);
      }
    }
    return new ast.ModuleHeader(span, nameTok.lexeme, mode);
  }

  parseBlockStatements() {
    const items = [];
    while (!this._check(TokenType.RBRACE) && !this._check(TokenType.EOF)) {
      try {
        items.push(this._declaration(false));
      } catch (err) {
        if (err instanceof ThirstyParseError) {
          this.errors.push(err);
          this._synchronize();
        } else {
          throw err;
        }
      }
    }
    return items;
  }

  _declaration(inClass) {
    let vis = null;
    if (this._match(TokenType.PUBLIC)) {
      vis = 'public';
    } else if (this._match(TokenType.PRIVATE)) {
      vis = 'private';
    }
    if (this._match(TokenType.IMPORT)) {
      return this._importDecl();
    }
    if (this._match(TokenType.FOUNTAIN)) {
      return this._classDecl();
    }
    if (this._match(TokenType.ENUM)) {
      return this._enumDecl();
    }
    if (this._match(TokenType.STRUCT)) {
      return this._structDecl();
    }
    if (this._match(TokenType.INTERFACE)) {
      return this._interfaceDecl();
    }
    if (this._match(TokenType.CASCADE)) {
      this._consume(TokenType.GLASS, "expected 'glass' after 'cascade'");
      return this._functionDecl(true, vis, inClass);
    }
    if (this._match(TokenType.GLASS)) {
      return this._functionDecl(false, vis, inClass);
    }
    if (this._match(TokenType.DRINK)) {
      return this._varDecl(vis, inClass);
    }
    if (this._match(TokenType.MUTATION)) {
      return this._mutationDecl();
    }
    return this._statement();
  }

  _enumDecl() {
    const name = this._consume(TokenType.IDENT, 'expected enum name');
    this._consume(TokenType.LBRACE, "expected '{' after enum name");
    const variants = [];
    while (!this._check(TokenType.RBRACE) && !this._check(TokenType.EOF)) {
      const v = this._consume(TokenType.IDENT, 'expected variant name');
      variants.push(v.lexeme);
      if (!this._match(TokenType.COMMA)) break;
    }
    const end = this._consume(TokenType.RBRACE, "expected '}' after enum variants");
    return new ast.EnumDecl(name.span.merge(end.span), name.lexeme, variants);
  }

  _structDecl() {
    const name = this._consume(TokenType.IDENT, 'expected struct name');
    this._consume(TokenType.LBRACE, "expected '{' after struct name");
    const fields = [];
    while (!this._check(TokenType.RBRACE) && !this._check(TokenType.EOF)) {
      const fname = this._consume(TokenType.IDENT, 'expected field name');
      this._consume(TokenType.COLON, "expected ':' after field name");
      const ftype = this._typeNode();
      fields.push(new ast.Param(fname.span.merge(ftype.span), fname.lexeme, ftype));
      if (!this._match(TokenType.COMMA)) break;
    }
    const end = this._consume(TokenType.RBRACE, "expected '}' after struct fields");
    return new ast.StructDecl(name.span.merge(end.span), name.lexeme, fields);
  }

  _interfaceDecl() {
    const name = this._consume(TokenType.IDENT, 'expected interface name');
    this._consume(TokenType.LBRACE, "expected '{' after interface name");
    const methods = [];
    while (!this._check(TokenType.RBRACE) && !this._check(TokenType.EOF)) {
      this._consume(TokenType.GLASS, "expected 'glass' in interface method");
      const fn = this._functionDecl(false, null, true);
      methods.push(fn);
    }
    const end = this._consume(TokenType.RBRACE, "expected '}' after interface body");
    return new ast.InterfaceDecl(name.span.merge(end.span), name.lexeme, methods);
  }

  _importDecl() {
    const mod = this._consume(TokenType.STRING, "expected string module path after import");
    let alias = null;
    if (this._match(TokenType.AS)) {
      alias = this._consume(TokenType.IDENT, "expected alias after 'as'").lexeme;
    }
    const semi = this._consume(TokenType.SEMICOLON, "expected ';' after import");
    return new ast.ImportDecl(mod.span.merge(semi.span), mod.value, alias);
  }

  _classDecl() {
    const name = this._consume(TokenType.IDENT, 'expected class name');
    this._consume(TokenType.LBRACE, "expected '{' after class name");
    const members = [];
    while (!this._check(TokenType.RBRACE) && !this._check(TokenType.EOF)) {
      members.push(this._declaration(true));
    }
    const end = this._consume(TokenType.RBRACE, "expected '}' after class body");
    return new ast.ClassDecl(name.span.merge(end.span), name.lexeme, members);
  }

  _functionDecl(isAsync, visibility, isMethod) {
    const name = this._consume(TokenType.IDENT, 'expected function name');
    this._consume(TokenType.LPAREN, "expected '(' after function name");
    const params = [];
    if (!this._check(TokenType.RPAREN)) {
      while (true) {
        const pname = this._consume(TokenType.IDENT, 'expected parameter name');
        this._consume(TokenType.COLON, "expected ':' after parameter name");
        const ptype = this._typeNode();
        params.push(new ast.Param(pname.span.merge(ptype.span), pname.lexeme, ptype));
        if (!this._match(TokenType.COMMA)) break;
      }
    }
    this._consume(TokenType.RPAREN, "expected ')' after parameters");
    let returnType = null;
    if (this._match(TokenType.ARROW)) {
      returnType = this._typeNode();
    }
    // Parse optional requires clauses
    const requires = [];
    while (this._check(TokenType.REQUIRES)) {
      const reqTok = this._advance();
      const annParts = [];
      while (!this._check(TokenType.LBRACE) && !this._check(TokenType.REQUIRES) && !this._check(TokenType.EOF)) {
        annParts.push(this._advance().lexeme);
      }
      const annotation = annParts.join(' ');
      requires.push(new ast.RequiresClause(reqTok.span, annotation));
    }
    const body = this._block();
    const span = name.span.merge(body.span);
    if (requires.length > 0) {
      return new ast.GovernedFunctionDecl(span, name.lexeme, params, returnType, body, requires, isAsync, visibility, isMethod);
    }
    return new ast.FunctionDecl(span, name.lexeme, params, returnType, body, isAsync, visibility, isMethod);
  }

  _varDecl(visibility, isField) {
    const mutable = this._match(TokenType.MUT);
    const name = this._consume(TokenType.IDENT, 'expected variable name');
    this._consume(TokenType.COLON, "expected ':' after variable name");
    const tnode = this._typeNode();
    if (isField && this._match(TokenType.SEMICOLON)) {
      const init = new ast.LiteralExpr(name.span, null);
      return new ast.VarDecl(name.span.merge(tnode.span), name.lexeme, tnode, init, mutable, visibility, true);
    }
    this._consume(TokenType.ASSIGN, "expected '=' after type annotation");
    const init = this._expression();
    const semi = this._consume(TokenType.SEMICOLON, "expected ';' after declaration");
    return new ast.VarDecl(name.span.merge(semi.span), name.lexeme, tnode, init, mutable, visibility, isField);
  }

  _mutationDecl() {
    this._consume(TokenType.VALIDATED_CANONICAL, "expected 'validated_canonical' after 'mutation'");
    const name = this._consume(TokenType.IDENT, 'expected mutation name');
    this._consume(TokenType.LPAREN, "expected '(' after mutation name");
    const params = [];
    if (!this._check(TokenType.RPAREN)) {
      while (true) {
        const pname = this._consume(TokenType.IDENT, 'expected parameter name');
        this._consume(TokenType.COLON, "expected ':' after parameter name");
        const ptype = this._typeNode();
        params.push(new ast.Param(pname.span.merge(ptype.span), pname.lexeme, ptype));
        if (!this._match(TokenType.COMMA)) break;
      }
    }
    this._consume(TokenType.RPAREN, "expected ')' after parameters");
    this._consume(TokenType.LBRACE, "expected '{' to start mutation block");
    this._consume(TokenType.SHADOW, "expected 'shadow' block");
    const shadowBlock = this._block();
    this._consume(TokenType.INVARIANT, "expected 'invariant' block");
    const invariantBlock = this._block();
    this._consume(TokenType.CANONICAL, "expected 'canonical' block");
    const canonicalBlock = this._block();
    const end = this._consume(TokenType.RBRACE, "expected '}' after mutation block");
    return new ast.MutationDecl(name.span.merge(end.span), name.lexeme, params, shadowBlock, invariantBlock, canonicalBlock);
  }

  _statement() {
    if (this._match(TokenType.POUR)) {
      const start = this._previous().span;
      const safe = this._match(TokenType.QUESTION);
      this._consume(TokenType.LPAREN, "expected '(' after pour");
      const expr = this._expression();
      this._consume(TokenType.RPAREN, "expected ')' after print expression");
      const semi = this._consume(TokenType.SEMICOLON, "expected ';' after pour");
      return new ast.PrintStmt(start.merge(semi.span), expr, safe);
    }
    if (this._match(TokenType.THIRSTY)) {
      const start = this._previous().span;
      this._consume(TokenType.LPAREN, "expected '(' after thirsty");
      const cond = this._expression();
      this._consume(TokenType.RPAREN, "expected ')' after condition");
      const thenBranch = this._block();
      let elseBranch = null;
      let endSpan = thenBranch.span;
      if (this._match(TokenType.HYDRATED)) {
        elseBranch = this._block();
        endSpan = elseBranch.span;
      }
      return new ast.IfStmt(start.merge(endSpan), cond, thenBranch, elseBranch);
    }
    if (this._match(TokenType.REFILL)) {
      const start = this._previous().span;
      const count = this._expression();
      this._consume(TokenType.TIMES, "expected 'times' after loop count");
      const body = this._block();
      return new ast.LoopStmt(start.merge(body.span), count, body);
    }
    if (this._match(TokenType.DRIP)) {
      const start = this._previous().span;
      const name = this._consume(TokenType.IDENT, "expected variable name after drip");
      let amount = null;
      if (this._match(TokenType.PLUS_EQ)) {
        amount = this._expression();
      }
      const semi = this._consume(TokenType.SEMICOLON, "expected ';' after drip");
      return new ast.DripStmt(start.merge(semi.span), name.lexeme, amount);
    }
    if (this._match(TokenType.RETURN)) {
      const start = this._previous().span;
      const expr = this._check(TokenType.SEMICOLON) ? null : this._expression();
      const semi = this._consume(TokenType.SEMICOLON, "expected ';' after return");
      return new ast.ReturnStmt(start.merge(semi.span), expr);
    }
    if (this._match(TokenType.SPILLAGE)) {
      const start = this._previous().span;
      const tryBlock = this._block();
      const catches = [];
      let finallyBlock = null;
      while (this._match(TokenType.CLEANUP)) {
        if (this._match(TokenType.FINALLY)) {
          finallyBlock = this._block();
          break;
        }
        this._consume(TokenType.ERROR, "expected 'error' after cleanup");
        this._consume(TokenType.LPAREN, "expected '(' after cleanup error");
        const catchName = this._consume(TokenType.IDENT, 'expected catch binding name');
        this._consume(TokenType.COLON, "expected ':' in catch clause");
        const typ = this._consumeAny([TokenType.IDENT, TokenType.ERROR], 'expected catch type');
        this._consume(TokenType.RPAREN, "expected ')' after catch clause");
        const block = this._block();
        catches.push(new ast.CatchClause(catchName.span.merge(block.span), catchName.lexeme, typ.lexeme, block));
      }
      if (catches.length === 0 && finallyBlock === null) {
        throw new ThirstyParseError('THIRSTY-E001', 'spillage requires cleanup error or cleanup finally', start);
      }
      const endSpan = finallyBlock ? finallyBlock.span : catches[catches.length - 1].span;
      return new ast.TryStmt(start.merge(endSpan), tryBlock, catches, finallyBlock);
    }
    if (this._match(TokenType.THROW)) {
      const start = this._previous().span;
      const expr = this._expression();
      const semi = this._consume(TokenType.SEMICOLON, "expected ';' after throw");
      return new ast.ThrowStmt(start.merge(semi.span), expr);
    }
    if (this._check(TokenType.LBRACE)) {
      return this._block();
    }
    const expr = this._expression();
    const semi = this._consume(TokenType.SEMICOLON, "expected ';' after expression");
    return new ast.ExprStmt(expr.span.merge(semi.span), expr);
  }

  _block() {
    const start = this._consume(TokenType.LBRACE, "expected '{' to start block");
    const items = this.parseBlockStatements();
    const end = this._consume(TokenType.RBRACE, "expected '}' after block");
    return new ast.BlockStmt(start.span.merge(end.span), items);
  }

  _typeNode() {
    if (this._match(TokenType.RESERVOIR)) {
      const baseTok = this._previous();
      this._consume(TokenType.LBRACKET, "expected '[' after reservoir");
      const arg = this._typeNode();
      const end = this._consume(TokenType.RBRACKET, "expected ']' after reservoir type");
      return new ast.GenericType(baseTok.span.merge(end.span), 'Reservoir', [arg]);
    }
    if (this._match(TokenType.WELL)) {
      const baseTok = this._previous();
      this._consume(TokenType.LBRACKET, "expected '[' after well");
      if (this._match(TokenType.OF)) {
        this._consume(TokenType.COLON, "expected ':' after 'of'");
      }
      const arg = this._typeNode();
      const end = this._consume(TokenType.RBRACKET, "expected ']' after well type");
      return new ast.GenericType(baseTok.span.merge(end.span), 'Reservoir', [arg]);
    }
    const name = this._consumeAny([TokenType.IDENT, TokenType.QUENCHED, TokenType.ERROR], 'expected type name');
    if (this._match(TokenType.LBRACKET)) {
      const args = [this._typeNode()];
      while (this._match(TokenType.COMMA)) {
        args.push(this._typeNode());
      }
      const end = this._consume(TokenType.RBRACKET, "expected ']' after generic args");
      return new ast.GenericType(name.span.merge(end.span), name.lexeme, args);
    }
    return new ast.NamedType(name.span, name.lexeme);
  }

  _expression() {
    return this._guard();
  }

  _guard() {
    if (this._match(TokenType.THIRST)) {
      const start = this._previous().span;
      const cond = this._expression();
      this._consume(TokenType.QUENCH, "expected 'quench' after thirst guard condition");
      const whenTrue = this._expression();
      let whenFalse = null;
      if (this._match(TokenType.HYDRATED)) {
        whenFalse = this._expression();
      }
      const span = start.merge((whenFalse || whenTrue).span);
      return new ast.GuardExpr(span, cond, whenTrue, whenFalse);
    }
    return this._assignment();
  }

  _assignment() {
    const expr = this._pipe();
    if (this._match(TokenType.ASSIGN)) {
      const eq = this._previous();
      const value = this._assignment();
      if (expr instanceof ast.VariableExpr || expr instanceof ast.MemberExpr || expr instanceof ast.IndexExpr) {
        return new ast.AssignExpr(expr.span.merge(value.span), expr, value);
      }
      throw new ThirstyParseError('THIRSTY-E001', 'invalid assignment target', eq.span);
    }
    return expr;
  }

  _pipe() {
    let expr = this._or();
    while (this._match(TokenType.PIPE)) {
      const right = this._or();
      expr = new ast.PipeExpr(expr.span.merge(right.span), expr, right);
    }
    return expr;
  }

  _or() {
    let expr = this._and();
    while (this._match(TokenType.OR)) {
      const op = this._previous();
      const right = this._and();
      expr = new ast.BinaryExpr(expr.span.merge(right.span), expr, op.lexeme, right);
    }
    return expr;
  }

  _and() {
    let expr = this._equality();
    while (this._match(TokenType.AND)) {
      const op = this._previous();
      const right = this._equality();
      expr = new ast.BinaryExpr(expr.span.merge(right.span), expr, op.lexeme, right);
    }
    return expr;
  }

  _equality() {
    let expr = this._comparison();
    while (this._match(TokenType.EQ, TokenType.NE)) {
      const op = this._previous();
      const right = this._comparison();
      expr = new ast.BinaryExpr(expr.span.merge(right.span), expr, op.lexeme, right);
    }
    return expr;
  }

  _comparison() {
    let expr = this._term();
    while (this._match(TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE)) {
      const op = this._previous();
      const right = this._term();
      expr = new ast.BinaryExpr(expr.span.merge(right.span), expr, op.lexeme, right);
    }
    return expr;
  }

  _term() {
    let expr = this._factor();
    while (this._match(TokenType.PLUS, TokenType.MINUS)) {
      const op = this._previous();
      const right = this._factor();
      expr = new ast.BinaryExpr(expr.span.merge(right.span), expr, op.lexeme, right);
    }
    return expr;
  }

  _factor() {
    let expr = this._unary();
    while (this._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT)) {
      const op = this._previous();
      const right = this._unary();
      expr = new ast.BinaryExpr(expr.span.merge(right.span), expr, op.lexeme, right);
    }
    return expr;
  }

  _unary() {
    if (this._match(TokenType.BANG, TokenType.MINUS)) {
      const op = this._previous();
      const right = this._unary();
      return new ast.UnaryExpr(op.span.merge(right.span), op.lexeme, right);
    }
    if (this._match(TokenType.AWAIT)) {
      const op = this._previous();
      const expr = this._unary();
      return new ast.AwaitExpr(op.span.merge(expr.span), expr);
    }
    if (this._match(TokenType.CONDENSE)) {
      const op = this._previous();
      const expr = this._unary();
      return new ast.CondenseExpr(op.span.merge(expr.span), expr);
    }
    if (this._match(TokenType.EVAPORATE)) {
      const op = this._previous();
      const expr = this._unary();
      return new ast.EvaporateExpr(op.span.merge(expr.span), expr);
    }
    return this._call();
  }

  _call() {
    let expr = this._primary();
    while (true) {
      if (this._match(TokenType.QUESTION)) {
        this._consume(TokenType.LPAREN, "expected '(' after safe call");
        const args = this._arguments();
        const end = this._consume(TokenType.RPAREN, "expected ')' after arguments");
        expr = new ast.CallExpr(expr.span.merge(end.span), expr, args, true);
      } else if (this._match(TokenType.LPAREN)) {
        const args = this._arguments();
        const end = this._consume(TokenType.RPAREN, "expected ')' after arguments");
        expr = new ast.CallExpr(expr.span.merge(end.span), expr, args);
      } else if (this._match(TokenType.DOT)) {
        const name = this._consume(TokenType.IDENT, "expected member name after '.'");
        expr = new ast.MemberExpr(expr.span.merge(name.span), expr, name.lexeme);
      } else if (this._match(TokenType.LBRACKET)) {
        const index = this._expression();
        const end = this._consume(TokenType.RBRACKET, "expected ']' after index");
        expr = new ast.IndexExpr(expr.span.merge(end.span), expr, index);
      } else {
        break;
      }
    }
    return expr;
  }

  _arguments() {
    const args = [];
    if (!this._check(TokenType.RPAREN)) {
      args.push(this._expression());
      while (this._match(TokenType.COMMA)) {
        args.push(this._expression());
      }
    }
    return args;
  }

  _primary() {
    if (this._match(TokenType.INT)) {
      const prev = this._previous();
      return new ast.LiteralExpr(prev.span, prev.value);
    }
    if (this._match(TokenType.FLOAT)) {
      const prev = this._previous();
      return new ast.LiteralExpr(prev.span, prev.value);
    }
    if (this._match(TokenType.STRING)) {
      const prev = this._previous();
      return new ast.LiteralExpr(prev.span, prev.value);
    }
    if (this._match(TokenType.PARCHED)) {
      return new ast.LiteralExpr(this._previous().span, true);
    }
    if (this._match(TokenType.QUENCHED)) {
      return new ast.LiteralExpr(this._previous().span, false);
    }
    if (this._match(TokenType.EMPTY)) {
      return new ast.LiteralExpr(this._previous().span, null);
    }
    if (this._match(TokenType.THIS)) {
      return new ast.ThisExpr(this._previous().span);
    }
    if (this._match(TokenType.SIP)) {
      const start = this._previous().span;
      const safe = this._match(TokenType.QUESTION);
      this._consume(TokenType.LPAREN, "expected '(' after sip");
      const end = this._consume(TokenType.RPAREN, "expected ')' after sip");
      return new ast.InputExpr(start.merge(end.span), safe);
    }
    if (this._match(TokenType.NEW)) {
      const start = this._previous().span;
      const name = this._consume(TokenType.IDENT, 'expected class name after new');
      this._consume(TokenType.LPAREN, "expected '(' after class name");
      const args = this._arguments();
      const end = this._consume(TokenType.RPAREN, 'expected ) after constructor args');
      return new ast.NewExpr(start.merge(end.span), name.lexeme, args);
    }
    if (this._match(TokenType.LBRACKET)) {
      const start = this._previous().span;
      const items = [];
      if (!this._check(TokenType.RBRACKET)) {
        items.push(this._expression());
        while (this._match(TokenType.COMMA)) {
          items.push(this._expression());
        }
      }
      const end = this._consume(TokenType.RBRACKET, "expected ']' after array literal");
      return new ast.ArrayExpr(start.merge(end.span), items);
    }
    // Security expressions
    if (this._match(TokenType.SHIELD)) {
      const start = this._previous().span;
      const block = this._block();
      // Treated as a call-like expression that executes block
      return new ast.CallExpr(start.merge(block.span), new ast.VariableExpr(start, '__shield__'), [new ast.LiteralExpr(start, block)]);
    }
    if (this._match(TokenType.SANITIZE)) {
      const start = this._previous().span;
      this._consume(TokenType.LPAREN, "expected '(' after sanitize");
      const arg = this._expression();
      const end = this._consume(TokenType.RPAREN, "expected ')' after sanitize");
      return new ast.CallExpr(start.merge(end.span), new ast.VariableExpr(start, '__sanitize__'), [arg]);
    }
    if (this._match(TokenType.ARMOR)) {
      const start = this._previous().span;
      this._consume(TokenType.LPAREN, "expected '(' after armor");
      const arg = this._expression();
      const end = this._consume(TokenType.RPAREN, "expected ')' after armor");
      return new ast.CallExpr(start.merge(end.span), new ast.VariableExpr(start, '__armor__'), [arg]);
    }
    if (this._match(TokenType.MORPH)) {
      const start = this._previous().span;
      this._consume(TokenType.LPAREN, "expected '(' after morph");
      const arg = this._expression();
      const end = this._consume(TokenType.RPAREN, "expected ')' after morph");
      return new ast.CallExpr(start.merge(end.span), new ast.VariableExpr(start, '__morph__'), [arg]);
    }
    if (this._match(TokenType.DETECT)) {
      const start = this._previous().span;
      this._consume(TokenType.LPAREN, "expected '(' after detect");
      const arg = this._expression();
      const end = this._consume(TokenType.RPAREN, "expected ')' after detect");
      return new ast.CallExpr(start.merge(end.span), new ast.VariableExpr(start, '__detect__'), [arg]);
    }
    if (this._match(TokenType.DEFEND)) {
      const start = this._previous().span;
      this._consume(TokenType.LPAREN, "expected '(' after defend");
      const arg = this._expression();
      const end = this._consume(TokenType.RPAREN, "expected ')' after defend");
      return new ast.CallExpr(start.merge(end.span), new ast.VariableExpr(start, '__defend__'), [arg]);
    }
    if (this._match(TokenType.IDENT)) {
      const prev = this._previous();
      return new ast.VariableExpr(prev.span, prev.lexeme);
    }
    if (this._match(TokenType.LPAREN)) {
      const expr = this._expression();
      this._consume(TokenType.RPAREN, "expected ')' after expression");
      return expr;
    }
    const tok = this._peek();
    throw new ThirstyParseError(
      'THIRSTY-E001',
      `unexpected token '${tok.lexeme || tok.kind}'`,
      tok.span
    );
  }

  _consume(kind, message) {
    if (this._check(kind)) return this._advance();
    const tok = this._peek();
    let msg = message;
    if (tok.kind === TokenType.IDENT) {
      const kwList = Object.keys(KEYWORDS).filter(k => k === k.toLowerCase());
      const suggestion = nearestWord(tok.lexeme, kwList);
      if (suggestion) msg += ` (did you mean '${suggestion}'?)`;
    }
    throw new ThirstyParseError('THIRSTY-E001', msg, tok.span);
  }

  _consumeAny(kinds, message) {
    for (const kind of kinds) {
      if (this._check(kind)) return this._advance();
    }
    const tok = this._peek();
    throw new ThirstyParseError('THIRSTY-E001', message, tok.span);
  }

  _synchronize() {
    while (!this._check(TokenType.EOF)) {
      if (this._previous().kind === TokenType.SEMICOLON) return;
      const syncSet = new Set([
        TokenType.DRINK, TokenType.GLASS, TokenType.FOUNTAIN,
        TokenType.RETURN, TokenType.THIRSTY, TokenType.REFILL,
        TokenType.SPILLAGE, TokenType.DRIP, TokenType.IMPORT,
      ]);
      if (syncSet.has(this._peek().kind)) return;
      this._advance();
    }
  }

  _match(...kinds) {
    for (const kind of kinds) {
      if (this._check(kind)) {
        this._advance();
        return true;
      }
    }
    return false;
  }

  _check(kind) {
    return this._peek().kind === kind;
  }

  _advance() {
    const tok = this.tokens[this.i];
    this.i++;
    return tok;
  }

  _peek() {
    return this.tokens[this.i];
  }

  _previous() {
    return this.tokens[this.i - 1];
  }
}

module.exports = { Parser, ThirstyParseError, DiagnosticBundle };
