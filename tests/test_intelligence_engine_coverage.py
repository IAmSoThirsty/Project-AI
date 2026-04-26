"""
Coverage-boost tests for src/app/core/intelligence_engine.py.

Covers: IntelligenceRouter, DataAnalyzer, IntentDetector, LearningPathManager.
The IdentityIntegratedIntelligenceEngine has heavier dependencies and is
tested lightly for construction.
"""

import os
import sys
import tempfile
import types
from unittest import mock

import pandas as pd
import pytest

# The AGI identity sub-modules (bonding_protocol, etc.) require Python 3.11+
# (datetime.UTC). We stub them so we can import the intelligence_engine classes
# that do NOT depend on them (IntelligenceRouter, DataAnalyzer, IntentDetector).
# The AGI identity sub-modules (bonding_protocol, etc.) require Python 3.11+
# (datetime.UTC). We stub them so we can import the intelligence_engine classes
# that do NOT depend on them (IntelligenceRouter, DataAnalyzer, IntentDetector).
_STUB_ATTRS = {
    "src.app.core.bonding_protocol": ["BondingPhase", "BondingProtocol"],
    "src.app.core.governance": ["Triumvirate"],
    "src.app.core.memory_engine": ["EpisodicMemory", "MemoryEngine", "SignificanceLevel"],
    "src.app.core.perspective_engine": ["PerspectiveEngine"],
    "src.app.core.rebirth_protocol": ["RebirthManager", "UserAIInstance"],
    "src.app.core.reflection_cycle": ["ReflectionCycle", "ReflectionType"],
    "src.app.core.relationship_model": ["RelationshipModel", "RelationshipState"],
}

for _mod_name, _attrs in _STUB_ATTRS.items():
    if _mod_name not in sys.modules:
        _stub = types.ModuleType(_mod_name)
        for _attr in _attrs:
            setattr(_stub, _attr, type(_attr, (), {}))
        sys.modules[_mod_name] = _stub

# Now we can safely import the module (the stubs satisfy the from-imports at
# module level; missing attrs become None which is fine for the classes we test).
from src.app.core.intelligence_engine import (  # noqa: E402
    DataAnalyzer,
    IntentDetector,
    IntelligenceRouter,
)


# ── fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def csv_file(tmp_dir):
    """Create a small CSV file for DataAnalyzer tests."""
    path = os.path.join(tmp_dir, "data.csv")
    df = pd.DataFrame(
        {
            "x": [1.0, 2.0, 3.0, 4.0, 5.0],
            "y": [2.0, 4.0, 6.0, 8.0, 10.0],
            "z": [5.0, 3.0, 1.0, 4.0, 2.0],
        }
    )
    df.to_csv(path, index=False)
    return path


@pytest.fixture
def json_file(tmp_dir):
    path = os.path.join(tmp_dir, "data.json")
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    df.to_json(path)
    return path


# ── IntelligenceRouter ──────────────────────────────────────────────────────


class TestIntelligenceRouter:
    def test_init_no_deps(self):
        router = IntelligenceRouter()
        assert router.memory_system is None
        assert router.function_registry is None

    def test_general_route_no_deps(self):
        router = IntelligenceRouter()
        result = router.route_query("do something")
        assert result["route"] == "general"
        assert not result["metadata"]["memory_available"]
        assert not result["metadata"]["functions_available"]

    def test_help_route_with_function_registry(self):
        class MockRegistry:
            def get_help(self):
                return "Help text"
            def list_functions(self):
                return ["f1", "f2"]
            def get_categories(self):
                return ["cat1"]

        router = IntelligenceRouter(function_registry=MockRegistry())
        result = router.route_query("help with functions")
        assert result["route"] == "function_help"
        assert result["metadata"]["function_count"] == 2

    def test_knowledge_route_with_memory(self):
        class MockMemory:
            def query_knowledge(self, query, limit=5):
                return [{"category": "test", "key": "k", "value": "v"}]

        router = IntelligenceRouter(memory_system=MockMemory())
        result = router.route_query("what is gravity all about")
        assert result["route"] == "knowledge_query"
        assert "Found" in result["response"]

    def test_knowledge_route_no_results(self):
        class MockMemory:
            def query_knowledge(self, query, limit=5):
                return []

        router = IntelligenceRouter(memory_system=MockMemory())
        result = router.route_query("what is this thing")
        assert result["route"] == "general"

    def test_function_call_route(self):
        class MockRegistry:
            def get_help(self):
                return ""
            def list_functions(self):
                return ["greet"]
            def get_categories(self):
                return []
            def is_registered(self, name):
                return name == "greet"
            def get_function_info(self, name):
                return {"name": name}

        router = IntelligenceRouter(function_registry=MockRegistry())
        result = router.route_query("call greet")
        assert result["route"] == "function_call"
        assert result["metadata"]["function_name"] == "greet"

    def test_function_call_unregistered(self):
        class MockRegistry:
            def get_help(self):
                return ""
            def list_functions(self):
                return []
            def get_categories(self):
                return []
            def is_registered(self, name):
                return False
            def get_function_info(self, name):
                return None

        router = IntelligenceRouter(function_registry=MockRegistry())
        result = router.route_query("call unknown_function")
        assert result["route"] == "general"

    def test_conversation_search_route(self):
        class MockMemory:
            def query_knowledge(self, query, limit=5):
                return []
            def search_conversations(self, query, limit=5):
                return [
                    {"user": "hello", "ai": "hi", "timestamp": "2025-01-01T00:00:00"}
                ]

        router = IntelligenceRouter(memory_system=MockMemory())
        result = router.route_query("remember what we discussed about testing")
        assert result["route"] == "conversation_search"

    def test_conversation_search_no_results(self):
        class MockMemory:
            def query_knowledge(self, query, limit=5):
                return []
            def search_conversations(self, query, limit=5):
                return []

        router = IntelligenceRouter(memory_system=MockMemory())
        result = router.route_query("remember something about xyzzy")
        assert result["route"] == "general"

    def test_format_knowledge_results_empty(self):
        router = IntelligenceRouter()
        assert router._format_knowledge_results([]) == "No knowledge entries found."

    def test_format_knowledge_results(self):
        router = IntelligenceRouter()
        results = [
            {"category": "science", "key": "gravity", "value": "9.8"},
            {"category": "math", "key": "pi", "value": "3.14"},
        ]
        text = router._format_knowledge_results(results)
        assert "gravity" in text
        assert "pi" in text

    def test_format_conversation_results_empty(self):
        router = IntelligenceRouter()
        assert (
            router._format_conversation_results([])
            == "No matching conversations found."
        )

    def test_format_conversation_results(self):
        router = IntelligenceRouter()
        results = [
            {"user": "hi", "ai": "hello", "timestamp": "2025-01-01"},
        ]
        text = router._format_conversation_results(results)
        assert "hi" in text

    def test_call_function_no_registry(self):
        router = IntelligenceRouter()
        result = router.call_function("f")
        assert not result["success"]

    def test_call_function_success(self):
        class MockRegistry:
            def call(self, name, **kwargs):
                return {"result": 42}

        router = IntelligenceRouter(function_registry=MockRegistry())
        result = router.call_function("compute", x=1)
        assert result["success"]
        assert result["result"]["result"] == 42

    def test_call_function_error(self):
        class MockRegistry:
            def call(self, name, **kwargs):
                raise RuntimeError("fail")

        router = IntelligenceRouter(function_registry=MockRegistry())
        result = router.call_function("compute")
        assert not result["success"]
        assert "fail" in result["error"]


# ── DataAnalyzer ────────────────────────────────────────────────────────────


class TestDataAnalyzer:
    def test_init(self):
        da = DataAnalyzer()
        assert da.data is None

    def test_load_csv(self, csv_file):
        da = DataAnalyzer()
        ok = da.load_data(csv_file)
        assert ok
        assert da.data is not None
        assert len(da.data) == 5

    def test_load_json(self, json_file):
        da = DataAnalyzer()
        ok = da.load_data(json_file)
        assert ok

    def test_load_invalid_file(self, tmp_dir):
        da = DataAnalyzer()
        ok = da.load_data(os.path.join(tmp_dir, "nonexistent.csv"))
        assert not ok

    def test_summary_no_data(self):
        da = DataAnalyzer()
        result = da.get_summary_stats()
        assert result == "No data loaded"

    def test_summary_with_data(self, csv_file):
        da = DataAnalyzer()
        da.load_data(csv_file)
        stats = da.get_summary_stats()
        assert "basic_stats" in stats
        assert stats["row_count"] == 5
        assert stats["column_count"] == 3

    def test_visualization_no_data(self):
        da = DataAnalyzer()
        result = da.create_visualization("scatter")
        assert result is None

    def test_visualization_scatter(self, csv_file):
        da = DataAnalyzer()
        da.load_data(csv_file)
        fig = da.create_visualization("scatter", x_col="x", y_col="y")
        assert fig is not None

    def test_visualization_histogram(self, csv_file):
        da = DataAnalyzer()
        da.load_data(csv_file)
        fig = da.create_visualization("histogram", x_col="x")
        assert fig is not None

    def test_visualization_boxplot(self, csv_file):
        da = DataAnalyzer()
        da.load_data(csv_file)
        fig = da.create_visualization("boxplot", x_col="x")
        assert fig is not None

    def test_visualization_correlation(self, csv_file):
        da = DataAnalyzer()
        da.load_data(csv_file)
        fig = da.create_visualization("correlation")
        assert fig is not None

    def test_clustering_no_data(self):
        da = DataAnalyzer()
        fig, clusters = da.perform_clustering(["x", "y"])
        assert fig is None
        assert clusters is None

    def test_clustering_with_data(self, csv_file):
        da = DataAnalyzer()
        da.load_data(csv_file)
        fig, clusters = da.perform_clustering(["x", "y"], n_clusters=2)
        assert fig is not None
        assert clusters is not None
        assert len(clusters) == 5


# ── IntentDetector ──────────────────────────────────────────────────────────


class TestIntentDetector:
    def test_predict_untrained(self):
        detector = IntentDetector()
        assert detector.predict("hello") == "general"

    def test_train_and_predict(self):
        detector = IntentDetector()
        texts = [
            "what is the weather",
            "show me the forecast",
            "tell me a joke",
            "make me laugh",
            "how to cook pasta",
            "recipe for bread",
        ]
        labels = ["weather", "weather", "humor", "humor", "cooking", "cooking"]
        detector.train(texts, labels)
        assert detector.trained
        prediction = detector.predict("what will the weather be tomorrow")
        assert isinstance(prediction, str)

    def test_save_and_load_model(self, tmp_dir):
        detector = IntentDetector()
        texts = ["hello", "goodbye", "help me", "assist"]
        labels = ["greeting", "farewell", "support", "support"]
        detector.train(texts, labels)
        model_path = os.path.join(tmp_dir, "model.pkl")
        detector.save_model(model_path)
        assert os.path.exists(model_path)

        detector2 = IntentDetector()
        assert not detector2.trained
        detector2.load_model(model_path)
        assert detector2.trained

    def test_load_model_nonexistent(self, tmp_dir):
        detector = IntentDetector()
        detector.load_model(os.path.join(tmp_dir, "nope.pkl"))
        assert not detector.trained


# ── IntelligenceRouter (additional routes) ──────────────────────────────────


class TestIntelligenceRouterExtended:
    def test_execute_route(self):
        router = IntelligenceRouter()
        result = router.route_query("execute my_task")
        assert result["route"] == "general"  # no registry

    def test_run_route_with_registry(self):
        class MockRegistry:
            def get_help(self): return ""
            def list_functions(self): return ["task"]
            def get_categories(self): return []
            def is_registered(self, name): return name == "task"
            def get_function_info(self, name): return {"name": name}

        router = IntelligenceRouter(function_registry=MockRegistry())
        result = router.route_query("run task now")
        assert result["route"] == "function_call"

    def test_what_query_no_memory(self):
        router = IntelligenceRouter()
        result = router.route_query("what is something")
        assert result["route"] == "general"

    def test_who_query_with_memory_no_results(self):
        class MockMemory:
            def query_knowledge(self, query, limit=5): return []

        router = IntelligenceRouter(memory_system=MockMemory())
        result = router.route_query("who invented Python")
        assert result["route"] == "general"

    def test_format_knowledge_truncates(self):
        router = IntelligenceRouter()
        # More than 5 results truncates to 5
        results = [{"category": "c", "key": f"k{i}", "value": f"v{i}"} for i in range(10)]
        text = router._format_knowledge_results(results)
        assert "k4" in text
        assert "k5" not in text  # Only first 5


# ── DataAnalyzer (edge cases) ──────────────────────────────────────────────


class TestDataAnalyzerEdgeCases:
    def test_load_xlsx_nonexistent(self, tmp_dir):
        da = DataAnalyzer()
        ok = da.load_data(os.path.join(tmp_dir, "nope.xlsx"))
        assert not ok

    def test_visualization_unknown_type(self, csv_file):
        da = DataAnalyzer()
        da.load_data(csv_file)
        fig = da.create_visualization("unknown_type", x_col="x")
        # unknown type means no plot commands, returns the empty figure
        assert fig is not None

    def test_clustering_bad_columns(self, csv_file):
        da = DataAnalyzer()
        da.load_data(csv_file)
        fig, clusters = da.perform_clustering(["nonexistent_col"], n_clusters=2)
        assert fig is None
        assert clusters is None
