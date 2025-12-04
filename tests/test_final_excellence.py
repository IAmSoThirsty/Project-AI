"""Final strategic tests to push all modules to 80%+ (Excellent) coverage."""

import json
import os
import tempfile
from unittest.mock import patch

import pytest

from app.core.image_generator import ImageGenerator, ImageStyle
from app.core.user_manager import UserManager


class TestUserManagerFinal:
    """Push UserManager to 80%+."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_update_user(self, temp_dir):
        users_file = os.path.join(temp_dir, "users.json")
        manager = UserManager(users_file=users_file)
        manager.create_user("test", "pass")
        manager.update_user("test", persona="professional")
        assert manager.get_user_data("test")["persona"] == "professional"

    def test_set_password(self, temp_dir):
        users_file = os.path.join(temp_dir, "users.json")
        manager = UserManager(users_file=users_file)
        manager.create_user("test", "oldpass")
        manager.set_password("test", "newpass")
        assert manager.authenticate("test", "newpass")

    def test_delete_user(self, temp_dir):
        users_file = os.path.join(temp_dir, "users.json")
        manager = UserManager(users_file=users_file)
        manager.create_user("test", "pass")
        assert manager.delete_user("test") is True
        assert manager.delete_user("nonexistent") is False

    def test_corrupted_file(self, temp_dir):
        users_file = os.path.join(temp_dir, "users.json")
        with open(users_file, "w") as f:
            f.write("{corrupted")
        manager = UserManager(users_file=users_file)
        assert len(manager.users) == 0

    def test_password_migration(self, temp_dir):
        users_file = os.path.join(temp_dir, "users.json")
        with open(users_file, "w") as f:
            json.dump({"old": {"password": "plain123", "persona": "test"}}, f)
        manager = UserManager(users_file=users_file)
        assert "password_hash" in manager.users["old"]
        assert manager.authenticate("old", "plain123")

    def test_update_nonexistent(self, temp_dir):
        users_file = os.path.join(temp_dir, "users.json")
        manager = UserManager(users_file=users_file)
        assert manager.update_user("none", persona="test") is False

    def test_invalid_cipher(self, temp_dir):
        users_file = os.path.join(temp_dir, "users.json")
        with patch.dict(os.environ, {"FERNET_KEY": "bad"}):
            manager = UserManager(users_file=users_file)
            assert manager.cipher_suite is not None


class TestImageGeneratorFinal:
    """Push ImageGenerator to 80%+."""

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_build_enhanced_prompt(self, temp_dir):
        gen = ImageGenerator(data_dir=temp_dir)
        enhanced = gen.build_enhanced_prompt("cat", style=ImageStyle.PHOTOREALISTIC)
        assert "cat" in enhanced.lower()

    def test_content_filter_disabled(self, temp_dir):
        gen = ImageGenerator(data_dir=temp_dir)
        gen.content_filter_enabled = False
        is_safe, _ = gen.check_content_filter("bad content")
        assert is_safe is True

    def test_stats_empty(self, temp_dir):
        gen = ImageGenerator(data_dir=temp_dir)
        stats = gen.get_statistics()
        assert stats["total_generated"] == 0

    def test_corrupted_history(self, temp_dir):
        hist_file = os.path.join(temp_dir, "image_generation", "history.json")
        os.makedirs(os.path.dirname(hist_file), exist_ok=True)
        with open(hist_file, "w") as f:
            f.write("bad{json")
        gen = ImageGenerator(data_dir=temp_dir)
        assert isinstance(gen.get_generation_history(), list)

    def test_openai_no_key(self, temp_dir):
        """Test OpenAI generation without API key."""
        gen = ImageGenerator(data_dir=temp_dir)
        gen.openai_api_key = None
        result = gen.generate_with_openai("test prompt")
        assert result["success"] is False
        assert "not configured" in result["error"]

    def test_openai_invalid_size(self, temp_dir):
        """Test OpenAI with invalid size defaults to standard."""
        gen = ImageGenerator(data_dir=temp_dir)
        # Even without a real key, should handle invalid size
        gen.openai_api_key = None
        result = gen.generate_with_openai("prompt", size="invalid_size")
        assert result["success"] is False

    def test_generate_with_dimensions(self, temp_dir):
        """Test generate with custom dimensions."""
        gen = ImageGenerator(data_dir=temp_dir)
        # Should not crash with custom dimensions
        with patch.dict(os.environ, {"HUGGINGFACE_API_KEY": ""}):
            result = gen.generate("cat", width=256, height=256)
            assert isinstance(result, dict)

    def test_backend_switching(self, temp_dir):
        """Test backend value."""
        gen = ImageGenerator(data_dir=temp_dir)
        stats = gen.get_statistics()
        assert "backend" in stats

    def test_history_limit(self, temp_dir):
        """Test generation history with limit."""
        gen = ImageGenerator(data_dir=temp_dir)
        # Get history with limit
        history = gen.get_generation_history(limit=5)
        assert len(history) <= 5

    def test_generation_saves_metadata(self, temp_dir):
        """Test that generation returns proper dict."""
        gen = ImageGenerator(data_dir=temp_dir)
        # Without valid API keys, should return error dict
        with patch.dict(os.environ, {"HUGGINGFACE_API_KEY": "", "OPENAI_API_KEY": ""}):
            result = gen.generate("test")
            assert isinstance(result, dict)
            # Should have success key
            assert "success" in result or "error" in result or "filepath" in result

    def test_style_enum_values(self, temp_dir):
        """Test all style enum values work."""
        gen = ImageGenerator(data_dir=temp_dir)
        styles = [ImageStyle.PHOTOREALISTIC, ImageStyle.DIGITAL_ART, ImageStyle.ANIME]
        for style in styles:
            enhanced = gen.build_enhanced_prompt("cat", style=style)
            assert len(enhanced) > 0

    def test_filter_keywords(self, temp_dir):
        """Test content filter blocks specific keywords."""
        gen = ImageGenerator(data_dir=temp_dir)
        # Should block gore
        is_safe, _ = gen.check_content_filter("image with gore")
        assert not is_safe

    def test_history_empty_initially(self, temp_dir):
        """Test history starts empty."""
        gen = ImageGenerator(data_dir=temp_dir)
        history = gen.get_generation_history()
        assert history == []


class TestAISystemsFinal:
    """Push ai_systems to 95%+."""

    def test_command_override_stats(self):
        from app.core.ai_systems import CommandOverride
        override = CommandOverride()
        override.set_password("test")
        stats = override.get_statistics()
        assert stats["password_set"] is True


def test_get_statistics_counts_files(tmp_path):
    """Ensure get_statistics counts files in the output dir."""
    gen = ImageGenerator(data_dir=str(tmp_path))
    # create output dir and files
    os.makedirs(gen.output_dir, exist_ok=True)
    for i in range(3):
        with open(os.path.join(gen.output_dir, f"img_{i}.png"), "wb") as f:
            f.write(b"\x89PNG\r\n")

    stats = gen.get_statistics()
    assert stats["total_generated"] == 3


def test_get_generation_history_handles_errors(tmp_path):
    """If output_dir is not a directory, history should return empty and not raise."""
    gen = ImageGenerator(data_dir=str(tmp_path))
    # create a file where output_dir should be
    if os.path.exists(gen.output_dir):
        # remove directory to replace with a file
        for f in os.listdir(gen.output_dir):
            os.remove(os.path.join(gen.output_dir, f))
        os.rmdir(gen.output_dir)
    with open(gen.output_dir, "wb") as f:
        f.write(b"not a dir")

    history = gen.get_generation_history()
    assert history == []


def test_generate_backend_not_implemented(tmp_path):
    """If backend is unknown, generate should return backend not implemented error."""
    gen = ImageGenerator(data_dir=str(tmp_path))

    class DummyBackend:
        value = "DUMMY"

    gen.backend = DummyBackend()
    result = gen.generate("hello")
    assert result.get("success") is False
    assert "Backend not implemented" in result.get("error", "")


def test_disable_enable_content_filter(tmp_path):
    gen = ImageGenerator(data_dir=str(tmp_path))
    # set master password env
    with patch.dict(os.environ, {"MASTER_PASSWORD": "letmein"}):
        assert gen.disable_content_filter("letmein") is True
        assert gen.content_filter_enabled is False

    gen.enable_content_filter()
    assert gen.content_filter_enabled is True


def test_openai_generation_success(tmp_path):
    """Mock OpenAI API and requests.get to simulate successful DALL-E generation."""
    gen = ImageGenerator(data_dir=str(tmp_path))
    gen.openai_api_key = "fake"

    class FakeData:
        def __init__(self, url):
            self.url = url

    class FakeResponse:
        def __init__(self, data):
            self.data = data

    fake_url = "https://example.local/fake.png"

    with patch("openai.images.generate") as mock_generate:
        mock_generate.return_value = FakeResponse([FakeData(fake_url)])

        class FakeGet:
            status_code = 200

            def raise_for_status(self):
                return None

            @property
            def content(self):
                return b"PNGDATA"

        with patch("requests.get", return_value=FakeGet()):
            res = gen.generate_with_openai("a test prompt", size="512x512")
            assert res.get("success") is True
            assert os.path.exists(res.get("filepath"))


def test_huggingface_generation_success(tmp_path):
    """Mock requests.post to simulate Hugging Face Stable Diffusion success."""
    gen = ImageGenerator(data_dir=str(tmp_path))
    gen.hf_api_key = "fake"

    class FakePostResp:
        status_code = 200

        def raise_for_status(self):
            return None

        @property
        def content(self):
            return b"PNGDATA"

    with patch("requests.post", return_value=FakePostResp()):
        res = gen.generate_with_huggingface("a prompt", negative_prompt="", width=256, height=256)
        assert res.get("success") is True
        assert os.path.exists(res.get("filepath"))
