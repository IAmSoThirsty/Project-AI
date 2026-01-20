#!/usr/bin/env python3
"""
Function Registry & Knowledge Base Integration Example

This example demonstrates the new modular, extensible knowledge base querying
and function calling capabilities in Project-AI.

Features demonstrated:
1. Function Registration - Register custom functions/tools
2. Knowledge Base Queries - Search and retrieve stored knowledge
3. Intelligence Routing - Automatic routing of queries to appropriate handlers
4. Function Invocation - Dynamic function calling by name
5. Integration Patterns - How to use these systems together
"""

import sys
import tempfile
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# ruff: noqa: E402 - Path manipulation required before imports
from app.core.ai_systems import MemoryExpansionSystem
from app.core.function_registry import FunctionRegistry
from app.core.intelligence_engine import IntelligenceRouter

# ============================================================================
# PART 1: Function Registry - Registering Custom Functions
# ============================================================================

def example_function_registry():
    """Demonstrate function registry capabilities."""
    print("=" * 70)
    print("PART 1: Function Registry")
    print("=" * 70)
    print()

    # Create a function registry
    registry = FunctionRegistry()

    # Define some example functions
    def calculate_area(length: float, width: float) -> float:
        """Calculate the area of a rectangle."""
        return length * width

    def greet_user(name: str, greeting: str = "Hello") -> str:
        """Greet a user with a customizable greeting."""
        return f"{greeting}, {name}!"

    def get_system_info() -> dict:
        """Get basic system information."""
        return {
            "platform": sys.platform,
            "python_version": sys.version.split()[0]
        }

    # Register functions with different categories
    print("Registering functions...")
    registry.register("calculate_area", calculate_area, category="math")
    registry.register("greet_user", greet_user, category="utility")
    registry.register("get_system_info", get_system_info, category="system")
    print(f"✓ Registered {len(registry.list_functions())} functions")
    print()

    # List all registered functions
    print("Available functions:")
    for func in registry.list_functions():
        print(f"  - {func['name']} ({func['category']}): {func['description'][:50]}...")
    print()

    # Get help for a specific function
    print("Help for 'calculate_area':")
    print("-" * 70)
    print(registry.get_help("calculate_area"))
    print()

    # Call functions dynamically
    print("Calling functions:")
    area = registry.call("calculate_area", length=5.0, width=3.0)
    print(f"  calculate_area(5.0, 3.0) = {area}")

    greeting = registry.call("greet_user", name="Alice")
    print(f"  greet_user('Alice') = '{greeting}'")

    info = registry.call("get_system_info")
    print(f"  get_system_info() = {info}")
    print()

    # OpenAI function calling format
    print("OpenAI function calling schema:")
    schema = registry.to_openai_function_schema("calculate_area")
    print(f"  {schema}")
    print()

    return registry


# ============================================================================
# PART 2: Knowledge Base Queries
# ============================================================================

def example_knowledge_base_queries():
    """Demonstrate knowledge base query capabilities."""
    print("=" * 70)
    print("PART 2: Knowledge Base Queries")
    print("=" * 70)
    print()

    # Create a memory system with test data
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = MemoryExpansionSystem(data_dir=tmpdir)

        # Add some knowledge
        print("Adding knowledge to the knowledge base...")
        memory.add_knowledge("user_preferences", "favorite_color", "blue")
        memory.add_knowledge("user_preferences", "favorite_language", "Python")
        memory.add_knowledge("user_preferences", "theme", "dark mode")

        memory.add_knowledge("skills", "programming", "advanced")
        memory.add_knowledge("skills", "machine_learning", "intermediate")
        memory.add_knowledge("skills", "web_development", "beginner")

        memory.add_knowledge("facts", "python_creator", "Guido van Rossum")
        memory.add_knowledge("facts", "python_year", "1991")
        memory.add_knowledge("facts", "ai_definition", "Artificial Intelligence")
        print("✓ Added 9 knowledge entries across 3 categories")
        print()

        # Query knowledge
        print("Querying knowledge base:")

        # Search by key
        results = memory.query_knowledge("favorite")
        print(f"  Query 'favorite': Found {len(results)} results")
        for r in results:
            print(f"    - [{r['category']}] {r['key']} = {r['value']}")
        print()

        # Search by value
        results = memory.query_knowledge("Python")
        print(f"  Query 'Python': Found {len(results)} results")
        for r in results:
            print(f"    - [{r['category']}] {r['key']} = {r['value']}")
        print()

        # Search within category
        results = memory.query_knowledge("programming", category="skills")
        print(f"  Query 'programming' in category 'skills': Found {len(results)} results")
        for r in results:
            print(f"    - {r['key']} = {r['value']}")
        print()

        # Get category summary
        summary = memory.get_category_summary("user_preferences")
        print("Category summary for 'user_preferences':")
        print(f"  Total entries: {summary['entries']}")
        print(f"  Keys: {', '.join(summary['keys'])}")
        print()

        # Log some conversations
        print("Logging conversations...")
        memory.log_conversation(
            "What is Python?",
            "Python is a high-level programming language."
        )
        memory.log_conversation(
            "Who created Python?",
            "Python was created by Guido van Rossum."
        )
        memory.log_conversation(
            "Tell me about AI",
            "AI stands for Artificial Intelligence."
        )
        print("✓ Logged 3 conversations")
        print()

        # Search conversations
        print("Searching conversation history:")
        results = memory.search_conversations("Python")
        print(f"  Query 'Python': Found {len(results)} conversations")
        for conv in results:
            print(f"    User: {conv['user']}")
            print(f"    AI: {conv['ai'][:60]}...")
            print()

        return memory


# ============================================================================
# PART 3: Intelligence Router Integration
# ============================================================================

def example_intelligence_router():
    """Demonstrate intelligence router capabilities."""
    print("=" * 70)
    print("PART 3: Intelligence Router Integration")
    print("=" * 70)
    print()

    # Set up the components
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = MemoryExpansionSystem(data_dir=tmpdir)
        registry = FunctionRegistry()

        # Add some test data
        memory.add_knowledge("facts", "capital_france", "Paris")
        memory.add_knowledge("facts", "python_language", "Programming language")

        def add_numbers(a: int, b: int) -> int:
            """Add two numbers together."""
            return a + b

        registry.register("add_numbers", add_numbers, category="math")

        # Create router
        router = IntelligenceRouter(
            memory_system=memory,
            function_registry=registry
        )

        print("Testing intelligent query routing:")
        print()

        # Test knowledge query
        print("1. Knowledge Query:")
        result = router.route_query("What is the capital of France?")
        print(f"   Route: {result['route']}")
        print(f"   Response: {result['response'][:100]}...")
        print()

        # Test function help
        print("2. Function Help Query:")
        result = router.route_query("What functions are available?")
        print(f"   Route: {result['route']}")
        print(f"   Response: {result['response'][:100]}...")
        print()

        # Test function call routing
        print("3. Function Call Routing:")
        result = router.route_query("Call add_numbers")
        print(f"   Route: {result['route']}")
        print(f"   Response: {result['response']}")
        print()

        # Actual function call
        print("4. Actual Function Call:")
        result = router.call_function("add_numbers", a=10, b=20)
        print(f"   Success: {result['success']}")
        print(f"   Result: {result['result']}")
        print()


# ============================================================================
# PART 4: Complete Integration Example
# ============================================================================

def example_complete_integration():
    """Demonstrate complete integration pattern."""
    print("=" * 70)
    print("PART 4: Complete Integration Example")
    print("=" * 70)
    print()

    print("This example shows how to integrate all components in a real application.")
    print()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Initialize all components
        memory = MemoryExpansionSystem(data_dir=tmpdir)
        registry = FunctionRegistry()
        router = IntelligenceRouter(memory, registry)

        # Register utility functions
        def save_note(title: str, content: str) -> str:
            """Save a note to the knowledge base."""
            memory.add_knowledge("notes", title, content)
            return f"Note '{title}' saved successfully"

        def search_notes(query: str) -> list:
            """Search notes in the knowledge base."""
            return memory.query_knowledge(query, category="notes")

        registry.register("save_note", save_note, category="notes")
        registry.register("search_notes", search_notes, category="notes")

        print("Registered utility functions:")
        for func in registry.list_functions():
            print(f"  - {func['name']}")
        print()

        # Simulate user interactions
        print("Simulating user interactions:")
        print()

        # Save a note via function call
        print("User: Save a note about Python")
        result = router.call_function(
            "save_note",
            title="python_info",
            content="Python is a versatile programming language"
        )
        print(f"System: {result['result']}")
        print()

        # Query knowledge
        print("User: What do you know about Python?")
        result = router.route_query("Tell me about Python")
        print(f"System: {result['response']}")
        print()

        # Search notes
        print("User: Search my notes for Python")
        result = router.call_function("search_notes", query="python")
        if result['success']:
            notes = result['result']
            print(f"System: Found {len(notes)} note(s):")
            for note in notes:
                print(f"  - {note['key']}: {note['value']}")
        print()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Run all examples."""
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "Function Registry & Knowledge Base Integration" + " " * 11 + "║")
    print("║" + " " * 24 + "Project-AI Demo" + " " * 29 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    try:
        # Run all examples
        example_function_registry()
        example_knowledge_base_queries()
        example_intelligence_router()
        example_complete_integration()

        print("=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)
        print()
        print("Key Takeaways:")
        print("  1. FunctionRegistry enables dynamic function registration and calling")
        print("  2. MemoryExpansionSystem now supports powerful knowledge queries")
        print("  3. IntelligenceRouter provides unified query handling")
        print("  4. All systems integrate seamlessly for agent-like behavior")
        print()
        print("Next Steps:")
        print("  - Register your own custom functions")
        print("  - Build a knowledge base for your domain")
        print("  - Integrate with LLM function calling APIs")
        print("  - Add UI components for interactive access")
        print()

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
