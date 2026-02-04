# Function Registry & Knowledge Base Querying

This document describes the new modular, extensible knowledge base querying and function calling capabilities in Project-AI.

## Overview

Project-AI now supports modern LLM-style function calling and knowledge base querying through three core components:

1. **FunctionRegistry** - Dynamic function/tool registration and invocation
1. **Enhanced MemoryExpansionSystem** - Powerful knowledge base querying
1. **IntelligenceRouter** - Unified query handling with automatic routing

These features enable Project-AI to act more like a modern AI agent with structured knowledge recall and extensible, dynamic tool calling.

## FunctionRegistry

The `FunctionRegistry` class provides a centralized system for registering, documenting, and calling Python functions by name.

### Features

- Dynamic function registration with metadata
- Automatic schema generation from function signatures
- OpenAI-compatible function calling schemas
- Function categorization and discovery
- Built-in help and documentation generation
- Type-safe parameter validation

### Basic Usage

```python
from app.core.function_registry import FunctionRegistry

# Create registry
registry = FunctionRegistry()

# Define a function
def calculate_area(length: float, width: float) -> float:
    """Calculate the area of a rectangle."""
    return length * width

# Register the function
registry.register("calculate_area", calculate_area, category="math")

# List available functions
functions = registry.list_functions()

# Get help
help_text = registry.get_help("calculate_area")

# Call the function
result = registry.call("calculate_area", length=5.0, width=3.0)
print(result)  # 15.0
```

### Advanced Features

**OpenAI Function Calling Integration:**

```python
# Get OpenAI-compatible schema for a single function
schema = registry.to_openai_function_schema("calculate_area")

# Get all functions as OpenAI schemas
all_schemas = registry.to_openai_function_schemas()

# Filter by category
math_schemas = registry.to_openai_function_schemas(category="math")
```

**Custom Schemas:**

```python
# Register with custom description and schema
custom_schema = {
    "type": "object",
    "properties": {
        "x": {"type": "number", "description": "First number"},
        "y": {"type": "number", "description": "Second number"}
    },
    "required": ["x", "y"]
}

registry.register(
    "custom_func",
    my_function,
    description="Custom description",
    schema=custom_schema
)
```

## Knowledge Base Querying

The `MemoryExpansionSystem` now includes powerful query capabilities for searching stored knowledge and conversations.

### Features

- Case-insensitive keyword search
- Category filtering
- Search across keys and values
- Conversation history search
- Category summaries and metadata

### Basic Usage

```python
from app.core.ai_systems import MemoryExpansionSystem

# Create memory system
memory = MemoryExpansionSystem(data_dir="data")

# Add knowledge
memory.add_knowledge("preferences", "favorite_color", "blue")
memory.add_knowledge("skills", "programming", "advanced")

# Query knowledge
results = memory.query_knowledge("programming")
for result in results:
    print(f"[{result['category']}] {result['key']}: {result['value']}")

# Search with category filter
results = memory.query_knowledge("programming", category="skills")

# Search conversations
memory.log_conversation("What is Python?", "Python is a programming language.")
conv_results = memory.search_conversations("Python")

# Get category info
summary = memory.get_category_summary("skills")
print(f"Total entries: {summary['entries']}")
```

### Query Methods

**query_knowledge(query, category=None, limit=10)**

- Searches knowledge base for matching entries
- Returns list of dicts with `category`, `key`, `value`, `match_type`

**search_conversations(query, limit=10, search_user=True, search_ai=True)**

- Searches conversation history
- Returns most recent matches first
- Can search user messages, AI responses, or both

**get_all_categories()**

- Returns list of all knowledge categories

**get_category_summary(category)**

- Returns metadata about a specific category
- Includes entry count and key preview

## IntelligenceRouter

The `IntelligenceRouter` provides unified query handling with automatic routing to appropriate handlers.

### Features

- Automatic query type detection
- Routing to knowledge base, function registry, or conversations
- Function invocation interface
- Context-aware responses
- Metadata tracking

### Basic Usage

```python
from app.core.intelligence_engine import IntelligenceRouter

# Create router with components
router = IntelligenceRouter(
    memory_system=memory,
    function_registry=registry
)

# Route a query
result = router.route_query("What do you know about Python?")
print(f"Route: {result['route']}")
print(f"Response: {result['response']}")

# Call a function
result = router.call_function("calculate_area", length=5.0, width=3.0)
if result['success']:
    print(f"Result: {result['result']}")
```

### Query Routing

The router automatically detects query types:

- **help/functions/tools** → Function help display
- **what/who/where/when** → Knowledge base query
- **call/run/execute** → Function invocation routing
- **remember/conversation** → Conversation search
- **general** → Default response with guidance

### Integration Example

```python
# Complete integration
from app.core.ai_systems import MemoryExpansionSystem
from app.core.function_registry import FunctionRegistry
from app.core.intelligence_engine import IntelligenceRouter

# Initialize components
memory = MemoryExpansionSystem(data_dir="data")
registry = FunctionRegistry()

# Register utility functions
def save_note(title: str, content: str) -> str:
    """Save a note to the knowledge base."""
    memory.add_knowledge("notes", title, content)
    return f"Note '{title}' saved successfully"

registry.register("save_note", save_note, category="notes")

# Create router
router = IntelligenceRouter(memory, registry)

# Use in your application
user_query = "Save a note about Python"
result = router.route_query(user_query)

if result['route'] == 'function_call':
    # Extract function name and parameters
    function_name = result['metadata']['function_name']
    # ... handle function invocation ...
```

## UI Components

The system includes PyQt6 UI components for interactive access:

### KnowledgeSearchPanel

- Search input with category filtering
- Real-time results display
- Category browsing

### FunctionRegistryPanel

- Function list with categorization
- Function details and help
- Invocation interface

### Usage in Dashboard

```python
from app.gui.knowledge_functions_panel import KnowledgeFunctionsWidget

# Add to your dashboard
widget = KnowledgeFunctionsWidget()

# Connect signals
widget.knowledge_panel.search_requested.connect(on_search)
widget.function_panel.function_selected.connect(on_function_selected)

# Update data
widget.knowledge_panel.update_categories(memory.get_all_categories())
widget.function_panel.update_functions(registry.list_functions())
```

## Testing

Comprehensive test coverage is included:

```bash
# Run all new tests
pytest tests/test_function_registry.py -v       # 26 tests
pytest tests/test_memory_query.py -v            # 21 tests
pytest tests/test_intelligence_router.py -v     # 19 tests

# Run example demonstration
python examples/function_knowledge_integration.py
```

## Example Scripts

See `examples/function_knowledge_integration.py` for a complete demonstration including:

1. Function registration and invocation
1. Knowledge base queries and searches
1. Intelligence router integration
1. Complete application integration pattern

## API Reference

### FunctionRegistry

```python
class FunctionRegistry:
    def register(name, func, description=None, schema=None, category="general")
    def unregister(name) -> bool
    def is_registered(name) -> bool
    def get_function_info(name) -> dict | None
    def list_functions(category=None, include_schema=False) -> list
    def get_categories() -> list
    def call(function_name, **kwargs) -> Any
    def get_help(name=None) -> str
    def to_openai_function_schema(name) -> dict | None
    def to_openai_function_schemas(category=None) -> list
```

### MemoryExpansionSystem (Enhanced)

```python
class MemoryExpansionSystem:
    # Existing methods...
    def query_knowledge(query, category=None, limit=10) -> list
    def search_conversations(query, limit=10, search_user=True, search_ai=True) -> list
    def get_all_categories() -> list
    def get_category_summary(category) -> dict | None
```

### IntelligenceRouter

```python
class IntelligenceRouter:
    def __init__(memory_system=None, function_registry=None)
    def route_query(query, context=None) -> dict
    def call_function(function_name, **kwargs) -> dict
```

## Best Practices

1. **Function Registration**: Register functions at application startup
1. **Categories**: Use meaningful categories for organization
1. **Schemas**: Let auto-generation work, override only when needed
1. **Error Handling**: Always check `success` field in function call results
1. **Search Limits**: Use reasonable limits to avoid overwhelming results
1. **Context**: Provide context to router for better query understanding

## Integration with LLMs

The FunctionRegistry is designed to work seamlessly with LLM function calling:

```python
# Get schemas for LLM
schemas = registry.to_openai_function_schemas()

# Use in LLM call
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Calculate area"}],
    functions=schemas
)

# If LLM returns function call
if response.choices[0].message.function_call:
    name = response.choices[0].message.function_call.name
    args = json.loads(response.choices[0].message.function_call.arguments)
    result = registry.call(name, **args)
```

## Future Enhancements

Potential future improvements include:

- Async function support
- Function chaining and composition
- Advanced query parsing with NLP
- Vector-based semantic search
- Function call history and analytics
- Web API endpoints for remote access

## Contributing

When adding new functions or extending the system:

1. Write comprehensive docstrings
1. Add appropriate type annotations
1. Include unit tests
1. Update this documentation
1. Follow repository conventions

## Support

For issues or questions:

- Check `examples/function_knowledge_integration.py` for usage patterns
- Review test files for additional examples
- See `PROGRAM_SUMMARY.md` for architecture details
- Open an issue on GitHub
