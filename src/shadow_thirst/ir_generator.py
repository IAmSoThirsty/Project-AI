"""
Shadow Thirst IR Generator

Converts Shadow Thirst AST to dual-plane IR.
Implements the Plane Splitter and IR generation stages of the compiler pipeline.

STATUS: PRODUCTION
VERSION: 1.0.0
"""

import logging
from typing import Any

from shadow_thirst.ast_nodes import (
    Assignment,
    ASTNode,
    BinaryOp,
    Expression,
    ExpressionStatement,
    FunctionCall,
    FunctionDefinition,
    Identifier,
    Literal,
    MemberAccess,
    OutputStatement,
    PlaneQualifier,
    Program,
    ReturnStatement,
    UnaryOp,
    VariableDeclaration,
)
from shadow_thirst.ir import (
    ExecutionPlane,
    IRBuilder,
    IRFunction,
    IROpcode,
    IRProgram,
    PlaneQualifierIR,
)

logger = logging.getLogger(__name__)


class IRGenerator:
    """
    Generate dual-plane IR from Shadow Thirst AST.

    Implements plane splitting and IR emission for primary, shadow,
    and invariant execution contexts.
    """

    def __init__(self):
        """Initialize IR generator."""
        self.builder = IRBuilder()
        self.program = IRProgram()

    def generate(self, ast: Program) -> IRProgram:
        """
        Generate IR from AST.

        Args:
            ast: Shadow Thirst Program AST

        Returns:
            IR program
        """
        logger.info("Generating IR from AST")

        # Generate IR for all functions
        for function_ast in ast.functions:
            ir_function = self._generate_function(function_ast)
            self.program.add_function(ir_function)

        # Generate IR for top-level statements (if any)
        if ast.statements:
            main_function = self._generate_main(ast.statements)
            self.program.add_function(main_function)

        logger.info("IR generation complete: %d functions", len(self.program.functions))
        return self.program

    def _generate_function(self, function_ast: FunctionDefinition) -> IRFunction:
        """Generate IR for function definition."""
        logger.debug("Generating IR for function: %s", function_ast.name)

        # Create new function
        return_type = str(function_ast.return_type) if function_ast.return_type else None
        ir_function = self.builder.new_function(function_ast.name, return_type)

        # Add parameters
        for param in function_ast.parameters:
            qualifier = self._convert_plane_qualifier(
                param.type_annotation.qualifier if param.type_annotation else None
            )
            type_name = param.type_annotation.name if param.type_annotation else None
            self.builder.add_variable(param.name, qualifier, type_name, is_parameter=True)

        # Generate primary plane IR
        if function_ast.primary_block:
            self.builder.set_plane(ExecutionPlane.PRIMARY)
            primary_block = self.builder.new_block(ExecutionPlane.PRIMARY)
            self._generate_block_statements(function_ast.primary_block.statements)
            ir_function.primary_blocks.append(primary_block)

        # Generate shadow plane IR
        if function_ast.shadow_block:
            ir_function.has_shadow = True
            self.builder.set_plane(ExecutionPlane.SHADOW)
            shadow_block = self.builder.new_block(ExecutionPlane.SHADOW)

            # Emit shadow activation check
            self.builder.emit(IROpcode.ACTIVATE_SHADOW)

            self._generate_block_statements(function_ast.shadow_block.statements)
            ir_function.shadow_blocks.append(shadow_block)

        # Generate activation predicate IR
        if function_ast.activation_predicate:
            predicate_block = self.builder.new_block(ExecutionPlane.SHADOW)
            self._generate_expression(function_ast.activation_predicate.condition)
            ir_function.activation_predicate_blocks.append(predicate_block)

        # Generate invariant IR
        if function_ast.invariants:
            ir_function.has_invariants = True
            self.builder.set_plane(ExecutionPlane.INVARIANT)
            invariant_block = self.builder.new_block(ExecutionPlane.INVARIANT)

            for condition in function_ast.invariants.conditions:
                self._generate_expression(condition)
                self.builder.emit(IROpcode.CHECK_INVARIANT)

            ir_function.invariant_blocks.append(invariant_block)

        # Set divergence policy
        if function_ast.divergence_policy:
            ir_function.divergence_policy = function_ast.divergence_policy.policy_type.value
            ir_function.divergence_epsilon = function_ast.divergence_policy.epsilon

        # Set mutation boundary
        if function_ast.mutation_boundary:
            ir_function.mutation_boundary = function_ast.mutation_boundary.boundary_type.value

        # Emit constitutional validation if needed
        if ir_function.has_shadow and ir_function.has_invariants:
            self.builder.set_plane(ExecutionPlane.PRIMARY)
            constitutional_block = self.builder.new_block(ExecutionPlane.PRIMARY)
            self.builder.emit(IROpcode.VALIDATE_AND_COMMIT)
            self.builder.emit(IROpcode.SEAL_AUDIT)
            ir_function.primary_blocks.append(constitutional_block)

        return ir_function

    def _generate_main(self, statements: list[Any]) -> IRFunction:
        """Generate IR for top-level statements as main function."""
        ir_function = self.builder.new_function("__main__", None)

        self.builder.set_plane(ExecutionPlane.PRIMARY)
        main_block = self.builder.new_block(ExecutionPlane.PRIMARY)

        self._generate_block_statements(statements)

        ir_function.primary_blocks.append(main_block)
        return ir_function

    def _generate_block_statements(self, statements: list[Any]):
        """Generate IR for a list of statements."""
        for stmt in statements:
            self._generate_statement(stmt)

    def _generate_statement(self, stmt: ASTNode):
        """Generate IR for a statement."""
        if isinstance(stmt, VariableDeclaration):
            self._generate_variable_declaration(stmt)
        elif isinstance(stmt, Assignment):
            self._generate_assignment(stmt)
        elif isinstance(stmt, ReturnStatement):
            self._generate_return(stmt)
        elif isinstance(stmt, OutputStatement):
            self._generate_output(stmt)
        elif isinstance(stmt, ExpressionStatement):
            self._generate_expression(stmt.expression)
            # Pop unused expression result
            self.builder.emit(IROpcode.POP)
        else:
            logger.warning("Unsupported statement type: %s", type(stmt).__name__)

    def _generate_variable_declaration(self, stmt: VariableDeclaration):
        """Generate IR for variable declaration."""
        # Determine plane qualifier
        qualifier = self._convert_plane_qualifier(stmt.type_annotation.qualifier if stmt.type_annotation else None)

        type_name = stmt.type_annotation.name if stmt.type_annotation else None

        # Add variable to function
        self.builder.add_variable(stmt.name, qualifier, type_name, is_parameter=False)

        # Generate initializer if present
        if stmt.initializer:
            self._generate_expression(stmt.initializer)
            self.builder.emit(IROpcode.STORE_VAR, stmt.name)

    def _generate_assignment(self, stmt: Assignment):
        """Generate IR for assignment."""
        self._generate_expression(stmt.value)
        self.builder.emit(IROpcode.STORE_VAR, stmt.target)

    def _generate_return(self, stmt: ReturnStatement):
        """Generate IR for return statement."""
        if stmt.value:
            self._generate_expression(stmt.value)
        else:
            # Push null/void return value
            self.builder.emit(IROpcode.PUSH, None)

        self.builder.emit(IROpcode.RETURN)

    def _generate_output(self, stmt: OutputStatement):
        """Generate IR for output statement."""
        self._generate_expression(stmt.expression)
        self.builder.emit(IROpcode.OUTPUT)

    def _generate_expression(self, expr: Expression):
        """Generate IR for expression."""
        if isinstance(expr, Literal):
            self._generate_literal(expr)
        elif isinstance(expr, Identifier):
            self._generate_identifier(expr)
        elif isinstance(expr, BinaryOp):
            self._generate_binary_op(expr)
        elif isinstance(expr, UnaryOp):
            self._generate_unary_op(expr)
        elif isinstance(expr, FunctionCall):
            self._generate_function_call(expr)
        elif isinstance(expr, MemberAccess):
            self._generate_member_access(expr)
        else:
            logger.warning("Unsupported expression type: %s", type(expr).__name__)

    def _generate_literal(self, expr: Literal):
        """Generate IR for literal."""
        self.builder.emit(IROpcode.LOAD_CONST, expr.value)

    def _generate_identifier(self, expr: Identifier):
        """Generate IR for identifier."""
        self.builder.emit(IROpcode.LOAD_VAR, expr.name)

    def _generate_binary_op(self, expr: BinaryOp):
        """Generate IR for binary operation."""
        # Generate left operand
        self._generate_expression(expr.left)

        # Generate right operand
        self._generate_expression(expr.right)

        # Emit operator instruction
        opcode_map = {
            "+": IROpcode.ADD,
            "-": IROpcode.SUB,
            "*": IROpcode.MUL,
            "/": IROpcode.DIV,
            "==": IROpcode.EQ,
            "!=": IROpcode.NE,
            "<": IROpcode.LT,
            "<=": IROpcode.LE,
            ">": IROpcode.GT,
            ">=": IROpcode.GE,
            "&&": IROpcode.AND,
            "||": IROpcode.OR,
        }

        opcode = opcode_map.get(expr.operator)
        if opcode:
            self.builder.emit(opcode)
        else:
            logger.warning("Unsupported binary operator: %s", expr.operator)

    def _generate_unary_op(self, expr: UnaryOp):
        """Generate IR for unary operation."""
        self._generate_expression(expr.operand)

        if expr.operator == "!":
            self.builder.emit(IROpcode.NOT)
        elif expr.operator == "-":
            self.builder.emit(IROpcode.NEG)
        else:
            logger.warning("Unsupported unary operator: %s", expr.operator)

    def _generate_function_call(self, expr: FunctionCall):
        """Generate IR for function call."""
        # Generate arguments (in reverse order for stack-based evaluation)
        for arg in expr.arguments:
            self._generate_expression(arg)

        # Emit call instruction
        self.builder.emit(IROpcode.CALL, expr.function, len(expr.arguments))

    def _generate_member_access(self, expr: MemberAccess):
        """Generate IR for member access."""
        # Generate object
        self._generate_expression(expr.object)

        # For now, simple member load
        # In a real implementation, this would need struct/object support
        self.builder.emit(IROpcode.LOAD_VAR, expr.member)

    def _convert_plane_qualifier(self, qualifier: PlaneQualifier | None) -> PlaneQualifierIR:
        """Convert AST plane qualifier to IR plane qualifier."""
        if qualifier == PlaneQualifier.CANONICAL:
            return PlaneQualifierIR.CANONICAL
        elif qualifier == PlaneQualifier.SHADOW:
            return PlaneQualifierIR.SHADOW
        elif qualifier == PlaneQualifier.EPHEMERAL:
            return PlaneQualifierIR.EPHEMERAL
        elif qualifier == PlaneQualifier.DUAL:
            return PlaneQualifierIR.DUAL
        else:
            # Default to ephemeral
            return PlaneQualifierIR.EPHEMERAL


def generate_ir(ast: Program) -> IRProgram:
    """
    Generate IR from AST.

    Args:
        ast: Shadow Thirst Program AST

    Returns:
        IR program
    """
    generator = IRGenerator()
    return generator.generate(ast)


__all__ = [
    "IRGenerator",
    "generate_ir",
]
