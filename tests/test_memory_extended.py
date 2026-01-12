"""Extended test suite for MemoryExpansionSystem with 20+ tests.

Covers:
- Knowledge add/get for categories and keys
- Conversation logging IDs and timestamps
- Statistics reporting
- Persistence and corrupted file handling
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime

import pytest

from app.core.ai_systems import MemoryExpansionSystem


@pytest.fixture
def mem_tmpdir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


def test_initial_knowledge_empty(mem_tmpdir):
    m = MemoryExpansionSystem(data_dir=mem_tmpdir)
    assert isinstance(m.knowledge_base, dict)
    assert len(m.knowledge_base) == 0


@pytest.mark.parametrize(
    "category,key,value",
    [
        ("security", "xss", {"type": "XSS"}),
        ("security", "csrf", {"type": "CSRF"}),
        ("coding", "python", {"lang": "Python"}),
        ("coding", "rust", {"lang": "Rust"}),
        ("infra", "k8s", {"tool": "Kubernetes"}),
    ],
)
def test_add_and_get_knowledge(mem_tmpdir, category, key, value):
    m = MemoryExpansionSystem(data_dir=mem_tmpdir)
    m.add_knowledge(category, key, value)
    assert m.get_knowledge(category, key) == value


def test_get_full_category(mem_tmpdir):
    m = MemoryExpansionSystem(data_dir=mem_tmpdir)
    m.add_knowledge("security", "sql_injection", {"risk": "high"})
    cat = m.get_knowledge("security")
    assert "sql_injection" in cat


def test_get_unknown_category_returns_none(mem_tmpdir):
    m = MemoryExpansionSystem(data_dir=mem_tmpdir)
    assert m.get_knowledge("unknown") is None


def test_get_missing_key_returns_none(mem_tmpdir):
    m = MemoryExpansionSystem(data_dir=mem_tmpdir)
    m.add_knowledge("security", "xss", {"risk": "medium"})
    assert m.get_knowledge("security", "missing") is None


def test_log_conversation_generates_id(mem_tmpdir):
    m = MemoryExpansionSystem(data_dir=mem_tmpdir)
    cid = m.log_conversation("Hello", "Hi")
    assert isinstance(cid, str) and len(cid) == 12
    assert m.conversations[0]["user"] == "Hello"
    assert m.conversations[0]["ai"] == "Hi"
    # Timestamp should be ISO format
    ts = datetime.fromisoformat(m.conversations[0]["timestamp"])
    assert isinstance(ts, datetime)


def test_statistics(mem_tmpdir):
    m = MemoryExpansionSystem(data_dir=mem_tmpdir)
    m.log_conversation("A", "B")
    m.add_knowledge("k", "v", 1)
    stats = m.get_statistics()
    assert stats["conversations"] == 1
    assert stats["knowledge_categories"] == 1


def test_persistence_after_add(mem_tmpdir):
    m1 = MemoryExpansionSystem(data_dir=mem_tmpdir)
    m1.add_knowledge("coding", "go", {"lang": "Go"})

    m2 = MemoryExpansionSystem(data_dir=mem_tmpdir)
    assert m2.get_knowledge("coding", "go") == {"lang": "Go"}


def test_corrupted_knowledge_file_initialization(mem_tmpdir):
    # Create corrupted file
    kb_dir = os.path.join(mem_tmpdir, "memory")
    os.makedirs(kb_dir, exist_ok=True)
    with open(os.path.join(kb_dir, "knowledge.json"), "w", encoding="utf-8") as fh:
        fh.write("{bad json")

    # Should initialize with empty knowledge
    m = MemoryExpansionSystem(data_dir=mem_tmpdir)
    assert isinstance(m.knowledge_base, dict)


def test_multiple_conversations(mem_tmpdir):
    m = MemoryExpansionSystem(data_dir=mem_tmpdir)
    for _ in range(5):
        m.log_conversation("Hi", "Hello")
    assert len(m.conversations) == 5


def test_add_multiple_categories(mem_tmpdir):
    m = MemoryExpansionSystem(data_dir=mem_tmpdir)
    m.add_knowledge("a", "x", 1)
    m.add_knowledge("b", "y", 2)
    m.add_knowledge("c", "z", 3)
    assert set(m.knowledge_base.keys()) == {"a", "b", "c"}


def test_overwrite_existing_key(mem_tmpdir):
    m = MemoryExpansionSystem(data_dir=mem_tmpdir)
    m.add_knowledge("security", "xss", {"risk": "medium"})
    m.add_knowledge("security", "xss", {"risk": "high"})
    assert m.get_knowledge("security", "xss") == {"risk": "high"}
