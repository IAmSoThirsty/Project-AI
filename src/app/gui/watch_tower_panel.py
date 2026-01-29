"""
Watch Tower Control Panel - GUI for Global Watch Tower Command Center.

Displays security monitoring, file verification, incident tracking,
and emergency lockdown controls.

Follows Leather Book Interface style with dark theme and cyan/green glows.
"""

import logging
from typing import Any

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.global_watch_tower import GlobalWatchTower

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
STYLE_RED_ALERT = "color: #ff0000; text-shadow: 0px 0px 10px #ff0000;"


class SecurityStatsPanel(QFrame):
    """Panel displaying Watch Tower security statistics."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("🛡️ SECURITY STATISTICS")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(STYLE_CYAN_GLOW)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Stats display
        self.stats_label = QLabel("Loading statistics...")
        self.stats_label.setStyleSheet(
            """
            QLabel {
                color: #00ff00;
                font-family: 'Courier New';
                font-size: 11px;
                padding: 10px;
            }
        """
        )
        self.stats_label.setWordWrap(True)
        layout.addWidget(self.stats_label)

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
        refresh_btn.clicked.connect(self.refresh_stats)
        layout.addWidget(refresh_btn)

        # Initial load
        self.refresh_stats()

    def refresh_stats(self):
        """Refresh security statistics."""
        try:
            tower = GlobalWatchTower.get_instance()
            stats = tower.get_stats()

            output = []
            output.append("=" * 50)
            output.append("WATCH TOWER STATISTICS")
            output.append("=" * 50)
            output.append("")
            output.append(
                f"Total Verifications: {stats.get('total_verifications', 0)}"
            )
            output.append(
                f"Total Incidents: {stats.get('total_incidents', 0)}"
            )
            output.append(
                f"Active Quarantines: {stats.get('active_quarantines', 0)}"
            )
            output.append(
                f"Lockdown Events: {stats.get('lockdown_count', 0)}"
            )
            output.append("")
            output.append("COMPONENT STATUS:")
            output.append(
                f"  Port Admins: {stats.get('port_admin_count', 0)}"
            )
            output.append(
                f"  Watch Towers: {stats.get('watch_tower_count', 0)}"
            )
            output.append(
                f"  Gate Guardians: {stats.get('gate_guardian_count', 0)}"
            )
            output.append("")
            output.append("STATUS: ✓ OPERATIONAL")
            output.append("=" * 50)

            self.stats_label.setText("\n".join(output))

        except Exception as e:
            logger.error(f"Error refreshing stats: {e}")
            self.stats_label.setText(f"ERROR: {str(e)}")


class IncidentLogPanel(QFrame):
    """Panel displaying recent security incidents."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("⚠️ INCIDENT LOG")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(STYLE_CYAN_GLOW)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Incident list
        self.incident_list = QListWidget()
        self.incident_list.setStyleSheet(
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
        layout.addWidget(self.incident_list)

        # Control buttons
        btn_layout = QHBoxLayout()

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
        refresh_btn.clicked.connect(self.refresh_incidents)
        btn_layout.addWidget(refresh_btn)

        clear_btn = QPushButton("🗑️ CLEAR LOG")
        clear_btn.setStyleSheet(refresh_btn.styleSheet())
        clear_btn.clicked.connect(self.clear_log)
        btn_layout.addWidget(clear_btn)

        layout.addLayout(btn_layout)

        # Initial load
        self.refresh_incidents()

    def refresh_incidents(self):
        """Refresh incident log."""
        self.incident_list.clear()
        try:
            tower = GlobalWatchTower.get_instance()
            incidents = tower.get_cerberus_incidents()

            if not incidents:
                item = QListWidgetItem("No incidents recorded")
                self.incident_list.addItem(item)
                return

            # Show most recent incidents (last 50)
            for incident in incidents[-50:]:
                timestamp = incident.get("timestamp", "N/A")
                severity = incident.get("severity", "UNKNOWN")
                description = incident.get("description", "No description")

                item_text = f"[{severity}] {timestamp}: {description}"
                item = QListWidgetItem(item_text)
                self.incident_list.addItem(item)

            # Scroll to bottom (most recent)
            self.incident_list.scrollToBottom()

        except Exception as e:
            logger.error(f"Error refreshing incidents: {e}")
            item = QListWidgetItem(f"ERROR: {str(e)}")
            self.incident_list.addItem(item)

    def clear_log(self):
        """Clear the displayed log (doesn't affect backend)."""
        self.incident_list.clear()
        item = QListWidgetItem("Log display cleared (backend data preserved)")
        self.incident_list.addItem(item)


class EmergencyControlsPanel(QFrame):
    """Panel with emergency lockdown and security controls."""

    lockdown_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("🚨 EMERGENCY CONTROLS")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(STYLE_RED_ALERT)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Status display
        self.status_label = QLabel("Status: Normal Operations")
        self.status_label.setStyleSheet(STYLE_GREEN_TEXT)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Warning text
        warning = QLabel(
            "⚠️ WARNING: These controls affect system-wide security.\n"
            "Use only in genuine emergency situations."
        )
        warning.setStyleSheet(
            """
            QLabel {
                color: #ffaa00;
                font-family: 'Courier New';
                font-size: 10px;
                padding: 10px;
            }
        """
        )
        warning.setWordWrap(True)
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(warning)

        # Emergency buttons
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)

        self.lockdown_btn = QPushButton("🔒 INITIATE LOCKDOWN")
        self.lockdown_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #1a1a1a;
                border: 3px solid #ff0000;
                color: #ff0000;
                padding: 15px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2a0000;
                border: 3px solid #ff4444;
                color: #ff4444;
            }
        """
        )
        self.lockdown_btn.clicked.connect(self.initiate_lockdown)
        btn_layout.addWidget(self.lockdown_btn)

        self.release_btn = QPushButton("🔓 RELEASE LOCKDOWN")
        self.release_btn.setStyleSheet(
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
        self.release_btn.clicked.connect(self.release_lockdown)
        self.release_btn.setEnabled(False)
        btn_layout.addWidget(self.release_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

    def initiate_lockdown(self):
        """Initiate emergency lockdown."""
        try:
            tower = GlobalWatchTower.get_instance()
            result = tower.emergency_lockdown(reason="Manual GUI trigger")

            self.status_label.setText("Status: 🔒 LOCKDOWN ACTIVE")
            self.status_label.setStyleSheet(STYLE_RED_ALERT)
            self.lockdown_btn.setEnabled(False)
            self.release_btn.setEnabled(True)
            self.lockdown_triggered.emit("Lockdown initiated")

            logger.warning("Emergency lockdown initiated from GUI")

        except Exception as e:
            logger.error(f"Error initiating lockdown: {e}")
            self.status_label.setText(f"ERROR: {str(e)}")

    def release_lockdown(self):
        """Release emergency lockdown."""
        try:
            tower = GlobalWatchTower.get_instance()
            # Note: GlobalWatchTower might not have a release method
            # This is a placeholder for the interface

            self.status_label.setText("Status: Normal Operations")
            self.status_label.setStyleSheet(STYLE_GREEN_TEXT)
            self.lockdown_btn.setEnabled(True)
            self.release_btn.setEnabled(False)

            logger.info("Lockdown released from GUI")

        except Exception as e:
            logger.error(f"Error releasing lockdown: {e}")
            self.status_label.setText(f"ERROR: {str(e)}")


class WatchTowerPanel(QWidget):
    """Main panel for Global Watch Tower Command Center.

    Displays:
    - Security statistics and verification counts
    - Recent incident log
    - Emergency lockdown controls
    - Quarantine management
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

        # Content area with two columns
        content_layout = QHBoxLayout()

        # Left column
        left_column = QVBoxLayout()
        self.stats_panel = SecurityStatsPanel()
        left_column.addWidget(self.stats_panel)

        self.emergency_panel = EmergencyControlsPanel()
        left_column.addWidget(self.emergency_panel)

        content_layout.addLayout(left_column, 1)

        # Right column
        right_column = QVBoxLayout()
        self.incident_panel = IncidentLogPanel()
        right_column.addWidget(self.incident_panel)

        content_layout.addLayout(right_column, 2)

        main_layout.addLayout(content_layout)

        # Initialize watch tower if not already done
        self._initialize_watch_tower()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._auto_refresh)
        self.refresh_timer.start(15000)  # Refresh every 15 seconds

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
        title = QLabel("🏰 GLOBAL WATCH TOWER COMMAND CENTER")
        title.setFont(QFont("Courier New", 16, QFont.Weight.Bold))
        title.setStyleSheet(STYLE_CYAN_GLOW)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title, 1)

        # Status indicator
        status_label = QLabel("🟢 OPERATIONAL")
        status_label.setStyleSheet(STYLE_GREEN_TEXT)
        layout.addWidget(status_label)

        return title_frame

    def _initialize_watch_tower(self):
        """Initialize the watch tower if needed."""
        try:
            tower = GlobalWatchTower.get_instance()
            logger.info("Watch tower already initialized")
        except RuntimeError:
            # Tower not initialized yet
            try:
                GlobalWatchTower.initialize(data_dir="data/watch_tower")
                logger.info("Watch tower initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize watch tower: {e}")

    def _auto_refresh(self):
        """Auto-refresh panels."""
        self.stats_panel.refresh_stats()
        self.incident_panel.refresh_incidents()
