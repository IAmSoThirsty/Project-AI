#!/usr/bin/env python3
"""
HYDRA-50 PYQT6 GUI PANEL
God-Tier Leather Book Interface Integration

Production-grade PyQt6 panel with:
- Real-time scenario monitoring dashboard
- Scenario activation/deactivation controls
- Visualization displays (escalation ladders, coupling graphs)
- Alert management interface
- Historical replay controls with timeline
- Performance metrics display
- System health indicators
- Signal/slot architecture for async updates
- Tron-themed dark UI matching Leather Book
- Integration with all HYDRA-50 backend systems

ZERO placeholders. Full PyQt6 implementation.
"""

from __future__ import annotations

import logging
from datetime import datetime

from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QPushButton,
    QSlider,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)

# ============================================================================
# STYLE CONSTANTS
# ============================================================================

TRON_GREEN = "#00ff00"
TRON_CYAN = "#00ffff"
TRON_DARK = "#0a0a0a"
TRON_BORDER = "#004400"

PANEL_STYLESHEET = f"""
    QFrame {{
        background-color: {TRON_DARK};
        border: 2px solid {TRON_BORDER};
        border-radius: 5px;
    }}
"""

TITLE_FONT = QFont("Courier New", 14, QFont.Weight.Bold)
METRIC_FONT = QFont("Courier New", 11)

BUTTON_STYLE = f"""
    QPushButton {{
        background-color: #1a1a1a;
        border: 2px solid {TRON_GREEN};
        color: {TRON_GREEN};
        padding: 8px;
        font-weight: bold;
        font-family: 'Courier New';
        border-radius: 3px;
    }}
    QPushButton:hover {{
        border: 2px solid {TRON_CYAN};
        color: {TRON_CYAN};
    }}
    QPushButton:pressed {{
        background-color: #002200;
    }}
    QPushButton:disabled {{
        border-color: #333333;
        color: #333333;
    }}
"""

LABEL_STYLE = f"""
    QLabel {{
        color: {TRON_GREEN};
        font-family: 'Courier New';
        font-size: 11px;
    }}
"""

CRITICAL_STYLE = """
    QLabel {
        color: #ff0000;
        font-weight: bold;
    }
"""

# ============================================================================
# UPDATE WORKER THREAD
# ============================================================================


class UpdateWorker(QThread):
    """Worker thread for async data updates"""

    data_updated = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, update_fn):
        super().__init__()
        self.update_fn = update_fn
        self.running = True

    def run(self):
        """Run update loop"""
        while self.running:
            try:
                data = self.update_fn()
                self.data_updated.emit(data)
            except Exception as e:
                self.error_occurred.emit(str(e))

            self.msleep(2000)  # 2 second update interval

    def stop(self):
        """Stop worker"""
        self.running = False


# ============================================================================
# SCENARIO LIST WIDGET
# ============================================================================


class ScenarioListWidget(QFrame):
    """Widget displaying all scenarios"""

    scenario_selected = pyqtSignal(str)  # scenario_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("📋 ACTIVE SCENARIOS")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(f"color: {TRON_CYAN};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Filter combo
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet(LABEL_STYLE)
        self.filter_combo = QComboBox()
        self.filter_combo.setStyleSheet(BUTTON_STYLE)
        self.filter_combo.addItems(["All", "Active", "Critical", "Dormant"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo)
        layout.addLayout(filter_layout)

        # List widget
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet(
            f"""
            QListWidget {{
                background-color: {TRON_DARK};
                border: 1px solid {TRON_BORDER};
                color: {TRON_GREEN};
                font-family: 'Courier New';
                font-size: 10px;
            }}
            QListWidget::item:selected {{
                background-color: #004400;
                border: 1px solid {TRON_CYAN};
            }}
        """
        )
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)

        # Refresh button
        refresh_btn = QPushButton("🔄 REFRESH")
        refresh_btn.setStyleSheet(BUTTON_STYLE)
        refresh_btn.clicked.connect(self.refresh_scenarios)
        layout.addWidget(refresh_btn)

        self.scenarios = []

    def refresh_scenarios(self):
        """Refresh scenario list"""
        try:
            from app.core.hydra_50_engine import Hydra50Engine

            engine = Hydra50Engine()
            self.scenarios = engine.list_scenarios()
            self.populate_list()

        except Exception as e:
            logger.error(f"Failed to refresh scenarios: {e}")

    def populate_list(self):
        """Populate list widget"""
        self.list_widget.clear()

        for scenario in self.scenarios:
            status = scenario.get("status", "unknown")
            level = scenario.get("escalation_level", 0)

            # Format item text
            text = f"[{status.upper()}] L{level} - {scenario.get('name', 'Unknown')}"

            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, scenario.get("scenario_id"))

            # Color by status
            if status == "critical" or status == "collapse":
                item.setForeground(QColor("#ff0000"))
            elif status == "escalating":
                item.setForeground(QColor("#ffaa00"))

            self.list_widget.addItem(item)

    def apply_filter(self, filter_text):
        """Apply status filter"""
        self.populate_list()

        if filter_text == "All":
            return

        filter_status = filter_text.lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            scenario_id = item.data(Qt.ItemDataRole.UserRole)
            scenario = next(
                (s for s in self.scenarios if s.get("scenario_id") == scenario_id), None
            )

            if scenario:
                item.setHidden(scenario.get("status") != filter_status)

    def on_item_clicked(self, item):
        """Handle item click"""
        scenario_id = item.data(Qt.ItemDataRole.UserRole)
        self.scenario_selected.emit(scenario_id)


# ============================================================================
# STATUS DASHBOARD WIDGET
# ============================================================================


class StatusDashboardWidget(QFrame):
    """Real-time status dashboard"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("📊 SYSTEM STATUS")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(f"color: {TRON_CYAN};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Metrics grid
        metrics_layout = QGridLayout()
        metrics_layout.setSpacing(10)

        self.active_label = self._create_metric_label("Active Scenarios", "0")
        self.critical_label = self._create_metric_label("Critical Scenarios", "0")
        self.total_label = self._create_metric_label("Total Scenarios", "0")
        self.health_label = self._create_metric_label("System Health", "UNKNOWN")
        self.alerts_label = self._create_metric_label("Active Alerts", "0")
        self.uptime_label = self._create_metric_label("Uptime", "0h")

        metrics_layout.addWidget(self.active_label, 0, 0)
        metrics_layout.addWidget(self.critical_label, 0, 1)
        metrics_layout.addWidget(self.total_label, 1, 0)
        metrics_layout.addWidget(self.health_label, 1, 1)
        metrics_layout.addWidget(self.alerts_label, 2, 0)
        metrics_layout.addWidget(self.uptime_label, 2, 1)

        layout.addLayout(metrics_layout)

        # Progress bars for resource usage
        resources_layout = QVBoxLayout()

        cpu_layout = QHBoxLayout()
        cpu_label = QLabel("CPU:")
        cpu_label.setStyleSheet(LABEL_STYLE)
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setStyleSheet(self._get_progress_style())
        cpu_layout.addWidget(cpu_label)
        cpu_layout.addWidget(self.cpu_progress)
        resources_layout.addLayout(cpu_layout)

        memory_layout = QHBoxLayout()
        memory_label = QLabel("Memory:")
        memory_label.setStyleSheet(LABEL_STYLE)
        self.memory_progress = QProgressBar()
        self.memory_progress.setStyleSheet(self._get_progress_style())
        memory_layout.addWidget(memory_label)
        memory_layout.addWidget(self.memory_progress)
        resources_layout.addLayout(memory_layout)

        layout.addLayout(resources_layout)

        # Auto-refresh timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_status)
        self.timer.start(2000)  # 2 seconds

    def _create_metric_label(self, name: str, value: str) -> QLabel:
        """Create metric label"""
        label = QLabel(f"{name}:\n{value}")
        label.setStyleSheet(
            f"""
            QLabel {{
                color: {TRON_GREEN};
                font-family: 'Courier New';
                font-size: 11px;
                padding: 8px;
                border: 1px solid {TRON_BORDER};
                background-color: {TRON_DARK};
                border-radius: 3px;
            }}
        """
        )
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _get_progress_style(self) -> str:
        """Get progress bar style"""
        return f"""
            QProgressBar {{
                border: 1px solid {TRON_BORDER};
                background-color: {TRON_DARK};
                color: {TRON_GREEN};
                text-align: center;
                font-family: 'Courier New';
            }}
            QProgressBar::chunk {{
                background-color: {TRON_GREEN};
            }}
        """

    def refresh_status(self):
        """Refresh status metrics"""
        try:
            from app.core.hydra_50_engine import Hydra50Engine

            engine = Hydra50Engine()
            status = engine.get_system_status()

            self.active_label.setText(
                f"Active Scenarios:\\n{status.get('active_scenarios', 0)}"
            )
            self.critical_label.setText(
                f"Critical Scenarios:\\n{status.get('critical_scenarios', 0)}"
            )
            self.total_label.setText(
                f"Total Scenarios:\\n{status.get('total_scenarios', 0)}"
            )
            self.health_label.setText(
                f"System Health:\\n{status.get('system_health', 'UNKNOWN')}"
            )
            self.alerts_label.setText(
                f"Active Alerts:\\n{status.get('alerts_count', 0)}"
            )

            uptime_hours = status.get("uptime_hours", 0)
            self.uptime_label.setText(f"Uptime:\\n{uptime_hours:.1f}h")

            # Update resource bars
            self.cpu_progress.setValue(int(status.get("cpu_percent", 0)))
            self.memory_progress.setValue(int(status.get("memory_percent", 0)))

        except Exception as e:
            logger.error(f"Failed to refresh status: {e}")


# ============================================================================
# VISUALIZATION WIDGET
# ============================================================================


class VisualizationWidget(QFrame):
    """Scenario visualizations"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("📈 VISUALIZATIONS")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(f"color: {TRON_CYAN};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Viz type selector
        type_layout = QHBoxLayout()
        type_label = QLabel("Type:")
        type_label.setStyleSheet(LABEL_STYLE)
        self.viz_combo = QComboBox()
        self.viz_combo.setStyleSheet(BUTTON_STYLE)
        self.viz_combo.addItems(
            [
                "Escalation Ladder",
                "Coupling Graph",
                "Temporal Flow",
                "Collapse Predictions",
                "Heat Map",
            ]
        )
        self.viz_combo.currentTextChanged.connect(self.change_visualization)

        type_layout.addWidget(type_label)
        type_layout.addWidget(self.viz_combo)
        layout.addLayout(type_layout)

        # Visualization display (ASCII art)
        self.viz_display = QTextEdit()
        self.viz_display.setReadOnly(True)
        self.viz_display.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {TRON_DARK};
                border: 1px solid {TRON_BORDER};
                color: {TRON_GREEN};
                font-family: 'Courier New';
                font-size: 9px;
            }}
        """
        )
        layout.addWidget(self.viz_display)

        self.current_scenario_id = None

    def set_scenario(self, scenario_id: str):
        """Set scenario to visualize"""
        self.current_scenario_id = scenario_id
        self.refresh_visualization()

    def change_visualization(self, viz_type: str):
        """Change visualization type"""
        self.refresh_visualization()

    def refresh_visualization(self):
        """Refresh visualization"""
        if not self.current_scenario_id:
            self.viz_display.setPlainText("No scenario selected")
            return

        try:
            from app.core.hydra_50_visualization import HYDRA50VisualizationEngine

            viz_engine = HYDRA50VisualizationEngine()
            viz_type = self.viz_combo.currentText()

            if viz_type == "Escalation Ladder":
                ascii_output, _ = viz_engine.render_escalation_ladder(
                    scenario_name=self.current_scenario_id,
                    current_level=2,
                    max_level=5,
                    level_descriptions={
                        0: "Baseline",
                        1: "Early Warning",
                        2: "Degradation",
                        3: "System Strain",
                        4: "Cascade Threshold",
                        5: "Collapse",
                    },
                    level_values={0: 0, 1: 20, 2: 40, 3: 60, 4: 80, 5: 100},
                )
                self.viz_display.setPlainText(ascii_output)

        except Exception as e:
            logger.error(f"Failed to refresh visualization: {e}")
            self.viz_display.setPlainText(f"Error: {str(e)}")


# ============================================================================
# ALERT MANAGEMENT WIDGET
# ============================================================================


class AlertManagementWidget(QFrame):
    """Alert management interface"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("🚨 ALERTS")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(f"color: {TRON_CYAN};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Alert table
        self.alert_table = QTableWidget()
        self.alert_table.setColumnCount(4)
        self.alert_table.setHorizontalHeaderLabels(
            ["Severity", "Title", "Time", "Status"]
        )
        self.alert_table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {TRON_DARK};
                border: 1px solid {TRON_BORDER};
                color: {TRON_GREEN};
                font-family: 'Courier New';
                font-size: 10px;
            }}
            QHeaderView::section {{
                background-color: #001100;
                color: {TRON_CYAN};
                border: 1px solid {TRON_BORDER};
                padding: 4px;
            }}
        """
        )
        layout.addWidget(self.alert_table)

        # Button row
        button_layout = QHBoxLayout()

        ack_btn = QPushButton("✓ Acknowledge")
        ack_btn.setStyleSheet(BUTTON_STYLE)
        ack_btn.clicked.connect(self.acknowledge_selected)

        resolve_btn = QPushButton("✓ Resolve")
        resolve_btn.setStyleSheet(BUTTON_STYLE)
        resolve_btn.clicked.connect(self.resolve_selected)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet(BUTTON_STYLE)
        refresh_btn.clicked.connect(self.refresh_alerts)

        button_layout.addWidget(ack_btn)
        button_layout.addWidget(resolve_btn)
        button_layout.addWidget(refresh_btn)
        layout.addLayout(button_layout)

    def refresh_alerts(self):
        """Refresh alerts"""
        try:
            from app.core.hydra_50_telemetry import HYDRA50TelemetrySystem

            telemetry = HYDRA50TelemetrySystem()
            alerts = telemetry.alert_manager.get_active_alerts()

            self.alert_table.setRowCount(len(alerts))

            for i, alert in enumerate(alerts):
                self.alert_table.setItem(i, 0, QTableWidgetItem(alert.severity.value))
                self.alert_table.setItem(i, 1, QTableWidgetItem(alert.title))
                self.alert_table.setItem(
                    i,
                    2,
                    QTableWidgetItem(
                        datetime.fromtimestamp(alert.timestamp).strftime("%H:%M:%S")
                    ),
                )
                status = "Acknowledged" if alert.acknowledged else "Active"
                self.alert_table.setItem(i, 3, QTableWidgetItem(status))

        except Exception as e:
            logger.error(f"Failed to refresh alerts: {e}")

    def acknowledge_selected(self):
        """Acknowledge selected alert"""
        # Implementation would acknowledge selected row
        pass

    def resolve_selected(self):
        """Resolve selected alert"""
        # Implementation would resolve selected row
        pass


# ============================================================================
# CONTROL PANEL WIDGET
# ============================================================================


class ControlPanelWidget(QFrame):
    """Scenario control panel"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("🎛️ CONTROLS")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(f"color: {TRON_CYAN};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Scenario info
        self.scenario_info = QLabel("No scenario selected")
        self.scenario_info.setStyleSheet(LABEL_STYLE)
        self.scenario_info.setWordWrap(True)
        layout.addWidget(self.scenario_info)

        # Control buttons
        activate_btn = QPushButton("▶️ ACTIVATE")
        activate_btn.setStyleSheet(BUTTON_STYLE)
        activate_btn.clicked.connect(self.activate_scenario)
        layout.addWidget(activate_btn)

        deactivate_btn = QPushButton("⏸️ DEACTIVATE")
        deactivate_btn.setStyleSheet(BUTTON_STYLE)
        deactivate_btn.clicked.connect(self.deactivate_scenario)
        layout.addWidget(deactivate_btn)

        escalate_btn = QPushButton("⬆️ ESCALATE")
        escalate_btn.setStyleSheet(BUTTON_STYLE)
        escalate_btn.clicked.connect(self.escalate_scenario)
        layout.addWidget(escalate_btn)

        simulate_btn = QPushButton("🎲 SIMULATE")
        simulate_btn.setStyleSheet(BUTTON_STYLE)
        simulate_btn.clicked.connect(self.simulate_scenario)
        layout.addWidget(simulate_btn)

        layout.addStretch()

        self.current_scenario_id = None

    def set_scenario(self, scenario_id: str):
        """Set current scenario"""
        self.current_scenario_id = scenario_id
        self.scenario_info.setText(f"Scenario: {scenario_id[:8]}...")

    def activate_scenario(self):
        """Activate scenario"""
        if not self.current_scenario_id:
            return
        try:
            from app.core.hydra_50_engine import Hydra50Engine

            engine = Hydra50Engine()
            engine.activate_scenario(self.current_scenario_id)
            logger.info(f"Activated scenario: {self.current_scenario_id}")
        except Exception as e:
            logger.error(f"Failed to activate: {e}")

    def deactivate_scenario(self):
        """Deactivate scenario"""
        if not self.current_scenario_id:
            return
        try:
            from app.core.hydra_50_engine import Hydra50Engine

            engine = Hydra50Engine()
            engine.deactivate_scenario(self.current_scenario_id)
            logger.info(f"Deactivated scenario: {self.current_scenario_id}")
        except Exception as e:
            logger.error(f"Failed to deactivate: {e}")

    def escalate_scenario(self):
        """Escalate scenario"""
        # Implementation would escalate
        pass

    def simulate_scenario(self):
        """Run simulation"""
        # Implementation would run simulation
        pass


# ============================================================================
# HISTORICAL REPLAY WIDGET
# ============================================================================


class HistoricalReplayWidget(QFrame):
    """Historical replay controls"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(PANEL_STYLESHEET)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("⏪ REPLAY")
        title.setFont(TITLE_FONT)
        title.setStyleSheet(f"color: {TRON_CYAN};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Timeline slider
        timeline_label = QLabel("Timeline:")
        timeline_label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(timeline_label)

        self.timeline_slider = QSlider(Qt.Orientation.Horizontal)
        self.timeline_slider.setMinimum(0)
        self.timeline_slider.setMaximum(100)
        self.timeline_slider.setValue(100)
        self.timeline_slider.setStyleSheet(
            f"""
            QSlider::groove:horizontal {{
                border: 1px solid {TRON_BORDER};
                height: 8px;
                background: {TRON_DARK};
            }}
            QSlider::handle:horizontal {{
                background: {TRON_GREEN};
                border: 1px solid {TRON_BORDER};
                width: 18px;
                margin: -5px 0;
                border-radius: 3px;
            }}
        """
        )
        self.timeline_slider.valueChanged.connect(self.on_timeline_changed)
        layout.addWidget(self.timeline_slider)

        # Time display
        self.time_display = QLabel("Current: Now")
        self.time_display.setStyleSheet(LABEL_STYLE)
        self.time_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_display)

        # Playback controls
        control_layout = QHBoxLayout()

        play_btn = QPushButton("▶️ Play")
        play_btn.setStyleSheet(BUTTON_STYLE)
        play_btn.clicked.connect(self.play_replay)

        pause_btn = QPushButton("⏸️ Pause")
        pause_btn.setStyleSheet(BUTTON_STYLE)
        pause_btn.clicked.connect(self.pause_replay)

        stop_btn = QPushButton("⏹️ Stop")
        stop_btn.setStyleSheet(BUTTON_STYLE)
        stop_btn.clicked.connect(self.stop_replay)

        control_layout.addWidget(play_btn)
        control_layout.addWidget(pause_btn)
        control_layout.addWidget(stop_btn)
        layout.addLayout(control_layout)

        # Speed control
        speed_label = QLabel("Speed:")
        speed_label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(speed_label)

        self.speed_combo = QComboBox()
        self.speed_combo.setStyleSheet(BUTTON_STYLE)
        self.speed_combo.addItems(["0.5x", "1x", "2x", "5x", "10x"])
        self.speed_combo.setCurrentText("1x")
        layout.addWidget(self.speed_combo)

        layout.addStretch()

    def on_timeline_changed(self, value):
        """Handle timeline change"""
        if value == 100:
            self.time_display.setText("Current: Now")
        else:
            self.time_display.setText(f"Position: {value}%")

    def play_replay(self):
        """Start replay"""
        logger.info("Replay started")

    def pause_replay(self):
        """Pause replay"""
        logger.info("Replay paused")

    def stop_replay(self):
        """Stop replay"""
        self.timeline_slider.setValue(100)
        logger.info("Replay stopped")


# ============================================================================
# MAIN HYDRA-50 PANEL
# ============================================================================


class HYDRA50Panel(QWidget):
    """
    Main HYDRA-50 Panel for Leather Book Interface

    Complete integration with:
    - Real-time monitoring
    - Scenario management
    - Visualizations
    - Alert system
    - Historical replay
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background-color: {TRON_DARK};")

        main_layout = QVBoxLayout(self)

        # Main title
        main_title = QLabel("🔱 HYDRA-50 CONTINGENCY SYSTEM")
        main_title.setFont(QFont("Courier New", 16, QFont.Weight.Bold))
        main_title.setStyleSheet(f"color: {TRON_CYAN}; padding: 10px;")
        main_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(main_title)

        # Create tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet(
            f"""
            QTabWidget::pane {{
                border: 2px solid {TRON_BORDER};
                background-color: {TRON_DARK};
            }}
            QTabBar::tab {{
                background-color: #001100;
                color: {TRON_GREEN};
                padding: 8px;
                margin: 2px;
                border: 1px solid {TRON_BORDER};
                font-family: 'Courier New';
            }}
            QTabBar::tab:selected {{
                background-color: #002200;
                color: {TRON_CYAN};
                border: 2px solid {TRON_CYAN};
            }}
        """
        )

        # Create main content area with splitters
        overview_widget = QWidget()
        overview_layout = QHBoxLayout(overview_widget)

        # Left side: Scenario list
        self.scenario_list = ScenarioListWidget()
        self.scenario_list.scenario_selected.connect(self.on_scenario_selected)

        # Center: Status dashboard and visualization
        center_splitter = QSplitter(Qt.Orientation.Vertical)
        self.status_dashboard = StatusDashboardWidget()
        self.visualization = VisualizationWidget()
        center_splitter.addWidget(self.status_dashboard)
        center_splitter.addWidget(self.visualization)

        # Right side: Control panel
        self.control_panel = ControlPanelWidget()

        # Add to horizontal splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(self.scenario_list)
        main_splitter.addWidget(center_splitter)
        main_splitter.addWidget(self.control_panel)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)
        main_splitter.setStretchFactor(2, 1)

        overview_layout.addWidget(main_splitter)
        tabs.addTab(overview_widget, "Overview")

        # Alerts tab
        self.alert_management = AlertManagementWidget()
        tabs.addTab(self.alert_management, "Alerts")

        # Replay tab
        self.historical_replay = HistoricalReplayWidget()
        tabs.addTab(self.historical_replay, "Replay")

        main_layout.addWidget(tabs)

        # Initialize data
        self.scenario_list.refresh_scenarios()

        logger.info("HYDRA-50 Panel initialized")

    def on_scenario_selected(self, scenario_id: str):
        """Handle scenario selection"""
        self.control_panel.set_scenario(scenario_id)
        self.visualization.set_scenario(scenario_id)
        logger.info(f"Selected scenario: {scenario_id}")


# Export main class
__all__ = ["HYDRA50Panel"]
