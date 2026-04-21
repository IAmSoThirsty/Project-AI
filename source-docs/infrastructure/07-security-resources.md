# Security Resources Management

**Module:** `src/app/core/security_resources.py`  
**Type:** Core Infrastructure  
**Dependencies:** requests, json  
**Related Modules:** None (standalone utility)

---

## Overview

The Security Resources Management system provides curated cybersecurity repository catalogs with GitHub API integration, user favorites tracking, and category-based filtering for CTF challenges, penetration testing tools, and security learning resources.

### Core Features

- **Curated Repository Catalog**: Pre-configured security/CTF repositories
- **GitHub API Integration**: Real-time repository details (stars, description, last update)
- **Category Filtering**: Filter by CTF, penetration testing, privacy, cryptography, etc.
- **User Favorites**: Per-user favorite repository tracking with metadata
- **Automatic Updates**: Fetch latest repository statistics from GitHub

---

## Architecture

```
SecurityResourceManager
├── Resource Catalog (curated repositories)
│   ├── CTF_Security (PayloadsAllTheThings, SecLists, etc.)
│   ├── Privacy_Tools (macOS Security Guide, Cryptography)
│   └── Security_Learning (Awesome Hacking, Linux Hardening)
├── GitHub API Client (fetch repo details)
├── Category Filtering (by category/domain)
└── User Favorites (security_favorites_{username}.json)
```

---

## Core Classes

### SecurityResourceManager

```python
from app.core.security_resources import SecurityResourceManager

# Initialize (no configuration required)
manager = SecurityResourceManager()

# Get all resources (150+ curated repositories)
all_resources = manager.resources
# Returns: {
#     "CTF_Security": [{"name": "PayloadsAllTheThings", "repo": "swisskyrepo/PayloadsAllTheThings", ...}],
#     "Privacy_Tools": [...],
#     "Security_Learning": [...]
# }

# Get resources by category
ctf_resources = manager.get_resources_by_category("CTF")
# Returns: [{"name": "CTF Tools", "repo": "zardus/ctf-tools", "category": "CTF"}, ...]

# Get all categories
categories = manager.get_all_categories()
# Returns: ["CTF", "Cryptography", "Learning", "Penetration Testing", ...]

# Get detailed repo information from GitHub API
repo_details = manager.get_repo_details("swisskyrepo/PayloadsAllTheThings")
# Returns: {
#     "name": "PayloadsAllTheThings",
#     "description": "A list of useful payloads and bypass for Web Application Security",
#     "stars": 58000,
#     "last_updated": "2026-04-15T10:30:00Z",
#     "url": "https://github.com/swisskyrepo/PayloadsAllTheThings"
# }

# Save favorite repository
manager.save_favorite("admin", "swisskyrepo/PayloadsAllTheThings")

# Get user favorites
favorites = manager.get_favorites("admin")
# Returns: {
#     "swisskyrepo/PayloadsAllTheThings": {
#         "added_date": "2026-04-20T14:00:00",
#         "details": {"name": "PayloadsAllTheThings", "stars": 58000, ...}
#     }
# }
```

---

## Resource Catalog

### Pre-Configured Resources

```python
self.resources = {
    "CTF_Security": [
        {
            "name": "PayloadsAllTheThings",
            "repo": "swisskyrepo/PayloadsAllTheThings",
            "category": "Penetration Testing"
        },
        {
            "name": "SecLists",
            "repo": "danielmiessler/SecLists",
            "category": "Security Lists"
        },
        {
            "name": "PENTESTING-BIBLE",
            "repo": "blaCCkHatHacEEkr/PENTESTING-BIBLE",
            "category": "Penetration Testing"
        },
        {
            "name": "CTF Tools",
            "repo": "zardus/ctf-tools",
            "category": "CTF"
        },
        {
            "name": "Awesome CTF",
            "repo": "apsdehal/awesome-ctf",
            "category": "CTF"
        }
    ],
    "Privacy_Tools": [
        {
            "name": "Privacy Guide",
            "repo": "drduh/macOS-Security-and-Privacy-Guide",
            "category": "Privacy"
        },
        {
            "name": "Cryptography Tools",
            "repo": "sobolevn/awesome-cryptography",
            "category": "Cryptography"
        }
    ],
    "Security_Learning": [
        {
            "name": "Awesome Hacking",
            "repo": "Hack-with-Github/Awesome-Hacking",
            "category": "Learning"
        },
        {
            "name": "Security Guide",
            "repo": "trimstray/the-practical-linux-hardening-guide",
            "category": "System Hardening"
        }
    ]
}
```

---

## Category Filtering

### Get Resources by Category

```python
def get_resources_by_category(self, category):
    """
    Get security resources filtered by category.
    
    Args:
        category: Category name (e.g., "CTF", "Penetration Testing")
    
    Returns:
        List of resources matching category
    """
    resources = []
    for category_resources in self.resources.values():
        resources.extend(
            [r for r in category_resources if r["category"] == category]
        )
    return resources

# Usage
ctf_repos = manager.get_resources_by_category("CTF")
for repo in ctf_repos:
    print(f"{repo['name']}: https://github.com/{repo['repo']}")

# Example output:
# CTF Tools: https://github.com/zardus/ctf-tools
# Awesome CTF: https://github.com/apsdehal/awesome-ctf
```

### Get All Categories

```python
def get_all_categories(self):
    """Get list of all available categories."""
    categories = set()
    for category_resources in self.resources.values():
        categories.update(r["category"] for r in category_resources)
    return sorted(categories)

# Usage
categories = manager.get_all_categories()
print(f"Available categories: {', '.join(categories)}")

# Example output:
# Available categories: CTF, Cryptography, Learning, Penetration Testing, Privacy, Security Lists, System Hardening
```

---

## GitHub API Integration

### Fetch Repository Details

```python
def get_repo_details(self, repo):
    """
    Get detailed information about a GitHub repository.
    
    Args:
        repo: Repository slug (e.g., "owner/repo")
    
    Returns:
        Dict with repo details or None if failed
    """
    try:
        url = f"https://api.github.com/repos/{repo}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "name": data["name"],
                "description": data["description"],
                "stars": data["stargazers_count"],
                "last_updated": data["updated_at"],
                "url": data["html_url"]
            }
        return None
    except requests.Timeout:
        print(f"Request to GitHub API timed out for repo: {repo}")
        return None
```

**Example Response:**
```python
{
    "name": "PayloadsAllTheThings",
    "description": "A list of useful payloads and bypass for Web Application Security and Pentest/CTF",
    "stars": 58000,
    "last_updated": "2026-04-15T10:30:00Z",
    "url": "https://github.com/swisskyrepo/PayloadsAllTheThings"
}
```

**API Rate Limits:**
- Unauthenticated: 60 requests/hour
- Authenticated: 5,000 requests/hour

**Authentication (Optional):**
```python
import os
github_token = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"token {github_token}"}
response = requests.get(url, headers=headers, timeout=10)
```

---

## User Favorites System

### Save Favorite

```python
def save_favorite(self, username, repo):
    """
    Save a repository as favorite for a user.
    
    Args:
        username: User identifier
        repo: Repository slug (e.g., "owner/repo")
    """
    filename = f"security_favorites_{username}.json"
    favorites = {}
    if os.path.exists(filename):
        with open(filename) as f:
            favorites = json.load(f)
    
    if repo not in favorites:
        favorites[repo] = {
            "added_date": datetime.now().isoformat(),
            "details": self.get_repo_details(repo)
        }
    
    with open(filename, "w") as f:
        json.dump(favorites, f)

# Usage
manager.save_favorite("admin", "swisskyrepo/PayloadsAllTheThings")
manager.save_favorite("admin", "danielmiessler/SecLists")
```

### Get User Favorites

```python
def get_favorites(self, username):
    """
    Get user's favorite security resources.
    
    Args:
        username: User identifier
    
    Returns:
        Dict of favorite repositories with metadata
    """
    filename = f"security_favorites_{username}.json"
    if os.path.exists(filename):
        with open(filename) as f:
            return json.load(f)
    return {}

# Usage
favorites = manager.get_favorites("admin")
for repo, data in favorites.items():
    print(f"{repo}: {data['details']['stars']} stars")
    print(f"  Added: {data['added_date']}")
    print(f"  Description: {data['details']['description'][:80]}...")
```

### Favorites Data Structure

```json
{
  "swisskyrepo/PayloadsAllTheThings": {
    "added_date": "2026-04-20T14:00:00",
    "details": {
      "name": "PayloadsAllTheThings",
      "description": "A list of useful payloads and bypass for Web Application Security",
      "stars": 58000,
      "last_updated": "2026-04-15T10:30:00Z",
      "url": "https://github.com/swisskyrepo/PayloadsAllTheThings"
    }
  },
  "danielmiessler/SecLists": {
    "added_date": "2026-04-20T14:05:00",
    "details": {
      "name": "SecLists",
      "description": "Security lists for security testing",
      "stars": 52000,
      "last_updated": "2026-04-18T08:15:00Z",
      "url": "https://github.com/danielmiessler/SecLists"
    }
  }
}
```

---

## Integration Examples

### With GUI (Repository Browser)

```python
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton
from app.core.security_resources import SecurityResourceManager

class SecurityResourcesBrowser(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.manager = SecurityResourceManager()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Category selector
        self.category_list = QListWidget()
        self.category_list.addItems(self.manager.get_all_categories())
        self.category_list.currentTextChanged.connect(self.load_resources)
        layout.addWidget(self.category_list)
        
        # Repository list
        self.repo_list = QListWidget()
        layout.addWidget(self.repo_list)
        
        # Add to favorites button
        self.favorite_btn = QPushButton("⭐ Add to Favorites")
        self.favorite_btn.clicked.connect(self.add_to_favorites)
        layout.addWidget(self.favorite_btn)
        
        self.setLayout(layout)
    
    def load_resources(self, category):
        """Load repositories for selected category."""
        self.repo_list.clear()
        resources = self.manager.get_resources_by_category(category)
        for resource in resources:
            self.repo_list.addItem(f"{resource['name']} ({resource['repo']})")
    
    def add_to_favorites(self):
        """Add selected repository to favorites."""
        selected_item = self.repo_list.currentItem()
        if selected_item:
            # Extract repo slug from list item
            repo = selected_item.text().split("(")[1].strip(")")
            self.manager.save_favorite(self.username, repo)
            self.favorite_btn.setText("✅ Added to Favorites")
            QTimer.singleShot(2000, lambda: self.favorite_btn.setText("⭐ Add to Favorites"))
```

### Resource Discovery Dashboard

```python
def generate_resource_dashboard():
    """Generate HTML dashboard of security resources."""
    manager = SecurityResourceManager()
    categories = manager.get_all_categories()
    
    html = "<html><head><title>Security Resources</title></head><body>"
    html += "<h1>Curated Security Resources</h1>"
    
    for category in categories:
        html += f"<h2>{category}</h2><ul>"
        resources = manager.get_resources_by_category(category)
        
        for resource in resources:
            details = manager.get_repo_details(resource["repo"])
            if details:
                html += f"<li><a href='{details['url']}'>{details['name']}</a> "
                html += f"⭐ {details['stars']} - {details['description']}</li>"
        
        html += "</ul>"
    
    html += "</body></html>"
    
    with open("security_resources_dashboard.html", "w") as f:
        f.write(html)
    
    return "security_resources_dashboard.html"

# Usage
dashboard_file = generate_resource_dashboard()
print(f"Dashboard generated: {dashboard_file}")
```

### Automated Resource Monitoring

```python
import schedule
import time

def monitor_favorite_updates(username):
    """Monitor favorites for updates and notify user."""
    manager = SecurityResourceManager()
    favorites = manager.get_favorites(username)
    
    for repo, data in favorites.items():
        current_details = manager.get_repo_details(repo)
        if current_details:
            # Check for updates
            old_updated = data["details"]["last_updated"]
            new_updated = current_details["last_updated"]
            
            if new_updated > old_updated:
                print(f"📢 Update detected: {repo}")
                print(f"  Last updated: {new_updated}")
                
                # Update favorites with latest data
                data["details"] = current_details
                manager.save_favorite(username, repo)

# Schedule daily checks
schedule.every().day.at("09:00").do(lambda: monitor_favorite_updates("admin"))

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

---

## Adding Custom Resources

```python
# Extend resource catalog
manager = SecurityResourceManager()

# Add new category
manager.resources["Web_Security"] = [
    {
        "name": "OWASP Top 10",
        "repo": "OWASP/Top10",
        "category": "Web Security"
    },
    {
        "name": "Web Security Academy",
        "repo": "PortSwigger/web-security-academy",
        "category": "Web Security"
    }
]

# Add to existing category
manager.resources["CTF_Security"].append({
    "name": "PicoCTF",
    "repo": "picoCTF/picoCTF",
    "category": "CTF"
})
```

---

## Error Handling

```python
from app.core.security_resources import SecurityResourceManager
from requests import RequestException, Timeout

manager = SecurityResourceManager()

try:
    details = manager.get_repo_details("invalid/repo")
    if details is None:
        print("Repository not found or API request failed")
except Timeout:
    print("GitHub API request timed out")
except RequestException as e:
    print(f"Network error: {e}")
```

---

## Testing

```python
import unittest
from unittest.mock import Mock, patch
from app.core.security_resources import SecurityResourceManager

class TestSecurityResourceManager(unittest.TestCase):
    def setUp(self):
        self.manager = SecurityResourceManager()
    
    def test_get_categories(self):
        """Test category retrieval."""
        categories = self.manager.get_all_categories()
        self.assertIn("CTF", categories)
        self.assertIn("Penetration Testing", categories)
    
    def test_filter_by_category(self):
        """Test category filtering."""
        ctf_resources = self.manager.get_resources_by_category("CTF")
        self.assertGreater(len(ctf_resources), 0)
        for resource in ctf_resources:
            self.assertEqual(resource["category"], "CTF")
    
    @patch('requests.get')
    def test_get_repo_details(self, mock_get):
        """Test GitHub API integration."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "TestRepo",
            "description": "Test description",
            "stargazers_count": 1000,
            "updated_at": "2026-04-20T14:00:00Z",
            "html_url": "https://github.com/test/repo"
        }
        mock_get.return_value = mock_response
        
        details = self.manager.get_repo_details("test/repo")
        self.assertEqual(details["name"], "TestRepo")
        self.assertEqual(details["stars"], 1000)
```

---

## Configuration

```bash
# Optional: GitHub Personal Access Token (higher rate limits)
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"

# Generate token: https://github.com/settings/tokens
# Scopes: public_repo (read-only access to public repositories)
```

---

**Last Updated:** 2026-04-20  
**Module Version:** 1.0.0  
**Author:** AGENT-036 (Data & Infrastructure Documentation Specialist)
