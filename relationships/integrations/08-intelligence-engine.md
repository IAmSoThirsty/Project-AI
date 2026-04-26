# Intelligence Engine Relationship Map

**Status**: 🟢 Production | **Type**: Core Business Logic  
**Priority**: P0 Critical | **Governance**: Central Orchestration

---


## Navigation

**Location**: `relationships\integrations\08-intelligence-engine.md`

**Parent**: [[relationships\integrations\README.md]]


## Overview

The Intelligence Engine is a unified system consolidating three intelligence subsystems:
1. **Data Analysis**: Load, analyze, and visualize tabular data
2. **Intent Detection**: Classify user intents using ML
3. **Learning Paths**: Generate personalized learning curricula
4. **Intelligence Router**: Route queries to knowledge base and function registry
5. **AGI Identity System**: Complete identity, bonding, and governance

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              INTELLIGENCE ENGINE (Hub)                       │
│         src/app/core/intelligence_engine.py                  │
│                                                              │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐             │
│  │ Data       │ │ Intent     │ │ Learning   │             │
│  │ Analysis   │ │ Detection  │ │ Paths      │             │
│  └────────────┘ └────────────┘ └────────────┘             │
│                                                              │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐             │
│  │ Intelligence│ │ AGI        │ │ Function   │             │
│  │ Router     │ │ Identity   │ │ Registry   │             │
│  └────────────┘ └────────────┘ └────────────┘             │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
┌─────┐  ┌─────┐  ┌─────┐
│OpenAI│ │scikit│ │pandas│
│ API  │ │-learn│ │      │
└─────┘  └─────┘  └─────┘
```

---

## Core Components

### 1. Data Analysis Subsystem

**Purpose**: Load and analyze CSV/XLSX/JSON data with K-means clustering and PCA

**Classes**:
- `DataAnalysis`: Load, preview, analyze, cluster, visualize

**Dependencies**:
- `pandas`: Data loading and manipulation
- `sklearn.cluster.KMeans`: Clustering analysis
- `sklearn.decomposition.PCA`: Dimensionality reduction
- `matplotlib`: Visualization

**Usage**:
```python
from app.core.intelligence_engine import DataAnalysis

analyzer = DataAnalysis()

# Load data
analyzer.load_data("sales_data.csv")

# Get summary statistics
summary = analyzer.get_summary()
print(f"Rows: {summary['rows']}, Columns: {summary['columns']}")

# Cluster data
clusters = analyzer.cluster_data(n_clusters=3)
print(f"Found {len(set(clusters))} clusters")

# Visualize
fig = analyzer.visualize_clusters(clusters)
# Display fig in GUI
```

**Key Methods**:
- `load_data(filepath)`: Load CSV/XLSX/JSON
- `get_summary()`: Return row count, column count, column names
- `cluster_data(n_clusters)`: K-means clustering on numeric columns
- `visualize_clusters(clusters)`: PCA projection scatter plot

### 2. Intent Detection Subsystem

**Purpose**: Classify user intents using TF-IDF + SGDClassifier

**Classes**:
- `IntentDetector`: Train, predict, save/load model

**Dependencies**:
- `sklearn.feature_extraction.text.TfidfVectorizer`: Text vectorization
- `sklearn.linear_model.SGDClassifier`: Linear classifier
- `sklearn.pipeline.Pipeline`: ML pipeline
- `joblib`: Model serialization

**Training Data Example**:
```python
training_data = [
    ("What is machine learning?", "question"),
    ("Tell me about AI", "question"),
    ("Create a function to sort a list", "code_request"),
    ("Write Python code for...", "code_request"),
    ("Hello!", "greeting"),
    ("Hi there", "greeting")
]

detector = IntentDetector()
detector.train(training_data)
detector.save_model("data/intent_model.pkl")
```

**Usage**:
```python
detector = IntentDetector()
detector.load_model("data/intent_model.pkl")

intent = detector.predict("How do I learn Python?")
print(f"Detected intent: {intent}")  # "question"
```

**Key Methods**:
- `train(training_data)`: Train on list of (text, label) tuples
- `predict(text)`: Return predicted intent label
- `save_model(filepath)`: Serialize pipeline to disk
- `load_model(filepath)`: Load serialized pipeline

### 3. Learning Paths Subsystem

**Purpose**: Generate personalized learning curricula via OpenAI

**Classes**:
- `LearningPathManager`: Generate paths, save to file

**Dependencies**:
- `app.core.ai.orchestrator`: AI orchestration (OpenAI fallback)
- `app.security.path_security`: Secure file paths

**Usage**:
```python
from app.core.intelligence_engine import LearningPathManager

manager = LearningPathManager(provider="openai")

# Generate learning path
path = manager.generate_path(
    interest="Python programming",
    skill_level="beginner",
    model="gpt-3.5-turbo"
)

print(path)  # Markdown-formatted learning plan

# Save to file
manager.save_path("alice", path)
```

**Generated Output Example**:
```markdown
# Learning Path: Python Programming (Beginner)

## Phase 1: Fundamentals (2 weeks)
- Variables and data types
- Control flow (if/else, loops)
- Functions and modules

## Phase 2: Data Structures (2 weeks)
- Lists, tuples, dictionaries
- Sets and comprehensions
- File I/O

## Phase 3: Object-Oriented Programming (2 weeks)
- Classes and objects
- Inheritance and polymorphism
- Special methods (__init__, __str__)

## Resources
- Python.org official tutorial
- Automate the Boring Stuff with Python
- Real Python tutorials
```

### 4. Intelligence Router

**Purpose**: Route user queries to appropriate knowledge source

**Components**:
- `GlobalIntelligenceLibrary`: Query knowledge base (6 domains)
- `FunctionRegistry`: Search and retrieve function definitions

**Usage**:
```python
from app.core.intelligence_engine import IntelligenceRouter

router = IntelligenceRouter()

# Query knowledge base
answer = router.query_knowledge("What is machine learning?")
print(answer)  # "Machine learning is a subset of AI..."

# Search functions
functions = router.search_functions("sort list")
print(functions)  # [{"name": "bubble_sort", "code": "def bubble_sort(...)"}]
```

**Knowledge Domains**:
1. Machine Learning
2. Data Science
3. Software Engineering
4. Cybersecurity
5. Cloud Computing
6. DevOps

### 5. AGI Identity System

**Purpose**: Complete identity, bonding, and governance integration

**Components**:
- `MemoryEngine`: Episodic memory, semantic memory
- `PerspectiveEngine`: Viewpoint management
- `BondingProtocol`: Identity bonding phases
- `Triumvirate`: Governance (Atlas, Prometheus, Erebus)
- `ReflectionCycle`: Daily/weekly/triggered reflections
- `RebirthManager`: User-AI instance lifecycle

**Usage**:
```python
from app.core.intelligence_engine import MemoryEngine, BondingProtocol, Triumvirate

# Memory
memory = MemoryEngine(user_id="alice", data_dir="data/memory")
memory.record_episodic(
    event="User asked about Python",
    significance=SignificanceLevel.MEDIUM
)

# Bonding
bonding = BondingProtocol(user_id="alice")
phase = bonding.check_phase()
print(f"Current bonding phase: {phase}")  # BondingPhase.DISCOVERY

# Governance
governance = Triumvirate()
decision = governance.vote_on_action(
    action="Execute system command",
    context={"risk_level": "high", "user_intent": "productivity"}
)
print(f"Vote: {decision}")  # {"atlas": "deny", "prometheus": "allow", "erebus": "deny"}
```

---

## Integration Points

### Consumers

**GUI Consumers**:
1. `LeatherBookDashboard` (`gui/leather_book_dashboard.py`): Main UI
2. `PersonaPanel` (`gui/persona_panel.py`): AI configuration
3. `IntelligenceLibraryPanel` (`gui/intelligence_library_panel.py`): Knowledge browser

**CLI Consumers**:
1. `project_ai_cli.py`: Command-line interface
2. `inspection_cli.py`: Inspection tools

**API Consumers**:
1. `start_api.py`: Flask REST API
2. Web frontend (React app)

### Data Flow

```
User Input (GUI/CLI/API)
    ↓
Intelligence Engine
    ↓
┌───────────┬───────────┬───────────┐
│           │           │           │
▼           ▼           ▼           ▼
Data      Intent    Learning   AGI Identity
Analysis  Detection  Paths      System
│           │           │           │
└───────────┴───────────┴───────────┘
    ↓
AI Orchestrator (OpenAI/HuggingFace)
    ↓
Response to User
```

---

## API Contracts

### DataAnalysis API

```python
class DataAnalysis:
    def load_data(self, filepath: str) -> bool:
        """Load CSV/XLSX/JSON data."""
        pass
    
    def get_summary(self) -> dict:
        """Return {'rows': int, 'columns': int, 'column_names': list}."""
        pass
    
    def cluster_data(self, n_clusters: int = 3) -> list:
        """Return cluster labels for each row."""
        pass
    
    def visualize_clusters(self, clusters: list) -> Figure:
        """Return matplotlib figure with PCA plot."""
        pass
```

### IntentDetector API

```python
class IntentDetector:
    def train(self, training_data: list[tuple[str, str]]) -> None:
        """Train on (text, label) tuples."""
        pass
    
    def predict(self, text: str) -> str:
        """Return predicted intent label."""
        pass
    
    def save_model(self, filepath: str) -> None:
        """Serialize model to disk."""
        pass
    
    def load_model(self, filepath: str) -> None:
        """Load model from disk."""
        pass
```

### LearningPathManager API

```python
class LearningPathManager:
    def generate_path(
        self, 
        interest: str, 
        skill_level: str = "beginner",
        model: str = None
    ) -> str:
        """Generate learning path via AI orchestrator."""
        pass
    
    def save_path(self, username: str, path: str) -> str:
        """Save path to data/learning_paths/{username}_{timestamp}.md."""
        pass
```

---

## Configuration

### Environment Variables

```bash
# AI Orchestrator (for learning paths)
OPENAI_API_KEY=sk-proj-...
HUGGINGFACE_API_KEY=hf_...

# Intent Detection Model
INTENT_MODEL_PATH=data/intent_model.pkl

# AGI Identity
AGI_IDENTITY_ENABLED=1
REFLECTION_CYCLE_ENABLED=1
```

---

## Performance

### Benchmarks

| Operation | Latency | Notes |
|-----------|---------|-------|
| Load CSV (10k rows) | 200ms | Pandas read_csv |
| K-means clustering (10k rows) | 1s | 3 clusters, 10 numeric columns |
| Intent detection | 5ms | Pre-trained model |
| Learning path generation | 3-5s | OpenAI API call |
| Memory retrieval | 10ms | Vector similarity search |

---

## Testing

```python
# tests/test_intelligence_engine.py
def test_data_analysis():
    analyzer = DataAnalysis()
    analyzer.load_data("test_data.csv")
    summary = analyzer.get_summary()
    assert summary["rows"] > 0
    assert summary["columns"] > 0

def test_intent_detection():
    detector = IntentDetector()
    training_data = [("What is AI?", "question"), ("Hello", "greeting")]
    detector.train(training_data)
    
    intent = detector.predict("How are you?")
    assert intent in ["question", "greeting"]

def test_learning_path_generation():
    manager = LearningPathManager(provider="openai")
    path = manager.generate_path("Python", "beginner")
    assert "Python" in path
    assert "Phase" in path
```

---

## Security

### Input Validation

```python
# Validate file paths
from app.security.path_security import safe_path_join, sanitize_filename

filepath = safe_path_join("data", user_input_filename)  # Prevents path traversal

# Validate data size
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
if os.path.getsize(filepath) > MAX_FILE_SIZE:
    raise ValueError("File too large")
```

### PII Protection

```python
# Remove PII from data before clustering
def remove_pii(df):
    """Remove columns likely to contain PII."""
    pii_columns = ["email", "phone", "ssn", "name", "address"]
    return df.drop(columns=[c for c in pii_columns if c in df.columns])
```

---

## Future Enhancements

### Phase 1: Real-Time Intent Learning ⏳ PLANNED
- Online learning: Update intent model based on user feedback
- Active learning: Request labels for ambiguous intents

### Phase 2: Multi-Modal Analysis 🔮 FUTURE
- Image analysis: Integrate computer vision
- Audio analysis: Speech-to-text + sentiment analysis

### Phase 3: Federated Intelligence 🔮 FUTURE
- Distribute intelligence across multiple nodes
- Privacy-preserving collaborative learning

---

## Related Systems

- **[01-openai-integration.md](01-openai-integration.md)**: AI orchestration
- **[09-learning-paths.md](09-learning-paths.md)**: Learning path subsystem
- **[04-database-connectors.md](04-database-connectors.md)**: Data persistence

---

**Last Updated**: 2025-01-26  
**Maintained By**: AGENT-060  
**Review Cycle**: Quarterly
