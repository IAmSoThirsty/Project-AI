# Function Registry System

## Overview

The Function Registry (`src/app/core/function_registry.py`) provides a dynamic function registration and invocation system for extensible AI agent tool calling, plugin systems, and runtime function discovery. It enables functions to be registered with metadata, documented automatically, and invoked by name with parameter validation.

**Location**: `src/app/core/function_registry.py`  
**Lines of Code**: ~250  
**Key Features**: Dynamic registration, auto-schema generation, parameter validation, LLM integration  
**Dependencies**: inspect, logging

---

## Architecture

```
FunctionRegistry
├── _functions: dict[str, FunctionMetadata]
│   ├── name: str
│   ├── func: Callable
│   ├── description: str
│   ├── schema: JSONSchema
│   └── category: str
│
├── register() - Register function with metadata
├── call() - Invoke function by name
├── list_functions() - Discover available functions
├── get_function_info() - Get metadata
└── unregister() - Remove function
```

---

## Core API

### 1. Registration

#### register()
```python
def register(
    self,
    name: str,
    func: Callable,
    description: str | None = None,
    schema: dict[str, Any] | None = None,
    category: str = "general",
) -> None:
```

**Purpose**: Register a function for dynamic invocation.

**Parameters**:
- `name`: Unique identifier for the function
- `func`: The callable to register
- `description`: Human-readable description (auto-extracted from docstring if None)
- `schema`: JSON schema for parameters (auto-generated if None)
- `category`: Organizational category (e.g., "file", "ai", "network")

**Example**:
```python
registry = FunctionRegistry()

def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    return a + b

registry.register("calculate_sum", calculate_sum)
```

**Auto-Schema Generation**:
```python
# Function with type hints
def search_file(
    filename: str,
    pattern: str,
    case_sensitive: bool = False
) -> list[str]:
    """Search for pattern in file."""
    # ...

registry.register("search_file", search_file)

# Generated schema:
{
    "type": "object",
    "properties": {
        "filename": {"type": "string"},
        "pattern": {"type": "string"},
        "case_sensitive": {"type": "boolean", "default": False}
    },
    "required": ["filename", "pattern"]
}
```

---

### 2. Invocation

#### call()
```python
def call(self, name: str, **kwargs) -> Any:
    """
    Invoke a registered function by name.
    
    Args:
        name: Function name
        **kwargs: Parameters to pass to function
    
    Returns:
        Function result
    
    Raises:
        ValueError: If function not found or parameters invalid
    """
```

**Example**:
```python
# Register functions
registry.register("add", lambda a, b: a + b)
registry.register("multiply", lambda a, b: a * b)

# Call by name
result1 = registry.call("add", a=5, b=3)  # 8
result2 = registry.call("multiply", a=4, b=7)  # 28
```

**With Validation**:
```python
def validate_email(email: str) -> bool:
    """Check if email is valid."""
    return "@" in email and "." in email

registry.register("validate_email", validate_email)

# Valid call
is_valid = registry.call("validate_email", email="user@example.com")  # True

# Invalid call (missing parameter)
try:
    registry.call("validate_email")  # Raises ValueError
except ValueError as e:
    print(f"Error: {e}")
```

---

### 3. Discovery

#### list_functions()
```python
def list_functions(
    self,
    category: str | None = None,
    include_schema: bool = False
) -> list[dict[str, Any]]:
    """
    List all registered functions.
    
    Args:
        category: Filter by category (None for all)
        include_schema: Include full JSON schema in results
    
    Returns:
        List of function metadata dictionaries
    """
```

**Example**:
```python
# Register functions in categories
registry.register("read_file", read_file, category="file")
registry.register("write_file", write_file, category="file")
registry.register("send_request", send_request, category="network")
registry.register("parse_json", parse_json, category="data")

# List all functions
all_functions = registry.list_functions()
print(f"Total functions: {len(all_functions)}")

# List by category
file_functions = registry.list_functions(category="file")
for func in file_functions:
    print(f"  - {func['name']}: {func['description']}")

# List with schemas (for LLM integration)
functions_with_schemas = registry.list_functions(include_schema=True)
```

---

#### get_function_info()
```python
def get_function_info(self, name: str) -> dict[str, Any] | None:
    """
    Get detailed metadata about a function.
    
    Returns:
        Dictionary with name, description, schema, category
        or None if function not found
    """
```

**Example**:
```python
info = registry.get_function_info("calculate_sum")
print(f"Name: {info['name']}")
print(f"Description: {info['description']}")
print(f"Category: {info['category']}")
print(f"Schema: {json.dumps(info['schema'], indent=2)}")
```

---

### 4. Management

#### unregister()
```python
def unregister(self, name: str) -> bool:
    """
    Remove a function from the registry.
    
    Returns:
        True if unregistered, False if not found
    """
```

**Example**:
```python
# Register temporary function
registry.register("temp_func", lambda: "temp")

# Use it
result = registry.call("temp_func")

# Clean up
if registry.unregister("temp_func"):
    print("Function removed")
```

---

#### is_registered()
```python
def is_registered(self, name: str) -> bool:
    """Check if function is registered."""
```

**Example**:
```python
if registry.is_registered("calculate_sum"):
    result = registry.call("calculate_sum", a=10, b=20)
else:
    print("Function not available")
```

---

## Usage Patterns

### Pattern 1: Plugin System

```python
class PluginManager:
    def __init__(self):
        self.registry = FunctionRegistry()
        self.loaded_plugins = {}
    
    def load_plugin(self, plugin_module):
        """Load a plugin and register its functions."""
        plugin_name = plugin_module.__name__
        
        # Discover functions with @plugin_function decorator
        for attr_name in dir(plugin_module):
            attr = getattr(plugin_module, attr_name)
            if callable(attr) and hasattr(attr, "_plugin_function"):
                self.registry.register(
                    f"{plugin_name}.{attr_name}",
                    attr,
                    category=plugin_name
                )
        
        self.loaded_plugins[plugin_name] = plugin_module
        logger.info(f"Loaded plugin: {plugin_name}")
    
    def unload_plugin(self, plugin_name: str):
        """Unload a plugin and unregister its functions."""
        functions = self.registry.list_functions(category=plugin_name)
        for func_info in functions:
            self.registry.unregister(func_info["name"])
        
        del self.loaded_plugins[plugin_name]
        logger.info(f"Unloaded plugin: {plugin_name}")

# Decorator for plugin functions
def plugin_function(func):
    func._plugin_function = True
    return func

# Example plugin
# plugins/math_tools.py
@plugin_function
def factorial(n: int) -> int:
    """Calculate factorial of n."""
    return 1 if n <= 1 else n * factorial(n - 1)

@plugin_function
def fibonacci(n: int) -> list[int]:
    """Generate Fibonacci sequence."""
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib[:n]
```

---

### Pattern 2: LLM Function Calling

```python
class LLMFunctionCaller:
    def __init__(self, registry: FunctionRegistry):
        self.registry = registry
        self.openai_client = OpenAI()
    
    def get_tool_definitions(self) -> list[dict]:
        """Convert registry functions to OpenAI tool format."""
        functions = self.registry.list_functions(include_schema=True)
        
        tools = []
        for func_info in functions:
            tool = {
                "type": "function",
                "function": {
                    "name": func_info["name"],
                    "description": func_info["description"],
                    "parameters": func_info["schema"]
                }
            }
            tools.append(tool)
        
        return tools
    
    def execute_tool_call(self, tool_call) -> str:
        """Execute a tool call from LLM response."""
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        # Call the function
        result = self.registry.call(function_name, **function_args)
        
        return json.dumps(result)
    
    def chat_with_tools(self, messages: list[dict]) -> str:
        """Chat with function calling enabled."""
        tools = self.get_tool_definitions()
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # Check if the model wants to call functions
        if response_message.tool_calls:
            # Execute function calls
            for tool_call in response_message.tool_calls:
                function_result = self.execute_tool_call(tool_call)
                
                # Add function result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": function_result
                })
            
            # Get final response
            final_response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )
            return final_response.choices[0].message.content
        
        return response_message.content

# Usage
registry = FunctionRegistry()

# Register tools
registry.register("get_weather", get_weather_data)
registry.register("search_web", search_web)
registry.register("calculate", evaluate_expression)

# Create LLM caller
llm_caller = LLMFunctionCaller(registry)

# Chat with tool access
messages = [
    {"role": "user", "content": "What's the weather in San Francisco?"}
]
response = llm_caller.chat_with_tools(messages)
```

---

### Pattern 3: Command-Line Interface

```python
class CLIInterface:
    def __init__(self, registry: FunctionRegistry):
        self.registry = registry
    
    def run_interactive(self):
        """Run interactive CLI."""
        print("Function Registry CLI")
        print("Type 'help' for commands, 'exit' to quit")
        
        while True:
            try:
                cmd = input("\n> ").strip()
                
                if cmd == "exit":
                    break
                elif cmd == "help":
                    self.show_help()
                elif cmd == "list":
                    self.list_functions()
                elif cmd.startswith("info "):
                    func_name = cmd[5:]
                    self.show_function_info(func_name)
                elif cmd.startswith("call "):
                    self.execute_command(cmd[5:])
                else:
                    print("Unknown command. Type 'help' for options.")
            except Exception as e:
                print(f"Error: {e}")
    
    def show_help(self):
        print("\nAvailable commands:")
        print("  list              - List all functions")
        print("  info <name>       - Show function details")
        print("  call <name> <json> - Call function with JSON args")
        print("  help              - Show this help")
        print("  exit              - Exit CLI")
    
    def list_functions(self):
        functions = self.registry.list_functions()
        print(f"\nRegistered functions ({len(functions)}):")
        
        by_category = {}
        for func in functions:
            category = func["category"]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(func)
        
        for category, funcs in sorted(by_category.items()):
            print(f"\n  {category}:")
            for func in funcs:
                print(f"    - {func['name']}: {func['description']}")
    
    def show_function_info(self, name: str):
        info = self.registry.get_function_info(name)
        if not info:
            print(f"Function '{name}' not found")
            return
        
        print(f"\nFunction: {info['name']}")
        print(f"Category: {info['category']}")
        print(f"Description: {info['description']}")
        print(f"Schema: {json.dumps(info['schema'], indent=2)}")
    
    def execute_command(self, command: str):
        # Parse: function_name {"arg1": value1, "arg2": value2}
        parts = command.split(" ", 1)
        func_name = parts[0]
        
        if len(parts) > 1:
            try:
                args = json.loads(parts[1])
            except json.JSONDecodeError:
                print("Invalid JSON arguments")
                return
        else:
            args = {}
        
        result = self.registry.call(func_name, **args)
        print(f"Result: {result}")

# Usage
registry = FunctionRegistry()
registry.register("add", lambda a, b: a + b)
registry.register("multiply", lambda a, b: a * b)

cli = CLIInterface(registry)
cli.run_interactive()

# Example session:
# > list
# Registered functions (2):
#   general:
#     - add: Add two numbers
#     - multiply: Multiply two numbers
#
# > call add {"a": 5, "b": 3}
# Result: 8
```

---

### Pattern 4: Rate-Limited Registry

```python
from functools import wraps
import time

class RateLimitedRegistry(FunctionRegistry):
    """Function registry with rate limiting."""
    
    def __init__(self):
        super().__init__()
        self._call_history = {}  # func_name -> list of timestamps
        self._rate_limits = {}   # func_name -> (calls, period_seconds)
    
    def register_with_rate_limit(
        self,
        name: str,
        func: Callable,
        max_calls: int,
        period_seconds: int,
        **kwargs
    ):
        """Register function with rate limit."""
        self.register(name, func, **kwargs)
        self._rate_limits[name] = (max_calls, period_seconds)
    
    def call(self, name: str, **kwargs) -> Any:
        """Call function with rate limit enforcement."""
        if name in self._rate_limits:
            max_calls, period = self._rate_limits[name]
            
            # Initialize history if needed
            if name not in self._call_history:
                self._call_history[name] = []
            
            # Clean old calls
            now = time.time()
            self._call_history[name] = [
                t for t in self._call_history[name]
                if now - t < period
            ]
            
            # Check rate limit
            if len(self._call_history[name]) >= max_calls:
                oldest_call = self._call_history[name][0]
                wait_time = period - (now - oldest_call)
                raise RuntimeError(
                    f"Rate limit exceeded for '{name}'. "
                    f"Wait {wait_time:.1f}s"
                )
            
            # Record this call
            self._call_history[name].append(now)
        
        # Execute function
        return super().call(name, **kwargs)

# Usage
registry = RateLimitedRegistry()

def expensive_api_call(query: str) -> dict:
    """Call expensive external API."""
    # ... actual API call
    return {"result": "data"}

# Limit to 10 calls per minute
registry.register_with_rate_limit(
    "expensive_api",
    expensive_api_call,
    max_calls=10,
    period_seconds=60
)

# Will work
for i in range(10):
    registry.call("expensive_api", query=f"query_{i}")

# Will raise RuntimeError
try:
    registry.call("expensive_api", query="query_11")
except RuntimeError as e:
    print(e)  # Rate limit exceeded...
```

---

## Security Considerations

### 1. Input Sanitization

```python
class SecureRegistry(FunctionRegistry):
    """Registry with input sanitization."""
    
    DANGEROUS_PATTERNS = [
        r"__.*__",  # Python magic methods
        r"eval",
        r"exec",
        r"compile",
    ]
    
    def call(self, name: str, **kwargs) -> Any:
        """Call with input validation."""
        # Validate function name
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, name):
                raise ValueError(f"Dangerous function name: {name}")
        
        # Sanitize string arguments
        for key, value in kwargs.items():
            if isinstance(value, str):
                kwargs[key] = self._sanitize_string(value)
        
        return super().call(name, **kwargs)
    
    def _sanitize_string(self, value: str) -> str:
        """Remove potentially dangerous characters."""
        # Remove null bytes
        value = value.replace('\x00', '')
        # Limit length
        return value[:1000]
```

---

### 2. Permission System

```python
class PermissionRegistry(FunctionRegistry):
    """Registry with permission-based access control."""
    
    def __init__(self):
        super().__init__()
        self._permissions = {}  # func_name -> set of allowed roles
    
    def register_with_permissions(
        self,
        name: str,
        func: Callable,
        allowed_roles: set[str],
        **kwargs
    ):
        """Register function with role-based permissions."""
        self.register(name, func, **kwargs)
        self._permissions[name] = allowed_roles
    
    def call_as(self, user_role: str, name: str, **kwargs) -> Any:
        """Call function with role-based access control."""
        if name in self._permissions:
            allowed_roles = self._permissions[name]
            if user_role not in allowed_roles:
                raise PermissionError(
                    f"Role '{user_role}' cannot call '{name}'. "
                    f"Required: {allowed_roles}"
                )
        
        return self.call(name, **kwargs)

# Usage
registry = PermissionRegistry()

registry.register_with_permissions(
    "delete_user",
    delete_user_from_db,
    allowed_roles={"admin", "superuser"}
)

registry.register_with_permissions(
    "view_data",
    view_user_data,
    allowed_roles={"admin", "user", "viewer"}
)

# Admin can delete
registry.call_as("admin", "delete_user", user_id=123)

# User cannot delete
try:
    registry.call_as("user", "delete_user", user_id=123)
except PermissionError as e:
    print(e)
```

---

## Testing Strategies

```python
import unittest

class TestFunctionRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = FunctionRegistry()
    
    def test_register_and_call(self):
        def add(a: int, b: int) -> int:
            return a + b
        
        self.registry.register("add", add)
        result = self.registry.call("add", a=2, b=3)
        self.assertEqual(result, 5)
    
    def test_auto_schema_generation(self):
        def func(a: str, b: int = 10):
            pass
        
        self.registry.register("func", func)
        info = self.registry.get_function_info("func")
        
        schema = info["schema"]
        self.assertEqual(schema["properties"]["a"]["type"], "string")
        self.assertEqual(schema["properties"]["b"]["type"], "integer")
        self.assertIn("a", schema["required"])
        self.assertNotIn("b", schema["required"])
    
    def test_unregister(self):
        self.registry.register("temp", lambda: "test")
        self.assertTrue(self.registry.is_registered("temp"))
        
        self.registry.unregister("temp")
        self.assertFalse(self.registry.is_registered("temp"))
    
    def test_list_by_category(self):
        self.registry.register("f1", lambda: 1, category="cat1")
        self.registry.register("f2", lambda: 2, category="cat1")
        self.registry.register("f3", lambda: 3, category="cat2")
        
        cat1_funcs = self.registry.list_functions(category="cat1")
        self.assertEqual(len(cat1_funcs), 2)
```

---

## Related Documentation

- **Plugin System**: `source-docs/core/plugin-manager.md`
- **AI Agent Integration**: `source-docs/agents/cognition-kernel.md`
- **CLI Interface**: `source-docs/cli/cli-commands.md`

---

**Last Updated**: 2025-01-24  
**Status**: Stable - Production Ready  
**Maintainer**: Core Infrastructure Team
