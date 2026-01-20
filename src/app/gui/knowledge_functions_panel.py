"""
Knowledge Base and Function Registry UI Components

This module provides PyQt6 UI components for:
- Knowledge base search and browsing
- Function registry browser and help viewer
- Function invocation interface
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
                             QListWidget, QListWidgetItem, QPushButton, QTextEdit,
                             QVBoxLayout, QWidget)

# ============================================================================
# STYLE CONSTANTS
# ============================================================================

PANEL_STYLESHEET = """
    QFrame {
        background-color: #0f0f0f;
        border: 2px solid #00ff00;
        border-radius: 5px;
    }
"""

BUTTON_STYLESHEET = """
    QPushButton {
        background-color: #1a1a1a;
        border: 2px solid #00ff00;
        color: #00ff00;
        padding: 8px;
        font-weight: bold;
        font-size: 10px;
    }
    QPushButton:hover {
        border: 2px solid #00ffff;
        color: #00ffff;
    }
"""

INPUT_STYLESHEET = """
    QLineEdit {
        background-color: #1a1a1a;
        border: 2px solid #00ff00;
        color: #00ff00;
        padding: 5px;
        font-family: 'Courier New';
    }
"""

LIST_STYLESHEET = """
    QListWidget {
        background-color: #1a1a1a;
        border: 2px solid #00ff00;
        color: #00ff00;
        font-family: 'Courier New';
    }
    QListWidget::item:selected {
        background-color: #2a2a2a;
        border-left: 3px solid #00ffff;
    }
"""


# ============================================================================
# KNOWLEDGE BASE SEARCH PANEL
# ============================================================================


class KnowledgeSearchPanel(QFrame):
    """Panel for searching and browsing the knowledge base.

    Signals:
        search_requested: Emitted when user requests a search (str: query, str: category)
        category_requested: Emitted when user requests category info (str: category)
    """

    search_requested = pyqtSignal(str, str)  # query, category
    category_requested = pyqtSignal(str)  # category

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)
        self._build_ui()

    def _build_ui(self):
        """Build the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title = QLabel("📚 KNOWLEDGE BASE SEARCH")
        title.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff; text-shadow: 0px 0px 10px #00ffff;")
        layout.addWidget(title)

        # Search input
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search query...")
        self.search_input.setStyleSheet(INPUT_STYLESHEET)
        self.search_input.returnPressed.connect(self._on_search)
        search_layout.addWidget(self.search_input)

        search_btn = QPushButton("SEARCH")
        search_btn.setStyleSheet(BUTTON_STYLESHEET)
        search_btn.clicked.connect(self._on_search)
        search_layout.addWidget(search_btn)

        layout.addLayout(search_layout)

        # Category filter
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Category:")
        filter_label.setStyleSheet("color: #00ff00;")
        filter_layout.addWidget(filter_label)

        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                border: 2px solid #00ff00;
                color: #00ff00;
                padding: 5px;
            }
        """)
        self.category_combo.addItem("All Categories", "")
        filter_layout.addWidget(self.category_combo)

        layout.addLayout(filter_layout)

        # Results display
        results_label = QLabel("Search Results:")
        results_label.setStyleSheet("color: #00ff00; margin-top: 10px;")
        layout.addWidget(results_label)

        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                border: 2px solid #00ff00;
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 10px;
            }
        """)
        layout.addWidget(self.results_display)

    def _on_search(self):
        """Handle search button click."""
        query = self.search_input.text().strip()
        if query:
            category = self.category_combo.currentData()
            self.search_requested.emit(query, category)

    def update_categories(self, categories: list[str]):
        """Update the category dropdown with available categories.

        Args:
            categories: List of category names
        """
        self.category_combo.clear()
        self.category_combo.addItem("All Categories", "")
        for cat in categories:
            self.category_combo.addItem(cat, cat)

    def display_results(self, results: list[dict]):
        """Display search results.

        Args:
            results: List of result dictionaries with category, key, value
        """
        if not results:
            self.results_display.setPlainText("No results found.")
            return

        lines = [f"Found {len(results)} result(s):", ""]
        for i, result in enumerate(results, 1):
            category = result.get("category", "Unknown")
            key = result.get("key", "")
            value = result.get("value", "")
            match_type = result.get("match_type", "")

            lines.append(f"{i}. [{category}] {key}")
            lines.append(f"   Value: {value}")
            lines.append(f"   Match: {match_type}")
            lines.append("")

        self.results_display.setPlainText("\n".join(lines))


# ============================================================================
# FUNCTION REGISTRY BROWSER PANEL
# ============================================================================


class FunctionRegistryPanel(QFrame):
    """Panel for browsing and viewing function registry.

    Signals:
        function_selected: Emitted when user selects a function (str: function_name)
        function_call_requested: Emitted when user wants to call a function (str: function_name)
    """

    function_selected = pyqtSignal(str)  # function_name
    function_call_requested = pyqtSignal(str)  # function_name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)
        self._build_ui()

    def _build_ui(self):
        """Build the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        title = QLabel("🔧 FUNCTION REGISTRY")
        title.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff; text-shadow: 0px 0px 10px #00ffff;")
        layout.addWidget(title)

        # Category filter
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Category:")
        filter_label.setStyleSheet("color: #00ff00;")
        filter_layout.addWidget(filter_label)

        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1a1a;
                border: 2px solid #00ff00;
                color: #00ff00;
                padding: 5px;
            }
        """)
        self.category_combo.addItem("All Categories", "")
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        filter_layout.addWidget(self.category_combo)

        layout.addLayout(filter_layout)

        # Function list
        functions_label = QLabel("Available Functions:")
        functions_label.setStyleSheet("color: #00ff00;")
        layout.addWidget(functions_label)

        self.function_list = QListWidget()
        self.function_list.setStyleSheet(LIST_STYLESHEET)
        self.function_list.itemClicked.connect(self._on_function_clicked)
        layout.addWidget(self.function_list)

        # Function details
        details_label = QLabel("Function Details:")
        details_label.setStyleSheet("color: #00ff00; margin-top: 10px;")
        layout.addWidget(details_label)

        self.details_display = QTextEdit()
        self.details_display.setReadOnly(True)
        self.details_display.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                border: 2px solid #00ff00;
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 10px;
            }
        """)
        layout.addWidget(self.details_display)

        # Action button
        self.call_button = QPushButton("INVOKE FUNCTION")
        self.call_button.setStyleSheet(BUTTON_STYLESHEET)
        self.call_button.clicked.connect(self._on_call_clicked)
        self.call_button.setEnabled(False)
        layout.addWidget(self.call_button)

    def _on_category_changed(self):
        """Handle category change."""
        # Would trigger update in main application
        pass

    def _on_function_clicked(self, item):
        """Handle function selection."""
        function_name = item.data(Qt.ItemDataRole.UserRole)
        if function_name:
            self.function_selected.emit(function_name)
            self.call_button.setEnabled(True)

    def _on_call_clicked(self):
        """Handle call button click."""
        current_item = self.function_list.currentItem()
        if current_item:
            function_name = current_item.data(Qt.ItemDataRole.UserRole)
            if function_name:
                self.function_call_requested.emit(function_name)

    def update_categories(self, categories: list[str]):
        """Update the category dropdown.

        Args:
            categories: List of category names
        """
        self.category_combo.clear()
        self.category_combo.addItem("All Categories", "")
        for cat in categories:
            self.category_combo.addItem(cat, cat)

    def update_functions(self, functions: list[dict]):
        """Update the function list.

        Args:
            functions: List of function info dictionaries
        """
        self.function_list.clear()
        for func in functions:
            name = func.get("name", "")
            desc = func.get("description", "")[:50]
            func.get("category", "")

            item = QListWidgetItem(f"{name} - {desc}...")
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.function_list.addItem(item)

    def display_function_details(self, help_text: str):
        """Display function details.

        Args:
            help_text: Function help text
        """
        self.details_display.setPlainText(help_text)


# ============================================================================
# COMBINED KNOWLEDGE & FUNCTIONS WIDGET
# ============================================================================


class KnowledgeFunctionsWidget(QWidget):
    """Combined widget with knowledge search and function registry.

    This widget provides a tabbed or split view for both knowledge base
    search and function registry browsing.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        """Build the UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Left side: Knowledge search
        self.knowledge_panel = KnowledgeSearchPanel()
        layout.addWidget(self.knowledge_panel, 1)

        # Right side: Function registry
        self.function_panel = FunctionRegistryPanel()
        layout.addWidget(self.function_panel, 1)

        self.setStyleSheet("background-color: #0a0a0a;")
