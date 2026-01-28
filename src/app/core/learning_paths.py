"""
Learning path generator and manager.
"""

import json
import logging
import os

from app.core.model_providers import get_provider

logger = logging.getLogger(__name__)


class LearningPathManager:
    def __init__(self, api_key=None, provider="openai"):
        """
        Initialize learning path manager.

        Args:
            api_key: API key for the model provider
            provider: Model provider to use ('openai' or 'perplexity')
        """
        self.provider_name = provider
        self.provider = get_provider(provider, api_key=api_key)

    def generate_path(self, interest, skill_level="beginner", model=None):
        """
        Generate a personalized learning path.

        Args:
            interest: Topic of interest
            skill_level: User's skill level (beginner/intermediate/advanced)
            model: Optional model name override

        Returns:
            Generated learning path content or error message
        """
        if not self.provider.is_available():
            return f"Error: {self.provider_name} provider is not available. Please check API key."

        try:
            # Build a prompt without long indented triple-quoted literal
            # to satisfy linters
            prompt = (
                f"Create a structured learning path for {interest} at "
                f"{skill_level} level.\n"
                "Include:\n"
                "1. Core concepts to master\n"
                "2. Recommended resources (tutorials, books, courses)\n"
                "3. Practice projects\n"
                "4. Timeline estimates\n"
                "5. Milestones and checkpoints"
            )

            messages = [
                {
                    "role": "system",
                    "content": "You are an educational expert creating learning paths.",
                },
                {"role": "user", "content": prompt},
            ]

            # Use default model based on provider if not specified
            if model is None:
                model = (
                    "gpt-3.5-turbo"
                    if self.provider_name == "openai"
                    else "llama-3.1-sonar-small-128k-online"
                )

            response = self.provider.chat_completion(messages=messages, model=model)
            return response
        except Exception as e:
            logger.error(f"Error generating learning path: {e}")
            return f"Error generating learning path: {str(e)}"

    def save_path(self, username, interest, path_content):
        """Save a generated learning path"""
        filename = f"learning_paths_{username}.json"
        paths = {}
        if os.path.exists(filename):
            with open(filename) as f:
                paths = json.load(f)

        paths[interest] = {
            "content": path_content,
            "progress": 0,
            "completed_milestones": [],
        }

        with open(filename, "w") as f:
            json.dump(paths, f)

    def get_saved_paths(self, username):
        """Get all saved learning paths for a user"""
        filename = f"learning_paths_{username}.json"
        if os.path.exists(filename):
            with open(filename) as f:
                return json.load(f)
        return {}
