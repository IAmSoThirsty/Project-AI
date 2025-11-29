"""
Security resources and repository management.
"""
import requests
import json
import os
from datetime import datetime
from app.core.network_utils import is_online


# Offline cached repository details for common security resources
OFFLINE_REPO_CACHE = {
    "swisskyrepo/PayloadsAllTheThings": {
        "name": "PayloadsAllTheThings",
        "description": "A list of useful payloads and bypass for Web Application Security and Pentest/CTF",
        "stars": 60000,
        "last_updated": "2024-01-01T00:00:00Z",
        "url": "https://github.com/swisskyrepo/PayloadsAllTheThings",
        "offline_cached": True
    },
    "danielmiessler/SecLists": {
        "name": "SecLists",
        "description": "Collection of multiple types of lists used during security assessments",
        "stars": 55000,
        "last_updated": "2024-01-01T00:00:00Z",
        "url": "https://github.com/danielmiessler/SecLists",
        "offline_cached": True
    },
    "blaCCkHatHacEEkr/PENTESTING-BIBLE": {
        "name": "PENTESTING-BIBLE",
        "description": "Comprehensive resource for penetration testing and ethical hacking",
        "stars": 15000,
        "last_updated": "2024-01-01T00:00:00Z",
        "url": "https://github.com/blaCCkHatHacEEkr/PENTESTING-BIBLE",
        "offline_cached": True
    },
    "zardus/ctf-tools": {
        "name": "ctf-tools",
        "description": "Collection of setup scripts to install various CTF tools",
        "stars": 8000,
        "last_updated": "2024-01-01T00:00:00Z",
        "url": "https://github.com/zardus/ctf-tools",
        "offline_cached": True
    },
    "apsdehal/awesome-ctf": {
        "name": "awesome-ctf",
        "description": "Curated list of CTF frameworks, libraries, resources and tools",
        "stars": 9000,
        "last_updated": "2024-01-01T00:00:00Z",
        "url": "https://github.com/apsdehal/awesome-ctf",
        "offline_cached": True
    },
    "drduh/macOS-Security-and-Privacy-Guide": {
        "name": "macOS-Security-and-Privacy-Guide",
        "description": "Guide to securing and improving privacy on macOS",
        "stars": 21000,
        "last_updated": "2024-01-01T00:00:00Z",
        "url": "https://github.com/drduh/macOS-Security-and-Privacy-Guide",
        "offline_cached": True
    },
    "sobolevn/awesome-cryptography": {
        "name": "awesome-cryptography",
        "description": "Curated list of cryptography resources and links",
        "stars": 5000,
        "last_updated": "2024-01-01T00:00:00Z",
        "url": "https://github.com/sobolevn/awesome-cryptography",
        "offline_cached": True
    },
    "Hack-with-Github/Awesome-Hacking": {
        "name": "Awesome-Hacking",
        "description": "Collection of awesome lists for hackers, pentesters & security researchers",
        "stars": 80000,
        "last_updated": "2024-01-01T00:00:00Z",
        "url": "https://github.com/Hack-with-Github/Awesome-Hacking",
        "offline_cached": True
    },
    "trimstray/the-practical-linux-hardening-guide": {
        "name": "the-practical-linux-hardening-guide",
        "description": "Practical guide to hardening a Linux system",
        "stars": 10000,
        "last_updated": "2024-01-01T00:00:00Z",
        "url": "https://github.com/trimstray/the-practical-linux-hardening-guide",
        "offline_cached": True
    }
}


class SecurityResourceManager:
    def __init__(self, cache_dir: str = None):
        self.cache_dir = cache_dir or os.getenv('DATA_DIR', 'data')
        self.cache_file = os.path.join(self.cache_dir, 'repo_cache.json')
        self._local_cache = self._load_cache()

        # break long entries across multiple lines to keep line lengths reasonable
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
                {"name": "CTF Tools", "repo": "zardus/ctf-tools", "category": "CTF"},
                {"name": "Awesome CTF", "repo": "apsdehal/awesome-ctf", "category": "CTF"},
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

    def _load_cache(self) -> dict:
        """Load cached repository details from disk."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save_cache(self) -> None:
        """Save repository cache to disk."""
        try:
            os.makedirs(self.cache_dir, exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self._local_cache, f)
        except IOError:
            pass

    def _get_cached_details(self, repo: str) -> dict | None:
        """Get cached repository details (local cache first, then built-in)."""
        # Check local cache first (more up-to-date)
        if repo in self._local_cache:
            return self._local_cache[repo]
        # Fall back to built-in offline cache
        if repo in OFFLINE_REPO_CACHE:
            return OFFLINE_REPO_CACHE[repo]
        return None

    def get_resources_by_category(self, category):
        """Get security resources filtered by category"""
        resources = []
        for category_resources in self.resources.values():
            resources.extend([r for r in category_resources if r['category'] == category])
        return resources

    def get_all_categories(self):
        """Get list of all available categories"""
        categories = set()
        for category_resources in self.resources.values():
            categories.update(r['category'] for r in category_resources)
        return sorted(categories)

    def get_repo_details(self, repo: str, force_online: bool = False) -> dict | None:
        """Get detailed information about a GitHub repository.

        Uses cached data when offline, fetches fresh data when online.
        """
        # Check if we're online
        if is_online(timeout=2.0) and (force_online or repo not in self._local_cache):
            try:
                url = f"https://api.github.com/repos/{repo}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    details = {
                        'name': data['name'],
                        'description': data['description'],
                        'stars': data['stargazers_count'],
                        'last_updated': data['updated_at'],
                        'url': data['html_url'],
                        'offline_cached': False
                    }
                    # Update local cache
                    self._local_cache[repo] = details
                    self._save_cache()
                    return details
            except Exception as fetch_error:
                print(f"Error fetching repo details: {str(fetch_error)}")
                # Fall through to cached data

        # Return cached data (offline mode or fetch failed)
        cached = self._get_cached_details(repo)
        if cached:
            return cached

        # No cached data available
        return {
            'name': repo.split('/')[-1],
            'description': 'Details unavailable offline',
            'stars': 0,
            'last_updated': None,
            'url': f'https://github.com/{repo}',
            'offline_cached': True
        }

    def save_favorite(self, username, repo):
        """Save a repository as favorite for a user"""
        filename = f"security_favorites_{username}.json"
        favorites = {}
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                favorites = json.load(f)

        if repo not in favorites:
            favorites[repo] = {
                'added_date': datetime.now().isoformat(),
                'details': self.get_repo_details(repo)
            }

        with open(filename, 'w') as f:
            json.dump(favorites, f)

    def get_favorites(self, username):
        """Get user's favorite security resources"""
        filename = f"security_favorites_{username}.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return {}

    def refresh_cache(self) -> int:
        """Refresh the local cache with fresh data from GitHub.

        Returns the number of repositories successfully updated.
        """
        if not is_online():
            return 0

        updated = 0
        for category_resources in self.resources.values():
            for resource in category_resources:
                repo = resource['repo']
                details = self.get_repo_details(repo, force_online=True)
                if details and not details.get('offline_cached'):
                    updated += 1

        return updated
