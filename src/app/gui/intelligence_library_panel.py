"""
Intelligence Library Panel - GUI for Global Intelligence Library System.

Displays 120+ intelligence agents across 6 domains with real-time status,
domain overseer analyses, and curator statistical simulations.

Follows Leather Book Interface style with dark theme and cyan/green glows.
"""

import logging

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.global_intelligence_library import (
    GlobalIntelligenceLibrary,
    IntelligenceDomain,
)

logger = logging.getLogger(__name__)

# Style constants matching leather book interface
PANEL_STYLESHEET = """
    QFrame {
        background-color: #0f0f0f;
        border: 2px solid #00ff00;
        border-radius: 5px;
    }
"""

TITLE_FONT = QFont("Courier New", 12, QFont.Weight.Bold)
STYLE_CYAN_GLOW = "color: #00ffff; text-shadow: 0px 0px 10px #00ffff;"
STYLE_GREEN_TEXT = "color: #00ff00;"


class DomainAgentsPanel(QFrame):
    """Panel showing agents for a specific intelligence domain."""

    def __init__(self, domain: IntelligenceDomain, parent=None):
        super().__init__(parent)
        self.domain = domain
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel(f"📊 {domain.value.upper()} DOMAIN")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(STYLE_CYAN_GLOW)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Agent list
        self.agent_list = QListWidget()
        self.agent_list.setStyleSheet(
            """
            QListWidget {
                background-color: #1a1a1a;
                border: 1px solid #00ff00;
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 10px;
            }
            QListWidget::item:selected {
                background-color: #2a2a2a;
                color: #00ffff;
            }
        """
        )
        layout.addWidget(self.agent_list)

        # Status info
        self.status_label = QLabel("Status: Loading...")
        self.status_label.setStyleSheet(STYLE_GREEN_TEXT)
        layout.addWidget(self.status_label)

        # Refresh button
        refresh_btn = QPushButton("🔄 REFRESH AGENTS")
        refresh_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #1a1a1a;
                border: 2px solid #00ff00;
                color: #00ff00;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 2px solid #00ffff;
                color: #00ffff;
            }
        """
        )
        refresh_btn.clicked.connect(self.refresh_agents)
        layout.addWidget(refresh_btn)

    def refresh_agents(self):
        """Refresh agent list for this domain."""
        self.agent_list.clear()
        try:
            library = GlobalIntelligenceLibrary.get_instance()
            if not library.curator:
                self.status_label.setText("Status: Library not initialized")
                return

            overseer = library.curator.overseers.get(self.domain)
            if not overseer:
                self.status_label.setText("Status: No overseer for this domain")
                return

            # Display agents
            for i, agent in enumerate(overseer.agents, 1):
                status = agent.status.value
                specialty = agent.specialty
                item_text = f"Agent {i:02d}: {specialty} [{status}]"
                item = QListWidgetItem(item_text)
                self.agent_list.addItem(item)

            self.status_label.setText(f"Status: {len(overseer.agents)} agents active")

        except Exception as e:
            logger.error("Error refreshing agents: %s", e)
            self.status_label.setText(f"Status: Error - {e}")


class SimulationViewerPanel(QFrame):
    """Panel showing curator statistical simulations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("🎲 STATISTICAL SIMULATIONS")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(STYLE_CYAN_GLOW)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Simulation display
        self.simulation_display = QTextEdit()
        self.simulation_display.setReadOnly(True)
        self.simulation_display.setStyleSheet(
            """
            QTextEdit {
                background-color: #0a0a0a;
                border: 1px solid #00ff00;
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 10px;
            }
        """
        )
        layout.addWidget(self.simulation_display)

        # Control buttons
        btn_layout = QHBoxLayout()

        self.run_btn = QPushButton("▶ RUN SIMULATION")
        self.run_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #1a1a1a;
                border: 2px solid #00ff00;
                color: #00ff00;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 2px solid #00ffff;
                color: #00ffff;
            }
        """
        )
        self.run_btn.clicked.connect(self.run_simulation)
        btn_layout.addWidget(self.run_btn)

        self.refresh_btn = QPushButton("🔄 REFRESH")
        self.refresh_btn.setStyleSheet(self.run_btn.styleSheet())
        self.refresh_btn.clicked.connect(self.load_latest_simulation)
        btn_layout.addWidget(self.refresh_btn)

        layout.addLayout(btn_layout)

    def run_simulation(self):
        """Run a new statistical simulation."""
        try:
            library = GlobalIntelligenceLibrary.get_instance()
            simulation = library.generate_statistical_simulation()

            # Display simulation results
            output = []
            output.append("=" * 60)
            output.append(f"SIMULATION ID: {simulation.simulation_id}")
            output.append("=" * 60)
            output.append("")
            output.append(f"SUMMARY: {simulation.statistical_summary}")
            output.append("")
            output.append("PREDICTED OUTCOMES:")
            for i, outcome in enumerate(simulation.predicted_outcomes, 1):
                output.append(f"  {i}. {outcome}")
            output.append("")
            output.append(f"CONFIDENCE SCORE: {simulation.confidence_score:.2%}")
            output.append("")
            output.append("CROSS-DOMAIN PATTERNS:")
            for key, value in simulation.cross_domain_patterns.items():
                output.append(f"  - {key}: {value}")
            output.append("")
            output.append("NOTE: Curator provides statistical analysis only. ")
            output.append("All command decisions are made by Global Watch Tower.")
            output.append("=" * 60)

            self.simulation_display.setText("\n".join(output))

        except Exception as e:
            logger.error("Error running simulation: %s", e)
            self.simulation_display.setText(f"ERROR: Failed to run simulation\n\n{str(e)}")

    def load_latest_simulation(self):
        """Load the most recent simulation."""
        try:
            library = GlobalIntelligenceLibrary.get_instance()
            if library.curator and library.curator.last_theory:
                simulation = library.curator.last_theory
                output = []
                output.append("=" * 60)
                output.append(f"LATEST SIMULATION: {simulation.simulation_id}")
                output.append("=" * 60)
                output.append("")
                output.append(f"SUMMARY: {simulation.statistical_summary}")
                output.append("")
                output.append("PREDICTED OUTCOMES:")
                for i, outcome in enumerate(simulation.predicted_outcomes, 1):
                    output.append(f"  {i}. {outcome}")
                output.append("")
                output.append(f"CONFIDENCE: {simulation.confidence_score:.2%}")
                output.append("=" * 60)

                self.simulation_display.setText("\n".join(output))
            else:
                self.simulation_display.setText(
                    "No simulations available yet.\n\nClick 'RUN SIMULATION' to generate one."
                )

        except Exception as e:
            logger.error("Error loading simulation: %s", e)
            self.simulation_display.setText(f"ERROR: {str(e)}")


class IntelligenceLibraryPanel(QWidget):
    """Main panel for Intelligence Library System.

    Displays:
    - 6 intelligence domains with 20+ agents each
    - Domain overseer analyses
    - Curator statistical simulations
    - Real-time monitoring status
    """

    back_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #1a1a1a;
            }
        """
        )

        main_layout = QVBoxLayout(self)

        # Title bar
        title_bar = self._create_title_bar()
        main_layout.addWidget(title_bar)

        # Tab widget for different views
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            """
            QTabWidget::pane {
                border: 2px solid #00ff00;
                background-color: #1a1a1a;
            }
            QTabBar::tab {
                background-color: #0f0f0f;
                color: #00ff00;
                padding: 8px 16px;
                border: 2px solid #00ff00;
                border-bottom: none;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #1a1a1a;
                color: #00ffff;
                border-color: #00ffff;
            }
            QTabBar::tab:hover {
                color: #00ffff;
            }
        """
        )

        # Overview tab
        overview_tab = self._create_overview_tab()
        self.tabs.addTab(overview_tab, "📊 OVERVIEW")

        # Domain tabs
        for domain in IntelligenceDomain:
            domain_panel = DomainAgentsPanel(domain)
            icon = self._get_domain_icon(domain)
            self.tabs.addTab(domain_panel, f"{icon} {domain.value.upper()}")

        # Simulations tab
        sim_panel = SimulationViewerPanel()
        self.tabs.addTab(sim_panel, "🎲 SIMULATIONS")

        main_layout.addWidget(self.tabs)

        # Initialize library if not already done
        self._initialize_library()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._auto_refresh)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds

    def _create_title_bar(self) -> QFrame:
        """Create title bar with back button."""
        title_frame = QFrame()
        title_frame.setStyleSheet(
            """
            QFrame {
                background-color: #0f0f0f;
                border: 2px solid #00ff00;
                border-radius: 5px;
            }
        """
        )
        title_frame.setFixedHeight(60)

        layout = QHBoxLayout(title_frame)

        # Back button
        back_btn = QPushButton("◀ BACK")
        back_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #1a1a1a;
                border: 2px solid #00ff00;
                color: #00ff00;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 2px solid #00ffff;
                color: #00ffff;
            }
        """
        )
        back_btn.clicked.connect(self.back_requested.emit)
        layout.addWidget(back_btn)

        # Title
        title = QLabel("🗂️ GLOBAL INTELLIGENCE LIBRARY")
        title.setFont(QFont("Courier New", 16, QFont.Weight.Bold))
        title.setStyleSheet(STYLE_CYAN_GLOW)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title, 1)

        # Spacer for symmetry
        layout.addWidget(QLabel(), 0)
        layout.addWidget(QLabel(), 0)
        layout.addWidget(QLabel(), 0)

        return title_frame

    def _create_overview_tab(self) -> QWidget:
        """Create overview tab with library statistics."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Stats display
        stats_frame = QFrame()
        stats_frame.setStyleSheet(PANEL_STYLESHEET)
        stats_layout = QVBoxLayout(stats_frame)

        self.stats_label = QLabel("Loading statistics...")
        self.stats_label.setStyleSheet(
            """
            QLabel {
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 12px;
                padding: 10px;
            }
        """
        )
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)

        layout.addWidget(stats_frame)

        # Control buttons
        btn_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 REFRESH STATS")
        refresh_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #1a1a1a;
                border: 2px solid #00ff00;
                color: #00ff00;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 2px solid #00ffff;
                color: #00ffff;
            }
        """
        )
        refresh_btn.clicked.connect(self._refresh_overview)
        btn_layout.addWidget(refresh_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

        # Initial load
        self._refresh_overview()

        return widget

    def _refresh_overview(self):
        """Refresh overview statistics."""
        try:
            library = GlobalIntelligenceLibrary.get_instance()
            status = library.get_library_status()

            output = []
            output.append("=" * 60)
            output.append("GLOBAL INTELLIGENCE LIBRARY STATUS")
            output.append("=" * 60)
            output.append("")
            output.append(f"Initialized: {'✓ YES' if status.get('initialized') else '✗ NO'}")
            output.append("")

            if status.get("curator"):
                curator_status = status["curator"]
                output.append("CURATOR STATUS:")
                output.append(f"  - Domains Managed: {curator_status.get('overseer_count', 0)}")
                output.append(f"  - Simulations Run: {curator_status.get('theory_count', 0)}")
                output.append("  - Role: Librarian & Statistician (NO command authority)")
                output.append("")

            output.append("INTELLIGENCE DOMAINS:")
            for domain in IntelligenceDomain:
                output.append(f"  ✓ {domain.value.upper()}")
            output.append("")

            output.append(
                f"Watch Tower Integration: {'✓ ACTIVE' if status.get('watch_tower_integrated') else '✗ INACTIVE'}"
            )
            output.append(
                f"24/7 Monitoring: {'✓ ENABLED' if status.get('continuous_monitoring_enabled') else '✗ DISABLED'}"
            )
            output.append("")
            output.append("Note: All command authority rests with Global Watch Tower.")
            output.append("=" * 60)

            self.stats_label.setText("\n".join(output))

        except Exception as e:
            logger.error("Error refreshing overview: %s", e)
            self.stats_label.setText(f"ERROR: Failed to load statistics\n\n{str(e)}")

    def _initialize_library(self):
        """Initialize the intelligence library if needed."""
        try:
            GlobalIntelligenceLibrary.get_instance()
            logger.info("Intelligence library already initialized")
        except RuntimeError:
            # Library not initialized yet
            try:
                GlobalIntelligenceLibrary.initialize(
                    data_dir="data/intelligence",
                    agents_per_domain=20,
                    use_watch_tower=True,
                )
                logger.info("Intelligence library initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize library: %s", e)

    def _get_domain_icon(self, domain: IntelligenceDomain) -> str:
        """Get icon for a domain."""
        icons = {
            IntelligenceDomain.ECONOMIC: "💰",
            IntelligenceDomain.RELIGIOUS: "🕊️",
            IntelligenceDomain.POLITICAL: "🏛️",
            IntelligenceDomain.MILITARY: "⚔️",
            IntelligenceDomain.ENVIRONMENTAL: "🌍",
            IntelligenceDomain.TECHNOLOGICAL: "🔬",
        }
        return icons.get(domain, "📊")

    def _auto_refresh(self):
        """Auto-refresh current tab."""
        current_index = self.tabs.currentIndex()
        current_widget = self.tabs.widget(current_index)

        # Refresh based on tab type
        if current_index == 0:  # Overview tab
            self._refresh_overview()
        elif isinstance(current_widget, DomainAgentsPanel):
            current_widget.refresh_agents()
