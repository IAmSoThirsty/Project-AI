from PyQt6.QtWidgets import (  # type: ignore
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QDialogButtonBox,
    QCheckBox,
    QLineEdit,
    QGroupBox,
    QTabWidget,
    QWidget,
)

import json
import os

DATA_DIR = os.getenv('DATA_DIR', 'data')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')


class SettingsDialog(QDialog):
    def __init__(self, parent=None, current=None):
        super().__init__(parent)
        self.setWindowTitle('⚙️ Application Settings')
        self.setModal(True)
        self.setMinimumWidth(500)
        
        main_layout = QVBoxLayout(self)
        
        # Create tabbed interface for organized settings
        tabs = QTabWidget()
        
        # Tab 1: Appearance
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout(appearance_tab)
        
        # Theme Group
        theme_group = QGroupBox("🎨 Theme & Appearance")
        theme_layout = QVBoxLayout()
        
        theme_layout.addWidget(QLabel('Color Theme:'))
        self.theme_select = QComboBox()
        self.theme_select.addItems(['light', 'dark'])
        theme_layout.addWidget(self.theme_select)
        
        theme_layout.addWidget(QLabel('UI Font Size:'))
        size_layout = QHBoxLayout()
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 20)
        self.size_spin.setSuffix(' pt')
        size_layout.addWidget(self.size_spin)
        size_layout.addStretch()
        theme_layout.addLayout(size_layout)
        
        theme_group.setLayout(theme_layout)
        appearance_layout.addWidget(theme_group)
        
        # Window Group
        window_group = QGroupBox("🖥️ Window Settings")
        window_layout = QVBoxLayout()
        
        self.fullscreen_check = QCheckBox("Start in fullscreen mode")
        window_layout.addWidget(self.fullscreen_check)
        
        self.remember_size_check = QCheckBox("Remember window size and position")
        self.remember_size_check.setChecked(True)
        window_layout.addWidget(self.remember_size_check)
        
        window_group.setLayout(window_layout)
        appearance_layout.addWidget(window_group)
        
        appearance_layout.addStretch()
        tabs.addTab(appearance_tab, "Appearance")
        
        # Tab 2: API & Integration
        api_tab = QWidget()
        api_layout = QVBoxLayout(api_tab)
        
        api_group = QGroupBox("🔑 API Configuration")
        api_form = QVBoxLayout()
        
        api_form.addWidget(QLabel('Hugging Face API Token (optional):'))
        self.hf_token_input = QLineEdit()
        self.hf_token_input.setPlaceholderText("Leave empty for free tier")
        self.hf_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_form.addWidget(self.hf_token_input)
        
        api_form.addWidget(QLabel('OpenAI API Key (optional):'))
        self.openai_key_input = QLineEdit()
        self.openai_key_input.setPlaceholderText("For advanced chat features")
        self.openai_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        api_form.addWidget(self.openai_key_input)
        
        api_group.setLayout(api_form)
        api_layout.addWidget(api_group)
        
        api_layout.addStretch()
        tabs.addTab(api_tab, "API Keys")
        
        # Tab 3: Image Generation
        image_tab = QWidget()
        image_layout = QVBoxLayout(image_tab)
        
        image_group = QGroupBox("🎨 Image Generation Settings")
        image_form = QVBoxLayout()
        
        self.content_filter_check = QCheckBox("Enable content filtering (recommended)")
        self.content_filter_check.setChecked(True)
        self.content_filter_check.setToolTip("Blocks inappropriate prompts")
        image_form.addWidget(self.content_filter_check)
        
        self.auto_save_check = QCheckBox("Auto-save generated images")
        image_form.addWidget(self.auto_save_check)
        
        image_form.addWidget(QLabel('Default image save location:'))
        save_loc_layout = QHBoxLayout()
        self.save_location_input = QLineEdit()
        self.save_location_input.setPlaceholderText("./generated_images")
        save_loc_layout.addWidget(self.save_location_input)
        image_form.addLayout(save_loc_layout)
        
        image_group.setLayout(image_form)
        image_layout.addWidget(image_group)
        
        image_layout.addStretch()
        tabs.addTab(image_tab, "Image Gen")
        
        # Tab 4: Advanced
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        advanced_group = QGroupBox("⚙️ Advanced Settings")
        advanced_form = QVBoxLayout()
        
        self.debug_mode_check = QCheckBox("Enable debug mode")
        advanced_form.addWidget(self.debug_mode_check)
        
        self.auto_update_check = QCheckBox("Check for updates automatically")
        self.auto_update_check.setChecked(True)
        advanced_form.addWidget(self.auto_update_check)
        
        advanced_form.addWidget(QLabel('Request timeout (seconds):'))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 300)
        self.timeout_spin.setValue(60)
        self.timeout_spin.setSuffix(' sec')
        advanced_form.addWidget(self.timeout_spin)
        
        advanced_group.setLayout(advanced_form)
        advanced_layout.addWidget(advanced_group)
        
        advanced_layout.addStretch()
        tabs.addTab(advanced_tab, "Advanced")
        
        main_layout.addWidget(tabs)
        
        # Load current settings
        if current:
            self.theme_select.setCurrentText(current.get('theme', 'dark'))
            self.size_spin.setValue(current.get('ui_scale', 11))
            self.fullscreen_check.setChecked(current.get('fullscreen', False))
            self.remember_size_check.setChecked(current.get('remember_size', True))
            self.hf_token_input.setText(current.get('hf_token', ''))
            self.openai_key_input.setText(current.get('openai_key', ''))
            self.content_filter_check.setChecked(current.get('content_filter', True))
            self.auto_save_check.setChecked(current.get('auto_save_images', False))
            self.save_location_input.setText(current.get('save_location', './generated_images'))
            self.debug_mode_check.setChecked(current.get('debug_mode', False))
            self.auto_update_check.setChecked(current.get('auto_update', True))
            self.timeout_spin.setValue(current.get('request_timeout', 60))
        else:
            # Set defaults
            self.theme_select.setCurrentText('dark')
            self.size_spin.setValue(11)
            self.content_filter_check.setChecked(True)
            self.auto_update_check.setChecked(True)
        
        # Compose button flags on a separate line to keep line lengths short
        btns_flags = (
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        btns = QDialogButtonBox(btns_flags)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        main_layout.addWidget(btns)

    def get_values(self):
        return {
            'theme': self.theme_select.currentText(),
            'ui_scale': int(self.size_spin.value()),
            'fullscreen': self.fullscreen_check.isChecked(),
            'remember_size': self.remember_size_check.isChecked(),
            'hf_token': self.hf_token_input.text().strip(),
            'openai_key': self.openai_key_input.text().strip(),
            'content_filter': self.content_filter_check.isChecked(),
            'auto_save_images': self.auto_save_check.isChecked(),
            'save_location': self.save_location_input.text().strip() or './generated_images',
            'debug_mode': self.debug_mode_check.isChecked(),
            'auto_update': self.auto_update_check.isChecked(),
            'request_timeout': int(self.timeout_spin.value()),
        }

    @staticmethod
    def load_settings():
        try:
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR, exist_ok=True)
            if os.path.exists(SETTINGS_FILE):
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        # Enhanced defaults
        return {
            'theme': 'dark',
            'ui_scale': 11,
            'fullscreen': False,
            'remember_size': True,
            'hf_token': '',
            'openai_key': '',
            'content_filter': True,
            'auto_save_images': False,
            'save_location': './generated_images',
            'debug_mode': False,
            'auto_update': True,
            'request_timeout': 60,
        }

    @staticmethod
    def save_settings(settings: dict):
        try:
            if not os.path.exists(DATA_DIR):
                os.makedirs(DATA_DIR, exist_ok=True)
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception:
            return False
