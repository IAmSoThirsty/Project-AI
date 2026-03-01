"""
Shared Sovereign Middleware for Emergent Microservices
Provides standardized logging, metrics, and Triumvirate-level security.
"""

import json
import logging
import time
import uuid

from fastapi import Request, Response
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware

# Standardized Metrics
REQUEST_COUNT = Counter(
    "sovereign_request_total",
    "Total HTTP requests",
    ["service", "method", "endpoint", "http_status"],
)
REQUEST_LATENCY = Histogram(
    "sovereign_request_latency_seconds", "HTTP request latency", ["service", "endpoint"]
)


class SovereignMonitoringMiddleware(BaseHTTPMiddleware):
    """Standardized monitoring and tracing middleware"""

    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start_time = time.time()

        # Inject context for logging
        logging.getLogger().extra = {
            "request_id": request_id,
            "service": self.service_name,
        }

        response = await call_next(request)

        process_time = time.time() - start_time
        REQUEST_COUNT.labels(
            service=self.service_name,
            method=request.method,
            endpoint=request.url.path,
            http_status=response.status_code,
        ).inc()

        REQUEST_LATENCY.labels(
            service=self.service_name, endpoint=request.url.path
        ).observe(process_time)

        response.headers["X-Request-ID"] = request_id
        return response


class SovereignJSONFormatter(logging.Formatter):
    """Standardized JSON log formatter for sovereign systems"""

    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": getattr(record, "service", "unknown"),
            "request_id": getattr(record, "request_id", "none"),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


def setup_sovereign_logging(service_name: str):
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = SovereignJSONFormatter()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
