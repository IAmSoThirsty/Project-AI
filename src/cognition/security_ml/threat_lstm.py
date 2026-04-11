#                                           [2026-04-09 05:30]
#                                          Productivity: Ultimate
"""
LSTM-based Threat Prediction Model
===================================

Implements LSTM neural network for time-series threat prediction.
Analyzes sequences of security events to predict future attacks.
"""

import logging
from typing import List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class ThreatLSTM:
    """
    LSTM model for threat sequence prediction.
    
    Analyzes temporal patterns in security events to predict future threats.
    Uses a multi-layer LSTM architecture with attention mechanism.
    """
    
    def __init__(
        self,
        input_dim: int = 32,
        hidden_dim: int = 128,
        num_layers: int = 3,
        dropout: float = 0.3,
        bidirectional: bool = True
    ):
        """
        Initialize LSTM model.
        
        Args:
            input_dim: Input feature dimension
            hidden_dim: Hidden layer dimension
            num_layers: Number of LSTM layers
            dropout: Dropout rate
            bidirectional: Use bidirectional LSTM
        """
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout
        self.bidirectional = bidirectional
        
        # Model parameters (simplified for demonstration)
        # In production, this would use PyTorch or TensorFlow
        self.lstm_weights = self._initialize_weights()
        self.attention_weights = np.random.randn(hidden_dim, hidden_dim) * 0.01
        
        self.is_trained = False
        self.training_history = []
        
        logger.info(f"ThreatLSTM initialized: {input_dim}→{hidden_dim}x{num_layers}")
    
    def _initialize_weights(self) -> dict:
        """Initialize LSTM weights."""
        weights = {}
        for layer in range(self.num_layers):
            # First layer uses input_dim, others use hidden_dim
            layer_input_dim = self.input_dim if layer == 0 else self.hidden_dim
            
            # LSTM has 4 gates: input, forget, output, cell
            weights[f'layer_{layer}'] = {
                'W_i': np.random.randn(layer_input_dim, self.hidden_dim) * 0.01,
                'W_f': np.random.randn(layer_input_dim, self.hidden_dim) * 0.01,
                'W_o': np.random.randn(layer_input_dim, self.hidden_dim) * 0.01,
                'W_c': np.random.randn(layer_input_dim, self.hidden_dim) * 0.01,
                'b_i': np.zeros(self.hidden_dim),
                'b_f': np.zeros(self.hidden_dim),
                'b_o': np.zeros(self.hidden_dim),
                'b_c': np.zeros(self.hidden_dim)
            }
        
        return weights
    
    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        """Sigmoid activation function."""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def _tanh(self, x: np.ndarray) -> np.ndarray:
        """Tanh activation function."""
        return np.tanh(np.clip(x, -500, 500))
    
    def _lstm_cell(
        self,
        x: np.ndarray,
        h_prev: np.ndarray,
        c_prev: np.ndarray,
        weights: dict
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Single LSTM cell forward pass.
        
        Args:
            x: Input vector
            h_prev: Previous hidden state
            c_prev: Previous cell state
            weights: Cell weights
            
        Returns:
            (h_next, c_next) tuple
        """
        # Input gate
        i = self._sigmoid(np.dot(x, weights['W_i']) + weights['b_i'])
        
        # Forget gate
        f = self._sigmoid(np.dot(x, weights['W_f']) + weights['b_f'])
        
        # Output gate
        o = self._sigmoid(np.dot(x, weights['W_o']) + weights['b_o'])
        
        # Cell candidate
        c_tilde = self._tanh(np.dot(x, weights['W_c']) + weights['b_c'])
        
        # New cell state
        c_next = f * c_prev + i * c_tilde
        
        # New hidden state
        h_next = o * self._tanh(c_next)
        
        return h_next, c_next
    
    def forward(self, sequence: np.ndarray) -> np.ndarray:
        """
        Forward pass through LSTM.
        
        Args:
            sequence: Input sequence (seq_len, input_dim)
            
        Returns:
            Output sequence (seq_len, hidden_dim)
        """
        seq_len = sequence.shape[0]
        outputs = []
        
        # Process sequence
        for t in range(seq_len):
            x_t = sequence[t]
            
            # Forward through layers
            for layer in range(self.num_layers):
                weights = self.lstm_weights[f'layer_{layer}']
                h = np.zeros(self.hidden_dim)
                c = np.zeros(self.hidden_dim)
                h, c = self._lstm_cell(x_t, h, c, weights)
                x_t = h  # Output of one layer is input to next
                
                # Apply dropout (simplified)
                if self.dropout > 0 and layer < self.num_layers - 1:
                    mask = (np.random.rand(*h.shape) > self.dropout).astype(float)
                    x_t = x_t * mask / (1 - self.dropout)
            
            outputs.append(x_t)
        
        return np.array(outputs)
    
    def apply_attention(self, lstm_output: np.ndarray) -> np.ndarray:
        """
        Apply attention mechanism to LSTM output.
        
        Args:
            lstm_output: LSTM output sequence
            
        Returns:
            Attention-weighted output
        """
        # Compute attention scores
        scores = np.dot(lstm_output, self.attention_weights)
        attention = self._sigmoid(scores)
        
        # Apply attention weights
        weighted = lstm_output * attention
        
        # Sum over sequence dimension
        context = np.sum(weighted, axis=0)
        
        return context
    
    def predict_threat(
        self,
        sequence: np.ndarray,
        use_attention: bool = True
    ) -> Tuple[float, np.ndarray]:
        """
        Predict threat probability from event sequence.
        
        Args:
            sequence: Input event sequence (seq_len, input_dim)
            use_attention: Apply attention mechanism
            
        Returns:
            (threat_probability, feature_importance) tuple
        """
        # Forward pass
        lstm_output = self.forward(sequence)
        
        # Apply attention if enabled
        if use_attention:
            context = self.apply_attention(lstm_output)
        else:
            context = lstm_output[-1]  # Use last hidden state
        
        # Predict threat probability (simplified)
        threat_score = np.mean(context)
        threat_probability = self._sigmoid(threat_score * 2)  # Scale and sigmoid
        
        # Calculate feature importance
        feature_importance = np.abs(context) / (np.sum(np.abs(context)) + 1e-8)
        
        return float(threat_probability), feature_importance
    
    def train_step(
        self,
        sequences: List[np.ndarray],
        labels: List[float],
        learning_rate: float = 0.001
    ) -> float:
        """
        Perform single training step.
        
        Args:
            sequences: List of input sequences
            labels: List of threat labels (0 or 1)
            learning_rate: Learning rate
            
        Returns:
            Average loss
        """
        total_loss = 0.0
        
        for sequence, label in zip(sequences, labels):
            # Forward pass
            prediction, _ = self.predict_threat(sequence)
            
            # Binary cross-entropy loss
            loss = -(label * np.log(prediction + 1e-8) + 
                    (1 - label) * np.log(1 - prediction + 1e-8))
            total_loss += loss
            
            # Simplified gradient update (in production, use proper backprop)
            # This is a placeholder for demonstration
            error = prediction - label
            # Update weights based on error (simplified)
            for layer_weights in self.lstm_weights.values():
                for key in layer_weights:
                    if key.startswith('W_'):
                        layer_weights[key] -= learning_rate * error * 0.01
        
        avg_loss = total_loss / len(sequences)
        self.training_history.append(avg_loss)
        
        return avg_loss
    
    def train(
        self,
        train_sequences: List[np.ndarray],
        train_labels: List[float],
        epochs: int = 10,
        learning_rate: float = 0.001,
        validation_split: float = 0.2
    ) -> dict:
        """
        Train the LSTM model.
        
        Args:
            train_sequences: Training sequences
            train_labels: Training labels
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
        
        logger.info(f"Training LSTM: {len(train_seq)} train, {len(val_seq)} val samples")
        
        history = {'train_loss': [], 'val_loss': []}
        
        for epoch in range(epochs):
            # Training
            train_loss = self.train_step(train_seq, train_lab, learning_rate)
            
            # Validation
            val_predictions = [self.predict_threat(seq)[0] for seq in val_seq]
            val_loss = np.mean([
                -(label * np.log(pred + 1e-8) + (1 - label) * np.log(1 - pred + 1e-8))
                for pred, label in zip(val_predictions, val_lab)
            ])
            
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            
            if (epoch + 1) % 5 == 0:
                logger.info(f"Epoch {epoch+1}/{epochs}: "
                          f"train_loss={train_loss:.4f}, val_loss={val_loss:.4f}")
        
        self.is_trained = True
        logger.info("Training completed")
        
        return history
    
    def save_model(self, path: str):
        """Save model weights to file."""
        import pickle
        with open(path, 'wb') as f:
            pickle.dump({
                'lstm_weights': self.lstm_weights,
                'attention_weights': self.attention_weights,
                'config': {
                    'input_dim': self.input_dim,
                    'hidden_dim': self.hidden_dim,
                    'num_layers': self.num_layers,
                    'dropout': self.dropout,
                    'bidirectional': self.bidirectional
                }
            }, f)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load model weights from file."""
        import pickle
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.lstm_weights = data['lstm_weights']
            self.attention_weights = data['attention_weights']
            self.is_trained = True
        logger.info(f"Model loaded from {path}")
