"""Tests for enhanced MemoryExpansionSystem query capabilities."""

import tempfile

import pytest

from app.core.ai_systems import MemoryExpansionSystem


class TestMemoryQueryCapabilities:
    """Test memory system query enhancements."""

    @pytest.fixture
    def memory(self):
        """Create memory system with test data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mem = MemoryExpansionSystem(data_dir=tmpdir)

            # Add some test knowledge
            mem.add_knowledge("preferences", "color", "blue")
            mem.add_knowledge("preferences", "language", "Python")
            mem.add_knowledge("skills", "programming", "advanced")
            mem.add_knowledge("skills", "design", "intermediate")
            mem.add_knowledge("facts", "capital_france", "Paris")
            mem.add_knowledge("facts", "python_creator", "Guido van Rossum")

            # Add some test conversations
            mem.log_conversation("What is Python?", "Python is a programming language.")
            mem.log_conversation(
                "Tell me about Paris", "Paris is the capital of France."
            )
            mem.log_conversation(
                "How do I learn Python?",
                "Start with the basics and practice regularly.",
            )

            yield mem

    def test_query_knowledge_by_key(self, memory):
        """Test querying knowledge by key match."""
        results = memory.query_knowledge("color")

        assert len(results) == 1
        assert results[0]["key"] == "color"
        assert results[0]["value"] == "blue"
        assert results[0]["category"] == "preferences"
        assert results[0]["match_type"] == "key"

    def test_query_knowledge_by_value(self, memory):
        """Test querying knowledge by value match."""
        results = memory.query_knowledge("Python")

        # Should match both "language" -> "Python" and "python_creator" -> "Guido van Rossum"
        assert len(results) >= 1

        # Check that we found the language preference
        python_matches = [r for r in results if r["value"] == "Python"]
        assert len(python_matches) == 1
        assert python_matches[0]["match_type"] == "value"

    def test_query_knowledge_case_insensitive(self, memory):
        """Test that knowledge queries are case-insensitive."""
        results_lower = memory.query_knowledge("python")
        results_upper = memory.query_knowledge("PYTHON")
        results_mixed = memory.query_knowledge("PyThOn")

        # All should return same results
        assert len(results_lower) == len(results_upper)
        assert len(results_lower) == len(results_mixed)

    def test_query_knowledge_with_category_filter(self, memory):
        """Test querying knowledge within specific category."""
        # Search for "programming" only in "skills" category
        results = memory.query_knowledge("programming", category="skills")

        assert len(results) == 1
        assert results[0]["category"] == "skills"
        assert results[0]["key"] == "programming"

    def test_query_knowledge_with_limit(self, memory):
        """Test query limit parameter."""
        # Add more data
        for i in range(20):
            memory.add_knowledge("test", f"key{i}", f"value{i}")

        # Query should respect limit
        results = memory.query_knowledge("key", limit=5)
        assert len(results) <= 5

    def test_query_knowledge_no_matches(self, memory):
        """Test query with no matches returns empty list."""
        results = memory.query_knowledge("nonexistent_query_xyz")
        assert len(results) == 0

    def test_query_knowledge_nonexistent_category(self, memory):
        """Test querying nonexistent category returns empty list."""
        results = memory.query_knowledge("test", category="nonexistent")
        assert len(results) == 0

    def test_search_conversations_in_user_messages(self, memory):
        """Test searching conversation user messages."""
        results = memory.search_conversations(
            "Python", search_user=True, search_ai=False
        )

        assert len(results) >= 1
        # Should find "What is Python?" and "How do I learn Python?"
        assert any("Python" in r["user"] for r in results)
        assert all("user" in r["match_location"] for r in results)

    def test_search_conversations_in_ai_responses(self, memory):
        """Test searching conversation AI responses."""
        results = memory.search_conversations(
            "programming", search_user=False, search_ai=True
        )

        assert len(results) >= 1
        assert any("programming" in r["ai"] for r in results)
        assert all("ai" in r["match_location"] for r in results)

    def test_search_conversations_both(self, memory):
        """Test searching both user and AI messages."""
        results = memory.search_conversations("Paris", search_user=True, search_ai=True)

        assert len(results) >= 1
        # Should find matches in both user message and AI response

    def test_search_conversations_case_insensitive(self, memory):
        """Test conversation search is case-insensitive."""
        results_lower = memory.search_conversations("python")
        results_upper = memory.search_conversations("PYTHON")

        assert len(results_lower) == len(results_upper)

    def test_search_conversations_with_limit(self, memory):
        """Test conversation search respects limit."""
        # Add more conversations
        for i in range(20):
            memory.log_conversation(f"Question {i}", f"Answer {i}")

        results = memory.search_conversations("Question", limit=5)
        assert len(results) <= 5

    def test_search_conversations_chronological_order(self, memory):
        """Test conversation search returns most recent first."""
        # Add conversations in sequence
        memory.log_conversation("First test message", "Response 1")
        memory.log_conversation("Second test message", "Response 2")
        memory.log_conversation("Third test message", "Response 3")

        results = memory.search_conversations("test message")

        # Most recent should be first
        assert "Third" in results[0]["user"]
        assert "Second" in results[1]["user"]
        assert "First" in results[2]["user"]

    def test_search_conversations_no_matches(self, memory):
        """Test conversation search with no matches returns empty list."""
        results = memory.search_conversations("xyz_nonexistent_query_abc")
        assert len(results) == 0

    def test_get_all_categories(self, memory):
        """Test getting list of all categories."""
        categories = memory.get_all_categories()

        assert "preferences" in categories
        assert "skills" in categories
        assert "facts" in categories

    def test_get_category_summary(self, memory):
        """Test getting summary of a category."""
        summary = memory.get_category_summary("preferences")

        assert summary is not None
        assert summary["category"] == "preferences"
        assert summary["entries"] == 2  # color and language
        assert "color" in summary["keys"]
        assert "language" in summary["keys"]
        assert summary["total_keys"] == 2

    def test_get_category_summary_nonexistent(self, memory):
        """Test getting summary for nonexistent category returns None."""
        summary = memory.get_category_summary("nonexistent")
        assert summary is None

    def test_get_category_summary_large_category(self):
        """Test category summary with many entries shows preview."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mem = MemoryExpansionSystem(data_dir=tmpdir)

            # Add many entries
            for i in range(20):
                mem.add_knowledge("large_cat", f"key{i}", f"value{i}")

            summary = mem.get_category_summary("large_cat")

            assert summary["total_keys"] == 20
            assert len(summary["keys"]) == 10  # Only first 10 in preview

    def test_query_knowledge_partial_match(self, memory):
        """Test that queries match partial strings."""
        # "paris" should match "capital_france" -> "Paris"
        results = memory.query_knowledge("paris")

        assert len(results) >= 1
        paris_result = [r for r in results if "Paris" in str(r["value"])]
        assert len(paris_result) > 0

    def test_integration_query_after_add(self):
        """Test querying knowledge immediately after adding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mem = MemoryExpansionSystem(data_dir=tmpdir)

            # Add and immediately query
            mem.add_knowledge("test", "new_key", "new_value")
            results = mem.query_knowledge("new_key")

            assert len(results) == 1
            assert results[0]["value"] == "new_value"

    def test_integration_search_after_conversation(self):
        """Test searching conversations immediately after logging."""
        with tempfile.TemporaryDirectory() as tmpdir:
            mem = MemoryExpansionSystem(data_dir=tmpdir)

            # Log and immediately search
            mem.log_conversation("Test user message", "Test AI response")
            results = mem.search_conversations("Test")

            assert len(results) >= 1
