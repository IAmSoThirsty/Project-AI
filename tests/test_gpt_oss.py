from app.agents.codex_deus_maximus import create_codex


def test_gpt_oss_generation_is_runtime_only(monkeypatch):
    """Importing this test module must not load GPT-OSS or torch at collection."""
    codex = create_codex()
    monkeypatch.setattr(codex, "_load_gpt_oss_model", lambda: None)

    response = codex.generate_gpt_oss("Hello, GPT-OSS 1208!")

    assert response == "[Dummy GPT‑OSS response] Hello, GPT-OSS 1208!"
