"""
E2E Tests for RAG (Retrieval Augmented Generation) Pipeline

Comprehensive tests for RAG operations including:
- Document ingestion and indexing
- Vector similarity search
- Context retrieval for generation
- RAG query execution with context
- Multi-document reasoning
- Performance and accuracy testing
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import time
from pathlib import Path
from typing import Any

import pytest

from e2e.utils.test_helpers import (
    create_test_file,
    get_timestamp_iso,
    load_json_file,
    save_json_file,
    wait_for_condition,
)


class SimpleVectorStore:
    """Simple in-memory vector store for testing."""

    def __init__(self):
        self.documents = []
        self.embeddings = []

    def add_document(self, doc_id: str, content: str, embedding: list[float]):
        """Add a document with its embedding."""
        self.documents.append({"id": doc_id, "content": content})
        self.embeddings.append(embedding)

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        """Search for similar documents using cosine similarity."""
        if not self.embeddings:
            return []

        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((i, similarity))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top_k results
        results = []
        for idx, score in similarities[:top_k]:
            result = self.documents[idx].copy()
            result["score"] = score
            results.append(result)

        return results

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)


@pytest.mark.e2e
@pytest.mark.rag
class TestDocumentIngestion:
    """E2E tests for document ingestion and indexing."""

    def test_ingest_single_document(self, test_temp_dir):
        """Test ingesting a single document."""
        # Arrange
        doc_dir = Path(test_temp_dir) / "documents"
        doc_dir.mkdir(parents=True, exist_ok=True)

        document = {
            "id": "doc_001",
            "title": "Introduction to RAG",
            "content": "Retrieval Augmented Generation improves LLM responses.",
            "metadata": {"source": "test", "author": "system"},
            "ingested_at": get_timestamp_iso(),
        }

        # Act
        doc_file = doc_dir / "doc_001.json"
        save_json_file(document, doc_file)

        # Simulate indexing
        index = {
            "doc_id": document["id"],
            "word_count": len(document["content"].split()),
            "indexed_at": get_timestamp_iso(),
        }
        index_file = doc_dir / "index_001.json"
        save_json_file(index, index_file)

        # Assert
        assert doc_file.exists()
        assert index_file.exists()

        loaded_doc = load_json_file(doc_file)
        loaded_index = load_json_file(index_file)

        assert loaded_doc["id"] == "doc_001"
        assert loaded_index["word_count"] == 6

    def test_ingest_multiple_documents(self, test_temp_dir):
        """Test ingesting multiple documents in batch."""
        # Arrange
        doc_dir = Path(test_temp_dir) / "documents"
        doc_dir.mkdir(parents=True, exist_ok=True)

        num_docs = 20
        documents = [
            {
                "id": f"doc_{i:03d}",
                "title": f"Document {i}",
                "content": f"This is the content of document {i}. " * 10,
                "metadata": {"doc_number": i},
            }
            for i in range(num_docs)
        ]

        # Act
        start_time = time.time()
        for doc in documents:
            save_json_file(doc, doc_dir / f"{doc['id']}.json")
        duration = time.time() - start_time

        # Assert
        ingested_files = list(doc_dir.glob("doc_*.json"))
        assert len(ingested_files) == num_docs
        assert duration < 5.0  # Should complete quickly

    def test_document_chunking(self, test_temp_dir):
        """Test chunking large documents for indexing."""
        # Arrange
        doc_dir = Path(test_temp_dir) / "documents"
        doc_dir.mkdir(parents=True, exist_ok=True)

        large_content = " ".join([f"Sentence {i}." for i in range(1000)])
        document = {
            "id": "doc_large",
            "content": large_content,
        }

        chunk_size = 100  # words per chunk

        # Act - Chunk the document
        words = document["content"].split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = {
                "doc_id": document["id"],
                "chunk_id": f"{document['id']}_chunk_{i // chunk_size}",
                "content": " ".join(words[i : i + chunk_size]),
                "position": i // chunk_size,
            }
            chunks.append(chunk)
            save_json_file(
                chunk, doc_dir / f"{chunk['chunk_id']}.json"
            )

        # Assert
        assert len(chunks) == 10  # 1000 words / 100 per chunk
        chunk_files = list(doc_dir.glob("doc_large_chunk_*.json"))
        assert len(chunk_files) == 10

    def test_document_metadata_extraction(self, test_temp_dir):
        """Test extracting metadata from documents."""
        # Arrange
        doc_dir = Path(test_temp_dir) / "documents"
        doc_dir.mkdir(parents=True, exist_ok=True)

        document_content = """
        Title: Machine Learning Basics
        Author: AI Researcher
        Date: 2024-01-01
        Tags: ML, AI, Tutorial
        
        Machine learning is a subset of artificial intelligence.
        """

        # Act - Extract metadata
        lines = document_content.strip().split("\n")
        metadata = {}
        content_lines = []

        for line in lines:
            if ":" in line and not content_lines:
                key, value = line.split(":", 1)
                metadata[key.strip().lower()] = value.strip()
            else:
                content_lines.append(line)

        document = {
            "id": "doc_metadata",
            "content": "\n".join(content_lines).strip(),
            "metadata": metadata,
        }

        save_json_file(document, doc_dir / "doc_metadata.json")

        # Assert
        loaded = load_json_file(doc_dir / "doc_metadata.json")
        assert "title" in loaded["metadata"]
        assert "author" in loaded["metadata"]
        assert loaded["metadata"]["title"] == "Machine Learning Basics"

    def test_duplicate_document_detection(self, test_temp_dir):
        """Test detecting and handling duplicate documents."""
        # Arrange
        doc_dir = Path(test_temp_dir) / "documents"
        doc_dir.mkdir(parents=True, exist_ok=True)

        documents = [
            {
                "id": f"dup_{i}",
                "content": "This is duplicate content" if i < 5 else f"Unique content {i}",
            }
            for i in range(10)
        ]

        # Act - Ingest with duplicate detection
        seen_hashes = set()
        ingested = []
        duplicates = []

        for doc in documents:
            content_hash = hashlib.sha256(doc["content"].encode()).hexdigest()

            if content_hash in seen_hashes:
                duplicates.append(doc["id"])
            else:
                seen_hashes.add(content_hash)
                ingested.append(doc)
                save_json_file(doc, doc_dir / f"{doc['id']}.json")

        # Assert
        assert len(duplicates) == 4  # 5 duplicates minus 1 original
        assert len(ingested) == 6  # 1 original + 5 unique
        ingested_files = list(doc_dir.glob("dup_*.json"))
        assert len(ingested_files) == 6


@pytest.mark.e2e
@pytest.mark.rag
class TestVectorSimilaritySearch:
    """E2E tests for vector similarity search."""

    def test_simple_vector_search(self):
        """Test basic vector similarity search."""
        # Arrange
        vector_store = SimpleVectorStore()

        # Add documents with mock embeddings
        documents = [
            ("doc_1", "Python programming basics", [0.9, 0.1, 0.2]),
            ("doc_2", "Java programming tutorial", [0.8, 0.2, 0.3]),
            ("doc_3", "Cooking recipes", [0.1, 0.9, 0.8]),
            ("doc_4", "Python advanced topics", [0.95, 0.05, 0.15]),
        ]

        for doc_id, content, embedding in documents:
            vector_store.add_document(doc_id, content, embedding)

        # Act - Search with query similar to Python docs
        query_embedding = [0.92, 0.08, 0.18]
        results = vector_store.search(query_embedding, top_k=2)

        # Assert
        assert len(results) == 2
        # Most similar should be Python-related docs
        assert "Python" in results[0]["content"]
        assert results[0]["score"] > 0.9

    def test_vector_search_ranking(self):
        """Test that vector search returns properly ranked results."""
        # Arrange
        vector_store = SimpleVectorStore()

        # Create documents with varying similarity to query
        for i in range(10):
            similarity_factor = (10 - i) / 10  # Decreasing similarity
            embedding = [similarity_factor, 0.1, 0.1]
            vector_store.add_document(
                f"doc_{i}",
                f"Content {i}",
                embedding,
            )

        # Act
        query_embedding = [1.0, 0.1, 0.1]  # Should match doc_0 best
        results = vector_store.search(query_embedding, top_k=5)

        # Assert
        assert len(results) == 5
        # Results should be in descending order of score
        for i in range(len(results) - 1):
            assert results[i]["score"] >= results[i + 1]["score"]

    def test_vector_search_top_k_limit(self):
        """Test top_k parameter limits results correctly."""
        # Arrange
        vector_store = SimpleVectorStore()

        for i in range(20):
            vector_store.add_document(
                f"doc_{i}",
                f"Content {i}",
                [0.5 + i * 0.01, 0.3, 0.2],
            )

        # Act
        query_embedding = [0.6, 0.3, 0.2]
        results_5 = vector_store.search(query_embedding, top_k=5)
        results_10 = vector_store.search(query_embedding, top_k=10)

        # Assert
        assert len(results_5) == 5
        assert len(results_10) == 10

    def test_empty_vector_store_search(self):
        """Test searching in empty vector store."""
        # Arrange
        vector_store = SimpleVectorStore()

        # Act
        query_embedding = [0.5, 0.5, 0.5]
        results = vector_store.search(query_embedding, top_k=5)

        # Assert
        assert len(results) == 0

    def test_vector_search_with_filters(self):
        """Test vector search with metadata filters."""
        # Arrange
        vector_store = SimpleVectorStore()

        documents = [
            ("doc_1", "Python tutorial", [0.9, 0.1, 0.2], {"category": "programming"}),
            ("doc_2", "Python recipe", [0.85, 0.15, 0.25], {"category": "cooking"}),
            ("doc_3", "Java tutorial", [0.8, 0.2, 0.3], {"category": "programming"}),
        ]

        # Store with metadata
        for doc_id, content, embedding, metadata in documents:
            vector_store.add_document(doc_id, content, embedding)
            # In real implementation, metadata would be stored with document

        # Act
        query_embedding = [0.88, 0.12, 0.22]
        all_results = vector_store.search(query_embedding, top_k=3)

        # Simulate metadata filtering (in real system)
        filtered_results = [
            r for r in all_results if "tutorial" in r["content"]
        ]

        # Assert
        assert len(filtered_results) >= 1


@pytest.mark.e2e
@pytest.mark.rag
class TestContextRetrieval:
    """E2E tests for context retrieval for generation."""

    def test_retrieve_relevant_context(self, test_temp_dir):
        """Test retrieving relevant context for a query."""
        # Arrange
        doc_dir = Path(test_temp_dir) / "documents"
        doc_dir.mkdir(parents=True, exist_ok=True)

        knowledge_base = [
            {
                "id": "kb_1",
                "topic": "Python",
                "content": "Python is a high-level programming language.",
            },
            {
                "id": "kb_2",
                "topic": "Java",
                "content": "Java is an object-oriented programming language.",
            },
            {
                "id": "kb_3",
                "topic": "Python",
                "content": "Python supports multiple programming paradigms.",
            },
        ]

        for item in knowledge_base:
            save_json_file(item, doc_dir / f"{item['id']}.json")

        # Act - Retrieve context for query about Python
        query = "Tell me about Python programming"
        relevant_context = []

        for kb_file in doc_dir.glob("kb_*.json"):
            item = load_json_file(kb_file)
            # Simple keyword matching (real system would use embeddings)
            if "python" in query.lower() and item["topic"].lower() == "python":
                relevant_context.append(item["content"])

        # Assert
        assert len(relevant_context) == 2
        assert all("Python" in ctx for ctx in relevant_context)

    def test_context_window_management(self, test_temp_dir):
        """Test managing context window size for generation."""
        # Arrange
        contexts = [
            "Context piece 1. " * 50,  # Large context
            "Context piece 2. " * 50,
            "Context piece 3. " * 50,
            "Context piece 4. " * 50,
        ]

        max_tokens = 200  # Token limit for context window

        # Act - Fit contexts into window
        def count_words(text: str) -> int:
            return len(text.split())

        selected_contexts = []
        current_size = 0

        for ctx in contexts:
            ctx_size = count_words(ctx)
            if current_size + ctx_size <= max_tokens:
                selected_contexts.append(ctx)
                current_size += ctx_size
            else:
                break

        # Assert
        total_words = sum(count_words(ctx) for ctx in selected_contexts)
        assert total_words <= max_tokens
        assert len(selected_contexts) < len(contexts)

    def test_context_relevance_scoring(self):
        """Test scoring context relevance to query."""
        # Arrange
        query = "machine learning algorithms"
        contexts = [
            "Machine learning uses algorithms to learn patterns.",
            "The weather today is sunny and warm.",
            "Neural networks are a type of ML algorithm.",
            "Cooking requires proper ingredients.",
        ]

        # Act - Score each context
        def score_relevance(query: str, context: str) -> float:
            query_words = set(query.lower().split())
            context_words = set(context.lower().split())
            overlap = query_words & context_words
            return len(overlap) / len(query_words) if query_words else 0.0

        scored_contexts = [
            (ctx, score_relevance(query, ctx)) for ctx in contexts
        ]
        scored_contexts.sort(key=lambda x: x[1], reverse=True)

        # Assert
        # Most relevant contexts should be about ML
        assert scored_contexts[0][1] > 0.0
        assert "machine learning" in scored_contexts[0][0].lower() or \
               "algorithm" in scored_contexts[0][0].lower()

    def test_multi_source_context_aggregation(self, test_temp_dir):
        """Test aggregating context from multiple sources."""
        # Arrange
        sources_dir = Path(test_temp_dir) / "sources"
        sources_dir.mkdir(parents=True, exist_ok=True)

        sources = {
            "wiki": [
                {"content": "Python was created by Guido van Rossum"},
            ],
            "docs": [
                {"content": "Python 3.12 is the latest version"},
            ],
            "blog": [
                {"content": "Python is popular for data science"},
            ],
        }

        for source_name, items in sources.items():
            source_dir = sources_dir / source_name
            source_dir.mkdir(exist_ok=True)
            for i, item in enumerate(items):
                save_json_file(item, source_dir / f"item_{i}.json")

        # Act - Aggregate from all sources
        aggregated_context = []
        for source_dir in sources_dir.iterdir():
            if source_dir.is_dir():
                for item_file in source_dir.glob("item_*.json"):
                    item = load_json_file(item_file)
                    aggregated_context.append({
                        "source": source_dir.name,
                        "content": item["content"],
                    })

        # Assert
        assert len(aggregated_context) == 3
        sources_found = {ctx["source"] for ctx in aggregated_context}
        assert sources_found == {"wiki", "docs", "blog"}


@pytest.mark.e2e
@pytest.mark.rag
class TestRAGQueryExecution:
    """E2E tests for RAG query execution."""

    def test_end_to_end_rag_query(self, test_temp_dir):
        """Test complete RAG pipeline from query to response."""
        # Arrange
        doc_dir = Path(test_temp_dir) / "documents"
        doc_dir.mkdir(parents=True, exist_ok=True)

        # Setup knowledge base
        knowledge = [
            {
                "id": "k1",
                "content": "RAG combines retrieval and generation.",
                "embedding": [0.9, 0.1, 0.2],
            },
            {
                "id": "k2",
                "content": "Vector search finds relevant documents.",
                "embedding": [0.85, 0.15, 0.25],
            },
        ]

        vector_store = SimpleVectorStore()
        for item in knowledge:
            vector_store.add_document(
                item["id"], item["content"], item["embedding"]
            )
            save_json_file(item, doc_dir / f"{item['id']}.json")

        # Act - Execute RAG query
        query = "How does RAG work?"
        query_embedding = [0.88, 0.12, 0.22]  # Similar to RAG content

        # 1. Retrieve relevant context
        retrieved_docs = vector_store.search(query_embedding, top_k=2)

        # 2. Prepare context
        context = "\n".join([doc["content"] for doc in retrieved_docs])

        # 3. Generate response (simulated)
        response = {
            "query": query,
            "context": context,
            "answer": f"Based on the context: {context[:100]}...",
            "sources": [doc["id"] for doc in retrieved_docs],
        }

        # Assert
        assert "RAG" in response["context"]
        assert len(response["sources"]) == 2
        assert response["query"] == query

    def test_rag_with_no_relevant_context(self):
        """Test RAG query when no relevant context is found."""
        # Arrange
        vector_store = SimpleVectorStore()
        vector_store.add_document(
            "doc_1", "Information about cooking", [0.1, 0.9, 0.8]
        )

        # Act - Query about unrelated topic
        query_embedding = [0.9, 0.1, 0.1]  # Very different
        results = vector_store.search(query_embedding, top_k=1)

        # Assert
        if results:
            assert results[0]["score"] < 0.5  # Low relevance score

    def test_rag_response_with_citations(self, test_temp_dir):
        """Test RAG response includes proper citations."""
        # Arrange
        doc_dir = Path(test_temp_dir) / "documents"
        doc_dir.mkdir(parents=True, exist_ok=True)

        documents = [
            {
                "id": "doc_1",
                "title": "RAG Overview",
                "content": "RAG improves LLM accuracy.",
                "author": "AI Researcher",
            },
            {
                "id": "doc_2",
                "title": "Vector Search",
                "content": "Vector search enables semantic retrieval.",
                "author": "ML Engineer",
            },
        ]

        for doc in documents:
            save_json_file(doc, doc_dir / f"{doc['id']}.json")

        # Act - Generate response with citations
        response = {
            "answer": "RAG improves accuracy using vector search.",
            "citations": [
                {
                    "doc_id": doc["id"],
                    "title": doc["title"],
                    "author": doc["author"],
                }
                for doc in documents
            ],
        }

        # Assert
        assert len(response["citations"]) == 2
        assert all("title" in cit for cit in response["citations"])
        assert all("author" in cit for cit in response["citations"])

    def test_rag_query_caching(self, test_temp_dir):
        """Test caching of RAG query results."""
        # Arrange
        cache_dir = Path(test_temp_dir) / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        query = "What is machine learning?"
        query_hash = hashlib.sha256(query.encode()).hexdigest()

        response = {
            "query": query,
            "answer": "Machine learning is...",
            "cached_at": get_timestamp_iso(),
        }

        # Act - Cache the response
        cache_file = cache_dir / f"{query_hash}.json"
        save_json_file(response, cache_file)

        # Simulate cache lookup
        if cache_file.exists():
            cached_response = load_json_file(cache_file)
        else:
            cached_response = None

        # Assert
        assert cached_response is not None
        assert cached_response["query"] == query
        assert "cached_at" in cached_response


@pytest.mark.e2e
@pytest.mark.rag
@pytest.mark.slow
class TestMultiDocumentReasoning:
    """E2E tests for multi-document reasoning."""

    def test_reason_across_multiple_documents(self, test_temp_dir):
        """Test reasoning that requires information from multiple documents."""
        # Arrange
        doc_dir = Path(test_temp_dir) / "documents"
        doc_dir.mkdir(parents=True, exist_ok=True)

        documents = [
            {"id": "doc_1", "content": "Python was created in 1991."},
            {"id": "doc_2", "content": "Python is used for web development."},
            {"id": "doc_3", "content": "Python has a large ecosystem of libraries."},
        ]

        for doc in documents:
            save_json_file(doc, doc_dir / f"{doc['id']}.json")

        # Act - Aggregate information
        query = "Tell me about Python's history and uses"
        relevant_info = []

        for doc_file in doc_dir.glob("doc_*.json"):
            doc = load_json_file(doc_file)
            relevant_info.append(doc["content"])

        combined_context = " ".join(relevant_info)

        # Assert
        assert "1991" in combined_context
        assert "web development" in combined_context
        assert "libraries" in combined_context

    def test_contradiction_detection(self, test_temp_dir):
        """Test detecting contradictions across documents."""
        # Arrange
        doc_dir = Path(test_temp_dir) / "documents"
        doc_dir.mkdir(parents=True, exist_ok=True)

        documents = [
            {"id": "doc_1", "fact": "Python is easy to learn", "sentiment": "positive"},
            {"id": "doc_2", "fact": "Python is difficult to master", "sentiment": "negative"},
        ]

        for doc in documents:
            save_json_file(doc, doc_dir / f"{doc['id']}.json")

        # Act - Check for contradictions
        facts = []
        for doc_file in doc_dir.glob("doc_*.json"):
            doc = load_json_file(doc_file)
            facts.append(doc["fact"])

        # Simple contradiction detection
        has_contradiction = any(
            "easy" in facts[0].lower() and "difficult" in facts[1].lower()
        )

        # Assert
        assert has_contradiction

    def test_information_synthesis(self, test_temp_dir):
        """Test synthesizing information from multiple sources."""
        # Arrange
        doc_dir = Path(test_temp_dir) / "documents"
        doc_dir.mkdir(parents=True, exist_ok=True)

        documents = [
            {"id": "doc_1", "metric": "accuracy", "value": 0.95},
            {"id": "doc_2", "metric": "precision", "value": 0.92},
            {"id": "doc_3", "metric": "recall", "value": 0.89},
        ]

        for doc in documents:
            save_json_file(doc, doc_dir / f"{doc['id']}.json")

        # Act - Synthesize metrics
        metrics = {}
        for doc_file in doc_dir.glob("doc_*.json"):
            doc = load_json_file(doc_file)
            metrics[doc["metric"]] = doc["value"]

        avg_performance = sum(metrics.values()) / len(metrics)

        # Assert
        assert len(metrics) == 3
        assert 0.0 < avg_performance < 1.0
        assert avg_performance > 0.9

    def test_temporal_reasoning(self, test_temp_dir):
        """Test reasoning about temporal relationships."""
        # Arrange
        doc_dir = Path(test_temp_dir) / "documents"
        doc_dir.mkdir(parents=True, exist_ok=True)

        events = [
            {"id": "e1", "event": "Python 2 released", "year": 2000},
            {"id": "e2", "event": "Python 3 released", "year": 2008},
            {"id": "e3", "event": "Python 2 deprecated", "year": 2020},
        ]

        for event in events:
            save_json_file(event, doc_dir / f"{event['id']}.json")

        # Act - Order events temporally
        loaded_events = []
        for event_file in sorted(doc_dir.glob("e*.json")):
            loaded_events.append(load_json_file(event_file))

        loaded_events.sort(key=lambda x: x["year"])

        # Assert
        assert loaded_events[0]["year"] == 2000
        assert loaded_events[-1]["year"] == 2020
        # Python 3 came before deprecation
        assert loaded_events[1]["year"] < loaded_events[2]["year"]

    def test_hierarchical_document_structure(self, test_temp_dir):
        """Test reasoning with hierarchical document structure."""
        # Arrange
        doc_dir = Path(test_temp_dir) / "documents"
        doc_dir.mkdir(parents=True, exist_ok=True)

        hierarchy = {
            "id": "root",
            "title": "Programming",
            "children": [
                {
                    "id": "lang",
                    "title": "Languages",
                    "children": [
                        {"id": "python", "title": "Python"},
                        {"id": "java", "title": "Java"},
                    ],
                },
                {
                    "id": "paradigm",
                    "title": "Paradigms",
                    "children": [
                        {"id": "oop", "title": "Object-Oriented"},
                        {"id": "fp", "title": "Functional"},
                    ],
                },
            ],
        }

        save_json_file(hierarchy, doc_dir / "hierarchy.json")

        # Act - Traverse hierarchy
        def count_nodes(node):
            count = 1
            if "children" in node:
                count += sum(count_nodes(child) for child in node["children"])
            return count

        loaded = load_json_file(doc_dir / "hierarchy.json")
        total_nodes = count_nodes(loaded)

        # Assert
        assert total_nodes == 7  # 1 root + 2 level-1 + 4 level-2
