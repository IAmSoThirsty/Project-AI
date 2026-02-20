"""
Image Generation GUI with dual-page layout.

Left page (Tron): Prompt input and controls
Right page: Generated image display
"""

import logging

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.image_generator import ImageGenerationBackend, ImageGenerator, ImageStyle

logger = logging.getLogger(__name__)

# Tron color scheme
TRON_GREEN = "#00ff00"
TRON_CYAN = "#00ffff"
TRON_BLACK = "#0a0a0a"
TRON_DARK = "#1a1a1a"


class ImageGenerationWorker(QThread):
    """Worker thread for image generation to prevent UI blocking."""

    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)

    def __init__(self, generator: ImageGenerator, prompt: str, style: ImageStyle):
        """Initialize worker."""
        super().__init__()
        self.generator = generator
        self.prompt = prompt
        self.style = style

    def run(self):
        """Run generation in background."""
        try:
            self.progress.emit("Initializing generation...")
            result = self.generator.generate(self.prompt, self.style)
            self.finished.emit(result)
        except Exception as e:
            logger.error("Generation worker error: %s", e)
            self.finished.emit({"success": False, "error": str(e)})


class ImageGenerationLeftPanel(QFrame):
    """Left panel (Tron themed) for prompt input and controls."""

    generate_requested = pyqtSignal(str, str)  # prompt, style

    def __init__(self, parent=None):
        """Initialize left panel."""
        super().__init__(parent)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {TRON_BLACK};
                border-right: 2px solid {TRON_CYAN};
            }}
            QLabel {{
                color: {TRON_CYAN};
                font-size: 14pt;
            }}
            QTextEdit {{
                background-color: {TRON_DARK};
                color: {TRON_GREEN};
                border: 2px solid {TRON_CYAN};
                border-radius: 5px;
                padding: 10px;
                font-size: 12pt;
            }}
            QPushButton {{
                background-color: {TRON_DARK};
                color: {TRON_GREEN};
                border: 2px solid {TRON_GREEN};
                border-radius: 5px;
                padding: 12px;
                font-size: 12pt;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {TRON_GREEN};
                color: {TRON_BLACK};
            }}
            QPushButton:disabled {{
                background-color: #2a2a2a;
                color: #555555;
                border-color: #555555;
            }}
            QComboBox {{
                background-color: {TRON_DARK};
                color: {TRON_CYAN};
                border: 2px solid {TRON_CYAN};
                border-radius: 5px;
                padding: 8px;
                font-size: 11pt;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {TRON_CYAN};
            }}
        """
        )

        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("🎨 AI IMAGE GENERATOR")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {TRON_GREEN}; text-shadow: 0px 0px 20px {TRON_GREEN};")
        layout.addWidget(title)

        # Prompt input label
        prompt_label = QLabel("Enter Image Prompt:")
        layout.addWidget(prompt_label)

        # Prompt text area
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText(
            "Describe the image you want to generate...\n\n"
            "Example: A serene mountain landscape at sunset with reflection in a lake"
        )
        self.prompt_input.setMinimumHeight(150)
        layout.addWidget(self.prompt_input)

        # Style selector
        style_label = QLabel("Select Style Preset:")
        layout.addWidget(style_label)

        self.style_combo = QComboBox()
        for style in ImageStyle:
            self.style_combo.addItem(style.value.replace("_", " ").title(), style.value)
        layout.addWidget(self.style_combo)

        # Backend selector
        backend_label = QLabel("Generation Backend:")
        layout.addWidget(backend_label)

        self.backend_combo = QComboBox()
        self.backend_combo.addItem("Hugging Face (Stable Diffusion)", "huggingface")
        self.backend_combo.addItem("OpenAI (DALL-E 3)", "openai")
        layout.addWidget(self.backend_combo)

        # Generate button
        self.generate_btn = QPushButton("⚡ GENERATE IMAGE")
        self.generate_btn.clicked.connect(self._on_generate)
        self.generate_btn.setMinimumHeight(50)
        layout.addWidget(self.generate_btn)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"color: {TRON_CYAN}; font-size: 10pt;")
        layout.addWidget(self.status_label)

        # History button
        self.history_btn = QPushButton("📜 VIEW HISTORY")
        self.history_btn.setMinimumHeight(40)
        layout.addWidget(self.history_btn)

        # Spacer
        layout.addStretch()

        # Info label
        info_label = QLabel("⚠️ Content filtering enabled\n" "All images comply with safety guidelines")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet(f"color: {TRON_CYAN}; font-size: 9pt;")
        layout.addWidget(info_label)

    def _on_generate(self):
        """Handle generate button click."""
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            self.status_label.setText("⚠️ Please enter a prompt")
            return

        style = self.style_combo.currentData()

        self.generate_requested.emit(prompt, style)
        self.set_generating(True)

    def set_generating(self, generating: bool):
        """Set UI state for generation."""
        self.generate_btn.setEnabled(not generating)
        self.prompt_input.setEnabled(not generating)
        self.style_combo.setEnabled(not generating)
        self.backend_combo.setEnabled(not generating)

        if generating:
            self.status_label.setText("🔄 Generating...")
            self.status_label.setStyleSheet(f"color: {TRON_GREEN}; font-size: 10pt; font-weight: bold;")
        else:
            self.status_label.setText("Ready")
            self.status_label.setStyleSheet(f"color: {TRON_CYAN}; font-size: 10pt;")

    def set_status(self, message: str, is_error: bool = False):
        """Set status message."""
        color = "#ff4444" if is_error else TRON_GREEN
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 10pt;")


class ImageGenerationRightPanel(QFrame):
    """Right panel for displaying generated images."""

    def __init__(self, parent=None):
        """Initialize right panel."""
        super().__init__(parent)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #1a1a1a;
                border-left: 2px solid #00ffff;
            }
            QLabel {
                color: #00ffff;
            }
        """
        )

        self.setup_ui()

    def setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Title
        title = QLabel("Generated Image")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {TRON_CYAN};")
        layout.addWidget(title)

        # Scroll area for image
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background-color: #0f0f0f; border: none;")

        # Image container
        self.image_container = QWidget()
        image_layout = QVBoxLayout(self.image_container)

        # Image label
        self.image_label = QLabel("No image generated yet")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("color: #555555; font-size: 12pt; padding: 50px;")
        self.image_label.setMinimumSize(512, 512)
        image_layout.addWidget(self.image_label)

        scroll.setWidget(self.image_container)
        layout.addWidget(scroll)

        # Metadata label
        self.metadata_label = QLabel("")
        self.metadata_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.metadata_label.setStyleSheet(f"color: {TRON_CYAN}; font-size: 9pt;")
        self.metadata_label.setWordWrap(True)
        layout.addWidget(self.metadata_label)

        # Action buttons
        buttons_layout = QHBoxLayout()

        self.save_btn = QPushButton("💾 Save")
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {TRON_DARK};
                color: {TRON_CYAN};
                border: 2px solid {TRON_CYAN};
                border-radius: 5px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: {TRON_CYAN};
                color: {TRON_BLACK};
            }}
            QPushButton:disabled {{
                background-color: #2a2a2a;
                color: #555555;
                border-color: #555555;
            }}
        """
        )
        buttons_layout.addWidget(self.save_btn)

        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.setEnabled(False)
        self.copy_btn.setStyleSheet(self.save_btn.styleSheet())
        buttons_layout.addWidget(self.copy_btn)

        layout.addLayout(buttons_layout)

    def display_image(self, filepath: str, metadata: dict):
        """Display generated image."""
        try:
            pixmap = QPixmap(filepath)
            if pixmap.isNull():
                raise ValueError("Failed to load image")

            # Scale to fit while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                800,
                800,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

            self.image_label.setPixmap(scaled_pixmap)
            self.image_label.setStyleSheet("")

            # Update metadata
            prompt = metadata.get("prompt", "Unknown")
            timestamp = metadata.get("timestamp", "")
            self.metadata_label.setText(f"Prompt: {prompt[:100]}...\n" f"Generated: {timestamp}")

            # Enable buttons
            self.save_btn.setEnabled(True)
            self.copy_btn.setEnabled(True)

        except Exception as e:
            logger.error("Error displaying image: %s", e)
            self.show_error("Failed to display image")

    def show_error(self, message: str):
        """Show error message."""
        self.image_label.setText(f"❌ {message}")
        self.image_label.setStyleSheet("color: #ff4444; font-size: 12pt; padding: 50px;")
        self.metadata_label.setText("")
        self.save_btn.setEnabled(False)
        self.copy_btn.setEnabled(False)

    def show_generating(self):
        """Show generating state."""
        self.image_label.setText("⚡ Generating...\n\nThis may take 20-60 seconds")
        self.image_label.setStyleSheet(f"color: {TRON_GREEN}; font-size: 14pt; padding: 50px;")
        self.metadata_label.setText("")


class ImageGenerationInterface(QWidget):
    """Main image generation interface with dual-page layout."""

    def __init__(self, parent=None):
        """Initialize interface."""
        super().__init__(parent)
        self.generator = ImageGenerator(backend=ImageGenerationBackend.HUGGINGFACE)
        self.worker = None
        self.setup_ui()

    def setup_ui(self):
        """Setup UI."""
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Left panel (prompt input)
        self.left_panel = ImageGenerationLeftPanel()
        self.left_panel.generate_requested.connect(self._start_generation)
        layout.addWidget(self.left_panel, stretch=1)

        # Right panel (image display)
        self.right_panel = ImageGenerationRightPanel()
        layout.addWidget(self.right_panel, stretch=2)

    def _start_generation(self, prompt: str, style_value: str):
        """Start image generation."""
        try:
            # Convert style string to enum
            style = ImageStyle(style_value)

            # Show generating state
            self.right_panel.show_generating()

            # Create and start worker
            self.worker = ImageGenerationWorker(self.generator, prompt, style)
            self.worker.finished.connect(self._on_generation_complete)
            self.worker.progress.connect(self.left_panel.set_status)
            self.worker.start()

        except Exception as e:
            logger.error("Error starting generation: %s", e)
            self.left_panel.set_status(f"Error: {e}", is_error=True)
            self.left_panel.set_generating(False)

    def _on_generation_complete(self, result: dict):
        """Handle generation completion."""
        self.left_panel.set_generating(False)

        if result["success"]:
            self.left_panel.set_status("✅ Generation complete!")
            self.right_panel.display_image(result["filepath"], result)
        else:
            error_msg = result.get("error", "Unknown error")
            if result.get("filtered"):
                self.left_panel.set_status(f"🚫 Blocked: {error_msg}", is_error=True)
            else:
                self.left_panel.set_status(f"❌ Error: {error_msg}", is_error=True)
            self.right_panel.show_error(error_msg)
