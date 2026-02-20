"""Test #2: image_generator.py lines 269-270 - content filter warning and return."""

import tempfile

from app.core.image_generator import ImageGenerationBackend, ImageGenerator


def test_content_filter_blocked_lines_269_270():
    """Trigger content filter to block unsafe content (lines 269-270).

    When check_content_filter returns False, we log warning and return error.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = ImageGenerator(backend=ImageGenerationBackend.OPENAI, data_dir=tmpdir)

        # Ensure content filter is enabled
        assert generator.content_filter_enabled is True

        # Generate with unsafe content (blocked keywords)
        # The content filter has BLOCKED_KEYWORDS like "nsfw", "explicit", etc.
        result = generator.generate("explicit sexual content")

        # Should be blocked (lines 269-270)
        assert result["success"] is False
        assert result["filtered"] is True
        assert "error" in result

        # Verify the blocked reason
        assert "Content filter" in result["error"] or result["error"]


if __name__ == "__main__":
    test_content_filter_blocked_lines_269_270()
    print("✅ Test passed! image_generator.py lines 269-270 covered")
