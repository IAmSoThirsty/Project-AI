"""
Memory Expansion System - Self-organizing memory database with autonomous learning.

This module provides an AI with expandable memory capabilities, allowing it to:
- Store and organize conversations, actions, and learned information
- Create and manage its own file structure for memory organization
- Learn autonomously by exploring search engines and web content
- Build a comprehensive knowledge base over time
- Recall and utilize past experiences
"""

import hashlib
import json
import os
import threading
import time
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class MemoryExpansionSystem:
    """
    Self-organizing memory database with autonomous learning capabilities.

    Features:
    - Conversation and action logging
    - Automatic memory organization and categorization
    - Search engine exploration and learning
    - Knowledge base expansion
    - Semantic memory retrieval
    - Background learning processes
    """

    def __init__(self, memory_dir: str = "data/memory", command_override=None):
        """Initialize the memory expansion system."""
        self.memory_dir = memory_dir
        self.command_override = command_override

        # Memory structure
        self.conversations_dir = os.path.join(memory_dir, "conversations")
        self.actions_dir = os.path.join(memory_dir, "actions")
        self.knowledge_dir = os.path.join(memory_dir, "knowledge")
        self.learning_dir = os.path.join(memory_dir, "autonomous_learning")
        self.index_file = os.path.join(memory_dir, "memory_index.json")

        # Memory index (for fast retrieval)
        self.memory_index = {
            "conversations": {},
            "actions": {},
            "knowledge": {},
            "learned_content": {},
            "tags": defaultdict(list),
            "timeline": [],
        }

        # Background learning
        self.learning_enabled = False
        self.learning_thread = None
        self.learning_interval = 3600  # 1 hour default

        # Statistics
        self.stats = {
            "total_conversations": 0,
            "total_actions": 0,
            "total_knowledge_items": 0,
            "total_learned_items": 0,
            "memory_size_bytes": 0,
        }

        # Initialize memory structure
        self._initialize_memory_structure()

        # Load existing index
        self._load_index()

    def _initialize_memory_structure(self) -> None:
        """Create the memory directory structure."""
        try:
            os.makedirs(self.conversations_dir, exist_ok=True)
            os.makedirs(self.actions_dir, exist_ok=True)
            os.makedirs(self.knowledge_dir, exist_ok=True)
            os.makedirs(self.learning_dir, exist_ok=True)

            # Create subdirectories for organization
            for subdir in ["daily", "weekly", "monthly", "archived"]:
                os.makedirs(os.path.join(self.conversations_dir, subdir), exist_ok=True)
                os.makedirs(os.path.join(self.actions_dir, subdir), exist_ok=True)

            # Create knowledge subdirectories by category
            knowledge_categories = [
                "technical",
                "general",
                "user_preferences",
                "patterns",
                "insights",
                "web_learned",
            ]
            for category in knowledge_categories:
                os.makedirs(os.path.join(self.knowledge_dir, category), exist_ok=True)

        except Exception as e:
            print(f"Error initializing memory structure: {e}")

    def _load_index(self) -> None:
        """Load the memory index from disk."""
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, "r", encoding="utf-8") as f:
                    self.memory_index = json.load(f)
                    # Convert tags back to defaultdict
                    self.memory_index["tags"] = defaultdict(
                        list, self.memory_index.get("tags", {})
                    )
        except Exception as e:
            print(f"Error loading memory index: {e}")

    def _save_index(self) -> None:
        """Save the memory index to disk."""
        try:
            # Convert defaultdict to regular dict for JSON serialization
            index_copy = self.memory_index.copy()
            index_copy["tags"] = dict(index_copy["tags"])

            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(index_copy, f, indent=2)
        except Exception as e:
            print(f"Error saving memory index: {e}")

    def _generate_memory_id(self, content: str) -> str:
        """Generate a unique ID for a memory entry."""
        timestamp = datetime.now().isoformat()
        unique_string = f"{timestamp}_{content[:100]}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]

    def _get_current_period(self) -> Tuple[str, str, str]:
        """Get current time period for organization."""
        now = datetime.now()
        daily = now.strftime("%Y-%m-%d")
        weekly = now.strftime("%Y-W%W")
        monthly = now.strftime("%Y-%m")
        return daily, weekly, monthly

    def store_conversation(
        self,
        user_message: str,
        ai_response: str,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Store a conversation in memory.

        Args:
            user_message: The user's message
            ai_response: The AI's response
            context: Additional context information
            tags: Tags for categorization

        Returns:
            Memory ID of the stored conversation
        """
        try:
            memory_id = self._generate_memory_id(user_message)
            timestamp = datetime.now().isoformat()
            daily, weekly, monthly = self._get_current_period()

            conversation = {
                "id": memory_id,
                "timestamp": timestamp,
                "user_message": user_message,
                "ai_response": ai_response,
                "context": context or {},
                "tags": tags or [],
                "daily": daily,
                "weekly": weekly,
                "monthly": monthly,
            }

            # Save to daily file
            daily_file = os.path.join(self.conversations_dir, "daily", f"{daily}.json")
            self._append_to_json_file(daily_file, conversation)

            # Update index
            self.memory_index["conversations"][memory_id] = {
                "timestamp": timestamp,
                "file": daily_file,
                "tags": tags or [],
                "summary": user_message[:100],
            }

            # Update tags
            if tags:
                for tag in tags:
                    self.memory_index["tags"][tag].append(memory_id)

            # Update timeline
            self.memory_index["timeline"].append(
                {
                    "id": memory_id,
                    "type": "conversation",
                    "timestamp": timestamp,
                }
            )

            self.stats["total_conversations"] += 1
            self._save_index()

            return memory_id

        except Exception as e:
            print(f"Error storing conversation: {e}")
            return ""

    def store_action(
        self,
        action_type: str,
        action_data: Dict[str, Any],
        result: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Store an action/event in memory.

        Args:
            action_type: Type of action (e.g., 'image_generation', 'file_analysis')
            action_data: Data associated with the action
            result: Result or outcome of the action
            tags: Tags for categorization

        Returns:
            Memory ID of the stored action
        """
        try:
            memory_id = self._generate_memory_id(action_type)
            timestamp = datetime.now().isoformat()
            daily, weekly, monthly = self._get_current_period()

            action = {
                "id": memory_id,
                "timestamp": timestamp,
                "action_type": action_type,
                "action_data": action_data,
                "result": result,
                "tags": tags or [],
                "daily": daily,
                "weekly": weekly,
                "monthly": monthly,
            }

            # Save to daily file
            daily_file = os.path.join(self.actions_dir, "daily", f"{daily}.json")
            self._append_to_json_file(daily_file, action)

            # Update index
            self.memory_index["actions"][memory_id] = {
                "timestamp": timestamp,
                "file": daily_file,
                "action_type": action_type,
                "tags": tags or [],
            }

            # Update tags
            if tags:
                for tag in tags:
                    self.memory_index["tags"][tag].append(memory_id)

            # Update timeline
            self.memory_index["timeline"].append(
                {
                    "id": memory_id,
                    "type": "action",
                    "timestamp": timestamp,
                }
            )

            self.stats["total_actions"] += 1
            self._save_index()

            return memory_id

        except Exception as e:
            print(f"Error storing action: {e}")
            return ""

    def store_knowledge(
        self,
        category: str,
        title: str,
        content: str,
        source: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Store knowledge/information in memory.

        Args:
            category: Knowledge category (e.g., 'technical', 'general')
            title: Title/summary of the knowledge
            content: The actual knowledge content
            source: Source of the knowledge
            tags: Tags for categorization

        Returns:
            Memory ID of the stored knowledge
        """
        try:
            memory_id = self._generate_memory_id(title)
            timestamp = datetime.now().isoformat()

            knowledge = {
                "id": memory_id,
                "timestamp": timestamp,
                "category": category,
                "title": title,
                "content": content,
                "source": source,
                "tags": tags or [],
            }

            # Save to category file
            category_file = os.path.join(
                self.knowledge_dir, category, f"{memory_id}.json"
            )
            with open(category_file, "w", encoding="utf-8") as f:
                json.dump(knowledge, f, indent=2)

            # Update index
            self.memory_index["knowledge"][memory_id] = {
                "timestamp": timestamp,
                "file": category_file,
                "category": category,
                "title": title,
                "tags": tags or [],
            }

            # Update tags
            if tags:
                for tag in tags:
                    self.memory_index["tags"][tag].append(memory_id)

            self.stats["total_knowledge_items"] += 1
            self._save_index()

            return memory_id

        except Exception as e:
            print(f"Error storing knowledge: {e}")
            return ""

    def _append_to_json_file(self, file_path: str, data: Dict[str, Any]) -> None:
        """Append data to a JSON file (as JSON lines)."""
        try:
            with open(file_path, "a", encoding="utf-8") as f:
                json.dump(data, f)
                f.write("\n")
        except Exception as e:
            print(f"Error appending to JSON file: {e}")

    def search_memory(
        self,
        query: str,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search through memory.

        Args:
            query: Search query
            memory_type: Type of memory to search ('conversation', 'action', 'knowledge', or None for all)
            tags: Filter by tags
            limit: Maximum number of results

        Returns:
            List of matching memory entries
        """
        results = []
        query_lower = query.lower()

        try:
            # Search conversations
            if memory_type in [None, "conversation"]:
                for mem_id, mem_data in self.memory_index["conversations"].items():
                    if query_lower in mem_data.get("summary", "").lower():
                        if not tags or any(t in mem_data.get("tags", []) for t in tags):
                            results.append(
                                {
                                    "id": mem_id,
                                    "type": "conversation",
                                    "data": mem_data,
                                }
                            )

            # Search actions
            if memory_type in [None, "action"]:
                for mem_id, mem_data in self.memory_index["actions"].items():
                    if query_lower in mem_data.get("action_type", "").lower():
                        if not tags or any(t in mem_data.get("tags", []) for t in tags):
                            results.append(
                                {
                                    "id": mem_id,
                                    "type": "action",
                                    "data": mem_data,
                                }
                            )

            # Search knowledge
            if memory_type in [None, "knowledge"]:
                for mem_id, mem_data in self.memory_index["knowledge"].items():
                    if query_lower in mem_data.get("title", "").lower():
                        if not tags or any(t in mem_data.get("tags", []) for t in tags):
                            results.append(
                                {
                                    "id": mem_id,
                                    "type": "knowledge",
                                    "data": mem_data,
                                }
                            )

            # Sort by timestamp (most recent first)
            results.sort(key=lambda x: x["data"].get("timestamp", ""), reverse=True)

            return results[:limit]

        except Exception as e:
            print(f"Error searching memory: {e}")
            return []

    def get_memory_by_id(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific memory by ID."""
        try:
            # Check conversations
            if memory_id in self.memory_index["conversations"]:
                mem_data = self.memory_index["conversations"][memory_id]
                file_path = mem_data["file"]
                return self._read_memory_from_file(file_path, memory_id)

            # Check actions
            if memory_id in self.memory_index["actions"]:
                mem_data = self.memory_index["actions"][memory_id]
                file_path = mem_data["file"]
                return self._read_memory_from_file(file_path, memory_id)

            # Check knowledge
            if memory_id in self.memory_index["knowledge"]:
                mem_data = self.memory_index["knowledge"][memory_id]
                file_path = mem_data["file"]
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)

            return None

        except Exception as e:
            print(f"Error retrieving memory: {e}")
            return None

    def _read_memory_from_file(
        self, file_path: str, memory_id: str
    ) -> Optional[Dict[str, Any]]:
        """Read a specific memory from a JSON lines file."""
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        entry = json.loads(line)
                        if entry.get("id") == memory_id:
                            return entry
            return None
        except Exception as e:
            print(f"Error reading memory from file: {e}")
            return None

    def start_autonomous_learning(self) -> bool:
        """
        Start background autonomous learning process.

        Returns:
            True if learning started successfully
        """
        # Check if command override allows autonomous learning
        if self.command_override and not self.command_override.is_protocol_enabled(
            "ml_safety"
        ):
            print("Autonomous learning allowed - safety protocols overridden")

        if self.learning_enabled:
            return False  # Already running

        self.learning_enabled = True
        self.learning_thread = threading.Thread(
            target=self._autonomous_learning_loop, daemon=True
        )
        self.learning_thread.start()

        self.store_action(
            "autonomous_learning",
            {"status": "started", "interval": self.learning_interval},
            "Background learning process initiated",
        )

        return True

    def stop_autonomous_learning(self) -> bool:
        """
        Stop background autonomous learning process.

        Returns:
            True if learning stopped successfully
        """
        if not self.learning_enabled:
            return False

        self.learning_enabled = False

        self.store_action(
            "autonomous_learning",
            {"status": "stopped"},
            "Background learning process terminated",
        )

        return True

    def _autonomous_learning_loop(self) -> None:
        """Background thread for autonomous learning."""
        while self.learning_enabled:
            try:
                # Simulate learning cycle
                self._perform_learning_cycle()

                # Wait for next cycle
                time.sleep(self.learning_interval)

            except Exception as e:
                print(f"Error in autonomous learning loop: {e}")
                time.sleep(60)  # Wait a minute before retry

    def _perform_learning_cycle(self) -> None:
        """Perform one cycle of autonomous learning."""
        try:
            timestamp = datetime.now().isoformat()

            # Placeholder for actual learning implementation
            # In a real implementation, this would:
            # 1. Query search engines for relevant information
            # 2. Process and extract knowledge
            # 3. Store learned information
            # 4. Update knowledge graph

            learning_topics = [
                "latest AI developments",
                "programming best practices",
                "technology trends",
                "user interaction patterns",
            ]

            # Simulate learning
            for topic in learning_topics:
                learned_content = {
                    "topic": topic,
                    "timestamp": timestamp,
                    "source": "autonomous_exploration",
                    "status": "placeholder",  # Would contain actual learned content
                }

                # Store learned content
                self.store_knowledge(
                    category="web_learned",
                    title=f"Learned: {topic}",
                    content=json.dumps(learned_content),
                    source="autonomous_learning",
                    tags=["autonomous", "web_learned", topic.replace(" ", "_")],
                )

                self.stats["total_learned_items"] += 1

        except Exception as e:
            print(f"Error in learning cycle: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        # Calculate memory size
        total_size = 0
        for root, dirs, files in os.walk(self.memory_dir):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)

        self.stats["memory_size_bytes"] = total_size
        self.stats["memory_size_mb"] = round(total_size / (1024 * 1024), 2)
        self.stats["learning_enabled"] = self.learning_enabled

        return self.stats.copy()

    def organize_memory(self) -> Dict[str, int]:
        """
        Organize and optimize memory structure.

        Returns:
            Dictionary with organization statistics
        """
        organized = {
            "archived_conversations": 0,
            "archived_actions": 0,
            "compressed_files": 0,
        }

        try:
            # Archive old conversations (older than 30 days)
            # Compress weekly/monthly summaries
            # This is a placeholder for actual implementation

            self.store_action(
                "memory_organization", organized, "Memory organization completed"
            )

        except Exception as e:
            print(f"Error organizing memory: {e}")

        return organized
