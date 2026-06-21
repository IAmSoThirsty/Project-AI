"""Project-AI read-only operator desktop window."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from project_ai_desktop.capability_inspector import (
    CapabilityInspectionError,
    inspect_capability,
)
from project_ai_desktop.client import DesktopGateway, DesktopGatewayError, Gateway
from project_ai_desktop.replay import run_replay_evidence_check
from project_ai_desktop.theme import STYLESHEET

GatewayFactory = Callable[[str, str, float], Gateway]


def _gateway_factory(url: str, token: str, timeout: float) -> DesktopGateway:
    return DesktopGateway(url, token=token, timeout=timeout)


class MainWindow(QMainWindow):
    PAGE_NAMES = ("Status", "Replay", "Audit", "Capability", "Governance", "Settings")

    def __init__(self, gateway_factory: GatewayFactory = _gateway_factory) -> None:
        super().__init__()
        self._gateway_factory = gateway_factory
        self._api_url = "http://127.0.0.1:8000"
        self._api_token = ""
        self._timeout = 10.0
        self.setWindowTitle("Project-AI Operator Desktop - 0.0.0.dev0")
        self.resize(1180, 760)
        self.setMinimumSize(900, 620)
        self.setStyleSheet(STYLESHEET)
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._build_ui()
        self._status_bar.showMessage("Development checkpoint - no governance authority")

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar)
        brand = QLabel("PAI  Project-AI")
        brand.setObjectName("brand")
        sidebar_layout.addWidget(brand)
        self.navigation = QListWidget()
        self.navigation.addItems(self.PAGE_NAMES)
        self.navigation.setCurrentRow(0)
        sidebar_layout.addWidget(self.navigation, 1)
        boundary = QLabel("READ-ONLY CLIENT\n0.0.0.dev0")
        boundary.setObjectName("muted")
        boundary.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(boundary)

        self.pages = QStackedWidget()
        self.pages.addWidget(self._status_page())
        self.pages.addWidget(self._replay_page())
        self.pages.addWidget(self._audit_page())
        self.pages.addWidget(self._capability_page())
        self.pages.addWidget(self._governance_page())
        self.pages.addWidget(self._settings_page())
        self.navigation.currentRowChanged.connect(self.pages.setCurrentIndex)

        layout.addWidget(sidebar)
        layout.addWidget(self.pages, 1)
        self.setCentralWidget(root)

    @staticmethod
    def _page(title: str, eyebrow: str) -> tuple[QWidget, QVBoxLayout]:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(18)
        eyebrow_label = QLabel(eyebrow)
        eyebrow_label.setObjectName("eyebrow")
        title_label = QLabel(title)
        title_label.setObjectName("title")
        layout.addWidget(eyebrow_label)
        layout.addWidget(title_label)
        return page, layout

    def _status_page(self) -> QWidget:
        page, layout = self._page("Gateway status", "LIVE / VERSION / REPLAY")
        self.status_summary = QLabel("Not checked")
        self.status_summary.setObjectName("muted")
        self.status_detail = QTextEdit()
        self.status_detail.setReadOnly(True)
        refresh = QPushButton("Refresh public status")
        refresh.clicked.connect(self.refresh_status)
        layout.addWidget(self.status_summary)
        layout.addWidget(self.status_detail, 1)
        layout.addWidget(refresh, 0, Qt.AlignmentFlag.AlignLeft)
        return page

    def _replay_page(self) -> QWidget:
        page, layout = self._page("Canonical replay evidence", "FIVE DETERMINISTIC DESKTOP CHECKS")
        note = QLabel(
            "This reads canonical replay status; it does not mutate or promote runtime state."
        )
        note.setObjectName("muted")
        self.replay_table = QTableWidget(0, 3)
        self.replay_table.setHorizontalHeaderLabels(("Check", "Result", "Detail"))
        replay_header = self.replay_table.horizontalHeader()
        if replay_header is not None:
            replay_header.setStretchLastSection(True)
        self.replay_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        run_button = QPushButton("Run replay evidence check")
        run_button.clicked.connect(self.run_replay)
        layout.addWidget(note)
        layout.addWidget(self.replay_table, 1)
        layout.addWidget(run_button, 0, Qt.AlignmentFlag.AlignLeft)
        return page

    def _audit_page(self) -> QWidget:
        page, layout = self._page("Chimera audit evidence", "VERIFIED APPEND-ONLY VIEW")
        controls = QHBoxLayout()
        self.audit_limit = QSpinBox()
        self.audit_limit.setRange(1, 500)
        self.audit_limit.setValue(100)
        load_button = QPushButton("Load authenticated evidence")
        load_button.clicked.connect(self.load_audit)
        controls.addWidget(QLabel("Limit"))
        controls.addWidget(self.audit_limit)
        controls.addWidget(load_button)
        controls.addStretch(1)
        self.audit_table = QTableWidget(0, 4)
        self.audit_table.setHorizontalHeaderLabels(("Event", "Subject", "Timestamp", "Hash"))
        audit_header = self.audit_table.horizontalHeader()
        if audit_header is not None:
            audit_header.setStretchLastSection(True)
        self.audit_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addLayout(controls)
        layout.addWidget(self.audit_table, 1)
        return page

    def _capability_page(self) -> QWidget:
        page, layout = self._page("Capability inspector", "DECODE ONLY / SIGNATURE UNVERIFIED")
        note = QLabel(
            "Claims are decoded locally. Only the issuing authority can verify the HMAC signature."
        )
        note.setObjectName("muted")
        self.capability_input = QTextEdit()
        self.capability_input.setPlaceholderText("Paste a capability token for local inspection")
        self.capability_output = QTextEdit()
        self.capability_output.setReadOnly(True)
        inspect_button = QPushButton("Inspect and clear token")
        inspect_button.clicked.connect(self.inspect_token)
        layout.addWidget(note)
        layout.addWidget(self.capability_input, 1)
        layout.addWidget(inspect_button, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.capability_output, 2)
        return page

    def _governance_page(self) -> QWidget:
        page, layout = self._page("Governance contract", "DISPLAY ONLY / NO AUTHORITY")
        for title, copy in (
            (
                "ALLOW",
                "Governance permits evaluation to continue to exact capability verification.",
            ),
            ("DENY", "Any unilateral veto or invalid invariant prevents execution."),
            ("ESCALATE", "The action remains unexecuted pending external review."),
        ):
            group = QGroupBox(title)
            group_layout = QVBoxLayout(group)
            group_layout.addWidget(QLabel(copy))
            layout.addWidget(group)
        warning = QLabel("Desktop, web, and mobile clients do not embed governance authority.")
        warning.setObjectName("muted")
        layout.addWidget(warning)
        layout.addStretch(1)
        return page

    def _settings_page(self) -> QWidget:
        page, layout = self._page("Connection settings", "TOKEN REMAINS IN MEMORY ONLY")
        form = QFormLayout()
        self.api_url_input = QLineEdit(self._api_url)
        self.api_token_input = QLineEdit()
        self.api_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_token_input.setPlaceholderText("Required only for audit evidence")
        self.timeout_input = QDoubleSpinBox()
        self.timeout_input.setRange(0.1, 300.0)
        self.timeout_input.setValue(self._timeout)
        self.timeout_input.setSuffix(" seconds")
        form.addRow("API URL", self.api_url_input)
        form.addRow("API token", self.api_token_input)
        form.addRow("Timeout", self.timeout_input)
        save = QPushButton("Apply in-memory settings")
        save.clicked.connect(self.apply_settings)
        layout.addLayout(form)
        layout.addWidget(save, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)
        return page

    def _gateway(self) -> Gateway:
        return self._gateway_factory(self._api_url, self._api_token, self._timeout)

    def refresh_status(self) -> None:
        try:
            gateway = self._gateway()
            health = gateway.health()
            replay = gateway.replay_status()
            self.status_summary.setText(
                f"Gateway {health.get('status')} / replay {replay.get('status')}"
            )
            self.status_detail.setPlainText(
                json.dumps({"health": health, "replay": replay}, indent=2)
            )
            self._status_bar.showMessage("Public status refreshed")
        except (DesktopGatewayError, OSError, ValueError) as error:
            self.status_summary.setText("Unavailable")
            self.status_detail.setPlainText(str(error))
            self._status_bar.showMessage("Public status refresh failed")

    def run_replay(self) -> None:
        self.replay_table.setRowCount(0)
        try:
            result = run_replay_evidence_check(self._gateway())
            for check in result.checks:
                row = self.replay_table.rowCount()
                self.replay_table.insertRow(row)
                self.replay_table.setItem(row, 0, QTableWidgetItem(check.name))
                self.replay_table.setItem(
                    row, 1, QTableWidgetItem("PASS" if check.passed else "FAIL")
                )
                self.replay_table.setItem(row, 2, QTableWidgetItem(check.detail))
            self._status_bar.showMessage(f"Replay evidence checks: {result.passed}/{result.total}")
        except (DesktopGatewayError, OSError, ValueError) as error:
            self._status_bar.showMessage(f"Replay evidence check failed: {error}")

    def load_audit(self) -> None:
        self.audit_table.setRowCount(0)
        try:
            response = self._gateway().audit(self.audit_limit.value())
            records = response.get("records")
            if not isinstance(records, list):
                raise DesktopGatewayError("Audit response records are invalid")
            for record in records:
                if not isinstance(record, dict):
                    continue
                row = self.audit_table.rowCount()
                self.audit_table.insertRow(row)
                subject = record.get("action_id") or record.get("canary_sha256") or "evidence"
                values = (record.get("event"), subject, record.get("timestamp"), record.get("hash"))
                for column, value in enumerate(values):
                    self.audit_table.setItem(row, column, QTableWidgetItem(str(value)))
            self._status_bar.showMessage(f"Verified audit entries: {self.audit_table.rowCount()}")
        except (DesktopGatewayError, OSError, ValueError) as error:
            self._status_bar.showMessage(f"Audit load failed: {error}")

    def inspect_token(self) -> None:
        token = self.capability_input.toPlainText()
        self.capability_input.clear()
        try:
            inspected = inspect_capability(token, now=datetime.now(UTC))
            self.capability_output.setPlainText(
                json.dumps(
                    {
                        "expires_at": inspected.expires_at,
                        "issued_at": inspected.issued_at,
                        "issuer": inspected.issuer,
                        "operation": inspected.operation,
                        "resource": inspected.resource,
                        "signature_status": inspected.signature_status,
                        "subject": inspected.subject,
                        "temporal_status": inspected.temporal_status,
                        "token_id": inspected.token_id,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
        except CapabilityInspectionError as error:
            self.capability_output.setPlainText(f"INVALID\n{error}")

    def apply_settings(self) -> None:
        try:
            candidate_url = self.api_url_input.text().strip()
            candidate_token = self.api_token_input.text()
            candidate_timeout = self.timeout_input.value()
            self._gateway_factory(candidate_url, candidate_token, candidate_timeout)
            self._api_url = candidate_url
            self._api_token = candidate_token
            self._timeout = candidate_timeout
            self.api_token_input.clear()
            self._status_bar.showMessage("In-memory settings applied; token was not persisted")
        except ValueError as error:
            self._status_bar.showMessage(f"Settings rejected: {error}")
