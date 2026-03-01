"""
Shadow Thirst Abstract Syntax Tree (AST) Node Definitions

Defines AST nodes for Shadow Thirst language constructs:
- Function definitions with primary/shadow/invariant blocks
- Statements and expressions
- Type annotations with plane qualifiers
- Activation predicates and invariants

STATUS: PRODUCTION
VERSION: 1.0.0
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PlaneQualifier(Enum):
    """Memory plane qualifiers."""

    CANONICAL = "Canonical"  # Primary plane only, persistent
    SHADOW = "Shadow"  # Shadow plane only, ephemeral
    EPHEMERAL = "Ephemeral"  # Both planes, ephemeral
    DUAL = "Dual"  # Both planes, conditionally persistent


class DivergencePolicyType(Enum):
    """Divergence handling policies."""

    REQUIRE_IDENTICAL = "require_identical"
    ALLOW_EPSILON = "allow_epsilon"
    LOG_DIVERGENCE = "log_divergence"
    QUARANTINE_ON_DIVERGE = "quarantine_on_diverge"
    FAIL_PRIMARY = "fail_primary"


class MutationBoundaryType(Enum):
    """Mutation boundary specifications."""

    READ_ONLY = "read_only"
    EPHEMERAL_ONLY = "ephemeral_only"
    SHADOW_STATE_ONLY = "shadow_state_only"
    VALIDATED_CANONICAL = "validated_canonical"
    EMERGENCY_OVERRIDE = "emergency_override"


# ============================================================================
# Base AST Node
# ============================================================================


@dataclass
class ASTNode:
    """Base class for all AST nodes."""

    line: int = 0
    column: int = 0


# ============================================================================
# Type Annotations
# ============================================================================


@dataclass
class TypeAnnotation(ASTNode):
    """Type annotation with optional plane qualifier."""

    name: str = ""
    qualifier: PlaneQualifier | None = None
    type_params: list["TypeAnnotation"] = field(default_factory=list)

    def __str__(self) -> str:
        if self.qualifier:
            base = f"{self.qualifier.value}<{self.name}>"
        else:
            base = self.name

        if self.type_params:
            params = ", ".join(str(t) for t in self.type_params)
            return f"{base}<{params}>"

        return base


# ============================================================================
# Expressions
# ============================================================================


@dataclass
class Expression(ASTNode):
    """Base class for expressions."""

    pass


@dataclass
class Literal(Expression):
    """Literal value (integer, float, string, boolean)."""

    value: Any = None


@dataclass
class Identifier(Expression):
    """Variable or function identifier."""

    name: str = ""


@dataclass
class BinaryOp(Expression):
    """Binary operation (e.g., a + b)."""

    operator: str = ""
    left: Expression = None
    right: Expression = None


@dataclass
class UnaryOp(Expression):
    """Unary operation (e.g., !x, -x)."""

    operator: str = ""
    operand: Expression = None


@dataclass
class FunctionCall(Expression):
    """Function call."""

    function: str = ""
    arguments: list[Expression] = field(default_factory=list)


@dataclass
class MemberAccess(Expression):
    """Member access (e.g., obj.field)."""

    object: Expression = None
    member: str = ""


# ============================================================================
# Statements
# ============================================================================


@dataclass
class Statement(ASTNode):
    """Base class for statements."""

    pass


@dataclass
class VariableDeclaration(Statement):
    """Variable declaration (drink x = value)."""

    name: str = ""
    type_annotation: TypeAnnotation | None = None
    initializer: Expression | None = None


@dataclass
class Assignment(Statement):
    """Assignment statement."""

    target: str = ""
    value: Expression = None


@dataclass
class ReturnStatement(Statement):
    """Return statement."""

    value: Expression | None = None


@dataclass
class IfStatement(Statement):
    """If-else control flow statement."""

    condition: Expression = None
    then_branch: list[Statement] = field(default_factory=list)
    else_branch: list[Statement] | None = None


@dataclass
class OutputStatement(Statement):
    """Output statement (pour x)."""

    expression: Expression = None


@dataclass
class InputStatement(Statement):
    """Input statement (sip x)."""

    variable: str = ""


@dataclass
class ExpressionStatement(Statement):
    """Expression as statement."""

    expression: Expression = None


@dataclass
class Block(Statement):
    """Block of statements."""

    statements: list[Statement] = field(default_factory=list)


# ============================================================================
# Shadow Thirst Specific Constructs
# ============================================================================


@dataclass
class PrimaryBlock(ASTNode):
    """Primary execution block."""

    statements: list[Statement] = field(default_factory=list)


@dataclass
class ShadowBlock(ASTNode):
    """Shadow execution block."""

    statements: list[Statement] = field(default_factory=list)


@dataclass
class ActivationPredicate(ASTNode):
    """Activation predicate (activate_if condition)."""

    condition: Expression = None


@dataclass
class InvariantClause(ASTNode):
    """Invariant clause (invariant { ... })."""

    conditions: list[Expression] = field(default_factory=list)


@dataclass
class DivergencePolicy(ASTNode):
    """Divergence policy specification."""

    policy_type: DivergencePolicyType = None
    epsilon: float | None = None  # For allow_epsilon policy


@dataclass
class MutationBoundary(ASTNode):
    """Mutation boundary specification."""

    boundary_type: MutationBoundaryType = None


# ============================================================================
# Function Definition
# ============================================================================


@dataclass
class Parameter(ASTNode):
    """Function parameter."""

    name: str = ""
    type_annotation: TypeAnnotation | None = None


@dataclass
class FunctionDefinition(ASTNode):
    """
    Complete function definition with dual-plane execution.

    Example:
        fn transfer(a: Account, b: Account, amt: Money) -> Result {
            primary {
                debit(a, amt)
                credit(b, amt)
                return Ok
            }

            shadow {
                projected = simulate_transfer(a, b, amt)
                return projected
            }

            activate_if is_high_stakes(amt)

            invariant {
                shadow.balance_projection >= 0 &&
                projected_consistent(primary, shadow)
            }

            divergence allow_epsilon(0.01)
            mutation read_only
        }
    """

    name: str = ""
    parameters: list[Parameter] = field(default_factory=list)
    return_type: TypeAnnotation | None = None

    # Execution blocks
    primary_block: PrimaryBlock | None = None
    shadow_block: ShadowBlock | None = None

    # Shadow configuration
    activation_predicate: ActivationPredicate | None = None
    invariants: InvariantClause | None = None
    divergence_policy: DivergencePolicy | None = None
    mutation_boundary: MutationBoundary | None = None


# ============================================================================
# Program Root
# ============================================================================


@dataclass
class Program(ASTNode):
    """Root program node containing all top-level declarations."""

    functions: list[FunctionDefinition] = field(default_factory=list)
    statements: list[Statement] = field(default_factory=list)


# ============================================================================
# Visitor Pattern Support
# ============================================================================


class ASTVisitor:
    """
    Base class for AST visitors.

    Implement visit_<NodeType> methods to process specific node types.
    """

    def visit(self, node: ASTNode) -> Any:
        """
        Visit an AST node.

        Args:
            node: AST node to visit

        Returns:
            Result of visiting the node
        """
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode) -> Any:
        """
        Default visitor for nodes without specific handlers.

        Args:
            node: AST node

        Returns:
            None
        """
        pass


__all__ = [
    # Enums
    "PlaneQualifier",
    "DivergencePolicyType",
    "MutationBoundaryType",
    # Base
    "ASTNode",
    "ASTVisitor",
    # Types
    "TypeAnnotation",
    # Expressions
    "Expression",
    "Literal",
    "Identifier",
    "BinaryOp",
    "UnaryOp",
    "FunctionCall",
    "MemberAccess",
    # Statements
    "Statement",
    "VariableDeclaration",
    "Assignment",
    "ReturnStatement",
    "OutputStatement",
    "InputStatement",
    "ExpressionStatement",
    "IfStatement",
    "Block",
    # Shadow Thirst constructs
    "PrimaryBlock",
    "ShadowBlock",
    "ActivationPredicate",
    "InvariantClause",
    "DivergencePolicy",
    "MutationBoundary",
    # Function
    "Parameter",
    "FunctionDefinition",
    # Program
    "Program",
]
