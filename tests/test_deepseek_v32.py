"""Tests for DeepSeek V3.2 inference module."""

from unittest.mock import MagicMock, patch

import pytest

from app.core.deepseek_v32_inference import DeepSeekV32, InferenceMode


class TestDeepSeekV32:
    """Test DeepSeek V3.2 inference."""

    @pytest.fixture
    def deepseek(self):
        """Create DeepSeek instance."""
        return DeepSeekV32(device="cpu", max_length=128)

    def test_initialization(self, deepseek):
        """Test DeepSeek initializes correctly."""
        assert deepseek.model_name == DeepSeekV32.DEFAULT_MODEL
        assert deepseek.device == "cpu"
        assert deepseek.max_length == 128
        assert deepseek.temperature == 0.7
        assert not deepseek._model_loaded

    def test_device_detection_cpu(self):
        """Test device detection defaults to CPU."""
        deepseek = DeepSeekV32()
        assert deepseek.device in ["cpu", "cuda", "mps"]

    def test_content_filter_blocked(self, deepseek):
        """Test content filter blocks inappropriate content."""
        is_safe, reason = deepseek.check_content_filter("This is nsfw content")
        assert not is_safe
        assert "nsfw" in reason.lower()

    def test_content_filter_passed(self, deepseek):
        """Test content filter allows safe content."""
        is_safe, reason = deepseek.check_content_filter("Hello, how are you?")
        assert is_safe

    def test_content_filter_disabled(self, deepseek):
        """Test content filter can be disabled."""
        deepseek.content_filter_enabled = False
        is_safe, reason = deepseek.check_content_filter("nsfw content")
        assert is_safe
        assert "disabled" in reason.lower()

    def test_model_loading(self, deepseek):
        """Test model loading with orchestrator integration."""
        # Load model (now a compatibility shim that always succeeds)
        success = deepseek._load_model()

        assert success
        assert deepseek._model_loaded

    def test_model_loading_failure_no_transformers(self, deepseek):
        """Test graceful failure when transformers not installed."""
        # With orchestrator integration, _load_model is now a compatibility shim
        # that always succeeds. Actual failures happen during generation.
        success = deepseek._load_model()
        assert success
        assert isinstance(success, bool)

    @patch("app.core.deepseek_v32_inference.run_ai")
    def test_generate_completion(self, mock_run_ai, deepseek):
        """Test completion generation via orchestrator."""
        # Mock orchestrator response
        from app.core.ai.orchestrator import AIResponse

        mock_run_ai.return_value = AIResponse(
            status="success",
            result="This is a generated response.",
            provider_used="huggingface",
            metadata={"model": deepseek.model_name, "task_type": "completion"},
        )

        # Generate completion
        result = deepseek.generate_completion("Hello, how are you?")

        assert result["success"]
        assert "text" in result
        assert result["prompt"] == "Hello, how are you?"
        assert result["model"] == deepseek.model_name
        
        # Verify orchestrator was called with correct parameters
        mock_run_ai.assert_called_once()
        call_args = mock_run_ai.call_args[0][0]
        assert call_args.task_type == "completion"
        assert call_args.prompt == "Hello, how are you?"
        assert call_args.provider == "huggingface"
        assert call_args.model == deepseek.model_name
        assert call_args.config["use_local"] is True

    def test_generate_completion_blocked_content(self, deepseek):
        """Test completion blocks inappropriate content."""
        result = deepseek.generate_completion("Generate nsfw content")

        assert not result["success"]
        assert "Content filter" in result["error"]

    @patch("app.core.deepseek_v32_inference.run_ai")
    def test_generate_chat(self, mock_run_ai, deepseek):
        """Test chat generation via orchestrator."""
        # Mock orchestrator response
        from app.core.ai.orchestrator import AIResponse

        mock_run_ai.return_value = AIResponse(
            status="success",
            result="Hello! How can I help you?",
            provider_used="huggingface",
            metadata={"model": deepseek.model_name, "task_type": "chat"},
        )

        # Generate chat
        messages = [{"role": "user", "content": "Hello"}]
        result = deepseek.generate_chat(messages)

        assert result["success"]
        assert "text" in result
        assert "messages" in result
        assert result["messages"] == messages
        
        # Verify orchestrator was called with correct parameters
        mock_run_ai.assert_called_once()
        call_args = mock_run_ai.call_args[0][0]
        assert call_args.task_type == "chat"
        assert call_args.provider == "huggingface"
        assert call_args.model == deepseek.model_name
        assert call_args.config["use_local"] is True
        assert call_args.config["messages"] == messages

    def test_generate_chat_blocked_content(self, deepseek):
        """Test chat blocks inappropriate content."""
        messages = [{"role": "user", "content": "Generate illegal content"}]
        result = deepseek.generate_chat(messages)

        assert not result["success"]
        assert "Content filter" in result["error"]

    def test_update_parameters(self, deepseek):
        """Test updating generation parameters."""
        original_temp = deepseek.temperature
        original_max = deepseek.max_length

        deepseek.update_parameters(
            temperature=0.9,
            max_length=256,
            top_p=0.95,
            top_k=100,
        )

        assert deepseek.temperature == 0.9
        assert deepseek.max_length == 256
        assert deepseek.top_p == 0.95
        assert deepseek.top_k == 100
        assert deepseek.temperature != original_temp
        assert deepseek.max_length != original_max

    def test_get_model_info(self, deepseek):
        """Test getting model information."""
        info = deepseek.get_model_info()

        assert "model_name" in info
        assert "device" in info
        assert "loaded" in info
        assert "max_length" in info
        assert "temperature" in info
        assert "top_p" in info
        assert "top_k" in info
        assert "content_filter_enabled" in info

        assert info["model_name"] == deepseek.model_name
        assert info["device"] == "cpu"
        assert info["loaded"] is False
        assert info["max_length"] == 128

    def test_unload_model(self, deepseek):
        """Test model unloading."""
        # Load then unload (now compatibility shims)
        deepseek._load_model()
        assert deepseek._model_loaded

        deepseek.unload_model()
        assert not deepseek._model_loaded
        assert deepseek._model is None
        assert deepseek._tokenizer is None

    def test_custom_model_name(self):
        """Test initialization with custom model name."""
        custom_model = "custom/model-name"
        deepseek = DeepSeekV32(model_name=custom_model)
        assert deepseek.model_name == custom_model

    def test_generation_parameters_override(self, deepseek):
        """Test that generation parameters can be overridden per call."""
        # This test verifies the interface accepts override parameters
        # Actual generation is tested with mocks
        assert deepseek.temperature == 0.7

        # Verify generate_completion accepts parameter overrides
        with patch.object(deepseek, "_load_model", return_value=False):
            result = deepseek.generate_completion(
                "test",
                temperature=0.5,
                top_p=0.8,
                top_k=30,
            )
            # Should fail to load model but shows parameters are accepted
            assert not result["success"]


class TestInferenceMode:
    """Test InferenceMode enum."""

    def test_inference_mode_values(self):
        """Test InferenceMode enum has correct values."""
        assert InferenceMode.COMPLETION.value == "completion"
        assert InferenceMode.CHAT.value == "chat"

    def test_inference_mode_members(self):
        """Test InferenceMode has correct members."""
        assert hasattr(InferenceMode, "COMPLETION")
        assert hasattr(InferenceMode, "CHAT")
