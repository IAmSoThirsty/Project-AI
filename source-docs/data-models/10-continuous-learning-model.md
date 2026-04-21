# Continuous Learning Data Model

**Module**: `src/app/core/continuous_learning.py` [[src/app/core/continuous_learning.py]]  
**Storage**: `data/continuous_learning/reports.json`, `data/continuous_learning/curated.json`  
**Persistence**: JSON with structured reports  
**Schema Version**: 1.0

---

## Overview

Continuous Learning Engine tracks incoming facts and generates structured reports with neutral perspectives, usage ideas, and pros/cons analysis.

### Key Features

- **Structured Reports**: Topic, facts, usage ideas, neutral summary, pros/cons
- **Automatic Fact Extraction**: Parses content for key facts
- **Controversy Detection**: Identifies debates and records both sides
- **Usage Suggestions**: Practical applications of new knowledge
- **Persistent Storage**: JSON-based report archive

---

## Schema Structure

### Learning Report

```python
@dataclass
class LearningReport:
    topic: str
    timestamp: str
    facts: list[str]
    usage_ideas: list[str]
    neutral_summary: str
    pros_cons: dict[str, list[str]]
    metadata: dict[str, Any]
```

### Reports Document

**File**: `data/continuous_learning/reports.json`

```json
[
  {
    "topic": "Python Async Programming",
    "timestamp": "2024-01-20T14:30:00Z",
    "facts": [
      "async/await syntax enables non-blocking I/O operations",
      "asyncio event loop manages concurrent coroutines",
      "aiohttp provides async HTTP client/server"
    ],
    "usage_ideas": [
      "Brief the team on Python Async Programming with the verified facts so they stay aligned.",
      "Create a small experiment around Python Async Programming that tests one of the recorded facts.",
      "Leverage the application-focused details to improve how Python Async Programming connects to daily practice."
    ],
    "neutral_summary": "Continuous learning update for Python Async Programming: 3 fact(s) recorded. The perspective remains centered on the documented facts.",
    "pros_cons": {
      "pros": [],
      "cons": []
    },
    "metadata": {
      "source": "documentation_review",
      "confidence": 0.9,
      "reviewed_by": "admin"
    }
  }
]
```

---

## Field Specifications

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `topic` | string | Yes | Subject of learning content |
| `timestamp` | string | Yes | ISO 8601 timestamp of learning |
| `facts` | array | Yes | Extracted key facts (up to 3) |
| `usage_ideas` | array | Yes | Practical applications |
| `neutral_summary` | string | Yes | Objective summary of learning |
| `pros_cons` | object | Yes | Arguments for/against (if controversial) |
| `metadata` | object | No | Additional context (source, confidence, etc.) |

---

## Fact Extraction

### Algorithm

```python
def _extract_facts(self, content: str) -> list[str]:
    """Find up to three meaningful facts in the text."""
    candidates = [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+", content)
        if len(s.strip()) >= 20  # Minimum 20 characters
    ]
    if not candidates:
        return [content.strip()]
    return candidates[:3]  # Return first 3
```

**Logic**:
1. Split content by sentence terminators (`.`, `!`, `?`)
2. Filter sentences with ≥20 characters
3. Take first 3 sentences as facts
4. If no sentences found, use entire content

---

## Usage Ideas Generation

### Template-Based Suggestions

```python
def _generate_usage(self, topic: str, content: str) -> list[str]:
    """Suggest how the new knowledge might be put to work."""
    ideas = [
        f"Brief the team on {topic} with the verified facts so they stay aligned.",
        f"Create a small experiment around {topic} that tests one of the recorded facts.",
    ]
    if "application" in content.lower():
        ideas.append(
            f"Leverage the application-focused details to improve how {topic} connects to daily practice."
        )
    return ideas
```

**Always includes**:
1. Team briefing suggestion
2. Experimental validation suggestion
3. Practical application (if content mentions "application")

---

## Controversy Detection

### Markers

```python
controversy_markers = [
    "controversy",
    "debate",
    "pro",
    "con",
    "opposition",
    "split",
]
```

### Pros/Cons Analysis

```python
def _evaluate_pros_cons(self, content: str) -> dict[str, list[str]]:
    """Detect whether the content outlines a controversy and mirror both perspectives."""
    normalized = content.lower()
    pros_cons = {"pros": [], "cons": []}
    
    if any(marker in normalized for marker in controversy_markers):
        pros_cons["pros"].append(
            "Summarizes the benefits or arguments that advocates are promoting."
        )
        pros_cons["cons"].append(
            "Remembers the counterpoints that keep the debate grounded and neutral."
        )
    
    return pros_cons
```

**Logic**: If controversy markers detected, add template pros/cons to maintain neutrality.

---

## Neutral Summary Generation

### Algorithm

```python
def _compose_neutral(
    self, topic: str, facts: list[str], pros_cons: dict[str, list[str]]
) -> str:
    """Compose a neutral perspective that accompanies the recorded facts."""
    base = f"Continuous learning update for {topic}: {len(facts)} fact(s) recorded."
    if pros_cons.get("pros") or pros_cons.get("cons"):
        base += " Neutral perspective weighs the pros and cons before suggesting action."
    else:
        base += " The perspective remains centered on the documented facts."
    return base
```

**Format**:
- Base: "Continuous learning update for {topic}: {N} fact(s) recorded."
- If controversial: "Neutral perspective weighs the pros and cons before suggesting action."
- If factual: "The perspective remains centered on the documented facts."

---

## Usage Examples

### Absorb Information

```python
from app.core.continuous_learning import ContinuousLearningEngine

engine = ContinuousLearningEngine(data_dir="data")

report = engine.absorb_information(
    topic="Python Async Programming",
    content="""
    Python's async/await syntax enables non-blocking I/O operations.
    The asyncio event loop manages concurrent coroutines efficiently.
    aiohttp provides async HTTP client and server capabilities.
    """,
    metadata={"source": "documentation", "confidence": 0.9}
)

print(f"Learned about: {report.topic}")
print(f"Facts extracted: {len(report.facts)}")
for fact in report.facts:
    print(f"  - {fact}")
```

### Query Reports

```python
# Get all reports
all_reports = engine.reports

# Filter by topic
async_reports = [r for r in engine.reports if "Async" in r.topic]

# Get recent reports
recent_reports = sorted(engine.reports, key=lambda r: r.timestamp, reverse=True)[:10]
```

### Integration with Memory System

```python
from app.core.ai_systems import MemoryExpansionSystem

memory = MemoryExpansionSystem(data_dir="data")
engine = ContinuousLearningEngine(data_dir="data")

# Absorb and store in memory
report = engine.absorb_information(
    topic="Python Type Hints",
    content="Type hints improve code readability and enable static analysis."
)

for fact in report.facts:
    memory.add_knowledge(
        category="technical",
        content=fact,
        source=f"learning_report_{report.timestamp}",
        confidence=0.8
    )
```

---

## Curated Knowledge (Optional)

### Curated Reports

**File**: `data/continuous_learning/curated.json`

**Purpose**: Manually reviewed and approved learning reports

```json
[
  {
    "topic": "Python Async Programming",
    "curated_by": "admin",
    "curated_at": "2024-01-20T15:00:00Z",
    "original_report_timestamp": "2024-01-20T14:30:00Z",
    "approved_facts": [
      "async/await syntax enables non-blocking I/O operations",
      "asyncio event loop manages concurrent coroutines"
    ],
    "modifications": "Removed third fact (inaccurate)"
  }
]
```

---

## Performance Considerations

### Memory Usage

- **Per Report**: ~500 bytes (JSON)
- **1000 Reports**: ~500KB
- **In-Memory**: All reports loaded at startup

### Optimization

```python
def get_recent_reports(self, limit: int = 100) -> list[LearningReport]:
    """Get recent reports without loading all."""
    # Sort by timestamp descending
    sorted_reports = sorted(self.reports, key=lambda r: r.timestamp, reverse=True)
    return sorted_reports[:limit]
```

---

## Testing Strategy

### Unit Tests

```python
def test_absorb_information():
    engine = ContinuousLearningEngine(data_dir="data/test")
    
    report = engine.absorb_information(
        topic="Test Topic",
        content="Fact 1. Fact 2. Fact 3."
    )
    
    assert report.topic == "Test Topic"
    assert len(report.facts) == 3
    assert len(report.usage_ideas) >= 2

def test_controversy_detection():
    engine = ContinuousLearningEngine(data_dir="data/test")
    
    report = engine.absorb_information(
        topic="Controversial Topic",
        content="This is a debate. There is opposition to this idea."
    )
    
    assert len(report.pros_cons["pros"]) > 0
    assert len(report.pros_cons["cons"]) > 0
```

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `ai_systems.py::AIPersona` | Uses engine for learning |
| `memory_engine.py` | Stores learned facts |
| `learning_paths.py` | Generates structured learning paths |

---

## Future Enhancements

1. **ML-Based Fact Extraction**: Use NLP for better fact identification
2. **Knowledge Graph**: Link related topics
3. **Quality Scoring**: Rate report quality automatically
4. **Multi-Source Aggregation**: Combine facts from multiple sources
5. **Conflict Detection**: Identify contradictory facts

---

**Last Updated**: 2024-01-20  
**Schema Version**: 1.0  
**Maintainer**: Project-AI Core Team


---

## Related Documentation

- **Relationship Map**: [[relationships\data\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/continuous_learning.py]]

### Related Modules

- [[src/app/core/ai_systems.py]]
