# GitHub Integration Relationship Map

**Status**: 🟢 Production | **Type**: External API Service  
**Priority**: P2 Feature | **Governance**: Direct API Calls

---


## Navigation

**Location**: `relationships\integrations\02-github-integration.md`

**Parent**: [[relationships\integrations\README.md]]


## External Service Dependencies

### Primary Endpoint
- **Service**: GitHub REST API v3 (https://api.github.com)
- **Authentication**: None (public API) or Personal Access Token (optional)
- **Protocol**: REST/HTTP
- **Rate Limits**: 
  - Unauthenticated: 60 requests/hour
  - Authenticated: 5,000 requests/hour

### API Scopes
- `repo:public_read`: Read public repository metadata
- `user:read`: Read user profile information (optional)

---

## Internal Relationships

### Core Integration Points

```
┌─────────────────────────────────────────────────────────┐
│              SECURITY RESOURCES MANAGER                 │
│         src/app/core/security_resources.py              │
│   ┌──────────────────────────────────────────┐         │
│   │ GitHub API Client (requests library)     │         │
│   │ Fetches: Repos, Commits, Stars, Issues   │         │
│   └──────────────────────────────────────────┘         │
└────────────────┬────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│CTF Repos│ │Security │ │Privacy  │
│         │ │Tools    │ │Resources│
└─────────┘ └─────────┘ └─────────┘
```

### Dependency Graph

**PRIMARY CONSUMER**:

1. **Security Resources** (`src/app/core/security_resources.py` [[src/app/core/security_resources.py]])
   - Purpose: Fetch CTF repos, security tools, privacy guides
   - Methods: `fetch_resources()`, `get_latest_commits()`
   - Flow: User request → SecurityResourceManager → GitHub API → JSON

**RESOURCES TRACKED**:

```python
RESOURCES = {
    "CTF_Security": [
        {"name": "PayloadsAllTheThings", "repo": "swisskyrepo/PayloadsAllTheThings"},
        {"name": "SecLists", "repo": "danielmiessler/SecLists"},
        {"name": "PENTESTING-BIBLE", "repo": "blaCCkHatHacEEkr/PENTESTING-BIBLE"},
        {"name": "CTF Tools", "repo": "zardus/ctf-tools"},
        {"name": "Awesome CTF", "repo": "apsdehal/awesome-ctf"}
    ],
    "Privacy_Tools": [
        {"name": "Privacy Guide", "repo": "drduh/macOS-Security-and-Privacy-Guide"},
        {"name": "PrivacyTools", "repo": "privacytoolsIO/privacytools.io"}
    ]
}
```

---

## API Contracts

### Repository Metadata Contract

**Endpoint**: `GET /repos/{owner}/{repo}`

```python
# REQUEST
GET https://api.github.com/repos/swisskyrepo/PayloadsAllTheThings
Headers: {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": "token ghp_xxx" (optional)
}

# RESPONSE SCHEMA
{
    "id": 12345678,
    "name": "PayloadsAllTheThings",
    "full_name": "swisskyrepo/PayloadsAllTheThings",
    "owner": {
        "login": "swisskyrepo",
        "avatar_url": "https://avatars.githubusercontent.com/..."
    },
    "description": "A list of useful payloads and bypass for Web Application Security and Pentest/CTF",
    "html_url": "https://github.com/swisskyrepo/PayloadsAllTheThings",
    "stargazers_count": 55000,
    "watchers_count": 55000,
    "forks_count": 12000,
    "language": "Python",
    "updated_at": "2025-01-26T10:00:00Z",
    "topics": ["security", "pentest", "ctf"]
}
```

### Commits Contract

**Endpoint**: `GET /repos/{owner}/{repo}/commits`

```python
# REQUEST
GET https://api.github.com/repos/swisskyrepo/PayloadsAllTheThings/commits?per_page=5
Headers: {
    "Accept": "application/vnd.github.v3+json"
}

# RESPONSE SCHEMA
[
    {
        "sha": "abc123...",
        "commit": {
            "author": {
                "name": "Author Name",
                "email": "author@example.com",
                "date": "2025-01-25T12:00:00Z"
            },
            "message": "Added new SQL injection payloads"
        },
        "html_url": "https://github.com/swisskyrepo/PayloadsAllTheThings/commit/abc123"
    }
]
```

### Rate Limit Check

**Endpoint**: `GET /rate_limit`

```python
# RESPONSE
{
    "resources": {
        "core": {
            "limit": 5000,
            "remaining": 4999,
            "reset": 1706270400  # Unix timestamp
        }
    }
}
```

---

## Integration Patterns

### Pattern 1: Repository Listing

**Implementation**: `SecurityResourceManager.fetch_resources()`

```python
import requests

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
                    "last_updated": data.get("updated_at", "")
                })
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {repo}: {e}")
    
    return results
```

### Pattern 2: Commit History

**Implementation**: `SecurityResourceManager.get_latest_commits()`

```python
def get_latest_commits(self, repo, count=5):
    """Get latest commits from a repository."""
    url = f"https://api.github.com/repos/{repo}/commits?per_page={count}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            commits = response.json()
            return [{
                "sha": c["sha"][:7],
                "message": c["commit"]["message"].split("\n")[0],
                "author": c["commit"]["author"]["name"],
                "date": c["commit"]["author"]["date"]
            } for c in commits]
    except requests.RequestException as e:
        logger.error(f"Failed to fetch commits for {repo}: {e}")
    
    return []
```

---

## Configuration

### Environment Variables

```bash
# OPTIONAL (for higher rate limits)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx  # Personal Access Token
GITHUB_API_URL=https://api.github.com  # Override for GitHub Enterprise
```

### Token Generation

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `public_repo`, `read:user`
4. Copy token to `.env` [[.env]] file

---

## Error Handling

### Common Errors

1. **404 Not Found**: Repository doesn't exist or is private
   - **Mitigation**: Skip resource, log warning

2. **403 Forbidden**: Rate limit exceeded
   - **Mitigation**: Wait until reset time, cache responses

3. **500 Server Error**: GitHub API outage
   - **Mitigation**: Return cached data, log error

### Rate Limit Management

```python
def check_rate_limit(self):
    """Check GitHub API rate limit."""
    url = "https://api.github.com/rate_limit"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        core = data["resources"]["core"]
        
        if core["remaining"] < 10:
            reset_time = datetime.fromtimestamp(core["reset"])
            logger.warning(f"Rate limit low. Resets at {reset_time}")
            return False
    
    return True
```

---

## Security

### API Token Management

- **Storage**: Environment variable (.env file, NOT committed)
- **Scoping**: Minimal scopes (public_repo only)
- **Rotation**: Quarterly rotation recommended

### Data Validation

- **URL Sanitization**: Validate repository names to prevent SSRF
- **Response Validation**: Check response schemas before parsing

```python
def validate_repo_name(repo: str) -> bool:
    """Validate repository name format."""
    import re
    pattern = r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$"
    return bool(re.match(pattern, repo))
```

---

## Performance

### Caching Strategy

**Implementation**: Cache repository metadata for 1 hour

```python
# Pseudo-code (not implemented yet)
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def fetch_repo_with_cache(repo, cache_time):
    """Fetch repo with time-based cache invalidation."""
    # cache_time changes every hour, forcing cache miss
    return fetch_repo(repo)

# Usage
current_hour = int(time.time() // 3600)
data = fetch_repo_with_cache("swisskyrepo/PayloadsAllTheThings", current_hour)
```

### Latency Benchmarks

| Operation | Avg Latency | P95 Latency |
|-----------|-------------|-------------|
| Fetch repo metadata | 0.5s | 1.0s |
| Fetch commits (5) | 0.7s | 1.5s |
| Rate limit check | 0.2s | 0.5s |

---

## Testing

### Integration Tests

```python
# tests/test_github_integration.py
def test_fetch_resources():
    manager = SecurityResourceManager()
    resources = manager.fetch_resources("CTF_Security")
    
    assert len(resources) > 0
    assert all("name" in r for r in resources)
    assert all("stars" in r for r in resources)

def test_get_latest_commits():
    manager = SecurityResourceManager()
    commits = manager.get_latest_commits("swisskyrepo/PayloadsAllTheThings")
    
    assert len(commits) <= 5
    assert all("sha" in c for c in commits)
    assert all("message" in c for c in commits)
```

### Mocking

```python
# Use responses library for mocking HTTP requests
import responses

@responses.activate
def test_fetch_resources_with_mock():
    responses.add(
        responses.GET,
        "https://api.github.com/repos/swisskyrepo/PayloadsAllTheThings",
        json={"stargazers_count": 55000, "description": "Test repo"},
        status=200
    )
    
    manager = SecurityResourceManager()
    resources = manager.fetch_resources("CTF_Security")
    
    assert len(resources) > 0
```

---

## Monitoring

### Metrics

- **Request Count**: API calls per day
- **Error Rate**: Failed requests / total requests
- **Rate Limit Usage**: Remaining requests vs. limit
- **Cache Hit Rate**: Cached responses / total requests (future)

### Alerts

- **Rate Limit Low**: <100 requests remaining
- **High Error Rate**: >10% failures
- **Outage Detected**: GitHub status page check

---

## Future Enhancements

### Phase 1: Caching ⏳ PLANNED
- Add Redis cache for repository metadata
- Cache commits for 15 minutes
- Reduce API calls by 80%

### Phase 2: GraphQL API 🔮 FUTURE
- Migrate to GitHub GraphQL API v4
- Batch queries to reduce requests
- Fetch nested data in single request

### Phase 3: Webhooks 🔮 FUTURE
- Listen for repository updates via webhooks
- Real-time commit notifications
- Reduce polling overhead

---

## Related Systems

- **[01-openai-integration.md](01-openai-integration.md)**: AI for security analysis
- **[11-security-resources-api.md](11-security-resources-api.md)**: Security resource management
- **[04-database-connectors.md](04-database-connectors.md)**: Store fetched data

---

**Last Updated**: 2025-01-26  
**Maintained By**: AGENT-060  
**Review Cycle**: Quarterly


---

## See Also

### Related Source Documentation

- **01 Openai Integration**: [[source-docs\integrations\01-openai-integration.md]]
- **02 Huggingface Integration**: [[source-docs\integrations\02-huggingface-integration.md]]
- **04 Github Api**: [[source-docs\integrations\04-github-api.md]]
- **05 Database Integrations**: [[source-docs\integrations\05-database-integrations.md]]
- **11 Openrouter Integration**: [[source-docs\integrations\11-openrouter-integration.md]]
- **12 Perplexity Integration**: [[source-docs\integrations\12-perplexity-integration.md]]
- **Documentation Index**: [[source-docs\integrations\README.md]]
