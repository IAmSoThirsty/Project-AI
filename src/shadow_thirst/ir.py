"""
Shadow Thirst Dual-Plane Intermediate Representation (IR)

Defines IR for dual-plane execution with:
- Plane-tagged instructions
- Primary/shadow/invariant execution contexts
- Constitutional hooks for commit validation
- Resource bounds and isolation metadata

IR Structure:
- Primary plane instructions: Execute canonical operations
- Shadow plane instructions: Execute validation/simulation
- Invariant instructions: Validate correctness conditions
- Constitutional hooks: Invariant validation and commit gates

STATUS: PRODUCTION
VERSION: 1.0.0
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class ExecutionPlane(Enum):
    """Execution plane identifier."""

    PRIMARY = "P"  # Primary canonical plane
    SHADOW = "Sh"  # Shadow validation plane
    INVARIANT = "Inv"  # Invariant checking plane


class IROpcode(Enum):
    """IR instruction opcodes."""

    # Stack operations
    PUSH = auto()  # Push value onto stack
    POP = auto()  # Pop value from stack
    DUP = auto()  # Duplicate top of stack
    SWAP = auto()  # Swap top two stack values

    # Memory operations
    LOAD_VAR = auto()  # Load variable
    STORE_VAR = auto()  # Store variable
    LOAD_CONST = auto()  # Load constant
    LOAD_PARAM = auto()  # Load parameter

    # Arithmetic operations
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    NEG = auto()  # Unary negation

    # Logical operations
    AND = auto()
    OR = auto()
    NOT = auto()

    # Comparison operations
    EQ = auto()  # Equal
    NE = auto()  # Not equal
    LT = auto()  # Less than
    LE = auto()  # Less than or equal
    GT = auto()  # Greater than
    GE = auto()  # Greater than or equal

    # Control flow
    JUMP = auto()  # Unconditional jump
    JUMP_IF_FALSE = auto()  # Conditional jump
    RETURN = auto()  # Return from function
    CALL = auto()  # Function call

    # I/O operations
    OUTPUT = auto()  # Output (pour)
    INPUT = auto()  # Input (sip)

    # Shadow-specific operations
    ACTIVATE_SHADOW = auto()  # Activate shadow execution
    CHECK_INVARIANT = auto()  # Check invariant condition
    RECORD_DIVERGENCE = auto()  # Record divergence metric
    COMMIT_PRIMARY = auto()  # Commit primary result
    QUARANTINE = auto()  # Quarantine result

    # Constitutional operations
    VALIDATE_AND_COMMIT = auto()  # Constitutional validation + commit
    SEAL_AUDIT = auto()  # Cryptographically seal audit
    INVOKE_TARL = auto()  # Invoke T.A.R.L. policy check


class PlaneQualifierIR(Enum):
    """Memory plane qualifiers in IR."""

    CANONICAL = "canonical"
    SHADOW = "shadow"
    EPHEMERAL = "ephemeral"
    DUAL = "dual"


@dataclass
class IRInstruction:
    """
    Single IR instruction with plane metadata.

    Each instruction is tagged with its execution plane and includes
    metadata for resource tracking and audit.
    """

    opcode: IROpcode
    plane: ExecutionPlane
    operands: list[Any] = field(default_factory=list)

    # Metadata
    line: int = 0
    column: int = 0
    resource_bound_ms: float | None = None  # CPU time bound
    memory_bound_mb: float | None = None  # Memory bound

    def __str__(self) -> str:
        operands_str = ", ".join(str(op) for op in self.operands)
        return f"[{self.plane.value}] {self.opcode.name} {operands_str}"


@dataclass
class IRBasicBlock:
    """
    Basic block in IR - sequence of instructions without jumps.

    Basic blocks form the control flow graph of the function.
    """

    block_id: int
    plane: ExecutionPlane
    instructions: list[IRInstruction] = field(default_factory=list)
    predecessors: list[int] = field(default_factory=list)
    successors: list[int] = field(default_factory=list)


@dataclass
class IRVariable:
    """Variable in IR with plane qualifier."""

    name: str
    qualifier: PlaneQualifierIR
    type_name: str | None = None
    is_parameter: bool = False


@dataclass
class IRFunction:
    """
    Complete IR function with dual-plane execution.

    Contains separate instruction sequences for primary, shadow, and
    invariant execution, along with activation and divergence metadata.
    """

    name: str
    parameters: list[IRVariable] = field(default_factory=list)
    return_type: str | None = None

    # Basic blocks by plane
    primary_blocks: list[IRBasicBlock] = field(default_factory=list)
    shadow_blocks: list[IRBasicBlock] = field(default_factory=list)
    invariant_blocks: list[IRBasicBlock] = field(default_factory=list)

    # Local variables
    variables: list[IRVariable] = field(default_factory=list)

    # Shadow configuration
    has_shadow: bool = False
    has_invariants: bool = False

    # Activation predicate IR
    activation_predicate_blocks: list[IRBasicBlock] = field(default_factory=list)

    # Divergence policy
    divergence_policy: str | None = None
    divergence_epsilon: float | None = None

    # Mutation boundary
    mutation_boundary: str | None = None

    # Resource bounds
    shadow_cpu_quota_ms: float = 1000.0
    shadow_memory_quota_mb: float = 256.0

    def get_all_blocks(self) -> list[IRBasicBlock]:
        """Get all basic blocks across all planes."""
        return self.primary_blocks + self.shadow_blocks + self.invariant_blocks + self.activation_predicate_blocks


@dataclass
class IRProgram:
    """
    Complete IR program.

    Contains all functions with dual-plane execution metadata.
    """

    functions: list[IRFunction] = field(default_factory=list)
    constants: dict[str, Any] = field(default_factory=dict)

    # Global configuration
    enable_shadow_execution: bool = True
    enable_audit_sealing: bool = True
    enable_constitutional_validation: bool = True

    def add_function(self, function: IRFunction):
        """Add function to program."""
        self.functions.append(function)

    def get_function(self, name: str) -> IRFunction | None:
        """Get function by name."""
        for func in self.functions:
            if func.name == name:
                return func
        return None


# ============================================================================
# IR Builder Helper Classes
# ============================================================================


class IRBuilder:
    """
    Helper class for building IR.

    Provides convenient methods for constructing IR instructions and blocks.
    """

    def __init__(self):
        """Initialize IR builder."""
        self.current_function: IRFunction | None = None
        self.current_block: IRBasicBlock | None = None
        self.current_plane: ExecutionPlane = ExecutionPlane.PRIMARY
        self.block_counter = 0
        self.temp_counter = 0

    def new_function(self, name: str, return_type: str | None = None) -> IRFunction:
        """Create new function."""
        function = IRFunction(name=name, return_type=return_type)
        self.current_function = function
        return function

    def new_block(self, plane: ExecutionPlane) -> IRBasicBlock:
        """Create new basic block."""
        block = IRBasicBlock(block_id=self.block_counter, plane=plane)
        self.block_counter += 1
        self.current_block = block
        return block

    def emit(
        self, opcode: IROpcode, *operands: Any, plane: ExecutionPlane | None = None, line: int = 0, column: int = 0
    ) -> IRInstruction:
        """
        Emit an instruction.

        Args:
            opcode: Instruction opcode
            *operands: Instruction operands
            plane: Execution plane (defaults to current plane)
            line: Source line number
            column: Source column number

        Returns:
            Emitted instruction
        """
        if plane is None:
            plane = self.current_plane

        instruction = IRInstruction(
            opcode=opcode,
            plane=plane,
            operands=list(operands),
            line=line,
            column=column,
        )

        if self.current_block:
            self.current_block.instructions.append(instruction)

        return instruction

    def set_plane(self, plane: ExecutionPlane):
        """Set current execution plane."""
        self.current_plane = plane

    def new_temp(self) -> str:
        """Generate new temporary variable name."""
        temp_name = f"$t{self.temp_counter}"
        self.temp_counter += 1
        return temp_name

    def add_variable(
        self, name: str, qualifier: PlaneQualifierIR, type_name: str | None = None, is_parameter: bool = False
    ) -> IRVariable:
        """Add variable to current function."""
        var = IRVariable(
            name=name,
            qualifier=qualifier,
            type_name=type_name,
            is_parameter=is_parameter,
        )

        if self.current_function:
            if is_parameter:
                self.current_function.parameters.append(var)
            else:
                self.current_function.variables.append(var)

        return var


# ============================================================================
# IR Optimization Passes
# ============================================================================


class IROptimizer:
    """
    IR optimization passes.

    Performs optimizations on IR while preserving dual-plane semantics.
    """

    @staticmethod
    def dead_code_elimination(function: IRFunction):
        """
        Remove dead code (unused instructions).

        Args:
            function: IR function to optimize
        """
        # Simple dead code elimination within basic blocks
        for block in function.get_all_blocks():
            live_instructions = []
            for instruction in block.instructions:
                # Keep all instructions that have side effects
                if IROptimizer._has_side_effects(instruction.opcode):
                    live_instructions.append(instruction)
                # Keep all constitutional and shadow operations
                elif instruction.opcode in (
                    IROpcode.ACTIVATE_SHADOW,
                    IROpcode.CHECK_INVARIANT,
                    IROpcode.VALIDATE_AND_COMMIT,
                    IROpcode.SEAL_AUDIT,
                ):
                    live_instructions.append(instruction)
                else:
                    # For now, keep all instructions (conservative)
                    live_instructions.append(instruction)

            block.instructions = live_instructions

    @staticmethod
    def _has_side_effects(opcode: IROpcode) -> bool:
        """Check if opcode has side effects."""
        side_effect_opcodes = {
            IROpcode.STORE_VAR,
            IROpcode.OUTPUT,
            IROpcode.INPUT,
            IROpcode.CALL,
            IROpcode.RETURN,
            IROpcode.COMMIT_PRIMARY,
            IROpcode.QUARANTINE,
        }
        return opcode in side_effect_opcodes

    @staticmethod
    def constant_folding(function: IRFunction):
        """
        Fold constant expressions.

        Args:
            function: IR function to optimize
        """
        # Placeholder for constant folding
        # Would analyze and pre-compute constant arithmetic
        pass


# ============================================================================
# IR Analysis
# ============================================================================


class IRAnalyzer:
    """
    IR analysis utilities.

    Provides analysis passes for validation and optimization.
    """

    @staticmethod
    def analyze_plane_isolation(function: IRFunction) -> tuple[bool, str]:
        """
        Analyze plane isolation - ensure shadow never mutates canonical state.

        Args:
            function: IR function to analyze

        Returns:
            Tuple of (is_isolated, reason)
        """
        # Check shadow blocks for canonical mutations
        for block in function.shadow_blocks:
            for instruction in block.instructions:
                # Shadow should not store to canonical variables
                if instruction.opcode == IROpcode.STORE_VAR:
                    var_name = instruction.operands[0] if instruction.operands else None
                    if var_name:
                        var = IRAnalyzer._find_variable(function, var_name)
                        if var and var.qualifier == PlaneQualifierIR.CANONICAL:
                            return False, f"Shadow mutates canonical variable: {var_name}"

        return True, "Plane isolation verified"

    @staticmethod
    def _find_variable(function: IRFunction, name: str) -> IRVariable | None:
        """Find variable by name."""
        for var in function.variables + function.parameters:
            if var.name == name:
                return var
        return None

    @staticmethod
    def estimate_resource_bounds(function: IRFunction) -> dict[str, float]:
        """
        Estimate resource bounds for function.

        Args:
            function: IR function to analyze

        Returns:
            Dict with estimated bounds
        """
        # Simple instruction counting heuristic
        primary_instructions = sum(len(block.instructions) for block in function.primary_blocks)
        shadow_instructions = sum(len(block.instructions) for block in function.shadow_blocks)

        # Estimate: ~1ms per 100 instructions
        estimated_primary_ms = primary_instructions / 100.0
        estimated_shadow_ms = shadow_instructions / 100.0

        return {
            "primary_cpu_ms": estimated_primary_ms,
            "shadow_cpu_ms": estimated_shadow_ms,
            "primary_instructions": primary_instructions,
            "shadow_instructions": shadow_instructions,
        }


__all__ = [
    # Enums
    "ExecutionPlane",
    "IROpcode",
    "PlaneQualifierIR",
    # Data structures
    "IRInstruction",
    "IRBasicBlock",
    "IRVariable",
    "IRFunction",
    "IRProgram",
    # Builders
    "IRBuilder",
    # Optimization
    "IROptimizer",
    # Analysis
    "IRAnalyzer",
]
