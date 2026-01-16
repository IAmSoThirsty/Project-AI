"""
Model Adapter - Modular ML Model Interface

Provides abstract interface for different model backends,
enabling easy swapping and testing of ML models.
"""

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class ModelAdapter(ABC):
    """Abstract base class for model adapters."""

    @abstractmethod
    def load_model(self, model_path: str, **kwargs) -> Any:
        """
        Load a model from path.

        Args:
            model_path: Path to model file or identifier
            **kwargs: Additional loading parameters

        Returns:
            Loaded model object
        """
        pass

    @abstractmethod
    def predict(self, input_data: Any, **kwargs) -> Any:
        """
        Run inference on input data.

        Args:
            input_data: Input for model
            **kwargs: Additional inference parameters

        Returns:
            Model predictions
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if model backend is available."""
        pass


class HuggingFaceAdapter(ModelAdapter):
    """Adapter for Hugging Face Transformers models."""

    def __init__(self, device: str = "auto"):
        """
        Initialize HuggingFace adapter.

        Args:
            device: Device to use ('cuda', 'cpu', or 'auto')
        """
        self.device = device
        self.model = None
        self.tokenizer = None

    def load_model(self, model_path: str, **kwargs) -> Any:
        """Load a Hugging Face model."""
        try:
            from transformers import AutoModel, AutoTokenizer

            logger.info(f"Loading HuggingFace model: {model_path}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModel.from_pretrained(
                model_path, device_map=self.device, **kwargs
            )
            return self.model
        except Exception as e:
            logger.error(f"Failed to load HuggingFace model: {e}")
            raise

    def predict(self, input_data: Any, **kwargs) -> Any:
        """Run inference with HuggingFace model."""
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        try:
            inputs = self.tokenizer(
                input_data, return_tensors="pt", padding=True, truncation=True
            )
            outputs = self.model(**inputs, **kwargs)
            return outputs
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise

    def is_available(self) -> bool:
        """Check if HuggingFace transformers is available."""
        try:
            import transformers  # noqa: F401

            return True
        except ImportError:
            return False


class PyTorchAdapter(ModelAdapter):
    """Adapter for PyTorch models."""

    def __init__(self, device: str = "auto"):
        """
        Initialize PyTorch adapter.

        Args:
            device: Device to use ('cuda', 'cpu', or 'auto')
        """
        try:
            import torch

            if device == "auto":
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            else:
                self.device = device
            self.model = None
        except ImportError as e:
            raise ImportError("PyTorch not available. Install with: pip install torch") from e

    def load_model(self, model_path: str, **kwargs) -> Any:
        """Load a PyTorch model."""
        try:
            import torch

            logger.info(f"Loading PyTorch model: {model_path}")
            self.model = torch.load(model_path, map_location=self.device, **kwargs)
            self.model.eval()
            return self.model
        except Exception as e:
            logger.error(f"Failed to load PyTorch model: {e}")
            raise

    def predict(self, input_data: Any, **kwargs) -> Any:
        """Run inference with PyTorch model."""
        import torch

        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        try:
            with torch.no_grad():
                outputs = self.model(input_data, **kwargs)
            return outputs
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise

    def is_available(self) -> bool:
        """Check if PyTorch is available."""
        try:
            import torch  # noqa: F401

            return True
        except ImportError:
            return False


class DummyAdapter(ModelAdapter):
    """Dummy adapter for testing without actual models."""

    def __init__(self):
        """Initialize dummy adapter."""
        self.loaded = False

    def load_model(self, model_path: str, **kwargs) -> Any:
        """Simulate model loading."""
        logger.info(f"Dummy adapter: loading {model_path}")
        self.loaded = True
        return "dummy_model"

    def predict(self, input_data: Any, **kwargs) -> Any:
        """Return dummy predictions."""
        if not self.loaded:
            raise RuntimeError("Model not loaded")
        return {"prediction": "dummy_result", "input": str(input_data)}

    def is_available(self) -> bool:
        """Dummy adapter is always available."""
        return True


def get_adapter(adapter_type: str = "auto", **kwargs) -> ModelAdapter:
    """
    Factory function to get appropriate model adapter.

    Args:
        adapter_type: Type of adapter ('huggingface', 'pytorch', 'dummy', 'auto')
        **kwargs: Additional parameters for adapter

    Returns:
        ModelAdapter instance

    Raises:
        ValueError: If adapter type is invalid or unavailable
    """
    if adapter_type == "auto":
        # Try adapters in order of preference
        for atype in ["huggingface", "pytorch", "dummy"]:
            try:
                adapter = get_adapter(atype, **kwargs)
                if adapter.is_available():
                    logger.info(f"Auto-selected adapter: {atype}")
                    return adapter
            except (ValueError, ImportError):
                continue
        raise ValueError("No suitable adapter found")

    adapters = {
        "huggingface": HuggingFaceAdapter,
        "pytorch": PyTorchAdapter,
        "dummy": DummyAdapter,
    }

    if adapter_type not in adapters:
        raise ValueError(
            f"Unknown adapter type: {adapter_type}. "
            f"Available: {list(adapters.keys())}"
        )

    adapter_class = adapters[adapter_type]
    adapter = adapter_class(**kwargs)

    if not adapter.is_available():
        raise ValueError(f"Adapter '{adapter_type}' is not available")

    return adapter
