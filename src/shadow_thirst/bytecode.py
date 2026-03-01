"""
Shadow Thirst Bytecode Specification and Generator

Defines bytecode format for dual-plane execution and generates bytecode from IR.

Bytecode Format:
- Each instruction is a tuple: (opcode_byte, plane_tag, operands...)
- Plane tags: 0x01=Primary, 0x02=Shadow, 0x03=Invariant
- Support for constitutional hooks and audit sealing

STATUS: PRODUCTION
VERSION: 1.0.0
"""

import logging
import struct
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any

from shadow_thirst.ir import (
    ExecutionPlane,
    IRBasicBlock,
    IRFunction,
    IRInstruction,
    IROpcode,
    IRProgram,
)

logger = logging.getLogger(__name__)


class BytecodeOpcode(IntEnum):
    """Bytecode instruction opcodes (as integers for binary encoding)."""

    # Stack operations
    PUSH = 0x01
    POP = 0x02
    DUP = 0x03
    SWAP = 0x04

    # Memory operations
    LOAD_VAR = 0x10
    STORE_VAR = 0x11
    LOAD_CONST = 0x12
    LOAD_PARAM = 0x13

    # Arithmetic
    ADD = 0x20
    SUB = 0x21
    MUL = 0x22
    DIV = 0x23
    NEG = 0x24

    # Logical
    AND = 0x30
    OR = 0x31
    NOT = 0x32

    # Comparison
    EQ = 0x40
    NE = 0x41
    LT = 0x42
    LE = 0x43
    GT = 0x44
    GE = 0x45

    # Control flow
    JUMP = 0x50
    JUMP_IF_FALSE = 0x51
    RETURN = 0x52
    CALL = 0x53

    # I/O
    OUTPUT = 0x60
    INPUT = 0x61

    # Shadow operations
    ACTIVATE_SHADOW = 0x70
    CHECK_INVARIANT = 0x71
    RECORD_DIVERGENCE = 0x72
    COMMIT_PRIMARY = 0x73
    QUARANTINE = 0x74

    # Constitutional operations
    VALIDATE_AND_COMMIT = 0x80
    SEAL_AUDIT = 0x81
    INVOKE_TARL = 0x82

    # Sentinel
    NOP = 0x00
    HALT = 0xFF


class PlaneTag(IntEnum):
    """Plane tags for bytecode instructions."""

    PRIMARY = 0x01
    SHADOW = 0x02
    INVARIANT = 0x03


@dataclass
class BytecodeInstruction:
    """Single bytecode instruction."""

    opcode: BytecodeOpcode
    plane: PlaneTag
    operands: list[Any] = field(default_factory=list)

    def encode(self) -> bytes:
        """
        Encode instruction to bytes.

        Format: [opcode:1][plane:1][operand_count:1][operands...]

        Returns:
            Encoded bytes
        """
        result = bytearray()

        # Opcode and plane
        result.append(self.opcode)
        result.append(self.plane)

        # Operand count
        result.append(len(self.operands))

        # Operands (simple encoding)
        for operand in self.operands:
            if isinstance(operand, int):
                # Encode as 4-byte signed integer
                result.extend(struct.pack(">i", operand))
            elif isinstance(operand, float):
                # Encode as 8-byte double
                result.extend(struct.pack(">d", operand))
            elif isinstance(operand, str):
                # Encode string as length + UTF-8 bytes
                encoded_str = operand.encode("utf-8")
                result.extend(struct.pack(">H", len(encoded_str)))
                result.extend(encoded_str)
            elif isinstance(operand, bool):
                result.append(1 if operand else 0)
            elif operand is None:
                result.append(0)  # Null marker
            else:
                logger.warning("Unsupported operand type: %s", type(operand))

        return bytes(result)

    @staticmethod
    def decode(data: bytes, offset: int = 0) -> tuple["BytecodeInstruction", int]:
        """
        Decode instruction from bytes.

        Args:
            data: Bytecode data
            offset: Starting offset

        Returns:
            Tuple of (instruction, new_offset)
        """
        opcode = BytecodeOpcode(data[offset])
        plane = PlaneTag(data[offset + 1])
        operand_count = data[offset + 2]

        offset += 3
        operands = []

        for _ in range(operand_count):
            # Simplified decoding - would need type tags in real implementation
            operand, offset = BytecodeInstruction._decode_operand(data, offset)
            operands.append(operand)

        return BytecodeInstruction(opcode, plane, operands), offset

    @staticmethod
    def _decode_operand(data: bytes, offset: int) -> tuple[Any, int]:
        """Decode a single operand (simplified)."""
        # In a real implementation, would use type tags
        # For now, assume strings
        str_len = struct.unpack(">H", data[offset : offset + 2])[0]
        offset += 2
        value = data[offset : offset + str_len].decode("utf-8")
        offset += str_len
        return value, offset


@dataclass
class BytecodeFunction:
    """Bytecode for a single function."""

    name: str
    parameter_count: int
    local_count: int

    # Bytecode by plane
    primary_bytecode: list[BytecodeInstruction] = field(default_factory=list)
    shadow_bytecode: list[BytecodeInstruction] = field(default_factory=list)
    invariant_bytecode: list[BytecodeInstruction] = field(default_factory=list)

    # Metadata
    has_shadow: bool = False
    has_invariants: bool = False
    divergence_policy: str | None = None
    mutation_boundary: str | None = None

    def encode(self) -> bytes:
        """
        Encode function to bytes.

        Returns:
            Encoded bytes
        """
        result = bytearray()

        # Function name
        name_bytes = self.name.encode("utf-8")
        result.extend(struct.pack(">H", len(name_bytes)))
        result.extend(name_bytes)

        # Metadata
        result.extend(struct.pack(">BB", self.parameter_count, self.local_count))
        result.append(1 if self.has_shadow else 0)
        result.append(1 if self.has_invariants else 0)

        # Encode bytecode for each plane
        for bytecode_list in [
            self.primary_bytecode,
            self.shadow_bytecode,
            self.invariant_bytecode,
        ]:
            result.extend(struct.pack(">H", len(bytecode_list)))
            for instruction in bytecode_list:
                result.extend(instruction.encode())

        return bytes(result)


@dataclass
class BytecodeProgram:
    """Complete bytecode program."""

    functions: list[BytecodeFunction] = field(default_factory=list)
    constants: list[Any] = field(default_factory=list)

    # Global configuration
    enable_shadow_execution: bool = True
    enable_audit_sealing: bool = True

    def encode(self) -> bytes:
        """
        Encode entire program to bytes.

        Returns:
            Encoded bytecode
        """
        result = bytearray()

        # Magic number and version
        result.extend(b"SHAD")  # Magic: Shadow Thirst bytecode
        result.extend(struct.pack(">H", 0x0100))  # Version 1.0

        # Flags
        flags = 0
        if self.enable_shadow_execution:
            flags |= 0x01
        if self.enable_audit_sealing:
            flags |= 0x02
        result.append(flags)

        # Constants table
        result.extend(struct.pack(">H", len(self.constants)))
        for const in self.constants:
            # Simple constant encoding
            if isinstance(const, int):
                result.append(0x01)  # Type tag: integer
                result.extend(struct.pack(">i", const))
            elif isinstance(const, float):
                result.append(0x02)  # Type tag: float
                result.extend(struct.pack(">d", const))
            elif isinstance(const, str):
                result.append(0x03)  # Type tag: string
                encoded_str = const.encode("utf-8")
                result.extend(struct.pack(">H", len(encoded_str)))
                result.extend(encoded_str)

        # Functions
        result.extend(struct.pack(">H", len(self.functions)))
        for function in self.functions:
            result.extend(function.encode())

        return bytes(result)


class BytecodeGenerator:
    """
    Generate bytecode from IR.

    Converts dual-plane IR to executable bytecode format.
    """

    # Opcode mapping from IR to bytecode
    OPCODE_MAP = {
        IROpcode.PUSH: BytecodeOpcode.PUSH,
        IROpcode.POP: BytecodeOpcode.POP,
        IROpcode.DUP: BytecodeOpcode.DUP,
        IROpcode.SWAP: BytecodeOpcode.SWAP,
        IROpcode.LOAD_VAR: BytecodeOpcode.LOAD_VAR,
        IROpcode.STORE_VAR: BytecodeOpcode.STORE_VAR,
        IROpcode.LOAD_CONST: BytecodeOpcode.LOAD_CONST,
        IROpcode.LOAD_PARAM: BytecodeOpcode.LOAD_PARAM,
        IROpcode.ADD: BytecodeOpcode.ADD,
        IROpcode.SUB: BytecodeOpcode.SUB,
        IROpcode.MUL: BytecodeOpcode.MUL,
        IROpcode.DIV: BytecodeOpcode.DIV,
        IROpcode.NEG: BytecodeOpcode.NEG,
        IROpcode.AND: BytecodeOpcode.AND,
        IROpcode.OR: BytecodeOpcode.OR,
        IROpcode.NOT: BytecodeOpcode.NOT,
        IROpcode.EQ: BytecodeOpcode.EQ,
        IROpcode.NE: BytecodeOpcode.NE,
        IROpcode.LT: BytecodeOpcode.LT,
        IROpcode.LE: BytecodeOpcode.LE,
        IROpcode.GT: BytecodeOpcode.GT,
        IROpcode.GE: BytecodeOpcode.GE,
        IROpcode.JUMP: BytecodeOpcode.JUMP,
        IROpcode.JUMP_IF_FALSE: BytecodeOpcode.JUMP_IF_FALSE,
        IROpcode.RETURN: BytecodeOpcode.RETURN,
        IROpcode.CALL: BytecodeOpcode.CALL,
        IROpcode.OUTPUT: BytecodeOpcode.OUTPUT,
        IROpcode.INPUT: BytecodeOpcode.INPUT,
        IROpcode.ACTIVATE_SHADOW: BytecodeOpcode.ACTIVATE_SHADOW,
        IROpcode.CHECK_INVARIANT: BytecodeOpcode.CHECK_INVARIANT,
        IROpcode.RECORD_DIVERGENCE: BytecodeOpcode.RECORD_DIVERGENCE,
        IROpcode.COMMIT_PRIMARY: BytecodeOpcode.COMMIT_PRIMARY,
        IROpcode.QUARANTINE: BytecodeOpcode.QUARANTINE,
        IROpcode.VALIDATE_AND_COMMIT: BytecodeOpcode.VALIDATE_AND_COMMIT,
        IROpcode.SEAL_AUDIT: BytecodeOpcode.SEAL_AUDIT,
        IROpcode.INVOKE_TARL: BytecodeOpcode.INVOKE_TARL,
    }

    PLANE_MAP = {
        ExecutionPlane.PRIMARY: PlaneTag.PRIMARY,
        ExecutionPlane.SHADOW: PlaneTag.SHADOW,
        ExecutionPlane.INVARIANT: PlaneTag.INVARIANT,
    }

    def __init__(self):
        """Initialize bytecode generator."""
        self.constants = []
        self.constant_map = {}

    def generate(self, ir_program: IRProgram) -> BytecodeProgram:
        """
        Generate bytecode from IR program.

        Args:
            ir_program: IR program

        Returns:
            Bytecode program
        """
        logger.info("Generating bytecode from IR")

        bytecode_program = BytecodeProgram(
            enable_shadow_execution=ir_program.enable_shadow_execution,
            enable_audit_sealing=ir_program.enable_audit_sealing,
        )

        # Generate bytecode for each function
        for ir_function in ir_program.functions:
            bytecode_function = self._generate_function(ir_function)
            bytecode_program.functions.append(bytecode_function)

        # Set constants
        bytecode_program.constants = self.constants

        logger.info(
            "Bytecode generation complete: %d functions",
            len(bytecode_program.functions),
        )
        return bytecode_program

    def _generate_function(self, ir_function: IRFunction) -> BytecodeFunction:
        """Generate bytecode for a function."""
        bytecode_function = BytecodeFunction(
            name=ir_function.name,
            parameter_count=len(ir_function.parameters),
            local_count=len(ir_function.variables),
            has_shadow=ir_function.has_shadow,
            has_invariants=ir_function.has_invariants,
            divergence_policy=ir_function.divergence_policy,
            mutation_boundary=ir_function.mutation_boundary,
        )

        # Generate bytecode for primary blocks
        for block in ir_function.primary_blocks:
            bytecode_function.primary_bytecode.extend(self._generate_block(block))

        # Generate bytecode for shadow blocks
        for block in ir_function.shadow_blocks:
            bytecode_function.shadow_bytecode.extend(self._generate_block(block))

        # Generate bytecode for invariant blocks
        for block in ir_function.invariant_blocks:
            bytecode_function.invariant_bytecode.extend(self._generate_block(block))

        return bytecode_function

    def _generate_block(self, block: IRBasicBlock) -> list[BytecodeInstruction]:
        """Generate bytecode for a basic block."""
        bytecode = []

        for ir_instruction in block.instructions:
            bytecode_instruction = self._generate_instruction(ir_instruction)
            if bytecode_instruction:
                bytecode.append(bytecode_instruction)

        return bytecode

    def _generate_instruction(
        self, ir_instruction: IRInstruction
    ) -> BytecodeInstruction | None:
        """Generate bytecode for an IR instruction."""
        # Map IR opcode to bytecode opcode
        bytecode_opcode = self.OPCODE_MAP.get(ir_instruction.opcode)
        if not bytecode_opcode:
            logger.warning(
                "No bytecode mapping for IR opcode: %s", ir_instruction.opcode
            )
            return None

        # Map plane
        plane = self.PLANE_MAP.get(ir_instruction.plane, PlaneTag.PRIMARY)

        # Convert operands
        operands = ir_instruction.operands.copy()

        return BytecodeInstruction(
            opcode=bytecode_opcode,
            plane=plane,
            operands=operands,
        )

    def _add_constant(self, value: Any) -> int:
        """Add constant to constant pool and return index."""
        if value in self.constant_map:
            return self.constant_map[value]

        index = len(self.constants)
        self.constants.append(value)
        self.constant_map[value] = index
        return index


def generate_bytecode(ir_program: IRProgram) -> BytecodeProgram:
    """
    Generate bytecode from IR program.

    Args:
        ir_program: IR program

    Returns:
        Bytecode program
    """
    generator = BytecodeGenerator()
    return generator.generate(ir_program)


__all__ = [
    # Opcodes and tags
    "BytecodeOpcode",
    "PlaneTag",
    # Structures
    "BytecodeInstruction",
    "BytecodeFunction",
    "BytecodeProgram",
    # Generator
    "BytecodeGenerator",
    "generate_bytecode",
]
