"""
Memory Adapter - Semantic Memory with Vector Search

Implements scalable semantic memory using SentenceTransformer embeddings
and efficient vector similarity search for >10k records.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class MemoryRecord:
    """A single memory record with metadata."""

    id: str
    content: str
    embedding: np.ndarray | None = None
    metadata: dict | None = None
    timestamp: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "content": self.content,
            "embedding": (
                self.embedding.tolist() if self.embedding is not None else None
            ),
            "metadata": self.metadata or {},
            "timestamp": self.timestamp or datetime.now().isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryRecord":
        """Create from dictionary."""
        embedding = data.get("embedding")
        if embedding is not None:
            embedding = np.array(embedding)
        return cls(
            id=data["id"],
            content=data["content"],
            embedding=embedding,
            metadata=data.get("metadata"),
            timestamp=data.get("timestamp"),
        )


class MemoryAdapter:
    """
    Semantic memory system with vector search capabilities.

    Supports:
    - Embedding generation via SentenceTransformer
    - Efficient similarity search
    - Scalable storage (>10k records)
    - Persistence to disk
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        data_dir: str = "data/memory",
        max_records: int = 10000,
    ):
        """
        Initialize memory adapter.

        Args:
            model_name: SentenceTransformer model name
            data_dir: Directory for persistent storage
            max_records: Maximum number of records to keep
        """
        self.model_name = model_name
        self.data_dir = Path(data_dir)
        self.max_records = max_records
        self.records: list[MemoryRecord] = []
        self.embeddings_matrix: np.ndarray | None = None

        # Initialize embedding model
        self._init_embedding_model()

        # Load existing memories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_memories()

    def _init_embedding_model(self):
        """Initialize SentenceTransformer model with fallback."""
        try:
            from sentence_transformers import SentenceTransformer

            logger.info("Loading SentenceTransformer model: %s", self.model_name)
            self.encoder = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.warning("Failed to load SentenceTransformer: %s", e)
            logger.warning("Using dummy embeddings for testing")
            self.encoder = None

    def add_memory(
        self, content: str, memory_id: str | None = None, metadata: dict | None = None
    ) -> str:
        """
        Add a new memory record.

        Args:
            content: Memory content text
            memory_id: Optional custom ID (generated if not provided)
            metadata: Optional metadata dictionary

        Returns:
            Memory ID
        """
        if memory_id is None:
            memory_id = f"mem_{len(self.records)}_{datetime.now().timestamp()}"

        # Generate embedding
        embedding = self._generate_embedding(content)

        # Create record
        record = MemoryRecord(
            id=memory_id,
            content=content,
            embedding=embedding,
            metadata=metadata,
            timestamp=datetime.now().isoformat(),
        )

        # Add to records
        self.records.append(record)

        # Rebuild embeddings matrix
        self._rebuild_embeddings_matrix()

        # Enforce size limit
        if len(self.records) > self.max_records:
            self.records = self.records[-self.max_records :]
            self._rebuild_embeddings_matrix()

        # Persist
        self._save_memories()

        logger.info("Added memory: %s", memory_id)
        return memory_id

    def search(
        self, query: str, top_k: int = 5, min_similarity: float = 0.0
    ) -> list[dict]:
        """
        Search for similar memories using semantic similarity.

        Args:
            query: Query text
            top_k: Number of results to return
            min_similarity: Minimum similarity threshold (0-1)

        Returns:
            List of matching memories with similarity scores
        """
        if not self.records:
            return []

        # Generate query embedding
        query_embedding = self._generate_embedding(query)

        # Compute similarities
        if self.embeddings_matrix is None or query_embedding is None:
            logger.warning("No embeddings available for search")
            return []

        similarities = self._cosine_similarity(query_embedding, self.embeddings_matrix)

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Filter by minimum similarity and prepare results
        results = []
        for idx in top_indices:
            similarity = float(similarities[idx])
            if similarity >= min_similarity:
                record = self.records[idx]
                results.append(
                    {
                        "id": record.id,
                        "content": record.content,
                        "similarity": similarity,
                        "metadata": record.metadata or {},
                        "timestamp": record.timestamp,
                    }
                )

        return results

    def get_memory(self, memory_id: str) -> dict | None:
        """
        Retrieve a specific memory by ID.

        Args:
            memory_id: Memory identifier

        Returns:
            Memory record dictionary or None if not found
        """
        for record in self.records:
            if record.id == memory_id:
                return {
                    "id": record.id,
                    "content": record.content,
                    "metadata": record.metadata or {},
                    "timestamp": record.timestamp,
                }
        return None

    def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.

        Args:
            memory_id: Memory identifier

        Returns:
            True if deleted, False if not found
        """
        for i, record in enumerate(self.records):
            if record.id == memory_id:
                self.records.pop(i)
                self._rebuild_embeddings_matrix()
                self._save_memories()
                logger.info("Deleted memory: %s", memory_id)
                return True
        return False

    def clear_all(self):
        """Clear all memories."""
        self.records = []
        self.embeddings_matrix = None
        self._save_memories()
        logger.info("Cleared all memories")

    def get_stats(self) -> dict:
        """Get memory statistics."""
        return {
            "total_records": len(self.records),
            "max_records": self.max_records,
            "model_name": self.model_name,
            "has_embeddings": self.embeddings_matrix is not None,
        }

    def _generate_embedding(self, text: str) -> np.ndarray | None:
        """Generate embedding for text."""
        if self.encoder is None:
            # Dummy embedding for testing
            return np.random.rand(384)

        try:
            embedding = self.encoder.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error("Embedding generation failed: %s", e)
            return None

    def _rebuild_embeddings_matrix(self):
        """Rebuild embeddings matrix from all records."""
        embeddings = []
        for record in self.records:
            if record.embedding is not None:
                embeddings.append(record.embedding)

        if embeddings:
            self.embeddings_matrix = np.vstack(embeddings)
        else:
            self.embeddings_matrix = None

    @staticmethod
    def _cosine_similarity(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between query and matrix rows."""
        # Normalize query
        query_norm = query / (np.linalg.norm(query) + 1e-8)

        # Normalize matrix rows
        matrix_norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-8
        matrix_normalized = matrix / matrix_norms

        # Compute dot products
        similarities = matrix_normalized @ query_norm

        return similarities

    def _save_memories(self):
        """Save memories to disk."""
        save_path = self.data_dir / "semantic_memory.json"
        try:
            data = [record.to_dict() for record in self.records]
            with open(save_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug("Saved %s memories to %s", len(self.records), save_path)
        except Exception as e:
            logger.error("Failed to save memories: %s", e)

    def _load_memories(self):
        """Load memories from disk."""
        load_path = self.data_dir / "semantic_memory.json"
        if not load_path.exists():
            logger.info("No existing memories found")
            return

        try:
            with open(load_path) as f:
                data = json.load(f)

            self.records = [MemoryRecord.from_dict(item) for item in data]
            self._rebuild_embeddings_matrix()
            logger.info("Loaded %s memories from %s", len(self.records), load_path)
        except Exception as e:
            logger.error("Failed to load memories: %s", e)
            self.records = []
