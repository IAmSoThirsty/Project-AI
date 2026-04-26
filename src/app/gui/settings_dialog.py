import json
import os

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QSpinBox,
    QVBoxLayout,
)

DATA_DIR = os.getenv("DATA_DIR", "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")


class SettingsDialog(QDialog):
    def __init__(self, parent=None, current=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Theme:"))
        self.theme_select = QComboBox()
        self.theme_select.addItems(["light", "dark"])
        layout.addWidget(self.theme_select)

        layout.addWidget(QLabel("UI font size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 20)
        layout.addWidget(self.size_spin)

        if current:
            self.theme_select.setCurrentText(current.get("theme", "light"))
            self.size_spin.setValue(current.get("ui_scale", 10))
        else:
            self.theme_select.setCurrentText("light")
            self.size_spin.setValue(10)

        # Compose button flags on a separate line to keep line lengths short
        btns_flags = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns = QDialogButtonBox(btns_flags)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_values(self):
        return {
            "theme": self.theme_select.currentText(),
            "ui_scale": int(self.size_spin.value()),
        }

    @staticmethod
    def load_settings():
        try:
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR, exist_ok=True)
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            # Log the error instead of silently passing
            import logging

            logging.warning("Failed to load settings: %s", e)
        return {"theme": "light", "ui_scale": 10}

    @staticmethod
    def save_settings(settings: dict):
        try:
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR, exist_ok=True)
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            # Log the error
            import logging

            logging.error("Failed to save settings: %s", e)
            return False
