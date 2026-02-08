"""
God Tier IR Schema - Intermediate Representation Type System and Validation

Provides deterministic IR node structures, type system, dataflow analysis,
and control flow validation for provably correct intent execution.

Architecture:
- IRNode: Single operation in execution graph
- IRGraph: DAG of IR nodes with dataflow edges
- IRSchema: Validates IR structure and type correctness
- Type system: Rich type inference and checking
- Dataflow analysis: Tracks data dependencies and side effects
- Control flow: Validates execution order and termination
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class IRType(Enum):
    """IR type system for operations and data"""
    VOID = "void"
    BOOL = "bool"
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    PATH = "path"
    LIST = "list"
    DICT = "dict"
    ANY = "any"
    ERROR = "error"


class IROpcode(Enum):
    """IR operation codes"""
    # Control flow
    NOP = "nop"
    SEQUENCE = "sequence"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    BREAK = "break"
    CONTINUE = "continue"
    RETURN = "return"

    # Data operations
    LOAD = "load"
    STORE = "store"
    CONST = "const"
    COPY = "copy"

    # Computation
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"
    CMP = "cmp"

    # I/O operations
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    EXEC = "exec"
    HTTP_REQUEST = "http_request"

    # Intent-specific
    VALIDATE_POLICY = "validate_policy"
    COMPILE = "compile"
    TEST = "test"
    PACKAGE = "package"
    DEPLOY = "deploy"

    # System
    LOG = "log"
    METRIC = "metric"
    CHECKPOINT = "checkpoint"
    ROLLBACK = "rollback"


@dataclass
class IRTypeInfo:
    """Type information with constraints"""
    base_type: IRType
    element_type: IRType | None = None  # For lists
    key_type: IRType | None = None  # For dicts
    value_type: IRType | None = None  # For dicts
    nullable: bool = False
    constraints: dict[str, Any] = field(default_factory=dict)

    def is_compatible(self, other: IRTypeInfo) -> bool:
        """Check type compatibility for assignment/parameter passing"""
        if self.base_type == IRType.ANY or other.base_type == IRType.ANY:
            return True
        if self.base_type != other.base_type:
            return False
        if self.base_type == IRType.LIST:
            if self.element_type and other.element_type:
                return self.element_type == other.element_type or \
                       self.element_type == IRType.ANY or \
                       other.element_type == IRType.ANY
        if self.base_type == IRType.DICT:
            key_compat = not self.key_type or not other.key_type or \
                        self.key_type == other.key_type
            val_compat = not self.value_type or not other.value_type or \
                        self.value_type == other.value_type
            return key_compat and val_compat
        return True

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "base_type": self.base_type.value,
            "element_type": self.element_type.value if self.element_type else None,
            "key_type": self.key_type.value if self.key_type else None,
            "value_type": self.value_type.value if self.value_type else None,
            "nullable": self.nullable,
            "constraints": self.constraints
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IRTypeInfo:
        """Deserialize from dictionary"""
        return cls(
            base_type=IRType(data["base_type"]),
            element_type=IRType(data["element_type"]) if data.get("element_type") else None,
            key_type=IRType(data["key_type"]) if data.get("key_type") else None,
            value_type=IRType(data["value_type"]) if data.get("value_type") else None,
            nullable=data.get("nullable", False),
            constraints=data.get("constraints", {})
        )


@dataclass
class IRNode:
    """Single IR operation node in execution graph"""
    id: str
    opcode: IROpcode
    inputs: list[str] = field(default_factory=list)  # Input node IDs
    outputs: list[str] = field(default_factory=list)  # Output node IDs
    operands: list[Any] = field(default_factory=list)  # Immediate operands
    attributes: dict[str, Any] = field(default_factory=dict)
    type_info: IRTypeInfo | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    line_number: int | None = None
    source_file: str | None = None

    def compute_hash(self) -> str:
        """Compute deterministic hash for node identity"""
        content = json.dumps({
            "opcode": self.opcode.value,
            "inputs": sorted(self.inputs),
            "operands": self.operands,
            "attributes": sorted(self.attributes.items())
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def is_pure(self) -> bool:
        """Check if operation has no side effects"""
        pure_ops = {
            IROpcode.NOP, IROpcode.CONST, IROpcode.COPY,
            IROpcode.ADD, IROpcode.SUB, IROpcode.MUL, IROpcode.DIV,
            IROpcode.MOD, IROpcode.CMP, IROpcode.LOAD
        }
        return self.opcode in pure_ops

    def is_terminator(self) -> bool:
        """Check if this is a control flow terminator"""
        return self.opcode in {
            IROpcode.RETURN, IROpcode.BREAK, IROpcode.CONTINUE
        }

    def get_resource_cost(self) -> dict[str, float]:
        """Estimate resource costs for this operation"""
        costs = {
            "cpu": 0.0,
            "memory": 0.0,
            "io": 0.0,
            "network": 0.0
        }

        # High-cost operations
        if self.opcode in {IROpcode.COMPILE, IROpcode.TEST}:
            costs["cpu"] = 10.0
            costs["memory"] = 100.0
        elif self.opcode in {IROpcode.READ_FILE, IROpcode.WRITE_FILE}:
            costs["io"] = 5.0
        elif self.opcode == IROpcode.HTTP_REQUEST:
            costs["network"] = 5.0
            costs["io"] = 2.0
        elif self.opcode == IROpcode.EXEC:
            costs["cpu"] = 5.0
            costs["memory"] = 50.0
        else:
            costs["cpu"] = 0.1
            costs["memory"] = 1.0

        return costs

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "opcode": self.opcode.value,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "operands": self.operands,
            "attributes": self.attributes,
            "type_info": self.type_info.to_dict() if self.type_info else None,
            "metadata": self.metadata,
            "line_number": self.line_number,
            "source_file": self.source_file
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IRNode:
        """Deserialize from dictionary"""
        return cls(
            id=data["id"],
            opcode=IROpcode(data["opcode"]),
            inputs=data.get("inputs", []),
            outputs=data.get("outputs", []),
            operands=data.get("operands", []),
            attributes=data.get("attributes", {}),
            type_info=IRTypeInfo.from_dict(data["type_info"]) if data.get("type_info") else None,
            metadata=data.get("metadata", {}),
            line_number=data.get("line_number"),
            source_file=data.get("source_file")
        )


@dataclass
class IRGraph:
    """Directed acyclic graph of IR nodes"""
    nodes: dict[str, IRNode] = field(default_factory=dict)
    entry_node: str | None = None
    exit_nodes: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add_node(self, node: IRNode) -> None:
        """Add node to graph"""
        if node.id in self.nodes:
            raise ValueError(f"Node {node.id} already exists in graph")
        self.nodes[node.id] = node

        if self.entry_node is None:
            self.entry_node = node.id

    def add_edge(self, from_id: str, to_id: str) -> None:
        """Add directed edge between nodes"""
        if from_id not in self.nodes:
            raise ValueError(f"Source node {from_id} not in graph")
        if to_id not in self.nodes:
            raise ValueError(f"Target node {to_id} not in graph")

        if to_id not in self.nodes[from_id].outputs:
            self.nodes[from_id].outputs.append(to_id)
        if from_id not in self.nodes[to_id].inputs:
            self.nodes[to_id].inputs.append(from_id)

    def get_predecessors(self, node_id: str) -> list[IRNode]:
        """Get all predecessor nodes"""
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not in graph")
        return [self.nodes[pred_id] for pred_id in self.nodes[node_id].inputs]

    def get_successors(self, node_id: str) -> list[IRNode]:
        """Get all successor nodes"""
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not in graph")
        return [self.nodes[succ_id] for succ_id in self.nodes[node_id].outputs]

    def topological_sort(self) -> list[IRNode]:
        """Return nodes in topological order (valid execution order)"""
        in_degree = {node_id: len(node.inputs) for node_id, node in self.nodes.items()}
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node_id = queue.pop(0)
            result.append(self.nodes[node_id])

            for succ_id in self.nodes[node_id].outputs:
                in_degree[succ_id] -= 1
                if in_degree[succ_id] == 0:
                    queue.append(succ_id)

        if len(result) != len(self.nodes):
            raise ValueError("Graph contains cycles - cannot compute topological sort")

        return result

    def has_cycle(self) -> bool:
        """Check if graph contains cycles"""
        try:
            self.topological_sort()
            return False
        except ValueError:
            return True

    def get_dataflow_chains(self) -> list[list[str]]:
        """Extract dataflow dependency chains"""
        chains = []
        visited = set()

        def dfs(node_id: str, chain: list[str]) -> None:
            if node_id in visited:
                return
            visited.add(node_id)
            chain.append(node_id)

            successors = self.nodes[node_id].outputs
            if not successors:
                chains.append(chain.copy())
            else:
                for succ_id in successors:
                    dfs(succ_id, chain.copy())

        if self.entry_node:
            dfs(self.entry_node, [])

        return chains

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "nodes": {node_id: node.to_dict() for node_id, node in self.nodes.items()},
            "entry_node": self.entry_node,
            "exit_nodes": self.exit_nodes,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> IRGraph:
        """Deserialize from dictionary"""
        graph = cls(
            entry_node=data.get("entry_node"),
            exit_nodes=data.get("exit_nodes", []),
            metadata=data.get("metadata", {})
        )

        for node_id, node_data in data.get("nodes", {}).items():
            graph.nodes[node_id] = IRNode.from_dict(node_data)

        return graph


class IRSchema:
    """Validates IR graph structure and type correctness"""

    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate(self, graph: IRGraph) -> bool:
        """Validate entire IR graph"""
        self.errors.clear()
        self.warnings.clear()

        if not graph.nodes:
            self.errors.append("Graph is empty")
            return False

        if not graph.entry_node:
            self.errors.append("Graph has no entry node")
            return False

        if graph.entry_node not in graph.nodes:
            self.errors.append(f"Entry node {graph.entry_node} not in graph")
            return False

        # Validate each node
        for node_id, node in graph.nodes.items():
            self._validate_node(node, graph)

        # Check for cycles
        if graph.has_cycle():
            self.errors.append("Graph contains cycles")

        # Validate dataflow
        self._validate_dataflow(graph)

        # Type checking
        self._validate_types(graph)

        return len(self.errors) == 0

    def _validate_node(self, node: IRNode, graph: IRGraph) -> None:
        """Validate single node"""
        # Check input references
        for input_id in node.inputs:
            if input_id not in graph.nodes:
                self.errors.append(f"Node {node.id} references non-existent input {input_id}")

        # Check output references
        for output_id in node.outputs:
            if output_id not in graph.nodes:
                self.errors.append(f"Node {node.id} references non-existent output {output_id}")

        # Validate opcode-specific constraints
        if node.opcode == IROpcode.CONDITIONAL:
            if len(node.inputs) < 1:
                self.errors.append(f"Conditional node {node.id} requires at least 1 input")
        elif node.opcode == IROpcode.LOOP:
            if "max_iterations" not in node.attributes:
                self.warnings.append(f"Loop node {node.id} has no max_iterations bound")

    def _validate_dataflow(self, graph: IRGraph) -> None:
        """Validate dataflow dependencies"""
        for node_id, node in graph.nodes.items():
            # Check that all inputs are produced before use
            for input_id in node.inputs:
                input_node = graph.nodes[input_id]
                if node_id not in input_node.outputs:
                    self.errors.append(
                        f"Dataflow inconsistency: {node_id} uses {input_id} but not in outputs"
                    )

    def _validate_types(self, graph: IRGraph) -> None:
        """Validate type consistency across dataflow"""
        for node_id, node in graph.nodes.items():
            if not node.type_info:
                continue

            for input_id in node.inputs:
                input_node = graph.nodes[input_id]
                if not input_node.type_info:
                    continue

                if not node.type_info.is_compatible(input_node.type_info):
                    self.errors.append(
                        f"Type mismatch: {node_id} expects {node.type_info.base_type.value} "
                        f"but {input_id} produces {input_node.type_info.base_type.value}"
                    )
