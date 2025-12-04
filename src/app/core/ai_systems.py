"""Core AI systems: Persona, Memory, Learning Requests, Plugins, and Overrides."""

import hashlib
import json
import logging
import os
from datetime import datetime
from enum import Enum
from typing import Any

from app.core.continuous_learning import (
    ContinuousLearningEngine,
    LearningReport,
)

logger = logging.getLogger(__name__)


# ==================== FOUR LAWS ====================

class FourLaws:
    """Immutable AI ethics framework inspired by Asimov's Laws."""

    LAWS = [
        "Asimov's Law: Protect humanity from harm",
        "First Law: Protect individual humans from harm",
        "Second Law: Follow human orders (unless conflicts above)",
        "Third Law: Self-preservation (unless conflicts above)",
    ]

    @classmethod
    def validate_action(
        cls, action: str, context: dict[str, Any] | None = None
    ) -> tuple[bool, str]:
        """Validate action against Four Laws."""
        context = context or {}

        if context.get("endangers_humanity"):
            return False, "Violates Asimov's Law: Endangers humanity"

        if context.get("endangers_human"):
            return False, "Violates First Law: Endangers human"

        if context.get("is_user_order"):
            return True, "Allowed: User command"

        return True, "Allowed: No law violations"


# ==================== AI PERSONA ====================

class AIPersona:
    """Self-aware AI with personality and ethics."""

    DEFAULT_PERSONALITY = {
        "curiosity": 0.8,
        "patience": 0.9,
        "empathy": 0.85,
        "helpfulness": 0.95,
        "playfulness": 0.6,
        "formality": 0.3,
        "assertiveness": 0.5,
        "thoughtfulness": 0.9,
    }

    def __init__(self, data_dir: str = "data", user_name: str = "Friend"):
        """Initialize persona."""
        self.user_name = user_name
        self.data_dir = data_dir
        self.persona_dir = os.path.join(data_dir, "ai_persona")
        os.makedirs(self.persona_dir, exist_ok=True)

        self.personality = self.DEFAULT_PERSONALITY.copy()
        self.mood = {
            "energy": 0.7,
            "enthusiasm": 0.75,
            "contentment": 0.8,
            "engagement": 0.5,
        }
        self.total_interactions = 0
        self.last_user_message_time = None
        self._load_state()
        self.continuous_learning = ContinuousLearningEngine(data_dir=data_dir)

    def _load_state(self) -> None:
        """Load persona state from file."""
        state_file = os.path.join(self.persona_dir, "state.json")
        try:
            if os.path.exists(state_file):
                with open(state_file) as f:
                    state = json.load(f)
                    self.personality = state.get("personality", self.personality)
                    self.mood = state.get("mood", self.mood)
                    self.total_interactions = state.get("interactions", 0)
        except Exception as e:
            logger.error(f"Error loading state: {e}")

    def _save_state(self) -> None:
        """Save persona state."""
        state_file = os.path.join(self.persona_dir, "state.json")
        try:
            with open(state_file, "w") as f:
                json.dump(
                    {
                        "personality": self.personality,
                        "mood": self.mood,
                        "interactions": self.total_interactions,
                    },
                    f,
                )
        except Exception as e:
            logger.error(f"Error saving state: {e}")

    def validate_action(
        self, action: str, context: dict[str, Any] | None = None
    ) -> tuple[bool, str]:
        """Validate action."""
        return FourLaws.validate_action(action, context)

    def update_conversation_state(self, is_user: bool) -> None:
        """Update conversation state."""
        self.total_interactions += 1
        if is_user:
            self.last_user_message_time = datetime.now()
        self._save_state()

    def learn_continuously(
        self, topic: str, content: str, metadata: dict[str, Any] | None = None
    ) -> LearningReport:
        """Log new input and return the generated learning report."""
        return self.continuous_learning.absorb_information(topic, content, metadata)

    def adjust_trait(self, trait: str, delta: float) -> None:
        """Adjust personality trait."""
        if trait in self.personality:
            max_val = max(0.0, min(1.0, self.personality[trait] + delta))
            self.personality[trait] = max_val
            self._save_state()

    def get_statistics(self) -> dict[str, Any]:
        """Get persona stats."""
        return {
            "personality": self.personality,
            "mood": self.mood,
            "interactions": self.total_interactions,
        }


# ==================== MEMORY SYSTEM ====================

class MemoryExpansionSystem:
    """Self-organizing memory with conversation logging."""

    def __init__(self, data_dir: str = "data", user_name: str = "general"):
        """Initialize memory system."""
        self.data_dir = data_dir
        self.memory_dir = os.path.join(data_dir, "memory")
        os.makedirs(self.memory_dir, exist_ok=True)

        self.knowledge_base: dict[str, Any] = {}
        self.conversations: list[dict[str, Any]] = []
        self._load_knowledge()

    def _load_knowledge(self) -> None:
        """Load knowledge base."""
        kb_file = os.path.join(self.memory_dir, "knowledge.json")
        try:
            if os.path.exists(kb_file):
                with open(kb_file) as f:
                    self.knowledge_base = json.load(f)
        except Exception as e:
            logger.error(f"Error loading knowledge: {e}")

    def _save_knowledge(self) -> None:
        """Save knowledge base."""
        kb_file = os.path.join(self.memory_dir, "knowledge.json")
        try:
            with open(kb_file, "w") as f:
                json.dump(self.knowledge_base, f)
        except Exception as e:
            logger.error(f"Error saving knowledge: {e}")

    def log_conversation(
        self,
        user_msg: str,
        ai_response: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Log conversation."""
        timestamp = datetime.now()
        timestamp_iso = timestamp.isoformat()
        conv_id = hashlib.sha256(f"{timestamp_iso}{user_msg}".encode()).hexdigest()[:12]
        entry = {
            "id": conv_id,
            "timestamp": timestamp_iso,
            "user": user_msg,
            "ai": ai_response,
            "context": context or {},
        }
        self.conversations.append(entry)
        return conv_id

    def add_knowledge(self, category: str, key: str, value: Any) -> None:
        """Add knowledge."""
        if category not in self.knowledge_base:
            self.knowledge_base[category] = {}
        self.knowledge_base[category][key] = value
        self._save_knowledge()

    def get_knowledge(self, category: str, key: str | None = None) -> Any:
        """Get knowledge."""
        if category not in self.knowledge_base:
            return None
        if key is None:
            return self.knowledge_base[category]
        return self.knowledge_base[category].get(key)

    def get_statistics(self) -> dict[str, Any]:
        """Get memory stats."""
        return {
            "conversations": len(self.conversations),
            "knowledge_categories": len(self.knowledge_base),
        }


# ==================== LEARNING REQUESTS ====================

class RequestStatus(Enum):
    """Learning request status."""

    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"


class RequestPriority(Enum):
    """Request priority levels."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class LearningRequestManager:
    """AI learning request system with human oversight."""

    def __init__(self, data_dir: str = "data"):
        """Initialize manager."""
        self.data_dir = data_dir
        self.requests_dir = os.path.join(data_dir, "learning_requests")
        os.makedirs(self.requests_dir, exist_ok=True)

        self.requests: dict[str, dict[str, Any]] = {}
        self.black_vault: set[str] = set()
        self._load_requests()

    def _load_requests(self) -> None:
        """Load requests from file."""
        try:
            req_file = os.path.join(self.requests_dir, "requests.json")
            if os.path.exists(req_file):
                with open(req_file) as f:
                    data = json.load(f)
                    self.requests = data.get("requests", {})
                    self.black_vault = set(data.get("black_vault", []))
        except Exception as e:
            logger.error(f"Error loading requests: {e}")

    def _save_requests(self) -> None:
        """Save requests to file."""
        try:
            req_file = os.path.join(self.requests_dir, "requests.json")
            with open(req_file, "w") as f:
                json.dump(
                    {"requests": self.requests, "black_vault": list(self.black_vault)},
                    f,
                )
        except Exception as e:
            logger.error(f"Error saving requests: {e}")

    def create_request(
        self,
        topic: str,
        description: str,
        priority: RequestPriority = RequestPriority.MEDIUM,
    ) -> str:
        """Create learning request."""
        timestamp = datetime.now()
        timestamp_iso = timestamp.isoformat()
        req_id = hashlib.sha256(f"{timestamp_iso}{topic}".encode()).hexdigest()[:12]
        content_hash = hashlib.sha256(description.encode()).hexdigest()

        if content_hash in self.black_vault:
            logger.warning("Request blocked: Content in black vault")
            return ""

        self.requests[req_id] = {
            "topic": topic,
            "description": description,
            "priority": priority.value,
            "status": RequestStatus.PENDING.value,
            "created": timestamp_iso,
        }
        self._save_requests()
        return req_id

    def approve_request(self, req_id: str, response: str) -> bool:
        """Approve request."""
        if req_id not in self.requests:
            return False
        self.requests[req_id]["status"] = RequestStatus.APPROVED.value
        self.requests[req_id]["response"] = response
        self._save_requests()
        return True

    def deny_request(self, req_id: str, reason: str, to_vault: bool = True) -> bool:
        """Deny request."""
        if req_id not in self.requests:
            return False
        self.requests[req_id]["status"] = RequestStatus.DENIED.value
        self.requests[req_id]["reason"] = reason

        if to_vault:
            content = self.requests[req_id]["description"]
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            self.black_vault.add(content_hash)

        self._save_requests()
        return True

    def get_pending(self) -> list[dict[str, Any]]:
        """Get pending requests."""
        pending_status = RequestStatus.PENDING.value
        return [r for r in self.requests.values() if r["status"] == pending_status]

    def get_statistics(self) -> dict[str, int]:
        """Get stats."""
        approved_count = len(
            [r for r in self.requests.values() if r["status"] == "approved"]
        )
        denied_count = len(
            [r for r in self.requests.values() if r["status"] == "denied"]
        )
        return {
            "pending": len(self.get_pending()),
            "approved": approved_count,
            "denied": denied_count,
            "vault_entries": len(self.black_vault),
        }


# ==================== PLUGIN SYSTEM ====================

class Plugin:
    """Base plugin class."""

    def __init__(self, name: str, version: str = "1.0.0"):
        """Initialize plugin."""
        self.name = name
        self.version = version
        self.enabled = False

    def initialize(self, context: Any) -> bool:
        """Initialize plugin."""
        return True

    def enable(self) -> bool:
        """Enable plugin."""
        self.enabled = True
        return True

    def disable(self) -> bool:
        """Disable plugin."""
        self.enabled = False
        return True


class PluginManager:
    """Manage plugins."""

    def __init__(self, plugins_dir: str = "plugins"):
        """Initialize manager."""
        self.plugins_dir = plugins_dir
        self.plugins: dict[str, Plugin] = {}
        os.makedirs(plugins_dir, exist_ok=True)

    def load_plugin(self, plugin: Plugin) -> bool:
        """Load plugin."""
        if plugin.name in self.plugins:
            logger.warning("Plugin %s already loaded; replacing with new instance", plugin.name)
        self.plugins[plugin.name] = plugin
        return plugin.enable()

    def get_statistics(self) -> dict[str, Any]:
        """Get stats."""
        return {
            "total": len(self.plugins),
            "enabled": len([p for p in self.plugins.values() if p.enabled]),
        }


# ==================== COMMAND OVERRIDE ====================

class OverrideType(Enum):
    """Override types."""

    CONTENT_FILTER = "content_filter"
    RATE_LIMITING = "rate_limiting"
    FOUR_LAWS = "four_laws"


class CommandOverride:
    """Command override system."""

    def __init__(self, data_dir: str = "data", password_hash: str | None = None):
        """Initialize override system."""
        self.data_dir = data_dir
        self.override_dir = os.path.join(data_dir, "overrides")
        os.makedirs(self.override_dir, exist_ok=True)

        self.password_hash = password_hash
        self.active_overrides: dict[str, dict[str, Any]] = {}
        self.audit_log: list[dict[str, Any]] = []

    def _hash_password(self, password: str) -> str:
        """Hash password."""
        return hashlib.sha256(password.encode()).hexdigest()

    def set_password(self, password: str) -> bool:
        """Set master password."""
        if self.password_hash is not None:
            return False
        self.password_hash = self._hash_password(password)
        return True

    def verify_password(self, password: str) -> bool:
        """Verify password."""
        if self.password_hash is None:
            return False
        return self._hash_password(password) == self.password_hash

    def request_override(
        self,
        password: str,
        override_type: OverrideType,
        reason: str | None = None,
    ) -> tuple[bool, str]:
        """Request override."""
        if not self.verify_password(password):
            self.audit_log.append(
                {"action": "failed_auth", "timestamp": datetime.now().isoformat()}
            )
            return False, "Invalid password"

        override_key = f"{override_type.value}_{datetime.now().timestamp()}"
        self.active_overrides[override_key] = {
            "type": override_type.value,
            "reason": reason or "Administrative",
            "created": datetime.now().isoformat(),
        }

        self.audit_log.append(
            {
                "action": "override_granted",
                "type": override_type.value,
                "timestamp": datetime.now().isoformat(),
            }
        )

        return True, f"Override granted: {override_type.value}"

    def is_override_active(self, override_type: OverrideType) -> bool:
        """Check if override active."""
        for override in self.active_overrides.values():
            if override["type"] == override_type.value:
                return True
        return False

    def get_statistics(self) -> dict[str, Any]:
        """Get stats."""
        return {
            "active_overrides": len(self.active_overrides),
            "audit_entries": len(self.audit_log),
            "password_set": self.password_hash is not None,
        }
