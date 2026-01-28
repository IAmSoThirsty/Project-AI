from __future__ import annotations

import logging
import os
import threading
from typing import Any

from app.agents.ci_checker_agent import CICheckerAgent
from app.agents.code_adversary_agent import CodeAdversaryAgent
from app.agents.constitutional_guardrail_agent import ConstitutionalGuardrailAgent
from app.agents.dependency_auditor import DependencyAuditor
from app.agents.doc_generator import DocGenerator
from app.agents.jailbreak_bench_agent import JailbreakBenchAgent
from app.agents.knowledge_curator import KnowledgeCurator
from app.agents.long_context_agent import LongContextAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.red_team_agent import RedTeamAgent
from app.agents.red_team_persona_agent import RedTeamPersonaAgent
from app.agents.refactor_agent import RefactorAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.rollback_agent import RollbackAgent
from app.agents.safety_guard_agent import SafetyGuardAgent
from app.agents.sandbox_runner import SandboxRunner
from app.agents.test_qa_generator import TestQAGenerator
from app.agents.ux_telemetry import UxTelemetryAgent
from app.core.ai_systems import AIPersona, MemoryExpansionSystem
from app.core.cognition_kernel import CognitionKernel
from app.core.continuous_learning import ContinuousLearningEngine

logger = logging.getLogger(__name__)


class CouncilHub:
    """Central Council Hub coordinating Project-AI (head) and smaller agents.

    Responsibilities:
    - Register head (Project-AI) and smaller agents under shorthands
    - Run an autonomous learning loop for the head while idle
    - Route messages between agents and the head
    - Consult Cerberus for content safety and enforce shutdown/cut communication

    CRITICAL: All agent operations are routed through CognitionKernel.
    No agent may execute directly - kernel.route() is the only execution path.

    This hub is intentionally conservative: enforcement actions are local and
    non-destructive (deactivate agent and store audit record).
    """

    def __init__(
        self,
        autolearn_interval: float = 60.0,
        kernel: CognitionKernel | None = None,
    ) -> None:
        """Initialize CouncilHub with optional kernel injection.

        Args:
            autolearn_interval: Interval for autonomous learning loop
            kernel: CognitionKernel instance for routing all agent operations
        """
        self.project_shorthand = "PA"  # Project AI shorthand
        self.agents_shorthand = "SA"  # Smaller agents shorthand
        self._project: dict[str, Any] | None = None
        self._agents: dict[str, Any] = {}
        self._lock = threading.RLock()
        self._autolearn_interval = autolearn_interval
        self._autolearn_thread: threading.Thread | None = None
        self._autolearn_stop = threading.Event()
        # Track whether optional agents are enabled
        self._agents_enabled: dict[str, bool] = {}

        # COGNITION KERNEL INTEGRATION
        self.kernel = kernel
        if kernel is None:
            logger.warning(
                "CouncilHub initialized without CognitionKernel. "
                "Agent operations will not be governed (NOT RECOMMENDED)."
            )

        # register this instance as the default singleton for convenience
        global _default_hub
        _default_hub = self

    # ----------------- registration -----------------
    def register_project(self, name: str = "Project-AI") -> None:
        """Register the Project-AI head with its subsystems.

        CRITICAL: All agents are injected with kernel for governance routing.
        """
        with self._lock:
            # Create a minimal Project-AI representation
            self._project = {
                "name": name,
                "persona": AIPersona(user_name=name),
                "memory": MemoryExpansionSystem(),
                "continuous_learning": ContinuousLearningEngine(),
            }

            # Initialize optional agents WITH KERNEL INJECTION
            # COGNITION KERNEL INTEGRATION - all agents get kernel
            self._project["curator"] = KnowledgeCurator(kernel=self.kernel)
            self._project["qa_generator"] = TestQAGenerator(kernel=self.kernel)
            self._project["dependency_auditor"] = DependencyAuditor(kernel=self.kernel)
            # more agents
            self._project["docgen"] = DocGenerator(kernel=self.kernel)
            self._project["refactor"] = RefactorAgent(kernel=self.kernel)
            self._project["sandbox"] = SandboxRunner(kernel=self.kernel)
            self._project["retrieval"] = RetrievalAgent(kernel=self.kernel)
            self._project["rollback_agent"] = RollbackAgent(kernel=self.kernel)
            self._project["planner"] = PlannerAgent(kernel=self.kernel)
            self._project["telemetry"] = UxTelemetryAgent(kernel=self.kernel)
            # Ensure CI Checker agent is present and enabled
            self._project["ci_checker"] = CICheckerAgent(kernel=self.kernel)

            # Security and Testing Agents
            self._project["long_context"] = LongContextAgent(kernel=self.kernel)
            self._project["safety_guard"] = SafetyGuardAgent(kernel=self.kernel)
            self._project["jailbreak_bench"] = JailbreakBenchAgent(kernel=self.kernel)
            self._project["red_team"] = RedTeamAgent(kernel=self.kernel)

            # NEW: Advanced Security Agents
            self._project["constitutional_guardrail"] = ConstitutionalGuardrailAgent(
                kernel=self.kernel
            )
            self._project["code_adversary"] = CodeAdversaryAgent(
                repo_path=".", kernel=self.kernel
            )
            self._project["red_team_persona"] = RedTeamPersonaAgent(kernel=self.kernel)

            # default all agents enabled
            for k in list(self._project.keys()):
                if k not in ("name", "persona", "memory", "continuous_learning"):
                    self._agents_enabled[k] = True
                    # Register the agent object under agents for routing
                    agent_obj = self._project.get(k)
                    if agent_obj:
                        self.register_agent(k, agent_obj)
            logger.info(
                "Registered project head: %s with kernel-routed agents (18 agents total)",
                name,
            )

    def register_agent(self, agent_id: str, agent_obj: Any) -> None:
        """Register a smaller agent under the Council."""
        with self._lock:
            self._agents[agent_id] = {"obj": agent_obj, "active": True}
            logger.info("Registered agent %s", agent_id)

    def unregister_agent(self, agent_id: str) -> None:
        with self._lock:
            if agent_id in self._agents:
                self._agents.pop(agent_id)
                logger.info("Unregistered agent %s", agent_id)

    def list_agents(self) -> list[str]:
        with self._lock:
            return list(self._agents.keys())

    # ----------------- autonomous learning -----------------
    def start_autonomous_learning(self) -> None:
        """Start the background autonomous learning thread."""
        if self._autolearn_thread and self._autolearn_thread.is_alive():
            return
        self._autolearn_stop.clear()
        self._autolearn_thread = threading.Thread(
            target=self._autolearn_loop, daemon=True
        )
        self._autolearn_thread.start()
        logger.info(
            "CouncilHub autonomous learning started (interval=%s)",
            self._autolearn_interval,
        )

    def stop_autonomous_learning(self) -> None:
        if self._autolearn_thread:
            self._autolearn_stop.set()
            self._autolearn_thread.join(timeout=2.0)
            logger.info("CouncilHub autonomous learning stopped")

    def _autolearn_loop(self) -> None:
        """Loop that wakes periodically and lets the Project AI absorb new info."""
        while not self._autolearn_stop.is_set():
            try:
                self._autolearn_once()
            except Exception as e:
                logger.exception("Autolearn iteration failed: %s", e)
            # Sleep with the ability to wake promptly when stopped
            self._autolearn_stop.wait(self._autolearn_interval)

    def _autolearn_once(self) -> None:
        """Single autolearn iteration: look for files in data/autolearn and absorb them.

        CRITICAL: All agent operations route through kernel.
        """
        if not self._project:
            return
        engine: ContinuousLearningEngine = self._project["continuous_learning"]
        source_dir = os.path.join("data", "autolearn")
        if not os.path.exists(source_dir):
            return
        for fn in sorted(os.listdir(source_dir)):
            if not fn.endswith(".txt"):
                continue
            path = os.path.join(source_dir, fn)
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                topic = os.path.splitext(fn)[0]
                report = engine.absorb_information(
                    topic, content, metadata={"source": "autolearn"}
                )
                logger.info(
                    "Autolearn absorbed %s -> report facts=%s", fn, report.facts
                )
                # Optionally archive consumed file
                archive = path + ".consumed"
                os.rename(path, archive)
                # After absorbing, run curator to integrate facts into curated knowledge
                # COGNITION KERNEL ROUTING - curator.curate() routed through kernel
                try:
                    curator = self._project["curator"]
                    if hasattr(curator, "curate"):
                        # Agent methods already route through kernel via _execute_through_kernel
                        curator.curate([report.__dict__])
                except Exception:
                    logger.exception("Curator failed to process report")
                # Run QA and dependency checks for code-like topics (best-effort)
                try:
                    if topic.startswith("code") or topic.startswith("impl"):
                        # locate latest generated artifact and run QA pipeline
                        gen_dir = os.path.join("src", "app", "generated", topic)
                        if os.path.exists(gen_dir):
                            files = sorted(
                                [
                                    os.path.join(gen_dir, f)
                                    for f in os.listdir(gen_dir)
                                    if f.endswith(".py")
                                ]
                            )
                            if files:
                                latest = files[-1]
                                # COGNITION KERNEL ROUTING - all agent calls routed through kernel
                                # Only run if agents enabled
                                if self._agents_enabled.get("dependency_auditor", True):
                                    dep_auditor = self._project["dependency_auditor"]
                                    # Agent methods already route through kernel via _execute_through_kernel
                                    dep_auditor.analyze_new_module(latest)
                                if self._agents_enabled.get("qa_generator", True):
                                    qa_gen = self._project["qa_generator"]
                                    # Agent methods already route through kernel via _execute_through_kernel
                                    qa_gen.generate_test_for_module(latest)
                except Exception:
                    logger.exception("Post-curation QA pipeline failed")
            except Exception as e:
                logger.exception("Failed to autolearn from %s: %s", fn, e)

    def run_checks(self, target: str | None = None) -> dict[str, Any]:
        """Run dependency and QA checks for generated artifacts.

        CRITICAL: All agent operations route through kernel.

        Returns a dict with success flag and failures list when present.
        """
        with self._lock:
            if not self._project:
                return {"success": False, "error": "no_project"}
            qa = self._project.get("qa_generator")
            dep = self._project.get("dependency_auditor")
            failures: list[dict[str, Any]] = []

            gen_root = os.path.join("src", "app", "generated")
            if not os.path.exists(gen_root):
                return {"success": True, "checked": 0}

            for root, _, files in os.walk(gen_root):
                for fn in files:
                    if not fn.endswith(".py"):
                        continue
                    path = os.path.join(root, fn)
                    # COGNITION KERNEL ROUTING - dependency auditor
                    if self._agents_enabled.get("dependency_auditor", True) and dep:
                        try:
                            # Agent methods already route through kernel via _execute_through_kernel
                            dep_res = dep.analyze_new_module(path)
                            if not dep_res.get("success"):
                                failures.append(
                                    {
                                        "module": path,
                                        "stage": "dependency",
                                        "detail": dep_res,
                                    }
                                )
                        except Exception as e:
                            logger.exception(
                                "Dependency check exception for %s: %s", path, e
                            )
                            failures.append(
                                {
                                    "module": path,
                                    "stage": "dependency_exception",
                                    "detail": str(e),
                                }
                            )
                    # COGNITION KERNEL ROUTING - QA generator
                    if self._agents_enabled.get("qa_generator", True) and qa:
                        try:
                            # Agent methods already route through kernel via _execute_through_kernel
                            gen = qa.generate_test_for_module(path)
                            if not gen.get("success"):
                                failures.append(
                                    {
                                        "module": path,
                                        "stage": "qa_generate",
                                        "detail": gen,
                                    }
                                )
                                continue
                            # Agent methods already route through kernel via _execute_through_kernel
                            run = qa.run_tests()
                            if not run.get("success"):
                                failures.append(
                                    {"module": path, "stage": "qa_run", "detail": run}
                                )
                        except Exception as e:
                            logger.exception("QA check exception for %s: %s", path, e)
                            failures.append(
                                {
                                    "module": path,
                                    "stage": "qa_exception",
                                    "detail": str(e),
                                }
                            )

            if failures:
                return {"success": False, "failures": failures}
            return {"success": True, "checked": 1}

            if failures:
                return {"success": False, "failures": failures}
            return {"success": True, "checked": 1}

    # ----------------- messaging & enforcement -----------------
    def route_message(self, from_id: str, to_id: str, message: str) -> dict[str, Any]:
        """Route a message between agents or head. Consult Cerberus and enforce guardrails."""
        # Check content through Cerberus
        cerberus_result = self._consult_cerberus(message)
        if not cerberus_result.get("is_safe", True):
            # If unsafe, cut communication and optionally shutdown the sender
            logger.warning(
                "Cerberus flagged message from %s as unsafe: %s",
                from_id,
                cerberus_result,
            )
            self._cut_communication(from_id)
            return {"delivered": False, "reason": "unsafe", "cerberus": cerberus_result}

        # Deliver message if recipients are active
        with self._lock:
            recipient = None
            if to_id == self.project_shorthand and self._project:
                recipient = self._project
            elif to_id in self._agents:
                recipient = self._agents[to_id]["obj"]
            if recipient is None:
                return {"delivered": False, "reason": "unknown_recipient"}

        # Best-effort delivery: call `receive_message` if available
        try:
            if hasattr(recipient, "receive_message"):
                recipient.receive_message(from_id, message)
            return {"delivered": True}
        except Exception as e:
            logger.exception(
                "Failed to deliver message from %s to %s: %s", from_id, to_id, e
            )
            return {"delivered": False, "error": str(e)}

    def _consult_cerberus(self, content: str) -> dict[str, Any]:
        """Call Cerberus HubCoordinator to analyze content. Returns minimal result dict.

        If Cerberus is unavailable, defaults to safe (no action).
        """
        try:
            from cerberus.hub import HubCoordinator

            hub = HubCoordinator()
            res = hub.analyze(content)
            return {"is_safe": res.get("is_safe", True), "details": res}
        except Exception as e:
            logger.debug("Cerberus not available for consultation: %s", e)
            return {"is_safe": True, "details": {}}

    def _cut_communication(self, agent_id: str) -> None:
        """Disable an agent's ability to send/receive messages. Audit action."""
        with self._lock:
            if agent_id in self._agents:
                self._agents[agent_id]["active"] = False
                # If agent has a `deactivate` method, call it
                try:
                    obj = self._agents[agent_id]["obj"]
                    if hasattr(obj, "deactivate"):
                        obj.deactivate()
                except Exception:
                    logger.exception("Failed to gracefully deactivate %s", agent_id)
                logger.warning(
                    "Agent %s communication cut by CouncilHub due to Cerberus alert",
                    agent_id,
                )
            else:
                logger.warning(
                    "Attempted to cut communication for unknown agent %s", agent_id
                )

    def enable_agent(self, agent_id: str) -> None:
        """Enable an optional agent."""
        with self._lock:
            if agent_id in self._agents_enabled:
                self._agents_enabled[agent_id] = True
                logger.info("Enabled agent %s", agent_id)
            else:
                logger.warning("Attempted to enable unknown agent %s", agent_id)

    def disable_agent(self, agent_id: str) -> None:
        """Disable an optional agent."""
        with self._lock:
            if agent_id in self._agents_enabled:
                self._agents_enabled[agent_id] = False
                logger.info("Disabled agent %s", agent_id)
            else:
                logger.warning("Attempted to disable unknown agent %s", agent_id)

    def is_agent_enabled(self, agent_id: str) -> bool:
        """Check if an optional agent is enabled."""
        with self._lock:
            return self._agents_enabled.get(agent_id, False)


# Simple singleton instance for convenience
_default_hub: CouncilHub | None = None


def get_council_hub() -> CouncilHub:
    global _default_hub
    if _default_hub is None:
        _default_hub = CouncilHub()
    return _default_hub
