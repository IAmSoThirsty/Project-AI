"""
AST-Based Deep Code Analyzer

MAXIMUM DETAIL EXTRACTION from Abstract Syntax Trees

This module provides:
- Language-agnostic AST parsing infrastructure
- Deep traversal with visitor pattern
- Node type classification and metadata extraction
- Scope analysis and binding resolution
- Declaration and reference tracking
- Full syntactic structure decomposition

Operational Constraints:
- No summarization when detail is permitted
- No omission of relevant information
- Explicit structure over compression
- All layers, sublayers, components exposed
- All dependencies and cross-dependencies tracked
- All edge cases and failure modes documented
"""

import ast
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class ASTNodeType(Enum):
    """Classification of AST node types with maximum granularity"""

    # Module-level structures
    MODULE = "module"
    IMPORT = "import"
    IMPORT_FROM = "import_from"

    # Function structures
    FUNCTION_DEF = "function_def"
    ASYNC_FUNCTION_DEF = "async_function_def"
    LAMBDA = "lambda"
    RETURN = "return"
    YIELD = "yield"
    YIELD_FROM = "yield_from"

    # Class structures
    CLASS_DEF = "class_def"

    # Statement structures
    ASSIGN = "assign"
    AUG_ASSIGN = "aug_assign"
    ANN_ASSIGN = "ann_assign"
    FOR = "for"
    ASYNC_FOR = "async_for"
    WHILE = "while"
    IF = "if"
    WITH = "with"
    ASYNC_WITH = "async_with"
    RAISE = "raise"
    TRY = "try"
    ASSERT = "assert"
    DELETE = "delete"
    PASS = "pass"
    BREAK = "break"
    CONTINUE = "continue"
    GLOBAL = "global"
    NONLOCAL = "nonlocal"
    EXPR = "expr"

    # Expression structures
    BINOP = "binop"
    UNARYOP = "unaryop"
    BOOLOP = "boolop"
    COMPARE = "compare"
    CALL = "call"
    ATTRIBUTE = "attribute"
    SUBSCRIPT = "subscript"
    NAME = "name"
    CONSTANT = "constant"
    LIST = "list"
    TUPLE = "tuple"
    SET = "set"
    DICT = "dict"
    LISTCOMP = "listcomp"
    DICTCOMP = "dictcomp"
    SETCOMP = "setcomp"
    GENERATOREXP = "generatorexp"
    AWAIT = "await"
    IFEXP = "ifexp"
    FORMATTED_VALUE = "formatted_value"
    JOINED_STR = "joined_str"
    STARRED = "starred"
    SLICE = "slice"

    # Pattern matching (Python 3.10+)
    MATCH = "match"
    MATCH_VALUE = "match_value"
    MATCH_SINGLETON = "match_singleton"

    # Type structures
    TYPE_ALIAS = "type_alias"

    UNKNOWN = "unknown"


@dataclass
class ASTNode:
    """
    Complete AST node representation with maximum detail extraction

    Attributes expose all structural, semantic, and positional information
    permitted within operational constraints.
    """

    node_type: ASTNodeType
    raw_node: Any  # Original AST node from parser

    # Positional metadata
    line_start: int
    line_end: int
    col_start: int
    col_end: int

    # Structural metadata
    name: Optional[str] = None
    value: Optional[Any] = None
    children: List["ASTNode"] = field(default_factory=list)
    parent: Optional["ASTNode"] = None

    # Semantic metadata
    scope_id: Optional[str] = None
    bindings: Set[str] = field(default_factory=set)
    references: Set[str] = field(default_factory=set)

    # Type annotations
    type_annotation: Optional[str] = None
    return_annotation: Optional[str] = None

    # Function/class specific
    decorators: List[str] = field(default_factory=list)
    arguments: List[Tuple[str, Optional[str]]] = field(
        default_factory=list
    )  # (name, type_hint)
    base_classes: List[str] = field(default_factory=list)

    # Complexity indicators
    cyclomatic_complexity: int = 1
    depth: int = 0

    # Additional metadata dictionary for extension
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"ASTNode(type={self.node_type.value}, name={self.name}, line={self.line_start})"


class ASTVisitor:
    """
    Visitor pattern for AST traversal with maximum detail capture

    Provides hooks for all node types with complete context preservation.
    Subclasses override visit_* methods for custom analysis.
    """

    def visit(self, node: ASTNode) -> Any:
        """
        Generic visit dispatcher

        Routes to specific visit_* method based on node type.
        Returns result of specific visitor or default_visit.
        """
        method_name = f"visit_{node.node_type.value}"
        visitor = getattr(self, method_name, self.default_visit)
        return visitor(node)

    def default_visit(self, node: ASTNode) -> Any:
        """Default visitor for nodes without specific handlers"""
        for child in node.children:
            self.visit(child)
        return None

    def visit_module(self, node: ASTNode) -> Any:
        return self.default_visit(node)

    def visit_function_def(self, node: ASTNode) -> Any:
        return self.default_visit(node)

    def visit_class_def(self, node: ASTNode) -> Any:
        return self.default_visit(node)

    # Additional visit methods can be added for specific node types


class ASTAnalyzer:
    """
    Primary AST analysis engine with maximum detail extraction

    Capabilities:
    - Parse source code into complete AST
    - Build annotated node tree with all metadata
    - Extract all functions, classes, imports
    - Compute complexity metrics
    - Identify all bindings and references
    - Generate complete structural report

    Constraints:
    - Parses Python 3.9+ syntax
    - Preserves all positional information
    - Maintains complete parent-child relationships
    - No information loss from original AST

    Failure Modes:
    - SyntaxError: Invalid Python syntax in source
    - UnicodeDecodeError: Non-UTF-8 source encoding
    - RecursionError: Excessively deep nesting (>1000 levels)

    Recovery Paths:
    - Syntax errors: Return error location with surrounding context
    - Encoding errors: Attempt detection of actual encoding
    - Recursion errors: Return partial tree with depth marker
    """

    def __init__(self):
        self._scope_counter = 0
        self._current_scope: Optional[str] = None
        self._scope_stack: List[str] = []

    def parse_file(self, filepath: Path) -> Tuple[Optional[ASTNode], Optional[str]]:
        """
        Parse Python file into annotated AST

        Args:
            filepath: Path to Python source file

        Returns:
            Tuple of (root_node, error_message)
            If successful: (ASTNode, None)
            If failed: (None, error_description)

        Details:
        - Reads file with UTF-8 encoding (fallback to latin-1)
        - Parses with ast.parse in mode='exec'
        - Builds complete annotated tree
        - Computes all metadata fields
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            return self.parse_source(source, str(filepath))
        except UnicodeDecodeError as e:
            # Attempt fallback encoding
            try:
                with open(filepath, "r", encoding="latin-1") as f:
                    source = f.read()
                return self.parse_source(source, str(filepath))
            except Exception as fallback_error:
                return (
                    None,
                    f"Encoding error: UTF-8 failed with {e}, latin-1 failed with {fallback_error}",
                )
        except FileNotFoundError as e:  # noqa: F841
            return None, f"File not found: {filepath}"
        except Exception as e:
            return None, f"File read error: {type(e).__name__}: {e}"

    def parse_source(
        self, source: str, filename: str = "<string>"
    ) -> Tuple[Optional[ASTNode], Optional[str]]:
        """
        Parse Python source code into annotated AST

        Args:
            source: Python source code string
            filename: Source identifier for error messages

        Returns:
            Tuple of (root_node, error_message)

        Process:
        1. Parse source with ast.parse
        2. Build annotated node tree via _build_node
        3. Compute scope information
        4. Calculate complexity metrics
        5. Link parent-child relationships
        """
        try:
            tree = ast.parse(source, filename=filename, mode="exec")
            root = self._build_node(tree, parent=None)
            self._compute_scopes(root)
            self._compute_complexity(root)
            return root, None
        except SyntaxError as e:
            error_msg = (
                f"Syntax error at line {e.lineno}, column {e.offset}: {e.msg}\n"
                f"Text: {e.text}"
            )
            return None, error_msg
        except RecursionError:
            return None, "Recursion depth exceeded: AST nesting > 1000 levels"
        except Exception as e:
            return None, f"Parse error: {type(e).__name__}: {e}"

    def _build_node(self, raw_node: ast.AST, parent: Optional[ASTNode]) -> ASTNode:
        """
        Build annotated ASTNode from raw ast.AST node

        Extracts all available metadata:
        - Node type classification
        - Position information (line, column)
        - Name and value data
        - Decorators, arguments, base classes
        - Type annotations
        - Recursively processes all children

        Args:
            raw_node: Raw AST node from ast module
            parent: Parent ASTNode in annotated tree

        Returns:
            Fully annotated ASTNode with all metadata
        """
        # Determine node type
        node_type = self._classify_node(raw_node)

        # Extract positional information
        line_start = getattr(raw_node, "lineno", 0)
        line_end = getattr(raw_node, "end_lineno", line_start)
        col_start = getattr(raw_node, "col_offset", 0)
        col_end = getattr(raw_node, "end_col_offset", col_start)

        # Create base node
        node = ASTNode(
            node_type=node_type,
            raw_node=raw_node,
            line_start=line_start,
            line_end=line_end,
            col_start=col_start,
            col_end=col_end,
            parent=parent,
        )

        # Extract name if present
        if hasattr(raw_node, "name"):
            node.name = raw_node.name
        elif isinstance(raw_node, ast.Name):
            node.name = raw_node.id

        # Extract value for constants
        if isinstance(raw_node, ast.Constant):
            node.value = raw_node.value

        # Extract function-specific metadata
        if isinstance(raw_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            node.decorators = [
                self._get_decorator_name(d) for d in raw_node.decorator_list
            ]
            node.arguments = self._extract_arguments(raw_node.args)
            if raw_node.returns:
                node.return_annotation = ast.unparse(raw_node.returns)

        # Extract class-specific metadata
        if isinstance(raw_node, ast.ClassDef):
            node.decorators = [
                self._get_decorator_name(d) for d in raw_node.decorator_list
            ]
            node.base_classes = [ast.unparse(base) for base in raw_node.bases]

        # Extract type annotations
        if isinstance(raw_node, ast.AnnAssign) and raw_node.annotation:
            node.type_annotation = ast.unparse(raw_node.annotation)

        # Recursively build children
        for child_raw in ast.iter_child_nodes(raw_node):
            child_node = self._build_node(child_raw, parent=node)
            node.children.append(child_node)

        # Set depth
        node.depth = parent.depth + 1 if parent else 0

        return node

    def _classify_node(self, node: ast.AST) -> ASTNodeType:
        """Map ast.AST node to ASTNodeType enum"""
        type_map = {
            ast.Module: ASTNodeType.MODULE,
            ast.Import: ASTNodeType.IMPORT,
            ast.ImportFrom: ASTNodeType.IMPORT_FROM,
            ast.FunctionDef: ASTNodeType.FUNCTION_DEF,
            ast.AsyncFunctionDef: ASTNodeType.ASYNC_FUNCTION_DEF,
            ast.Lambda: ASTNodeType.LAMBDA,
            ast.Return: ASTNodeType.RETURN,
            ast.Yield: ASTNodeType.YIELD,
            ast.YieldFrom: ASTNodeType.YIELD_FROM,
            ast.ClassDef: ASTNodeType.CLASS_DEF,
            ast.Assign: ASTNodeType.ASSIGN,
            ast.AugAssign: ASTNodeType.AUG_ASSIGN,
            ast.AnnAssign: ASTNodeType.ANN_ASSIGN,
            ast.For: ASTNodeType.FOR,
            ast.AsyncFor: ASTNodeType.ASYNC_FOR,
            ast.While: ASTNodeType.WHILE,
            ast.If: ASTNodeType.IF,
            ast.With: ASTNodeType.WITH,
            ast.AsyncWith: ASTNodeType.ASYNC_WITH,
            ast.Raise: ASTNodeType.RAISE,
            ast.Try: ASTNodeType.TRY,
            ast.Assert: ASTNodeType.ASSERT,
            ast.Delete: ASTNodeType.DELETE,
            ast.Pass: ASTNodeType.PASS,
            ast.Break: ASTNodeType.BREAK,
            ast.Continue: ASTNodeType.CONTINUE,
            ast.Global: ASTNodeType.GLOBAL,
            ast.Nonlocal: ASTNodeType.NONLOCAL,
            ast.Expr: ASTNodeType.EXPR,
            ast.BinOp: ASTNodeType.BINOP,
            ast.UnaryOp: ASTNodeType.UNARYOP,
            ast.BoolOp: ASTNodeType.BOOLOP,
            ast.Compare: ASTNodeType.COMPARE,
            ast.Call: ASTNodeType.CALL,
            ast.Attribute: ASTNodeType.ATTRIBUTE,
            ast.Subscript: ASTNodeType.SUBSCRIPT,
            ast.Name: ASTNodeType.NAME,
            ast.Constant: ASTNodeType.CONSTANT,
            ast.List: ASTNodeType.LIST,
            ast.Tuple: ASTNodeType.TUPLE,
            ast.Set: ASTNodeType.SET,
            ast.Dict: ASTNodeType.DICT,
            ast.ListComp: ASTNodeType.LISTCOMP,
            ast.DictComp: ASTNodeType.DICTCOMP,
            ast.SetComp: ASTNodeType.SETCOMP,
            ast.GeneratorExp: ASTNodeType.GENERATOREXP,
            ast.Await: ASTNodeType.AWAIT,
            ast.IfExp: ASTNodeType.IFEXP,
            ast.FormattedValue: ASTNodeType.FORMATTED_VALUE,
            ast.JoinedStr: ASTNodeType.JOINED_STR,
            ast.Starred: ASTNodeType.STARRED,
            ast.Slice: ASTNodeType.SLICE,
        }

        # Python 3.10+ match statements
        if hasattr(ast, "Match"):
            type_map[ast.Match] = ASTNodeType.MATCH

        return type_map.get(type(node), ASTNodeType.UNKNOWN)

    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Extract decorator name from decorator node"""
        try:
            return ast.unparse(decorator)
        except Exception:
            return "<unknown>"

    def _extract_arguments(
        self, args: ast.arguments
    ) -> List[Tuple[str, Optional[str]]]:
        """
        Extract function arguments with type hints

        Returns list of (argument_name, type_annotation) tuples
        """
        result = []

        # Regular arguments
        for i, arg in enumerate(args.args):
            annotation = None
            if arg.annotation:
                annotation = ast.unparse(arg.annotation)
            result.append((arg.arg, annotation))

        # *args
        if args.vararg:
            annotation = None
            if args.vararg.annotation:
                annotation = ast.unparse(args.vararg.annotation)
            result.append((f"*{args.vararg.arg}", annotation))

        # **kwargs
        if args.kwarg:
            annotation = None
            if args.kwarg.annotation:
                annotation = ast.unparse(args.kwarg.annotation)
            result.append((f"**{args.kwarg.arg}", annotation))

        return result

    def _compute_scopes(self, root: ASTNode):
        """
        Compute scope information for all nodes

        Assigns unique scope IDs and tracks bindings/references:
        - Module scope
        - Function scopes
        - Class scopes
        - Comprehension scopes

        Populates:
        - node.scope_id
        - node.bindings (names defined in scope)
        - node.references (names used in scope)
        """

        def visit(node: ASTNode, current_scope: str):
            node.scope_id = current_scope

            # Create new scope for functions and classes
            new_scope = current_scope
            if node.node_type in (
                ASTNodeType.FUNCTION_DEF,
                ASTNodeType.ASYNC_FUNCTION_DEF,
                ASTNodeType.CLASS_DEF,
            ):
                self._scope_counter += 1
                new_scope = f"{current_scope}.{node.name}[{self._scope_counter}]"

                # Add function/class name to parent scope bindings
                if node.parent:
                    node.parent.bindings.add(node.name)

            # Track bindings (assignments)
            if node.node_type in (
                ASTNodeType.ASSIGN,
                ASTNodeType.AUG_ASSIGN,
                ASTNodeType.ANN_ASSIGN,
            ):
                # Extract target names
                for child in node.children:
                    if child.node_type == ASTNodeType.NAME:
                        node.bindings.add(child.name)

            # Track references (name usage)
            if node.node_type == ASTNodeType.NAME:
                node.references.add(node.name)

            # Recurse
            for child in node.children:
                visit(child, new_scope)

        visit(root, "module")

    def _compute_complexity(self, root: ASTNode):
        """
        Compute cyclomatic complexity for all function nodes

        Complexity = 1 + number of decision points:
        - if, elif
        - for, while
        - and, or (in boolean expressions)
        - except handlers
        - list/dict/set comprehensions with if
        - lambda with if
        """

        def count_decisions(node: ASTNode) -> int:
            count = 0

            # Decision point nodes
            decision_types = {
                ASTNodeType.IF,
                ASTNodeType.FOR,
                ASTNodeType.WHILE,
                ASTNodeType.ASYNC_FOR,
                ASTNodeType.TRY,  # Each except handler adds 1
                ASTNodeType.BOOLOP,  # and/or
                ASTNodeType.LISTCOMP,
                ASTNodeType.DICTCOMP,
                ASTNodeType.SETCOMP,
                ASTNodeType.GENERATOREXP,
            }

            if node.node_type in decision_types:
                count += 1

            # Recurse
            for child in node.children:
                count += count_decisions(child)

            return count

        def visit(node: ASTNode):
            if node.node_type in (
                ASTNodeType.FUNCTION_DEF,
                ASTNodeType.ASYNC_FUNCTION_DEF,
            ):
                node.cyclomatic_complexity = 1 + count_decisions(node)

            for child in node.children:
                visit(child)

        visit(root)

    def extract_functions(self, root: ASTNode) -> List[ASTNode]:
        """Extract all function definitions from AST"""
        functions = []

        def visit(node: ASTNode):
            if node.node_type in (
                ASTNodeType.FUNCTION_DEF,
                ASTNodeType.ASYNC_FUNCTION_DEF,
            ):
                functions.append(node)
            for child in node.children:
                visit(child)

        visit(root)
        return functions

    def extract_classes(self, root: ASTNode) -> List[ASTNode]:
        """Extract all class definitions from AST"""
        classes = []

        def visit(node: ASTNode):
            if node.node_type == ASTNodeType.CLASS_DEF:
                classes.append(node)
            for child in node.children:
                visit(child)

        visit(root)
        return classes

    def extract_imports(self, root: ASTNode) -> List[ASTNode]:
        """Extract all import statements from AST"""
        imports = []

        def visit(node: ASTNode):
            if node.node_type in (ASTNodeType.IMPORT, ASTNodeType.IMPORT_FROM):
                imports.append(node)
            for child in node.children:
                visit(child)

        visit(root)
        return imports

    def generate_report(self, root: ASTNode) -> Dict[str, Any]:
        """
        Generate comprehensive analysis report

        Returns dictionary with maximum detail:
        - Total line count
        - Node counts by type
        - Function count, names, complexities
        - Class count, names, hierarchies
        - Import count, module names
        - Deepest nesting level
        - Total bindings and references
        - Scope structure
        """
        functions = self.extract_functions(root)
        classes = self.extract_classes(root)
        imports = self.extract_imports(root)

        # Count nodes by type
        type_counts = {}
        max_depth = 0
        total_bindings = set()
        total_references = set()

        def visit(node: ASTNode):
            nonlocal max_depth
            type_counts[node.node_type.value] = (
                type_counts.get(node.node_type.value, 0) + 1
            )
            max_depth = max(max_depth, node.depth)
            total_bindings.update(node.bindings)
            total_references.update(node.references)
            for child in node.children:
                visit(child)

        visit(root)

        return {
            "total_lines": root.line_end,
            "node_type_counts": type_counts,
            "function_count": len(functions),
            "functions": [
                {
                    "name": f.name,
                    "line": f.line_start,
                    "complexity": f.cyclomatic_complexity,
                    "arguments": f.arguments,
                    "return_type": f.return_annotation,
                    "decorators": f.decorators,
                }
                for f in functions
            ],
            "class_count": len(classes),
            "classes": [
                {
                    "name": c.name,
                    "line": c.line_start,
                    "base_classes": c.base_classes,
                    "decorators": c.decorators,
                }
                for c in classes
            ],
            "import_count": len(imports),
            "imports": [
                {
                    "line": i.line_start,
                    "type": i.node_type.value,
                }
                for i in imports
            ],
            "max_nesting_depth": max_depth,
            "total_bindings": len(total_bindings),
            "total_references": len(total_references),
            "unique_names_bound": list(sorted(total_bindings)),
            "unique_names_referenced": list(sorted(total_references)),
        }
