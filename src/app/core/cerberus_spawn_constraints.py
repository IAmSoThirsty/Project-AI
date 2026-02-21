"""
Cerberus Hydra Defense - Spawn Constraints and Adaptive Control

Implements hard caps, rate limiting, adaptive spawning, and resource budgets
to prevent resource exhaustion and enable intelligent response scaling.
"""

import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SpawnBudget:
    """Resource budget for agent spawning."""

    max_cpu_seconds: float = 3600.0  # 1 hour of CPU time
    max_memory_mb: float = 1024.0  # 1GB of memory
    max_network_mb: float = 100.0  # 100MB of network
    max_spawns: int = 100  # Max total spawns
    used_cpu_seconds: float = 0.0
    used_memory_mb: float = 0.0
    used_network_mb: float = 0.0
    current_spawns: int = 0

    def can_spawn(self, estimated_cost: dict[str, float] | None = None) -> bool:
        """Check if spawn is within budget."""
        if self.current_spawns >= self.max_spawns:
            return False

        if estimated_cost:
            cpu = estimated_cost.get("cpu_seconds", 1.0)
            memory = estimated_cost.get("memory_mb", 50.0)
            network = estimated_cost.get("network_mb", 1.0)

            if self.used_cpu_seconds + cpu > self.max_cpu_seconds:
                return False
            if self.used_memory_mb + memory > self.max_memory_mb:
                return False
            if self.used_network_mb + network > self.max_network_mb:
                return False

        return True

    def consume(self, actual_cost: dict[str, float]) -> None:
        """Consume budget resources."""
        self.used_cpu_seconds += actual_cost.get("cpu_seconds", 0.0)
        self.used_memory_mb += actual_cost.get("memory_mb", 0.0)
        self.used_network_mb += actual_cost.get("network_mb", 0.0)
        self.current_spawns += 1

    def get_utilization(self) -> dict[str, float]:
        """Get budget utilization percentage."""
        return {
            "cpu_percent": (self.used_cpu_seconds / self.max_cpu_seconds) * 100,
            "memory_percent": (self.used_memory_mb / self.max_memory_mb) * 100,
            "network_percent": (self.used_network_mb / self.max_network_mb) * 100,
            "spawns_percent": (self.current_spawns / self.max_spawns) * 100,
        }


@dataclass
class SystemLoad:
    """Current system load metrics."""

    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    active_agents: int = 0
    total_agents: int = 0
    incident_rate: float = 0.0  # Incidents per minute

    def is_high_load(self) -> bool:
        """Check if system is under high load."""
        return (
            self.cpu_percent > 80.0
            or self.memory_percent > 85.0
            or self.active_agents > 500
        )

    def is_critical_load(self) -> bool:
        """Check if system is under critical load."""
        return (
            self.cpu_percent > 95.0
            or self.memory_percent > 95.0
            or self.active_agents > 800
        )


@dataclass
class CooldownState:
    """Cooldown state for adaptive spawning."""

    active: bool = False
    start_time: float = 0.0
    duration_seconds: float = 60.0
    observations: list[dict[str, Any]] = field(default_factory=list)

    def enter_cooldown(self, duration: float = 60.0) -> None:
        """Enter cooldown period."""
        self.active = True
        self.start_time = time.time()
        self.duration_seconds = duration
        self.observations.clear()

    def is_active(self) -> bool:
        """Check if still in cooldown."""
        if not self.active:
            return False

        elapsed = time.time() - self.start_time
        if elapsed >= self.duration_seconds:
            self.active = False
            return False

        return True

    def add_observation(self, observation: dict[str, Any]) -> None:
        """Add observation during cooldown."""
        if self.is_active():
            observation["timestamp"] = time.time()
            self.observations.append(observation)


class SpawnConstraints:
    """
    Manages spawn constraints, rate limiting, and adaptive control.

    Implements:
    - Hard caps (max agents, max depth, max budget)
    - Rate limiting (spawns per minute)
    - Adaptive spawn factor based on risk/load
    - Cooldown periods for observation
    """

    def __init__(
        self,
        max_concurrent_agents: int = 50,
        max_spawn_depth: int = 5,
        max_spawns_per_minute: int = 100,
        default_spawn_factor: int = 3,
        enable_adaptive_spawning: bool = True,
    ):
        """
        Initialize spawn constraints.

        Args:
            max_concurrent_agents: Maximum concurrent agents
            max_spawn_depth: Maximum generation depth
            max_spawns_per_minute: Rate limit for spawning
            default_spawn_factor: Base spawn multiplier
            enable_adaptive_spawning: Enable dynamic spawn adjustment
        """
        self.max_concurrent_agents = max_concurrent_agents
        self.max_spawn_depth = max_spawn_depth
        self.max_spawns_per_minute = max_spawns_per_minute
        self.default_spawn_factor = default_spawn_factor
        self.enable_adaptive_spawning = enable_adaptive_spawning

        # Rate limiting
        self.spawn_times: deque[float] = deque(maxlen=max_spawns_per_minute)

        # Budget tracking
        self.incident_budgets: dict[str, SpawnBudget] = {}
        self.global_budget = SpawnBudget(
            max_cpu_seconds=36000.0,  # 10 hours
            max_memory_mb=10240.0,  # 10GB
            max_spawns=max_concurrent_agents,
        )

        # Cooldown management
        self.cooldown_state = CooldownState()

        # Statistics
        self.total_spawns_attempted = 0
        self.total_spawns_rejected = 0
        self.rejection_reasons: dict[str, int] = defaultdict(int)

        logger.info(
            f"SpawnConstraints initialized: max_agents={max_concurrent_agents}, "
            f"max_depth={max_spawn_depth}, rate_limit={max_spawns_per_minute}/min"
        )

    def can_spawn(
        self,
        generation: int,
        incident_id: str,
        current_agent_count: int,
        system_load: SystemLoad | None = None,
    ) -> tuple[bool, str]:
        """
        Check if spawning is allowed under current constraints.

        Args:
            generation: Generation depth of spawn
            incident_id: Incident identifier for budget tracking
            current_agent_count: Current number of active agents
            system_load: Current system load metrics

        Returns:
            (allowed, reason) tuple
        """
        self.total_spawns_attempted += 1

        # Check max concurrent agents
        if current_agent_count >= self.max_concurrent_agents:
            self.total_spawns_rejected += 1
            self.rejection_reasons["max_concurrent"] += 1
            return False, "max_concurrent_agents_reached"

        # Check max spawn depth
        if generation >= self.max_spawn_depth:
            self.total_spawns_rejected += 1
            self.rejection_reasons["max_depth"] += 1
            return False, "max_spawn_depth_reached"

        # Check rate limit
        if not self._check_rate_limit():
            self.total_spawns_rejected += 1
            self.rejection_reasons["rate_limit"] += 1
            return False, "spawn_rate_limit_exceeded"

        # Check incident budget
        if incident_id not in self.incident_budgets:
            self.incident_budgets[incident_id] = SpawnBudget(
                max_spawns=min(50, self.max_concurrent_agents // 2)
            )

        if not self.incident_budgets[incident_id].can_spawn():
            self.total_spawns_rejected += 1
            self.rejection_reasons["incident_budget"] += 1
            return False, "incident_budget_exceeded"

        # Check global budget
        if not self.global_budget.can_spawn():
            self.total_spawns_rejected += 1
            self.rejection_reasons["global_budget"] += 1
            return False, "global_budget_exceeded"

        # Check system load (if provided)
        if system_load and system_load.is_critical_load():
            self.total_spawns_rejected += 1
            self.rejection_reasons["critical_load"] += 1
            return False, "system_under_critical_load"

        # Check cooldown
        if self.cooldown_state.is_active():
            self.total_spawns_rejected += 1
            self.rejection_reasons["cooldown"] += 1
            return False, "in_cooldown_period"

        return True, "allowed"

    def _check_rate_limit(self) -> bool:
        """Check if within spawn rate limit."""
        now = time.time()
        minute_ago = now - 60.0

        # Remove old entries
        while self.spawn_times and self.spawn_times[0] < minute_ago:
            self.spawn_times.popleft()

        # Check limit
        return len(self.spawn_times) < self.max_spawns_per_minute

    def record_spawn(
        self, incident_id: str, resource_cost: dict[str, float] | None = None
    ) -> None:
        """Record a successful spawn."""
        now = time.time()
        self.spawn_times.append(now)

        # Update budgets
        if resource_cost:
            if incident_id in self.incident_budgets:
                self.incident_budgets[incident_id].consume(resource_cost)
            self.global_budget.consume(resource_cost)
        else:
            # Default cost estimate
            default_cost = {"cpu_seconds": 1.0, "memory_mb": 50.0, "network_mb": 0.5}
            if incident_id in self.incident_budgets:
                self.incident_budgets[incident_id].consume(default_cost)
            self.global_budget.consume(default_cost)

    def compute_adaptive_spawn_factor(
        self,
        risk_score: float,
        confidence: float,
        system_load: SystemLoad,
        generation: int,
    ) -> int:
        """
        Compute adaptive spawn factor based on context.

        Args:
            risk_score: Risk score (0.0-1.0)
            confidence: Detection confidence (0.0-1.0)
            system_load: Current system load
            generation: Generation depth

        Returns:
            Spawn factor (1-5)
        """
        if not self.enable_adaptive_spawning:
            return self.default_spawn_factor

        # Start with base factor
        factor = self.default_spawn_factor

        # Adjust based on risk score
        if risk_score > 0.9:
            factor += 1  # High risk: spawn more
        elif risk_score < 0.3:
            factor = max(1, factor - 1)  # Low risk: spawn less

        # Adjust based on confidence
        if confidence < 0.5:
            factor = max(1, factor - 1)  # Low confidence: be conservative

        # Adjust based on system load
        if system_load.is_critical_load():
            factor = 1  # Critical load: minimal spawning
        elif system_load.is_high_load():
            factor = max(1, factor - 1)  # High load: reduce spawning

        # Adjust based on generation (decay with depth)
        if generation >= 3:
            factor = max(1, factor - 1)
        if generation >= 4:
            factor = 1  # Deep generations: minimal spawning

        # Cap at reasonable limits
        return max(1, min(5, factor))

    def enter_cooldown(
        self, duration: float = 60.0, reason: str = "adaptive_response"
    ) -> None:
        """Enter cooldown period for observation."""
        self.cooldown_state.enter_cooldown(duration)
        logger.warning("🧊 Entering cooldown period for %ss: %s", duration, reason)

    def should_enter_cooldown(
        self, recent_incidents: list[dict[str, Any]], system_load: SystemLoad
    ) -> bool:
        """
        Determine if system should enter cooldown.

        Args:
            recent_incidents: Recent incident data
            system_load: Current system load

        Returns:
            True if should enter cooldown
        """
        # Enter cooldown if system load is very high
        if system_load.is_critical_load():
            return True

        # Enter cooldown if too many incidents in short time
        if len(recent_incidents) > 10:
            recent_time = datetime.now() - timedelta(minutes=5)
            recent_count = sum(
                1
                for inc in recent_incidents
                if datetime.fromisoformat(inc.get("timestamp", "2000-01-01"))
                > recent_time
            )
            if recent_count > 5:
                return True

        return False

    def get_statistics(self) -> dict[str, Any]:
        """Get spawn constraint statistics."""
        return {
            "total_spawns_attempted": self.total_spawns_attempted,
            "total_spawns_rejected": self.total_spawns_rejected,
            "rejection_rate": (
                self.total_spawns_rejected / max(1, self.total_spawns_attempted)
            ),
            "rejection_reasons": dict(self.rejection_reasons),
            "current_rate_per_minute": len(self.spawn_times),
            "global_budget_utilization": self.global_budget.get_utilization(),
            "cooldown_active": self.cooldown_state.is_active(),
            "active_incident_budgets": len(self.incident_budgets),
        }


class ResourceMonitor:
    """Monitor system resources for adaptive control."""

    def __init__(self):
        """Initialize resource monitor."""
        self.cpu_samples: deque[float] = deque(maxlen=10)
        self.memory_samples: deque[float] = deque(maxlen=10)

    def get_system_load(self, active_agents: int, total_agents: int) -> SystemLoad:
        """
        Get current system load.

        Args:
            active_agents: Number of currently active agents
            total_agents: Total number of spawned agents

        Returns:
            SystemLoad metrics
        """
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent

            self.cpu_samples.append(cpu_percent)
            self.memory_samples.append(memory_percent)

            avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples)
            avg_memory = sum(self.memory_samples) / len(self.memory_samples)
        except ImportError:
            # psutil not available, use estimates
            avg_cpu = 0.0
            avg_memory = 0.0

        return SystemLoad(
            cpu_percent=avg_cpu,
            memory_percent=avg_memory,
            active_agents=active_agents,
            total_agents=total_agents,
        )


if __name__ == "__main__":
    # Example usage
    constraints = SpawnConstraints(
        max_concurrent_agents=100,
        max_spawn_depth=5,
        max_spawns_per_minute=20,
    )

    system_load = SystemLoad(cpu_percent=45.0, memory_percent=60.0, active_agents=30)

    # Check if can spawn
    can_spawn, reason = constraints.can_spawn(
        generation=2,
        incident_id="inc-001",
        current_agent_count=30,
        system_load=system_load,
    )
    print(f"Can spawn: {can_spawn}, Reason: {reason}")

    # Compute adaptive factor
    factor = constraints.compute_adaptive_spawn_factor(
        risk_score=0.85, confidence=0.9, system_load=system_load, generation=2
    )
    print(f"Adaptive spawn factor: {factor}")

    # Get statistics
    stats = constraints.get_statistics()
    print(f"Statistics: {stats}")
