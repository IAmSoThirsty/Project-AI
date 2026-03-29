# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_web_frontend.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_web_frontend.py


from pathlib import Path


def test_frontend_placeholder_exists():
    root = Path(__file__).resolve().parent.parent
    index = root / "web" / "frontend" / "index.html"

    assert index.exists(), "Frontend placeholder should exist"
    content = index.read_text(encoding="utf-8")
    assert "Project-AI Frontend" in content
