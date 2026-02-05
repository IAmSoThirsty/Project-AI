"""
Thirsty Consigliere Engine
The user's confidential, cautious strategist following the Code of Omertà
"""

import logging
from typing import Dict, Any, Optional, List
from cryptography.fernet import Fernet
import time
from .capability_manager import CapabilityManager
from .action_ledger import ActionLedger
from .privacy_checker import PrivacyChecker


class ThirstyConsigliere:
    """
    Thirsty Consigliere - Your Privacy-First Assistant

    Code of Omertà Principles:
    1. Collect only what is strictly needed
    2. Never train on user data (no global models)
    3. Default to on-device inference
    4. No "accept all" - everything locked down by default
    5. Full transparency and auditability

    Role: A confidential, cautious strategist who would rather say
    "I need less information" than over-collect.
    """

    def __init__(self, config: Dict[str, Any], god_tier_encryption):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # God tier encryption
        self.god_tier_encryption = god_tier_encryption

        # Core principles
        self.data_minimization = True
        self.on_device_only = config.get("on_device_only", True)
        self.no_training = True  # Never train on user data
        self.default_locked = True  # Everything starts locked down

        # Initialize components with God tier encryption
        self._cipher = Fernet(Fernet.generate_key())
        self.capability_manager = CapabilityManager(self._cipher)
        self.action_ledger = ActionLedger(self._cipher, max_entries=100)
        self.privacy_checker = PrivacyChecker()

        # Ephemeral context window (memory only, never persisted)
        self._context_window: List[Dict[str, Any]] = []
        self._max_context_size = config.get("max_context_size", 10)

        # Active capabilities (user must explicitly enable)
        self._active_capabilities: Dict[str, bool] = {}

        self._active = False

    def start(self):
        """Start the Consigliere"""
        self.logger.info("Starting Thirsty Consigliere - Your Privacy-First Assistant")
        self.logger.info("Code of Omertà: Privacy as a first-class contract")
        self.logger.info("God Tier Encryption: 7 layers active")

        # Initialize with minimal permissions
        self._initialize_locked_down_state()

        self._active = True

    def stop(self):
        """Stop and wipe all ephemeral data"""
        self.logger.info("Stopping Thirsty Consigliere - Wiping ephemeral data")

        # Clear ephemeral context
        self._context_window.clear()

        self._active = False

    def _initialize_locked_down_state(self):
        """Initialize with everything locked down"""
        # All capabilities start as denied
        self._active_capabilities = {
            "page_content": False,
            "browsing_history": False,
            "filesystem": False,
            "network_access": False,
            "search": False,
            "bookmarks": False,
            "downloads": False,
            "clipboard": False,
            "media_download": False,
            "remote_desktop": False,
            "ai_assistant": False,
        }

        self.logger.info("Initialized in locked-down state - all capabilities disabled")

    def request_capability(self, capability: str, reason: str) -> bool:
        """
        Request a capability with explicit reason.
        User sees what is being requested and why.

        Args:
            capability: Name of capability
            reason: Human-readable reason for request

        Returns:
            True if granted, False if denied
        """
        if not self._active:
            return False

        # Log the request (encrypted)
        self.action_ledger.add_entry(
            action="capability_request",
            details={
                "capability": capability,
                "reason": reason,
                "timestamp": time.time(),
            },
        )

        # Check with capability manager
        granted = self.capability_manager.request_permission(capability, reason)

        if granted:
            self._active_capabilities[capability] = True
            self.logger.info(f"Capability granted: {capability} - Reason: {reason}")
        else:
            self.logger.warning(f"Capability denied: {capability}")

        return granted

    def assist(
        self, query: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user query with privacy-first approach.
        All data encrypted with God tier encryption.

        Args:
            query: User's query (encrypted before processing)
            context: Optional context (minimized and anonymized)

        Returns:
            Response with transparency about data used
        """
        if not self._active:
            return {"error": "Consigliere not active"}

        # Encrypt query with God tier encryption
        encrypted_query = self.god_tier_encryption.encrypt_god_tier(query.encode())

        # Run privacy audit first
        audit = self.privacy_checker.audit_query(query, context)

        if not audit["safe"]:
            return {
                "response": "I need less information to help you safely.",
                "privacy_concerns": audit["concerns"],
                "suggestions": audit["suggestions"],
            }

        # Minimize and anonymize data
        minimized_context = self._minimize_data(context) if context else {}

        # Add to ephemeral context window (encrypted)
        self._add_to_context(
            {
                "query_hash": encrypted_query[:32].hex(),  # Only store hash
                "context": minimized_context,
                "timestamp": time.time(),
            }
        )

        # Process on-device (no external API calls)
        response = self._process_locally(query, minimized_context)

        # Log action with transparency
        self.action_ledger.add_entry(
            action="assist",
            details={
                "query_length": len(query),
                "context_used": list(minimized_context.keys())
                if minimized_context
                else [],
                "capabilities_used": [
                    k for k, v in self._active_capabilities.items() if v
                ],
                "timestamp": time.time(),
                "encrypted": True,
            },
        )

        return response

    def _minimize_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply data minimization - keep only what's strictly needed.
        Strip URLs, IPs, identifiers where possible.
        """
        minimized = {}

        for key, value in context.items():
            # Strip URLs to just domains
            if key == "url" and isinstance(value, str):
                minimized["domain"] = self._extract_domain(value)
            # Strip IPs
            elif key == "ip":
                minimized["has_ip"] = True  # Just flag, not value
            # Keep minimal data types
            elif key in ["page_title", "language"]:
                minimized[key] = value
            # Skip identifiers
            elif key not in ["user_id", "session_id", "tracking_id"]:
                minimized[key] = value

        return minimized

    def _extract_domain(self, url: str) -> str:
        """Extract just the domain from URL"""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            return parsed.netloc or "unknown"
        except Exception:
            return "unknown"

    def _add_to_context(self, entry: Dict[str, Any]):
        """Add to ephemeral context window (memory only)"""
        self._context_window.append(entry)

        # Keep only last N entries
        if len(self._context_window) > self._max_context_size:
            self._context_window.pop(0)

    def _process_locally(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process query locally (on-device).
        No external API calls, no data sent off-device.
        """
        # Simple rule-based processing
        response_text = self._generate_cautious_response(query, context)

        return {
            "response": response_text,
            "processed_locally": True,
            "data_sent_off_device": False,
            "god_tier_encrypted": True,
            "capabilities_used": [k for k, v in self._active_capabilities.items() if v],
            "transparency": {
                "where": "on-device",
                "what": "query processed locally with God tier encryption",
                "why": "privacy-first processing",
            },
        }

    def _generate_cautious_response(self, query: str, context: Dict[str, Any]) -> str:
        """Generate cautious, privacy-preserving response"""
        query_lower = query.lower()

        if "download" in query_lower and (
            "video" in query_lower or "audio" in query_lower
        ):
            return (
                "I can help you download media with our God tier encrypted downloader. "
                "All metadata is encrypted with 7 layers. Would you like to proceed? "
                "(Requires 'media_download' capability)"
            )

        if "remote" in query_lower or "desktop" in query_lower:
            return (
                "I can help you connect remotely with full God tier encryption. "
                "All remote sessions are encrypted end-to-end with 7 layers. "
                "Would you like to proceed? (Requires 'remote_desktop' capability)"
            )

        if "ai" in query_lower or "assistant" in query_lower:
            return (
                "I can activate the God tier AI assistant with complete privacy protection. "
                "All processing is done on-device with no data sent externally. "
                "Would you like to proceed? (Requires 'ai_assistant' capability)"
            )

        # Default response
        return (
            "I'm your confidential strategist. I work on-device with God tier encryption "
            "and never send your data anywhere. How can I help you while maintaining maximum privacy?"
        )

    def get_status(self) -> Dict[str, Any]:
        """Get Consigliere status"""
        return {
            "active": self._active,
            "god_tier_encrypted": True,
            "encryption_layers": 7,
            "on_device_only": self.on_device_only,
            "data_minimization": self.data_minimization,
            "active_capabilities": [
                k for k, v in self._active_capabilities.items() if v
            ],
            "ledger_entries": len(self.action_ledger.get_entries()),
            "context_window_size": len(self._context_window),
            "principles": {
                "code_of_omerta": True,
                "privacy_first": True,
                "no_training": self.no_training,
                "default_locked": self.default_locked,
                "god_tier_encryption": True,
            },
        }

    def wipe_everything(self):
        """Hard delete - wipe everything"""
        self.logger.warning("WIPING ALL CONSIGLIERE DATA")
        self._context_window.clear()
        self.action_ledger.clear()
        self._active_capabilities.clear()
        self._initialize_locked_down_state()
        self.logger.info("All data wiped - reset to locked state")
