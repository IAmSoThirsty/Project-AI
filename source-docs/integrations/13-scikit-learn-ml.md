# Scikit-Learn Machine Learning Integration

## Overview
Project-AI uses scikit-learn for intent classification (src/app/core/intent_detection.py) and data clustering (src/app/core/data_analysis.py).

## Use Cases

### 1. Intent Classification
`python
# src/app/core/intent_detection.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

class IntentClassifier:
    def __init__(self):
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=1000)),
            ('clf', SGDClassifier(loss='hinge', random_state=42))
        ])
    
    def train(self, texts: list[str], labels: list[str]):
        self.pipeline.fit(texts, labels)
    
    def predict(self, text: str) -> str:
        return self.pipeline.predict([text])[0]
    
    def predict_proba(self, text: str) -> dict:
        # Get confidence scores
        proba = self.pipeline.predict_proba([text])[0]
        return dict(zip(self.pipeline.classes_, proba))
`

### 2. Data Clustering
`python
# src/app/core/data_analysis.py
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class DataAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
    
    def cluster_data(self, data, n_clusters: int = 3):
        # Normalize data
        scaled_data = self.scaler.fit_transform(data)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(scaled_data)
        
        return labels, kmeans.cluster_centers_
`

### 3. Dimensionality Reduction
`python
from sklearn.decomposition import PCA

def reduce_dimensions(data, n_components: int = 2):
    pca = PCA(n_components=n_components)
    reduced = pca.fit_transform(data)
    return reduced, pca.explained_variance_ratio_
`

## Training Intent Classifier
`python
from app.core.intent_detection import IntentClassifier

classifier = IntentClassifier()

# Training data
texts = [
    'What is machine learning?',
    'Explain neural networks',
    'Tell me a joke',
    'Make me laugh',
    'Generate an image of a cat',
    'Create a picture'
]

labels = [
    'question',
    'question', 
    'entertainment',
    'entertainment',
    'image_generation',
    'image_generation'
]

# Train
classifier.train(texts, labels)

# Predict
intent = classifier.predict('How does AI work?')
print(f'Intent: {intent}')

# Get confidence
proba = classifier.predict_proba('Draw a landscape')
print(f'Probabilities: {proba}')
`

## Model Persistence
`python
import joblib

# Save model
joblib.dump(classifier.pipeline, 'data/models/intent_classifier.pkl')

# Load model
loaded_pipeline = joblib.load('data/models/intent_classifier.pkl')
`

## References
- scikit-learn: https://scikit-learn.org
- TfidfVectorizer: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
- KMeans: https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html


---

## Related Documentation

- **Relationship Map**: [[relationships\integrations\README.md]]
