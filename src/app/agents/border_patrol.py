from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from queue import Queue
from typing import Any

from app.agents.dependency_auditor import DependencyAuditor

logger = logging.getLogger(__name__)


@dataclass
class QuarantineBox:
    path: str
    created_ts: float
    sealed: bool = True
    verified: bool = False
    metadata: dict[str, Any] | None = None


class VerifierAgent:
    """VerifierAgent executes audits in a sandbox and reports results.

    It uses DependencyAuditor to run sandboxed execution and returns a structured
    verification report. The agent runs tasks from a work queue so it can be
    scaled or run in its own thread/process.
    """

    def __init__(self, agent_id: str, data_dir: str = "data"):
        self.agent_id = agent_id
        self.auditor = DependencyAuditor(data_dir=data_dir)

    def verify(self, file_path: str) -> dict[str, Any]:
        logger.info("VerifierAgent %s verifying %s", self.agent_id, file_path)
        report = self.auditor.analyze_new_module(file_path)
        return report


class GateGuardian:
    """GateGuardian is responsible for placing incoming files into quarantine
    and coordinating with a VerifierAgent to allow/deny passage.
    """

    def __init__(self, gate_id: str, verifier: VerifierAgent, watch_tower: "WatchTower"):
        self.gate_id = gate_id
        self.verifier = verifier
        self.watch_tower = watch_tower
        self.quarantine: dict[str, QuarantineBox] = {}
        self.lock = threading.Lock()
        self.force_field_active = False

    def ingest(self, file_path: str) -> QuarantineBox:
        with self.lock:
            box = QuarantineBox(path=file_path, created_ts=time.time())
            self.quarantine[file_path] = box
            logger.info("Gate %s quarantined %s", self.gate_id, file_path)
            return box

    def process_next(self, file_path: str) -> dict[str, Any]:
        box = self.quarantine.get(file_path)
        if not box:
            raise KeyError("file not found in quarantine")
        # Run verification
        report = self.verifier.verify(file_path)
        box.verified = True if report.get("success") else False
        box.metadata = report
        # Notify watch tower of result
        self.watch_tower.receive_report(self.gate_id, box)
        return report

    def activate_force_field(self) -> None:
        logger.warning("Gate %s activating force field", self.gate_id)
        self.force_field_active = True
        # Signal watch tower for emergency
        self.watch_tower.signal_emergency(self.gate_id)

    def release(self, file_path: str) -> None:
        with self.lock:
            if file_path in self.quarantine:
                del self.quarantine[file_path]
                logger.info("Gate %s released %s from quarantine", self.gate_id, file_path)


class WatchTower:
    def __init__(self, tower_id: str, port_admin: "PortAdmin"):
        self.tower_id = tower_id
        self.port_admin = port_admin
        self.reports: list[QuarantineBox] = []

    def receive_report(self, gate_id: str, box: QuarantineBox) -> None:
        logger.info("WatchTower %s received report from gate %s", self.tower_id, gate_id)
        self.reports.append(box)
        # Evaluate report & escalate if necessary
        if box.metadata and box.metadata.get("sandbox", {}).get("exception"):
            # suspicious or crashed in sandbox -> escalate
            self.port_admin.notify_incident(self.tower_id, gate_id, box)

    def signal_emergency(self, gate_id: str) -> None:
        logger.critical("WatchTower %s: emergency signaled by gate %s", self.tower_id, gate_id)
        self.port_admin.handle_emergency(self.tower_id, gate_id)


class PortAdmin:
    def __init__(self, admin_id: str, command_center: "Cerberus"):
        self.admin_id = admin_id
        self.command_center = command_center
        self.towers: list[WatchTower] = []

    def notify_incident(self, tower_id: str, gate_id: str, box: QuarantineBox) -> None:
        logger.warning("PortAdmin %s notified of incident at tower %s gate %s", self.admin_id, tower_id, gate_id)
        # create incident report and pass to Cerberus
        self.command_center.record_incident({"tower": tower_id, "gate": gate_id, "box": box})

    def handle_emergency(self, tower_id: str, gate_id: str) -> None:
        logger.critical("PortAdmin %s handling emergency at tower %s gate %s", self.admin_id, tower_id, gate_id)
        # instruct Cerberus to quarantine/obliterate box contents safely
        self.command_center.execute_lockdown(tower_id, gate_id)


class Cerberus:
    def __init__(self):
        self.incidents: list[Any] = []

    def record_incident(self, incident: dict[str, Any]) -> None:
        logger.error("Cerberus recording incident: %s", incident)
        self.incidents.append(incident)

    def execute_lockdown(self, tower_id: str, gate_id: str) -> None:
        logger.critical("Cerberus executing lockdown for tower %s, gate %s", tower_id, gate_id)
        # Non-destructive approach: mark box sealed and create audit entry
        self.record_incident({"action": "lockdown", "tower": tower_id, "gate": gate_id, "ts": time.time()})


# Helper: build the hierarchy
def build_border_patrol(num_port_admins: int = 1) -> list[PortAdmin]:
    cer = Cerberus()
    admins: list[PortAdmin] = []
    for a in range(num_port_admins):
        pa = PortAdmin(str(a), cer)
        for t in range(10):
            wt = WatchTower(str(t), pa)
            pa.towers.append(wt)
            # create 5 gates with verifier/scanner pairs
            for g in range(5):
                verifier = VerifierAgent(f"v-{a}-{t}-{g}")
                gate = GateGuardian(f"g-{a}-{t}-{g}", verifier, wt)
                wt.reports = []
        admins.append(pa)
    return admins
