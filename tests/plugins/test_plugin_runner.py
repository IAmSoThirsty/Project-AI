from __future__ import annotations

import pytest

from app.plugins.plugin_runner import PluginRunner


def test_plugin_runner_initializes(tmp_path, monkeypatch):
    # Create a small script that implements the JSONL init protocol
    plugin_script = tmp_path / "echo_plugin.py"
    plugin_script.write_text(
        'import sys, json\nfor line in sys.stdin:\n    o=json.loads(line)\n    if o.get("method")=="init":\n        print(json.dumps({"id": o.get("id"), "result": {"ok": True}}))\n        sys.stdout.flush()\n        break\n'
    )

    runner = PluginRunner(str(plugin_script), timeout=2.0)
    runner.start()
    resp = runner.call_init({"hello": "world"})
    assert resp.get("result", {}).get("ok") is True
    runner.stop()


@pytest.mark.timeout(5)
def test_plugin_runner_timeout(tmp_path):
    plugin_script = tmp_path / "slow_plugin.py"
    plugin_script.write_text(
        'import sys, time\nfor line in sys.stdin:\n    time.sleep(3)\n    try:\n        o=json.loads(line)\n    except Exception:\n        continue\n    if o.get("method")=="init":\n        print(json.dumps({"id": o.get("id"), "result": {"ok": True}}))\n        sys.stdout.flush()\n        break\n'
    )

    runner = PluginRunner(str(plugin_script), timeout=1.0)
    runner.start()
    with pytest.raises(TimeoutError):
        runner.call_init({"hello": "slow"})
    runner.stop()
