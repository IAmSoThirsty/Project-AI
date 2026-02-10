"""
DeepSeek V3.2 (Mixture-of-Experts) Language Model Integration.

This module provides inference capabilities for DeepSeek V3.2, a state-of-the-art
Mixture-of-Experts (MoE) language model. The MoE architecture is internal to the
model and handled automatically.

Features:
- Text completion and chat inference
- Support for Hugging Face models
- GPU acceleration with automatic fallback to CPU
- Configurable generation parameters
- Content filtering and safety checks
- Error handling and logging
"""

import logging
import os
from enum import Enum
from typing import Any

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class InferenceMode(Enum):
    """DeepSeek inference modes."""

    COMPLETION = "completion"
    CHAT = "chat"


class DeepSeekV32:
    """DeepSeek V3.2 Mixture-of-Experts language model interface.

    This class provides a high-level API for performing inference with the
    DeepSeek V3.2 model. The MoE architecture is handled internally by the model.

    Attributes:
        model_name: Hugging Face model identifier
        device: Computation device (cuda, mps, or cpu)
        max_length: Maximum sequence length for generation
        temperature: Sampling temperature (higher = more random)
        top_p: Nucleus sampling parameter
        top_k: Top-k sampling parameter
    """

    # Default model name on Hugging Face
    DEFAULT_MODEL = "deepseek-ai/deepseek-v3"

    # Content filtering keywords (same as image generator)
    BLOCKED_KEYWORDS = [
        "nsfw",
        "explicit",
        "nude",
        "violence",
        "gore",
        "hate",
        "illegal",
        "drug",
        "weapon",
        "harm",
        "abuse",
        "discrimin",
        "racist",
        "sexist",
        "child",
    ]

    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
        max_length: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        use_cache: bool = True,
    ):
        """Initialize DeepSeek V3.2 inference engine.

        Args:
            model_name: Hugging Face model identifier (default: deepseek-ai/deepseek-v3)
            device: Device for inference (cuda/mps/cpu), auto-detected if None
            max_length: Maximum generation length
            temperature: Sampling temperature (0.0-2.0)
            top_p: Nucleus sampling threshold
            top_k: Top-k sampling parameter
            use_cache: Whether to use model cache for faster inference
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self.max_length = max_length
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.use_cache = use_cache

        # Detect device
        self.device = self._detect_device(device)
        logger.info("Using device: %s", self.device)

        # Model and tokenizer (lazy loaded)
        self._model = None
        self._tokenizer = None
        self._model_loaded = False

        # Content filter
        self.content_filter_enabled = True

        # API key (if using inference API instead of local model)
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")

    def _detect_device(self, device: str | None) -> str:
        """Detect the best available device for inference.

        Args:
            device: User-specified device or None for auto-detection

        Returns:
            Device string: 'cuda', 'mps', or 'cpu'
        """
        if device:
            return device

        try:
            import torch

            if torch.cuda.is_available():
                return "cuda"
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            logger.warning("PyTorch not available, falling back to CPU")

        return "cpu"

    def _load_model(self) -> bool:
        """Load the model and tokenizer.

        Returns:
            True if successful, False otherwise
        """
        if self._model_loaded:
            return True

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer

            logger.info("Loading model: %s", self.model_name)

            # Load tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True,
            )

            # Load model with appropriate device settings
            if self.device == "cpu":
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    trust_remote_code=True,
                    torch_dtype="auto",
                )
            else:
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    trust_remote_code=True,
                    torch_dtype="auto",
                    device_map="auto",
                )

            # Move to device if not using device_map
            if self.device == "cpu":
                self._model = self._model.to(self.device)

            self._model_loaded = True
            logger.info("Model loaded successfully")
            return True

        except ImportError as e:
            logger.error(
                f"Required library not installed: {e}. "
                "Install with: pip install transformers torch accelerate"
            )
            return False
        except Exception as e:
            logger.error("Error loading model: %s", e)
            return False

    def check_content_filter(self, text: str) -> tuple[bool, str]:
        """Check if text passes content filter.

        Args:
            text: Text to check

        Returns:
            Tuple of (is_safe, reason)
        """
        if not self.content_filter_enabled:
            return True, "Content filter disabled"

        text_lower = text.lower()
        for keyword in self.BLOCKED_KEYWORDS:
            if keyword in text_lower:
                return False, f"Blocked keyword detected: {keyword}"

        return True, "Content filter passed"

    def generate_completion(
        self,
        prompt: str,
        max_new_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        do_sample: bool = True,
    ) -> dict[str, Any]:
        """Generate text completion for a prompt.

        Args:
            prompt: Input prompt text
            max_new_tokens: Maximum new tokens to generate (overrides max_length)
            temperature: Sampling temperature (overrides default)
            top_p: Nucleus sampling threshold (overrides default)
            top_k: Top-k sampling parameter (overrides default)
            do_sample: Whether to use sampling (True) or greedy decoding (False)

        Returns:
            Dictionary with 'success', 'text', 'prompt', and optional 'error'
        """
        # Content filter check
        is_safe, reason = self.check_content_filter(prompt)
        if not is_safe:
            return {
                "success": False,
                "error": f"Content filter: {reason}",
                "prompt": prompt,
            }

        # Load model if needed
        if not self._load_model():
            return {
                "success": False,
                "error": "Failed to load model",
                "prompt": prompt,
            }

        try:
            # Tokenize input
            inputs = self._tokenizer(prompt, return_tensors="pt").to(self.device)

            # Use provided parameters or defaults
            gen_temp = temperature if temperature is not None else self.temperature
            gen_top_p = top_p if top_p is not None else self.top_p
            gen_top_k = top_k if top_k is not None else self.top_k
            gen_max_new = (
                max_new_tokens if max_new_tokens is not None else self.max_length
            )

            # Generate
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=gen_max_new,
                temperature=gen_temp,
                top_p=gen_top_p,
                top_k=gen_top_k,
                do_sample=do_sample,
                use_cache=self.use_cache,
                pad_token_id=self._tokenizer.eos_token_id,
            )

            # Decode output
            generated_text = self._tokenizer.decode(
                outputs[0], skip_special_tokens=True
            )

            return {
                "success": True,
                "text": generated_text,
                "prompt": prompt,
                "model": self.model_name,
            }

        except Exception as e:
            logger.error("Generation error: %s", e)
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt,
            }

    def generate_chat(
        self,
        messages: list[dict[str, str]],
        max_new_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        do_sample: bool = True,
    ) -> dict[str, Any]:
        """Generate chat response for conversation history.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
                     Example: [{"role": "user", "content": "Hello"}]
            max_new_tokens: Maximum new tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling threshold
            top_k: Top-k sampling parameter
            do_sample: Whether to use sampling

        Returns:
            Dictionary with 'success', 'text', 'messages', and optional 'error'
        """
        # Content filter check on last user message
        user_messages = [m for m in messages if m.get("role") == "user"]
        if user_messages:
            last_message = user_messages[-1].get("content", "")
            is_safe, reason = self.check_content_filter(last_message)
            if not is_safe:
                return {
                    "success": False,
                    "error": f"Content filter: {reason}",
                    "messages": messages,
                }

        # Load model if needed
        if not self._load_model():
            return {
                "success": False,
                "error": "Failed to load model",
                "messages": messages,
            }

        try:
            # Apply chat template if available
            if hasattr(self._tokenizer, "apply_chat_template"):
                prompt = self._tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True,
                )
            else:
                # Fallback: simple concatenation
                prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
                prompt += "\nassistant:"

            # Use completion method with formatted prompt
            result = self.generate_completion(
                prompt=prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                do_sample=do_sample,
            )

            # Add messages to result
            if result["success"]:
                result["messages"] = messages

            return result

        except Exception as e:
            logger.error("Chat generation error: %s", e)
            return {
                "success": False,
                "error": str(e),
                "messages": messages,
            }

    def update_parameters(
        self,
        max_length: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
    ) -> None:
        """Update generation parameters.

        Args:
            max_length: New maximum length
            temperature: New temperature
            top_p: New top_p
            top_k: New top_k
        """
        if max_length is not None:
            self.max_length = max_length
        if temperature is not None:
            self.temperature = temperature
        if top_p is not None:
            self.top_p = top_p
        if top_k is not None:
            self.top_k = top_k

    def get_model_info(self) -> dict[str, Any]:
        """Get information about the loaded model.

        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "device": self.device,
            "loaded": self._model_loaded,
            "max_length": self.max_length,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "content_filter_enabled": self.content_filter_enabled,
        }

    def unload_model(self) -> None:
        """Unload model from memory to free resources."""
        if self._model is not None:
            del self._model
            self._model = None
        if self._tokenizer is not None:
            del self._tokenizer
            self._tokenizer = None
        self._model_loaded = False

        # Clear CUDA cache if available
        try:
            import torch

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass

        logger.info("Model unloaded")
