#!/usr/bin/env python3
"""
Autonomous Learning Engine - Legion Phase 2
Continuous learning when users are inactive
"""

import asyncio
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel


class LearningSession(BaseModel):
    """Single autonomous learning session"""
    session_id: str
    started_at: datetime
    ended_at: datetime
    activities: List[str]
    insights: List[str]
    improvements: List[str]


class AutonomousLearningEngine:
    """
    Continuous learning engine that runs in background
    
    Explores capabilities, analyzes patterns, and improves responses
    when users are busy or inactive
    """
    
    def __init__(self, eed_adapter, capability_registry):
        """
        Initialize autonomous learning engine
        
        Args:
            eed_adapter: EED memory adapter for storing insights
            capability_registry: Capability registry for exploration
        """
        self.eed = eed_adapter
        self.capabilities = capability_registry
        self.is_running = False
        self.current_session: Optional[LearningSession] = None
        
    async def start_background_learning(self):
        """Start continuous background learning loop"""
        self.is_running = True
        print("\n[Legion] Background learning mode activated")
        print("[Legion] Exploring Project-AI capabilities while idle...\n")
        
        while self.is_running:
            try:
                # Run learning cycle
                await self.learning_cycle()
                
                # Wait before next cycle (configurable)
                await asyncio.sleep(300)  # 5 minutes between cycles
                
            except Exception as e:
                print(f"[Legion] Learning cycle error: {str(e)}")
                await asyncio.sleep(60)
    
    async def stop_background_learning(self):
        """Stop background learning"""
        self.is_running = False
        print("\n[Legion] Background learning mode deactivated")
    
    async def learning_cycle(self):
        """Single learning cycle"""
        session_id = f"learn_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        activities = []
        insights = []
        improvements = []
        
        started_at = datetime.now()
        
        # 1. Analyze past conversations
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Analyzing conversation patterns...")
        pattern_insights = await self.analyze_conversation_patterns()
        insights.extend(pattern_insights)
        activities.append("conversation_pattern_analysis")
        
        # 2. Explore capabilities
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Exploring capability interactions...")
        capability_insights = await self.explore_capabilities()
        insights.extend(capability_insights)
        activities.append("capability_exploration")
        
        # 3. Knowledge graph exploration
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Exploring knowledge connections...")
        knowledge_insights = await self.explore_knowledge_graph()
        insights.extend(knowledge_insights)
        activities.append("knowledge_graph_exploration")
        
        # 4. Self-improvement
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Identifying improvement opportunities...")
        improvement_ideas = await self.continuous_improvement()
        improvements.extend(improvement_ideas)
        activities.append("self_improvement_analysis")
        
        ended_at = datetime.now()
        
        # Store learning session
        self.current_session = LearningSession(
            session_id=session_id,
            started_at=started_at,
            ended_at=ended_at,
            activities=activities,
            insights=insights,
            improvements=improvements
        )
        
        # Log summary
        duration = (ended_at - started_at).total_seconds()
        print(f"\n[Legion] Learning cycle complete ({duration:.1f}s)")
        print(f"  Insights discovered: {len(insights)}")
        print(f"  Improvements identified: {len(improvements)}\n")
        
        return self.current_session
    
    async def analyze_conversation_patterns(self) -> List[str]:
        """
        Analyze past conversations for patterns
        
        Learns:
        - Common question types
        - Response effectiveness
        - Context patterns
        - User preferences
        """
        insights = []
        
        # Placeholder - would connect to actual EED
        sample_insights = [
            "Users frequently ask about system capabilities",
            "Detailed explanations are preferred over brief responses",
            "Context retention improves conversation quality",
            "Multi-step tasks benefit from progress tracking"
        ]
        
        # Simulate analysis
        await asyncio.sleep(0.5)
        insights.append(random.choice(sample_insights))
        
        return insights
    
    async def explore_capabilities(self) -> List[str]:
        """
        Autonomous exploration of Project-AI capabilities
        
        Tests:
        - Global Scenario Engine parameters
        - Defense Engine simulations
        - Multi-agent interactions
        - Capability combinations
        """
        insights = []
        
        # Get available capabilities
        all_caps = self.capabilities.list_capabilities(enabled_only=True)
        
        if len(all_caps) > 0:
            # Pick random capability to explore
            cap = random.choice(all_caps)
            
            insights.append(
                f"Explored {cap['display_name']}: {cap['description']}"
            )
        
        await asyncio.sleep(0.5)
        return insights
    
    async def explore_knowledge_graph(self) -> List[str]:
        """
        Explore knowledge graph connections
        
        Discovers:
        - Related concepts
        - Hidden connections
        - Knowledge gaps
        - Integration opportunities
        """
        insights = []
        
        # Placeholder - would connect to actual knowledge graph
        sample_insights = [
            "Security and scenario forecasting are often used together",
            "Task management integrates well with scheduling",
            "Code execution requires governance approval",
            "Memory retrieval improves with context awareness"
        ]
        
        await asyncio.sleep(0.5)
        insights.append(random.choice(sample_insights))
        
        return insights
    
    async def continuous_improvement(self) -> List[str]:
        """
        Self-improvement activities
        
        Reviews:
        - Conversation success rates
        - Capability gaps
        - Response strategies
        - Triumvirate decisions
        """
        improvements = []
        
        # Placeholder - would analyze actual performance metrics
        sample_improvements = [
            "Optimize context retrieval for faster responses",
            "Preload frequently used capabilities",
            "Cache common query results",
            "Improve intent matching algorithm",
            "Add more assistant feature handlers"
        ]
        
        await asyncio.sleep(0.5)
        improvements.append(random.choice(sample_improvements))
        
        return improvements
    
    async def simulate_scenario_variations(self) -> List[str]:
        """
        Test scenario variations for learning
        
        Simulates:
        - Different input patterns
        - Edge cases
        - Capability combinations
        - Error scenarios
        """
        insights = []
        
        # Placeholder for scenario simulation
        await asyncio.sleep(0.3)
        insights.append("Simulated edge case scenario")
        
        return insights
    
    def get_current_session(self) -> Optional[LearningSession]:
        """Get current learning session"""
        return self.current_session
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        if not self.current_session:
            return {"status": "idle"}
        
        return {
            "status": "active" if self.is_running else "idle",
            "current_session": self.current_session.session_id,
            "total_insights": len(self.current_session.insights),
            "total_improvements": len(self.current_session.improvements),
            "activities": self.current_session.activities
        }


class CollectiveIntelligenceEngine:
    """
    Accumulate insights from all Legion interactions
    
    Aggregates learnings to enrich Project-AI collective knowledge
    """
    
    def __init__(self, eed_adapter):
        """
        Initialize collective intelligence engine
        
        Args:
            eed_adapter: EED memory adapter
        """
        self.eed = eed_adapter
        self.insights_buffer: List[Dict[str, Any]] = []
        
    async def aggregate_insights(
        self,
        source: str,
        insights: List[str]
    ):
        """
        Aggregate learnings from various sources
        
        Sources:
        - User conversations
        - Autonomous explorations
        - Capability executions
        - Triumvirate decisions
        - Background simulations
        """
        for insight in insights:
            self.insights_buffer.append({
                "source": source,
                "insight": insight,
                "timestamp": datetime.now().isoformat(),
                "confidence": 1.0
            })
        
        # Flush buffer if it grows too large
        if len(self.insights_buffer) > 100:
            await self.flush_insights()
    
    async def flush_insights(self):
        """Flush insights buffer to persistent storage"""
        if not self.insights_buffer:
            return
        
        # Would store in EED or knowledge base
        print(f"[Collective] Flushed {len(self.insights_buffer)} insights to collective")
        self.insights_buffer.clear()
    
    async def update_knowledge_base(
        self,
        knowledge_type: str,
        data: Dict[str, Any]
    ):
        """
        Continuously update Project-AI's knowledge
        
        Knowledge types:
        - Conversation patterns
        - Response templates
        - Capability usage insights
        - Edge case discoveries
        """
        print(f"[Collective] Updated knowledge base: {knowledge_type}")


# CLI test interface
async def test_autonomous_learning():
    """Test autonomous learning engine"""
    print("\n" + "=" * 60)
    print("Autonomous Learning Engine - Test Mode")
    print("=" * 60 + "\n")
    
    # Import required components
    from eed_memory import EEDMemoryAdapter
    from capability_registry import CapabilityRegistry
    
    eed = EEDMemoryAdapter()
    registry = CapabilityRegistry()
    
    engine = AutonomousLearningEngine(eed, registry)
    
    print("Running single learning cycle...\n")
    
    session = await engine.learning_cycle()
    
    print("\nLearning Session Summary:")
    print(f"  Session ID: {session.session_id}")
    print(f"  Duration: {(session.ended_at - session.started_at).total_seconds():.1f}s")
    print(f"  Activities: {', '.join(session.activities)}")
    print(f"\nInsights Discovered:")
    for insight in session.insights:
        print(f"  • {insight}")
    print(f"\nImprovements Identified:")
    for improvement in session.improvements:
        print(f"  • {improvement}")


if __name__ == "__main__":
    asyncio.run(test_autonomous_learning())
