from __future__ import annotations

import json
import tempfile
import platform
from pathlib import Path

from app.agents.dependency_auditor import DependencyAuditor


def test_analyze_harmless_module(tmp_path: Path):
    module_file = tmp_path / "harmless.py"
    module_file.write_text('print("hello from harmless module")\n')

    auditor = DependencyAuditor(data_dir=str(tmp_path))
    report = auditor.analyze_new_module(str(module_file))

    assert report["success"] is True
    assert report["module"].endswith("harmless.py")
    assert "sandbox" in report
    # On Windows outside containers, sandbox may be declined for safety
    if platform.system() == "Windows":
        assert report["sandbox"].get("error") in ("platform_unsafe", None)
    # ensure persisted file exists
    reports = list(Path(str(tmp_path)).glob("sandbox_reports/sandbox_report_harmless_*.json"))
    assert len(reports) >= 1
    # load and check json
    r = json.loads(reports[0].read_text(encoding="utf-8"))
    assert r["module"].endswith("harmless.py")
