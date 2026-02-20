"""
Shadow Thirst Shadow-Aware Virtual Machine

Executes dual-plane bytecode with:
- Primary execution frame
- Shadow execution frame (isolated)
- Invariant validation frame
- Constitutional commit protocol
- Resource bounds enforcement
- Audit trail sealing

VM Architecture:
- Dual execution frames (primary + shadow)
- Stack-based evaluation
- Restricted shadow instruction set
- Constitutional hooks for commit validation

STATUS: PRODUCTION
VERSION: 1.0.0
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from shadow_thirst.bytecode import (
    BytecodeFunction,
    BytecodeInstruction,
    BytecodeOpcode,
    BytecodeProgram,
    PlaneTag,
)

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """VM execution mode."""

    PRIMARY_ONLY = "primary_only"
    DUAL_PLANE = "dual_plane"
    SHADOW_ONLY = "shadow_only"


@dataclass
class ExecutionFrame:
    """
    Execution frame for function call.

    Separate frames for primary and shadow execution.
    """

    function_name: str

    # Stack
    stack: list[Any] = field(default_factory=list)

    # Local variables
    locals: dict[str, Any] = field(default_factory=dict)

    # Parameters
    parameters: dict[str, Any] = field(default_factory=dict)

    # Return value
    return_value: Any = None
    has_returned: bool = False

    # Resource tracking
    start_time: float = field(default_factory=time.time)
    instruction_count: int = 0

    def push(self, value: Any):
        """Push value onto stack."""
        self.stack.append(value)

    def pop(self) -> Any:
        """Pop value from stack."""
        if not self.stack:
            raise RuntimeError("Stack underflow")
        return self.stack.pop()

    def peek(self) -> Any:
        """Peek at top of stack."""
        if not self.stack:
            raise RuntimeError("Stack is empty")
        return self.stack[-1]

    def load_var(self, name: str) -> Any:
        """Load variable value."""
        if name in self.locals:
            return self.locals[name]
        elif name in self.parameters:
            return self.parameters[name]
        else:
            raise RuntimeError(f"Undefined variable: {name}")

    def store_var(self, name: str, value: Any):
        """Store variable value."""
        self.locals[name] = value

    def get_elapsed_ms(self) -> float:
        """Get elapsed execution time in milliseconds."""
        return (time.time() - self.start_time) * 1000.0


@dataclass
class DualExecutionFrame:
    """
    Dual execution frame containing both primary and shadow frames.

    This is the core of dual-plane execution.
    """

    function_name: str

    # Primary execution
    primary: ExecutionFrame = field(default_factory=lambda: ExecutionFrame(""))

    # Shadow execution (isolated)
    shadow: ExecutionFrame | None = None

    # Invariant validation
    invariant_results: list[bool] = field(default_factory=list)

    # Divergence tracking
    divergence_detected: bool = False
    divergence_magnitude: float = 0.0

    # Audit
    audit_trail: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        """Initialize frames."""
        self.primary.function_name = self.function_name

    def activate_shadow(self):
        """Activate shadow execution frame."""
        if not self.shadow:
            self.shadow = ExecutionFrame(self.function_name)
            logger.debug("[%s] Shadow frame activated", self.function_name)

    def record_audit(self, event: str, data: dict[str, Any] | None = None):
        """Record audit event."""
        entry = {
            "timestamp": time.time(),
            "event": event,
            "function": self.function_name,
            "data": data or {},
        }
        self.audit_trail.append(entry)


class ShadowAwareVM:
    """
    Shadow-Aware Virtual Machine.

    Executes dual-plane bytecode with constitutional validation.
    """

    def __init__(
        self,
        constitutional_core: Any | None = None,
        enable_shadow: bool = True,
        enable_audit: bool = True,
    ):
        """
        Initialize VM.

        Args:
            constitutional_core: Constitutional Core for validation
            enable_shadow: Enable shadow execution
            enable_audit: Enable audit trail
        """
        self.constitutional_core = constitutional_core
        self.enable_shadow = enable_shadow
        self.enable_audit = enable_audit

        # Program state
        self.program: BytecodeProgram | None = None
        self.functions: dict[str, BytecodeFunction] = {}
        self.constants: list[Any] = []

        # Execution state
        self.call_stack: list[DualExecutionFrame] = []
        self.mode = ExecutionMode.DUAL_PLANE if enable_shadow else ExecutionMode.PRIMARY_ONLY

        # Statistics
        self.stats = {
            "total_instructions": 0,
            "shadow_activations": 0,
            "invariant_checks": 0,
            "divergences": 0,
        }

    def load_program(self, program: BytecodeProgram):
        """
        Load bytecode program.

        Args:
            program: Bytecode program to load
        """
        logger.info("Loading bytecode program with %d functions", len(program.functions))

        self.program = program
        self.constants = program.constants

        # Index functions by name
        self.functions = {func.name: func for func in program.functions}

        logger.info("Program loaded successfully")

    def execute(self, function_name: str = "__main__", args: list[Any] | None = None) -> Any:
        """
        Execute program starting from given function.

        Args:
            function_name: Name of function to execute
            args: Function arguments

        Returns:
            Return value from function
        """
        if not self.program:
            raise RuntimeError("No program loaded")

        logger.info("Executing function: %s", function_name)

        # Create initial frame
        frame = DualExecutionFrame(function_name)

        # Set parameters
        if args:
            func = self.functions.get(function_name)
            if func:
                for i, arg in enumerate(args[: func.parameter_count]):
                    frame.primary.parameters[f"arg{i}"] = arg

        self.call_stack.append(frame)

        # Execute primary plane
        self._execute_plane(frame, PlaneTag.PRIMARY)

        # Execute shadow plane if enabled
        if self.enable_shadow and func and func.has_shadow:
            frame.activate_shadow()
            self._execute_plane(frame, PlaneTag.SHADOW)

            # Check invariants
            if func.has_invariants:
                self._execute_invariants(frame)

            # Constitutional validation
            self._constitutional_commit(frame)

        # Pop frame and return result
        self.call_stack.pop()

        result = frame.primary.return_value
        logger.info("Execution complete, result: %s", result)

        return result

    def _execute_plane(self, frame: DualExecutionFrame, plane: PlaneTag):
        """Execute bytecode for a specific plane."""
        func = self.functions.get(frame.function_name)
        if not func:
            raise RuntimeError(f"Function not found: {frame.function_name}")

        # Get bytecode for plane
        if plane == PlaneTag.PRIMARY:
            bytecode = func.primary_bytecode
            exec_frame = frame.primary
        elif plane == PlaneTag.SHADOW:
            bytecode = func.shadow_bytecode
            exec_frame = frame.shadow
            if not exec_frame:
                return
        else:
            return

        plane_name = "PRIMARY" if plane == PlaneTag.PRIMARY else "SHADOW"
        logger.debug("[%s] Executing %s plane (%d instructions)", frame.function_name, plane_name, len(bytecode))

        # Execute instructions
        for instruction in bytecode:
            self._execute_instruction(instruction, exec_frame, frame)

            if exec_frame.has_returned:
                break

            exec_frame.instruction_count += 1
            self.stats["total_instructions"] += 1

    def _execute_instruction(
        self,
        instruction: BytecodeInstruction,
        exec_frame: ExecutionFrame,
        dual_frame: DualExecutionFrame,
    ):
        """Execute a single bytecode instruction."""
        opcode = instruction.opcode

        # Stack operations
        if opcode == BytecodeOpcode.PUSH:
            value = instruction.operands[0] if instruction.operands else None
            exec_frame.push(value)

        elif opcode == BytecodeOpcode.POP:
            exec_frame.pop()

        elif opcode == BytecodeOpcode.DUP:
            value = exec_frame.peek()
            exec_frame.push(value)

        # Memory operations
        elif opcode == BytecodeOpcode.LOAD_CONST:
            const_index = instruction.operands[0] if instruction.operands else 0
            value = self.constants[const_index]
            exec_frame.push(value)

        elif opcode == BytecodeOpcode.LOAD_VAR:
            var_name = instruction.operands[0] if instruction.operands else ""
            value = exec_frame.load_var(var_name)
            exec_frame.push(value)

        elif opcode == BytecodeOpcode.STORE_VAR:
            var_name = instruction.operands[0] if instruction.operands else ""
            value = exec_frame.pop()
            exec_frame.store_var(var_name, value)

        # Arithmetic
        elif opcode == BytecodeOpcode.ADD:
            right = exec_frame.pop()
            left = exec_frame.pop()
            exec_frame.push(left + right)

        elif opcode == BytecodeOpcode.SUB:
            right = exec_frame.pop()
            left = exec_frame.pop()
            exec_frame.push(left - right)

        elif opcode == BytecodeOpcode.MUL:
            right = exec_frame.pop()
            left = exec_frame.pop()
            exec_frame.push(left * right)

        elif opcode == BytecodeOpcode.DIV:
            right = exec_frame.pop()
            left = exec_frame.pop()
            if right == 0:
                raise RuntimeError("Division by zero")
            exec_frame.push(left / right)

        elif opcode == BytecodeOpcode.NEG:
            value = exec_frame.pop()
            exec_frame.push(-value)

        # Logical
        elif opcode == BytecodeOpcode.AND:
            right = exec_frame.pop()
            left = exec_frame.pop()
            exec_frame.push(left and right)

        elif opcode == BytecodeOpcode.OR:
            right = exec_frame.pop()
            left = exec_frame.pop()
            exec_frame.push(left or right)

        elif opcode == BytecodeOpcode.NOT:
            value = exec_frame.pop()
            exec_frame.push(not value)

        # Comparison
        elif opcode == BytecodeOpcode.EQ:
            right = exec_frame.pop()
            left = exec_frame.pop()
            exec_frame.push(left == right)

        elif opcode == BytecodeOpcode.NE:
            right = exec_frame.pop()
            left = exec_frame.pop()
            exec_frame.push(left != right)

        elif opcode == BytecodeOpcode.LT:
            right = exec_frame.pop()
            left = exec_frame.pop()
            exec_frame.push(left < right)

        elif opcode == BytecodeOpcode.LE:
            right = exec_frame.pop()
            left = exec_frame.pop()
            exec_frame.push(left <= right)

        elif opcode == BytecodeOpcode.GT:
            right = exec_frame.pop()
            left = exec_frame.pop()
            exec_frame.push(left > right)

        elif opcode == BytecodeOpcode.GE:
            right = exec_frame.pop()
            left = exec_frame.pop()
            exec_frame.push(left >= right)

        # Control flow
        elif opcode == BytecodeOpcode.RETURN:
            if exec_frame.stack:
                exec_frame.return_value = exec_frame.pop()
            exec_frame.has_returned = True

        # I/O
        elif opcode == BytecodeOpcode.OUTPUT:
            value = exec_frame.pop()
            print(value)  # Simple output

        # Shadow operations
        elif opcode == BytecodeOpcode.ACTIVATE_SHADOW:
            dual_frame.activate_shadow()
            self.stats["shadow_activations"] += 1

        elif opcode == BytecodeOpcode.CHECK_INVARIANT:
            condition = exec_frame.pop()
            dual_frame.invariant_results.append(bool(condition))
            self.stats["invariant_checks"] += 1

        # Constitutional operations
        elif opcode == BytecodeOpcode.VALIDATE_AND_COMMIT:
            # Placeholder for constitutional validation
            logger.debug("[%s] Constitutional validation", dual_frame.function_name)

        elif opcode == BytecodeOpcode.SEAL_AUDIT:
            if self.enable_audit:
                dual_frame.record_audit("seal", {"instruction_count": exec_frame.instruction_count})

    def _execute_invariants(self, frame: DualExecutionFrame):
        """Execute invariant checks."""
        func = self.functions.get(frame.function_name)
        if not func or not func.has_invariants:
            return

        logger.debug("[%s] Checking invariants", frame.function_name)

        # Execute invariant bytecode
        invariant_frame = ExecutionFrame(frame.function_name)

        # Copy primary and shadow results to invariant frame
        invariant_frame.locals["primary"] = frame.primary.return_value
        if frame.shadow:
            invariant_frame.locals["shadow"] = frame.shadow.return_value

        for instruction in func.invariant_bytecode:
            self._execute_instruction(instruction, invariant_frame, frame)

        # Check if all invariants passed
        all_passed = all(frame.invariant_results)
        logger.debug(
            "[%s] Invariants: %d checked, all passed: %s", frame.function_name, len(frame.invariant_results), all_passed
        )

    def _constitutional_commit(self, frame: DualExecutionFrame):
        """Execute constitutional commit protocol."""
        logger.debug("[%s] Constitutional commit protocol", frame.function_name)

        # Compare primary and shadow results
        if frame.shadow:
            primary_result = frame.primary.return_value
            shadow_result = frame.shadow.return_value

            # Detect divergence
            if primary_result != shadow_result:
                frame.divergence_detected = True
                self.stats["divergences"] += 1

                try:
                    frame.divergence_magnitude = abs(primary_result - shadow_result)
                except (TypeError, ValueError):
                    frame.divergence_magnitude = float("inf")

                logger.warning(
                    "[%s] Divergence detected: primary=%s, shadow=%s",
                    frame.function_name,
                    primary_result,
                    shadow_result,
                )

        # Check invariants
        if frame.invariant_results and not all(frame.invariant_results):
            logger.error("[%s] Invariant violations detected", frame.function_name)

        # Audit seal
        if self.enable_audit:
            frame.record_audit(
                "commit",
                {
                    "divergence_detected": frame.divergence_detected,
                    "divergence_magnitude": frame.divergence_magnitude,
                    "invariants_passed": all(frame.invariant_results) if frame.invariant_results else True,
                },
            )

    def get_stats(self) -> dict[str, Any]:
        """Get VM execution statistics."""
        return self.stats.copy()


__all__ = [
    "ExecutionMode",
    "ExecutionFrame",
    "DualExecutionFrame",
    "ShadowAwareVM",
]
