"""
Advanced Machine Learning Models Module
Provides enhanced ML capabilities beyond basic intent detection
"""

import os
import pickle
from typing import Any, Dict, List, Optional, Tuple

import numpy as np  # type: ignore
from sklearn.ensemble import (  # type: ignore
    GradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
from sklearn.metrics import accuracy_score, classification_report  # type: ignore
from sklearn.model_selection import train_test_split  # type: ignore
from sklearn.neural_network import MLPClassifier  # type: ignore


class AdvancedMLManager:
    """Manages advanced ML models for various prediction tasks."""
    
    def __init__(self, models_dir: str = "data/ml_models"):
        """
        Initialize ML manager.
        
        Args:
            models_dir: Directory to store trained models
        """
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        
        self.models: Dict[str, Any] = {}
        self.vectorizers: Dict[str, TfidfVectorizer] = {}
        
        # Initialize available models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize default ML models."""
        # Enhanced Intent Classifier (Random Forest)
        self.models['intent_rf'] = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # Sentiment Analysis (Gradient Boosting)
        self.models['sentiment_gb'] = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        # User Behavior Prediction (Neural Network)
        self.models['behavior_nn'] = MLPClassifier(
            hidden_layer_sizes=(128, 64, 32),
            activation='relu',
            solver='adam',
            max_iter=500,
            random_state=42
        )
        
        # Text vectorizer for NLP tasks
        self.vectorizers['default'] = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words='english'
        )
    
    def train_intent_classifier(
        self,
        texts: List[str],
        labels: List[str],
        model_name: str = 'intent_rf'
    ) -> Dict[str, float]:
        """
        Train intent classification model.
        
        Args:
            texts: Training text samples
            labels: Corresponding labels
            model_name: Name of model to train
            
        Returns:
            Training metrics dictionary
        """
        try:
            # Vectorize texts
            X = self.vectorizers['default'].fit_transform(texts)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, labels, test_size=0.2, random_state=42
            )
            
            # Train model
            model = self.models.get(model_name)
            if not model:
                raise ValueError(f"Model {model_name} not found")
            
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Save model
            self.save_model(model_name)
            
            return {
                'accuracy': accuracy,
                'samples': len(texts),
                'features': X.shape[1]
            }
            
        except Exception as e:
            print(f"Training error: {e}")
            return {'accuracy': 0.0, 'error': str(e)}
    
    def predict_intent(self, text: str, model_name: str = 'intent_rf') -> Tuple[str, float]:
        """
        Predict intent from text.
        
        Args:
            text: Input text
            model_name: Model to use for prediction
            
        Returns:
            Tuple of (predicted_label, confidence)
        """
        try:
            # Vectorize input
            X = self.vectorizers['default'].transform([text])
            
            # Get model
            model = self.models.get(model_name)
            if not model:
                return ("unknown", 0.0)
            
            # Predict
            prediction = model.predict(X)[0]
            
            # Get confidence (probability)
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(X)[0]
                confidence = float(np.max(proba))
            else:
                confidence = 0.5
            
            return (str(prediction), confidence)
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return ("error", 0.0)
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Input text
            
        Returns:
            Sentiment analysis results
        """
        try:
            # Use sentiment model if trained
            model = self.models.get('sentiment_gb')
            
            if model and hasattr(model, 'predict'):
                X = self.vectorizers['default'].transform([text])
                sentiment = model.predict(X)[0]
                
                if hasattr(model, 'predict_proba'):
                    proba = model.predict_proba(X)[0]
                    confidence = float(np.max(proba))
                else:
                    confidence = 0.5
                
                return {
                    'sentiment': str(sentiment),
                    'confidence': confidence,
                    'text_length': len(text)
                }
            else:
                # Fallback to simple sentiment
                return {
                    'sentiment': 'neutral',
                    'confidence': 0.5,
                    'text_length': len(text),
                    'note': 'Model not trained'
                }
                
        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return {'sentiment': 'error', 'confidence': 0.0}
    
    def predict_user_behavior(self, features: List[float]) -> str:
        """
        Predict user behavior pattern.
        
        Args:
            features: Feature vector describing user activity
            
        Returns:
            Predicted behavior category
        """
        try:
            model = self.models.get('behavior_nn')
            if not model or not hasattr(model, 'predict'):
                return "unknown"
            
            X = np.array(features).reshape(1, -1)
            prediction = model.predict(X)[0]
            
            return str(prediction)
            
        except Exception as e:
            print(f"Behavior prediction error: {e}")
            return "error"
    
    def save_model(self, model_name: str) -> bool:
        """
        Save trained model to disk.
        
        Args:
            model_name: Name of model to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            model = self.models.get(model_name)
            if not model:
                return False
            
            model_path = os.path.join(self.models_dir, f"{model_name}.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            
            # Also save vectorizer if exists
            vectorizer_path = os.path.join(self.models_dir, "vectorizer.pkl")
            with open(vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizers['default'], f)
            
            return True
            
        except Exception as e:
            print(f"Model save error: {e}")
            return False
    
    def load_model(self, model_name: str) -> bool:
        """
        Load trained model from disk.
        
        Args:
            model_name: Name of model to load
            
        Returns:
            True if successful, False otherwise
        """
        try:
            model_path = os.path.join(self.models_dir, f"{model_name}.pkl")
            if not os.path.exists(model_path):
                return False
            
            with open(model_path, 'rb') as f:
                self.models[model_name] = pickle.load(f)
            
            # Load vectorizer
            vectorizer_path = os.path.join(self.models_dir, "vectorizer.pkl")
            if os.path.exists(vectorizer_path):
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizers['default'] = pickle.load(f)
            
            return True
            
        except Exception as e:
            print(f"Model load error: {e}")
            return False
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """
        Get information about a model.
        
        Args:
            model_name: Name of model
            
        Returns:
            Model information dictionary
        """
        model = self.models.get(model_name)
        if not model:
            return {'error': 'Model not found'}
        
        info = {
            'name': model_name,
            'type': type(model).__name__,
            'trained': hasattr(model, 'classes_'),
        }
        
        if hasattr(model, 'n_features_in_'):
            info['features'] = model.n_features_in_
        
        if hasattr(model, 'classes_'):
            info['classes'] = list(model.classes_)
        
        return info
