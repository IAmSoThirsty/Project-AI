from __future__ import annotations

from pathlib import Path

from app.core.ai_systems import PluginManager


def create_sample_plugin(path: Path):
    code = '''
class Plugin:
    def __init__(self, name=None):
        self.name = name or 'sample'
        self.enabled = False
    def initialize(self, context=None):
        return True
    def enable(self):
        self.enabled = True
        return True
'''
    path.write_text(code)


def test_plugin_load_flow(tmp_path: Path):
    plugin_file = tmp_path / "sample_plugin.py"
    create_sample_plugin(plugin_file)

    manager = PluginManager(str(tmp_path))
    ok = manager.load_plugin_file(str(plugin_file))
    assert ok is True
    stats = manager.get_statistics()
    assert stats["total"] >= 1
