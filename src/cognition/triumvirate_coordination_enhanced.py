#                                           [2026-04-09 Enhanced]
#                                          Productivity: Active
"""
Enhanced Triumvirate Coordination System

Provides advanced real-time coordination between Galahad, Cerberus, and Codex with:
- Sub-millisecond voting protocol for policy decisions
- Automatic deadlock resolution using priority-based tiebreaking
- Configurable priority-based arbitration (Security > Ethics > Consistency)
- Performance monitoring with voting latency and decision quality metrics
- Graceful degradation with Liara failover support

Architecture:
    Galahad (Ethics Pillar) - Reasoning and ethical oversight
    Cerberus (Security Pillar) - Policy enforcement and security
    Codex (Consistency Pillar) - ML inference and consistency checks
    
Priority Model:
    Security > Ethics > Consistency (default, configurable)
"""

import asyncio
import logging
import time
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class PillarType(Enum):
    """Triumvirate pillar types"""
    GALAHAD = "galahad"  # Ethics
    CERBERUS = "cerberus"  # Security
    CODEX = "codex"  # Consistency


class VoteType(Enum):
    """Vote decision types"""
    ALLOW = "allow"
    DENY = "deny"
    MODIFY = "modify"
    ABSTAIN = "abstain"


class Priority(Enum):
    """Priority levels for arbitration"""
    CRITICAL = 3  # Security-critical decisions
    HIGH = 2      # Ethics-related decisions
    NORMAL = 1    # Consistency and optimization
    LOW = 0       # Advisory votes


@dataclass
class Vote:
    """Represents a single vote from a pillar"""
    pillar: PillarType
    decision: VoteType
    confidence: float  # 0.0 to 1.0
    priority: Priority
    rationale: str
    timestamp: float = field(default_factory=time.perf_counter)
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate vote parameters"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be [0.0, 1.0], got {self.confidence}")


@dataclass
class VotingResult:
    """Result of a voting round"""
    decision: VoteType
    confidence: float
    votes: list[Vote]
    resolution_method: str  # 'unanimous', 'majority', 'priority', 'deadlock_broken'
    latency_ms: float
    participating_pillars: list[PillarType]
    metadata: dict = field(default_factory=dict)


@dataclass
class PerformanceMetrics:
    """Performance and quality metrics for the coordination system"""
    total_votes: int = 0
    avg_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    max_latency_ms: float = 0.0
    decisions_by_type: dict = field(default_factory=lambda: {
        VoteType.ALLOW: 0,
        VoteType.DENY: 0,
        VoteType.MODIFY: 0,
        VoteType.ABSTAIN: 0
    })
    deadlocks_resolved: int = 0
    unanimous_decisions: int = 0
    priority_overrides: int = 0
    pillar_failures: dict = field(default_factory=lambda: {
        PillarType.GALAHAD: 0,
        PillarType.CERBERUS: 0,
        PillarType.CODEX: 0
    })
    liara_activations: int = 0
    avg_confidence: float = 0.0
    
    def update_latency(self, latency_ms: float):
        """Update latency statistics"""
        self.avg_latency_ms = (self.avg_latency_ms * self.total_votes + latency_ms) / (self.total_votes + 1)
        self.min_latency_ms = min(self.min_latency_ms, latency_ms)
        self.max_latency_ms = max(self.max_latency_ms, latency_ms)
    
    def update_confidence(self, confidence: float):
        """Update average confidence"""
        self.avg_confidence = (self.avg_confidence * self.total_votes + confidence) / (self.total_votes + 1)
    
    def record_decision(self, result: VotingResult):
        """Record a voting decision"""
        self.total_votes += 1
        self.decisions_by_type[result.decision] += 1
        self.update_latency(result.latency_ms)
        self.update_confidence(result.confidence)
        
        if result.resolution_method == 'unanimous':
            self.unanimous_decisions += 1
        elif 'deadlock' in result.resolution_method:
            self.deadlocks_resolved += 1
        elif 'priority' in result.resolution_method:
            self.priority_overrides += 1


@dataclass
class CoordinationConfig:
    """Configuration for enhanced coordination"""
    # Priority ordering (highest to lowest)
    priority_order: list[PillarType] = field(default_factory=lambda: [
        PillarType.CERBERUS,  # Security first
        PillarType.GALAHAD,   # Ethics second
        PillarType.CODEX      # Consistency third
    ])
    
    # Voting timeout in seconds
    voting_timeout: float = 0.001  # 1ms for sub-millisecond target
    
    # Minimum confidence threshold for decisions
    min_confidence: float = 0.5
    
    # Enable automatic Liara failover
    enable_liara_failover: bool = True
    
    # Pillar health check interval (seconds)
    health_check_interval: float = 1.0
    
    # Enable performance monitoring
    enable_metrics: bool = True
    
    # Deadlock resolution strategy
    deadlock_strategy: str = "priority"  # 'priority', 'highest_confidence', 'random'
    
    # Enable async voting (faster but requires async context)
    async_voting: bool = True


class EnhancedTriumvirateCoordinator:
    """
    Enhanced coordination system for Triumvirate pillars
    
    Features:
    - Sub-millisecond voting protocol
    - Priority-based arbitration
    - Automatic deadlock resolution
    - Performance metrics collection
    - Graceful degradation with Liara failover
    """
    
    def __init__(
        self,
        config: Optional[CoordinationConfig] = None,
        galahad_engine=None,
        cerberus_engine=None,
        codex_engine=None,
        liara_bridge=None
    ):
        """
        Initialize enhanced coordinator
        
        Args:
            config: Coordination configuration
            galahad_engine: Galahad engine instance
            cerberus_engine: Cerberus engine instance
            codex_engine: Codex engine instance
            liara_bridge: Optional Liara bridge for failover
        """
        self.config = config or CoordinationConfig()
        self.galahad = galahad_engine
        self.cerberus = cerberus_engine
        self.codex = codex_engine
        self.liara_bridge = liara_bridge
        
        # Performance metrics
        self.metrics = PerformanceMetrics() if self.config.enable_metrics else None
        
        # Pillar health status
        self.pillar_health = {
            PillarType.GALAHAD: True,
            PillarType.CERBERUS: True,
            PillarType.CODEX: True
        }
        
        # Vote history for analysis
        self.vote_history: list[VotingResult] = []
        
        # Last health check time
        self._last_health_check = time.time()
        
        logger.info("Enhanced Triumvirate Coordinator initialized")
        logger.info(f"Priority order: {[p.value for p in self.config.priority_order]}")
        logger.info(f"Voting timeout: {self.config.voting_timeout * 1000:.3f}ms")
    
    async def vote_async(
        self,
        decision_id: str,
        context: dict,
        timeout: Optional[float] = None
    ) -> VotingResult:
        """
        Asynchronous voting protocol for sub-millisecond latency
        
        Args:
            decision_id: Unique identifier for the decision
            context: Decision context with data and metadata
            timeout: Optional timeout override
            
        Returns:
            VotingResult with decision and metrics
        """
        start_time = time.perf_counter()
        timeout = timeout or self.config.voting_timeout
        
        logger.debug(f"Starting async vote {decision_id}")
        
        # Check pillar health before voting
        self._check_pillar_health()
        
        # Collect votes from all healthy pillars concurrently
        vote_tasks = []
        for pillar_type in PillarType:
            if self.pillar_health[pillar_type]:
                vote_tasks.append(self._collect_vote_async(pillar_type, context))
        
        # Wait for all votes with timeout
        try:
            votes = await asyncio.wait_for(
                asyncio.gather(*vote_tasks, return_exceptions=True),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning(f"Vote {decision_id} timed out after {timeout*1000:.3f}ms")
            votes = [v for v in vote_tasks if v.done()]
        
        # Filter out exceptions and failed votes
        valid_votes = [v for v in votes if isinstance(v, Vote)]
        
        # Handle degraded state if too few votes
        if len(valid_votes) == 0:
            return await self._handle_total_failure(decision_id, context, start_time)
        
        # Resolve votes to final decision
        result = self._resolve_votes(valid_votes, start_time)
        
        # Record metrics
        if self.metrics:
            self.metrics.record_decision(result)
        
        # Store in history
        self.vote_history.append(result)
        
        logger.info(
            f"Vote {decision_id} complete: {result.decision.value} "
            f"({result.latency_ms:.3f}ms, confidence={result.confidence:.2f})"
        )
        
        return result
    
    def vote_sync(
        self,
        decision_id: str,
        context: dict,
        timeout: Optional[float] = None
    ) -> VotingResult:
        """
        Synchronous voting protocol (fallback when async not available)
        
        Args:
            decision_id: Unique identifier for the decision
            context: Decision context with data and metadata
            timeout: Optional timeout override
            
        Returns:
            VotingResult with decision and metrics
        """
        start_time = time.perf_counter()
        timeout = timeout or self.config.voting_timeout
        
        logger.debug(f"Starting sync vote {decision_id}")
        
        # Check pillar health
        self._check_pillar_health()
        
        # Collect votes sequentially with timeout
        votes = []
        for pillar_type in PillarType:
            if time.perf_counter() - start_time > timeout:
                logger.warning(f"Vote {decision_id} timeout during collection")
                break
            
            if self.pillar_health[pillar_type]:
                try:
                    vote = self._collect_vote_sync(pillar_type, context)
                    votes.append(vote)
                except Exception as e:
                    logger.error(f"Failed to collect vote from {pillar_type.value}: {e}")
                    self._mark_pillar_failed(pillar_type)
        
        # Handle total failure
        if len(votes) == 0:
            return self._handle_total_failure_sync(decision_id, context, start_time)
        
        # Resolve votes
        result = self._resolve_votes(votes, start_time)
        
        # Record metrics
        if self.metrics:
            self.metrics.record_decision(result)
        
        # Store in history
        self.vote_history.append(result)
        
        logger.info(
            f"Vote {decision_id} complete: {result.decision.value} "
            f"({result.latency_ms:.3f}ms, confidence={result.confidence:.2f})"
        )
        
        return result
    
    async def _collect_vote_async(self, pillar: PillarType, context: dict) -> Vote:
        """Collect vote from a pillar asynchronously"""
        try:
            if pillar == PillarType.GALAHAD and self.galahad:
                return await self._vote_galahad_async(context)
            elif pillar == PillarType.CERBERUS and self.cerberus:
                return await self._vote_cerberus_async(context)
            elif pillar == PillarType.CODEX and self.codex:
                return await self._vote_codex_async(context)
            else:
                raise ValueError(f"Pillar {pillar.value} not configured")
        except Exception as e:
            logger.error(f"Error collecting vote from {pillar.value}: {e}")
            self._mark_pillar_failed(pillar)
            raise
    
    def _collect_vote_sync(self, pillar: PillarType, context: dict) -> Vote:
        """Collect vote from a pillar synchronously"""
        if pillar == PillarType.GALAHAD and self.galahad:
            return self._vote_galahad_sync(context)
        elif pillar == PillarType.CERBERUS and self.cerberus:
            return self._vote_cerberus_sync(context)
        elif pillar == PillarType.CODEX and self.codex:
            return self._vote_codex_sync(context)
        else:
            raise ValueError(f"Pillar {pillar.value} not configured")
    
    async def _vote_galahad_async(self, context: dict) -> Vote:
        """Get Galahad's vote (ethics perspective)"""
        # Call Galahad reasoning engine
        result = self.galahad.reason([context.get('data')], context)
        
        # Map result to vote
        decision = VoteType.ALLOW
        if not result.get('success', True):
            decision = VoteType.DENY
        elif result.get('contradictions'):
            decision = VoteType.MODIFY
        
        return Vote(
            pillar=PillarType.GALAHAD,
            decision=decision,
            confidence=result.get('confidence', 0.7),
            priority=Priority.HIGH,  # Ethics has high priority
            rationale=result.get('explanation', 'Galahad reasoning complete'),
            metadata={'result': result}
        )
    
    def _vote_galahad_sync(self, context: dict) -> Vote:
        """Synchronous Galahad vote"""
        result = self.galahad.reason([context.get('data')], context)
        
        decision = VoteType.ALLOW
        if not result.get('success', True):
            decision = VoteType.DENY
        elif result.get('contradictions'):
            decision = VoteType.MODIFY
        
        return Vote(
            pillar=PillarType.GALAHAD,
            decision=decision,
            confidence=result.get('confidence', 0.7),
            priority=Priority.HIGH,
            rationale=result.get('explanation', 'Galahad reasoning complete'),
            metadata={'result': result}
        )
    
    async def _vote_cerberus_async(self, context: dict) -> Vote:
        """Get Cerberus's vote (security perspective)"""
        # Call Cerberus validation
        result = self.cerberus.validate_input(context.get('data'), context)
        
        # Map result to vote
        if result.get('valid'):
            decision = VoteType.ALLOW
        elif result.get('modified'):
            decision = VoteType.MODIFY
        else:
            decision = VoteType.DENY
        
        return Vote(
            pillar=PillarType.CERBERUS,
            decision=decision,
            confidence=0.95 if result.get('valid') else 0.9,
            priority=Priority.CRITICAL,  # Security has critical priority
            rationale=result.get('reason', 'Cerberus validation complete'),
            metadata={'result': result}
        )
    
    def _vote_cerberus_sync(self, context: dict) -> Vote:
        """Synchronous Cerberus vote"""
        result = self.cerberus.validate_input(context.get('data'), context)
        
        if result.get('valid'):
            decision = VoteType.ALLOW
        elif result.get('modified'):
            decision = VoteType.MODIFY
        else:
            decision = VoteType.DENY
        
        return Vote(
            pillar=PillarType.CERBERUS,
            decision=decision,
            confidence=0.95 if result.get('valid') else 0.9,
            priority=Priority.CRITICAL,
            rationale=result.get('reason', 'Cerberus validation complete'),
            metadata={'result': result}
        )
    
    async def _vote_codex_async(self, context: dict) -> Vote:
        """Get Codex's vote (consistency perspective)"""
        # Call Codex inference
        result = self.codex.process(context.get('data'), context)
        
        # Map result to vote
        decision = VoteType.ALLOW if result.get('success') else VoteType.DENY
        
        return Vote(
            pillar=PillarType.CODEX,
            decision=decision,
            confidence=0.8 if result.get('success') else 0.6,
            priority=Priority.NORMAL,  # Consistency has normal priority
            rationale='Codex inference complete',
            metadata={'result': result}
        )
    
    def _vote_codex_sync(self, context: dict) -> Vote:
        """Synchronous Codex vote"""
        result = self.codex.process(context.get('data'), context)
        
        decision = VoteType.ALLOW if result.get('success') else VoteType.DENY
        
        return Vote(
            pillar=PillarType.CODEX,
            decision=decision,
            confidence=0.8 if result.get('success') else 0.6,
            priority=Priority.NORMAL,
            rationale='Codex inference complete',
            metadata={'result': result}
        )
    
    def _resolve_votes(self, votes: list[Vote], start_time: float) -> VotingResult:
        """
        Resolve votes using priority-based arbitration with deadlock handling
        
        Resolution order:
        1. Unanimous decision -> use it
        2. Majority decision -> use it
        3. Deadlock -> apply priority-based tiebreaking
        """
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        # Count decisions
        decision_counts = Counter(v.decision for v in votes)
        
        # Check for unanimous decision
        if len(decision_counts) == 1:
            decision = votes[0].decision
            confidence = sum(v.confidence for v in votes) / len(votes)
            return VotingResult(
                decision=decision,
                confidence=confidence,
                votes=votes,
                resolution_method='unanimous',
                latency_ms=latency_ms,
                participating_pillars=[v.pillar for v in votes]
            )
        
        # Check for majority decision
        most_common = decision_counts.most_common(1)[0]
        if most_common[1] > len(votes) / 2:
            decision = most_common[0]
            # Average confidence of majority votes
            majority_votes = [v for v in votes if v.decision == decision]
            confidence = sum(v.confidence for v in majority_votes) / len(majority_votes)
            return VotingResult(
                decision=decision,
                confidence=confidence,
                votes=votes,
                resolution_method='majority',
                latency_ms=latency_ms,
                participating_pillars=[v.pillar for v in votes]
            )
        
        # Deadlock - apply priority-based tiebreaking
        return self._resolve_deadlock(votes, latency_ms)
    
    def _resolve_deadlock(self, votes: list[Vote], latency_ms: float) -> VotingResult:
        """
        Resolve deadlock using configured strategy
        
        Default: Priority-based (Security > Ethics > Consistency)
        """
        logger.warning(f"Deadlock detected with {len(votes)} votes, applying {self.config.deadlock_strategy}")
        
        if self.config.deadlock_strategy == "priority":
            # Sort by priority order defined in config
            for pillar_type in self.config.priority_order:
                pillar_votes = [v for v in votes if v.pillar == pillar_type]
                if pillar_votes:
                    # Use the highest priority pillar's vote
                    winning_vote = pillar_votes[0]
                    return VotingResult(
                        decision=winning_vote.decision,
                        confidence=winning_vote.confidence * 0.8,  # Reduce confidence for deadlock
                        votes=votes,
                        resolution_method=f'deadlock_broken_by_priority_{pillar_type.value}',
                        latency_ms=latency_ms,
                        participating_pillars=[v.pillar for v in votes],
                        metadata={'tiebreaker': pillar_type.value}
                    )
        
        elif self.config.deadlock_strategy == "highest_confidence":
            # Use vote with highest confidence
            winning_vote = max(votes, key=lambda v: v.confidence)
            return VotingResult(
                decision=winning_vote.decision,
                confidence=winning_vote.confidence * 0.9,
                votes=votes,
                resolution_method='deadlock_broken_by_confidence',
                latency_ms=latency_ms,
                participating_pillars=[v.pillar for v in votes],
                metadata={'tiebreaker': winning_vote.pillar.value}
            )
        
        else:
            # Random selection (least preferred)
            import random
            winning_vote = random.choice(votes)
            return VotingResult(
                decision=winning_vote.decision,
                confidence=winning_vote.confidence * 0.7,
                votes=votes,
                resolution_method='deadlock_broken_randomly',
                latency_ms=latency_ms,
                participating_pillars=[v.pillar for v in votes],
                metadata={'tiebreaker': 'random'}
            )
    
    async def _handle_total_failure(
        self,
        decision_id: str,
        context: dict,
        start_time: float
    ) -> VotingResult:
        """Handle total pillar failure with Liara failover"""
        logger.error(f"Total pillar failure for decision {decision_id}")
        
        # Record metrics
        if self.metrics:
            for pillar in PillarType:
                if not self.pillar_health[pillar]:
                    self.metrics.pillar_failures[pillar] += 1
        
        # Attempt Liara failover if enabled
        if self.config.enable_liara_failover and self.liara_bridge:
            logger.info("Activating Liara failover")
            if self.metrics:
                self.metrics.liara_activations += 1
            
            try:
                # Liara makes emergency decision
                liara_decision = await self._liara_emergency_decision(context)
                latency_ms = (time.perf_counter() - start_time) * 1000
                
                return VotingResult(
                    decision=liara_decision,
                    confidence=0.6,  # Lower confidence for emergency mode
                    votes=[],
                    resolution_method='liara_emergency_failover',
                    latency_ms=latency_ms,
                    participating_pillars=[],
                    metadata={'failover': 'liara', 'reason': 'total_pillar_failure'}
                )
            except Exception as e:
                logger.error(f"Liara failover failed: {e}")
        
        # Last resort: deny for safety
        latency_ms = (time.perf_counter() - start_time) * 1000
        return VotingResult(
            decision=VoteType.DENY,
            confidence=0.5,
            votes=[],
            resolution_method='emergency_deny',
            latency_ms=latency_ms,
            participating_pillars=[],
            metadata={'reason': 'total_failure_safety_deny'}
        )
    
    def _handle_total_failure_sync(
        self,
        decision_id: str,
        context: dict,
        start_time: float
    ) -> VotingResult:
        """Synchronous version of total failure handler"""
        logger.error(f"Total pillar failure for decision {decision_id}")
        
        if self.metrics:
            for pillar in PillarType:
                if not self.pillar_health[pillar]:
                    self.metrics.pillar_failures[pillar] += 1
        
        # Emergency deny for safety
        latency_ms = (time.perf_counter() - start_time) * 1000
        return VotingResult(
            decision=VoteType.DENY,
            confidence=0.5,
            votes=[],
            resolution_method='emergency_deny',
            latency_ms=latency_ms,
            participating_pillars=[],
            metadata={'reason': 'total_failure_safety_deny'}
        )
    
    async def _liara_emergency_decision(self, context: dict) -> VoteType:
        """Make emergency decision via Liara"""
        # This would integrate with actual Liara system
        # For now, return safe default
        logger.info("Liara making emergency decision")
        return VoteType.DENY  # Fail safe
    
    def _check_pillar_health(self):
        """Check health of all pillars"""
        current_time = time.time()
        
        # Only check at configured interval
        if current_time - self._last_health_check < self.config.health_check_interval:
            return
        
        self._last_health_check = current_time
        
        # Check each pillar
        for pillar_type in PillarType:
            try:
                if pillar_type == PillarType.GALAHAD and self.galahad:
                    # Try to get status
                    _ = self.galahad.get_curiosity_metrics()
                    self.pillar_health[pillar_type] = True
                elif pillar_type == PillarType.CERBERUS and self.cerberus:
                    _ = self.cerberus.get_statistics()
                    self.pillar_health[pillar_type] = True
                elif pillar_type == PillarType.CODEX and self.codex:
                    _ = self.codex.get_status()
                    self.pillar_health[pillar_type] = True
            except Exception as e:
                logger.error(f"Health check failed for {pillar_type.value}: {e}")
                self._mark_pillar_failed(pillar_type)
    
    def _mark_pillar_failed(self, pillar: PillarType):
        """Mark a pillar as failed"""
        if self.pillar_health[pillar]:
            logger.error(f"Pillar {pillar.value} marked as FAILED")
            self.pillar_health[pillar] = False
            
            if self.metrics:
                self.metrics.pillar_failures[pillar] += 1
    
    def get_metrics(self) -> Optional[PerformanceMetrics]:
        """Get current performance metrics"""
        return self.metrics
    
    def get_health_status(self) -> dict:
        """Get health status of all pillars"""
        return {
            'pillars': {
                pillar.value: {
                    'healthy': self.pillar_health[pillar],
                    'status': 'operational' if self.pillar_health[pillar] else 'failed'
                }
                for pillar in PillarType
            },
            'overall_healthy': all(self.pillar_health.values()),
            'healthy_count': sum(1 for h in self.pillar_health.values() if h),
            'failed_count': sum(1 for h in self.pillar_health.values() if not h)
        }
    
    def get_vote_history(self, limit: int = 100) -> list[VotingResult]:
        """Get recent voting history"""
        return self.vote_history[-limit:]
    
    def reset_metrics(self):
        """Reset performance metrics"""
        if self.metrics:
            self.metrics = PerformanceMetrics()
            logger.info("Performance metrics reset")
    
    def restore_pillar(self, pillar: PillarType):
        """Manually restore a failed pillar"""
        if not self.pillar_health[pillar]:
            logger.info(f"Restoring pillar {pillar.value}")
            self.pillar_health[pillar] = True
