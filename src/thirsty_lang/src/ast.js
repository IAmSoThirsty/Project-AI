'use strict';

/**
 * Thirsty-Lang AST Node Classes
 * Matching Python ast.py
 */

class Node {
  constructor(span) {
    this.span = span;
  }
}

// Type nodes
class TypeNode extends Node {}

class NamedType extends TypeNode {
  constructor(span, name) {
    super(span);
    this.name = name;
  }
}

class GenericType extends TypeNode {
  constructor(span, base, args) {
    super(span);
    this.base = base;
    this.args = args;
  }
}

class FunctionType extends TypeNode {
  constructor(span, params, result) {
    super(span);
    this.params = params;
    this.result = result;
  }
}

// Expressions
class Expr extends Node {}

class LiteralExpr extends Expr {
  constructor(span, value) {
    super(span);
    this.value = value;
  }
}

class VariableExpr extends Expr {
  constructor(span, name) {
    super(span);
    this.name = name;
  }
}

class ThisExpr extends Expr {
  constructor(span) {
    super(span);
  }
}

class InputExpr extends Expr {
  constructor(span, safe = false) {
    super(span);
    this.safe = safe;
  }
}

class ArrayExpr extends Expr {
  constructor(span, items) {
    super(span);
    this.items = items;
  }
}

class AssignExpr extends Expr {
  constructor(span, target, value) {
    super(span);
    this.target = target;
    this.value = value;
  }
}

class UnaryExpr extends Expr {
  constructor(span, op, right) {
    super(span);
    this.op = op;
    this.right = right;
  }
}

class BinaryExpr extends Expr {
  constructor(span, left, op, right) {
    super(span);
    this.left = left;
    this.op = op;
    this.right = right;
  }
}

class PipeExpr extends Expr {
  constructor(span, left, right) {
    super(span);
    this.left = left;
    this.right = right;
  }
}

class GuardExpr extends Expr {
  constructor(span, condition, whenTrue, whenFalse) {
    super(span);
    this.condition = condition;
    this.whenTrue = whenTrue;
    this.whenFalse = whenFalse;
  }
}

class CallExpr extends Expr {
  constructor(span, callee, args, safe = false) {
    super(span);
    this.callee = callee;
    this.args = args;
    this.safe = safe;
  }
}

class MemberExpr extends Expr {
  constructor(span, obj, name) {
    super(span);
    this.obj = obj;
    this.name = name;
  }
}

class IndexExpr extends Expr {
  constructor(span, obj, index) {
    super(span);
    this.obj = obj;
    this.index = index;
  }
}

class NewExpr extends Expr {
  constructor(span, className, args) {
    super(span);
    this.className = className;
    this.args = args;
  }
}

class AwaitExpr extends Expr {
  constructor(span, expr) {
    super(span);
    this.expr = expr;
  }
}

class CondenseExpr extends Expr {
  constructor(span, expr) {
    super(span);
    this.expr = expr;
  }
}

class EvaporateExpr extends Expr {
  constructor(span, expr) {
    super(span);
    this.expr = expr;
  }
}

// Statements
class Stmt extends Node {}

class BlockStmt extends Stmt {
  constructor(span, statements) {
    super(span);
    this.statements = statements;
  }
}

class ExprStmt extends Stmt {
  constructor(span, expr) {
    super(span);
    this.expr = expr;
  }
}

class PrintStmt extends Stmt {
  constructor(span, expr, safe = false) {
    super(span);
    this.expr = expr;
    this.safe = safe;
  }
}

class ReturnStmt extends Stmt {
  constructor(span, expr) {
    super(span);
    this.expr = expr; // null if no value
  }
}

class ThrowStmt extends Stmt {
  constructor(span, expr) {
    super(span);
    this.expr = expr;
  }
}

class DripStmt extends Stmt {
  constructor(span, name, amount = null) {
    super(span);
    this.name = name;
    this.amount = amount;
  }
}

class IfStmt extends Stmt {
  constructor(span, condition, thenBranch, elseBranch) {
    super(span);
    this.condition = condition;
    this.thenBranch = thenBranch;
    this.elseBranch = elseBranch;
  }
}

class LoopStmt extends Stmt {
  constructor(span, count, body) {
    super(span);
    this.count = count;
    this.body = body;
  }
}

class CatchClause extends Node {
  constructor(span, name, typeName, block) {
    super(span);
    this.name = name;
    this.typeName = typeName;
    this.block = block;
  }
}

class TryStmt extends Stmt {
  constructor(span, tryBlock, catches, finallyBlock = null) {
    super(span);
    this.tryBlock = tryBlock;
    this.catches = catches;
    this.finallyBlock = finallyBlock;
  }
}

class Param extends Node {
  constructor(span, name, typeNode) {
    super(span);
    this.name = name;
    this.typeNode = typeNode;
  }
}

class VarDecl extends Stmt {
  constructor(span, name, typeNode, initializer, mutable = false, visibility = null, isField = false) {
    super(span);
    this.name = name;
    this.typeNode = typeNode;
    this.initializer = initializer;
    this.mutable = mutable;
    this.visibility = visibility;
    this.isField = isField;
  }
}

class FunctionDecl extends Stmt {
  constructor(span, name, params, returnType, body, isAsync = false, visibility = null, isMethod = false) {
    super(span);
    this.name = name;
    this.params = params;
    this.returnType = returnType;
    this.body = body;
    this.isAsync = isAsync;
    this.visibility = visibility;
    this.isMethod = isMethod;
  }
}

class ClassDecl extends Stmt {
  constructor(span, name, members) {
    super(span);
    this.name = name;
    this.members = members;
  }
}

class ImportDecl extends Stmt {
  constructor(span, module, alias = null) {
    super(span);
    this.module = module;
    this.alias = alias;
  }
}

class ModuleHeader extends Node {
  constructor(span, name, mode = 'core') {
    super(span);
    this.name = name;
    this.mode = mode;
  }
}

class RequiresClause extends Node {
  constructor(span, annotation) {
    super(span);
    this.annotation = annotation;
  }
}

class GovernedFunctionDecl extends Stmt {
  constructor(span, name, params, returnType, body, requires = [], isAsync = false, visibility = null, isMethod = false) {
    super(span);
    this.name = name;
    this.params = params;
    this.returnType = returnType;
    this.body = body;
    this.requires = requires;
    this.isAsync = isAsync;
    this.visibility = visibility;
    this.isMethod = isMethod;
  }
}

class EnumDecl extends Stmt {
  constructor(span, name, variants) {
    super(span);
    this.name = name;
    this.variants = variants;
  }
}

class StructDecl extends Stmt {
  constructor(span, name, fields) {
    super(span);
    this.name = name;
    this.fields = fields;
  }
}

class InterfaceDecl extends Stmt {
  constructor(span, name, methods) {
    super(span);
    this.name = name;
    this.methods = methods;
  }
}

class Program extends Node {
  constructor(span, declarations = [], header = null) {
    super(span);
    this.declarations = declarations;
    this.header = header;
  }
}

class MutationDecl extends Stmt {
  constructor(span, name, params, shadowBlock, invariantBlock, canonicalBlock) {
    super(span);
    this.name = name;
    this.params = params;
    this.shadowBlock = shadowBlock;
    this.invariantBlock = invariantBlock;
    this.canonicalBlock = canonicalBlock;
  }
}

module.exports = {
  Node, TypeNode, NamedType, GenericType, FunctionType,
  Expr, LiteralExpr, VariableExpr, ThisExpr, InputExpr, ArrayExpr,
  AssignExpr, UnaryExpr, BinaryExpr, PipeExpr, GuardExpr,
  CallExpr, MemberExpr, IndexExpr, NewExpr, AwaitExpr,
  CondenseExpr, EvaporateExpr,
  Stmt, BlockStmt, ExprStmt, PrintStmt, ReturnStmt, ThrowStmt,
  DripStmt, IfStmt, LoopStmt, CatchClause, TryStmt,
  Param, VarDecl, FunctionDecl, ClassDecl, ImportDecl,
  ModuleHeader, RequiresClause, GovernedFunctionDecl,
  EnumDecl, StructDecl, InterfaceDecl, Program, MutationDecl,
};
