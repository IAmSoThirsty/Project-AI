"""
Learning path generator and manager.

REFACTORED: Now uses AI orchestrator instead of direct provider calls.
"""

import json
import logging
import os

from app.core.ai.orchestrator import run_ai, AIRequest
from app.security.path_security import safe_path_join, sanitize_filename

logger = logging.getLogger(__name__)


class LearningPathManager:
    def __init__(self, api_key=None, provider="openai", data_dir="data/learning_paths"):
        """
        Initialize learning path manager.

        Args:
            api_key: API key for the model provider (deprecated - uses orchestrator)
            provider: Model provider to use ('openai' or 'perplexity')
            data_dir: Directory to store learning paths
        """
        self.provider_name = provider
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        logger.info("LearningPathManager initialized with AI orchestrator")

    def generate_path(self, interest, skill_level="beginner", model=None):
        """
        Generate a personalized learning path via AI orchestrator.

        Args:
            interest: Topic of interest
            skill_level: User's skill level (beginner/intermediate/advanced)
            model: Optional model name override

        Returns:
            Generated learning path content or error message
        """
        try:
            # Build a prompt for the learning path
            system_context = "You are an educational expert creating learning paths."
            user_prompt = (
                f"Create a structured learning path for {interest} at "
                f"{skill_level} level.\n"
                "Include:\n"
                "1. Core concepts to master\n"
                "2. Recommended resources (tutorials, books, courses)\n"
                "3. Practice projects\n"
                "4. Timeline estimates\n"
                "5. Milestones and checkpoints"
            )
            
            full_prompt = f"{system_context}\n\n{user_prompt}"

            # Use AI orchestrator (with fallback support)
            request = AIRequest(
                task_type="chat",
                prompt=full_prompt,
                model=model or "gpt-3.5-turbo",
                provider=self.provider_name if self.provider_name != "openai" else None,
                context={"interest": interest, "skill_level": skill_level}
            )
            
            response = run_ai(request)
            
            if response.status == "success":
                return response.result
            else:
                return f"Error generating learning path: {response.error}"
                
        except Exception as e:
            logger.error("Error generating learning path: %s", e)
            return f"Error generating learning path: {str(e)}"

    def save_path(self, username, interest, path_content):
        """Save a generated learning path.
        
        Args:
            username: User identifier (sanitized for filename)
            interest: Learning interest topic
            path_content: Generated path content
        """
        # Sanitize username to prevent path traversal
        safe_username = sanitize_filename(username)
        filename = f"learning_paths_{safe_username}.json"
        filepath = safe_path_join(self.data_dir, filename)
        
        paths = {}
        if os.path.exists(filepath):
            with open(filepath) as f:
                paths = json.load(f)

        paths[interest] = {
            "content": path_content,
            "progress": 0,
            "completed_milestones": [],
        }

        with open(filepath, "w") as f:
            json.dump(paths, f)

    def get_saved_paths(self, username):
        """Get all saved learning paths for a user.
        
        Args:
            username: User identifier (sanitized for filename)
            
        Returns:
            Dictionary of saved learning paths
        """
        # Sanitize username to prevent path traversal
        safe_username = sanitize_filename(username)
        filename = f"learning_paths_{safe_username}.json"
        filepath = safe_path_join(self.data_dir, filename)
        
        if os.path.exists(filepath):
            with open(filepath) as f:
                return json.load(f)
        return {}
