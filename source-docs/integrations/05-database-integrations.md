# Database Integrations - ClickHouse & RisingWave

## Overview

Project-AI integrates with two specialized database systems for high-performance analytics and streaming data processing:

1. **ClickHouse** - Column-oriented OLAP database for billion-row analytics
2. **RisingWave** - Distributed SQL streaming database for real-time event processing

These integrations enable Project-AI to handle massive-scale data operations, real-time monitoring, and complex analytical workloads.

## ClickHouse Integration

### Architecture

```
Application Layer (Analytics, Metrics)
    ↓
ClickHouseClient (src/app/core/clickhouse_integration.py)
    ↓
ClickHouse Native Protocol (port 9000)
    ↓
ClickHouse Server
```

### Key Capabilities

- **Ingestion Rate**: 1 billion+ rows/second
- **Compression**: 10-30x data compression
- **Query Speed**: Sub-second queries on billions of rows
- **Scalability**: Horizontal scaling to 1000+ nodes

### Use Cases

1. **Metrics Storage**: Prometheus long-term storage backend
2. **Log Aggregation**: ELK alternative for log analytics
3. **Time-Series Data**: High-volume sensor data, financial ticks
4. **ML Feature Stores**: Fast feature extraction for model training
5. **Real-Time Dashboards**: Low-latency aggregations

### Configuration

```bash
# Environment variables
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000              # Native protocol port
CLICKHOUSE_DATABASE=default
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=               # Empty by default
CLICKHOUSE_COMPRESSION=true       # Enable LZ4 compression
```

### Implementation

```python
# src/app/core/clickhouse_integration.py

from clickhouse_driver import Client as ClickHouseDriver
import logging

logger = logging.getLogger(__name__)

class ClickHouseClient:
    """Client for ClickHouse OLAP database."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 9000,
        database: str = "default",
        user: str = "default",
        password: str = "",
        compression: bool = True,
    ):
        """Initialize ClickHouse client with native driver."""
        self.host = host
        self.port = port
        self.database = database
        
        # Native driver for best performance
        self.client = ClickHouseDriver(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            compression=compression,
        )
        
        logger.info(f"ClickHouse client initialized: {host}:{port}/{database}")
    
    def execute(self, query: str, params: dict = None) -> list[tuple]:
        """Execute SQL query and return results."""
        try:
            result = self.client.execute(query, params or {})
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def insert(self, table: str, data: list[dict]):
        """Bulk insert data into table."""
        if not data:
            return
        
        # Extract column names from first row
        columns = list(data[0].keys())
        values = [tuple(row[col] for col in columns) for row in data]
        
        # Build INSERT query
        query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES"
        
        try:
            self.client.execute(query, values)
            logger.info(f"Inserted {len(data)} rows into {table}")
        except Exception as e:
            logger.error(f"Bulk insert failed: {e}")
            raise
    
    def create_table(self, table: str, schema: dict[str, str], engine: str = "MergeTree"):
        """Create table with specified schema."""
        columns = ", ".join([f"{name} {dtype}" for name, dtype in schema.items()])
        
        # Primary key required for MergeTree engines
        primary_key = list(schema.keys())[0]
        
        query = f"""
        CREATE TABLE IF NOT EXISTS {table} (
            {columns}
        ) ENGINE = {engine}()
        ORDER BY {primary_key}
        """
        
        try:
            self.execute(query)
            logger.info(f"Created table: {table}")
        except Exception as e:
            logger.error(f"Table creation failed: {e}")
            raise
    
    def query_dataframe(self, query: str) -> "pd.DataFrame":
        """Execute query and return pandas DataFrame."""
        try:
            import pandas as pd
            
            result = self.execute(query)
            
            # Get column names from query result
            columns = self.client.execute(f"DESCRIBE ({query})")[0]
            column_names = [col[0] for col in columns]
            
            return pd.DataFrame(result, columns=column_names)
        
        except ImportError:
            logger.error("pandas not installed")
            raise
        except Exception as e:
            logger.error(f"DataFrame query failed: {e}")
            raise
```

### Usage Patterns

#### 1. Metrics Storage

```python
from app.core.clickhouse_integration import ClickHouseClient
from datetime import datetime

# Initialize client
ch = ClickHouseClient(host="localhost", port=9000)

# Create metrics table
ch.create_table(
    table="system_metrics",
    schema={
        "timestamp": "DateTime",
        "metric_name": "String",
        "value": "Float64",
        "host": "String",
        "tags": "Map(String, String)"
    },
    engine="MergeTree"
)

# Insert metrics
metrics = [
    {
        "timestamp": datetime.now(),
        "metric_name": "cpu_usage",
        "value": 75.5,
        "host": "server-01",
        "tags": {"region": "us-east", "env": "prod"}
    },
    {
        "timestamp": datetime.now(),
        "metric_name": "memory_usage",
        "value": 4096.0,
        "host": "server-01",
        "tags": {"region": "us-east", "env": "prod"}
    }
]

ch.insert("system_metrics", metrics)

# Query aggregated metrics
query = """
SELECT 
    toStartOfMinute(timestamp) as minute,
    metric_name,
    avg(value) as avg_value,
    max(value) as max_value
FROM system_metrics
WHERE timestamp >= now() - INTERVAL 1 HOUR
GROUP BY minute, metric_name
ORDER BY minute DESC
"""

results = ch.execute(query)
for row in results:
    print(f"{row[0]}: {row[1]} = {row[2]:.2f} (max: {row[3]:.2f})")
```

#### 2. Log Aggregation

```python
# Create logs table
ch.create_table(
    table="application_logs",
    schema={
        "timestamp": "DateTime64(3)",  # Millisecond precision
        "level": "Enum8('DEBUG'=1, 'INFO'=2, 'WARNING'=3, 'ERROR'=4)",
        "message": "String",
        "logger": "String",
        "exception": "Nullable(String)",
        "user_id": "Nullable(String)"
    },
    engine="MergeTree"
)

# Insert logs
logs = [
    {
        "timestamp": datetime.now(),
        "level": "INFO",
        "message": "User login successful",
        "logger": "auth.service",
        "exception": None,
        "user_id": "user123"
    },
    {
        "timestamp": datetime.now(),
        "level": "ERROR",
        "message": "Database connection failed",
        "logger": "db.connection",
        "exception": "ConnectionError: timeout",
        "user_id": None
    }
]

ch.insert("application_logs", logs)

# Analyze error patterns
query = """
SELECT 
    toStartOfHour(timestamp) as hour,
    logger,
    count() as error_count
FROM application_logs
WHERE level = 'ERROR'
  AND timestamp >= now() - INTERVAL 24 HOUR
GROUP BY hour, logger
ORDER BY error_count DESC
LIMIT 10
"""

error_patterns = ch.execute(query)
```

#### 3. Time-Series Analytics

```python
# Create sensor data table
ch.create_table(
    table="sensor_readings",
    schema={
        "timestamp": "DateTime64(6)",     # Microsecond precision
        "sensor_id": "String",
        "temperature": "Float32",
        "humidity": "Float32",
        "pressure": "Float32"
    },
    engine="MergeTree"
)

# Insert high-volume sensor data
readings = [
    {
        "timestamp": datetime.now(),
        "sensor_id": "temp_01",
        "temperature": 22.5,
        "humidity": 45.0,
        "pressure": 1013.25
    }
    # ... thousands of readings
]

ch.insert("sensor_readings", readings)

# Real-time aggregation
query = """
SELECT 
    sensor_id,
    avg(temperature) as avg_temp,
    stddevPop(temperature) as temp_stddev,
    min(temperature) as min_temp,
    max(temperature) as max_temp
FROM sensor_readings
WHERE timestamp >= now() - INTERVAL 5 MINUTE
GROUP BY sensor_id
"""

stats = ch.execute(query)
```

#### 4. Dashboard Queries with Materialized Views

```python
# Create materialized view for pre-aggregated metrics
materialized_view = """
CREATE MATERIALIZED VIEW IF NOT EXISTS metrics_hourly
ENGINE = SummingMergeTree()
ORDER BY (hour, metric_name)
AS SELECT
    toStartOfHour(timestamp) as hour,
    metric_name,
    host,
    sum(value) as total_value,
    count() as sample_count
FROM system_metrics
GROUP BY hour, metric_name, host
"""

ch.execute(materialized_view)

# Query pre-aggregated data (much faster)
query = "SELECT * FROM metrics_hourly WHERE hour >= now() - INTERVAL 24 HOUR"
dashboard_data = ch.execute(query)
```

## RisingWave Integration

### Architecture

```
Application Layer (Event Processing)
    ↓
RisingWaveClient (src/app/core/risingwave_integration.py)
    ↓
PostgreSQL Protocol (port 4566)
    ↓
RisingWave Server
```

### Key Capabilities

- **Stream Processing**: Real-time event processing with SQL
- **Materialized Views**: Incremental updates on streaming data
- **CDC Integration**: Change Data Capture from MySQL, PostgreSQL
- **Exactly-Once Semantics**: Guaranteed message delivery
- **Decoupled Storage**: Unlimited storage with S3/MinIO backend

### Use Cases

1. **Event-Driven Pipelines**: Process Kafka/Pulsar streams
2. **Real-Time Analytics**: Continuous aggregations on live data
3. **CDC Pipelines**: Sync data from operational databases
4. **Alerting Systems**: Real-time anomaly detection
5. **Stream Joins**: Complex event correlation

### Configuration

```bash
# Environment variables
RISINGWAVE_HOST=localhost
RISINGWAVE_PORT=4566              # PostgreSQL-compatible port
RISINGWAVE_DATABASE=dev
RISINGWAVE_USER=root
RISINGWAVE_PASSWORD=
RISINGWAVE_CONNECT_TIMEOUT=10
```

### Implementation

```python
# src/app/core/risingwave_integration.py

import psycopg2
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)

class RisingWaveClient:
    """Client for RisingWave streaming database."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 4566,
        database: str = "dev",
        user: str = "root",
        password: str = "",
        connect_timeout: int = 10,
    ):
        """Initialize RisingWave client (PostgreSQL protocol)."""
        self.connection_params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
            "connect_timeout": connect_timeout,
        }
        self.conn: psycopg2.extensions.connection | None = None
        self._connect()
        
        logger.info(f"RisingWave client initialized: {host}:{port}/{database}")
    
    def _connect(self):
        """Establish connection to RisingWave."""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.conn.autocommit = True
            logger.info("Connected to RisingWave")
        except psycopg2.Error as e:
            logger.error(f"Failed to connect to RisingWave: {e}")
            raise
    
    def execute(self, query: str, params: tuple = None) -> list[dict]:
        """Execute SQL query and return results as dictionaries."""
        if not self.conn or self.conn.closed:
            self._connect()
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                
                # Check if query returns results
                if cursor.description:
                    return [dict(row) for row in cursor.fetchall()]
                return []
        
        except psycopg2.Error as e:
            logger.error(f"Query execution failed: {e}")
            raise
    
    def create_source(self, source_name: str, source_config: dict):
        """Create streaming source (Kafka, Pulsar, Kinesis)."""
        connector = source_config["connector"]
        properties = source_config["properties"]
        
        # Build CREATE SOURCE statement
        props_str = ", ".join([f"{k} = '{v}'" for k, v in properties.items()])
        
        query = f"""
        CREATE SOURCE IF NOT EXISTS {source_name}
        WITH (
            connector = '{connector}',
            {props_str}
        )
        FORMAT {source_config.get('format', 'JSON')}
        """
        
        try:
            self.execute(query)
            logger.info(f"Created source: {source_name}")
        except Exception as e:
            logger.error(f"Source creation failed: {e}")
            raise
    
    def create_materialized_view(self, view_name: str, query: str):
        """Create materialized view with incremental updates."""
        mv_query = f"CREATE MATERIALIZED VIEW IF NOT EXISTS {view_name} AS {query}"
        
        try:
            self.execute(mv_query)
            logger.info(f"Created materialized view: {view_name}")
        except Exception as e:
            logger.error(f"Materialized view creation failed: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("RisingWave connection closed")
```

### Usage Patterns

#### 1. Kafka Stream Processing

```python
from app.core.risingwave_integration import RisingWaveClient

# Initialize client
rw = RisingWaveClient(host="localhost", port=4566)

# Create Kafka source
rw.create_source(
    source_name="user_events_kafka",
    source_config={
        "connector": "kafka",
        "properties": {
            "topic": "user-events",
            "properties.bootstrap.server": "kafka:9092",
            "scan.startup.mode": "earliest"
        },
        "format": "JSON"
    }
)

# Create materialized view for real-time aggregation
mv_query = """
SELECT 
    window_start,
    event_type,
    COUNT(*) as event_count
FROM TUMBLE(user_events_kafka, timestamp, INTERVAL '1' MINUTE)
GROUP BY window_start, event_type
"""

rw.create_materialized_view("user_events_per_minute", mv_query)

# Query materialized view
results = rw.execute("SELECT * FROM user_events_per_minute ORDER BY window_start DESC LIMIT 10")
for row in results:
    print(f"{row['window_start']}: {row['event_type']} - {row['event_count']} events")
```

#### 2. CDC from PostgreSQL

```python
# Create CDC source from PostgreSQL
rw.create_source(
    source_name="postgres_users_cdc",
    source_config={
        "connector": "postgres-cdc",
        "properties": {
            "hostname": "postgres-db",
            "port": "5432",
            "username": "postgres",
            "password": "password",
            "database.name": "myapp",
            "schema.name": "public",
            "table.name": "users"
        }
    }
)

# Create materialized view to track user activity
mv_query = """
SELECT 
    user_id,
    COUNT(*) as login_count,
    MAX(last_login) as last_seen
FROM postgres_users_cdc
WHERE event_type = 'login'
GROUP BY user_id
"""

rw.create_materialized_view("user_activity", mv_query)
```

#### 3. Real-Time Anomaly Detection

```python
# Create source for metrics stream
rw.create_source(
    source_name="system_metrics_stream",
    source_config={
        "connector": "kafka",
        "properties": {
            "topic": "system-metrics",
            "properties.bootstrap.server": "kafka:9092"
        },
        "format": "JSON"
    }
)

# Materialized view for anomaly detection
anomaly_query = """
SELECT 
    window_start,
    host,
    AVG(cpu_usage) as avg_cpu,
    STDDEV(cpu_usage) as cpu_stddev,
    CASE 
        WHEN AVG(cpu_usage) > 90 THEN 'CRITICAL'
        WHEN AVG(cpu_usage) > 75 THEN 'WARNING'
        ELSE 'NORMAL'
    END as alert_level
FROM TUMBLE(system_metrics_stream, timestamp, INTERVAL '5' MINUTE)
GROUP BY window_start, host
HAVING AVG(cpu_usage) > 75
"""

rw.create_materialized_view("cpu_anomalies", anomaly_query)

# Poll for anomalies
anomalies = rw.execute("""
SELECT * FROM cpu_anomalies 
WHERE alert_level IN ('WARNING', 'CRITICAL')
ORDER BY window_start DESC
""")
```

#### 4. Stream Joins

```python
# Join user events with user profiles
join_query = """
SELECT 
    e.event_id,
    e.user_id,
    e.event_type,
    e.timestamp,
    u.username,
    u.email,
    u.subscription_tier
FROM user_events_stream e
LEFT JOIN user_profiles_table u
ON e.user_id = u.user_id
WHERE e.timestamp >= NOW() - INTERVAL '1' HOUR
"""

rw.create_materialized_view("enriched_events", join_query)
```

## Performance Optimization

### ClickHouse Best Practices

```python
# 1. Use appropriate table engine
ch.create_table(
    table="events",
    schema={"timestamp": "DateTime", "user_id": "String", "event": "String"},
    engine="MergeTree"  # For most cases
    # engine="ReplacingMergeTree"  # For deduplication
    # engine="AggregatingMergeTree"  # For pre-aggregation
)

# 2. Optimize ORDER BY clause (affects storage and query performance)
query = """
CREATE TABLE events (
    timestamp DateTime,
    user_id String,
    event String
) ENGINE = MergeTree()
ORDER BY (user_id, timestamp)  # Order by most selective columns first
"""

# 3. Use PREWHERE for filtering (more efficient than WHERE)
query = """
SELECT user_id, count() as event_count
FROM events
PREWHERE timestamp >= today() - 7
WHERE event = 'purchase'
GROUP BY user_id
"""

# 4. Partition large tables by date
query = """
CREATE TABLE events_partitioned (
    timestamp DateTime,
    user_id String,
    event String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)  # Monthly partitions
ORDER BY (user_id, timestamp)
"""
```

### RisingWave Best Practices

```python
# 1. Use appropriate window types
tumble_window = """
SELECT window_start, COUNT(*) as count
FROM TUMBLE(events, timestamp, INTERVAL '1' MINUTE)
GROUP BY window_start
"""

hop_window = """
SELECT window_start, window_end, AVG(value) as avg_value
FROM HOP(metrics, timestamp, INTERVAL '30' SECOND, INTERVAL '5' MINUTE)
GROUP BY window_start, window_end
"""

# 2. Create indexes on frequently queried columns
rw.execute("CREATE INDEX idx_user_id ON user_events(user_id)")

# 3. Use connection pooling for high-throughput scenarios
from psycopg2 import pool

connection_pool = pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=20,
    host="localhost",
    port=4566,
    database="dev"
)
```

## Monitoring

### ClickHouse Metrics

```python
# Check query performance
query_stats = ch.execute("""
SELECT 
    query,
    query_duration_ms,
    read_rows,
    read_bytes,
    result_rows
FROM system.query_log
WHERE type = 'QueryFinish'
  AND event_time >= now() - INTERVAL 1 HOUR
ORDER BY query_duration_ms DESC
LIMIT 10
""")

# Monitor table sizes
table_sizes = ch.execute("""
SELECT 
    database,
    table,
    formatReadableSize(sum(bytes)) as size,
    sum(rows) as rows
FROM system.parts
WHERE active
GROUP BY database, table
ORDER BY sum(bytes) DESC
""")
```

### RisingWave Metrics

```python
# Check materialized view status
mv_status = rw.execute("""
SELECT 
    name,
    definition,
    is_mview,
    created_at
FROM rw_catalog.rw_views
WHERE is_mview = true
""")

# Monitor source lag
source_lag = rw.execute("""
SELECT 
    name,
    connector,
    split_id,
    latest_offset,
    lag_ms
FROM rw_catalog.rw_source_offsets
ORDER BY lag_ms DESC
""")
```

## References

- **ClickHouse Documentation**: https://clickhouse.com/docs
- **RisingWave Documentation**: https://docs.risingwave.com
- **ClickHouse Python Driver**: https://clickhouse-driver.readthedocs.io
- **psycopg2 Documentation**: https://www.psycopg.org/docs

## Related Documentation

- [Data Persistence](./05-data-persistence.md)
- [Monitoring Systems](../architecture/monitoring.md)
- [Real-Time Analytics](../architecture/analytics.md)
