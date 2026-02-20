from __future__ import annotations

import logging
import os

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.agents.expert_agent import ExpertAgent
from app.core.access_control import get_access_control
from app.core.ai_systems import LearningRequestManager
from app.core.council_hub import get_council_hub
from app.core.platform_tiers import (
    AuthorityLevel,
    ComponentRole,
    PlatformTier,
    get_tier_registry,
)
from app.plugins.codex_adapter import CodexAdapter

logger = logging.getLogger(__name__)


class DashboardMainWindow(QMainWindow):
    """A simple dashboard that integrates Persona, Learning Requests, Cerberus and Codex."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Project-AI Dashboard")
        self.resize(1000, 700)

        self.central = QTabWidget()
        self.setCentralWidget(self.central)

        # Managers and adapters
        self.lrm = LearningRequestManager(data_dir="data")
        self.codex_adapter = CodexAdapter()
        self.codex_adapter.register_with_manager(self.lrm)

        # Tabs
        self._init_requests_tab()
        self._init_cerberus_tab()
        self._init_codex_tab()
        self._init_logs_tab()
        self._init_waiting_tab()

        # Register with Tier Registry as Tier-3 User Interface
        try:
            tier_registry = get_tier_registry()
            tier_registry.register_component(
                component_id="dashboard_main",
                component_name="DashboardMainWindow",
                tier=PlatformTier.TIER_3_APPLICATION,
                authority_level=AuthorityLevel.SANDBOXED,
                role=ComponentRole.USER_INTERFACE,
                component_ref=self,
                dependencies=["cognition_kernel", "council_hub"],
                can_be_paused=True,  # Can be paused by Tier-1
                can_be_replaced=True,  # GUI is replaceable
            )
            logger.info("DashboardMainWindow registered as Tier-3 User Interface")
        except Exception as e:
            logger.warning("Failed to register DashboardMainWindow in tier registry: %s", e)

    def _init_requests_tab(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.pending_list = QListWidget()
        refresh_btn = QPushButton("Refresh Pending Requests")
        approve_btn = QPushButton("Approve Selected")
        deny_btn = QPushButton("Deny Selected")

        refresh_btn.clicked.connect(self.refresh_pending)
        approve_btn.clicked.connect(self.approve_selected)
        deny_btn.clicked.connect(self.deny_selected)

        layout.addWidget(QLabel("Pending Learning Requests:"))
        layout.addWidget(self.pending_list)

        btn_row = QHBoxLayout()
        btn_row.addWidget(refresh_btn)
        btn_row.addWidget(approve_btn)
        btn_row.addWidget(deny_btn)
        layout.addLayout(btn_row)

        self.central.addTab(widget, "Learning Requests")
        self.refresh_pending()

    def refresh_pending(self) -> None:
        self.pending_list.clear()
        for req in self.lrm.get_pending():
            display = f"{req.get('topic')} - {req.get('created')}"
            self.pending_list.addItem(display)

    def _selected_req_id(self) -> str | None:
        item = self.pending_list.currentItem()
        if not item:
            return None
        text = item.text()
        # naive matching by topic and created timestamp
        for k, v in self.lrm.requests.items():
            if v.get("topic") in text and v.get("created") in text:
                return k
        # fallback: first pending
        pend = self.lrm.get_pending()
        return pend[0] if pend else None

    def approve_selected(self) -> None:
        sel = self._selected_req_id()
        if not sel:
            QMessageBox.warning(self, "No Selection", "No request selected")
            return
        ok = self.lrm.approve_request(sel, response="Approved via Dashboard")
        if ok:
            QMessageBox.information(self, "Approved", f"Request {sel} approved")
            self.refresh_pending()
        else:
            QMessageBox.critical(self, "Error", "Failed to approve request")

    def deny_selected(self) -> None:
        sel = self._selected_req_id()
        if not sel:
            QMessageBox.warning(self, "No Selection", "No request selected")
            return
        ok = self.lrm.deny_request(sel, reason="Denied via Dashboard", to_vault=True)
        if ok:
            QMessageBox.information(self, "Denied", f"Request {sel} denied and vaulted")
            self.refresh_pending()
        else:
            QMessageBox.critical(self, "Error", "Failed to deny request")

    def _init_cerberus_tab(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.cerberus_status_label = QLabel("Cerberus status: not initialized")
        refresh_btn = QPushButton("Refresh Cerberus Status")
        refresh_btn.clicked.connect(self.refresh_cerberus)

        layout.addWidget(self.cerberus_status_label)
        layout.addWidget(refresh_btn)

        self.central.addTab(widget, "Cerberus")
        self.refresh_cerberus()

    def refresh_cerberus(self) -> None:
        try:
            from cerberus.hub import HubCoordinator

            hub = HubCoordinator()
            status = hub.get_status()
            self.cerberus_status_label.setText(
                f"Cerberus status: {status.get('hub_status')}, guardians: {status.get('guardian_count')}"
            )
        except Exception as e:
            self.cerberus_status_label.setText(f"Cerberus not available: {e}")

    def _init_codex_tab(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.codex_status = QLabel("Codex: initializing")
        run_fix_btn = QPushButton("Run repo auto-fix (conservative)")
        list_styles_btn = QPushButton("List Codex styles")

        run_fix_btn.clicked.connect(self.run_codex_fix)
        list_styles_btn.clicked.connect(self.show_codex_styles)

        layout.addWidget(self.codex_status)
        layout.addWidget(run_fix_btn)
        layout.addWidget(list_styles_btn)

        self.central.addTab(widget, "Codex (Head Butler)")

    def run_codex_fix(self) -> None:
        try:
            adapter = self.codex_adapter
            # Use codex instance
            codex = adapter.codex
            res = codex.fix_repo(root=os.getcwd())
            QMessageBox.information(
                self,
                "Codex Fix Report",
                f"Fixed: {len(res.get('fixed', []))}, Errors: {len(res.get('errors', []))}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Codex Error", str(e))

    def show_codex_styles(self) -> None:
        styles = self.codex_adapter.codex.list_styles()
        QMessageBox.information(self, "Codex Styles", "\n".join(styles))

    def _init_logs_tab(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.logs_view = QTextEdit()
        self.logs_view.setReadOnly(True)
        layout.addWidget(QLabel("Recent Audit Log (Codex)"))
        layout.addWidget(self.logs_view)

        refresh_btn = QPushButton("Refresh Audit Log")
        refresh_btn.clicked.connect(self.refresh_logs)
        layout.addWidget(refresh_btn)

        # Admin controls
        admin_row = QHBoxLayout()
        self.grant_btn = QPushButton("Grant Integrator Role to system")
        self.grant_btn.clicked.connect(self.grant_integrator)
        self.export_audit_btn = QPushButton("Export Audit (expert)")
        self.export_audit_btn.clicked.connect(self.export_audit)
        self.toggle_agents_btn = QPushButton("Toggle QA/Dependency Agents")
        self.toggle_agents_btn.clicked.connect(self.toggle_agents)
        admin_row.addWidget(self.grant_btn)
        admin_row.addWidget(self.export_audit_btn)
        admin_row.addWidget(self.toggle_agents_btn)
        layout.addLayout(admin_row)

        self.central.addTab(widget, "Logs")
        self.refresh_logs()

    def refresh_logs(self) -> None:
        try:
            import json

            path = "data/codex_audit.json"
            if not os.path.exists(path):
                self.logs_view.setPlainText("(no audit file yet)")
                return
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            pretty = json.dumps(data[-100:], indent=2)
            self.logs_view.setPlainText(pretty)
        except Exception as e:
            self.logs_view.setPlainText(str(e))

    def grant_integrator(self) -> None:
        ac = get_access_control()
        ac.grant_role("system", "integrator")
        QMessageBox.information(self, "Access Control", "Granted 'integrator' role to 'system'")

    def export_audit(self) -> None:
        expert = ExpertAgent(name="admin_expert")
        res = expert.export_and_review(self.codex_adapter.codex)
        if res.get("success"):
            QMessageBox.information(self, "Export", f"Audit exported to {res.get('out')}")
        else:
            QMessageBox.critical(self, "Export Failed", str(res))

    def _init_waiting_tab(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.waiting_list = QListWidget()
        refresh_btn = QPushButton("Refresh Waiting Room")
        activate_btn = QPushButton("Activate Selected")

        refresh_btn.clicked.connect(self.refresh_waiting)
        activate_btn.clicked.connect(self.activate_selected)

        layout.addWidget(QLabel("Staged Artifacts:"))
        layout.addWidget(self.waiting_list)
        btn_row = QHBoxLayout()
        btn_row.addWidget(refresh_btn)
        btn_row.addWidget(activate_btn)
        runqa_btn = QPushButton("Run QA Pipeline on Selected")
        runqa_btn.clicked.connect(self.run_qa_on_selected)
        btn_row.addWidget(runqa_btn)
        layout.addLayout(btn_row)

        self.central.addTab(widget, "Waiting Room")
        self.refresh_waiting()

    def refresh_waiting(self) -> None:
        self.waiting_list.clear()
        staged_dir = "data/waiting_room/staged"
        if not os.path.exists(staged_dir):
            return
        for fn in sorted(os.listdir(staged_dir)):
            self.waiting_list.addItem(fn)

    def activate_selected(self) -> None:
        item = self.waiting_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No selection", "No staged artifact selected")
            return
        staged_path = os.path.join("data/waiting_room/staged", item.text())
        # Attempt activation as 'system' (automatic integrator path)
        res = self.codex_adapter.codex.activate_staged(staged_path, requester="system")
        if res.get("success"):
            QMessageBox.information(self, "Activated", "Staged artifact activated and integrated")
            self.refresh_waiting()
        else:
            QMessageBox.critical(self, "Activation Failed", str(res))

    def run_qa_on_selected(self) -> None:
        item = self.waiting_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No selection", "No staged artifact selected")
            return
        staged_path = os.path.join("data/waiting_room/staged", item.text())
        try:
            # read staged metadata and run QA on archived path
            import json

            with open(staged_path, encoding="utf-8") as f:
                meta = json.load(f)
            archived = meta.get("archived")
            if not archived or not os.path.exists(archived):
                QMessageBox.critical(self, "QA Error", "Archived artifact missing")
                return
            hub = get_council_hub()
            project = getattr(hub, "_project", None)
            if not project:
                QMessageBox.critical(self, "QA Error", "No project agents available")
                return
            qa = project.get("qa_generator")
            dep = project.get("dependency_auditor")
            dep_res = dep.analyze_new_module(archived) if dep else {"success": True}
            qa_res = qa.generate_test_for_module(archived) if qa else {"success": True}
            if qa_res.get("success"):
                run_res = qa.run_tests()
            else:
                run_res = {"success": False, "detail": qa_res}

            QMessageBox.information(
                self,
                "QA Results",
                f"Dependency: {dep_res.get('success')}, Tests: {run_res.get('success')}",
            )
        except Exception as e:
            QMessageBox.critical(self, "QA Error", str(e))

    def toggle_agents(self) -> None:
        hub = get_council_hub()
        # flip qa/dependency enabled state
        current = hub._agents_enabled.get("qa_generator", True)
        hub._agents_enabled["qa_generator"] = not current
        hub._agents_enabled["dependency_auditor"] = not current
        QMessageBox.information(self, "Agents", f"QA/Dependency agents enabled: {not current}")
