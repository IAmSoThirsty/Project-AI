"""
Leather Book Interface - Main container with left/right page layout.

Creates an old leather book aesthetic with:
- Left page: Futuristic Tron-themed digital face
- Right page: User login, glossary, table of contents
- 3D elements with modern graphics
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QGraphicsDropShadowEffect, QHBoxLayout, QMainWindow,
                             QStackedWidget, QWidget)

from app.gui.leather_book_panels import IntroInfoPage, TronFacePage


class LeatherBookInterface(QMainWindow):
    """Main window with leather book aesthetic."""

    page_changed = pyqtSignal(int)  # Signal for page changes
    user_logged_in = pyqtSignal(str)  # Signal for user login

    def __init__(self, username: str | None = None):
        super().__init__()
        self.username = username
        self.backend_token: str | None = None
        self.current_page = 0  # 0 = login/intro, 1 = main dashboard

        self.setWindowTitle("Project-AI: Leather Book Interface")
        self.setGeometry(100, 100, 1920, 1080)
        self.setStyleSheet(self._get_stylesheet())

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.left_page = TronFacePage(self)
        self.right_page = IntroInfoPage(self)

        self.page_container = QStackedWidget()
        self.page_container.addWidget(self.right_page)

        self.main_layout.addWidget(self.left_page, 2)
        self.main_layout.addWidget(self.page_container, 3)

        self._apply_leather_texture()
        self.show()

    def _get_stylesheet(self) -> str:
        """Return QSS stylesheet for leather book theme."""
        return """
        QMainWindow {
            background-color: #1a1a1a;
        }
        QLabel {
            color: #e0e0e0;
        }
        QPushButton {
            background-color: #2a2a2a;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 8px;
            border-radius: 4px;
            font-weight: bold;
            text-shadow: 0px 0px 10px #00ff00;
        }
        QPushButton:hover {
            background-color: #3a3a3a;
            border: 2px solid #00ffff;
            color: #00ffff;
            text-shadow: 0px 0px 15px #00ffff;
        }
        QPushButton:pressed {
            background-color: #1a1a1a;
        }
        QLineEdit {
            background-color: #1a1a1a;
            border: 2px solid #00ff00;
            color: #00ff00;
            padding: 5px;
            font-weight: bold;
        }
        QLineEdit:focus {
            border: 2px solid #00ffff;
        }
        QTextEdit {
            background-color: #1a1a1a;
            border: 2px solid #00ff00;
            color: #00ff00;
        }
        """

    def _apply_leather_texture(self):
        """Apply leather texture and shadows."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 200))
        shadow.setOffset(0, 10)
        self.main_widget.setGraphicsEffect(shadow)

    def _set_stack_page(self, widget: QWidget, target_index: int):
        """Replace the widget at ``target_index`` and activate it."""
        while self.page_container.count() > target_index:
            old_widget = self.page_container.widget(target_index)
            if old_widget is None:
                break
            self.page_container.removeWidget(old_widget)
            old_widget.deleteLater()

        self.page_container.insertWidget(target_index, widget)
        self.page_container.setCurrentIndex(target_index)
        self.current_page = target_index

    def switch_to_main_dashboard(self, username: str):
        """Switch from intro page to main dashboard."""
        self.username = username
        self.user_logged_in.emit(username)

        from app.gui.leather_book_dashboard import LeatherBookDashboard

        dashboard = LeatherBookDashboard(username)
        
        # Connect existing signals
        dashboard.actions_panel.image_gen_requested.connect(
            self.switch_to_image_generation
        )
        
        # Connect new intelligence system signals
        dashboard.actions_panel.news_intelligence_requested.connect(
            self.switch_to_news_intelligence
        )
        dashboard.actions_panel.intelligence_library_requested.connect(
            self.switch_to_intelligence_library
        )
        dashboard.actions_panel.watch_tower_requested.connect(
            self.switch_to_watch_tower
        )
        dashboard.actions_panel.command_center_requested.connect(
            self.switch_to_command_center
        )

        self._set_stack_page(dashboard, 1)

    def set_backend_token(self, token: str | None):
        """Store backend auth token for downstream components."""
        self.backend_token = token

    def switch_to_image_generation(self):
        """Switch to image generation interface."""
        from app.gui.image_generation import ImageGenerationInterface

        image_gen = ImageGenerationInterface()

        self._set_stack_page(image_gen, 2)

    def switch_to_dashboard(self):
        """Switch back to dashboard."""
        if self.page_container.count() > 1:
            self.page_container.setCurrentIndex(1)
            self.current_page = 1

    def switch_to_news_intelligence(self):
        """Switch to news intelligence panel."""
        from app.gui.news_intelligence_panel import NewsIntelligencePanel

        news_panel = NewsIntelligencePanel()
        news_panel.back_requested.connect(self.switch_to_dashboard)

        self._set_stack_page(news_panel, 2)

    def switch_to_intelligence_library(self):
        """Switch to intelligence library panel."""
        from app.gui.intelligence_library_panel import IntelligenceLibraryPanel

        library_panel = IntelligenceLibraryPanel()
        library_panel.back_requested.connect(self.switch_to_dashboard)

        self._set_stack_page(library_panel, 2)

    def switch_to_watch_tower(self):
        """Switch to watch tower panel."""
        from app.gui.watch_tower_panel import WatchTowerPanel

        tower_panel = WatchTowerPanel()
        tower_panel.back_requested.connect(self.switch_to_dashboard)

        self._set_stack_page(tower_panel, 2)

    def switch_to_command_center(self):
        """Switch to god-tier command center panel."""
        from app.gui.god_tier_panel import GodTierCommandPanel

        command_panel = GodTierCommandPanel()
        command_panel.back_requested.connect(self.switch_to_dashboard)

        self._set_stack_page(command_panel, 2)
