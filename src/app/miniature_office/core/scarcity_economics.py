"""
Scarcity Economics System
Implements Civilization Tier Architecture - Part II (Scarcity Economics)

Why Decisions Matter Instead of Infinite AI Slop
Forces judgment through resource constraints
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from app.miniature_office.core.audit import EventType, get_audit_log


class ResourceType(Enum):
    """Types of scarce resources"""

    AGENT_TIME = "agent_time"  # Work capacity per tick
    MANAGER_ATTENTION = "manager_attention"  # Decisions per tick
    CONSENSUS_BANDWIDTH = "consensus_bandwidth"  # Votes per tick
    TOOL_SLOTS = "tool_slots"  # Concurrent tool usage
    SIMULATION_BUDGET = "simulation_budget"  # Forks / what-ifs


@dataclass
class ResourceAllocation:
    """
    Resource allocation for an entity.
    No resource may be infinite (II.1)
    """

    agent_time: int = 0  # Time units available
    manager_attention: int = 0  # Decision slots
    consensus_bandwidth: int = 0  # Vote capacity
    tool_slots: int = 0  # Concurrent tools
    simulation_budget: int = 0  # What-if simulations

    def to_dict(self) -> Dict:
        return {
            "agent_time": self.agent_time,
            "manager_attention": self.manager_attention,
            "consensus_bandwidth": self.consensus_bandwidth,
            "tool_slots": self.tool_slots,
            "simulation_budget": self.simulation_budget,
        }

    def has_capacity(self, resource_type: ResourceType, amount: int) -> bool:
        """Check if entity has capacity for resource"""
        if resource_type == ResourceType.AGENT_TIME:
            return self.agent_time >= amount
        elif resource_type == ResourceType.MANAGER_ATTENTION:
            return self.manager_attention >= amount
        elif resource_type == ResourceType.CONSENSUS_BANDWIDTH:
            return self.consensus_bandwidth >= amount
        elif resource_type == ResourceType.TOOL_SLOTS:
            return self.tool_slots >= amount
        elif resource_type == ResourceType.SIMULATION_BUDGET:
            return self.simulation_budget >= amount
        return False

    def consume(self, resource_type: ResourceType, amount: int) -> bool:
        """Consume a resource if available"""
        if not self.has_capacity(resource_type, amount):
            return False

        if resource_type == ResourceType.AGENT_TIME:
            self.agent_time -= amount
        elif resource_type == ResourceType.MANAGER_ATTENTION:
            self.manager_attention -= amount
        elif resource_type == ResourceType.CONSENSUS_BANDWIDTH:
            self.consensus_bandwidth -= amount
        elif resource_type == ResourceType.TOOL_SLOTS:
            self.tool_slots -= amount
        elif resource_type == ResourceType.SIMULATION_BUDGET:
            self.simulation_budget -= amount

        return True


@dataclass
class ResourceLedgerEntry:
    """
    Resource Ledger - Civilization Accounting (II.2)
    Tracks resources allocated and spent per tick
    """

    entity_id: str
    tick: int
    allocated: ResourceAllocation
    spent: ResourceAllocation = field(default_factory=ResourceAllocation)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def remaining(self) -> ResourceAllocation:
        """Calculate remaining resources"""
        return ResourceAllocation(
            agent_time=self.allocated.agent_time - self.spent.agent_time,
            manager_attention=self.allocated.manager_attention - self.spent.manager_attention,
            consensus_bandwidth=self.allocated.consensus_bandwidth - self.spent.consensus_bandwidth,
            tool_slots=self.allocated.tool_slots - self.spent.tool_slots,
            simulation_budget=self.allocated.simulation_budget - self.spent.simulation_budget,
        )

    def is_exhausted(self) -> bool:
        """Check if any resource is exhausted"""
        remaining = self.remaining()
        return (
            remaining.agent_time <= 0
            or remaining.manager_attention <= 0
            or remaining.consensus_bandwidth <= 0
            or remaining.tool_slots <= 0
            or remaining.simulation_budget <= 0
        )

    def to_dict(self) -> Dict:
        return {
            "entity_id": self.entity_id,
            "tick": self.tick,
            "allocated": self.allocated.to_dict(),
            "spent": self.spent.to_dict(),
            "remaining": self.remaining().to_dict(),
            "timestamp": self.timestamp.isoformat(),
        }


class TaskCostProfile:
    """
    Cost profile for tasks based on Economic Laws (II.3)
    """

    @staticmethod
    def calculate_cost(
        is_high_risk: bool = False, is_rework: bool = False, is_blocked: bool = False, is_meta_office: bool = False
    ) -> ResourceAllocation:
        """
        Calculate resource cost based on task characteristics.

        Economic Laws:
        - High-risk tasks cost more
        - Rework costs double
        - Blocked tasks still consume attention
        - Meta-Office decisions cost the most
        """
        base_cost = ResourceAllocation(
            agent_time=10, manager_attention=1, consensus_bandwidth=1, tool_slots=1, simulation_budget=0
        )

        multiplier = 1.0

        if is_high_risk:
            multiplier *= 1.5

        if is_rework:
            multiplier *= 2.0  # Rework costs double

        if is_blocked:
            # Blocked tasks still consume attention
            base_cost.manager_attention *= 2

        if is_meta_office:
            # Meta-Office decisions cost the most
            multiplier *= 3.0
            base_cost.manager_attention *= 3

        # Apply multiplier
        return ResourceAllocation(
            agent_time=int(base_cost.agent_time * multiplier),
            manager_attention=base_cost.manager_attention,
            consensus_bandwidth=int(base_cost.consensus_bandwidth * multiplier),
            tool_slots=base_cost.tool_slots,
            simulation_budget=base_cost.simulation_budget,
        )


@dataclass
class PriorityBid:
    """
    Priority Market - Optional but God-Tier (II.4)
    Tasks may bid for resources, trade priority, or be deferred
    """

    bid_id: str
    task_id: str
    resource_type: ResourceType
    amount_requested: int
    priority_offered: int  # Higher = more important
    justification: str
    submitted_at_tick: int
    status: str = "pending"  # pending, accepted, rejected

    def to_dict(self) -> Dict:
        return {
            "bid_id": self.bid_id,
            "task_id": self.task_id,
            "resource_type": self.resource_type.value,
            "amount_requested": self.amount_requested,
            "priority_offered": self.priority_offered,
            "justification": self.justification,
            "submitted_at_tick": self.submitted_at_tick,
            "status": self.status,
        }


class ResourceLedger:
    """
    Resource Ledger system for tracking all resource allocations.
    Implements Civilization Accounting (II.2)
    """

    def __init__(self):
        self.ledger: Dict[str, Dict[int, ResourceLedgerEntry]] = {}  # entity_id -> tick -> entry
        self.priority_market: Dict[str, PriorityBid] = {}

    def allocate_resources(self, entity_id: str, tick: int, allocation: ResourceAllocation) -> ResourceLedgerEntry:
        """Allocate resources to an entity for a tick"""
        if entity_id not in self.ledger:
            self.ledger[entity_id] = {}

        entry = ResourceLedgerEntry(entity_id=entity_id, tick=tick, allocated=allocation)

        self.ledger[entity_id][tick] = entry

        get_audit_log().log_event(
            EventType.AGENT_ACTION,
            target_id=entity_id,
            data={"action": "resources_allocated", "tick": tick, "allocation": allocation.to_dict()},
        )

        return entry

    def spend_resource(self, entity_id: str, tick: int, resource_type: ResourceType, amount: int) -> bool:
        """
        Spend a resource.
        Returns False if insufficient resources (triggers halt/reprioritization)
        """
        if entity_id not in self.ledger or tick not in self.ledger[entity_id]:
            return False

        entry = self.ledger[entity_id][tick]
        remaining = entry.remaining()

        if not remaining.has_capacity(resource_type, amount):
            # Budget exceeded - triggers civilization fault
            self._handle_budget_exceeded(entity_id, tick, resource_type)
            return False

        # Consume resource
        if resource_type == ResourceType.AGENT_TIME:
            entry.spent.agent_time += amount
        elif resource_type == ResourceType.MANAGER_ATTENTION:
            entry.spent.manager_attention += amount
        elif resource_type == ResourceType.CONSENSUS_BANDWIDTH:
            entry.spent.consensus_bandwidth += amount
        elif resource_type == ResourceType.TOOL_SLOTS:
            entry.spent.tool_slots += amount
        elif resource_type == ResourceType.SIMULATION_BUDGET:
            entry.spent.simulation_budget += amount

        get_audit_log().log_event(
            EventType.AGENT_ACTION,
            actor_id=entity_id,
            data={"action": "resource_spent", "tick": tick, "resource_type": resource_type.value, "amount": amount},
        )

        return True

    def _handle_budget_exceeded(self, entity_id: str, tick: int, resource_type: ResourceType):
        """
        Handle budget exceedance (II.2).
        Exceeding budget:
        - Halts execution
        - Forces reprioritization
        - Triggers escalation
        """
        get_audit_log().log_event(
            EventType.SECURITY_EVENT,
            actor_id=entity_id,
            data={"event": "budget_exceeded", "tick": tick, "resource_type": resource_type.value, "severity": "high"},
        )

        # In production, this would trigger:
        # 1. Halt execution
        # 2. Notification to managers
        # 3. Emergency reprioritization

    def get_ledger_entry(self, entity_id: str, tick: int) -> Optional[ResourceLedgerEntry]:
        """Get ledger entry for entity at tick"""
        if entity_id in self.ledger and tick in self.ledger[entity_id]:
            return self.ledger[entity_id][tick]
        return None

    def submit_priority_bid(self, bid: PriorityBid) -> str:
        """
        Submit a priority bid to the market (II.4).
        Enables emergent scheduling and strategic planning.
        """
        self.priority_market[bid.bid_id] = bid

        get_audit_log().log_event(
            EventType.AGENT_ACTION,
            target_id=bid.task_id,
            data={"action": "priority_bid_submitted", "bid": bid.to_dict()},
        )

        return bid.bid_id

    def resolve_priority_bids(self, tick: int) -> Dict[str, str]:
        """
        Resolve pending priority bids.
        Returns dict of bid_id -> status
        """
        pending_bids = [b for b in self.priority_market.values() if b.status == "pending"]

        # Sort by priority (higher priority wins)
        pending_bids.sort(key=lambda b: b.priority_offered, reverse=True)

        results = {}

        for bid in pending_bids:
            # Check if resources are available
            entry = self.get_ledger_entry(bid.task_id, tick)
            if entry and entry.remaining().has_capacity(bid.resource_type, bid.amount_requested):
                bid.status = "accepted"
                results[bid.bid_id] = "accepted"
            else:
                bid.status = "rejected"
                results[bid.bid_id] = "rejected"

        return results

    def get_entity_resources(self, entity_id: str, tick: int) -> Optional[ResourceAllocation]:
        """Get remaining resources for entity at tick"""
        entry = self.get_ledger_entry(entity_id, tick)
        if entry:
            return entry.remaining()
        return None


class EconomicLaws:
    """
    Enforcement of Economic Laws (II.3)
    This prevents infinite "thinking loops"
    """

    @staticmethod
    def enforce_no_free_parallelism(parallel_tasks: int) -> int:
        """
        Economic Law: No free parallelism
        Each parallel task consumes agent time
        """
        return parallel_tasks * 10  # Each parallel task costs 10 time units

    @staticmethod
    def calculate_rework_penalty(original_cost: int) -> int:
        """
        Economic Law: Rework costs double
        """
        return original_cost * 2

    @staticmethod
    def calculate_blocked_overhead(attention_cost: int) -> int:
        """
        Economic Law: Blocked tasks still consume attention
        """
        return attention_cost * 2

    @staticmethod
    def validate_meta_office_budget(requested: int, max_allowed: int) -> bool:
        """
        Economic Law: Meta-Office decisions cost the most
        """
        return requested <= max_allowed


# Global resource ledger
_resource_ledger = ResourceLedger()


def get_resource_ledger() -> ResourceLedger:
    """Get the global resource ledger"""
    return _resource_ledger
