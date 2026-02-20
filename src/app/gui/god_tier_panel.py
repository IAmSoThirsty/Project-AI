"""
God-Tier Command Center Panel - GUI for unified system monitoring.

Displays comprehensive status of all systems:
- Global Watch Tower
- Intelligence Library
- 24/7 Monitoring System
- Resource usage and health metrics

Follows Leather Book Interface style with dark theme and cyan/green glows.
"""

import logging

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.god_tier_command_center import GodTierCommandCenter

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
STYLE_YELLOW_WARNING = "color: #ffaa00;"


class SystemHealthPanel(QFrame):
    """Panel showing overall system health."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("💚 SYSTEM HEALTH")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(STYLE_CYAN_GLOW)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Health metrics
        metrics_layout = QGridLayout()
        metrics_layout.setSpacing(10)

        # Create metric labels
        self.total_agents_label = self._create_metric_label("Total Agents", "0")
        self.active_agents_label = self._create_metric_label("Active Agents", "0")
        self.verifications_label = self._create_metric_label("Verifications", "0")
        self.incidents_label = self._create_metric_label("Incidents", "0")
        self.cache_hit_label = self._create_metric_label("Cache Hit", "0%")
        self.uptime_label = self._create_metric_label("Uptime", "0h")

        # Add to grid
        metrics_layout.addWidget(self.total_agents_label, 0, 0)
        metrics_layout.addWidget(self.active_agents_label, 0, 1)
        metrics_layout.addWidget(self.verifications_label, 1, 0)
        metrics_layout.addWidget(self.incidents_label, 1, 1)
        metrics_layout.addWidget(self.cache_hit_label, 2, 0)
        metrics_layout.addWidget(self.uptime_label, 2, 1)

        layout.addLayout(metrics_layout)

        # Refresh button
        refresh_btn = QPushButton("🔄 REFRESH")
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
        refresh_btn.clicked.connect(self.refresh_health)
        layout.addWidget(refresh_btn)

        # Initial load
        self.refresh_health()

    def _create_metric_label(self, name: str, value: str) -> QLabel:
        """Create a styled metric label."""
        label = QLabel(f"{name}:\n{value}")
        label.setStyleSheet(
            """
            QLabel {
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 11px;
                padding: 5px;
                border: 1px solid #004400;
                background-color: #0a0a0a;
                border-radius: 3px;
            }
        """
        )
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def refresh_health(self):
        """Refresh health metrics."""
        try:
            command_center = GodTierCommandCenter.get_instance()
            status = command_center.get_comprehensive_status()
            metrics = status.get("current_metrics", {})

            self.total_agents_label.setText(f"Total Agents:\n{metrics.get('total_agents', 0)}")
            self.active_agents_label.setText(f"Active Agents:\n{metrics.get('active_agents', 0)}")
            self.verifications_label.setText(f"Verifications:\n{metrics.get('watch_tower_verifications', 0)}")
            self.incidents_label.setText(f"Incidents:\n{metrics.get('watch_tower_incidents', 0)}")
            self.cache_hit_label.setText(f"Cache Hit:\n{metrics.get('cache_hit_rate', '0%')}")
            self.uptime_label.setText(f"Uptime:\n{status.get('uptime_formatted', '0h')}")

        except Exception as e:
            logger.error("Error refreshing health: %s", e)


class ComponentStatusPanel(QFrame):
    """Panel showing status of all components."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("🔧 COMPONENT STATUS")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(STYLE_CYAN_GLOW)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Component list
        self.status_label = QLabel("Loading component status...")
        self.status_label.setStyleSheet(
            """
            QLabel {
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 10px;
                padding: 10px;
            }
        """
        )
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Refresh button
        refresh_btn = QPushButton("🔄 REFRESH")
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
        refresh_btn.clicked.connect(self.refresh_components)
        layout.addWidget(refresh_btn)

        # Initial load
        self.refresh_components()

    def refresh_components(self):
        """Refresh component status."""
        try:
            command_center = GodTierCommandCenter.get_instance()
            status = command_center.get_comprehensive_status()
            components = status.get("components", {})

            output = []
            output.append("=" * 40)
            output.append("COMPONENT STATUS")
            output.append("=" * 40)

            for name, state in components.items():
                icon = "✓" if state == "operational" else "✗"
                output.append(f"{icon} {name.replace('_', ' ').title()}")

            output.append("=" * 40)

            self.status_label.setText("\n".join(output))

        except Exception as e:
            logger.error("Error refreshing components: %s", e)
            self.status_label.setText(f"ERROR: {str(e)}")


class IntelligenceAssessmentPanel(QFrame):
    """Panel showing latest intelligence assessment."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("📊 INTELLIGENCE ASSESSMENT")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(STYLE_CYAN_GLOW)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Assessment display
        self.assessment_display = QTextEdit()
        self.assessment_display.setReadOnly(True)
        self.assessment_display.setStyleSheet(
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
        layout.addWidget(self.assessment_display)

        # Control buttons
        btn_layout = QHBoxLayout()

        self.generate_btn = QPushButton("▶ GENERATE ASSESSMENT")
        self.generate_btn.setStyleSheet(
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
        self.generate_btn.clicked.connect(self.generate_assessment)
        btn_layout.addWidget(self.generate_btn)

        layout.addLayout(btn_layout)

        # Show initial message
        self.assessment_display.setText(
            "No assessment generated yet.\n\n"
            "Click 'GENERATE ASSESSMENT' to create a comprehensive "
            "intelligence analysis."
        )

    def generate_assessment(self):
        """Generate new intelligence assessment."""
        try:
            command_center = GodTierCommandCenter.get_instance()
            assessment = command_center.generate_intelligence_assessment()

            output = []
            output.append("=" * 60)
            output.append(f"ASSESSMENT ID: {assessment['assessment_id']}")
            output.append("=" * 60)
            output.append("")

            # Statistical simulation (from curator)
            sim = assessment.get("statistical_simulation", {})
            output.append("STATISTICAL SIMULATION (Curator):")
            output.append(f"  ID: {sim.get('simulation_id', 'N/A')}")
            output.append(f"  Summary: {sim.get('statistical_summary', 'N/A')}")
            output.append(f"  Confidence: {sim.get('confidence', 0):.2%}")
            output.append("")

            # Domain summaries
            output.append("DOMAIN SUMMARIES:")
            for domain, summary in assessment.get("domain_summaries", {}).items():
                output.append(f"  {domain.upper()}:")
                output.append(f"    Risk: {summary.get('risk_level', 'N/A')}")
                output.append(f"    Agents: {summary.get('agent_count', 0)}")
            output.append("")

            # Command assessment (from Watch Tower)
            output.append("COMMAND ASSESSMENT (Watch Tower):")
            output.append(f"  {assessment.get('command_assessment', 'N/A')}")
            output.append("")

            output.append(f"Watch Tower Alerts: {assessment.get('watch_tower_alerts', 0)}")
            output.append("")
            output.append(assessment.get("note", ""))
            output.append("=" * 60)

            self.assessment_display.setText("\n".join(output))

        except Exception as e:
            logger.error("Error generating assessment: %s", e)
            self.assessment_display.setText(f"ERROR: Failed to generate assessment\n\n{str(e)}")


class GodTierCommandPanel(QWidget):
    """Main panel for God-Tier Command Center.

    Displays:
    - Overall system health and metrics
    - Component status (all subsystems)
    - Intelligence assessments
    - Resource usage monitoring
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

        # Content area
        content_layout = QVBoxLayout()

        # Top row - Health and Component Status
        top_row = QHBoxLayout()
        self.health_panel = SystemHealthPanel()
        top_row.addWidget(self.health_panel)

        self.component_panel = ComponentStatusPanel()
        top_row.addWidget(self.component_panel)

        content_layout.addLayout(top_row, 1)

        # Bottom row - Intelligence Assessment
        self.assessment_panel = IntelligenceAssessmentPanel()
        content_layout.addWidget(self.assessment_panel, 2)

        main_layout.addLayout(content_layout)

        # Initialize command center if not already done
        self._initialize_command_center()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._auto_refresh)
        self.refresh_timer.start(20000)  # Refresh every 20 seconds

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
        title = QLabel("👑 GOD-TIER COMMAND CENTER")
        title.setFont(QFont("Courier New", 16, QFont.Weight.Bold))
        title.setStyleSheet(STYLE_CYAN_GLOW)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title, 1)

        # Status indicator
        status_label = QLabel("🟢 OPERATIONAL")
        status_label.setStyleSheet(STYLE_GREEN_TEXT)
        layout.addWidget(status_label)

        return title_frame

    def _initialize_command_center(self):
        """Initialize the command center if needed."""
        try:
            GodTierCommandCenter.get_instance()
            logger.info("Command center already initialized")
        except RuntimeError:
            # Command center not initialized yet
            try:
                GodTierCommandCenter.initialize(
                    data_dir="data/intelligence",
                    agents_per_domain=20,
                    monitoring_interval=60,
                )
                logger.info("Command center initialized successfully")
            except Exception as e:
                logger.error("Failed to initialize command center: %s", e)

    def _auto_refresh(self):
        """Auto-refresh panels."""
        self.health_panel.refresh_health()
        self.component_panel.refresh_components()
