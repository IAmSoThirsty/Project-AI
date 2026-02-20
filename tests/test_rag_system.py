"""Tests for RAG (Retrieval-Augmented Generation) system."""

import tempfile
from pathlib import Path

import pytest

from app.core.rag_system import RAGSystem, RetrievalResult, TextChunk


class TestTextChunk:
    """Test TextChunk dataclass."""

    def test_chunk_creation(self):
        """Test creating a text chunk."""
        chunk = TextChunk(
            text="This is a test chunk",
            source="test.txt",
            chunk_id="abc123",
            metadata={"key": "value"},
        )
        assert chunk.text == "This is a test chunk"
        assert chunk.source == "test.txt"
        assert chunk.chunk_id == "abc123"
        assert chunk.metadata["key"] == "value"

    def test_chunk_serialization(self):
        """Test chunk to_dict and from_dict."""
        chunk = TextChunk(
            text="Test",
            source="file.txt",
            chunk_id="id123",
            metadata={"meta": "data"},
            embedding=[0.1, 0.2, 0.3],
        )

        # Serialize
        chunk_dict = chunk.to_dict()
        assert chunk_dict["text"] == "Test"
        assert chunk_dict["embedding"] == [0.1, 0.2, 0.3]

        # Deserialize
        restored = TextChunk.from_dict(chunk_dict)
        assert restored.text == chunk.text
        assert restored.source == chunk.source
        assert restored.embedding == chunk.embedding


class TestRAGSystem:
    """Test RAG system functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def rag_system(self, temp_dir):
        """Create RAG system with temporary directory."""
        return RAGSystem(data_dir=temp_dir)

    @pytest.fixture
    def sample_knowledge_base(self, temp_dir):
        """Create sample knowledge base files."""
        kb_dir = Path(temp_dir) / "knowledge_base"
        kb_dir.mkdir()

        # Create sample documents
        doc1 = kb_dir / "company_info.txt"
        doc1.write_text("Peter Gibbons is the CEO of Initech. " "The company specializes in software development.")

        doc2 = kb_dir / "projects.md"
        doc2.write_text(
            "The TPS report project has a deadline of Q4 2025. " "This is a critical project for the company."
        )

        doc3 = kb_dir / "team.txt"
        doc3.write_text(
            "The engineering team consists of 10 developers. "
            "They work on various projects using Python and JavaScript."
        )

        return str(kb_dir)

    def test_initialization(self, rag_system):
        """Test RAG system initialization."""
        assert rag_system.model is not None
        assert rag_system.chunk_size == 500
        assert rag_system.chunk_overlap == 50
        assert len(rag_system.chunks) == 0

    def test_chunk_text(self, rag_system):
        """Test text chunking."""
        text = "a" * 1000  # Long text
        chunks = rag_system._chunk_text(text, "test.txt")

        assert len(chunks) > 1  # Should create multiple chunks
        # Check overlap
        assert chunks[0].text[-50:] == chunks[1].text[:50]

    def test_ingest_text(self, rag_system):
        """Test ingesting a single text document."""
        text = "This is a test document about artificial intelligence."
        num_chunks = rag_system.ingest_text(text, "test_doc.txt", metadata={"category": "test"})

        assert num_chunks >= 1
        assert len(rag_system.chunks) == num_chunks
        assert rag_system.chunks[0].source == "test_doc.txt"
        assert rag_system.chunks[0].metadata["category"] == "test"
        assert rag_system.chunks[0].embedding is not None

    def test_ingest_directory(self, rag_system, sample_knowledge_base):
        """Test ingesting multiple files from directory."""
        num_chunks = rag_system.ingest_directory(sample_knowledge_base)

        assert num_chunks > 0
        assert len(rag_system.chunks) == num_chunks

        # Check that different sources were ingested
        sources = {chunk.source for chunk in rag_system.chunks}
        assert len(sources) >= 2  # At least 2 different files

    def test_retrieve_relevant_chunks(self, rag_system, sample_knowledge_base):
        """Test retrieving relevant chunks for a query."""
        # Ingest knowledge base
        rag_system.ingest_directory(sample_knowledge_base)

        # Query about CEO
        results = rag_system.retrieve("Who is the CEO?", top_k=2)

        assert len(results) > 0
        assert isinstance(results[0], RetrievalResult)
        assert results[0].score > 0
        assert results[0].rank == 1

        # Check that relevant content was retrieved
        context = " ".join(r.chunk.text for r in results)
        assert "CEO" in context or "Gibbons" in context

    def test_retrieve_with_min_score(self, rag_system, sample_knowledge_base):
        """Test retrieval with minimum score threshold."""
        rag_system.ingest_directory(sample_knowledge_base)

        # Query with high minimum score
        results = rag_system.retrieve("Who is the CEO?", top_k=10, min_score=0.5)

        # All results should have score >= 0.5
        for result in results:
            assert result.score >= 0.5

    def test_build_context(self, rag_system, sample_knowledge_base):
        """Test building context string."""
        rag_system.ingest_directory(sample_knowledge_base)

        context = rag_system.build_context("CEO", top_k=2, max_length=500)

        assert isinstance(context, str)
        assert len(context) > 0
        assert len(context) <= 500 + 100  # Allow some overhead

    def test_retrieve_empty_index(self, rag_system):
        """Test retrieval on empty index."""
        results = rag_system.retrieve("test query")
        assert len(results) == 0

    def test_save_and_load_index(self, temp_dir):
        """Test index persistence."""
        # Create and populate RAG system
        rag1 = RAGSystem(data_dir=temp_dir)
        rag1.ingest_text("Test document for persistence", "persistence_test.txt")

        original_chunks = len(rag1.chunks)
        assert original_chunks > 0

        # Create new instance (should load from disk)
        rag2 = RAGSystem(data_dir=temp_dir)
        assert len(rag2.chunks) == original_chunks
        assert rag2.chunks[0].text == rag1.chunks[0].text

    def test_clear_index(self, rag_system):
        """Test clearing the index."""
        rag_system.ingest_text("Test text", "test.txt")
        assert len(rag_system.chunks) > 0

        rag_system.clear_index()
        assert len(rag_system.chunks) == 0

    def test_get_statistics(self, rag_system, sample_knowledge_base):
        """Test getting index statistics."""
        rag_system.ingest_directory(sample_knowledge_base)

        stats = rag_system.get_statistics()

        assert stats["total_chunks"] > 0
        assert stats["embedded_chunks"] == stats["total_chunks"]
        assert stats["unique_sources"] >= 2
        assert "embedding_model" in stats
        assert stats["chunk_size"] == 500

    def test_custom_chunk_size(self, temp_dir):
        """Test RAG system with custom chunk size."""
        rag = RAGSystem(data_dir=temp_dir, chunk_size=100, chunk_overlap=10)

        text = "a" * 500  # Long text
        chunks = rag._chunk_text(text, "test.txt")

        # With chunk_size=100 and overlap=10, we expect multiple chunks
        assert len(chunks) >= 4

    def test_metadata_preservation(self, rag_system):
        """Test that metadata is preserved through ingestion."""
        custom_metadata = {
            "author": "Test Author",
            "date": "2025-12-20",
            "category": "documentation",
        }

        rag_system.ingest_text("Test document", "meta_test.txt", metadata=custom_metadata)

        chunk = rag_system.chunks[0]
        assert chunk.metadata["author"] == "Test Author"
        assert chunk.metadata["date"] == "2025-12-20"
        assert chunk.metadata["category"] == "documentation"

    def test_query_with_llm_no_openai(self, rag_system, sample_knowledge_base):
        """Test LLM query when OpenAI is not available."""
        rag_system.ingest_directory(sample_knowledge_base)

        # This should handle the case gracefully
        result = rag_system.query_with_llm("Who is the CEO?")

        assert "answer" in result
        assert "context" in result
        assert "chunks_used" in result

    def test_large_text_chunking(self, rag_system):
        """Test chunking of large text documents."""
        # Create a large document
        large_text = " ".join([f"Sentence {i}." for i in range(500)])

        num_chunks = rag_system.ingest_text(large_text, "large_doc.txt")

        # Should create multiple chunks
        assert num_chunks > 5
        assert all(chunk.embedding is not None for chunk in rag_system.chunks)

    def test_special_characters_handling(self, rag_system):
        """Test handling of special characters in text."""
        text = "Test with special chars: émojis 🚀, symbols $%&, and unicode 你好"

        num_chunks = rag_system.ingest_text(text, "special.txt")

        assert num_chunks > 0
        assert rag_system.chunks[0].text == text
        assert rag_system.chunks[0].embedding is not None

    def test_empty_text_handling(self, rag_system):
        """Test handling of empty or very short text."""
        # Very short text (< 50 chars should be skipped)
        text = "abc"

        num_chunks = rag_system.ingest_text(text, "short.txt")

        # Should not create chunks for very short text
        assert num_chunks == 0

    def test_retrieve_ranking(self, rag_system):
        """Test that retrieval results are properly ranked."""
        # Add documents with varying relevance
        rag_system.ingest_text("Python programming language is great", "doc1.txt")
        rag_system.ingest_text("Java is also a programming language", "doc2.txt")
        rag_system.ingest_text("Python is used for data science and AI", "doc3.txt")

        results = rag_system.retrieve("Python programming", top_k=3)

        # Check ranking is correct
        assert len(results) > 0
        assert results[0].rank == 1
        if len(results) > 1:
            assert results[0].score >= results[1].score
            assert results[1].rank == 2


class TestRAGConvenienceFunctions:
    """Test convenience functions."""

    def test_create_rag_system(self, tmp_path):
        """Test create_rag_system convenience function."""
        from app.core.rag_system import create_rag_system

        rag = create_rag_system(data_dir=str(tmp_path))

        assert rag is not None
        assert isinstance(rag, RAGSystem)
        assert rag.model is not None

    def test_quick_ingest_and_query(self, tmp_path):
        """Test quick_ingest_and_query convenience function."""
        from app.core.rag_system import quick_ingest_and_query

        # Create sample directory
        kb_dir = tmp_path / "kb"
        kb_dir.mkdir()
        (kb_dir / "test.txt").write_text("This is a test document")

        # Should work without errors
        results = quick_ingest_and_query(str(kb_dir), "test", top_k=1)

        assert isinstance(results, list)
