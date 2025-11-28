"""
Learning path generator and manager.
"""
import openai
import os

from app.core.json_file_utils import load_json_file, save_json_file


class LearningPathManager:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key

    def generate_path(self, interest, skill_level="beginner"):
        """Generate a personalized learning path"""
        try:
            # Build a prompt without long indented triple-quoted literal to satisfy linters
            prompt = (
                f"Create a structured learning path for {interest} at {skill_level} level.\n"
                "Include:\n"
                "1. Core concepts to master\n"
                "2. Recommended resources (tutorials, books, courses)\n"
                "3. Practice projects\n"
                "4. Timeline estimates\n"
                "5. Milestones and checkpoints"
            )

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an educational expert creating learning paths."},
                    {"role": "user", "content": prompt},
                ],
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating learning path: {str(e)}"

    def save_path(self, username, interest, path_content):
        """Save a generated learning path"""
        filename = f"learning_paths_{username}.json"
        paths = load_json_file(filename)

        paths[interest] = {
            'content': path_content,
            'progress': 0,
            'completed_milestones': []
        }

        save_json_file(filename, paths)

    def get_saved_paths(self, username):
        """Get all saved learning paths for a user"""
        filename = f"learning_paths_{username}.json"
        return load_json_file(filename)
