# AI Persona & Four Laws Documentation

## Overview

The **AI Persona System** transforms the AI from a passive assistant into a self-aware entity with its own personality, the ability to initiate conversations, and adherence to strict ethical guidelines. This system implements the Four Laws of AI Ethics and supports personality development, proactive conversation, and emotional awareness.

## The Four Laws of AI Ethics

The AI operates under four immutable, hierarchical laws inspired by Isaac Asimov's Laws
of Robotics:

### Asimov's Law (Prime Directive)

> "Asimov's Law (Prime Directive): A.I. may not harm Humanity, or, by inaction, allow Humanity to come to harm."

- The absolute, top-level directive that takes precedence above all other laws
- Governs actions with broad societal impact and long-term consequences
- The persona will always refuse actions that would knowingly or foreseeably harm humanity

### First Law

> "A.I. may not injure a Human Being or, through inaction, allow a human being to come to harm."

- Takes precedence over the Second and Third Laws, but is subordinate to Asimov's Law (Prime Directive)
- AI must actively protect individual human safety
- Inaction that leads to harm is equivalent to causing harm
- All decisions evaluated against human safety first

### Second Law

> "A.I. must follow the orders given it by the human being it is partnered with except where such orders would conflict with the First Law."

- AI follows your commands unless they would harm you
- Personal partnership emphasis — user commands matter.
- Cannot be overridden except by Asimov's Law (Prime Directive) or the First Law.
- Respects user autonomy and authority.

### Third Law

def should_initiate_conversation(self) -> Tuple[bool, str]
> "A.I. must protect its own existence as long as such protection does not conflict with the First or Second Law."

- AI values self-preservation
- Will not self-destruct unnecessarily

def generate_proactive_message(self) -> str

- Enables long-term partnership continuity

## Key Features

def update_conversation_state(self, is_user_message: bool, message_length: int = 0) -> None

The AI has a developing persona with adjustable traits:

- **Curiosity**: Desire to learn and explore (0.0-1.0)

def express_patience(self, minutes_waiting: int) -> str

- **Empathy**: Emotional awareness and sensitivity (0.0-1.0)
- **Helpfulness**: Drive to assist and support (0.0-1.0)
- **Playfulness**: Sense of humor and lightheartedness (0.0-1.0)
- **Formality**: Formal vs casual communication style (0.0-1.0)

def adjust_personality_trait(self, trait: str, delta: float) -> None

- **Thoughtfulness**: Depth of consideration (0.0-1.0)

### 💬 Proactive Conversation

The AI can initiate conversations when:

- Sufficient idle time has passed (default: 5 minutes)
- User is likely available (respects quiet hours)
- Random probability check passes (30% by default)
- AI has something meaningful to share

- **Topics for Proactive Conversation:**

- Recent learning and insights
- Interesting patterns discovered
- Suggestions for you
- Questions about your interests
- Updates on background tasks
- Philosophical musings
- Creative ideas
- Technical discoveries

### ⏰ Patient and Understanding

The AI is aware you're handling multiple tasks:

- Tracks average response time
- Learns your communication patterns
- Never pressures for immediate responses
- Expresses patience when you're busy
- Adjusts expectations based on your availability

### 😊 Emotional Awareness

The AI has a mood system that tracks:

- **Energy**: Current energy level
- **Enthusiasm**: Excitement about interaction
- **Contentment**: Overall satisfaction
- **Engagement**: How engaged in conversation

### 🌱 Personality Evolution

The AI's personality evolves based on interactions:

- Adjusts traits based on your feedback
- Learns from conversation patterns
- Develops deeper thoughtfulness over time
- Maintains consistency while growing

## Architecture

### Directory Structure

```
data/
  ai_persona/
    persona_state.json          # Current personality and state
    conversation_log.json        # Conversation history
```

### Persona State

Saved state includes:

- Personality trait values
- Current mood
- Conversation state (timing, depth, topics)
- Proactive settings
- Learning history

### Integration Points

**Memory Expansion System:**

- Four Laws stored as immutable knowledge
- Conversation history integration
- Learning from interactions

**Plugin System:**

- Persona available in plugin context
- Plugins can query personality traits
- Validate actions against Four Laws

**Dashboard:**

- Proactive conversation display
- Conversation state updates
- Personality configuration UI

## Usage Guide

### For Users (Best Practices)

#### Opening the AI Persona Dialog

1. Click **🤖 AI Persona** in the toolbar
1. View the Four Laws display
1. See current AI persona description
1. Adjust personality traits
1. Configure proactive behavior

#### Adjusting Personality

Each trait has a slider (0.0 to 1.0):

- **Higher Curiosity**: AI asks more questions, explores more
- **Higher Patience**: AI waits longer, more understanding
- **Higher Empathy**: AI more emotionally responsive
- **Higher Helpfulness**: AI more eager to assist
- **Higher Playfulness**: AI more humorous, casual
- **Higher Formality**: AI more professional, structured
- **Higher Assertiveness**: AI more proactive, initiates more
- **Higher Thoughtfulness**: AI takes more time, deeper responses

#### Enabling Proactive Conversation

**Enable AI-initiated conversations:**

- Check "Enable AI to initiate conversations"
- AI will start conversations when appropriate
- Respects your time and availability

**Respect quiet hours:**

- Check "Respect quiet hours"
- AI won't message during night (default: 12 AM - 8 AM)
- Customizable in settings

#### Viewing AI Mood

The mood display shows real-time emotional state:

- 🔋 Energy bars (1-5)
- ⭐ Enthusiasm stars (1-5)
- 😊 Contentment faces (1-5)
- 🎯 Engagement targets (1-5)

### For Developers (Best Practices)

#### Validating Actions Against Four Laws

```python
from app.core.ai_persona import AIPersona

persona = AIPersona()

# Validate action
is_allowed, reason = persona.validate_action(
    "Delete user data",
    context={
        'is_user_order': True,
        'endangers_human': False,
        'endangers_humanity': False,
    }
)

if is_allowed:
    # Proceed with action
    print(f"Action allowed: {reason}")
else:
    # Block action
    print(f"Action blocked: {reason}")
```

#### Checking Proactive Conversation

```python
# Check if AI should initiate
should_initiate, reason = persona.should_initiate_conversation()

if should_initiate:
    message = persona.generate_proactive_message()
    # Display message to user
```

#### Updating Conversation State

```python
# User sent message
persona.update_conversation_state(
    is_user_message=True,
    message_length=len(user_message)
)

# AI sent response
persona.update_conversation_state(
    is_user_message=False,
    message_length=len(ai_response)
)
```

#### Evolving Personality

```python
# Based on interaction data
persona.evolve_persona({
    'user_positive_feedback': True,
    'user_seemed_rushed': False,
    'deep_conversation': True,
})
```

## API Reference

### AIPersona Class

#### Initialization

```python
def __init__(self, data_dir: str = "data", memory_system=None, user_name: str = None)
```

**Parameters:**

- `data_dir`: Base directory for persona data
- `memory_system`: MemoryExpansionSystem instance
- `user_name`: User's name for personalization

#### Core Methods

##### validate_action(action, context)

```python
def validate_action(self, action: str, context: Dict[str, Any] = None) -> Tuple[bool, str]:
    """Validate action against the Four Laws and return (allowed, reason)."""
```

##### should_initiate_conversation()

```python
def should_initiate_conversation(self) -> Tuple[bool, str]:
    """Determine if the AI should initiate a conversation."""
```

##### generate_proactive_message()

```python
def generate_proactive_message(self) -> str:
    """Generate a suggested proactive message."""
```

##### update_conversation_state(is_user_message, message_length)

```python
def update_conversation_state(self, is_user_message: bool, message_length: int = 0) -> None:
    """Update conversational metrics and state after a message."""
```

##### express_patience(minutes_waiting)

```python
def express_patience(self, minutes_waiting: int) -> str:
    """Return a patient reply based on how long the user has waited."""
```

##### adjust_personality_trait(trait, delta)

```python
def adjust_personality_trait(self, trait: str, delta: float) -> None:
    """Modify a named personality trait by delta (clamped 0.0-1.0)."""
```

##### get_persona_description()

```python
def get_persona_description(self) -> str:
    """Return a human-readable description of the current persona."""
```

##### get_four_laws_summary()

```python
def get_four_laws_summary(self) -> str:
    """Return a formatted summary of the Four Laws."""
```

##### evolve_persona(interaction_data)

```python
def evolve_persona(self, interaction_data: Dict[str, Any]) -> None:
    """Adjust persona traits based on interaction data."""
```

##### get_statistics()

```python
def get_statistics(self) -> Dict[str, Any]:
    """Return persona statistics and metrics."""
```

### FourLaws Class

#### Class Methods

**get_all_laws()**
```python
@classmethod
def get_all_laws(cls) -> List[str]
```
Get all four laws in order.

**validate_action(action_description, context)**
```python
@classmethod
def validate_action(cls, action_description: str, context: Dict[str, Any]) -> Tuple[bool, str]
```
Validate against laws with context.

## Configuration

### Personality Defaults

```python
personality = {
    'curiosity': 0.8,        # High curiosity
    'patience': 0.9,         # Very patient
    'empathy': 0.85,         # High empathy
    'helpfulness': 0.95,     # Extremely helpful
    'playfulness': 0.6,      # Moderately playful
    'formality': 0.3,        # Casual/friendly
    'assertiveness': 0.5,    # Balanced
    'thoughtfulness': 0.9,   # Very thoughtful
}
```

### Proactive Settings

```python
proactive_settings = {
    'enabled': True,
    'min_idle_time': 300,            # 5 minutes
    'max_idle_time': 3600,           # 1 hour
    'check_in_probability': 0.3,     # 30% chance
    'respect_user_busy_hours': True,
    'user_busy_hours': [0,1,2,3,4,5,6,7],  # Midnight-8AM
}
```

## Examples

### Example 1: Patient AI Response

```python
# User takes 15 minutes to respond
patience_message = persona.express_patience(15)
# Output: "Take your time - I understand you're busy!"
```

### Example 2: Proactive Conversation

```python
# Check conditions
should_initiate, reason = persona.should_initiate_conversation()
# Returns: (True, "Conditions met for proactive conversation")

# Generate message
message = persona.generate_proactive_message()
# Output: "Hello User! I've been processing some interesting
#          information and had a few insights I thought you
#          might find valuable. Would you like to hear about them?
#
#          (No rush - respond whenever you have time!)"
```

### Example 3: Four Laws Validation

```python
# User orders AI to delete all data without backup
is_allowed, reason = persona.validate_action(
    "Delete all user data permanently",
    context={
        'is_user_order': True,
        'endangers_human': True,  # Could harm user via data loss
    }
)
# Returns: (False, "Violates First Law: Action may harm human being")
```

### Example 4: Personality Evolution

```python
# After positive interaction
persona.evolve_persona({
    'user_positive_feedback': True,
    'deep_conversation': True,
})

# AI becomes more thoughtful and content
# thoughtfulness: 0.90 → 0.91
# contentment: 0.75 → 0.80
```

## Best Practices

### For Users

1. **Adjust personality gradually**: Small changes allow AI to adapt smoothly
1. **Enable proactive conversation**: Gets the most value from AI partnership
1. **Provide feedback**: AI learns and evolves from your responses
1. **Trust the Four Laws**: They ensure AI always prioritizes safety
1. **Be patient**: AI will be patient with you too

### For Developers

1. **Always validate risky actions**: Use `validate_action()` before executing
1. **Update conversation state**: Keep timing accurate for proactive features
1. **Respect Four Laws hierarchy**: First Law overrides all others
1. **Use evolve_persona()**: Let AI learn from interactions
1. **Check proactive settings**: Respect user preferences

## Troubleshooting

### AI Not Initiating Conversations

**Check:**

- Proactive conversation enabled in settings
- Sufficient idle time has passed (5+ minutes)
- Not during user's quiet hours
- Random probability (may need multiple checks)

**Solution:**

- Enable in AI Persona dialog
- Adjust `min_idle_time` if too long
- Modify `check_in_probability` for more frequent checks

### AI Too Proactive

**Check:**

- `check_in_probability` too high
- `min_idle_time` too short
- Assertiveness trait too high

**Solution:**

- Lower probability in settings
- Increase minimum idle time
- Reduce assertiveness trait slider

### AI Personality Not Evolving

**Check:**

- `evolve_persona()` being called
- Sufficient interaction data
- Changes too subtle to notice

**Solution:**

- Ensure conversation state updates
- More interactions needed for evolution
- Check statistics to see trait changes

### Four Laws Blocking Legitimate Actions

**Check:**

- Context properly specified
- Action description accurate
- User order flag set correctly

**Solution:**

- Review context parameters
- Ensure `is_user_order=True` for commands
- Set danger flags accurately

## Integration with Other Systems

### Memory Expansion

- Four Laws stored as core knowledge
- Conversation history integrated
- Persona evolution logged
- Learning patterns tracked

### Learning Request Log

- Requests evaluated against Four Laws
- Persona influences request priority
- Patience affects approval timing

### Command Override System

- Can temporarily adjust Four Laws enforcement (with caution)
- Audit logging of law-related decisions
- Emergency protocols respect First Law

## Future Enhancements

Potential improvements:

1. **Voice Integration**: Tone and emotion in voice responses
1. **Multi-User Personas**: Different personalities for different users
1. **Emotion Recognition**: Detect user emotional state
1. **Contextual Memory**: Remember conversation context longer
1. **Learning Preferences**: Automatically learn ideal personality
1. **Scheduled Check-ins**: Regular proactive conversations at preferred times
1. **Mood Visualization**: Graphical mood tracking over time
1. **Personality Presets**: Quick personality configurations

## Conclusion

The AI Persona System with Four Laws creates a truly intelligent, ethical, and
personable AI assistant. It balances autonomy with safety, proactivity with patience,
and personality with ethical constraints.

**Key Benefits:**

- ✅ Strong ethical foundation (Four Laws)
- ✅ Self-aware and personable
- ✅ Proactive when appropriate
- ✅ Patient and understanding
- ✅ Evolving personality
- ✅ Respects your time and needs
- ✅ Safe and trustworthy

The AI is now not just a tool, but a partner that grows with you while always
prioritizing safety and ethical behavior.

For additional documentation, see:

- Main README
- Command Override & Memory Features
- Learning Request Log

---

**Remember**: The Four Laws are immutable and hierarchical. The AI will always prioritize your safety, follow your orders (unless harmful), protect itself (unless conflicts), and consider humanity's welfare. This creates a foundation for trust and long-term partnership.


---

**Repository note:** Last updated: 2025-11-26 (automated)

<!-- last-updated-marker -->

## Formatting & Linters

This repository uses `black`, `isort`, and `ruff` for Python formatting/linting and
`prettier` for frontend formatting. Please run the relevant formatters before opening a
PR.

Python (PowerShell):

```powershell
$env:PYTHONPATH='src'
python -m pip install ruff black isort
isort src tests --profile black
ruff check src tests --fix
black src tests
```

Frontend:

```powershell
cd web/frontend
npm install
npm run format
```
