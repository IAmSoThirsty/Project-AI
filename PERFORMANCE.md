# Performance Improvement Suggestions

This document identifies slow or inefficient code patterns in the Project-AI codebase and provides suggestions for improvement.

## 1. Repeated File I/O Operations

### Issue
Multiple modules (`emergency_alert.py`, `learning_paths.py`, `location_tracker.py`, `security_resources.py`) perform read-then-write operations on JSON files without caching. Every file access requires disk I/O.

### Affected Files
- `src/app/core/emergency_alert.py`: `log_alert()`, `get_alert_history()`, `load_contacts()`, `save_contacts()`
- `src/app/core/learning_paths.py`: `save_path()`, `get_saved_paths()`
- `src/app/core/location_tracker.py`: `save_location_history()`, `get_location_history()`
- `src/app/core/security_resources.py`: `save_favorite()`, `get_favorites()`

### Example (security_resources.py:92-107)
```python
def save_favorite(self, username, repo):
    filename = f"security_favorites_{username}.json"
    favorites = {}
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            favorites = json.load(f)  # Read entire file

    if repo not in favorites:
        favorites[repo] = {
            'added_date': datetime.now().isoformat(),
            'details': self.get_repo_details(repo)  # Makes HTTP request here!
        }

    with open(filename, 'w') as f:
        json.dump(favorites, f)  # Write entire file
```

### Suggestions
1. **Add in-memory caching**: Maintain a dict cache of loaded data to avoid repeated file reads.
2. **Batch writes**: Accumulate changes and write periodically rather than on every operation.
3. **Use `lru_cache`**: For read-heavy operations like `get_favorites()`.

---

## 2. Blocking Network Calls in UI Code

### Issue
The `get_repo_details()` method in `security_resources.py` makes synchronous HTTP requests. When called from the GUI (e.g., `save_favorite()`), this blocks the UI thread.

### Affected Files
- `src/app/core/security_resources.py`: `get_repo_details()` method
- `src/app/core/location_tracker.py`: `get_location_from_ip()` method

### Example (before fix)
```python
def get_repo_details(self, repo):
    try:
        url = f"https://api.github.com/repos/{repo}"
        response = requests.get(url)  # Blocks until response received
        if response.status_code == 200:
            data = response.json()
            return {...}
    except Exception as e:
        ...
```

### Suggestions
1. **Use async/await**: Refactor to use `aiohttp` or `httpx` with async patterns.
2. **Use QThread or ThreadPoolExecutor**: Move network operations off the main thread.
3. ✅ **Add timeout parameters**: Prevent indefinite hangs on slow networks. (IMPLEMENTED)

```python
# Improved version with timeout (implemented)
response = requests.get(url, timeout=10)  # 10-second timeout
```

---

## 3. ✅ Inefficient List/Set Operations (FIXED)

### Issue
The `get_all_categories()` method in `security_resources.py` used unnecessary conversions.

### Affected Files
- `src/app/core/security_resources.py`: `get_all_categories()` method

### Resolution
Changed from:
```python
return sorted(list(categories))  # sorted() already returns a list
```
To:
```python
return sorted(categories)  # sorted() accepts any iterable
```

---

## 4. Dashboard Initialization Overhead

### Issue
`DashboardWindow.__init__()` instantiates all core components eagerly, even if they won't be used in the session.

### Affected Files
- `src/app/gui/dashboard.py`: `__init__()` (lines 31-40)

### Example
```python
def __init__(self, username: str = None, initial_tab: int = 0):
    super().__init__()
    # All these are created even if user only uses Chat tab
    self.user_manager = UserManager()
    self.intent_detector = IntentDetector()
    self.learning_manager = LearningPathManager()
    self.data_analyzer = DataAnalyzer()
    self.security_manager = SecurityResourceManager()
    self.location_tracker = LocationTracker()
    self.emergency_alert = EmergencyAlert()
```

### Suggestions
1. **Lazy initialization**: Create components on first access using properties.
2. **Dependency injection**: Pass only required components based on initial_tab.

```python
@property
def learning_manager(self):
    if self._learning_manager is None:
        self._learning_manager = LearningPathManager()
    return self._learning_manager
```

---

## 5. Location History Decryption Loop

### Issue
`get_location_history()` decrypts all entries every time it's called, even if no new entries exist.

### Affected Files
- `src/app/core/location_tracker.py`: `get_location_history()` (lines 106-121)

### Example
```python
def get_location_history(self, username):
    filename = f"location_history_{username}.json"
    if not os.path.exists(filename):
        return []

    with open(filename, 'r') as f:
        history = json.load(f)

    decrypted_history = []
    for encrypted_location in history:  # O(n) decryption every call
        location_data = self.decrypt_location(encrypted_location.encode())
        if location_data:
            decrypted_history.append(location_data)

    return decrypted_history
```

### Suggestions
1. **Cache decrypted results**: Store decrypted data in memory after first load.
2. **Incremental decryption**: Only decrypt new entries since last call.
3. **Paginate results**: Return only recent N entries instead of full history.

---

## 6. ✅ Missing Request Timeouts (FIXED)

### Issue
HTTP requests didn't specify timeouts, risking indefinite blocking.

### Affected Files
- `src/app/core/location_tracker.py`: `get_location_from_ip()` method
- `src/app/core/security_resources.py`: `get_repo_details()` method

### Resolution
Added 10-second timeout to all `requests.get()` calls:
```python
response = requests.get(url, timeout=10)  # 10-second timeout
```

---

## 7. UserManager Password Migration on Every Load

### Issue
`UserManager.__init__()` iterates through all users checking for plaintext passwords on every instantiation.

### Affected Files
- `src/app/core/user_manager.py`: `__init__()` (lines 56-79)

### Suggestions
1. **Add migration flag**: Store a version/migrated flag in the JSON to skip checking if already migrated.
2. **Use a migration tool**: Move migration logic to a one-time CLI tool (already exists: `tools/migrate_users.py`).

---

## 8. Redundant Object Creation

### Issue
Multiple widgets create separate `UserManager` instances instead of sharing one.

### Affected Files
- `src/app/gui/dashboard.py`: Creates `UserManager` (line 34)
- `src/app/gui/login.py`: Creates `UserManager` (line 27)
- `src/app/gui/user_management.py`: Creates `UserManager` (line 31)

### Suggestions
1. **Singleton pattern**: Use a module-level instance or singleton.
2. **Pass by reference**: Inject the same instance across widgets.

---

## 9. DataAnalyzer Repeated Computation

### Issue
`get_summary_stats()` computes all statistics every call without caching.

### Affected Files
- `src/app/core/data_analysis.py`: `get_summary_stats()` (lines 47-58)

### Suggestions
1. **Memoize results**: Cache stats and invalidate only when data changes.
2. **Lazy computation**: Only compute requested statistics.

---

## 10. Inefficient String Parsing

### Issue
`open_security_resource()` and `add_security_favorite()` use string parsing with `find()` instead of storing structured data.

### Affected Files
- `src/app/gui/dashboard_handlers.py`: lines 52-57, 62-64

### Example
```python
def open_security_resource(self, item):
    text = item.text()
    repo = text[text.find("(")+1:text.find(")")]  # Fragile parsing
```

### Suggestions
1. **Use QListWidgetItem.setData()**: Store the repo as item data.
2. **Use a model/view pattern**: Separate data from display.

---

## Summary Priority

| Priority | Issue | Impact | Effort | Status |
|----------|-------|--------|--------|--------|
| High | Missing request timeouts | Can hang application | Low | ✅ Fixed |
| High | Blocking network calls | Freezes UI | Medium | Open |
| Medium | Repeated file I/O | Disk overhead | Medium | Open |
| Medium | Multiple UserManager instances | Memory waste | Low | Open |
| Medium | Location decryption loop | CPU overhead | Medium | Open |
| Low | Sorted list conversion | Minor overhead | Trivial | ✅ Fixed |
| Low | Eager dashboard init | Startup delay | Medium | Open |
| Low | String parsing | Fragile code | Low | Open |

## Quick Wins (Minimal Changes)

1. ✅ **Add timeouts to requests** - DONE
2. ✅ **Fix sorted(list(x))** - DONE
3. **Share UserManager instance** - Refactor injection pattern (remaining)
