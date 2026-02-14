"""
OpenTelemetry Integration for Production Observability
Provides distributed tracing, metrics, and logging
"""

import logging
import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import start_http_server

logger = logging.getLogger(__name__)


class ObservabilityConfig:
    """Configuration for observability setup"""

    def __init__(self):
        self.service_name = os.getenv("SERVICE_NAME", "project-ai")
        self.service_version = os.getenv("SERVICE_VERSION", "1.0.0")
        self.environment = os.getenv("APP_ENV", "production")

        # OTLP configuration
        self.otlp_endpoint = os.getenv("OTLP_ENDPOINT", "localhost:4317")
        self.enable_otlp = os.getenv("ENABLE_OTLP", "true").lower() == "true"

        # Prometheus configuration
        self.prometheus_port = int(os.getenv("PROMETHEUS_PORT", "9090"))
        self.enable_prometheus = os.getenv("ENABLE_PROMETHEUS", "true").lower() == "true"

        # Tracing configuration
        self.trace_sample_rate = float(os.getenv("TRACE_SAMPLE_RATE", "0.1"))

        # Logging configuration
        self.log_level = os.getenv("LOG_LEVEL", "INFO")


def setup_observability(app, config: ObservabilityConfig | None = None):
    """
    Setup comprehensive observability for FastAPI application

    Args:
        app: FastAPI application instance
        config: Optional observability configuration
    """
    if config is None:
        config = ObservabilityConfig()

    # Create resource
    resource = Resource.create({
        SERVICE_NAME: config.service_name,
        SERVICE_VERSION: config.service_version,
        "deployment.environment": config.environment,
    })

    # Setup tracing
    _setup_tracing(config, resource)

    # Setup metrics
    _setup_metrics(config, resource)

    # Setup logging
    _setup_logging(config)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrument HTTP client
    HTTPXClientInstrumentor().instrument()

    logger.info(
        f"Observability initialized for {config.service_name} v{config.service_version}"
    )


def _setup_tracing(config: ObservabilityConfig, resource: Resource):
    """Setup distributed tracing"""
    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)

    # Add OTLP exporter if enabled
    if config.enable_otlp:
        try:
            otlp_exporter = OTLPSpanExporter(endpoint=config.otlp_endpoint)
            span_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(span_processor)
            logger.info(f"OTLP trace exporter configured: {config.otlp_endpoint}")
        except Exception as e:
            logger.warning(f"Failed to setup OTLP trace exporter: {e}")

    # Set global tracer provider
    trace.set_tracer_provider(tracer_provider)


def _setup_metrics(config: ObservabilityConfig, resource: Resource):
    """Setup metrics collection"""
    readers = []

    # Add Prometheus exporter if enabled
    if config.enable_prometheus:
        try:
            prometheus_reader = PrometheusMetricReader()
            readers.append(prometheus_reader)

            # Start Prometheus HTTP server
            start_http_server(port=config.prometheus_port)
            logger.info(f"Prometheus metrics server started on port {config.prometheus_port}")
        except Exception as e:
            logger.warning(f"Failed to setup Prometheus exporter: {e}")

    # Add OTLP exporter if enabled
    if config.enable_otlp:
        try:
            otlp_exporter = OTLPMetricExporter(endpoint=config.otlp_endpoint)
            otlp_reader = PeriodicExportingMetricReader(otlp_exporter)
            readers.append(otlp_reader)
            logger.info(f"OTLP metric exporter configured: {config.otlp_endpoint}")
        except Exception as e:
            logger.warning(f"Failed to setup OTLP metric exporter: {e}")

    # Create meter provider
    if readers:
        meter_provider = MeterProvider(resource=resource, metric_readers=readers)
        metrics.set_meter_provider(meter_provider)


def _setup_logging(config: ObservabilityConfig):
    """Setup structured logging"""
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Setup basic logging
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format=log_format
    )

    # Instrument logging to add trace context
    LoggingInstrumentor().instrument(set_logging_format=True)


# Custom metrics helpers
def get_meter(name: str = "project-ai"):
    """Get a meter for creating custom metrics"""
    return metrics.get_meter(name)


def get_tracer(name: str = "project-ai"):
    """Get a tracer for creating custom spans"""
    return trace.get_tracer(name)


# Example custom metrics
def create_custom_metrics():
    """Create custom application metrics"""
    meter = get_meter()

    # Counter for total requests
    request_counter = meter.create_counter(
        name="app.requests.total",
        description="Total number of requests",
        unit="1"
    )

    # Histogram for request duration
    request_duration = meter.create_histogram(
        name="app.requests.duration",
        description="Request duration in milliseconds",
        unit="ms"
    )

    # UpDownCounter for active connections
    active_connections = meter.create_up_down_counter(
        name="app.connections.active",
        description="Number of active connections",
        unit="1"
    )

    return {
        "request_counter": request_counter,
        "request_duration": request_duration,
        "active_connections": active_connections
    }


# Usage example
"""
from fastapi import FastAPI
from observability import setup_observability

app = FastAPI()

# Setup observability
setup_observability(app)

# Create custom metrics
custom_metrics = create_custom_metrics()

@app.get("/api/endpoint")
async def endpoint():
    # Increment request counter
    custom_metrics["request_counter"].add(1, {"endpoint": "/api/endpoint"})

    # Create custom span
    tracer = get_tracer()
    with tracer.start_as_current_span("custom_operation"):
        # Your operation here
        pass

    return {"status": "ok"}
"""
