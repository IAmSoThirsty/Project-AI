"""
Image Generation UI Tab (Chapter 7)
Professional image generation interface with content filtering
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,  # type: ignore
                              QLineEdit, QTextEdit, QPushButton, QComboBox,
                              QProgressBar, QFileDialog, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal  # type: ignore
from PyQt6.QtGui import QPixmap  # type: ignore
from app.core.image_generator import ImageGenerator
import os


class ImageGenerationThread(QThread):
    """Thread for async image generation."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, generator, prompt, negative_prompt, style):
        super().__init__()
        self.generator = generator
        self.prompt = prompt
        self.negative_prompt = negative_prompt
        self.style = style
    
    def run(self):
        try:
            image = self.generator.generate_image(
                self.prompt,
                self.negative_prompt,
                self.style
            )
            self.finished.emit(image)
        except Exception as e:
            self.error.emit(str(e))


class ImageGenerationTab(QWidget):
    """Image generation UI tab."""
    
    def __init__(self):
        super().__init__()
        self.generator = ImageGenerator()
        self.current_image = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(" AI Image Generation")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Prompt input
        layout.addWidget(QLabel("Prompt:"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Describe the image you want to generate...")
        self.prompt_input.setMaximumHeight(100)
        layout.addWidget(self.prompt_input)
        
        # Negative prompt input
        layout.addWidget(QLabel("Negative Prompt (optional):"))
        self.negative_input = QLineEdit()
        self.negative_input.setPlaceholderText("Things to avoid in the image...")
        layout.addWidget(self.negative_input)
        
        # Style selector
        layout.addWidget(QLabel("Style:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(self.generator.get_available_styles())
        layout.addWidget(self.style_combo)
        
        # Generate button
        self.generate_btn = QPushButton(" Generate Image")
        self.generate_btn.clicked.connect(self._generate_image)
        layout.addWidget(self.generate_btn)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Image preview
        self.image_label = QLabel()
        self.image_label.setStyleSheet("border: 2px solid #444; background: #222;")
        self.image_label.setMinimumSize(512, 512)
        self.image_label.setScaledContents(True)
        layout.addWidget(self.image_label)
        
        # Save button
        self.save_btn = QPushButton(" Save Image")
        self.save_btn.clicked.connect(self._save_image)
        self.save_btn.setEnabled(False)
        layout.addWidget(self.save_btn)
        
        self.setLayout(layout)
    
    def _generate_image(self):
        """Generate an image."""
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Error", "Please enter a prompt")
            return
        
        self.generate_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # Indeterminate
        
        self.thread = ImageGenerationThread(
            self.generator,
            prompt,
            self.negative_input.text(),
            self.style_combo.currentText()
        )
        self.thread.finished.connect(self._on_image_generated)
        self.thread.error.connect(self._on_error)
        self.thread.start()
    
    def _on_image_generated(self, image):
        """Handle generated image."""
        self.progress.setVisible(False)
        self.generate_btn.setEnabled(True)
        
        if image:
            self.current_image = image
            # Convert PIL Image to QPixmap
            image.save("temp_image.png")
            pixmap = QPixmap("temp_image.png")
            self.image_label.setPixmap(pixmap)
            self.save_btn.setEnabled(True)
            os.remove("temp_image.png")
        else:
            QMessageBox.critical(self, "Error", "Failed to generate image")
    
    def _on_error(self, error_msg):
        """Handle error."""
        self.progress.setVisible(False)
        self.generate_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", error_msg)
    
    def _save_image(self):
        """Save the generated image."""
        if not self.current_image:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Image",
            "",
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        
        if file_path:
            try:
                self.current_image.save(file_path)
                QMessageBox.information(self, "Success", f"Image saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save image: {e}")