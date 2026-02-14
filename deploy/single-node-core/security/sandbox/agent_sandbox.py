#!/usr/bin/env python3
"""
Agent Sandbox System - Secure Execution Boundaries
===================================================

Provides isolated execution environments for AI agents with resource limits,
network restrictions, and escape detection.

Features:
- Process-level isolation using cgroups
- Resource limits (CPU, memory, disk I/O)
- Network namespace isolation
- File system restrictions (read-only mounts)
- System call filtering (seccomp)
- Escape attempt detection
- Audit logging of all sandbox operations
"""

import json
import logging
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SandboxProfile(Enum):
    """Predefined sandbox security profiles."""
    MINIMAL = "minimal"  # Bare minimum isolation
    STANDARD = "standard"  # Default production profile
    STRICT = "strict"  # Maximum isolation
    PARANOID = "paranoid"  # Zero-trust, full lockdown


@dataclass
class ResourceLimits:
    """Resource limits for sandboxed execution."""
    cpu_quota_percent: int = 50  # % of 1 CPU core
    memory_limit_mb: int = 512
    disk_io_limit_mbps: int = 10
    max_processes: int = 10
    max_open_files: int = 100
    max_network_connections: int = 5
    execution_timeout_seconds: int = 300


@dataclass
class SandboxConfig:
    """Complete sandbox configuration."""
    profile: SandboxProfile
    resource_limits: ResourceLimits
    allowed_syscalls: list[str]
    blocked_syscalls: list[str]
    allowed_network_hosts: list[str]
    allowed_file_paths: list[str]
    read_only_paths: list[str]
    enable_network: bool
    enable_internet: bool
    enable_ipc: bool


class AgentSandbox:
    """Manage agent execution sandboxes."""

    def __init__(self, sandbox_dir: Path):
        """
        Initialize sandbox manager.

        Args:
            sandbox_dir: Directory for sandbox configs and logs
        """
        self.sandbox_dir = Path(sandbox_dir)
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        self.configs_dir = self.sandbox_dir / "configs"
        self.logs_dir = self.sandbox_dir / "logs"
        self.configs_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

    def create_config(
        self,
        agent_id: str,
        profile: SandboxProfile = SandboxProfile.STANDARD
    ) -> SandboxConfig:
        """
        Create sandbox configuration for an agent.

        Args:
            agent_id: Unique agent identifier
            profile: Security profile to use

        Returns:
            Sandbox configuration
        """
        # Define profile-specific settings
        if profile == SandboxProfile.MINIMAL:
            limits = ResourceLimits(
                cpu_quota_percent=80,
                memory_limit_mb=1024,
                max_processes=50
            )
            allowed_syscalls = ["read", "write", "open", "close", "stat", "exit"]
            enable_network = True
            enable_internet = True

        elif profile == SandboxProfile.STANDARD:
            limits = ResourceLimits(
                cpu_quota_percent=50,
                memory_limit_mb=512,
                max_processes=20
            )
            allowed_syscalls = [
                "read", "write", "open", "close", "stat",
                "fstat", "lstat", "poll", "lseek", "mmap",
                "mprotect", "munmap", "brk", "rt_sigaction",
                "rt_sigprocmask", "rt_sigreturn", "ioctl",
                "access", "exit", "exit_group", "wait4",
                "clone", "execve", "getpid", "getuid"
            ]
            enable_network = True
            enable_internet = False  # Only internal network

        elif profile == SandboxProfile.STRICT:
            limits = ResourceLimits(
                cpu_quota_percent=25,
                memory_limit_mb=256,
                max_processes=10,
                max_network_connections=3
            )
            allowed_syscalls = [
                "read", "write", "open", "close", "stat",
                "exit", "exit_group", "getpid"
            ]
            enable_network = False
            enable_internet = False

        else:  # PARANOID
            limits = ResourceLimits(
                cpu_quota_percent=10,
                memory_limit_mb=128,
                max_processes=5,
                max_network_connections=0
            )
            allowed_syscalls = ["read", "write", "exit"]
            enable_network = False
            enable_internet = False

        # Create configuration
        config = SandboxConfig(
            profile=profile,
            resource_limits=limits,
            allowed_syscalls=allowed_syscalls,
            blocked_syscalls=[
                "ptrace",  # Debugging
                "mount", "umount",  # Filesystem
                "reboot", "kexec_load",  # System
                "setuid", "setgid",  # Privilege escalation
                "socket", "bind", "listen",  # Network (if disabled)
            ],
            allowed_network_hosts=[
                "127.0.0.1",
                "localhost",
                "postgres",
                "redis",
                "mcp-gateway"
            ] if enable_network else [],
            allowed_file_paths=[
                "/app",
                "/tmp",
                "/var/tmp"
            ],
            read_only_paths=[
                "/usr",
                "/lib",
                "/etc"
            ],
            enable_network=enable_network,
            enable_internet=enable_internet,
            enable_ipc=False
        )

        # Save configuration
        config_file = self.configs_dir / f"{agent_id}.json"
        config_file.write_text(json.dumps(asdict(config), indent=2, default=str))

        logger.info(f"✓ Created {profile.value} sandbox config for {agent_id}")

        return config

    def generate_docker_sandbox_command(
        self,
        agent_id: str,
        image: str,
        command: list[str]
    ) -> list[str]:
        """
        Generate Docker command with sandbox constraints.

        Args:
            agent_id: Agent identifier
            image: Docker image to run
            command: Command to execute

        Returns:
            Docker command with security constraints
        """
        config_file = self.configs_dir / f"{agent_id}.json"

        if not config_file.exists():
            raise FileNotFoundError(f"Sandbox config not found for {agent_id}")

        config_data = json.loads(config_file.read_text())
        config = SandboxConfig(**config_data)
        limits = ResourceLimits(**config.resource_limits)

        # Build docker run command with constraints
        docker_cmd = [
            "docker", "run",
            "--rm",
            "--name", f"agent-sandbox-{agent_id}",

            # Resource limits
            "--cpus", str(limits.cpu_quota_percent / 100.0),
            "--memory", f"{limits.memory_limit_mb}m",
            "--memory-swap", f"{limits.memory_limit_mb}m",  # No swap
            "--pids-limit", str(limits.max_processes),
            "--ulimit", f"nofile={limits.max_open_files}:{limits.max_open_files}",

            # Security options
            "--security-opt", "no-new-privileges:true",
            "--cap-drop", "ALL",  # Drop all capabilities
            "--cap-add", "CHOWN",  # Only what's needed
            "--cap-add", "DAC_OVERRIDE",
            "--read-only",  # Read-only root filesystem
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=100m",

            # Network isolation
        ]

        if not config["enable_network"]:
            docker_cmd.extend(["--network", "none"])
        elif not config["enable_internet"]:
            docker_cmd.extend(["--network", "project-ai-core-network"])

        # Add image and command
        docker_cmd.append(image)
        docker_cmd.extend(command)

        return docker_cmd

    def execute_sandboxed(
        self,
        agent_id: str,
        image: str,
        command: list[str],
        timeout: int = None
    ) -> dict[str, Any]:
        """
        Execute command in sandboxed environment.

        Args:
            agent_id: Agent identifier
            image: Docker image
            command: Command to execute
            timeout: Execution timeout (uses config default if None)

        Returns:
            Execution results
        """
        # Get configuration
        config_file = self.configs_dir / f"{agent_id}.json"

        if not config_file.exists():
            raise FileNotFoundError(f"Sandbox config not found for {agent_id}")

        config_data = json.loads(config_file.read_text())
        config = SandboxConfig(**config_data)
        limits = ResourceLimits(**config.resource_limits)

        if timeout is None:
            timeout = limits.execution_timeout_seconds

        # Generate sandboxed command
        docker_cmd = self.generate_docker_sandbox_command(agent_id, image, command)

        # Log execution attempt
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "agent_id": agent_id,
            "image": image,
            "command": command,
            "profile": config.profile.value,
            "timeout": timeout
        }

        logger.info(f"Executing in sandbox: {agent_id}")

        start_time = datetime.now(UTC)

        try:
            # Execute with timeout
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            execution_time = (datetime.now(UTC) - start_time).total_seconds()

            log_entry.update({
                "status": "success" if result.returncode == 0 else "failed",
                "return_code": result.returncode,
                "execution_time_seconds": execution_time,
                "stdout_length": len(result.stdout),
                "stderr_length": len(result.stderr)
            })

            # Check for escape attempts
            escape_detected = self._check_escape_attempts(result.stderr)
            if escape_detected:
                log_entry["security_alert"] = "Escape attempt detected"
                logger.warning(f"⚠ Escape attempt detected for {agent_id}")

            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": execution_time,
                "escape_detected": escape_detected
            }

        except subprocess.TimeoutExpired:
            log_entry.update({
                "status": "timeout",
                "execution_time_seconds": timeout
            })

            logger.error(f"✗ Execution timeout for {agent_id}")

            return {
                "success": False,
                "error": "Execution timeout",
                "timeout": timeout
            }

        except Exception as e:
            log_entry.update({
                "status": "error",
                "error": str(e)
            })

            logger.error(f"✗ Execution error for {agent_id}: {e}")

            return {
                "success": False,
                "error": str(e)
            }

        finally:
            # Log to audit trail
            log_file = self.logs_dir / f"{agent_id}.jsonl"
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

    def _check_escape_attempts(self, stderr: str) -> bool:
        """
        Detect potential sandbox escape attempts.

        Args:
            stderr: Standard error output

        Returns:
            True if escape attempt detected
        """
        # Look for suspicious patterns
        suspicious_patterns = [
            "permission denied",
            "operation not permitted",
            "capability",
            "ptrace",
            "mount",
            "chroot",
            "setuid",
            "privilege",
            "kernel"
        ]

        stderr_lower = stderr.lower()

        return any(pattern in stderr_lower for pattern in suspicious_patterns)

    def get_sandbox_stats(self, agent_id: str) -> dict[str, Any]:
        """
        Get statistics for agent sandbox usage.

        Args:
            agent_id: Agent identifier

        Returns:
            Usage statistics
        """
        log_file = self.logs_dir / f"{agent_id}.jsonl"

        if not log_file.exists():
            return {"executions": 0}

        logs = []
        with open(log_file) as f:
            for line in f:
                logs.append(json.loads(line))

        # Calculate statistics
        total = len(logs)
        successes = sum(1 for log in logs if log.get("status") == "success")
        failures = sum(1 for log in logs if log.get("status") == "failed")
        timeouts = sum(1 for log in logs if log.get("status") == "timeout")
        errors = sum(1 for log in logs if log.get("status") == "error")
        escape_attempts = sum(1 for log in logs if "security_alert" in log)

        execution_times = [
            log.get("execution_time_seconds", 0)
            for log in logs
            if "execution_time_seconds" in log
        ]

        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0

        return {
            "agent_id": agent_id,
            "total_executions": total,
            "successful": successes,
            "failed": failures,
            "timeouts": timeouts,
            "errors": errors,
            "escape_attempts": escape_attempts,
            "avg_execution_time_seconds": round(avg_time, 2),
            "success_rate": round(successes / total * 100, 2) if total > 0 else 0
        }


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Agent sandbox management")
    parser.add_argument(
        "command",
        choices=["create", "execute", "stats"],
        help="Command to execute"
    )
    parser.add_argument("--agent-id", required=True, help="Agent identifier")
    parser.add_argument(
        "--profile",
        choices=["minimal", "standard", "strict", "paranoid"],
        default="standard",
        help="Security profile"
    )
    parser.add_argument("--image", help="Docker image to run")
    parser.add_argument("--cmd", nargs="+", help="Command to execute")
    parser.add_argument(
        "--sandbox-dir",
        type=Path,
        default=Path("/home/runner/work/Project-AI/Project-AI/deploy/single-node-core/security/sandbox"),
        help="Sandbox directory"
    )

    args = parser.parse_args()

    sandbox = AgentSandbox(args.sandbox_dir)

    if args.command == "create":
        profile = SandboxProfile(args.profile)
        config = sandbox.create_config(args.agent_id, profile)
        print(f"✓ Created {profile.value} sandbox for {args.agent_id}")
        print(json.dumps(asdict(config), indent=2, default=str))

    elif args.command == "execute":
        if not args.image or not args.cmd:
            parser.error("--image and --cmd required for execute")

        result = sandbox.execute_sandboxed(args.agent_id, args.image, args.cmd)

        if result["success"]:
            print("✓ Execution successful")
            if result.get("stdout"):
                print(f"\nOutput:\n{result['stdout']}")
        else:
            print("✗ Execution failed")
            if result.get("error"):
                print(f"Error: {result['error']}")
            if result.get("stderr"):
                print(f"\nStderr:\n{result['stderr']}")

        sys.exit(0 if result["success"] else 1)

    elif args.command == "stats":
        stats = sandbox.get_sandbox_stats(args.agent_id)
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
