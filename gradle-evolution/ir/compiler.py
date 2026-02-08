"""
God Tier Intent Compiler - YAML to IR Compilation Engine

Compiles YAML intent specifications into deterministic intermediate representation
with semantic analysis, type inference, optimization, and dependency resolution.

Features:
- YAML parsing with schema validation
- Semantic analysis and error checking
- Type inference and propagation
- Dependency resolution
- Dead code elimination
- Constant folding
- Error reporting with line numbers
- Integration with governance policies
"""

from __future__ import annotations

import logging
import os
from typing import Any

import yaml

from .ir_schema import (
    IRGraph,
    IRNode,
    IROpcode,
    IRType,
    IRTypeInfo,
)

logger = logging.getLogger(__name__)


class CompilationError(Exception):
    """Compilation error with line number context"""
    def __init__(self, message: str, line_number: int | None = None, source_file: str | None = None):
        self.message = message
        self.line_number = line_number
        self.source_file = source_file
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format error message with context"""
        parts = []
        if self.source_file:
            parts.append(f"{self.source_file}")
        if self.line_number:
            parts.append(f"line {self.line_number}")
        if parts:
            return f"{':'.join(parts)}: {self.message}"
        return self.message


class IntentCompiler:
    """Compiles YAML intent specifications into IR"""

    def __init__(self, governance_enabled: bool = True):
        """
        Initialize compiler
        
        Args:
            governance_enabled: Whether to enforce governance policies
        """
        self.governance_enabled = governance_enabled
        self.graph = IRGraph()
        self.node_counter = 0
        self.errors: list[CompilationError] = []
        self.warnings: list[str] = []
        self.symbol_table: dict[str, IRNode] = {}
        self.type_env: dict[str, IRTypeInfo] = {}
        self.current_file: str | None = None

    def compile(self, yaml_content: str, source_file: str | None = None) -> IRGraph:
        """
        Compile YAML intent to IR graph
        
        Args:
            yaml_content: YAML intent specification
            source_file: Optional source file path for error reporting
        
        Returns:
            Compiled IR graph
        
        Raises:
            CompilationError: If compilation fails
        """
        self.current_file = source_file
        self.errors.clear()
        self.warnings.clear()
        self.graph = IRGraph()
        self.node_counter = 0
        self.symbol_table.clear()
        self.type_env.clear()

        try:
            # Parse YAML
            intent_spec = yaml.safe_load(yaml_content)
            if not isinstance(intent_spec, dict):
                raise CompilationError("Intent must be a YAML dictionary", source_file=source_file)

            # Validate schema
            self._validate_intent_schema(intent_spec)

            # Extract metadata
            self.graph.metadata = {
                "intent": intent_spec.get("intent", "unknown"),
                "version": intent_spec.get("version", "1.0"),
                "source_file": source_file,
                "compiler_version": "1.0.0"
            }

            # Compile steps
            if "steps" in intent_spec:
                entry_node = self._compile_steps(intent_spec["steps"])
                self.graph.entry_node = entry_node.id

            # Semantic analysis
            self._semantic_analysis()

            # Type inference
            self._type_inference()

            # Dependency resolution
            self._resolve_dependencies()

            # Basic optimizations
            self._optimize_basic()

            if self.errors:
                error_msg = "\n".join(str(e) for e in self.errors)
                raise CompilationError(f"Compilation failed with {len(self.errors)} errors:\n{error_msg}")

            logger.info(f"Compiled {len(self.graph.nodes)} IR nodes from {source_file or 'inline'}")
            return self.graph

        except yaml.YAMLError as e:
            raise CompilationError(f"YAML parsing error: {e}", source_file=source_file)
        except Exception as e:
            if isinstance(e, CompilationError):
                raise
            raise CompilationError(f"Compilation error: {e}", source_file=source_file)

    def _validate_intent_schema(self, intent: dict[str, Any]) -> None:
        """Validate intent specification schema"""
        required_fields = ["intent", "version"]
        for field in required_fields:
            if field not in intent:
                raise CompilationError(f"Missing required field: {field}")

        if "steps" in intent:
            if not isinstance(intent["steps"], list):
                raise CompilationError("'steps' must be a list")
            if not intent["steps"]:
                self.warnings.append("Intent has no steps")

    def _compile_steps(self, steps: list[dict[str, Any]]) -> IRNode:
        """Compile list of steps into IR sequence"""
        if not steps:
            return self._create_node(IROpcode.NOP)

        # Create sequence node
        sequence = self._create_node(IROpcode.SEQUENCE, attributes={"step_count": len(steps)})
        prev_node = sequence

        for idx, step in enumerate(steps):
            step_node = self._compile_step(step, line_number=idx + 1)
            self.graph.add_edge(prev_node.id, step_node.id)
            prev_node = step_node

        return sequence

    def _compile_step(self, step: dict[str, Any], line_number: int | None = None) -> IRNode:
        """Compile single step into IR node(s)"""
        if "action" not in step:
            raise CompilationError("Step missing 'action' field", line_number=line_number)

        action = step["action"]

        # Map action to opcode
        action_map = {
            "validate": IROpcode.VALIDATE_POLICY,
            "compile": IROpcode.COMPILE,
            "test": IROpcode.TEST,
            "package": IROpcode.PACKAGE,
            "deploy": IROpcode.DEPLOY,
            "exec": IROpcode.EXEC,
            "log": IROpcode.LOG,
            "checkpoint": IROpcode.CHECKPOINT,
        }

        opcode = action_map.get(action)
        if not opcode:
            raise CompilationError(f"Unknown action: {action}", line_number=line_number)

        # Create node with attributes
        attributes = {k: v for k, v in step.items() if k != "action"}
        node = self._create_node(opcode, attributes=attributes, line_number=line_number)

        # Add governance validation if enabled
        # These three policies are always injected for sensitive operations as they
        # form the core governance framework:
        # - non_maleficence: Ensure action doesn't cause harm
        # - transparency: Action must be auditable
        # - accountability: Action must be traceable to responsible party
        # Additional policies can be specified in YAML via explicit validate actions
        entry_node = node  # Default entry point
        if self.governance_enabled and opcode in {IROpcode.COMPILE, IROpcode.DEPLOY, IROpcode.EXEC}:
            validate_node = self._create_node(
                IROpcode.VALIDATE_POLICY,
                attributes={"policies": ["non_maleficence", "transparency", "accountability"]},
                line_number=line_number
            )
            self.graph.add_edge(validate_node.id, node.id)
            entry_node = validate_node  # Validation is now the entry point

        # Handle special cases
        if action == "validate" and "policies" in step:
            node.attributes["policies"] = step["policies"]
        elif action == "compile":
            node.type_info = IRTypeInfo(base_type=IRType.PATH)
        elif action == "test":
            node.type_info = IRTypeInfo(base_type=IRType.BOOL)

        return entry_node

    def _create_node(
        self,
        opcode: IROpcode,
        inputs: list[str] | None = None,
        operands: list[Any] | None = None,
        attributes: dict[str, Any] | None = None,
        line_number: int | None = None
    ) -> IRNode:
        """Create new IR node and add to graph"""
        node_id = f"n{self.node_counter}"
        self.node_counter += 1

        node = IRNode(
            id=node_id,
            opcode=opcode,
            inputs=inputs or [],
            operands=operands or [],
            attributes=attributes or {},
            line_number=line_number,
            source_file=self.current_file
        )

        self.graph.add_node(node)
        return node

    def _semantic_analysis(self) -> None:
        """Perform semantic analysis on IR graph"""
        logger.debug("Running semantic analysis")

        for node_id, node in self.graph.nodes.items():
            # Check policy validation nodes
            if node.opcode == IROpcode.VALIDATE_POLICY:
                if "policies" not in node.attributes:
                    self.errors.append(
                        CompilationError("Policy validation missing 'policies' attribute", node.line_number)
                    )
                else:
                    self._validate_policies(node.attributes["policies"], node.line_number)

            # Check compile nodes
            if node.opcode == IROpcode.COMPILE:
                if "source" not in node.attributes:
                    self.errors.append(
                        CompilationError("Compile action missing 'source' attribute", node.line_number)
                    )

            # Check test nodes
            if node.opcode == IROpcode.TEST:
                if "suite" not in node.attributes:
                    self.warnings.append(
                        f"Test action at line {node.line_number} has no 'suite' attribute"
                    )

            # Check loops for termination
            if node.opcode == IROpcode.LOOP:
                if "max_iterations" not in node.attributes:
                    self.warnings.append(
                        f"Loop at line {node.line_number} has no max_iterations - may not terminate"
                    )

    def _validate_policies(self, policies: list[str], line_number: int | None) -> None:
        """Validate policy names"""
        valid_policies = {
            "non_maleficence", "transparency", "accountability",
            "privacy", "fairness", "safety", "security"
        }

        for policy in policies:
            if policy not in valid_policies:
                self.warnings.append(
                    f"Unknown policy '{policy}' at line {line_number}"
                )

    def _type_inference(self) -> None:
        """Infer types for all nodes in topological order"""
        logger.debug("Running type inference")

        try:
            sorted_nodes = self.graph.topological_sort()
        except ValueError as e:
            self.errors.append(CompilationError(f"Cannot perform type inference: {e}"))
            return

        for node in sorted_nodes:
            if node.type_info:
                continue  # Already has type

            # Infer type based on opcode
            if node.opcode == IROpcode.CONST:
                node.type_info = self._infer_const_type(node)
            elif node.opcode == IROpcode.COMPILE:
                node.type_info = IRTypeInfo(base_type=IRType.PATH)
            elif node.opcode == IROpcode.TEST:
                node.type_info = IRTypeInfo(base_type=IRType.BOOL)
            elif node.opcode in {IROpcode.ADD, IROpcode.SUB, IROpcode.MUL, IROpcode.DIV}:
                node.type_info = self._infer_arithmetic_type(node)
            elif node.opcode == IROpcode.CMP:
                node.type_info = IRTypeInfo(base_type=IRType.BOOL)
            elif node.opcode == IROpcode.READ_FILE:
                node.type_info = IRTypeInfo(base_type=IRType.STRING)
            else:
                node.type_info = IRTypeInfo(base_type=IRType.VOID)

            # Store in type environment
            self.type_env[node.id] = node.type_info

    def _infer_const_type(self, node: IRNode) -> IRTypeInfo:
        """Infer type of constant value"""
        if not node.operands:
            return IRTypeInfo(base_type=IRType.VOID)

        value = node.operands[0]
        if isinstance(value, bool):
            return IRTypeInfo(base_type=IRType.BOOL)
        elif isinstance(value, int):
            return IRTypeInfo(base_type=IRType.INT)
        elif isinstance(value, float):
            return IRTypeInfo(base_type=IRType.FLOAT)
        elif isinstance(value, str):
            return IRTypeInfo(base_type=IRType.STRING)
        elif isinstance(value, list):
            return IRTypeInfo(base_type=IRType.LIST, element_type=IRType.ANY)
        elif isinstance(value, dict):
            return IRTypeInfo(base_type=IRType.DICT, key_type=IRType.STRING, value_type=IRType.ANY)
        else:
            return IRTypeInfo(base_type=IRType.ANY)

    def _infer_arithmetic_type(self, node: IRNode) -> IRTypeInfo:
        """Infer type of arithmetic operation"""
        if not node.inputs:
            return IRTypeInfo(base_type=IRType.INT)

        # Get types of inputs
        input_types = [self.type_env.get(inp_id) for inp_id in node.inputs]
        input_types = [t for t in input_types if t]

        if not input_types:
            return IRTypeInfo(base_type=IRType.INT)

        # If any input is float, result is float
        if any(t.base_type == IRType.FLOAT for t in input_types):
            return IRTypeInfo(base_type=IRType.FLOAT)

        return IRTypeInfo(base_type=IRType.INT)

    def _resolve_dependencies(self) -> None:
        """Resolve dependencies between nodes"""
        logger.debug("Resolving dependencies")

        # Build dependency map
        deps: dict[str, set[str]] = {}
        for node_id, node in self.graph.nodes.items():
            deps[node_id] = set(node.inputs)

        # Check for missing dependencies
        for node_id, dep_ids in deps.items():
            for dep_id in dep_ids:
                if dep_id not in self.graph.nodes:
                    self.errors.append(
                        CompilationError(f"Node {node_id} depends on non-existent node {dep_id}")
                    )

        # Topological sort to ensure valid execution order
        try:
            sorted_nodes = self.graph.topological_sort()
            self.graph.metadata["execution_order"] = [n.id for n in sorted_nodes]
        except ValueError as e:
            self.errors.append(CompilationError(f"Dependency resolution failed: {e}"))

    def _optimize_basic(self) -> None:
        """Run basic optimizations"""
        logger.debug("Running basic optimizations")

        # Dead code elimination
        self._eliminate_dead_code()

        # Constant folding
        self._fold_constants()

        # Remove NOP nodes
        self._remove_nops()

    def _eliminate_dead_code(self) -> None:
        """Remove unreachable nodes"""
        if not self.graph.entry_node:
            return

        # Mark reachable nodes
        reachable = set()
        queue = [self.graph.entry_node]

        while queue:
            node_id = queue.pop(0)
            if node_id in reachable:
                continue
            reachable.add(node_id)

            if node_id in self.graph.nodes:
                queue.extend(self.graph.nodes[node_id].outputs)

        # Remove unreachable nodes
        dead_nodes = set(self.graph.nodes.keys()) - reachable
        for node_id in dead_nodes:
            del self.graph.nodes[node_id]
            logger.debug(f"Eliminated dead code: {node_id}")

    def _fold_constants(self) -> None:
        """Fold constant expressions"""
        for node_id, node in list(self.graph.nodes.items()):
            if node.opcode not in {IROpcode.ADD, IROpcode.SUB, IROpcode.MUL, IROpcode.DIV}:
                continue

            # Check if all inputs are constants
            input_nodes = [self.graph.nodes[inp_id] for inp_id in node.inputs if inp_id in self.graph.nodes]
            if not all(n.opcode == IROpcode.CONST for n in input_nodes):
                continue

            # Compute constant value
            try:
                values = [n.operands[0] for n in input_nodes if n.operands]
                if len(values) != 2:
                    continue

                result = None
                if node.opcode == IROpcode.ADD:
                    result = values[0] + values[1]
                elif node.opcode == IROpcode.SUB:
                    result = values[0] - values[1]
                elif node.opcode == IROpcode.MUL:
                    result = values[0] * values[1]
                elif node.opcode == IROpcode.DIV:
                    if values[1] != 0:
                        result = values[0] / values[1]

                if result is not None:
                    # Replace with constant node
                    node.opcode = IROpcode.CONST
                    node.operands = [result]
                    node.inputs.clear()
                    logger.debug(f"Folded constant: {node_id} = {result}")
            except Exception as e:
                logger.warning(f"Constant folding failed for {node_id}: {e}")

    def _remove_nops(self) -> None:
        """Remove NOP nodes and reconnect edges"""
        nop_nodes = [nid for nid, node in self.graph.nodes.items() if node.opcode == IROpcode.NOP]

        for nop_id in nop_nodes:
            nop_node = self.graph.nodes[nop_id]

            # Reconnect inputs to outputs
            for input_id in nop_node.inputs:
                for output_id in nop_node.outputs:
                    if input_id in self.graph.nodes and output_id in self.graph.nodes:
                        self.graph.add_edge(input_id, output_id)

            # Remove NOP node
            del self.graph.nodes[nop_id]
            logger.debug(f"Removed NOP: {nop_id}")

    def compile_file(self, file_path: str) -> IRGraph:
        """Compile YAML file to IR graph"""
        if not os.path.exists(file_path):
            raise CompilationError(f"File not found: {file_path}")

        with open(file_path) as f:
            yaml_content = f.read()

        return self.compile(yaml_content, source_file=file_path)

    def get_compilation_report(self) -> dict[str, Any]:
        """Generate compilation report"""
        return {
            "nodes_compiled": len(self.graph.nodes),
            "errors": [str(e) for e in self.errors],
            "warnings": self.warnings,
            "entry_node": self.graph.entry_node,
            "metadata": self.graph.metadata
        }
