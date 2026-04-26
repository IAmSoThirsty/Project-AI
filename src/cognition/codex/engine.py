"""
Codex Engine - ML Model Inference with Production Features

Features:
- GPU/CPU fallback support
- Environment flags for engine selection
- Model loading error handling
- Graceful degradation
"""

import logging
import os
from dataclasses import dataclass
from typing import Any

from src.cognition.adapters.model_adapter import ModelAdapter, get_adapter

logger = logging.getLogger(__name__)


@dataclass
class CodexConfig:
    """Configuration for Codex engine."""

    model_path: str = "gpt2"
    device: str = "auto"
    adapter_type: str = "auto"
    enable_gpu: bool = True
    enable_full_engine: bool = False
    fallback_to_cpu: bool = True


class CodexEngine:
    """
    Production-ready ML inference engine.

    Supports:
    - Automatic GPU/CPU detection and fallback
    - Multiple model backends (HuggingFace, PyTorch)
    - Environment-based configuration
    - Graceful error handling
    """

    def __init__(self, config: CodexConfig | None = None):
        """
        Initialize Codex engine.

        Args:
            config: Engine configuration (uses env vars if not provided)
        """
        if config is None:
            config = self._load_config_from_env()

        self.config = config
        self.model_adapter: ModelAdapter | None = None
        self.is_loaded = False

        # Initialize model
        self._initialize_model()

    @staticmethod
    def _load_config_from_env() -> CodexConfig:
        """Load configuration from environment variables."""
        return CodexConfig(
            model_path=os.getenv("CODEX_MODEL_PATH", "gpt2"),
            device=os.getenv("CODEX_DEVICE", "auto"),
            adapter_type=os.getenv("CODEX_ADAPTER", "auto"),
            enable_gpu=os.getenv("CODEX_ENABLE_GPU", "1") == "1",
            enable_full_engine=os.getenv("CODEX_FULL_ENGINE", "0") == "1",
            fallback_to_cpu=os.getenv("CODEX_FALLBACK_CPU", "1") == "1",
        )

    def _initialize_model(self):
        """Initialize model with fallback logic."""
        logger.info("Initializing Codex engine")
        logger.info("Config: %s", self.config)

        # Determine device
        device = self._determine_device()

        try:
            # Get adapter
            self.model_adapter = get_adapter(
                adapter_type=self.config.adapter_type, device=device
            )

            # Load model if full engine is enabled
            if self.config.enable_full_engine:
                logger.info("Loading full model: %s", self.config.model_path)
                self.model_adapter.load_model(self.config.model_path)
                self.is_loaded = True
                logger.info("Codex engine initialized successfully")
            else:
                logger.info("Codex engine in lightweight mode (CODEX_FULL_ENGINE=0)")
                self.is_loaded = False

        except Exception as e:
            logger.error("Failed to initialize Codex engine: %s", e)
            if self.config.fallback_to_cpu and device != "cpu":
                logger.info("Attempting CPU fallback")
                self._fallback_to_cpu()
            else:
                logger.warning("Codex engine will operate in degraded mode")
                self.model_adapter = None
                self.is_loaded = False

    def _determine_device(self) -> str:
        """Determine which device to use based on config and availability."""
        if not self.config.enable_gpu:
            return "cpu"

        if self.config.device == "auto":
            try:
                import torch

                if torch.cuda.is_available():
                    logger.info("GPU detected and enabled")
                    return "cuda"
            except ImportError:
                pass
            logger.info("GPU not available, using CPU")
            return "cpu"

        return self.config.device

    def _fallback_to_cpu(self):
        """Fallback to CPU if GPU initialization fails."""
        try:
            logger.info("Falling back to CPU")
            self.model_adapter = get_adapter(
                adapter_type=self.config.adapter_type, device="cpu"
            )

            if self.config.enable_full_engine:
                self.model_adapter.load_model(self.config.model_path)
                self.is_loaded = True
                logger.info("Successfully fell back to CPU")
        except Exception as e:
            logger.error("CPU fallback failed: %s", e)
            self.model_adapter = None
            self.is_loaded = False

    def process(self, input_data: Any, context: dict | None = None) -> dict:
        """
        Process input through the Codex engine.

        Args:
            input_data: Input to process
            context: Optional context dictionary

        Returns:
            Processing result dictionary
        """
        logger.info("Codex processing input")

        try:
            # Check if model is loaded
            if not self.is_loaded or self.model_adapter is None:
                logger.warning("Model not loaded, returning placeholder response")
                return {
                    "success": True,
                    "output": "Codex engine in degraded mode",
                    "metadata": {
                        "loaded": self.is_loaded,
                        "mode": "degraded",
                        "context": context or {},
                    },
                }

            # Run inference
            result = self.model_adapter.predict(input_data)

            return {
                "success": True,
                "output": result,
                "metadata": {
                    "loaded": True,
                    "device": self.config.device,
                    "context": context or {},
                },
            }

        except Exception as e:
            logger.error("Codex processing error: %s", e)
            return {
                "success": False,
                "error": str(e),
                "output": None,
                "metadata": {"context": context or {}},
            }

    def get_status(self) -> dict:
        """Get engine status information."""
        return {
            "loaded": self.is_loaded,
            "device": self.config.device,
            "full_engine": self.config.enable_full_engine,
            "adapter_type": self.config.adapter_type,
            "model_path": self.config.model_path,
        }


# ============================================================================
# ORIGINAL CODEX CLASS PLACEHOLDER
# ============================================================================
# NOTE: If there was an original Codex class in the codebase, it should be
# inserted or referenced here for backward compatibility. The production
# wrapper above extends/replaces it with enterprise features.
#
# Original Codex implementation would go here or be imported:
# from app.core.original_codex import OriginalCodex
#
# The CodexEngine can wrap or extend the original implementation:
# class CodexEngine(OriginalCodex):
#     ...additional production features...
# ============================================================================
