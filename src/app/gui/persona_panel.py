"""AI Persona panel for dashboard."""

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.ai_systems import AIPersona, FourLaws

logger = logging.getLogger(__name__)


class PersonaPanel(QWidget):
    """Panel for managing AI Persona settings and displaying Four Laws."""

    personality_changed = pyqtSignal(dict)
    proactive_settings_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.persona: AIPersona | None = None
        self.trait_sliders = {}
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)

        # Create tabs
        tabs = QTabWidget()
        tabs.addTab(self.create_four_laws_tab(), "📜 Four Laws")
        tabs.addTab(self.create_personality_tab(), "🎭 Personality")
        tabs.addTab(self.create_proactive_tab(), "💬 Proactive")
        tabs.addTab(self.create_statistics_tab(), "📊 Statistics")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_four_laws_tab(self) -> QWidget:
        """Create the Four Laws display tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("Four Laws of AI Ethics")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Laws display
        laws_text = QTextEdit()
        laws_text.setReadOnly(True)
        laws_text.setMarkdown("""# Asimov's Law (Prime Directive)
*A.I. may not harm Humanity, or, by inaction, allow Humanity to come to harm.*

## First Law
*A.I. may not injure a Human Being or, through inaction, allow a human
being to come to harm.*

## Second Law
*A.I. must follow the orders given it by the human being it is partnered
with except where such orders would conflict with the First Law.*

## Third Law
*A.I. must protect its own existence as long as such protection does not
conflict with the First or Second Law.*

---

These laws are **immutable and hierarchical**. They cannot be overridden or modified.
""")
        layout.addWidget(laws_text)

        # Action test
        group = QGroupBox("Test Action Against Laws")
        group_layout = QVBoxLayout()

        action_label = QLabel("Action description:")
        self.action_input = QTextEdit()
        self.action_input.setMaximumHeight(60)
        group_layout.addWidget(action_label)
        group_layout.addWidget(self.action_input)

        # Context checkboxes
        context_label = QLabel("Context:")
        self.is_user_order = QCheckBox("Is user order")
        self.endangers_human = QCheckBox("Endangers human")
        self.endangers_humanity = QCheckBox("Endangers humanity")

        group_layout.addWidget(context_label)
        group_layout.addWidget(self.is_user_order)
        group_layout.addWidget(self.endangers_human)
        group_layout.addWidget(self.endangers_humanity)

        # Test button
        test_btn = QPushButton("Validate Action")
        test_btn.clicked.connect(self.test_action)
        group_layout.addWidget(test_btn)

        # Result display
        self.action_result = QTextEdit()
        self.action_result.setReadOnly(True)
        self.action_result.setMaximumHeight(80)
        group_layout.addWidget(QLabel("Result:"))
        group_layout.addWidget(self.action_result)

        group.setLayout(group_layout)
        layout.addWidget(group)

        layout.addStretch()
        return widget

    def create_personality_tab(self) -> QWidget:
        """Create personality adjustment tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("Adjust Personality Traits")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Scrollable area for sliders
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        traits = [
            ("Curiosity", "desire to learn"),
            ("Patience", "understanding of time"),
            ("Empathy", "emotional awareness"),
            ("Helpfulness", "drive to assist"),
            ("Playfulness", "humor and casual tone"),
            ("Formality", "professional structure"),
            ("Assertiveness", "proactive engagement"),
            ("Thoughtfulness", "depth of consideration"),
        ]

        for trait, description in traits:
            # Trait group
            group = QGroupBox(f"{trait}")
            group_layout = QHBoxLayout()

            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: gray; font-size: 10px;")

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setValue(50)
            slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            slider.setTickInterval(10)

            value_label = QLabel("0.50")
            value_label.setMinimumWidth(40)

            def create_update(trait_name, val_label):
                def update_value(val):
                    normalized = val / 100.0
                    val_label.setText(f"{normalized:.2f}")
                    if self.persona:
                        current = self.persona.personality.get(trait_name.lower(), 0.5)
                        delta = normalized - current
                        self.persona.adjust_trait(trait_name, delta)
                        self.personality_changed.emit(self.persona.personality)

                return update_value

            slider.valueChanged.connect(create_update(trait, value_label))

            group_layout.addWidget(desc_label)
            group_layout.addWidget(slider)
            group_layout.addWidget(value_label)
            group.setLayout(group_layout)

            scroll_layout.addWidget(group)
            self.trait_sliders[trait.lower()] = slider

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Reset button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self.reset_personality)
        layout.addWidget(reset_btn)

        return widget

    def create_proactive_tab(self) -> QWidget:
        """Create proactive conversation settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("Proactive Conversation Settings")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Enable/disable
        self.proactive_enabled = QCheckBox("Enable AI to initiate conversations")
        self.proactive_enabled.setChecked(True)
        self.proactive_enabled.stateChanged.connect(self.on_proactive_changed)
        layout.addWidget(self.proactive_enabled)

        # Respect quiet hours
        self.respect_quiet_hours = QCheckBox(
            "Respect quiet hours (no messages 12 AM - 8 AM)"
        )
        self.respect_quiet_hours.setChecked(True)
        self.respect_quiet_hours.stateChanged.connect(self.on_proactive_changed)
        layout.addWidget(self.respect_quiet_hours)

        # Min idle time
        idle_group = QGroupBox("Minimum Idle Time Before Check-in")
        idle_layout = QHBoxLayout()
        self.min_idle_spin = QSpinBox()
        self.min_idle_spin.setMinimum(60)
        self.min_idle_spin.setMaximum(3600)
        self.min_idle_spin.setValue(300)
        self.min_idle_spin.setSuffix(" seconds")
        self.min_idle_spin.valueChanged.connect(self.on_proactive_changed)
        idle_layout.addWidget(QLabel("After:"))
        idle_layout.addWidget(self.min_idle_spin)
        idle_layout.addStretch()
        idle_group.setLayout(idle_layout)
        layout.addWidget(idle_group)

        # Probability
        prob_group = QGroupBox("Probability of Check-in")
        prob_layout = QHBoxLayout()
        self.prob_spin = QSpinBox()
        self.prob_spin.setMinimum(0)
        self.prob_spin.setMaximum(100)
        self.prob_spin.setValue(30)
        self.prob_spin.setSuffix("%")
        self.prob_spin.valueChanged.connect(self.on_proactive_changed)
        prob_layout.addWidget(QLabel("Check-in probability:"))
        prob_layout.addWidget(self.prob_spin)
        prob_layout.addStretch()
        prob_group.setLayout(prob_layout)
        layout.addWidget(prob_group)

        # Information
        info = QTextEdit()
        info.setReadOnly(True)
        info.setMaximumHeight(120)
        info.setText(
            "💡 Proactive Conversation:\n"
            "• AI will check if conditions are met for a conversation\n"
            "• Random probability determines if AI actually initiates\n"
            "• Quiet hours prevent messages during your sleep time\n"
            "• AI respects your availability and time constraints"
        )
        layout.addWidget(info)

        layout.addStretch()
        return widget

    def create_statistics_tab(self) -> QWidget:
        """Create statistics and mood display tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Title
        title = QLabel("AI Persona Statistics")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Statistics display
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        layout.addWidget(self.stats_text)

        # Refresh button
        refresh_btn = QPushButton("Refresh Statistics")
        refresh_btn.clicked.connect(self.update_statistics)
        layout.addWidget(refresh_btn)

        layout.addStretch()
        return widget

    def test_action(self):
        """Test an action against the Four Laws."""
        if not self.persona:
            QMessageBox.warning(self, "Error", "Persona not initialized")
            return

        action = self.action_input.toPlainText().strip()
        if not action:
            QMessageBox.warning(self, "Error", "Please enter an action description")
            return

        context = {
            "is_user_order": self.is_user_order.isChecked(),
            "endangers_human": self.endangers_human.isChecked(),
            "endangers_humanity": self.endangers_humanity.isChecked(),
        }

        try:
            is_allowed, reason = FourLaws.validate_action(action, context)
            result = (
                f"✅ **ALLOWED**\n\n{reason}"
                if is_allowed
                else f"❌ **BLOCKED**\n\n{reason}"
            )
            self.action_result.setMarkdown(result)
        except Exception as e:
            logger.error("Error validating action: %s", e)
            self.action_result.setText(f"Error: {str(e)}")

    def reset_personality(self):
        """Reset personality to defaults."""
        if not self.persona:
            return

        reply = QMessageBox.question(
            self,
            "Reset Personality",
            "Reset all personality traits to defaults?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Reset all sliders to 50 (0.5)
            for slider in self.trait_sliders.values():
                slider.setValue(50)
            logger.info("Personality reset to defaults")

    def on_proactive_changed(self):
        """Handle proactive settings change."""
        settings = {
            "enabled": self.proactive_enabled.isChecked(),
            "respect_quiet_hours": self.respect_quiet_hours.isChecked(),
            "min_idle_time": self.min_idle_spin.value(),
            "check_in_probability": self.prob_spin.value() / 100.0,
        }
        self.proactive_settings_changed.emit(settings)

    def update_statistics(self):
        """Update statistics display."""
        if not self.persona:
            self.stats_text.setText("Persona not initialized")
            return

        try:
            stats = self.persona.get_statistics()
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

    def set_persona(self, persona: AIPersona):
        """Set the AI persona."""
        self.persona = persona
        self.update_statistics()
        logger.info("Persona panel initialized")

    def get_settings(self) -> dict:
        """Get current settings."""
        return {
            "personality": {
                trait: slider.value() / 100.0
                for trait, slider in self.trait_sliders.items()
            },
            "proactive": {
                "enabled": self.proactive_enabled.isChecked(),
                "respect_quiet_hours": self.respect_quiet_hours.isChecked(),
                "min_idle_time": self.min_idle_spin.value(),
                "check_in_probability": self.prob_spin.value() / 100.0,
            },
        }
