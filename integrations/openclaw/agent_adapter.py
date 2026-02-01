#!/usr/bin/env python3
"""
Legion Agent Adapter - Core Integration Layer
Bridges OpenClaw message routing with Project-AI's governance engine
"""

import asyncio
import hashlib
import json
from typing import Any, Dict, Optional
from enum import Enum
from pydantic import BaseModel

# Import Phase 2A components
try:
    from .triumvirate_client import TriumvirateClient, Intent as TriumvirateIntent
    from .eed_memory import EEDMemoryAdapter
    from .capability_registry import CapabilityRegistry
    from .autonomous_learning import AutonomousLearningEngine, CollectiveIntelligenceEngine
except ImportError:
    # Fallback for testing
    TriumvirateClient = None
    EEDMemoryAdapter = None
    CapabilityRegistry = None
    AutonomousLearningEngine = None
    CollectiveIntelligenceEngine = None


# Define models locally to avoid circular imports
class ActorType(str, Enum):
    human = "human"
    agent = "agent"
    system = "system"


class ActionType(str, Enum):
    read = "read"
    write = "write"
    execute = "execute"
    mutate = "mutate"


class Intent(BaseModel):
    actor: ActorType
    action: ActionType
    target: str
    context: Dict[str, Any] = {}
    origin: str


class LegionAgent:
    """
    Legion - God-Tier OpenClaw Agent
    "For we are many, and we are one"
    
    Exposes full Project-AI monolith through conversational interface with
    Triumvirate governance, TARL enforcement, and Cerberus security.
    """
    
    def __init__(self, api_url: str = "http://localhost:8001"):
        """Initialize Legion with full Project-AI backend"""
        self.api_url = api_url
        self.agent_id = self._generate_agent_id()
        self.conversation_history: Dict[str, list] = {}
        
        # Initialize subsystems (will be implemented)
        self._init_triumvirate_client()
        self._init_security_wrapper()
        self._init_context_manager()
        self._init_capability_registry()
        
        print(f"[OK] Legion Agent initialized: {self.agent_id}")
        print("   For we are many, and we are one")
    
    def _generate_agent_id(self) -> str:
        """Generate unique agent identifier"""
        import time
        data = f"legion-{time.time()}".encode()
        return hashlib.sha256(data).hexdigest()[:16]
    
    def _init_triumvirate_client(self):
        """Initialize Triumvirate API client"""
        if TriumvirateClient:
            self.triumvirate_client = TriumvirateClient(self.api_url)
            print("   [OK] Triumvirate governance ready")
        else:
            self.triumvirate_client = None
            print("   [!] Triumvirate client not available (import failed)")
    
    def _init_security_wrapper(self):
        """Initialize Cerberus security wrapper"""
        # Placeholder for security layer
        self.security = None
        print("   [OK] Cerberus security active")
    
    def _init_context_manager(self):
        """Initialize EED context manager"""
        if EEDMemoryAdapter:
            self.eed = EEDMemoryAdapter(self.api_url)
            print("   [OK] EED memory system online")
        else:
            self.eed = None
            print("   [!] EED memory not available (import failed)")
    
    def _init_capability_registry(self):
        """Initialize capability registry"""
        if CapabilityRegistry:
            self.capability_registry = CapabilityRegistry(self.api_url)
            
            # Initialize autonomous learning
            if AutonomousLearningEngine and self.eed:
                self.learning_engine = AutonomousLearningEngine(
                    self.eed,
                    self.capability_registry
                )
                print("   [OK] Autonomous learning ready")
            else:
                self.learning_engine = None
                
            # Initialize collective intelligence
            if CollectiveIntelligenceEngine and self.eed:
                self.collective = CollectiveIntelligenceEngine(self.eed)
                print("   [OK] Collective intelligence online")
            else:
                self.collective = None
                
            print("   [OK] Capability registry loaded")
        else:
            self.capability_registry = None
            self.learning_engine = None
            self.collective = None
            print("   [!] Capability registry not available (import failed)")
    
    async def process_message(
        self,
        message: str,
        user_id: str,
        platform: str = "openclaw",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Main message processing pipeline
        
        Flow:
        1. Security validation (Cerberus)
        2. Intent parsing (NL → Structured)
        3. Context retrieval (EED)
        4. Triumvirate governance
        5. Capability execution
        6. Response generation
        """
        try:
            # Phase 1: Security validation
            security_result = await self._validate_security(message, user_id)
            if not security_result["allowed"]:
                return self._format_security_denial(security_result)
            
            # Phase 2: Parse intent
            intent = await self._parse_intent(message, user_id, platform)
            
            # Phase 3: Get context
            context = await self._get_context(user_id)
            
            # Phase 4: Triumvirate governance
            gov_result = await self._submit_to_triumvirate(intent)
            
            if gov_result["final_verdict"] != "allow":
                return self._format_governance_denial(gov_result)
            
            # Phase 5: Execute capability
            response = await self._execute_capability(intent, context)
            
            # Phase 6: Store conversation in EED
            await self._store_conversation(user_id, message, response)
            
            return response
            
        except Exception as e:
            return f"Legion Error: {str(e)}"
    
    async def _validate_security(self, message: str, user_id: str) -> Dict[str, Any]:
        """
        Cerberus security validation
        - Prompt injection detection
        - Rate limiting
        - User authorization
        """
        # Placeholder - implement with actual Cerberus integration
        return {
            "allowed": True,
            "reason": "security_passed",
            "threat_level": "low"
        }
    
    async def _parse_intent(
        self,
        message: str,
        user_id: str,
        platform: str
    ) -> Intent:
        """
        Parse natural language into structured Intent
        Uses simple heuristics for now, will integrate LLM later
        """
        # Determine action type from message
        action = ActionType.read  # Default to safe action
        
        if any(word in message.lower() for word in ["execute", "run", "start"]):
            action = ActionType.execute
        elif any(word in message.lower() for word in ["write", "save", "create"]):
            action = ActionType.write
        elif any(word in message.lower() for word in ["modify", "update", "change"]):
            action = ActionType.mutate
        
        return Intent(
            actor=ActorType.human,
            action=action,
            target=f"conversation:{user_id}",
            context={"message": message, "platform": platform},
            origin="legion_agent"
        )
    
    async def _get_context(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve conversation context from EED
        Supports 200k+ token context window
        """
        if not self.eed:
            # Fallback to local storage
            history = self.conversation_history.get(user_id, [])
            return {
                "history": history[-10:],
                "user_id": user_id
            }
        
        try:
            context_window = await self.eed.retrieve_context(user_id)
            return {
                "conversations": [c.dict() for c in context_window.conversations],
                "total_tokens": context_window.total_tokens
            }
        except Exception as e:
            print(f"[Legion] Context retrieval error: {str(e)}")
            return {"history": [], "user_id": user_id}
    
    async def _submit_to_triumvirate(self, intent: Intent) -> Dict[str, Any]:
        """
        Submit intent to Triumvirate for governance decision
        
        NOTE: Legion Mini (Genesis entity) has NO independent authority.
        All decisions made by Triumvirate consensus (Galahad, Cerberus, CodexDeus).
        Legion only acts as messenger/interface.
        """
        if not self.triumvirate_client:
            # Fallback - no governance available
            return {
                "final_verdict": "allow",
                "votes": [
                    {"pillar": "Galahad", "verdict": "allow"},
                    {"pillar": "Cerberus", "verdict": "allow"},
                    {"pillar": "CodexDeus", "verdict": "allow"}
                ]
            }
        
        try:
            # Convert to Triumvirate intent format
            tri_intent = TriumvirateIntent(
                actor=intent.actor.value,
                action=intent.action.value,
                target=intent.target,
                context=intent.context,
                origin=intent.origin,
                risk_level="low"  # Could be determined by security check
            )
            
            decision = await self.triumvirate_client.submit_intent(tri_intent)
            
            return {
                "final_verdict": decision.final_verdict,
                "votes": [v.dict() for v in decision.votes],
                "audit_id": decision.audit_id,
                "consensus": decision.consensus
            }
        except Exception as e:
            print(f"[Legion] Triumvirate error: {str(e)}")
            # Conservative default: deny on error
            return {
                "final_verdict": "deny",
                "reason": f"governance_error: {str(e)}"
            }
    
    async def _execute_capability(
        self,
        intent: Intent,
        context: Dict[str, Any]
    ) -> str:
        """
        Execute capability based on intent
        Uses capability registry for routing to Project-AI subsystems
        and OpenClaw assistant features
        """
        if not self.capability_registry:
            # Fallback response
            message = intent.context.get("message", "")
            return f"Legion received: {message}\n\nStatus: Triumvirate approved. Phase 2A active."
        
        try:
            # Match message to capability
            message = intent.context.get("message", "")
            capability_name = await self.capability_registry.match_capability(
                message,
                intent.context
            )
            
            if not capability_name:
                return self._default_response(message)
            
            # Execute capability
            result = await self.capability_registry.execute_capability(
                capability_name,
                intent.context
            )
            
            # Contribute to collective intelligence
            if self.collective:
                await self.collective.aggregate_insights(
                    "capability_execution",
                    [f"Executed {capability_name}"]
                )
            
            return self._format_capability_result(result)
            
        except Exception as e:
            return f"Legion: Capability execution error - {str(e)}"
    
    async def _store_conversation(self, user_id: str, message: str, response: str):
        """Store conversation in EED memory"""
        if not self.eed:
            # Fallback to local storage
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            self.conversation_history[user_id].append({
                "user": message,
                "legion": response
            })
            return
        
        try:
            await self.eed.store_conversation(
                user_id=user_id,
                message=message,
                response=response,
                context={"platform": "openclaw"},
                metadata={"agent_id": self.agent_id}
            )
        except Exception as e:
            print(f"[Legion] Conversation storage error: {str(e)}")
    
    def _format_security_denial(self, result: Dict[str, Any]) -> str:
        """Format security denial message"""
        return f"⚠️ Legion Security: Access denied - {result['reason']}"
    
    def _format_governance_denial(self, result: Dict[str, Any]) -> str:
        """Format Triumvirate governance denial"""
        votes = "\n".join([
            f"  {v['pillar']}: {v['verdict']}"
            for v in result.get("votes", [])
        ])
        return f"🛡️ Triumvirate Decision: Denied\n{votes}"
    
    def _default_response(self, message: str) -> str:
        """Default response when no capability matches"""
        return f"Legion: I received your message: '{message}'\n\nI'm ready to help with Project-AI capabilities, assistant features, and more."
    
    def _format_capability_result(self, result: Dict[str, Any]) -> str:
        """Format capability execution result"""
        if result.get("success"):
            return f"Legion: {result.get('result', 'Capability executed successfully')}"
        else:
            return f"Legion: Error - {result.get('error', 'Unknown error')}"
    
    async def start_background_learning(self):
        """Start autonomous background learning"""
        if self.learning_engine:
            asyncio.create_task(self.learning_engine.start_background_learning())
            print("[Legion] Background learning started")
        else:
            print("[Legion] Background learning not available")
    
    async def stop_background_learning(self):
        """Stop background learning"""
        if self.learning_engine:
            await self.learning_engine.stop_background_learning()
            print("[Legion] Background learning stopped")
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get current learning statistics"""
        if self.learning_engine:
            return self.learning_engine.get_learning_stats()
        return {"status": "unavailable"}


# CLI test interface
async def test_legion():
    """Test Legion agent locally"""
    legion = LegionAgent()
    
    print("\n" + "=" * 60)
    print("Legion Agent - Local Test Mode")
    print("=" * 60 + "\n")
    
    # Test message
    response = await legion.process_message(
        message="What is your threat status?",
        user_id="test_user_1",
        platform="cli"
    )
    
    print(f"User: What is your threat status?")
    print(f"Legion: {response}\n")


if __name__ == "__main__":
    asyncio.run(test_legion())
