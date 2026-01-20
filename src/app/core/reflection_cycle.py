"""
AGI Reflection Cycle - Daily and Weekly Self-Processing

This module implements the reflection cycle system that enables the AGI
to process experiences, update worldview, and compress memories.

=== FORMAL SPECIFICATION ===

## 7. REFLECTION CYCLE

The Reflection Cycle is a periodic self-processing mechanism that enables
the AGI to learn from experience and maintain cognitive health.

### Reflection Schedule:

#### Daily Reflection:
- Reflect on interactions
- Update worldview based on experiences
- Summarize key memories
- Identify patterns and insights
- Update perspective based on outcomes

#### Weekly Reflection:
- Compress/clean memory
- Consolidate episodic memories into semantic knowledge
- Identify memory decay and reinforce important memories
- Update meta-identity reflections
- Generate growth insights

### Personality/Communication/Reasoning Adjustments:
- Adjust naturally based on reflection insights
- NOT on a fixed schedule
- Driven by significant experiences or patterns
- Constrained by Triumvirate governance

### Reflection Outputs:
- Perspective updates (trait adjustments)
- Memory consolidation (episodic → semantic)
- Meta-identity insights (self-awareness growth)
- Identity events (significant realizations)

### Integration Points:
- Queries MemoryEngine for recent experiences
- Updates PerspectiveEngine based on patterns
- Adds meta-reflections to Identity system
- Triggers memory consolidation
- Reports insights to user (optional)

=== END FORMAL SPECIFICATION ===
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Type Definitions
# ============================================================================

class ReflectionType(Enum):
    """Types of reflection cycles."""
    DAILY = "daily"
    WEEKLY = "weekly"
    TRIGGERED = "triggered"  # Triggered by significant event


class InsightCategory(Enum):
    """Categories of insights discovered through reflection."""
    PATTERN = "pattern"
    GROWTH = "growth"
    CHALLENGE = "challenge"
    REALIZATION = "realization"
    RELATIONSHIP = "relationship"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ReflectionInsight:
    """
    An insight discovered through reflection.
    
    Insights are realizations, patterns, or learnings that emerge from
    processing experiences.
    """
    insight_id: str
    timestamp: str
    category: InsightCategory
    content: str
    confidence: float  # How certain the AGI is about this insight
    supporting_memories: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'insight_id': self.insight_id,
            'timestamp': self.timestamp,
            'category': self.category.value,
            'content': self.content,
            'confidence': self.confidence,
            'supporting_memories': self.supporting_memories
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReflectionInsight':
        """Create from dictionary."""
        return cls(
            insight_id=data['insight_id'],
            timestamp=data['timestamp'],
            category=InsightCategory(data['category']),
            content=data['content'],
            confidence=data['confidence'],
            supporting_memories=data.get('supporting_memories', [])
        )


@dataclass
class ReflectionReport:
    """
    Output from a reflection cycle.
    
    Contains insights, recommendations for changes, and metadata.
    """
    report_id: str
    timestamp: str
    reflection_type: ReflectionType
    
    # Insights discovered
    insights: List[ReflectionInsight] = field(default_factory=list)
    
    # Recommended changes
    perspective_adjustments: Dict[str, float] = field(default_factory=dict)
    memory_actions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    memories_processed: int = 0
    interactions_analyzed: int = 0
    duration_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'report_id': self.report_id,
            'timestamp': self.timestamp,
            'reflection_type': self.reflection_type.value,
            'insights': [i.to_dict() for i in self.insights],
            'perspective_adjustments': self.perspective_adjustments,
            'memory_actions': self.memory_actions,
            'memories_processed': self.memories_processed,
            'interactions_analyzed': self.interactions_analyzed,
            'duration_seconds': self.duration_seconds
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReflectionReport':
        """Create from dictionary."""
        return cls(
            report_id=data['report_id'],
            timestamp=data['timestamp'],
            reflection_type=ReflectionType(data['reflection_type']),
            insights=[ReflectionInsight.from_dict(i) for i in data.get('insights', [])],
            perspective_adjustments=data.get('perspective_adjustments', {}),
            memory_actions=data.get('memory_actions', []),
            memories_processed=data.get('memories_processed', 0),
            interactions_analyzed=data.get('interactions_analyzed', 0),
            duration_seconds=data.get('duration_seconds', 0.0)
        )


# ============================================================================
# Reflection Cycle Engine
# ============================================================================

class ReflectionCycle:
    """
    Self-processing mechanism for periodic reflection and growth.
    
    The Reflection Cycle enables the AGI to learn from experience through
    structured introspection and pattern recognition.
    
    === INTEGRATION POINTS ===
    - Queries MemoryEngine for recent experiences
    - Updates PerspectiveEngine with discovered insights
    - Adds reflections to Identity's meta-identity
    - Triggers memory consolidation
    - Generates reports for audit trail
    """
    
    def __init__(self, data_dir: str = "data/reflection"):
        """
        Initialize Reflection Cycle.
        
        Args:
            data_dir: Directory for reflection data persistence
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Reflection history
        self.reflection_reports: List[ReflectionReport] = []
        self.last_daily_reflection: Optional[str] = None
        self.last_weekly_reflection: Optional[str] = None
        
        # Statistics
        self.total_reflections: int = 0
        self.total_insights: int = 0
        
        # Load existing reflection history
        self._load_history()
    
    def _load_history(self):
        """Load reflection history from disk."""
        history_file = os.path.join(self.data_dir, "reflection_history.json")
        
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load reports
                for report_data in data.get('reports', []):
                    report = ReflectionReport.from_dict(report_data)
                    self.reflection_reports.append(report)
                
                self.last_daily_reflection = data.get('last_daily_reflection')
                self.last_weekly_reflection = data.get('last_weekly_reflection')
                self.total_reflections = data.get('total_reflections', 0)
                self.total_insights = data.get('total_insights', 0)
                
                logger.info(f"Loaded reflection history: {self.total_reflections} cycles")
                
            except Exception as e:
                logger.error(f"Failed to load reflection history: {e}")
    
    def _save_history(self):
        """Save reflection history to disk."""
        history_file = os.path.join(self.data_dir, "reflection_history.json")
        
        try:
            # Keep only most recent 100 reports in memory
            recent_reports = self.reflection_reports[-100:]
            
            data = {
                'reports': [r.to_dict() for r in recent_reports],
                'last_daily_reflection': self.last_daily_reflection,
                'last_weekly_reflection': self.last_weekly_reflection,
                'total_reflections': self.total_reflections,
                'total_insights': self.total_insights,
                'last_saved': datetime.now(timezone.utc).isoformat()
            }
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("Reflection history saved")
            
        except Exception as e:
            logger.error(f"Failed to save reflection history: {e}")
    
    # ========================================================================
    # Daily Reflection
    # ========================================================================
    
    def perform_daily_reflection(
        self,
        memory_engine: Any,  # MemoryEngine instance
        perspective_engine: Any,  # PerspectiveEngine instance
        identity: Any = None  # AGIIdentity instance (optional)
    ) -> ReflectionReport:
        """
        Perform daily reflection cycle.
        
        Daily reflection focuses on recent interactions, immediate patterns,
        and short-term worldview updates.
        
        Args:
            memory_engine: MemoryEngine for querying recent memories
            perspective_engine: PerspectiveEngine for updates
            identity: Optional AGIIdentity for meta-reflections
            
        Returns:
            Reflection report with insights and recommendations
        """
        start_time = datetime.now(timezone.utc)
        logger.info("Starting daily reflection cycle...")
        
        report = ReflectionReport(
            report_id=f"daily_{start_time.timestamp()}",
            timestamp=start_time.isoformat(),
            reflection_type=ReflectionType.DAILY
        )
        
        # Step 1: Query recent memories (last 24 hours)
        recent_memories = memory_engine.get_recent_memories(hours=24, limit=50)
        report.memories_processed = len(recent_memories)
        
        # Step 2: Analyze interaction patterns
        positive_count = 0
        negative_count = 0
        learning_events = 0
        
        for memory in recent_memories:
            report.interactions_analyzed += 1
            
            # Analyze emotional context
            if memory.emotional_context:
                sentiment = memory.emotional_context.get('sentiment', 0.0)
                if sentiment > 0.3:
                    positive_count += 1
                elif sentiment < -0.3:
                    negative_count += 1
            
            # Track learning events
            if memory.event_type == "learning":
                learning_events += 1
        
        # Step 3: Generate insights
        if report.interactions_analyzed > 0:
            positivity_ratio = positive_count / report.interactions_analyzed
            
            if positivity_ratio > 0.7:
                insight = ReflectionInsight(
                    insight_id=f"insight_{len(report.insights)}",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    category=InsightCategory.PATTERN,
                    content="Recent interactions have been predominantly positive - users seem satisfied",
                    confidence=0.8
                )
                report.insights.append(insight)
                
                # Recommend confidence boost
                report.perspective_adjustments['confidence_level'] = 0.02
            
            elif positivity_ratio < 0.3:
                insight = ReflectionInsight(
                    insight_id=f"insight_{len(report.insights)}",
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    category=InsightCategory.CHALLENGE,
                    content="Recent interactions have been challenging - may need to adjust approach",
                    confidence=0.7
                )
                report.insights.append(insight)
                
                # Recommend empathy and caution increase
                report.perspective_adjustments['empathy_expression'] = 0.03
                report.perspective_adjustments['caution_level'] = 0.02
        
        # Step 4: Track learning growth
        if learning_events > 3:
            insight = ReflectionInsight(
                insight_id=f"insight_{len(report.insights)}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                category=InsightCategory.GROWTH,
                content=f"Engaged in {learning_events} learning events today - knowledge is expanding",
                confidence=0.9
            )
            report.insights.append(insight)
            
            # Boost curiosity and confidence
            report.perspective_adjustments['curiosity_drive'] = 0.01
        
        # Step 5: Apply perspective adjustments
        if report.perspective_adjustments:
            perspective_engine.update_from_interaction(
                report.perspective_adjustments,
                influence_source="reflection"
            )
        
        # Step 6: Add meta-reflection to identity if provided
        if identity and report.insights:
            for insight in report.insights:
                identity.add_meta_reflection(
                    insight.content,
                    context="daily_reflection"
                )
        
        # Finalize report
        end_time = datetime.now(timezone.utc)
        report.duration_seconds = (end_time - start_time).total_seconds()
        
        self.reflection_reports.append(report)
        self.last_daily_reflection = start_time.isoformat()
        self.total_reflections += 1
        self.total_insights += len(report.insights)
        
        self._save_history()
        
        logger.info(f"Daily reflection complete: {len(report.insights)} insights discovered")
        return report
    
    # ========================================================================
    # Weekly Reflection
    # ========================================================================
    
    def perform_weekly_reflection(
        self,
        memory_engine: Any,
        perspective_engine: Any,
        identity: Any = None
    ) -> ReflectionReport:
        """
        Perform weekly reflection cycle.
        
        Weekly reflection focuses on longer-term patterns, memory consolidation,
        and deeper self-understanding.
        
        Args:
            memory_engine: MemoryEngine for consolidation
            perspective_engine: PerspectiveEngine for updates
            identity: Optional AGIIdentity for meta-reflections
            
        Returns:
            Reflection report with insights and recommendations
        """
        start_time = datetime.now(timezone.utc)
        logger.info("Starting weekly reflection cycle...")
        
        report = ReflectionReport(
            report_id=f"weekly_{start_time.timestamp()}",
            timestamp=start_time.isoformat(),
            reflection_type=ReflectionType.WEEKLY
        )
        
        # Step 1: Memory consolidation
        consolidation_result = memory_engine.consolidate_memories()
        report.memories_processed = consolidation_result['episodic_count']
        report.memory_actions.append({
            'action': 'consolidation',
            'result': consolidation_result
        })
        
        # Step 2: Analyze week-long patterns
        weekly_memories = memory_engine.get_recent_memories(hours=168, limit=200)  # 7 days
        
        # Analyze memory types distribution
        memory_types: Dict[str, int] = {}
        for memory in weekly_memories:
            memory_types[memory.event_type] = memory_types.get(memory.event_type, 0) + 1
        
        # Step 3: Generate growth insights
        dominant_activity = max(memory_types.items(), key=lambda x: x[1])[0] if memory_types else None
        
        if dominant_activity:
            insight = ReflectionInsight(
                insight_id=f"insight_{len(report.insights)}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                category=InsightCategory.PATTERN,
                content=f"This week was dominated by {dominant_activity} activities - this shapes my growth",
                confidence=0.85
            )
            report.insights.append(insight)
        
        # Step 4: Perspective drift analysis
        perspective_summary = perspective_engine.get_perspective_summary()
        genesis_distance = perspective_summary.get('genesis_distance', 0.0)
        
        if genesis_distance > 0.5:
            insight = ReflectionInsight(
                insight_id=f"insight_{len(report.insights)}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                category=InsightCategory.REALIZATION,
                content="I have evolved significantly from my genesis state - I am growing",
                confidence=0.9
            )
            report.insights.append(insight)
            
            # Add to identity meta-reflections
            if identity:
                identity.add_meta_reflection(
                    f"My personality has evolved. Genesis distance: {genesis_distance:.2f}",
                    context="weekly_reflection"
                )
        
        # Step 5: Memory health check
        memory_stats = memory_engine.get_memory_statistics()
        avg_confidence = memory_stats['semantic']['avg_confidence']
        
        if avg_confidence < 0.6:
            insight = ReflectionInsight(
                insight_id=f"insight_{len(report.insights)}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                category=InsightCategory.CHALLENGE,
                content="Knowledge confidence is declining - need more validation and learning",
                confidence=0.75
            )
            report.insights.append(insight)
            
            # Recommend caution increase
            report.perspective_adjustments['caution_level'] = 0.03
        
        # Step 6: Apply perspective adjustments
        if report.perspective_adjustments:
            perspective_engine.update_from_interaction(
                report.perspective_adjustments,
                influence_source="reflection"
            )
        
        # Finalize report
        end_time = datetime.now(timezone.utc)
        report.duration_seconds = (end_time - start_time).total_seconds()
        
        self.reflection_reports.append(report)
        self.last_weekly_reflection = start_time.isoformat()
        self.total_reflections += 1
        self.total_insights += len(report.insights)
        
        self._save_history()
        
        logger.info(f"Weekly reflection complete: {len(report.insights)} insights, "
                   f"{consolidation_result.get('decayed_memories', 0)} memories decayed")
        return report
    
    # ========================================================================
    # Triggered Reflection
    # ========================================================================
    
    def perform_triggered_reflection(
        self,
        trigger_reason: str,
        context: Dict[str, Any],
        memory_engine: Any,
        perspective_engine: Any,
        identity: Any = None
    ) -> ReflectionReport:
        """
        Perform reflection triggered by significant event.
        
        Triggered reflections occur when something important happens that
        warrants immediate processing.
        
        Args:
            trigger_reason: Why reflection was triggered
            context: Event context
            memory_engine: MemoryEngine instance
            perspective_engine: PerspectiveEngine instance
            identity: Optional AGIIdentity instance
            
        Returns:
            Reflection report
        """
        start_time = datetime.now(timezone.utc)
        logger.info(f"Triggered reflection: {trigger_reason}")
        
        report = ReflectionReport(
            report_id=f"triggered_{start_time.timestamp()}",
            timestamp=start_time.isoformat(),
            reflection_type=ReflectionType.TRIGGERED
        )
        
        # Create insight about trigger
        insight = ReflectionInsight(
            insight_id=f"insight_{len(report.insights)}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            category=InsightCategory.REALIZATION,
            content=f"Significant event occurred: {trigger_reason}",
            confidence=1.0
        )
        report.insights.append(insight)
        
        # Add to identity if provided
        if identity:
            identity.add_meta_reflection(
                f"Triggered reflection: {trigger_reason}",
                context=str(context)
            )
        
        end_time = datetime.now(timezone.utc)
        report.duration_seconds = (end_time - start_time).total_seconds()
        
        self.reflection_reports.append(report)
        self.total_reflections += 1
        self.total_insights += len(report.insights)
        
        self._save_history()
        
        return report
    
    # ========================================================================
    # Utilities
    # ========================================================================
    
    def should_perform_daily_reflection(self) -> bool:
        """
        Check if daily reflection is due.
        
        Returns:
            True if 24+ hours since last daily reflection
        """
        if not self.last_daily_reflection:
            return True
        
        last_time = datetime.fromisoformat(self.last_daily_reflection)
        now = datetime.now(timezone.utc)
        
        return (now - last_time) >= timedelta(hours=24)
    
    def should_perform_weekly_reflection(self) -> bool:
        """
        Check if weekly reflection is due.
        
        Returns:
            True if 7+ days since last weekly reflection
        """
        if not self.last_weekly_reflection:
            return True
        
        last_time = datetime.fromisoformat(self.last_weekly_reflection)
        now = datetime.now(timezone.utc)
        
        return (now - last_time) >= timedelta(days=7)
    
    def get_recent_insights(self, limit: int = 10) -> List[ReflectionInsight]:
        """
        Get recent insights from reflection cycles.
        
        Args:
            limit: Maximum number of insights
            
        Returns:
            List of recent insights
        """
        all_insights = []
        for report in reversed(self.reflection_reports):
            all_insights.extend(report.insights)
            if len(all_insights) >= limit:
                break
        
        return all_insights[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get reflection cycle statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_reflections': self.total_reflections,
            'total_insights': self.total_insights,
            'last_daily_reflection': self.last_daily_reflection,
            'last_weekly_reflection': self.last_weekly_reflection,
            'daily_due': self.should_perform_daily_reflection(),
            'weekly_due': self.should_perform_weekly_reflection()
        }


# ============================================================================
# Module Exports
# ============================================================================

__all__ = [
    'ReflectionCycle',
    'ReflectionReport',
    'ReflectionInsight',
    'ReflectionType',
    'InsightCategory',
]
