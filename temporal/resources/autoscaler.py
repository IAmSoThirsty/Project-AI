"""
AutoScaler - Dynamic scaling based on metrics
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional

from .types import (
    ScalingDecision,
    ScalingDirection,
    ScalingMetrics,
)

logger = logging.getLogger(__name__)


class AutoScaler:
    """
    Autoscaling system for agent fleet management.
    
    Scales agent count based on:
    - Queue depth
    - Request latency (avg, p95, p99)
    - Resource utilization
    """
    
    def __init__(
        self,
        min_agents: int = 1,
        max_agents: int = 1000,
        target_queue_depth: int = 10,
        target_latency_ms: float = 100.0,
        scale_up_threshold: float = 0.8,
        scale_down_threshold: float = 0.2,
        cooldown_seconds: int = 300,
    ):
        """
        Initialize autoscaler.
        
        Args:
            min_agents: Minimum number of agents
            max_agents: Maximum number of agents
            target_queue_depth: Target queue depth per agent
            target_latency_ms: Target average latency in ms
            scale_up_threshold: Utilization threshold for scaling up
            scale_down_threshold: Utilization threshold for scaling down
            cooldown_seconds: Cooldown period between scaling operations
        """
        self.min_agents = min_agents
        self.max_agents = max_agents
        self.target_queue_depth = target_queue_depth
        self.target_latency_ms = target_latency_ms
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        self.cooldown_seconds = cooldown_seconds
        
        self._last_scale_time: Optional[datetime] = None
        self._scaling_history: List[ScalingDecision] = []
        self._metrics_history: List[ScalingMetrics] = []
        
        logger.info(
            f"Initialized AutoScaler: min={min_agents}, max={max_agents}, "
            f"target_queue={target_queue_depth}, target_latency={target_latency_ms}ms"
        )
    
    async def evaluate(
        self,
        metrics: ScalingMetrics,
    ) -> ScalingDecision:
        """
        Evaluate metrics and decide on scaling action.
        
        Args:
            metrics: Current system metrics
            
        Returns:
            Scaling decision
        """
        self._metrics_history.append(metrics)
        
        # Keep only last 100 metrics
        if len(self._metrics_history) > 100:
            self._metrics_history = self._metrics_history[-100:]
        
        # Check cooldown
        if self._last_scale_time:
            elapsed = (datetime.utcnow() - self._last_scale_time).total_seconds()
            if elapsed < self.cooldown_seconds:
                logger.debug(f"In cooldown period ({elapsed}s < {self.cooldown_seconds}s)")
                return ScalingDecision(
                    direction=ScalingDirection.NONE,
                    target_count=metrics.active_agents,
                    current_count=metrics.active_agents,
                    reason=f"Cooldown ({int(self.cooldown_seconds - elapsed)}s remaining)",
                    metrics=metrics,
                )
        
        # Calculate scaling signals
        queue_signal = self._evaluate_queue_depth(metrics)
        latency_signal = self._evaluate_latency(metrics)
        utilization_signal = self._evaluate_utilization(metrics)
        
        # Combine signals
        scale_up_votes = sum([
            queue_signal == ScalingDirection.UP,
            latency_signal == ScalingDirection.UP,
            utilization_signal == ScalingDirection.UP,
        ])
        
        scale_down_votes = sum([
            queue_signal == ScalingDirection.DOWN,
            latency_signal == ScalingDirection.DOWN,
            utilization_signal == ScalingDirection.DOWN,
        ])
        
        # Decision logic
        if scale_up_votes >= 2:
            direction = ScalingDirection.UP
            target_count = self._calculate_scale_up_target(metrics)
            reason = f"Scale up: queue={queue_signal}, latency={latency_signal}, util={utilization_signal}"
        elif scale_down_votes >= 2:
            direction = ScalingDirection.DOWN
            target_count = self._calculate_scale_down_target(metrics)
            reason = f"Scale down: queue={queue_signal}, latency={latency_signal}, util={utilization_signal}"
        else:
            direction = ScalingDirection.NONE
            target_count = metrics.active_agents
            reason = "No consensus on scaling direction"
        
        decision = ScalingDecision(
            direction=direction,
            target_count=target_count,
            current_count=metrics.active_agents,
            reason=reason,
            metrics=metrics,
        )
        
        if direction != ScalingDirection.NONE:
            self._scaling_history.append(decision)
            self._last_scale_time = datetime.utcnow()
            logger.info(
                f"Scaling decision: {direction.value} from {metrics.active_agents} to {target_count} - {reason}"
            )
        
        return decision
    
    def _evaluate_queue_depth(self, metrics: ScalingMetrics) -> ScalingDirection:
        """Evaluate queue depth signal"""
        queue_per_agent = metrics.queue_depth / max(metrics.active_agents, 1)
        
        if queue_per_agent > self.target_queue_depth * 1.5:
            return ScalingDirection.UP
        elif queue_per_agent < self.target_queue_depth * 0.5:
            return ScalingDirection.DOWN
        else:
            return ScalingDirection.NONE
    
    def _evaluate_latency(self, metrics: ScalingMetrics) -> ScalingDirection:
        """Evaluate latency signal"""
        if metrics.p95_latency_ms > self.target_latency_ms * 2:
            return ScalingDirection.UP
        elif metrics.avg_latency_ms < self.target_latency_ms * 0.5:
            return ScalingDirection.DOWN
        else:
            return ScalingDirection.NONE
    
    def _evaluate_utilization(self, metrics: ScalingMetrics) -> ScalingDirection:
        """Evaluate resource utilization signal"""
        avg_util = (
            metrics.cpu_utilization +
            metrics.memory_utilization +
            metrics.gpu_utilization
        ) / 3.0
        
        if avg_util > self.scale_up_threshold * 100:
            return ScalingDirection.UP
        elif avg_util < self.scale_down_threshold * 100:
            return ScalingDirection.DOWN
        else:
            return ScalingDirection.NONE
    
    def _calculate_scale_up_target(self, metrics: ScalingMetrics) -> int:
        """Calculate target agent count for scale up"""
        # Use queue depth to estimate needed capacity
        needed_agents = max(
            int(metrics.queue_depth / self.target_queue_depth),
            int(metrics.active_agents * 1.5),  # At least 50% increase
        )
        
        return min(needed_agents, self.max_agents)
    
    def _calculate_scale_down_target(self, metrics: ScalingMetrics) -> int:
        """Calculate target agent count for scale down"""
        # Conservative scale down - reduce by 25%
        target = int(metrics.active_agents * 0.75)
        return max(target, self.min_agents)
    
    async def get_recommendations(
        self,
        lookback_minutes: int = 60,
    ) -> Dict[str, any]:
        """
        Get scaling recommendations based on historical data.
        
        Args:
            lookback_minutes: Minutes of history to analyze
            
        Returns:
            Dictionary with recommendations
        """
        cutoff = datetime.utcnow() - timedelta(minutes=lookback_minutes)
        recent_metrics = [
            m for m in self._metrics_history
            if m.timestamp >= cutoff
        ]
        
        if not recent_metrics:
            return {
                "status": "insufficient_data",
                "message": "Not enough historical data",
            }
        
        # Calculate statistics
        avg_queue = sum(m.queue_depth for m in recent_metrics) / len(recent_metrics)
        avg_latency = sum(m.avg_latency_ms for m in recent_metrics) / len(recent_metrics)
        avg_agents = sum(m.active_agents for m in recent_metrics) / len(recent_metrics)
        
        # Calculate recommended target
        queue_based = int(avg_queue / self.target_queue_depth)
        latency_based = int(avg_agents * (avg_latency / self.target_latency_ms))
        recommended = max(queue_based, latency_based)
        recommended = max(self.min_agents, min(recommended, self.max_agents))
        
        return {
            "status": "ok",
            "recommended_agents": recommended,
            "current_avg": int(avg_agents),
            "metrics": {
                "avg_queue_depth": avg_queue,
                "avg_latency_ms": avg_latency,
                "samples": len(recent_metrics),
            },
        }
    
    async def get_scaling_history(
        self,
        limit: int = 10,
    ) -> List[ScalingDecision]:
        """Get recent scaling decisions"""
        return self._scaling_history[-limit:]
