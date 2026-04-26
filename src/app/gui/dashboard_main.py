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
        
        # Governance adapter (injected from main.py)
        self.desktop_adapter = None

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
            logger.warning(
                "Failed to register DashboardMainWindow in tier registry: %s", e
            )

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
        """Approve the selected learning request."""
        sel = self._selected_req_id()
        if not sel:
            QMessageBox.warning(self, "No Selection", "No request selected")
            return
        
        # MANDATORY governance routing - no fallback
        if not self.desktop_adapter:
            QMessageBox.critical(
                self, 
                "Governance Error", 
                "Desktop governance adapter not initialized. Cannot execute governed action."
            )
            return
        
        response = self._route_through_governance(
            "learning.approve",
            {
                "request_id": sel,
                "response": "Approved via Dashboard"
            }
        )
        
        if response.get("status") == "success":
            QMessageBox.information(self, "Approved", f"Request {sel} approved")
            self.refresh_pending()
        else:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to approve request: {response.get('error', 'Unknown error')}"
            )

    def deny_selected(self) -> None:
        """Deny the selected learning request (send to Black Vault)."""
        sel = self._selected_req_id()
        if not sel:
            QMessageBox.warning(self, "No Selection", "No request selected")
            return
        
        # MANDATORY governance routing - no fallback
        if not self.desktop_adapter:
            QMessageBox.critical(
                self, 
                "Governance Error", 
                "Desktop governance adapter not initialized. Cannot execute governed action."
            )
            return
        
        response = self._route_through_governance(
            "learning.deny",
            {
                "request_id": sel,
                "reason": "Denied via Dashboard",
                "to_vault": True
            }
        )
        
        if response.get("status") == "success":
            QMessageBox.information(self, "Denied", f"Request {sel} denied and vaulted")
            self.refresh_pending()
        else:
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to deny request: {response.get('error', 'Unknown error')}"
            )

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
        # MANDATORY governance routing - no fallback
        if not self.desktop_adapter:
            QMessageBox.critical(
                self, 
                "Governance Error", 
                "Desktop governance adapter not initialized. Cannot execute governed action."
            )
            return
        
        # Route through governance pipeline
        response = self._route_through_governance(
            "codex.fix",
            {
                "root": os.getcwd()
            }
        )
        
        if response.get("status") == "success":
            result = response.get("result", {})
            QMessageBox.information(
                self,
                "Codex Fix Report",
                f"Fixed: {len(result.get('fixed', []))}, Errors: {len(result.get('errors', []))}",
            )
        else:
            QMessageBox.critical(self, "Codex Error", response.get("error", "Unknown error"))

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
        """Grant integrator role to system user."""
        # MANDATORY governance routing - no fallback
        if not self.desktop_adapter:
            QMessageBox.critical(
                self, 
                "Governance Error", 
                "Desktop governance adapter not initialized. Cannot execute governed action."
            )
            return
        
        # Route through governance pipeline
        response = self._route_through_governance(
            "access.grant",
            {
                "username": "system",
                "role": "integrator"
            }
        )
        
        if response.get("status") == "success":
            QMessageBox.information(
                self, "Access Control", "Granted 'integrator' role to 'system'"
            )
        else:
            QMessageBox.critical(self, "Error", response.get("error", "Failed to grant role"))

    def export_audit(self) -> None:
        """Export audit log via expert agent."""
        # MANDATORY governance routing - no fallback
        if not self.desktop_adapter:
            QMessageBox.critical(
                self, 
                "Governance Error", 
                "Desktop governance adapter not initialized. Cannot execute governed action."
            )
            return
        
        # Route through governance pipeline
        response = self._route_through_governance(
            "audit.export",
            {
                "requester": "system"
            }
        )
        
        if response.get("status") == "success":
            result = response.get("result", {})
            output_file = result.get("out", "audit_exported.json")
            QMessageBox.information(
                self, "Export", f"Audit exported to {output_file}"
            )
        else:
            QMessageBox.critical(self, "Export Failed", response.get("error", "Unknown error"))

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
        
        # MANDATORY governance routing - no fallback
        
        if not self.desktop_adapter:
        
            QMessageBox.critical(
        
                self, 
        
                "Governance Error", 
        
                "Desktop governance adapter not initialized. Cannot execute governed action."
        
            )
        
            return
        
        
        
        # Route through governance pipeline
        response = self._route_through_governance(
            "codex.activate",
            {
                "staged_path": staged_path,
                "requester": "system"
            }
        )
        
        if response.get("status") == "success":
            QMessageBox.information(
                self, "Activated", "Staged artifact activated and integrated"
            )
            self.refresh_waiting()
        else:
            QMessageBox.critical(self, "Activation Failed", response.get("error", "Unknown error"))

    def run_qa_on_selected(self) -> None:
        item = self.waiting_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No selection", "No staged artifact selected")
            return
        staged_path = os.path.join("data/waiting_room/staged", item.text())
        
        # MANDATORY governance routing - no fallback
        
        if not self.desktop_adapter:
        
            QMessageBox.critical(
        
                self, 
        
                "Governance Error", 
        
                "Desktop governance adapter not initialized. Cannot execute governed action."
        
            )
        
            return
        
        
        
        # Route through governance pipeline
        response = self._route_through_governance(
            "codex.qa",
            {
                "staged_path": staged_path
            }
        )
        
        if response.get("status") == "success":
            result = response.get("result", {})
            QMessageBox.information(
                self,
                "QA Results",
                f"Dependency: {result.get('dependency_success')}, Tests: {result.get('test_success')}",
            )
        else:
            QMessageBox.critical(self, "QA Error", response.get("error", "Unknown error"))

    def toggle_agents(self) -> None:
        """Toggle QA/Dependency agents on/off."""
        # MANDATORY governance routing - no fallback
        if not self.desktop_adapter:
            QMessageBox.critical(
                self, 
                "Governance Error", 
                "Desktop governance adapter not initialized. Cannot execute governed action."
            )
            return
        
        # Route through governance pipeline
        response = self._route_through_governance(
            "agents.toggle",
            {
                "agent_types": ["qa_generator", "dependency_auditor"]
            }
        )
        
        if response.get("status") == "success":
            enabled = response.get("result", {}).get("enabled", False)
            QMessageBox.information(
                self, "Agents", f"QA/Dependency agents enabled: {enabled}"
            )
        else:
            QMessageBox.critical(self, "Error", response.get("error", "Failed to toggle agents"))

    def set_desktop_adapter(self, adapter) -> None:
        """Inject desktop adapter for governance routing.
        
        Args:
            adapter: Desktop adapter instance from governance pipeline
        """
        self.desktop_adapter = adapter
        logger.info("Desktop adapter injected into DashboardMainWindow")

    def _route_through_governance(self, action: str, payload: dict) -> dict:
        """Route action through governance pipeline (MANDATORY - no fallback).
        
        Args:
            action: Action identifier (e.g., "learning.approve", "learning.deny")
            payload: Action parameters
            
        Returns:
            Response dict with status and result
            
        Raises:
            RuntimeError: If desktop adapter not initialized
        """
        if not self.desktop_adapter:
            raise RuntimeError(
                "Desktop governance adapter not initialized. "
                "Cannot execute governed action. "
                "This indicates a system initialization failure."
            )
        
        try:
            return self.desktop_adapter.execute(action, payload)
        except Exception as e:
            logger.error(f"Governance routing failed for {action}: {e}")
            return {"status": "error", "error": str(e)}

