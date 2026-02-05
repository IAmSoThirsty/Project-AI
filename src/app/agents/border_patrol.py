from __future__ import annotations

import logging
import threading
import time
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.agents.dependency_auditor import DependencyAuditor
from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent
from app.monitoring.cerberus_dashboard import record_incident

logger = logging.getLogger(__name__)


@dataclass
class QuarantineBox:
    path: str
    created_ts: float
    sealed: bool = True
    verified: bool = False
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert QuarantineBox to a serializable dictionary."""
        return {
            "path": self.path,
            "created_ts": self.created_ts,
            "sealed": self.sealed,
            "verified": self.verified,
            "metadata": self.metadata,
        }


class VerifierAgent(KernelRoutedAgent):
    """VerifierAgent executes audits in a sandbox and reports results.

    Uses a ProcessPoolExecutor to run sandbox executions in isolated processes with a configurable timeout.
    """

    def __init__(
        self,
        agent_id: str,
        data_dir: str = "data",
        max_workers: int = 2,
        timeout: int = 8,
        kernel: CognitionKernel | None = None,
    ):
        # Initialize kernel routing (COGNITION KERNEL INTEGRATION)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="high",
        )
        self.agent_id = agent_id
        self.auditor = DependencyAuditor(data_dir=data_dir)
        self.executor = ProcessPoolExecutor(max_workers=max_workers)
        self.timeout = timeout

    def _run_sandbox(self, module_path: str) -> dict[str, Any]:
        # sandbox_worker.run_module is importable by path; use module run via python -m is safer
        worker = Path(__file__).parent.parent / "agents" / "sandbox_worker.py"
        # Use ProcessPoolExecutor to call run_module by import
        try:
            future = self.executor.submit(
                self._call_worker_run, str(worker), str(Path(module_path).resolve())
            )
            return future.result(timeout=self.timeout)
        except TimeoutError:
            logger.exception("Sandbox execution timed out for %s", module_path)
            return {"error": "timeout", "success": False}
        except Exception as e:
            logger.exception("Sandbox execution failed for %s: %s", module_path, e)
            return {"error": str(e), "success": False}

    @staticmethod
    def _call_worker_run(worker_script: str, module_path: str) -> dict[str, Any]:
        # Import the worker module and call run_module
        import importlib.util

        spec = importlib.util.spec_from_file_location("sandbox_worker", worker_script)
        if spec is None or spec.loader is None:
            return {"error": "failed_to_load_worker_spec", "success": False}
        module = importlib.util.module_from_spec(spec)  # type: ignore
        try:
            spec.loader.exec_module(module)  # type: ignore
        except Exception as e:
            return {"error": f"failed_to_exec_worker: {e}", "success": False}
        # call run_module
        try:
            return module.run_module(module_path)
        except Exception as e:
            return {"error": f"worker_run_exception: {e}", "success": False}

    def verify(self, file_path: str) -> dict[str, Any]:
        # Route through kernel (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            self._do_verify,
            action_name="verify_file",
            action_args=(file_path,),
            risk_level="high",
            metadata={"file_path": file_path, "agent_id": self.agent_id},
        )

    def _do_verify(self, file_path: str) -> dict[str, Any]:
        """Internal implementation of file verification."""
        logger.info("VerifierAgent %s verifying %s", self.agent_id, file_path)
        # quick dependency scan
        deps_report = self.auditor.analyze_new_module(file_path)
        # run sandboxed execution
        sandbox_report = self._run_sandbox(file_path)
        # merge reports
        report = {"success": True, "deps": deps_report, "sandbox": sandbox_report}
        # decide verdict
        if sandbox_report.get("exception"):
            report["success"] = False
            report["verdict"] = "suspicious"
        else:
            report["verdict"] = "clean"
        return report


class GateGuardian:
    """GateGuardian is responsible for placing incoming files into quarantine
    and coordinating with a VerifierAgent to allow/deny passage.
    """

    def __init__(self, gate_id: str, verifier: VerifierAgent, watch_tower: WatchTower):
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
        box.verified = bool(report.get("success"))
        box.metadata = report
        # Notify watch tower of result
        self.watch_tower.receive_report(self.gate_id, box)
        # record incident for monitoring if suspicious
        if not box.verified:
            record_incident(
                {
                    "type": "suspicious_plugin",
                    "gate": self.gate_id,
                    "module": file_path,
                    "metadata": report,
                }
            )
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
                logger.info(
                    "Gate %s released %s from quarantine", self.gate_id, file_path
                )


class WatchTower:
    def __init__(self, tower_id: str, port_admin: PortAdmin):
        self.tower_id = tower_id
        self.port_admin = port_admin
        self.reports: list[QuarantineBox] = []
        self.attack_counts: dict[str, int] = {}

    def receive_report(self, gate_id: str, box: QuarantineBox) -> None:
        logger.info(
            "WatchTower %s received report from gate %s", self.tower_id, gate_id
        )
        self.reports.append(box)
        # Evaluate report & escalate if necessary
        src = box.metadata.get("sandbox", {}).get("source") if box.metadata else None
        src_id = src or gate_id
        self.attack_counts[src_id] = self.attack_counts.get(src_id, 0) + 1
        # If repeated attacks from same source, escalate
        if self.attack_counts[src_id] > 3:
            self.port_admin.notify_incident(self.tower_id, gate_id, box)
            record_incident(
                {
                    "type": "repeated_attacks",
                    "tower": self.tower_id,
                    "gate": gate_id,
                    "source": src_id,
                }
            )
        # If sandbox crashed or exception, escalate immediately
        if box.metadata and box.metadata.get("sandbox", {}).get("exception"):
            self.port_admin.notify_incident(self.tower_id, gate_id, box)

    def signal_emergency(self, gate_id: str) -> None:
        logger.critical(
            "WatchTower %s: emergency signaled by gate %s", self.tower_id, gate_id
        )
        self.port_admin.handle_emergency(self.tower_id, gate_id)


class PortAdmin:
    def __init__(self, admin_id: str, command_center: Cerberus):
        self.admin_id = admin_id
        self.command_center = command_center
        self.towers: list[WatchTower] = []

    def notify_incident(self, tower_id: str, gate_id: str, box: QuarantineBox) -> None:
        logger.warning(
            "PortAdmin %s notified of incident at tower %s gate %s",
            self.admin_id,
            tower_id,
            gate_id,
        )
        # create incident report and pass to Cerberus
        self.command_center.record_incident(
            {"tower": tower_id, "gate": gate_id, "box": box.to_dict()}
        )

    def handle_emergency(self, tower_id: str, gate_id: str) -> None:
        logger.critical(
            "PortAdmin %s handling emergency at tower %s gate %s",
            self.admin_id,
            tower_id,
            gate_id,
        )
        # instruct Cerberus to quarantine/obliterate box contents safely
        self.command_center.execute_lockdown(tower_id, gate_id)


class Cerberus:
    """Cerberus - Chief of Security.

    Cerberus is the supreme security authority in Project-AI, overseeing all
    security operations through the Watch Tower / Security Command Center.

    As Chief of Security, Cerberus coordinates:
    - Border Patrol Operations (PortAdmins, WatchTowers, GateGuardians, Verifiers)
    - Active Defense (Safety Guards, Constitutional Guardrails, Protectors)
    - Red Team / Adversarial Testing (Red Team Agents, Code Adversaries, Jailbreak Tests)
    - Oversight & Analysis (Oversight Agents, Validators, Explainability)

    All security agents and roles operate under Cerberus's command through the
    Global Watch Tower Security Command Center.
    """

    def __init__(self):
        self.title = "Chief of Security"
        self.incidents: list[Any] = []
        self.security_agents: dict[str, list[str]] = {
            "border_patrol": [],
            "active_defense": [],
            "red_team": [],
            "oversight": [],
        }
        logger.info("Cerberus initialized as Chief of Security")

    def record_incident(self, incident: dict[str, Any]) -> None:
        logger.error("Cerberus (Chief of Security) recording incident: %s", incident)
        # record in persistent monitor
        record_incident({"type": "incident", "detail": incident})
        self.incidents.append(incident)

    def execute_lockdown(self, tower_id: str, gate_id: str) -> None:
        logger.critical(
            "Cerberus (Chief of Security) executing lockdown for tower %s, gate %s",
            tower_id,
            gate_id,
        )
        # Non-destructive approach: mark box sealed and create audit entry
        self.record_incident(
            {
                "action": "lockdown",
                "tower": tower_id,
                "gate": gate_id,
                "ts": time.time(),
            }
        )

    def register_security_agent(self, agent_type: str, agent_id: str) -> None:
        """Register a security agent under Cerberus's command.

        Args:
            agent_type: Category of agent (border_patrol, active_defense, red_team, oversight)
            agent_id: Unique identifier for the agent
        """
        if agent_type in self.security_agents:
            if agent_id not in self.security_agents[agent_type]:
                self.security_agents[agent_type].append(agent_id)
                logger.info("Cerberus registered %s agent: %s", agent_type, agent_id)
        else:
            logger.warning(
                "Unknown agent type '%s' for agent '%s'", agent_type, agent_id
            )

    def get_security_status(self) -> dict[str, Any]:
        """Get comprehensive security status report.

        Returns:
            dict: Security status including all registered agents and incident count
        """
        return {
            "chief_of_security": "Cerberus",
            "total_incidents": len(self.incidents),
            "registered_agents": {
                agent_type: len(agents)
                for agent_type, agents in self.security_agents.items()
            },
            "agent_details": self.security_agents,
        }


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
                GateGuardian(f"g-{a}-{t}-{g}", verifier, wt)
                wt.reports = []
        admins.append(pa)
    return admins
