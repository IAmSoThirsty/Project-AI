"""
Security resources and repository management.
"""

import json
import logging
import os
from datetime import datetime

import requests

from app.core.utils.path_validator import validate_path
from app.core.utils.secure_storage import SecureStorage

logger = logging.getLogger(__name__)


class SecurityResourceManager:
    def __init__(self):
        self.storage = SecureStorage()
        # break long entries across multiple lines to keep line
        # lengths reasonable
        self.resources = {
            "CTF_Security": [
                {
                    "name": "PayloadsAllTheThings",
                    "repo": "swisskyrepo/PayloadsAllTheThings",
                    "category": "Penetration Testing",
                },
                {
                    "name": "SecLists",
                    "repo": "danielmiessler/SecLists",
                    "category": "Security Lists",
                },
                {
                    "name": "PENTESTING-BIBLE",
                    "repo": "blaCCkHatHacEEkr/PENTESTING-BIBLE",
                    "category": "Penetration Testing",
                },
                {
                    "name": "CTF Tools",
                    "repo": "zardus/ctf-tools",
                    "category": "CTF",
                },
                {
                    "name": "Awesome CTF",
                    "repo": "apsdehal/awesome-ctf",
                    "category": "CTF",
                },
            ],
            "Privacy_Tools": [
                {
                    "name": "Privacy Guide",
                    "repo": "drduh/macOS-Security-and-Privacy-Guide",
                    "category": "Privacy",
                },
                {
                    "name": "Cryptography Tools",
                    "repo": "sobolevn/awesome-cryptography",
                    "category": "Cryptography",
                },
            ],
            "Security_Learning": [
                {
                    "name": "Awesome Hacking",
                    "repo": "Hack-with-Github/Awesome-Hacking",
                    "category": "Learning",
                },
                {
                    "name": "Security Guide",
                    "repo": "trimstray/the-practical-linux-hardening-guide",
                    "category": "System Hardening",
                },
            ],
        }

    def get_resources_by_category(self, category):
        """Get security resources filtered by category"""
        resources = []
        for category_resources in self.resources.values():
            resources.extend(
                [r for r in category_resources if r["category"] == category]
            )
        return resources

    def get_all_categories(self):
        """Get list of all available categories"""
        categories = set()
        for category_resources in self.resources.values():
            categories.update(r["category"] for r in category_resources)
        return sorted(categories)

    def get_repo_details(self, repo):
        """Get detailed information about a GitHub repository"""
        try:
            url = f"https://api.github.com/repos/{repo}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data["name"],
                    "description": data["description"],
                    "stars": data["stargazers_count"],
                    "last_updated": data["updated_at"],
                    "url": data["html_url"],
                }
            return None
        except Exception as e:
            print(f"Error fetching repo details: {str(e)}")
            return None

    def save_favorite(self, username, repo):
        """Save a repository as favorite for a user securely"""
        filename = (
            validate_path(f"security_favorites_{username}.json", os.getcwd())
            or f"security_favorites_{username}.json"
        )

        # Load existing (encrypted or plain)
        favorites = self.storage.load_encrypted_json(filename)
        if favorites is None:
            if os.path.exists(filename):
                try:
                    with open(filename) as f:
                        favorites = json.load(f)
                except Exception:
                    favorites = {}
            else:
                favorites = {}

        if repo not in favorites:
            favorites[repo] = {
                "added_date": datetime.now().isoformat(),
                "details": self.get_repo_details(repo),
            }

        try:
            self.storage.save_encrypted_json(filename, favorites)
        except Exception as e:
            logger.error(f"Failed to save favorites securely: {e}")
            raise

    def get_favorites(self, username):
        """Get user's favorite security resources securely"""
        filename = (
            validate_path(f"security_favorites_{username}.json", os.getcwd())
            or f"security_favorites_{username}.json"
        )

        # Try encrypted first
        favorites = self.storage.load_encrypted_json(filename)
        if favorites is not None:
            return favorites

        # Fallback to plain if it exists (migration)
        if os.path.exists(filename):
            try:
                with open(filename) as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
