#!/usr/bin/env python3
"""
Capability Registry - Legion Phase 2
Maps natural language intents to Project-AI subsystems and assistant features
"""

import asyncio
from typing import Any
from collections.abc import Callable
from enum import Enum
from pydantic import BaseModel


class CapabilityCategory(str, Enum):
    """Capability categories"""
    AI_SUBSYSTEMS = "ai_subsystems"  # Project-AI core systems
    ASSISTANT = "assistant"  # Task management, scheduling, etc
    SYSTEM = "system"  # File ops, system commands
    RESEARCH = "research"  # Web search, knowledge queries
    COMMUNICATION = "communication"  # Email, messaging
    DEVELOPMENT = "development"  # Code execution, git ops


class Capability(BaseModel):
    """Single capability definition"""
    name: str
    category: CapabilityCategory
    description: str
    keywords: list[str]  # For intent matching
    handler: Callable | None = None
    enabled: bool = True
    requires_online: bool = False
    risk_level: str = "low"  # low, medium, high


class CapabilityRegistry:
    """
    Maps natural language to Project-AI subsystems and assistant features

    Integrates:
    - Project-AI subsystems (Triumvirate, Global Scenario Engine, etc.)
    - OpenClaw assistant features (tasks, scheduling, files, search)
    """

    def __init__(self, api_url: str = "http://localhost:8001"):
        """
        Initialize capability registry

        Args:
            api_url: Base URL for Project-AI API
        """
        self.api_url = api_url
        self.capabilities: dict[str, Capability] = {}
        self._register_all_capabilities()

    def _register_all_capabilities(self):
        """Register all available capabilities"""
        # Project-AI Core Subsystems
        self._register_ai_subsystems()

        # OpenClaw Assistant Features
        self._register_assistant_features()
        self._register_system_features()
        self._register_research_features()
        self._register_communication_features()
        self._register_development_features()

    def _register_ai_subsystems(self):
        """Register Project-AI core subsystems"""
        self.capabilities.update({
            "scenario_forecasting": Capability(
                name="Global Scenario Engine",
                category=CapabilityCategory.AI_SUBSYSTEMS,
                description="Probabilistic forecasting with real-world data (IMF, World Bank, ACLED)",
                keywords=["forecast", "predict", "scenario", "future", "simulation", "monte carlo"],
                requires_online=True,
                risk_level="low"
            ),
            "security_operations": Capability(
                name="Cerberus Hydra Defense",
                category=CapabilityCategory.AI_SUBSYSTEMS,
                description="Security threat detection and Hydra spawning",
                keywords=["security", "threat", "attack", "defend", "hydra", "cerberus"],
                requires_online=True,
                risk_level="medium"
            ),
            "defense_simulations": Capability(
                name="Defense Engine",
                category=CapabilityCategory.AI_SUBSYSTEMS,
                description="Catastrophic event orchestration and survivability protocols",
                keywords=["defense", "survival", "catastrophe", "emergency", "protocol"],
                requires_online=True,
                risk_level="medium"
            ),
            "knowledge_query": Capability(
                name="Cognition Kernel",
                category=CapabilityCategory.AI_SUBSYSTEMS,
                description="200k token context AI reasoning and knowledge queries",
                keywords=["knowledge", "learn", "understand", "explain", "reason", "think"],
                requires_online=False,
                risk_level="low"
            ),
            "memory_management": Capability(
                name="EED Memory System",
                category=CapabilityCategory.AI_SUBSYSTEMS,
                description="Episodic memory storage and retrieval across conversations",
                keywords=["remember", "recall", "memory", "history", "forget", "store"],
                requires_online=False,
                risk_level="low"
            ),
            "governance_decisions": Capability(
                name="Triumvirate Governance",
                category=CapabilityCategory.AI_SUBSYSTEMS,
                description="Ethical, security, and orchestration decisions",
                keywords=["govern", "decide", "policy", "ethics", "permission", "allow", "deny"],
                requires_online=True,
                risk_level="medium"
            ),
            "code_orchestration": Capability(
                name="CodexDeus",
                category=CapabilityCategory.AI_SUBSYSTEMS,
                description="Multi-domain orchestration and autonomous AI governance",
                keywords=["orchestrate", "coordinate", "manage", "deploy", "automate"],
                requires_online=True,
                risk_level="high"
            ),
        })

    def _register_assistant_features(self):
        """Register OpenClaw assistant features"""
        self.capabilities.update({
            "task_management": Capability(
                name="Task Manager",
                category=CapabilityCategory.ASSISTANT,
                description="Create, list, update, and complete tasks",
                keywords=["task", "todo", "reminder", "checklist", "complete", "done"],
                requires_online=False,
                risk_level="low"
            ),
            "scheduling": Capability(
                name="Calendar & Scheduling",
                category=CapabilityCategory.ASSISTANT,
                description="Schedule events, set appointments, manage calendar",
                keywords=["schedule", "calendar", "appointment", "meeting", "event", "book"],
                requires_online=False,
                risk_level="low"
            ),
            "note_taking": Capability(
                name="Notes Manager",
                category=CapabilityCategory.ASSISTANT,
                description="Create, search, and organize notes",
                keywords=["note", "write", "jot", "save", "document", "memo"],
                requires_online=False,
                risk_level="low"
            ),
            "timer_alarms": Capability(
                name="Timers & Alarms",
                category=CapabilityCategory.ASSISTANT,
                description="Set timers, alarms, and countdowns",
                keywords=["timer", "alarm", "countdown", "stopwatch", "alert", "notify"],
                requires_online=False,
                risk_level="low"
            ),
        })

    def _register_system_features(self):
        """Register system operation features"""
        self.capabilities.update({
            "file_operations": Capability(
                name="File Manager",
                category=CapabilityCategory.SYSTEM,
                description="Read, write, move, delete files and directories",
                keywords=["file", "read", "write", "delete", "move", "copy", "directory", "folder"],
                requires_online=False,
                risk_level="high"
            ),
            "system_info": Capability(
                name="System Information",
                category=CapabilityCategory.SYSTEM,
                description="Get system stats, processes, resource usage",
                keywords=["system", "cpu", "memory", "disk", "process", "resource", "stats"],
                requires_online=False,
                risk_level="low"
            ),
            "command_execution": Capability(
                name="Shell Command Executor",
                category=CapabilityCategory.SYSTEM,
                description="Execute system commands (with governance)",
                keywords=["execute", "run", "command", "shell", "terminal", "cmd"],
                requires_online=False,
                risk_level="high"
            ),
        })

    def _register_research_features(self):
        """Register research and search features"""
        self.capabilities.update({
            "web_search": Capability(
                name="Web Search",
                category=CapabilityCategory.RESEARCH,
                description="Search the web for information",
                keywords=["search", "google", "find", "lookup", "web", "internet"],
                requires_online=True,
                risk_level="low"
            ),
            "knowledge_base": Capability(
                name="Knowledge Base Query",
                category=CapabilityCategory.RESEARCH,
                description="Query local knowledge base and documentation",
                keywords=["knowledge", "docs", "documentation", "reference", "manual"],
                requires_online=False,
                risk_level="low"
            ),
            "wikipedia": Capability(
                name="Wikipedia Lookup",
                category=CapabilityCategory.RESEARCH,
                description="Search Wikipedia for facts and information",
                keywords=["wikipedia", "wiki", "fact", "encyclopedia", "definition"],
                requires_online=True,
                risk_level="low"
            ),
        })

    def _register_communication_features(self):
        """Register communication features"""
        self.capabilities.update({
            "email": Capability(
                name="Email Client",
                category=CapabilityCategory.COMMUNICATION,
                description="Send, read, and manage emails (when configured)",
                keywords=["email", "mail", "send", "inbox", "message", "gmail"],
                requires_online=True,
                risk_level="medium"
            ),
            "messaging": Capability(
                name="Messaging",
                category=CapabilityCategory.COMMUNICATION,
                description="Send messages via integrated platforms",
                keywords=["message", "chat", "send", "text", "dm", "slack"],
                requires_online=True,
                risk_level="medium"
            ),
        })

    def _register_development_features(self):
        """Register development and code features"""
        self.capabilities.update({
            "code_execution": Capability(
                name="Code Executor",
                category=CapabilityCategory.DEVELOPMENT,
                description="Execute code snippets (Python, JavaScript, etc.)",
                keywords=["code", "execute", "run", "python", "javascript", "script"],
                requires_online=False,
                risk_level="high"
            ),
            "git_operations": Capability(
                name="Git Manager",
                category=CapabilityCategory.DEVELOPMENT,
                description="Git operations (status, commit, push, pull)",
                keywords=["git", "commit", "push", "pull", "branch", "merge", "repository"],
                requires_online=True,
                risk_level="high"
            ),
            "code_analysis": Capability(
                name="Code Analyzer",
                category=CapabilityCategory.DEVELOPMENT,
                description="Analyze code for issues, suggestions, optimization",
                keywords=["analyze", "lint", "review", "refactor", "optimize", "debug"],
                requires_online=False,
                risk_level="low"
            ),
        })

    async def match_capability(
        self,
        message: str,
        context: dict[str, Any] = None
    ) -> str | None:
        """
        Match user message to a capability

        Args:
            message: User message
            context: Additional context

        Returns:
            Capability name if matched, None otherwise
        """
        message_lower = message.lower()

        # Score each capability by keyword matches
        scores = {}
        for cap_name, capability in self.capabilities.items():
            if not capability.enabled:
                continue

            score = sum(
                1 for keyword in capability.keywords
                if keyword in message_lower
            )

            if score > 0:
                scores[cap_name] = score

        # Return highest scoring capability
        if scores:
            return max(scores, key=scores.get)
        return None

    async def execute_capability(
        self,
        capability_name: str,
        parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Execute a capability

        Args:
            capability_name: Name of capability to execute
            parameters: Execution parameters

        Returns:
            Execution result

        Raises:
            CapabilityError: If capability fails
        """
        capability = self.capabilities.get(capability_name)
        if not capability:
            raise CapabilityError(f"Unknown capability: {capability_name}")

        if not capability.enabled:
            raise CapabilityError(f"Capability disabled: {capability_name}")

        # Route to appropriate handler
        if capability.category == CapabilityCategory.AI_SUBSYSTEMS:
            return await self._execute_ai_subsystem(capability_name, parameters)
        elif capability.category == CapabilityCategory.ASSISTANT:
            return await self._execute_assistant_feature(capability_name, parameters)
        elif capability.category == CapabilityCategory.SYSTEM:
            return await self._execute_system_feature(capability_name, parameters)
        elif capability.category == CapabilityCategory.RESEARCH:
            return await self._execute_research_feature(capability_name, parameters)
        elif capability.category == CapabilityCategory.COMMUNICATION:
            return await self._execute_communication_feature(capability_name, parameters)
        elif capability.category == CapabilityCategory.DEVELOPMENT:
            return await self._execute_development_feature(capability_name, parameters)
        else:
            raise CapabilityError(f"Unknown category: {capability.category}")

    async def _execute_ai_subsystem(
        self,
        capability_name: str,
        parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute Project-AI subsystem capability"""
        # Placeholder - will connect to actual subsystems
        return {
            "success": True,
            "capability": capability_name,
            "result": f"Executed {capability_name} with parameters: {parameters}",
            "note": "Placeholder - integrate with actual Project-AI subsystems"
        }

    async def _execute_assistant_feature(
        self,
        capability_name: str,
        parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute assistant feature"""
        if capability_name == "task_management":
            return await self._handle_task_management(parameters)
        elif capability_name == "scheduling":
            return await self._handle_scheduling(parameters)
        elif capability_name == "note_taking":
            return await self._handle_note_taking(parameters)
        elif capability_name == "timer_alarms":
            return await self._handle_timer_alarms(parameters)
        else:
            return {"success": False, "error": "Handler not implemented"}

    async def _execute_system_feature(
        self,
        capability_name: str,
        parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute system feature"""
        return {
            "success": True,
            "capability": capability_name,
            "result": f"System feature {capability_name} placeholder",
            "note": "Requires Triumvirate approval for execution"
        }

    async def _execute_research_feature(
        self,
        capability_name: str,
        parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute research feature"""
        return {
            "success": True,
            "capability": capability_name,
            "result": f"Research feature {capability_name} placeholder"
        }

    async def _execute_communication_feature(
        self,
        capability_name: str,
        parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute communication feature"""
        return {
            "success": True,
            "capability": capability_name,
            "result": f"Communication feature {capability_name} placeholder"
        }

    async def _execute_development_feature(
        self,
        capability_name: str,
        parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute development feature"""
        return {
            "success": True,
            "capability": capability_name,
            "result": f"Development feature {capability_name} placeholder"
        }

    # Assistant feature handlers
    async def _handle_task_management(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle task management operations"""
        action = params.get("action", "list")  # create, list, update, complete

        return {
            "success": True,
            "action": action,
            "result": f"Task {action} - placeholder implementation"
        }

    async def _handle_scheduling(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle scheduling operations"""
        return {
            "success": True,
            "result": "Scheduling feature - placeholder implementation"
        }

    async def _handle_note_taking(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle note-taking operations"""
        return {
            "success": True,
            "result": "Note-taking feature - placeholder implementation"
        }

    async def _handle_timer_alarms(self, params: dict[str, Any]) -> dict[str, Any]:
        """Handle timers and alarms"""
        return {
            "success": True,
            "result": "Timer/alarm feature - placeholder implementation"
        }

    def list_capabilities(
        self,
        category: CapabilityCategory | None = None,
        enabled_only: bool = True
    ) -> list[dict[str, Any]]:
        """
        List available capabilities

        Args:
            category: Filter by category
            enabled_only: Only show enabled capabilities

        Returns:
            List of capability descriptions
        """
        caps = []
        for name, cap in self.capabilities.items():
            if category and cap.category != category:
                continue
            if enabled_only and not cap.enabled:
                continue

            caps.append({
                "name": name,
                "display_name": cap.name,
                "category": cap.category,
                "description": cap.description,
                "requires_online": cap.requires_online,
                "risk_level": cap.risk_level
            })

        return caps


class CapabilityError(Exception):
    """Exception raised for capability execution errors"""
    pass


# Import for type hints
from pydantic import BaseModel


# CLI test interface
async def test_capability_registry():
    """Test capability registry"""
    print("\n" + "=" * 60)
    print("Capability Registry - Test Mode")
    print("=" * 60 + "\n")

    registry = CapabilityRegistry()

    # List all capabilities
    print("Available Capabilities:\n")

    for category in CapabilityCategory:
        caps = registry.list_capabilities(category=category)
        if caps:
            print(f"  {category.value.upper().replace('_', ' ')}:")
            for cap in caps:
                online = " [Online]" if cap["requires_online"] else ""
                risk = f" [{cap['risk_level'].upper()}]"
                print(f"    • {cap['display_name']}{online}{risk}")
                print(f"      {cap['description']}")
            print()

    # Test intent matching
    print("\nIntent Matching Tests:\n")

    test_messages = [
        "Can you forecast the global economy for next year?",
        "Set a reminder for 3pm tomorrow",
        "Search the web for Python tutorials",
        "Execute this Python code",
        "What's on my calendar today?",
    ]

    for msg in test_messages:
        matched = await registry.match_capability(msg)
        print(f"  '{msg}'")
        print(f"    → Matched: {matched or 'None'}\n")


if __name__ == "__main__":
    asyncio.run(test_capability_registry())
