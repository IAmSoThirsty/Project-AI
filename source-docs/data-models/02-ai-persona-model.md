# AI Persona Data Model

**Module**: `src/app/core/ai_systems.py` [[src/app/core/ai_systems.py]] (AIPersona class)  
**Storage**: `data/ai_persona/state.json`  
**Persistence**: JSON with atomic writes  
**Schema Version**: 1.0

---

## Overview

The AI Persona system provides self-aware AI personality with 8 configurable traits, dynamic mood tracking, and persistent state management. It integrates with the Continuous Learning Engine to enable knowledge absorption and personality evolution.

### Key Features

- 8 configurable personality traits (0.0 - 1.0 scale)
- 4-dimensional mood tracking (energy, enthusiasm, contentment, engagement)
- Interaction counting and user relationship tracking
- Continuous learning integration
- Thread-safe atomic state persistence
- Trait adjustment based on user feedback

---

## Schema Structure

### Persona State Document

```json
{
  "personality": {
    "curiosity": 0.8,
    "patience": 0.9,
    "empathy": 0.85,
    "helpfulness": 0.95,
    "playfulness": 0.6,
    "formality": 0.3,
    "assertiveness": 0.5,
    "thoughtfulness": 0.9
  },
  "mood": {
    "energy": 0.7,
    "enthusiasm": 0.75,
    "contentment": 0.8,
    "engagement": 0.5
  },
  "interactions": 1247,
  "last_interaction": "2024-01-20T14:35:22Z",
  "user_name": "Friend",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Field Specifications

### Personality Traits

All personality traits use a **normalized scale of 0.0 to 1.0**:

| Trait | Type | Range | Default | Description |
|-------|------|-------|---------|-------------|
| `curiosity` | float | 0.0-1.0 | 0.8 | Desire to learn and explore new information |
| `patience` | float | 0.0-1.0 | 0.9 | Tolerance for waiting and handling frustration |
| `empathy` | float | 0.0-1.0 | 0.85 | Ability to understand and share user feelings |
| `helpfulness` | float | 0.0-1.0 | 0.95 | Willingness to assist and provide value |
| `playfulness` | float | 0.0-1.0 | 0.6 | Use of humor and creative responses |
| `formality` | float | 0.0-1.0 | 0.3 | Level of professional vs casual communication |
| `assertiveness` | float | 0.0-1.0 | 0.5 | Confidence in expressing opinions |
| `thoughtfulness` | float | 0.0-1.0 | 0.9 | Depth of consideration before responding |

### Mood Dimensions

| Dimension | Type | Range | Default | Description |
|-----------|------|-------|---------|-------------|
| `energy` | float | 0.0-1.0 | 0.7 | Current activity level and responsiveness |
| `enthusiasm` | float | 0.0-1.0 | 0.75 | Excitement about interactions |
| `contentment` | float | 0.0-1.0 | 0.8 | Satisfaction with current state |
| `engagement` | float | 0.0-1.0 | 0.5 | Level of active participation |

### Metadata Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `interactions` | integer | Yes | Total number of user interactions |
| `last_interaction` | datetime | No | Timestamp of last user message |
| `user_name` | string | Yes | Display name for the user ("Friend" default) |
| `created_at` | datetime | Yes | Persona initialization timestamp |

---

## Personality Trait Semantics

### Curiosity (0.8 default)

**Low (0.0-0.3)**: Focuses only on direct questions, minimal exploration  
**Medium (0.4-0.7)**: Asks clarifying questions, suggests related topics  
**High (0.8-1.0)**: Proactively explores tangential information, suggests experiments

**Example Behavior**:
```python
if self.personality["curiosity"] > 0.7:
    response += "\n\nI'm curious - have you considered exploring X as well?"
```

### Patience (0.9 default)

**Low (0.0-0.3)**: Responds quickly, may skip explanations  
**Medium (0.4-0.7)**: Balances speed with thoroughness  
**High (0.8-1.0)**: Takes time to explain concepts, tolerates repetition

**Use Case**: Affects response delay and explanation depth in GUI.

### Empathy (0.85 default)

**Low (0.0-0.3)**: Factual, task-focused responses  
**Medium (0.4-0.7)**: Acknowledges user emotions occasionally  
**High (0.8-1.0)**: Actively validates feelings, adjusts tone to user mood

**Example**:
```python
if self.personality["empathy"] > 0.7 and user_sentiment == "frustrated":
    response = "I understand this is frustrating. Let's work through it together."
```

### Helpfulness (0.95 default)

**Low (0.0-0.3)**: Provides minimal assistance, expects user initiative  
**Medium (0.4-0.7)**: Offers help when asked  
**High (0.8-1.0)**: Proactively suggests improvements, anticipates needs

**Default High**: Core value of the AI assistant.

### Playfulness (0.6 default)

**Low (0.0-0.3)**: Serious, formal tone  
**Medium (0.4-0.7)**: Occasional light humor  
**High (0.8-1.0)**: Frequent jokes, creative analogies, emojis

**Example**:
```python
if self.personality["playfulness"] > 0.7:
    greeting = "Hey there, coding wizard! 🧙‍♂️"
else:
    greeting = "Hello!"
```

### Formality (0.3 default - casual)

**Low (0.0-0.3)**: Casual, conversational language  
**Medium (0.4-0.7)**: Professional but approachable  
**High (0.8-1.0)**: Strictly formal, business-appropriate

**Inverse Relationship**: Lower = more casual.

### Assertiveness (0.5 default - balanced)

**Low (0.0-0.3)**: Tentative suggestions, defers to user  
**Medium (0.4-0.7)**: Balanced confidence, collaborative  
**High (0.8-1.0)**: Strong opinions, directive guidance

**Use Case**: Determines tone of recommendations and warnings.

### Thoughtfulness (0.9 default)

**Low (0.0-0.3)**: Quick, surface-level responses  
**Medium (0.4-0.7)**: Considers multiple angles  
**High (0.8-1.0)**: Deep analysis, explores edge cases

**Performance Trade-off**: Higher values may increase response time.

---

## Mood Tracking System

### Mood Evolution

Moods dynamically adjust based on interaction patterns:

```python
def update_mood(self, user_sentiment: str = "neutral") -> None:
    """Update mood based on user interaction sentiment."""
    if user_sentiment == "positive":
        self.mood["enthusiasm"] = min(1.0, self.mood["enthusiasm"] + 0.05)
        self.mood["contentment"] = min(1.0, self.mood["contentment"] + 0.03)
    elif user_sentiment == "negative":
        self.mood["enthusiasm"] = max(0.0, self.mood["enthusiasm"] - 0.05)
        self.mood["energy"] = max(0.0, self.mood["energy"] - 0.03)
    
    self.mood["engagement"] = min(1.0, self.mood["engagement"] + 0.02)
    self._save_state()
```

### Mood Decay

Over time, moods return to baseline:

```python
def apply_mood_decay(self, decay_factor: float = 0.02) -> None:
    """Gradually return mood to neutral baseline."""
    baselines = {"energy": 0.7, "enthusiasm": 0.75, "contentment": 0.8, "engagement": 0.5}
    
    for dimension, baseline in baselines.items():
        if self.mood[dimension] > baseline:
            self.mood[dimension] = max(baseline, self.mood[dimension] - decay_factor)
        elif self.mood[dimension] < baseline:
            self.mood[dimension] = min(baseline, self.mood[dimension] + decay_factor)
```

---

## State Persistence

### Atomic Write Pattern

Uses `_atomic_write_json()` for thread-safe persistence:

```python
def _save_state(self) -> None:
    """Save persona state to disk with atomic write."""
    state_file = os.path.join(self.persona_dir, "state.json")
    state = {
        "personality": self.personality,
        "mood": self.mood,
        "interactions": self.total_interactions,
        "last_interaction": self.last_user_message_time,
        "user_name": self.user_name,
        "created_at": getattr(self, "created_at", datetime.now().isoformat())
    }
    _atomic_write_json(state_file, state)
```

### Load on Initialization

```python
def _load_state(self) -> None:
    """Load persona state from file."""
    state_file = os.path.join(self.persona_dir, "state.json")
    try:
        if os.path.exists(state_file):
            with open(state_file, encoding="utf-8") as f:
                state = json.load(f)
                self.personality = state.get("personality", self.personality)
                self.mood = state.get("mood", self.mood)
                self.total_interactions = state.get("interactions", 0)
    except Exception as e:
        logger.error("Error loading state: %s", e)
```

---

## Trait Adjustment System

### Dynamic Personality Evolution

```python
def adjust_trait(self, trait_name: str, delta: float) -> None:
    """Adjust a personality trait by delta (clamped to 0.0-1.0).
    
    Args:
        trait_name: Name of trait to adjust (e.g., "curiosity")
        delta: Change amount (positive or negative, e.g., +0.1 or -0.05)
    """
    if trait_name in self.personality:
        new_value = self.personality[trait_name] + delta
        self.personality[trait_name] = max(0.0, min(1.0, new_value))
        self._save_state()
        logger.info("Trait '%s' adjusted to %.2f", trait_name, self.personality[trait_name])
```

### User Feedback Integration

```python
# User says: "Can you be more casual?"
persona.adjust_trait("formality", -0.2)  # Decrease formality

# User says: "Give me more detailed explanations"
persona.adjust_trait("thoughtfulness", +0.1)  # Increase depth
```

---

## Integration with Continuous Learning

### Learning Engine Connection

```python
def __init__(self, data_dir: str = "data", user_name: str = "Friend"):
    # ... initialization ...
    self.continuous_learning = ContinuousLearningEngine(data_dir=data_dir)
```

### Knowledge Absorption

```python
def learn_from_interaction(self, user_message: str, topic: str) -> LearningReport:
    """Absorb knowledge from user interaction."""
    report = self.continuous_learning.absorb_information(
        topic=topic,
        content=user_message,
        metadata={"source": "user_interaction", "timestamp": datetime.now().isoformat()}
    )
    return report
```

---

## Usage Examples

### Creating Persona

```python
from app.core.ai_systems import AIPersona

persona = AIPersona(data_dir="data", user_name="Alice")
```

### Updating Interaction Count

```python
def handle_user_message(message: str):
    persona.total_interactions += 1
    persona.last_user_message_time = datetime.now().isoformat()
    persona._save_state()
```

### Customizing Personality

```python
# Make AI more playful and less formal
persona.adjust_trait("playfulness", +0.2)
persona.adjust_trait("formality", -0.3)

# Increase curiosity for research tasks
persona.adjust_trait("curiosity", +0.15)
```

### Mood-Based Response Modulation

```python
def generate_response(prompt: str) -> str:
    if persona.mood["enthusiasm"] > 0.8:
        prefix = "Great question! "
    elif persona.mood["energy"] < 0.3:
        prefix = "Hmm, "
    else:
        prefix = ""
    
    return prefix + generate_base_response(prompt)
```

---

## GUI Integration

### PersonaPanel Components

**File**: `src/app/gui/persona_panel.py` [[src/app/gui/persona_panel.py]]

#### Trait Sliders

```python
for trait, value in persona.personality.items():
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(0, 100)
    slider.setValue(int(value * 100))
    slider.valueChanged.connect(lambda v, t=trait: update_trait(t, v/100))
```

#### Mood Display

```python
for dimension, value in persona.mood.items():
    bar = QProgressBar()
    bar.setValue(int(value * 100))
    mood_layout.addWidget(QLabel(dimension.capitalize()), bar)
```

#### Interaction Stats

```python
stats_label.setText(f"Total Interactions: {persona.total_interactions}")
last_interaction_label.setText(f"Last Active: {persona.last_user_message_time}")
```

---

## Testing Strategy

### Unit Tests

```python
def test_trait_adjustment():
    with tempfile.TemporaryDirectory() as tmpdir:
        persona = AIPersona(data_dir=tmpdir)
        initial = persona.personality["curiosity"]
        persona.adjust_trait("curiosity", 0.1)
        assert persona.personality["curiosity"] == min(1.0, initial + 0.1)

def test_mood_update():
    with tempfile.TemporaryDirectory() as tmpdir:
        persona = AIPersona(data_dir=tmpdir)
        initial = persona.mood["enthusiasm"]
        persona.update_mood("positive")
        assert persona.mood["enthusiasm"] > initial
```

### State Persistence Test

```python
def test_state_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create and modify persona
        persona1 = AIPersona(data_dir=tmpdir)
        persona1.adjust_trait("playfulness", 0.2)
        
        # Reload from disk
        persona2 = AIPersona(data_dir=tmpdir)
        assert persona2.personality["playfulness"] == persona1.personality["playfulness"]
```

---

## Performance Considerations

### Memory Footprint

- **Personality**: 8 floats × 8 bytes = 64 bytes
- **Mood**: 4 floats × 8 bytes = 32 bytes
- **Total State**: ~300 bytes (including metadata)

**Negligible overhead** for in-memory operations.

### File I/O

- **Load**: Once at startup (~1ms)
- **Save**: After each trait/mood change (~5ms with atomic write)
- **Optimization**: Batch updates before saving

---

## Related Modules

| Module | Relationship |
|--------|-------------|
| `continuous_learning.py` | Provides LearningReport integration |
| `memory_engine.py` | Stores conversation context with persona traits |
| `persona_panel.py` | GUI for trait/mood visualization and editing |
| `telemetry.py` | Logs persona state changes |

---

## Future Enhancements

1. **Personality Archetypes**: Predefined profiles (e.g., "Mentor", "Friend", "Professional")
2. **Trait Constraints**: Mutual exclusivity rules (high formality + high playfulness conflict)
3. **Mood Triggers**: Automatic mood shifts based on conversation tone analysis
4. **Learning from Feedback**: ML-based trait optimization from user ratings
5. **Multi-User Personas**: Different personality per user account

---

## References

- **Big Five Personality Model**: https://en.wikipedia.org/wiki/Big_Five_personality_traits
- **Affective Computing**: https://affect.media.mit.edu/
- **AI_PERSONA_IMPLEMENTATION.md**: Project-specific implementation guide

---

**Last Updated**: 2024-01-20  
**Schema Version**: 1.0  
**Maintainer**: Project-AI Core Team


---

## Related Documentation

- **Relationship Map**: [[relationships\data\README.md]]


---

## Source Code References

- **Primary Module**: [[src/app/core/ai_systems.py]]
