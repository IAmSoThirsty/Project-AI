"""
Learning path generator and manager.
"""
import openai
import json
import os


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
        except Exception as generation_error:
            return f"Error generating learning path: {str(generation_error)}"

    def save_path(self, username, interest, path_content):
        """Save a generated learning path"""
        filename = f"learning_paths_{username}.json"
        paths = {}
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                paths = json.load(f)

        paths[interest] = {
            'content': path_content,
            'progress': 0,
            'completed_milestones': []
        }

        with open(filename, 'w') as f:
            json.dump(paths, f)

    def get_saved_paths(self, username):
        """Get all saved learning paths for a user"""
        filename = f"learning_paths_{username}.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return {}
