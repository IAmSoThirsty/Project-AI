"""
Tests for storage layer and interface abstractions.

This test suite validates:
- SQLiteStorage functionality
- JSONStorage backward compatibility
- GovernanceEngineInterface implementations
- MemoryEngineInterface implementations
- PluginInterface and PluginRegistry
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from app.core.interfaces import (
    GovernanceEngineInterface,
    MemoryEngineInterface,
    PluginInterface,
    PluginRegistry,
)
from app.core.services.governance_service import Decision
from app.core.storage import JSONStorage, SQLiteStorage, get_storage_engine


class TestSQLiteStorage:
    """Test suite for SQLiteStorage."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        yield db_path
        # Cleanup
        Path(db_path).unlink(missing_ok=True)

    @pytest.fixture
    def storage(self, temp_db):
        """Create SQLiteStorage instance."""
        storage = SQLiteStorage(db_path=temp_db)
        storage.initialize()
        return storage

    def test_initialization(self, temp_db):
        """Test that storage initializes correctly."""
        storage = SQLiteStorage(db_path=temp_db)
        storage.initialize()

        # Verify database file exists
        assert Path(temp_db).exists()

    def test_store_and_retrieve_governance_state(self, storage):
        """Test storing and retrieving governance state."""
        data = {
            "version": "1.0.0",
            "quorum_threshold": 0.51,
            "voting_period_days": 7,
        }

        # Store
        success = storage.store("governance_state", "config", data)
        assert success is True

        # Retrieve
        retrieved = storage.retrieve("governance_state", "config")
        assert retrieved is not None
        assert retrieved["version"] == "1.0.0"
        assert retrieved["quorum_threshold"] == 0.51

    def test_store_governance_decision(self, storage):
        """Test storing governance decisions."""
        decision_data = {
            "decision_id": "dec_123",
            "action_id": "act_456",
            "approved": True,
            "reason": "Test decision",
            "council_votes": {"galahad": "approve", "cerberus": "approve"},
            "timestamp": "2026-01-01T00:00:00Z",
        }

        # Store
        success = storage.store("governance_decisions", "dec_123", decision_data)
        assert success is True

        # Retrieve
        retrieved = storage.retrieve("governance_decisions", "dec_123")
        assert retrieved is not None
        assert retrieved["decision_id"] == "dec_123"
        assert retrieved["approved"] == 1  # SQLite stores as int

    def test_store_execution_history(self, storage):
        """Test storing execution history."""
        execution_data = {
            "trace_id": "trace_789",
            "action_name": "test_action",
            "action_type": "agent_action",
            "status": "completed",
            "source": "test",
            "duration_ms": 10.5,
            "channels": {"attempt": {}, "result": "success"},
        }

        # Store
        success = storage.store("execution_history", "trace_789", execution_data)
        assert success is True

        # Retrieve
        retrieved = storage.retrieve("execution_history", "trace_789")
        assert retrieved is not None
        assert retrieved["trace_id"] == "trace_789"
        assert retrieved["action_name"] == "test_action"

    def test_query_with_filters(self, storage):
        """Test querying with filters."""
        # Store multiple records
        for i in range(5):
            data = {
                "trace_id": f"trace_{i}",
                "action_name": f"action_{i}",
                "action_type": "agent_action",
                "status": "completed" if i % 2 == 0 else "failed",
                "source": "test",
                "duration_ms": 10.0,
                "channels": {},
            }
            storage.store("execution_history", f"trace_{i}", data)

        # Query completed only
        results = storage.query("execution_history", {"status": "completed"})
        assert len(results) == 3
        assert all(r["status"] == "completed" for r in results)

    def test_query_without_filters(self, storage):
        """Test querying without filters (all records)."""
        # Store multiple records
        for i in range(3):
            data = {
                "trace_id": f"trace_{i}",
                "action_name": f"action_{i}",
                "action_type": "agent_action",
                "status": "completed",
                "source": "test",
                "duration_ms": 10.0,
                "channels": {},
            }
            storage.store("execution_history", f"trace_{i}", data)

        # Query all
        results = storage.query("execution_history")
        assert len(results) == 3

    def test_delete(self, storage):
        """Test deleting records."""
        data = {"version": "1.0.0"}
        storage.store("governance_state", "test_key", data)

        # Verify exists
        retrieved = storage.retrieve("governance_state", "test_key")
        assert retrieved is not None

        # Delete
        success = storage.delete("governance_state", "test_key")
        assert success is True

        # Verify deleted
        retrieved = storage.retrieve("governance_state", "test_key")
        assert retrieved is None

    def test_update_overwrites(self, storage):
        """Test that storing with same key updates the record."""
        # Store initial
        data1 = {"version": "1.0.0"}
        storage.store("governance_state", "config", data1)

        # Store updated
        data2 = {"version": "2.0.0"}
        storage.store("governance_state", "config", data2)

        # Verify updated
        retrieved = storage.retrieve("governance_state", "config")
        assert retrieved["version"] == "2.0.0"


class TestJSONStorage:
    """Test suite for JSONStorage (legacy)."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def storage(self, temp_dir):
        """Create JSONStorage instance."""
        storage = JSONStorage(data_dir=temp_dir)
        storage.initialize()
        return storage

    def test_initialization(self, temp_dir):
        """Test that storage initializes correctly."""
        storage = JSONStorage(data_dir=temp_dir)
        storage.initialize()

        # Verify directory exists
        assert Path(temp_dir).exists()

    def test_store_and_retrieve(self, storage):
        """Test storing and retrieving JSON data."""
        data = {"key": "value", "number": 42}

        # Store
        success = storage.store("test_table", "test_key", data)
        assert success is True

        # Retrieve
        retrieved = storage.retrieve("test_table", "test_key")
        assert retrieved is not None
        assert retrieved["key"] == "value"
        assert retrieved["number"] == 42

    def test_retrieve_nonexistent(self, storage):
        """Test retrieving nonexistent key."""
        retrieved = storage.retrieve("test_table", "nonexistent")
        assert retrieved is None

    def test_query_with_filters(self, storage):
        """Test querying with filters."""
        # Store multiple records
        for i in range(5):
            data = {"id": i, "status": "active" if i % 2 == 0 else "inactive"}
            storage.store("test_table", f"key_{i}", data)

        # Query active only
        results = storage.query("test_table", {"status": "active"})
        assert len(results) == 3

    def test_delete(self, storage):
        """Test deleting records."""
        data = {"test": "data"}
        storage.store("test_table", "test_key", data)

        # Verify exists
        retrieved = storage.retrieve("test_table", "test_key")
        assert retrieved is not None

        # Delete
        success = storage.delete("test_table", "test_key")
        assert success is True

        # Verify deleted
        retrieved = storage.retrieve("test_table", "test_key")
        assert retrieved is None


class TestStorageFactory:
    """Test suite for storage factory function."""

    def test_get_sqlite_storage(self):
        """Test getting SQLite storage."""
        storage = get_storage_engine("sqlite", db_path=":memory:")
        assert isinstance(storage, SQLiteStorage)

    def test_get_json_storage(self):
        """Test getting JSON storage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = get_storage_engine("json", data_dir=tmpdir)
            assert isinstance(storage, JSONStorage)

    def test_invalid_storage_type(self):
        """Test that invalid storage type raises error."""
        with pytest.raises(ValueError):
            get_storage_engine("invalid")


class TestGovernanceEngineInterface:
    """Test suite for GovernanceEngineInterface."""

    def test_custom_governance_implementation(self):
        """Test implementing custom governance engine."""

        class SimpleGovernance(GovernanceEngineInterface):
            def __init__(self):
                self.evaluation_count = 0

            def evaluate_action(self, action, context):
                self.evaluation_count += 1
                return Decision(
                    decision_id="simple_123",
                    action_id="act_123",
                    approved=True,
                    reason="Simple approval",
                )

            def get_statistics(self):
                return {"evaluations": self.evaluation_count}

        # Create instance
        governance = SimpleGovernance()

        # Evaluate action
        action = Mock(action_id="act_123", risk_level="low")
        context = Mock(trace_id="trace_123")

        decision = governance.evaluate_action(action, context)

        # Verify
        assert decision.approved is True
        assert governance.evaluation_count == 1

        stats = governance.get_statistics()
        assert stats["evaluations"] == 1


class TestMemoryEngineInterface:
    """Test suite for MemoryEngineInterface."""

    def test_custom_memory_implementation(self):
        """Test implementing custom memory engine."""

        class SimpleMemory(MemoryEngineInterface):
            def __init__(self):
                self.records = []

            def record_execution(self, trace_id, channels, status):
                self.records.append({"trace_id": trace_id, "channels": channels, "status": status})
                return trace_id

            def query_executions(self, filters=None, limit=10):
                return self.records[-limit:]

            def get_statistics(self):
                return {"total_records": len(self.records)}

        # Create instance
        memory = SimpleMemory()

        # Record execution
        memory_id = memory.record_execution("trace_123", {"attempt": {}, "result": "success"}, "completed")

        # Verify
        assert memory_id == "trace_123"
        assert len(memory.records) == 1

        stats = memory.get_statistics()
        assert stats["total_records"] == 1

        # Query
        executions = memory.query_executions()
        assert len(executions) == 1

    def test_add_memory_default_implementation(self):
        """Test default add_memory implementation."""

        class TestMemory(MemoryEngineInterface):
            def __init__(self):
                self.last_record = None

            def record_execution(self, trace_id, channels, status):
                self.last_record = (trace_id, channels, status)
                return trace_id

            def query_executions(self, filters=None, limit=10):
                return []

            def get_statistics(self):
                return {}

        memory = TestMemory()

        # Use default add_memory
        memory_id = memory.add_memory(
            "Test content",
            "test_category",
            {
                "trace_id": "trace_456",
                "channels": {"test": "data"},
                "status": "completed",
            },
        )

        # Verify record_execution was called
        assert memory_id == "trace_456"
        assert memory.last_record[0] == "trace_456"


class TestPluginInterface:
    """Test suite for PluginInterface and PluginRegistry."""

    def test_custom_plugin_implementation(self):
        """Test implementing custom plugin."""

        class TestPlugin(PluginInterface):
            def get_name(self):
                return "test_plugin"

            def get_version(self):
                return "1.0.0"

            def execute(self, context):
                return {"result": "success", "input": context.get("input")}

            def get_metadata(self):
                return {
                    "name": self.get_name(),
                    "version": self.get_version(),
                    "description": "Test plugin",
                    "author": "Test Author",
                }

        plugin = TestPlugin()

        # Test basic methods
        assert plugin.get_name() == "test_plugin"
        assert plugin.get_version() == "1.0.0"

        # Test execution
        result = plugin.execute({"input": "test"})
        assert result["result"] == "success"
        assert result["input"] == "test"

        # Test metadata
        metadata = plugin.get_metadata()
        assert metadata["author"] == "Test Author"

    def test_plugin_registry(self):
        """Test PluginRegistry functionality."""

        class Plugin1(PluginInterface):
            def get_name(self):
                return "plugin1"

            def get_version(self):
                return "1.0.0"

            def execute(self, context):
                return {"plugin": 1}

        class Plugin2(PluginInterface):
            def get_name(self):
                return "plugin2"

            def get_version(self):
                return "2.0.0"

            def execute(self, context):
                return {"plugin": 2}

        # Create registry
        registry = PluginRegistry()

        # Register plugins
        registry.register(Plugin1())
        registry.register(Plugin2())

        # List plugins
        plugins = registry.list_plugins()
        assert len(plugins) == 2
        assert "plugin1" in plugins
        assert "plugin2" in plugins

        # Get plugin
        plugin = registry.get_plugin("plugin1")
        assert plugin is not None
        assert plugin.get_version() == "1.0.0"

        # Execute plugin
        result = registry.execute_plugin("plugin1", {})
        assert result["plugin"] == 1

    def test_plugin_registry_duplicate(self):
        """Test that duplicate plugin names are rejected."""

        class DuplicatePlugin(PluginInterface):
            def get_name(self):
                return "duplicate"

            def get_version(self):
                return "1.0.0"

            def execute(self, context):
                return {}

        registry = PluginRegistry()
        registry.register(DuplicatePlugin())

        # Try to register again
        with pytest.raises(ValueError):
            registry.register(DuplicatePlugin())

    def test_plugin_registry_unregister(self):
        """Test unregistering plugins."""

        class TestPlugin(PluginInterface):
            def get_name(self):
                return "test"

            def get_version(self):
                return "1.0.0"

            def execute(self, context):
                return {}

        registry = PluginRegistry()
        registry.register(TestPlugin())

        # Verify registered
        assert "test" in registry.list_plugins()

        # Unregister
        registry.unregister("test")

        # Verify unregistered
        assert "test" not in registry.list_plugins()

    def test_plugin_registry_execute_nonexistent(self):
        """Test executing nonexistent plugin."""
        registry = PluginRegistry()

        with pytest.raises(ValueError):
            registry.execute_plugin("nonexistent", {})

    def test_plugin_validation(self):
        """Test plugin context validation."""

        class ValidatingPlugin(PluginInterface):
            def get_name(self):
                return "validator"

            def get_version(self):
                return "1.0.0"

            def execute(self, context):
                return {"validated": True}

            def validate_context(self, context):
                # Require 'required_field' in context
                return "required_field" in context

        registry = PluginRegistry()
        registry.register(ValidatingPlugin())

        # Valid context
        result = registry.execute_plugin("validator", {"required_field": "value"})
        assert result["validated"] is True

        # Invalid context
        with pytest.raises(RuntimeError):
            registry.execute_plugin("validator", {})
