import os

from app.agents.codex_deus_maximus import create_codex


def test_codex_implements_and_rolls_back(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    codex = create_codex(data_dir=str(data_dir), allow_integration=False)
    # Implement a fake request
    res = codex.implement_request("req123", "sample_topic", "do something")
    assert res["success"]
    path = res["path"]
    assert os.path.exists(path)
    # Attempt integration should be blocked by default
    rep = codex.integrate_across_project(target_modules=[str(tmp_path / "nope.py")])
    assert rep["success"] is False
    # Cleanup
    # Should be able to rollback (no-op but must not throw)
    rb = codex.rollback_integrations({"report": {"integrated": []}})
    assert isinstance(rb, dict)


def test_codex_auto_fix(tmp_path):
    codex = create_codex(data_dir=str(tmp_path), allow_integration=False)
    # Create a malformed python file with tabs and trailing spaces
    p = tmp_path / "bad.py"
    p.write_text("def x():\n\tprint('hi')  \n")
    res = codex.auto_fix_file(str(p))
    assert res["success"]
    # Validate content
    txt = p.read_text()
    assert "\t" not in txt
    assert txt.endswith("\n")
