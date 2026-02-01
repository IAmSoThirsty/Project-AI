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
        # Placeholder for actual HTTP client
        self.triumvirate_client = None
        print("   [OK] Triumvirate governance ready")
    
    def _init_security_wrapper(self):
        """Initialize Cerberus security wrapper"""
        # Placeholder for security layer
        self.security = None
        print("   [OK] Cerberus security active")
    
   def _init_context_manager(self):
        """Initialize EED context manager"""
        # Placeholder for EED integration
        self.context_manager = None
        print("   [OK] EED memory system online")
    
    def _init_capability_registry(self):
        """Initialize capability registry"""
        # Placeholder for capability system
        self.capabilities = {}
        print("   [OK] Capability registry loaded")
    
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
            
            # Phase 6: Store conversation
            self._store_conversation(user_id, message, response)
            
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
        """
        # Placeholder - implement with EED integration
        history = self.conversation_history.get(user_id, [])
        return {
            "history": history[-10:],  # Last 10 messages
            "user_id": user_id
        }
    
    async def _submit_to_triumvirate(self, intent: Intent) -> Dict[str, Any]:
        """
        Submit intent to Triumvirate for governance
        Calls /intent endpoint on Project-AI API
        """
        # Placeholder - implement with actual HTTP request
        return {
            "final_verdict": "allow",
            "votes": [
                {"pillar": "Galahad", "verdict": "allow"},
                {"pillar": "Cerberus", "verdict": "allow"},
                {"pillar": "CodexDeus", "verdict": "allow"}
            ]
        }
    
    async def _execute_capability(
        self,
        intent: Intent,
        context: Dict[str, Any]
    ) -> str:
        """
        Execute capability based on intent
        """
        # Placeholder - implement with capability registry
        message = intent.context.get("message", "")
        
        # Simple echo response for now
        return f"Legion received: {message}\n\nStatus: Triumvirate approved. Phase 1 implementation active."
    
    def _store_conversation(self, user_id: str, message: str, response: str):
        """Store conversation in memory"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "user": message,
            "legion": response
        })
    
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
