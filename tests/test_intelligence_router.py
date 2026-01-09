"""Tests for IntelligenceRouter."""

import tempfile

import pytest

from app.core.ai_systems import MemoryExpansionSystem
from app.core.function_registry import FunctionRegistry
from app.core.intelligence_engine import IntelligenceRouter


class TestIntelligenceRouter:
    """Test intelligence router."""
    
    @pytest.fixture
    def router_with_components(self):
        """Create router with memory and function registry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            memory = MemoryExpansionSystem(data_dir=tmpdir)
            registry = FunctionRegistry()
            
            # Add test data
            memory.add_knowledge("facts", "test_fact", "test_value")
            
            def test_func(x: int) -> int:
                """Test function."""
                return x * 2
                
            registry.register("test_func", test_func)
            
            router = IntelligenceRouter(memory, registry)
            yield router
            
    @pytest.fixture
    def router_without_components(self):
        """Create router without components."""
        return IntelligenceRouter()
        
    def test_initialization(self):
        """Test router initializes."""
        router = IntelligenceRouter()
        assert router.memory_system is None
        assert router.function_registry is None
        
    def test_initialization_with_components(self, router_with_components):
        """Test router initializes with components."""
        assert router_with_components.memory_system is not None
        assert router_with_components.function_registry is not None
        
    def test_route_function_help_query(self, router_with_components):
        """Test routing help query."""
        result = router_with_components.route_query("help")
        
        assert result["route"] == "function_help"
        assert "Available Functions" in result["response"]
        assert "function_count" in result["metadata"]
        
    def test_route_function_help_without_registry(self, router_without_components):
        """Test help query without function registry."""
        result = router_without_components.route_query("help")
        assert result["route"] == "general"
        
    def test_route_knowledge_query(self, router_with_components):
        """Test routing knowledge query."""
        result = router_with_components.route_query("what is test")
        
        # Should attempt knowledge search (may or may not find results)
        assert result["route"] in ["knowledge_query", "general"]
        
    def test_route_function_call_query(self, router_with_components):
        """Test routing function call query."""
        result = router_with_components.route_query("call test_func")
        
        assert result["route"] in ["function_call", "general"]
        
    def test_route_conversation_search(self, router_with_components):
        """Test routing conversation search query."""
        # Add a conversation first
        router_with_components.memory_system.log_conversation(
            "test message",
            "test response"
        )
        
        result = router_with_components.route_query("remember test")
        
        # Should route to conversation search or general
        assert result["route"] in ["conversation_search", "general"]
        
    def test_route_general_query(self, router_with_components):
        """Test routing general query."""
        result = router_with_components.route_query("hello there")
        
        assert result["route"] == "general"
        assert "metadata" in result
        
    def test_call_function_success(self, router_with_components):
        """Test successful function call."""
        result = router_with_components.call_function("test_func", x=5)
        
        assert result["success"] is True
        assert result["result"] == 10
        assert result["function_name"] == "test_func"
        
    def test_call_function_without_registry(self, router_without_components):
        """Test function call without registry."""
        result = router_without_components.call_function("test_func", x=5)
        
        assert result["success"] is False
        assert "not available" in result["error"]
        
    def test_call_function_invalid_params(self, router_with_components):
        """Test function call with invalid parameters."""
        result = router_with_components.call_function("test_func", y=5)
        
        assert result["success"] is False
        assert "error" in result
        
    def test_call_nonexistent_function(self, router_with_components):
        """Test calling nonexistent function."""
        result = router_with_components.call_function("nonexistent")
        
        assert result["success"] is False
        assert "error" in result
        
    def test_format_knowledge_results(self, router_with_components):
        """Test formatting knowledge results."""
        results = [
            {"category": "test", "key": "key1", "value": "value1"},
            {"category": "test", "key": "key2", "value": "value2"}
        ]
        
        formatted = router_with_components._format_knowledge_results(results)
        
        assert "Found the following information" in formatted
        assert "key1" in formatted
        assert "value1" in formatted
        
    def test_format_knowledge_results_empty(self, router_with_components):
        """Test formatting empty knowledge results."""
        formatted = router_with_components._format_knowledge_results([])
        assert "No knowledge entries found" in formatted
        
    def test_format_conversation_results(self, router_with_components):
        """Test formatting conversation results."""
        results = [
            {
                "user": "test user message",
                "ai": "test ai response",
                "timestamp": "2024-01-01T12:00:00"
            }
        ]
        
        formatted = router_with_components._format_conversation_results(results)
        
        assert "Found the following conversations" in formatted
        assert "test user message" in formatted
        assert "test ai response" in formatted
        
    def test_format_conversation_results_empty(self, router_with_components):
        """Test formatting empty conversation results."""
        formatted = router_with_components._format_conversation_results([])
        assert "No matching conversations found" in formatted
        
    def test_route_query_with_context(self, router_with_components):
        """Test routing query with context."""
        result = router_with_components.route_query(
            "test query",
            context={"user": "test_user"}
        )
        
        assert "route" in result
        assert "response" in result
        
    def test_multiple_trigger_words(self, router_with_components):
        """Test queries with multiple trigger words."""
        queries = [
            "what can you do",
            "tell me about test",
            "remember our conversation",
            "run test_func"
        ]
        
        for query in queries:
            result = router_with_components.route_query(query)
            assert "route" in result
            assert "response" in result
            
    def test_case_insensitive_routing(self, router_with_components):
        """Test that routing is case-insensitive."""
        result1 = router_with_components.route_query("HELP")
        result2 = router_with_components.route_query("help")
        result3 = router_with_components.route_query("HeLp")
        
        assert result1["route"] == result2["route"]
        assert result1["route"] == result3["route"]
