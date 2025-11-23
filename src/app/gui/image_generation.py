"""Image generation tab for the AI Assistant dashboard."""

from datetime import datetime

from PyQt6.QtCore import Qt, QThread, pyqtSignal  # type: ignore
from PyQt6.QtGui import QImage, QPixmap  # type: ignore
from PyQt6.QtWidgets import (  # type: ignore
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.image_generator import ImageGenerator


class ImageGenerationThread(QThread):
    """Background thread for image generation to keep UI responsive."""
    
    finished = pyqtSignal(object)  # Emits PIL Image or None
    error = pyqtSignal(str)  # Emits error message
    
    def __init__(self, generator, prompt, negative_prompt=""):
        super().__init__()
        self.generator = generator
        self.prompt = prompt
        self.negative_prompt = negative_prompt
    
    def run(self):
        """Generate the image in background thread."""
        try:
            image = self.generator.generate_image(
                self.prompt,
                self.negative_prompt
            )
            self.finished.emit(image)
        except Exception as e:
            self.error.emit(str(e))


class ImageGenerationTab(QWidget):
    """Widget for AI image generation interface."""
    
    def __init__(self):
        super().__init__()
        self.generator = ImageGenerator()
        self.current_image = None
        self.generation_thread = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the image generation interface."""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title = QLabel("🎨 AI Image Generation")
        title.setStyleSheet("""
            font-size: 18pt;
            font-weight: bold;
            color: #5a8aca;
            padding: 10px;
        """)
        layout.addWidget(title)
        
        # Description
        desc = QLabel(
            "Generate stunning images from text descriptions using AI. "
            "Powered by Stable Diffusion (free Hugging Face API)."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #c8d8f0; font-size: 10pt; padding: 5px;")
        layout.addWidget(desc)
        
        # Style selector
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("Style Preset:"))
        self.style_combo = QComboBox()
        self.style_combo.addItem("None", "")
        for style_name in self.generator.get_style_presets().keys():
            self.style_combo.addItem(style_name, style_name)
        self.style_combo.setStyleSheet("font-size: 11pt; padding: 8px;")
        style_layout.addWidget(self.style_combo)
        style_layout.addStretch()
        layout.addLayout(style_layout)
        
        # Prompt input
        layout.addWidget(QLabel("Prompt (describe what you want to create):"))
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText(
            "Example: A majestic mountain landscape at sunset with snow-capped peaks"
        )
        self.prompt_input.setMaximumHeight(100)
        self.prompt_input.setStyleSheet("font-size: 11pt; padding: 8px;")
        layout.addWidget(self.prompt_input)
        
        # Negative prompt
        layout.addWidget(QLabel("Negative Prompt (what to avoid - optional):"))
        self.negative_input = QLineEdit()
        self.negative_input.setPlaceholderText(
            "Example: blurry, low quality, distorted"
        )
        self.negative_input.setStyleSheet("font-size: 11pt; padding: 8px;")
        layout.addWidget(self.negative_input)
        
        # Generate button
        button_layout = QHBoxLayout()
        self.generate_btn = QPushButton("🚀 Generate Image")
        self.generate_btn.clicked.connect(self.generate_image)
        self.generate_btn.setStyleSheet("""
            font-size: 13pt;
            padding: 12px;
            font-weight: bold;
        """)
        button_layout.addWidget(self.generate_btn)
        
        self.save_btn = QPushButton("💾 Save Image")
        self.save_btn.clicked.connect(self.save_image)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("font-size: 11pt; padding: 10px;")
        button_layout.addWidget(self.save_btn)
        
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #4a5a7a;
                border-radius: 5px;
                text-align: center;
                font-size: 10pt;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4a6a9a, stop:1 #5a8aca);
            }
        """)
        layout.addWidget(self.progress)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #8090a8; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Image display area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: 2px solid #2a3a5a;
                border-radius: 8px;
                background: #0f1419;
            }
        """)
        
        self.image_label = QLabel("Generated image will appear here")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            padding: 40px;
            color: #6070a0;
            font-size: 12pt;
            font-style: italic;
        """)
        self.image_label.setMinimumSize(512, 512)
        
        scroll.setWidget(self.image_label)
        layout.addWidget(scroll, 1)  # Takes remaining space
        
        self.setLayout(layout)
    
    def generate_image(self):
        """Start image generation process."""
        prompt = self.prompt_input.toPlainText().strip()
        
        if not prompt:
            QMessageBox.warning(
                self,
                "Empty Prompt",
                "Please enter a description of what you want to generate."
            )
            return
        
        # Add style preset if selected
        style = self.style_combo.currentText()
        if style != "None":
            style_modifier = self.generator.get_style_presets()[style]
            prompt = f"{prompt}, {style_modifier}"
        
        negative_prompt = self.negative_input.text().strip()
        
        # Disable UI during generation
        self.generate_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.progress.setVisible(True)
        self.status_label.setText("🎨 Generating image... This may take 20-60 seconds...")
        
        # Start generation in background thread
        self.generation_thread = ImageGenerationThread(
            self.generator,
            prompt,
            negative_prompt
        )
        self.generation_thread.finished.connect(self.on_generation_complete)
        self.generation_thread.error.connect(self.on_generation_error)
        self.generation_thread.start()
    
    def on_generation_complete(self, image):
        """Handle successful image generation."""
        self.progress.setVisible(False)
        self.generate_btn.setEnabled(True)
        
        if image:
            self.current_image = image
            self.display_image(image)
            self.save_btn.setEnabled(True)
            self.status_label.setText("✅ Image generated successfully!")
            self.status_label.setStyleSheet("color: #4ade80; font-style: italic;")
        else:
            self.status_label.setText("❌ Failed to generate image")
            self.status_label.setStyleSheet("color: #ff4757; font-style: italic;")
    
    def on_generation_error(self, error_msg):
        """Handle generation error."""
        self.progress.setVisible(False)
        self.generate_btn.setEnabled(True)
        self.status_label.setText(f"❌ Error: {error_msg}")
        self.status_label.setStyleSheet("color: #ff4757; font-style: italic;")
        
        if "loading" in error_msg.lower():
            QMessageBox.information(
                self,
                "Model Loading",
                "The AI model is loading. Please wait 20-30 seconds and try again.\n\n"
                "This is normal for the free Hugging Face API."
            )
    
    def display_image(self, pil_image):
        """Display the PIL image in the label."""
        # Convert PIL Image to QPixmap
        pil_image = pil_image.convert("RGB")
        data = pil_image.tobytes("raw", "RGB")
        qimage = QImage(
            data,
            pil_image.width,
            pil_image.height,
            pil_image.width * 3,
            QImage.Format.Format_RGB888
        )
        pixmap = QPixmap.fromImage(qimage)
        
        # Scale to fit while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.image_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)
    
    def save_image(self):
        """Save the current image to disk."""
        if not self.current_image:
            return
        
        # Generate default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"ai_generated_{timestamp}.png"
        
        # Open save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Generated Image",
            default_name,
            "PNG Image (*.png);;JPEG Image (*.jpg);;All Files (*.*)"
        )
        
        if file_path:
            try:
                self.current_image.save(file_path)
                self.status_label.setText(f"✅ Image saved to: {file_path}")
                self.status_label.setStyleSheet("color: #4ade80; font-style: italic;")
                QMessageBox.information(
                    self,
                    "Success",
                    f"Image saved successfully to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Save Error",
                    f"Failed to save image:\n{str(e)}"
                )
