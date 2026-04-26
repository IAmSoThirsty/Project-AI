from pathlib import Path


def test_frontend_placeholder_exists():
    root = Path(__file__).resolve().parent.parent
    index = root / "web" / "frontend" / "index.html"

    assert index.exists(), "Frontend placeholder should exist"
    content = index.read_text(encoding="utf-8")
    assert "Project-AI Frontend" in content
