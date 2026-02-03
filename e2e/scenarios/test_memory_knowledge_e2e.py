"""
E2E Tests for Memory and Knowledge Management

Comprehensive tests for memory persistence, knowledge base operations,
and information retrieval including:
- Memory persistence and retrieval across sessions
- Knowledge base CRUD operations
- Memory search, filtering, and categorization
- Knowledge base integrity and consistency
- Memory cleanup and archival workflows
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from e2e.utils.test_helpers import (
    compare_json_objects,
    get_timestamp_iso,
    load_json_file,
    save_json_file,
    wait_for_condition,
)


@pytest.mark.e2e
@pytest.mark.memory
class TestMemoryPersistence:
    """E2E tests for memory persistence and retrieval."""

    def test_memory_save_and_load(self, test_temp_dir):
        """Test basic memory save and load operations."""
        # Arrange
        memory_dir = Path(test_temp_dir) / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        test_memory = {
            "conversation_id": "conv_001",
            "timestamp": get_timestamp_iso(),
            "user_input": "What is the capital of France?",
            "ai_response": "The capital of France is Paris.",
            "context": {"topic": "geography", "confidence": 0.95},
        }

        # Act
        memory_file = memory_dir / "conversation_001.json"
        save_json_file(test_memory, memory_file)
        
        loaded_memory = load_json_file(memory_file)

        # Assert
        assert loaded_memory["conversation_id"] == test_memory["conversation_id"]
        assert loaded_memory["user_input"] == test_memory["user_input"]
        assert loaded_memory["ai_response"] == test_memory["ai_response"]
        assert loaded_memory["context"]["topic"] == "geography"

    def test_multiple_memory_sessions(self, test_temp_dir):
        """Test persistence across multiple conversation sessions."""
        # Arrange
        memory_dir = Path(test_temp_dir) / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        num_sessions = 10
        sessions = []

        # Act - Create multiple sessions
        for i in range(num_sessions):
            session = {
                "session_id": f"session_{i:03d}",
                "timestamp": get_timestamp_iso(),
                "messages": [
                    {"role": "user", "content": f"Question {i}"},
                    {"role": "assistant", "content": f"Answer {i}"},
                ],
                "metadata": {"turn_count": 2, "session_duration": 30 + i},
            }
            sessions.append(session)
            save_json_file(session, memory_dir / f"session_{i:03d}.json")

        # Assert - Load and verify all sessions
        loaded_sessions = []
        for i in range(num_sessions):
            loaded = load_json_file(memory_dir / f"session_{i:03d}.json")
            loaded_sessions.append(loaded)

        assert len(loaded_sessions) == num_sessions
        for i, session in enumerate(loaded_sessions):
            assert session["session_id"] == f"session_{i:03d}"
            assert len(session["messages"]) == 2

    def test_memory_with_large_content(self, test_temp_dir):
        """Test memory persistence with large content payloads."""
        # Arrange
        memory_dir = Path(test_temp_dir) / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        large_content = "x" * 100000  # 100KB of data
        memory = {
            "id": "large_memory_001",
            "content": large_content,
            "size_bytes": len(large_content),
            "timestamp": get_timestamp_iso(),
        }

        # Act
        memory_file = memory_dir / "large_memory.json"
        save_json_file(memory, memory_file)
        loaded = load_json_file(memory_file)

        # Assert
        assert loaded["id"] == memory["id"]
        assert len(loaded["content"]) == len(large_content)
        assert loaded["size_bytes"] == len(large_content)

    def test_memory_integrity_verification(self, test_temp_dir):
        """Test memory integrity using checksums."""
        # Arrange
        memory_dir = Path(test_temp_dir) / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        content = "Important information that must not be corrupted"
        checksum = hashlib.sha256(content.encode()).hexdigest()
        
        memory = {
            "id": "integrity_test_001",
            "content": content,
            "checksum": checksum,
            "timestamp": get_timestamp_iso(),
        }

        # Act
        memory_file = memory_dir / "integrity_test.json"
        save_json_file(memory, memory_file)
        loaded = load_json_file(memory_file)
        
        # Verify integrity
        loaded_checksum = hashlib.sha256(loaded["content"].encode()).hexdigest()

        # Assert
        assert loaded["checksum"] == checksum
        assert loaded_checksum == checksum

    def test_concurrent_memory_writes(self, test_temp_dir):
        """Test concurrent memory write operations."""
        # Arrange
        memory_dir = Path(test_temp_dir) / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def write_memory(index):
            memory = {
                "id": f"concurrent_{index}",
                "data": f"data_{index}",
                "timestamp": get_timestamp_iso(),
            }
            save_json_file(memory, memory_dir / f"concurrent_{index}.json")
            return index

        # Act
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(write_memory, i) for i in range(20)]
            results = [future.result() for future in as_completed(futures)]

        # Assert
        assert len(results) == 20
        # Verify all files were created
        memory_files = list(memory_dir.glob("concurrent_*.json"))
        assert len(memory_files) == 20

    def test_memory_search_by_timestamp(self, test_temp_dir):
        """Test searching memories by timestamp range."""
        # Arrange
        memory_dir = Path(test_temp_dir) / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        base_time = datetime.now()
        memories = []
        
        for i in range(20):
            timestamp = base_time + timedelta(hours=i)
            memory = {
                "id": f"timed_{i}",
                "timestamp": timestamp.isoformat(),
                "content": f"Memory at hour {i}",
            }
            memories.append(memory)
            save_json_file(memory, memory_dir / f"timed_{i}.json")

        # Act - Search for memories in middle range (hours 5-10)
        target_start = (base_time + timedelta(hours=5)).isoformat()
        target_end = (base_time + timedelta(hours=10)).isoformat()
        
        found_memories = []
        for memory_file in memory_dir.glob("timed_*.json"):
            memory = load_json_file(memory_file)
            if target_start <= memory["timestamp"] <= target_end:
                found_memories.append(memory)

        # Assert
        assert len(found_memories) == 6  # Hours 5-10 inclusive


@pytest.mark.e2e
@pytest.mark.knowledge
class TestKnowledgeBaseCRUD:
    """E2E tests for knowledge base CRUD operations."""

    def test_create_knowledge_entry(self, test_temp_dir):
        """Test creating new knowledge base entries."""
        # Arrange
        kb_dir = Path(test_temp_dir) / "knowledge_base"
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        entry = {
            "id": "kb_001",
            "title": "Python Best Practices",
            "category": "programming",
            "content": "Use PEP 8 style guide for Python code.",
            "tags": ["python", "coding", "style"],
            "created_at": get_timestamp_iso(),
            "updated_at": get_timestamp_iso(),
        }

        # Act
        entry_file = kb_dir / "kb_001.json"
        save_json_file(entry, entry_file)

        # Assert
        assert entry_file.exists()
        loaded = load_json_file(entry_file)
        assert loaded["id"] == "kb_001"
        assert loaded["category"] == "programming"
        assert "python" in loaded["tags"]

    def test_read_knowledge_entries(self, test_temp_dir):
        """Test reading knowledge base entries."""
        # Arrange
        kb_dir = Path(test_temp_dir) / "knowledge_base"
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        entries = [
            {
                "id": f"kb_{i:03d}",
                "title": f"Topic {i}",
                "category": "general",
                "content": f"Content for topic {i}",
            }
            for i in range(5)
        ]
        
        for entry in entries:
            save_json_file(entry, kb_dir / f"{entry['id']}.json")

        # Act
        loaded_entries = []
        for kb_file in sorted(kb_dir.glob("kb_*.json")):
            loaded_entries.append(load_json_file(kb_file))

        # Assert
        assert len(loaded_entries) == 5
        for i, entry in enumerate(loaded_entries):
            assert entry["id"] == f"kb_{i:03d}"

    def test_update_knowledge_entry(self, test_temp_dir):
        """Test updating existing knowledge base entries."""
        # Arrange
        kb_dir = Path(test_temp_dir) / "knowledge_base"
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        original_entry = {
            "id": "kb_update",
            "title": "Original Title",
            "content": "Original content",
            "version": 1,
            "updated_at": get_timestamp_iso(),
        }
        
        entry_file = kb_dir / "kb_update.json"
        save_json_file(original_entry, entry_file)

        # Act - Update the entry
        time.sleep(0.1)  # Ensure different timestamp
        updated_entry = load_json_file(entry_file)
        updated_entry["title"] = "Updated Title"
        updated_entry["content"] = "Updated content"
        updated_entry["version"] = 2
        updated_entry["updated_at"] = get_timestamp_iso()
        save_json_file(updated_entry, entry_file)

        # Assert
        final_entry = load_json_file(entry_file)
        assert final_entry["title"] == "Updated Title"
        assert final_entry["content"] == "Updated content"
        assert final_entry["version"] == 2
        assert final_entry["updated_at"] != original_entry["updated_at"]

    def test_delete_knowledge_entry(self, test_temp_dir):
        """Test deleting knowledge base entries."""
        # Arrange
        kb_dir = Path(test_temp_dir) / "knowledge_base"
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        entry = {
            "id": "kb_delete",
            "title": "To Be Deleted",
            "content": "This will be deleted",
        }
        
        entry_file = kb_dir / "kb_delete.json"
        save_json_file(entry, entry_file)
        assert entry_file.exists()

        # Act
        entry_file.unlink()

        # Assert
        assert not entry_file.exists()

    def test_batch_knowledge_creation(self, test_temp_dir):
        """Test batch creation of knowledge entries."""
        # Arrange
        kb_dir = Path(test_temp_dir) / "knowledge_base"
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        batch_size = 50
        entries = [
            {
                "id": f"batch_{i:04d}",
                "title": f"Batch Entry {i}",
                "category": "batch_test",
                "content": f"Content {i}",
            }
            for i in range(batch_size)
        ]

        # Act
        start_time = time.time()
        for entry in entries:
            save_json_file(entry, kb_dir / f"{entry['id']}.json")
        duration = time.time() - start_time

        # Assert
        created_files = list(kb_dir.glob("batch_*.json"))
        assert len(created_files) == batch_size
        assert duration < 5.0  # Should complete within 5 seconds

    def test_knowledge_entry_validation(self, test_temp_dir):
        """Test validation of knowledge entry structure."""
        # Arrange
        kb_dir = Path(test_temp_dir) / "knowledge_base"
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        valid_entry = {
            "id": "kb_valid",
            "title": "Valid Entry",
            "category": "test",
            "content": "Valid content",
            "created_at": get_timestamp_iso(),
        }

        # Act
        entry_file = kb_dir / "kb_valid.json"
        save_json_file(valid_entry, entry_file)
        loaded = load_json_file(entry_file)

        # Assert - Validate required fields
        required_fields = ["id", "title", "category", "content", "created_at"]
        for field in required_fields:
            assert field in loaded, f"Missing required field: {field}"


@pytest.mark.e2e
@pytest.mark.knowledge
class TestKnowledgeSearchAndFilter:
    """E2E tests for knowledge search and filtering."""

    def test_search_by_category(self, test_temp_dir):
        """Test searching knowledge by category."""
        # Arrange
        kb_dir = Path(test_temp_dir) / "knowledge_base"
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        categories = ["programming", "science", "history", "art"]
        entries = []
        
        for i, category in enumerate(categories * 3):
            entry = {
                "id": f"cat_{i}",
                "title": f"Entry {i}",
                "category": category,
                "content": f"Content about {category}",
            }
            entries.append(entry)
            save_json_file(entry, kb_dir / f"cat_{i}.json")

        # Act - Search for programming entries
        programming_entries = []
        for kb_file in kb_dir.glob("cat_*.json"):
            entry = load_json_file(kb_file)
            if entry["category"] == "programming":
                programming_entries.append(entry)

        # Assert
        assert len(programming_entries) == 3

    def test_search_by_tags(self, test_temp_dir):
        """Test searching knowledge by tags."""
        # Arrange
        kb_dir = Path(test_temp_dir) / "knowledge_base"
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        entries = [
            {
                "id": "tag_1",
                "title": "Python Tutorial",
                "tags": ["python", "tutorial", "beginner"],
            },
            {
                "id": "tag_2",
                "title": "Python Advanced",
                "tags": ["python", "advanced", "expert"],
            },
            {
                "id": "tag_3",
                "title": "JavaScript Basics",
                "tags": ["javascript", "tutorial", "beginner"],
            },
        ]
        
        for entry in entries:
            save_json_file(entry, kb_dir / f"{entry['id']}.json")

        # Act - Search for entries with "python" tag
        python_entries = []
        for kb_file in kb_dir.glob("tag_*.json"):
            entry = load_json_file(kb_file)
            if "python" in entry.get("tags", []):
                python_entries.append(entry)

        # Assert
        assert len(python_entries) == 2

    def test_full_text_search(self, test_temp_dir):
        """Test full-text search in knowledge content."""
        # Arrange
        kb_dir = Path(test_temp_dir) / "knowledge_base"
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        entries = [
            {
                "id": "search_1",
                "content": "The quick brown fox jumps over the lazy dog",
            },
            {
                "id": "search_2",
                "content": "A journey of a thousand miles begins with a single step",
            },
            {
                "id": "search_3",
                "content": "To be or not to be, that is the question",
            },
        ]
        
        for entry in entries:
            save_json_file(entry, kb_dir / f"{entry['id']}.json")

        # Act - Search for "journey"
        search_term = "journey"
        found_entries = []
        for kb_file in kb_dir.glob("search_*.json"):
            entry = load_json_file(kb_file)
            if search_term.lower() in entry["content"].lower():
                found_entries.append(entry)

        # Assert
        assert len(found_entries) == 1
        assert found_entries[0]["id"] == "search_2"

    def test_filter_by_date_range(self, test_temp_dir):
        """Test filtering knowledge by creation date."""
        # Arrange
        kb_dir = Path(test_temp_dir) / "knowledge_base"
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        base_date = datetime.now()
        entries = []
        
        for i in range(10):
            created_at = (base_date - timedelta(days=i)).isoformat()
            entry = {
                "id": f"date_{i}",
                "title": f"Entry {i}",
                "created_at": created_at,
            }
            entries.append(entry)
            save_json_file(entry, kb_dir / f"date_{i}.json")

        # Act - Filter entries from last 5 days
        cutoff_date = (base_date - timedelta(days=5)).isoformat()
        recent_entries = []
        
        for kb_file in kb_dir.glob("date_*.json"):
            entry = load_json_file(kb_file)
            if entry["created_at"] >= cutoff_date:
                recent_entries.append(entry)

        # Assert
        assert len(recent_entries) == 6  # Days 0-5 inclusive

    def test_combined_filters(self, test_temp_dir):
        """Test combining multiple filter criteria."""
        # Arrange
        kb_dir = Path(test_temp_dir) / "knowledge_base"
        kb_dir.mkdir(parents=True, exist_ok=True)
        
        entries = [
            {
                "id": "combo_1",
                "category": "tech",
                "tags": ["python", "ai"],
                "priority": "high",
            },
            {
                "id": "combo_2",
                "category": "tech",
                "tags": ["java", "backend"],
                "priority": "low",
            },
            {
                "id": "combo_3",
                "category": "tech",
                "tags": ["python", "web"],
                "priority": "high",
            },
            {
                "id": "combo_4",
                "category": "business",
                "tags": ["python", "analytics"],
                "priority": "high",
            },
        ]
        
        for entry in entries:
            save_json_file(entry, kb_dir / f"{entry['id']}.json")

        # Act - Filter: category=tech AND tags contains python AND priority=high
        filtered_entries = []
        for kb_file in kb_dir.glob("combo_*.json"):
            entry = load_json_file(kb_file)
            if (
                entry["category"] == "tech"
                and "python" in entry.get("tags", [])
                and entry["priority"] == "high"
            ):
                filtered_entries.append(entry)

        # Assert
        assert len(filtered_entries) == 2
        assert all(e["category"] == "tech" for e in filtered_entries)


@pytest.mark.e2e
@pytest.mark.memory
@pytest.mark.slow
class TestMemoryCleanupArchival:
    """E2E tests for memory cleanup and archival."""

    def test_archive_old_memories(self, test_temp_dir):
        """Test archiving old memories based on age."""
        # Arrange
        memory_dir = Path(test_temp_dir) / "memory"
        archive_dir = Path(test_temp_dir) / "archive"
        memory_dir.mkdir(parents=True, exist_ok=True)
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        base_date = datetime.now()
        
        # Create memories of different ages
        for i in range(20):
            created_at = (base_date - timedelta(days=i * 10)).isoformat()
            memory = {
                "id": f"mem_{i}",
                "created_at": created_at,
                "content": f"Memory {i}",
            }
            save_json_file(memory, memory_dir / f"mem_{i}.json")

        # Act - Archive memories older than 100 days
        cutoff_date = (base_date - timedelta(days=100)).isoformat()
        archived_count = 0
        
        for memory_file in list(memory_dir.glob("mem_*.json")):
            memory = load_json_file(memory_file)
            if memory["created_at"] < cutoff_date:
                # Move to archive
                archive_file = archive_dir / memory_file.name
                save_json_file(memory, archive_file)
                memory_file.unlink()
                archived_count += 1

        # Assert
        active_memories = list(memory_dir.glob("mem_*.json"))
        archived_memories = list(archive_dir.glob("mem_*.json"))
        
        assert archived_count > 0
        assert len(active_memories) + len(archived_memories) == 20

    def test_cleanup_duplicate_memories(self, test_temp_dir):
        """Test removing duplicate memory entries."""
        # Arrange
        memory_dir = Path(test_temp_dir) / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Create memories with some duplicates
        base_memory = {
            "content": "This is duplicate content",
            "context": {"topic": "test"},
        }
        
        for i in range(10):
            memory = base_memory.copy()
            memory["id"] = f"dup_{i}"
            # Make half of them true duplicates
            if i >= 5:
                memory["content"] = f"Unique content {i}"
            save_json_file(memory, memory_dir / f"dup_{i}.json")

        # Act - Remove duplicates based on content hash
        seen_hashes = set()
        removed_count = 0
        
        for memory_file in list(memory_dir.glob("dup_*.json")):
            memory = load_json_file(memory_file)
            content_hash = hashlib.sha256(
                memory["content"].encode()
            ).hexdigest()
            
            if content_hash in seen_hashes:
                memory_file.unlink()
                removed_count += 1
            else:
                seen_hashes.add(content_hash)

        # Assert
        remaining_memories = list(memory_dir.glob("dup_*.json"))
        assert len(remaining_memories) == 6  # 1 original + 5 unique
        assert removed_count == 4

    def test_compress_archived_memories(self, test_temp_dir):
        """Test compression of archived memories."""
        # Arrange
        import gzip
        
        archive_dir = Path(test_temp_dir) / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        memory = {
            "id": "compress_test",
            "content": "x" * 10000,  # Large content
            "metadata": {"size": "large"},
        }
        
        memory_file = archive_dir / "compress_test.json"
        save_json_file(memory, memory_file)
        
        original_size = memory_file.stat().st_size

        # Act - Compress the memory
        compressed_file = archive_dir / "compress_test.json.gz"
        with open(memory_file, "rb") as f_in:
            with gzip.open(compressed_file, "wb") as f_out:
                f_out.writelines(f_in)
        
        compressed_size = compressed_file.stat().st_size
        
        # Verify decompression
        with gzip.open(compressed_file, "rb") as f:
            decompressed_data = json.loads(f.read().decode())

        # Assert
        assert compressed_size < original_size
        assert decompressed_data["id"] == "compress_test"
        assert len(decompressed_data["content"]) == 10000

    def test_memory_retention_policy(self, test_temp_dir):
        """Test enforcement of memory retention policy."""
        # Arrange
        memory_dir = Path(test_temp_dir) / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        retention_days = 30
        base_date = datetime.now()
        
        # Create memories with various priorities
        for i in range(50):
            created_at = (base_date - timedelta(days=i)).isoformat()
            memory = {
                "id": f"retention_{i}",
                "created_at": created_at,
                "priority": "high" if i % 5 == 0 else "low",
                "content": f"Memory {i}",
            }
            save_json_file(memory, memory_dir / f"retention_{i}.json")

        # Act - Apply retention policy (keep high priority always, others 30 days)
        cutoff_date = (base_date - timedelta(days=retention_days)).isoformat()
        deleted_count = 0
        
        for memory_file in list(memory_dir.glob("retention_*.json")):
            memory = load_json_file(memory_file)
            should_delete = (
                memory["priority"] == "low"
                and memory["created_at"] < cutoff_date
            )
            if should_delete:
                memory_file.unlink()
                deleted_count += 1

        # Assert
        remaining_memories = list(memory_dir.glob("retention_*.json"))
        # Should keep all high priority (10) + recent low priority (30)
        assert deleted_count > 0
        assert len(remaining_memories) < 50

    def test_memory_statistics_collection(self, test_temp_dir):
        """Test collection of memory statistics."""
        # Arrange
        memory_dir = Path(test_temp_dir) / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        categories = ["tech", "personal", "work", "learning"]
        
        for i in range(100):
            memory = {
                "id": f"stat_{i}",
                "category": categories[i % len(categories)],
                "size": 100 + (i * 10),
                "timestamp": get_timestamp_iso(),
            }
            save_json_file(memory, memory_dir / f"stat_{i}.json")

        # Act - Collect statistics
        stats = {
            "total_count": 0,
            "total_size": 0,
            "by_category": {},
            "avg_size": 0,
        }
        
        for memory_file in memory_dir.glob("stat_*.json"):
            memory = load_json_file(memory_file)
            stats["total_count"] += 1
            stats["total_size"] += memory["size"]
            
            category = memory["category"]
            if category not in stats["by_category"]:
                stats["by_category"][category] = 0
            stats["by_category"][category] += 1
        
        stats["avg_size"] = stats["total_size"] / stats["total_count"]

        # Assert
        assert stats["total_count"] == 100
        assert len(stats["by_category"]) == 4
        assert all(count == 25 for count in stats["by_category"].values())
        assert stats["avg_size"] > 0
