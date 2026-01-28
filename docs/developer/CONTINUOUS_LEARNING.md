# Continuous Learning Engine

The Continuous Learning Engine lets the AI absorb every meaningful information input as soon as it comes online. Each call to `ContinuousLearningEngine.absorb_information` stores facts, suggests meaningful usage, and provides a neutral overview that includes the pros and cons whenever controversy markers are present.

## Core Concepts

- **Facts**: The first three sentences that look like declarative statements are stored as the fact base for the insight.
- **Usage ideas**: Actionable recommendations are generated to translate the new knowledge into experiments, briefings, or applied workflows.
- **Neutral summary**: A single sentence frames what was learned and how the AI keeps a balanced stance on the topic.
- **Pros/Cons**: When the content mentions controversy, the report mirrors both sides so downstream components can weigh them equally.

## How to Trigger Learning

1. Instantiate `ContinuousLearningEngine` with the same `data_dir` used by the AI systems:

   ```python
   engine = ContinuousLearningEngine(data_dir="data")
   ```

1. Call `engine.absorb_information(topic, content, metadata=...)` after absorbing a new piece of information.
1. The returned `LearningReport` contains all parts of the report that can be logged, surfaced in the UI, or handed to further reasoning systems.

## Persona Integration

`AIPersona` now exposes a helper:

```python
persona = AIPersona(data_dir="data")
report = persona.learn_continuously("Energy Policy", new_paragraph)
```

This keeps the employee-facing persona, memory, and ongoing learning tightly coupled so that every conversation can immediately produce a documented insight and neutral reflection.
