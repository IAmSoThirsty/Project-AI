"""
Function Registry - Dynamic function/tool registration and invocation system.

This module provides a registry for Python functions that can be dynamically
discovered, documented, and called by name. It supports:
- Function registration with metadata (name, description, parameters)
- Dynamic function invocation with parameter validation
- Documentation generation from docstrings and schemas
- Integration with LLM function calling patterns
"""

import inspect
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class FunctionRegistry:
    """Registry for dynamic function registration and invocation.

    This class enables extensible function calling for AI agents, plugins,
    and other dynamic tool invocation patterns. Functions can be registered
    with metadata and invoked by name with parameter validation.

    Example:
        >>> registry = FunctionRegistry()
        >>> def add(a: int, b: int) -> int:
        ...     '''Add two numbers.'''
        ...     return a + b
        >>> registry.register("add", add)
        >>> result = registry.call("add", a=5, b=3)
        >>> print(result)  # 8
    """

    def __init__(self):
        """Initialize the function registry."""
        self._functions: dict[str, dict[str, Any]] = {}

    def register(
        self,
        name: str,
        func: Callable,
        description: str | None = None,
        schema: dict[str, Any] | None = None,
        category: str = "general"
    ) -> None:
        """Register a function with the registry.

        Args:
            name: Unique name for the function
            func: The callable function to register
            description: Optional description (uses docstring if not provided)
            schema: Optional JSON schema for parameters (auto-generated if not provided)
            category: Category for organizing functions (default: "general")

        Raises:
            ValueError: If function name is empty or already registered
            TypeError: If func is not callable
        """
        if not name:
            raise ValueError("Function name cannot be empty")
        if name in self._functions:
            raise ValueError(f"Function '{name}' is already registered")
        if not callable(func):
            raise TypeError(f"'{name}' is not callable")

        # Extract description from docstring if not provided
        if description is None:
            description = inspect.getdoc(func) or "No description available"

        # Auto-generate schema from function signature if not provided
        if schema is None:
            schema = self._generate_schema(func)

        self._functions[name] = {
            "func": func,
            "description": description,
            "schema": schema,
            "category": category,
            "name": name
        }
        logger.info(f"Registered function: {name} (category: {category})")

    def _generate_schema(self, func: Callable) -> dict[str, Any]:
        """Generate a JSON schema from function signature.

        Args:
            func: The function to analyze

        Returns:
            A JSON schema dictionary describing the function's parameters
        """
        sig = inspect.signature(func)
        parameters = {}
        required = []

        for param_name, param in sig.parameters.items():
            # Skip self/cls parameters
            if param_name in ("self", "cls"):
                continue

            param_info: dict[str, Any] = {}

            # Extract type annotation if available
            if param.annotation != inspect.Parameter.empty:
                param_info["type"] = self._python_type_to_json_type(param.annotation)
            else:
                param_info["type"] = "any"

            # Check if parameter has a default value
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
            else:
                param_info["default"] = param.default

            parameters[param_name] = param_info

        return {
            "type": "object",
            "properties": parameters,
            "required": required
        }

    def _python_type_to_json_type(self, python_type: type) -> str:
        """Convert Python type to JSON schema type.

        Args:
            python_type: Python type annotation

        Returns:
            JSON schema type string
        """
        type_mapping = {
            int: "integer",
            float: "number",
            str: "string",
            bool: "boolean",
            list: "array",
            dict: "object",
            type(None): "null"
        }

        # Handle typing module types (e.g., Optional, Union)
        type_str = str(python_type)
        if "Optional" in type_str or "Union" in type_str:
            return "any"

        return type_mapping.get(python_type, "any")

    def unregister(self, name: str) -> bool:
        """Unregister a function from the registry.

        Args:
            name: Name of the function to unregister

        Returns:
            True if function was unregistered, False if not found
        """
        if name in self._functions:
            del self._functions[name]
            logger.info(f"Unregistered function: {name}")
            return True
        return False

    def is_registered(self, name: str) -> bool:
        """Check if a function is registered.

        Args:
            name: Function name to check

        Returns:
            True if function is registered, False otherwise
        """
        return name in self._functions

    def get_function_info(self, name: str) -> dict[str, Any] | None:
        """Get metadata about a registered function.

        Args:
            name: Function name

        Returns:
            Dictionary with function metadata, or None if not found
        """
        if name not in self._functions:
            return None

        func_data = self._functions[name].copy()
        # Don't expose the actual callable in the info
        func_data.pop("func", None)
        return func_data

    def list_functions(
        self,
        category: str | None = None,
        include_schema: bool = False
    ) -> list[dict[str, Any]]:
        """List all registered functions.

        Args:
            category: Optional category filter
            include_schema: Whether to include full schema in results

        Returns:
            List of function metadata dictionaries
        """
        functions = []
        for name, func_data in self._functions.items():
            if category and func_data["category"] != category:
                continue

            info = {
                "name": name,
                "description": func_data["description"],
                "category": func_data["category"]
            }

            if include_schema:
                info["schema"] = func_data["schema"]

            functions.append(info)

        return functions

    def get_categories(self) -> list[str]:
        """Get list of all function categories.

        Returns:
            Sorted list of unique categories
        """
        categories = {func_data["category"] for func_data in self._functions.values()}
        return sorted(categories)

    def call(self, function_name: str, **kwargs) -> Any:
        """Call a registered function by name.

        Args:
            function_name: Function name
            **kwargs: Parameters to pass to the function

        Returns:
            Result from the function call

        Raises:
            ValueError: If function is not registered
            TypeError: If parameters don't match function signature
        """
        if function_name not in self._functions:
            raise ValueError(f"Function '{function_name}' is not registered")

        func_data = self._functions[function_name]
        func = func_data["func"]

        try:
            result = func(**kwargs)
            logger.debug(f"Called function '{function_name}' with kwargs: {kwargs}")
            return result
        except TypeError as e:
            logger.error(f"Parameter mismatch calling '{function_name}': {e}")
            raise TypeError(
                f"Invalid parameters for function '{function_name}': {e}"
            ) from e

    def get_help(self, name: str | None = None) -> str:
        """Get help text for a function or all functions.

        Args:
            name: Optional function name (if None, returns help for all functions)

        Returns:
            Formatted help text
        """
        if name is not None:
            # Help for specific function
            if name not in self._functions:
                return f"Function '{name}' not found"

            func_data = self._functions[name]
            help_text = f"Function: {name}\n"
            help_text += f"Category: {func_data['category']}\n"
            help_text += f"Description: {func_data['description']}\n\n"

            schema = func_data["schema"]
            if schema.get("properties"):
                help_text += "Parameters:\n"
                for param_name, param_info in schema["properties"].items():
                    param_type = param_info.get("type", "any")
                    required = param_name in schema.get("required", [])
                    req_str = " (required)" if required else " (optional)"
                    default = param_info.get("default")
                    default_str = f" [default: {default}]" if default is not None else ""
                    help_text += f"  - {param_name}: {param_type}{req_str}{default_str}\n"
            else:
                help_text += "Parameters: None\n"

            return help_text
        else:
            # Help for all functions
            if not self._functions:
                return "No functions registered"

            categories = self.get_categories()
            help_lines = ["Available Functions", "=" * 50, ""]

            for category in categories:
                help_lines.append(f"\n[{category.upper()}]")
                help_lines.append("-" * 50)

                funcs = self.list_functions(category=category)
                for func_info in funcs:
                    help_lines.append(f"  {func_info['name']}")
                    # Truncate long descriptions
                    desc = func_info['description']
                    if len(desc) > 60:
                        desc = desc[:57] + "..."
                    help_lines.append(f"    {desc}")

            return "\n".join(help_lines)

    def to_openai_function_schema(self, name: str) -> dict[str, Any] | None:
        """Convert a function to OpenAI function calling schema format.

        Args:
            name: Function name

        Returns:
            OpenAI-compatible function schema, or None if not found
        """
        if name not in self._functions:
            return None

        func_data = self._functions[name]
        return {
            "name": name,
            "description": func_data["description"],
            "parameters": func_data["schema"]
        }

    def to_openai_function_schemas(
        self,
        category: str | None = None
    ) -> list[dict[str, Any]]:
        """Get all functions as OpenAI function calling schemas.

        Args:
            category: Optional category filter

        Returns:
            List of OpenAI-compatible function schemas
        """
        schemas = []
        for name in self._functions:
            func_data = self._functions[name]
            if category and func_data["category"] != category:
                continue
            schema = self.to_openai_function_schema(name)
            if schema:
                schemas.append(schema)
        return schemas
