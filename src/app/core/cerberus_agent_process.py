"""
Cerberus Agent Process Manager
================================

Manages agent lifecycle and execution across multiple programming languages.
Abstracts process management, I/O handling, and monitoring.
"""

import json
import logging
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AgentProcessInfo:
    """Process information for a Cerberus agent."""

    agent_id: str
    pid: int | None
    status: str  # starting, running, stopped, failed
    start_time: str
    stop_time: str | None = None
    exit_code: int | None = None
    error_message: str | None = None


class AgentProcess:
    """
    Abstract agent execution regardless of programming language.

    Features:
    - Spawn agent processes with language-specific runtime
    - Monitor agent lifecycle (starting, running, stopped, failed)
    - Handle stdin/stdout/stderr for agent communication
    - Track PID and exit status
    - Emit structured JSON logs for all lifecycle events
    - Support graceful and forced termination
    """

    def __init__(
        self,
        agent_id: str,
        runtime_path: str,
        script_path: str,
        log_dir: str | None = None,
    ):
        """
        Initialize AgentProcess.

        Args:
            agent_id: Unique agent identifier
            runtime_path: Path to runtime executable (e.g., python3, node, go run)
            script_path: Path to agent script file
            log_dir: Directory for agent logs (optional)
        """
        self.agent_id = agent_id
        self.runtime_path = runtime_path
        self.script_path = script_path
        self.log_dir = log_dir

        # Process state
        self.process: subprocess.Popen | None = None
        self.info = AgentProcessInfo(
            agent_id=agent_id,
            pid=None,
            status="initialized",
            start_time=datetime.now().isoformat(),
        )

        # I/O state
        self.stdout_lines: list[str] = []
        self.stderr_lines: list[str] = []

    def spawn(self, timeout: int = 10) -> bool:
        """
        Spawn the agent process.

        Args:
            timeout: Timeout in seconds for process startup

        Returns:
            True if spawn successful, False otherwise
        """
        try:
            self._emit_log("agent_spawning", {"runtime": self.runtime_path})
            self.info.status = "starting"

            # Prepare command
            command = [self.runtime_path, self.script_path]

            # Spawn process
            self.process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )

            self.info.pid = self.process.pid
            self.info.status = "running"

            self._emit_log(
                "agent_spawned",
                {"pid": self.info.pid, "command": " ".join(command)},
            )

            logger.info("Spawned agent %s (PID: %s)", self.agent_id, self.info.pid)

            return True

        except Exception as e:
            self.info.status = "failed"
            self.info.error_message = str(e)

            self._emit_log("agent_spawn_failed", {"error": str(e)})

            logger.error("Failed to spawn agent %s: %s", self.agent_id, e)

            return False

    def is_running(self) -> bool:
        """
        Check if agent process is currently running.

        Returns:
            True if running, False otherwise
        """
        if self.process is None:
            return False

        # Check if process has exited
        poll_result = self.process.poll()

        if poll_result is not None:
            # Process has exited
            if self.info.status == "running":
                self.info.status = "stopped"
                self.info.stop_time = datetime.now().isoformat()
                self.info.exit_code = poll_result

                self._emit_log(
                    "agent_stopped",
                    {"exit_code": poll_result, "stop_time": self.info.stop_time},
                )

            return False

        return True

    def send_input(self, data: str) -> bool:
        """
        Send input to agent via stdin.

        Args:
            data: Data to send to agent

        Returns:
            True if successful, False otherwise
        """
        if not self.is_running() or self.process is None:
            logger.warning("Cannot send input to non-running agent %s", self.agent_id)
            return False

        try:
            if self.process.stdin:
                self.process.stdin.write(data + "\n")
                self.process.stdin.flush()

                self._emit_log("agent_input_sent", {"data_length": len(data)})

                return True

        except Exception as e:
            logger.error("Failed to send input to agent %s: %s", self.agent_id, e)

        return False

    def read_output(self, max_lines: int = 100) -> dict[str, list[str]]:
        """
        Read available output from agent (non-blocking).

        Args:
            max_lines: Maximum lines to read

        Returns:
            Dictionary with stdout and stderr lines
        """
        output = {"stdout": [], "stderr": []}

        if self.process is None:
            return output

        try:
            # Read stdout (non-blocking)
            if self.process.stdout:
                for _ in range(max_lines):
                    line = self.process.stdout.readline()
                    if not line:
                        break
                    output["stdout"].append(line.rstrip())
                    self.stdout_lines.append(line.rstrip())

            # Read stderr (non-blocking)
            if self.process.stderr:
                for _ in range(max_lines):
                    line = self.process.stderr.readline()
                    if not line:
                        break
                    output["stderr"].append(line.rstrip())
                    self.stderr_lines.append(line.rstrip())

        except Exception as e:
            logger.error("Failed to read output from agent %s: %s", self.agent_id, e)

        return output

    def terminate(self, graceful: bool = True, timeout: int = 5) -> bool:
        """
        Terminate the agent process.

        Args:
            graceful: Whether to attempt graceful termination first
            timeout: Timeout in seconds for graceful termination

        Returns:
            True if terminated successfully, False otherwise
        """
        if self.process is None:
            return True

        try:
            if graceful:
                # Send SIGTERM
                self.process.terminate()

                # Wait for graceful shutdown
                try:
                    self.process.wait(timeout=timeout)
                    self._emit_log("agent_terminated", {"method": "graceful"})

                except subprocess.TimeoutExpired:
                    # Force kill if timeout
                    logger.warning(
                        "Agent %s did not terminate gracefully, forcing...",
                        self.agent_id,
                    )
                    self.process.kill()
                    self.process.wait(timeout=2)
                    self._emit_log("agent_terminated", {"method": "forced"})

            else:
                # Immediate force kill
                self.process.kill()
                self.process.wait(timeout=2)
                self._emit_log("agent_terminated", {"method": "forced"})

            self.info.status = "stopped"
            self.info.stop_time = datetime.now().isoformat()
            self.info.exit_code = self.process.returncode

            logger.info(
                "Terminated agent %s (exit code: %s)",
                self.agent_id,
                self.info.exit_code,
            )

            return True

        except Exception as e:
            logger.error("Failed to terminate agent %s: %s", self.agent_id, e)
            return False

    def get_info(self) -> AgentProcessInfo:
        """
        Get current process information.

        Returns:
            AgentProcessInfo dataclass
        """
        # Update status if needed
        if self.info.status == "running":
            self.is_running()

        return self.info

    def get_full_output(self) -> dict[str, list[str]]:
        """
        Get all collected output from agent.

        Returns:
            Dictionary with all stdout and stderr lines
        """
        return {
            "stdout": self.stdout_lines.copy(),
            "stderr": self.stderr_lines.copy(),
        }

    def _emit_log(self, event_type: str, details: dict[str, Any] | None = None) -> None:
        """
        Emit structured JSON log for lifecycle event.

        Args:
            event_type: Type of lifecycle event
            details: Additional event details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "agent_id": self.agent_id,
            "pid": self.info.pid,
            "status": self.info.status,
        }

        if details:
            log_entry.update(details)

        # Log as JSON
        logger.info(json.dumps(log_entry))

        # Also write to agent-specific log file if log_dir provided
        if self.log_dir:
            try:
                import os

                log_file = os.path.join(self.log_dir, f"{self.agent_id}.jsonl")
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry) + "\n")

            except Exception as e:
                logger.error("Failed to write to agent log file: %s", e)

    def __repr__(self) -> str:
        """String representation of AgentProcess."""
        return f"AgentProcess(agent_id={self.agent_id}, " f"pid={self.info.pid}, status={self.info.status})"
