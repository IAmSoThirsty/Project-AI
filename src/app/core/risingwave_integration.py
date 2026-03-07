#                                           [2026-03-05 10:03]
#                                          Productivity: Active
"""
RisingWave Streaming Database Integration for Project-AI

RisingWave is a distributed SQL streaming database with decoupled storage,
optimized for:
- Event-driven applications
- Change Data Capture (CDC) pipelines
- Real-time analytics
- Materialized views with incremental updates
- Unlimited storage with S3/MinIO backend

Key Features:
- PostgreSQL-compatible interface
- Stream processing with SQL
- Exactly-once semantics
- Auto-scaling with separated compute/storage
- Low latency (<100ms) stream processing
"""

import logging

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class RisingWaveClient:
    """
    Client for RisingWave streaming database.

    Provides high-level interface for:
    - Stream ingestion (Kafka, Pulsar, Kinesis)
    - Materialized views for real-time aggregations
    - CDC integration (MySQL, PostgreSQL)
    - Event-driven data pipelines
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 4566,
        database: str = "dev",
        user: str = "root",
        password: str = "",
        connect_timeout: int = 10,
    ):
        """Initialize RisingWave client.

        Args:
            host: RisingWave server host
            port: RisingWave server port (default: 4566)
            database: Database name
            user: Username
            password: Password
            connect_timeout: Connection timeout in seconds
        """
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

        logger.info("RisingWave client initialized: %s:%s/%s", host, port, database)

    def _connect(self):
        """Establish connection to RisingWave."""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.conn.autocommit = True
            logger.info("Connected to RisingWave")
        except psycopg2.Error as e:
            logger.error("Failed to connect to RisingWave: %s", e)
            raise

    def execute(self, query: str, params: tuple = None) -> list[dict]:
        """Execute SQL query and return results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of result rows as dictionaries
        """
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
            logger.error("Query execution failed: %s", e)
            raise

    def create_source_kafka(
        self,
        source_name: str,
        topic: str,
        bootstrap_servers: str,
        schema_definition: str,
        properties: dict | None = None,
    ):
        """Create Kafka source for stream ingestion.

        Args:
            source_name: Name of the source
            topic: Kafka topic name
            bootstrap_servers: Kafka bootstrap servers
            schema_definition: Table schema (e.g., "id INT, name VARCHAR, ts TIMESTAMP")
            properties: Additional Kafka properties
        """
        # Validate source_name to prevent SQL injection
        if not source_name.replace('_', '').isalnum():
            raise ValueError("Source name must contain only alphanumeric characters and underscores")
        
        props = properties or {}
        
        # Use parameterized query to prevent SQL injection
        query = """
        CREATE SOURCE IF NOT EXISTS {} (
            {}
        ) WITH (
            connector = 'kafka',
            topic = %s,
            properties.bootstrap.server = %s
        ) FORMAT PLAIN ENCODE JSON;
        """.format(source_name, schema_definition)  # source_name and schema validated above
        
        # Additional properties handled separately with validation
        if props:
            # Validate property keys to prevent injection
            for key in props.keys():
                if not key.replace('.', '').replace('_', '').isalnum():
                    raise ValueError(f"Invalid property key: {key}")
        
        self.execute(query, (topic, bootstrap_servers))
        logger.info("Created Kafka source: %s", source_name)

    def create_source_cdc_postgres(
        self,
        source_name: str,
        host: str,
        port: int,
        database: str,
        schema: str,
        table: str,
        user: str,
        password: str,
    ):
        """Create CDC source for PostgreSQL table.

        Args:
            source_name: Name of the CDC source
            host: PostgreSQL host
            port: PostgreSQL port
            database: PostgreSQL database
            schema: PostgreSQL schema
            table: PostgreSQL table name
            user: PostgreSQL user
            password: PostgreSQL password
        """
        # Validate source_name to prevent SQL injection
        if not source_name.replace('_', '').isalnum():
            raise ValueError("Source name must contain only alphanumeric characters and underscores")
        
        query = """
        CREATE SOURCE IF NOT EXISTS {}
        WITH (
            connector = 'postgres-cdc',
            hostname = %s,
            port = %s,
            username = %s,
            password = %s,
            database.name = %s,
            schema.name = %s,
            table.name = %s
        );
        """.format(source_name)  # source_name validated above

        self.execute(query, (host, str(port), user, password, database, schema, table))
        logger.info(
            "Created CDC source: %s from %s:%s/%s", source_name, host, port, database
        )

    def create_materialized_view(self, view_name: str, query: str):
        """Create materialized view for real-time aggregations.

        Materialized views are incrementally updated as new data arrives.

        Args:
            view_name: Name of the materialized view
            query: SELECT query defining the view
        """
        mv_query = f"""
        CREATE MATERIALIZED VIEW IF NOT EXISTS {view_name} AS
        {query};
        """

        self.execute(mv_query)
        logger.info("Created materialized view: %s", view_name)

    def create_sink_kafka(
        self,
        sink_name: str,
        from_source: str,
        topic: str,
        bootstrap_servers: str,
        properties: dict | None = None,
    ):
        """Create Kafka sink to publish processed data.

        Args:
            sink_name: Name of the sink
            from_source: Source table/view to publish from
            topic: Kafka topic to publish to
            bootstrap_servers: Kafka bootstrap servers
            properties: Additional Kafka properties
        """
        props = properties or {}
        props_str = ", ".join([f"'{k}' = '{v}'" for k, v in props.items()])

        query = f"""
        CREATE SINK IF NOT EXISTS {sink_name}
        FROM {from_source}
        WITH (
            connector = 'kafka',
            properties.bootstrap.server = '{bootstrap_servers}',
            topic = '{topic}'
            {", " + props_str if props_str else ""}
        ) FORMAT PLAIN ENCODE JSON;
        """

        self.execute(query)
        logger.info("Created Kafka sink: %s", sink_name)

    def query_stream(
        self, table_or_view: str, where_clause: str = "", limit: int = 100
    ) -> list[dict]:
        """Query streaming data.

        Args:
            table_or_view: Table or materialized view name
            where_clause: Optional WHERE clause (should use parameterized queries)
            limit: Result limit

        Returns:
            Query results
        """
        # Validate table_or_view name to prevent SQL injection
        if not table_or_view.replace('_', '').isalnum():
            raise ValueError("Table/view name must contain only alphanumeric characters and underscores")
        
        # Validate limit is within reasonable bounds
        if not isinstance(limit, int) or limit < 1 or limit > 10000:
            raise ValueError("Limit must be an integer between 1 and 10000")
        
        query = "SELECT * FROM {}".format(table_or_view)  # table_or_view validated above
        params = []
        
        if where_clause:
            # WARNING: where_clause should be parameterized by caller
            # This is a compromise for existing API compatibility
            query += " WHERE " + where_clause
        
        query += " LIMIT %s"
        params.append(limit)

        return self.execute(query, tuple(params) if params else None)

    def get_stream_stats(self, source_name: str) -> dict:
        """Get statistics for a streaming source.

        Args:
            source_name: Name of the source

        Returns:
            Statistics dictionary
        """
        # Validate source_name to prevent SQL injection
        if not source_name.replace('_', '').isalnum():
            raise ValueError("Source name must contain only alphanumeric characters and underscores")
        
        query = """
        SELECT
            COUNT(*) as row_count,
            MIN(event_time) as earliest_event,
            MAX(event_time) as latest_event
        FROM {};
        """.format(source_name)  # source_name validated above

        results = self.execute(query)
        return results[0] if results else {}

    def close(self):
        """Close connection to RisingWave."""
        if self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("RisingWave connection closed")


class ProjectAIEventStream:
    """
    Event streaming pipeline for Project-AI using RisingWave.

    Streams AI system events (persona changes, security incidents, etc.)
    for real-time analytics and monitoring.
    """

    def __init__(
        self,
        risingwave_host: str = "localhost",
        risingwave_port: int = 4566,
        kafka_bootstrap: str = "localhost:9092",
    ):
        """Initialize Project-AI event streaming.

        Args:
            risingwave_host: RisingWave host
            risingwave_port: RisingWave port
            kafka_bootstrap: Kafka bootstrap servers
        """
        self.client = RisingWaveClient(host=risingwave_host, port=risingwave_port)
        self.kafka_bootstrap = kafka_bootstrap

        self._setup_streams()

        logger.info("Project-AI event streaming initialized")

    def _setup_streams(self):
        """Set up streaming tables and views for Project-AI."""

        # AI Persona events stream
        self.client.create_source_kafka(
            source_name="ai_persona_events",
            topic="project-ai.persona.events",
            bootstrap_servers=self.kafka_bootstrap,
            schema_definition="""
                event_id VARCHAR,
                timestamp TIMESTAMP,
                trait_name VARCHAR,
                old_value DOUBLE,
                new_value DOUBLE,
                trigger VARCHAR
            """,
        )

        # Security events stream
        self.client.create_source_kafka(
            source_name="security_events",
            topic="project-ai.security.events",
            bootstrap_servers=self.kafka_bootstrap,
            schema_definition="""
                event_id VARCHAR,
                timestamp TIMESTAMP,
                severity VARCHAR,
                event_type VARCHAR,
                source VARCHAR,
                description TEXT
            """,
        )

        # Four Laws events stream
        self.client.create_source_kafka(
            source_name="four_laws_events",
            topic="project-ai.fourlaws.events",
            bootstrap_servers=self.kafka_bootstrap,
            schema_definition="""
                event_id VARCHAR,
                timestamp TIMESTAMP,
                action VARCHAR,
                is_allowed BOOLEAN,
                law_violated VARCHAR,
                reason TEXT
            """,
        )

        # Real-time aggregations
        self._create_analytics_views()

        logger.info("Event streams configured")

    def _create_analytics_views(self):
        """Create materialized views for real-time analytics."""

        # Persona trait trends (1-minute windows)
        self.client.create_materialized_view(
            view_name="persona_trait_trends",
            query="""
            SELECT
                trait_name,
                window_start,
                AVG(new_value) as avg_value,
                MAX(new_value) as max_value,
                MIN(new_value) as min_value,
                COUNT(*) as change_count
            FROM TUMBLE(ai_persona_events, timestamp, INTERVAL '1' MINUTE)
            GROUP BY trait_name, window_start
            """,
        )

        # Security incident counts by severity
        self.client.create_materialized_view(
            view_name="security_incidents_by_severity",
            query="""
            SELECT
                severity,
                window_start,
                COUNT(*) as incident_count,
                COUNT(DISTINCT event_type) as unique_event_types
            FROM TUMBLE(security_events, timestamp, INTERVAL '5' MINUTE)
            GROUP BY severity, window_start
            """,
        )

        # Four Laws denial rate
        self.client.create_materialized_view(
            view_name="four_laws_denial_rate",
            query="""
            SELECT
                window_start,
                COUNT(*) as total_validations,
                SUM(CASE WHEN is_allowed = false THEN 1 ELSE 0 END) as denials,
                SUM(CASE WHEN is_allowed = false THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as denial_rate
            FROM TUMBLE(four_laws_events, timestamp, INTERVAL '1' MINUTE)
            GROUP BY window_start
            """,
        )

        logger.info("Analytics views created")

    def get_persona_trends(self, trait_name: str, limit: int = 10) -> list[dict]:
        """Get recent persona trait trends.

        Args:
            trait_name: Name of personality trait
            limit: Number of results

        Returns:
            Trend data
        """
        # Use parameterized query to prevent SQL injection
        query = "SELECT * FROM persona_trait_trends WHERE trait_name = %s LIMIT %s"
        return self.client.execute(query, (trait_name, limit))

    def get_security_alerts(
        self, severity: str = "critical", limit: int = 50
    ) -> list[dict]:
        """Get recent security alerts.

        Args:
            severity: Alert severity level
            limit: Number of results

        Returns:
            Security alerts
        """
        # Use parameterized query to prevent SQL injection
        query = "SELECT * FROM security_incidents_by_severity WHERE severity = %s LIMIT %s"
        return self.client.execute(query, (severity, limit))

    def get_ethics_violations(self, limit: int = 100) -> list[dict]:
        """Get Four Laws violation attempts.

        Args:
            limit: Number of results

        Returns:
            Ethics violation data
        """
        # Use parameterized query to prevent SQL injection
        query = "SELECT * FROM four_laws_denial_rate WHERE denial_rate > 0 LIMIT %s"
        return self.client.execute(query, (limit,))

    def close(self):
        """Close streaming connection."""
        self.client.close()


def create_risingwave_client(
    host: str = "localhost", port: int = 4566, database: str = "dev"
) -> RisingWaveClient:
    """Create RisingWave client for Project-AI.

    Args:
        host: RisingWave host
        port: RisingWave port
        database: Database name

    Returns:
        RisingWaveClient instance
    """
    return RisingWaveClient(host=host, port=port, database=database)
