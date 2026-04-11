#                                           [2026-04-09 05:35]
#                                          Productivity: Ultimate
"""
Transformer-based Threat Predictor
===================================

Implements Transformer architecture for advanced threat prediction.
Uses self-attention to capture complex relationships in security events.
"""

import logging
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class MultiHeadAttention:
    """Multi-head self-attention mechanism."""
    
    def __init__(self, d_model: int, num_heads: int):
        """
        Initialize multi-head attention.
        
        Args:
            d_model: Model dimension
            num_heads: Number of attention heads
        """
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        # Weight matrices
        self.W_q = np.random.randn(d_model, d_model) * 0.01
        self.W_k = np.random.randn(d_model, d_model) * 0.01
        self.W_v = np.random.randn(d_model, d_model) * 0.01
        self.W_o = np.random.randn(d_model, d_model) * 0.01
    
    def scaled_dot_product_attention(
        self,
        Q: np.ndarray,
        K: np.ndarray,
        V: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute scaled dot-product attention.
        
        Args:
            Q: Query matrix
            K: Key matrix
            V: Value matrix
            mask: Optional attention mask
            
        Returns:
            (attention_output, attention_weights) tuple
        """
        # Compute attention scores
        scores = np.dot(Q, K.T) / np.sqrt(self.d_k)
        
        # Apply mask if provided
        if mask is not None:
            scores = np.where(mask, scores, -1e9)
        
        # Softmax
        exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        attention_weights = exp_scores / np.sum(exp_scores, axis=-1, keepdims=True)
        
        # Apply attention to values
        output = np.dot(attention_weights, V)
        
        return output, attention_weights
    
    def forward(
        self,
        x: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Forward pass through multi-head attention.
        
        Args:
            x: Input tensor (seq_len, d_model)
            mask: Optional attention mask
            
        Returns:
            Attention output
        """
        seq_len = x.shape[0]
        
        # Linear projections
        Q = np.dot(x, self.W_q)
        K = np.dot(x, self.W_k)
        V = np.dot(x, self.W_v)
        
        # Split into heads (simplified, treating as single head for demo)
        attention_output, _ = self.scaled_dot_product_attention(Q, K, V, mask)
        
        # Output projection
        output = np.dot(attention_output, self.W_o)
        
        return output


class FeedForward:
    """Position-wise feed-forward network."""
    
    def __init__(self, d_model: int, d_ff: int):
        """
        Initialize feed-forward network.
        
        Args:
            d_model: Model dimension
            d_ff: Feed-forward dimension
        """
        self.W1 = np.random.randn(d_model, d_ff) * 0.01
        self.b1 = np.zeros(d_ff)
        self.W2 = np.random.randn(d_ff, d_model) * 0.01
        self.b2 = np.zeros(d_model)
    
    def relu(self, x: np.ndarray) -> np.ndarray:
        """ReLU activation."""
        return np.maximum(0, x)
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        Forward pass through feed-forward network.
        
        Args:
            x: Input tensor
            
        Returns:
            Output tensor
        """
        # First layer with ReLU
        hidden = self.relu(np.dot(x, self.W1) + self.b1)
        
        # Second layer
        output = np.dot(hidden, self.W2) + self.b2
        
        return output


class TransformerBlock:
    """Single Transformer encoder block."""
    
    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1):
        """
        Initialize Transformer block.
        
        Args:
            d_model: Model dimension
            num_heads: Number of attention heads
            d_ff: Feed-forward dimension
            dropout: Dropout rate
        """
        self.attention = MultiHeadAttention(d_model, num_heads)
        self.feed_forward = FeedForward(d_model, d_ff)
        self.dropout = dropout
        
        # Layer normalization parameters
        self.gamma1 = np.ones(d_model)
        self.beta1 = np.zeros(d_model)
        self.gamma2 = np.ones(d_model)
        self.beta2 = np.zeros(d_model)
    
    def layer_norm(self, x: np.ndarray, gamma: np.ndarray, beta: np.ndarray) -> np.ndarray:
        """Layer normalization."""
        mean = np.mean(x, axis=-1, keepdims=True)
        std = np.std(x, axis=-1, keepdims=True)
        return gamma * (x - mean) / (std + 1e-6) + beta
    
    def forward(self, x: np.ndarray, mask: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Forward pass through Transformer block.
        
        Args:
            x: Input tensor
            mask: Optional attention mask
            
        Returns:
            Output tensor
        """
        # Multi-head attention with residual connection
        attention_output = self.attention.forward(x, mask)
        x = x + attention_output  # Residual
        x = self.layer_norm(x, self.gamma1, self.beta1)
        
        # Feed-forward with residual connection
        ff_output = self.feed_forward.forward(x)
        x = x + ff_output  # Residual
        x = self.layer_norm(x, self.gamma2, self.beta2)
        
        return x


class TransformerPredictor:
    """
    Transformer-based threat prediction model.
    
    Uses Transformer architecture with self-attention to analyze
    security event sequences and predict future threats.
    """
    
    def __init__(
        self,
        input_dim: int = 32,
        d_model: int = 128,
        num_heads: int = 8,
        num_layers: int = 4,
        d_ff: int = 512,
        dropout: float = 0.1,
        max_seq_length: int = 100
    ):
        """
        Initialize Transformer predictor.
        
        Args:
            input_dim: Input feature dimension
            d_model: Model dimension
            num_heads: Number of attention heads
            num_layers: Number of Transformer layers
            d_ff: Feed-forward dimension
            dropout: Dropout rate
            max_seq_length: Maximum sequence length
        """
        self.input_dim = input_dim
        self.d_model = d_model
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.d_ff = d_ff
        self.dropout = dropout
        self.max_seq_length = max_seq_length
        
        # Input embedding
        self.input_projection = np.random.randn(input_dim, d_model) * 0.01
        
        # Positional encoding
        self.positional_encoding = self._create_positional_encoding()
        
        # Transformer blocks
        self.transformer_blocks = [
            TransformerBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ]
        
        # Output projection
        self.output_projection = np.random.randn(d_model, 1) * 0.01
        
        self.is_trained = False
        
        logger.info(f"TransformerPredictor initialized: "
                   f"d_model={d_model}, layers={num_layers}, heads={num_heads}")
    
    def _create_positional_encoding(self) -> np.ndarray:
        """
        Create sinusoidal positional encoding.
        
        Returns:
            Positional encoding matrix
        """
        position = np.arange(self.max_seq_length)[:, np.newaxis]
        div_term = np.exp(np.arange(0, self.d_model, 2) * 
                         -(np.log(10000.0) / self.d_model))
        
        pe = np.zeros((self.max_seq_length, self.d_model))
        pe[:, 0::2] = np.sin(position * div_term)
        pe[:, 1::2] = np.cos(position * div_term)
        
        return pe
    
    def forward(
        self,
        x: np.ndarray,
        mask: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """
        Forward pass through Transformer.
        
        Args:
            x: Input sequence (seq_len, input_dim)
            mask: Optional attention mask
            
        Returns:
            Output tensor
        """
        seq_len = x.shape[0]
        
        # Input projection
        x = np.dot(x, self.input_projection)
        
        # Add positional encoding
        x = x + self.positional_encoding[:seq_len]
        
        # Pass through Transformer blocks
        for block in self.transformer_blocks:
            x = block.forward(x, mask)
        
        return x
    
    def predict_threat_sequence(
        self,
        sequence: np.ndarray
    ) -> Tuple[List[float], np.ndarray]:
        """
        Predict threat probability for each position in sequence.
        
        Args:
            sequence: Input event sequence (seq_len, input_dim)
            
        Returns:
            (threat_probabilities, attention_map) tuple
        """
        # Forward pass
        transformer_output = self.forward(sequence)
        
        # Project to threat scores
        threat_scores = np.dot(transformer_output, self.output_projection).flatten()
        
        # Apply sigmoid
        threat_probabilities = 1 / (1 + np.exp(-threat_scores))
        
        # Get attention map (simplified - would use actual attention weights)
        attention_map = np.abs(transformer_output)
        
        return threat_probabilities.tolist(), attention_map
    
    def predict_next_threat(
        self,
        sequence: np.ndarray,
        horizon: int = 1
    ) -> Tuple[float, dict]:
        """
        Predict threat probability for next time steps.
        
        Args:
            sequence: Input event sequence
            horizon: Prediction horizon (number of steps ahead)
            
        Returns:
            (threat_probability, analysis_dict) tuple
        """
        # Get predictions for sequence
        probabilities, attention_map = self.predict_threat_sequence(sequence)
        
        # Use last prediction as next-step prediction
        next_threat_prob = probabilities[-1]
        
        # Calculate trend
        if len(probabilities) > 1:
            trend = probabilities[-1] - probabilities[-2]
        else:
            trend = 0.0
        
        # Analyze attention patterns
        attention_weights = np.mean(attention_map, axis=1)
        most_important_idx = np.argmax(attention_weights)
        
        analysis = {
            'probability': next_threat_prob,
            'trend': trend,
            'confidence': float(1.0 - np.std(probabilities)),
            'sequence_avg': float(np.mean(probabilities)),
            'sequence_max': float(np.max(probabilities)),
            'critical_index': int(most_important_idx),
            'attention_weights': attention_weights.tolist()
        }
        
        return next_threat_prob, analysis
    
    def train_step(
        self,
        sequences: List[np.ndarray],
        labels: List[np.ndarray],
        learning_rate: float = 0.0001
    ) -> float:
        """
        Perform single training step.
        
        Args:
            sequences: List of input sequences
            labels: List of label sequences
            learning_rate: Learning rate
            
        Returns:
            Average loss
        """
        total_loss = 0.0
        
        for sequence, label in zip(sequences, labels):
            # Forward pass
            predictions, _ = self.predict_threat_sequence(sequence)
            predictions = np.array(predictions)
            
            # Mean squared error loss
            loss = np.mean((predictions - label) ** 2)
            total_loss += loss
            
            # Simplified weight update (placeholder for demonstration)
            # In production, use proper backpropagation
            error = np.mean(predictions - label)
            self.output_projection -= learning_rate * error * 0.01
        
        return total_loss / len(sequences)
    
    def train(
        self,
        train_sequences: List[np.ndarray],
        train_labels: List[np.ndarray],
        epochs: int = 10,
        learning_rate: float = 0.0001,
        validation_split: float = 0.2
    ) -> dict:
        """
        Train the Transformer model.
        
        Args:
            train_sequences: Training sequences
            train_labels: Training label sequences
            epochs: Number of epochs
            learning_rate: Learning rate
            validation_split: Validation data fraction
            
        Returns:
            Training history
        """
        # Split data
        split_idx = int(len(train_sequences) * (1 - validation_split))
        train_seq = train_sequences[:split_idx]
        train_lab = train_labels[:split_idx]
        val_seq = train_sequences[split_idx:]
        val_lab = train_labels[split_idx:]
        
        logger.info(f"Training Transformer: {len(train_seq)} train, {len(val_seq)} val samples")
        
        history = {'train_loss': [], 'val_loss': []}
        
        for epoch in range(epochs):
            # Training
            train_loss = self.train_step(train_seq, train_lab, learning_rate)
            
            # Validation
            val_losses = []
            for seq, label in zip(val_seq, val_lab):
                predictions, _ = self.predict_threat_sequence(seq)
                predictions = np.array(predictions)
                val_loss = np.mean((predictions - label) ** 2)
                val_losses.append(val_loss)
            
            avg_val_loss = np.mean(val_losses)
            
            history['train_loss'].append(train_loss)
            history['val_loss'].append(avg_val_loss)
            
            if (epoch + 1) % 5 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs}: "
                          f"train_loss={train_loss:.4f}, val_loss={avg_val_loss:.4f}")
        
        self.is_trained = True
        logger.info("Training completed")
        
        return history
    
    def save_model(self, path: str):
        """Save model weights to file."""
        import pickle
        with open(path, 'wb') as f:
            pickle.dump({
                'input_projection': self.input_projection,
                'output_projection': self.output_projection,
                'positional_encoding': self.positional_encoding,
                'transformer_blocks': self.transformer_blocks,
                'config': {
                    'input_dim': self.input_dim,
                    'd_model': self.d_model,
                    'num_heads': self.num_heads,
                    'num_layers': self.num_layers,
                    'd_ff': self.d_ff,
                    'dropout': self.dropout,
                    'max_seq_length': self.max_seq_length
                }
            }, f)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load model weights from file."""
        import pickle
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.input_projection = data['input_projection']
            self.output_projection = data['output_projection']
            self.positional_encoding = data['positional_encoding']
            self.transformer_blocks = data['transformer_blocks']
            self.is_trained = True
        logger.info(f"Model loaded from {path}")
