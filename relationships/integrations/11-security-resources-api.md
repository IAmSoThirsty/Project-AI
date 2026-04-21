# Security Resources API Relationship Map

**Status**: 🟢 Production | **Type**: External API Integration  
**Priority**: P2 Feature | **Governance**: GitHub API

---


## Navigation

**Location**: `relationships\integrations\11-security-resources-api.md`

**Parent**: [[relationships\integrations\README.md]]


## Overview

Security Resources Manager provides access to curated security tools and repositories via GitHub API. Tracks CTF resources, penetration testing tools, privacy guides, and security education materials.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           SECURITY RESOURCE MANAGER                          │
│         src/app/core/security_resources.py                   │
│  ┌──────────────────────────────────────────┐              │
│  │ Resource Categories (3):                 │              │
│  │ - CTF_Security (5 repos)                 │              │
│  │ - Privacy_Tools (2 repos)                │              │
│  │ - Security_Education (planned)           │              │
│  └──────────────────────────────────────────┘              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                  GITHUB REST API v3                          │
│            https://api.github.com                            │
│  ┌──────────────────────────────────────────┐              │
│  │ Endpoints Used:                          │              │
│  │ - GET /repos/{owner}/{repo}              │              │
│  │ - GET /repos/{owner}/{repo}/commits      │              │
│  │ - GET /rate_limit                        │              │
│  └──────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

---

## Tracked Resources

### Category: CTF_Security

**5 Repositories**:

1. **PayloadsAllTheThings** (`swisskyrepo/PayloadsAllTheThings`)
   - **Stars**: ~55,000
   - **Purpose**: Comprehensive payload collection for web security testing
   - **Languages**: Python, Shell
   - **Topics**: penetration-testing, security, payloads, ctf

2. **SecLists** (`danielmiessler/SecLists`)
   - **Stars**: ~52,000
   - **Purpose**: Security testing wordlists (usernames, passwords, URLs, fuzzing)
   - **Languages**: Text files
   - **Topics**: security, wordlists, pentesting

3. **PENTESTING-BIBLE** (`blaCCkHatHacEEkr/PENTESTING-BIBLE`)
   - **Stars**: ~12,000
   - **Purpose**: Collection of pentesting tools and techniques
   - **Languages**: Python, Shell
   - **Topics**: pentesting, security, hacking

4. **CTF Tools** (`zardus/ctf-tools`)
   - **Stars**: ~8,000
   - **Purpose**: Setup scripts for CTF competition tools
   - **Languages**: Shell, Python
   - **Topics**: ctf, tools, security

5. **Awesome CTF** (`apsdehal/awesome-ctf`)
   - **Stars**: ~9,000
   - **Purpose**: Curated list of CTF resources
   - **Languages**: Markdown
   - **Topics**: ctf, awesome-list, resources

### Category: Privacy_Tools

**2 Repositories**:

1. **Privacy Guide** (`drduh/macOS-Security-and-Privacy-Guide`)
   - **Stars**: ~22,000
   - **Purpose**: macOS security and privacy configuration guide
   - **Languages**: Markdown
   - **Topics**: privacy, security, macos

2. **PrivacyTools** (`privacytoolsIO/privacytools.io`)
   - **Stars**: ~16,000
   - **Purpose**: Privacy-focused tools and services directory
   - **Languages**: HTML, CSS
   - **Topics**: privacy, security, tools

---

## Core Functionality

### Fetch Repository Metadata

**Method**: `fetch_resources(category="CTF_Security")`

**Returns**: List of repository metadata dictionaries

```python
from app.core.security_resources import SecurityResourceManager

manager = SecurityResourceManager()

# Fetch CTF resources
resources = manager.fetch_resources("CTF_Security")

for resource in resources:
    print(f"{resource['name']}: {resource['stars']} stars")
    print(f"  Description: {resource['description']}")
    print(f"  URL: {resource['url']}")
    print(f"  Last updated: {resource['last_updated']}")
```

**Example Output**:
```python
[
    {
        "name": "PayloadsAllTheThings",
        "repo": "swisskyrepo/PayloadsAllTheThings",
        "stars": 55342,
        "description": "A list of useful payloads and bypass for Web Application Security",
        "url": "https://github.com/swisskyrepo/PayloadsAllTheThings",
        "last_updated": "2025-01-25T10:30:00Z",
        "category": "Penetration Testing"
    },
    {
        "name": "SecLists",
        "repo": "danielmiessler/SecLists",
        "stars": 52108,
        "description": "SecLists is the security tester's companion",
        "url": "https://github.com/danielmiessler/SecLists",
        "last_updated": "2025-01-24T14:20:00Z",
        "category": "Security Lists"
    }
]
```

### Get Latest Commits

**Method**: `get_latest_commits(repo, count=5)`

**Returns**: List of commit summaries

```python
commits = manager.get_latest_commits("swisskyrepo/PayloadsAllTheThings", count=5)

for commit in commits:
    print(f"{commit['sha']}: {commit['message']}")
    print(f"  Author: {commit['author']} on {commit['date']}")
```

**Example Output**:
```python
[
    {
        "sha": "abc1234",
        "message": "Added new SQL injection payloads",
        "author": "swisskyrepo",
        "date": "2025-01-25T08:00:00Z"
    },
    {
        "sha": "def5678",
        "message": "Updated XSS bypass techniques",
        "author": "contributor123",
        "date": "2025-01-24T16:30:00Z"
    }
]
```

---

## Implementation

### Resource Registry

**Data Structure**:
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
        # ... 3 more repos
    ],
    "Privacy_Tools": [
        {
            "name": "Privacy Guide",
            "repo": "drduh/macOS-Security-and-Privacy-Guide",
            "category": "Privacy"
        },
        {
            "name": "PrivacyTools",
            "repo": "privacytoolsIO/privacytools.io",
            "category": "Privacy"
        }
    ]
}
```

### API Integration

```python
import requests
import logging

logger = logging.getLogger(__name__)

def fetch_resources(self, category="CTF_Security"):
    """Fetch metadata for repositories in a category."""
    results = []
    
    for resource in self.resources.get(category, []):
        repo = resource["repo"]
        url = f"https://api.github.com/repos/{repo}"
        
        try:
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results.append({
                    "name": resource["name"],
                    "repo": repo,
                    "stars": data.get("stargazers_count", 0),
                    "description": data.get("description", ""),
                    "url": data.get("html_url", ""),
                    "last_updated": data.get("updated_at", ""),
                    "category": resource["category"],
                    "language": data.get("language", ""),
                    "topics": data.get("topics", [])
                })
            elif response.status_code == 404:
                logger.warning(f"Repository not found: {repo}")
            elif response.status_code == 403:
                logger.error(f"Rate limit exceeded or access denied: {repo}")
            else:
                logger.error(f"GitHub API error {response.status_code} for {repo}")
        
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {repo}: {e}")
    
    return results

def get_latest_commits(self, repo, count=5):
    """Get latest commits from a repository."""
    url = f"https://api.github.com/repos/{repo}/commits?per_page={count}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            commits = response.json()
            return [
                {
                    "sha": c["sha"][:7],
                    "message": c["commit"]["message"].split("\n")[0],
                    "author": c["commit"]["author"]["name"],
                    "date": c["commit"]["author"]["date"]
                }
                for c in commits
            ]
        else:
            logger.error(f"Failed to fetch commits: {response.status_code}")
            return []
    
    except requests.RequestException as e:
        logger.error(f"Failed to fetch commits for {repo}: {e}")
        return []
```

---

## Configuration

### Environment Variables

```bash
# OPTIONAL (for higher rate limits)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx

# Resource cache TTL (seconds)
SECURITY_RESOURCES_CACHE_TTL=3600
```

### Rate Limit Management

**Free Tier** (unauthenticated): 60 requests/hour  
**Authenticated**: 5,000 requests/hour

**Strategy**: Cache responses for 1 hour to minimize API calls

```python
from datetime import datetime, timedelta

class SecurityResourceManager:
    def __init__(self):
        self.resources = {...}
        self._cache = {}
        self._cache_ttl = timedelta(hours=1)
    
    def fetch_resources(self, category):
        """Fetch with caching."""
        cache_key = f"resources_{category}"
        
        # Check cache
        if cache_key in self._cache:
            cached_time, cached_data = self._cache[cache_key]
            if datetime.now() - cached_time < self._cache_ttl:
                logger.debug(f"Cache hit for {category}")
                return cached_data
        
        # Fetch from API
        data = self._fetch_from_github(category)
        self._cache[cache_key] = (datetime.now(), data)
        
        return data
```

---

## Error Handling

### Common Errors

1. **404 Not Found**: Repository renamed or deleted
   - **Mitigation**: Skip resource, update registry

2. **403 Forbidden**: Rate limit exceeded
   - **Mitigation**: Return cached data, wait for reset

3. **500 Server Error**: GitHub API outage
   - **Mitigation**: Return cached data, log error

---

## Security

### API Token Security

```python
import os

# Load token from environment (never hardcode)
github_token = os.getenv("GITHUB_TOKEN")

if github_token:
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }
else:
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
```

### Repository Validation

```python
import re

def validate_repo_name(repo: str) -> bool:
    """Validate repository name format (owner/repo)."""
    pattern = r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$"
    return bool(re.match(pattern, repo))

# Usage
if not validate_repo_name(user_input_repo):
    raise ValueError("Invalid repository format")
```

---

## Performance

### Benchmarks

| Operation | Latency | Cache Hit Ratio |
|-----------|---------|-----------------|
| Fetch resources (7 repos) | 3-5s | 95% (1hr cache) |
| Get commits (1 repo) | 0.5s | 90% (1hr cache) |
| Rate limit check | 0.2s | N/A |

---

## Testing

```python
# tests/test_security_resources.py
def test_fetch_resources():
    manager = SecurityResourceManager()
    resources = manager.fetch_resources("CTF_Security")
    
    assert len(resources) >= 5
    assert all("name" in r for r in resources)
    assert all("stars" in r for r in resources)

def test_get_latest_commits():
    manager = SecurityResourceManager()
    commits = manager.get_latest_commits("swisskyrepo/PayloadsAllTheThings")
    
    assert len(commits) <= 5
    assert all("sha" in c for c in commits)
```

---

## GUI Integration

**Panel**: Security Resources Browser (planned)

**Features**:
- Category tabs (CTF, Privacy, Education)
- Repository cards with stars, description, last update
- View commits button
- Open in browser button

---

## Future Enhancements

### Phase 1: Additional Categories ⏳ PLANNED
- **Security_Education**: Courses, tutorials, books
- **Bug_Bounty**: Platforms, writeups, tools
- **Malware_Analysis**: Reverse engineering tools

### Phase 2: Local Repository Cloning 🔮 FUTURE
- Clone repositories locally
- Search across cloned repos
- Offline access to security tools

### Phase 3: Tool Integration 🔮 FUTURE
- Launch security tools from GUI
- Run automated scans
- Generate reports

---

## Related Systems

- **[02-github-integration.md](02-github-integration.md)**: GitHub API details
- **[05-external-apis.md](05-external-apis.md)**: External API patterns
- **[04-database-connectors.md](04-database-connectors.md)**: Cache storage

---

**Last Updated**: 2025-01-26  
**Maintained By**: AGENT-060  
**Review Cycle**: Quarterly
