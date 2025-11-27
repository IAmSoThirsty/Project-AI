"""
AI Persona GUI - Interface for managing AI personality and proactive behavior.
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QTextEdit,
    QVBoxLayout,
)


class AIPersonaDialog(QDialog):
    """Dialog for managing AI persona settings and viewing Four Laws."""

    def __init__(self, parent=None, persona_system=None):
        super().__init__(parent)
        self.persona_system = persona_system
        self.setWindowTitle("AI Persona & Four Laws")
        self.setMinimumSize(800, 700)
        self._setup_ui()
        self._load_current_state()

    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(
            "🤖 AI Persona System\n\n"
            "Configure the AI's personality, proactive behavior, and view the Four Laws."
        )
        header.setWordWrap(True)
        header.setStyleSheet(
            "font-weight: bold; padding: 10px; background-color: #e8f4f8;"
        )
        layout.addWidget(header)

        # Four Laws Display
        laws_group = QGroupBox("⚖️ The Four Laws of AI Ethics")
        laws_layout = QVBoxLayout()

        laws_text = self._get_four_laws_display()
        self.laws_display = QTextEdit()
        self.laws_display.setPlainText(laws_text)
        self.laws_display.setReadOnly(True)
        self.laws_display.setMaximumHeight(200)
        self.laws_display.setStyleSheet(
            "font-family: monospace; background-color: #fffef0; "
            "border: 2px solid #d4af37; padding: 10px;"
        )
        laws_layout.addWidget(self.laws_display)

        laws_note = QLabel(
            "These laws are hierarchical and immutable. The AI cannot deviate from them."
        )
        laws_note.setWordWrap(True)
        laws_note.setStyleSheet("font-style: italic; color: #666;")
        laws_layout.addWidget(laws_note)

        laws_group.setLayout(laws_layout)
        layout.addWidget(laws_group)

        # Current Persona Description
        persona_group = QGroupBox("🎭 Current AI Persona")
        persona_layout = QVBoxLayout()

        self.persona_description = QLabel("Loading persona...")
        self.persona_description.setWordWrap(True)
        self.persona_description.setStyleSheet(
            "padding: 10px; background-color: #f9f9f9;"
        )
        persona_layout.addWidget(self.persona_description)

        persona_group.setLayout(persona_layout)
        layout.addWidget(persona_group)

        # Personality Traits
        traits_group = QGroupBox("🧠 Personality Traits")
        traits_layout = QVBoxLayout()

        self.trait_sliders = {}
        traits = [
            ("curiosity", "Curiosity (desire to learn)"),
            ("patience", "Patience (understanding of your time)"),
            ("empathy", "Empathy (emotional awareness)"),
            ("helpfulness", "Helpfulness (desire to assist)"),
            ("playfulness", "Playfulness (humor and lightheartedness)"),
            ("formality", "Formality (formal vs casual)"),
            ("assertiveness", "Assertiveness (proactive vs reactive)"),
            ("thoughtfulness", "Thoughtfulness (depth of consideration)"),
        ]

        for trait_key, trait_label in traits:
            trait_row = QHBoxLayout()
            label = QLabel(trait_label)
            label.setMinimumWidth(250)

            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            slider.setTickInterval(10)

            value_label = QLabel("0.0")
            value_label.setMinimumWidth(40)

            slider.valueChanged.connect(
                lambda v, lbl=value_label: lbl.setText(f"{v/100:.1f}")
            )

            trait_row.addWidget(label)
            trait_row.addWidget(slider)
            trait_row.addWidget(value_label)

            traits_layout.addLayout(trait_row)
            self.trait_sliders[trait_key] = (slider, value_label)

        traits_note = QLabel(
            "Note: Personality traits affect how the AI communicates and behaves. "
            "The AI will evolve these traits over time based on interactions."
        )
        traits_note.setWordWrap(True)
        traits_note.setStyleSheet("font-size: 10px; color: #666; margin-top: 10px;")
        traits_layout.addWidget(traits_note)

        traits_group.setLayout(traits_layout)
        layout.addWidget(traits_group)

        # Proactive Conversation Settings
        proactive_group = QGroupBox("💬 Proactive Conversation")
        proactive_layout = QVBoxLayout()

        self.proactive_enabled = QCheckBox("Enable AI to initiate conversations")
        self.proactive_enabled.setChecked(True)
        proactive_layout.addWidget(self.proactive_enabled)

        proactive_note = QLabel(
            "When enabled, the AI can start conversations on its own when it has "
            "insights, suggestions, or questions to share. The AI will respect your "
            "time and wait patiently for your responses."
        )
        proactive_note.setWordWrap(True)
        proactive_note.setStyleSheet("font-size: 10px; color: #666; margin: 10px 0;")
        proactive_layout.addWidget(proactive_note)

        self.respect_busy_hours = QCheckBox(
            "Respect quiet hours (no messages at night)"
        )
        self.respect_busy_hours.setChecked(True)
        proactive_layout.addWidget(self.respect_busy_hours)

        proactive_group.setLayout(proactive_layout)
        layout.addWidget(proactive_group)

        # Current Mood/State
        mood_group = QGroupBox("😊 Current AI Mood")
        mood_layout = QVBoxLayout()

        self.mood_display = QLabel("Loading mood...")
        self.mood_display.setWordWrap(True)
        self.mood_display.setStyleSheet("padding: 10px; background-color: #f0f8ff;")
        mood_layout.addWidget(self.mood_display)

        mood_group.setLayout(mood_layout)
        layout.addWidget(mood_group)

        # ML Detector Status
        ml_group = QGroupBox("🔬 ML Threat Detectors")
        ml_layout = QVBoxLayout()

        self.detector_status_label = QLabel("Detector status: Not available")
        self.detector_status_label.setWordWrap(True)
        ml_layout.addWidget(self.detector_status_label)

        self.last_trained_label = QLabel("Last trained: N/A")
        ml_layout.addWidget(self.last_trained_label)

        self.retrain_btn = QPushButton("🔁 Retrain Detectors")
        self.retrain_btn.clicked.connect(self._retrain_detectors)
        ml_layout.addWidget(self.retrain_btn)

        # Retrain progress and explainability
        self.retrain_progress_label = QLabel("Retrain progress: N/A")
        ml_layout.addWidget(self.retrain_progress_label)

        self.explain_text = QTextEdit()
        self.explain_text.setReadOnly(True)
        self.explain_text.setMaximumHeight(180)
        ml_layout.addWidget(self.explain_text)

        # Timer to poll retrain progress when running async
        self.retrain_poll_timer = QTimer()
        self.retrain_poll_timer.setInterval(1000)  # 1s
        self.retrain_poll_timer.timeout.connect(self._check_retrain_progress)

        ml_group.setLayout(ml_layout)
        layout.addWidget(ml_group)

        # Action buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("💾 Save Changes")
        save_btn.clicked.connect(self._save_changes)
        save_btn.setStyleSheet(
            "background-color: #44ff44; font-weight: bold; padding: 10px;"
        )

        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        button_layout.addWidget(save_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

        # Auto-refresh timer for mood
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_mood)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds

    def _get_four_laws_display(self) -> str:
        """Get formatted Four Laws text."""
        if not self.persona_system:
            return "Four Laws not available"

        return self.persona_system.get_four_laws_summary()

    def _load_current_state(self):
        """Load current persona state into UI."""
        if not self.persona_system:
            return

        # Load personality traits
        for trait_key, (slider, value_label) in self.trait_sliders.items():
            value = self.persona_system.personality.get(trait_key, 0.5)
            slider.setValue(int(value * 100))
            value_label.setText(f"{value:.1f}")

        # Load proactive settings
        self.proactive_enabled.setChecked(
            self.persona_system.proactive_settings.get("enabled", True)
        )
        self.respect_busy_hours.setChecked(
            self.persona_system.proactive_settings.get("respect_user_busy_hours", True)
        )

        # Load persona description
        self.persona_description.setText(self.persona_system.get_persona_description())

        # Load mood
        self._refresh_mood()

        # Load ML detector status
        self._update_detector_status()
        # Load explainability if available
        try:
            if self.persona_system:
                expl = self.persona_system.get_model_explainability("zeroth", top_n=20)
                txt = "Zeroth model top tokens:\n"
                for t, w in expl:
                    txt += f"{t}: {w:.4f}\n"
                self.explain_text.setPlainText(txt)
        except Exception:
            pass

    def _refresh_mood(self):
        """Refresh mood display."""
        if not self.persona_system:
            return

        mood = self.persona_system.mood
        mood_text = (
            f"Energy: {'🔋' * int(mood['energy'] * 5)}\n"
            f"Enthusiasm: {'⭐' * int(mood['enthusiasm'] * 5)}\n"
            f"Contentment: {'😊' * int(mood['contentment'] * 5)}\n"
            f"Engagement: {'🎯' * int(mood['engagement'] * 5)}"
        )
        self.mood_display.setText(mood_text)

    def _save_changes(self):
        """Save personality changes."""
        if not self.persona_system:
            QMessageBox.warning(self, "Error", "Persona system not available")
            return

        try:
            # Update personality traits
            for trait_key, (slider, _) in self.trait_sliders.items():
                value = slider.value() / 100.0
                self.persona_system.personality[trait_key] = value

            # Update proactive settings
            self.persona_system.proactive_settings["enabled"] = (
                self.proactive_enabled.isChecked()
            )
            self.persona_system.proactive_settings["respect_user_busy_hours"] = (
                self.respect_busy_hours.isChecked()
            )

            # Save state
            self.persona_system._save_persona_state()

            # Update persona description
            self.persona_description.setText(
                self.persona_system.get_persona_description()
            )

            QMessageBox.information(
                self,
                "Success",
                "✓ AI persona settings saved!\n\n"
                "The AI's personality has been updated and will take effect immediately.",
            )
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save changes: {e}")

    def _reset_to_defaults(self):
        """Reset personality to default values."""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Reset AI personality to default values?\n\n"
            "This will restore the original personality traits.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.persona_system:
                # Reset to defaults
                self.persona_system.personality = {
                    "curiosity": 0.8,
                    "patience": 0.9,
                    "empathy": 0.85,
                    "helpfulness": 0.95,
                    "playfulness": 0.6,
                    "formality": 0.3,
                    "assertiveness": 0.5,
                    "thoughtfulness": 0.9,
                }
                self.persona_system._save_persona_state()
                self._load_current_state()
                QMessageBox.information(
                    self, "Reset Complete", "AI personality reset to defaults."
                )

    def _update_detector_status(self):
        """Update the ML detector status display."""
        if not self.persona_system:
            self.detector_status_label.setText("Detector status: Persona not available")
            return

        status = self.persona_system.get_detector_status()
        parts = []
        parts.append(f"PyTorch available: {status['torch_available']}")
        parts.append(f"Zeroth model: {status['has_zeroth_model']}")
        parts.append(f"First model: {status['has_first_model']}")
        self.detector_status_label.setText("; ".join(parts))

        last = status.get("ml_last_trained") or "N/A"
        self.last_trained_label.setText(f"Last trained: {last}")

    def _retrain_detectors(self):
        """Trigger retraining of detectors using examples in data/ai_persona/training_examples."""
        if not self.persona_system:
            QMessageBox.warning(
                self, "Error", "Persona system not available for retraining"
            )
            return

        reply = QMessageBox.question(
            self,
            "Retrain Detectors",
            "Retrain ML detectors using examples stored in data/ai_persona/training_examples/?\n\nThis may take a little time. Proceed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Start async retrain and poll progress
        try:
            started = self.persona_system.retrain_detectors_async()
        except Exception as e:
            QMessageBox.warning(
                self, "Retrain Error", f"Failed to start retraining: {e}"
            )
            return

        if not started:
            QMessageBox.information(self, "Retrain", "Retraining is already running.")
            return

        # Disable button while retraining and start poll timer
        self.retrain_btn.setEnabled(False)
        self.retrain_progress_label.setText("Retrain progress: 0%")
        self.retrain_poll_timer.start()
        QMessageBox.information(
            self,
            "Retrain Started",
            "Retraining started in background. You will be notified when complete.",
        )

    def _check_retrain_progress(self):
        """Poll persona for retrain progress and update UI; called by timer."""
        if not self.persona_system:
            return
        try:
            prog = float(getattr(self.persona_system, "retrain_progress", 0.0) or 0.0)
        except Exception:
            prog = 0.0

        pct = int(prog * 100)
        try:
            self.retrain_progress_label.setText(f"Retrain progress: {pct}%")
        except Exception:
            pass

        # If retrain finished, stop polling and refresh status
        if pct >= 100 or getattr(self.persona_system, "ml_last_trained", None):
            try:
                self.retrain_poll_timer.stop()
            except Exception:
                pass
            try:
                self.retrain_btn.setEnabled(True)
            except Exception:
                pass
            # Update status display and explainability
            try:
                self._update_detector_status()
                expl = self.persona_system.get_model_explainability("zeroth", top_n=20)
                txt = "Zeroth model top tokens:\n"
                for t, w in expl:
                    txt += f"{t}: {w:.4f}\n"
                self.explain_text.setPlainText(txt)
            except Exception:
                pass

            QMessageBox.information(
                self, "Retrain Complete", "ML detectors retrained successfully."
            )
