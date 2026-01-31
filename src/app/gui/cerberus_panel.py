from __future__ import annotations

import logging
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.monitoring.cerberus_dashboard import get_metrics, record_incident

logger = logging.getLogger(__name__)

DATA_FILE = Path("data/monitoring/cerberus_incidents.json")


class CerberusPanel(QWidget):
    """Lightweight monitoring panel for Cerberus incidents.

    Shows recent incidents, attack counts, and provides controls to tag or release quarantined items.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cerberus - Monitoring")
        self.layout = QVBoxLayout(self)
        self._build_ui()
        self._refresh()
        # refresh periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh)
        self.timer.start(3000)

    def _build_ui(self) -> None:
        header = QLabel("Cerberus Incident Dashboard")
        self.layout.addWidget(header)

        self.metrics_label = QLabel("")
        self.layout.addWidget(self.metrics_label)

        self.incident_list = QListWidget()
        self.layout.addWidget(self.incident_list)

        btn_layout = QHBoxLayout()
        self.btn_tag = QPushButton("Tag Selected")
        self.btn_release = QPushButton("Release Selected")
        self.btn_refresh = QPushButton("Refresh Now")

        self.btn_tag.clicked.connect(self._tag_selected)
        self.btn_release.clicked.connect(self._release_selected)
        self.btn_refresh.clicked.connect(self._refresh)

        btn_layout.addWidget(self.btn_tag)
        btn_layout.addWidget(self.btn_release)
        btn_layout.addWidget(self.btn_refresh)
        self.layout.addLayout(btn_layout)

    def _refresh(self) -> None:
        data = get_metrics()
        incidents = data.get("incidents", [])
        counts = data.get("attack_counts", {})
        self.metrics_label.setText(
            f"Incidents: {len(incidents)}  |  Unique sources: {len(counts)}"
        )
        self.incident_list.clear()
        for inc in reversed(incidents[-100:]):
            item = QListWidgetItem(
                f"{inc.get('ts', 0)} - {inc.get('type')} - {inc.get('gate') or inc.get('source')}"
            )
            item.setData(32, inc)  # store dict
            self.incident_list.addItem(item)

    def _tag_selected(self) -> None:
        item = self.incident_list.currentItem()
        if not item:
            return
        inc = item.data(32)
        # open a simple tagging flow: append tag to incident and persist
        inc.setdefault("tags", []).append("manual_tag")
        record_incident({"type": "tag", "incident": inc})
        self._refresh()

    def _release_selected(self) -> None:
        item = self.incident_list.currentItem()
        if not item:
            return
        inc = item.data(32)
        # create a release action record (non-destructive)
        record_incident({"type": "release", "incident": inc})
        self._refresh()
