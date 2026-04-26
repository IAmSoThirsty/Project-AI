# Learning Paths Integration Relationship Map

**Status**: 🟢 Production | **Type**: AI-Powered Feature  
**Priority**: P1 Feature | **Governance**: AI Orchestrator

---


## Navigation

**Location**: `relationships\integrations\09-learning-paths.md`

**Parent**: [[relationships\integrations\README.md]]


## Overview

The Learning Paths system generates personalized learning curricula using AI (OpenAI GPT models). It produces structured, multi-phase learning plans with resources, timelines, and skill progression.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│            LEARNING PATH MANAGER                             │
│         src/app/core/learning_paths.py                       │
│                                                              │
│  ┌──────────────────────────────────────────┐              │
│  │ generate_path(interest, skill_level)     │              │
│  │ save_path(username, path)                │              │
│  │ list_paths(username)                     │              │
│  └──────────────────────────────────────────┘              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                  AI ORCHESTRATOR                             │
│         src/app/core/ai/orchestrator.py                      │
│  ┌──────────────────────────────────────────┐              │
│  │ Primary: OpenAI GPT-3.5/GPT-4            │              │
│  │ Fallback: HuggingFace Mistral-7B         │              │
│  └──────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Functionality

### Generate Learning Path

**Method**: `generate_path(interest, skill_level="beginner", model=None)`

**Input**:
- `interest`: Topic (e.g., "Python programming", "Machine learning")
- `skill_level`: "beginner", "intermediate", or "advanced"
- `model`: Optional model override (default: gpt-3.5-turbo)

**Output**: Markdown-formatted learning plan

**Example**:
```python
from app.core.learning_paths import LearningPathManager

manager = LearningPathManager(provider="openai")

path = manager.generate_path(
    interest="Machine Learning",
    skill_level="intermediate"
)

print(path)
```

**Generated Output**:
```markdown
# Learning Path: Machine Learning (Intermediate)

## Prerequisites
- Python programming fundamentals
- Linear algebra basics
- Basic statistics

## Phase 1: Supervised Learning (3 weeks)
### Week 1: Regression
- Linear regression
- Polynomial regression
- Regularization (L1/L2)

**Resources:**
- Coursera: Machine Learning by Andrew Ng
- Hands-On Machine Learning (Géron) - Chapters 4-5

### Week 2: Classification
- Logistic regression
- Decision trees
- Random forests
- Gradient boosting

**Resources:**
- Scikit-learn documentation
- Kaggle: Titanic dataset

### Week 3: Model Evaluation
- Cross-validation
- Confusion matrix
- ROC curves
- Hyperparameter tuning

**Project:** Build a spam classifier

## Phase 2: Unsupervised Learning (2 weeks)
### Week 1: Clustering
- K-means
- Hierarchical clustering
- DBSCAN

### Week 2: Dimensionality Reduction
- PCA
- t-SNE
- UMAP

**Project:** Customer segmentation analysis

## Phase 3: Deep Learning (4 weeks)
### Week 1-2: Neural Networks
- Perceptrons
- Backpropagation
- Activation functions
- PyTorch/TensorFlow basics

### Week 3-4: CNNs and RNNs
- Convolutional layers
- Image classification
- Recurrent networks
- LSTM/GRU

**Project:** Image classifier with transfer learning

## Final Project
Build an end-to-end ML pipeline:
- Data collection and cleaning
- Feature engineering
- Model training and evaluation
- Deployment (Flask/FastAPI)

## Recommended Resources
- Books: "Deep Learning" by Goodfellow et al.
- Courses: Fast.ai Practical Deep Learning
- Practice: Kaggle competitions
```

---

## Integration Points

### Data Storage

**Location**: `data/learning_paths/{username}_{timestamp}.md`

**Persistence**:
```python
def save_path(self, username: str, path: str) -> str:
    """Save learning path to file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = sanitize_filename(f"{username}_{timestamp}.md")
    filepath = safe_path_join(self.data_dir, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(path)
    
    logger.info(f"Learning path saved: {filepath}")
    return filepath
```

### AI Orchestrator Integration

**Refactored Architecture** (Post-2024):
```python
from app.core.ai.orchestrator import run_ai, AIRequest

def generate_path(self, interest, skill_level="beginner", model=None):
    """Generate path via AI orchestrator (MANDATORY governance)."""
    system_context = "You are an educational expert creating learning paths."
    user_prompt = (
        f"Create a structured learning path for {interest} at {skill_level} level.\n"
        "Include:\n"
        "- Prerequisites\n"
        "- Phases with timelines\n"
        "- Resources (books, courses, tutorials)\n"
        "- Hands-on projects\n"
        "Format in Markdown with clear sections."
    )
    
    request = AIRequest(
        task_type="chat",
        prompt=user_prompt,
        model=model or "gpt-3.5-turbo",
        provider="openai",
        context={"system": system_context}
    )
    
    response = run_ai(request)
    
    if response.status == "success":
        return response.result
    else:
        logger.error(f"AI generation failed: {response.error}")
        return f"Error generating learning path: {response.error}"
```

---

## API Contracts

### Learning Path Manager Interface

```python
class LearningPathManager:
    def __init__(self, api_key=None, provider="openai", data_dir="data/learning_paths"):
        """Initialize with AI orchestrator (api_key deprecated)."""
        pass
    
    def generate_path(
        self, 
        interest: str, 
        skill_level: str = "beginner",
        model: str = None
    ) -> str:
        """
        Generate learning path.
        
        Returns:
            Markdown-formatted learning plan or error message
        """
        pass
    
    def save_path(self, username: str, path: str) -> str:
        """
        Save path to file.
        
        Returns:
            Filepath where path was saved
        """
        pass
    
    def list_paths(self, username: str = None) -> list[dict]:
        """
        List saved learning paths.
        
        Args:
            username: Filter by username (optional)
        
        Returns:
            [{"filepath": str, "timestamp": str, "username": str}]
        """
        pass
```

---

## Configuration

### Environment Variables

```bash
# AI Provider (via orchestrator)
OPENAI_API_KEY=sk-proj-...
HUGGINGFACE_API_KEY=hf_...

# Learning Paths Storage
LEARNING_PATHS_DIR=data/learning_paths
```

### Prompt Engineering

**System Prompt**:
```
You are an educational expert creating learning paths.
Your responses should be:
- Structured with clear phases and timelines
- Include prerequisites and final projects
- Provide specific resources (books, courses, tutorials)
- Use Markdown formatting
- Tailored to the user's skill level
```

**User Prompt Template**:
```
Create a structured learning path for {interest} at {skill_level} level.

Include:
- Prerequisites
- Phases with timelines (weeks)
- Topics and subtopics
- Resources (books, courses, tutorials)
- Hands-on projects
- Final capstone project

Format in Markdown with clear sections.
```

---

## Error Handling

### Common Errors

1. **OpenAI API Failure**: Orchestrator auto-falls back to HuggingFace
2. **Invalid Skill Level**: Default to "beginner"
3. **Empty Response**: Return fallback template

```python
def generate_path(self, interest, skill_level="beginner", model=None):
    """Generate with error handling."""
    # Validate skill level
    if skill_level not in ["beginner", "intermediate", "advanced"]:
        logger.warning(f"Invalid skill level '{skill_level}', defaulting to 'beginner'")
        skill_level = "beginner"
    
    try:
        # Generate via orchestrator
        response = run_ai(request)
        
        if response.status == "success":
            return response.result
        else:
            # Return fallback template
            return self._get_fallback_template(interest, skill_level)
    
    except Exception as e:
        logger.error(f"Learning path generation failed: {e}")
        return self._get_fallback_template(interest, skill_level)
```

---

## Security

### Path Traversal Prevention

```python
from app.security.path_security import safe_path_join, sanitize_filename

# SAFE: Prevent path traversal
username = "../../../etc/passwd"  # Malicious input
filename = sanitize_filename(f"{username}_path.md")  # "etc_passwd_path.md"
filepath = safe_path_join(self.data_dir, filename)  # "data/learning_paths/etc_passwd_path.md"
```

### Content Filtering

```python
# Filter inappropriate topics
BLOCKED_TOPICS = ["hacking", "exploit", "malware", "cracking"]

def is_safe_topic(interest: str) -> bool:
    """Check if topic is safe."""
    interest_lower = interest.lower()
    for blocked in BLOCKED_TOPICS:
        if blocked in interest_lower:
            logger.warning(f"Blocked topic: {interest}")
            return False
    return True
```

---

## Performance

### Benchmarks

| Operation | Latency | Notes |
|-----------|---------|-------|
| Generate path (GPT-3.5) | 3-5s | Depends on complexity |
| Generate path (GPT-4) | 8-12s | Higher quality, slower |
| Save path to file | 5ms | File I/O |
| List paths | 10ms | Directory scan |

### Optimization

**Caching**: Cache generated paths to avoid redundant API calls

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=50)
def generate_path_cached(interest_hash: str, skill_level: str):
    """Generate with caching (hash to make hashable)."""
    interest = self._unhash_interest(interest_hash)
    return self.generate_path(interest, skill_level)

# Usage
interest_hash = hashlib.md5(interest.encode()).hexdigest()
path = generate_path_cached(interest_hash, skill_level)
```

---

## Testing

```python
# tests/test_learning_paths.py
def test_generate_path():
    manager = LearningPathManager(provider="openai")
    path = manager.generate_path("Python", "beginner")
    
    assert "Python" in path
    assert "Phase" in path
    assert "Resources" in path

def test_save_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = LearningPathManager(data_dir=tmpdir)
        path = "# Test Path\n\n## Phase 1"
        
        filepath = manager.save_path("alice", path)
        
        assert os.path.exists(filepath)
        assert "alice" in filepath

def test_list_paths():
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = LearningPathManager(data_dir=tmpdir)
        manager.save_path("alice", "Path 1")
        manager.save_path("alice", "Path 2")
        
        paths = manager.list_paths(username="alice")
        assert len(paths) == 2
```

---

## GUI Integration

### Usage in LeatherBookDashboard

```python
# src/app/gui/leather_book_dashboard.py
def on_generate_learning_path_clicked(self):
    """Handle learning path generation button click."""
    interest = self.interest_input.text()
    skill_level = self.skill_level_combo.currentText()
    
    # Show loading indicator
    self.loading_indicator.show()
    
    # Generate path (in background thread to avoid blocking UI)
    def generate():
        manager = LearningPathManager()
        return manager.generate_path(interest, skill_level)
    
    # Use QThread to avoid blocking
    thread = QThread()
    worker = Worker(generate)
    worker.result_ready.connect(self.on_path_generated)
    thread.start()

def on_path_generated(self, path: str):
    """Display generated path."""
    self.loading_indicator.hide()
    self.path_display.setMarkdown(path)
    
    # Save path
    username = self.current_user
    filepath = self.learning_manager.save_path(username, path)
    logger.info(f"Path saved: {filepath}")
```

---

## Future Enhancements

### Phase 1: Interactive Learning ⏳ PLANNED
- Progress tracking: Mark completed topics
- Quizzes: Auto-generate assessments
- Adaptive paths: Adjust based on progress

### Phase 2: Collaborative Learning 🔮 FUTURE
- Share paths with community
- Rate and review paths
- Remix existing paths

### Phase 3: Multi-Modal Learning 🔮 FUTURE
- Video tutorials: YouTube integration
- Podcasts: Audio learning resources
- Interactive coding: Embedded code editors

---

## Related Systems

- **[01-openai-integration.md](01-openai-integration.md)**: AI generation
- **[08-intelligence-engine.md](08-intelligence-engine.md)**: Learning path subsystem
- **[04-database-connectors.md](04-database-connectors.md)**: Path storage

---

**Last Updated**: 2025-01-26  
**Maintained By**: AGENT-060  
**Review Cycle**: Quarterly
