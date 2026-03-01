"""
Prometheus metrics instrumentation
"""

from prometheus_client import Counter, Gauge, Histogram, Info

# Service info
service_info = Info(
    "service_autonomous_compliance_as_code_engine", "Service information"
)
service_info.info(
    {
        "version": "1.0.0",
        "name": "Autonomous Compliance-as-Code Engine",
    }
)

# HTTP Metrics
REQUEST_COUNT = Counter(
    "service_autonomous_compliance_as_code_engine_requests_total",
    "Total number of requests",
    ["method", "route_template", "status_class"],
)

REQUEST_DURATION = Histogram(
    "service_autonomous_compliance_as_code_engine_request_duration_seconds",
    "Request duration in seconds",
    ["method", "route_template"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5],
)

INFLIGHT_REQUESTS = Gauge(
    "service_autonomous_compliance_as_code_engine_requests_inflight",
    "Number of requests currently being processed",
)

# Database Metrics
DB_CONNECTIONS_ACTIVE = Gauge(
    "service_autonomous_compliance_as_code_engine_db_connections_active",
    "Number of active database connections",
)

DB_QUERY_DURATION = Histogram(
    "service_autonomous_compliance_as_code_engine_db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5],
)

DB_ERRORS = Counter(
    "service_autonomous_compliance_as_code_engine_db_errors_total",
    "Total database errors",
    ["operation", "error_type"],
)

# Business Metrics
DOMAIN_EVENTS = Counter(
    "service_autonomous_compliance_as_code_engine_domain_events_total",
    "Total domain events",
    ["event_type"],
)

DOMAIN_FAILURES = Counter(
    "service_autonomous_compliance_as_code_engine_domain_failures_total",
    "Total domain operation failures",
    ["operation", "reason"],
)

# Rate Limiting Metrics
RATE_LIMIT_REJECTIONS = Counter(
    "service_autonomous_compliance_as_code_engine_rate_limit_rejections_total",
    "Total rate limit rejections",
    ["client_type"],
)

# Authentication Metrics
AUTH_ATTEMPTS = Counter(
    "service_autonomous_compliance_as_code_engine_auth_attempts_total",
    "Total authentication attempts",
    ["status"],
)
