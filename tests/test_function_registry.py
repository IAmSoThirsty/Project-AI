"""Tests for FunctionRegistry."""

import pytest

from app.core.function_registry import FunctionRegistry


class TestFunctionRegistry:
    """Test function registry."""

    @pytest.fixture
    def registry(self):
        """Create function registry."""
        return FunctionRegistry()

    def test_initialization(self, registry):
        """Test registry initializes empty."""
        assert len(registry.list_functions()) == 0

    def test_register_function(self, registry):
        """Test registering a function."""

        def sample_func(x: int) -> int:
            """Sample function."""
            return x * 2

        registry.register("double", sample_func)
        assert registry.is_registered("double")

    def test_register_duplicate_raises(self, registry):
        """Test registering duplicate function raises error."""

        def func1():
            pass

        registry.register("test", func1)

        with pytest.raises(ValueError, match="already registered"):
            registry.register("test", func1)

    def test_register_non_callable_raises(self, registry):
        """Test registering non-callable raises error."""
        with pytest.raises(TypeError, match="not callable"):
            registry.register("test", "not a function")

    def test_register_empty_name_raises(self, registry):
        """Test registering with empty name raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            registry.register("", lambda: None)

    def test_unregister_function(self, registry):
        """Test unregistering a function."""
        registry.register("test", lambda: None)
        assert registry.unregister("test")
        assert not registry.is_registered("test")

    def test_unregister_nonexistent_returns_false(self, registry):
        """Test unregistering nonexistent function returns False."""
        assert not registry.unregister("nonexistent")

    def test_call_function(self, registry):
        """Test calling a registered function."""

        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        registry.register("add", add)
        result = registry.call("add", a=5, b=3)
        assert result == 8

    def test_call_with_defaults(self, registry):
        """Test calling function with default parameters."""

        def greet(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"

        registry.register("greet", greet)
        result = registry.call("greet", name="World")
        assert result == "Hello, World!"

        result = registry.call("greet", name="World", greeting="Hi")
        assert result == "Hi, World!"

    def test_call_unregistered_raises(self, registry):
        """Test calling unregistered function raises error."""
        with pytest.raises(ValueError, match="not registered"):
            registry.call("nonexistent")

    def test_call_invalid_params_raises(self, registry):
        """Test calling with invalid parameters raises error."""

        def func(x: int) -> int:
            return x

        registry.register("func", func)

        with pytest.raises(TypeError, match="Invalid parameters"):
            registry.call("func", y=5)  # Wrong parameter name

    def test_get_function_info(self, registry):
        """Test getting function metadata."""

        def multiply(x: int, y: int) -> int:
            """Multiply two numbers."""
            return x * y

        registry.register("multiply", multiply, category="math")
        info = registry.get_function_info("multiply")

        assert info is not None
        assert info["name"] == "multiply"
        assert info["category"] == "math"
        assert "Multiply two numbers" in info["description"]
        assert "func" not in info  # Should not expose callable

    def test_get_function_info_nonexistent(self, registry):
        """Test getting info for nonexistent function returns None."""
        assert registry.get_function_info("nonexistent") is None

    def test_list_functions(self, registry):
        """Test listing all functions."""
        registry.register("func1", lambda: 1, category="cat1")
        registry.register("func2", lambda: 2, category="cat2")
        registry.register("func3", lambda: 3, category="cat1")

        all_funcs = registry.list_functions()
        assert len(all_funcs) == 3

        # Filter by category
        cat1_funcs = registry.list_functions(category="cat1")
        assert len(cat1_funcs) == 2
        assert all(f["category"] == "cat1" for f in cat1_funcs)

    def test_list_functions_with_schema(self, registry):
        """Test listing functions with schema included."""

        def func(x: int) -> int:
            return x

        registry.register("func", func)

        without_schema = registry.list_functions(include_schema=False)
        assert "schema" not in without_schema[0]

        with_schema = registry.list_functions(include_schema=True)
        assert "schema" in with_schema[0]

    def test_get_categories(self, registry):
        """Test getting list of categories."""
        registry.register("f1", lambda: 1, category="math")
        registry.register("f2", lambda: 2, category="string")
        registry.register("f3", lambda: 3, category="math")

        categories = registry.get_categories()
        assert len(categories) == 2
        assert "math" in categories
        assert "string" in categories
        assert categories == sorted(categories)  # Should be sorted

    def test_schema_generation(self, registry):
        """Test automatic schema generation from function signature."""

        def func(a: int, b: str, c: float = 3.14, d: bool = True) -> str:
            """Test function."""
            return f"{a}-{b}"

        registry.register("func", func)
        info = registry.get_function_info("func")
        schema = info["schema"]

        assert schema["type"] == "object"
        assert "a" in schema["properties"]
        assert "b" in schema["properties"]
        assert "c" in schema["properties"]
        assert "d" in schema["properties"]

        # Check required parameters (no defaults)
        assert "a" in schema["required"]
        assert "b" in schema["required"]
        assert "c" not in schema["required"]
        assert "d" not in schema["required"]

        # Check types
        assert schema["properties"]["a"]["type"] == "integer"
        assert schema["properties"]["b"]["type"] == "string"
        assert schema["properties"]["c"]["type"] == "number"
        assert schema["properties"]["d"]["type"] == "boolean"

        # Check defaults
        assert schema["properties"]["c"]["default"] == 3.14
        assert schema["properties"]["d"]["default"] is True

    def test_get_help_specific_function(self, registry):
        """Test getting help for specific function."""

        def add(x: int, y: int) -> int:
            """Add two integers."""
            return x + y

        registry.register("add", add, category="math")
        help_text = registry.get_help("add")

        assert "Function: add" in help_text
        assert "Category: math" in help_text
        assert "Add two integers" in help_text
        assert "Parameters:" in help_text
        assert "x: integer (required)" in help_text
        assert "y: integer (required)" in help_text

    def test_get_help_with_optional_params(self, registry):
        """Test help display for functions with optional parameters."""

        def greet(name: str, prefix: str = "Hello") -> str:
            """Greet someone."""
            return f"{prefix}, {name}"

        registry.register("greet", greet)
        help_text = registry.get_help("greet")

        assert "name: string (required)" in help_text
        assert "prefix: string (optional)" in help_text
        assert "[default: Hello]" in help_text

    def test_get_help_nonexistent_function(self, registry):
        """Test getting help for nonexistent function."""
        help_text = registry.get_help("nonexistent")
        assert "not found" in help_text

    def test_get_help_all_functions(self, registry):
        """Test getting help for all functions."""
        registry.register("func1", lambda: 1, description="First function", category="cat1")
        registry.register("func2", lambda: 2, description="Second function", category="cat2")

        help_text = registry.get_help()

        assert "Available Functions" in help_text
        assert "func1" in help_text
        assert "func2" in help_text
        assert "First function" in help_text
        assert "Second function" in help_text

    def test_get_help_empty_registry(self, registry):
        """Test getting help when no functions registered."""
        help_text = registry.get_help()
        assert "No functions registered" in help_text

    def test_to_openai_function_schema(self, registry):
        """Test converting function to OpenAI format."""

        def calculate(x: int, y: int, operation: str = "add") -> int:
            """Perform calculation on two numbers."""
            return x + y if operation == "add" else x - y

        registry.register("calculate", calculate)
        schema = registry.to_openai_function_schema("calculate")

        assert schema is not None
        assert schema["name"] == "calculate"
        assert "Perform calculation" in schema["description"]
        assert "parameters" in schema
        assert schema["parameters"]["type"] == "object"
        assert "x" in schema["parameters"]["properties"]

    def test_to_openai_function_schemas_all(self, registry):
        """Test getting all functions as OpenAI schemas."""
        registry.register("func1", lambda x: x, category="cat1")
        registry.register("func2", lambda y: y, category="cat2")
        registry.register("func3", lambda z: z, category="cat1")

        # Get all schemas
        all_schemas = registry.to_openai_function_schemas()
        assert len(all_schemas) == 3

        # Filter by category
        cat1_schemas = registry.to_openai_function_schemas(category="cat1")
        assert len(cat1_schemas) == 2

    def test_custom_description_and_schema(self, registry):
        """Test registering with custom description and schema."""

        def func(x):
            """Original docstring."""
            return x

        custom_desc = "Custom description"
        custom_schema = {
            "type": "object",
            "properties": {"x": {"type": "number", "description": "Input value"}},
            "required": ["x"],
        }

        registry.register("func", func, description=custom_desc, schema=custom_schema)
        info = registry.get_function_info("func")

        assert info["description"] == custom_desc
        assert info["schema"] == custom_schema

    def test_function_without_type_annotations(self, registry):
        """Test registering function without type annotations."""

        def no_types(x, y):
            """Function without types."""
            return x + y

        registry.register("no_types", no_types)
        info = registry.get_function_info("no_types")

        # Should still generate schema but with 'any' type
        assert info["schema"]["properties"]["x"]["type"] == "any"
        assert info["schema"]["properties"]["y"]["type"] == "any"
