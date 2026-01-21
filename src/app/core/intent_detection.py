"""
Intent detection system using scikit-learn for text classification.
"""

import os

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline


class IntentDetector:
    def __init__(self):
        self.pipeline = Pipeline(
            [
                ("tfidf", TfidfVectorizer()),
                ("clf", SGDClassifier(loss="modified_huber")),
            ],
            memory=None,
        )
        self.trained = False

    def train(self, texts, labels):
        """Train the intent detection model"""
        self.pipeline.fit(texts, labels)
        self.trained = True

    def predict(self, text):
        """Predict the intent of a given text"""
        if not self.trained:
            return "general"  # Default fallback
        return self.pipeline.predict([text])[0]

    def save_model(self, path):
        """Save the trained model"""
        joblib.dump(self.pipeline, path)

    def load_model(self, path):
        """Load a trained model"""
        if os.path.exists(path):
            self.pipeline = joblib.load(path)
            self.trained = True
