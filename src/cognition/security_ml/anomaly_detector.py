#                                           [2026-04-09 05:40]
#                                          Productivity: Ultimate
"""
Advanced Anomaly Detector
==========================

Implements multiple anomaly detection algorithms for zero-day threat detection.
Uses statistical, isolation forest, and autoencoder-based approaches.
"""

import logging
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class IsolationTree:
    """Single tree for isolation forest."""
    
    def __init__(self, height_limit: int):
        """
        Initialize isolation tree.
        
        Args:
            height_limit: Maximum tree height
        """
        self.height_limit = height_limit
        self.split_feature = None
        self.split_value = None
        self.left = None
        self.right = None
        self.size = 0
        self.is_external = False
    
    def fit(self, X: np.ndarray, current_height: int = 0):
        """
        Build isolation tree from data.
        
        Args:
            X: Training data
            current_height: Current tree height
        """
        self.size = X.shape[0]
        
        # Stop conditions
        if current_height >= self.height_limit or self.size <= 1:
            self.is_external = True
            return
        
        # Random feature and split
        n_features = X.shape[1]
        self.split_feature = np.random.randint(0, n_features)
        
        feature_values = X[:, self.split_feature]
        min_val, max_val = feature_values.min(), feature_values.max()
        
        if min_val == max_val:
            self.is_external = True
            return
        
        self.split_value = np.random.uniform(min_val, max_val)
        
        # Split data
        left_mask = feature_values < self.split_value
        right_mask = ~left_mask
        
        # Build subtrees
        self.left = IsolationTree(self.height_limit)
        self.right = IsolationTree(self.height_limit)
        
        self.left.fit(X[left_mask], current_height + 1)
        self.right.fit(X[right_mask], current_height + 1)
    
    def path_length(self, x: np.ndarray, current_height: int = 0) -> float:
        """
        Calculate path length for a sample.
        
        Args:
            x: Sample
            current_height: Current path length
            
        Returns:
            Path length
        """
        if self.is_external:
            return current_height + self._c(self.size)
        
        if x[self.split_feature] < self.split_value:
            return self.left.path_length(x, current_height + 1)
        else:
            return self.right.path_length(x, current_height + 1)
    
    def _c(self, n: int) -> float:
        """Average path length of unsuccessful search in BST."""
        if n <= 1:
            return 0
        return 2 * (np.log(n - 1) + 0.5772156649) - 2 * (n - 1) / n


class IsolationForest:
    """
    Isolation Forest for anomaly detection.
    
    Isolates anomalies using random decision trees.
    """
    
    def __init__(self, n_estimators: int = 100, max_samples: int = 256):
        """
        Initialize isolation forest.
        
        Args:
            n_estimators: Number of trees
            max_samples: Number of samples per tree
        """
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.trees: List[IsolationTree] = []
        self.height_limit = int(np.ceil(np.log2(max_samples)))
        
        logger.info(f"IsolationForest initialized: {n_estimators} trees")
    
    def fit(self, X: np.ndarray):
        """
        Fit isolation forest on data.
        
        Args:
            X: Training data
        """
        n_samples = X.shape[0]
        
        for i in range(self.n_estimators):
            # Sample data
            sample_indices = np.random.choice(
                n_samples,
                min(self.max_samples, n_samples),
                replace=False
            )
            sample = X[sample_indices]
            
            # Build tree
            tree = IsolationTree(self.height_limit)
            tree.fit(sample)
            self.trees.append(tree)
        
        logger.info(f"Fitted {len(self.trees)} isolation trees")
    
    def anomaly_score(self, x: np.ndarray) -> float:
        """
        Calculate anomaly score for sample.
        
        Args:
            x: Sample
            
        Returns:
            Anomaly score (0-1, higher = more anomalous)
        """
        # Average path length across all trees
        avg_path_length = np.mean([tree.path_length(x) for tree in self.trees])
        
        # Normalize
        c = 2 * (np.log(self.max_samples - 1) + 0.5772156649) - \
            2 * (self.max_samples - 1) / self.max_samples
        
        score = 2 ** (-avg_path_length / c)
        
        return score
    
    def predict(self, X: np.ndarray, threshold: float = 0.6) -> np.ndarray:
        """
        Predict anomalies.
        
        Args:
            X: Data to predict
            threshold: Anomaly threshold
            
        Returns:
            Binary predictions (1 = anomaly)
        """
        scores = np.array([self.anomaly_score(x) for x in X])
        return (scores > threshold).astype(int)


class AutoEncoder:
    """
    Simple autoencoder for anomaly detection.
    
    Learns to reconstruct normal patterns; anomalies have high reconstruction error.
    """
    
    def __init__(
        self,
        input_dim: int,
        encoding_dim: int = 16,
        hidden_dims: Optional[List[int]] = None
    ):
        """
        Initialize autoencoder.
        
        Args:
            input_dim: Input dimension
            encoding_dim: Encoding (latent) dimension
            hidden_dims: Hidden layer dimensions
        """
        self.input_dim = input_dim
        self.encoding_dim = encoding_dim
        self.hidden_dims = hidden_dims or [32]
        
        # Build encoder
        self.encoder_weights = []
        prev_dim = input_dim
        for hidden_dim in self.hidden_dims:
            self.encoder_weights.append({
                'W': np.random.randn(prev_dim, hidden_dim) * 0.01,
                'b': np.zeros(hidden_dim)
            })
            prev_dim = hidden_dim
        
        # Encoding layer
        self.encoder_weights.append({
            'W': np.random.randn(prev_dim, encoding_dim) * 0.01,
            'b': np.zeros(encoding_dim)
        })
        
        # Build decoder (mirror of encoder)
        self.decoder_weights = []
        prev_dim = encoding_dim
        for hidden_dim in reversed(self.hidden_dims):
            self.decoder_weights.append({
                'W': np.random.randn(prev_dim, hidden_dim) * 0.01,
                'b': np.zeros(hidden_dim)
            })
            prev_dim = hidden_dim
        
        # Output layer
        self.decoder_weights.append({
            'W': np.random.randn(prev_dim, input_dim) * 0.01,
            'b': np.zeros(input_dim)
        })
        
        logger.info(f"AutoEncoder initialized: {input_dim}→{encoding_dim}→{input_dim}")
    
    def relu(self, x: np.ndarray) -> np.ndarray:
        """ReLU activation."""
        return np.maximum(0, x)
    
    def sigmoid(self, x: np.ndarray) -> np.ndarray:
        """Sigmoid activation."""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def encode(self, x: np.ndarray) -> np.ndarray:
        """
        Encode input to latent space.
        
        Args:
            x: Input vector
            
        Returns:
            Encoded vector
        """
        h = x
        for weights in self.encoder_weights[:-1]:
            h = self.relu(np.dot(h, weights['W']) + weights['b'])
        
        # Final encoding (no activation)
        encoding = np.dot(h, self.encoder_weights[-1]['W']) + self.encoder_weights[-1]['b']
        return encoding
    
    def decode(self, z: np.ndarray) -> np.ndarray:
        """
        Decode from latent space.
        
        Args:
            z: Latent vector
            
        Returns:
            Reconstructed vector
        """
        h = z
        for weights in self.decoder_weights[:-1]:
            h = self.relu(np.dot(h, weights['W']) + weights['b'])
        
        # Final output with sigmoid
        output = self.sigmoid(np.dot(h, self.decoder_weights[-1]['W']) + 
                             self.decoder_weights[-1]['b'])
        return output
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        Forward pass (encode + decode).
        
        Args:
            x: Input vector
            
        Returns:
            Reconstructed vector
        """
        encoding = self.encode(x)
        reconstruction = self.decode(encoding)
        return reconstruction
    
    def reconstruction_error(self, x: np.ndarray) -> float:
        """
        Calculate reconstruction error.
        
        Args:
            x: Input vector
            
        Returns:
            Mean squared error
        """
        reconstruction = self.forward(x)
        return np.mean((x - reconstruction) ** 2)
    
    def train_step(
        self,
        X: np.ndarray,
        learning_rate: float = 0.001
    ) -> float:
        """
        Single training step.
        
        Args:
            X: Training batch
            learning_rate: Learning rate
            
        Returns:
            Average loss
        """
        total_loss = 0.0
        
        for x in X:
            reconstruction = self.forward(x)
            loss = np.mean((x - reconstruction) ** 2)
            total_loss += loss
            
            # Simplified gradient update (placeholder)
            error = reconstruction - x
            for weights in self.encoder_weights:
                weights['W'] -= learning_rate * error.mean() * 0.01
        
        return total_loss / len(X)
    
    def fit(
        self,
        X: np.ndarray,
        epochs: int = 50,
        learning_rate: float = 0.001
    ):
        """
        Train autoencoder.
        
        Args:
            X: Training data
            epochs: Number of epochs
            learning_rate: Learning rate
        """
        logger.info(f"Training AutoEncoder on {len(X)} samples")
        
        for epoch in range(epochs):
            loss = self.train_step(X, learning_rate)
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs}: loss={loss:.6f}")


class AnomalyDetector:
    """
    Advanced anomaly detector combining multiple algorithms.
    
    Uses statistical methods, isolation forest, and autoencoder
    for robust zero-day threat detection.
    """
    
    def __init__(
        self,
        feature_dim: int,
        use_isolation_forest: bool = True,
        use_autoencoder: bool = True,
        use_statistical: bool = True
    ):
        """
        Initialize anomaly detector.
        
        Args:
            feature_dim: Feature dimension
            use_isolation_forest: Enable isolation forest
            use_autoencoder: Enable autoencoder
            use_statistical: Enable statistical detection
        """
        self.feature_dim = feature_dim
        
        # Components
        self.isolation_forest = IsolationForest() if use_isolation_forest else None
        self.autoencoder = AutoEncoder(feature_dim) if use_autoencoder else None
        
        # Statistical baselines
        self.mean = None
        self.std = None
        self.use_statistical = use_statistical
        
        # Thresholds
        self.isolation_threshold = 0.6
        self.autoencoder_threshold = 0.01
        self.statistical_threshold = 3.0  # z-score
        
        logger.info(f"AnomalyDetector initialized with {feature_dim} features")
    
    def fit(self, X: np.ndarray, train_autoencoder: bool = True):
        """
        Train anomaly detector on normal data.
        
        Args:
            X: Normal training data
            train_autoencoder: Whether to train autoencoder
        """
        logger.info(f"Training anomaly detector on {len(X)} samples")
        
        # Statistical baseline
        if self.use_statistical:
            self.mean = np.mean(X, axis=0)
            self.std = np.std(X, axis=0) + 1e-8
            logger.info("Statistical baseline computed")
        
        # Isolation forest
        if self.isolation_forest:
            self.isolation_forest.fit(X)
        
        # Autoencoder
        if self.autoencoder and train_autoencoder:
            self.autoencoder.fit(X, epochs=50)
        
        logger.info("Anomaly detector training completed")
    
    def detect(self, x: np.ndarray) -> Tuple[bool, float, Dict[str, float]]:
        """
        Detect if sample is anomalous.
        
        Args:
            x: Sample to check
            
        Returns:
            (is_anomaly, composite_score, component_scores) tuple
        """
        component_scores = {}
        votes = []
        
        # Statistical detection
        if self.use_statistical and self.mean is not None:
            z_scores = np.abs((x - self.mean) / self.std)
            max_z = np.max(z_scores)
            component_scores['statistical'] = float(max_z)
            votes.append(max_z > self.statistical_threshold)
        
        # Isolation forest
        if self.isolation_forest:
            iso_score = self.isolation_forest.anomaly_score(x)
            component_scores['isolation_forest'] = iso_score
            votes.append(iso_score > self.isolation_threshold)
        
        # Autoencoder
        if self.autoencoder:
            recon_error = self.autoencoder.reconstruction_error(x)
            component_scores['autoencoder'] = recon_error
            votes.append(recon_error > self.autoencoder_threshold)
        
        # Composite decision (majority voting)
        is_anomaly = sum(votes) >= 2 if len(votes) >= 2 else votes[0] if votes else False
        
        # Composite score (weighted average)
        if component_scores:
            # Normalize scores
            normalized_scores = []
            if 'statistical' in component_scores:
                normalized_scores.append(min(component_scores['statistical'] / 5.0, 1.0))
            if 'isolation_forest' in component_scores:
                normalized_scores.append(component_scores['isolation_forest'])
            if 'autoencoder' in component_scores:
                normalized_scores.append(min(component_scores['autoencoder'] / 0.05, 1.0))
            
            composite_score = np.mean(normalized_scores)
        else:
            composite_score = 0.0
        
        return is_anomaly, composite_score, component_scores
    
    def batch_detect(self, X: np.ndarray) -> List[Tuple[bool, float, Dict[str, float]]]:
        """
        Detect anomalies in batch.
        
        Args:
            X: Batch of samples
            
        Returns:
            List of detection results
        """
        return [self.detect(x) for x in X]
    
    def update_thresholds(
        self,
        isolation_threshold: Optional[float] = None,
        autoencoder_threshold: Optional[float] = None,
        statistical_threshold: Optional[float] = None
    ):
        """Update detection thresholds."""
        if isolation_threshold is not None:
            self.isolation_threshold = isolation_threshold
        if autoencoder_threshold is not None:
            self.autoencoder_threshold = autoencoder_threshold
        if statistical_threshold is not None:
            self.statistical_threshold = statistical_threshold
        
        logger.info(f"Updated thresholds: iso={self.isolation_threshold}, "
                   f"ae={self.autoencoder_threshold}, stat={self.statistical_threshold}")
