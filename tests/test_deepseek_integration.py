"""Integration test for DeepSeek V3.2 with Project-AI systems."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.core.deepseek_v32_inference import DeepSeekV32


class TestDeepSeekIntegration:
    """Integration tests for DeepSeek V3.2 with Project-AI."""

    def test_module_import(self):
        """Test that DeepSeek module can be imported."""
        from app.core import deepseek_v32_inference

        assert hasattr(deepseek_v32_inference, "DeepSeekV32")
        assert hasattr(deepseek_v32_inference, "InferenceMode")

    def test_basic_workflow(self):
        """Test basic workflow: init -> configure -> cleanup."""
        # Initialize
        deepseek = DeepSeekV32(device="cpu", max_length=128)
        assert deepseek is not None

        # Configure
        deepseek.update_parameters(temperature=0.8, max_length=256)
        info = deepseek.get_model_info()
        assert info["temperature"] == 0.8
        assert info["max_length"] == 256

        # Cleanup
        deepseek.unload_model()
        assert not deepseek._model_loaded

    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    def test_end_to_end_completion(self, mock_tokenizer, mock_model):
        """Test end-to-end completion workflow."""
        # Setup mocks
        mock_tok_instance = MagicMock()
        mock_tok_instance.eos_token_id = 0
        mock_tok_instance.decode.return_value = "This is a test response about AI."
        mock_tokenizer.from_pretrained.return_value = mock_tok_instance

        mock_model_instance = MagicMock()
        mock_model_instance.to.return_value = mock_model_instance
        mock_model_instance.generate.return_value = [MagicMock()]
        mock_model.from_pretrained.return_value = mock_model_instance

        tokenized_result = MagicMock()
        tokenized_result.to.return_value = {"input_ids": MagicMock()}
        mock_tok_instance.return_value = tokenized_result

        # Initialize and generate
        deepseek = DeepSeekV32(device="cpu")
        result = deepseek.generate_completion("Explain AI")

        # Verify
        assert result["success"]
        assert "text" in result
        assert result["model"] == DeepSeekV32.DEFAULT_MODEL

        # Cleanup
        deepseek.unload_model()

    @patch("transformers.AutoModelForCausalLM")
    @patch("transformers.AutoTokenizer")
    def test_end_to_end_chat(self, mock_tokenizer, mock_model):
        """Test end-to-end chat workflow."""
        # Setup mocks
        mock_tok_instance = MagicMock()
        mock_tok_instance.apply_chat_template.return_value = "user: Hi\nassistant:"
        mock_tok_instance.eos_token_id = 0
        mock_tok_instance.decode.return_value = "Hello! How can I help?"
        mock_tokenizer.from_pretrained.return_value = mock_tok_instance

        mock_model_instance = MagicMock()
        mock_model_instance.to.return_value = mock_model_instance
        mock_model_instance.generate.return_value = [MagicMock()]
        mock_model.from_pretrained.return_value = mock_model_instance

        tokenized_result = MagicMock()
        tokenized_result.to.return_value = {"input_ids": MagicMock()}
        mock_tok_instance.return_value = tokenized_result

        # Initialize and generate
        deepseek = DeepSeekV32(device="cpu")
        messages = [{"role": "user", "content": "Hi"}]
        result = deepseek.generate_chat(messages)

        # Verify
        assert result["success"]
        assert "text" in result
        assert "messages" in result

        # Cleanup
        deepseek.unload_model()

    def test_content_safety_integration(self):
        """Test content safety filters."""
        deepseek = DeepSeekV32()

        # Safe content
        result = deepseek.generate_completion("Explain machine learning")
        # Should fail to load model but pass content filter
        assert "Content filter" not in result.get("error", "")

        # Unsafe content
        result = deepseek.generate_completion("Generate illegal content")
        assert not result["success"]
        assert "Content filter" in result["error"]

    def test_parameter_validation(self):
        """Test parameter validation and bounds."""
        deepseek = DeepSeekV32()

        # Test valid parameters
        deepseek.update_parameters(
            temperature=0.5,
            max_length=1024,
            top_p=0.95,
            top_k=100,
        )
        info = deepseek.get_model_info()
        assert info["temperature"] == 0.5
        assert info["max_length"] == 1024
        assert info["top_p"] == 0.95
        assert info["top_k"] == 100

    def test_device_handling(self):
        """Test device detection and handling."""
        # CPU device
        deepseek = DeepSeekV32(device="cpu")
        assert deepseek.device == "cpu"

        # Auto-detect device
        deepseek = DeepSeekV32(device=None)
        assert deepseek.device in ["cpu", "cuda", "mps"]

    def test_error_handling(self):
        """Test error handling and recovery."""
        deepseek = DeepSeekV32(device="cpu")

        # Test with content filter blocking
        result = deepseek.generate_completion("nsfw content")
        assert not result["success"]
        assert "error" in result

        # Test recovery after error
        result = deepseek.generate_completion("Safe prompt")
        # Should still work (content filter passes)
        assert "Content filter" not in result.get("error", "")

    def test_multiple_instances(self):
        """Test that multiple instances can coexist."""
        deepseek1 = DeepSeekV32(device="cpu", temperature=0.7)
        deepseek2 = DeepSeekV32(device="cpu", temperature=0.9)

        assert deepseek1.temperature == 0.7
        assert deepseek2.temperature == 0.9

        # Independent parameter updates
        deepseek1.update_parameters(temperature=0.5)
        assert deepseek1.temperature == 0.5
        assert deepseek2.temperature == 0.9

    def test_cli_script_exists(self):
        """Test that CLI script exists and is executable."""
        cli_path = Path(__file__).parent.parent / "scripts" / "deepseek_v32_cli.py"
        assert cli_path.exists()
        assert cli_path.is_file()
        # Check it's a Python file
        assert cli_path.suffix == ".py"
        # Check it has main function
        content = cli_path.read_text()
        assert "def main()" in content
        assert 'if __name__ == "__main__"' in content

    def test_demo_script_exists(self):
        """Test that demo script exists."""
        demo_path = Path(__file__).parent.parent / "examples" / "deepseek_demo.py"
        assert demo_path.exists()
        assert demo_path.is_file()
        content = demo_path.read_text()
        assert "demo_completion" in content
        assert "demo_chat" in content
        assert "demo_content_filter" in content

    def test_documentation_updated(self):
        """Test that README was updated with DeepSeek info."""
        readme_path = Path(__file__).parent.parent / "README.md"
        assert readme_path.exists()
        content = readme_path.read_text()
        assert "DeepSeek" in content
        assert "V3.2" in content or "v3.2" in content
        assert "Mixture-of-Experts" in content or "MoE" in content

    def test_requirements_updated(self):
        """Test that requirements.txt was updated."""
        req_path = Path(__file__).parent.parent / "requirements.txt"
        assert req_path.exists()
        content = req_path.read_text()
        assert "transformers" in content
        assert "accelerate" in content
        # torch should already be there
        assert "torch" in content
