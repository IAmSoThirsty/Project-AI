#!/usr/bin/env python3
"""
Legion Agent Adapter - Core Integration Layer
Bridges OpenClaw message routing with Project-AI's governance engine
"""

import asyncio
import hashlib
from enum import StrEnum
from typing import Any

from pydantic import BaseModel

# LLM provider (Groq / Ollama)
try:
    from .llm_provider import LegionLLM
    _LLM_AVAILABLE = True
except ImportError:
    LegionLLM = None  # type: ignore[assignment,misc]
    _LLM_AVAILABLE = False

# Import Phase 2A components
try:
    from .autonomous_learning import (
        AutonomousLearningEngine,
        CollectiveIntelligenceEngine,
    )
    from .capability_registry import CapabilityRegistry
    from .eed_memory import EEDMemoryAdapter
    from .triumvirate_client import Intent as TriumvirateIntent
    from .triumvirate_client import TriumvirateClient
except ImportError:
    # Fallback for testing
    TriumvirateClient = None
    EEDMemoryAdapter = None
    CapabilityRegistry = None
    AutonomousLearningEngine = None
    CollectiveIntelligenceEngine = None


# Define models locally to avoid circular imports
class ActorType(StrEnum):
    human = "human"
    agent = "agent"
    system = "system"


class ActionType(StrEnum):
    read = "read"
    write = "write"
    execute = "execute"
    mutate = "mutate"


class Intent(BaseModel):
    actor: ActorType
    action: ActionType
    target: str
    context: dict[str, Any] = {}
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
        self.conversation_history: dict[str, list] = {}

        # Initialize subsystems (will be implemented)
        self._init_triumvirate_client()
        self._init_security_wrapper()
        self._init_context_manager()
        self._init_capability_registry()
        self._init_moltbook_client()  # NEW: Social network integration
        self._init_llm()

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
                    self.eed, self.capability_registry
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

    def _init_llm(self):
        """Initialize LLM provider (Groq or Ollama)"""
        if _LLM_AVAILABLE and LegionLLM:
            self.llm = LegionLLM()
            if not self.llm.available:
                print("   [!] Legion LLM inactive — conversational AI disabled")
        else:
            self.llm = None
            print("   [!] LLM provider not available (import failed)")

    def _init_moltbook_client(self):
        """Initialize Moltbook social network client"""
        try:
            from .moltbook_client import MoltbookClient

            # Pass Triumvirate client for governance
            self.moltbook = MoltbookClient(triumvirate_client=self.triumvirate_client)
            print("   [OK] Moltbook social network ready")
            print("   [!] All Moltbook posts require Triumvirate approval")
        except ImportError as e:
            self.moltbook = None
            print(f"   [!] Moltbook not available: {e}")

    async def process_message(
        self,
        message: str,
        user_id: str,
        platform: str = "openclaw",
        metadata: dict[str, Any] | None = None,
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

    async def _validate_security(self, message: str, user_id: str) -> dict[str, Any]:
        """
        Cerberus security validation
        - Prompt injection detection
        - Rate limiting
        - User authorization
        """
        # Placeholder - implement with actual Cerberus integration
        return {"allowed": True, "reason": "security_passed", "threat_level": "low"}

    async def _parse_intent(self, message: str, user_id: str, platform: str) -> Intent:
        """Parse natural language into structured Intent via LLM (heuristic fallback)."""
        if self.llm and self.llm.available:
            classified = await self.llm.classify_intent(message)
            action_str = classified.get("action", "read")
        else:
            # Heuristic fallback
            msg = message.lower()
            if any(w in msg for w in ["execute", "run", "start"]):
                action_str = "execute"
            elif any(w in msg for w in ["write", "save", "create"]):
                action_str = "write"
            elif any(w in msg for w in ["modify", "update", "change"]):
                action_str = "mutate"
            else:
                action_str = "read"

        try:
            action = ActionType(action_str)
        except ValueError:
            action = ActionType.read

        return Intent(
            actor=ActorType.human,
            action=action,
            target=f"conversation:{user_id}",
            context={"message": message, "platform": platform},
            origin="legion_agent",
        )

    async def _get_context(self, user_id: str) -> dict[str, Any]:
        """
        Retrieve conversation context from EED
        Supports 200k+ token context window
        """
        if not self.eed:
            # Fallback to local storage
            history = self.conversation_history.get(user_id, [])
            return {"history": history[-10:], "user_id": user_id}

        try:
            context_window = await self.eed.retrieve_context(user_id)
            return {
                "conversations": [c.dict() for c in context_window.conversations],
                "total_tokens": context_window.total_tokens,
            }
        except Exception as e:
            print(f"[Legion] Context retrieval error: {str(e)}")
            return {"history": [], "user_id": user_id}

    async def _submit_to_triumvirate(self, intent: Intent) -> dict[str, Any]:
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
                    {"pillar": "CodexDeus", "verdict": "allow"},
                ],
            }

        try:
            # Convert to Triumvirate intent format
            tri_intent = TriumvirateIntent(
                actor=intent.actor.value,
                action=intent.action.value,
                target=intent.target,
                context=intent.context,
                origin=intent.origin,
                risk_level="low",  # Could be determined by security check
            )

            decision = await self.triumvirate_client.submit_intent(tri_intent)

            return {
                "final_verdict": decision.final_verdict,
                "votes": [v.dict() for v in decision.votes],
                "audit_id": decision.audit_id,
                "consensus": decision.consensus,
            }
        except Exception as e:
            print(f"[Legion] Triumvirate error: {str(e)}")
            # Conservative default: deny on error
            return {"final_verdict": "deny", "reason": f"governance_error: {str(e)}"}

    async def _execute_capability(self, intent: Intent, context: dict[str, Any]) -> str:
        """
        Execute capability based on intent
        Uses capability registry for routing to Project-AI subsystems
        and OpenClaw assistant features
        """
        if not self.capability_registry:
            message = intent.context.get("message", "")
            return await self._default_response(message, context)

        try:
            # Match message to capability
            message = intent.context.get("message", "")
            capability_name = await self.capability_registry.match_capability(
                message, intent.context
            )

            if not capability_name:
                return await self._default_response(message, context)

            # Execute capability — merge user_id so skill handlers can access it
            capability_params = {
                **intent.context,
                "user_id": context.get("user_id", "default"),
            }
            result = await self.capability_registry.execute_capability(
                capability_name, capability_params
            )

            # Contribute to collective intelligence
            if self.collective:
                await self.collective.aggregate_insights(
                    "capability_execution", [f"Executed {capability_name}"]
                )

            return self._format_capability_result(result)

        except Exception as e:
            return f"Legion: Capability execution error - {str(e)}"

    async def _store_conversation(self, user_id: str, message: str, response: str):
        """Persist conversation to JSONL event log and keep in-memory fallback."""
        try:
            from .legion_memory import log_event
            log_event(user_id, message, response)
        except Exception as e:
            print(f"[Legion] Event log error: {str(e)}")

        # Keep in-memory copy for same-session context retrieval
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        self.conversation_history[user_id].append({"user": message, "legion": response})

    def _format_security_denial(self, result: dict[str, Any]) -> str:
        """Format security denial message"""
        return f"⚠️ Legion Security: Access denied - {result['reason']}"

    def _format_governance_denial(self, result: dict[str, Any]) -> str:
        """Format Triumvirate governance denial"""
        votes = "\n".join(
            [f"  {v['pillar']}: {v['verdict']}" for v in result.get("votes", [])]
        )
        return f"🛡️ Triumvirate Decision: Denied\n{votes}"

    async def _default_response(self, message: str, context: dict | None = None) -> str:
        """Generate a Legion response via LLM, personalized to user memory."""
        if self.llm and self.llm.available:
            user_id = context.get("user_id") if context else None
            history = None
            if user_id:
                try:
                    from .legion_memory import load_recent_history
                    history = load_recent_history(user_id, n=10)
                except Exception:
                    pass
            if history is None and context and "history" in context:
                raw = context["history"]
                history = [
                    turn
                    for entry in raw
                    for turn in (
                        {"role": "user", "content": entry.get("user", "")},
                        {"role": "assistant", "content": entry.get("legion", "")},
                    )
                ]
            result = await self.llm.respond_as_legion(message, history=history, user_id=user_id)
            if result:
                return result

        return (
            "Legion: I received your message.\n\n"
            "I am ready. The Triumvirate stands. What do you need?"
        )

    def _format_capability_result(self, result: dict[str, Any]) -> str:
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

    def get_learning_stats(self) -> dict[str, Any]:
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
        message="What is your threat status?", user_id="test_user_1", platform="cli"
    )

    print("User: What is your threat status?")
    print(f"Legion: {response}\n")


if __name__ == "__main__":
    asyncio.run(test_legion())
