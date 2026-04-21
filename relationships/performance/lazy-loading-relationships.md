# Lazy Loading System Relationships

**System ID:** PERF-008  
**Category:** Performance Optimization  
**Layer:** Application/Data Access  
**Status:** Production

## Overview

Lazy Loading defers initialization of resources until they are actually needed, reducing initial load times, memory consumption, and unnecessary data fetching. It's a core pattern for optimizing application startup and runtime performance.

---

## Upstream Dependencies

### Application State
- **User Interaction** → Loading Triggers
  - Page navigation
  - Component visibility
  - User actions
  - Scroll position

### Data Sources
- **Database/API** → Deferred Data
  - Large datasets
  - Related entities
  - Expensive computations
  - File downloads

### System Resources
- **Memory Constraints** → Loading Decisions
  - Available RAM
  - Cache capacity
  - Network bandwidth

---

## Downstream Impacts

### Performance Systems
- **Caching** ← Lazy-Loaded Data
  - Cache loaded data for reuse
  - Prefetch predictions
  
- **Resource Management** ← Memory Efficiency
  - Deferred memory allocation
  - On-demand resource usage
  
- **Query Optimization** ← Deferred Queries
  - Avoid unnecessary queries
  - Batch related queries
  
- **Connection Pooling** ← Reduced Connections
  - Fewer simultaneous connections
  - Staggered connection usage

---

## Lazy Loading Patterns

### 1. Lazy Object Initialization
**Pattern:** Create objects only when first accessed

```python
class LazyObject:
    def __init__(self, initializer):
        """
        Args:
            initializer: Function that creates the actual object
        """
        self._initializer = initializer
        self._object = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Initialize object if not already done"""
        if not self._initialized:
            self._object = self._initializer()
            self._initialized = True
    
    def __getattr__(self, name):
        """Proxy attribute access to actual object"""
        self._ensure_initialized()
        return getattr(self._object, name)
    
    def __call__(self, *args, **kwargs):
        """Proxy function calls to actual object"""
        self._ensure_initialized()
        return self._object(*args, **kwargs)

# Usage
def expensive_database_connection():
    print("Creating expensive database connection...")
    time.sleep(2)  # Simulate expensive operation
    return DatabaseConnection()

# Connection not created until first use
db = LazyObject(expensive_database_connection)

# ... later in code ...
result = db.query("SELECT * FROM users")  # NOW connection is created
```

**Benefits:**
- Fast application startup
- Memory saved if object never used
- Resources allocated on-demand

**Relationships:**
- → Resource Management (deferred allocation)
- → Optimization (lazy evaluation pattern)

### 2. Lazy Property Loading
**Pattern:** Load property values on first access

```python
class LazyProperty:
    """Decorator for lazy-loaded properties"""
    def __init__(self, function):
        self.function = function
        self.name = function.__name__
    
    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        # Load value on first access
        value = self.function(instance)
        
        # Cache value on instance
        setattr(instance, self.name, value)
        
        return value

class User:
    def __init__(self, user_id):
        self.user_id = user_id
    
    @LazyProperty
    def posts(self):
        """Load posts only when accessed"""
        print(f"Loading posts for user {self.user_id}...")
        return db.query("SELECT * FROM posts WHERE user_id = ?", self.user_id)
    
    @LazyProperty
    def profile_image(self):
        """Load image only when accessed"""
        print(f"Loading profile image for user {self.user_id}...")
        return download_image(f"/images/user_{self.user_id}.jpg")

# Usage
user = User(123)  # No queries executed yet

# First access loads posts
posts = user.posts  # Prints "Loading posts..." and executes query

# Second access uses cached value
posts = user.posts  # No print, uses cached value

# profile_image never accessed = never loaded (saves bandwidth)
```

**Relationships:**
- → Caching (automatic result caching)
- → Query Optimization (avoid unnecessary queries)
- → Resource Management (deferred memory allocation)

### 3. Lazy Collection Loading (ORM Pattern)
**Pattern:** Load related objects on first access

```python
class LazyCollection:
    """Lazy-loading collection for ORM relationships"""
    def __init__(self, loader_function, parent_id):
        self.loader = loader_function
        self.parent_id = parent_id
        self._items = None
        self._loaded = False
    
    def _load(self):
        """Load items from database"""
        if not self._loaded:
            print(f"Loading collection for parent {self.parent_id}...")
            self._items = self.loader(self.parent_id)
            self._loaded = True
    
    def __iter__(self):
        self._load()
        return iter(self._items)
    
    def __len__(self):
        self._load()
        return len(self._items)
    
    def __getitem__(self, index):
        self._load()
        return self._items[index]
    
    def filter(self, predicate):
        """Allow filtering without loading all items"""
        self._load()
        return [item for item in self._items if predicate(item)]

class Author:
    def __init__(self, author_id, name):
        self.id = author_id
        self.name = name
        
        # Lazy-loaded collection
        self.books = LazyCollection(
            loader_function=lambda author_id: db.query(
                "SELECT * FROM books WHERE author_id = ?", author_id
            ),
            parent_id=self.id
        )

# Usage
author = Author(1, "Jane Doe")  # No books loaded yet

# Books loaded on first access
for book in author.books:  # Loads books here
    print(book.title)

# Already loaded, no additional query
book_count = len(author.books)
```

**Relationships:**
- → Query Optimization (N+1 query prevention)
- → Caching (collection caching)
- ← Profiling (detect lazy loading inefficiencies)

### 4. Lazy Module Import
**Pattern:** Import modules only when needed

```python
class LazyImporter:
    """Lazy module importer"""
    def __init__(self, module_name):
        self.module_name = module_name
        self._module = None
    
    def __getattr__(self, name):
        if self._module is None:
            print(f"Importing {self.module_name}...")
            self._module = __import__(self.module_name, fromlist=[name])
        return getattr(self._module, name)

# Usage in application
class ImageProcessor:
    def __init__(self):
        # Don't import PIL until needed
        self.PIL = LazyImporter('PIL')
    
    def process_image(self, image_path):
        # PIL imported only when this method called
        from self.PIL import Image
        img = Image.open(image_path)
        return img.resize((800, 600))

# Fast startup - PIL not imported until image processing needed
processor = ImageProcessor()

# ... later, if image processing needed ...
processed = processor.process_image('photo.jpg')  # NOW PIL is imported
```

**Benefits:**
- Faster application startup (100-500ms saved per heavy import)
- Reduced memory footprint
- Import only what's used

**Relationships:**
- → Optimization (startup time optimization)
- → Resource Management (deferred memory usage)

### 5. Lazy Data Loading (Pagination)
**Pattern:** Load data in chunks as needed

```python
class LazyDataLoader:
    def __init__(self, query, page_size=100):
        self.query = query
        self.page_size = page_size
        self.current_page = 0
        self.cache = {}
        self.total_count = None
    
    def _load_page(self, page_num):
        """Load specific page from database"""
        if page_num in self.cache:
            return self.cache[page_num]
        
        offset = page_num * self.page_size
        print(f"Loading page {page_num} (offset {offset})...")
        
        results = db.query(
            f"{self.query} LIMIT {self.page_size} OFFSET {offset}"
        )
        
        self.cache[page_num] = results
        return results
    
    def __iter__(self):
        """Iterate through all data, loading pages as needed"""
        page_num = 0
        while True:
            page_data = self._load_page(page_num)
            
            if not page_data:
                break
            
            for item in page_data:
                yield item
            
            page_num += 1
    
    def __getitem__(self, index):
        """Access item by index, loading page if needed"""
        page_num = index // self.page_size
        page_offset = index % self.page_size
        
        page_data = self._load_page(page_num)
        return page_data[page_offset]

# Usage
users = LazyDataLoader("SELECT * FROM users ORDER BY id", page_size=100)

# Only loads first 100 users
for i, user in enumerate(users):
    print(user.name)
    if i >= 99:  # Stop after first page
        break

# Load specific user (loads page 5 if not cached)
user_500 = users[500]  # Loads page 5 (users 500-599)
```

**Relationships:**
- → Query Optimization (pagination pattern)
- → Caching (page caching)
- → Resource Management (bounded memory usage)

---

## Lazy Loading Strategies

### Eager vs Lazy Loading Decision Matrix
| Scenario | Strategy | Reason |
|----------|----------|--------|
| Data always used | Eager | Avoid overhead of lazy loading |
| Data rarely used | Lazy | Save resources |
| Large dataset | Lazy + Pagination | Memory constraints |
| Critical path | Eager | Avoid latency on user action |
| Cheap to load | Eager | Overhead not worth it |
| Expensive to load | Lazy | Significant savings |
| Initial page load | Lazy | Fast initial render |
| User likely to need | Eager/Prefetch | Better UX |

### Hybrid: Eager + Lazy with Prefetching
```python
class SmartDataLoader:
    def __init__(self):
        self.cache = {}
        self.prefetch_queue = queue.Queue()
        
        # Background prefetch thread
        self.prefetcher = threading.Thread(
            target=self._prefetch_loop,
            daemon=True
        )
        self.prefetcher.start()
    
    def get_user_with_posts(self, user_id):
        """Load user eagerly, posts lazily with prefetch"""
        # Eager: Load user immediately (always needed)
        user = db.query("SELECT * FROM users WHERE id = ?", user_id)
        
        # Lazy: Posts loaded on access
        user.posts = LazyCollection(
            loader_function=lambda uid: self._load_posts(uid),
            parent_id=user_id
        )
        
        # Prefetch: Queue posts for background loading
        self.prefetch_queue.put(('posts', user_id))
        
        return user
    
    def _prefetch_loop(self):
        """Background thread prefetches data"""
        while True:
            data_type, entity_id = self.prefetch_queue.get()
            
            if data_type == 'posts':
                self._load_posts(entity_id)
            
            self.prefetch_queue.task_done()
    
    def _load_posts(self, user_id):
        cache_key = f"posts:{user_id}"
        
        if cache_key in self.cache:
            print(f"Posts for user {user_id} already prefetched!")
            return self.cache[cache_key]
        
        print(f"Loading posts for user {user_id}...")
        posts = db.query("SELECT * FROM posts WHERE user_id = ?", user_id)
        self.cache[cache_key] = posts
        
        return posts

# Usage
loader = SmartDataLoader()

user = loader.get_user_with_posts(123)  # Loads user, queues posts prefetch
print(user.name)  # User data available immediately

time.sleep(0.1)  # Prefetch may complete

# Access posts - likely already prefetched
for post in user.posts:  # May hit cache from prefetch
    print(post.title)
```

**Relationships:**
- → Caching (prefetch to cache)
- → Optimization (balance between eager and lazy)
- ← Profiling (access patterns drive prefetch strategy)

---

## Lazy Loading in UI Components

### Lazy Component Rendering
```python
class LazyUIComponent:
    def __init__(self, component_factory):
        self.factory = component_factory
        self.component = None
        self.visible = False
    
    def show(self):
        """Render component only when made visible"""
        if not self.component:
            print("Rendering component for first time...")
            self.component = self.factory()
        
        self.component.display()
        self.visible = True
    
    def hide(self):
        self.visible = False
        if self.component:
            self.component.hide()

# Usage - Tab interface
class TabPanel:
    def __init__(self):
        self.tabs = {
            'dashboard': LazyUIComponent(lambda: DashboardTab()),
            'reports': LazyUIComponent(lambda: ReportsTab()),  # Heavy component
            'settings': LazyUIComponent(lambda: SettingsTab()),
        }
        self.active_tab = None
    
    def switch_tab(self, tab_name):
        # Hide current tab
        if self.active_tab:
            self.tabs[self.active_tab].hide()
        
        # Show new tab (renders if first time)
        self.tabs[tab_name].show()
        self.active_tab = tab_name

panel = TabPanel()
panel.switch_tab('dashboard')  # Only dashboard rendered
# Reports tab not rendered until switched to
```

### Infinite Scroll / Virtual Scrolling
```python
class VirtualScrollList:
    """Render only visible items in large list"""
    def __init__(self, items, item_height=50, viewport_height=800):
        self.items = items
        self.item_height = item_height
        self.viewport_height = viewport_height
        self.scroll_position = 0
    
    def get_visible_items(self):
        """Calculate which items are visible"""
        start_index = self.scroll_position // self.item_height
        visible_count = (self.viewport_height // self.item_height) + 2  # +2 buffer
        end_index = min(start_index + visible_count, len(self.items))
        
        return {
            'items': self.items[start_index:end_index],
            'start_index': start_index,
            'end_index': end_index,
            'total_height': len(self.items) * self.item_height,
            'offset': start_index * self.item_height
        }
    
    def on_scroll(self, new_position):
        """Update scroll position and re-render"""
        self.scroll_position = new_position
        visible = self.get_visible_items()
        
        print(f"Rendering items {visible['start_index']}-{visible['end_index']} of {len(self.items)}")
        return visible

# Usage with 10,000 items - only render ~20 at a time
items = [f"Item {i}" for i in range(10000)]
scroll_list = VirtualScrollList(items)

visible = scroll_list.get_visible_items()  # Returns ~20 items
# Memory: 20 items rendered instead of 10,000 (500x reduction)
```

**Relationships:**
- → Resource Management (bounded memory usage)
- → Optimization (render performance)

---

## Lazy Loading with Caching

### Cache-Aware Lazy Loader
```python
class CachedLazyLoader:
    def __init__(self, cache, ttl=3600):
        self.cache = cache
        self.ttl = ttl
    
    def lazy_load(self, key, loader_function):
        """Load from cache if available, otherwise execute loader"""
        # Check cache first
        cached_value = self.cache.get(key)
        if cached_value is not None:
            print(f"Cache hit for {key}")
            return cached_value
        
        # Cache miss - execute loader
        print(f"Cache miss for {key}, loading...")
        value = loader_function()
        
        # Store in cache
        self.cache.set(key, value, ttl=self.ttl)
        
        return value

# Usage
cache = RedisCache()
loader = CachedLazyLoader(cache, ttl=3600)

def load_user_posts(user_id):
    return db.query("SELECT * FROM posts WHERE user_id = ?", user_id)

# First call: loads from DB and caches
posts = loader.lazy_load(f"user:123:posts", lambda: load_user_posts(123))

# Second call: loads from cache (fast)
posts = loader.lazy_load(f"user:123:posts", lambda: load_user_posts(123))
```

**Relationships:**
- → Caching (integrated caching)
- → Query Optimization (avoid repeated queries)

---

## Lazy Loading Pitfalls & Solutions

### 1. N+1 Query Problem
**Problem:** Lazy loading causes separate query per item

```python
# BAD: Lazy loading in loop (N+1 queries)
users = db.query("SELECT * FROM users LIMIT 100")

for user in users:
    # Lazy load posts - 100 separate queries!
    posts = user.posts  # Each access = 1 query
    print(f"{user.name}: {len(posts)} posts")

# GOOD: Eager load with JOIN or batch load
users_with_posts = db.query("""
    SELECT u.*, p.id as post_id, p.title
    FROM users u
    LEFT JOIN posts p ON u.id = p.user_id
    LIMIT 100
""")

# Or batch load
user_ids = [u.id for u in users]
all_posts = db.query("SELECT * FROM posts WHERE user_id IN (?)", user_ids)
posts_by_user = group_by(all_posts, 'user_id')

for user in users:
    posts = posts_by_user.get(user.id, [])
    print(f"{user.name}: {len(posts)} posts")
```

**Solution:** Detect access patterns and batch load
**Relationships:** → Query Optimization (N+1 prevention)

### 2. Lazy Loading in Serialization
**Problem:** JSON serialization triggers all lazy loads

```python
# BAD: Serialization triggers all lazy loads
import json

user = User(id=123)  # Has lazy-loaded posts, comments, etc.

# This triggers ALL lazy loads!
json_data = json.dumps(user.__dict__)

# GOOD: Explicitly control what's serialized
def serialize_user(user):
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        # Only include posts if already loaded
        'posts': user._posts if hasattr(user, '_posts') else None
    }

json_data = json.dumps(serialize_user(user))
```

### 3. Lazy Loading with Closed Connections
**Problem:** Lazy load fails if connection closed

```python
# BAD: Connection closed before lazy load
def get_user():
    with db.connection() as conn:
        user = conn.query("SELECT * FROM users WHERE id = 1")[0]
        user.posts = LazyCollection(...)  # Loader uses conn
        return user
    # Connection closed here!

user = get_user()
posts = user.posts  # ERROR: Connection closed!

# GOOD: Eager load within connection scope
def get_user():
    with db.connection() as conn:
        user = conn.query("SELECT * FROM users WHERE id = 1")[0]
        user.posts = conn.query("SELECT * FROM posts WHERE user_id = ?", user.id)
        return user

user = get_user()
posts = user.posts  # Works - data already loaded
```

**Relationships:** → Connection Pooling (connection lifecycle)

---

## Lazy Loading Metrics

### Lazy Loading Monitor
```python
class LazyLoadingMonitor:
    def __init__(self):
        self.loads = {}
        self.cache_hits = {}
        self.load_times = {}
    
    def record_load(self, key, was_cached, load_time):
        """Record lazy load event"""
        self.loads[key] = self.loads.get(key, 0) + 1
        
        if was_cached:
            self.cache_hits[key] = self.cache_hits.get(key, 0) + 1
        
        if key not in self.load_times:
            self.load_times[key] = []
        self.load_times[key].append(load_time)
    
    def get_stats(self):
        """Get lazy loading statistics"""
        stats = {}
        
        for key in self.loads:
            total_loads = self.loads[key]
            hits = self.cache_hits.get(key, 0)
            avg_time = sum(self.load_times[key]) / len(self.load_times[key])
            
            stats[key] = {
                'total_loads': total_loads,
                'cache_hits': hits,
                'cache_hit_rate': hits / total_loads if total_loads > 0 else 0,
                'avg_load_time': avg_time,
            }
        
        return stats
    
    def identify_hot_paths(self):
        """Identify frequently lazy-loaded data (candidates for eager loading)"""
        stats = self.get_stats()
        
        hot_paths = {
            key: data
            for key, data in stats.items()
            if data['total_loads'] > 10 and data['cache_hit_rate'] < 0.5
        }
        
        return hot_paths

# Usage
monitor = LazyLoadingMonitor()

def lazy_load_with_monitoring(key, loader):
    start = time.perf_counter()
    
    cached = cache.get(key)
    was_cached = cached is not None
    
    value = cached if was_cached else loader()
    
    elapsed = time.perf_counter() - start
    monitor.record_load(key, was_cached, elapsed)
    
    return value

# Analyze lazy loading patterns
hot_paths = monitor.identify_hot_paths()
print("Consider eager loading these:", hot_paths)
```

**Relationships:**
- ← Profiling (lazy loading metrics)
- → Optimization (identify optimization targets)

---

## Lazy Loading Checklist

- [ ] Identify expensive resources for lazy loading
- [ ] Implement lazy loading for rarely-used data
- [ ] Add caching to lazy-loaded data
- [ ] Monitor lazy loading patterns
- [ ] Watch for N+1 query problems
- [ ] Test with closed connections
- [ ] Implement prefetching for predictable access
- [ ] Use eager loading for always-needed data
- [ ] Avoid lazy loading in serialization
- [ ] Set appropriate cache TTLs
- [ ] Monitor cache hit rates
- [ ] Test lazy loading under load
- [ ] Document lazy loading decisions

---

## Performance Impact

| Scenario | Without Lazy Loading | With Lazy Loading | Improvement |
|----------|---------------------|-------------------|-------------|
| Application startup | 5 seconds (load all) | 0.5 seconds | 10x faster |
| Initial page render | 2 seconds (all data) | 200ms (minimal data) | 10x faster |
| Memory usage | 500MB (all data loaded) | 50MB (on-demand) | 10x reduction |
| Tab switch | Instant (pre-loaded) | 100ms (lazy load) | Slower but saves RAM |
| Rarely-used features | Always loaded (waste) | Never loaded (savings) | ∞ savings |

---

## Related Documentation
- Caching: `caching-relationships.md`
- Query Optimization: `query-optimization-relationships.md`
- Resource Management: `resource-management-relationships.md`
- Optimization: `optimization-relationships.md`
