"""Tests for Local Fallback Offline (FBO) system."""

import json
import tempfile

import pytest

from app.core.local_fbo import (
    LocalFBOSystem,
    OfflineContext,
    ReflectionEntry,
    create_local_fbo,
    quick_offline_query,
)


class TestReflectionEntry:
    """Test ReflectionEntry dataclass."""

    def test_reflection_creation(self):
        """Test creating a reflection entry."""
        reflection = ReflectionEntry(
            content="Learned something new",
            timestamp="2025-12-20T00:00:00",
            category="learning",
            confidence=0.9,
            source="user_interaction",
            tags=["important", "ai"],
        )

        assert reflection.content == "Learned something new"
        assert reflection.category == "learning"
        assert reflection.confidence == 0.9
        assert "important" in reflection.tags

    def test_reflection_serialization(self):
        """Test reflection to_dict and from_dict."""
        reflection = ReflectionEntry(
            content="Test reflection",
            timestamp="2025-12-20",
            category="insight",
            confidence=0.8,
            source="test",
        )

        # Serialize
        data = reflection.to_dict()
        assert data["content"] == "Test reflection"
        assert data["category"] == "insight"

        # Deserialize
        restored = ReflectionEntry.from_dict(data)
        assert restored.content == reflection.content
        assert restored.confidence == reflection.confidence


class TestLocalFBOSystem:
    """Test Local FBO system."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def fbo_system(self, temp_dir):
        """Create FBO system instance."""
        return LocalFBOSystem(
            data_dir=temp_dir, enable_rag=False, enable_reflection=True
        )

    def test_initialization(self, fbo_system):
        """Test FBO system initialization."""
        assert fbo_system.enable_reflection is True
        assert isinstance(fbo_system.reflections, list)
        assert isinstance(fbo_system.response_cache, dict)
        assert isinstance(fbo_system.offline_knowledge, dict)

    def test_initialization_with_rag(self, temp_dir):
        """Test initialization with RAG enabled."""
        # This might fail if sentence-transformers not installed
        # That's expected for minimal installation
        fbo = LocalFBOSystem(data_dir=temp_dir, enable_rag=True)
        # Should initialize without error even if RAG unavailable
        assert fbo is not None

    def test_check_connectivity(self, fbo_system):
        """Test connectivity check."""
        # May return True or False depending on environment
        result = fbo_system.check_connectivity()
        assert isinstance(result, bool)

    def test_get_context(self, fbo_system):
        """Test getting offline context."""
        context = fbo_system.get_context()

        assert isinstance(context, OfflineContext)
        assert isinstance(context.is_online, bool)
        assert context.local_knowledge_size == 0  # Initially empty
        assert context.reflection_count == 0
        assert context.cached_responses == 0

    def test_add_offline_knowledge(self, fbo_system):
        """Test adding offline knowledge."""
        fbo_system.add_offline_knowledge(
            "test_key", "test_value", category="test"
        )

        assert "test" in fbo_system.offline_knowledge
        assert "test_key" in fbo_system.offline_knowledge["test"]
        assert (
            fbo_system.offline_knowledge["test"]["test_key"] == "test_value"
        )

    def test_offline_knowledge_persistence(self, temp_dir):
        """Test that offline knowledge persists."""
        # Create system and add knowledge
        fbo1 = LocalFBOSystem(data_dir=temp_dir)
        fbo1.add_offline_knowledge("key1", "value1", "category1")

        # Create new instance (should load from disk)
        fbo2 = LocalFBOSystem(data_dir=temp_dir)
        assert "category1" in fbo2.offline_knowledge
        assert fbo2.offline_knowledge["category1"]["key1"] == "value1"

    def test_add_reflection(self, fbo_system):
        """Test adding a reflection."""
        reflection = fbo_system.add_reflection(
            content="Test reflection",
            category="insight",
            confidence=0.8,
            source="test",
            tags=["test", "important"],
        )

        assert isinstance(reflection, ReflectionEntry)
        assert reflection.content == "Test reflection"
        assert reflection.category == "insight"
        assert len(fbo_system.reflections) == 1

    def test_reflection_persistence(self, temp_dir):
        """Test reflection persistence."""
        # Add reflections
        fbo1 = LocalFBOSystem(data_dir=temp_dir)
        fbo1.add_reflection("Reflection 1", category="learning")
        fbo1.add_reflection("Reflection 2", category="insight")

        # Create new instance
        fbo2 = LocalFBOSystem(data_dir=temp_dir)
        assert len(fbo2.reflections) == 2

    def test_search_reflections_by_category(self, fbo_system):
        """Test searching reflections by category."""
        fbo_system.add_reflection("Learning 1", category="learning")
        fbo_system.add_reflection("Insight 1", category="insight")
        fbo_system.add_reflection("Learning 2", category="learning")

        results = fbo_system.search_reflections(category="learning")
        assert len(results) == 2
        assert all(r.category == "learning" for r in results)

    def test_search_reflections_by_query(self, fbo_system):
        """Test searching reflections by text."""
        fbo_system.add_reflection("Python programming is great")
        fbo_system.add_reflection("Java is also good")
        fbo_system.add_reflection("Python is versatile")

        results = fbo_system.search_reflections(query="Python")
        assert len(results) == 2

    def test_search_reflections_with_limit(self, fbo_system):
        """Test reflection search with limit."""
        for i in range(20):
            fbo_system.add_reflection(f"Reflection {i}")

        results = fbo_system.search_reflections(limit=5)
        assert len(results) == 5

    def test_reflect_on_patterns(self, fbo_system):
        """Test pattern analysis."""
        # Add various reflections
        for i in range(5):
            fbo_system.add_reflection(
                f"Learning {i}", category="learning", tags=["python"]
            )

        patterns = fbo_system.reflect_on_patterns()
        assert isinstance(patterns, list)
        assert len(patterns) > 0

    def test_patterns_insufficient_data(self, fbo_system):
        """Test pattern analysis with insufficient data."""
        fbo_system.add_reflection("Only one reflection")

        patterns = fbo_system.reflect_on_patterns()
        assert "Insufficient data" in patterns[0]

    def test_query_offline_basic(self, fbo_system):
        """Test basic offline query without RAG."""
        # Add some knowledge
        fbo_system.add_offline_knowledge(
            "python", "A programming language", "languages"
        )

        result = fbo_system.query_offline("python")

        assert "answer" in result
        assert "source" in result
        assert result["source"] == "offline_basic"
        assert isinstance(result["confidence"], float)

    def test_query_offline_no_match(self, fbo_system):
        """Test offline query with no knowledge match."""
        result = fbo_system.query_offline("something unknown")

        assert "answer" in result
        assert "offline" in result["answer"].lower()
        assert result["confidence"] == 0.0

    def test_response_caching(self, fbo_system):
        """Test that responses are cached."""
        # First query
        result1 = fbo_system.query_offline("test query")
        assert result1["from_cache"] is False

        # Second query (should be cached)
        result2 = fbo_system.query_offline("test query")
        assert result2["from_cache"] is True

    def test_cache_persistence(self, temp_dir):
        """Test cache persistence across instances."""
        # Create system and query
        fbo1 = LocalFBOSystem(data_dir=temp_dir)
        fbo1.add_offline_knowledge("test", "value", "cat")
        fbo1.query_offline("test")

        # Create new instance
        fbo2 = LocalFBOSystem(data_dir=temp_dir)
        assert len(fbo2.response_cache) > 0

    def test_clear_cache(self, fbo_system):
        """Test clearing cache."""
        # Add some cached responses
        fbo_system.query_offline("query 1")
        fbo_system.query_offline("query 2")
        assert len(fbo_system.response_cache) > 0

        fbo_system.clear_cache()
        assert len(fbo_system.response_cache) == 0

    def test_prepare_for_offline(self, fbo_system):
        """Test preparing system for offline operation."""
        fbo_system.add_offline_knowledge("key", "value", "cat")
        fbo_system.add_reflection("Test reflection")

        fbo_system.prepare_for_offline()

        # Check that sync file was created
        sync_file = fbo_system.data_dir / "last_sync.json"
        assert sync_file.exists()

        # Verify sync time was saved
        with open(sync_file) as f:
            data = json.load(f)
            assert "timestamp" in data

    def test_sync_when_online(self, fbo_system):
        """Test sync operation."""
        result = fbo_system.sync_when_online()

        assert "success" in result
        assert "message" in result
        assert isinstance(result["success"], bool)

    def test_get_statistics(self, fbo_system):
        """Test getting system statistics."""
        fbo_system.add_offline_knowledge("key", "value", "cat")
        fbo_system.add_reflection("Reflection")
        fbo_system.query_offline("test")

        stats = fbo_system.get_statistics()

        assert "is_online" in stats
        assert "local_knowledge_entries" in stats
        assert "cached_responses" in stats
        assert "reflections" in stats
        assert stats["reflections"] == 1
        assert stats["local_knowledge_entries"] == 1

    def test_ingest_for_offline_no_rag(self, fbo_system):
        """Test ingest when RAG not available."""
        # Should not raise error
        fbo_system.ingest_for_offline(
            "Some text", "source", {"key": "value"}
        )

    def test_multiple_reflections_same_category(self, fbo_system):
        """Test adding multiple reflections in same category."""
        for i in range(10):
            fbo_system.add_reflection(
                f"Learning {i}", category="learning", confidence=0.7 + i * 0.01
            )

        learning_reflections = fbo_system.search_reflections(
            category="learning"
        )
        assert len(learning_reflections) == 10

    def test_reflection_tags(self, fbo_system):
        """Test reflection tagging system."""
        fbo_system.add_reflection(
            "Python is great", tags=["python", "programming", "learning"]
        )
        fbo_system.add_reflection("AI is fascinating", tags=["ai", "learning"])

        # Analyze patterns should detect common tags
        patterns = fbo_system.reflect_on_patterns()
        pattern_text = " ".join(patterns)
        assert "learning" in pattern_text.lower()

    def test_offline_context_updates(self, fbo_system):
        """Test that offline context updates correctly."""
        # Initially empty
        context1 = fbo_system.get_context()
        assert context1.reflection_count == 0

        # Add reflection
        fbo_system.add_reflection("Test")

        # Should update
        context2 = fbo_system.get_context()
        assert context2.reflection_count == 1

    def test_generate_cache_key(self, fbo_system):
        """Test cache key generation."""
        key1 = fbo_system._generate_cache_key("test query")
        key2 = fbo_system._generate_cache_key("TEST QUERY")
        key3 = fbo_system._generate_cache_key("different query")

        # Same query (case insensitive) should produce same key
        assert key1 == key2

        # Different query should produce different key
        assert key1 != key3


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_create_local_fbo(self, temp_dir):
        """Test create_local_fbo function."""
        fbo = create_local_fbo(data_dir=temp_dir, enable_all=True)

        assert isinstance(fbo, LocalFBOSystem)
        assert fbo.enable_reflection is True

    def test_create_local_fbo_disabled(self, temp_dir):
        """Test creating FBO with features disabled."""
        fbo = create_local_fbo(data_dir=temp_dir, enable_all=False)

        assert isinstance(fbo, LocalFBOSystem)
        assert fbo.enable_reflection is False

    def test_quick_offline_query(self, temp_dir):
        """Test quick offline query function."""
        # Add some knowledge first
        fbo = create_local_fbo(temp_dir)
        fbo.add_offline_knowledge("test", "Test value", "category")
        fbo.prepare_for_offline()

        # Now use quick query
        answer = quick_offline_query("test", data_dir=temp_dir)

        assert isinstance(answer, str)
        assert len(answer) > 0


class TestIntegration:
    """Integration tests for complete workflows."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_complete_offline_workflow(self, temp_dir):
        """Test complete offline operation workflow."""
        # Create system
        fbo = LocalFBOSystem(data_dir=temp_dir)

        # Add knowledge
        fbo.add_offline_knowledge("python", "Programming language", "tech")
        fbo.add_offline_knowledge("ai", "Artificial Intelligence", "tech")

        # Add reflections
        fbo.add_reflection(
            "User prefers Python", category="preference", tags=["python"]
        )
        fbo.add_reflection(
            "Interest in AI topics", category="interest", tags=["ai"]
        )

        # Query
        result = fbo.query_offline("python")
        assert result["answer"] is not None

        # Analyze patterns
        patterns = fbo.reflect_on_patterns()
        assert len(patterns) > 0

        # Get statistics
        stats = fbo.get_statistics()
        assert stats["reflections"] == 2
        assert stats["local_knowledge_entries"] == 1

        # Prepare for offline
        fbo.prepare_for_offline()

        # Verify persistence
        fbo2 = LocalFBOSystem(data_dir=temp_dir)
        assert len(fbo2.reflections) == 2
        assert len(fbo2.offline_knowledge) == 1

    def test_offline_online_transition(self, temp_dir):
        """Test transitioning between offline and online."""
        fbo = LocalFBOSystem(data_dir=temp_dir)

        # Add data while "online"
        fbo.add_offline_knowledge("key1", "value1", "cat1")
        fbo.prepare_for_offline()

        # Check offline context
        context = fbo.get_context()
        assert context.last_sync is not None

        # Query while "offline"
        result = fbo.query_offline("key1")
        assert result is not None

        # Sync when "back online"
        sync_result = fbo.sync_when_online()
        assert "success" in sync_result

    def test_reflection_based_learning(self, temp_dir):
        """Test learning through reflections."""
        fbo = LocalFBOSystem(data_dir=temp_dir)

        # Simulate learning process
        topics = ["python", "ai", "machine learning", "data science", "python"]

        for topic in topics:
            fbo.add_reflection(
                f"Discussed {topic}",
                category="learning",
                tags=[topic],
                confidence=0.8,
            )

        # Analyze what was learned
        patterns = fbo.reflect_on_patterns()

        # Should detect python as frequent topic
        pattern_text = " ".join(patterns)
        assert "python" in pattern_text.lower()

    def test_multi_category_knowledge(self, temp_dir):
        """Test organizing knowledge across categories."""
        fbo = LocalFBOSystem(data_dir=temp_dir)

        # Add knowledge in different categories
        categories = {
            "programming": {"python": "Language", "java": "Language"},
            "ai": {"ml": "Machine Learning", "dl": "Deep Learning"},
            "database": {"sql": "Query Language", "nosql": "Document DB"},
        }

        for category, items in categories.items():
            for key, value in items.items():
                fbo.add_offline_knowledge(key, value, category)

        # Verify organization
        stats = fbo.get_statistics()
        assert stats["local_knowledge_entries"] == len(categories)
