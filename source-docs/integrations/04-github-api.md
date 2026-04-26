# GitHub API Integration

## Overview

Project-AI integrates with GitHub's REST API for security resource management, repository discovery, and cybersecurity knowledge curation. The `SecurityResourceManager` (`src/app/core/security_resources.py` [[src/app/core/security_resources.py]]) provides programmatic access to curated CTF tools, penetration testing frameworks, and security learning resources hosted on GitHub.

## Architecture

### Integration Components

```
Application Layer (Security Dashboard)
    ↓
SecurityResourceManager
    ↓
GitHub REST API v3
    ↓
Public Repository Data
```

### Key Features

1. **Resource Categorization**: CTF tools, privacy tools, security learning
2. **Repository Metadata Retrieval**: Stars, description, last update
3. **Dynamic Discovery**: Search GitHub for security-related repositories
4. **Rate-Aware Access**: Respects GitHub rate limits (60/hour unauthenticated, 5000/hour authenticated)

## Configuration

### Environment Variables

```bash
# Optional: Increases rate limit from 60 to 5000 requests/hour
GITHUB_TOKEN=ghp_...                    # Personal access token from github.com/settings/tokens

# Optional: Custom GitHub API endpoint (for GitHub Enterprise)
GITHUB_API_URL=https://api.github.com   # Default
```

### Setup Instructions

1. **Generate Personal Access Token (Optional)**
   ```bash
   # Visit https://github.com/settings/tokens
   # Create "Classic" token with 'public_repo' scope
   # Copy to .env file
   ```

2. **Verify Access**
   ```python
   import requests
   
   headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}
   response = requests.get("https://api.github.com/rate_limit", headers=headers)
   
   print(f"Rate limit: {response.json()['rate']['limit']}")
   # Should show 5000 with token, 60 without
   ```

## Core Implementation

### SecurityResourceManager Class

```python
# src/app/core/security_resources.py

import requests
import json
from datetime import datetime

class SecurityResourceManager:
    """Manages curated security resources from GitHub."""
    
    def __init__(self):
        """Initialize with predefined resource catalog."""
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
    
    def get_resources_by_category(self, category: str) -> list[dict]:
        """Filter resources by category (e.g., 'CTF', 'Penetration Testing')."""
        resources = []
        for category_resources in self.resources.values():
            resources.extend(
                [r for r in category_resources if r["category"] == category]
            )
        return resources
    
    def get_all_categories(self) -> list[str]:
        """Get list of all available categories."""
        categories = set()
        for category_resources in self.resources.values():
            categories.update(r["category"] for r in category_resources)
        return sorted(categories)
    
    def get_repo_details(self, repo: str) -> dict | None:
        """
        Fetch detailed repository information from GitHub API.
        
        Args:
            repo: Repository in format "owner/name"
        
        Returns:
            Dictionary with name, description, stars, last_updated, url
        """
        try:
            url = f"https://api.github.com/repos/{repo}"
            headers = {}
            
            # Use authentication if available
            token = os.getenv("GITHUB_TOKEN")
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data["name"],
                    "description": data["description"],
                    "stars": data["stargazers_count"],
                    "forks": data["forks_count"],
                    "last_updated": data["updated_at"],
                    "url": data["html_url"],
                    "language": data["language"],
                    "topics": data.get("topics", [])
                }
            else:
                logger.error(f"GitHub API error {response.status_code}: {repo}")
                return None
        
        except requests.Timeout:
            logger.warning(f"GitHub API timeout for {repo}")
            return None
        except Exception as e:
            logger.error(f"Error fetching repo details: {e}")
            return None
```

## Usage Patterns

### 1. List Available Resources

```python
from app.core.security_resources import SecurityResourceManager

manager = SecurityResourceManager()

# Get all categories
categories = manager.get_all_categories()
print(f"Categories: {categories}")
# Output: ['CTF', 'Cryptography', 'Learning', 'Penetration Testing', 'Privacy', 'System Hardening']

# Get resources by category
ctf_tools = manager.get_resources_by_category("CTF")
for tool in ctf_tools:
    print(f"- {tool['name']}: {tool['repo']}")
```

### 2. Fetch Repository Metadata

```python
manager = SecurityResourceManager()

# Get detailed info for specific repository
repo_info = manager.get_repo_details("swisskyrepo/PayloadsAllTheThings")

if repo_info:
    print(f"Name: {repo_info['name']}")
    print(f"Description: {repo_info['description']}")
    print(f"Stars: {repo_info['stars']:,}")
    print(f"Last Updated: {repo_info['last_updated']}")
    print(f"URL: {repo_info['url']}")
```

### 3. Batch Repository Analysis

```python
import concurrent.futures

def analyze_repositories(repos: list[str]) -> dict:
    """Fetch metadata for multiple repositories in parallel."""
    manager = SecurityResourceManager()
    
    def fetch_single(repo: str) -> tuple[str, dict]:
        return repo, manager.get_repo_details(repo)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = dict(executor.map(lambda r: fetch_single(r), repos))
    
    return results

# Usage
repos = [
    "swisskyrepo/PayloadsAllTheThings",
    "danielmiessler/SecLists",
    "zardus/ctf-tools"
]

metadata = analyze_repositories(repos)

# Find most popular
sorted_repos = sorted(
    metadata.items(),
    key=lambda x: x[1]["stars"] if x[1] else 0,
    reverse=True
)

print(f"Most starred: {sorted_repos[0][0]} ({sorted_repos[0][1]['stars']} stars)")
```

### 4. Search for Security Tools

```python
import requests

def search_github_security_tools(query: str, max_results: int = 10) -> list[dict]:
    """Search GitHub for security-related repositories."""
    
    url = "https://api.github.com/search/repositories"
    headers = {}
    
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    params = {
        "q": f"{query} topic:security",
        "sort": "stars",
        "order": "desc",
        "per_page": max_results
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    
    results = []
    for item in data["items"]:
        results.append({
            "name": item["name"],
            "full_name": item["full_name"],
            "description": item["description"],
            "stars": item["stargazers_count"],
            "language": item["language"],
            "url": item["html_url"]
        })
    
    return results

# Usage
tools = search_github_security_tools("penetration testing")
for tool in tools:
    print(f"{tool['name']} ({tool['stars']} stars): {tool['description']}")
```

### 5. Monitor Repository Updates

```python
from datetime import datetime, timedelta

def check_repository_updates(repos: list[str], days_threshold: int = 30) -> list[dict]:
    """Check which repositories have been updated recently."""
    manager = SecurityResourceManager()
    
    recent_updates = []
    cutoff_date = datetime.now() - timedelta(days=days_threshold)
    
    for repo in repos:
        details = manager.get_repo_details(repo)
        if details:
            last_updated = datetime.fromisoformat(
                details["last_updated"].replace("Z", "+00:00")
            )
            
            if last_updated > cutoff_date:
                recent_updates.append({
                    "repo": repo,
                    "last_updated": last_updated.strftime("%Y-%m-%d"),
                    "stars": details["stars"]
                })
    
    return sorted(recent_updates, key=lambda x: x["last_updated"], reverse=True)

# Usage
repos_to_monitor = [
    "swisskyrepo/PayloadsAllTheThings",
    "danielmiessler/SecLists",
    "Hack-with-Github/Awesome-Hacking"
]

recent = check_repository_updates(repos_to_monitor, days_threshold=30)
print(f"Recently updated repositories: {len(recent)}")
```

## Rate Limiting

### Understanding GitHub Limits

| Authentication | Rate Limit | Reset Window |
|---------------|-----------|--------------|
| Unauthenticated | 60 requests/hour | 60 minutes |
| Personal Token | 5,000 requests/hour | 60 minutes |
| GitHub App | 5,000 requests/hour | 60 minutes |

### Rate Limit Checking

```python
import requests
import time

def check_rate_limit() -> dict:
    """Check current GitHub API rate limit status."""
    headers = {}
    
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    response = requests.get("https://api.github.com/rate_limit", headers=headers)
    data = response.json()
    
    core_rate = data["rate"]
    
    return {
        "limit": core_rate["limit"],
        "remaining": core_rate["remaining"],
        "reset": datetime.fromtimestamp(core_rate["reset"]),
        "used": core_rate["limit"] - core_rate["remaining"]
    }

# Usage
limits = check_rate_limit()
print(f"Rate limit: {limits['remaining']}/{limits['limit']}")
print(f"Resets at: {limits['reset']}")
```

### Rate-Aware Request Wrapper

```python
from functools import wraps
import time

def rate_limited_github_request(func):
    """Decorator to handle GitHub rate limiting."""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check rate limit before request
        limits = check_rate_limit()
        
        if limits["remaining"] < 10:
            # Approaching limit
            reset_time = limits["reset"]
            wait_seconds = (reset_time - datetime.now()).total_seconds()
            
            if wait_seconds > 0:
                logger.warning(f"Approaching rate limit. Waiting {wait_seconds}s")
                time.sleep(wait_seconds + 1)
        
        # Make request
        try:
            return func(*args, **kwargs)
        
        except requests.HTTPError as e:
            if e.response.status_code == 403:
                # Check if it's rate limit error
                if "rate limit" in e.response.text.lower():
                    logger.error("Rate limit exceeded")
                    raise RateLimitError("GitHub rate limit exceeded")
            raise
    
    return wrapper

class RateLimitError(Exception):
    """Raised when GitHub rate limit is exceeded."""
    pass

# Usage
@rate_limited_github_request
def fetch_repo_safe(repo: str) -> dict:
    manager = SecurityResourceManager()
    return manager.get_repo_details(repo)
```

## Error Handling

### Common Error Scenarios

```python
from requests.exceptions import HTTPError, Timeout, ConnectionError

def safe_repo_fetch(repo: str) -> dict | None:
    """Fetch repository with comprehensive error handling."""
    manager = SecurityResourceManager()
    
    try:
        return manager.get_repo_details(repo)
    
    except HTTPError as e:
        if e.response.status_code == 404:
            logger.warning(f"Repository not found: {repo}")
        elif e.response.status_code == 403:
            logger.error(f"Access forbidden (rate limit?): {repo}")
        elif e.response.status_code == 401:
            logger.error(f"Authentication failed: Check GITHUB_TOKEN")
        else:
            logger.error(f"HTTP error {e.response.status_code}: {repo}")
        return None
    
    except Timeout:
        logger.warning(f"Request timeout for {repo}")
        return None
    
    except ConnectionError:
        logger.error(f"Network connection failed")
        return None
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None
```

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def fetch_repo_with_retry(repo: str) -> dict:
    """Fetch repository with automatic retry on transient failures."""
    manager = SecurityResourceManager()
    result = manager.get_repo_details(repo)
    
    if result is None:
        raise ValueError(f"Failed to fetch {repo}")
    
    return result

# Usage
try:
    repo_info = fetch_repo_with_retry("swisskyrepo/PayloadsAllTheThings")
except Exception as e:
    logger.error(f"Failed after retries: {e}")
```

## Testing

### Mock GitHub API Responses

```python
import pytest
from unittest.mock import patch, MagicMock
from app.core.security_resources import SecurityResourceManager

class TestGitHubIntegration:
    
    @patch('requests.get')
    def test_get_repo_details_success(self, mock_get):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "PayloadsAllTheThings",
            "description": "A list of useful payloads",
            "stargazers_count": 50000,
            "forks_count": 10000,
            "updated_at": "2024-01-15T10:00:00Z",
            "html_url": "https://github.com/swisskyrepo/PayloadsAllTheThings",
            "language": "Python",
            "topics": ["security", "penetration-testing"]
        }
        mock_get.return_value = mock_response
        
        # Test
        manager = SecurityResourceManager()
        details = manager.get_repo_details("swisskyrepo/PayloadsAllTheThings")
        
        assert details["name"] == "PayloadsAllTheThings"
        assert details["stars"] == 50000
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_repo_details_404(self, mock_get):
        # Mock 404 response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        manager = SecurityResourceManager()
        details = manager.get_repo_details("nonexistent/repo")
        
        assert details is None
    
    def test_get_resources_by_category(self):
        manager = SecurityResourceManager()
        
        ctf_resources = manager.get_resources_by_category("CTF")
        assert len(ctf_resources) > 0
        
        for resource in ctf_resources:
            assert resource["category"] == "CTF"
```

## Advanced Features

### GitHub GraphQL API Integration

```python
import requests

class GitHubGraphQLClient:
    """Client for GitHub GraphQL API (more efficient than REST)."""
    
    def __init__(self):
        self.url = "https://api.github.com/graphql"
        self.token = os.getenv("GITHUB_TOKEN")
        
        if not self.token:
            raise ValueError("GITHUB_TOKEN required for GraphQL API")
    
    def query(self, query_string: str, variables: dict = None) -> dict:
        """Execute GraphQL query."""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query_string,
            "variables": variables or {}
        }
        
        response = requests.post(
            self.url,
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        return response.json()
    
    def get_repository_info(self, owner: str, name: str) -> dict:
        """Fetch repository info using GraphQL."""
        query = """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            name
            description
            stargazerCount
            forkCount
            updatedAt
            url
            primaryLanguage {
              name
            }
            repositoryTopics(first: 10) {
              nodes {
                topic {
                  name
                }
              }
            }
          }
        }
        """
        
        variables = {"owner": owner, "name": name}
        result = self.query(query, variables)
        
        return result["data"]["repository"]

# Usage
client = GitHubGraphQLClient()
repo_info = client.get_repository_info("swisskyrepo", "PayloadsAllTheThings")
print(f"Stars: {repo_info['stargazerCount']}")
```

## Monitoring and Analytics

### Resource Popularity Tracking

```python
import json
from datetime import datetime

class ResourceAnalytics:
    """Track and analyze security resource metrics."""
    
    def __init__(self, cache_file: str = "data/github_analytics.json"):
        self.cache_file = cache_file
        self.manager = SecurityResourceManager()
    
    def update_metrics(self):
        """Fetch and cache current metrics for all resources."""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "repositories": {}
        }
        
        # Collect all repository names
        all_repos = []
        for category_resources in self.manager.resources.values():
            all_repos.extend([r["repo"] for r in category_resources])
        
        # Fetch details
        for repo in all_repos:
            details = self.manager.get_repo_details(repo)
            if details:
                metrics["repositories"][repo] = {
                    "stars": details["stars"],
                    "forks": details["forks"],
                    "last_updated": details["last_updated"]
                }
        
        # Save to cache
        with open(self.cache_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return metrics
    
    def get_trending(self, timeframe_days: int = 7) -> list[dict]:
        """Identify trending repositories based on star growth."""
        # Load historical data and compare
        pass

# Usage
analytics = ResourceAnalytics()
metrics = analytics.update_metrics()
print(f"Tracked {len(metrics['repositories'])} repositories")
```

## References

- **GitHub REST API**: https://docs.github.com/en/rest
- **GraphQL API**: https://docs.github.com/en/graphql
- **Rate Limiting**: https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting
- **Personal Access Tokens**: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

## Related Documentation

- [Security Resources](../architecture/security-systems.md)
- [Data Analysis](./data-persistence.md)
- [External APIs](./external-apis-overview.md)
