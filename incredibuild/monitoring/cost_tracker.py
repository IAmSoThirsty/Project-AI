#!/usr/bin/env python3
"""
Cost Tracker - Tracks and manages build costs
"""

import time
import logging
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger("CostTracker")


@dataclass
class CostRecord:
    """Record of a build cost"""
    timestamp: float
    build_id: str
    duration: float
    job_count: int
    node_hours: float
    cost: float


class CostTracker:
    """Tracks build costs and enforces budgets"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cost_config = config.get('cost', {})
        
        self.daily_limit = self.cost_config.get('daily_limit', 50.0)
        self.monthly_limit = self.cost_config.get('monthly_limit', 1000.0)
        self.per_build_limit = self.cost_config.get('per_build_limit', 5.0)
        
        self.records: List[CostRecord] = []
    
    def check_budget(self) -> bool:
        """Check if we're within budget limits"""
        now = time.time()
        
        # Check daily limit
        daily_start = now - (24 * 3600)
        daily_cost = sum(r.cost for r in self.records if r.timestamp >= daily_start)
        
        if daily_cost >= self.daily_limit:
            logger.error(f"Daily budget limit exceeded: ${daily_cost:.2f} / ${self.daily_limit:.2f}")
            return False
        
        # Check monthly limit
        monthly_start = now - (30 * 24 * 3600)
        monthly_cost = sum(r.cost for r in self.records if r.timestamp >= monthly_start)
        
        if monthly_cost >= self.monthly_limit:
            logger.error(f"Monthly budget limit exceeded: ${monthly_cost:.2f} / ${self.monthly_limit:.2f}")
            return False
        
        logger.info(f"Budget check passed - Daily: ${daily_cost:.2f}/{self.daily_limit:.2f}, Monthly: ${monthly_cost:.2f}/{self.monthly_limit:.2f}")
        return True
    
    def record_build(self, duration: float, job_count: int) -> None:
        """Record a build's cost"""
        # Estimate cost based on node usage
        # Assume c5.2xlarge spot @ $0.085/hr
        node_hours = (duration / 3600) * job_count * 0.1  # Simplified
        cost = node_hours * 0.085
        
        # Cap at per-build limit
        cost = min(cost, self.per_build_limit)
        
        record = CostRecord(
            timestamp=time.time(),
            build_id=f"build-{int(time.time())}",
            duration=duration,
            job_count=job_count,
            node_hours=node_hours,
            cost=cost,
        )
        
        self.records.append(record)
        logger.info(f"Build cost recorded: ${cost:.2f}")
    
    def get_daily_cost(self) -> float:
        """Get total cost for last 24 hours"""
        cutoff = time.time() - (24 * 3600)
        return sum(r.cost for r in self.records if r.timestamp >= cutoff)
    
    def get_monthly_cost(self) -> float:
        """Get total cost for last 30 days"""
        cutoff = time.time() - (30 * 24 * 3600)
        return sum(r.cost for r in self.records if r.timestamp >= cutoff)
