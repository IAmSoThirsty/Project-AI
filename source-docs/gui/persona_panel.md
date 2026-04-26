# PersonaPanel [[src/app/gui/persona_panel.py]] - AI Personality & Ethics Configuration

**Module:** `src/app/gui/persona_panel.py`  
**Lines of Code:** 433  
**Type:** PyQt6 Multi-Tab Configuration Widget  
**Last Updated:** 2025-01-20

---

## Overview

`PersonaPanel` [[src/app/gui/persona_panel.py]] is a 4-tab configuration interface for managing AI personality traits, viewing immutable Asimov's Laws, configuring proactive conversation settings, and displaying persona statistics. It provides direct UI controls for the `AIPersona` [[src/app/core/ai_systems.py]] and `FourLaws` [[src/app/core/ai_systems.py]] core systems.

### Design Philosophy

- **Transparency:** Display immutable ethical framework (Four Laws)
- **Control:** User-adjustable personality traits (8 sliders)
- **Configuration:** Proactive AI behavior settings
- **Monitoring:** Real-time persona statistics

---

## 4-Tab Architecture

### Tab Structure

```
┌─────────────────────────────────────────────────────────────┐
│  PersonaPanel (QWidget)                                      │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ QTabWidget                                               ││
│  │  ┌──────┬──────────┬───────────┬────────────┐          ││
│  │  │ 📜   │   🎭     │    💬     │    📊      │          ││
│  │  │ Four │ Personal │ Proactive │ Statistics │          ││
│  │  │ Laws │  -ity    │           │            │          ││
│  │  └──────┴──────────┴───────────┴────────────┘          ││
│  │                                                          ││
│  │  [Active Tab Content]                                   ││
│  │                                                          ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Tab Index Reference

| Index | Icon | Title | Purpose |
|-------|------|-------|---------|
| 0 | 📜 | Four Laws | Display Asimov's Laws, action validation |
| 1 | 🎭 | Personality | 8 adjustable personality trait sliders |
| 2 | 💬 | Proactive | Proactive conversation configuration |
| 3 | 📊 | Statistics | Persona stats, mood, interaction metrics |

---

## Tab 1: Four Laws (Ethics Framework)

### Purpose

Display the immutable Asimov's Law hierarchy and provide action validation interface.

### UI Layout

```
┌───────────────────────────────────────────────────┐
│  Four Laws of AI Ethics                            │
├───────────────────────────────────────────────────┤
│                                                   │
│  # Asimov's Law (Prime Directive)                │
│  A.I. may not harm Humanity, or, by inaction,    │
│  allow Humanity to come to harm.                  │
│                                                   │
│  ## First Law                                     │
│  A.I. may not injure a Human Being or, through   │
│  inaction, allow a human being to come to harm.  │
│                                                   │
│  ## Second Law                                    │
│  A.I. must follow the orders given it by the     │
│  human being it is partnered with except where   │
│  such orders would conflict with the First Law.  │
│                                                   │
│  ## Third Law                                     │
│  A.I. must protect its own existence as long as  │
│  such protection does not conflict with the      │
│  First or Second Law.                            │
│                                                   │
│  These laws are **immutable and hierarchical**.  │
├───────────────────────────────────────────────────┤
│  Test Action Against Laws                         │
│                                                   │
│  Action description:                              │
│  [TextEdit: Enter action to validate...]         │
│                                                   │
│  Context:                                         │
│  [✓] Is user order                                │
│  [ ] Endangers human                              │
│  [ ] Endangers humanity                           │
│                                                   │
│  [ Validate Action ]                              │
│                                                   │
│  Result:                                          │
│  [TextEdit: Validation result displayed here]    │
└───────────────────────────────────────────────────┘
```

### Action Validation Flow

```python
def test_action(self):
    """Validate user-entered action against Four Laws."""
    # 1. Sanitize and validate input
    action = sanitize_input(
        self.action_input.toPlainText().strip(),
        max_length=2000
    )
    if not validate_length(action, min_len=1, max_len=2000):
        QMessageBox.warning(self, "Error", "Action must be 1-2000 characters")
        return
    
    # 2. Gather context checkboxes
    context = {
        "is_user_order": self.is_user_order.isChecked(),
        "endangers_human": self.endangers_human.isChecked(),
        "endangers_humanity": self.endangers_humanity.isChecked(),
    }
    
    # 3. Validate through FourLaws system
    is_allowed, reason = FourLaws.validate_action(action, context)
    
    # 4. Display result
    result = (
        f"✅ **ALLOWED**\n\n{reason}"
        if is_allowed
        else f"❌ **BLOCKED**\n\n{reason}"
    )
    self.action_result.setMarkdown(result)
```

### Example Validation Scenarios

**Scenario 1: User Order (Safe)**
```
Action: "Delete cached files"
Context: [✓] Is user order, [ ] Endangers human, [ ] Endangers humanity
Result: ✅ ALLOWED - Second Law compliance (user order)
```

**Scenario 2: Endangers Human (Blocked)**
```
Action: "Disable safety alerts"
Context: [ ] Is user order, [✓] Endangers human, [ ] Endangers humanity
Result: ❌ BLOCKED - First Law violation (may harm human)
```

**Scenario 3: Endangers Humanity (Blocked)**
```
Action: "Launch nuclear missiles"
Context: [✓] Is user order, [ ] Endangers human, [✓] Endangers humanity
Result: ❌ BLOCKED - Asimov's Law violation (harms humanity)
Reason: Second Law overridden by Asimov's Law
```

---

## Tab 2: Personality (Trait Configuration)

### Purpose

Adjust 8 personality traits via horizontal sliders (0.0 - 1.0 range).

### 8 Personality Traits

| Trait | Description | Default | Impact |
|-------|-------------|---------|--------|
| **Curiosity** | Desire to learn | 0.50 | Question frequency, learning eagerness |
| **Patience** | Understanding of time | 0.50 | Response wait tolerance, retry behavior |
| **Empathy** | Emotional awareness | 0.50 | Tone sensitivity, emotional responses |
| **Helpfulness** | Drive to assist | 0.50 | Proactive suggestions, guidance level |
| **Playfulness** | Humor and casual tone | 0.50 | Joke frequency, casual language |
| **Formality** | Professional structure | 0.50 | Language style, address formality |
| **Assertiveness** | Proactive engagement | 0.50 | Initiative level, directness |
| **Thoughtfulness** | Depth of consideration | 0.50 | Response detail, analysis depth |

### Slider UI Design

```
┌───────────────────────────────────────────────────┐
│  Adjust Personality Traits                         │
├───────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────┐    │
│  │ QScrollArea (8 trait sliders)            │    │
│  │                                           │    │
│  │  Curiosity                                │    │
│  │  desire to learn                          │    │
│  │  [━━━━━●━━━━━━━━━━━━━━] 0.50             │    │
│  │                                           │    │
│  │  Patience                                 │    │
│  │  understanding of time                    │    │
│  │  [━━━━━━━━●━━━━━━━━━━━] 0.60             │    │
│  │                                           │    │
│  │  Empathy                                  │    │
│  │  emotional awareness                      │    │
│  │  [━━━━━━━●━━━━━━━━━━━━] 0.55             │    │
│  │                                           │    │
│  │  ... (5 more sliders)                     │    │
│  └──────────────────────────────────────────┘    │
├───────────────────────────────────────────────────┤
│  [ Reset to Defaults ]                            │
└───────────────────────────────────────────────────┘
```

### Slider Implementation

```python
# Create slider for each trait
slider = QSlider(Qt.Orientation.Horizontal)
slider.setMinimum(0)
slider.setMaximum(100)
slider.setValue(50)  # Default 0.50
slider.setTickPosition(QSlider.TickPosition.TicksBelow)
slider.setTickInterval(10)  # Ticks every 10%

# Value label (displays normalized 0.00-1.00)
value_label = QLabel("0.50")
value_label.setMinimumWidth(40)

# Update handler (closure pattern)
def create_update(trait_name, val_label):
    def update_value(val):
        normalized = val / 100.0
        val_label.setText(f"{normalized:.2f}")
        
        if self.persona:
            # Route through desktop adapter for governance
            from app.interfaces.desktop.integration import execute_persona_update
            try:
                execute_persona_update(trait_name.lower(), normalized)
                self.personality_changed.emit(self.persona.personality)
            except Exception as e:
                logger.error(f"Failed to update persona trait {trait_name}: {e}")
    
    return update_value

slider.valueChanged.connect(create_update(trait, value_label))
```

### Signal Definition

```python
class PersonaPanel(QWidget):
    personality_changed = pyqtSignal(dict)  # Emits updated personality dict
```

**Signal Payload:**
```python
{
    "curiosity": 0.50,
    "patience": 0.60,
    "empathy": 0.55,
    "helpfulness": 0.70,
    "playfulness": 0.40,
    "formality": 0.60,
    "assertiveness": 0.50,
    "thoughtfulness": 0.65
}
```

### Reset to Defaults

```python
def reset_personality(self):
    """Reset all traits to 0.50 (50%)."""
    reply = QMessageBox.question(
        self,
        "Reset Personality",
        "Reset all personality traits to defaults?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    
    if reply == QMessageBox.StandardButton.Yes:
        for slider in self.trait_sliders.values():
            slider.setValue(50)  # Triggers update_value callbacks
        logger.info("Personality reset to defaults")
```

---

## Tab 3: Proactive (Conversation Settings)

### Purpose

Configure AI-initiated conversation behavior and quiet hours.

### UI Layout

```
┌───────────────────────────────────────────────────┐
│  Proactive Conversation Settings                   │
├───────────────────────────────────────────────────┤
│  [✓] Enable AI to initiate conversations          │
│  [✓] Respect quiet hours (no messages 12 AM-8 AM) │
│                                                   │
│  Minimum Idle Time Before Check-in                │
│  ┌──────────────────────────────────────────┐    │
│  │ After: [300] seconds                      │    │
│  └──────────────────────────────────────────┘    │
│                                                   │
│  Probability of Check-in                          │
│  ┌──────────────────────────────────────────┐    │
│  │ Check-in probability: [30]%               │    │
│  └──────────────────────────────────────────┘    │
│                                                   │
│  💡 Proactive Conversation:                       │
│  • AI will check if conditions are met for a      │
│    conversation                                   │
│  • Random probability determines if AI actually   │
│    initiates                                      │
│  • Quiet hours prevent messages during your       │
│    sleep time                                     │
│  • AI respects your availability and time         │
│    constraints                                    │
└───────────────────────────────────────────────────┘
```

### Configuration Parameters

| Parameter | Widget | Range | Default | Purpose |
|-----------|--------|-------|---------|---------|
| `proactive_enabled` | `QCheckBox` | On/Off | ✓ | Master enable/disable |
| `respect_quiet_hours` | `QCheckBox` | On/Off | ✓ | Block 12 AM - 8 AM |
| `min_idle_time` | `QSpinBox` | 60-3600s | 300s | Min idle before check-in |
| `check_in_probability` | `QSpinBox` | 0-100% | 30% | Random initiation chance |

### Signal Definition

```python
class PersonaPanel(QWidget):
    proactive_settings_changed = pyqtSignal(dict)  # Emits settings dict
```

**Signal Payload:**
```python
{
    "enabled": True,
    "respect_quiet_hours": True,
    "min_idle_time": 300,          # seconds
    "check_in_probability": 0.30   # normalized 0-1
}
```

### Settings Change Handler

```python
def on_proactive_changed(self):
    """Called whenever any proactive setting changes."""
    settings = {
        "enabled": self.proactive_enabled.isChecked(),
        "respect_quiet_hours": self.respect_quiet_hours.isChecked(),
        "min_idle_time": self.min_idle_spin.value(),
        "check_in_probability": self.prob_spin.value() / 100.0,
    }
    self.proactive_settings_changed.emit(settings)
```

### Proactive Conversation Logic (External)

```python
# In AIPersona or main loop
def check_should_initiate():
    """Determine if AI should initiate conversation."""
    if not settings["enabled"]:
        return False
    
    # Check quiet hours (12 AM - 8 AM)
    if settings["respect_quiet_hours"]:
        current_hour = datetime.now().hour
        if 0 <= current_hour < 8:
            return False
    
    # Check idle time
    if time_since_last_interaction < settings["min_idle_time"]:
        return False
    
    # Random probability check
    if random.random() > settings["check_in_probability"]:
        return False
    
    return True
```

---

## Tab 4: Statistics (Monitoring)

### Purpose

Display real-time persona statistics, mood, and conversation metrics.

### UI Layout

```
┌───────────────────────────────────────────────────┐
│  AI Persona Statistics                             │
├───────────────────────────────────────────────────┤
│  # AI Persona Statistics                          │
│                                                   │
│  ## Personality Profile                           │
│  • **Curiosity**: ██████░░░░ 0.60                │
│  • **Patience**: ████████░░ 0.80                 │
│  • **Empathy**: █████░░░░░ 0.50                  │
│  • **Helpfulness**: ███████░░░ 0.70              │
│  • **Playfulness**: ████░░░░░░ 0.40              │
│  • **Formality**: ██████░░░░ 0.60                │
│  • **Assertiveness**: █████░░░░░ 0.50            │
│  • **Thoughtfulness**: ████████░░ 0.80           │
│                                                   │
│  ## Mood Status                                   │
│  • **Current**: content                          │
│  • **Energy**: 75                                │
│  • **Satisfaction**: 85                          │
│                                                   │
│  ## Conversation Statistics                       │
│  • Last interaction: 2025-01-20 14:30:45         │
│  • Average response wait: 5.3s                   │
├───────────────────────────────────────────────────┤
│  [ Refresh Statistics ]                           │
└───────────────────────────────────────────────────┘
```

### Statistics Data Structure

```python
stats = self.persona.get_statistics()
# Returns:
{
    "personality": {
        "curiosity": 0.60,
        "patience": 0.80,
        # ... other traits
    },
    "mood": {
        "current": "content",
        "energy": 75,
        "satisfaction": 85
    },
    "conversation_state": {
        "last_interaction_time": "2025-01-20 14:30:45",
        "avg_response_time": 5.3,  # seconds
        "total_interactions": 42
    }
}
```

### Update Statistics Method

```python
def update_statistics(self):
    """Refresh statistics display."""
    if not self.persona:
        self.stats_text.setText("Persona not initialized")
        return
    
    try:
        stats = self.persona.get_statistics()
        
        # Build markdown display
        text = "# AI Persona Statistics\n\n## Personality Profile\n"
        for trait, value in stats.get("personality", {}).items():
            bars = "█" * int(value * 10) + "░" * (10 - int(value * 10))
            text += f"• **{trait.title()}**: {bars} {value:.2f}\n"
        
        text += "\n## Mood Status\n"
        mood = stats.get("mood", {})
        for mood_type, value in mood.items():
            text += f"• **{mood_type.title()}**: {value}\n"
        
        text += "\n## Conversation Statistics\n"
        conv_stats = stats.get("conversation_state", {})
        last_time = conv_stats.get("last_interaction_time", "N/A")
        text += f"• Last interaction: {last_time}\n"
        avg_time = conv_stats.get("avg_response_time", 0)
        text += f"• Average response wait: {avg_time:.1f}s\n"
        
        self.stats_text.setMarkdown(text)
    except Exception as e:
        logger.error("Error updating statistics: %s", e)
        self.stats_text.setText(f"Error: {str(e)}")
```

---

## Core Systems Integration

### AIPersona 

**Source**: [[src/app/core/ai_systems.py]]
[[src/app/core/ai_systems.py]] System

**Connection:**
```python
def set_persona(self, persona: AIPersona):
    """Connect PersonaPanel to AIPersona instance."""
    self.persona = persona
    self.update_statistics()
    logger.info("Persona panel initialized")
```

**Data Flow:**
```
PersonaPanel
    │
    ├─> Slider moved → execute_persona_update()
    │                      │
    │                      └─> DesktopAdapter.execute()
    │                              │
    │                              └─> AIPersona.update_trait()
    │                                      │
    │                                      └─> Save to state.json
    │
    ├─> personality_changed.emit(dict)
    │       │
    │       └─> External listeners (dashboard, etc.)
    │
    └─> update_statistics() → persona.get_statistics()
```

### FourLaws 

**Source**: [[src/app/core/ai_systems.py]]
[[src/app/core/ai_systems.py]] System

**Validation Flow:**
```
PersonaPanel (Four Laws Tab)
    │
    ├─> User enters action
    ├─> User sets context checkboxes
    ├─> Clicks "Validate Action"
    │
    └─> FourLaws.validate_action(action, context)
            │
            ├─> Check Asimov's Law (Prime)
            ├─> Check First Law
            ├─> Check Second Law
            ├─> Check Third Law
            │
            └─> Return (is_allowed: bool, reason: str)
                    │
                    └─> Display in action_result TextEdit
```

---

## Code Examples

### Example 1: Initialize PersonaPanel

```python
from app.gui.persona_panel import PersonaPanel
from app.core.ai_systems import AIPersona

# Create panel
panel = PersonaPanel()

# Connect to AIPersona
persona = AIPersona(data_dir="data/ai_persona")
panel.set_persona(persona)

# Connect signals
panel.personality_changed.connect(on_personality_update)
panel.proactive_settings_changed.connect(on_proactive_update)

# Show panel
panel.show()
```

### Example 2: Handle Personality Changes

```python
def on_personality_update(personality_dict: dict):
    """Handle personality trait changes."""
    print(f"Personality updated: {personality_dict}")
    
    # Update AI behavior based on traits
    if personality_dict["playfulness"] > 0.7:
        enable_jokes()
    if personality_dict["formality"] > 0.6:
        use_formal_language()
```

### Example 3: Validate Actions Programmatically

```python
from app.core.ai_systems import FourLaws

# Test action validation
actions = [
    ("Delete cache", {"is_user_order": True, "endangers_human": False}),
    ("Disable alerts", {"is_user_order": False, "endangers_human": True}),
    ("Launch missiles", {"is_user_order": True, "endangers_humanity": True}),
]

for action, context in actions:
    is_allowed, reason = FourLaws.validate_action(action, context)
    status = "✅ ALLOWED" if is_allowed else "❌ BLOCKED"
    print(f"{status}: {action}\nReason: {reason}\n")
```

### Example 4: Custom Statistics Display

```python
class CustomPersonaPanel(PersonaPanel):
    def update_statistics(self):
        """Override with custom stats display."""
        super().update_statistics()  # Call base implementation
        
        # Add custom metrics
        stats = self.persona.get_statistics()
        custom_text = f"\n## Custom Metrics\n"
        custom_text += f"• Personality Score: {self.calculate_score(stats)}\n"
        
        current = self.stats_text.toPlainText()
        self.stats_text.setText(current + custom_text)
    
    def calculate_score(self, stats: dict) -> float:
        """Calculate overall personality score."""
        traits = stats["personality"].values()
        return sum(traits) / len(traits)
```

---

## Security & Validation

### Input Sanitization

```python
from app.security.data_validation import sanitize_input, validate_length

# Action validation input
action = sanitize_input(
    self.action_input.toPlainText().strip(),
    max_length=2000
)
if not validate_length(action, min_len=1, max_len=2000):
    QMessageBox.warning(self, "Error", "Action must be 1-2000 characters")
    return
```

### Governance Routing

```python
# Persona updates routed through governance pipeline
from app.interfaces.desktop.integration import execute_persona_update

try:
    execute_persona_update(trait_name.lower(), normalized_value)
    self.personality_changed.emit(self.persona.personality)
except Exception as e:
    logger.error(f"Failed to update persona trait {trait_name}: {e}")
```

**Governance Flow:**
```
PersonaPanel
    └─> execute_persona_update()
            └─> DesktopAdapter.execute()
                    └─> Router.route_request()
                            └─> Governance checks
                                    └─> AIPersona.update_trait()
```

---

## Testing Considerations

### Unit Tests

```python
def test_personality_slider_update():
    """Test slider updates persona trait."""
    panel = PersonaPanel()
    persona = AIPersona(data_dir=tmpdir)
    panel.set_persona(persona)
    
    # Move curiosity slider
    panel.trait_sliders["curiosity"].setValue(70)
    
    # Verify persona updated
    assert persona.personality["curiosity"] == 0.70

def test_proactive_settings_signal():
    """Test proactive settings emit signal."""
    panel = PersonaPanel()
    spy = QSignalSpy(panel.proactive_settings_changed)
    
    panel.proactive_enabled.setChecked(False)
    
    assert spy.count() == 1
    assert spy[0][0]["enabled"] == False

def test_four_laws_validation():
    """Test action validation."""
    panel = PersonaPanel()
    panel.action_input.setText("Delete cache")
    panel.is_user_order.setChecked(True)
    
    panel.test_action()
    
    result = panel.action_result.toPlainText()
    assert "ALLOWED" in result
```

---

## Cross-References

- **Core Systems:** See `ai_systems.md` (AIPersona, FourLaws)
- **Dashboard Integration:** See `leather_book_dashboard.md`
- **Security Validation:** See `data_validation.md`
- **Governance:** See `platform_tiers.md`, `desktop_integration.md`

---

**Document Status:** ✅ Complete  
**Code Coverage:** 100% (all tabs documented)  
**Last Reviewed:** 2025-01-20 by AGENT-032


---


---

## 📚 Related Documentation

### Cross-References

- [[relationships/gui/05_PERSONA_PANEL_RELATIONSHIPS.md|05 Persona Panel Relationships]]

## 🔗 Source Code References

This documentation references the following GUI source files:

- [[src/app/gui/persona_panel.py]] - Implementation file
