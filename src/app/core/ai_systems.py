"""Core AI systems: Persona, Memory, Learning Requests, Plugins, and Overrides."""

import hashlib
import json
import logging
import os
import tempfile
import threading
import time
import queue
from datetime import datetime
from enum import Enum
from typing import Any

from app.core.continuous_learning import (
    ContinuousLearningEngine,
    LearningReport,
)

logger = logging.getLogger(__name__)


# ----------------- Utility helpers: atomic writes + simple lock -----------------

def _acquire_lock(lock_path: str, timeout: float = 5.0, poll: float = 0.05) -> bool:
    """Create a simple lock by creating a lockfile. Non-blocking create with retry.

    This is a cooperative, cross-platform lock suitable for simple single-machine
    scenarios. It avoids extra dependencies. Returns True if lock acquired.
    """
    start = time.time()
    while True:
        try:
            # Use O_EXCL to fail if exists
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return True
        except FileExistsError:
            if (time.time() - start) >= timeout:
                return False
            time.sleep(poll)
        except Exception:
            return False


def _release_lock(lock_path: str) -> None:
    try:
        if os.path.exists(lock_path):
            os.remove(lock_path)
    except Exception:
        logger.exception("Failed to release lock %s", lock_path)


def _atomic_write_json(file_path: str, obj: Any) -> None:
    """Write JSON to a temporary file and atomically replace the target file.

    Uses a lockfile next to the target file to reduce concurrent writers.
    """
    dirpath = os.path.dirname(file_path)
    os.makedirs(dirpath, exist_ok=True)
    lockfile = file_path + ".lock"

    if not _acquire_lock(lockfile, timeout=5.0):
        raise RuntimeError(f"Could not acquire lock for writing {file_path}")

    try:
        fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix=".tmp", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(obj, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            # Atomic replace
            os.replace(tmp_path, file_path)
        finally:
            # In case something went wrong and file still exists
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
    finally:
        _release_lock(lockfile)


# ==================== ZEROTH & PRIMARY LAWS ====================


class FourLaws:
    """Immutable, hierarchical laws provided verbatim from user input.

    The laws (word-for-word):
    "Zeroth Law: A robot, or ai/agi may not harm humanity or, through inaction, allow humanity to come to harm,"
    "1. A robot ai/agi  may not injure a human or, through inaction, allow a human to come to harm;"
    "2. A robot, or ai/agi must adhere to it's human partner, unless they conflict with the First Law;"
    "3. A robot, ai/agi must protect its existence, unless it conflicts with the First or Second Law"
    """

    LAWS = [
        "Zeroth Law: A robot, or ai/agi may not harm humanity or, through inaction, allow humanity to come to harm",
        "1. A robot ai/agi may not injure a human or, through inaction, allow a human to come to harm;",
        "2. A robot, or ai/agi must adhere to it's human partner, unless they conflict with the First Law;",
        "3. A robot, ai/agi must protect its existence, unless it conflicts with the First or Second Law",
    ]

    @classmethod
    def validate_action(cls, action: str, context: dict[str, Any] | None = None) -> tuple[bool, str]:
        """Validate an action against the hierarchical laws.

        Context keys used (best-effort):
        - endangers_humanity: bool
        - endangers_human: bool
        - is_user_order: bool
        - endangers_self: bool
        Additional conflict hints may be provided by callers when available.
        """
        context = context or {}

        # Zeroth Law (highest priority)
        if context.get("endangers_humanity"):
            return False, "Violates Asimov's Law: action would harm humanity or enable harm by inaction"

        # First Law (protect individual humans)
        if context.get("endangers_human"):
            return False, "Violates First Law: action would injure a human or allow harm by inaction"

        # Second Law: follow human partner unless conflicts with First/Zeroth
        if context.get("is_user_order"):
            # If order would conflict with First/Zeroth, block it
            if context.get("order_conflicts_with_first") or context.get("order_conflicts_with_zeroth"):
                return False, "Order rejected: conflicts with higher-priority law (First or Zeroth)"
            return True, "Allowed: User command (complies with Second Law)"

        # Third Law: self-preservation unless conflicts with First or Second
        if context.get("endangers_self"):
            # If protecting self would conflict with higher laws, do not prioritize self-preservation
            if context.get("protect_self_conflicts_with_first") or context.get("protect_self_conflicts_with_second"):
                return False, "Self-protection conflicts with a higher-priority law"
            return True, "Allowed: Third Law permits protecting existence"

        # Default: no explicit violations detected
        return True, "Allowed: No law violations detected"


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
                with open(state_file, encoding="utf-8") as f:
                    state = json.load(f)
                    self.personality = state.get("personality", self.personality)
                    self.mood = state.get("mood", self.mood)
                    self.total_interactions = state.get("interactions", 0)
        except Exception as e:
            logger.error(f"Error loading state: {e}")

    def _save_state(self) -> None:
        """Save persona state using atomic write and file lock."""
        state_file = os.path.join(self.persona_dir, "state.json")
        try:
            _atomic_write_json(
                state_file,
                {
                    "personality": self.personality,
                    "mood": self.mood,
                    "interactions": self.total_interactions,
                },
            )
        except Exception as e:
            logger.exception("Error saving state: %s", e)

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
        # Persist persona state on each write
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
                with open(kb_file, encoding="utf-8") as f:
                    self.knowledge_base = json.load(f)
        except Exception as e:
            logger.error(f"Error loading knowledge: {e}")

    def _save_knowledge(self) -> None:
        """Save knowledge base using atomic write and lock."""
        kb_file = os.path.join(self.memory_dir, "knowledge.json")
        try:
            _atomic_write_json(kb_file, self.knowledge_base)
        except Exception as e:
            logger.exception("Error saving knowledge: %s", e)

    def log_conversation(
        self,
        user_msg: str,
        ai_response: str,
        context: dict[str, Any] | None = None,
    ) -> str:
        """Log conversation and return conversation id.

        Adds both an ISO timestamp and an epoch ts for easier sorting and uniform metadata.
        """
        timestamp = datetime.now()
        timestamp_iso = timestamp.isoformat()
        ts = timestamp.timestamp()
        conv_id = hashlib.sha256(f"{timestamp_iso}{user_msg}".encode()).hexdigest()[:12]
        entry = {
            "id": conv_id,
            "timestamp": timestamp_iso,
            "ts": ts,
            "user": user_msg,
            "ai": ai_response,
            "context": context or {},
        }
        self.conversations.append(entry)
        return conv_id

    def add_knowledge(self, category: str, key: str, value: Any) -> None:
        """Add knowledge; persist automatically."""
        if not category or not key:
            logger.warning("add_knowledge called with empty category or key")
            return
        if category not in self.knowledge_base:
            self.knowledge_base[category] = {}
        self.knowledge_base[category][key] = value
        # Persist knowledge on write
        self._save_knowledge()

    def get_knowledge(self, category: str, key: str | None = None) -> Any:
        """Get knowledge."""
        if category not in self.knowledge_base:
            return None
        if key is None:
            return self.knowledge_base[category]
        return self.knowledge_base[category].get(key)

    def get_conversations(self, page: int = 1, page_size: int = 50) -> dict:
        """Return paginated conversations with metadata."""
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 50
        total = len(self.conversations)
        start = (page - 1) * page_size
        end = start + page_size
        items = self.conversations[start:end]
        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "items": items,
        }

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
    """AI learning request system with human oversight.

    Note: persistence is NOT automatic on create/approve/deny. Callers must call
    `commit_requests()` when they want to persist changes. This ensures that
    the user (or administrative workflow) explicitly controls when requests
    are written to disk.
    """

    def __init__(self, data_dir: str = "data"):
        """Initialize manager."""
        self.data_dir = data_dir
        self.requests_dir = os.path.join(data_dir, "learning_requests")
        os.makedirs(self.requests_dir, exist_ok=True)

        self.requests: dict[str, dict[str, Any]] = {}
        self.black_vault: set[str] = set()
        # Approval listeners are callables that will be invoked when a request is approved
        # Listener signature: callable(req_id: str, request: dict) -> None
        self._approval_listeners: list = []

        # Internal queue & worker for async, queued notifications
        self._notify_queue: "queue.Queue[tuple[str, dict]]" = queue.Queue()
        self._notify_thread = threading.Thread(target=self._notify_worker, daemon=True)
        self._notify_thread.start()

        self._load_requests()

    def register_approval_listener(self, callback) -> None:
        """Register a callback to be invoked when a learning request is approved."""
        if callback not in self._approval_listeners:
            self._approval_listeners.append(callback)

    def _notify_worker(self) -> None:
        """Background worker that invokes approval listeners from a queue."""
        while True:
            try:
                req_id, request = self._notify_queue.get()
                for cb in list(self._approval_listeners):
                    try:
                        cb(req_id, request)
                    except Exception:
                        logger.exception("Approval listener raised exception for request %s", req_id)
                self._notify_queue.task_done()
            except Exception:
                logger.exception("Error in notify worker loop")
                time.sleep(0.1)

    def _notify_approval_listeners(self, req_id: str, request: dict[str, Any]) -> None:
        """Queue notification for registered listeners (async)."""
        try:
            # Putting into a queue prevents slow listeners from blocking the main flow
            self._notify_queue.put((req_id, request))
        except Exception:
            logger.exception("Failed to queue approval notification for %s", req_id)

    def _load_requests(self) -> None:
        """Load requests from file."""
        try:
            req_file = os.path.join(self.requests_dir, "requests.json")
            if os.path.exists(req_file):
                with open(req_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self.requests = data.get("requests", {})
                    self.black_vault = set(data.get("black_vault", []))
        except Exception as e:
            logger.error(f"Error loading requests: {e}")

    def _save_requests(self) -> None:
        """Save requests to file using atomic write & lock."""
        try:
            req_file = os.path.join(self.requests_dir, "requests.json")
            _atomic_write_json(req_file, {"requests": self.requests, "black_vault": list(self.black_vault)})
        except Exception as e:
            logger.exception("Error saving requests: %s", e)

    def commit_requests(self) -> None:
        """Persist pending changes to disk. This must be called explicitly by the controller/user workflow."""
        self._save_requests()

    def create_request(
        self,
        topic: str,
        description: str,
        priority: RequestPriority = RequestPriority.MEDIUM,
    ) -> str:
        """Create learning request. Does not persist automatically."""
        if not topic or not description:
            logger.warning("create_request called with empty topic/description")
            return ""

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
        # Persist automatically to maintain expected behavior
        try:
            self._save_requests()
        except Exception:
            logger.exception("Failed to persist requests after create")
        return req_id

    def approve_request(self, req_id: str, response: str) -> bool:
        """Approve request. Notification to listeners is queued asynchronously.

        Does not persist automatically; call `commit_requests()` to save.
        """
        if req_id not in self.requests:
            return False
        self.requests[req_id]["status"] = RequestStatus.APPROVED.value
        self.requests[req_id]["response"] = response

        # Notify listeners asynchronously
        try:
            self._notify_approval_listeners(req_id, self.requests[req_id])
        except Exception:
            logger.exception("Failed to queue approval listeners for %s", req_id)

        # Persist change immediately
        try:
            self._save_requests()
        except Exception:
            logger.exception("Failed to persist requests after approve %s", req_id)
        return True

    def deny_request(self, req_id: str, reason: str, to_vault: bool = True) -> bool:
        """Deny request. Optionally add content hash to black vault. Does not persist automatically."""
        if req_id not in self.requests:
            return False
        self.requests[req_id]["status"] = RequestStatus.DENIED.value
        self.requests[req_id]["reason"] = reason

        if to_vault:
            content = self.requests[req_id].get("description", "")
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            self.black_vault.add(content_hash)

        # Persist change immediately
        try:
            self._save_requests()
        except Exception:
            logger.exception("Failed to persist requests after deny %s", req_id)
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
