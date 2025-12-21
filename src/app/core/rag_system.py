"""
RAG (Retrieval-Augmented Generation) System for Project-AI.

This module implements a complete RAG pipeline that can:
1. Ingest data from various sources (files, APIs, databases)
2. Chunk and embed text using sentence-transformers
3. Store embeddings in a vector database (in-memory with disk persistence)
4. Retrieve relevant context for user queries
5. Augment LLM prompts with retrieved context

The system is designed to be extensible for future data sources like:
- Confluence API
- Slack exports
- SQL databases
- Web scraping
"""

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""

    text: str
    source: str
    chunk_id: str
    metadata: dict = field(default_factory=dict)
    embedding: list[float] | None = None

    def to_dict(self) -> dict:
        """Convert chunk to dictionary for serialization."""
        return {
            "text": self.text,
            "source": self.source,
            "chunk_id": self.chunk_id,
            "metadata": self.metadata,
            "embedding": self.embedding,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TextChunk":
        """Create chunk from dictionary."""
        return cls(
            text=data["text"],
            source=data["source"],
            chunk_id=data["chunk_id"],
            metadata=data.get("metadata", {}),
            embedding=data.get("embedding"),
        )


@dataclass
class RetrievalResult:
    """Represents a retrieved chunk with relevance score."""

    chunk: TextChunk
    score: float
    rank: int


class RAGSystem:
    """
    Complete RAG pipeline implementation.

    Supports:
    - Multiple data sources (directory, API, database)
    - Configurable chunking strategies
    - Efficient vector similarity search
    - Persistent storage of embeddings
    """

    def __init__(
        self,
        data_dir: str = "data/rag_index",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ):
        """
        Initialize RAG system.

        Args:
            data_dir: Directory for storing embeddings and metadata
            embedding_model: Name of sentence-transformers model to use
            chunk_size: Maximum characters per chunk
            chunk_overlap: Characters to overlap between chunks
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.embedding_model_name = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        self.chunks: list[TextChunk] = []
        self.model = None
        self._load_model()
        self._load_index()

    def _load_model(self):
        """Load the sentence-transformers model."""
        try:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.model = SentenceTransformer(self.embedding_model_name)
            logger.info("Embedding model loaded successfully")
        except ImportError as e:
            logger.error(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
            raise ImportError(
                "sentence-transformers required for RAG system"
            ) from e
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise

    def _load_index(self):
        """Load existing index from disk if available."""
        index_file = self.data_dir / "index.json"
        if index_file.exists():
            try:
                with open(index_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self.chunks = [
                        TextChunk.from_dict(chunk_data)
                        for chunk_data in data.get("chunks", [])
                    ]
                logger.info(f"Loaded {len(self.chunks)} chunks from index")
            except Exception as e:
                logger.error(f"Error loading index: {e}")
                self.chunks = []

    def _save_index(self):
        """Save index to disk."""
        index_file = self.data_dir / "index.json"
        try:
            data = {
                "chunks": [chunk.to_dict() for chunk in self.chunks],
                "metadata": {
                    "embedding_model": self.embedding_model_name,
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap,
                    "last_updated": datetime.now().isoformat(),
                },
            }
            with open(index_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved index with {len(self.chunks)} chunks")
        except Exception as e:
            logger.error(f"Error saving index: {e}")

    def _chunk_text(self, text: str, source: str) -> list[TextChunk]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            source: Source identifier (filename, URL, etc.)

        Returns:
            List of TextChunk objects
        """
        chunks = []
        text_length = len(text)

        for i in range(0, text_length, self.chunk_size - self.chunk_overlap):
            chunk_text = text[i : i + self.chunk_size]

            # Skip very small chunks at the end
            if len(chunk_text.strip()) < 50:
                continue

            # Create unique chunk ID based on content hash
            chunk_id = hashlib.sha256(
                f"{source}:{i}:{chunk_text}".encode()
            ).hexdigest()

            chunk = TextChunk(
                text=chunk_text,
                source=source,
                chunk_id=chunk_id,
                metadata={
                    "start_pos": i,
                    "end_pos": i + len(chunk_text),
                    "created_at": datetime.now().isoformat(),
                },
            )
            chunks.append(chunk)

        return chunks

    def _embed_chunks(self, chunks: list[TextChunk]) -> None:
        """
        Generate embeddings for chunks.

        Args:
            chunks: List of TextChunk objects to embed
        """
        if not chunks:
            return

        try:
            texts = [chunk.text for chunk in chunks]
            logger.info(f"Generating embeddings for {len(texts)} chunks...")

            embeddings = self.model.encode(
                texts, convert_to_tensor=False, show_progress_bar=True
            )

            # Convert numpy arrays to lists for JSON serialization
            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding = embedding.tolist()

            logger.info("Embeddings generated successfully")
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    def ingest_directory(
        self, directory_path: str, file_extensions: list[str] = None
    ) -> int:
        """
        Ingest all text files from a directory.

        Args:
            directory_path: Path to directory containing text files
            file_extensions: List of file extensions to process (default: ['.txt', '.md'])

        Returns:
            Number of chunks created
        """
        if file_extensions is None:
            file_extensions = [".txt", ".md"]

        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        logger.info(f"Ingesting files from: {directory_path}")
        new_chunks = []

        for filepath in directory.rglob("*"):
            if filepath.suffix.lower() in file_extensions and filepath.is_file():
                try:
                    with open(filepath, encoding="utf-8") as f:
                        text = f.read()

                    source = str(filepath.relative_to(directory))
                    file_chunks = self._chunk_text(text, source)
                    new_chunks.extend(file_chunks)

                    logger.info(
                        f"Processed {filepath.name}: {len(file_chunks)} chunks"
                    )
                except Exception as e:
                    logger.error(f"Error processing {filepath}: {e}")

        # Generate embeddings for new chunks
        self._embed_chunks(new_chunks)

        # Add to index
        self.chunks.extend(new_chunks)
        self._save_index()

        logger.info(f"Ingestion complete: {len(new_chunks)} new chunks")
        return len(new_chunks)

    def ingest_text(
        self, text: str, source: str, metadata: dict[str, Any] = None
    ) -> int:
        """
        Ingest a single text document.

        Args:
            text: Text content to ingest
            source: Source identifier
            metadata: Optional metadata dictionary

        Returns:
            Number of chunks created
        """
        logger.info(f"Ingesting text from: {source}")

        chunks = self._chunk_text(text, source)

        # Add custom metadata if provided
        if metadata:
            for chunk in chunks:
                chunk.metadata.update(metadata)

        # Generate embeddings
        self._embed_chunks(chunks)

        # Add to index
        self.chunks.extend(chunks)
        self._save_index()

        logger.info(f"Ingestion complete: {len(chunks)} chunks")
        return len(chunks)

    def retrieve(
        self, query: str, top_k: int = 3, min_score: float = 0.0
    ) -> list[RetrievalResult]:
        """
        Retrieve most relevant chunks for a query.

        Args:
            query: Query text
            top_k: Number of results to return
            min_score: Minimum similarity score (0-1)

        Returns:
            List of RetrievalResult objects sorted by relevance
        """
        if not self.chunks:
            logger.warning("No chunks in index")
            return []

        try:
            from sentence_transformers import util

            # Embed the query
            query_embedding = self.model.encode(
                query, convert_to_tensor=False
            )

            # Calculate similarities
            results = []
            for chunk in self.chunks:
                if chunk.embedding is None:
                    continue

                # Compute cosine similarity
                score = util.cos_sim(
                    query_embedding, chunk.embedding
                ).item()

                if score >= min_score:
                    results.append((chunk, score))

            # Sort by score descending
            results.sort(key=lambda x: x[1], reverse=True)

            # Take top k
            results = results[:top_k]

            # Create RetrievalResult objects
            return [
                RetrievalResult(chunk=chunk, score=score, rank=i + 1)
                for i, (chunk, score) in enumerate(results)
            ]

        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            return []

    def build_context(
        self, query: str, top_k: int = 3, max_length: int = 2000
    ) -> str:
        """
        Build context string for LLM augmentation.

        Args:
            query: Query text
            top_k: Number of chunks to retrieve
            max_length: Maximum characters in context

        Returns:
            Formatted context string
        """
        results = self.retrieve(query, top_k=top_k)

        if not results:
            return ""

        context_parts = []
        current_length = 0

        for result in results:
            chunk_text = result.chunk.text
            chunk_length = len(chunk_text)

            if current_length + chunk_length > max_length:
                # Truncate to fit
                remaining = max_length - current_length
                if remaining > 100:  # Only add if we have meaningful space
                    context_parts.append(chunk_text[:remaining] + "...")
                break

            context_parts.append(
                f"[Source: {result.chunk.source}, Score: {result.score:.3f}]\n{chunk_text}"
            )
            current_length += chunk_length

        return "\n\n---\n\n".join(context_parts)

    def query_with_llm(
        self, query: str, top_k: int = 3, model: str = "gpt-4"
    ) -> dict[str, Any]:
        """
        Query using RAG + LLM generation.

        Args:
            query: User's question
            top_k: Number of context chunks to retrieve
            model: OpenAI model to use

        Returns:
            Dictionary with answer, context, and metadata
        """
        try:
            import openai

            # Retrieve relevant context
            context = self.build_context(query, top_k=top_k)

            if not context:
                return {
                    "answer": "I don't have enough information to answer that question.",
                    "context": "",
                    "chunks_used": 0,
                }

            # Build augmented prompt
            prompt = f"""Using only the following context, answer the question.
If the context doesn't contain enough information, say so.

Context:
{context}

Question: {query}

Answer:"""

            # Call OpenAI API with timeout and error handling
            try:
                response = openai.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that answers questions based on provided context.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.3,
                    timeout=30,  # 30 second timeout
                )

                answer = response.choices[0].message.content

                return {
                    "answer": answer,
                    "context": context,
                    "chunks_used": top_k,
                    "model": model,
                }
            except openai.RateLimitError as e:
                logger.error(f"OpenAI rate limit exceeded: {e}")
                return {
                    "answer": "Rate limit exceeded. Please try again later.",
                    "context": context,
                    "chunks_used": 0,
                    "error": "rate_limit",
                }
            except openai.AuthenticationError as e:
                logger.error(f"OpenAI authentication failed: {e}")
                return {
                    "answer": "Authentication error. Please check your API key.",
                    "context": context,
                    "chunks_used": 0,
                    "error": "authentication",
                }
            except openai.APITimeoutError as e:
                logger.error(f"OpenAI API timeout: {e}")
                return {
                    "answer": "Request timed out. Please try again.",
                    "context": context,
                    "chunks_used": 0,
                    "error": "timeout",
                }
            except openai.APIError as e:
                logger.error(f"OpenAI API error: {e}")
                return {
                    "answer": f"API error occurred: {str(e)}",
                    "context": context,
                    "chunks_used": 0,
                    "error": "api_error",
                }

        except ImportError:
            logger.error("OpenAI not installed")
            return {
                "answer": "OpenAI integration not available",
                "context": context if "context" in locals() else "",
                "chunks_used": 0,
            }
        except Exception as e:
            logger.error(f"Error in LLM query: {e}")
            return {
                "answer": f"Error: {str(e)}",
                "context": context if "context" in locals() else "",
                "chunks_used": 0,
            }

    def clear_index(self):
        """Clear all chunks from the index."""
        self.chunks = []
        self._save_index()
        logger.info("Index cleared")

    def get_statistics(self) -> dict[str, Any]:
        """Get statistics about the RAG index."""
        sources = set(chunk.source for chunk in self.chunks)
        embedded_count = sum(
            1 for chunk in self.chunks if chunk.embedding is not None
        )

        return {
            "total_chunks": len(self.chunks),
            "embedded_chunks": embedded_count,
            "unique_sources": len(sources),
            "sources": list(sources),
            "embedding_model": self.embedding_model_name,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
        }


# Convenience functions for common use cases


def create_rag_system(
    data_dir: str = "data/rag_index",
    embedding_model: str = "all-MiniLM-L6-v2",
) -> RAGSystem:
    """
    Create a RAG system with default settings.

    Args:
        data_dir: Directory for storing index
        embedding_model: Sentence-transformers model name

    Returns:
        Initialized RAGSystem instance
    """
    return RAGSystem(data_dir=data_dir, embedding_model=embedding_model)


def quick_ingest_and_query(
    directory: str, query: str, top_k: int = 3
) -> list[RetrievalResult]:
    """
    Quick helper to ingest a directory and query it.

    Args:
        directory: Path to directory with text files
        query: Query string
        top_k: Number of results

    Returns:
        List of retrieval results
    """
    rag = create_rag_system()
    rag.ingest_directory(directory)
    return rag.retrieve(query, top_k=top_k)
