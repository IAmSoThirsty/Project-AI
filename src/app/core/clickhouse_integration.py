"""
ClickHouse Integration for Project-AI

ClickHouse is a column-oriented OLAP database with:
- 1B+ rows/second ingestion rate
- Real-time analytics on massive datasets
- SQL interface with advanced analytics functions
- Excellent compression (10-30x)
- Horizontal scaling to 1000+ nodes

Perfect for:
- High-volume metrics storage (Prometheus long-term)
- Log aggregation and analytics (ELK alternative)
- Real-time dashboards
- Time-series data
- ML feature stores
"""

import logging
from datetime import datetime

from clickhouse_driver import Client as ClickHouseDriver

logger = logging.getLogger(__name__)


class ClickHouseClient:
    """
    Client for ClickHouse OLAP database.

    Provides high-level interface for:
    - Billion+ row ingestion
    - Real-time analytics queries
    - Time-series data storage
    - Metrics aggregation
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 9000,
        database: str = "default",
        user: str = "default",
        password: str = "",
        compression: bool = True,
    ):
        """Initialize ClickHouse client.

        Args:
            host: ClickHouse server host
            port: Native protocol port (default: 9000)
            database: Database name
            user: Username
            password: Password
            compression: Enable LZ4 compression
        """
        self.host = host
        self.port = port
        self.database = database

        # Use native driver for best performance
        self.client = ClickHouseDriver(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            compression=compression,
        )

        logger.info("ClickHouse client initialized: %s:%s/%s", host, port, database)

    def execute(self, query: str, params: dict = None) -> list[tuple]:
        """Execute SQL query.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Query results
        """
        try:
            result = self.client.execute(query, params or {})
            return result
        except Exception as e:
            logger.error("Query execution failed: %s", e)
            raise

    def insert(self, table: str, data: list[dict]):
        """Bulk insert data into table.

        Args:
            table: Table name
            data: List of dictionaries to insert
        """
        if not data:
            return

        # Get column names from first row
        columns = list(data[0].keys())

        # Prepare values
        values = [[row[col] for col in columns] for row in data]

        # Build insert query
        columns_str = ", ".join(columns)
        query = f"INSERT INTO {table} ({columns_str}) VALUES"

        self.client.execute(query, values)
        logger.info("Inserted %s rows into %s", len(data), table)

    def query_dataframe(self, query: str):
        """Execute query and return as pandas DataFrame.

        Args:
            query: SQL query

        Returns:
            pandas DataFrame
        """
        try:
            import pandas as pd

            result = self.execute(query)

            # Get column names from query
            # This is a simplified approach
            columns = [f"col_{i}" for i in range(len(result[0]))] if result else []

            return pd.DataFrame(result, columns=columns)
        except ImportError:
            logger.error("pandas not installed - cannot return DataFrame")
            return self.execute(query)

    def create_metrics_table(self, table_name: str = "project_ai_metrics"):
        """Create table for Project-AI metrics storage.

        Args:
            table_name: Name of metrics table
        """
        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            timestamp DateTime,
            metric_name String,
            metric_value Float64,
            labels Map(String, String),
            component String,
            severity String
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMM(timestamp)
        ORDER BY (component, metric_name, timestamp)
        SETTINGS index_granularity = 8192;
        """

        self.execute(query)
        logger.info("Created metrics table: %s", table_name)

    def create_logs_table(self, table_name: str = "project_ai_logs"):
        """Create table for high-volume log storage.

        Args:
            table_name: Name of logs table
        """
        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            timestamp DateTime64(3),
            level String,
            component String,
            message String,
            metadata String,  -- JSON string
            source_ip String,
            user_id String
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMMDD(timestamp)
        ORDER BY (component, level, timestamp)
        SETTINGS index_granularity = 8192;
        """

        self.execute(query)
        logger.info("Created logs table: %s", table_name)

    def create_events_table(self, table_name: str = "project_ai_events"):
        """Create table for AI system events.

        Args:
            table_name: Name of events table
        """
        query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            event_id String,
            timestamp DateTime64(3),
            event_type String,
            component String,
            severity String,
            data String,  -- JSON string
            processed Boolean DEFAULT false
        ) ENGINE = MergeTree()
        PARTITION BY toYYYYMMDD(timestamp)
        ORDER BY (component, event_type, timestamp)
        SETTINGS index_granularity = 8192;
        """

        self.execute(query)
        logger.info("Created events table: %s", table_name)

    def insert_metric(
        self,
        metric_name: str,
        value: float,
        component: str = "unknown",
        labels: dict | None = None,
        timestamp: datetime | None = None,
    ):
        """Insert single metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            component: Component generating metric
            labels: Additional labels
            timestamp: Metric timestamp (defaults to now)
        """
        ts = timestamp or datetime.now()
        labels = labels or {}

        self.insert(
            "project_ai_metrics",
            [
                {
                    "timestamp": ts,
                    "metric_name": metric_name,
                    "metric_value": value,
                    "labels": labels,
                    "component": component,
                    "severity": "info",
                }
            ],
        )

    def query_metrics_aggregated(
        self,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        interval: str = "1m",
    ) -> list[tuple]:
        """Query aggregated metrics over time windows.

        Args:
            metric_name: Metric to query
            start_time: Start time
            end_time: End time
            interval: Aggregation interval (e.g., '1m', '5m', '1h')

        Returns:
            Aggregated metric data
        """
        query = f"""
        SELECT
            toStartOfInterval(timestamp, INTERVAL {interval}) as time_bucket,
            avg(metric_value) as avg_value,
            max(metric_value) as max_value,
            min(metric_value) as min_value,
            count() as sample_count
        FROM project_ai_metrics
        WHERE metric_name = '{metric_name}'
        AND timestamp BETWEEN '{start_time}' AND '{end_time}'
        GROUP BY time_bucket
        ORDER BY time_bucket;
        """

        return self.execute(query)

    def get_top_components_by_events(
        self, limit: int = 10, hours: int = 24
    ) -> list[tuple]:
        """Get components with most events in last N hours.

        Args:
            limit: Number of results
            hours: Time window in hours

        Returns:
            Component statistics
        """
        query = f"""
        SELECT
            component,
            count() as event_count,
            uniqExact(event_type) as unique_event_types,
            countIf(severity = 'critical') as critical_count
        FROM project_ai_events
        WHERE timestamp > now() - INTERVAL {hours} HOUR
        GROUP BY component
        ORDER BY event_count DESC
        LIMIT {limit};
        """

        return self.execute(query)

    def close(self):
        """Close connection to ClickHouse."""
        self.client.disconnect()
        logger.info("ClickHouse connection closed")


class ProjectAIAnalytics:
    """
    Analytics layer for Project-AI using ClickHouse.

    Provides billion-scale analytics on AI system data.
    """

    def __init__(self, clickhouse_host: str = "localhost", clickhouse_port: int = 9000):
        """Initialize analytics layer.

        Args:
            clickhouse_host: ClickHouse host
            clickhouse_port: ClickHouse port
        """
        self.client = ClickHouseClient(
            host=clickhouse_host, port=clickhouse_port, database="project_ai"
        )

        # Create database if not exists
        self.client.execute("CREATE DATABASE IF NOT EXISTS project_ai")

        # Setup tables
        self._setup_tables()

        logger.info("Project-AI analytics initialized")

    def _setup_tables(self):
        """Set up analytics tables."""
        self.client.create_metrics_table()
        self.client.create_logs_table()
        self.client.create_events_table()

        # Create materialized views for common queries
        self._create_materialized_views()

    def _create_materialized_views(self):
        """Create materialized views for fast queries."""

        # Hourly metrics aggregation
        self.client.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS metrics_hourly
        ENGINE = SummingMergeTree()
        PARTITION BY toYYYYMM(hour)
        ORDER BY (component, metric_name, hour)
        AS SELECT
            toStartOfHour(timestamp) as hour,
            component,
            metric_name,
            avg(metric_value) as avg_value,
            max(metric_value) as max_value,
            min(metric_value) as min_value,
            count() as sample_count
        FROM project_ai_metrics
        GROUP BY hour, component, metric_name;
        """)

        logger.info("Materialized views created")

    def store_prometheus_metrics(self, metrics_batch: list[dict]):
        """Store Prometheus metrics in ClickHouse for long-term retention.

        Args:
            metrics_batch: List of metric dictionaries from Prometheus
        """
        self.client.insert("project_ai_metrics", metrics_batch)

    def analyze_persona_evolution(self, trait_name: str, days: int = 30) -> list[tuple]:
        """Analyze AI persona trait evolution over time.

        Args:
            trait_name: Personality trait name
            days: Number of days to analyze

        Returns:
            Evolution data
        """
        query = f"""
        SELECT
            toDate(timestamp) as date,
            avg(metric_value) as avg_trait_value,
            stddevPop(metric_value) as trait_variance
        FROM project_ai_metrics
        WHERE metric_name = 'persona_trait'
        AND labels['trait'] = '{trait_name}'
        AND timestamp > now() - INTERVAL {days} DAY
        GROUP BY date
        ORDER BY date;
        """

        return self.client.execute(query)

    def get_security_incident_trends(self, hours: int = 24) -> list[tuple]:
        """Get security incident trends.

        Args:
            hours: Time window in hours

        Returns:
            Incident trend data
        """
        query = f"""
        SELECT
            toStartOfHour(timestamp) as hour,
            severity,
            count() as incident_count
        FROM project_ai_events
        WHERE component = 'security'
        AND timestamp > now() - INTERVAL {hours} HOUR
        GROUP BY hour, severity
        ORDER BY hour, severity;
        """

        return self.client.execute(query)

    def close(self):
        """Close analytics connection."""
        self.client.close()


def create_clickhouse_client(
    host: str = "localhost", port: int = 9000, database: str = "default"
) -> ClickHouseClient:
    """Create ClickHouse client for Project-AI.

    Args:
        host: ClickHouse host
        port: ClickHouse port
        database: Database name

    Returns:
        ClickHouseClient instance
    """
    return ClickHouseClient(host=host, port=port, database=database)
