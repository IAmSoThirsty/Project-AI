"""
Tests for Image Generation System.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

from app.core.image_generator import ImageGenerator, ImageStyle


@pytest.fixture
def temp_dir():
    """Create temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def generator(temp_dir):
    """Create ImageGenerator instance with temp directory."""
    return ImageGenerator(data_dir=temp_dir)


class TestImageGenerator:
    """Test suite for ImageGenerator class."""

    def test_initialization(self, generator, temp_dir):
        """Test generator initializes with correct data directory."""
        assert generator.data_dir == temp_dir
        assert Path(temp_dir, "generated_images").exists()
        # History is managed by file listing, not a separate JSON file

    def test_content_filter_blocks_forbidden_keywords(self, generator):
        """Test content filter blocks prompts with forbidden keywords."""
        forbidden_prompts = [
            "violence in the streets",
            "explicit adult content",
            "gore and blood everywhere",
            "hate speech content",
            "illegal drug use",
        ]

        for prompt in forbidden_prompts:
            is_safe, reason = generator.check_content_filter(prompt)
            assert not is_safe, f"Expected '{prompt}' to be blocked"
            assert "blocked" in reason.lower() or "keyword" in reason.lower()

    def test_content_filter_allows_safe_prompts(self, generator):
        """Test content filter allows safe prompts."""
        safe_prompts = [
            "a beautiful landscape with mountains",
            "abstract geometric art",
            "cyberpunk city at night",
            "oil painting of a cat",
        ]

        for prompt in safe_prompts:
            is_safe, reason = generator.check_content_filter(prompt)
            assert is_safe, f"Expected '{prompt}' to be allowed"
            # Reason can be "Content filter passed" or similar

    def test_style_presets_available(self, generator):
        """Test all style presets are properly defined."""
        expected_styles = [
            ImageStyle.PHOTOREALISTIC,
            ImageStyle.DIGITAL_ART,
            ImageStyle.OIL_PAINTING,
            ImageStyle.WATERCOLOR,
            ImageStyle.ANIME,
            ImageStyle.CYBERPUNK,
            ImageStyle.FANTASY,
            ImageStyle.MINIMALIST,
            ImageStyle.ABSTRACT,
            ImageStyle.CINEMATIC,
        ]

        for style in expected_styles:
            assert style in generator.STYLE_PRESETS
            preset = generator.STYLE_PRESETS[style]
            assert isinstance(preset, str)
            assert len(preset) > 0

    def test_history_tracking(self, generator, temp_dir):
        """Test generation history is tracked correctly."""
        # Create a test image file
        test_image_path = Path(temp_dir, "generated_images", "test_image.png")
        test_image_path.write_bytes(b"fake image data")

        # Get history
        history = generator.get_generation_history(limit=10)

        assert len(history) == 1
        assert history[0]["filename"] == "test_image.png"
        assert "filepath" in history[0]
        assert "timestamp" in history[0]

    @patch("app.core.image_generator.requests.post")
    def test_generate_with_huggingface_success(self, mock_post, generator):
        """Test successful image generation with Hugging Face backend."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake_image_data"
        mock_post.return_value = mock_response

        with patch.dict("os.environ", {"HUGGINGFACE_API_KEY": "test_key"}):
            # Recreate generator with API key set
            generator.hf_api_key = "test_key"

            result = generator.generate_with_huggingface(
                "a beautiful sunset",
                "",
                512,
                512,
            )

            assert result["success"] is True
            assert "filepath" in result
            assert Path(result["filepath"]).exists()

    @patch("app.core.image_generator.requests.post")
    def test_generate_with_huggingface_failure(self, mock_post, generator):
        """Test error handling for Hugging Face generation failure."""
        # Mock failed API response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Error")
        mock_post.return_value = mock_response

        with patch.dict("os.environ", {"HUGGINGFACE_API_KEY": "test_key"}):
            generator.hf_api_key = "test_key"

            result = generator.generate_with_huggingface(
                "test prompt",
                "",
                512,
                512,
            )

            assert result["success"] is False
            assert "error" in result

    def test_generate_without_api_key(self, generator):
        """Test generation fails gracefully without API key."""
        with patch.dict("os.environ", {}, clear=True):
            # Recreate generator without API keys
            generator.hf_api_key = None
            generator.openai_api_key = None

            result = generator.generate_with_huggingface(
                "test prompt",
                "",
                512,
                512,
            )

            assert result["success"] is False
            assert "api key" in result["error"].lower() or "not configured" in result["error"].lower()

    def test_multiple_generations_tracked(self, generator, temp_dir):
        """Test multiple generations are tracked in history."""
        # Create multiple test image files
        for i in range(3):
            test_image_path = Path(temp_dir, "generated_images", f"image_{i}.png")
            test_image_path.write_bytes(b"fake image data")

        history = generator.get_generation_history(limit=10)
        assert len(history) == 3
        assert any("image_0.png" in h["filename"] for h in history)
        assert any("image_2.png" in h["filename"] for h in history)
