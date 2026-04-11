"""
Security ML Module
==================

Machine learning models for security threat prediction and detection.
"""

from pathlib import Path

__version__ = "1.0.0"
__all__ = [
    "ThreatLSTM",
    "TransformerPredictor",
    "AnomalyDetector",
    "FeatureExtractor"
]

# Module paths
MODULE_DIR = Path(__file__).parent
MODELS_DIR = MODULE_DIR / "models"
DATA_DIR = MODULE_DIR / "data"

# Create directories
MODELS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
