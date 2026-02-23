"""Tests for OSINT plugins — SampleOSINTPlugin + OSINTLoader."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

# ── Stub heavy dependencies ───────────────────────────────────

_stubs: dict = {}
for _mod in [
    "app.core.ai_systems",
    "app.core.observability",
]:
    if _mod not in sys.modules:
        _stubs[_mod] = MagicMock()

# Wire FourLaws.validate_action to always allow by default
if "app.core.ai_systems" in _stubs:
    ai_mod = _stubs["app.core.ai_systems"]
    ai_mod.FourLaws = MagicMock()
    ai_mod.FourLaws.validate_action = MagicMock(return_value=(True, "OK"))
    # Plugin base class
    ai_mod.Plugin = type(
        "Plugin",
        (),
        {"__init__": lambda self, name="", version="": setattr(self, "name", name) or setattr(self, "version", version) or setattr(self, "enabled", False)},
    )

sys.modules.update(_stubs)

from plugins.osint.sample_osint_plugin import SampleOSINTPlugin  # noqa: E402
from app.knowledge.osint_loader import OSINTLoader  # noqa: E402


# ═══════════════════════════════════════════════════════════════
# SampleOSINTPlugin Tests
# ═══════════════════════════════════════════════════════════════


class TestSampleOSINTPlugin:
    """Tests for SampleOSINTPlugin."""

    def test_init_defaults(self):
        p = SampleOSINTPlugin()
        assert p.tool_name == "sample_osint_tool"
        assert p.enabled is False

    def test_initialize_enables(self):
        p = SampleOSINTPlugin(tool_name="test_tool")
        ok = p.initialize()
        assert ok is True
        assert p.enabled is True

    def test_initialize_blocked_by_four_laws(self):
        from app.core.ai_systems import FourLaws

        FourLaws.validate_action.return_value = (False, "law violation")
        try:
            p = SampleOSINTPlugin(tool_name="blocked_tool")
            ok = p.initialize()
            assert ok is False
            assert p.enabled is False
        finally:
            FourLaws.validate_action.return_value = (True, "OK")

    def test_initialize_requires_explicit_order(self):
        p = SampleOSINTPlugin()
        ok = p.initialize({"requires_explicit_order": True, "is_user_order": False})
        assert ok is False

    def test_initialize_explicit_order_granted(self):
        p = SampleOSINTPlugin()
        ok = p.initialize({"requires_explicit_order": True, "is_user_order": True})
        assert ok is True

    def test_execute_not_initialized(self):
        p = SampleOSINTPlugin()
        result = p.execute({"query": "test"})
        assert result["status"] == "error"

    def test_execute_missing_params(self):
        p = SampleOSINTPlugin()
        p.initialize()
        result = p.execute({})  # missing "query"
        assert result["status"] == "error"
        assert "missing" in result["message"].lower()

    def test_execute_success(self):
        p = SampleOSINTPlugin()
        p.initialize()
        result = p.execute({"query": "example.com"})
        assert result["status"] == "success"
        assert "duration_ms" in result
        assert result["results"]["query"] == "example.com"

    def test_execute_domain_tool_type(self):
        p = SampleOSINTPlugin(tool_name="whois", tool_type="domain_lookup")
        p.initialize()
        result = p.execute({"domain": "example.com"})
        assert result["status"] == "success"

    def test_statistics_tracking(self):
        p = SampleOSINTPlugin()
        p.initialize()
        p.execute({"query": "a"})
        p.execute({"query": "b"})
        stats = p.get_statistics()
        assert stats["executions"] == 2
        assert stats["successes"] == 2
        assert stats["success_rate"] == 1.0

    def test_shutdown_disables(self):
        p = SampleOSINTPlugin()
        p.initialize()
        assert p.enabled is True
        p.shutdown()
        assert p.enabled is False

    def test_get_metadata(self):
        p = SampleOSINTPlugin(tool_name="meta_test", tool_url="https://example.com")
        meta = p.get_metadata()
        assert meta["tool_name"] == "meta_test"
        assert meta["tool_url"] == "https://example.com"


# ═══════════════════════════════════════════════════════════════
# OSINTLoader Tests
# ═══════════════════════════════════════════════════════════════


class TestOSINTLoader:
    """Tests for OSINTLoader."""

    def _write_osint_data(self, tmp_path):
        data_dir = tmp_path / "osint"
        data_dir.mkdir()
        data = {
            "metadata": {"source": "test", "updated": "2025-01-01"},
            "categories": {
                "recon": [
                    {"name": "nmap", "description": "Network scanner", "url": "https://nmap.org"},
                    {"name": "shodan", "description": "IoT search engine", "url": "https://shodan.io"},
                ],
                "social": [
                    {"name": "sherlock", "description": "Username finder"},
                ],
            },
        }
        (data_dir / "osint_bible.json").write_text(json.dumps(data))
        return data_dir

    def test_load_osint_data(self, tmp_path):
        data_dir = self._write_osint_data(tmp_path)
        loader = OSINTLoader(data_dir=data_dir)
        ok = loader.load_osint_data()
        assert ok is True
        assert len(loader.get_categories()) == 2

    def test_load_missing_file(self, tmp_path):
        data_dir = tmp_path / "empty_osint"
        data_dir.mkdir()
        loader = OSINTLoader(data_dir=data_dir)
        ok = loader.load_osint_data()
        assert ok is False

    def test_get_tools_by_category(self, tmp_path):
        data_dir = self._write_osint_data(tmp_path)
        loader = OSINTLoader(data_dir=data_dir)
        loader.load_osint_data()
        recon_tools = loader.get_tools_by_category("recon")
        assert len(recon_tools) == 2

    def test_search_tools(self, tmp_path):
        data_dir = self._write_osint_data(tmp_path)
        loader = OSINTLoader(data_dir=data_dir)
        loader.load_osint_data()
        results = loader.search_tools("network")
        assert len(results) == 1
        assert results[0]["name"] == "nmap"

    def test_search_case_insensitive(self, tmp_path):
        data_dir = self._write_osint_data(tmp_path)
        loader = OSINTLoader(data_dir=data_dir)
        loader.load_osint_data()
        results = loader.search_tools("IOT")
        assert len(results) == 1

    # ── Plugin registration ──

    def test_register_as_plugin(self, tmp_path):
        data_dir = self._write_osint_data(tmp_path)
        loader = OSINTLoader(data_dir=data_dir)
        loader.load_osint_data()
        ok = loader.register_as_plugin({"name": "nmap", "url": "https://nmap.org"})
        assert ok is True
        assert "osint_nmap" in loader.get_registered_plugins()

    def test_register_idempotent(self, tmp_path):
        data_dir = self._write_osint_data(tmp_path)
        loader = OSINTLoader(data_dir=data_dir)
        loader.register_as_plugin({"name": "nmap"})
        loader.register_as_plugin({"name": "nmap"})
        assert len(loader.get_registered_plugins()) == 1

    def test_register_no_name(self, tmp_path):
        data_dir = self._write_osint_data(tmp_path)
        loader = OSINTLoader(data_dir=data_dir)
        ok = loader.register_as_plugin({"description": "no name"})
        assert ok is False

    def test_unregister_plugin(self, tmp_path):
        data_dir = self._write_osint_data(tmp_path)
        loader = OSINTLoader(data_dir=data_dir)
        loader.register_as_plugin({"name": "nmap"})
        assert loader.unregister_plugin("nmap") is True
        assert "osint_nmap" not in loader.get_registered_plugins()

    def test_unregister_nonexistent(self, tmp_path):
        loader = OSINTLoader(data_dir=tmp_path)
        assert loader.unregister_plugin("fake") is False

    def test_batch_register(self, tmp_path):
        data_dir = self._write_osint_data(tmp_path)
        loader = OSINTLoader(data_dir=data_dir)
        loader.load_osint_data()
        results = loader.batch_register(category="recon")
        assert results["nmap"] is True
        assert results["shodan"] is True
        assert len(loader.get_registered_plugins()) == 2

    def test_registration_log(self, tmp_path):
        data_dir = self._write_osint_data(tmp_path)
        loader = OSINTLoader(data_dir=data_dir)
        loader.register_as_plugin({"name": "nmap"})
        log = loader.get_registration_log()
        assert len(log) == 1
        assert log[0]["success"] is True

    # ── Export ──

    def test_export_knowledge_base(self, tmp_path):
        data_dir = self._write_osint_data(tmp_path)
        loader = OSINTLoader(data_dir=data_dir)
        loader.load_osint_data()
        out = tmp_path / "kb.json"
        ok = loader.export_knowledge_base(out)
        assert ok is True
        kb = json.loads(out.read_text())
        assert len(kb["tools"]) == 3

    def test_get_metadata(self, tmp_path):
        data_dir = self._write_osint_data(tmp_path)
        loader = OSINTLoader(data_dir=data_dir)
        loader.load_osint_data()
        meta = loader.get_metadata()
        assert meta["source"] == "test"
