# Query Optimization System Relationships

**System ID:** PERF-006  
**Category:** Data Access Performance  
**Layer:** Data/Persistence  
**Status:** Production

## Overview

Query Optimization focuses on improving database query performance through indexing, query rewriting, execution plan optimization, and data access pattern refinement to minimize latency and resource consumption.

---

## Upstream Dependencies

### Database Systems
- **RDBMS Engines** → Query Execution
  - PostgreSQL, MySQL, SQLite
  - Query parsers and optimizers
  - Index management
  - Statistics collection

### Application Data Access
- **ORM Layers** → Query Generation
  - SQLAlchemy, Django ORM
  - Query builder patterns
  - N+1 query problems
  
### Data Models
- **Schema Design** → Query Patterns
  - Table relationships
  - Normalization vs denormalization
  - Data distribution

---

## Downstream Impacts

### Performance Systems
- **Caching** ← Query Results
  - Cache frequently executed queries
  - Invalidation on data changes
  
- **Connection Pooling** ← Connection Usage
  - Efficient connection reuse
  - Reduced connection overhead
  
- **Load Balancing** ← Read/Write Split
  - Route reads to replicas
  - Route writes to master
  
- **Profiling** ← Slow Query Log
  - Query performance metrics
  - Optimization candidates

---

## Query Optimization Techniques

### 1. Index Optimization

#### Index Selection Strategy
```python
class IndexAnalyzer:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def analyze_query(self, query):
        """Analyze query and recommend indexes"""
        # Get query execution plan
        explain_result = self.db.execute(f"EXPLAIN ANALYZE {query}")
        
        recommendations = []
        
        # Check for sequential scans
        if 'Seq Scan' in str(explain_result):
            # Extract table and filter columns
            table = self.extract_table(query)
            columns = self.extract_where_columns(query)
            
            recommendations.append({
                'type': 'missing_index',
                'table': table,
                'columns': columns,
                'sql': f"CREATE INDEX idx_{table}_{'_'.join(columns)} ON {table}({', '.join(columns)});"
            })
        
        # Check for index usage
        if 'Index Scan' in str(explain_result):
            # Good - using index
            pass
        
        return recommendations
```

#### Common Index Types
```sql
-- B-Tree Index (default, good for equality and range queries)
CREATE INDEX idx_users_email ON users(email);

-- Partial Index (index subset of rows)
CREATE INDEX idx_active_users ON users(email) WHERE active = true;

-- Composite Index (multiple columns, order matters!)
CREATE INDEX idx_users_city_age ON users(city, age);
-- Good: WHERE city = 'NYC' AND age > 30
-- Good: WHERE city = 'NYC'
-- Bad:  WHERE age > 30 (doesn't use index efficiently)

-- Covering Index (include additional columns to avoid table lookup)
CREATE INDEX idx_users_email_name ON users(email) INCLUDE (name, created_at);

-- Unique Index (enforce uniqueness + fast lookup)
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- Full-Text Search Index
CREATE INDEX idx_posts_content_fts ON posts USING gin(to_tsvector('english', content));

-- Hash Index (equality only, not range)
CREATE INDEX idx_users_hash ON users USING hash(user_id);
```

**Index Selection Guidelines:**
| Query Pattern | Best Index Type |
|---------------|-----------------|
| `WHERE id = ?` | B-Tree or Hash |
| `WHERE age > ? AND age < ?` | B-Tree |
| `WHERE city = ? AND age > ?` | Composite B-Tree (city, age) |
| `WHERE active = true` (low cardinality) | Partial index or no index |
| `WHERE email = ?` (unique) | Unique B-Tree |
| `WHERE content LIKE '%keyword%'` | Full-text search (GIN/GIST) |

**Relationships:**
- → Caching (index reduces need for caching)
- ← Profiling (slow query log identifies missing indexes)
- → Resource Management (indexes consume disk space)

### 2. Query Rewriting Optimization

#### N+1 Query Elimination
```python
# BEFORE: N+1 Query Problem (1 + 1000 queries)
def get_users_with_posts_bad():
    users = db.query("SELECT * FROM users LIMIT 1000")
    
    for user in users:
        # Executes 1000 separate queries!
        posts = db.query("SELECT * FROM posts WHERE user_id = ?", user.id)
        user.posts = posts
    
    return users

# AFTER: Join or Batch Loading (2 queries)
def get_users_with_posts_good():
    # Option 1: JOIN query
    result = db.query("""
        SELECT u.*, p.id as post_id, p.title, p.content
        FROM users u
        LEFT JOIN posts p ON u.id = p.user_id
        LIMIT 1000
    """)
    
    # Option 2: Batch loading
    users = db.query("SELECT * FROM users LIMIT 1000")
    user_ids = [u.id for u in users]
    posts = db.query("SELECT * FROM posts WHERE user_id IN (?)", user_ids)
    
    # Group posts by user_id
    posts_by_user = {}
    for post in posts:
        posts_by_user.setdefault(post.user_id, []).append(post)
    
    for user in users:
        user.posts = posts_by_user.get(user.id, [])
    
    return users

# Performance: 1001 queries → 1-2 queries (500x faster)
```

**Relationships:**
- → Connection Pooling (reduces connection churn)
- → Profiling (identify N+1 problems)
- → Optimization (algorithmic improvement)

#### Subquery to JOIN Conversion
```sql
-- BEFORE: Subquery (slower, executed for each row)
SELECT u.*
FROM users u
WHERE u.id IN (
    SELECT DISTINCT user_id 
    FROM posts 
    WHERE created_at > '2024-01-01'
);

-- AFTER: JOIN (faster, optimized by query planner)
SELECT DISTINCT u.*
FROM users u
INNER JOIN posts p ON u.id = p.user_id
WHERE p.created_at > '2024-01-01';

-- AFTER: EXISTS (faster for large datasets)
SELECT u.*
FROM users u
WHERE EXISTS (
    SELECT 1 
    FROM posts p 
    WHERE p.user_id = u.id AND p.created_at > '2024-01-01'
);
```

**Performance Impact:** 10-100x faster depending on dataset size

#### Avoid SELECT *
```sql
-- BEFORE: Fetches all columns (slow, wastes bandwidth)
SELECT * FROM users WHERE email = 'user@example.com';

-- AFTER: Fetch only needed columns
SELECT id, name, email FROM users WHERE email = 'user@example.com';

-- Even better: Use covering index
CREATE INDEX idx_users_email_covering ON users(email) INCLUDE (id, name);
-- Now query uses index only, no table lookup!
```

**Relationships:**
- → Network bandwidth (less data transferred)
- → Resource Management (less memory per row)

### 3. Pagination Optimization

#### Offset-Based Pagination (Inefficient for Large Offsets)
```sql
-- BEFORE: Slow for large offsets (scans and discards first 100000 rows)
SELECT * FROM posts
ORDER BY created_at DESC
LIMIT 20 OFFSET 100000;  -- Scans 100,020 rows, returns 20

-- AFTER: Cursor-based pagination (efficient)
SELECT * FROM posts
WHERE created_at < '2024-01-15 10:30:00'  -- Last seen timestamp
ORDER BY created_at DESC
LIMIT 20;
-- Only scans 20 rows
```

**Python Implementation:**
```python
class CursorPaginator:
    def __init__(self, db):
        self.db = db
    
    def get_page(self, cursor=None, page_size=20):
        """Efficient cursor-based pagination"""
        if cursor:
            query = """
                SELECT id, title, created_at
                FROM posts
                WHERE created_at < ?
                ORDER BY created_at DESC
                LIMIT ?
            """
            results = self.db.query(query, cursor, page_size)
        else:
            # First page
            query = """
                SELECT id, title, created_at
                FROM posts
                ORDER BY created_at DESC
                LIMIT ?
            """
            results = self.db.query(query, page_size)
        
        # Next cursor is the timestamp of last item
        next_cursor = results[-1].created_at if results else None
        
        return {
            'results': results,
            'next_cursor': next_cursor,
            'has_more': len(results) == page_size
        }

# Usage
paginator = CursorPaginator(db)
page1 = paginator.get_page()  # First 20 items
page2 = paginator.get_page(cursor=page1['next_cursor'])  # Next 20
```

**Relationships:**
- → Lazy Loading (deferred loading pattern)
- → Optimization (algorithmic improvement O(n) → O(1))

### 4. Aggregation Optimization

#### Pre-Aggregation (Materialized Views)
```sql
-- BEFORE: Calculate aggregates on every query (slow)
SELECT 
    user_id,
    COUNT(*) as post_count,
    AVG(view_count) as avg_views
FROM posts
GROUP BY user_id;

-- AFTER: Materialized view (pre-calculated, fast)
CREATE MATERIALIZED VIEW user_post_stats AS
SELECT 
    user_id,
    COUNT(*) as post_count,
    AVG(view_count) as avg_views,
    MAX(created_at) as last_post_at
FROM posts
GROUP BY user_id;

-- Refresh periodically
REFRESH MATERIALIZED VIEW user_post_stats;

-- Query is now instant
SELECT * FROM user_post_stats WHERE user_id = 123;
```

**Relationships:**
- → Caching (database-level caching)
- → Resource Management (trade storage for speed)

#### Partial Aggregation
```python
class PartialAggregator:
    """Incrementally update aggregates instead of recalculating"""
    def __init__(self, db):
        self.db = db
        # Table: user_stats (user_id, post_count, total_views, avg_views)
    
    def add_post(self, user_id, view_count):
        """Update aggregates when new post added"""
        self.db.execute("""
            INSERT INTO user_stats (user_id, post_count, total_views, avg_views)
            VALUES (?, 1, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                post_count = user_stats.post_count + 1,
                total_views = user_stats.total_views + ?,
                avg_views = (user_stats.total_views + ?) / (user_stats.post_count + 1)
        """, user_id, view_count, view_count, view_count, view_count)
    
    def get_stats(self, user_id):
        """Instant lookup, no aggregation needed"""
        return self.db.query(
            "SELECT * FROM user_stats WHERE user_id = ?",
            user_id
        )

# Performance: O(1) instead of O(n) for each lookup
```

**Relationships:**
- → Optimization (incremental computation)
- → Caching (pre-computed results)

### 5. Batch Operations Optimization

#### Bulk Insert Optimization
```python
# BEFORE: Individual inserts (1000 queries, slow)
for user in users:
    db.execute("INSERT INTO users (name, email) VALUES (?, ?)", user.name, user.email)

# AFTER: Batch insert (1 query, 100x faster)
db.executemany(
    "INSERT INTO users (name, email) VALUES (?, ?)",
    [(u.name, u.email) for u in users]
)

# EVEN BETTER: Multi-row insert (PostgreSQL)
values = ', '.join([f"('{u.name}', '{u.email}')" for u in users])
db.execute(f"INSERT INTO users (name, email) VALUES {values}")

# BEST: Use database-specific bulk loading (e.g., PostgreSQL COPY)
import io
import csv

csv_buffer = io.StringIO()
writer = csv.writer(csv_buffer)
writer.writerows([(u.name, u.email) for u in users])
csv_buffer.seek(0)

cursor.copy_from(csv_buffer, 'users', columns=('name', 'email'), sep=',')
# 10,000x faster than individual inserts for large datasets
```

**Relationships:**
- → Optimization (batch processing pattern)
- → Resource Management (reduced overhead)
- → Connection Pooling (fewer round-trips)

---

## Database-Specific Optimizations

### PostgreSQL Optimizations

#### Analyze and Vacuum
```python
class PostgreSQLOptimizer:
    def __init__(self, db):
        self.db = db
    
    def update_statistics(self, table_name):
        """Update query planner statistics"""
        self.db.execute(f"ANALYZE {table_name};")
        print(f"Statistics updated for {table_name}")
    
    def vacuum_table(self, table_name, full=False):
        """Reclaim storage and update stats"""
        if full:
            self.db.execute(f"VACUUM FULL ANALYZE {table_name};")
        else:
            self.db.execute(f"VACUUM ANALYZE {table_name};")
    
    def get_table_bloat(self, table_name):
        """Check for table bloat"""
        result = self.db.query(f"""
            SELECT 
                pg_size_pretty(pg_total_relation_size('{table_name}')) as total_size,
                pg_size_pretty(pg_relation_size('{table_name}')) as table_size,
                pg_size_pretty(pg_total_relation_size('{table_name}') - pg_relation_size('{table_name}')) as index_size
        """)
        return result
```

#### Partial Indexes
```sql
-- Index only active users (smaller, faster)
CREATE INDEX idx_active_users ON users(email) WHERE active = true;

-- Index only recent posts
CREATE INDEX idx_recent_posts ON posts(created_at) 
WHERE created_at > CURRENT_DATE - INTERVAL '30 days';
```

### MySQL Optimizations

#### Query Cache (MySQL 5.7 and earlier)
```sql
-- Enable query cache
SET GLOBAL query_cache_size = 268435456;  -- 256MB
SET GLOBAL query_cache_type = 1;

-- Check cache stats
SHOW STATUS LIKE 'Qcache%';
```

#### Covering Indexes
```sql
-- Include all columns needed by query in index
ALTER TABLE users ADD INDEX idx_users_email_covering (email, name, created_at);

-- Query uses index only, no table lookup
SELECT name, created_at FROM users WHERE email = 'user@example.com';
```

---

## Query Profiling & Analysis

### Execution Plan Analysis
```python
class QueryProfiler:
    def __init__(self, db):
        self.db = db
        self.slow_query_threshold = 0.1  # 100ms
        
    def profile_query(self, query, params=None):
        """Profile query execution"""
        # Get execution plan
        explain = self.db.query(f"EXPLAIN ANALYZE {query}", params)
        
        # Execute and time query
        start = time.perf_counter()
        result = self.db.query(query, params)
        elapsed = time.perf_counter() - start
        
        analysis = {
            'query': query,
            'execution_time': elapsed,
            'row_count': len(result),
            'execution_plan': explain,
            'is_slow': elapsed > self.slow_query_threshold,
        }
        
        # Identify issues
        issues = []
        explain_str = str(explain)
        
        if 'Seq Scan' in explain_str:
            issues.append("Sequential scan detected - missing index?")
        
        if 'Nested Loop' in explain_str and 'Seq Scan' in explain_str:
            issues.append("Nested loop with seq scan - add index on join column")
        
        if elapsed > 1.0:
            issues.append("Query takes > 1 second - consider optimization")
        
        analysis['issues'] = issues
        
        return analysis
    
    def recommend_indexes(self, query):
        """Analyze query and suggest indexes"""
        # Parse WHERE clauses
        where_columns = self.extract_where_columns(query)
        join_columns = self.extract_join_columns(query)
        order_columns = self.extract_order_columns(query)
        
        recommendations = []
        
        if where_columns:
            recommendations.append(f"Consider index on WHERE columns: {where_columns}")
        
        if join_columns:
            recommendations.append(f"Consider index on JOIN columns: {join_columns}")
        
        if order_columns:
            recommendations.append(f"Consider index on ORDER BY columns: {order_columns}")
        
        return recommendations

# Usage
profiler = QueryProfiler(db)
analysis = profiler.profile_query("SELECT * FROM users WHERE email = ?", ('user@example.com',))

if analysis['is_slow']:
    print(f"⚠️ Slow query detected: {analysis['execution_time']*1000:.1f}ms")
    print("Issues:", analysis['issues'])
    print("Recommendations:", profiler.recommend_indexes(analysis['query']))
```

**Relationships:**
- ← Profiling (query performance data)
- → Optimization (optimization targets)

---

## Query Optimization Patterns

### 1. Read-Through Cache Pattern
```python
class QueryCache:
    def __init__(self, db, cache, ttl=3600):
        self.db = db
        self.cache = cache
        self.ttl = ttl
    
    def query_with_cache(self, query, params, cache_key):
        """Execute query with caching"""
        # Check cache
        cached = self.cache.get(cache_key)
        if cached:
            return cached
        
        # Execute query
        result = self.db.query(query, params)
        
        # Cache result
        self.cache.set(cache_key, result, ttl=self.ttl)
        
        return result
    
    def invalidate_cache(self, pattern):
        """Invalidate cache entries matching pattern"""
        self.cache.delete_pattern(pattern)

# Usage
cache = QueryCache(db, redis_cache)

# Read with caching
users = cache.query_with_cache(
    "SELECT * FROM users WHERE city = ?",
    ('NYC',),
    cache_key="users:city:NYC"
)

# Invalidate on write
db.execute("UPDATE users SET name = ? WHERE id = ?", ('New Name', 123))
cache.invalidate_cache("users:*")
```

**Relationships:**
- → Caching (query result caching)
- → Optimization (reduce database load)

### 2. Connection Pool Pattern
```python
class QueryExecutor:
    def __init__(self, connection_pool):
        self.pool = connection_pool
    
    def execute(self, query, params=None):
        """Execute query using pooled connection"""
        with self.pool.connection() as conn:
            return conn.execute(query, params)
    
    def execute_batch(self, queries):
        """Execute multiple queries in one connection"""
        with self.pool.connection() as conn:
            results = []
            for query, params in queries:
                results.append(conn.execute(query, params))
            return results

# Performance: Reuses connections instead of creating new ones
```

**Relationships:**
- → Connection Pooling (efficient connection use)
- → Resource Management (connection limits)

---

## Query Optimization Checklist

- [ ] Add indexes on WHERE clause columns
- [ ] Add indexes on JOIN columns
- [ ] Add indexes on foreign keys
- [ ] Use covering indexes where possible
- [ ] Avoid SELECT * - fetch only needed columns
- [ ] Eliminate N+1 queries with JOINs or batch loading
- [ ] Use cursor-based pagination instead of OFFSET
- [ ] Use prepared statements for repeated queries
- [ ] Batch INSERT/UPDATE operations
- [ ] Use EXPLAIN ANALYZE to verify index usage
- [ ] Configure database statistics updates (ANALYZE)
- [ ] Monitor slow query log
- [ ] Implement query result caching
- [ ] Use connection pooling
- [ ] Set appropriate query timeouts
- [ ] Monitor query execution plans
- [ ] Test with production-sized datasets

---

## Performance Impact

| Optimization | Before | After | Improvement |
|--------------|--------|-------|-------------|
| Add index on WHERE column | 5000ms | 50ms | 100x |
| N+1 query → JOIN | 10s (1001 queries) | 100ms (1 query) | 100x |
| SELECT * → specific columns | 200ms | 80ms | 2.5x |
| OFFSET → cursor pagination | 5000ms (page 1000) | 50ms | 100x |
| Individual → batch insert | 10s (1000 rows) | 100ms | 100x |
| Subquery → JOIN | 800ms | 80ms | 10x |
| Covering index | 150ms | 30ms | 5x |

---

## Related Documentation
- Caching: `caching-relationships.md`
- Connection Pooling: `connection-pooling-relationships.md`
- Profiling: `profiling-relationships.md`
- Optimization: `optimization-relationships.md`
