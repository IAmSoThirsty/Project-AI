# OpenTelemetry Instrumentation Guide

# Team Charlie - Observability Engineer

## Overview

This guide explains how to instrument microservices with OpenTelemetry for distributed tracing with Jaeger.

## Prerequisites

- Jaeger deployed in `observability` namespace
- Services running in Kubernetes with Istio sidecar injection

## Python Services Instrumentation

### 1. Install Dependencies

```bash
pip install opentelemetry-api \
            opentelemetry-sdk \
            opentelemetry-instrumentation-fastapi \
            opentelemetry-instrumentation-requests \
            opentelemetry-instrumentation-sqlalchemy \
            opentelemetry-exporter-jaeger
```

### 2. Add to `requirements.txt`

```
opentelemetry-api==1.21.0
opentelemetry-sdk==1.21.0
opentelemetry-instrumentation-fastapi==0.42b0
opentelemetry-instrumentation-requests==0.42b0
opentelemetry-instrumentation-sqlalchemy==0.42b0
opentelemetry-exporter-jaeger==1.21.0
```

### 3. Create Tracing Configuration (`app/tracing.py`)

```python
"""OpenTelemetry tracing configuration"""

import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

def setup_tracing(service_name: str, app=None, engine=None):
    """
    Configure OpenTelemetry tracing for a microservice
    
    Args:
        service_name: Name of the service (e.g., 'sovereign-data-vault')
        app: FastAPI application instance (optional)
        engine: SQLAlchemy engine instance (optional)
    """

    # Jaeger collector endpoint

    jaeger_endpoint = os.getenv(
        "JAEGER_ENDPOINT",
        "http://jaeger-collector.observability.svc.cluster.local:14268/api/traces"
    )
    
    # Create resource with service name

    resource = Resource(attributes={
        SERVICE_NAME: service_name,
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": os.getenv("SERVICE_VERSION", "1.0.0"),
    })
    
    # Configure tracer provider

    tracer_provider = TracerProvider(resource=resource)
    
    # Configure Jaeger exporter

    jaeger_exporter = JaegerExporter(
        collector_endpoint=jaeger_endpoint,
    )
    
    # Add batch span processor

    tracer_provider.add_span_processor(
        BatchSpanProcessor(jaeger_exporter)
    )
    
    # Set global tracer provider

    trace.set_tracer_provider(tracer_provider)
    
    # Auto-instrument FastAPI

    if app:
        FastAPIInstrumentor.instrument_app(app)
    
    # Auto-instrument requests library

    RequestsInstrumentor().instrument()
    
    # Auto-instrument SQLAlchemy

    if engine:
        SQLAlchemyInstrumentor().instrument(engine=engine)
    
    print(f"✅ OpenTelemetry tracing initialized for {service_name}")
    print(f"   Exporting to: {jaeger_endpoint}")

def get_tracer(name: str):
    """Get a tracer instance for manual instrumentation"""
    return trace.get_tracer(name)
```

### 4. Instrument FastAPI Application (`app/main.py`)

```python
from fastapi import FastAPI
from .tracing import setup_tracing, get_tracer
from .database import engine

app = FastAPI(title="Sovereign Data Vault")

# Initialize tracing

setup_tracing(
    service_name="sovereign-data-vault",
    app=app,
    engine=engine
)

# Get tracer for manual spans

tracer = get_tracer(__name__)

@app.get("/api/v1/items/{item_id}")
async def get_item(item_id: str):

    # Manual span example

    with tracer.start_as_current_span("database.query") as span:
        span.set_attribute("item_id", item_id)
        span.set_attribute("operation", "fetch_item")
        
        # Your business logic here

        item = await fetch_item_from_db(item_id)
        
        span.set_attribute("found", item is not None)
        return item
```

### 5. Update Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sovereign-vault
spec:
  template:
    spec:
      containers:

        - name: app
          env:
            # Jaeger configuration
            - name: JAEGER_ENDPOINT
              value: "http://jaeger-collector.observability:14268/api/traces"
            - name: OTEL_TRACES_EXPORTER
              value: "jaeger"
            - name: OTEL_SERVICE_NAME
              valueFrom:
                fieldRef:
                  fieldPath: metadata.labels['app']
            - name: ENVIRONMENT
              value: "production"
            - name: SERVICE_VERSION
              value: "1.0.0"

```

## Manual Instrumentation Patterns

### Async Operations

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def process_mutation(proposal_id: str):
    with tracer.start_as_current_span("mutation.process") as span:
        span.set_attribute("proposal_id", proposal_id)
        
        # Add events to trace

        span.add_event("Starting simulation")
        
        try:
            result = await run_simulation(proposal_id)
            span.set_attribute("simulation.result", result)
            return result
        except Exception as e:
            span.record_exception(e)
            span.set_status(trace.Status(trace.StatusCode.ERROR))
            raise
```

### Cross-Service Calls

```python
import requests
from opentelemetry import trace
from opentelemetry.propagate import inject

tracer = trace.get_tracer(__name__)

def call_trust_graph(node_id: str):
    with tracer.start_as_current_span("trust_graph.get_score") as span:
        headers = {}

        # Inject trace context into headers

        inject(headers)
        
        response = requests.get(
            f"http://trust-graph:8000/api/v1/analysis/trust-score/{node_id}",
            headers=headers
        )
        
        span.set_attribute("http.status_code", response.status_code)
        return response.json()
```

### Database Queries

```python
from sqlalchemy.orm import Session

def query_items(db: Session, user_id: str):
    with tracer.start_as_current_span("database.query_items") as span:
        span.set_attribute("db.system", "postgresql")
        span.set_attribute("db.user", user_id)
        
        items = db.query(Item).filter(Item.owner_id == user_id).all()
        
        span.set_attribute("db.rows_returned", len(items))
        return items
```

## Context Propagation

OpenTelemetry automatically propagates trace context across:

- HTTP requests (via headers)
- gRPC calls
- Message queues (with appropriate instrumentation)

### W3C Trace Context Headers

Automatically injected by OpenTelemetry:

- `traceparent`: `00-{trace-id}-{span-id}-{flags}`
- `tracestate`: Additional vendor-specific data

## Viewing Traces in Jaeger

1. **Access Jaeger UI**: https://jaeger.sovereign.ai
2. **Select Service**: Choose microservice from dropdown
3. **Search Traces**:
   - By operation name
   - By tags (e.g., `http.status_code=500`)
   - By time range
4. **Analyze**:
   - Trace timeline visualization
   - Service dependency graph
   - Error analysis
   - Latency percentiles

## Common Trace Queries

### Find Slow Requests

```
duration > 1s
```

### Find Errors

```
error=true
```

### Find Specific User's Requests

```
user.id=abc123
```

### Find Cross-Service Calls

```
span.kind=client AND service=sovereign-vault
```

## Sampling Configuration

Configure sampling rate in production:

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

# Sample 10% of traces

tracer_provider = TracerProvider(
    sampler=TraceIdRatioBased(0.1),
    resource=resource
)
```

## Best Practices

1. **Span Naming**: Use descriptive names like `service.operation`
2. **Attributes**: Add relevant metadata (IDs, status codes, etc.)
3. **Events**: Mark important moments in trace timeline
4. **Errors**: Always record exceptions in spans
5. **Sampling**: Use appropriate sampling rates in production
6. **Resource Attributes**: Include service version and environment

## Troubleshooting

### No Traces Appearing

```bash

# Check Jaeger collector is reachable

kubectl -n observability port-forward svc/jaeger-collector 14268:14268
curl http://localhost:14268/

# Check service logs

kubectl logs -n default <pod-name> | grep -i "tracing\|opentelemetry"

# Verify environment variables

kubectl exec -n default <pod-name> -- env | grep -i jaeger
```

### High Cardinality Attributes

Avoid high-cardinality attributes (e.g., UUIDs as attribute keys). Use as values instead:

❌ Bad: `span.set_attribute(f"user_{user_id}", "active")`
✅ Good: `span.set_attribute("user.id", user_id)`

## Performance Impact

OpenTelemetry overhead:

- **CPU**: ~1-2% additional CPU usage
- **Memory**: ~50-100MB per service
- **Latency**: <1ms per span

## Integration with Other Services

### Prometheus Metrics

Jaeger exports metrics to Prometheus automatically:

- `jaeger_spans_received_total`
- `jaeger_spans_rejected_total`
- `jaeger_trace_latency`

### Grafana Dashboards

Import Jaeger dashboard (ID: 11668) in Grafana for:

- Trace volume over time
- Service error rates
- P95/P99 latencies
- Service dependency graphs

## Next Steps

1. Instrument remaining microservices
2. Create custom dashboards for key user flows
3. Set up alerts for trace error rates
4. Implement trace-based SLOs
5. Use trace IDs in logs for correlation
