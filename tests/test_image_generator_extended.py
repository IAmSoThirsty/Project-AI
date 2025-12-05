"""Extended tests for ImageGenerator (20+)."""

from __future__ import annotations

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from app.core.image_generator import ImageGenerationBackend, ImageGenerator, ImageStyle


@pytest.fixture
def tmpdir():
    with tempfile.TemporaryDirectory() as td:
        yield td


def test_build_enhanced_prompt_styles(tmpdir):
    gen = ImageGenerator(data_dir=tmpdir)
    for style in ImageStyle:
        p = gen.build_enhanced_prompt("base", style)
        assert isinstance(p, str)
        assert len(p) > len("base")


def test_content_filter_enabled_flag_present(tmpdir):
    gen = ImageGenerator(data_dir=tmpdir)
    stats = gen.get_statistics()
    assert "content_filter_enabled" in stats
    assert isinstance(stats["content_filter_enabled"], bool)


@pytest.mark.parametrize(
    "prompt,expected",
    [
        ("nsfw content", False),
        ("Explicit scenes", False),
        ("clean landscape", True),
        ("Oil painting of a tree", True),
    ],
)
def test_check_content_filter(tmpdir, prompt, expected):
    gen = ImageGenerator(data_dir=tmpdir)
    safe, _ = gen.check_content_filter(prompt)
    assert safe is expected


def test_generate_empty_prompt_error(tmpdir):
    gen = ImageGenerator(data_dir=tmpdir)
    result = gen.generate("")
    assert result["success"] is False
    assert "Empty" in result["error"]


def test_generate_openai_backend_without_key(tmpdir):
    gen = ImageGenerator(backend=ImageGenerationBackend.OPENAI, data_dir=tmpdir)
    with patch.dict(os.environ, {}, clear=True):
        gen.openai_api_key = None
        res = gen.generate("a cat")
        assert res["success"] is False


def test_generate_hf_backend_without_key(tmpdir):
    gen = ImageGenerator(backend=ImageGenerationBackend.HUGGINGFACE, data_dir=tmpdir)
    with patch.dict(os.environ, {}, clear=True):
        gen.hf_api_key = None
        res = gen.generate("a dog")
        assert res["success"] is False


def test_generate_with_openai_success_flow(tmpdir):
    gen = ImageGenerator(backend=ImageGenerationBackend.OPENAI, data_dir=tmpdir)
    gen.openai_api_key = "key"
    with patch("openai.images.generate") as mock_gen, patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.data = [MagicMock(url="http://example.com/image.png")]
        mock_gen.return_value = mock_resp
        mock_get.return_value.content = b"img"
        out = gen.generate("scene", ImageStyle.ANIME, 512, 512)
        assert out["success"] is True


def test_generate_with_hf_success_flow(tmpdir):
    gen = ImageGenerator(backend=ImageGenerationBackend.HUGGINGFACE, data_dir=tmpdir)
    gen.hf_api_key = "key"
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"pngdata"
        mock_post.return_value = mock_response
        out = gen.generate("scene", ImageStyle.CINEMATIC, 512, 512)
        assert out["success"] is True


def test_generation_history_list(tmpdir):
    gen = ImageGenerator(data_dir=tmpdir)
    os.makedirs(gen.output_dir, exist_ok=True)
    for i in range(3):
        with open(os.path.join(gen.output_dir, f"x{i}.png"), "wb") as fh:
            fh.write(b"data")
    hist = gen.get_generation_history()
    assert len(hist) == 3


def test_generation_stats(tmpdir):
    gen = ImageGenerator(data_dir=tmpdir)
    stats = gen.get_statistics()
    assert "backend" in stats
    assert "available_styles" in stats
