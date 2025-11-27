"""
Learning Request Log System - AI-initiated learning with human approval workflow.

This module provides a system where the AI can discover information during exploration
and submit learning requests to the user. Approved requests are integrated into the AI's
knowledge base, while denied requests go to a "Black Vault" that the AI cannot access.

Features:
- AI can submit learning requests with justification
- Pending requests stored in secure location (AI cannot retrieve)
- User approval/denial workflow
- Approved content integrated into memory automatically
- Denied content goes to Black Vault with content fingerprinting
- Black Vault content is invisible/irrelevant to AI
- Subliminal filtering prevents AI from re-discovering denied content
"""

import hashlib
import json
import os
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class RequestStatus(Enum):
    """Status of a learning request."""

    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    INTEGRATED = "integrated"


class RequestPriority(Enum):
    """Priority level of a learning request."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LearningRequestLog:
    """
    Manages AI learning requests with approval workflow and Black Vault.

    The AI can submit requests to learn new information. These requests are:
    1. Stored in a pending area (AI cannot access)
    2. Reviewed and approved/denied by user
    3. If approved: integrated into AI memory automatically
    4. If denied: moved to Black Vault with content fingerprinting
    5. Black Vault content is filtered from future AI searches
    """

    def __init__(self, data_dir: str = "data", memory_system=None):
        """Initialize the learning request log system."""
        self.data_dir = data_dir
        self.memory_system = memory_system

        # Directory structure
        self.requests_dir = os.path.join(data_dir, "learning_requests")
        self.pending_dir = os.path.join(self.requests_dir, "pending_secure")
        self.approved_dir = os.path.join(self.requests_dir, "approved")
        self.integrated_dir = os.path.join(self.requests_dir, "integrated")
        self.black_vault_dir = os.path.join(data_dir, "black_vault_secure")

        # Index files
        self.request_index_file = os.path.join(self.requests_dir, "request_index.json")
        self.black_vault_index_file = os.path.join(
            self.black_vault_dir, "vault_index.json"
        )
        self.fingerprint_file = os.path.join(
            self.black_vault_dir, "content_fingerprints.json"
        )

        # In-memory data (for user interface only)
        self.request_index = {}
        self.black_vault_fingerprints = set()

        # Statistics
        self.stats = {
            "total_requests": 0,
            "pending_requests": 0,
            "approved_requests": 0,
            "denied_requests": 0,
            "integrated_requests": 0,
            "black_vault_items": 0,
        }

        # Initialize structure
        self._initialize_structure()
        self._load_indexes()

    def _initialize_structure(self) -> None:
        """Create the directory structure."""
        try:
            os.makedirs(self.pending_dir, exist_ok=True)
            os.makedirs(self.approved_dir, exist_ok=True)
            os.makedirs(self.integrated_dir, exist_ok=True)
            os.makedirs(self.black_vault_dir, exist_ok=True)

            # Create .aiignore files to mark directories as AI-inaccessible
            for secure_dir in [self.pending_dir, self.black_vault_dir]:
                ignore_file = os.path.join(secure_dir, ".aiignore")
                if not os.path.exists(ignore_file):
                    with open(ignore_file, "w") as f:
                        f.write("# AI CANNOT ACCESS THIS DIRECTORY\n")
                        f.write("# All content here is filtered from AI retrieval\n")

        except Exception as e:
            print(f"Error initializing learning request structure: {e}")

    def _load_indexes(self) -> None:
        """Load request index and black vault fingerprints."""
        try:
            # Load request index
            if os.path.exists(self.request_index_file):
                with open(self.request_index_file, "r", encoding="utf-8") as f:
                    self.request_index = json.load(f)

            # Load black vault fingerprints
            if os.path.exists(self.fingerprint_file):
                with open(self.fingerprint_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.black_vault_fingerprints = set(data.get("fingerprints", []))

            # Update statistics
            self._update_statistics()

        except Exception as e:
            print(f"Error loading indexes: {e}")

    def _save_request_index(self) -> None:
        """Save the request index."""
        try:
            with open(self.request_index_file, "w", encoding="utf-8") as f:
                json.dump(self.request_index, f, indent=2)
        except Exception as e:
            print(f"Error saving request index: {e}")

    def _save_black_vault_index(self) -> None:
        """Save the black vault fingerprints."""
        try:
            data = {
                "fingerprints": list(self.black_vault_fingerprints),
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.fingerprint_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving black vault index: {e}")

    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        timestamp = datetime.now().isoformat()
        unique_string = f"{timestamp}_{len(self.request_index)}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]

    def _generate_content_fingerprint(self, content: str) -> str:
        """Generate a fingerprint for content to detect duplicates."""
        # Use multiple hashing techniques for robust detection
        full_hash = hashlib.sha256(content.encode()).hexdigest()

        # Also hash normalized content (lowercase, no whitespace)
        normalized = "".join(content.lower().split())
        normalized_hash = hashlib.sha256(normalized.encode()).hexdigest()

        # Combine for robust fingerprint
        return f"{full_hash[:32]}_{normalized_hash[:32]}"

    def _is_content_blacklisted(self, content: str) -> bool:
        """Check if content matches anything in the Black Vault."""
        fingerprint = self._generate_content_fingerprint(content)

        # Check full fingerprint
        if fingerprint in self.black_vault_fingerprints:
            return True

        # Check individual hash components
        parts = fingerprint.split("_")
        for part in parts:
            if any(part in fp for fp in self.black_vault_fingerprints):
                return True

        return False

    def _update_statistics(self) -> None:
        """Update statistics from request index."""
        self.stats["total_requests"] = len(self.request_index)
        self.stats["pending_requests"] = sum(
            1
            for r in self.request_index.values()
            if r.get("status") == RequestStatus.PENDING.value
        )
        self.stats["approved_requests"] = sum(
            1
            for r in self.request_index.values()
            if r.get("status") == RequestStatus.APPROVED.value
        )
        self.stats["denied_requests"] = sum(
            1
            for r in self.request_index.values()
            if r.get("status") == RequestStatus.DENIED.value
        )
        self.stats["integrated_requests"] = sum(
            1
            for r in self.request_index.values()
            if r.get("status") == RequestStatus.INTEGRATED.value
        )
        self.stats["black_vault_items"] = len(self.black_vault_fingerprints)

    def submit_learning_request(
        self,
        title: str,
        content: str,
        justification: str,
        source: str,
        category: str = "general",
        priority: str = "medium",
        tags: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Submit a learning request (called by AI).

        Args:
            title: Brief title of the learning request
            content: The actual content/knowledge to learn
            justification: Why the AI thinks this is valuable
            source: Where the information came from
            category: Knowledge category
            priority: Priority level ("low", "medium", "high", "critical")
            tags: Optional tags

        Returns:
            Request ID if submitted, None if blacklisted
        """
        # Check Black Vault first - if content is denied, ignore it
        if self._is_content_blacklisted(content):
            # Silently return None - AI sees this as irrelevant/uninteresting
            return None

        try:
            # Convert priority string to enum if needed
            if isinstance(priority, str):
                priority_map = {
                    "low": RequestPriority.LOW,
                    "medium": RequestPriority.MEDIUM,
                    "high": RequestPriority.HIGH,
                    "critical": RequestPriority.CRITICAL,
                }
                priority_enum = priority_map.get(
                    priority.lower(), RequestPriority.MEDIUM
                )
            else:
                priority_enum = priority

            request_id = self._generate_request_id()
            timestamp = datetime.now().isoformat()

            request_data = {
                "id": request_id,
                "timestamp": timestamp,
                "title": title,
                "content": content,
                "justification": justification,
                "source": source,
                "category": category,
                "priority": priority_enum.value,
                "tags": tags or [],
                "status": RequestStatus.PENDING.value,
                "fingerprint": self._generate_content_fingerprint(content),
            }

            # Save to pending directory (AI cannot access)
            pending_file = os.path.join(self.pending_dir, f"{request_id}.json")
            with open(pending_file, "w", encoding="utf-8") as f:
                json.dump(request_data, f, indent=2)

            # Update index (but not accessible to AI during search)
            self.request_index[request_id] = {
                "timestamp": timestamp,
                "title": title,
                "status": RequestStatus.PENDING.value,
                "priority": priority_enum.value,
                "file": pending_file,
            }

            self._save_request_index()
            self._update_statistics()

            return request_id

        except Exception as e:
            print(f"Error submitting learning request: {e}")
            return None

    def get_pending_requests(self, for_ai: bool = False) -> List[Dict[str, Any]]:
        """
        Get pending requests awaiting approval.

        Args:
            for_ai: If True, returns empty (AI cannot see pending)

        Returns:
            List of pending requests (empty if for_ai=True)
        """
        # AI CANNOT access pending requests
        if for_ai:
            return []

        pending = []
        for request_id, request_info in self.request_index.items():
            if request_info.get("status") == RequestStatus.PENDING.value:
                file_path = request_info.get("file")
                if file_path and os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            request_data = json.load(f)
                            pending.append(request_data)
                    except Exception as e:
                        print(f"Error reading request {request_id}: {e}")

        # Sort by priority and timestamp
        priority_order = {
            RequestPriority.CRITICAL.value: 0,
            RequestPriority.HIGH.value: 1,
            RequestPriority.MEDIUM.value: 2,
            RequestPriority.LOW.value: 3,
        }
        pending.sort(
            key=lambda x: (
                priority_order.get(x.get("priority", "medium"), 2),
                x.get("timestamp", ""),
            )
        )

        return pending

    def approve_request(self, request_id: str, user_notes: str = "") -> bool:
        """
        Approve a learning request and integrate it.

        Args:
            request_id: ID of the request to approve
            user_notes: Optional notes from user

        Returns:
            True if approved and integrated successfully
        """
        try:
            if request_id not in self.request_index:
                return False

            request_info = self.request_index[request_id]
            file_path = request_info.get("file")

            if not file_path or not os.path.exists(file_path):
                return False

            # Load request data
            with open(file_path, "r", encoding="utf-8") as f:
                request_data = json.load(f)

            # Update status
            request_data["status"] = RequestStatus.APPROVED.value
            request_data["approved_timestamp"] = datetime.now().isoformat()
            request_data["user_notes"] = user_notes

            # Move to approved directory
            approved_file = os.path.join(self.approved_dir, f"{request_id}.json")
            with open(approved_file, "w", encoding="utf-8") as f:
                json.dump(request_data, f, indent=2)

            # Delete from pending
            os.remove(file_path)

            # Integrate into memory if available
            if self.memory_system:
                self.memory_system.store_knowledge(
                    category=request_data.get("category", "general"),
                    title=request_data["title"],
                    content=request_data["content"],
                    source=f"AI_Learning_Request_{request_data.get('source', 'unknown')}",
                    tags=request_data.get("tags", []) + ["ai_requested", "approved"],
                )

                request_data["status"] = RequestStatus.INTEGRATED.value
                request_data["integrated_timestamp"] = datetime.now().isoformat()

                # Move to integrated directory
                integrated_file = os.path.join(
                    self.integrated_dir, f"{request_id}.json"
                )
                with open(integrated_file, "w", encoding="utf-8") as f:
                    json.dump(request_data, f, indent=2)
                os.remove(approved_file)

                # Update index
                request_info["status"] = RequestStatus.INTEGRATED.value
                request_info["file"] = integrated_file
            else:
                # Update index
                request_info["status"] = RequestStatus.APPROVED.value
                request_info["file"] = approved_file

            self._save_request_index()
            self._update_statistics()

            return True

        except Exception as e:
            print(f"Error approving request: {e}")
            return False

    def deny_request(self, request_id: str, reason: str = "") -> bool:
        """
        Deny a learning request and move to Black Vault.

        Args:
            request_id: ID of the request to deny
            reason: Reason for denial

        Returns:
            True if denied and moved to Black Vault
        """
        try:
            if request_id not in self.request_index:
                return False

            request_info = self.request_index[request_id]
            file_path = request_info.get("file")

            if not file_path or not os.path.exists(file_path):
                return False

            # Load request data
            with open(file_path, "r", encoding="utf-8") as f:
                request_data = json.load(f)

            # Update status
            request_data["status"] = RequestStatus.DENIED.value
            request_data["denied_timestamp"] = datetime.now().isoformat()
            request_data["denial_reason"] = reason

            # Add content fingerprint to Black Vault
            fingerprint = request_data.get("fingerprint")
            if fingerprint:
                self.black_vault_fingerprints.add(fingerprint)
                self._save_black_vault_index()

            # Move to Black Vault (AI cannot access)
            vault_file = os.path.join(self.black_vault_dir, f"{request_id}.json")
            with open(vault_file, "w", encoding="utf-8") as f:
                json.dump(request_data, f, indent=2)

            # Delete from pending
            os.remove(file_path)

            # Update index
            request_info["status"] = RequestStatus.DENIED.value
            request_info["file"] = vault_file

            self._save_request_index()
            self._update_statistics()

            return True

        except Exception as e:
            print(f"Error denying request: {e}")
            return False

    def get_request_by_id(
        self, request_id: str, for_ai: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get a specific request by ID.

        Args:
            request_id: ID of the request
            for_ai: If True and request is pending/denied, returns None

        Returns:
            Request data or None
        """
        if request_id not in self.request_index:
            return None

        request_info = self.request_index[request_id]
        status = request_info.get("status")

        # AI cannot see pending or denied requests
        if for_ai and status in [
            RequestStatus.PENDING.value,
            RequestStatus.DENIED.value,
        ]:
            return None

        file_path = request_info.get("file")
        if not file_path or not os.path.exists(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading request: {e}")
            return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about learning requests."""
        self._update_statistics()
        return self.stats.copy()

    def search_approved_content(
        self, query: str, for_ai: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search through approved/integrated content.

        Args:
            query: Search query
            for_ai: If True, includes subliminal filtering

        Returns:
            List of matching approved content
        """
        results = []
        query_lower = query.lower()

        # Search approved and integrated requests
        for request_id, request_info in self.request_index.items():
            status = request_info.get("status")

            if status in [RequestStatus.APPROVED.value, RequestStatus.INTEGRATED.value]:
                if query_lower in request_info.get("title", "").lower():
                    request_data = self.get_request_by_id(request_id, for_ai=for_ai)
                    if request_data:
                        results.append(request_data)

        return results

    def is_content_relevant(self, content: str, for_ai: bool = True) -> bool:
        """
        Check if content is relevant (not in Black Vault).

        This is the subliminal filter - returns False for blacklisted content,
        making the AI treat it as irrelevant.

        Args:
            content: Content to check
            for_ai: If True, applies Black Vault filtering

        Returns:
            False if content is blacklisted, True otherwise
        """
        if not for_ai:
            return True

        return not self._is_content_blacklisted(content)
